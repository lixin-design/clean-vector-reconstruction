# Adobe Illustrator Human Review — [version]

> A real user or reviewer must complete this document after opening and editing the actual SVG files in Adobe Illustrator. Codex must not fabricate or prefill the findings, scores, compatibility result, or final grade.

## 1. Review information

- Reviewer:
- Date:
- Illustrator version:
- Layered SVG reviewed:
- Plain SVG reviewed:
- Automatic checks available:

## 2. Seven-part score

Use 1–5, where 1 is unusable/seriously wrong, 3 is usable with meaningful correction, and 5 is strong with only negligible differences.

| Category | Score (1–5) | Observations |
|---|:---:|---|
| Visual similarity | | |
| Edge and curve quality | | |
| Object editability | | |
| Gradient editability | | |
| Layer structure | | |
| Anchor-point quality | | |
| Plain SVG compatibility | | |

## 3. Editing checks

- [ ] Major objects can be selected independently
- [ ] Major fills can be recolored as units
- [ ] Repeated elements can be moved/edited
- [ ] Gradients are recognized and adjustable
- [ ] Layer/group names are readable
- [ ] Anchor counts and handles are practical
- [ ] Plain SVG opens without missing content
- [ ] File can be saved for continued editing

## 4. Critical-region review

| Region | Semantic completeness | Repeated-detail retention | Local motif fidelity | Critical contour/landmark fidelity | Representation semantics | Coverage/gaps | Needs adjustment? | Isolated fix or multi-region revision? |
|---|---|---|---|---|---|---|:---:|---|
| | | | | | | | | |

- Number of critical regions needing adjustment:
- Local motifs replaced or over-generalized:
- Critical endpoints, curvature, or clipping relationships needing correction:
- Gradient fidelity observations beyond mere definition/editability:
- Differences supported as isolated single-object fixes:
- Differences requiring multi-region revision:
- Missing required object families:
- Repeated families below or above the expected range:
- Multiple detail families deleted:
- Accidental transparency gaps:
- Background coverage:
- Foreground coverage:

## 5. Spatial fidelity review

- Overall spatial fidelity:
- Relative building/object proportions:
- Major object positions, spacing, overlap, and shared baselines:
- Perspective / plane consistency:
- Repeated-element arrangement, order, spacing, direction, and relative scale:
- Critical contour start/end/turning/extremum/intersection/clip points:
- Objects present but wrongly placed:
- Clean paths with wrong geometry:
- Spatial failures isolated to one object or coupled across regions:

## 6. Reference-grounded boundary review

- Boundary validation applicable to this reference: yes / limited / no
- Do mismatch maps correspond to visible problems? yes / mixed / no; observations:
- Do the top metric mismatch regions match the visually important regions? yes / mixed / no:
- Did metric-guided corrections improve the actual drawing? yes / mixed / no / not run:
- Did higher metric scores come at the cost of path cleanliness, semantic grouping, required detail, or editability? yes / no / unclear:
- Does boundary validation agree with overall human visual judgment? yes / mixed / no:
- Important disagreement between boundary evidence, internal geometry, semantics, and visible result:
- Dense tracing, unsupported decoration, or suspicious edge-density increase observed:

Boundary evidence is advisory. Do not let it prefill or determine the human grade.

## 7. Critical issues

List any issue that blocks continued use or requires major reconstruction:

1.

## 8. Noncritical differences

Classify important differences and explain their design impact:

1.

## 9. Easy-to-fix differences

List only differences where the correct object exists and moving, scaling, recoloring, gradient adjustment, or a few anchor edits is sufficient:

1.

Do not classify multi-region deviations as easy to fix without explicit evidence.

## 10. Plain SVG compatibility

- Opens correctly:
- Missing/clipped content:
- Gradient behavior:
- Color changes:
- Save/edit behavior:

## 11. Final result

- [ ] Pass — no critical issue; strong usability; only negligible differences
- [ ] Conditional pass — core workflow succeeds; only minor easy-to-fix differences remain
- [ ] Conditional pass — borderline — usable/editable, but a serious fidelity concern or several critical regions require coordinated revision
- [ ] Fail — critical structure, raster, editability, gradient, or compatibility problem
- [ ] Fail — visual fidelity — technically editable but missing, displaced, or uncovered content requires major reconstruction

## 12. Regression category

- [ ] Pass — clear improvement
- [ ] Conditional pass
- [ ] No improvement
- [ ] No sufficient visual improvement
- [ ] Regression

## 13. Final comments

Overall assessment and recommended next revision:
