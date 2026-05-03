# Hatch Pet Source Inventory

The original `hatch-pet` skill was copied into this research folder without editing:

```text
source/hatch-pet/
├── LICENSE.txt
├── SKILL.md
├── agents/
│   └── openai.yaml
├── references/
│   ├── animation-rows.md
│   ├── codex-pet-contract.md
│   └── qa-rubric.md
└── scripts/
    ├── compose_atlas.py
    ├── derive_running_left_from_running_right.py
    ├── extract_strip_frames.py
    ├── finalize_pet_run.py
    ├── generate_pet_images.py
    ├── inspect_frames.py
    ├── make_contact_sheet.py
    ├── package_custom_pet.py
    ├── pet_job_status.py
    ├── prepare_pet_run.py
    ├── queue_pet_repairs.py
    ├── record_imagegen_result.py
    ├── render_animation_videos.py
    ├── render_animation_videos.sh
    └── validate_atlas.py
```

Line count snapshot:

| File group | Lines |
| --- | ---: |
| `source/hatch-pet/SKILL.md` | 320 |
| `source/hatch-pet/references/*.md` | 124 |
| `source/hatch-pet/scripts/*.py` | 3221 |
| Total counted source | 3665 |

This snapshot is preserved as evidence and source material. The generalized rewrite lives at the research root as `SKILL.md` with supporting references under `references/`.

## Generalized Script Layer

The research root also includes a rewritten script layer for the new `character-sheet-animator` contract:

```text
scripts/
├── character_job_status.py
├── finalize_character_run.py
├── make_contact_sheet.py
├── prepare_character_run.py
├── queue_character_repairs.py
├── record_imagegen_result.py
└── validate_character_run.py
```

These scripts intentionally do not overwrite the original pet scripts. They replace pet-specific terms and fixed Codex pet geometry with a neutral run contract:

- `request.json`
- `generation-jobs.json`
- `manifest.json`
- configurable output modes
- configurable action rows
- configurable cell width/height
- canonical character base reference
- project-local QA outputs

Root script line count snapshot:

| File group | Lines |
| --- | ---: |
| `scripts/*.py` | 1452 |
| `SKILL.md` | 275 |
| `README.md` | 195 |
| `references/*.md` | 601 |
| Root rewrite docs/scripts total | 2523 |

## Demo Run Inventory

The `runs/vidtory-spark-demo/` folder is a real workflow test using the generalized scripts and `$imagegen`.

Key outputs:

```text
runs/vidtory-spark-demo/
├── request.json
├── generation-jobs.json
├── manifest.json
├── generated/
│   ├── base.png
│   ├── character-sheet.png
│   └── sprite-sheet.png
├── processed/
│   ├── base-transparent.png
│   ├── character-sheet-transparent.png
│   └── sprite-sheet-transparent.png
├── prompts/
├── references/
│   ├── canonical-base.png
│   ├── input-01.png
│   ├── input-02.png
│   └── layout-guides/
└── qa/
    ├── review.json
    └── run-summary.json
```

The demo confirms the current end-to-end path: prepare run, generate with `$imagegen`, record selected outputs, remove chroma key into alpha files, validate, and finalize.
