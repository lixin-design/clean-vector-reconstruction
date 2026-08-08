# Reconstruction Rules

Use this reference before drawing geometry, curves, gradients, repeated elements, shared boundaries, or key landmarks.

## Contents

1. Structural plan
2. Geometry and curves
3. Color blocks and gradients
4. Repeated elements and regularization
5. Mixed local strategies
6. Groups and complexity
7. Auto-tracing boundary

## 1. Structural plan

### Key landmarks

Record construction references before drawing:

- canvas edges and major divisions;
- important intersections;
- primary object bounding boxes;
- centers and radii of important circles or arcs;
- significant line endpoints;
- centerlines, baselines, and repeated-unit start/end positions.

Landmarks control composition. They are not Bézier anchor points.

Store validation-bearing landmarks in the case-authored geometry inventory. Reuse shared coordinates instead of separately approximating edges, baselines, centers, or intersections that are meant to coincide. Preserve proportional placement between major regions, not merely each object's isolated shape.

For each critical region, also record local extrema, contour endpoints, intersections, tangency intent, clipping points, and distances or alignments that control recognition. Link each critical contour to these landmarks before drawing.

### Shared boundaries

Identify common horizontal/vertical edges, endpoints, baselines, centers, and aligned intersections. When adjacent objects should meet exactly, reuse the same coordinate. After rendering, check for gaps, background leaks, accidental overlaps, and nearly aligned edges.

When the case brief expects an opaque result, provide an opaque full-canvas background and complete foreground coverage. Do not rely on clipping, masks, or overlapping near-matches to conceal uncovered canvas. Audit rendered alpha because structural inspection cannot prove that adjoining shapes leave no holes.

### Plane-relative geometry

Define each visibly oblique or perspective-affected plane from three or four boundary landmarks. Record its dominant edge directions and construct important children from shared plane-relative coordinates. Repeated children on the same plane must share its orientation, relative scaling, ordering, and spacing system. Do not turn them into unrelated axis-aligned objects.

### Occlusion

List major back-to-front relationships. Keep clipping and masks simple and justified. Do not hide structural mistakes behind complex clipping.

## 2. Geometry and curves

### Regular geometry

- Keep horizontal and vertical edges exact.
- Use `<rect>`, `<circle>`, `<ellipse>`, `<line>`, and `<polygon>` when they express the intended shape.
- Use consistent parameters for related arcs, radii, centers, and stroke widths.
- Use mirrors and shared construction values for true symmetry.
- Do not approximate an obvious regular shape with many path nodes.

### Free curves

- Preserve distinctive turns, asymmetry, silhouette, endpoint placement, curvature direction, and visual weight.
- Use the fewest anchors that maintain the intended contour.
- Keep joins continuous and handles smooth where the source is smooth.
- Do not replace a recognizable curve with a generic ellipse or arc.
- Compare the curve's bounding box, endpoints, key extrema, inflections, and nearby intersections against local landmarks.
- Do not accept a smooth, editable path when its critical curvature or clipping relationship is wrong.
- Preserve every authored critical-contour start, end, turning, extremum, intersection, and clipping landmark within its tolerance. Endpoint fidelity takes precedence over cosmetic path smoothness.

## 3. Color blocks and gradients

### Complete color blocks

Represent one meaningful visual region with one object or a few necessary objects. Merge variations caused by anti-aliasing, compression, one-pixel noise, or insignificant brightness changes. Keep intentional color separation.

Reject regions that become mosaics, oil-paint fragments, or large collections of near-identical colors.

### Edges

Keep primary edges continuous, smooth, and free of raster stair-steps. Reconstruct the design boundary rather than every transition pixel.

### Gradients

- Use `<linearGradient>` or `<radialGradient>` for real transitions.
- Preserve direction, main endpoint colors, important middle stops, transition extent, and brightness relationship.
- Keep gradients editable in Illustrator.
- Never simulate a gradient with many solid paths.
- Preserve whether an important object is a solid fill, stroke, fill plus stroke, linear gradient, radial gradient, or transparent element.
- Treat a change of representation semantics as a documented design deviation, not an automatic simplification.

## 4. Repeated elements and regularization

Classify a family before rebuilding it:

- exact repeat;
- mirror;
- rotation/translation;
- scaled variant;
- intentionally irregular;
- individually designed with shared visual language.

Reuse a base unit only where the design supports reuse. Keep meaningful differences in size, angle, spacing, silhouette, and rhythm.

Do not over-regularize:

- intentional asymmetry into symmetry;
- natural variation into identical copies;
- meaningful size differences into one size;
- distinctive curves into generic curves;
- designed spacing into mathematical uniformity.

If intent is uncertain, preserve the visible distinction and document the uncertainty.

Never replace a distinctive local motif with a generic symbol, stock contour, or regularized family merely because the substitute is concise. Preserve identity-bearing count, overlap, internal division, orientation, and variation.

Record exact required-family counts or justified bounded ranges before construction and recheck them after cleanup. Do not delete visible repeated members solely to reduce complexity. Do not replace distinct repeated members with one generic object when their differences are semantically visible. A family is not preserved merely because one representative remains.

Record repeated-element placement separately from count: shared row/column or baseline, left-to-right/top-to-bottom order, plane membership, relative spacing, dominant direction, and visible scale progression. Use one shared geometric system for each authored group.

Require evidence of minimum semantic completeness before describing simplification as successful. Record retained, simplified-but-retained, and omitted members. Missing mandatory families or multiple regions with deleted details require revision even when global metrics improve.

## 5. Mixed local strategies

Choose one primary mode for the case, then assign region-specific construction strategies where necessary. Regular regions may use shared-coordinate geometry while a critical free contour uses controlled Béziers and a distinctive repeated family uses individually varied semantic objects. Do not invent a new formal mode name for these local exceptions.

Map each critical region to named SVG objects or groups so local diagnostics and later edits can identify the responsible geometry.

Give important semantic groups, planes, and landmark-bearing objects stable public-safe SVG IDs or data attributes where appropriate. IDs must be unique, plain-SVG compatible, and free of private paths or unpublished case identifiers. Do not require an ID on every minor path.

## 6. Groups and complexity

Use short English IDs, preferably one to three words, such as `background`, `base-blocks`, `gradients`, `top-arcs`, `leaf-shapes`, or `line-details`. Adapt names to the image. Avoid `group1`, very long labels, a top-level layer per tiny item, or one opaque group for everything.

Treat object counts as warning levels, not universal limits:

- simple logo/icon: usually below 200 major objects;
- simple geometric illustration: usually below 500;
- medium flat illustration: usually below 1200;
- high-detail work: justify any larger count.

Investigate regardless of total count when one simple region has hundreds of fragments, many tiny objects appear, colors proliferate near edges, or major objects cannot be selected/recolored as units.

Interpret a count decrease conservatively, especially for medium- and high-density scenes. Fewer objects are not an optimization unless required-family inventory, repeated-detail counts, region evidence, and human comparison show that visible semantic content remains complete.

## 7. Auto-tracing boundary

Use tracing only for candidate contours, masks, boundary estimates, initial colors, or missing-region discovery. Record where it was used and how it was cleaned.

Never deliver:

- uncleaned whole-image tracing;
- anti-alias or compression pixels converted to paths;
- fragmented soft edges;
- polygon-built gradients;
- a trace accepted only because SSIM, PSNR, MAE, or RMSE looks favorable.

Rebuild regular geometry and semantic regions after measurement. Keep case-specific tracing or drawing code with the case, outside the reusable Skill.
