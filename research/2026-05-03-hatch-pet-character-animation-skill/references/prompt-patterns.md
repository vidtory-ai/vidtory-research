# Prompt Patterns

Use these patterns as starting points. Keep prompts specific, visual, and sheet-oriented. Do not add unrelated story, scenery, marketing, or decorative text.

## Canonical Base

```text
Create the canonical visual reference for this character.

Character identity:
- Name or slug: <name>
- Description: <description>
- Must preserve: <face, silhouette, costume, markings, props, colors>
- Personality signal: <personality>

Style:
- <target art style>
- <line/rendering/color constraints>

Composition:
- one full-body character only
- neutral standing pose
- clear front three-quarter view
- complete unclipped body
- generous padding around the character
- clean flat background suitable for reuse as a reference

Avoid:
- extra characters, scenery, UI, labels, watermarks, speech bubbles
- dramatic lighting that hides the design
- redesigning or omitting required details
```

## Turnaround / Model Sheet

```text
Create a clean character model sheet for the same character shown in the attached canonical base.

Identity lock:
- preserve the exact same character, proportions, face, palette, costume, markings, and props
- no redesigns and no alternate character

Sheet layout:
- one character repeated across clean panels
- full-body views: front, three-quarter front, side, three-quarter back, back
- consistent scale and camera height across views
- neutral pose for each view
- clean panel spacing, no scene

Style:
- match the canonical base style exactly
- consistent lighting and outline/rendering

Avoid:
- labels or text unless explicitly requested
- extra characters, scenery, shadows, watermarks, UI, speech bubbles
- cropped limbs, inconsistent height, different costume, changed markings
```

## Expression Sheet

```text
Create an expression sheet for the same character shown in the attached canonical base.

Identity lock:
- same face structure, head shape, hair/ears/horns/helmet, palette, and rendering style
- expressions vary; identity does not

Expressions:
- neutral
- happy
- surprised
- angry
- sad
- determined
- confused
- scared

Composition:
- head-and-shoulders or bust crops, consistent angle and scale
- clean grid with separated panels
- no labels or text unless requested
- flat neutral background

Avoid:
- changing age, species, costume, proportions, palette, or line style
- unreadable text, scenery, speech bubbles, duplicate identical faces
```

## Outfit Or Prop Variant Sheet

```text
Create a focused variant sheet for the same character shown in the attached canonical base.

Variant target:
- <outfit, prop, accessory, material, colorway, or detail>

Rules:
- only change the requested variant target
- preserve face, body type, proportions, expression language, palette relationship, and base style
- show enough of the character to understand how the variant fits
- include clean separated variants with consistent scale

Avoid:
- turning variants into different characters
- changing anatomy, face, age, species, or core silhouette
- cluttered background, text, UI, watermarks
```

## Animation Row Strip

```text
Create one animation row strip for the same character shown in the attached canonical base.

Action:
- Row id: <action-id>
- Frame count: <number>
- Direction: <left, right, front, back, in-place, or none>
- Looping: <yes/no>
- Motion notes: <anticipation, contact poses, settle, etc.>

Identity lock:
- preserve the same character, proportions, face, costume, markings, palette, props, and style
- no redesigns and no extra characters

Layout:
- <number> complete full-body frames in one horizontal row
- frames are evenly spaced and separated
- each pose stays inside its own frame slot with safe padding
- no visible grid, labels, frame numbers, borders, or construction marks
- flat background suitable for transparent cleanup if requested

Animation quality:
- each frame should be a distinct pose in the action cycle
- first and last frames should loop or transition according to the requested action
- show motion through body, limbs, cloth, hair, or prop pose changes

Avoid:
- repeated duplicate frames
- cropped body parts
- pose crossing into adjacent slot
- speed lines, dust, shadows, glows, afterimages, motion smears, floating icons
- text, UI, watermarks, scenery
```

## Transparent Sprite Prompt Add-On

Use this add-on when the output must become transparent through chroma-key removal:

```text
Use a perfectly flat solid <key-color> chroma-key background for background removal.
The background must be one uniform color with no shadows, gradients, texture, floor plane, reflections, or lighting variation.
Do not use <key-color> anywhere in the character, props, effects, highlights, or shadows.
Keep every character frame fully separated from the background with crisp edges and generous padding.
No cast shadow, no contact shadow, no glow, no transparent effects, no watermark, and no text.
```

## Combined Visual Sprite Sheet

Use this only for fast concept review or AI-video reference. For game-ready output, prefer separate row strip prompts and deterministic packing.

```text
Create one combined sprite sheet for the same character shown in the attached canonical base and character sheet.

Sheet structure:
- one single image
- <row-count> horizontal animation rows stacked vertically
- Row 1: <action>, <frame-count> full-body frames, <motion notes>
- Row 2: <action>, <frame-count> full-body frames, <motion notes>
- Row 3: <action>, <frame-count> full-body frames, <motion notes>

Identity lock:
- preserve the exact same character, proportions, face, costume, markings, palette, props, and style
- no redesigns, no alternate character, no extra character

Layout:
- full-body frames only
- even spacing in invisible frame slots
- each pose stays inside its own slot with safe padding
- no visible grid, labels, frame numbers, or text
- use a perfectly flat chroma-key background if alpha cleanup is needed

Animation quality:
- frames in each row should be distinct poses
- looping rows should have loop-friendly first and last frames
- show motion through body and limb pose changes

Avoid:
- repeated stills, copied frame transforms, cropped body parts, overlapping frames
- speed lines, dust, glows, shadows, afterimages, floating icons
- wordmarks, readable text, labels, watermarks, UI panels, speech bubbles
```

## AI Video Consistency Plate

```text
Create a clean AI video consistency reference plate for this character.

Identity lock:
- preserve the attached canonical character exactly
- prioritize stable silhouette, readable face, costume, markings, palette, and prop placement

Plate contents:
- one neutral full-body pose
- one action key pose relevant to <scene/use case>
- one close-up face reference
- optional side/back reference if requested

Style:
- match the target video style: <style>
- clean lighting, no extreme perspective, no heavy effects

Avoid:
- poster composition, cinematic background, text, logos, watermarks, extra characters
- changing costume, age, species, palette, or proportions
```
