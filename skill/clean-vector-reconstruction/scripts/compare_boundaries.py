#!/usr/bin/env python3
"""Compare reference and candidate raster boundaries with one frozen configuration."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import os
import re
import tempfile
from collections import deque
from pathlib import Path, PureWindowsPath
from typing import Any


REGION_NAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{0,63}$")
DEFAULT_MAX_REGIONS = 8
ABSOLUTE_MAX_REGIONS = 12


def require_dependencies():
    try:
        import numpy as np
        from PIL import Image, ImageFilter
    except ImportError as exc:
        raise RuntimeError("Pillow and NumPy are required for boundary comparison but are unavailable") from exc
    return np, Image, ImageFilter


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


def validate_prefix(prefix: str) -> str:
    if not prefix or not prefix.strip():
        raise ValueError("--prefix must not be empty")
    windows = PureWindowsPath(prefix)
    if prefix in {".", ".."} or ".." in prefix or "/" in prefix or "\\" in prefix:
        raise ValueError("--prefix must be a filename stem without path traversal")
    if Path(prefix).is_absolute() or windows.is_absolute() or windows.drive or ":" in prefix or "\x00" in prefix:
        raise ValueError("--prefix contains an unsafe filename character")
    return prefix


def _finite_number(value: object, label: str, minimum: float | None = None) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(float(value)):
        raise ValueError(f"{label} must be a finite number")
    result = float(value)
    if minimum is not None and result < minimum:
        raise ValueError(f"{label} must be at least {minimum}")
    return result


def _positive_int(value: object, label: str, maximum: int | None = None) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise ValueError(f"{label} must be a positive integer")
    if maximum is not None and value > maximum:
        raise ValueError(f"{label} must not exceed {maximum}")
    return value


def _optional_positive_int(value: object, label: str) -> int | None:
    if value is None:
        return None
    return _positive_int(value, label)


def canonical_hash(payload: object) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def load_method_config(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise FileNotFoundError("boundary method config not found")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"malformed boundary method config JSON: {exc.msg}") from exc
    if not isinstance(payload, dict):
        raise ValueError("boundary method config must be an object")

    allowed = {
        "version", "fullRenderSize", "analysisSize", "preprocessing", "extraction",
        "tolerancesFullPixels", "maxRegions", "output",
    }
    unknown = sorted(set(payload) - allowed)
    if unknown:
        raise ValueError("unsupported config keys (candidate-specific tuning is forbidden): " + ", ".join(unknown))
    if payload.get("version") != 1:
        raise ValueError("config version must be 1")

    full = payload.get("fullRenderSize")
    if not isinstance(full, dict) or set(full) != {"width", "height"}:
        raise ValueError("fullRenderSize must contain only width and height")
    full_width = _optional_positive_int(full["width"], "fullRenderSize.width")
    full_height = _optional_positive_int(full["height"], "fullRenderSize.height")
    if (full_width is None) != (full_height is None):
        raise ValueError("fullRenderSize width and height must both be null or both be positive integers")

    analysis = payload.get("analysisSize")
    if not isinstance(analysis, dict):
        raise ValueError("analysisSize must be an object")
    if set(analysis) == {"maxDimension"}:
        analysis_spec = {"maxDimension": _positive_int(analysis["maxDimension"], "analysisSize.maxDimension", 4096)}
    elif set(analysis) == {"width", "height"}:
        analysis_spec = {
            "width": _positive_int(analysis["width"], "analysisSize.width", 4096),
            "height": _positive_int(analysis["height"], "analysisSize.height", 4096),
        }
    else:
        raise ValueError("analysisSize must contain maxDimension or width and height")

    preprocessing = payload.get("preprocessing")
    if not isinstance(preprocessing, dict) or set(preprocessing) != {"blurRadius"}:
        raise ValueError("preprocessing must contain only blurRadius")
    blur_radius = _finite_number(preprocessing["blurRadius"], "preprocessing.blurRadius", 0.0)
    if blur_radius > 5.0:
        raise ValueError("preprocessing.blurRadius must not exceed 5.0 analysis pixels")

    extraction = payload.get("extraction")
    expected_extraction = {
        "colorSpace", "gradientOperator", "nonMaximumSuppression", "thresholdMethod",
        "thresholdFloor", "highPercentileClip", "lowHighRatio", "minimumComponentSize",
    }
    if not isinstance(extraction, dict) or set(extraction) != expected_extraction:
        raise ValueError("extraction keys must match the documented v1 schema")
    if extraction["colorSpace"] != "CIELAB-D65":
        raise ValueError("extraction.colorSpace must be CIELAB-D65")
    if extraction["gradientOperator"] != "sobel-3x3":
        raise ValueError("extraction.gradientOperator must be sobel-3x3")
    if extraction["nonMaximumSuppression"] is not True:
        raise ValueError("nonMaximumSuppression must be true")
    if extraction["thresholdMethod"] not in {"reference-otsu", "fixed"}:
        raise ValueError("thresholdMethod must be reference-otsu or fixed")
    threshold_floor = _finite_number(extraction["thresholdFloor"], "extraction.thresholdFloor", 0.0)
    percentile = _finite_number(extraction["highPercentileClip"], "extraction.highPercentileClip", 50.0)
    if percentile > 100.0:
        raise ValueError("extraction.highPercentileClip must not exceed 100")
    ratio = _finite_number(extraction["lowHighRatio"], "extraction.lowHighRatio", 0.01)
    if ratio >= 1.0:
        raise ValueError("extraction.lowHighRatio must be below 1")
    min_component = _positive_int(extraction["minimumComponentSize"], "extraction.minimumComponentSize", 10000)

    tolerances_raw = payload.get("tolerancesFullPixels")
    if not isinstance(tolerances_raw, list) or not tolerances_raw or len(tolerances_raw) > 8:
        raise ValueError("tolerancesFullPixels must contain 1–8 values")
    tolerances = sorted({_finite_number(item, "tolerancesFullPixels item", 0.0) for item in tolerances_raw})
    if not tolerances or tolerances[0] <= 0:
        raise ValueError("tolerancesFullPixels values must be positive")

    max_regions = _positive_int(payload.get("maxRegions", DEFAULT_MAX_REGIONS), "maxRegions", ABSOLUTE_MAX_REGIONS)
    output = payload.get("output")
    output_keys = {"writeCsv", "boundaryMaps", "mismatchVisualizations", "visualizationToleranceFullPixels"}
    if not isinstance(output, dict) or set(output) != output_keys:
        raise ValueError("output keys must match the documented v1 schema")
    for key in ("writeCsv", "boundaryMaps", "mismatchVisualizations"):
        if not isinstance(output[key], bool):
            raise ValueError(f"output.{key} must be boolean")
    visual_tolerance = _finite_number(
        output["visualizationToleranceFullPixels"], "output.visualizationToleranceFullPixels", 0.0
    )
    if visual_tolerance <= 0:
        raise ValueError("output.visualizationToleranceFullPixels must be positive")

    validated = {
        "version": 1,
        "fullRenderSize": {"width": full_width, "height": full_height},
        "analysisSize": analysis_spec,
        "preprocessing": {"blurRadius": blur_radius},
        "extraction": {
            "colorSpace": "CIELAB-D65",
            "gradientOperator": "sobel-3x3",
            "nonMaximumSuppression": True,
            "thresholdMethod": extraction["thresholdMethod"],
            "thresholdFloor": threshold_floor,
            "highPercentileClip": percentile,
            "lowHighRatio": ratio,
            "minimumComponentSize": min_component,
        },
        "tolerancesFullPixels": tolerances,
        "maxRegions": max_regions,
        "output": {
            "writeCsv": output["writeCsv"],
            "boundaryMaps": output["boundaryMaps"],
            "mismatchVisualizations": output["mismatchVisualizations"],
            "visualizationToleranceFullPixels": visual_tolerance,
        },
    }
    return validated


def resolve_sizes(config: dict[str, Any], image_size: tuple[int, int]) -> tuple[tuple[int, int], float]:
    width, height = image_size
    declared = config["fullRenderSize"]
    if declared["width"] is not None and (declared["width"], declared["height"]) != image_size:
        raise ValueError("input dimensions do not match fullRenderSize")
    analysis = config["analysisSize"]
    if "maxDimension" in analysis:
        scale = min(1.0, analysis["maxDimension"] / max(width, height))
        analysis_size = (max(1, round(width * scale)), max(1, round(height * scale)))
    else:
        analysis_size = (analysis["width"], analysis["height"])
        scale_x = analysis_size[0] / width
        scale_y = analysis_size[1] / height
        if not math.isclose(scale_x, scale_y, rel_tol=1e-6, abs_tol=1e-9):
            raise ValueError("analysisSize must preserve the full-render aspect ratio and uniform distance scale")
        scale = scale_x
    return analysis_size, scale


def srgb_to_lab(rgb, np):
    values = rgb.astype(np.float64) / 255.0
    linear = np.where(values <= 0.04045, values / 12.92, ((values + 0.055) / 1.055) ** 2.4)
    matrix = np.array([
        [0.4124564, 0.3575761, 0.1804375],
        [0.2126729, 0.7151522, 0.0721750],
        [0.0193339, 0.1191920, 0.9503041],
    ])
    xyz = linear @ matrix.T
    xyz /= np.array([0.95047, 1.0, 1.08883])
    delta = 6.0 / 29.0
    transformed = np.where(xyz > delta ** 3, np.cbrt(xyz), xyz / (3 * delta ** 2) + 4.0 / 29.0)
    x, y, z = transformed[..., 0], transformed[..., 1], transformed[..., 2]
    return np.stack((116 * y - 16, 500 * (x - y), 200 * (y - z)), axis=-1)


def sobel_lab(lab, np):
    padded = np.pad(lab, ((1, 1), (1, 1), (0, 0)), mode="edge")
    gx = (
        padded[:-2, 2:] + 2 * padded[1:-1, 2:] + padded[2:, 2:]
        - padded[:-2, :-2] - 2 * padded[1:-1, :-2] - padded[2:, :-2]
    )
    gy = (
        padded[2:, :-2] + 2 * padded[2:, 1:-1] + padded[2:, 2:]
        - padded[:-2, :-2] - 2 * padded[:-2, 1:-1] - padded[:-2, 2:]
    )
    magnitude = np.sqrt(np.sum(gx * gx + gy * gy, axis=2))
    dominant = np.argmax(gx * gx + gy * gy, axis=2)[..., None]
    direction_x = np.take_along_axis(gx, dominant, axis=2)[..., 0]
    direction_y = np.take_along_axis(gy, dominant, axis=2)[..., 0]
    angle = (np.rad2deg(np.arctan2(direction_y, direction_x)) + 180.0) % 180.0
    return magnitude, angle


def nonmaximum_suppression(magnitude, angle, np):
    padded = np.pad(magnitude, 1, mode="constant")
    left, right = padded[1:-1, :-2], padded[1:-1, 2:]
    up, down = padded[:-2, 1:-1], padded[2:, 1:-1]
    up_right, down_left = padded[:-2, 2:], padded[2:, :-2]
    up_left, down_right = padded[:-2, :-2], padded[2:, 2:]
    result = np.zeros_like(magnitude)
    masks = (
        (((angle < 22.5) | (angle >= 157.5)), left, right),
        (((angle >= 22.5) & (angle < 67.5)), up_right, down_left),
        (((angle >= 67.5) & (angle < 112.5)), up, down),
        (((angle >= 112.5) & (angle < 157.5)), up_left, down_right),
    )
    for mask, first, second in masks:
        keep = mask & (magnitude >= first) & (magnitude >= second)
        result[keep] = magnitude[keep]
    result[[0, -1], :] = 0
    result[:, [0, -1]] = 0
    return result


def otsu_threshold(values, upper: float, np) -> float:
    clipped = np.clip(values, 0.0, upper)
    histogram, edges = np.histogram(clipped, bins=256, range=(0.0, upper))
    total = int(histogram.sum())
    if total == 0:
        return 0.0
    centers = (edges[:-1] + edges[1:]) / 2.0
    cumulative_count = np.cumsum(histogram)
    cumulative_weight = np.cumsum(histogram * centers)
    denominator = cumulative_count * (total - cumulative_count)
    numerator = (cumulative_weight[-1] * cumulative_count - cumulative_weight) ** 2
    score = np.divide(numerator, denominator, out=np.zeros_like(numerator, dtype=float), where=denominator > 0)
    return float(centers[int(np.argmax(score))])


def resolve_thresholds(reference_nms, config: dict[str, Any], np) -> dict[str, float]:
    extraction = config["extraction"]
    nonzero = reference_nms[reference_nms > 0]
    if nonzero.size == 0:
        raise ValueError("reference contains no extractable color-discontinuity boundaries")
    clip = float(np.percentile(nonzero, extraction["highPercentileClip"]))
    if extraction["thresholdMethod"] == "reference-otsu":
        derived = otsu_threshold(nonzero, max(clip, 1e-9), np)
        high = max(extraction["thresholdFloor"], derived)
    else:
        high = extraction["thresholdFloor"]
        derived = high
        if high <= 0:
            raise ValueError("fixed thresholdMethod requires a positive thresholdFloor")
    return {
        "high": float(high),
        "low": float(high * extraction["lowHighRatio"]),
        "referencePercentileClip": clip,
        "referenceDerivedThreshold": float(derived),
    }


def hysteresis(nms, low: float, high: float, np):
    weak = nms >= low
    strong_points = np.argwhere(nms >= high)
    retained = np.zeros(weak.shape, dtype=bool)
    queue = deque((int(y), int(x)) for y, x in strong_points)
    height, width = weak.shape
    for y, x in queue:
        retained[y, x] = True
    while queue:
        y, x = queue.popleft()
        for ny in range(max(0, y - 1), min(height, y + 2)):
            for nx in range(max(0, x - 1), min(width, x + 2)):
                if weak[ny, nx] and not retained[ny, nx]:
                    retained[ny, nx] = True
                    queue.append((ny, nx))
    return retained


def filter_small_components(mask, minimum_size: int, np):
    if minimum_size <= 1:
        return mask.copy()
    height, width = mask.shape
    visited = np.zeros(mask.shape, dtype=bool)
    retained = np.zeros(mask.shape, dtype=bool)
    for start_y, start_x in np.argwhere(mask):
        y0, x0 = int(start_y), int(start_x)
        if visited[y0, x0]:
            continue
        component: list[tuple[int, int]] = []
        queue = deque([(y0, x0)])
        visited[y0, x0] = True
        while queue:
            y, x = queue.popleft()
            component.append((y, x))
            for ny in range(max(0, y - 1), min(height, y + 2)):
                for nx in range(max(0, x - 1), min(width, x + 2)):
                    if mask[ny, nx] and not visited[ny, nx]:
                        visited[ny, nx] = True
                        queue.append((ny, nx))
        if len(component) >= minimum_size:
            ys, xs = zip(*component)
            retained[list(ys), list(xs)] = True
    return retained


def prepare_nms(rgb_image, blur_radius: float, np, ImageFilter):
    image = rgb_image.convert("RGB")
    if blur_radius > 0:
        image = image.filter(ImageFilter.GaussianBlur(radius=blur_radius))
    lab = srgb_to_lab(np.asarray(image), np)
    magnitude, angle = sobel_lab(lab, np)
    return nonmaximum_suppression(magnitude, angle, np)


def extract_with_resolved(nms, resolved_thresholds: dict[str, float], minimum_size: int, np):
    connected = hysteresis(nms, resolved_thresholds["low"], resolved_thresholds["high"], np)
    return filter_small_components(connected, minimum_size, np)


def extract_boundary_pair(reference_image, candidate_image, config: dict[str, Any], np, ImageFilter):
    reference_nms = prepare_nms(reference_image, config["preprocessing"]["blurRadius"], np, ImageFilter)
    candidate_nms = prepare_nms(candidate_image, config["preprocessing"]["blurRadius"], np, ImageFilter)
    resolved = resolve_thresholds(reference_nms, config, np)
    minimum = config["extraction"]["minimumComponentSize"]
    reference_boundaries = extract_with_resolved(reference_nms, resolved, minimum, np)
    candidate_boundaries = extract_with_resolved(candidate_nms, resolved, minimum, np)
    return reference_boundaries, candidate_boundaries, resolved


def _edt_1d(values, np):
    finite = np.flatnonzero(np.isfinite(values))
    length = values.shape[0]
    if finite.size == 0:
        return np.full(length, np.inf, dtype=float)
    vertices = np.empty(finite.size, dtype=np.int64)
    intersections = np.empty(finite.size + 1, dtype=float)
    k = 0
    vertices[0] = finite[0]
    intersections[0] = -np.inf
    intersections[1] = np.inf
    for q_value in finite[1:]:
        q = int(q_value)
        while True:
            p = int(vertices[k])
            s = ((values[q] + q * q) - (values[p] + p * p)) / (2.0 * (q - p))
            if s > intersections[k] or k == 0:
                break
            k -= 1
        if s <= intersections[k] and k == 0:
            k = -1
        k += 1
        vertices[k] = q
        intersections[k] = s
        intersections[k + 1] = np.inf
    result = np.empty(length, dtype=float)
    k = 0
    for q in range(length):
        while intersections[k + 1] < q:
            k += 1
        delta = q - int(vertices[k])
        result[q] = delta * delta + values[int(vertices[k])]
    return result


def distance_transform(boundary_mask, np):
    if not bool(boundary_mask.any()):
        return np.full(boundary_mask.shape, np.inf, dtype=float)
    first = np.empty(boundary_mask.shape, dtype=float)
    source = np.where(boundary_mask, 0.0, np.inf)
    for row in range(source.shape[0]):
        first[row, :] = _edt_1d(source[row, :], np)
    second = np.empty(boundary_mask.shape, dtype=float)
    for column in range(source.shape[1]):
        second[:, column] = _edt_1d(first[:, column], np)
    return np.sqrt(second)


def distance_statistics(samples, scale_to_full: float, np) -> dict[str, object]:
    if samples.size == 0:
        return {"count": 0, "mean": None, "median": None, "p90": None, "p95": None, "unmatched": False}
    if not bool(np.isfinite(samples).all()):
        return {"count": int(samples.size), "mean": None, "median": None, "p90": None, "p95": None, "unmatched": True}
    scaled = samples * scale_to_full
    return {
        "count": int(samples.size),
        "mean": float(np.mean(scaled)),
        "median": float(np.median(scaled)),
        "p90": float(np.percentile(scaled, 90)),
        "p95": float(np.percentile(scaled, 95)),
        "unmatched": False,
    }


def compute_metrics(reference_mask, candidate_mask, tolerances_analysis: list[float], scale_to_full: float, np, sample_mask=None):
    if sample_mask is None:
        sample_mask = np.ones(reference_mask.shape, dtype=bool)
    reference_samples = reference_mask & sample_mask
    candidate_samples = candidate_mask & sample_mask
    to_reference = distance_transform(reference_mask, np)
    to_candidate = distance_transform(candidate_mask, np)
    reference_distances = to_candidate[reference_samples]
    candidate_distances = to_reference[candidate_samples]
    tolerance_rows = []
    ref_count = int(reference_samples.sum())
    candidate_count = int(candidate_samples.sum())
    for tolerance_analysis in tolerances_analysis:
        precision = None if candidate_count == 0 else float(np.mean(candidate_distances <= tolerance_analysis))
        recall = None if ref_count == 0 else float(np.mean(reference_distances <= tolerance_analysis))
        if precision is None and recall is None:
            f1 = None
        elif precision is None or recall is None:
            f1 = 0.0
        elif precision + recall == 0:
            f1 = 0.0
        else:
            f1 = 2.0 * precision * recall / (precision + recall)
        tolerance_rows.append({
            "fullPixels": float(tolerance_analysis * scale_to_full),
            "analysisPixels": float(tolerance_analysis),
            "precision": precision,
            "recall": recall,
            "f1": f1,
        })
    return {
        "referenceBoundaryCount": ref_count,
        "candidateBoundaryCount": candidate_count,
        "referenceToCandidate": distance_statistics(reference_distances, scale_to_full, np),
        "candidateToReference": distance_statistics(candidate_distances, scale_to_full, np),
        "tolerances": tolerance_rows,
    }, to_reference, to_candidate


def validate_region_name(name: object) -> str:
    if not isinstance(name, str) or not REGION_NAME.fullmatch(name):
        raise ValueError("region names must use 1–64 ASCII letters, digits, hyphens, or underscores")
    if name in {".", ".."} or ".." in name or "/" in name or "\\" in name or ":" in name:
        raise ValueError("region name contains traversal or an unsafe filename character")
    return name


def load_regions(path: Path, maximum: int) -> tuple[str, list[dict[str, object]]]:
    if not path.is_file():
        raise FileNotFoundError("boundary regions file not found")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"malformed boundary regions JSON: {exc.msg}") from exc
    if not isinstance(payload, dict) or set(payload) != {"coordinateMode", "regions"}:
        raise ValueError("boundary regions JSON must contain only coordinateMode and regions")
    mode = payload["coordinateMode"]
    if mode not in {"normalized", "pixels"}:
        raise ValueError("coordinateMode must be normalized or pixels")
    raw_regions = payload["regions"]
    if not isinstance(raw_regions, list) or not raw_regions:
        raise ValueError("regions must be a non-empty list")
    if len(raw_regions) > maximum:
        raise ValueError(f"regions list exceeds configured maximum of {maximum}")
    result = []
    seen: set[str] = set()
    for raw in raw_regions:
        if not isinstance(raw, dict) or set(raw) != {"name", "x", "y", "width", "height"}:
            raise ValueError("each region must contain name, x, y, width, and height")
        name = validate_region_name(raw["name"])
        folded = name.casefold()
        if folded in seen:
            raise ValueError(f"duplicate region name: {name}")
        seen.add(folded)
        values = [raw[key] for key in ("x", "y", "width", "height")]
        if mode == "pixels":
            if any(isinstance(value, bool) or not isinstance(value, int) for value in values):
                raise ValueError(f"pixel coordinates for region '{name}' must be integers")
        else:
            if any(isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(float(value)) for value in values):
                raise ValueError(f"normalized coordinates for region '{name}' must be finite numbers")
        x, y, width, height = map(float, values)
        if x < 0 or y < 0:
            raise ValueError(f"region '{name}' has negative coordinates")
        if width <= 0 or height <= 0:
            raise ValueError(f"region '{name}' has zero or negative area")
        if mode == "normalized" and (x + width > 1 or y + height > 1):
            raise ValueError(f"region '{name}' is out of normalized bounds")
        result.append(dict(raw))
    return mode, result


def region_boxes(mode: str, regions: list[dict[str, object]], full_size: tuple[int, int], analysis_size: tuple[int, int]):
    full_width, full_height = full_size
    analysis_width, analysis_height = analysis_size
    boxes = []
    for region in regions:
        if mode == "pixels":
            left, top = int(region["x"]), int(region["y"])
            right = left + int(region["width"])
            bottom = top + int(region["height"])
            if right > full_width or bottom > full_height:
                raise ValueError(f"region '{region['name']}' is out of image bounds")
            normalized = (left / full_width, top / full_height, right / full_width, bottom / full_height)
        else:
            normalized = (
                float(region["x"]), float(region["y"]),
                float(region["x"]) + float(region["width"]),
                float(region["y"]) + float(region["height"]),
            )
        a_left = max(0, math.floor(normalized[0] * analysis_width))
        a_top = max(0, math.floor(normalized[1] * analysis_height))
        a_right = min(analysis_width, math.ceil(normalized[2] * analysis_width))
        a_bottom = min(analysis_height, math.ceil(normalized[3] * analysis_height))
        if a_right <= a_left or a_bottom <= a_top:
            raise ValueError(f"region '{region['name']}' becomes empty at analysis dimensions")
        boxes.append({
            **region,
            "fullPixelBox": [
                math.floor(normalized[0] * full_width), math.floor(normalized[1] * full_height),
                math.ceil(normalized[2] * full_width), math.ceil(normalized[3] * full_height),
            ],
            "analysisPixelBox": [a_left, a_top, a_right, a_bottom],
        })
    return boxes


def boundary_image(mask, np, Image):
    return Image.fromarray(np.where(mask, 255, 0).astype(np.uint8), mode="L")


def mismatch_image(reference_mask, candidate_mask, to_reference, to_candidate, tolerance: float, np, Image):
    close_reference = reference_mask & (to_candidate <= tolerance)
    close_candidate = candidate_mask & (to_reference <= tolerance)
    reference_only = reference_mask & ~close_reference
    candidate_only = candidate_mask & ~close_candidate
    overlap = close_reference | close_candidate
    rgb = np.zeros((*reference_mask.shape, 3), dtype=np.uint8)
    rgb[reference_only] = (255, 70, 70)
    rgb[candidate_only] = (40, 220, 255)
    rgb[overlap] = (245, 245, 245)
    return Image.fromarray(rgb, mode="RGB")


def commit_outputs(staged: dict[str, Path], final: dict[str, Path], overwrite: bool, temp_dir: Path) -> None:
    backups: dict[str, Path] = {}
    committed: list[str] = []
    try:
        if overwrite:
            for name, target in final.items():
                if target.exists():
                    backup = temp_dir / ("backup-" + re.sub(r"[^A-Za-z0-9_-]", "_", name))
                    os.replace(target, backup)
                    backups[name] = backup
        for name, target in final.items():
            if target.exists() and not overwrite:
                raise FileExistsError(f"refusing to overwrite existing output: {target.name}")
            os.replace(staged[name], target)
            committed.append(name)
    except Exception:
        for name in committed:
            if final[name].exists():
                final[name].unlink()
        for name, backup in backups.items():
            if backup.exists():
                os.replace(backup, final[name])
        raise


def csv_rows(report: dict[str, Any]):
    for scope, name, metrics in [("global", "global", report["globalMetrics"])] + [
        ("region", item["name"], item["metrics"]) for item in report["regions"]
    ]:
        row = {
            "scope": scope,
            "name": name,
            "reference_boundary_count": metrics["referenceBoundaryCount"],
            "candidate_boundary_count": metrics["candidateBoundaryCount"],
        }
        for prefix, key in (("ref_to_candidate", "referenceToCandidate"), ("candidate_to_ref", "candidateToReference")):
            for stat in ("mean", "median", "p90", "p95"):
                row[f"{prefix}_{stat}_full_px"] = metrics[key][stat]
        for index, tolerance in enumerate(metrics["tolerances"], start=1):
            row[f"t{index}_full_px"] = tolerance["fullPixels"]
            row[f"t{index}_precision"] = tolerance["precision"]
            row[f"t{index}_recall"] = tolerance["recall"]
            row[f"t{index}_f1"] = tolerance["f1"]
        yield row


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Compare a reference raster and same-render candidate raster using one reference-resolved boundary configuration."
    )
    parser.add_argument("reference", type=Path, help="Original reference raster.")
    parser.add_argument("candidate", type=Path, help="Candidate raster produced by the existing safe same-render workflow.")
    parser.add_argument("--config", type=Path, required=True, help="Boundary validation method config JSON.")
    parser.add_argument("--output-dir", type=Path, required=True, help="Directory for atomic metrics and visualizations.")
    parser.add_argument("--regions-file", type=Path, help="Optional named rectangular boundary regions JSON.")
    parser.add_argument("--prefix", help="Safe filename stem; defaults to the candidate stem.")
    parser.add_argument("--overwrite", action="store_true", help="Replace an existing complete output set with rollback protection.")
    parser.add_argument("--path-mode", choices=["basename", "relative", "absolute"], default="relative")
    parser.add_argument("--format", choices=["json", "markdown"], default="markdown", help="Standard-output summary format.")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    np, Image, ImageFilter = require_dependencies()
    cwd = Path.cwd().resolve()
    reference_path = args.reference.resolve()
    candidate_path = args.candidate.resolve()
    if not reference_path.is_file():
        raise FileNotFoundError(f"reference not found: {display_path(reference_path, args.path_mode, cwd)}")
    if not candidate_path.is_file():
        raise FileNotFoundError(f"candidate not found: {display_path(candidate_path, args.path_mode, cwd)}")
    config = load_method_config(args.config.resolve())
    method_hash = canonical_hash(config)
    prefix = validate_prefix(args.prefix or candidate_path.stem)
    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    with Image.open(reference_path) as opened_reference, Image.open(candidate_path) as opened_candidate:
        reference = opened_reference.convert("RGB")
        candidate = opened_candidate.convert("RGB")
    if reference.size != candidate.size:
        raise ValueError("reference and candidate raster dimensions must be identical")
    analysis_size, analysis_scale = resolve_sizes(config, reference.size)
    if analysis_scale <= 0:
        raise ValueError("invalid analysis scale")
    reference_analysis = reference.resize(analysis_size, Image.Resampling.LANCZOS)
    candidate_analysis = candidate.resize(analysis_size, Image.Resampling.LANCZOS)
    reference_mask, candidate_mask, thresholds = extract_boundary_pair(
        reference_analysis, candidate_analysis, config, np, ImageFilter
    )
    scale_to_full = 1.0 / analysis_scale
    tolerances_analysis = [value * analysis_scale for value in config["tolerancesFullPixels"]]
    global_metrics, to_reference, to_candidate = compute_metrics(
        reference_mask, candidate_mask, tolerances_analysis, scale_to_full, np
    )

    boxes = []
    if args.regions_file:
        mode, regions = load_regions(args.regions_file.resolve(), config["maxRegions"])
        boxes = region_boxes(mode, regions, reference.size, analysis_size)
    region_results = []
    for box in boxes:
        sample_mask = np.zeros(reference_mask.shape, dtype=bool)
        left, top, right, bottom = box["analysisPixelBox"]
        sample_mask[top:bottom, left:right] = True
        metrics, _, _ = compute_metrics(
            reference_mask, candidate_mask, tolerances_analysis, scale_to_full, np, sample_mask
        )
        region_results.append({"name": box["name"], "fullPixelBox": box["fullPixelBox"], "analysisPixelBox": box["analysisPixelBox"], "metrics": metrics})

    resolved_config = {
        **config,
        "fullRenderSize": {"width": reference.width, "height": reference.height},
        "analysisSize": {"width": analysis_size[0], "height": analysis_size[1]},
        "analysisScale": analysis_scale,
        "distanceScaleFullPerAnalysisPixel": scale_to_full,
        "resolvedThresholds": thresholds,
        "methodConfigSha256": method_hash,
        "sharedByReferenceAndCandidate": True,
        "candidateSpecificOverridesAccepted": False,
    }
    resolved_hash = canonical_hash(resolved_config)
    report = {
        "schemaVersion": 1,
        "status": "diagnostic-evidence-only",
        "paths": {
            "reference": display_path(reference_path, args.path_mode, cwd),
            "candidate": display_path(candidate_path, args.path_mode, cwd),
            "config": display_path(args.config.resolve(), args.path_mode, cwd),
            "regions": display_path(args.regions_file.resolve(), args.path_mode, cwd) if args.regions_file else None,
        },
        "normalization": {
            "fullRenderSize": [reference.width, reference.height],
            "analysisSize": list(analysis_size),
            "colorMode": "RGB",
            "downsampling": "Pillow Lanczos",
            "sameDimensionsValidated": True,
        },
        "configurationIntegrity": {
            "methodConfigSha256": method_hash,
            "resolvedConfigSha256": resolved_hash,
            "sharedResolvedConfig": True,
            "referenceDerivedOnce": True,
            "candidateSpecificOverridesAccepted": False,
        },
        "globalMetrics": global_metrics,
        "regions": region_results,
        "interpretationWarning": "Boundary metrics are geometric diagnostic evidence, not editability, semantics, or a universal quality score.",
    }

    output_settings = config["output"]
    names = {"metrics": f"{prefix}-boundary-metrics.json", "resolved": f"{prefix}-boundary-config-resolved.json"}
    if output_settings["writeCsv"]:
        names["csv"] = f"{prefix}-boundary-metrics.csv"
    if output_settings["boundaryMaps"]:
        names["referenceMap"] = f"{prefix}-reference-boundaries.png"
        names["candidateMap"] = f"{prefix}-candidate-boundaries.png"
    if output_settings["mismatchVisualizations"]:
        names["mismatch"] = f"{prefix}-boundary-mismatch.png"
        for box in boxes:
            names[f"region:{box['name']}"] = f"{prefix}-region-{box['name']}-boundary-mismatch.png"
    final = {name: (output_dir / filename).resolve() for name, filename in names.items()}
    for path in final.values():
        try:
            path.relative_to(output_dir)
        except ValueError as exc:
            raise ValueError("constructed output path escapes --output-dir") from exc
    existing = [path.name for path in final.values() if path.exists()]
    if existing and not args.overwrite:
        raise FileExistsError("refusing to overwrite existing outputs: " + ", ".join(existing))

    visualization_tolerance = output_settings["visualizationToleranceFullPixels"] * analysis_scale
    with tempfile.TemporaryDirectory(prefix=f".{prefix}-boundary-", dir=output_dir) as temp_name:
        temp_dir = Path(temp_name)
        staged = {name: temp_dir / filename for name, filename in names.items()}
        staged["metrics"].write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        staged["resolved"].write_text(json.dumps(resolved_config, indent=2) + "\n", encoding="utf-8")
        if "csv" in staged:
            rows = list(csv_rows(report))
            fields = list(rows[0]) if rows else ["scope", "name"]
            with staged["csv"].open("w", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(handle, fieldnames=fields)
                writer.writeheader()
                writer.writerows(rows)
        if "referenceMap" in staged:
            boundary_image(reference_mask, np, Image).save(staged["referenceMap"])
            boundary_image(candidate_mask, np, Image).save(staged["candidateMap"])
        if "mismatch" in staged:
            mismatch = mismatch_image(reference_mask, candidate_mask, to_reference, to_candidate, visualization_tolerance, np, Image)
            mismatch.save(staged["mismatch"])
            for box in boxes:
                left, top, right, bottom = box["analysisPixelBox"]
                mismatch.crop((left, top, right, bottom)).save(staged[f"region:{box['name']}"])
        commit_outputs(staged, final, args.overwrite, temp_dir)

    if args.format == "json":
        print(json.dumps(report, indent=2))
    else:
        print("# Reference-Grounded Boundary Comparison")
        print(f"\n- Reference: `{report['paths']['reference']}`")
        print(f"- Candidate: `{report['paths']['candidate']}`")
        print(f"- Shared resolved config: `yes` ({resolved_hash})")
        print(f"- Reference boundaries: `{global_metrics['referenceBoundaryCount']}`")
        print(f"- Candidate boundaries: `{global_metrics['candidateBoundaryCount']}`")
        print("- Status: diagnostic evidence only; no universal F1 pass threshold applied")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
