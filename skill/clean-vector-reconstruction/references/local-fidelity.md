# Local Fidelity

Use this reference before defining critical regions, reconstructing distinctive local content, producing region diagnostics, or grading local differences.

## Critical regions

A critical region is a bounded part of the reference whose failure would materially change recognition, composition, representation semantics, or the design's distinctive character even when its pixel area is small.

Select 3–8 non-redundant regions before reconstruction. Cover the primary subject or structure, the most identity-bearing local motifs, the most important free contour or boundary, any important gradient region, and any high-risk occlusion or repeated family. Do not select regions only because they are easy to measure. If fewer than three or more than eight appear necessary, narrow or regroup the case and document why.

Record this inventory for each region:

- stable short name and rectangular bounds, with coordinate mode;
- design role and major objects or groups;
- distinctive local motifs that must remain recognizable;
- critical contours, extrema, endpoints, curvature changes, intersections, and clipping relationships;
- local landmarks and shared boundaries;
- counts, order, overlap, spacing, orientation, and intentional variation;
- expected object families and exact repeated-object counts or justified bounded ranges;
- mandatory details, optional details, and the minimum content that keeps the region semantically complete;
- reconstructed families, missing required families, and simplification notes;
- representation semantics for important objects;
- region-specific construction strategy under the selected primary mode;
- prohibited generic substitutions;
- expected SVG object or group mapping;
- required automatic evidence and human-review questions.

## Distinctive motifs and contours

A distinctive local motif is a small arrangement whose specific silhouette, count, rhythm, overlap, orientation, or internal division contributes to the design identity. Preserve those recorded relationships. Do not replace it with a stock symbol, generic curve, regular repeat, or convenient primitive when that changes its identity-bearing structure.

Anchor every required local motif to one or more named spatial landmarks and record the relations that control its placement. Local accuracy cannot be judged only by shape similarity: a recognizable motif in the wrong location, row, plane, or clipping relationship is a local-fidelity failure.

A region can be geometrically present yet semantically incomplete. A bounding shape, major color block, or named group does not prove that its required families and repeated details survive. Local metrics, clean geometry, or successful rendering cannot override a missing required family, a count below the authored minimum, or deletion of mandatory details.

For every critical contour, record named start and end landmarks, extrema, turning points, intersections, clip points, curvature direction, tangent intent, thickness or stroke behavior, and relationships to nearby anchors. A smooth curve is not faithful merely because it has few anchors. Check endpoint placement, curvature, and local alignment against the reference.

## Representation semantics

Record the intended visual mechanism for every important object:

- `solid fill`;
- `stroke`;
- `fill + stroke`;
- `linear gradient`;
- `radial gradient`;
- `transparency`.

Preserve the mechanism and its role. Any change must be explicit, justified, and reviewed for visual and editing impact. A set of solid bands is not automatically equivalent to a gradient; an outlined shape is not automatically equivalent to a filled silhouette.

## Region-specific construction

Keep one primary reconstruction mode. Within it, assign a suitable local strategy: shared-coordinate geometry for regular blocks, controlled Bézier construction for a signature contour, independent semantic objects for a distinctive motif, or native gradient geometry for a transition. These are strategies, not new formal mode names.

Do not optimize every region by the same technique. Use the simplest construction that preserves the recorded local relationships and remains editable. Preserve intentional variation instead of regularizing it into identical units.

## Region-level diagnostics

Produce global diagnostics and, for every critical region, retain:

- a reference crop;
- an SVG preview crop;
- an equal-opacity overlay crop;
- a difference crop;
- region bounds and diagnostic metrics;
- the mapped SVG group or objects;
- a classified local-difference note.
- expected versus reconstructed families, missing families, retained/omitted repeated counts, and simplification notes.

Use [`../scripts/render_compare.py`](../scripts/render_compare.py) with a safe `--regions-file` when a local renderer is available. Region metrics are diagnostic only. Region-level MAE or any favorable global metric cannot override a missing motif, wrong semantic mechanism, mandatory landmark/relationship failure, or failed critical contour.

When the reference has stable color-block edges, also use [reference-grounded-validation.md](reference-grounded-validation.md) to localize displaced contours directly from reference boundaries. Author boundary rectangles from the current reference, not old diagnostics. Boundary mismatch can identify where a contour is misplaced, but cannot determine whether the SVG uses the required fill/stroke/gradient mechanism or preserves the motif's semantic representation.

Region crops and diagnostic images inherit the reference's privacy and publication status.

## Human review

Ask a real reviewer to compare each critical region for motif identity, contour endpoints and curvature, landmark alignment, representation semantics, gradient placement and stops, occlusion, and intentional variation. Record how many regions need adjustment and whether each correction is isolated or coupled to other regions.

Call a difference easy to fix only when the correct object and semantic mechanism already exist, the correction is localized to one object or one tightly bounded relationship, only a small number of anchors or parameters must change, and no neighboring critical region or occlusion chain must be rebuilt. Multiple visibly wrong regions, a generic substitution, a missing semantic mechanism, or a coupled contour change is not proven easy to fix without explicit human evidence.

General examples include a signature edge whose endpoint controls an adjacent join, an irregular family of small marks whose count and rhythm matter, a filled emblem that must not become an outline, and a focal transition whose gradient direction and extent affect depth. Treat these as patterns, not required object types.
