#!/usr/bin/env python3
"""Safely render an audited SVG and create an atomic diagnostic PNG set."""

from __future__ import annotations

import argparse
import importlib.util
import json
import math
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path, PureWindowsPath
from xml.etree import ElementTree as ET


DIMENSION = re.compile(
    r"^\s*([-+]?(?:\d*\.\d+|\d+\.?)(?:[eE][-+]?\d+)?)\s*(px)?\s*$",
    re.IGNORECASE,
)
URL_REFERENCE = re.compile(r"url\(\s*['\"]?([^)'\"\s]+)", re.IGNORECASE)


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


def require_pillow():
    try:
        from PIL import Image, ImageChops
    except ImportError as exc:
        raise RuntimeError("Pillow is required for raster comparison but is unavailable") from exc
    return Image, ImageChops


def parse_dimension(value: str | None) -> float | None:
    if value is None:
        return None
    match = DIMENSION.fullmatch(value)
    if not match:
        return None
    number = float(match.group(1))
    return number if math.isfinite(number) and number > 0 else None


def parse_svg_for_render(path: Path) -> tuple[float, str, dict[str, object]]:
    text = path.read_text(encoding="utf-8")
    lowered = text.lower()
    if "<!doctype" in lowered or "<!entity" in lowered:
        raise ValueError("SVG contains a DOCTYPE or entity declaration; rendering is blocked")
    root = ET.fromstring(text)
    if local(root.tag) != "svg":
        raise ValueError("XML root element is not <svg>")

    viewbox = root.get("viewBox")
    ratio = None
    source = None
    if viewbox:
        tokens = [item for item in re.split(r"[\s,]+", viewbox.strip()) if item]
        try:
            values = [float(item) for item in tokens]
        except ValueError:
            values = []
        if len(values) == 4 and all(math.isfinite(item) for item in values) and values[2] > 0 and values[3] > 0:
            ratio = values[2] / values[3]
            source = "viewBox"
    if ratio is None:
        width, height = parse_dimension(root.get("width")), parse_dimension(root.get("height"))
        if width is not None and height is not None:
            ratio = width / height
            source = "width-height"
    if ratio is None:
        raise ValueError("SVG canvas is not reliably measurable from a valid viewBox or numeric width/height")

    counts = {"image": 0, "foreignObject": 0, "script": 0, "externalReferences": 0, "embeddedData": 0}
    for element in root.iter():
        tag = local(element.tag)
        if tag in counts:
            counts[tag] += 1
        for attr_name, attr_value in element.attrib.items():
            if local(attr_name) == "href":
                target = attr_value.strip()
                if target.lower().startswith("data:"):
                    counts["embeddedData"] += 1
                elif not target.startswith("#"):
                    counts["externalReferences"] += 1
            for target in URL_REFERENCE.findall(attr_value):
                if target.lower().startswith("data:"):
                    counts["embeddedData"] += 1
                elif not target.startswith("#"):
                    counts["externalReferences"] += 1
        if tag == "style" and element.text:
            if "@import" in element.text.lower():
                counts["externalReferences"] += 1
            for target in URL_REFERENCE.findall(element.text):
                if target.lower().startswith("data:"):
                    counts["embeddedData"] += 1
                elif not target.startswith("#"):
                    counts["externalReferences"] += 1

    blocked = [name for name, count in counts.items() if count]
    if blocked:
        detail = ", ".join(f"{name}={counts[name]}" for name in blocked)
        raise ValueError(f"SVG failed raster/external-resource safety audit ({detail})")
    return ratio, source or "unknown", {"passed": True, **counts}


def validate_prefix(prefix: str) -> str:
    if not prefix or not prefix.strip():
        raise ValueError("--prefix must not be empty")
    if prefix in {".", ".."} or ".." in prefix:
        raise ValueError("--prefix must be a filename stem without path traversal")
    if "/" in prefix or "\\" in prefix:
        raise ValueError("--prefix must not contain path separators")
    if Path(prefix).is_absolute() or PureWindowsPath(prefix).is_absolute() or PureWindowsPath(prefix).drive:
        raise ValueError("--prefix must not be an absolute path or contain a drive prefix")
    if ":" in prefix or "\x00" in prefix:
        raise ValueError("--prefix contains an unsafe filename character")
    return prefix


def output_paths(output_dir: Path, prefix: str) -> dict[str, Path]:
    outputs = {
        "preview": (output_dir / f"{prefix}-preview.png").resolve(),
        "overlay": (output_dir / f"{prefix}-overlay.png").resolve(),
        "difference": (output_dir / f"{prefix}-difference.png").resolve(),
    }
    for path in outputs.values():
        try:
            path.relative_to(output_dir)
        except ValueError as exc:
            raise ValueError("constructed output path escapes --output-dir") from exc
    return outputs


def command_version(command: list[str]) -> str | None:
    try:
        completed = subprocess.run(command, capture_output=True, text=True, timeout=5, check=False)
    except (OSError, subprocess.SubprocessError):
        return None
    output = (completed.stdout or completed.stderr).strip().splitlines()
    return output[0][:240] if output else None


def sharp_available(node: str | None, node_modules: Path | None) -> bool:
    if not node:
        return False
    environment = os.environ.copy()
    if node_modules:
        environment["NODE_PATH"] = str(node_modules)
    try:
        completed = subprocess.run([node, "-e", "require('sharp');"], capture_output=True, text=True, timeout=8, check=False, env=environment)
        return completed.returncode == 0
    except (OSError, subprocess.SubprocessError):
        return False


def choose_renderer(requested: str, node_arg: Path | None, node_modules: Path | None) -> tuple[str, str | None]:
    node = str(node_arg) if node_arg else shutil.which("node")
    candidates = {
        "inkscape": shutil.which("inkscape"),
        "rsvg-convert": shutil.which("rsvg-convert"),
        "magick": shutil.which("magick"),
        "cairosvg": "python-module" if importlib.util.find_spec("cairosvg") else None,
        "sharp": node if sharp_available(node, node_modules) else None,
    }
    if requested != "auto":
        if not candidates.get(requested):
            raise RuntimeError(f"requested renderer '{requested}' is unavailable")
        return requested, candidates[requested]
    for name in ("inkscape", "rsvg-convert", "cairosvg", "sharp", "magick"):
        if candidates.get(name):
            return name, candidates[name]
    raise RuntimeError("no supported local SVG renderer found (Inkscape, rsvg-convert, CairoSVG, Sharp, or ImageMagick)")


def run_command(command: list[str], timeout: int, environment: dict[str, str] | None = None) -> None:
    completed = subprocess.run(command, capture_output=True, text=True, timeout=timeout, check=False, env=environment)
    if completed.returncode != 0:
        detail = (completed.stderr or completed.stdout).strip()[-1000:]
        raise RuntimeError(f"renderer failed with exit {completed.returncode}: {detail}")


def render_svg(renderer: str, executable: str | None, svg: Path, output: Path, width: int, height: int, timeout: int, node_modules: Path | None) -> str:
    if renderer == "inkscape":
        run_command([executable or "inkscape", str(svg), f"--export-filename={output}", "--export-type=png", f"--export-width={width}", f"--export-height={height}"], timeout)
        return command_version([executable or "inkscape", "--version"]) or "Inkscape"
    if renderer == "rsvg-convert":
        run_command([executable or "rsvg-convert", "-w", str(width), "-h", str(height), "-o", str(output), str(svg)], timeout)
        return command_version([executable or "rsvg-convert", "--version"]) or "rsvg-convert"
    if renderer == "magick":
        run_command([executable or "magick", str(svg), "-resize", f"{width}x{height}!", str(output)], timeout)
        return command_version([executable or "magick", "-version"]) or "ImageMagick"
    if renderer == "cairosvg":
        import cairosvg
        cairosvg.svg2png(url=str(svg), write_to=str(output), output_width=width, output_height=height)
        return f"CairoSVG {getattr(cairosvg, '__version__', 'unknown')}"
    if renderer == "sharp":
        code = (
            "const sharp=require('sharp');"
            "const [input,output,width,height]=process.argv.slice(1);"
            "sharp(input).resize(Number(width),Number(height),{fit:'fill'}).png().toFile(output)"
            ".catch(e=>{console.error(e.message);process.exit(1);});"
        )
        environment = os.environ.copy()
        if node_modules:
            environment["NODE_PATH"] = str(node_modules)
        run_command([executable or "node", "-e", code, str(svg), str(output), str(width), str(height)], timeout, environment)
        return f"Sharp via {command_version([executable or 'node', '--version']) or 'Node.js'}"
    raise RuntimeError(f"unsupported renderer: {renderer}")


def composite_white(image, Image):
    rgba = image.convert("RGBA")
    base = Image.new("RGBA", rgba.size, (255, 255, 255, 255))
    return Image.alpha_composite(base, rgba).convert("RGB")


def difference_metrics(difference) -> tuple[float, float, int]:
    histogram = difference.histogram()
    channels = len(difference.getbands())
    samples = difference.width * difference.height * channels
    absolute_sum = squared_sum = maximum = 0
    for channel in range(channels):
        for value, count in enumerate(histogram[channel * 256:(channel + 1) * 256]):
            absolute_sum += value * count
            squared_sum += value * value * count
            if count and value > maximum:
                maximum = value
    return absolute_sum / samples, math.sqrt(squared_sum / samples), maximum


def commit_outputs(staged: dict[str, Path], final: dict[str, Path], overwrite: bool, temp_dir: Path) -> None:
    backups: dict[str, Path] = {}
    committed: list[str] = []
    try:
        if overwrite:
            for name, target in final.items():
                if target.exists():
                    backup = temp_dir / f"backup-{name}.png"
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


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Render an audited SVG at reference dimensions and atomically create preview, overlay, and difference PNGs.")
    parser.add_argument("reference", type=Path, help="Reference raster image.")
    parser.add_argument("svg", type=Path, help="SVG to render; it is never modified.")
    parser.add_argument("--output-dir", type=Path, required=True, help="Directory for diagnostic PNGs.")
    parser.add_argument("--prefix", help="Safe single filename stem; defaults to the SVG stem.")
    parser.add_argument("--renderer", choices=["auto", "inkscape", "rsvg-convert", "cairosvg", "sharp", "magick"], default="auto")
    parser.add_argument("--node-executable", type=Path, help="Optional Node.js executable for the Sharp fallback.")
    parser.add_argument("--node-modules", type=Path, help="Optional node_modules directory containing Sharp.")
    parser.add_argument("--timeout", type=int, default=60, help="Renderer timeout in seconds.")
    parser.add_argument("--aspect-tolerance", type=float, default=0.01, help="Maximum relative SVG/reference aspect-ratio difference (default: 0.01).")
    parser.add_argument("--allow-aspect-mismatch", action="store_true", help="Explicitly allow a distorted diagnostic render; never normal fidelity evidence.")
    parser.add_argument("--overwrite", action="store_true", help="Explicitly allow replacing an existing complete diagnostic set.")
    parser.add_argument("--format", choices=["markdown", "json"], default="markdown")
    parser.add_argument("--path-mode", choices=["basename", "relative", "absolute"], default="relative", help="Path display policy for reports.")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    cwd = Path.cwd().resolve()
    if not args.reference.is_file():
        raise FileNotFoundError(f"reference not found: {display_path(args.reference, args.path_mode, cwd)}")
    if not args.svg.is_file():
        raise FileNotFoundError(f"SVG not found: {display_path(args.svg, args.path_mode, cwd)}")
    if args.timeout <= 0:
        raise ValueError("--timeout must be positive")
    if not math.isfinite(args.aspect_tolerance) or args.aspect_tolerance < 0:
        raise ValueError("--aspect-tolerance must be a finite non-negative number")

    prefix = validate_prefix(args.prefix if args.prefix is not None else args.svg.stem)
    output_dir = args.output_dir.resolve()
    outputs = output_paths(output_dir, prefix)
    existing = [path.name for path in outputs.values() if path.exists()]
    if existing and not args.overwrite:
        raise FileExistsError("refusing to overwrite existing outputs: " + ", ".join(existing))

    svg_ratio, ratio_source, resource_audit = parse_svg_for_render(args.svg.resolve())
    Image, ImageChops = require_pillow()
    with Image.open(args.reference) as opened:
        reference_rgba = opened.convert("RGBA")
    width, height = reference_rgba.size
    if width <= 0 or height <= 0:
        raise ValueError("reference has invalid dimensions")
    reference_ratio = width / height
    relative_difference = abs(svg_ratio - reference_ratio) / reference_ratio
    mismatch = relative_difference > args.aspect_tolerance
    if mismatch and not args.allow_aspect_mismatch:
        raise ValueError(
            "aspect ratio mismatch exceeds tolerance: "
            f"SVG={svg_ratio:.8g}, reference={reference_ratio:.8g}, "
            f"relative difference={relative_difference:.6g}, tolerance={args.aspect_tolerance:.6g}"
        )

    renderer, executable = choose_renderer(args.renderer, args.node_executable, args.node_modules)
    output_dir.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="render-compare-", dir=output_dir) as temp_name:
        temp_dir = Path(temp_name)
        temporary_render = temp_dir / "renderer-output.png"
        staged = {
            "preview": temp_dir / "preview.png",
            "overlay": temp_dir / "overlay.png",
            "difference": temp_dir / "difference.png",
        }
        renderer_version = render_svg(renderer, executable, args.svg.resolve(), temporary_render, width, height, args.timeout, args.node_modules.resolve() if args.node_modules else None)
        with Image.open(temporary_render) as opened:
            preview_rgba = opened.convert("RGBA")
        if preview_rgba.size != (width, height):
            raise RuntimeError(f"renderer returned {preview_rgba.size}, expected {(width, height)}")
        preview_rgba.save(staged["preview"])
        reference_rgb = composite_white(reference_rgba, Image)
        preview_rgb = composite_white(preview_rgba, Image)
        Image.blend(reference_rgb, preview_rgb, 0.5).save(staged["overlay"])
        difference = ImageChops.difference(reference_rgb, preview_rgb)
        difference.save(staged["difference"])
        mae, rmse, maximum = difference_metrics(difference)
        if not all(path.is_file() and path.stat().st_size > 0 for path in staged.values()):
            raise RuntimeError("diagnostic staging set is incomplete")
        commit_outputs(staged, outputs, args.overwrite, temp_dir)

    aspect = {
        "svg": round(svg_ratio, 8), "svgSource": ratio_source,
        "reference": round(reference_ratio, 8),
        "relativeDifference": round(relative_difference, 8),
        "tolerance": args.aspect_tolerance,
        "mismatch": mismatch,
        "mismatchExplicitlyAllowed": bool(mismatch and args.allow_aspect_mismatch),
        "diagnosticMayBeDistorted": bool(mismatch),
    }
    report = {
        "pathMode": args.path_mode,
        "reference": display_path(args.reference, args.path_mode, cwd),
        "svg": display_path(args.svg, args.path_mode, cwd),
        "dimensions": {"width": width, "height": height},
        "aspectRatio": aspect,
        "resourceAudit": resource_audit,
        "renderer": renderer,
        "rendererVersion": renderer_version,
        "outputs": {name: display_path(path, args.path_mode, cwd) for name, path in outputs.items()},
        "metrics": {"maeRgb": round(mae, 4), "rmseRgb": round(rmse, 4), "maxChannelDifference": maximum},
        "notes": [
            "Metrics are diagnostic and do not prove visual fidelity or editability.",
            "The reference raster was used only for comparison and was not embedded in the SVG.",
            "A comparison with an explicitly allowed aspect mismatch may be distorted and is not normal positional-fidelity evidence." if mismatch else "SVG and reference aspect ratios are within the declared tolerance.",
        ],
    }
    if args.format == "json":
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print("# Render Comparison\n")
        print(f"- Path display mode: `{args.path_mode}`")
        print(f"- Reference: `{report['reference']}`")
        print(f"- SVG: `{report['svg']}`")
        print(f"- Dimensions: {width} × {height}")
        print(f"- SVG aspect ratio: {svg_ratio:.8g} (from {ratio_source})")
        print(f"- Reference aspect ratio: {reference_ratio:.8g}")
        print(f"- Relative ratio difference: {relative_difference:.6g}")
        print(f"- Aspect mismatch: {'yes' if mismatch else 'no'}")
        print(f"- Mismatch explicitly allowed: {'yes' if mismatch and args.allow_aspect_mismatch else 'no'}")
        print(f"- External-resource audit: {'passed' if resource_audit['passed'] else 'failed'}")
        print(f"- Renderer: {renderer_version}")
        for name in ("preview", "overlay", "difference"):
            print(f"- {name.title()}: `{report['outputs'][name]}`")
        print(f"- RGB MAE: {mae:.4f}")
        print(f"- RGB RMSE: {rmse:.4f}")
        print(f"- Maximum channel difference: {maximum}")
        if mismatch:
            print("\nWARNING: The explicitly allowed comparison may be distorted and is not normal positional-fidelity evidence.")
        print("\nMetrics are diagnostic only; human design/editability review is still required.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        raise SystemExit(130)
    except Exception as exc:
        print(f"render comparison failed: {exc}", file=sys.stderr)
        raise SystemExit(1)
