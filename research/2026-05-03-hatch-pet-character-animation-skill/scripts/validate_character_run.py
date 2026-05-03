#!/usr/bin/env python3
"""Run deterministic validation checks for a character sheet run."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image


def load_json(path: Path) -> dict[str, object]:
    if not path.exists():
        raise SystemExit(f"required file not found: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def load_jobs(run_dir: Path) -> list[dict[str, object]]:
    manifest = load_json(run_dir / "generation-jobs.json")
    jobs = manifest.get("jobs")
    if not isinstance(jobs, list):
        raise SystemExit("invalid generation-jobs.json: jobs must be a list")
    return [job for job in jobs if isinstance(job, dict)]


def image_info(path: Path) -> dict[str, object]:
    with Image.open(path) as image:
        image.verify()
    with Image.open(path) as image:
        return {
            "width": image.width,
            "height": image.height,
            "mode": image.mode,
            "has_alpha": image.mode in {"RGBA", "LA"} or "transparency" in image.info,
        }


def check_transparent_corners(path: Path) -> bool:
    with Image.open(path) as image:
        rgba = image.convert("RGBA")
        points = [
            (0, 0),
            (rgba.width - 1, 0),
            (0, rgba.height - 1),
            (rgba.width - 1, rgba.height - 1),
        ]
        return all(rgba.getpixel(point)[3] == 0 for point in points)


def add_error(errors: list[dict[str, object]], job_id: str, message: str) -> None:
    errors.append({"job_id": job_id, "message": message})


def add_warning(warnings: list[dict[str, object]], job_id: str, message: str) -> None:
    warnings.append({"job_id": job_id, "message": message})


def validate_job(
    *,
    run_dir: Path,
    request: dict[str, object],
    job: dict[str, object],
    errors: list[dict[str, object]],
    warnings: list[dict[str, object]],
) -> dict[str, object] | None:
    job_id = str(job.get("id"))
    output_raw = job.get("output_path")
    if job.get("status") != "complete":
        add_warning(warnings, job_id, "job is not complete")
        return None
    if not isinstance(output_raw, str):
        add_error(errors, job_id, "job has no output_path")
        return None
    output = run_dir / output_raw
    if not output.is_file():
        add_error(errors, job_id, f"output file missing: {output}")
        return None

    try:
        info = image_info(output)
    except Exception as exc:  # noqa: BLE001
        add_error(errors, job_id, f"output is not a readable image: {exc}")
        return None

    if job.get("kind") == "animation-row":
        action = job.get("action") if isinstance(job.get("action"), dict) else {}
        frames = action.get("frames")
        if not isinstance(frames, int) or frames <= 0:
            add_error(errors, job_id, "animation row is missing a positive frame count")
        elif int(info["width"]) % frames != 0:
            add_warning(
                warnings,
                job_id,
                f"row width {info['width']} is not evenly divisible by {frames} frames",
            )
    if request.get("transparent"):
        transparent_raw = job.get("transparent_output_path")
        transparent_path = (
            run_dir / transparent_raw if isinstance(transparent_raw, str) else output
        )
        if not transparent_path.is_file():
            add_warning(warnings, job_id, "transparent run output has no alpha channel yet")
        else:
            transparent_info = image_info(transparent_path)
            if not transparent_info["has_alpha"]:
                add_warning(warnings, job_id, "transparent run output has no alpha channel yet")
            elif not check_transparent_corners(transparent_path):
                add_warning(warnings, job_id, "alpha output does not have transparent corners")
    return {"job_id": job_id, "path": output_raw, "metadata": info}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", required=True)
    args = parser.parse_args()

    run_dir = Path(args.run_dir).expanduser().resolve()
    request = load_json(run_dir / "request.json")
    jobs = load_jobs(run_dir)
    errors: list[dict[str, object]] = []
    warnings: list[dict[str, object]] = []
    checked: list[dict[str, object]] = []

    canonical = run_dir / "references/canonical-base.png"
    if not canonical.is_file():
        add_warning(warnings, "base", "canonical base reference has not been recorded yet")

    for job in jobs:
        result = validate_job(
            run_dir=run_dir,
            request=request,
            job=job,
            errors=errors,
            warnings=warnings,
        )
        if result:
            checked.append(result)

    review = {
        "ok": not errors,
        "run_dir": str(run_dir),
        "checked_outputs": checked,
        "errors": errors,
        "warnings": warnings,
        "visual_review_required": [
            "same character identity across every sheet and frame",
            "no accidental redesign, extra character, generated text, or copied layout guide",
            "animation frames are distinct poses, not repeated static transforms",
        ],
    }
    output = run_dir / "qa/review.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(review, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(review, indent=2))
    raise SystemExit(0 if not errors else 1)


if __name__ == "__main__":
    main()
