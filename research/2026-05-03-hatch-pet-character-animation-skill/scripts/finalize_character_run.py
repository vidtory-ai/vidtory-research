#!/usr/bin/env python3
"""Finalize a character sheet run with QA files and a run summary."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent


def run_command(args: list[str], *, allow_failure: bool = False) -> tuple[int, str]:
    completed = subprocess.run(
        args,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    if completed.returncode != 0 and not allow_failure:
        raise SystemExit(completed.stdout)
    return completed.returncode, completed.stdout


def load_json(path: Path) -> dict[str, object]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def completed_jobs(run_dir: Path) -> list[dict[str, object]]:
    manifest = load_json(run_dir / "generation-jobs.json")
    jobs = manifest.get("jobs")
    if not isinstance(jobs, list):
        return []
    return [
        job
        for job in jobs
        if isinstance(job, dict) and job.get("status") == "complete"
    ]


def has_completed_rows(run_dir: Path) -> bool:
    return any(job.get("kind") == "animation-row" for job in completed_jobs(run_dir))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", required=True)
    parser.add_argument("--skip-contact-sheet", action="store_true")
    args = parser.parse_args()

    run_dir = Path(args.run_dir).expanduser().resolve()
    if not run_dir.is_dir():
        raise SystemExit(f"run dir not found: {run_dir}")

    validate_code, validate_output = run_command(
        [
            sys.executable,
            str(SCRIPT_DIR / "validate_character_run.py"),
            "--run-dir",
            str(run_dir),
        ],
        allow_failure=True,
    )

    contact_output = None
    contact_code = None
    contact_log = ""
    if has_completed_rows(run_dir) and not args.skip_contact_sheet:
        contact_code, contact_log = run_command(
            [
                sys.executable,
                str(SCRIPT_DIR / "make_contact_sheet.py"),
                "--run-dir",
                str(run_dir),
            ],
            allow_failure=True,
        )
        if contact_code == 0:
            contact_output = "qa/contact-sheet.png"

    summary = {
        "ok": validate_code == 0 and (contact_code in {None, 0}),
        "finalized_at": datetime.now(timezone.utc).isoformat(),
        "run_dir": str(run_dir),
        "request": load_json(run_dir / "request.json"),
        "manifest": load_json(run_dir / "manifest.json"),
        "generation_jobs": load_json(run_dir / "generation-jobs.json"),
        "qa": {
            "review": load_json(run_dir / "qa/review.json"),
            "contact_sheet": contact_output,
            "validate_exit_code": validate_code,
            "contact_sheet_exit_code": contact_code,
        },
        "logs": {
            "validate": validate_output,
            "contact_sheet": contact_log,
        },
    }
    output = run_dir / "qa/run-summary.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"ok": summary["ok"], "summary": str(output)}, indent=2))
    raise SystemExit(0 if summary["ok"] else 1)


if __name__ == "__main__":
    main()
