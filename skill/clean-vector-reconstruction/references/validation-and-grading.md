# Validation and Grading

Use this reference before auditing, grading, revising, or declaring completion.

## Required evidence

Retain for each version:

- reference metadata and permission status;
- execution prompt/case brief;
- layered and plain SVG files;
- same-size preview, equal-opacity overlay, and difference image;
- a 3–8 item critical-region inventory and region-level preview, overlay, difference, and metrics evidence;
- case-specific scripts;
- environment, reconstruction, SVG audit, fragment, and render reports;
- real human-review record;
- conclusion and revision notes.

Never overwrite prior evidence.

## Automatic checks

Verify objectively:

- XML parsing, `width`, `height`, and `viewBox`;
- a real `<svg>` root and a reliably measurable positive canvas;
- counts of path, rect, circle, ellipse, line, polyline, polygon, group, gradients, image, use, symbol, foreignObject, text, and total drawables;
- absence of `<image>`, `data:image`, base64 bitmap data, external PNG/JPG/JPEG links, `foreignObject`, and unsafe external resource references;
- obvious unclosed filled paths, degenerate objects, very short/tiny objects, duplicates, overlap candidates, color proliferation, and fragmented groups;
- successful rendering of layered and plain SVG at correct dimensions;
- visual consistency of both SVG variants;
- rough alignment of major blocks, boundaries, endpoints, centers, bounding boxes, and repeated spacing.
- defined, used, unused, missing, and duplicate gradient IDs when gradients matter;
- representation-semantic consistency and mapped SVG objects/groups for every critical region.
- a valid required object-family inventory with reconstructed counts inside authored ranges;
- repeated-detail retention and mandatory/optional simplification records;
- structural full-canvas background evidence plus rendered alpha coverage for layered and plain variants;
- reference/render transparent-pixel counts, unexpected-gap regions, and declared transparency intent.
- a valid authored geometry inventory plus reconstruction-side named coordinate/relationship report;
- mandatory landmark tolerance, relation, plane child-orientation/scale, repeated-layout, and critical-contour landmark results.
- when applicable, one fixed reference-grounded boundary config, its resolved reference-only thresholds, global/region bidirectional distances, tolerance precision/recall/F1, boundary counts, and mismatch maps.

Use metrics only as diagnostics. Rendering success or a favorable SSIM, PSNR, MAE, or RMSE does not prove design fidelity or editability.

Review every critical region separately. Global metrics and a strong whole-image impression cannot override a missing distinctive motif, failed critical contour, wrong representation semantic, or major local landmark error.

Report `semantic completeness pass`, `internal geometry consistency pass`, and `reference-grounded boundary evidence` separately. Required relation failure, mandatory landmark deviation beyond authored tolerance, wrong-plane repeated elements, or unresolved critical-contour landmarks block automatic readiness. Clean paths cannot compensate for wrong geometry.

Internal geometry evidence answers whether the reconstruction matches the case-authored geometry contract. Reference-grounded evidence answers how rendered boundaries correspond directly to the current raster reference. Either may expose a failure the other misses. Do not average them into one score, and do not call a candidate visually validated merely because the internal contract passes.

An automatic structural pass is not a visual-regression pass. Clean XML, safe resources, valid gradients, successful rendering, and editable-looking groups can coexist with missing semantic content or degraded composition. Keep the two conclusions separate in every report.

For regression boundary evidence, use the identical renderer, viewport, raster dimensions, background handling, color mode, downsampling, regions, method config, resolved thresholds, and tolerances for every candidate. If boundary metrics and human judgment disagree, retain the fixed evidence, report the disagreement, inspect the affected regions and other gates, and defer the visual conclusion to real human review. No single boundary metric, SSIM-family metric, internal geometry result, or human subscore overrides all other evidence.

## Complex-scene completeness gate

Before reporting `Ready for human Illustrator review`, require:

- every required object family present;
- every repeated-family count inside its authored exact count or bounded range;
- mandatory details retained and generic substitutions documented as failures;
- no meaningful detail deletion across multiple regions;
- expected background and foreground coverage;
- no unexpected rendered transparency above the declared safe threshold;
- matching completeness and alpha results for layered and plain variants.

A missing required family or a blocking accidental transparency gap is an automatic blocker. A count decrease is not favorable evidence by itself; interpret it as a possible deletion regression until the inventory, region evidence, and human comparison establish completeness.

## Spatial fidelity readiness gate

`Ready for human Illustrator regression review` requires all relevant automatic gates:

1. structural validity and safe resources;
2. semantic completeness;
3. coverage and rendered alpha;
4. valid gradient references;
5. a passing mandatory spatial geometry inventory evaluated against the reconstruction-side report.

Any unresolved or failed mandatory spatial constraint blocks readiness. Use `Automatic regression blocked — spatial fidelity gate failed`. Schema validity by itself is not a spatial pass, and no automatic result is a substitute for real visual review.

A gradient definition proves only that a definition exists. Even a referenced definition does not prove gradient fidelity. Human review must compare placement, direction, colors, stops, transition extent, opacity, and correspondence with the reference.

Run the SVG/resource audit before rendering. Resolve raster, `foreignObject`, and unsafe external-resource warnings before final grading; rendering must never be used to legitimize a failed resource audit.

Treat an SVG/reference aspect-ratio mismatch as a canvas problem, not a difference-map detail. Stop and repair it by default. If a mismatch is explicitly allowed for diagnosis, label the render as potentially distorted and never use the stretched comparison as normal positional-fidelity evidence.

## Difference classification

Classify each important difference:

- **Structural**: wrong shape relationship, topology, or occlusion.
- **Positional**: correct object exists but is displaced.
- **Color**: main fill/stroke color differs.
- **Gradient**: direction, stops, or transition extent differs.
- **Edge anti-aliasing**: raster/vector edge-rendering difference only.
- **Acceptable regularization**: noise removal or restoration of intended regular geometry.
- **Missing element**: meaningful source element absent.
- **Extra element**: output adds unsupported design content.

Prioritize structural, missing, and major positional differences over normal edge anti-aliasing.

## Illustrator human review

A real user/reviewer must score each item from 1 to 5:

1. visual similarity;
2. edge and curve quality;
3. object editability;
4. gradient editability;
5. layer structure;
6. anchor-point quality;
7. plain SVG compatibility.

Record observations, critical issues, noncritical differences, easy-to-fix differences, and final comments. Codex must not fill this review or infer Illustrator behavior.

`Ready for human Illustrator review` means the automatic resource, canvas, rendering, variant-consistency, critical-region-evidence, and applicable gradient-usage prerequisites passed. It does not mean visual fidelity, editability, or the final grade passed.

## Easy-to-fix differences

Classify a difference as easy to fix only when:

- the correct object already exists;
- moving, scaling, recoloring, adjusting a gradient, or editing a few anchors resolves it;
- the overall composition or primary subject need not be rebuilt;
- it does not reveal failure of the core method.
- it is localized rather than one of several coupled region failures.

Document it even when nonblocking.

Do not describe multi-region deviations as minor or easy to fix without explicit human evidence. Count affected critical regions and distinguish an isolated object edit from a coordinated multi-region revision.

## Result grades

### Pass

- No critical issue exists.
- Automatic checks pass.
- Human review confirms strong usability.
- Only negligible differences remain.
- No protocol-level revision is needed.

### Conditional pass

- The core workflow succeeds and the SVG is clean/editable.
- Only minor position, spacing, naming, curve, or gradient changes remain.
- Remaining issues are easy to fix.
- A light workflow/protocol revision may be useful.

### Conditional pass — borderline

Use when the SVG remains usable and editable but one serious fidelity concern or several critical regions require coordinated revision; the result is close to Fail and must not be presented as a strong success. Require a versioned revision and new automatic plus human review before promotion.

### Fail

Use when composition or primary shapes are seriously wrong; meaningful elements are missing; raster content is embedded; tracing fragments remain; editability or gradients fail; Illustrator/plain SVG compatibility fails; shared boundaries are materially wrong; or major rebuilding is required.

Use `Fail — visual fidelity` when the files remain technically structured or editable but missing families, broad positional errors, coverage gaps, or multi-region deletion make the visual result unsuitable without major reconstruction.

## Revision order

1. Composition and major positions.
2. Primary contours and occlusion.
3. Landmarks and shared boundaries.
4. Regular geometry.
5. Complete color blocks and fragment removal.
6. Curves and anchor reduction.
7. Gradients.
8. Repeated elements and intentional variation.
9. Layer/group names.
10. Full automatic recheck.
11. New real human review.

Do not improve similarity only by adding paths. Never add dense tracing fragments, decorative edges, or delete supported detail merely to improve boundary precision, recall, or F1.

## Regression comparison

After a Skill revision, keep the prior evidence unchanged and create a new versioned regression case. Compare the same critical-region inventory, representation semantics, gradient usage, global outputs, editability evidence, and human-review categories. Record improvements, regressions, and unchanged limitations. Do not claim the Skill revision improved quality until the regression evidence supports it.

Assign exactly one regression category:

- `Pass — clear improvement`;
- `Conditional pass`;
- `No improvement`;
- `Regression`.

Treat meaningful deletion across multiple regions, a newly missing required family, or a new coverage gap as a regression indicator even when object count, path count, or global metrics decrease.

Use `No sufficient visual improvement` when the new output preserves technical validity or completeness but does not show a meaningful visual recovery in spatial relationships, perspective consistency, contour landmarks, or overall composition. Do not promote a version merely because automatic structure passes.
