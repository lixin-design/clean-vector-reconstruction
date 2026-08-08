#!/usr/bin/env python3
"""Validate case-authored spatial geometry inventories and reconstruction reports.

This module validates authored JSON and named coordinate mappings. It does not
inspect images, infer perspective, or discover semantic objects inside SVG.
"""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from pathlib import Path
from typing import Any


SAFE_NAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{0,63}$")
MAX_ENTITIES = 512
MAX_LANDMARKS = 1024
MAX_PLANES = 128
MAX_RELATIONS = 1024
MAX_CONTOURS = 256
MAX_SUBJECTS = 128
COORDINATE_MODES = {"normalized", "case"}
LANDMARK_ROLES = {
    "canvas-anchor",
    "bounding-corner",
    "roof-peak",
    "facade-corner",
    "shared-baseline-point",
    "center-point",
    "endpoint",
    "intersection",
    "clipping-point",
    "turning-point",
    "high-extremum",
    "low-extremum",
    "other",
}
RELATION_ARITY: dict[str, tuple[int, int | None]] = {
    "aligned-x": (2, None),
    "aligned-y": (2, None),
    "parallel": (2, 2),
    "approximately-parallel": (2, 2),
    "shares-baseline": (2, None),
    "centered-under": (2, 2),
    "centered-over": (2, 2),
    "offset-from": (2, 2),
    "attached-to": (2, 2),
    "overlaps": (2, 2),
    "contained-in": (2, 2),
    "follows-plane": (2, 2),
    "clipped-by": (2, 2),
    "same-row": (2, None),
    "same-column": (2, None),
    "ordered-left-to-right": (2, None),
    "ordered-top-to-bottom": (2, None),
    "relative-spacing": (2, None),
}


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


def safe_name(value: object, label: str) -> str:
    if not isinstance(value, str) or not SAFE_NAME.fullmatch(value):
        raise ValueError(
            f"{label} must use 1–64 ASCII letters, digits, hyphens, or underscores "
            "and start with a letter or digit"
        )
    if ".." in value or "/" in value or "\\" in value or ":" in value:
        raise ValueError(f"{label} contains a traversal-like or unsafe value")
    return value


def required_bool(value: object, label: str) -> bool:
    if not isinstance(value, bool):
        raise ValueError(f"{label} must be a boolean")
    return value


def number(value: object, label: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{label} must be a finite number")
    result = float(value)
    if not math.isfinite(result):
        raise ValueError(f"{label} must be a finite number")
    return result


def nonnegative(value: object, label: str) -> float:
    result = number(value, label)
    if result < 0:
        raise ValueError(f"{label} must be nonnegative")
    return result


def coordinate(value: object, label: str, mode: str) -> float:
    result = number(value, label)
    if mode == "normalized" and not 0.0 <= result <= 1.0:
        raise ValueError(f"{label} must be in normalized range 0..1")
    return result


def named_list(payload: dict[str, Any], key: str, maximum: int) -> list[dict[str, Any]]:
    value = payload.get(key, [])
    if not isinstance(value, list):
        raise ValueError(f"{key} must be a list")
    if len(value) > maximum:
        raise ValueError(f"{key} exceeds maximum count of {maximum}")
    if any(not isinstance(item, dict) for item in value):
        raise ValueError(f"every {key} entry must be an object")
    return value


def unique_name(name: str, section: str, seen: dict[str, str]) -> None:
    folded = name.casefold()
    if folded in seen:
        raise ValueError(f"duplicate name '{name}' in {section}; already used in {seen[folded]}")
    seen[folded] = section


def name_references(values: object, label: str, minimum: int = 0, maximum: int = MAX_SUBJECTS) -> list[str]:
    if not isinstance(values, list) or len(values) < minimum or len(values) > maximum:
        raise ValueError(f"{label} must contain {minimum}–{maximum} names")
    result = [safe_name(value, f"{label} reference") for value in values]
    if len({value.casefold() for value in result}) != len(result):
        raise ValueError(f"{label} contains duplicate references")
    return result


def validate_inventory(payload: object, shown_path: str = "geometry-inventory.json", path_mode: str = "basename") -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise ValueError("geometry inventory JSON must be an object")
    if payload.get("version") != 1:
        raise ValueError("version must be integer 1")
    mode = payload.get("coordinateMode")
    if mode not in COORDINATE_MODES:
        raise ValueError("coordinateMode must be 'normalized' or 'case'")

    raw_entities = named_list(payload, "entities", MAX_ENTITIES)
    raw_landmarks = named_list(payload, "landmarks", MAX_LANDMARKS)
    raw_planes = named_list(payload, "planes", MAX_PLANES)
    raw_relations = named_list(payload, "relations", MAX_RELATIONS)
    raw_contours = named_list(payload, "contours", MAX_CONTOURS)
    if not raw_landmarks:
        raise ValueError("landmarks must be a non-empty list")

    seen: dict[str, str] = {}
    entities: list[dict[str, Any]] = []
    landmarks: list[dict[str, Any]] = []
    planes: list[dict[str, Any]] = []
    relations: list[dict[str, Any]] = []
    contours: list[dict[str, Any]] = []

    for raw in raw_entities:
        name = safe_name(raw.get("name"), "entity name")
        unique_name(name, "entities", seen)
        region = safe_name(raw.get("region"), f"entity '{name}' region")
        svg_id = raw.get("svg_id")
        if svg_id is not None:
            svg_id = safe_name(svg_id, f"entity '{name}' svg_id")
        entities.append({
            "name": name,
            "region": region,
            "svgId": svg_id,
            "mandatory": required_bool(raw.get("mandatory"), f"entity '{name}' mandatory"),
        })

    for raw in raw_landmarks:
        name = safe_name(raw.get("name"), "landmark name")
        unique_name(name, "landmarks", seen)
        role = raw.get("role")
        if role not in LANDMARK_ROLES:
            raise ValueError(f"landmark '{name}' role is unsupported")
        tolerance = nonnegative(raw.get("tolerance", 0.0), f"landmark '{name}' tolerance")
        landmarks.append({
            "name": name,
            "region": safe_name(raw.get("region"), f"landmark '{name}' region"),
            "x": coordinate(raw.get("x"), f"landmark '{name}' x", mode),
            "y": coordinate(raw.get("y"), f"landmark '{name}' y", mode),
            "role": role,
            "tolerance": tolerance,
            "mandatory": required_bool(raw.get("mandatory"), f"landmark '{name}' mandatory"),
        })

    landmark_names = {item["name"].casefold(): item["name"] for item in landmarks}
    entity_names = {item["name"].casefold(): item["name"] for item in entities}

    for raw in raw_planes:
        name = safe_name(raw.get("name"), "plane name")
        unique_name(name, "planes", seen)
        anchors = name_references(raw.get("anchors"), f"plane '{name}' anchors", 3, 4)
        for anchor in anchors:
            if anchor.casefold() not in landmark_names:
                raise ValueError(f"plane '{name}' references missing landmark '{anchor}'")
        directions_raw = raw.get("dominant_edge_directions")
        if not isinstance(directions_raw, list) or not 1 <= len(directions_raw) <= 2:
            raise ValueError(f"plane '{name}' dominant_edge_directions must contain one or two angles")
        directions = [number(value, f"plane '{name}' direction") for value in directions_raw]
        if any(not -180.0 <= value <= 180.0 for value in directions):
            raise ValueError(f"plane '{name}' directions must be in -180..180 degrees")
        children = name_references(raw.get("children", []), f"plane '{name}' children", 0)
        for child in children:
            if child.casefold() not in entity_names:
                raise ValueError(f"plane '{name}' references missing child entity '{child}'")
        progression_raw = raw.get("relative_scale_progression", [])
        if not isinstance(progression_raw, list):
            raise ValueError(f"plane '{name}' relative_scale_progression must be a list")
        progression = [nonnegative(value, f"plane '{name}' relative scale") for value in progression_raw]
        if progression and len(progression) != len(children):
            raise ValueError(f"plane '{name}' relative_scale_progression must match children count")
        planes.append({
            "name": name,
            "anchors": anchors,
            "dominantEdgeDirections": directions,
            "children": children,
            "childrenFollowPlane": required_bool(
                raw.get("children_follow_plane"), f"plane '{name}' children_follow_plane"
            ),
            "relativeScaleProgression": progression,
            "tolerance": nonnegative(raw.get("tolerance", 0.0), f"plane '{name}' tolerance"),
            "mandatory": required_bool(raw.get("mandatory"), f"plane '{name}' mandatory"),
        })

    subject_names = set(landmark_names) | set(entity_names) | {item["name"].casefold() for item in planes}
    for raw in raw_relations:
        name = safe_name(raw.get("name"), "relation name")
        unique_name(name, "relations", seen)
        relation_type = raw.get("type")
        if relation_type not in RELATION_ARITY:
            raise ValueError(f"relation '{name}' type is unsupported")
        minimum, maximum = RELATION_ARITY[relation_type]
        subjects = name_references(
            raw.get("subjects"), f"relation '{name}' subjects", minimum, maximum or MAX_SUBJECTS
        )
        for subject in subjects:
            if subject.casefold() not in subject_names:
                raise ValueError(f"relation '{name}' references missing subject '{subject}'")
        expected_offset = raw.get("expected_offset")
        if relation_type == "offset-from":
            if not isinstance(expected_offset, list) or len(expected_offset) != 2:
                raise ValueError(f"relation '{name}' expected_offset must contain dx and dy")
            expected_offset = [number(value, f"relation '{name}' expected_offset") for value in expected_offset]
        elif expected_offset is not None:
            raise ValueError(f"relation '{name}' expected_offset is only valid for offset-from")
        expected_spacing = raw.get("expected_spacing")
        axis = raw.get("axis", "euclidean")
        if relation_type == "relative-spacing":
            if axis not in {"x", "y", "euclidean"}:
                raise ValueError(f"relation '{name}' axis must be x, y, or euclidean")
            if not isinstance(expected_spacing, list) or len(expected_spacing) != len(subjects) - 1:
                raise ValueError(f"relation '{name}' expected_spacing must match adjacent subject count")
            expected_spacing = [nonnegative(value, f"relation '{name}' expected spacing") for value in expected_spacing]
        elif expected_spacing is not None or "axis" in raw:
            raise ValueError(f"relation '{name}' spacing fields are only valid for relative-spacing")
        relations.append({
            "name": name,
            "type": relation_type,
            "subjects": subjects,
            "tolerance": nonnegative(raw.get("tolerance", 0.0), f"relation '{name}' tolerance"),
            "mandatory": required_bool(raw.get("mandatory"), f"relation '{name}' mandatory"),
            "expectedOffset": expected_offset,
            "expectedSpacing": expected_spacing,
            "axis": axis if relation_type == "relative-spacing" else None,
        })

    for raw in raw_contours:
        name = safe_name(raw.get("name"), "contour name")
        unique_name(name, "contours", seen)
        start = safe_name(raw.get("start"), f"contour '{name}' start")
        end = safe_name(raw.get("end"), f"contour '{name}' end")
        ordered = name_references(raw.get("landmarks"), f"contour '{name}' landmarks", 2)
        if ordered[0].casefold() != start.casefold() or ordered[-1].casefold() != end.casefold():
            raise ValueError(f"contour '{name}' landmarks must begin with start and end with end")
        for landmark in ordered:
            if landmark.casefold() not in landmark_names:
                raise ValueError(f"contour '{name}' references missing landmark '{landmark}'")
        subsets: dict[str, list[str]] = {}
        for source_key, output_key in (
            ("extrema", "extrema"),
            ("turning_points", "turningPoints"),
            ("intersections", "intersections"),
            ("clip_points", "clipPoints"),
        ):
            refs = name_references(raw.get(source_key, []), f"contour '{name}' {source_key}", 0)
            if any(ref.casefold() not in {item.casefold() for item in ordered} for ref in refs):
                raise ValueError(f"contour '{name}' {source_key} must reference its ordered landmarks")
            subsets[output_key] = refs
        nearby_raw = raw.get("nearby_anchor_distances", [])
        if not isinstance(nearby_raw, list) or len(nearby_raw) > MAX_SUBJECTS:
            raise ValueError(f"contour '{name}' nearby_anchor_distances must be a bounded list")
        nearby: list[dict[str, Any]] = []
        seen_nearby: set[str] = set()
        for entry in nearby_raw:
            if not isinstance(entry, dict):
                raise ValueError(f"contour '{name}' nearby distance entries must be objects")
            anchor = safe_name(entry.get("anchor"), f"contour '{name}' nearby anchor")
            if anchor.casefold() not in landmark_names:
                raise ValueError(f"contour '{name}' references missing nearby anchor '{anchor}'")
            if anchor.casefold() in seen_nearby:
                raise ValueError(f"contour '{name}' has duplicate nearby anchor '{anchor}'")
            seen_nearby.add(anchor.casefold())
            nearby.append({
                "anchor": anchor,
                "distance": nonnegative(entry.get("distance"), f"contour '{name}' nearby distance"),
                "tolerance": nonnegative(entry.get("tolerance", 0.0), f"contour '{name}' nearby tolerance"),
            })
        tangent = raw.get("major_tangent_direction")
        if tangent is not None:
            tangent = number(tangent, f"contour '{name}' major_tangent_direction")
            if not -180.0 <= tangent <= 180.0:
                raise ValueError(f"contour '{name}' major_tangent_direction must be in -180..180")
        contours.append({
            "name": name,
            "region": safe_name(raw.get("region"), f"contour '{name}' region"),
            "start": start,
            "end": end,
            "landmarks": ordered,
            **subsets,
            "majorTangentDirection": tangent,
            "nearbyAnchorDistances": nearby,
            "mandatory": required_bool(raw.get("mandatory"), f"contour '{name}' mandatory"),
        })

    return {
        "file": shown_path,
        "pathMode": path_mode,
        "schemaValid": True,
        "version": 1,
        "coordinateMode": mode,
        "counts": {
            "entities": len(entities),
            "landmarks": len(landmarks),
            "planes": len(planes),
            "relations": len(relations),
            "contours": len(contours),
        },
        "entities": entities,
        "landmarks": landmarks,
        "planes": planes,
        "relations": relations,
        "contours": contours,
        "supportedRelationTypes": sorted(RELATION_ARITY),
        "geometryReadinessEvaluated": False,
        "automaticReadinessBlocked": False,
        "mandatoryFailures": [],
        "notes": [
            "This validator checks authored JSON and named mappings; it does not inspect artwork or infer geometry.",
            "Schema validity alone does not prove reconstructed spatial fidelity; pass --actual for readiness evaluation.",
        ],
    }


def load_json(path: Path, label: str) -> object:
    if not path.is_file():
        raise FileNotFoundError(f"{label} not found: {path.name}")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"malformed {label} JSON: {exc.msg}") from exc


def validate_actual(payload: object, expected: dict[str, Any], shown_path: str) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise ValueError("actual geometry report JSON must be an object")
    if payload.get("version") != 1:
        raise ValueError("actual report version must be integer 1")
    if payload.get("coordinateMode") != expected["coordinateMode"]:
        raise ValueError("actual coordinateMode must match inventory coordinateMode")
    mode = expected["coordinateMode"]
    allowed_points = {
        item["name"].casefold(): item["name"] for item in expected["landmarks"] + expected["entities"]
    }
    points: dict[str, dict[str, Any]] = {}
    for raw in named_list(payload, "points", MAX_LANDMARKS + MAX_ENTITIES):
        name = safe_name(raw.get("name"), "actual point name")
        folded = name.casefold()
        if folded not in allowed_points:
            raise ValueError(f"actual point '{name}' is not declared by the inventory")
        if folded in points:
            raise ValueError(f"duplicate actual point name: {name}")
        points[folded] = {
            "name": allowed_points[folded],
            "x": coordinate(raw.get("x"), f"actual point '{name}' x", mode),
            "y": coordinate(raw.get("y"), f"actual point '{name}' y", mode),
        }

    actual_relations: dict[str, dict[str, Any]] = {}
    expected_relation_names = {item["name"].casefold() for item in expected["relations"]}
    for raw in named_list(payload, "relations", MAX_RELATIONS):
        name = safe_name(raw.get("name"), "actual relation name")
        folded = name.casefold()
        if folded not in expected_relation_names:
            raise ValueError(f"actual relation '{name}' is not declared by the inventory")
        if folded in actual_relations:
            raise ValueError(f"duplicate actual relation name: {name}")
        actual_relations[folded] = {
            "name": name,
            "passed": required_bool(raw.get("passed"), f"actual relation '{name}' passed"),
            "delta": nonnegative(raw.get("delta", 0.0), f"actual relation '{name}' delta"),
        }

    actual_planes: dict[str, dict[str, Any]] = {}
    expected_plane_names = {item["name"].casefold() for item in expected["planes"]}
    for raw in named_list(payload, "planes", MAX_PLANES):
        name = safe_name(raw.get("name"), "actual plane name")
        folded = name.casefold()
        if folded not in expected_plane_names:
            raise ValueError(f"actual plane '{name}' is not declared by the inventory")
        if folded in actual_planes:
            raise ValueError(f"duplicate actual plane name: {name}")
        progression_raw = raw.get("relative_scale_progression", [])
        if not isinstance(progression_raw, list):
            raise ValueError(f"actual plane '{name}' relative_scale_progression must be a list")
        actual_planes[folded] = {
            "name": name,
            "childOrientationConsistent": required_bool(
                raw.get("child_orientation_consistent"),
                f"actual plane '{name}' child_orientation_consistent",
            ),
            "relativeScaleProgression": [
                nonnegative(value, f"actual plane '{name}' relative scale") for value in progression_raw
            ],
        }
    return {"file": shown_path, "points": points, "relations": actual_relations, "planes": actual_planes}


def point_delta(a: dict[str, Any], b: dict[str, Any]) -> float:
    return math.hypot(a["x"] - b["x"], a["y"] - b["y"])


def relation_result(relation: dict[str, Any], points: dict[str, dict[str, Any]], authored: dict[str, Any] | None) -> dict[str, Any]:
    subjects = [points.get(name.casefold()) for name in relation["subjects"]]
    relation_type = relation["type"]
    tolerance = relation["tolerance"]
    result: dict[str, Any] = {"name": relation["name"], "type": relation_type, "resolved": True}
    if relation_type in {"attached-to", "overlaps", "contained-in", "follows-plane", "clipped-by"}:
        if authored is None:
            return {**result, "resolved": False, "passed": False, "reason": "actual relation result missing"}
        return {**result, "passed": authored["passed"], "delta": authored["delta"], "source": "authored-actual"}
    if any(item is None for item in subjects):
        if authored is not None:
            return {**result, "passed": authored["passed"], "delta": authored["delta"], "source": "authored-actual"}
        return {**result, "resolved": False, "passed": False, "reason": "actual subject point missing"}
    actual_points = [item for item in subjects if item is not None]
    xs = [item["x"] for item in actual_points]
    ys = [item["y"] for item in actual_points]
    if relation_type in {"aligned-x", "same-column"}:
        delta = max(xs) - min(xs)
        passed = delta <= tolerance
    elif relation_type in {"aligned-y", "shares-baseline", "same-row"}:
        delta = max(ys) - min(ys)
        passed = delta <= tolerance
    elif relation_type == "ordered-left-to-right":
        delta = max((xs[index] - xs[index + 1]) for index in range(len(xs) - 1))
        passed = delta <= tolerance
    elif relation_type == "ordered-top-to-bottom":
        delta = max((ys[index] - ys[index + 1]) for index in range(len(ys) - 1))
        passed = delta <= tolerance
    elif relation_type in {"centered-under", "centered-over"}:
        centered_delta = abs(xs[0] - xs[1])
        ordered = ys[0] >= ys[1] - tolerance if relation_type == "centered-under" else ys[0] <= ys[1] + tolerance
        delta = centered_delta
        passed = centered_delta <= tolerance and ordered
    elif relation_type == "offset-from":
        expected_offset = relation["expectedOffset"]
        dx = (xs[0] - xs[1]) - expected_offset[0]
        dy = (ys[0] - ys[1]) - expected_offset[1]
        delta = math.hypot(dx, dy)
        passed = delta <= tolerance
    elif relation_type == "relative-spacing":
        actual_spacing = []
        for first, second in zip(actual_points, actual_points[1:]):
            if relation["axis"] == "x":
                actual_spacing.append(abs(second["x"] - first["x"]))
            elif relation["axis"] == "y":
                actual_spacing.append(abs(second["y"] - first["y"]))
            else:
                actual_spacing.append(point_delta(first, second))
        errors = [abs(actual - expected) for actual, expected in zip(actual_spacing, relation["expectedSpacing"])]
        delta = max(errors, default=0.0)
        passed = delta <= tolerance
        result["actualSpacing"] = actual_spacing
    elif authored is not None:
        return {**result, "passed": authored["passed"], "delta": authored["delta"], "source": "authored-actual"}
    else:
        return {**result, "resolved": False, "passed": False, "reason": "relation requires authored actual result"}
    return {**result, "passed": passed, "delta": delta, "tolerance": tolerance, "source": "computed"}


def evaluate_geometry(expected: dict[str, Any], actual: dict[str, Any]) -> dict[str, Any]:
    points = actual["points"]
    failures: list[dict[str, str]] = []
    landmark_results: list[dict[str, Any]] = []
    landmark_by_name: dict[str, dict[str, Any]] = {}
    for landmark in expected["landmarks"]:
        point = points.get(landmark["name"].casefold())
        if point is None:
            result = {"name": landmark["name"], "resolved": False, "passed": False, "mandatory": landmark["mandatory"]}
        else:
            dx = point["x"] - landmark["x"]
            dy = point["y"] - landmark["y"]
            delta = math.hypot(dx, dy)
            result = {
                "name": landmark["name"],
                "resolved": True,
                "passed": delta <= landmark["tolerance"],
                "mandatory": landmark["mandatory"],
                "expected": [landmark["x"], landmark["y"]],
                "actual": [point["x"], point["y"]],
                "dx": dx,
                "dy": dy,
                "distance": delta,
                "tolerance": landmark["tolerance"],
            }
        landmark_results.append(result)
        landmark_by_name[landmark["name"].casefold()] = result
        if landmark["mandatory"] and not result["passed"]:
            failures.append({"kind": "landmark", "name": landmark["name"]})

    relation_results = []
    for relation in expected["relations"]:
        result = relation_result(relation, points, actual["relations"].get(relation["name"].casefold()))
        result["mandatory"] = relation["mandatory"]
        relation_results.append(result)
        if relation["mandatory"] and not result["passed"]:
            failures.append({"kind": "relation", "name": relation["name"]})

    plane_results = []
    for plane in expected["planes"]:
        observed = actual["planes"].get(plane["name"].casefold())
        if observed is None:
            result = {"name": plane["name"], "resolved": False, "passed": False, "mandatory": plane["mandatory"]}
        else:
            orientation_pass = not plane["childrenFollowPlane"] or observed["childOrientationConsistent"]
            expected_scale = plane["relativeScaleProgression"]
            actual_scale = observed["relativeScaleProgression"]
            scale_errors = [abs(a - b) for a, b in zip(expected_scale, actual_scale)] if len(expected_scale) == len(actual_scale) else []
            scale_pass = not expected_scale or (
                len(expected_scale) == len(actual_scale) and max(scale_errors, default=0.0) <= plane["tolerance"]
            )
            result = {
                "name": plane["name"],
                "resolved": True,
                "passed": orientation_pass and scale_pass,
                "mandatory": plane["mandatory"],
                "childOrientationPassed": orientation_pass,
                "relativeScalePassed": scale_pass,
                "maximumScaleDelta": max(scale_errors, default=None),
                "tolerance": plane["tolerance"],
            }
        plane_results.append(result)
        if plane["mandatory"] and not result["passed"]:
            failures.append({"kind": "plane", "name": plane["name"]})

    contour_results = []
    for contour in expected["contours"]:
        ordered_results = [landmark_by_name[name.casefold()] for name in contour["landmarks"]]
        endpoint_results = [landmark_by_name[contour["start"].casefold()], landmark_by_name[contour["end"].casefold()]]
        turning_results = [landmark_by_name[name.casefold()] for name in contour["turningPoints"]]
        endpoint_pass = all(item["passed"] for item in endpoint_results)
        turning_pass = all(item["passed"] for item in turning_results)
        all_pass = all(item["passed"] for item in ordered_results)
        result = {
            "name": contour["name"],
            "resolved": all(item["resolved"] for item in ordered_results),
            "passed": all_pass,
            "mandatory": contour["mandatory"],
            "endpointPassed": endpoint_pass,
            "turningPointPassed": turning_pass,
            "failedLandmarks": [item["name"] for item in ordered_results if not item["passed"]],
        }
        contour_results.append(result)
        if contour["mandatory"] and not result["passed"]:
            failures.append({"kind": "contour", "name": contour["name"]})

    result = dict(expected)
    result.update({
        "actualFile": actual["file"],
        "geometryReadinessEvaluated": True,
        "landmarkValidation": landmark_results,
        "relationValidation": relation_results,
        "planeValidation": plane_results,
        "contourValidation": contour_results,
        "mandatoryFailures": failures,
        "automaticReadinessBlocked": bool(failures),
        "status": "Automatic regression blocked — spatial fidelity gate failed" if failures else "spatial fidelity gate passed",
    })
    return result


def markdown(report: dict[str, Any]) -> str:
    counts = report["counts"]
    lines = [
        "# Geometry Inventory Audit",
        "",
        f"- Inventory: `{report['file']}`",
        f"- Schema valid: {'yes' if report['schemaValid'] else 'no'}",
        f"- Coordinate mode: `{report['coordinateMode']}`",
        f"- Entities / landmarks / planes / relations / contours: "
        f"{counts['entities']} / {counts['landmarks']} / {counts['planes']} / {counts['relations']} / {counts['contours']}",
        f"- Geometry readiness evaluated: {'yes' if report['geometryReadinessEvaluated'] else 'no'}",
        f"- Automatic readiness blocked: {'yes' if report['automaticReadinessBlocked'] else 'no'}",
    ]
    if report["geometryReadinessEvaluated"]:
        lines.extend(["", f"- Status: {report['status']}", "", "## Mandatory failures"])
        if report["mandatoryFailures"]:
            lines.extend(f"- `{item['kind']}`: `{item['name']}`" for item in report["mandatoryFailures"])
        else:
            lines.append("- None")
        lines.extend([
            "",
            "## Validation summary",
            "",
            f"- Landmarks passed: {sum(item['passed'] for item in report['landmarkValidation'])}/{len(report['landmarkValidation'])}",
            f"- Relations passed: {sum(item['passed'] for item in report['relationValidation'])}/{len(report['relationValidation'])}",
            f"- Planes passed: {sum(item['passed'] for item in report['planeValidation'])}/{len(report['planeValidation'])}",
            f"- Contours passed: {sum(item['passed'] for item in report['contourValidation'])}/{len(report['contourValidation'])}",
        ])
    lines.extend(["", *[f"- Note: {note}" for note in report["notes"]]])
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate a case-authored geometry inventory and optional reconstruction-side report without image inference."
    )
    parser.add_argument("inventory", type=Path, help="Expected geometry inventory JSON.")
    parser.add_argument("--actual", type=Path, help="Optional reconstruction-side geometry report JSON.")
    parser.add_argument("--format", choices=["json", "markdown"], default="json")
    parser.add_argument(
        "--path-mode", choices=["basename", "relative", "absolute"], default="relative",
        help="Path display policy for reports.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    cwd = Path.cwd().resolve()
    try:
        inventory_path = args.inventory.resolve()
        expected = validate_inventory(
            load_json(inventory_path, "geometry inventory"),
            display_path(inventory_path, args.path_mode, cwd),
            args.path_mode,
        )
        report = expected
        if args.actual is not None:
            actual_path = args.actual.resolve()
            actual = validate_actual(
                load_json(actual_path, "actual geometry report"),
                expected,
                display_path(actual_path, args.path_mode, cwd),
            )
            report = evaluate_geometry(expected, actual)
        print(json.dumps(report, indent=2, ensure_ascii=False) if args.format == "json" else markdown(report))
        return 2 if report["automaticReadinessBlocked"] else 0
    except (OSError, ValueError) as exc:
        if args.format == "json":
            print(json.dumps({"schemaValid": False, "error": str(exc)}, indent=2, ensure_ascii=False))
        else:
            print(f"Geometry inventory validation failed: {exc}")
        return 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        raise SystemExit(130)
