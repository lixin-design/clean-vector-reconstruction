# Reconstruction Rules

Use this reference before drawing geometry, curves, gradients, repeated elements, shared boundaries, or key landmarks.

## Contents

1. Structural plan
2. Geometry and curves
3. Color blocks and gradients
4. Repeated elements and regularization
5. Groups and complexity
6. Auto-tracing boundary

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

### Shared boundaries

Identify common horizontal/vertical edges, endpoints, baselines, centers, and aligned intersections. When adjacent objects should meet exactly, reuse the same coordinate. After rendering, check for gaps, background leaks, accidental overlaps, and nearly aligned edges.

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

- Preserve distinctive turns, asymmetry, silhouette, and visual weight.
- Use the fewest anchors that maintain the intended contour.
- Keep joins continuous and handles smooth where the source is smooth.
- Do not replace a recognizable curve with a generic ellipse or arc.
- Compare the curve's bounding box and key extrema against landmarks.

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

## 5. Groups and complexity

Use short English IDs, preferably one to three words, such as `background`, `base-blocks`, `gradients`, `top-arcs`, `leaf-shapes`, or `line-details`. Adapt names to the image. Avoid `group1`, very long labels, a top-level layer per tiny item, or one opaque group for everything.

Treat object counts as warning levels, not universal limits:

- simple logo/icon: usually below 200 major objects;
- simple geometric illustration: usually below 500;
- medium flat illustration: usually below 1200;
- high-detail work: justify any larger count.

Investigate regardless of total count when one simple region has hundreds of fragments, many tiny objects appear, colors proliferate near edges, or major objects cannot be selected/recolored as units.

## 6. Auto-tracing boundary

Use tracing only for candidate contours, masks, boundary estimates, initial colors, or missing-region discovery. Record where it was used and how it was cleaned.

Never deliver:

- uncleaned whole-image tracing;
- anti-alias or compression pixels converted to paths;
- fragmented soft edges;
- polygon-built gradients;
- a trace accepted only because SSIM, PSNR, MAE, or RMSE looks favorable.

Rebuild regular geometry and semantic regions after measurement. Keep case-specific tracing or drawing code with the case, outside the reusable Skill.
