# Validation and Grading

Use this reference before auditing, grading, revising, or declaring completion.

## Required evidence

Retain for each version:

- reference metadata and permission status;
- execution prompt/case brief;
- layered and plain SVG files;
- same-size preview, equal-opacity overlay, and difference image;
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

Use metrics only as diagnostics. Rendering success or a favorable SSIM, PSNR, MAE, or RMSE does not prove design fidelity or editability.

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

## Easy-to-fix differences

Classify a difference as easy to fix only when:

- the correct object already exists;
- moving, scaling, recoloring, adjusting a gradient, or editing a few anchors resolves it;
- the overall composition or primary subject need not be rebuilt;
- it does not reveal failure of the core method.

Document it even when nonblocking.

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

### Fail

Use when composition or primary shapes are seriously wrong; meaningful elements are missing; raster content is embedded; tracing fragments remain; editability or gradients fail; Illustrator/plain SVG compatibility fails; shared boundaries are materially wrong; or major rebuilding is required.

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

Do not improve similarity only by adding paths.
