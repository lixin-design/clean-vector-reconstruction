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
- a scene complexity profile with `low`, `medium`, or `high` semantic density; this classification does not create a new reconstruction mode;
- semantic regions, major objects, gradients, lines, repeated elements, and occlusion order;
- 3–8 critical regions in a critical-region inventory;
- whether reference-grounded boundary validation is applicable, why, its critical boundary regions, and its limitations;
- required object families per region, exact repeated-detail counts or justified bounded ranges, and the expected minimum semantic completeness;
- mandatory details, optional simplifications, expected full-canvas coverage, and whether reference transparency is intentional;
- each critical region's distinctive local motifs, critical contours, landmarks, and representation semantics;
- key landmarks such as major divisions, intersections, centers, endpoints, baselines, and bounding boxes;
- shared horizontal/vertical boundaries and coordinates;
- a case-authored spatial landmark inventory with named coordinates, roles, tolerances, and mandatory status;
- relational constraints for alignment, ordering, offsets, attachment, overlap, containment, clipping, and shared baselines;
- perspective-aware planar groups with boundary anchors, dominant directions, child orientation, and visible scale progression;
- ordered start/end/turning/intersection/clip landmarks for every critical contour;
- whether repeated elements are exact, mirrored, scaled, rotated, or intentionally varied;
- one primary mode plus any justified region-specific construction strategies;
- proposed short English group IDs;
- estimated object/path complexity.

Read [reconstruction-rules.md](references/reconstruction-rules.md) before constructing geometry, curves, gradients, repeated elements, shared boundaries, or key landmarks.
Read [local-fidelity.md](references/local-fidelity.md) before selecting critical regions, recording representation semantics, choosing region-specific strategies, or judging local differences.
Read [complex-scene-retention.md](references/complex-scene-retention.md) before simplifying a medium/high-density scene, defining required families, auditing repeated-detail retention, checking coverage, or declaring automatic readiness.
Read [spatial-fidelity.md](references/spatial-fidelity.md) before placing major regions, authoring geometry constraints, constructing repeated elements on a plane, rebuilding critical contours, or declaring spatial readiness.
Read [reference-grounded-validation.md](references/reference-grounded-validation.md) when direct boundary fidelity matters, clean color-block edges are available, critical contours/planes/layout are important, or a regression needs evidence independent of authored geometry.

### 3. Reconstruct semantically

Construct in geometry-first order: canvas/global layout, major region bounds, planes/shared axes, major landmarks, repeated elements on planes, critical contours, local motifs, then decorative details. This order does not override semantic completeness or representation semantics.

- Use `<rect>`, `<circle>`, `<ellipse>`, `<line>`, and simple paths for regular geometry.
- Represent each meaningful color block with one object or a few necessary objects.
- Rebuild free curves with few smooth anchors while preserving distinctive asymmetry.
- Use native `<linearGradient>` or `<radialGradient>` elements for real gradients.
- Preserve important fill, stroke, fill-plus-stroke, gradient, and transparency semantics unless a documented reason requires a change.
- Reconstruct distinctive local motifs from their recorded relationships; never replace them with a generic motif merely because the substitute is cleaner or easier.
- Give adjacent shapes intended to meet the same boundary the same coordinate when practical.
- Preserve intentional variation; do not regularize merely to make spacing mathematically uniform.
- Retain every mandatory family and keep required repeated counts within their authored ranges. Never delete visible repeated details solely to reduce object count or replace distinct members with one generic template.
- Anchor local motifs to authored spatial landmarks. Reuse shared coordinates and plane-relative construction values for aligned or perspective-related objects.
- Do not rebuild children on a visibly oblique plane as independent axis-aligned objects. Preserve their shared orientation, relative scaling, ordering, and spacing system.
- Give validation-bearing semantic groups, planes, and landmark-bearing objects stable public-safe SVG IDs or data attributes when appropriate. Do not tag every minor path or expose private identifiers.
- Cover the full canvas when the reference is declared opaque; prevent transparent seams between intended adjoining background and foreground shapes.
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
- reference-grounded boundary maps, mismatch visualizations, resolved configuration, and global/region metrics when applicable.

Retain the scene complexity profile and a validated case-authored required object-family JSON inventory with the versioned evidence.
Retain a validated case-authored geometry inventory and a reconstruction-side geometry report mapping expected names to actual coordinates, relations, plane metadata, and contour landmarks.

Use a new version identifier for every revision. Keep the reference, prompt, prior versions, reports, human review, conclusion, and revision notes.

Use [case-brief-template.md](assets/templates/case-brief-template.md) to define a new case. Use [automatic-report-template.md](assets/templates/automatic-report-template.md) for objective evidence.

### 5. Validate automatically

For each final SVG:

1. Run [`scripts/audit_svg.py`](scripts/audit_svg.py) with Python for every final SVG.
2. Record the case-authored transparency intent and inspect the structural background-coverage result. Stop and fix raster content, unsafe external resources, an invalid root, or an unreliable canvas. Structural coverage is heuristic and never replaces rendered alpha evidence.
3. When gradients matter, audit defined, used, unused, missing, and duplicate gradient IDs. Actual use still does not prove gradient fidelity.
4. Validate the case-authored inventory with [`scripts/validate_object_inventory.py`](scripts/validate_object_inventory.py). Do not infer families from images. Missing required families or out-of-range repeated counts block automatic readiness.
5. Validate the authored spatial contract with [`scripts/validate_geometry_inventory.py`](scripts/validate_geometry_inventory.py), then pass the reconstruction-side report with `--actual`. Missing or out-of-tolerance mandatory landmarks, failed relations, wrong-plane child metadata, or failed critical-contour landmarks block spatial readiness. The validator does not infer geometry from artwork or SVG.
6. Run [`scripts/render_compare.py`](scripts/render_compare.py) only after the structural audit passes and when a reference and local renderer are available. Use `--regions-file` for critical regions and `--check-alpha-coverage`; add `--expected-opaque-reference` for a fully opaque reference.
7. When reference-grounded validation is applicable, run [`scripts/compare_boundaries.py`](scripts/compare_boundaries.py) on the normalized reference and candidate rasters with one pre-authored config. Resolve thresholds from the reference once, apply the same resolved config to both inputs, retain global and critical-region bidirectional distances plus precision/recall/F1, and never introduce a universal F1 pass threshold.
8. Stop and fix a material SVG/reference aspect-ratio mismatch, unexpected transparency above the declared threshold, or failed expected background/foreground coverage. An explicitly allowed diagnostic mismatch may be distorted and must not be used as normal positional-fidelity evidence.
9. Confirm both SVG variants parse, render at correct dimensions, remain visually consistent, preserve required families, agree on alpha coverage, and map their validation-bearing geometry to the same authored contract. Never use forced stretching to manufacture apparent alignment.
10. Validate the whole composition and every critical region. Global metrics, successful structure, or a lower object count cannot excuse a missing family, failed landmark/relation, failed critical region, or multi-region detail deletion.
11. Classify visible differences and interpret object-count decreases conservatively. Do not treat every bright difference-map pixel as equally serious.
12. Treat structural heuristics, SSIM, PSNR, MAE, RMSE, boundary distances, boundary precision/recall/F1, and successful rendering only as diagnostic evidence—not proof of Illustrator editability, semantic correctness, visual fidelity, or regression improvement.
13. Use `--path-mode relative` or `basename` and inspect reports before sharing or publication.

Read [validation-and-grading.md](references/validation-and-grading.md) before auditing, grading, revising, or declaring completion.

### 6. Run a bounded targeted correction loop

When boundary evidence identifies material local mismatches, run at most two correction iterations. Keep the renderer, dimensions, downsampling, regions, method config, resolved thresholds, and tolerances unchanged. Correct only the largest 3–5 critical mismatch regions, retain every iteration, and report each region as improved, regressed, unchanged, or mixed.

Never add dense trace fragments or unsupported decoration, delete required detail to improve precision, or claim success from one direction, tolerance, percentile, or F1 alone. Recheck semantic completeness, internal geometry, path cleanliness, boundary counts, and mismatch maps after every correction.

### 7. Hand off for human review

- Leave Adobe Illustrator review to a real user or reviewer.
- Never fabricate scores, editing behavior, compatibility, or a final human grade.
- Provide [human-review-template.md](assets/templates/human-review-template.md) for the reviewer.
- Ask the reviewer whether mismatch maps correspond to visible problems, metric-guided corrections improved the drawing, or score gains damaged path cleanliness.
- Report `Ready for human Illustrator regression review` only after structural, semantic-completeness, coverage/alpha, gradient-reference, and mandatory spatial-geometry gates pass. Missing required families, blocking transparency gaps, multi-region detail deletion, or unresolved/failed mandatory geometry prevent this status.
- If mandatory authored geometry fails, report exactly: `Automatic regression blocked — spatial fidelity gate failed`.

After real review, assign Pass, Conditional pass, Conditional pass — borderline, or Fail using both automatic and human evidence. Do not call multi-region deviations minor or easy to fix without explicit human evidence. Document every claimed easy-to-fix difference.

After revising this Skill, run its validation, synthetic coverage/inventory fixtures, and safety tests. Then perform separately versioned complex-scene regression tests before claiming the revision improves reconstruction quality.

## Report completion

Report:

- selected mode and rationale;
- files created and their versions;
- element/object/path and gradient counts;
- critical regions and region-level evidence;
- scene complexity profile, required/reconstructed/missing object families, and repeated-detail retention;
- landmark, relation, plane-group, repeated-layout, and critical-contour validation summaries plus every mandatory geometry failure;
- boundary-validation applicability, normalization, resolved-config integrity, global/region bidirectional metrics, precision/recall/F1, top mismatches, and correction-iteration results;
- reference opacity intent, full-canvas background/foreground coverage, transparent-pixel counts, unexpected-gap regions, and automatic-readiness blockers;
- defined, used, unused, missing, and duplicate gradient IDs when gradients matter;
- raster-reference count;
- render and dimension results;
- warning-threshold status;
- classified known differences and limitations;
- whether automatic checks passed;
- whether geometry readiness was evaluated and blocked;
- whether the work is only ready for human review or has a real human result.

Distinguish structural pass, semantic completeness, internal geometry consistency, reference-grounded boundary evidence, and human visual review. Do not claim full success when required checks fail, signals disagree without review, human review is missing, or the input exceeds validated scope.
