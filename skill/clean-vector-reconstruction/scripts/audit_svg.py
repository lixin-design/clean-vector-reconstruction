#!/usr/bin/env python3
"""Read-only structural, canvas, and resource audit for SVG files."""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from collections import Counter
from pathlib import Path
from urllib.parse import urlsplit
from xml.etree import ElementTree as ET


DRAWABLE = {"path", "rect", "circle", "ellipse", "line", "polyline", "polygon"}
COUNTED = [
    "path", "rect", "circle", "ellipse", "line", "polyline", "polygon",
    "g", "linearGradient", "radialGradient", "clipPath", "mask", "image",
    "use", "symbol", "foreignObject", "text",
]
NUMBER = re.compile(r"[-+]?(?:\d*\.\d+|\d+\.?)(?:[eE][-+]?\d+)?")
DIMENSION = re.compile(
    r"^\s*([-+]?(?:\d*\.\d+|\d+\.?)(?:[eE][-+]?\d+)?)\s*(px)?\s*$",
    re.IGNORECASE,
)
RASTER_SUFFIX = re.compile(r"\.(?:png|jpe?g)(?:[?#].*)?$", re.IGNORECASE)
GRADIENT_URL = re.compile(r"url\(\s*['\"]?\s*#([^)'\"\s]+)\s*['\"]?\s*\)", re.IGNORECASE)


def local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def display_path(path: Path, mode: str, cwd: Path) -> str:
    resolved = path.resolve()
    if mode == "absolute":
        return str(resolved)
    if mode == "basename":
        return resolved.name
    try:
        return str(resolved.relative_to(cwd.resolve()))
    except ValueError:
        return resolved.name


def style_map(value: str | None) -> dict[str, str]:
    result: dict[str, str] = {}
    for declaration in (value or "").split(";"):
        if ":" in declaration:
            key, raw = declaration.split(":", 1)
            result[key.strip()] = raw.strip()
    return result


def inherited_value(element: ET.Element, key: str, parents: dict[ET.Element, ET.Element]) -> str | None:
    current: ET.Element | None = element
    while current is not None:
        if key in current.attrib:
            return current.attrib[key]
        styled = style_map(current.get("style"))
        if key in styled:
            return styled[key]
        current = parents.get(current)
    return None


def gradient_references(value: str | None) -> set[str]:
    return {match.group(1) for match in GRADIENT_URL.finditer(value or "")}


def floats(value: str | None) -> list[float]:
    return [float(item) for item in NUMBER.findall(value or "")]


def first_number(value: str | None) -> float | None:
    numbers = floats(value)
    return numbers[0] if numbers else None


def parse_dimension(value: str | None) -> tuple[float | None, str | None]:
    if value is None or not value.strip():
        return None, "missing"
    match = DIMENSION.fullmatch(value)
    if not match:
        return None, "unsupported-unit-or-malformed"
    number = float(match.group(1))
    if not math.isfinite(number):
        return None, "non-finite"
    if number <= 0:
        return None, "non-positive"
    return number, None


def analyze_canvas(root: ET.Element) -> tuple[dict[str, object], list[dict[str, str]]]:
    warnings: list[dict[str, str]] = []
    root_is_svg = local(root.tag) == "svg"
    if not root_is_svg:
        warnings.append({"code": "root-not-svg", "message": "XML root element is not <svg>"})

    raw_viewbox = root.get("viewBox")
    viewbox: list[float] | None = None
    viewbox_issue: str | None = None
    if raw_viewbox is None or not raw_viewbox.strip():
        viewbox_issue = "missing"
        warnings.append({"code": "missing-viewbox", "message": "viewBox is missing"})
    else:
        tokens = [item for item in re.split(r"[\s,]+", raw_viewbox.strip()) if item]
        try:
            values = [float(item) for item in tokens]
        except ValueError:
            values = []
        if len(values) != 4:
            viewbox_issue = "malformed"
            warnings.append({"code": "malformed-viewbox", "message": "viewBox must contain four numeric values"})
        elif not all(math.isfinite(item) for item in values):
            viewbox_issue = "non-finite"
            warnings.append({"code": "non-finite-viewbox", "message": "viewBox contains a non-finite value"})
        elif values[2] <= 0 or values[3] <= 0:
            viewbox_issue = "non-positive"
            warnings.append({"code": "non-positive-viewbox", "message": "viewBox width and height must be positive"})
        else:
            viewbox = values

    width, width_issue = parse_dimension(root.get("width"))
    height, height_issue = parse_dimension(root.get("height"))
    for name, raw, issue in (
        ("width", root.get("width"), width_issue),
        ("height", root.get("height"), height_issue),
    ):
        if issue and raw is not None:
            code = f"{issue}-{name}"
            warnings.append({
                "code": code,
                "message": f"{name} is not a usable positive numeric or px dimension: {raw!r}",
            })

    source = None
    ratio = None
    reliable = False
    if root_is_svg and viewbox is not None:
        source = "viewBox"
        ratio = viewbox[2] / viewbox[3]
        reliable = True
    elif root_is_svg and width is not None and height is not None:
        source = "width-height"
        ratio = width / height
        reliable = True
    else:
        warnings.append({
            "code": "canvas-not-measurable",
            "message": "no valid viewBox or usable numeric width/height pair is available",
        })

    if not root_is_svg or not reliable:
        status = "invalid"
    elif warnings:
        status = "warning"
    else:
        status = "valid"
    return {
        "status": status,
        "reliablyMeasurable": reliable,
        "source": source,
        "aspectRatio": ratio,
        "width": root.get("width"),
        "height": root.get("height"),
        "viewBox": raw_viewbox,
        "viewBoxIssue": viewbox_issue,
    }, warnings


def opacity_value(value: str | None, default: float = 1.0) -> float:
    if value is None or not value.strip():
        return default
    stripped = value.strip()
    try:
        parsed = float(stripped[:-1]) / 100.0 if stripped.endswith("%") else float(stripped)
    except ValueError:
        return 0.0
    return parsed if math.isfinite(parsed) else 0.0


def paint_is_opaque(element: ET.Element, parents: dict[ET.Element, ET.Element]) -> bool:
    fill = (inherited_value(element, "fill", parents) or "black").strip().lower()
    if fill in {"none", "transparent"}:
        return False
    if opacity_value(inherited_value(element, "opacity", parents)) < 1.0:
        return False
    if opacity_value(inherited_value(element, "fill-opacity", parents)) < 1.0:
        return False
    if re.fullmatch(r"#[0-9a-f]{8}", fill) and fill[-2:] != "ff":
        return False
    rgba = re.fullmatch(r"rgba\([^,]+,[^,]+,[^,]+,\s*([^)]+)\)", fill)
    return not rgba or opacity_value(rgba.group(1)) >= 1.0


def structural_coverage_audit(
    root: ET.Element,
    elements: list[ET.Element],
    parents: dict[ET.Element, ET.Element],
    canvas: dict[str, object],
    transparency_intent: str,
) -> dict[str, object]:
    bounds: tuple[float, float, float, float] | None = None
    raw_viewbox = root.get("viewBox")
    if raw_viewbox:
        values = floats(raw_viewbox)
        if len(values) == 4 and values[2] > 0 and values[3] > 0:
            bounds = (values[0], values[1], values[2], values[3])
    if bounds is None:
        width, _ = parse_dimension(root.get("width"))
        height, _ = parse_dimension(root.get("height"))
        if width is not None and height is not None:
            bounds = (0.0, 0.0, width, height)

    candidates: list[dict[str, object]] = []
    if bounds is not None:
        canvas_x, canvas_y, canvas_width, canvas_height = bounds
        canvas_right, canvas_bottom = canvas_x + canvas_width, canvas_y + canvas_height
        for index, element in enumerate(elements):
            if local(element.tag) != "rect" or element.get("transform"):
                continue
            x = first_number(element.get("x")) or 0.0
            y = first_number(element.get("y")) or 0.0
            width = first_number(element.get("width"))
            height = first_number(element.get("height"))
            if width is None or height is None:
                continue
            if x <= canvas_x and y <= canvas_y and x + width >= canvas_right and y + height >= canvas_bottom:
                candidates.append({
                    "id": element.get("id") or f"rect-{index}",
                    "tag": "rect",
                    "opaque": paint_is_opaque(element, parents),
                })

    opaque_candidates = [item for item in candidates if item["opaque"]]
    clip_count = sum(1 for element in elements if local(element.tag) == "clipPath")
    mask_count = sum(1 for element in elements if local(element.tag) == "mask")
    return {
        "canvasReliablyMeasurable": bool(canvas["reliablyMeasurable"]),
        "fullCanvasBackgroundObjectExists": bool(candidates),
        "fullCanvasBackgroundOpaque": bool(opaque_candidates),
        "fullCanvasBackgroundCandidates": candidates,
        "clipPathCount": clip_count,
        "maskCount": mask_count,
        "clippingOrMasksMayExposeCanvas": bool(clip_count or mask_count),
        "obviousFullCanvasHoles": "not-provable-from-svg-structure",
        "transparencyIntent": transparency_intent,
        "transparencyIntentDeclared": transparency_intent != "unknown",
        "renderedAlphaRequired": True,
        "structuralCoverageProven": False,
        "notes": [
            "Only an untransformed rect that obviously spans the measurable canvas is reported as a structural background candidate.",
            "SVG structure cannot prove perfect coverage or distinguish every intentional and accidental hole.",
            "Use rendered alpha evidence from render_compare.py as the coverage source of truth.",
        ],
    }


def path_bbox_heuristic(path_d: str) -> tuple[float, float] | None:
    values = floats(path_d)
    if len(values) < 4:
        return None
    pairs = [(values[index], values[index + 1]) for index in range(0, len(values) - 1, 2)]
    finite = [(x, y) for x, y in pairs if math.isfinite(x) and math.isfinite(y)]
    if not finite:
        return None
    xs, ys = zip(*finite)
    return max(xs) - min(xs), max(ys) - min(ys)


def classify_href(value: str) -> str:
    stripped = value.strip()
    if stripped.startswith("#"):
        return "internalFragment"
    if stripped.lower().startswith("data:"):
        return "embeddedData"
    return "external"


def safe_href(value: str, category: str, path_mode: str) -> str:
    value = value.strip()
    if category == "internalFragment":
        return value[:240]
    if category == "embeddedData":
        media_type = value[5:].split(";", 1)[0].split(",", 1)[0]
        return f"data:{media_type or '[redacted]'};[redacted]"
    if path_mode == "absolute":
        return value[:240]
    parsed = urlsplit(value)
    if parsed.scheme and parsed.netloc:
        return f"{parsed.scheme}://{parsed.netloc}/[redacted]"
    base, marker, fragment = value.partition("#")
    safe_base = Path(base.replace("\\", "/")).name or "[external resource]"
    return safe_base + (marker + fragment if marker else "")


def audit(
    path: Path,
    shown_path: str,
    path_mode: str,
    tiny_area: float,
    short_length: float,
    path_warning: int,
    transparency_intent: str = "unknown",
) -> dict[str, object]:
    text = path.read_text(encoding="utf-8")
    root = ET.fromstring(text)
    canvas, warnings = analyze_canvas(root)
    elements = list(root.iter())
    parents = {child: parent for parent in elements for child in parent}
    coverage_audit = structural_coverage_audit(
        root, elements, parents, canvas, transparency_intent
    )
    counts = Counter(local(element.tag) for element in elements)
    gradient_elements = [element for element in elements if local(element.tag) in {"linearGradient", "radialGradient"}]
    gradient_ids = [element.get("id") for element in gradient_elements if element.get("id")]
    gradient_id_counts = Counter(gradient_ids)
    defined_gradient_ids = set(gradient_ids)
    duplicate_gradient_ids = sorted(identifier for identifier, count in gradient_id_counts.items() if count > 1)
    definitions_without_id = sum(1 for element in gradient_elements if not element.get("id"))
    gradient_object_ids: dict[str, set[str]] = {}
    duplicates: Counter[tuple[str, str, str, str]] = Counter()
    tiny: list[str] = []
    short: list[str] = []
    degenerate: list[str] = []
    unclosed: list[str] = []
    references: dict[str, list[dict[str, str]]] = {
        "internalFragment": [], "embeddedData": [], "external": []
    }
    raster_href_detected = False

    for index, element in enumerate(elements):
        tag = local(element.tag)
        ident = element.get("id") or f"{tag}-{index}"
        for attr_name, attr_value in element.attrib.items():
            if local(attr_name) == "href":
                category = classify_href(attr_value)
                if attr_value.strip().lower().startswith("data:image") or RASTER_SUFFIX.search(attr_value.strip()):
                    raster_href_detected = True
                references[category].append({
                    "element": tag,
                    "id": ident,
                    "target": safe_href(attr_value, category, path_mode),
                })

        if tag in DRAWABLE:
            object_gradient_ids = set()
            for property_name in ("fill", "stroke"):
                object_gradient_ids.update(gradient_references(inherited_value(element, property_name, parents)))
            for gradient_id in object_gradient_ids:
                gradient_object_ids.setdefault(gradient_id, set()).add(ident)

        if tag == "path":
            d = (element.get("d") or "").strip()
            fill = (inherited_value(element, "fill", parents) or "black").strip().lower()
            if not d:
                degenerate.append(ident)
            else:
                if fill not in {"none", "transparent"} and not re.search(r"[zZ]\s*$", d):
                    unclosed.append(ident)
                bbox = path_bbox_heuristic(d)
                if bbox:
                    bbox_width, bbox_height = bbox
                    if max(0.0, bbox_width) * max(0.0, bbox_height) < tiny_area:
                        tiny.append(ident)
                    if math.hypot(bbox_width, bbox_height) < short_length:
                        short.append(ident)
            duplicates[(d, fill, inherited_value(element, "stroke", parents) or "", element.get("transform", ""))] += 1
        elif tag == "rect":
            width, height = first_number(element.get("width")), first_number(element.get("height"))
            if width is None or height is None or width <= 0 or height <= 0:
                degenerate.append(ident)
            elif width * height < tiny_area:
                tiny.append(ident)
        elif tag == "circle":
            radius = first_number(element.get("r"))
            if radius is None or radius <= 0:
                degenerate.append(ident)
            elif math.pi * radius * radius < tiny_area:
                tiny.append(ident)
        elif tag == "ellipse":
            rx, ry = first_number(element.get("rx")), first_number(element.get("ry"))
            if rx is None or ry is None or rx <= 0 or ry <= 0:
                degenerate.append(ident)
            elif math.pi * rx * ry < tiny_area:
                tiny.append(ident)
        elif tag == "line":
            x1, y1 = first_number(element.get("x1")) or 0.0, first_number(element.get("y1")) or 0.0
            x2, y2 = first_number(element.get("x2")) or 0.0, first_number(element.get("y2")) or 0.0
            if math.hypot(x2 - x1, y2 - y1) < short_length:
                short.append(ident)

    duplicate_paths = sum(count - 1 for signature, count in duplicates.items() if signature[0] and count > 1)
    raster_terms = {
        "<image": text.lower().count("<image"),
        "data:image": text.lower().count("data:image"),
        ".png": text.lower().count(".png"),
        ".jpg": text.lower().count(".jpg"),
        ".jpeg": text.lower().count(".jpeg"),
    }
    if counts["path"] > path_warning:
        warnings.append({"code": "path-count", "message": f"path count {counts['path']} exceeds advisory threshold {path_warning}"})
    if any(raster_terms.values()) or raster_href_detected or counts["image"]:
        warnings.append({"code": "raster-reference", "message": "<image> or embedded/linked raster content detected"})
    if references["external"]:
        warnings.append({"code": "external-resource", "message": f"{len(references['external'])} external local/remote resource reference(s) detected"})
    if references["embeddedData"]:
        warnings.append({"code": "embedded-data", "message": f"{len(references['embeddedData'])} embedded data reference(s) detected"})
    if counts["foreignObject"]:
        warnings.append({"code": "foreign-object", "message": f"{counts['foreignObject']} foreignObject element(s) detected"})
    referenced_gradient_ids = set(gradient_object_ids)
    used_gradient_ids = sorted(referenced_gradient_ids & defined_gradient_ids)
    unused_gradient_ids = sorted(defined_gradient_ids - referenced_gradient_ids)
    missing_gradient_ids = sorted(referenced_gradient_ids - defined_gradient_ids)
    if definitions_without_id:
        warnings.append({"code": "gradient-without-id", "message": f"{definitions_without_id} gradient definition(s) have no ID"})
    if duplicate_gradient_ids:
        warnings.append({"code": "duplicate-gradient-id", "message": "duplicate gradient ID(s): " + ", ".join(duplicate_gradient_ids)})
    if unused_gradient_ids:
        warnings.append({"code": "unused-gradient", "message": "defined but unused gradient ID(s): " + ", ".join(unused_gradient_ids)})
    if missing_gradient_ids:
        warnings.append({"code": "missing-gradient-reference", "message": "object fill/stroke references missing gradient ID(s): " + ", ".join(missing_gradient_ids)})
    for code, items, label in (
        ("unclosed-fill-heuristic", unclosed, "possibly unclosed filled path candidates"),
        ("degenerate-heuristic", degenerate, "degenerate object candidates"),
        ("tiny-heuristic", tiny, "extremely small object candidates"),
        ("short-heuristic", short, "very short object candidates"),
    ):
        if items:
            warnings.append({"code": code, "message": f"{len(items)} {label}"})
    if duplicate_paths:
        warnings.append({"code": "duplicate-path-heuristic", "message": f"{duplicate_paths} exact duplicate path candidates"})

    group_sizes = []
    for index, group in enumerate(element for element in elements if local(element.tag) == "g"):
        ident = group.get("id") or f"unnamed-group-{index}"
        group_sizes.append((ident, sum(1 for child in group.iter() if local(child.tag) in DRAWABLE)))

    gradient_audit = {
        "definedLinearGradientCount": counts["linearGradient"],
        "definedRadialGradientCount": counts["radialGradient"],
        "definedGradientIds": sorted(defined_gradient_ids),
        "definitionsWithoutId": definitions_without_id,
        "referencedGradientIds": sorted(referenced_gradient_ids),
        "usedGradientCount": len(used_gradient_ids),
        "usedGradientIds": used_gradient_ids,
        "unusedGradientIds": unused_gradient_ids,
        "missingGradientReferences": missing_gradient_ids,
        "duplicateGradientIds": duplicate_gradient_ids,
        "objectsUsingEachGradient": {
            gradient_id: {
                "count": len(object_ids),
                "objectIds": sorted(object_ids),
            }
            for gradient_id, object_ids in sorted(gradient_object_ids.items())
        },
    }

    return {
        "file": shown_path,
        "pathMode": path_mode,
        "xmlParses": True,
        "rootElement": local(root.tag),
        "canvas": canvas,
        "counts": {name: counts[name] for name in COUNTED},
        "gradientAudit": gradient_audit,
        "coverageAudit": coverage_audit,
        "totalDrawableObjects": sum(counts[name] for name in DRAWABLE),
        "rasterTerms": raster_terms,
        "resourceReferences": references,
        "possiblyUnclosedFilledPathCandidates": unclosed,
        "degenerateObjectCandidates": degenerate,
        "tinyObjectCandidates": tiny,
        "veryShortObjectCandidates": short,
        "exactDuplicatePathCandidates": duplicate_paths,
        "largestGroups": sorted(group_sizes, key=lambda item: item[1], reverse=True)[:10],
        "warnings": warnings,
        "notes": [
            "Path closure, numeric path bounding boxes, tiny/short objects, duplicates, and overlaps are heuristics that require interpretation.",
            "A filled open SVG path may render as visually closed; an open-path warning does not prove a defect.",
            "Numeric coordinate pairing is not a complete Bezier geometry engine and cannot prove geometric quality.",
            "Automatic auditing does not prove Illustrator editability, design quality, or a passing human grade.",
            "Actual gradient use does not prove visual fidelity.",
            "Human review must compare gradient placement, direction, colors, stops, transition extent, and opacity with the reference.",
        ],
    }


def markdown(results: list[dict[str, object]]) -> str:
    lines = ["# SVG Audit", ""]
    for result in results:
        canvas = result["canvas"]
        references = result["resourceReferences"]
        gradients = result["gradientAudit"]
        coverage = result["coverageAudit"]
        lines += [
            f"## `{result['file']}`", "",
            f"- Path display mode: `{result['pathMode']}`",
            f"- XML parses: {'yes' if result['xmlParses'] else 'no'}",
            f"- Root element: `{result['rootElement']}`",
            f"- Canvas status: **{canvas['status']}**",
            f"- Dimensions: `{canvas['width']}` × `{canvas['height']}`",
            f"- viewBox: `{canvas['viewBox']}`",
            f"- Measured aspect ratio: `{canvas['aspectRatio']}` (source: `{canvas['source']}`)",
            f"- Total drawable objects: {result['totalDrawableObjects']}",
            f"- Raster/image elements: {result['counts']['image']}",
            f"- External resources: {len(references['external'])}",
            f"- Embedded data references: {len(references['embeddedData'])}",
            f"- Internal fragment references: {len(references['internalFragment'])}",
            "", "| Element | Count |", "|---|---:|",
        ]
        lines.extend(f"| `{name}` | {count} |" for name, count in result["counts"].items())
        lines += [
            "", "### Gradient usage audit", "",
            f"- Defined linear gradients: {gradients['definedLinearGradientCount']}",
            f"- Defined radial gradients: {gradients['definedRadialGradientCount']}",
            f"- Defined gradient IDs: {', '.join(f'`{item}`' for item in gradients['definedGradientIds']) or 'none'}",
            f"- Gradient IDs referenced by object fill/stroke: {', '.join(f'`{item}`' for item in gradients['referencedGradientIds']) or 'none'}",
            f"- Used gradient count: {gradients['usedGradientCount']}",
            f"- Unused gradient IDs: {', '.join(f'`{item}`' for item in gradients['unusedGradientIds']) or 'none'}",
            f"- Missing gradient references: {', '.join(f'`{item}`' for item in gradients['missingGradientReferences']) or 'none'}",
            f"- Duplicate gradient IDs: {', '.join(f'`{item}`' for item in gradients['duplicateGradientIds']) or 'none'}",
            "", "| Gradient ID | Object count | Object IDs |", "|---|---:|---|",
        ]
        if gradients["objectsUsingEachGradient"]:
            for gradient_id, usage in gradients["objectsUsingEachGradient"].items():
                lines.append(f"| `{gradient_id}` | {usage['count']} | {', '.join(f'`{item}`' for item in usage['objectIds'])} |")
        else:
            lines.append("| — | 0 | — |")
        lines += [
            "", "### Structural coverage audit", "",
            f"- Full-canvas background candidate exists: {'yes' if coverage['fullCanvasBackgroundObjectExists'] else 'no'}",
            f"- Opaque full-canvas background candidate exists: {'yes' if coverage['fullCanvasBackgroundOpaque'] else 'no'}",
            f"- clipPath count: {coverage['clipPathCount']}",
            f"- mask count: {coverage['maskCount']}",
            f"- Clipping or masks may expose canvas: {'yes' if coverage['clippingOrMasksMayExposeCanvas'] else 'no'}",
            f"- Case-declared transparency intent: `{coverage['transparencyIntent']}`",
            "- Structural proof of complete coverage: no; rendered alpha evidence is required.",
        ]
        lines += ["", "### Warnings", ""]
        if result["warnings"]:
            lines.extend(f"- **{item['code']}**: {item['message']}" for item in result["warnings"])
        else:
            lines.append("- None detected by this structural audit.")
        lines += ["", *[f"- Note: {note}" for note in result["notes"]], ""]
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Audit SVG structure, canvas, and resource references without modifying inputs.")
    parser.add_argument("svg", nargs="+", type=Path, help="SVG file(s) to inspect.")
    parser.add_argument("--format", choices=["markdown", "json"], default="markdown")
    parser.add_argument("--path-mode", choices=["basename", "relative", "absolute"], default="relative", help="Path display policy for reports.")
    parser.add_argument("--tiny-area", type=float, default=4.0, help="Advisory tiny-object area threshold.")
    parser.add_argument("--short-length", type=float, default=2.0, help="Advisory short-object length threshold.")
    parser.add_argument("--path-warning", type=int, default=300, help="Advisory path-count threshold.")
    parser.add_argument(
        "--transparency-intent",
        choices=["opaque", "intentional", "unknown"],
        default="unknown",
        help="Case-authored transparency intent; structural analysis does not infer intent.",
    )
    parser.add_argument("--fail-on-warning", action="store_true", help="Return exit code 2 if warnings exist.")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    cwd = Path.cwd().resolve()
    results: list[dict[str, object]] = []
    for svg in args.svg:
        shown = display_path(svg, args.path_mode, cwd)
        if not svg.is_file():
            raise FileNotFoundError(f"SVG not found: {shown}")
        actual = svg.resolve()
        results.append(
            audit(
                actual,
                shown,
                args.path_mode,
                args.tiny_area,
                args.short_length,
                args.path_warning,
                args.transparency_intent,
            )
        )
    print(json.dumps(results, indent=2, ensure_ascii=False) if args.format == "json" else markdown(results))
    return 2 if args.fail_on_warning and any(result["warnings"] for result in results) else 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        raise SystemExit(130)
    except (OSError, ET.ParseError, ValueError) as exc:
        print(f"SVG audit failed: {exc}", file=sys.stderr)
        raise SystemExit(1)
