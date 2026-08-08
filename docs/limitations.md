# Limitations

Clean Vector Reconstruction is experimental and intentionally optimized for a narrow class of illustrations.

## Best-fit inputs

The workflow is most reliable when the reference has:

- clear color-block boundaries
- readable silhouettes
- flat or semi-flat rendering
- limited texture
- moderate semantic complexity

## Known difficult cases

### Articulated anatomy

Characters or animals with complex limb relationships can fail even when individual body parts are present.

A result may be semantically complete but still have incorrect joint, attachment, or pose topology.

### Complex perspective

Repeated objects on oblique or perspective planes can remain geometrically inaccurate even when object counts and internal constraints pass.

### Dense scenes

Large numbers of small architectural or decorative elements increase the risk of over-simplification or layout drift.

### Painterly / photographic input

Boundary-based validation is not designed for photography, heavy texture, painterly shading, blurry low-contrast boundaries, or dense natural detail.

### Boundary metrics

Reference-grounded boundary metrics are useful diagnostic signals, but they do not measure semantic correctness, topology, editability, layer quality, gradient construction quality, or Illustrator usability.

A higher boundary score does not automatically mean a better SVG.

### Downsampling

Boundary analysis may use a smaller analysis raster than the full render. This introduces quantization error.

### Rectangular regions

Region-level diagnostics may include several overlapping semantic objects. A region score can therefore mix multiple causes.

## No guarantee of pixel-perfect reconstruction

The project does not target pixel-perfect tracing.

Its target is an Illustrator-ready vector reconstruction: major structure should be correct, while remaining differences should be fixable through limited local editing.

If a major object, pose, facade, or landscape region must be redrawn, the result should not be considered ready.
