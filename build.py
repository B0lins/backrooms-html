#!/usr/bin/env python3
"""
Generates a standalone version of the game for a specific theme (friend group).

Usage: python3 build.py <theme>
Ex:    python3 build.py janta   -> generates backrooms-janta.html

Convention: each customizable asset has a "base name" (e.g. "enemy") and lives
under a level folder: assets/<theme>/level_<N>/<base-name>.*

Lookup order for a given theme/level/asset (first match wins):
  1. assets/<theme>/level_<N>/<base-name>.*
  2. assets/default/level_<N>/<base-name>.*
  3. assets/<theme>/level_1/<base-name>.*      (falls back to that theme's level 1)
  4. assets/default/level_1/<base-name>.*      (final fallback)
"""
import base64
import pathlib
import sys

ROOT = pathlib.Path(__file__).parent
TEMPLATE = ROOT / "template" / "backrooms.template.html"
ASSETS = ROOT / "assets"

MIME_TYPES = {
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".mp3": "audio/mpeg",
}

# Each entry links a template placeholder to a binary asset's "base name", per level
BINARY_ASSET_PLACEHOLDERS = {
    1: {
        "__LEVEL1_VILLAIN_IMAGE_DATA_URI__": "enemy",
        "__LEVEL1_CHASE_AUDIO_DATA_URI__": "chase",
        "__LEVEL1_COLLECTIBLE_IMAGE_DATA_URI__": "collectible",
        "__LEVEL1_JUMPSCARE_AUDIO_DATA_URI__": "jumpscare",
        "__LEVEL1_HEARTBEAT_AUDIO_DATA_URI__": "heartbeat",
    },
    2: {
        "__LEVEL2_VILLAIN_IMAGE_DATA_URI__": "enemy",
        "__LEVEL2_CHASE_AUDIO_DATA_URI__": "chase",
        "__LEVEL2_COLLECTIBLE_IMAGE_DATA_URI__": "collectible",
        "__LEVEL2_JUMPSCARE_AUDIO_DATA_URI__": "jumpscare",
        "__LEVEL2_AMBIENT_AUDIO_DATA_URI__": "ambient",
        "__LEVEL2_HEARTBEAT_AUDIO_DATA_URI__": "heartbeat",
    },
}

# Plain-text (non-base64) placeholders, per level
TEXT_ASSET_PLACEHOLDERS = {
    1: {
        "__COLLECTIBLE_COUNT__": "collectible_count",
        "__WIN_SCREEN_TEXT__": "win_text",
    },
}


def find_asset(theme, level, base_name):
    candidates = [
        ASSETS / theme / f"level_{level}",
        ASSETS / "default" / f"level_{level}",
    ]
    if level != 1:
        candidates += [
            ASSETS / theme / "level_1",
            ASSETS / "default" / "level_1",
        ]
    for folder in candidates:
        matches = sorted(folder.glob(base_name + ".*"))
        if matches:
            return matches[0]
    raise FileNotFoundError(
        f"No '{base_name}.*' file found for theme '{theme}' level {level} "
        f"(checked theme/default x level_{level}/level_1)"
    )


def to_data_uri(path):
    mime = MIME_TYPES.get(path.suffix.lower(), "application/octet-stream")
    b64 = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{b64}"


def build(theme):
    content = TEMPLATE.read_text(encoding="utf-8")

    for level, placeholders in BINARY_ASSET_PLACEHOLDERS.items():
        for placeholder, base_name in placeholders.items():
            asset_path = find_asset(theme, level, base_name)
            content = content.replace(placeholder, to_data_uri(asset_path))
            print(f"  level {level} {base_name}: using {asset_path.relative_to(ROOT)}")

    for level, placeholders in TEXT_ASSET_PLACEHOLDERS.items():
        for placeholder, base_name in placeholders.items():
            text_path = find_asset(theme, level, base_name)
            value = text_path.read_text(encoding="utf-8").strip()
            content = content.replace(placeholder, value)
            print(f"  level {level} {base_name}: using {text_path.relative_to(ROOT)} (value: {value})")

    out_path = ROOT / f"backrooms-{theme}.html"
    out_path.write_text(content, encoding="utf-8")
    print(f"Generated: {out_path.name}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 build.py <theme>")
        sys.exit(1)
    build(sys.argv[1])
