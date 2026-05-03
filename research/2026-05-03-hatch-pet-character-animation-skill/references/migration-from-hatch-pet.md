# Migration From Hatch Pet

This research keeps the original `hatch-pet` source unchanged under `source/hatch-pet/`. The rewritten skill at `SKILL.md` generalizes its workflow for arbitrary character sheets and animation sheets.

## Preserved Ideas

| Hatch Pet idea | Generalized use |
| --- | --- |
| Canonical base pet | Canonical base character reference for all later sheets. |
| `$imagegen` as primary generator | `$imagegen` remains the only normal visual generation layer. |
| Row-specific prompts | Animation rows are planned and generated one action at a time. |
| Layout guides | Used for any exact frame count, grid, cell, or row geometry. |
| Chroma-key transparency | Used for transparent sprites and game-ready sheets through `$imagegen` transparent workflow. |
| Deterministic atlas composition | Used only after generated row strips exist and are visually accepted. |
| Contact sheet and preview QA | Used for multi-frame animation outputs. |
| Targeted repair queue | Smallest failing frame, panel, row, or sheet is repaired before broad regeneration. |
| Visual identity drift as blocker | Identity consistency is required even when geometry checks pass. |

## Removed Pet-Specific Constraints

- Codex app pet package output.
- `pet.json`.
- `${CODEX_HOME:-$HOME/.codex}/pets/<pet-name>/` install location.
- Fixed `1536x1872` atlas.
- Fixed `8 columns x 9 rows`.
- Fixed `192x208` cell size.
- Fixed pet states: `idle`, `running-right`, `running-left`, `waving`, `jumping`, `failed`, `waiting`, `running`, `review`.
- Codex digital-pet pixel-adjacent style as default.
- Requirement that row-strip generation must use subagents.

## New General Character Scope

The rewritten skill supports:

- model sheets
- turnarounds
- expression sheets
- outfit and prop variant sheets
- animation pose sheets
- sprite row strips
- assembled sprite atlases
- AI video consistency reference plates
- characters in any visual style, not only pixel mascots

## Behavioral Changes

The original skill is deliberately strict because the Codex pet runtime requires one exact atlas. The generalized skill is strict only when the target requires it.

- If the output is a concept sheet, prioritize clear design and identity.
- If the output is an AI video reference, prioritize stable identity, camera clarity, and clean plates.
- If the output is a game sprite, require geometry, transparency, frame counts, manifest, and visual QA.
- If the user gives no target, produce a reusable character sheet plus a clean animation sheet, not a Codex pet package.

## Subagent Policy

The original `hatch-pet` skill requires subagents after base generation. The generalized skill does not require subagents by default because a skill should not assume parallel-agent availability for every environment.

Use subagents only when the active environment and user request allow it. Keep parent ownership of manifests, selected outputs, and final packaging.

## Script Migration Notes

The copied source scripts in `source/hatch-pet/scripts/` are useful evidence of the deterministic pipeline, but most are still pet-specific. The research root now includes a first generalized script layer in `scripts/` that applies these migrations:

- `pet_request.json` -> `request.json`
- `imagegen-jobs.json` -> `generation-jobs.json`
- `pet_name` -> `character_name`
- fixed animation rows -> configurable row/action schema
- Codex pet atlas constants -> target geometry from request or manifest
- package output -> project-local package or engine-specific output

The root scripts cover run preparation, job status, imagegen result recording, contact sheets, deterministic validation, targeted repair queueing, and final summaries. They do not yet fully replace the pet atlas compositor for every game engine. Engine-specific packing should be added as a separate script once the target runtime contract is known.

## Current Root Script Coverage

| Root script | Replaces hatch-pet idea | Current status |
| --- | --- | --- |
| `prepare_character_run.py` | `prepare_pet_run.py` | Generalized for character ids, output modes, references, configurable actions, and layout guides. |
| `character_job_status.py` | `pet_job_status.py` | Generalized for `generation-jobs.json`. |
| `record_imagegen_result.py` | `record_imagegen_result.py` | Generalized for character runs and optional `transparent_output_path` derivatives. |
| `make_contact_sheet.py` | `make_contact_sheet.py` | Generalized for completed animation row jobs. |
| `validate_character_run.py` | `validate_atlas.py` plus review checks | General deterministic file/image/alpha validation, not engine-specific atlas validation. |
| `queue_character_repairs.py` | `queue_pet_repairs.py` | Generalized job reopening for targeted repairs. |
| `finalize_character_run.py` | `finalize_pet_run.py` | Runs validation/contact sheet and writes `qa/run-summary.json`. |

## Verified Demo

`runs/vidtory-spark-demo/` was created after the root scripts were added. It validates the generalized flow:

1. `prepare_character_run.py` created request, prompts, copied references, layout guides, and job queue.
2. `$imagegen` generated a branded Vidtory mascot canonical base and model sheet.
3. `record_imagegen_result.py` recorded selected original `$imagegen` files.
4. `$imagegen` generated a combined visual sprite sheet for quick review.
5. The imagegen chroma-key helper produced alpha outputs under `processed/`.
6. `validate_character_run.py` and `finalize_character_run.py` produced `qa/review.json` and `qa/run-summary.json`.

The demo is not an engine-grade packed atlas. It is a visual proof that the generalized skill and script contract work end to end.
