#!/usr/bin/env python3
"""Generate every app's theme files from the palettes in palettes/."""

import json
import math
import tomllib
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
TRANSPARENT = "#00000000"
ZED_SCHEMA = "https://zed.dev/schema/themes/v0.2.0.json"
ANSI_NAMES = ["black", "red", "green", "yellow", "blue", "magenta", "cyan", "white"]
# libm differs by an ulp between macOS and Linux, so unrounded output drifts across platforms.
OKLCH_DECIMALS = 6

type Palette = dict[str, Any]

ZED_SYNTAX = {
    "attribute": ("attribute", None),
    "boolean": ("constant", None),
    "comment": ("comment", "italic"),
    "comment.doc": ("comment", "italic"),
    "constant": ("constant", None),
    "constructor": ("type", None),
    "emphasis": ("plain", "italic"),
    "emphasis.strong": ("plain", "bold"),
    "enum": ("type", None),
    "function": ("function", None),
    "function.macro": ("attribute", None),
    "keyword": ("keyword", None),
    "label": ("attribute", None),
    "link_text": ("link", None),
    "link_uri": ("link", None),
    "namespace": ("namespace", None),
    "number": ("number", None),
    "operator": ("punctuation", None),
    "preproc": ("attribute", None),
    "property": ("variable", None),
    "punctuation": ("punctuation", None),
    "string": ("string", None),
    "string.escape": ("number", None),
    "string.regex": ("regex", None),
    "string.special": ("string", None),
    "string.special.symbol": ("constant", None),
    "tag": ("tag", None),
    "text.literal": ("literal", None),
    "title": ("plain", "bold"),
    "type": ("type", None),
    "type.parameter": ("type_parameter", None),
    "variable": ("variable", None),
    "variable.parameter": ("variable", None),
    "variant": ("constant", None),
}

XCODE_OVERRIDES = {
    "comment": "syntax.comment",
    "commentEmphasized": "syntax.comment_emphasized",
    "currentLineHighlight": "ui.hover",
    "insertionPointColor": "ui.cursor",
    "invisibles": "ui.invisible",
    "keyword": "syntax.keyword",
    "keyword.attribute": "syntax.attribute",
    "link": "syntax.link",
    "markdown": "syntax.literal",
    "memberDeclaration": "syntax.function",
    "number": "syntax.number",
    "number.character": "syntax.number",
    "otherMember": "syntax.variable",
    "otherMember.constant": "syntax.constant",
    "otherMember.function": "syntax.function_system",
    "otherMember.variable": "syntax.variable",
    "otherType": "syntax.type_system",
    "otherType.class": "syntax.type_system",
    "otherType.type": "syntax.type_system",
    "plainText": "syntax.plain",
    "preprocessor": "syntax.attribute",
    "preprocessor.macro": "syntax.attribute",
    "preprocessor.macroSystem": "syntax.attribute",
    "projectMember": "syntax.variable",
    "projectMember.constant": "syntax.constant",
    "projectMember.function": "syntax.function",
    "projectMember.variable": "syntax.variable",
    "projectType": "syntax.type",
    "projectType.class": "syntax.type",
    "projectType.type": "syntax.type",
    "selectedTextBackgroundColor": "ui.selection",
    "string": "syntax.string",
    "string.regex": "syntax.regex",
    "typeDeclaration": "syntax.type",
}


def slug(palette: Palette) -> str:
    return palette["name"].lower().replace(" ", "-")


def zed_syntax_style(colour: str, style: str | None) -> dict[str, Any]:
    if style == "bold":
        return {"color": colour, "font_weight": 700}
    if style == "italic":
        return {"color": colour, "font_style": "italic"}
    return {"color": colour}


def zed_style(palette: Palette) -> dict[str, Any]:
    ui, ansi, syntax = palette["ui"], palette["ansi"], palette["syntax"]
    style = {
        "accents": ui["accents"],
        "background": ui["panel"],
        "border": ui["border"],
        "border.disabled": ui["border"],
        "border.focused": ui["accent"],
        "border.selected": ui["accent"],
        "border.transparent": TRANSPARENT,
        "border.variant": ui["border_variant"],
        "editor.active_line.background": ui["hover"],
        "editor.active_line_number": ui["foreground"],
        "editor.background": ui["background"],
        "editor.document_highlight.bracket_background": ui["selection"],
        "editor.document_highlight.read_background": ui["selection"],
        "editor.document_highlight.write_background": ui["selection"],
        "editor.foreground": ui["foreground"],
        "editor.gutter.background": ui["background"],
        "editor.highlighted_line.background": ui["hover"],
        "editor.indent_guide": ui["border"],
        "editor.indent_guide_active": ui["indent_active"],
        "editor.invisible": ui["invisible"],
        "editor.line_number": ui["quiet"],
        "editor.subheader.background": ui["panel"],
        "editor.wrap_guide": ui["border"],
        "element.active": ui["selection"],
        "element.background": ui["element"],
        "element.hover": ui["hover"],
        "element.selected": ui["selection"],
        "elevated_surface.background": ui["background"],
        "ghost_element.active": ui["selection"],
        "ghost_element.background": TRANSPARENT,
        "ghost_element.hover": ui["hover"],
        "ghost_element.selected": ui["element"],
        "icon": ui["foreground"],
        "icon.accent": ui["accent"],
        "icon.disabled": ui["quiet"],
        "icon.muted": ui["muted"],
        "icon.placeholder": ui["quiet"],
        "link_text.hover": ui["accent_strong"],
        "pane.focused_border": ui["accent"],
        "pane_group.border": ui["border"],
        "panel.background": ui["panel"],
        "panel.focused_border": ui["accent"],
        "panel.indent_guide": ui["border"],
        "panel.indent_guide_active": ui["indent_active"],
        "players": [
            {
                "background": ui["cursor"],
                "cursor": ui["cursor"],
                "selection": ui["selection"],
            },
        ],
        "scrollbar.thumb.background": ui["indent_active"] + "50",
        "scrollbar.thumb.hover_background": ui["muted"] + "80",
        "scrollbar.track.background": TRANSPARENT,
        "scrollbar.track.border": TRANSPARENT,
        "search.match_background": ui["find"],
        "status_bar.background": ui["panel"],
        "surface.background": ui["panel"],
        "syntax": {
            token: zed_syntax_style(syntax[role], font)
            for token, (role, font) in ZED_SYNTAX.items()
        },
        "tab.active_background": ui["background"],
        "tab.inactive_background": ui["panel"],
        "tab_bar.background": ui["panel"],
        "terminal.background": ui["background"],
        "terminal.bright_foreground": ansi["bright"][7],
        "terminal.foreground": ui["foreground"],
        "text": ui["foreground"],
        "text.accent": ui["accent_strong"],
        "text.disabled": ui["quiet"],
        "text.muted": ui["muted"],
        "text.placeholder": ui["quiet"],
        "title_bar.background": ui["panel"],
        "title_bar.inactive_background": ui["panel"],
        "toolbar.background": ui["background"],
    }
    for name, colour in palette["status"].items():
        style[name] = colour
        style[f"{name}.background"] = colour + "20"
        style[f"{name}.border"] = colour
    for index, name in enumerate(ANSI_NAMES):
        style[f"terminal.ansi.{name}"] = ansi["normal"][index]
        style[f"terminal.ansi.bright_{name}"] = ansi["bright"][index]
    return dict(sorted(style.items()))


def zed_family(palettes: list[Palette]) -> dict[str, Any]:
    return {
        "$schema": ZED_SCHEMA,
        "name": "Geist",
        "author": "brzzdev",
        "themes": [
            {"name": p["name"], "appearance": p["appearance"], "style": zed_style(p)}
            for p in palettes
        ],
    }


def ghostty(palette: Palette) -> str:
    ui, ansi = palette["ui"], palette["ansi"]
    lines = [
        f"background = {ui['background']}",
        f"foreground = {ui['foreground']}",
        f"cursor-color = {ui['cursor']}",
        f"cursor-text = {ui['background']}",
        f"selection-background = {ui['selection']}",
        f"selection-foreground = {ui['foreground']}",
        "",
    ]
    colours = ansi["normal"] + ansi["bright"]
    lines += [f"palette = {index}={colour}" for index, colour in enumerate(colours)]
    return "\n".join(lines) + "\n"


def oklch(hex_colour: str) -> tuple[float, float, float]:
    def linear(channel: str) -> float:
        c = int(channel, 16) / 255
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4

    r, g, b = (linear(hex_colour[i : i + 2]) for i in (1, 3, 5))
    lms = (
        0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b,
        0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b,
        0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b,
    )
    l_, m_, s_ = (math.copysign(abs(v) ** (1 / 3), v) for v in lms)
    lightness = 0.2104542553 * l_ + 0.7936177850 * m_ - 0.0040720468 * s_
    a = 1.9779984951 * l_ - 2.4285922050 * m_ + 0.4505937099 * s_
    b = 0.0259040371 * l_ + 0.7827717662 * m_ - 0.8086757660 * s_
    return lightness, math.hypot(a, b), math.atan2(b, a) % math.tau


def xcode_colour(hex_colour: str) -> dict[str, Any]:
    lightness, chroma, hue = (round(v, OKLCH_DECIMALS) for v in oklch(hex_colour))
    if chroma == 0:
        # A grey's hue is noise from cancelling terms and can straddle a rounding boundary.
        hue = 0.0
    return {
        "wrapped": {
            "oklch": {
                "chroma": {"kind": {"exact": {"_0": chroma}}},
                "gamut": {"P3": {}},
                "hue": {"radiansValue": hue},
                "lightness": {"kind": {"exact": {"_0": lightness}}},
                "opacity": 1,
            },
        },
    }


def xcode_recipe(palette: Palette) -> dict[str, Any]:
    def lookup(path: str) -> str:
        group, key = path.split(".")
        return palette[group][key]

    overrides: list[Any] = []
    for token, path in XCODE_OVERRIDES.items():
        overrides += [token, {"color": {"_0": xcode_colour(lookup(path))}}]
    return {
        "name": palette["name"],
        "recipe": {
            "background": {
                "customColor": {"_0": xcode_colour(palette["ui"]["background"])}
            },
            "colorScheme": {palette["appearance"]: {}},
            "palette": {
                "colorGranularity": "expanded",
                "colorOverrides": overrides,
                "primary": {
                    "custom": {"_0": xcode_colour(palette["syntax"]["keyword"])}
                },
                "secondary": {
                    "custom": {"_0": xcode_colour(palette["ui"]["background"])}
                },
            },
        },
    }


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)
    print(path.relative_to(ROOT))


def main() -> None:
    palettes = [
        tomllib.loads(p.read_text()) for p in sorted((ROOT / "palettes").glob("*.toml"))
    ]
    write(
        ROOT / "zed" / "geist.json", json.dumps(zed_family(palettes), indent=2) + "\n"
    )
    for palette in palettes:
        name = slug(palette)
        write(ROOT / "ghostty" / name, ghostty(palette))
        write(
            ROOT / "xcode" / f"{name}.json",
            json.dumps(xcode_recipe(palette), indent=2) + "\n",
        )


if __name__ == "__main__":
    main()
