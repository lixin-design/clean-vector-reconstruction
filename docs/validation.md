# Validation

Validation checks whether an SVG is structurally sound and practical to inspect. It does not automatically prove visual fidelity, editability, or final quality.

## Structural checks

- Parse the SVG/XML and confirm that the document has a measurable canvas.
- Check for embedded raster content, linked raster content, and unsafe external resources.
- When layered and plain versions are both present, compare their canvas and visible consistency.

## Diagnostic viewing

Rendering an SVG and viewing it beside its reference can reveal clipping, missing shapes, unexpected scaling, or other visible issues. These are diagnostic aids, not an automatic measurement or quality guarantee.

## Human review

A person reviews the important composition, object relationships, group structure, and remaining edit work. A successful structural check means that the file has cleared useful technical checks; it does not mean that the drawing is finished.
