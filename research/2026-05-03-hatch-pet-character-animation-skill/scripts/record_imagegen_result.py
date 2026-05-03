#!/usr/bin/env python3
"""Record a selected $imagegen output for a character sheet generation job."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image

CANONICAL_BASE_PATH = "references/canonical-base.png"


def load_jobs(run_dir: Path) -> dict[str, object]:
    path = run_dir / "generation-jobs.json"
    if not path.exists():
        raise SystemExit(f"job manifest not found: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def save_jobs(run_dir: Path, manifest: dict[str, object]) -> None:
    (run_dir / "generation-jobs.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )


def job_list(manifest: dict[str, object]) -> list[dict[str, object]]:
    jobs = manifest.get("jobs")
    if not isinstance(jobs, list):
        raise SystemExit("invalid generation-jobs.json: jobs must be a list")
    return [job for job in jobs if isinstance(job, dict)]


def find_job(manifest: dict[str, object], job_id: str) -> dict[str, object]:
    for job in job_list(manifest):
        if job.get("id") == job_id:
            return job
    raise SystemExit(f"unknown job id: {job_id}")


def completed_job_ids(manifest: dict[str, object]) -> set[str]:
    return {
        str(job["id"])
        for job in job_list(manifest)
        if job.get("status") == "complete" and isinstance(job.get("id"), str)
    }


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def image_metadata(path: Path) -> dict[str, object]:
    with Image.open(path) as image:
        image.verify()
    with Image.open(path) as image:
        return {
            "width": image.width,
            "height": image.height,
            "mode": image.mode,
            "format": image.format,
        }


def is_relative_to(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
    except ValueError:
        return False
    return True


def default_generated_images_root() -> Path:
    return Path(os.environ.get("CODEX_HOME") or "~/.codex").expanduser().resolve() / "generated_images"


def validate_source_path(source: Path, run_dir: Path, allow_local_source: bool) -> str:
    if allow_local_source:
        return "local-explicit"
    if is_relative_to(source, run_dir):
        raise SystemExit(
            "source image is inside the run directory; record the original "
            "$imagegen output from $CODEX_HOME/generated_images/.../ig_*.png instead"
        )
    generated_root = default_generated_images_root()
    if not is_relative_to(source, generated_root) or not source.name.startswith("ig_"):
        raise SystemExit(
            "source image does not look like a built-in $imagegen output; expected "
            f"{generated_root}/.../ig_*.png. Use --allow-local-source only for tests or manual import."
        )
    return "built-in-imagegen"


def copy_image_as_png(source: Path, output: Path) -> dict[str, object]:
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.suffix.lower() == source.suffix.lower() == ".png":
        shutil.copy2(source, output)
    else:
        with Image.open(source) as image:
            image.save(output, "PNG")
    return image_metadata(output)


def manifest_relative(path: Path, run_dir: Path) -> str:
    return str(path.resolve().relative_to(run_dir.resolve()))


def validate_dependencies(job: dict[str, object], manifest: dict[str, object], job_id: str) -> None:
    completed = completed_job_ids(manifest)
    deps = job.get("depends_on") if isinstance(job.get("depends_on"), list) else []
    missing = [dep for dep in deps if isinstance(dep, str) and dep not in completed]
    if missing:
        raise SystemExit(
            f"job {job_id} is not ready; missing dependency result(s): {', '.join(missing)}"
        )


def validate_required_inputs(job: dict[str, object], run_dir: Path) -> None:
    if job.get("allow_prompt_only_generation"):
        return
    inputs = job.get("input_images")
    if not isinstance(inputs, list) or not inputs:
        raise SystemExit(f"job {job.get('id')} requires grounded image inputs")
    missing: list[str] = []
    for item in inputs:
        if not isinstance(item, dict) or not isinstance(item.get("path"), str):
            raise SystemExit(f"job {job.get('id')} has an invalid input image entry")
        path = run_dir / item["path"]
        if not path.is_file():
            missing.append(str(path))
    if missing:
        raise SystemExit(
            f"job {job.get('id')} is missing required input image(s): "
            + ", ".join(missing)
        )


def load_project_manifest(run_dir: Path) -> dict[str, object]:
    path = run_dir / "manifest.json"
    if not path.exists():
        return {
            "schema": "character-sheet-animator.manifest.v1",
            "outputs": [],
            "animation_rows": [],
            "limitations": [],
        }
    return json.loads(path.read_text(encoding="utf-8"))


def save_project_manifest(run_dir: Path, manifest: dict[str, object]) -> None:
    (run_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )


def update_project_manifest(
    *,
    run_dir: Path,
    job: dict[str, object],
    output: Path,
    metadata: dict[str, object],
) -> None:
    manifest = load_project_manifest(run_dir)
    outputs = manifest.setdefault("outputs", [])
    if not isinstance(outputs, list):
        outputs = []
        manifest["outputs"] = outputs
    rows = manifest.setdefault("animation_rows", [])
    if not isinstance(rows, list):
        rows = []
        manifest["animation_rows"] = rows

    record = {
        "id": job.get("id"),
        "type": job.get("kind"),
        "path": manifest_relative(output, run_dir),
        "prompt": job.get("prompt_file"),
        "metadata": metadata,
        "qa_status": "pending-visual-review",
    }
    if job.get("kind") == "animation-row":
        action = job.get("action") if isinstance(job.get("action"), dict) else {}
        record["action"] = action
        rows[:] = [item for item in rows if isinstance(item, dict) and item.get("id") != job.get("id")]
        rows.append(record)
    else:
        outputs[:] = [item for item in outputs if isinstance(item, dict) and item.get("id") != job.get("id")]
        outputs.append(record)
    save_project_manifest(run_dir, manifest)


def update_canonical_base(
    *,
    run_dir: Path,
    output: Path,
    manifest: dict[str, object],
    job: dict[str, object],
    metadata: dict[str, object],
) -> None:
    if job.get("id") != "base":
        return
    canonical = run_dir / CANONICAL_BASE_PATH
    canonical.parent.mkdir(parents=True, exist_ok=True)
    copy_image_as_png(output, canonical)
    reference = {
        "path": manifest_relative(canonical, run_dir),
        "source_job": "base",
        "sha256": file_sha256(canonical),
        "metadata": image_metadata(canonical),
    }
    job["canonical_reference_path"] = reference["path"]
    manifest["canonical_identity_reference"] = reference
    request_path = run_dir / "request.json"
    if request_path.exists():
        request = json.loads(request_path.read_text(encoding="utf-8"))
        request["canonical_identity_reference"] = reference
        request_path.write_text(json.dumps(request, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", required=True)
    parser.add_argument("--job-id", required=True)
    parser.add_argument("--source", required=True)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--allow-local-source", action="store_true")
    args = parser.parse_args()

    run_dir = Path(args.run_dir).expanduser().resolve()
    source = Path(args.source).expanduser().resolve()
    if not source.is_file():
        raise SystemExit(f"source image not found: {source}")
    provenance = validate_source_path(source, run_dir, args.allow_local_source)

    manifest = load_jobs(run_dir)
    job = find_job(manifest, args.job_id)
    validate_dependencies(job, manifest, args.job_id)
    validate_required_inputs(job, run_dir)

    output_raw = job.get("output_path")
    if not isinstance(output_raw, str):
        raise SystemExit(f"job {args.job_id} has no output_path")
    output = run_dir / output_raw
    if output.exists() and not args.force:
        raise SystemExit(f"{output} already exists; pass --force to replace it")

    metadata = copy_image_as_png(source, output)
    job["status"] = "complete"
    job["source_path"] = str(source)
    job["source_provenance"] = provenance
    job["source_sha256"] = file_sha256(source)
    job["output_sha256"] = file_sha256(output)
    job["completed_at"] = datetime.now(timezone.utc).isoformat()
    job["metadata"] = metadata
    for key in ["last_error", "repair_reason", "queued_at"]:
        job.pop(key, None)

    update_canonical_base(
        run_dir=run_dir,
        output=output,
        manifest=manifest,
        job=job,
        metadata=metadata,
    )
    update_project_manifest(run_dir=run_dir, job=job, output=output, metadata=metadata)
    save_jobs(run_dir, manifest)
    print(
        json.dumps(
            {
                "ok": True,
                "job_id": args.job_id,
                "output": str(output),
                "provenance": provenance,
                "metadata": metadata,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
