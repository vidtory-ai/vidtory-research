#!/usr/bin/env python3
"""Create a character sheet run folder, prompts, layout guides, and job manifest."""

from __future__ import annotations

import argparse
import json
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image, ImageDraw

DEFAULT_ACTIONS = [
    {"id": "idle", "frames": 6, "direction": "front", "loop": True, "notes": "subtle breathing, blink, and small body motion"},
    {"id": "walk", "frames": 8, "direction": "right", "loop": True, "notes": "clear readable walking cycle"},
    {"id": "run", "frames": 8, "direction": "right", "loop": True, "notes": "faster locomotion with stronger body lean"},
    {"id": "jump", "frames": 6, "direction": "front", "loop": False, "notes": "anticipation, lift, peak, fall, and settle"},
    {"id": "emote", "frames": 6, "direction": "front", "loop": False, "notes": "one clear personality gesture"},
]

OUTPUT_CHOICES = {
    "character-sheet",
    "turnaround",
    "expression-sheet",
    "animation-sheet",
    "video-consistency-pack",
    "game-sprite-package",
}


def slugify(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    value = re.sub(r"-{2,}", "-", value)
    return value.strip("-") or "character"


def display_from_slug(value: str) -> str:
    words = [word for word in re.split(r"[^a-zA-Z0-9]+", value.strip()) if word]
    return " ".join(word.capitalize() for word in words) or "Character"


def sentence(value: str) -> str:
    value = " ".join(value.strip().split())
    if value and value[-1] not in ".!?":
        value += "."
    return value


def default_output_dir(character_id: str) -> Path:
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return Path.cwd() / "character-sheet-runs" / f"{character_id}-{timestamp}"


def rel(path: Path, root: Path) -> str:
    return str(path.resolve().relative_to(root.resolve()))


def parse_output(raw_values: list[str]) -> list[str]:
    if not raw_values:
        return ["character-sheet", "animation-sheet"]
    outputs: list[str] = []
    for raw in raw_values:
        for item in raw.split(","):
            value = item.strip()
            if not value:
                continue
            if value not in OUTPUT_CHOICES:
                raise SystemExit(f"unknown output type: {value}")
            if value not in outputs:
                outputs.append(value)
    return outputs


def parse_action(raw: str) -> dict[str, object]:
    parts = [part.strip() for part in raw.split(":")]
    if len(parts) < 2:
        raise SystemExit(
            "invalid --action; expected id:frames[:direction[:loop[:notes]]]"
        )
    action_id = slugify(parts[0])
    try:
        frames = int(parts[1])
    except ValueError as exc:
        raise SystemExit(f"invalid frame count for action {parts[0]}") from exc
    if frames <= 0:
        raise SystemExit(f"action {action_id} must have at least one frame")
    direction = parts[2] if len(parts) >= 3 and parts[2] else "front"
    loop = True
    if len(parts) >= 4 and parts[3]:
        loop = parts[3].lower() in {"1", "yes", "true", "loop", "looping"}
    notes = parts[4] if len(parts) >= 5 else ""
    return {
        "id": action_id,
        "frames": frames,
        "direction": direction,
        "loop": loop,
        "notes": notes,
    }


def copy_references(raw_paths: list[str], run_dir: Path) -> list[dict[str, object]]:
    copied: list[dict[str, object]] = []
    ref_dir = run_dir / "references"
    ref_dir.mkdir(parents=True, exist_ok=True)
    for index, raw in enumerate(raw_paths, start=1):
        source = Path(raw).expanduser().resolve()
        if not source.is_file():
            raise SystemExit(f"reference not found: {source}")
        suffix = source.suffix.lower() or ".png"
        target = ref_dir / f"input-{index:02d}{suffix}"
        shutil.copy2(source, target)
        copied.append(
            {
                "path": rel(target, run_dir),
                "source_path": str(source),
                "role": "identity reference" if index == 1 else "supporting reference",
                "metadata": image_metadata(target),
            }
        )
    return copied


def image_metadata(path: Path) -> dict[str, object]:
    with Image.open(path) as image:
        return {
            "width": image.width,
            "height": image.height,
            "mode": image.mode,
            "format": image.format,
        }


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def create_layout_guide(
    path: Path,
    *,
    action_id: str,
    frames: int,
    cell_width: int,
    cell_height: int,
) -> dict[str, object]:
    width = frames * cell_width
    height = cell_height
    margin_x = max(8, round(cell_width * 0.08))
    margin_y = max(8, round(cell_height * 0.08))
    image = Image.new("RGB", (width, height), "#f7f7f7")
    draw = ImageDraw.Draw(image)
    for index in range(frames):
        left = index * cell_width
        right = left + cell_width - 1
        draw.rectangle((left, 0, right, height - 1), outline="#111111", width=2)
        draw.rectangle(
            (
                left + margin_x,
                margin_y,
                right - margin_x,
                height - 1 - margin_y,
            ),
            outline="#2f80ed",
            width=2,
        )
        draw.line((left + cell_width // 2, margin_y, left + cell_width // 2, height - 1 - margin_y), fill="#aaaaaa")
        draw.text((left + 8, 8), f"{action_id} {index + 1}", fill="#111111")
    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path)
    return {
        "path": str(path),
        "frames": frames,
        "cell_width": cell_width,
        "cell_height": cell_height,
        "width": width,
        "height": height,
    }


def base_prompt(
    *,
    name: str,
    description: str,
    character_notes: str,
    style_notes: str,
    transparent: bool,
    chroma_key: str,
) -> str:
    background = (
        f"Use a perfectly flat solid {chroma_key} chroma-key background for later background removal."
        if transparent
        else "Use a clean neutral studio background that does not distract from the design."
    )
    return f"""
Create the canonical visual reference for this character.

Character:
- Name: {name}
- Description: {description}
- Character notes: {character_notes or "infer from the description and references"}

Style:
- {style_notes or "clean production character-design style"}

Composition:
- one full-body character only
- neutral standing pose
- clear front three-quarter view
- complete unclipped body
- generous padding around the character
- {background}

Avoid:
- extra characters, scenery, UI, fake labels, watermarks, speech bubbles
- dramatic lighting that hides design details
- changing or omitting required identity details
"""


def character_sheet_prompt(name: str, style_notes: str) -> str:
    return f"""
Create a clean character model sheet for the same character shown in the attached canonical base.

Identity lock:
- preserve the exact same character: proportions, face, palette, costume, markings, props, and rendering style
- no redesigns and no alternate character

Sheet layout:
- one character repeated across clean panels
- full-body views: front, three-quarter front, side, three-quarter back, back
- consistent scale and camera height across views
- neutral pose for each view
- clean spacing, no scene

Style:
- match the canonical base exactly
- {style_notes or "consistent clean character-design rendering"}

Avoid:
- labels or generated text unless explicitly requested
- extra characters, scenery, shadows, watermarks, UI, speech bubbles
- cropped limbs, inconsistent height, different costume, changed markings

Character name for manifest only: {name}
"""


def expression_sheet_prompt(style_notes: str) -> str:
    return f"""
Create an expression sheet for the same character shown in the attached canonical base.

Identity lock:
- same face structure, head shape, hair/ears/horns/helmet, palette, and rendering style
- expressions vary; identity does not

Expressions:
- neutral, happy, surprised, angry, sad, determined, confused, scared

Composition:
- head-and-shoulders or bust crops
- consistent angle and scale
- clean grid with separated panels
- no labels or generated text
- flat neutral background

Style:
- {style_notes or "match the canonical base exactly"}

Avoid:
- changing age, species, costume, proportions, palette, or line style
- unreadable text, scenery, speech bubbles, duplicate identical faces
"""


def video_plate_prompt(style_notes: str) -> str:
    return f"""
Create a clean AI video consistency reference plate for the same character shown in the attached canonical base.

Identity lock:
- preserve the attached canonical character exactly
- prioritize stable silhouette, readable face, costume, markings, palette, and prop placement

Plate contents:
- one neutral full-body pose
- one action key pose
- one close-up face reference
- one side or back reference

Style:
- {style_notes or "match the canonical base exactly"}
- clean lighting, no extreme perspective, no heavy effects

Avoid:
- poster composition, cinematic background, text, logos, watermarks, extra characters
- changing costume, age, species, palette, or proportions
"""


def animation_prompt(
    *,
    action: dict[str, object],
    style_notes: str,
    transparent: bool,
    chroma_key: str,
) -> str:
    frames = int(action["frames"])
    action_id = str(action["id"])
    background = (
        f"Use a perfectly flat solid {chroma_key} chroma-key background for background removal. Do not use {chroma_key} anywhere in the character, props, effects, highlights, or shadows."
        if transparent
        else "Use a clean flat neutral background."
    )
    loop_text = "The first and last frames should loop cleanly." if action.get("loop") else "The row should read as a clear non-looping action sequence."
    return f"""
Create one animation row strip for the same character shown in the attached canonical base.

Action:
- Row id: {action_id}
- Frame count: {frames}
- Direction: {action.get("direction", "front")}
- Looping: {bool(action.get("loop"))}
- Motion notes: {action.get("notes") or "make the action readable at sprite-sheet scale"}

Identity lock:
- preserve the same character, proportions, face, costume, markings, palette, props, and style
- no redesigns and no extra characters

Layout:
- {frames} complete full-body frames in one horizontal row
- frames are evenly spaced and separated
- each pose stays inside its own frame slot with safe padding
- no visible grid, labels, frame numbers, borders, or construction marks
- {background}

Animation quality:
- each frame should be a distinct pose in the action cycle
- {loop_text}
- show motion through body, limbs, cloth, hair, or prop pose changes

Style:
- {style_notes or "match the canonical base exactly"}

Avoid:
- repeated duplicate frames
- cropped body parts
- pose crossing into adjacent slot
- speed lines, dust, shadows, glows, afterimages, motion smears, floating icons
- text, UI, watermarks, scenery
"""


def job(
    *,
    job_id: str,
    kind: str,
    prompt_file: str,
    output_path: str,
    depends_on: list[str] | None = None,
    input_images: list[dict[str, str]] | None = None,
    allow_prompt_only: bool = False,
    extra: dict[str, object] | None = None,
) -> dict[str, object]:
    item = {
        "id": job_id,
        "kind": kind,
        "status": "pending",
        "prompt_file": prompt_file,
        "output_path": output_path,
        "depends_on": depends_on or [],
        "input_images": input_images or [],
        "generation_skill": "$imagegen",
        "allow_prompt_only_generation": allow_prompt_only,
        "requires_grounded_generation": not allow_prompt_only,
        "recording_owner": "parent",
    }
    if extra:
        item.update(extra)
    return item


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--character-name", default="")
    parser.add_argument("--character-id", default="")
    parser.add_argument("--description", default="")
    parser.add_argument("--character-notes", default="")
    parser.add_argument("--style-notes", default="")
    parser.add_argument("--reference", action="append", default=[])
    parser.add_argument("--output", action="append", default=[])
    parser.add_argument("--action", action="append", default=[])
    parser.add_argument("--cell-width", type=int, default=512)
    parser.add_argument("--cell-height", type=int, default=512)
    parser.add_argument("--transparent", action="store_true")
    parser.add_argument("--chroma-key", default="#FF00FF")
    parser.add_argument("--output-dir", default="")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    character_name = args.character_name.strip()
    if not character_name:
        character_name = display_from_slug(args.character_id) if args.character_id else "Character"
    character_id = slugify(args.character_id or character_name)
    description = sentence(args.description or args.character_notes or f"{character_name} character for sheet generation")
    outputs = parse_output(args.output)
    actions = [parse_action(raw) for raw in args.action] if args.action else list(DEFAULT_ACTIONS)

    run_dir = Path(args.output_dir).expanduser().resolve() if args.output_dir else default_output_dir(character_id).resolve()
    if run_dir.exists() and any(run_dir.iterdir()) and not args.force:
        raise SystemExit(f"{run_dir} already exists and is not empty; pass --force")
    run_dir.mkdir(parents=True, exist_ok=True)
    for child in ["prompts/rows", "generated/rows", "processed/rows", "references/layout-guides", "qa", "final"]:
        (run_dir / child).mkdir(parents=True, exist_ok=True)

    references = copy_references(args.reference, run_dir)
    request = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "character": {
            "id": character_id,
            "display_name": character_name,
            "description": description,
            "notes": args.character_notes,
        },
        "style_notes": args.style_notes,
        "outputs": outputs,
        "transparent": args.transparent,
        "chroma_key": args.chroma_key,
        "geometry": {
            "cell_width": args.cell_width,
            "cell_height": args.cell_height,
        },
        "actions": actions if any(output in outputs for output in ["animation-sheet", "game-sprite-package"]) else [],
        "references": references,
    }
    (run_dir / "request.json").write_text(json.dumps(request, indent=2) + "\n", encoding="utf-8")

    jobs: list[dict[str, object]] = []
    write_text(
        run_dir / "prompts/base.txt",
        base_prompt(
            name=character_name,
            description=description,
            character_notes=args.character_notes,
            style_notes=args.style_notes,
            transparent=args.transparent,
            chroma_key=args.chroma_key,
        ),
    )
    jobs.append(
        job(
            job_id="base",
            kind="canonical-base",
            prompt_file="prompts/base.txt",
            output_path="generated/base.png",
            input_images=[{"path": ref["path"], "role": ref["role"]} for ref in references],
            allow_prompt_only=True,
        )
    )

    canonical_input = [{"path": "references/canonical-base.png", "role": "canonical identity reference"}]
    original_ref_inputs = [{"path": ref["path"], "role": ref["role"]} for ref in references]

    if "character-sheet" in outputs or "turnaround" in outputs:
        write_text(run_dir / "prompts/character-sheet.txt", character_sheet_prompt(character_name, args.style_notes))
        jobs.append(
            job(
                job_id="character-sheet",
                kind="character-sheet",
                prompt_file="prompts/character-sheet.txt",
                output_path="generated/character-sheet.png",
                depends_on=["base"],
                input_images=canonical_input + original_ref_inputs,
            )
        )

    if "expression-sheet" in outputs:
        write_text(run_dir / "prompts/expression-sheet.txt", expression_sheet_prompt(args.style_notes))
        jobs.append(
            job(
                job_id="expression-sheet",
                kind="expression-sheet",
                prompt_file="prompts/expression-sheet.txt",
                output_path="generated/expression-sheet.png",
                depends_on=["base"],
                input_images=canonical_input + original_ref_inputs,
            )
        )

    if "video-consistency-pack" in outputs:
        write_text(run_dir / "prompts/video-consistency-pack.txt", video_plate_prompt(args.style_notes))
        jobs.append(
            job(
                job_id="video-consistency-pack",
                kind="video-consistency-pack",
                prompt_file="prompts/video-consistency-pack.txt",
                output_path="generated/video-consistency-pack.png",
                depends_on=["base"],
                input_images=canonical_input + original_ref_inputs,
            )
        )

    if any(output in outputs for output in ["animation-sheet", "game-sprite-package"]):
        for action in actions:
            action_id = str(action["id"])
            prompt_path = f"prompts/rows/{action_id}.txt"
            guide_path = run_dir / "references/layout-guides" / f"{action_id}.png"
            guide = create_layout_guide(
                guide_path,
                action_id=action_id,
                frames=int(action["frames"]),
                cell_width=args.cell_width,
                cell_height=args.cell_height,
            )
            write_text(
                run_dir / prompt_path,
                animation_prompt(
                    action=action,
                    style_notes=args.style_notes,
                    transparent=args.transparent,
                    chroma_key=args.chroma_key,
                ),
            )
            jobs.append(
                job(
                    job_id=f"row-{action_id}",
                    kind="animation-row",
                    prompt_file=prompt_path,
                    output_path=f"generated/rows/{action_id}.png",
                    depends_on=["base"],
                    input_images=canonical_input
                    + original_ref_inputs
                    + [{"path": rel(guide_path, run_dir), "role": "layout guide"}],
                    extra={
                        "action": action,
                        "layout_guide": {
                            "path": rel(guide_path, run_dir),
                            "metadata": guide,
                        },
                    },
                )
            )

    manifest = {
        "schema": "character-sheet-animator.generation-jobs.v1",
        "run_dir": str(run_dir),
        "request_path": "request.json",
        "jobs": jobs,
    }
    (run_dir / "generation-jobs.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    (run_dir / "manifest.json").write_text(
        json.dumps(
            {
                "schema": "character-sheet-animator.manifest.v1",
                "character": request["character"],
                "style_notes": args.style_notes,
                "outputs": [],
                "animation_rows": [],
                "limitations": ["Visual identity still requires human inspection."],
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(json.dumps({"ok": True, "run_dir": str(run_dir), "jobs": len(jobs)}, indent=2))


if __name__ == "__main__":
    main()
