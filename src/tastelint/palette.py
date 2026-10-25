"""Color helpers for contrast and hue checks. No network, no extra deps."""

from __future__ import annotations

import colorsys
import re

# Tailwind v3 neutrals. Used when a class string names a gray instead of a hex.
NEUTRALS: dict[str, dict[int, str]] = {
    "gray": {
        50: "#f9fafb",
        100: "#f3f4f6",
        200: "#e5e7eb",
        300: "#d1d5db",
        400: "#9ca3af",
        500: "#6b7280",
        600: "#4b5563",
        700: "#374151",
        800: "#1f2937",
        900: "#111827",
    },
    "slate": {
        50: "#f8fafc",
        100: "#f1f5f9",
        200: "#e2e8f0",
        300: "#cbd5e1",
        400: "#94a3b8",
        500: "#64748b",
        600: "#475569",
        700: "#334155",
        800: "#1e293b",
        900: "#0f172a",
    },
    "zinc": {
        50: "#fafafa",
        100: "#f4f4f5",
        200: "#e4e4e7",
        300: "#d4d4d8",
        400: "#a1a1aa",
        500: "#71717a",
        600: "#52525b",
        700: "#3f3f46",
        800: "#27272a",
        900: "#18181b",
    },
    "neutral": {
        50: "#fafafa",
        100: "#f5f5f5",
        200: "#e5e5e5",
        300: "#d4d4d4",
        400: "#a3a3a3",
        500: "#737373",
        600: "#525252",
        700: "#404040",
        800: "#262626",
        900: "#171717",
    },
    "stone": {
        50: "#fafaf9",
        100: "#f5f5f4",
        200: "#e7e5e4",
        300: "#d6d3d1",
        400: "#a8a29e",
        500: "#78716c",
        600: "#57534e",
        700: "#44403c",
        800: "#292524",
        900: "#1c1917",
    },
}

NAMED = {
    "white": (255, 255, 255),
    "black": (0, 0, 0),
    "purple": (128, 0, 128),
    "rebeccapurple": (102, 51, 153),
    "indigo": (75, 0, 130),
    "violet": (238, 130, 238),
    "blue": (0, 0, 255),
    "fuchsia": (255, 0, 255),
    "magenta": (255, 0, 255),
}

_HEX = re.compile(r"#([0-9a-fA-F]{3,8})\b")
_RGB = re.compile(
    r"rgba?\(\s*(\d{1,3})\s*,\s*(\d{1,3})\s*,\s*(\d{1,3})(?:\s*,\s*([0-9.]+))?\s*\)",
    re.IGNORECASE,
)
_UTIL = re.compile(r"^(text|bg)-(white|black|[a-z]+)(?:-(\d{2,3}))?$")


def hex_to_rgb(raw: str) -> tuple[int, int, int] | None:
    chars = raw.strip().lstrip("#")
    if len(chars) in {3, 4}:
        chars = "".join(c * 2 for c in chars)
    if len(chars) not in {6, 8}:
        return None
    if len(chars) == 8:
        alpha = int(chars[6:8], 16) / 255
        if alpha < 0.85:
            return None
    try:
        return (int(chars[0:2], 16), int(chars[2:4], 16), int(chars[4:6], 16))
    except ValueError:
        return None


def hsl(rgb: tuple[int, int, int]) -> tuple[float, float, float]:
    h, light, sat = colorsys.rgb_to_hls(*(c / 255 for c in rgb))
    return h * 360, light, sat


def chroma(rgb: tuple[int, int, int]) -> int:
    return max(rgb) - min(rgb)


def achromatic(rgb: tuple[int, int, int]) -> bool:
    """True for grays, off-whites, and near-blacks. Warm paper still counts."""
    return chroma(rgb) <= 42


def relative_luminance(rgb: tuple[int, int, int]) -> float:
    def channel(c: int) -> float:
        v = c / 255
        return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4

    r, g, b = (channel(c) for c in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast_ratio(a: tuple[int, int, int], b: tuple[int, int, int]) -> float:
    hi, lo = sorted((relative_luminance(a), relative_luminance(b)), reverse=True)
    return (hi + 0.05) / (lo + 0.05)


def is_violet_accent(rgb: tuple[int, int, int]) -> bool:
    """Indigo, violet, purple, fuchsia used as a default brand button."""
    hue, light, sat = hsl(rgb)
    return 235 <= hue <= 315 and sat >= 0.45 and 0.30 <= light <= 0.80


def is_cool_stop(rgb: tuple[int, int, int]) -> bool:
    """A blue-to-magenta gradient stop. Plain clay and amber are not this."""
    hue, light, sat = hsl(rgb)
    return 200 <= hue <= 320 and sat >= 0.35 and 0.25 <= light <= 0.85


def colors_in(value: str) -> list[tuple[int, int, int]]:
    found: list[tuple[int, int, int]] = []
    for match in _HEX.finditer(value):
        rgb = hex_to_rgb(match.group(1))
        if rgb:
            found.append(rgb)
    for match in _RGB.finditer(value):
        alpha = match.group(4)
        if alpha is not None and float(alpha) < 0.85:
            continue
        found.append((int(match.group(1)), int(match.group(2)), int(match.group(3))))
    return found


def plain_color(value: str) -> tuple[int, int, int] | None:
    """First solid color in a CSS value. Gradients and images return None."""
    if not value:
        return None
    low = value.lower()
    if "gradient" in low or "url(" in low:
        return None
    colors = colors_in(value)
    if colors:
        return colors[0]
    for name, rgb in NAMED.items():
        if re.search(rf"\b{name}\b", low):
            return rgb
    return None


def utility_color(token: str) -> tuple[str, tuple[int, int, int]] | None:
    """Map a Tailwind color utility to (role, rgb). Role is 'text' or 'bg'."""
    base = token.split("/")[0]
    match = _UTIL.match(base)
    if not match:
        return None
    role, family, shade = match.group(1), match.group(2), match.group(3)
    if family in {"white", "black"}:
        return role, NAMED[family]
    if shade is None or family not in NEUTRALS:
        return None
    hex_value = NEUTRALS[family].get(int(shade))
    if not hex_value:
        return None
    rgb = hex_to_rgb(hex_value)
    if rgb is None:
        return None
    return role, rgb
