# Validation

The project intentionally separates several kinds of validation evidence.

## Structural quality

Checks may include:

- SVG/XML integrity
- embedded raster count
- external resource count
- layered/plain render consistency
- degenerate paths
- fragment warnings
- path complexity
- public-safe paths

## Semantic completeness

Authored inventories help ensure that important semantic object families and repeated details are not silently deleted during simplification.

## Internal geometry consistency

Authored geometry inventories may describe:

- landmarks
- alignments
- baselines
- ordering
- planar groups
- repeated-element layout
- critical contour start/turn/end points

This validates internal structure, but does not by itself prove fidelity to the raster reference.

## Reference-grounded boundary evidence

For suitable flat illustrations, the Skill can compare a same-size candidate render directly with the source raster.

Metrics include:

- reference → candidate boundary distance
- candidate → reference boundary distance
- mean / median / p90 / p95
- tolerance-based precision
- tolerance-based recall
- tolerance-based F1
- region-level metrics
- mismatch maps

The same renderer, analysis size, boundary configuration, and thresholds must be used across correction iterations.

## Anti-gaming rules

Boundary metrics are not a reconstruction objective.

The workflow prohibits:

- dense trace fragments to inflate recall
- deleting real details to inflate precision
- candidate-specific threshold tuning
- adding unsupported decorative edges
- claiming success from a single F1 value

## Human review

Final review still asks whether:

- major structure is visually correct
- the result remains editable
- mismatch maps correspond to visible problems
- metric-guided corrections actually improved the drawing
- the remaining work fits the Illustrator correction budget

No automatic metric replaces human visual judgment.
