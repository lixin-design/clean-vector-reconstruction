# Methodology

Clean Vector Reconstruction is built around one practical target:

> Produce a clean semantic SVG whose major structure is already correct, so Adobe Illustrator is used for refinement rather than reconstruction.

## Structure-first reconstruction

The workflow prioritizes:

1. global composition
2. major proportions
3. perspective / plane relationships
4. relative placement and spacing
5. occlusion and attachment
6. major contour envelopes
7. semantic object completeness
8. fill / stroke / gradient semantics
9. local motifs
10. micro-details

Higher-priority structure should never be sacrificed for lower-priority similarity metrics.

## Geometry skeleton

Before decorative detail, the reconstruction should establish:

- canvas
- major object envelopes
- major planes
- shared baselines
- important centers / peaks / anchors
- major foreground/background contours
- major overlap relationships

This skeleton is rendered and checked before detail work begins.

## Semantic reconstruction

The objective is not raster tracing.

Objects should remain meaningful and editable rather than becoming thousands of tiny trace fragments.

## Local fidelity

After structure is locked, local refinement may target distinctive silhouettes, hair, flowers, snow lines, decorative arcs, repeated objects, and local contour differences.

## Illustrator-ready output

The reconstruction is considered successful when major geometry does not need to be rebuilt.

Remaining work should be limited to local Illustrator operations such as anchor adjustment, Bézier refinement, object repositioning, fill/stroke changes, and native gradient-stop tuning.

## Reference-grounded validation

Internal geometry constraints can remain self-consistent while drifting away from the reference.

For suitable flat illustrations, the Skill therefore compares the rendered SVG directly with the raster reference.

Reference-grounded validation is used to locate mismatch, not to turn the SVG into a dense trace.

See [Validation](validation.md).
