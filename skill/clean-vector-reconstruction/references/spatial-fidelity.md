# Spatial Fidelity

Use this reference before constructing a composition, positioning repeated elements, rebuilding a visibly oblique plane, validating critical contours, or declaring automatic readiness.

Spatial fidelity is separate from semantic completeness. An object can exist, have a clean path, and remain editable while still being in the wrong place, on the wrong baseline, or outside the geometric system of its parent plane. The case-authored geometry inventory validates internal consistency against authored expectations; it does not independently prove that those expectations match the raster reference.

## 1. Author the geometry inventory

Create a versioned, case-authored geometry inventory before drawing. Start from [`../assets/templates/geometry-inventory-template.json`](../assets/templates/geometry-inventory-template.json) and validate it with [`../scripts/validate_geometry_inventory.py`](../scripts/validate_geometry_inventory.py).

Do not infer landmarks or relations automatically from artwork. Record only relationships supported by deliberate case analysis. Keep names generic, public-safe, stable across versions, and independent of private filenames or user paths.

### Spatial landmarks

A landmark is a semantic construction reference, not necessarily an SVG path node. Supported roles include:

- canvas-relative anchor;
- object bounding corner;
- roof peak;
- facade corner;
- shared baseline point;
- center point;
- endpoint;
- intersection;
- clipping point;
- turning point;
- high or low extremum.

Each landmark must have a stable name, region, normalized `x`/`y` or declared case coordinate, semantic role, mandatory status, and an optional nonnegative tolerance. Use normalized `0..1` coordinates when practical. If `case` coordinates are used, document the coordinate system in the case brief.

Landmarks should be sparse and decisive. Prefer a few anchors that control proportion, placement, joins, and contour identity over dense tracing.

### Relational constraints

Relations connect named landmarks, entities, or planes. Supported relation types are:

- `aligned-x`;
- `aligned-y`;
- `parallel`;
- `approximately-parallel`;
- `shares-baseline`;
- `centered-under`;
- `centered-over`;
- `offset-from`;
- `attached-to`;
- `overlaps`;
- `contained-in`;
- `follows-plane`;
- `clipped-by`;
- `same-row`;
- `same-column`;
- `ordered-left-to-right`;
- `ordered-top-to-bottom`;
- `relative-spacing`.

Every relation has a stable name, ordered subject list, mandatory status, and optional tolerance. Relations must use generic subjects; never hard-code artwork-specific nouns into the reusable Skill. Use `expected_offset` for `offset-from` and `expected_spacing` plus an axis for `relative-spacing`.

An object-family count pass does not satisfy a relation. Semantic completeness and relational fidelity are separate gates.

## 2. Define perspective-aware planar groups

For each visually planar group:

1. define the plane with three or four unique boundary anchors, preferably a quadrilateral when four corners are visible;
2. record one or two dominant edge directions in degrees;
3. identify repeated or important child entities on the plane;
4. record whether children must follow the plane orientation;
5. record a relative scale progression when it is visible;
6. require repeated children to share one plane-relative construction system.

Do not reconstruct children independently as axis-aligned shapes when the reference plane is visibly oblique or perspective-affected. No automated perspective inference is required. The case author defines the plane, and reconstruction logic records how each child follows it.

The inventory expresses a plane with `anchors`, `dominant_edge_directions`, `children`, `children_follow_plane`, optional `relative_scale_progression`, optional `tolerance`, and `mandatory`. A reconstruction-side report supplies `child_orientation_consistent` and reconstructed scale metadata for validation.

## 3. Record critical contour landmarks

For each identity-bearing curve, record:

- explicit `start` and `end` landmarks;
- ordered landmark traversal;
- high/low extrema where relevant;
- turning points;
- intersection points;
- clip points;
- major tangent direction;
- approximate relative distances to nearby anchors.

The ordered list must start with `start`, end with `end`, contain unique existing landmarks, and follow the intended traversal direction. This is a sparse contour contract, not dense tracing. A clean or low-anchor path fails when its endpoint, turn, intersection, or clipping geometry is wrong.

## 4. Construct geometry first

Use this default construction order:

1. canvas and global layout;
2. major region bounds;
3. planes and shared axes;
4. major landmarks;
5. repeated elements on planes;
6. critical contours;
7. local motifs;
8. decorative details.

This order does not override semantic completeness or representation semantics. Preserve required families, fill/stroke/gradient meaning, occlusion, coverage, and editability throughout.

## 5. Tag validation-bearing SVG objects

Give important reconstructed objects used by geometry validation stable, non-private SVG IDs or data attributes when appropriate. Suitable targets include semantic groups, plane groups, and landmark-bearing objects.

IDs must be unique, public-safe, generic, and compatible with plain SVG. Do not include user paths or case-private identifiers unless publication is authorized. Do not assign an ID to every minor path. Prefer explicit authored mappings over fragile automatic SVG semantic-object detection.

## 6. Write the reconstruction-side geometry report

Reconstruction logic must write a versioned JSON report that maps authored expectations to reconstructed coordinates and relationships. Start from [`../assets/templates/geometry-report-template.json`](../assets/templates/geometry-report-template.json), pass it to the validator with `--actual`, and include:

- actual coordinates in `points` for named landmarks and entity anchors;
- measured or explicitly evaluated relation results when a relation cannot be derived from points;
- plane child-orientation consistency and relative scale metadata in `planes`;
- the same coordinate mode as the expected inventory.

The validator can check landmark tolerance, simple alignment and baseline deltas, ordering, authored offsets, relative spacing, plane child orientation metadata, and contour endpoint deltas. It does not inspect pixels, infer perspective, or discover semantic SVG objects.

Use stable SVG IDs, data attributes, or an authored name-to-coordinate mapping to produce the report. Unresolved mandatory landmarks, relations, planes, or contour endpoints block readiness.

## 7. Apply the spatial readiness gate

`Ready for human Illustrator regression review` requires all applicable automatic gates:

1. structural validity and safe resources;
2. semantic completeness;
3. coverage and rendered alpha;
4. valid gradient references;
5. a valid mandatory spatial geometry inventory and passing reconstruction-side geometry report.

If a mandatory authored geometry constraint fails or remains unresolved, report exactly:

`Automatic regression blocked — spatial fidelity gate failed`

Clean paths, successful rendering, or favorable global/region metrics cannot override landmark or relationship failure. A valid schema without an actual report proves only that the authored contract is well formed; it does not prove reconstructed geometry.

Use [reference-grounded-validation.md](reference-grounded-validation.md) as an independent complementary signal when the reference has suitable boundaries. A plane/landmark pass cannot by itself prove reference fidelity, while favorable boundary evidence cannot prove semantic structure or validate the authored plane model. Preserve and report disagreement instead of allowing either signal to override the other.
