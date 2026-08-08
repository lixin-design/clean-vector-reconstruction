# Vector Reconstruction Automatic Report — [version]

## 1. Environment

- Python executable/version:
- SVG renderer/version:
- Available optional tools:
- Missing optional tools:
- Required dependency missing: yes / no
- Installations performed: none (unless separately approved and documented)
- Path-display mode: `basename` / `relative` / `absolute`

## 2. Method

- Selected mode:
- Geometry strategy:
- Free-curve strategy:
- Gradient strategy:
- Repeated-element strategy:
- Auto-tracing assistance, if any:
- Shared-boundary and landmark strategy:
- Critical regions analyzed:
- Region-specific construction strategies:
- Scene complexity profile:
- Semantic-density level: `low` / `medium` / `high`
- Mandatory details and optional simplifications:
- Geometry inventory path/version:
- Reconstruction-side geometry report path/version:

## 3. Files created

- Layered SVG:
- Plain SVG:
- Preview:
- Overlay:
- Difference:
- Scripts/reports:
- Region-level evidence directory/paths:

## 4. SVG statistics

| Element | Layered SVG | Plain SVG |
|---|---:|---:|
| path | | |
| rect | | |
| circle | | |
| ellipse | | |
| line | | |
| polyline | | |
| polygon | | |
| group | | |
| linearGradient | | |
| radialGradient | | |
| image | | |
| total drawable objects | | |

## 5. Raster-reference audit

| Search | Layered SVG | Plain SVG |
|---|---:|---:|
| `<image` | | |
| `data:image` | | |
| `.png` | | |
| `.jpg` | | |
| `.jpeg` | | |

Required result: all raster-reference counts are zero.

### Resource-reference result

- Internal fragment references:
- Embedded data references:
- External local/remote references:
- `<foreignObject>` count:
- External-resource audit passed: yes / no
- Unresolved resource warnings:

## 6. Fragment and structure warnings

- XML parsing:
- Width/height/viewBox:
- Possibly unclosed filled paths:
- Degenerate objects:
- Tiny/very short candidates:
- Duplicate/overlap candidates:
- Fragmented groups or color proliferation:
- Advisory threshold status:

## 7. Gradient usage audit

Complete for each SVG when gradients matter.

- Defined linear-gradient IDs:
- Defined radial-gradient IDs:
- Gradient IDs referenced by object fill/stroke:
- Used gradient count:
- Unused gradient IDs:
- Missing gradient references:
- Duplicate gradient IDs:
- Objects using each gradient:

Actual gradient use does not prove visual fidelity. Human review must compare placement, direction, colors, stops, transition extent, and opacity with the reference.

## 8. Render results

- Layered SVG rendered:
- Plain SVG rendered:
- Correct dimensions:
- Variant consistency:
- Gradients visible:
- Blank or clipping errors:
- Renderer used:
- SVG aspect ratio and source (`viewBox` or width/height):
- Reference aspect ratio:
- Relative aspect-ratio difference and tolerance:
- Aspect-ratio mismatch: yes / no
- Mismatch explicitly allowed: yes / no
- Diagnostic rendering distorted or potentially distorted: yes / no
- Eligible as normal positional-fidelity evidence: yes / no

## 9. Global and critical-region comparison

- Major block/bounding-box alignment:
- Shared boundaries:
- Important centers/endpoints:
- Repeated spacing:
- Overlay observations:
- Optional diagnostic metrics (never a final grade):

| Critical region | Mapped SVG objects/groups | Preview | Overlay | Difference | Metrics | Automatic observation |
|---|---|---|---|---|---|---|
| | | | | | | |

Global metrics cannot override a critical-region failure.

## 10. Required object-family completeness

| Region | Expected family | Expected count/range | Reconstructed count | Status | Simplification note |
|---|---|---:|---:|---|---|
| | | | | | |

- Expected families:
- Reconstructed families:
- Missing required families:
- Below-minimum repeated families:
- Above-maximum repeated families:
- Repeated-detail retention:
- Minimum semantic completeness passed: yes / no
- Inventory validator exit status:

## 11. Canvas coverage and transparent-gap audit

- Reference fully opaque: yes / no / unclear
- Case-declared transparency intent:
- Structural full-canvas background object exists/opaque:
- Background coverage result:
- Foreground coverage result:
- Reference transparent-pixel count:
- Rendered SVG transparent-pixel count:
- Unexpected transparent-pixel count and canvas percentage:
- Unexpected gap regions/bounding boxes:
- Internal foreground-boundary contact:
- Canvas-edge-only contact:
- Layered/plain alpha agreement:
- Alpha coverage passed: yes / no

## 12. Spatial geometry validation

### Landmark validation summary

- Authored landmarks:
- Resolved landmarks:
- Mandatory landmarks passed:
- Mandatory landmark failures and deltas/tolerances:

### Relational constraint summary

- Supported/applicable relations:
- Mandatory relations passed:
- Alignment and baseline deltas:
- Ordering and relative-spacing results:
- Mandatory relation failures:

### Plane-group summary

- Authored plane groups:
- Boundary anchors resolved:
- Child-orientation consistency:
- Relative scale progression:
- Wrong-plane repeated elements:

### Repeated-element layout summary

- Rows/columns/baselines:
- Ordering:
- Relative spacing:
- Plane ownership and direction:

### Critical-contour landmark summary

- Start/end landmark results:
- Turning/extremum/intersection/clip landmark results:
- Failed contour landmarks:

- Geometry readiness evaluated: yes / no
- Geometry readiness blocked: yes / no
- Spatial gate status:

## 13. Representation-semantic deviations

List any difference from recorded `solid fill`, `stroke`, `fill + stroke`, `linear gradient`, `radial gradient`, or `transparency` semantics.

1.

## 14. Conservative known-difference summary

Classify each as structural, positional, color, gradient, edge anti-aliasing, acceptable regularization, missing element, or extra element.

1.
2.

- Number of critical regions needing adjustment:
- Isolated single-object fixes:
- Multi-region or coupled revisions:
- Human evidence supporting any “easy to fix” claim:
- Object-count change from the prior version:
- Conservative interpretation of the object-count change:
- Multiple detail families deleted: yes / no / unknown

## 15. Reference-grounded boundary evidence

- Applicable: yes / limited / no
- Applicability rationale and limitations:
- Candidate raster produced by the audited same-render workflow: yes / no
- Renderer/version:
- Full render size:
- Analysis size:
- Background handling and color mode:
- Downsampling:
- Method config path/version:
- Method config SHA-256:
- Resolved config SHA-256:
- Reference-derived high/low thresholds:
- Same resolved config used for reference and candidate: yes / no
- Candidate-specific tuning accepted: must be `no`
- Boundary pixel counts — reference / candidate:

### Global directional metrics

| Direction | Mean full px | Median full px | p90 full px | p95 full px |
|---|---:|---:|---:|---:|
| Reference → candidate | | | | |
| Candidate → reference | | | | |

| Tolerance full px | Precision | Recall | F1 |
|---:|---:|---:|---:|
| | | | |

### Critical-region boundary metrics

| Region | Ref→candidate mean/p90/p95 | Candidate→ref mean/p90/p95 | Precision/recall/F1 by tolerance | Boundary counts | Evidence classification |
|---|---|---|---|---|---|
| | | | | | |

- Top 3–5 critical mismatch regions:
- Mismatch map paths:
- Mixed or contradictory metric evidence:
- Relationship to internal geometry result:

### Targeted correction iterations

Use no more than two rows and keep the exact same config, resolved thresholds, tolerances, regions, and renderer.

| Iteration | Regions corrected | Classified cause | Both-direction result | Precision/recall/F1 result | Boundary/path/detail anti-gaming checks | Outcome per region |
|---:|---|---|---|---|---|---|
| 1 | | | | | | |
| 2 | | | | | | |

Boundary metrics are geometric diagnostic evidence. They are not editability, semantic, gradient, or universal quality scores, and no single F1 value establishes a pass.

## 16. Automatic status

- [ ] Automatic critical checks passed
- [ ] Warnings require revision
- [ ] Blocked by missing tool/input/permission

- Automatic structural pass: yes / no
- Visual-regression pass: not established / established by real review
- Missing-family blocker: yes / no
- Transparency/coverage blocker: yes / no
- Other completeness blocker:
- Spatial geometry blocker: yes / no
- Boundary evidence status: favorable / unfavorable / mixed / limited / not applicable
- Boundary metric gaming warning: yes / no
- Automatic readiness blocked: yes / no

- Structural pass: yes / no
- Semantic completeness pass: yes / no
- Internal geometry consistency pass: yes / no
- Reference-grounded boundary evidence recorded: yes / no / limited / not applicable
- Human visual agreement: not established / established by real review

Ready for human Illustrator regression review: yes / no

If mandatory authored geometry fails, use: `Automatic regression blocked — spatial fidelity gate failed`.

This report does not contain or imply a human Illustrator score or final human grade.
