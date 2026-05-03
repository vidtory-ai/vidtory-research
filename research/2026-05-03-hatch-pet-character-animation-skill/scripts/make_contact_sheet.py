#!/usr/bin/env python3
"""Create a contact sheet for generated character animation rows."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

LABEL_HEIGHT = 28
GAP = 8


def checker(size: tuple[int, int], square: int = 16) -> Image.Image:
    image = Image.new("RGB", size, "#ffffff")
    draw = ImageDraw.Draw(image)
    for y in range(0, size[1], square):
        for x in range(0, size[0], square):
            if (x // square + y // square) % 2:
                draw.rectangle((x, y, x + square - 1, y + square - 1), fill="#e8e8e8")
    return image


def load_jobs(run_dir: Path) -> list[dict[str, object]]:
    path = run_dir / "generation-jobs.json"
    if not path.exists():
        raise SystemExit(f"job manifest not found: {path}")
    manifest = json.loads(path.read_text(encoding="utf-8"))
    jobs = manifest.get("jobs")
    if not isinstance(jobs, list):
        raise SystemExit("invalid generation-jobs.json: jobs must be a list")
    return [job for job in jobs if isinstance(job, dict)]


def action_frame_count(job: dict[str, object], image: Image.Image) -> int:
    action = job.get("action") if isinstance(job.get("action"), dict) else {}
    frames = action.get("frames")
    if isinstance(frames, int) and frames > 0:
        return frames
    return 1


def paste_rgba_on_checker(source: Image.Image, size: tuple[int, int]) -> Image.Image:
    resized = source.convert("RGBA").resize(size, Image.Resampling.LANCZOS)
    background = checker(size)
    background.paste(resized, (0, 0), resized)
    return background


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", required=True)
    parser.add_argument("--output", default="qa/contact-sheet.png")
    parser.add_argument("--scale", type=float, default=0.35)
    args = parser.parse_args()

    run_dir = Path(args.run_dir).expanduser().resolve()
    rows = [
        job
        for job in load_jobs(run_dir)
        if job.get("kind") == "animation-row" and job.get("status") == "complete"
    ]
    if not rows:
        raise SystemExit("no completed animation-row jobs found")

    opened: list[tuple[dict[str, object], Image.Image, int]] = []
    max_width = 0
    total_height = 0
    for job in rows:
        output_path = job.get("output_path")
        if not isinstance(output_path, str):
            continue
        path = run_dir / output_path
        if not path.is_file():
            continue
        image = Image.open(path).convert("RGBA")
        frames = action_frame_count(job, image)
        row_width = max(1, round(image.width * args.scale))
        row_height = max(1, round(image.height * args.scale))
        opened.append((job, image, frames))
        max_width = max(max_width, row_width)
        total_height += LABEL_HEIGHT + row_height + GAP
    if not opened:
        raise SystemExit("completed animation-row jobs have no readable output files")

    sheet = Image.new("RGB", (max_width, max(1, total_height - GAP)), "#f7f7f7")
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.load_default()
    y = 0
    for job, image, frames in opened:
        row_width = max(1, round(image.width * args.scale))
        row_height = max(1, round(image.height * args.scale))
        label = f"{job.get('id')} / {frames} frames"
        draw.rectangle((0, y, max_width, y + LABEL_HEIGHT - 1), fill="#111111")
        draw.text((8, y + 8), label, fill="#ffffff", font=font)
        y += LABEL_HEIGHT
        rendered = paste_rgba_on_checker(image, (row_width, row_height))
        sheet.paste(rendered, (0, y))
        if frames > 1:
            frame_w = row_width / frames
            for index in range(frames + 1):
                x = round(index * frame_w)
                draw.line((x, y, x, y + row_height - 1), fill="#2f80ed")
        draw.rectangle((0, y, row_width - 1, y + row_height - 1), outline="#18a058")
        y += row_height + GAP

    output = run_dir / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(output)
    print(json.dumps({"ok": True, "output": str(output), "rows": len(opened)}, indent=2))


if __name__ == "__main__":
    main()
