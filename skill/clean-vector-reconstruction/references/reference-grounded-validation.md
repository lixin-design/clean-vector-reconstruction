# Reference-Grounded Boundary Validation

Use this reference when geometry fidelity matters, a flat or semi-flat reference has readable color-block boundaries, critical contours or planes control the composition, or a regression needs evidence independent of authored geometry JSON.

## Contents

1. Purpose and boundary
2. Applicability
3. Normalization contract
4. Fixed reference-derived extraction
5. Metrics and regions
6. Outputs and interpretation
7. Targeted correction loop
8. Anti-gaming rules
9. Relationship to other gates
10. Failure modes and limits

## 1. Purpose and boundary

Use the original raster reference as an independent source of geometric evidence. Detect displaced boundaries, wrong perspective edges, incorrect contour start/end/turning locations, wrong large-scale layout, and geometry that is internally consistent with an authored contract but inaccurate to the reference.

Keep the reconstruction target as clean, semantic, editable SVG. Boundary validation is not:

- a replacement for semantic reconstruction;
- a raster-tracing objective;
- proof of editability or Illustrator compatibility;
- proof of semantic completeness, topology, or grouping;
- proof of gradient fidelity;
- a universal single quality score.

Never infer that a high boundary F1 establishes visual validity. Do not define a universal absolute F1 pass threshold from one case or one prototype.

## 2. Applicability

Apply boundary validation when:

- major color blocks create stable visible boundaries;
- perspective, planes, layout, or critical contours materially affect fidelity;
- the case brief identifies critical boundary regions;
- a regression needs direct reference-grounded evidence.

Mark it `limited` or skip it with a reason when heavy texture, photography, painterly gradients, low-contrast ambiguous boundaries, compression noise, or natural detail makes color-discontinuity extraction unreliable. Do not broaden the supported reconstruction modes merely because the validator can process a raster.

## 3. Normalization contract

Before comparing boundaries, require:

1. the same audited renderer and renderer version for every SVG candidate;
2. the same viewport and full raster dimensions;
3. the same background and alpha compositing policy;
4. the same RGB color mode;
5. the same aspect-preserving downsampling method and analysis size;
6. one method config authored before candidate metrics are inspected;
7. one resolved threshold set applied unchanged to the reference and every candidate.

Run [`../scripts/audit_svg.py`](../scripts/audit_svg.py) before rendering. Use the existing safe same-render workflow to produce candidate rasters; [`../scripts/compare_boundaries.py`](../scripts/compare_boundaries.py) intentionally accepts raster inputs so it cannot bypass SVG resource auditing or silently choose a different renderer.

Start from [`../assets/templates/boundary-validation-config-template.json`](../assets/templates/boundary-validation-config-template.json). Leave `fullRenderSize.width` and `height` as `null` only when they should resolve from the identically sized inputs. `analysisSize.maxDimension` preserves aspect ratio. If explicit analysis width and height are used, preserve a uniform distance scale.

Record the renderer, renderer version, full size, analysis size, background handling, color mode, downsampling, method-config SHA-256, and resolved-config SHA-256. Reject dimension mismatches and candidate-specific configuration keys.

## 4. Fixed reference-derived extraction

Use this reusable flat-illustration pipeline:

1. convert the normalized inputs to RGB;
2. apply a light Gaussian blur to suppress small antialias oscillations;
3. convert sRGB to CIELAB D65;
4. calculate a multi-channel 3×3 Sobel color-discontinuity magnitude;
5. thin responses with four-direction non-maximum suppression;
6. derive the high threshold once from the reference-only response distribution, using the configured percentile clip and Otsu method, subject to the authored floor;
7. derive the low threshold only from the fixed low/high ratio;
8. apply those exact high and low values to both reference and candidate using 8-connected hysteresis;
9. remove connected components smaller than the configured minimum.

Do not copy threshold constants from a prior artwork as universal defaults. The template values are conservative starting parameters based on the validated method shape, not universal pass settings. The resolved high/low thresholds remain reference-dependent.

When `thresholdMethod` is `fixed`, treat `thresholdFloor` as the explicitly authored high threshold and record why a fixed threshold is justified. Never switch methods or change blur, thresholds, component size, analysis size, or tolerances after seeing candidate scores.

## 5. Metrics and regions

Compute an exact Euclidean distance field to each binary boundary map.

- `reference → candidate`: sample distance to the nearest candidate boundary at every reference boundary pixel.
- `candidate → reference`: sample distance to the nearest reference boundary at every candidate boundary pixel.

Report mean, median, p90, and p95 in full-resolution pixel units for both directions. Read both directions and several statistics; one favorable mean or percentile cannot establish improvement.

For each full-resolution tolerance `t`:

- precision = candidate boundary pixels whose nearest reference boundary is within `t` / all candidate boundary pixels;
- recall = reference boundary pixels whose nearest candidate boundary is within `t` / all reference boundary pixels;
- F1 = harmonic mean of precision and recall.

Report boundary counts with precision and recall. Extra decoration can increase recall while hurting precision; deletion can shrink the precision denominator while hurting recall. Treat empty-boundary cases as missing evidence or complete directional failure, never a perfect match.

Author critical rectangles directly from the current reference using [`../assets/templates/boundary-regions-template.json`](../assets/templates/boundary-regions-template.json). Do not copy rectangles from old diagnostics. Use normalized coordinates or integer full-resolution pixels. Keep names unique, public-safe, and traversal-free; require positive area, in-bounds coordinates, and the configured region cap.

For region metrics, select source boundary pixels inside the region but sample the full-image distance fields. This avoids artificial nearest-boundary failures at crop edges.

## 6. Outputs and interpretation

Retain:

- the original method config and resolved config;
- reference and candidate boundary maps;
- global bidirectional distance and tolerance metrics;
- the same metrics for every critical region;
- a global mismatch map and region mismatch crops;
- JSON and, when enabled, CSV evidence.

The mismatch map uses red for reference-only mismatches, cyan for candidate-only mismatches, and pale values for close overlap. Interpret it with the reference and candidate render; a colored pixel does not identify the semantic cause by itself.

Classify the largest 3–5 critical mismatches as boundary displacement, perspective/plane mismatch, contour start/end mismatch, missing detail, or extra unsupported boundary. Preserve mixed evidence. If the metric conflicts with human visual judgment, report the conflict with the frozen config instead of tuning it to force agreement.

## 7. Targeted correction loop

Use at most two correction iterations:

1. reconstruct and retain versioned SVG evidence;
2. audit and render with the normalization contract;
3. compare against the reference with the frozen resolved config;
4. identify the largest 3–5 critical mismatch regions;
5. classify each mismatch cause;
6. correct only those regions unless a documented coupled dependency requires broader work;
7. rerender with the same renderer and normalization;
8. recompute with the exact same config, resolved thresholds, tolerances, and regions;
9. retain previous evidence and classify each region as improved, regressed, unchanged, or mixed.

Do not claim success from one directional metric, one tolerance, one percentile, or F1 alone. Require coherent evidence across both directional distances, precision and recall, boundary counts, mismatch visualization, semantic completeness, path cleanliness, and the affected geometry contract. Stop after two iterations and hand unresolved issues to human review or a separately versioned reconstruction task.

## 8. Anti-gaming rules

Prohibit:

- adding dense trace fragments to inflate recall;
- adding decorative edges only to improve boundary metrics;
- deleting supported detail merely to improve precision;
- replacing clean semantic paths with raster-like contour fragments;
- changing analysis size, blur, thresholds, component filtering, tolerances, or regions between candidates or correction iterations;
- selecting only favorable regions or dropping a regressed critical region;
- treating F1 or any aggregate as the reconstruction objective;
- calling a correction successful when only one direction improves.

For every correction, compare boundary pixel counts, required object-family counts, SVG drawable/path counts, fragment warnings, semantic grouping, and human-visible cleanliness. A metric gain accompanied by new unsupported boundaries, lost mandatory details, fragmented paths, or worse editability is a failed correction.

## 9. Relationship to other gates

Keep these conclusions distinct:

- `structural pass`: valid safe SVG, canvas, resources, and rendering prerequisites;
- `semantic completeness pass`: required families, counts, motifs, and representation semantics survive;
- `internal geometry consistency pass`: reconstruction-side landmarks, relations, planes, and contour contracts match the case-authored inventory;
- `reference-grounded boundary evidence`: rendered boundaries agree or disagree directly with the current reference;
- `human review`: visible fidelity, path cleanliness, editability, gradient behavior, and final judgment.

Internal geometry may pass while the authored geometry itself is reference-inaccurate. Boundary evidence may look favorable while semantic grouping, completeness, editability, or gradient construction fails. Neither signal overrides the other, and neither overrides a real human review. A candidate is not visually validated merely because internal geometry JSON passes or boundary metrics improve.

When signals disagree, freeze and retain all inputs/configuration, localize the disagreement, inspect region maps, recheck the authored geometry and semantic inventory, and ask the human reviewer to judge the visible result. Do not average incompatible gates into one score.

## 10. Failure modes and limits

- High edge density can dominate global scores and hide broad low-density contour errors.
- Decorative edges can raise recall; unsupported edges should lower precision but may still bias aggregates.
- Missing detail generally lowers recall but can make precision appear better by shrinking the candidate set.
- Fragmented tracing can place many short edges near reference pixels despite poor editability.
- Broad rectangles can mix unrelated objects and dilute diagnostic value.
- Reference-derived thresholds can omit subtle low-contrast boundaries or retain internal decoration.
- Downsampled analysis quantizes short distances and makes subpixel tolerances discrete.
- Boundary distance does not measure semantic grouping, topology, object completeness, gradient construction, anchor quality, or Illustrator compatibility.

Keep boundary validation as independent diagnostic, regression, and targeted-correction evidence. Validate the reconstruction, not the metric.
