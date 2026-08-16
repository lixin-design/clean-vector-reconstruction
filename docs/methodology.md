# Methodology

Clean Vector Reconstruction rebuilds suitable raster illustrations as editable SVG geometry. The work starts with the canvas and the major relationships in the composition: large regions, shared boundaries, spacing, overlap, and the underlying spatial scaffold.

Meaningful objects are then built with native SVG primitives where they fit and concise Bézier paths where they do not. Fills, strokes, gradients, and readable groups keep the drawing understandable as well as renderable. Adjacent shapes that share an edge should use a shared coordinate when practical.

## Two working modes

`geometric-flat` is a practical fit for aligned blocks, repeated units, regular geometry, and broad colour regions. `clean-flat` is for controlled free curves and mixed structured scenes. Both modes aim for semantic, editable construction rather than a trace made from many small fragments.

## Choosing a reference

Clean colour-block compositions, still lifes, structured interiors, architecture, and repeated systems are often good candidates. Visual complexity alone is not the dividing line: a detailed scene can still work when its parts separate cleanly, its boundaries are legible, and its spatial or repeated structure is stable.

## Outputs and review

The workflow can produce a layered SVG for useful editing groups and a plain SVG for simpler compatibility. Previews support inspection. Structural checks and rendering help identify technical problems, but final judgment remains a human visual review of the composition, relationships, and remaining edit work.

See [Validation](validation.md) for the available checks and [Limitations](limitations.md) for the boundaries of the workflow.
