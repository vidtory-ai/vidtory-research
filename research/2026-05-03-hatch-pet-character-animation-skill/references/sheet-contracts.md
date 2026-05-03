# Sheet Contracts

Use this reference when deciding what to create, how to package it, and what geometry to enforce.

## Output Modes

| Mode | Use when | Normal deliverables |
| --- | --- | --- |
| `character-sheet` | User needs the definitive design for a character. | Canonical base, turnaround/model sheet, optional expressions, optional props/outfits, manifest. |
| `animation-sheet` | User needs repeated poses or frame sequences. | Canonical base, one row strip per action, optional assembled sheet, contact sheet, manifest. |
| `video-consistency-pack` | User wants stable references for AI video generation. | Clean plates for front/side/back/3/4, expressions, action poses, negative constraints, manifest. |
| `game-sprite-package` | User provides or accepts engine geometry. | Transparent atlas, frame manifest, durations if known, contact sheet, preview if practical. |

Do not force all modes. Match the deliverable to the target workflow.

## Default Character Sheet Layout

If the user asks for a character sheet but gives no layout:

- Full-body canonical pose.
- Turnaround: front, three-quarter front, side, three-quarter back, back.
- Expressions: neutral, happy, surprised, angry, sad, determined, confused, scared.
- Optional closeups: face, hands/paws, prop, material/detail.
- Palette swatches can appear visually, but reliable color names and notes belong in the manifest.

Avoid in-image labels unless the user specifically asks. If labels are needed, keep them simple and verify manually.

## Default Animation Planning

If the user asks for an animation sheet but gives no actions, propose or infer actions from use case.

Common game/app rows:

| Action | Frames | Loop | Notes |
| --- | ---: | --- | --- |
| `idle` | 4-6 | yes | breathing, blink, subtle body motion |
| `walk` | 6-8 | yes | clear footfall cycle |
| `run` | 6-8 | yes | stronger body lean and stride |
| `jump` | 5-7 | no | anticipation, lift, peak, fall, land |
| `turn` | 5-7 | no | rotate or direction change |
| `emote` | 4-8 | usually no | wave, cheer, think, fail, custom mood |

For exact engine work, require or infer:

- cell width and height
- columns and rows
- row/action order
- frame count per row
- padding and safe area
- frame durations if animation playback is expected
- trim policy: fixed cell, trimmed frames, or packed atlas

When geometry matters, generate each action row separately and assemble deterministically after visual selection.

## Folder Contract

Use a run folder that can be read without conversation context:

```text
character-sheet-runs/<character-slug>/
├── request.json
├── manifest.json
├── generation-jobs.json
├── references/
│   ├── canonical-base.png
│   └── input-*.png
├── prompts/
│   ├── base.txt
│   ├── character-sheet.txt
│   └── rows/<action>.txt
├── generated/
│   └── original imagegen outputs or recorded source paths
├── processed/
│   ├── character-sheet.png
│   ├── animation-sheet.png
│   ├── rows/<action>.png
│   └── atlas.webp
└── qa/
    ├── contact-sheet.png
    ├── preview-*.mp4
    └── review.json
```

The exact file list can be smaller for concept-only work, but `request.json`, `manifest.json`, prompts, and selected outputs should exist for production runs.

## Job Manifest Shape

`generation-jobs.json` is the operational queue for `$imagegen` work. It records which visual jobs are ready, which are blocked by the canonical base, and which selected original generated files were ingested.

```json
{
  "schema": "character-sheet-animator.generation-jobs.v1",
  "run_dir": "/absolute/path/to/run",
  "request_path": "request.json",
  "jobs": [
    {
      "id": "base",
      "kind": "canonical-base",
      "status": "complete",
      "prompt_file": "prompts/base.txt",
      "output_path": "generated/base.png",
      "transparent_output_path": "processed/base-transparent.png",
      "depends_on": [],
      "input_images": [
        {"path": "references/input-01.png", "role": "identity reference"}
      ],
      "generation_skill": "$imagegen",
      "source_path": "/Users/name/.codex/generated_images/.../ig_*.png",
      "source_provenance": "built-in-imagegen",
      "source_sha256": "..."
    }
  ]
}
```

Rules:

- `source_path` should point to the original `$imagegen` output, not a copied or processed derivative.
- `output_path` is the project-local recorded copy.
- `transparent_output_path` is optional and should point to the chroma-key-removed alpha output when transparency was requested.
- Jobs after `base` should depend on `base` and include `references/canonical-base.png`.
- Layout guides are input images with role `layout guide`; generated outputs must not copy guide pixels.

## Manifest Shape

Use JSON for machine-readable output. Keep paths absolute or clearly relative to the run folder.

```json
{
  "character": {
    "id": "short-slug",
    "display_name": "Character Name",
    "description": "One concise identity sentence."
  },
  "style_lock": {
    "medium": "pixel art, cartoon, anime, 3D, etc.",
    "palette": ["optional", "color", "notes"],
    "must_preserve": ["head shape", "costume", "markings", "prop"]
  },
  "sources": {
    "canonical_base": "references/canonical-base.png",
    "input_references": []
  },
  "sheets": [
    {
      "id": "turnaround",
      "type": "character-sheet",
      "path": "processed/character-sheet.png",
      "prompt": "prompts/character-sheet.txt",
      "qa_status": "pass"
    }
  ],
  "animation_rows": [
    {
      "id": "idle",
      "path": "processed/rows/idle.png",
      "frames": 6,
      "cell": {"width": 512, "height": 512},
      "duration_ms": [160, 160, 180, 160, 160, 220],
      "qa_status": "pass"
    }
  ],
  "limitations": []
}
```

Do not store unreliable generated in-image text as the only metadata source.

## Combined Sprite Sheets

A combined sprite sheet is acceptable for quick visual review or AI-video reference when the user needs one fast asset. Record it as `combined-animation-sprite-sheet` and include row metadata in `manifest.json`.

For production game/runtime use, prefer separate row jobs:

1. Generate one row strip per action.
2. Record each row with `record_imagegen_result.py`.
3. Validate frame counts and cell geometry.
4. Compose or pack the atlas only after rows pass visual review.

## Geometry Defaults

Only use defaults when the user gives no target.

- Concept/model sheet: one high-resolution image with clean panel separation.
- Row strip: 6-8 frames horizontally per action.
- Sprite cell: square cells for game assets unless the character shape requires otherwise.
- Safe padding: 10-15 percent inside each cell.
- Background for non-transparent concept sheets: neutral light or flat studio color.
- Background for transparent assets: flat chroma key chosen through `$imagegen` transparent workflow.

If the user specifies a target engine, override these defaults with the engine contract.
