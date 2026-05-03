---
name: character-sheet-animator
description: Create character model sheets, turnaround sheets, pose sheets, expression sheets, animation sheets, sprite sheets, and frame grids for any character from text or reference images. Use when the user wants consistent character design across front, side, back, three-quarter views, expressions, props, or animation frames for games, video, comics, apps, or AI video workflows. Delegates visual generation to $imagegen and uses deterministic tooling only for layout, validation, alpha cleanup, manifests, contact sheets, and packaging.
---

# Character Sheet Animator

## Overview

Create production-ready character sheets and animation sheets for any character: human, animal, creature, robot, mascot, object-character, brand avatar, game NPC, comic character, or video protagonist. The skill owns character identity planning, sheet layout, prompt planning, generation sequencing, frame/pose consistency, transparent-background handling, QA, repair, and packaging. It delegates visual generation to `$imagegen`.

This is a generalized rewrite of the pet-specific `hatch-pet` workflow. It keeps the reliable parts: canonical base art, grounded row generation, deterministic manifests, layout guides, contact sheets, visual QA, and smallest-scope repair. It removes the Codex digital-pet contract, fixed 8x9 atlas, `pet.json`, and built-in pet packaging requirements.

## Output Types

Use one or more of these outputs based on the user request:

- **Character sheet:** model sheet, turnaround, front/side/back/three-quarter views, expression sheet, outfit/prop variants, color palette, detail callouts.
- **Animation sheet:** pose sheet, frame grid, row strips, sprite sheet, motion studies, action cycles such as idle, walk, run, jump, attack, emote, lip sync, or custom actions.
- **AI video consistency pack:** clean reference plates for image-to-video or video-to-video tools, usually canonical base, turnarounds, expressions, key poses, and negative constraints.
- **Game-ready sprite package:** transparent sprite atlas plus manifest when the target engine, cell size, frame count, and row layout are specified or can be safely inferred.

If the user only says "character sheet and animation sheet", create both: a canonical character sheet first, then an animation sheet grounded by that canonical sheet.

## Generation Delegation

Use `$imagegen` for all normal visual generation.

Before generating base art, sheets, row strips, repairs, or transparent cutouts, load and follow:

```text
${CODEX_HOME:-$HOME/.codex}/skills/.system/imagegen/SKILL.md
```

Do not call the Image API directly for the normal path. Let `$imagegen` choose its built-in-first path and CLI fallback rules. If `$imagegen` says a fallback requires confirmation, ask the user before continuing.

When invoking `$imagegen`, pass this skill's prompt as the authoritative visual spec. Do not add unrelated hero-art, marketing, scene, product-shot, or decorative prompt augmentation. Character sheet prompts should stay layout-specific and identity-specific.

Use local deterministic tools only for non-creative work: preparing prompts, creating layout guides, copying selected `$imagegen` outputs, removing chroma-key backgrounds, splitting frames when geometry is explicit, composing final atlases, creating contact sheets, validating transparency/geometry, and writing manifests.

Hard boundary: do not create, draw, tile, warp, mirror, or synthesize character visuals with local Python/Pillow, SVG, canvas, HTML/CSS, or other code-native art as a substitute for `$imagegen`. Local transforms are allowed only when they are deterministic layout operations on already-generated visual outputs and are visually appropriate.

Bundled scripts are the deterministic run layer:

- `scripts/prepare_character_run.py`: create `request.json`, `generation-jobs.json`, prompts, copied references, and layout guides.
- `scripts/character_job_status.py`: list ready and blocked `$imagegen` jobs.
- `scripts/record_imagegen_result.py`: ingest selected original `$imagegen` outputs and update `manifest.json`.
- `scripts/make_contact_sheet.py`: render contact sheets for completed animation rows.
- `scripts/validate_character_run.py`: run deterministic file/image/alpha checks and write `qa/review.json`.
- `scripts/queue_character_repairs.py`: reopen the smallest failing job scope.
- `scripts/finalize_character_run.py`: run QA helpers and write `qa/run-summary.json`.

## First Decisions

Collect or infer these before generation:

- Character name or short slug.
- Character description and personality/function.
- Input references and their roles: identity reference, style reference, pose reference, costume reference, prop reference, layout guide, edit target.
- Intended use: concept design, AI video consistency, comic, game sprite, app mascot, animation planning, or engine-ready sprite atlas.
- Art style: pixel sprite, anime, cartoon, children's book, 3D look, flat vector-like, realistic, clay, paper cutout, etc.
- Sheet outputs: character sheet, expression sheet, turnaround, animation rows, sprite atlas, or all.
- Geometry constraints: canvas size, transparent background, cell size, columns, rows, frame count, padding, naming, engine format.

If the user omits details, choose conservative defaults:

- Generate a canonical base first.
- Use a clean neutral studio or flat chroma-key background, depending on whether transparency is needed.
- Avoid labels and text inside generated images unless explicitly requested, because generated text is unreliable.
- Make the character sheet a clean visual reference plate, and store labels/metadata in a sidecar manifest.
- For animation, generate row strips one action at a time rather than one giant sheet when consistency or exact frame counts matter.

## Identity Lock

Every run needs a canonical visual source of truth.

If the user provides references, generate or choose a clean canonical base image from them before making sheets. If no references exist, generate the base from text first. All later sheets and animation rows must use the canonical base and any approved references as grounding images whenever `$imagegen` supports image inputs.

Preserve these across every output:

- species/body type, height and proportions
- head shape, face, eyes, mouth, ears/hair/horns/helmet
- costume, markings, palette, material, outline/rendering style
- props, accessories, handedness, side-specific details
- personality signal and expression language

Treat identity drift as a failed generation even if the sheet is visually appealing.

## Character Sheet Rules

For model sheets and turnarounds:

- Keep one character only unless the user requests a lineup.
- Use complete, unclipped full-body poses unless a close-up sheet is requested.
- Keep scale consistent across views.
- Prefer neutral standing views for turnaround: front, three-quarter front, side, three-quarter back, back.
- For expression sheets, keep the head angle and lighting consistent; vary expression, not identity.
- For outfit or prop variants, change only the requested costume/prop region.
- Avoid scenery, dramatic lighting, shadows, extra characters, speech bubbles, UI panels, watermarks, fake labels, and unreadable annotations.
- Put textual labels in the manifest or README unless the user explicitly wants them inside the image.

For AI video workflows, create clean plates with strong silhouette, consistent camera angle, and minimal background. The sheet should help downstream tools preserve identity, not look like a poster.

## Animation Sheet Rules

For animation rows or sprite sheets:

- Define each row/action before generation: action id, frame count, direction, looping behavior, cell geometry, and notes.
- Generate row strips separately when exact rows matter. A single all-in-one sheet is acceptable only for loose visual exploration.
- Attach the canonical base and any pose/style references to each row job.
- Attach a layout guide when frame count, padding, or cell positions matter. The guide is construction-only; generated outputs must not include visible boxes, labels, borders, center marks, or guide colors.
- Keep every frame complete, separated, and inside its slot. No pose should cross into a neighboring frame slot.
- Show motion through body and limb pose changes. Avoid speed lines, motion arcs, afterimages, dust, shadows, floor marks, glow, aura, or detached effects unless the user specifically wants a stylized non-game sheet.
- Do not accept rows made of repeated copies, tiny transforms, or crops from one static image.
- Mirror a direction only when symmetry, markings, props, lighting, and handedness make mirroring visually correct. Otherwise regenerate the opposite direction.

When transparency is required, follow `$imagegen` transparent-image guidance: generate on a removable flat chroma-key background first, then remove the key locally and validate alpha. Ask before switching to a true native-transparency CLI fallback.

## Workflow

### 1. Prepare The Run

Create a project-local run folder unless the user names another destination:

```text
character-sheet-runs/<character-slug>/
├── request.json
├── generation-jobs.json
├── references/
├── prompts/
├── generated/
├── processed/
├── qa/
└── manifest.json
```

Write `request.json` with the character description, references, target outputs, style notes, geometry constraints, and avoid list. Write a `manifest.json` as outputs are selected.

Use the bundled script for deterministic setup:

```bash
SKILL_DIR=/absolute/path/to/character-sheet-animator
python "$SKILL_DIR/scripts/prepare_character_run.py" \
  --character-name "<Name>" \
  --description "<one sentence>" \
  --reference /absolute/path/to/reference.png \
  --output character-sheet,animation-sheet \
  --action idle:6:front:true:"breathing and blink" \
  --cell-width 512 \
  --cell-height 512
```

Then inspect ready jobs:

```bash
python "$SKILL_DIR/scripts/character_job_status.py" --run-dir /absolute/path/to/run
```

### 2. Generate Canonical Base

Generate or choose the canonical base image first. Save the selected source path and a local copy. This image becomes the identity reference for every later sheet or row.

Block progression if the base character is wrong, unclear, over-detailed for the target, missing essential props/markings, or unsuitable for downstream consistency.

After selecting the original `$imagegen` output, record it:

```bash
python "$SKILL_DIR/scripts/record_imagegen_result.py" \
  --run-dir /absolute/path/to/run \
  --job-id base \
  --source /absolute/path/to/$CODEX_HOME/generated_images/.../ig_*.png
```

### 3. Generate Character Sheet

Create the requested model sheet, turnaround, expression sheet, outfit sheet, prop sheet, or reference plate. For production use, prefer separate focused sheets over one crowded sheet.

Inspect for identity consistency, complete anatomy/silhouette, same proportions across views, and absence of accidental extra characters or unreadable labels.

### 4. Generate Animation Sheet

For each action row:

1. Write a row-specific prompt.
2. Include canonical base and relevant references.
3. Include a layout guide if exact geometry matters.
4. Generate with `$imagegen`.
5. Select the best original generated output.
6. Process alpha or split frames only after generation.
7. Validate row geometry and visual identity.

Generate important identity-check rows first, such as `idle` and one locomotion row. Continue only after those rows preserve the character.

Record each selected sheet or row with `record_imagegen_result.py`, using the job ids from `character_job_status.py`.

### 5. Assemble And Package

When the target is a game-ready sprite sheet, assemble the accepted rows into the requested atlas and write a manifest that records:

- character id and display name
- output file paths
- sheet types
- row ids, frame counts, durations if known
- cell size, columns, rows, padding, trim policy
- source prompt files and source image paths
- style and identity notes
- QA status and known limitations

For non-game character sheets, package the selected images plus manifest and prompt files. Do not force a sprite atlas when the user only needs design references.

Use the deterministic QA helpers:

```bash
python "$SKILL_DIR/scripts/make_contact_sheet.py" --run-dir /absolute/path/to/run
python "$SKILL_DIR/scripts/validate_character_run.py" --run-dir /absolute/path/to/run
python "$SKILL_DIR/scripts/finalize_character_run.py" --run-dir /absolute/path/to/run
```

If transparent assets were created by chroma-key removal, save them under `processed/` and add `transparent_output_path` to the matching entry in `generation-jobs.json`. The validator will check that alpha output while keeping the original generated RGB file recorded for provenance.

For quick concept validation, a combined all-in-one sprite sheet may be recorded as a `combined-animation-sprite-sheet` output. Mark it as a visual review artifact unless each row has been separately generated or split and packed under an explicit engine contract.

### 6. Repair

Repair the smallest failing scope:

1. one bad frame or crop
2. one animation row
3. one character-sheet panel
4. canonical base only if identity is fundamentally wrong

Use the canonical base, failing output, exact failure note, and the original prompt as repair context. Do not regenerate the whole package when a targeted repair is enough.

Queue repairs from QA or explicitly by job id:

```bash
python "$SKILL_DIR/scripts/queue_character_repairs.py" \
  --run-dir /absolute/path/to/run \
  --job-id row-idle \
  --reason "identity drift in frames 3-4"
```

## References

Load these only when needed:

- `references/sheet-contracts.md`: output modes, folder contract, manifest schema, and geometry defaults.
- `references/prompt-patterns.md`: prompt templates for base, character sheets, expression sheets, and animation rows.
- `references/qa-rubric.md`: acceptance criteria and repair triggers.
- `references/migration-from-hatch-pet.md`: what changed from the original `hatch-pet` skill and what was intentionally preserved.

The original unmodified `hatch-pet` source is archived separately under `source/hatch-pet/` in the research package that produced this rewrite.

## Rules

- `$imagegen` is the primary visual generation layer.
- Every generated sheet after the base must be grounded by the canonical base whenever image inputs are available.
- Do not redesign the character between sheets unless the user asks for variants.
- Do not let generated labels become the source of truth; store reliable labels in manifests.
- Do not substitute locally drawn or code-generated art for missing `$imagegen` outputs.
- Do not accept visually pleasing outputs that break identity, frame count, transparency, or target use.
- Do not preserve Codex pet-specific constraints unless the user explicitly asks for a Codex pet.
- Do not create `pet.json` or install into `${CODEX_HOME:-$HOME/.codex}/pets/` unless the user specifically requests a Codex pet package.

## Acceptance Criteria

- Canonical base exists and is visually approved by inspection.
- Character sheet preserves the same identity across all views, expressions, and variants.
- Animation sheet rows use the requested frame counts and actions.
- Frames are complete, separated, and not clipped.
- Transparent outputs have real alpha, transparent empty regions, and no visible chroma-key fringe.
- Manifest records prompts, references, source images, output paths, geometry, and QA notes.
- `generation-jobs.json` records original `$imagegen` source paths and any `transparent_output_path` derivatives.
- Contact sheet or preview is produced for any multi-frame animation output when practical.
- Remaining limitations are stated clearly instead of hidden.
