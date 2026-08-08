<p align="center">
  <a href="README.md"><strong>English</strong></a> |
  <a href="README.zh-CN.md">简体中文</a>
</p>

# Clean Vector Reconstruction

Reconstruct flat and semi-flat raster illustrations into **clean, semantic, Illustrator-editable SVGs**.

> Structure first. Editable detail second. Pixel similarity third.

## Why this project?

Raster-to-vector workflows often force a tradeoff:

- **High visual similarity** can produce thousands of fragmented paths that are difficult to edit.
- **Clean SVG generation** can look neat but drift away from the reference in composition, geometry, or local contours.

Clean Vector Reconstruction explores a middle path: rebuild the image as a **small set of meaningful vector objects**, preserve major structure and visual relationships, then use reference-grounded validation to identify where the SVG still differs from the source.

The target is not perfect auto-tracing.

The target is:

**Illustrator-ready reconstruction** — the major structure should already be correct, so Adobe Illustrator is used for local refinement rather than rebuilding the artwork.

---

## What it is designed for

Best suited to illustrations with:

- clear color blocks
- readable silhouettes
- flat or semi-flat rendering
- limited texture
- identifiable semantic objects
- clean foreground / middle-ground / background separation

Typical examples:

- geometric landscape illustrations
- editorial flat illustrations
- poster-style graphics
- simple character illustrations
- clean decorative scenes

---

## What it is not designed for

This project is not intended to replace:

- photographic vectorization
- painterly image reconstruction
- texture-heavy tracing
- dense line-art tracing
- pixel-perfect raster replication

Complex articulated anatomy, dense perspective scenes, heavy texture, or ambiguous low-contrast boundaries may still require structural correction.

See [Limitations](docs/limitations.md).

---

## Core idea

The workflow separates reconstruction into four priorities:

1. **Geometry skeleton**  
   Lock composition, major proportions, planes, spacing, occlusion, and large contours.

2. **Semantic structure**  
   Build meaningful editable objects instead of trace fragments.

3. **Local fidelity**  
   Refine distinctive motifs, curves, repeated details, and representation semantics.

4. **Reference-grounded validation**  
   Compare rendered SVG boundaries directly with the raster reference to locate geometric mismatch without turning boundary metrics into a tracing objective.

The final question is not:

> “Is every pixel identical?”

It is:

> “Can the remaining difference be corrected in Illustrator with limited local editing?”

---

## Illustrator-ready criterion

A result is considered ready for Illustrator refinement only when:

- major composition is correct
- major object proportions are credible
- major perspective / plane relationships are correct
- key occlusion and attachment relationships are correct
- major contour start / turn / end relationships are correct
- required semantic regions are present
- no accidental transparency gaps remain
- the SVG remains clean and editable
- no major object needs to be redrawn

Acceptable remaining work includes:

- moving or scaling an existing object
- adjusting a small number of anchors
- Bézier handle refinement
- fill / stroke adjustment
- native gradient-stop refinement
- small decorative corrections

If a major object, pose, facade, or landscape region must be reconstructed, the result is **not** Illustrator-ready.

---

## Reconstruction modes

### `geometric-flat`

For references dominated by:

- geometric regions
- shared baselines
- repeated structures
- planar relationships
- large clean color blocks

### `clean-flat`

For references dominated by:

- organic silhouettes
- free semantic curves
- mixed fill/stroke elements
- character or decorative forms

The mode is selected from the reference rather than forced in advance.

---

## Validation layers

### Structural quality

Checks SVG integrity, resources, path cleanliness, layered/plain consistency, and editability proxies.

### Semantic completeness

Checks required object families and repeated details so simplification does not silently remove important content.

### Internal geometry consistency

Uses landmarks, relations, planes, and critical contours to verify that the reconstruction follows its authored geometric structure.

### Reference-grounded boundary evidence

Compares the rendered SVG directly with the raster reference using fixed, reference-derived boundary extraction.

It supports:

- bidirectional boundary distance
- tolerance-based precision / recall / F1
- region-level mismatch metrics
- mismatch visualizations
- bounded local correction

Boundary metrics are **diagnostic evidence**, not a single quality score and not the reconstruction objective.

---

## Reference-grounded correction

For suitable flat illustrations, the workflow can perform a bounded correction loop:

```text
initial reconstruction
        ↓
render
        ↓
compare directly with reference boundaries
        ↓
identify the largest mismatch regions
        ↓
correct only those regions
        ↓
rerender with the same validation configuration
```

The correction loop is intentionally limited.

It must not:

- add dense trace fragments to improve recall
- delete real details to improve precision
- tune thresholds separately for each candidate
- sacrifice semantic SVG structure for a higher score

---

## Quick start

### 1. Copy the Skill into your repository

Copy:

```text
skill/clean-vector-reconstruction
```

to your repository-local Skill directory:

```text
.agents/skills/clean-vector-reconstruction
```

### 2. Start a reconstruction task

Example:

```text
$clean-vector-reconstruction

Reconstruct this flat illustration as a clean, editable SVG.

Target:
- Adobe Illustrator
- preserve major composition and object relationships
- no embedded raster
- semantic editable objects
- structure must be correct before local detail
- remaining differences should be limited to Illustrator refinement
```

For stricter workflows, provide a case brief that defines:

- target editor
- permissions
- output directory
- expected reconstruction mode
- critical regions
- publication/privacy constraints

### 3. Review the output

Typical outputs may include:

- layered SVG
- plain SVG
- rendered preview
- overlay / difference diagnostics
- SVG audit
- object-family inventory
- geometry validation
- boundary comparison
- human-review template

---

## Example results

### Geometric Harvest

A user-created original illustration reconstructed with the `geometric-flat` workflow.

| Reference | Reconstruction |
|---|---|
| <img src="examples/geometric-harvest/reference/reference.png" alt="Geometric Harvest reference" width="420"> | <img src="examples/geometric-harvest/output/preview.png" alt="Geometric Harvest reconstructed SVG preview" width="420"> |

Public files:

- [Layered SVG](examples/geometric-harvest/output/layered.svg)
- [Plain SVG](examples/geometric-harvest/output/plain.svg)
- [Example notes](examples/geometric-harvest/notes.md)

This example focuses on clean color-block reconstruction, semantic SVG structure, and Illustrator-oriented editability.

Additional public examples will be added only when both the reference artwork and reconstructed outputs are cleared for redistribution.

---

## Repository structure

```text
clean-vector-reconstruction/
├─ README.md
├─ README.zh-CN.md
├─ LICENSE
├─ CHANGELOG.md
├─ .gitignore
├─ skill/
│  └─ clean-vector-reconstruction/
├─ examples/
│  ├─ README.md
│  └─ geometric-harvest/
│     ├─ reference/
│     │  └─ reference.png
│     ├─ output/
│     │  ├─ layered.svg
│     │  ├─ plain.svg
│     │  └─ preview.png
│     └─ notes.md
└─ docs/
   ├─ methodology.md
   ├─ validation.md
   └─ limitations.md
```

---

## Project status

Current focus:

- clean semantic SVG reconstruction
- Illustrator-ready output
- reference-grounded validation
- bounded correction without trace fragmentation

The project is still experimental. Results vary by illustration structure and complexity.

---

## Documentation

- [Methodology](docs/methodology.md)
- [Validation](docs/validation.md)
- [Limitations](docs/limitations.md)

---

## License

The project-authored software and documentation are released under the [MIT License](LICENSE).

Example reference artwork and visual outputs may have separate rights terms. See the corresponding example notes before reusing or redistributing visual assets.
