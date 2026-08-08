#!/usr/bin/env python3
"""Self-contained safety and fixture tests for the reusable Skill scripts."""

from __future__ import annotations

import argparse
import importlib.util
import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest import mock


SCRIPT_DIR = Path(__file__).resolve().parent


def load_module(name: str):
    spec = importlib.util.spec_from_file_location(name, SCRIPT_DIR / f"{name}.py")
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


audit_svg = load_module("audit_svg")
render_compare = load_module("render_compare")
compare_boundaries = load_module("compare_boundaries")
validate_object_inventory = load_module("validate_object_inventory")
validate_geometry_inventory = load_module("validate_geometry_inventory")


def svg_document(definitions: str, objects: str) -> str:
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 20 20">'
        f"<defs>{definitions}</defs>{objects}</svg>"
    )


def boundary_config(**updates: object) -> dict[str, object]:
    payload: dict[str, object] = {
        "version": 1,
        "fullRenderSize": {"width": None, "height": None},
        "analysisSize": {"maxDimension": 128},
        "preprocessing": {"blurRadius": 0.5},
        "extraction": {
            "colorSpace": "CIELAB-D65",
            "gradientOperator": "sobel-3x3",
            "nonMaximumSuppression": True,
            "thresholdMethod": "reference-otsu",
            "thresholdFloor": 1.0,
            "highPercentileClip": 99.5,
            "lowHighRatio": 0.5,
            "minimumComponentSize": 2,
        },
        "tolerancesFullPixels": [1, 2, 4],
        "maxRegions": 8,
        "output": {
            "writeCsv": True,
            "boundaryMaps": True,
            "mismatchVisualizations": True,
            "visualizationToleranceFullPixels": 2,
        },
    }
    payload.update(updates)
    return payload


class GradientAuditTests(unittest.TestCase):
    def run_audit(self, svg: str) -> dict[str, object]:
        with tempfile.TemporaryDirectory(prefix="gradient-audit-test-") as temp_name:
            path = Path(temp_name) / "fixture.svg"
            path.write_text(svg, encoding="utf-8")
            return audit_svg.audit(path, path.name, "basename", 0.0, 0.0, 300)

    def test_defined_and_used_linear_gradient_direct_fill(self):
        result = self.run_audit(svg_document(
            '<linearGradient id="g1"><stop offset="0" stop-color="#000"/><stop offset="1" stop-color="#fff"/></linearGradient>',
            '<rect id="a" x="0" y="0" width="10" height="10" fill="url(#g1)"/>',
        ))
        self.assertEqual(result["gradientAudit"]["usedGradientIds"], ["g1"])
        self.assertEqual(result["gradientAudit"]["objectsUsingEachGradient"]["g1"]["count"], 1)

    def test_defined_but_unused_gradient(self):
        result = self.run_audit(svg_document('<linearGradient id="g1"/>', '<rect width="10" height="10"/>'))
        self.assertEqual(result["gradientAudit"]["unusedGradientIds"], ["g1"])

    def test_missing_gradient_reference(self):
        result = self.run_audit(svg_document("", '<rect width="10" height="10" fill="url(#missing)"/>'))
        self.assertEqual(result["gradientAudit"]["missingGradientReferences"], ["missing"])

    def test_multiple_objects_use_one_gradient(self):
        result = self.run_audit(svg_document(
            '<linearGradient id="shared"/>',
            '<rect id="a" width="5" height="5" fill="url(#shared)"/><circle id="b" cx="10" cy="10" r="2" fill="url(#shared)"/>',
        ))
        usage = result["gradientAudit"]["objectsUsingEachGradient"]["shared"]
        self.assertEqual(usage["count"], 2)
        self.assertEqual(usage["objectIds"], ["a", "b"])

    def test_radial_gradient_usage(self):
        result = self.run_audit(svg_document('<radialGradient id="radial"/>', '<circle r="3" fill="url(#radial)"/>'))
        self.assertEqual(result["gradientAudit"]["definedRadialGradientCount"], 1)
        self.assertEqual(result["gradientAudit"]["usedGradientIds"], ["radial"])

    def test_gradient_in_style(self):
        result = self.run_audit(svg_document('<linearGradient id="styled"/>', '<rect width="5" height="5" style="fill:url(#styled)"/>'))
        self.assertEqual(result["gradientAudit"]["referencedGradientIds"], ["styled"])

    def test_gradient_in_direct_stroke(self):
        result = self.run_audit(svg_document('<linearGradient id="stroke-gradient"/>', '<line x1="0" y1="0" x2="10" y2="10" stroke="url(#stroke-gradient)"/>'))
        self.assertEqual(result["gradientAudit"]["usedGradientIds"], ["stroke-gradient"])

    def test_duplicate_gradient_ids(self):
        result = self.run_audit(svg_document('<linearGradient id="dup"/><radialGradient id="dup"/>', '<rect width="5" height="5" fill="url(#dup)"/>'))
        self.assertEqual(result["gradientAudit"]["duplicateGradientIds"], ["dup"])

    def test_raster_and_external_resource_safety_remain_active(self):
        result = self.run_audit('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 10 10"><image href="private/path/reference.png"/></svg>')
        warning_codes = {warning["code"] for warning in result["warnings"]}
        self.assertIn("raster-reference", warning_codes)
        self.assertIn("external-resource", warning_codes)
        target = result["resourceReferences"]["external"][0]["target"]
        self.assertEqual(target, "reference.png")


class StructuralCoverageAuditTests(unittest.TestCase):
    def run_audit(self, objects: str, definitions: str = "", intent: str = "opaque") -> dict[str, object]:
        with tempfile.TemporaryDirectory(prefix="coverage-structure-test-") as temp_name:
            path = Path(temp_name) / "fixture.svg"
            path.write_text(svg_document(definitions, objects), encoding="utf-8")
            return audit_svg.audit(path, path.name, "basename", 0.0, 0.0, 300, intent)

    def test_opaque_full_canvas_background_is_reported(self):
        result = self.run_audit('<rect id="background" width="20" height="20" fill="#fff"/>')
        coverage = result["coverageAudit"]
        self.assertTrue(coverage["fullCanvasBackgroundObjectExists"])
        self.assertTrue(coverage["fullCanvasBackgroundOpaque"])
        self.assertFalse(coverage["structuralCoverageProven"])

    def test_transparent_background_is_not_opaque(self):
        result = self.run_audit('<rect width="20" height="20" fill="#ffffff00"/>', intent="intentional")
        self.assertFalse(result["coverageAudit"]["fullCanvasBackgroundOpaque"])
        self.assertEqual(result["coverageAudit"]["transparencyIntent"], "intentional")

    def test_mask_is_reported_as_possible_exposure(self):
        result = self.run_audit(
            '<rect width="20" height="20" fill="#fff" mask="url(#m)"/>',
            '<mask id="m"><rect width="20" height="20" fill="#fff"/></mask>',
        )
        self.assertTrue(result["coverageAudit"]["clippingOrMasksMayExposeCanvas"])


class AlphaCoverageTests(unittest.TestCase):
    def audit(self, reference, preview, expected_opaque: bool = False, allowance: int = 0):
        return render_compare.audit_alpha_coverage(
            reference,
            preview,
            expected_opaque_reference=expected_opaque,
            alpha_threshold=254,
            max_unexpected_transparent_pixels=allowance,
        )

    def test_opaque_reference_and_fully_covered_preview(self):
        from PIL import Image

        reference = Image.new("RGBA", (8, 8), (10, 20, 30, 255))
        preview = Image.new("RGBA", (8, 8), (40, 50, 60, 255))
        result = self.audit(reference, preview, expected_opaque=True)
        self.assertEqual(result["unexpectedTransparentPixelCount"], 0)
        self.assertFalse(result["automaticReadinessBlocked"])

    def test_opaque_reference_and_internal_transparent_gap(self):
        from PIL import Image

        reference = Image.new("RGBA", (8, 8), (10, 20, 30, 255))
        preview = Image.new("RGBA", (8, 8), (40, 50, 60, 255))
        preview.putpixel((4, 4), (40, 50, 60, 0))
        result = self.audit(reference, preview, expected_opaque=True)
        self.assertEqual(result["unexpectedTransparentPixelCount"], 1)
        self.assertTrue(result["unexpectedGapsTouchInternalForegroundBoundaries"])
        self.assertTrue(result["automaticReadinessBlocked"])

    def test_intended_transparent_reference(self):
        from PIL import Image, ImageDraw

        reference = Image.new("RGBA", (8, 8), (0, 0, 0, 0))
        preview = Image.new("RGBA", (8, 8), (0, 0, 0, 0))
        ImageDraw.Draw(reference).rectangle((2, 2, 5, 5), fill=(20, 30, 40, 255))
        ImageDraw.Draw(preview).rectangle((2, 2, 5, 5), fill=(60, 70, 80, 255))
        result = self.audit(reference, preview)
        self.assertEqual(result["unexpectedTransparentPixelCount"], 0)
        self.assertTrue(result["transparencyTouchesOnlyIntendedOuterCanvasBoundary"])
        self.assertFalse(result["automaticReadinessBlocked"])

    def test_gap_touching_canvas_edge_only_fixture(self):
        from PIL import Image

        reference = Image.new("RGBA", (8, 8), (10, 20, 30, 255))
        preview = Image.new("RGBA", (8, 8), (40, 50, 60, 255))
        preview.putpixel((0, 3), (40, 50, 60, 0))
        result = self.audit(reference, preview, expected_opaque=True)
        region = result["unexpectedTransparentRegions"]["regions"][0]
        self.assertTrue(region["touchesCanvasEdge"])
        self.assertEqual(region["boundingBox"], [0, 3, 1, 4])

    def test_multiple_internal_gaps(self):
        from PIL import Image

        reference = Image.new("RGBA", (8, 8), (10, 20, 30, 255))
        preview = Image.new("RGBA", (8, 8), (40, 50, 60, 255))
        preview.putpixel((2, 2), (0, 0, 0, 0))
        preview.putpixel((5, 5), (0, 0, 0, 0))
        result = self.audit(reference, preview, expected_opaque=True)
        self.assertEqual(result["unexpectedTransparentRegions"]["regionCount"], 2)
        self.assertEqual(len(result["unexpectedTransparentBoundingBoxes"]), 2)

    def test_small_explicit_tolerance(self):
        from PIL import Image

        reference = Image.new("RGBA", (4, 4), (0, 0, 0, 255))
        preview = Image.new("RGBA", (4, 4), (0, 0, 0, 255))
        preview.putpixel((1, 1), (0, 0, 0, 0))
        self.assertFalse(self.audit(reference, preview, expected_opaque=True, allowance=1)["automaticReadinessBlocked"])

    def test_malformed_alpha_input(self):
        from PIL import Image

        with self.assertRaisesRegex(ValueError, "RGBA"):
            self.audit(Image.new("RGB", (4, 4)), Image.new("RGBA", (4, 4)))

    def test_mismatched_dimensions(self):
        from PIL import Image

        with self.assertRaisesRegex(RuntimeError, "renderer returned"):
            self.audit(Image.new("RGBA", (4, 4)), Image.new("RGBA", (5, 4)))


class ObjectFamilyInventoryTests(unittest.TestCase):
    def family(self, **updates: object) -> dict[str, object]:
        value: dict[str, object] = {
            "family": "detail-family",
            "expected_min": 1,
            "expected_max": 3,
            "reconstructed_count": 2,
            "status": "pass",
        }
        value.update(updates)
        return value

    def payload(self, families: list[dict[str, object]] | None = None) -> dict[str, object]:
        return {"regions": [{"name": "primary-region", "required_families": families or [self.family()]}]}

    def test_required_family_present(self):
        result = validate_object_inventory.validate_inventory(self.payload())
        self.assertTrue(result["minimumSemanticCompletenessPassed"])
        self.assertFalse(result["automaticReadinessBlocked"])

    def test_required_family_missing(self):
        result = validate_object_inventory.validate_inventory(
            self.payload([self.family(reconstructed_count=0, status="missing")])
        )
        self.assertEqual(len(result["missingRequiredFamilies"]), 1)
        self.assertTrue(result["automaticReadinessBlocked"])

    def test_repeated_count_below_minimum(self):
        result = validate_object_inventory.validate_inventory(
            self.payload([self.family(expected_min=2, reconstructed_count=1, status="below-minimum")])
        )
        self.assertEqual(len(result["belowMinimumFamilies"]), 1)

    def test_repeated_count_above_maximum(self):
        result = validate_object_inventory.validate_inventory(
            self.payload([self.family(expected_max=2, reconstructed_count=3, status="above-maximum")])
        )
        self.assertEqual(len(result["aboveMaximumFamilies"]), 1)

    def assert_invalid(self, payload: object, pattern: str):
        with self.assertRaisesRegex(ValueError, pattern):
            validate_object_inventory.validate_inventory(payload)

    def test_malformed_inventory_json(self):
        with tempfile.TemporaryDirectory(prefix="inventory-json-test-") as temp_name:
            path = Path(temp_name) / "inventory.json"
            path.write_text("{not-json", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "malformed"):
                validate_object_inventory.load_inventory(path, "basename", Path.cwd())

    def test_duplicate_region_name(self):
        region = self.payload()["regions"][0]
        self.assert_invalid({"regions": [region, {**region, "name": "PRIMARY-REGION"}]}, "duplicate region")

    def test_duplicate_family_name(self):
        self.assert_invalid(self.payload([self.family(), self.family(family="DETAIL-FAMILY")]), "duplicate family")

    def test_invalid_ranges(self):
        self.assert_invalid(self.payload([self.family(expected_min=4, expected_max=3)]), "must not exceed")

    def test_negative_count(self):
        self.assert_invalid(self.payload([self.family(reconstructed_count=-1)]), "nonnegative")

    def test_authored_status_must_match_computed_status(self):
        self.assert_invalid(self.payload([self.family(reconstructed_count=0, status="pass")]), "does not match")

    def test_traversal_like_names(self):
        self.assert_invalid({"regions": [{"name": "../escape", "required_families": [self.family()]}]}, "region name")
        self.assert_invalid(self.payload([self.family(family="..\\escape")]), "family name")

    def test_excessive_regions(self):
        regions = [
            {"name": f"region-{index}", "required_families": [self.family()]}
            for index in range(validate_object_inventory.MAX_REGIONS + 1)
        ]
        self.assert_invalid({"regions": regions}, "maximum")

    def test_excessive_families(self):
        families = [self.family(family=f"family-{index}") for index in range(validate_object_inventory.MAX_FAMILIES_PER_REGION + 1)]
        self.assert_invalid(self.payload(families), "maximum")

    def test_cli_returns_nonzero_when_mandatory_family_is_missing(self):
        with tempfile.TemporaryDirectory(prefix="inventory-cli-test-") as temp_name:
            path = Path(temp_name) / "inventory.json"
            path.write_text(
                json.dumps(self.payload([self.family(reconstructed_count=0, status="missing")])),
                encoding="utf-8",
            )
            argv = ["validate_object_inventory.py", str(path), "--format", "json", "--path-mode", "basename"]
            with mock.patch.object(sys, "argv", argv), redirect_stdout(io.StringIO()):
                self.assertEqual(validate_object_inventory.main(), 2)


class GeometryInventorySchemaTests(unittest.TestCase):
    def landmark(self, name: str, x: float, y: float, **updates: object) -> dict[str, object]:
        value: dict[str, object] = {
            "name": name,
            "region": "region-a",
            "x": x,
            "y": y,
            "role": "canvas-anchor",
            "tolerance": 0.02,
            "mandatory": True,
        }
        value.update(updates)
        return value

    def payload(self, **updates: object) -> dict[str, object]:
        value: dict[str, object] = {
            "version": 1,
            "coordinateMode": "normalized",
            "entities": [],
            "landmarks": [
                self.landmark("point-a", 0.2, 0.3),
                self.landmark("point-b", 0.5, 0.3),
                self.landmark("point-c", 0.5, 0.6, role="turning-point"),
                self.landmark("point-d", 0.2, 0.6),
            ],
            "planes": [],
            "relations": [],
            "contours": [],
        }
        value.update(updates)
        return value

    def validate(self, payload: dict[str, object]) -> dict[str, object]:
        return validate_geometry_inventory.validate_inventory(payload)

    def assert_invalid(self, payload: dict[str, object], pattern: str):
        with self.assertRaisesRegex(ValueError, pattern):
            self.validate(payload)

    def test_valid_normalized_landmark(self):
        result = self.validate(self.payload())
        self.assertTrue(result["schemaValid"])
        self.assertEqual(result["counts"]["landmarks"], 4)

    def test_landmark_out_of_range_coordinate(self):
        self.assert_invalid(self.payload(landmarks=[self.landmark("point-a", 1.1, 0.2)]), "normalized range")

    def test_landmark_negative_tolerance(self):
        self.assert_invalid(
            self.payload(landmarks=[self.landmark("point-a", 0.1, 0.2, tolerance=-0.01)]),
            "nonnegative",
        )

    def test_duplicate_landmark_name(self):
        self.assert_invalid(
            self.payload(landmarks=[self.landmark("point-a", 0.1, 0.2), self.landmark("POINT-A", 0.2, 0.3)]),
            "duplicate name",
        )

    def test_landmark_missing_mandatory_field(self):
        item = self.landmark("point-a", 0.1, 0.2)
        del item["mandatory"]
        self.assert_invalid(self.payload(landmarks=[item]), "mandatory")

    def plane(self, **updates: object) -> dict[str, object]:
        value: dict[str, object] = {
            "name": "plane-a",
            "anchors": ["point-a", "point-b", "point-c", "point-d"],
            "dominant_edge_directions": [0.0, 90.0],
            "children": [],
            "children_follow_plane": True,
            "relative_scale_progression": [],
            "tolerance": 0.02,
            "mandatory": True,
        }
        value.update(updates)
        return value

    def test_valid_quadrilateral_plane(self):
        result = self.validate(self.payload(planes=[self.plane()]))
        self.assertEqual(result["planes"][0]["anchors"], ["point-a", "point-b", "point-c", "point-d"])

    def test_plane_too_few_anchors(self):
        self.assert_invalid(self.payload(planes=[self.plane(anchors=["point-a", "point-b"])]), "3–4")

    def test_plane_duplicate_anchor(self):
        self.assert_invalid(
            self.payload(planes=[self.plane(anchors=["point-a", "point-b", "point-a"])]),
            "duplicate references",
        )

    def test_plane_missing_anchor_reference(self):
        self.assert_invalid(
            self.payload(planes=[self.plane(anchors=["point-a", "point-b", "missing"])]),
            "missing landmark",
        )

    def relation(self, relation_type: str = "aligned-x", **updates: object) -> dict[str, object]:
        value: dict[str, object] = {
            "name": "relation-a",
            "type": relation_type,
            "subjects": ["point-a", "point-b"],
            "tolerance": 0.02,
            "mandatory": True,
        }
        value.update(updates)
        return value

    def test_valid_alignment_relation(self):
        result = self.validate(self.payload(relations=[self.relation()]))
        self.assertEqual(result["relations"][0]["type"], "aligned-x")

    def test_valid_ordering_relation(self):
        result = self.validate(self.payload(relations=[self.relation("ordered-left-to-right")]))
        self.assertEqual(result["relations"][0]["type"], "ordered-left-to-right")

    def test_unsupported_relation_type(self):
        self.assert_invalid(self.payload(relations=[self.relation("diagonal-ish")]), "unsupported")

    def test_relation_wrong_number_of_subjects(self):
        self.assert_invalid(
            self.payload(relations=[self.relation("centered-under", subjects=["point-a", "point-b", "point-c"])]),
            "2–2",
        )

    def test_relation_missing_subject_reference(self):
        self.assert_invalid(
            self.payload(relations=[self.relation(subjects=["point-a", "missing"])]),
            "missing subject",
        )

    def contour(self, **updates: object) -> dict[str, object]:
        value: dict[str, object] = {
            "name": "curve-a",
            "region": "region-a",
            "start": "point-a",
            "end": "point-b",
            "landmarks": ["point-a", "point-c", "point-b"],
            "turning_points": ["point-c"],
            "major_tangent_direction": 0.0,
            "nearby_anchor_distances": [],
            "mandatory": True,
        }
        value.update(updates)
        return value

    def test_valid_ordered_contour_landmarks(self):
        result = self.validate(self.payload(contours=[self.contour()]))
        self.assertEqual(result["contours"][0]["turningPoints"], ["point-c"])

    def test_contour_missing_start_or_end(self):
        item = self.contour()
        del item["start"]
        self.assert_invalid(self.payload(contours=[item]), "start")

    def test_contour_duplicate_landmark(self):
        self.assert_invalid(
            self.payload(contours=[self.contour(landmarks=["point-a", "point-c", "point-c", "point-b"])]),
            "duplicate references",
        )

    def test_contour_invalid_reference(self):
        self.assert_invalid(
            self.payload(contours=[self.contour(landmarks=["point-a", "missing", "point-b"])]),
            "missing landmark",
        )

    def test_traversal_like_entity_and_svg_id(self):
        entity = {"name": "object-a", "region": "../region", "svg_id": "object-a", "mandatory": True}
        self.assert_invalid(self.payload(entities=[entity]), "region")
        entity["region"] = "region-a"
        entity["svg_id"] = "folder/object"
        self.assert_invalid(self.payload(entities=[entity]), "svg_id")

    def test_malformed_json_cli_summary(self):
        with tempfile.TemporaryDirectory(prefix="geometry-json-test-") as temp_name:
            path = Path(temp_name) / "geometry.json"
            path.write_text("{not-json", encoding="utf-8")
            argv = ["validate_geometry_inventory.py", str(path), "--format", "json", "--path-mode", "basename"]
            output = io.StringIO()
            with mock.patch.object(sys, "argv", argv), redirect_stdout(output):
                self.assertEqual(validate_geometry_inventory.main(), 1)
            self.assertFalse(json.loads(output.getvalue())["schemaValid"])


class GeometryActualValidationTests(GeometryInventorySchemaTests):
    def actual(self, points: list[dict[str, object]], **updates: object) -> dict[str, object]:
        value: dict[str, object] = {
            "version": 1,
            "coordinateMode": "normalized",
            "points": points,
            "relations": [],
            "planes": [],
        }
        value.update(updates)
        return value

    def point(self, name: str, x: float, y: float) -> dict[str, object]:
        return {"name": name, "x": x, "y": y}

    def evaluate(self, expected_payload: dict[str, object], actual_payload: dict[str, object]) -> dict[str, object]:
        expected = validate_geometry_inventory.validate_inventory(expected_payload)
        actual = validate_geometry_inventory.validate_actual(actual_payload, expected, "actual.json")
        return validate_geometry_inventory.evaluate_geometry(expected, actual)

    def two_landmarks(self) -> list[dict[str, object]]:
        return [
            self.landmark("point-a", 0.2, 0.3, tolerance=0.02),
            self.landmark("point-b", 0.5, 0.3, tolerance=0.02),
        ]

    def test_landmark_within_tolerance(self):
        expected = self.payload(landmarks=[self.landmark("point-a", 0.2, 0.3, tolerance=0.03)])
        result = self.evaluate(expected, self.actual([self.point("point-a", 0.22, 0.3)]))
        self.assertFalse(result["automaticReadinessBlocked"])

    def test_landmark_outside_tolerance(self):
        expected = self.payload(landmarks=[self.landmark("point-a", 0.2, 0.3, tolerance=0.01)])
        result = self.evaluate(expected, self.actual([self.point("point-a", 0.22, 0.3)]))
        self.assertTrue(result["automaticReadinessBlocked"])

    def test_alignment_pass_and_fail(self):
        expected = self.payload(landmarks=self.two_landmarks(), relations=[self.relation("aligned-x")])
        passed = self.evaluate(expected, self.actual([self.point("point-a", 0.2, 0.2), self.point("point-b", 0.21, 0.6)]))
        failed = self.evaluate(expected, self.actual([self.point("point-a", 0.2, 0.2), self.point("point-b", 0.3, 0.6)]))
        self.assertTrue(passed["relationValidation"][0]["passed"])
        self.assertFalse(failed["relationValidation"][0]["passed"])

    def test_ordering_pass_and_fail(self):
        expected = self.payload(
            landmarks=self.two_landmarks(), relations=[self.relation("ordered-left-to-right", tolerance=0.0)]
        )
        passed = self.evaluate(expected, self.actual([self.point("point-a", 0.2, 0.3), self.point("point-b", 0.5, 0.3)]))
        failed = self.evaluate(expected, self.actual([self.point("point-a", 0.6, 0.3), self.point("point-b", 0.5, 0.3)]))
        self.assertTrue(passed["relationValidation"][0]["passed"])
        self.assertFalse(failed["relationValidation"][0]["passed"])

    def test_baseline_pass_and_fail(self):
        expected = self.payload(landmarks=self.two_landmarks(), relations=[self.relation("shares-baseline")])
        passed = self.evaluate(expected, self.actual([self.point("point-a", 0.2, 0.3), self.point("point-b", 0.5, 0.31)]))
        failed = self.evaluate(expected, self.actual([self.point("point-a", 0.2, 0.3), self.point("point-b", 0.5, 0.4)]))
        self.assertTrue(passed["relationValidation"][0]["passed"])
        self.assertFalse(failed["relationValidation"][0]["passed"])

    def test_relative_spacing_pass_and_fail(self):
        landmarks = [
            self.landmark("point-a", 0.1, 0.3, tolerance=1.0),
            self.landmark("point-b", 0.3, 0.3, tolerance=1.0),
            self.landmark("point-c", 0.5, 0.3, tolerance=1.0),
        ]
        relation = self.relation(
            "relative-spacing",
            subjects=["point-a", "point-b", "point-c"],
            expected_spacing=[0.2, 0.2],
            axis="x",
            tolerance=0.01,
        )
        expected = self.payload(landmarks=landmarks, relations=[relation])
        passed = self.evaluate(expected, self.actual([self.point("point-a", 0.1, 0.3), self.point("point-b", 0.3, 0.3), self.point("point-c", 0.5, 0.3)]))
        failed = self.evaluate(expected, self.actual([self.point("point-a", 0.1, 0.3), self.point("point-b", 0.4, 0.3), self.point("point-c", 0.5, 0.3)]))
        self.assertTrue(passed["relationValidation"][0]["passed"])
        self.assertFalse(failed["relationValidation"][0]["passed"])

    def test_plane_child_orientation_metadata_pass_and_fail(self):
        expected = self.payload(planes=[self.plane()])
        points = [self.point(item["name"], item["x"], item["y"]) for item in expected["landmarks"]]
        passed = self.evaluate(expected, self.actual(points, planes=[{
            "name": "plane-a", "child_orientation_consistent": True, "relative_scale_progression": []
        }]))
        failed = self.evaluate(expected, self.actual(points, planes=[{
            "name": "plane-a", "child_orientation_consistent": False, "relative_scale_progression": []
        }]))
        self.assertTrue(passed["planeValidation"][0]["passed"])
        self.assertFalse(failed["planeValidation"][0]["passed"])

    def test_contour_endpoint_and_turning_pass_and_fail(self):
        expected = self.payload(contours=[self.contour()])
        passing_points = [self.point(item["name"], item["x"], item["y"]) for item in expected["landmarks"]]
        passed = self.evaluate(expected, self.actual(passing_points))
        failing_points = [dict(item) for item in passing_points]
        failing_points[1]["x"] = 0.8
        failing_points[2]["y"] = 0.9
        failed = self.evaluate(expected, self.actual(failing_points))
        self.assertTrue(passed["contourValidation"][0]["endpointPassed"])
        self.assertTrue(passed["contourValidation"][0]["turningPointPassed"])
        self.assertFalse(failed["contourValidation"][0]["endpointPassed"])
        self.assertFalse(failed["contourValidation"][0]["turningPointPassed"])

    def test_cli_returns_nonzero_for_mandatory_geometry_failure(self):
        with tempfile.TemporaryDirectory(prefix="geometry-cli-test-") as temp_name:
            base = Path(temp_name)
            inventory = base / "expected.json"
            actual = base / "actual.json"
            inventory.write_text(json.dumps(self.payload(landmarks=[self.landmark("point-a", 0.2, 0.3, tolerance=0.01)])), encoding="utf-8")
            actual.write_text(json.dumps(self.actual([self.point("point-a", 0.4, 0.3)])), encoding="utf-8")
            argv = ["validate_geometry_inventory.py", str(inventory), "--actual", str(actual), "--format", "json", "--path-mode", "basename"]
            with mock.patch.object(sys, "argv", argv), redirect_stdout(io.StringIO()):
                self.assertEqual(validate_geometry_inventory.main(), 2)


class BoundaryExtractionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.np, cls.Image, cls.ImageFilter = compare_boundaries.require_dependencies()

    def split_image(self, left=(30, 70, 120), right=(220, 180, 60), antialias=False):
        array = self.np.zeros((64, 64, 3), dtype=self.np.uint8)
        array[:, :32] = left
        array[:, 32:] = right
        if antialias:
            array[:, 31] = tuple((3 * a + b) // 4 for a, b in zip(left, right))
            array[:, 32] = tuple((a + 3 * b) // 4 for a, b in zip(left, right))
        return self.Image.fromarray(array, mode="RGB")

    def extract(self, image, **extraction_updates):
        config = boundary_config()
        config["extraction"].update(extraction_updates)
        nms = compare_boundaries.prepare_nms(image, config["preprocessing"]["blurRadius"], self.np, self.ImageFilter)
        resolved = compare_boundaries.resolve_thresholds(nms, config, self.np)
        return compare_boundaries.extract_with_resolved(
            nms, resolved, config["extraction"]["minimumComponentSize"], self.np
        )

    def test_simple_two_color_boundary(self):
        boundaries = self.extract(self.split_image())
        self.assertGreater(int(boundaries.sum()), 40)

    def test_antialiased_edge_remains_thin_and_detectable(self):
        boundaries = self.extract(self.split_image(antialias=True))
        self.assertGreater(int(boundaries.sum()), 40)
        self.assertLess(int(boundaries.sum()), 180)

    def test_low_contrast_edge_with_authored_floor(self):
        boundaries = self.extract(self.split_image((100, 100, 100), (108, 108, 108)), thresholdFloor=0.5)
        self.assertGreater(int(boundaries.sum()), 40)

    def test_tiny_isolated_component_removal(self):
        image = self.split_image()
        array = self.np.asarray(image).copy()
        array[8, 8] = (250, 10, 10)
        image = self.Image.fromarray(array, mode="RGB")
        unfiltered = self.extract(image, minimumComponentSize=1)
        filtered = self.extract(image, minimumComponentSize=20)
        self.assertGreater(int(unfiltered.sum()), int(filtered.sum()))
        self.assertGreater(int(filtered.sum()), 40)


class BoundaryMetricTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.np, _, _ = compare_boundaries.require_dependencies()

    def vertical(self, column: int, width=12, height=10):
        mask = self.np.zeros((height, width), dtype=bool)
        mask[:, column] = True
        return mask

    def test_identical_boundaries(self):
        mask = self.vertical(4)
        metrics, _, _ = compare_boundaries.compute_metrics(mask, mask, [0.5], 1.0, self.np)
        self.assertEqual(metrics["referenceToCandidate"]["mean"], 0.0)
        self.assertEqual(metrics["candidateToReference"]["p95"], 0.0)
        self.assertEqual(metrics["tolerances"][0]["f1"], 1.0)

    def test_shifted_boundary_and_tolerance_inside_outside(self):
        metrics, _, _ = compare_boundaries.compute_metrics(
            self.vertical(3), self.vertical(5), [1.0, 2.0], 1.0, self.np
        )
        self.assertEqual(metrics["referenceToCandidate"]["mean"], 2.0)
        self.assertEqual(metrics["candidateToReference"]["mean"], 2.0)
        self.assertEqual(metrics["tolerances"][0]["f1"], 0.0)
        self.assertEqual(metrics["tolerances"][1]["f1"], 1.0)

    def test_missing_boundary(self):
        empty = self.np.zeros((10, 12), dtype=bool)
        metrics, _, _ = compare_boundaries.compute_metrics(self.vertical(4), empty, [1.0], 1.0, self.np)
        self.assertEqual(metrics["candidateBoundaryCount"], 0)
        self.assertEqual(metrics["tolerances"][0]["recall"], 0.0)
        self.assertEqual(metrics["tolerances"][0]["f1"], 0.0)

    def test_extra_boundary(self):
        empty = self.np.zeros((10, 12), dtype=bool)
        metrics, _, _ = compare_boundaries.compute_metrics(empty, self.vertical(4), [1.0], 1.0, self.np)
        self.assertEqual(metrics["referenceBoundaryCount"], 0)
        self.assertEqual(metrics["tolerances"][0]["precision"], 0.0)
        self.assertEqual(metrics["tolerances"][0]["f1"], 0.0)

    def test_precision_recall_asymmetry(self):
        reference = self.vertical(3)
        candidate = self.vertical(3) | self.vertical(9)
        metrics, _, _ = compare_boundaries.compute_metrics(reference, candidate, [0.5], 1.0, self.np)
        self.assertEqual(metrics["tolerances"][0]["recall"], 1.0)
        self.assertEqual(metrics["tolerances"][0]["precision"], 0.5)
        self.assertAlmostEqual(metrics["tolerances"][0]["f1"], 2 / 3)
        self.assertGreater(metrics["candidateToReference"]["mean"], metrics["referenceToCandidate"]["mean"])


class BoundaryRegionValidationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="boundary-region-test-")
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)

    def write(self, payload: object) -> Path:
        path = self.base / "regions.json"
        path.write_text(json.dumps(payload), encoding="utf-8")
        return path

    def valid(self, **updates: object):
        value = {"name": "focus", "x": 0.1, "y": 0.2, "width": 0.4, "height": 0.5}
        value.update(updates)
        return value

    def assert_invalid(self, payload: object, pattern: str, maximum=8):
        with self.assertRaisesRegex((ValueError, FileNotFoundError), pattern):
            mode, regions = compare_boundaries.load_regions(self.write(payload), maximum)
            compare_boundaries.region_boxes(mode, regions, (100, 80), (50, 40))

    def test_valid_normalized_and_pixel_region(self):
        mode, regions = compare_boundaries.load_regions(
            self.write({"coordinateMode": "normalized", "regions": [self.valid()]}), 8
        )
        self.assertEqual(compare_boundaries.region_boxes(mode, regions, (100, 80), (50, 40))[0]["analysisPixelBox"], [5, 8, 25, 28])
        mode, regions = compare_boundaries.load_regions(self.write({
            "coordinateMode": "pixels",
            "regions": [{"name": "pixel", "x": 10, "y": 8, "width": 20, "height": 16}],
        }), 8)
        self.assertEqual(compare_boundaries.region_boxes(mode, regions, (100, 80), (50, 40))[0]["analysisPixelBox"], [5, 4, 15, 12])

    def test_invalid_bounds(self):
        self.assert_invalid({"coordinateMode": "normalized", "regions": [self.valid(width=1.0)]}, "out of normalized bounds")

    def test_duplicate_name(self):
        self.assert_invalid({"coordinateMode": "normalized", "regions": [self.valid(), self.valid(name="FOCUS")]}, "duplicate")

    def test_too_many_regions(self):
        self.assert_invalid({"coordinateMode": "normalized", "regions": [self.valid(name=f"r{i}") for i in range(3)]}, "maximum", maximum=2)

    def test_traversal_like_name(self):
        self.assert_invalid({"coordinateMode": "normalized", "regions": [self.valid(name="../escape")]}, "region names")


class BoundaryReproducibilityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.np, cls.Image, cls.ImageFilter = compare_boundaries.require_dependencies()

    def image(self, split: int):
        array = self.np.zeros((48, 48, 3), dtype=self.np.uint8)
        array[:, :split] = (30, 80, 140)
        array[:, split:] = (220, 170, 50)
        return self.Image.fromarray(array, mode="RGB")

    def test_same_config_gives_same_output(self):
        config = boundary_config()
        first = compare_boundaries.extract_boundary_pair(self.image(24), self.image(25), config, self.np, self.ImageFilter)
        second = compare_boundaries.extract_boundary_pair(self.image(24), self.image(25), config, self.np, self.ImageFilter)
        self.assertTrue(self.np.array_equal(first[0], second[0]))
        self.assertTrue(self.np.array_equal(first[1], second[1]))
        self.assertEqual(first[2], second[2])

    def test_reference_resolved_threshold_is_reused_unchanged(self):
        config = boundary_config()
        reference = self.image(20)
        candidate = self.image(29)
        _, candidate_boundaries, resolved = compare_boundaries.extract_boundary_pair(
            reference, candidate, config, self.np, self.ImageFilter
        )
        candidate_nms = compare_boundaries.prepare_nms(
            candidate, config["preprocessing"]["blurRadius"], self.np, self.ImageFilter
        )
        manual = compare_boundaries.extract_with_resolved(
            candidate_nms, resolved, config["extraction"]["minimumComponentSize"], self.np
        )
        self.assertTrue(self.np.array_equal(candidate_boundaries, manual))

    def test_candidate_specific_config_key_is_rejected(self):
        with tempfile.TemporaryDirectory(prefix="boundary-config-test-") as temp_name:
            path = Path(temp_name) / "config.json"
            payload = boundary_config(candidateThreshold=9)
            path.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "candidate-specific tuning is forbidden"):
                compare_boundaries.load_method_config(path)


class BoundaryOutputSafetyTests(unittest.TestCase):
    def test_prefix_traversal_is_rejected(self):
        for value in ("../escape", "folder/name", "folder\\name", "C:\\escape"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                compare_boundaries.validate_prefix(value)

    def test_atomic_commit_rolls_back_partial_set(self):
        with tempfile.TemporaryDirectory(prefix="boundary-atomic-test-") as temp_name:
            base = Path(temp_name)
            staged = {"one": base / "staged-one", "two": base / "missing-two"}
            final = {"one": base / "final-one", "two": base / "final-two"}
            staged["one"].write_text("new", encoding="utf-8")
            with self.assertRaises(OSError):
                compare_boundaries.commit_outputs(staged, final, False, base)
            self.assertFalse(final["one"].exists())

    def test_synthetic_end_to_end_outputs_and_overwrite_refusal(self):
        np, Image, _ = compare_boundaries.require_dependencies()
        with tempfile.TemporaryDirectory(prefix="boundary-integration-test-") as temp_name:
            base = Path(temp_name)
            reference = base / "reference.png"
            candidate = base / "candidate.png"
            config_path = base / "config.json"
            regions_path = base / "regions.json"
            output_dir = base / "outputs"
            reference_array = np.zeros((32, 32, 3), dtype=np.uint8)
            reference_array[:, :16] = (20, 70, 130)
            reference_array[:, 16:] = (230, 180, 50)
            candidate_array = reference_array.copy()
            candidate_array[:, 16:18] = (20, 70, 130)
            Image.fromarray(reference_array, mode="RGB").save(reference)
            Image.fromarray(candidate_array, mode="RGB").save(candidate)
            config_path.write_text(json.dumps(boundary_config()), encoding="utf-8")
            regions_path.write_text(json.dumps({
                "coordinateMode": "normalized",
                "regions": [{"name": "focus", "x": 0, "y": 0, "width": 1, "height": 1}],
            }), encoding="utf-8")
            argv = [
                "compare_boundaries.py", str(reference), str(candidate), "--config", str(config_path),
                "--regions-file", str(regions_path), "--output-dir", str(output_dir), "--prefix", "synthetic",
                "--path-mode", "basename", "--format", "json",
            ]
            with mock.patch.object(sys, "argv", argv), redirect_stdout(io.StringIO()):
                self.assertEqual(compare_boundaries.main(), 0)
            expected = {
                "synthetic-boundary-metrics.json", "synthetic-boundary-config-resolved.json",
                "synthetic-boundary-metrics.csv", "synthetic-reference-boundaries.png",
                "synthetic-candidate-boundaries.png", "synthetic-boundary-mismatch.png",
                "synthetic-region-focus-boundary-mismatch.png",
            }
            self.assertEqual({path.name for path in output_dir.iterdir()}, expected)
            report = json.loads((output_dir / "synthetic-boundary-metrics.json").read_text(encoding="utf-8"))
            self.assertTrue(report["configurationIntegrity"]["sharedResolvedConfig"])
            self.assertFalse(report["configurationIntegrity"]["candidateSpecificOverridesAccepted"])
            self.assertEqual(report["paths"]["reference"], "reference.png")
            with mock.patch.object(sys, "argv", argv), redirect_stdout(io.StringIO()), self.assertRaises(FileExistsError):
                compare_boundaries.main()


class RegionValidationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="region-validation-test-")
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)

    def write_payload(self, payload: object) -> Path:
        path = self.base / "regions.json"
        path.write_text(json.dumps(payload), encoding="utf-8")
        return path

    def valid_region(self, **updates: object) -> dict[str, object]:
        region: dict[str, object] = {"name": "focus", "x": 0.1, "y": 0.1, "width": 0.4, "height": 0.4}
        region.update(updates)
        return region

    def test_valid_normalized_and_pixel_regions(self):
        mode, regions = render_compare.load_regions(self.write_payload({"coordinateMode": "normalized", "regions": [self.valid_region()]}))
        self.assertEqual(render_compare.region_boxes(mode, regions, 100, 80)[0]["pixelBox"], [10, 8, 50, 40])
        mode, regions = render_compare.load_regions(self.write_payload({"coordinateMode": "pixels", "regions": [{"name": "pixels", "x": 1, "y": 2, "width": 10, "height": 11}]}))
        self.assertEqual(render_compare.region_boxes(mode, regions, 100, 80)[0]["pixelBox"], [1, 2, 11, 13])

    def assert_invalid(self, payload: object, pattern: str):
        with self.assertRaisesRegex((ValueError, FileNotFoundError), pattern):
            mode, regions = render_compare.load_regions(self.write_payload(payload))
            render_compare.region_boxes(mode, regions, 100, 100)

    def test_negative_coordinates(self):
        self.assert_invalid({"coordinateMode": "normalized", "regions": [self.valid_region(x=-0.1)]}, "negative")

    def test_zero_size_region(self):
        self.assert_invalid({"coordinateMode": "normalized", "regions": [self.valid_region(width=0)]}, "zero or negative")

    def test_out_of_bounds_region(self):
        self.assert_invalid({"coordinateMode": "pixels", "regions": [{"name": "focus", "x": 95, "y": 0, "width": 10, "height": 5}]}, "out of image bounds")

    def test_duplicate_names(self):
        self.assert_invalid({"coordinateMode": "normalized", "regions": [self.valid_region(), self.valid_region(name="FOCUS")]}, "duplicate")

    def test_too_many_regions(self):
        regions = [self.valid_region(name=f"r{index}") for index in range(render_compare.MAX_REGIONS + 1)]
        self.assert_invalid({"coordinateMode": "normalized", "regions": regions}, "maximum")

    def test_traversal_like_region_name(self):
        self.assert_invalid({"coordinateMode": "normalized", "regions": [self.valid_region(name="../escape")]}, "region names")

    def test_malformed_json(self):
        path = self.base / "regions.json"
        path.write_text("{not-json", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "malformed"):
            render_compare.load_regions(path)

    def test_wrong_image_dimensions(self):
        with self.assertRaisesRegex(RuntimeError, "renderer returned"):
            render_compare.validate_same_dimensions((99, 100), (100, 100))


class OutputSafetyTests(unittest.TestCase):
    def test_prefix_path_traversal_and_absolute_paths(self):
        for value in ("../escape", "folder/name", "folder\\name", "C:\\escape"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                render_compare.validate_prefix(value)

    def test_default_path_display_is_private(self):
        with tempfile.TemporaryDirectory(prefix="path-privacy-test-") as temp_name:
            cwd = Path(temp_name) / "workspace"
            outside = Path(temp_name) / "private" / "secret.svg"
            cwd.mkdir()
            outside.parent.mkdir()
            outside.write_text("x", encoding="utf-8")
            self.assertEqual(render_compare.display_path(outside, "relative", cwd), "secret.svg")
            self.assertEqual(audit_svg.display_path(outside, "basename", cwd), "secret.svg")

    def test_overwrite_is_refused_by_default(self):
        with tempfile.TemporaryDirectory(prefix="overwrite-test-") as temp_name:
            base = Path(temp_name)
            staged = {"one": base / "staged-one"}
            final = {"one": base / "final-one"}
            staged["one"].write_text("new", encoding="utf-8")
            final["one"].write_text("old", encoding="utf-8")
            with self.assertRaises(FileExistsError):
                render_compare.commit_outputs(staged, final, False, base)
            self.assertEqual(final["one"].read_text(encoding="utf-8"), "old")

    def test_atomic_commit_removes_partial_set_on_failure(self):
        with tempfile.TemporaryDirectory(prefix="atomic-output-test-") as temp_name:
            base = Path(temp_name)
            staged = {"one": base / "staged-one", "two": base / "missing-two"}
            final = {"one": base / "final-one", "two": base / "final-two"}
            staged["one"].write_text("new", encoding="utf-8")
            with self.assertRaises(OSError):
                render_compare.commit_outputs(staged, final, False, base)
            self.assertFalse(final["one"].exists())
            self.assertFalse(final["two"].exists())


class RegionIntegrationTests(unittest.TestCase):
    def test_synthetic_global_and_region_outputs(self):
        from PIL import Image

        with tempfile.TemporaryDirectory(prefix="region-integration-test-") as temp_name:
            base = Path(temp_name)
            reference = base / "reference.png"
            svg = base / "fixture.svg"
            regions = base / "regions.json"
            output_dir = base / "outputs"
            Image.new("RGB", (40, 30), (240, 240, 240)).save(reference)
            svg.write_text('<svg xmlns="http://www.w3.org/2000/svg" width="40" height="30" viewBox="0 0 40 30"><rect width="40" height="30" fill="#dddddd"/></svg>', encoding="utf-8")
            regions.write_text(json.dumps({
                "coordinateMode": "normalized",
                "regions": [
                    {"name": "upper", "x": 0, "y": 0, "width": 0.5, "height": 0.5},
                    {"name": "lower", "x": 0.5, "y": 0.5, "width": 0.5, "height": 0.5},
                ],
            }), encoding="utf-8")

            def fake_render(renderer, executable, svg_path, output, width, height, timeout, node_modules):
                rendered = Image.new("RGB", (width, height), (221, 221, 221))
                rendered.save(output)
                return "synthetic renderer"

            argv = [
                "render_compare.py", str(reference), str(svg), "--output-dir", str(output_dir),
                "--prefix", "synthetic", "--regions-file", str(regions), "--format", "json",
                "--path-mode", "basename",
            ]
            with mock.patch.object(sys, "argv", argv), \
                    mock.patch.object(render_compare, "choose_renderer", return_value=("synthetic", "synthetic")), \
                    mock.patch.object(render_compare, "render_svg", side_effect=fake_render), \
                    redirect_stdout(io.StringIO()):
                self.assertEqual(render_compare.main(), 0)

            expected = {
                "synthetic-preview.png", "synthetic-overlay.png", "synthetic-difference.png", "synthetic-regions.json",
                "synthetic-region-upper-reference.png", "synthetic-region-upper-preview.png",
                "synthetic-region-upper-overlay.png", "synthetic-region-upper-difference.png",
                "synthetic-region-lower-reference.png", "synthetic-region-lower-preview.png",
                "synthetic-region-lower-overlay.png", "synthetic-region-lower-difference.png",
            }
            self.assertEqual({path.name for path in output_dir.iterdir()}, expected)
            summary = json.loads((output_dir / "synthetic-regions.json").read_text(encoding="utf-8"))
            self.assertEqual(summary["regionCount"], 2)
            self.assertEqual([item["name"] for item in summary["regions"]], ["upper", "lower"])

            with mock.patch.object(sys, "argv", argv), redirect_stdout(io.StringIO()), self.assertRaises(FileExistsError):
                render_compare.main()


class AlphaCoverageIntegrationTests(unittest.TestCase):
    def run_fixture(self, gap: bool) -> tuple[int, dict[str, object]]:
        from PIL import Image

        with tempfile.TemporaryDirectory(prefix="alpha-integration-test-") as temp_name:
            base = Path(temp_name)
            reference = base / "reference.png"
            svg = base / "fixture.svg"
            output_dir = base / "outputs"
            Image.new("RGB", (12, 10), (240, 240, 240)).save(reference)
            svg.write_text(
                '<svg xmlns="http://www.w3.org/2000/svg" width="12" height="10" viewBox="0 0 12 10"><rect width="12" height="10" fill="#ddd"/></svg>',
                encoding="utf-8",
            )

            def fake_render(renderer, executable, svg_path, output, width, height, timeout, node_modules):
                rendered = Image.new("RGBA", (width, height), (221, 221, 221, 255))
                if gap:
                    rendered.putpixel((5, 5), (221, 221, 221, 0))
                rendered.save(output)
                return "synthetic renderer"

            argv = [
                "render_compare.py", str(reference), str(svg), "--output-dir", str(output_dir),
                "--prefix", "alpha", "--check-alpha-coverage", "--expected-opaque-reference",
                "--format", "json", "--path-mode", "basename",
            ]
            with mock.patch.object(sys, "argv", argv), \
                    mock.patch.object(render_compare, "choose_renderer", return_value=("synthetic", "synthetic")), \
                    mock.patch.object(render_compare, "render_svg", side_effect=fake_render), \
                    redirect_stdout(io.StringIO()):
                exit_code = render_compare.main()
            summary_path = output_dir / "alpha-alpha-coverage.json"
            self.assertTrue(summary_path.is_file())
            summary = json.loads(summary_path.read_text(encoding="utf-8"))
            self.assertEqual(
                {path.name for path in output_dir.iterdir()},
                {"alpha-preview.png", "alpha-overlay.png", "alpha-difference.png", "alpha-alpha-coverage.json"},
            )
            return exit_code, summary

    def test_machine_readable_alpha_pass(self):
        exit_code, summary = self.run_fixture(False)
        self.assertEqual(exit_code, 0)
        self.assertEqual(summary["status"], "pass")

    def test_machine_readable_alpha_blocker_exit(self):
        exit_code, summary = self.run_fixture(True)
        self.assertEqual(exit_code, 2)
        self.assertEqual(summary["status"], "fail")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run synthetic boundary, geometry, gradient, coverage, inventory, and output-safety tests without real artwork."
    )
    parser.add_argument("--verbose", action="store_true", help="Show each test name.")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    suite = unittest.defaultTestLoader.loadTestsFromModule(__import__(__name__))
    result = unittest.TextTestRunner(verbosity=2 if args.verbose else 1).run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())
