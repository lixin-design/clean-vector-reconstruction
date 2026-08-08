#!/usr/bin/env python3
"""Read-only preflight for clean vector reconstruction tools."""

from __future__ import annotations

import argparse
import importlib.metadata
import importlib.util
import json
import platform
import shutil
import subprocess
import sys
from pathlib import Path


DEFAULT_TOOLS = ["inkscape", "rsvg-convert", "magick", "node"]
DEFAULT_MODULES = ["PIL", "numpy", "cv2", "cairosvg", "vtracer"]
VERSION_ARGS = {
    "inkscape": ["--version"],
    "rsvg-convert": ["--version"],
    "magick": ["-version"],
    "node": ["--version"],
}


def display_path(path: Path | str, mode: str, cwd: Path) -> str:
    """Return a report-safe path while retaining real paths for internal use."""
    resolved = Path(path).resolve()
    if mode == "absolute":
        return str(resolved)
    if mode == "basename":
        return resolved.name
    try:
        return str(resolved.relative_to(cwd.resolve()))
    except ValueError:
        return resolved.name


def split_csv(values: list[str] | None, defaults: list[str]) -> list[str]:
    if not values:
        return defaults.copy()
    result: list[str] = []
    for value in values:
        result.extend(item.strip() for item in value.split(",") if item.strip())
    return list(dict.fromkeys(result))


def executable_record(name: str, required: bool, path_mode: str, cwd: Path) -> dict[str, object]:
    path = shutil.which(name)
    record: dict[str, object] = {
        "kind": "executable",
        "name": name,
        "required": required,
        "available": bool(path),
        "path": display_path(path, path_mode, cwd) if path else None,
        "version": None,
    }
    if not path:
        return record
    args = VERSION_ARGS.get(name, ["--version"])
    try:
        completed = subprocess.run(
            [path, *args], capture_output=True, text=True, timeout=5, check=False
        )
        output = (completed.stdout or completed.stderr).strip().splitlines()
        record["version"] = output[0][:240] if output else f"exit {completed.returncode}"
    except (OSError, subprocess.SubprocessError) as exc:
        record["version"] = f"unavailable: {exc}"
    return record


def module_record(name: str, required: bool) -> dict[str, object]:
    available = importlib.util.find_spec(name) is not None
    version = None
    distribution = None
    if available:
        mapping = importlib.metadata.packages_distributions()
        candidates = mapping.get(name, [])
        for candidate in candidates:
            try:
                version = importlib.metadata.version(candidate)
                distribution = candidate
                break
            except importlib.metadata.PackageNotFoundError:
                continue
    return {
        "kind": "python-module",
        "name": name,
        "distribution": distribution,
        "required": required,
        "available": available,
        "version": version,
    }


def markdown_report(report: dict[str, object]) -> str:
    lines = [
        "# Vector Reconstruction Environment Check",
        "",
        f"- Python: `{report['python']['version']}`",
        f"- Executable: `{report['python']['executable']}`",
        f"- Platform: `{report['python']['platform']}`",
        f"- Path display mode: `{report['pathMode']}`",
        "",
        "| Kind | Name | Required | Available | Version / path |",
        "|---|---|:---:|:---:|---|",
    ]
    for item in report["checks"]:
        detail = item.get("version") or item.get("path") or item.get("distribution") or "—"
        lines.append(
            f"| {item['kind']} | `{item['name']}` | "
            f"{'yes' if item['required'] else 'no'} | "
            f"{'yes' if item['available'] else 'no'} | {detail} |"
        )
    lines += [
        "",
        f"- Missing required items: {len(report['missingRequired'])}",
        "- No installation or environment change was performed.",
    ]
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Check Python plus optional local SVG/image tools without installing or modifying anything."
    )
    parser.add_argument(
        "--tool", action="append", help="Executable name or comma-separated names; repeatable."
    )
    parser.add_argument(
        "--module", action="append", help="Python module name or comma-separated names; repeatable."
    )
    parser.add_argument("--require-tool", action="append", default=[], help="Tool that must be available.")
    parser.add_argument("--require-module", action="append", default=[], help="Python module that must be available.")
    parser.add_argument("--format", choices=["markdown", "json"], default="markdown")
    parser.add_argument(
        "--path-mode",
        choices=["basename", "relative", "absolute"],
        default="relative",
        help="Path display policy for reports; absolute paths require explicit selection.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    required_tools = set(split_csv(args.require_tool, []))
    required_modules = set(split_csv(args.require_module, []))
    tools = list(dict.fromkeys(split_csv(args.tool, DEFAULT_TOOLS) + list(required_tools)))
    modules = list(dict.fromkeys(split_csv(args.module, DEFAULT_MODULES) + list(required_modules)))

    cwd = Path.cwd().resolve()
    checks = [executable_record(name, name in required_tools, args.path_mode, cwd) for name in tools]
    checks.extend(module_record(name, name in required_modules) for name in modules)
    missing = [item["name"] for item in checks if item["required"] and not item["available"]]
    report: dict[str, object] = {
        "python": {
            "version": platform.python_version(),
            "executable": display_path(sys.executable, args.path_mode, cwd),
            "platform": platform.platform(),
            "required": True,
            "available": True,
        },
        "checks": checks,
        "missingRequired": missing,
        "readOnly": True,
        "pathMode": args.path_mode,
    }
    print(json.dumps(report, indent=2, ensure_ascii=False) if args.format == "json" else markdown_report(report))
    return 2 if missing else 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        raise SystemExit(130)
    except Exception as exc:
        print(f"environment check failed: {exc}", file=sys.stderr)
        raise SystemExit(1)
