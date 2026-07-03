"""Render terminal log text as a PNG screenshot-style image."""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


def _load_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = (
        "Cascadia Mono",
        "Consolas",
        "Courier New",
        "Lucida Console",
    )
    for name in candidates:
        try:
            return ImageFont.truetype(name, size=size)
        except OSError:
            continue
    return ImageFont.load_default()


def render_terminal_image(
    log_text: str,
    output_path: Path,
    title: str = "PowerShell",
    width: int = 1100,
    padding: int = 24,
    font_size: int = 15,
    line_spacing: int = 4,
) -> Path:
    font = _load_font(font_size)
    lines = log_text.splitlines() or [""]

    dummy = Image.new("RGB", (width, 10))
    draw = ImageDraw.Draw(dummy)
    max_line_width = 0
    line_height = 0
    for line in lines:
        bbox = draw.textbbox((0, 0), line or " ", font=font)
        max_line_width = max(max_line_width, bbox[2] - bbox[0])
        line_height = max(line_height, bbox[3] - bbox[1])

    content_width = min(width - padding * 2, max(max_line_width + 20, 700))
    content_height = padding * 2 + len(lines) * (line_height + line_spacing) + 36
    image = Image.new("RGB", (content_width + padding * 2, content_height), "#1e1e1e")
    draw = ImageDraw.Draw(image)

    header_h = 36
    draw.rectangle((0, 0, image.width, header_h), fill="#2d2d2d")
    for i, color in enumerate(("#ff5f57", "#febc2e", "#28c840")):
        draw.ellipse((16 + i * 22, 12, 28 + i * 22, 24), fill=color)
    draw.text((image.width // 2 - 80, 10), title, fill="#d4d4d4", font=font)

    y = header_h + padding
    for line in lines:
        color = "#4ec9b0" if line.strip().startswith("[Task") else "#d4d4d4"
        if "->" in line and "True" in line:
            color = "#9cdcfe"
        if "Saved" in line or "summary" in line.lower():
            color = "#b5cea8"
        if "error" in line.lower() or "failed" in line.lower():
            color = "#f48771"
        draw.text((padding, y), line, fill=color, font=font)
        y += line_height + line_spacing

    output_path.parent.mkdir(parents=True, exist_ok=True)
    image.save(output_path, format="PNG", optimize=True)
    return output_path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("log_file", type=Path)
    parser.add_argument("output_png", type=Path)
    parser.add_argument("--title", default="PowerShell — salesnow-jp-web-scraping-test")
    args = parser.parse_args()
    text = args.log_file.read_text(encoding="utf-8", errors="replace")
    path = render_terminal_image(text, args.output_png, title=args.title)
    print(path)


if __name__ == "__main__":
    main()
