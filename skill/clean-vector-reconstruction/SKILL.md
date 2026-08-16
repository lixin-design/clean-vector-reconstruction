---
name: clean-vector-reconstruction
description: Reconstruct flat, semi-flat, and geometric color-block raster illustrations as clean, editable layered and plain SVG artwork for Adobe Illustrator. Use for raster-to-SVG reconstruction, clean vectorization, editable illustration tracing, geometric SVG rebuilding, semantic color blocks, repeated elements, or native gradients. Do not use for photography, watercolor, oil painting, dense natural textures, missing or unclear references, or pixel-perfect conversion that sacrifices editability.
---

# Clean Vector Reconstruction

Rebuild supported raster illustrations as semantic SVG geometry. Preserve design relationships while prioritizing clean paths, editable fills and gradients, concise groups, and verifiable evidence.

## Apply hard gates

Before writing anything:

1. Confirm the real reference file, output directory, version, target editor, and ownership/publication permission.
2. Stop if the reference is missing, unclear, a preview/difference image, or outside the permitted scope.
3. Stop if required permissions are missing or a private-material boundary would be crossed.
4. Never install tools or dependencies without explicit user permission.
5. Never overwrite a reference, prior output, report, or experiment version.
6. Keep all case-specific reconstruction code and coordinates in the case workspace, not inside this reusable Skill.
7. Prefer project-relative paths; derive paths from script locations when practical.

Read [privacy-and-limitations.md](references/privacy-and-limitations.md) whenever materials may be private, publication is requested, permissions are unclear, or the input may be outside validated scope.

## Select a mode

Choose only after inspecting the image:

- Use `geometric-flat` for aligned blocks, regular geometry, arcs, lines, repeated units, and limited gradients.
- Use `clean-flat` for semantic subjects made from complete color regions and controlled free curves.
- Treat `line-art`, `logo`, and `high-fidelity` as experimental until independently validated for the task context.
- Stop or narrow the task for photography, painterly media, dense texture, highly realistic lighting, or incompatible fidelity requirements.

Read [reconstruction-modes.md](references/reconstruction-modes.md) when selecting, questioning, switching, or rejecting a mode.

## Run the workflow

### 1. Preflight

- Inspect available local tools without changing the environment.
- Run [`scripts/check_environment.py`](scripts/check_environment.py) with Python when renderer or library availability matters.
- Record executable paths, versions, intended use, optional gaps, and any blocker. Use `--path-mode relative` or `basename` for any report that may be shared.
- Continue without nonessential tools when a safe alternative exists.

### 2. Analyze before drawing

Document:

- canvas dimensions, aspect ratio, color mode, alpha, and SVG `viewBox`;
- semantic regions, major objects, gradients, lines, repeated elements, and occlusion order;
- key landmarks such as major divisions, intersections, centers, endpoints, baselines, and bounding boxes;
- shared horizontal/vertical boundaries and coordinates;
- whether repeated elements are exact, mirrored, scaled, rotated, or intentionally varied;
- proposed short English group IDs;
- estimated object/path complexity.

Read [reconstruction-rules.md](references/reconstruction-rules.md) before constructing geometry, curves, gradients, repeated elements, shared boundaries, or key landmarks.

### 3. Reconstruct semantically

- Use `<rect>`, `<circle>`, `<ellipse>`, `<line>`, and simple paths for regular geometry.
- Represent each meaningful color block with one object or a few necessary objects.
- Rebuild free curves with few smooth anchors while preserving distinctive asymmetry.
- Use native `<linearGradient>` or `<radialGradient>` elements for real gradients.
- Give adjacent shapes intended to meet the same boundary the same coordinate when practical.
- Preserve intentional variation; do not regularize merely to make spacing mathematically uniform.
- Maintain correct occlusion and independently selectable major objects.
- Use short, readable English group names, preferably one to three words.

Never use whole-image auto-tracing as final artwork. Use tracing only for measurement, masks, candidate contours, or initial colors, then rebuild and clean the result.

Never embed or link raster content in a final SVG: no `<image>`, `data:image`, base64 bitmap data, PNG, JPG, or JPEG references.

### 4. Produce versioned deliverables

Create at least:

- a layered SVG with useful semantic/layer metadata;
- a plain SVG prioritizing standard structure and Illustrator compatibility;
- a same-size preview;
- an equal-opacity overlay;
- a difference image;
- automatic reports and retained case-specific scripts.

Use a new version identifier for every revision. Keep the reference, prompt, prior versions, reports, human review, conclusion, and revision notes.

Use [case-brief-template.md](assets/templates/case-brief-template.md) to define a new case. Use [automatic-report-template.md](assets/templates/automatic-report-template.md) for objective evidence.

### 5. Validate automatically

For each final SVG:

1. Run [`scripts/audit_svg.py`](scripts/audit_svg.py) with Python for every final SVG.
2. Stop and fix the SVG if the audit finds raster content, unsafe external resources, an invalid root, or an unreliable canvas. Do not use rendering to legitimize a failed audit.
3. Run [`scripts/render_compare.py`](scripts/render_compare.py) only after the audit passes and when a reference and local renderer are available.
4. Stop and fix a material SVG/reference aspect-ratio mismatch. An explicitly allowed diagnostic mismatch may be distorted and must not be used as normal positional-fidelity evidence.
5. Confirm both SVG variants parse, render at correct dimensions, and remain visually consistent. Never use forced stretching to manufacture apparent alignment.
6. Classify visible differences; do not treat every bright difference-map pixel as equally serious.
7. Treat structural heuristics, SSIM, PSNR, MAE, RMSE, and successful rendering only as diagnostic evidence—not proof of Illustrator editability or design quality.
8. Use `--path-mode relative` or `basename` and inspect reports before sharing or publication.

Read [validation-and-grading.md](references/validation-and-grading.md) before auditing, grading, revising, or declaring completion.

### 6. Hand off for human review

- Leave Adobe Illustrator review to a real user or reviewer.
- Never fabricate scores, editing behavior, compatibility, or a final human grade.
- Provide [human-review-template.md](assets/templates/human-review-template.md) for the reviewer.
- Report the result as ready for human review until completed evidence exists.

After real review, assign Pass, Conditional pass, or Fail using both automatic and human evidence. Document every easy-to-fix difference; do not silently ignore it.

## Report completion

Report:

- selected mode and rationale;
- files created and their versions;
- element/object/path and gradient counts;
- raster-reference count;
- render and dimension results;
- warning-threshold status;
- classified known differences and limitations;
- whether automatic checks passed;
- whether the work is only ready for human review or has a real human result.

Do not claim full success when required checks fail, human review is missing, or the input exceeds validated scope.
