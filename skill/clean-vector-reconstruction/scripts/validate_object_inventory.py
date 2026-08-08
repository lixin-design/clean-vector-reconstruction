#!/usr/bin/env python3
"""Validate a case-authored required object-family inventory without image inference."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


SAFE_NAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{0,63}$")
MAX_REGIONS = 24
MAX_FAMILIES_PER_REGION = 64
MAX_TOTAL_FAMILIES = 512
MAX_COUNT = 1_000_000
VALID_STATUSES = {"pass", "missing", "below-minimum", "above-maximum"}


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


def validate_name(value: object, label: str) -> str:
    if not isinstance(value, str) or not SAFE_NAME.fullmatch(value):
        raise ValueError(
            f"{label} must use 1–64 ASCII letters, digits, hyphens, or underscores "
            "and start with a letter or digit"
        )
    if value in {".", ".."} or ".." in value or "/" in value or "\\" in value or ":" in value:
        raise ValueError(f"{label} contains path traversal or an unsafe filename character")
    return value


def validate_count(value: object, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{label} must be an integer")
    if value < 0:
        raise ValueError(f"{label} must be nonnegative")
    if value > MAX_COUNT:
        raise ValueError(f"{label} exceeds maximum of {MAX_COUNT}")
    return value


def computed_status(expected_min: int, expected_max: int, reconstructed_count: int) -> str:
    if expected_min > 0 and reconstructed_count == 0:
        return "missing"
    if reconstructed_count < expected_min:
        return "below-minimum"
    if reconstructed_count > expected_max:
        return "above-maximum"
    return "pass"


def validate_inventory(payload: object, shown_path: str = "inventory.json", path_mode: str = "basename") -> dict[str, object]:
    if not isinstance(payload, dict):
        raise ValueError("inventory JSON must be an object")
    raw_regions = payload.get("regions")
    if not isinstance(raw_regions, list) or not raw_regions:
        raise ValueError("regions must be a non-empty list")
    if len(raw_regions) > MAX_REGIONS:
        raise ValueError(f"regions list exceeds maximum of {MAX_REGIONS}")

    seen_regions: set[str] = set()
    region_records: list[dict[str, object]] = []
    total_families = 0
    missing: list[dict[str, str]] = []
    below: list[dict[str, object]] = []
    above: list[dict[str, object]] = []

    for raw_region in raw_regions:
        if not isinstance(raw_region, dict):
            raise ValueError("each region must be an object")
        region_name = validate_name(raw_region.get("name"), "region name")
        folded_region = region_name.casefold()
        if folded_region in seen_regions:
            raise ValueError(f"duplicate region name: {region_name}")
        seen_regions.add(folded_region)

        raw_families = raw_region.get("required_families")
        if not isinstance(raw_families, list) or not raw_families:
            raise ValueError(f"region '{region_name}' required_families must be a non-empty list")
        if len(raw_families) > MAX_FAMILIES_PER_REGION:
            raise ValueError(
                f"region '{region_name}' exceeds maximum of {MAX_FAMILIES_PER_REGION} families"
            )
        total_families += len(raw_families)
        if total_families > MAX_TOTAL_FAMILIES:
            raise ValueError(f"inventory exceeds maximum of {MAX_TOTAL_FAMILIES} total families")

        seen_families: set[str] = set()
        family_records: list[dict[str, object]] = []
        for raw_family in raw_families:
            if not isinstance(raw_family, dict):
                raise ValueError(f"families in region '{region_name}' must be objects")
            family_name = validate_name(raw_family.get("family"), "family name")
            folded_family = family_name.casefold()
            if folded_family in seen_families:
                raise ValueError(f"duplicate family name in region '{region_name}': {family_name}")
            seen_families.add(folded_family)

            expected_min = validate_count(raw_family.get("expected_min"), f"{region_name}/{family_name} expected_min")
            expected_max = validate_count(raw_family.get("expected_max"), f"{region_name}/{family_name} expected_max")
            reconstructed = validate_count(
                raw_family.get("reconstructed_count"),
                f"{region_name}/{family_name} reconstructed_count",
            )
            if expected_min > expected_max:
                raise ValueError(f"{region_name}/{family_name} expected_min must not exceed expected_max")

            authored_status = raw_family.get("status")
            if authored_status not in VALID_STATUSES:
                raise ValueError(
                    f"{region_name}/{family_name} status must be one of: "
                    + ", ".join(sorted(VALID_STATUSES))
                )
            status = computed_status(expected_min, expected_max, reconstructed)
            if authored_status != status:
                raise ValueError(
                    f"{region_name}/{family_name} authored status '{authored_status}' "
                    f"does not match computed status '{status}'"
                )

            record = {
                "family": family_name,
                "expectedMin": expected_min,
                "expectedMax": expected_max,
                "reconstructedCount": reconstructed,
                "status": status,
            }
            family_records.append(record)
            identity = {"region": region_name, "family": family_name}
            if status == "missing":
                missing.append(identity)
            elif status == "below-minimum":
                below.append({**identity, "expectedMin": expected_min, "reconstructedCount": reconstructed})
            elif status == "above-maximum":
                above.append({**identity, "expectedMax": expected_max, "reconstructedCount": reconstructed})

        region_records.append({
            "name": region_name,
            "requiredFamilyCount": len(family_records),
            "families": family_records,
            "complete": all(item["status"] == "pass" for item in family_records),
        })

    blocked = bool(missing or below or above)
    return {
        "file": shown_path,
        "pathMode": path_mode,
        "valid": True,
        "regionCount": len(region_records),
        "requiredFamilyCount": total_families,
        "regions": region_records,
        "missingRequiredFamilies": missing,
        "belowMinimumFamilies": below,
        "aboveMaximumFamilies": above,
        "minimumSemanticCompletenessPassed": not blocked,
        "automaticReadinessBlocked": blocked,
        "notes": [
            "Counts are case-authored evidence; this validator does not infer objects from images.",
            "A valid inventory can still block readiness when required counts are outside their authored ranges.",
        ],
    }


def load_inventory(path: Path, path_mode: str, cwd: Path) -> dict[str, object]:
    if not path.is_file():
        raise FileNotFoundError(f"inventory not found: {display_path(path, path_mode, cwd)}")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"malformed inventory JSON: {exc.msg}") from exc
    return validate_inventory(payload, display_path(path, path_mode, cwd), path_mode)


def markdown(report: dict[str, object]) -> str:
    lines = [
        "# Required Object-Family Inventory Audit",
        "",
        f"- File: `{report['file']}`",
        f"- Regions: {report['regionCount']}",
        f"- Required families: {report['requiredFamilyCount']}",
        f"- Minimum semantic completeness: {'passed' if report['minimumSemanticCompletenessPassed'] else 'failed'}",
        f"- Automatic readiness blocked: {'yes' if report['automaticReadinessBlocked'] else 'no'}",
        "",
        "| Region | Family | Expected | Reconstructed | Status |",
        "|---|---|---:|---:|---|",
    ]
    for region in report["regions"]:
        for family in region["families"]:
            lines.append(
                f"| `{region['name']}` | `{family['family']}` | "
                f"{family['expectedMin']}–{family['expectedMax']} | "
                f"{family['reconstructedCount']} | `{family['status']}` |"
            )
    lines.extend(["", *[f"- Note: {note}" for note in report["notes"]]])
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate a case-authored required object-family inventory without computer-vision inference."
    )
    parser.add_argument("inventory", type=Path, help="JSON inventory to validate.")
    parser.add_argument("--format", choices=["json", "markdown"], default="json")
    parser.add_argument(
        "--path-mode",
        choices=["basename", "relative", "absolute"],
        default="relative",
        help="Path display policy for reports.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    report = load_inventory(args.inventory.resolve(), args.path_mode, Path.cwd().resolve())
    print(json.dumps(report, indent=2, ensure_ascii=False) if args.format == "json" else markdown(report))
    return 2 if report["automaticReadinessBlocked"] else 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        raise SystemExit(130)
    except (OSError, ValueError) as exc:
        print(f"object-family inventory validation failed: {exc}", file=sys.stderr)
        raise SystemExit(1)
