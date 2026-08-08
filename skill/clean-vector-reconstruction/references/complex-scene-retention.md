# Complex-Scene Retention

Use this reference before reconstructing a scene with medium or high semantic density, defining required object families, simplifying repeated details, auditing canvas coverage, or declaring automatic readiness.

## Contents

1. Scene complexity profile
2. Required object-family inventory
3. Repeated-detail retention
4. Minimum semantic completeness
5. Conservative simplification
6. Coverage and transparency gaps
7. Automatic readiness gate
8. Human review

## 1. Scene complexity profile

Create one profile before drawing. Keep the selected reconstruction mode; semantic density is not a new mode.

Record:

- `semanticDensity`: `low`, `medium`, or `high`;
- major semantic groups and their region ownership;
- number and density of repeated-detail families;
- small semantic elements whose absence would change identity or composition;
- critical occlusion chains, shared boundaries, and foreground/background coverage;
- expected minimum detail retention and the evidence used to verify it.

Use `low` when few independent groups and repeated families exist, `medium` when several interacting groups or locally dense families require separate accounting, and `high` when many regions, repeated families, small semantic elements, or coupled occlusions make omission likely. Record the rationale; do not classify density from drawable count alone.

For medium/high-density scenes, define perspective-aware plane groups and repeated-layout relations whenever visible organization depends on a shared plane, axis, row, column, order, or spacing system.

## 2. Required object-family inventory

Author a JSON inventory before reconstruction and validate it with [`../scripts/validate_object_inventory.py`](../scripts/validate_object_inventory.py). The validator checks authored evidence; it never infers objects from an image.

For each region, list every required family with:

- a generic, safe family name;
- `expected_min` and `expected_max` counts or a justified bounded range;
- `reconstructed_count` after drawing;
- authored `status`, matching the computed count result.

Names must be unique within their scope. Keep optional details outside `required_families`, but record them in the case brief. A family is missing when its required minimum is positive and no reconstructed member exists. A below-minimum or above-maximum count is also incomplete until reviewed and corrected or the authored range is revised with evidence.

Do not substitute a different family merely to satisfy a total object count. Map reconstructed families back to named SVG groups or objects and to their critical regions.

## 3. Repeated-detail retention

Record exact counts when the reference is unambiguous. Use bounded ranges only when raster ambiguity, clipping, or overlap prevents an exact count, and state why.

For each repeated family, preserve:

- required member count or bounded range;
- family-specific silhouette and internal division;
- intentional variation in size, angle, spacing, color, or overlap;
- spatial distribution across regions;
- occlusion and attachment relationships;
- simplified-but-retained members and omitted members.

Combine required-family presence with authored spatial placement constraints. A repeated-object count pass does not imply correct arrangement: validate row/column order, shared baselines, spacing, plane ownership, orientation, and relative scale when relevant.

Do not delete visible repeated members solely to reduce complexity. Do not replace visibly distinct members with a single generic template. Recheck counts after any cleanup, grouping, clipping, or plain-SVG conversion.

## 4. Minimum semantic completeness

A region can be geometrically present yet semantically incomplete. Require all of the following before automatic readiness:

- every required family is represented;
- every required count is within its authored range;
- mandatory details and critical repeated members remain recognizable;
- no multi-region family deletion is hidden by acceptable global metrics;
- expected background and foreground coverage is present;
- no blocking accidental transparency gap exists.

Global similarity, successful rendering, clean structure, or a lower drawable count cannot override missing required content.

Semantic completeness and relational fidelity are separate gates. A scene can pass every family/count check and still fail spatial fidelity because objects are displaced or constructed on the wrong plane. Object-family completeness also does not imply correct rendered boundaries; when applicable, use reference-grounded boundary evidence as a complementary check without allowing it to excuse missing families.

## 5. Conservative simplification

Separate `mandatory_details` from `optional_simplifications` before drawing. Mandatory details include identity-bearing families, count-bearing repeated elements, important internal divisions, and elements that control occlusion or coverage. Optional simplifications may include raster noise, insignificant subpixel variation, or explicitly approved micro-detail that does not change family identity.

Simplify conservatively:

- retain a semantic object before optimizing its anchors;
- merge only elements proven equivalent in design role;
- preserve visible distinctions within a family;
- do not describe object-count reduction as improvement without completeness evidence;
- treat a large count decrease in a medium- or high-density scene as a deletion warning, not a success signal;
- require a new inventory check after count-reducing revisions.

## 6. Coverage and transparency gaps

For a fully opaque reference, require an opaque rendered result across the full canvas unless the case brief explicitly authorizes transparency. Record expected background and foreground coverage separately.

Use [`../scripts/audit_svg.py`](../scripts/audit_svg.py) for structural evidence about an obvious full-canvas background, its opacity, and clipping or masks. This is heuristic evidence only and cannot prove coverage.

Use [`../scripts/render_compare.py`](../scripts/render_compare.py) with `--check-alpha-coverage`; add `--expected-opaque-reference` when the case brief declares the reference fully opaque. Rendered alpha is the source of truth. Require equal dimensions and review:

- reference and rendered transparent-pixel counts;
- unexpected transparent pixels where the reference is opaque;
- connected unexpected-gap regions and bounding boxes;
- affected canvas percentage;
- internal versus edge-touching gaps;
- whether transparency matches only intended outer-canvas transparency.

Any unexpected internal transparency above the declared safe threshold blocks readiness. A structural background object does not excuse a rendered gap. Treat clipping, masks, adjacent shape boundaries, and plain/layered variant conversion as possible gap sources.

## 7. Automatic readiness gate

Distinguish an automatic structural pass from a visual-regression pass. `Ready for human Illustrator review` is blocked when any of these applies:

- a required family is missing;
- a repeated-family count is outside its authored range;
- mandatory details are absent or replaced generically;
- multiple regions show meaningful detail deletion;
- an opaque reference has unexpected transparency above threshold;
- expected background or foreground coverage fails;
- layered and plain variants disagree on completeness or alpha coverage;
- the inventory, critical-region evidence, or machine-readable audit is incomplete.
- a mandatory spatial landmark, relation, plane group, repeated-layout constraint, or critical-contour landmark is unresolved or fails its authored tolerance.

Passing the gate only permits human review. It does not prove visual fidelity, correct reference-grounded boundaries, editability, or regression improvement.

When the spatial condition blocks readiness, use `Automatic regression blocked — spatial fidelity gate failed`.

## 8. Human review

Ask the reviewer to compare semantic completeness, repeated-detail count and variation, background and foreground coverage, transparency gaps, multi-region deletion, and the interpretation of object-count changes. Require one regression category: `Pass — clear improvement`, `Conditional pass`, `No improvement`, or `Regression`. Use `Fail — visual fidelity` when the result remains technically editable but missing or displaced content requires broad reconstruction.

General examples include a row of repeated architectural details, a decorative family distributed across several regions, small semantic elements that preserve scene identity, and adjacent foreground color blocks that must meet without a transparent seam. These examples are patterns, not required artwork content.
