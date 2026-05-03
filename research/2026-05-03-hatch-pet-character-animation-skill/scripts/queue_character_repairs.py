#!/usr/bin/env python3
"""Reopen failed character sheet jobs for targeted repair."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


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


def repair_ids_from_review(run_dir: Path) -> dict[str, str]:
    path = run_dir / "qa/review.json"
    if not path.exists():
        return {}
    review = json.loads(path.read_text(encoding="utf-8"))
    repair_ids: dict[str, str] = {}
    for key in ["errors", "warnings"]:
        items = review.get(key)
        if not isinstance(items, list):
            continue
        for item in items:
            if not isinstance(item, dict):
                continue
            job_id = item.get("job_id")
            message = item.get("message")
            if isinstance(job_id, str) and isinstance(message, str):
                repair_ids.setdefault(job_id, message)
    return repair_ids


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", required=True)
    parser.add_argument("--job-id", action="append", default=[])
    parser.add_argument("--reason", default="")
    parser.add_argument("--include-warnings", action="store_true")
    args = parser.parse_args()

    run_dir = Path(args.run_dir).expanduser().resolve()
    manifest = load_jobs(run_dir)
    requested = {job_id: args.reason or "manual repair request" for job_id in args.job_id}
    if not requested:
        requested = repair_ids_from_review(run_dir)
    if not requested:
        raise SystemExit("no repair jobs specified and qa/review.json has no repairable entries")

    queued: list[str] = []
    known = {str(job.get("id")): job for job in job_list(manifest) if isinstance(job.get("id"), str)}
    for job_id, reason in requested.items():
        job = known.get(job_id)
        if not job:
            continue
        if job.get("id") == "base":
            reason = reason + " Base repairs may require regenerating every dependent sheet."
        job["status"] = "pending"
        job["repair_attempt"] = int(job.get("repair_attempt", 0) or 0) + 1
        job["repair_reason"] = reason
        job["queued_at"] = datetime.now(timezone.utc).isoformat()
        for key in [
            "completed_at",
            "source_path",
            "source_provenance",
            "source_sha256",
            "output_sha256",
            "metadata",
        ]:
            job.pop(key, None)
        queued.append(job_id)

    if not queued:
        raise SystemExit("no matching jobs found to queue")
    save_jobs(run_dir, manifest)
    print(json.dumps({"ok": True, "queued": queued}, indent=2))


if __name__ == "__main__":
    main()
