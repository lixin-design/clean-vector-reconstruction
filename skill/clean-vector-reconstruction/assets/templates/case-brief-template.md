# Vector Reconstruction Case Brief — [version]

## 1. Case identity

- Case name:
- Case code:
- Version:
- Date:
- Reference path:
- Reference format and dimensions:
- Ownership/licensing status:
- Local-use permission:
- Publication status: private / publication permitted / unclear

Stop if the reference or required permission is missing.

## 2. Intended output

- Target editor: Adobe Illustrator / other:
- Layered SVG path:
- Plain SVG path:
- Diagnostic/report directories:
- Selected mode: `geometric-flat` / `clean-flat` / experimental mode
- Mode rationale:

## 3. Scene complexity profile

- Semantic-density level: `low` / `medium` / `high`
- Density rationale:
- Major semantic groups:
- Repeated-detail density:
- Critical repeated-object families:
- Expected minimum detail retention:
- Reference fully opaque: yes / no / unclear
- Expected full-canvas background coverage:
- Expected foreground coverage:

## 4. Required design content

- Canvas ratio and background:
- Primary subject or major blocks:
- Secondary subjects:
- Key colors and gradients:
- Important line elements:
- Repeated elements and intended variation:
- Key landmarks:
- Shared boundaries:
- Required occlusion relationships:
- Meaningful small details:

### Required object-family inventory

Store the machine-readable form in a versioned JSON file and validate it with `validate_object_inventory.py`.

| Region | Required family | Expected minimum | Expected maximum | Mandatory details | Reconstructed count | Status |
|---|---|---:|---:|---|---:|---|
| | | | | | | |

### Repeated-detail retention

- Exact counts or justified bounded ranges:
- Intentional member variation:
- Simplified-but-retained details:
- Omitted details:

### Spatial landmark inventory

Store the machine-readable form in a versioned JSON file and validate it with `validate_geometry_inventory.py`. Landmarks are authored construction references, not automatically inferred image features.

Write reconstructed coordinates and relationship/plane results to a separate versioned JSON using `geometry-report-template.json`, then validate the pair with `--actual`.

| Landmark | Region | Coordinate mode | X | Y | Semantic role | Tolerance | Mandatory / optional | Mapped SVG ID/data attribute |
|---|---|---|---:|---:|---|---:|---|---|
| | | | | | | | | |

### Perspective-aware plane-group inventory

| Plane | 3–4 boundary anchors | Dominant edge directions | Child entities | Children follow plane | Relative scale progression | Tolerance | Mandatory / optional |
|---|---|---|---|---|---|---:|---|
| | | | | | | | |

Do not reconstruct children as unrelated axis-aligned objects when their plane is visibly oblique or perspective-affected.

### Relational constraints

| Relation | Type | Ordered subjects | Expected offset/spacing | Axis | Tolerance | Mandatory / optional | Reconstruction mapping |
|---|---|---|---|---|---:|---|---|
| | | | | | | | |

- Mandatory relations:
- Optional relations:
- Authored tolerance rationale:

## 5. Allowed simplifications

- Anti-aliasing/compression colors that may be ignored:
- Near-identical colors that may be merged:
- Geometry that may be regularized:
- Curves or details that may be simplified:
- Explicit limits on regularization:
- Mandatory details that must not be simplified or deleted:
- Optional simplifications:

## 6. Critical-region inventory

Define 3–8 regions. Bounds must use one declared coordinate mode: normalized `0..1` or integer pixels.

| Region | Bounds | Expected families/counts | Mandatory/optional details | Reconstructed/missing families | Distinctive motif | Critical contours/landmarks | Representation semantics | Region strategy | Simplification notes/prohibited substitutions |
|---|---|---|---|---|---|---|---|---|---|
| | | | | | | | | | |

Representation semantics must identify applicable `solid fill`, `stroke`, `fill + stroke`, `linear gradient`, `radial gradient`, and `transparency` behavior.

### Critical contours

- Region / contour:
- Endpoints, extrema, inflections, intersections, and clipping relationships:
- Curvature and tangent intent:
- Required local comparison evidence:

### Critical-contour landmark inventory

| Contour | Region | Start | Ordered landmarks | Turning/extrema/intersection/clip points | End | Major tangent | Nearby-anchor distances | Mandatory / optional |
|---|---|---|---|---|---|---|---|---|
| | | | | | | | | |

### Reference-grounded boundary validation

- Applicable: yes / limited / no
- Applicability rationale:
- Limiting reference characteristics (texture, painterly gradient, low contrast, ambiguity):
- Boundary method config path/version:
- Critical boundary regions authored from this reference:
- Boundary-validation limitations for this case:
- Fixed renderer, viewport, background, color, and downsampling contract:
- Correction iteration cap: `0` / `1` / `2` (never above 2)

## 7. Forbidden changes

- No raster embedding or external bitmap link.
- No whole-image auto-trace as final artwork.
- No redesign of composition or primary shapes.
- No deletion/addition of meaningful content without approval.
- No generic replacement of a recorded distinctive motif.
- No undocumented change to an important object's representation semantics.
- No dense trace fragments, unsupported decoration, or required-detail deletion to improve boundary metrics.
- No candidate-specific boundary config, threshold, tolerance, analysis-size, or region tuning.
- Case-specific restrictions:

## 8. Expected semantic groups

Use short English names; adapt this list to the image:

- `background`
- `base-blocks`
- `primary-subject`
- `gradients`
- `line-details`
- `repeated-elements`
- `decorations`

## 9. Automatic checks

- [ ] Dimensions and `viewBox`
- [ ] Element/object/path counts
- [ ] Zero raster references
- [ ] Fragment and closure heuristics
- [ ] Layered and plain SVG rendering
- [ ] Same-size preview, overlay, and difference
- [ ] Major landmark/boundary/position comparison
- [ ] Every critical region mapped to SVG objects/groups
- [ ] Region preview, overlay, difference, and metrics evidence
- [ ] Defined/used/unused/missing/duplicate gradient audit when applicable
- [ ] Representation-semantic deviations recorded
- [ ] Warning thresholds recorded
- [ ] Required object-family inventory validates and all required counts pass
- [ ] Geometry inventory schema validates
- [ ] Reconstruction-side landmark coordinates are within authored tolerances
- [ ] Mandatory relations and repeated-element layout constraints pass
- [ ] Perspective-aware plane child orientation/scale metadata passes
- [ ] Critical-contour start/end/turning landmarks pass
- [ ] Repeated-detail retention and omissions recorded
- [ ] Structural full-canvas background audit
- [ ] Rendered alpha coverage and transparent-gap audit
- [ ] Layered/plain coverage and completeness agree
- [ ] Automatic readiness blockers recorded
- [ ] Spatial fidelity gate status recorded
- [ ] Boundary-validation applicability and limitations recorded
- [ ] Reference/candidate use identical normalization and one shared resolved boundary config
- [ ] Global and critical-region bidirectional boundary metrics plus precision/recall/F1 retained
- [ ] Boundary maps, mismatch maps, boundary counts, and resolved-config hashes retained
- [ ] Correction loop uses no more than two fixed-config iterations and preserves prior evidence
- [ ] Structural, semantic, internal geometry, and reference-grounded conclusions remain separate

## 10. Human-review requirements

A real reviewer must evaluate visual similarity, edge/curve quality, object editability, gradient editability, layer structure, anchor quality, and plain SVG compatibility. Codex must not fill this review.

## 11. Pass criteria

- Automatic critical checks:
- Required human minimums:
- Differences acceptable as easy to fix:
- Conditions that force Fail:
