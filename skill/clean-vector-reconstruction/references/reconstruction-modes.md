# Reconstruction Modes

Use this reference to select, switch, or reject a reconstruction mode. Inspect the actual image before choosing.

## Decision table

| Mode | Status | Suitable input | Primary construction | Switch or stop when |
|---|---|---|---|---|
| `geometric-flat` | Supported | Rectangular layouts, circles, ellipses, arcs, straight lines, repeated geometry, limited gradients | Native geometric elements, shared coordinates, simple paths, native gradients | Free-form subjects dominate or distinctive contours cannot be expressed with regular geometry |
| `clean-flat` | Supported | Flat or semi-flat subjects with complete semantic color regions and controlled curves | Closed color-block paths, smooth Béziers, semantic groups, limited gradients | Texture, lighting, or contour detail requires extensive fragmentation |
| `line-art` | Experimental | Black/white or few-color outlines, uniform strokes | Repaired strokes, endpoints, intersections, consistent widths | Stroke topology is unclear or dense shading behaves like texture |
| `logo` | Experimental | Small, highly controlled marks with symmetry or few shapes | Precise geometry, symmetry, minimal anchors | Legal/source accuracy is unclear or pixel reference is too weak for exact reconstruction |
| `high-fidelity` | Experimental | Complex but still vector-suitable illustration where more detail is justified | Semantic regions plus selectively greater path detail | Photography, painterly texture, or path volume would destroy editability |

## Selection procedure

1. Measure the share of regular geometry, free curves, texture, gradients, repeated units, and small detail.
2. Choose the narrowest supported mode that preserves the design without fragmentation.
3. Record why the mode fits and which regions may need a secondary technique.
4. Treat mixed images by assigning one primary mode and documenting exceptional regions; do not invent a new mode casually.
5. Reassess if reconstruction begins producing many tiny paths, genericized curves, or unstable positioning.

## Suitable inputs

- Clear raster reference at usable resolution.
- Identifiable semantic regions and major boundaries.
- Solid fills, limited gradients, clean lines, or moderate free curves.
- Rights and permissions sufficient for the requested work and publication status.
- A target where editability matters more than automatic pixel equality.

## Unsuitable inputs

- Photography, watercolor, oil painting, dense natural texture, or highly realistic lighting.
- Missing, ambiguous, heavily compressed, or tiny reference images.
- A request for automatic pixel-perfect conversion regardless of path count or editability.
- Materials that cannot be read or transformed under the stated permission boundary.

## Stop indicators

Stop and explain the limitation when:

- the reference or permissions are missing;
- the image is outside supported scope and narrowing is not acceptable;
- a required renderer or editor check cannot be performed and no safe fallback exists;
- the only available approach would be embedding the raster or delivering uncleaned full-image tracing;
- continuing would require installing software without user approval.

## Mode-switch indicators

- Switch from `geometric-flat` to `clean-flat` when distinctive free contours dominate.
- Switch from `clean-flat` to `geometric-flat` when most apparent curves resolve into regular arcs or aligned blocks.
- Do not switch to `high-fidelity` merely to raise SSIM or reduce a difference-map score.
- Mark experimental modes honestly and require extra evidence before claiming broad reliability.
