# QA Rubric

Do not accept a character sheet or animation sheet until the checks relevant to its target use pass.

## Character Identity

- Same character across base, turnaround, expressions, variants, and animation frames.
- Same species/body type, silhouette, height relationship, head shape, face, hair/ears/horns/helmet, and costume.
- Same palette, material treatment, line/rendering style, and prop design.
- Side-specific markings, accessories, scars, readable symbols, and handed props stay on the correct side unless intentionally mirrored.
- No accidental extra character, duplicate identity, or character fusion.

## Character Sheet Quality

- Full-body views are complete and not clipped unless a crop sheet was requested.
- Turnaround views use consistent scale, camera height, and proportions.
- Expression sheets vary expression without changing identity.
- Outfit/prop sheets change only the requested variable.
- The sheet is clean enough to act as a production reference, not a poster or narrative scene.
- Generated text, labels, or annotations are not relied on unless manually verified.

## Animation Sheet Quality

- Each row has the requested action, direction, and frame count.
- Frames are separated and do not overlap neighboring slots.
- Each pose is complete and inside its frame safe area.
- Motion reads through pose changes, not through forbidden effects.
- Looping rows can loop without an obvious visual pop.
- Non-looping rows include clear anticipation, action, and settle when appropriate.
- Frames are not repeated copies, small transforms, or crops from one static pose.

## Geometry And Transparency

- Output dimensions and cell sizes match user or engine requirements when specified.
- Transparent outputs have a real alpha channel and transparent empty regions.
- No visible chroma-key fringe remains around the character.
- No background shadows, floor patches, glows, dust, smears, or other effects survive as accidental artifacts.
- Cell padding is sufficient for hair, ears, tails, weapons, props, and squash/stretch.
- If a packed atlas or sprite sheet is required, the manifest records exact row, column, frame, and duration data.

## Prompt And Manifest Integrity

- The canonical base prompt, sheet prompts, row prompts, selected source images, and final output paths are recorded.
- `generation-jobs.json` records the original `$imagegen` source path for every completed visual job.
- If alpha cleanup was performed, the job records `transparent_output_path` and the alpha file exists.
- Reference image roles are recorded.
- Manifest states known limitations instead of implying unsupported certainty.
- Labels and metadata are stored in machine-readable form, not only inside generated pixels.
- Any local deterministic processing is reproducible from recorded paths and settings.

## Deterministic QA Scripts

Use the bundled scripts as the baseline machine check:

- `validate_character_run.py` checks that completed jobs have readable images, animation rows have plausible frame divisibility, and transparent jobs point to alpha output when available.
- `make_contact_sheet.py` creates a visual review sheet for completed row jobs.
- `finalize_character_run.py` writes `qa/run-summary.json` with request, manifest, generation jobs, and QA logs.

Script success is necessary but not sufficient. The final decision must still include visual review for identity, frame quality, copied guide marks, and generated text artifacts.

## Repair Triggers

Repair the smallest failing scope when any of these appear:

- character identity drift
- wrong or missing required prop/costume/marking
- different proportions between panels
- wrong view or missing view in a turnaround
- expression changes face structure
- repeated animation frames
- frame count mismatch
- cropped limbs, ears, tail, weapon, hair, or prop
- visible grid/guide copied into output
- generated text artifacts
- opaque or dirty background in transparent-target outputs
- chroma-key color inside the character after extraction
- speed lines, dust, shadows, glows, or detached effects in game-ready rows

Repair order:

1. Single bad frame or panel if separable.
2. One animation row or sheet section.
3. Character sheet only.
4. Canonical base only when the identity source is wrong.
5. Full regeneration only when the visual direction is broadly unusable.

## Acceptance Summary

A production run is acceptable when:

- canonical base exists
- requested sheets exist
- identity is consistent
- geometry and transparency match target requirements
- contact sheet or preview exists for multi-frame outputs when practical
- manifest records source, prompt, output, and QA state
- unresolved limitations are explicit
- `qa/review.json` and `qa/run-summary.json` exist for scripted runs
