#!/usr/bin/env python3
"""Generate every app's theme files from the palettes in palettes/."""

import json
import math
import plistlib
import textwrap
import tomllib
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
AUTHOR = "brzzdev"
FAMILY = "Geist"
REPOSITORY_URL = "https://github.com/brzzdev/geist-themes"
SCROLLBAR_ALPHA = "50"
SCROLLBAR_HOVER_ALPHA = "80"
TRANSPARENT = "#00000000"
ZED_SCHEMA = "https://zed.dev/schema/themes/v0.2.0.json"
OPAQUE_HEX_LENGTH = len("#rrggbb")
ANSI_NAMES = ["black", "red", "green", "yellow", "blue", "magenta", "cyan", "white"]
# libm differs by an ulp between macOS and Linux, so unrounded output drifts across platforms.
OKLCH_DECIMALS = 6

type Palette = dict[str, Any]

# Dark takes the unsuffixed table, the one herdr keeps when auto_switch is off.
HERDR_TABLES = {"dark": "theme.custom", "light": "theme.custom.light"}

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

NETNEWSWIRE_VARIABLES = {
    "accent": "ui.accent",
    "background": "ui.background",
    "border": "ui.border",
    "border-variant": "ui.border_variant",
    "code-background": "ui.element",
    "foreground": "ui.foreground",
    "link": "syntax.link",
    "muted": "ui.muted",
    "panel": "ui.panel",
    "quiet": "ui.quiet",
    "selection": "ui.selection",
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


VSCODE_UI_THEMES = {"dark": "vs-dark", "light": "vs"}

VSCODE_TOKENS = [
    (
        [
            "entity.name.function.decorator",
            "entity.name.function.preprocessor",
            "entity.other.attribute-name",
            "keyword.control.directive",
            "meta.decorator",
            "meta.preprocessor",
            "punctuation.decorator",
            "storage.type.annotation",
        ],
        "attribute",
        None,
    ),
    (["comment", "punctuation.definition.comment"], "comment", "italic"),
    (
        ["constant.language", "support.constant", "variable.other.enummember"],
        "constant",
        None,
    ),
    (["entity.name.function", "meta.function-call.generic"], "function", None),
    (["support.function"], "function_system", None),
    (
        [
            "keyword",
            "keyword.operator.alignas",
            "keyword.operator.alignof",
            "keyword.operator.cast",
            "keyword.operator.expression",
            "keyword.operator.instanceof",
            "keyword.operator.logical.python",
            "keyword.operator.new",
            "keyword.operator.noexcept",
            "keyword.operator.sizeof",
            "keyword.operator.type.asserts",
            "keyword.operator.typeid",
            "keyword.operator.wordlike",
            "storage",
            "variable.language",
        ],
        "keyword",
        None,
    ),
    (["markup.underline.link"], "link", None),
    (["markup.fenced_code", "markup.inline.raw"], "literal", None),
    (["entity.name.namespace", "entity.name.type.module"], "namespace", None),
    (["constant.character", "constant.numeric"], "number", None),
    (["markup.bold", "markup.heading"], "plain", "bold"),
    (["markup.italic"], "plain", "italic"),
    (["keyword.operator", "meta.brace", "punctuation"], "punctuation", None),
    (["string.regexp"], "regex", None),
    (["punctuation.definition.string", "string"], "string", None),
    (["entity.name.tag"], "tag", None),
    (
        ["entity.name.class", "entity.name.type", "entity.other.inherited-class"],
        "type",
        None,
    ),
    (["entity.name.type.parameter"], "type_parameter", None),
    (["support.class", "support.type"], "type_system", None),
    (
        [
            "meta.definition.variable",
            "support.type.property-name",
            "support.variable",
            "variable",
        ],
        "variable",
        None,
    ),
]

VSCODE_SEMANTIC = {
    "class": "type",
    "class.defaultLibrary": "type_system",
    "decorator": "attribute",
    "enum": "type",
    "enum.defaultLibrary": "type_system",
    "enumMember": "constant",
    "function": "function",
    "function.defaultLibrary": "function_system",
    "interface": "type",
    "interface.defaultLibrary": "type_system",
    "macro": "attribute",
    "method": "function",
    "method.defaultLibrary": "function_system",
    "namespace": "namespace",
    "parameter": "variable",
    "property": "variable",
    "struct": "type",
    "struct.defaultLibrary": "type_system",
    "type": "type",
    "type.defaultLibrary": "type_system",
    "typeParameter": "type_parameter",
    "variable": "variable",
}


JETBRAINS_PLUGIN_DEV_VERSION = "0.0.0-dev"
JETBRAINS_PLUGIN_ID = "dev.brzz.geist-themes"
JETBRAINS_ISLANDS_TOKENS_SINCE_BUILD = "261"
JETBRAINS_PARENT_SCHEMES = {"dark": "Darcula", "light": "Default"}
JETBRAINS_PARENT_THEMES = {"dark": "Islands Dark", "light": "Islands Light"}
JETBRAINS_SCHEME_VERSION = "142"
JETBRAINS_EFFECT_UNDERSCORE = "1"
JETBRAINS_EFFECT_WAVE = "2"
JETBRAINS_FONT_ITALIC = "2"
JETBRAINS_TINT_ALPHA = "33"

# 2026.1 names the container tokens `container-*`; 2026.2 dropped the prefix.
JETBRAINS_THEME_TOKENS = {
    "accent-brand-bg": "ui.accent",
    "accent-brand-border": "ui.accent",
    "container-dialog-bg": "ui.panel",
    "container-dialog-border": "ui.border",
    "container-editor-bg": "ui.background",
    "container-editor-bg-inline": "ui.panel",
    "container-editor-border": "ui.border",
    "container-editor-border-inline": "ui.border",
    "container-main-window-bg": "ui.element",
    "container-popup-bg": "ui.panel",
    "container-popup-border": "ui.border",
    "container-tool-window-bg": "ui.panel",
    "container-tool-window-border": "ui.border",
    "dialog-bg": "ui.panel",
    "dialog-border": "ui.border",
    "editor-bg": "ui.background",
    "editor-bg-inline": "ui.panel",
    "editor-border": "ui.border",
    "editor-border-inline": "ui.border",
    "editor-text": "ui.foreground",
    "main-window-bg": "ui.element",
    "popup-bg": "ui.panel",
    "popup-border": "ui.border",
    "selection-bg-active": "ui.selection",
    "selection-bg-inactive": "ui.element",
    "tab-selected-bg-active": "ui.selection",
    "tab-selected-bg-inactive": "ui.element",
    "tab-selected-border-active": "ui.accent",
    "tab-selected-border-inactive": "ui.border",
    "text-default": "ui.foreground",
    "text-error": "status.error",
    "text-link": "ui.accent",
    "text-muted": "ui.muted",
    "text-secondary": "ui.quiet",
    "text-success": "status.success",
    "text-warning": "status.warning",
    "tool-window-bg": "ui.panel",
    "tool-window-border": "ui.border",
}

JETBRAINS_COLOURS = {
    "ADDED_LINES_COLOR": "status.created",
    "BLOCK_TERMINAL_DEFAULT_BACKGROUND": "ui.background",
    "BLOCK_TERMINAL_DEFAULT_FOREGROUND": "ui.foreground",
    "CARET_COLOR": "ui.cursor",
    "CARET_ROW_COLOR": "ui.hover",
    "CONSOLE_BACKGROUND_KEY": "ui.background",
    "DELETED_LINES_COLOR": "status.deleted",
    "DOCUMENTATION_COLOR": "ui.panel",
    "FILESTATUS_ADDED": "status.created",
    "FILESTATUS_COPIED": "status.created",
    "FILESTATUS_DELETED": "status.deleted",
    "FILESTATUS_IDEA_FILESTATUS_DELETED_FROM_FILE_SYSTEM": "status.deleted",
    "FILESTATUS_IDEA_FILESTATUS_IGNORED": "status.ignored",
    "FILESTATUS_IDEA_FILESTATUS_MERGED_WITH_BOTH_CONFLICTS": "status.conflict",
    "FILESTATUS_IDEA_FILESTATUS_MERGED_WITH_CONFLICTS": "status.conflict",
    "FILESTATUS_IDEA_FILESTATUS_MERGED_WITH_PROPERTY_CONFLICTS": "status.conflict",
    "FILESTATUS_MODIFIED": "status.modified",
    "FILESTATUS_RENAMED": "status.renamed",
    "GUTTER_BACKGROUND": "ui.background",
    "INDENT_GUIDE": "ui.indent",
    "LINE_NUMBERS_COLOR": "ui.quiet",
    "LINE_NUMBER_ON_CARET_ROW_COLOR": "ui.foreground",
    "LOOKUP_COLOR": "ui.panel",
    "METHOD_SEPARATORS_COLOR": "ui.border",
    "MODIFIED_LINES_COLOR": "status.modified",
    "NOTIFICATION_BACKGROUND": "ui.element",
    "RIGHT_MARGIN_COLOR": "ui.border",
    "SELECTED_INDENT_GUIDE": "ui.indent_active",
    "SELECTION_BACKGROUND": "ui.selection",
    "VISUAL_INDENT_GUIDE": "ui.indent",
    "WHITESPACES": "ui.invisible",
}

JETBRAINS_FOREGROUNDS = {
    "CONSOLE_NORMAL_OUTPUT": "ui.foreground",
    "DEFAULT_ATTRIBUTE": "syntax.attribute",
    "DEFAULT_BLOCK_COMMENT": "syntax.comment",
    "DEFAULT_BRACES": "syntax.punctuation",
    "DEFAULT_BRACKETS": "syntax.punctuation",
    "DEFAULT_CLASS_NAME": "syntax.type",
    "DEFAULT_CLASS_REFERENCE": "syntax.type",
    "DEFAULT_COMMA": "syntax.punctuation",
    "DEFAULT_CONSTANT": "syntax.constant",
    "DEFAULT_DOC_COMMENT": "syntax.comment",
    "DEFAULT_DOC_COMMENT_TAG": "syntax.comment_emphasized",
    "DEFAULT_DOC_COMMENT_TAG_VALUE": "syntax.comment_emphasized",
    "DEFAULT_DOC_MARKUP": "syntax.comment",
    "DEFAULT_DOT": "syntax.punctuation",
    "DEFAULT_ENTITY": "syntax.number",
    "DEFAULT_FUNCTION_CALL": "syntax.function",
    "DEFAULT_FUNCTION_DECLARATION": "syntax.function",
    "DEFAULT_GLOBAL_VARIABLE": "syntax.variable",
    "DEFAULT_IDENTIFIER": "syntax.variable",
    "DEFAULT_INSTANCE_FIELD": "syntax.variable",
    "DEFAULT_INSTANCE_METHOD": "syntax.function",
    "DEFAULT_INTERFACE_NAME": "syntax.type",
    "DEFAULT_KEYWORD": "syntax.keyword",
    "DEFAULT_LABEL": "syntax.attribute",
    "DEFAULT_LINE_COMMENT": "syntax.comment",
    "DEFAULT_LOCAL_VARIABLE": "syntax.variable",
    "DEFAULT_METADATA": "syntax.attribute",
    "DEFAULT_NUMBER": "syntax.number",
    "DEFAULT_OPERATION_SIGN": "syntax.punctuation",
    "DEFAULT_PARAMETER": "syntax.variable",
    "DEFAULT_PARENTHS": "syntax.punctuation",
    "DEFAULT_PREDEFINED_SYMBOL": "syntax.function_system",
    "DEFAULT_SEMICOLON": "syntax.punctuation",
    "DEFAULT_STATIC_FIELD": "syntax.variable",
    "DEFAULT_STATIC_METHOD": "syntax.function",
    "DEFAULT_STRING": "syntax.string",
    "DEFAULT_TAG": "syntax.tag",
    "DEFAULT_TEMPLATE_LANGUAGE_COLOR": "syntax.plain",
    "DEFAULT_VALID_STRING_ESCAPE": "syntax.number",
    "HTML_ATTRIBUTE_NAME": "syntax.attribute",
    "HTML_ATTRIBUTE_VALUE": "syntax.string",
    "HTML_CUSTOM_TAG_NAME": "syntax.tag",
    "HTML_ENTITY_REFERENCE": "syntax.number",
    "HTML_TAG": "syntax.punctuation",
    "HTML_TAG_NAME": "syntax.tag",
    "JS.GLOBAL_FUNCTION": "syntax.function",
    "JS.GLOBAL_VARIABLE": "syntax.variable",
    "JS.INSTANCE_MEMBER_FUNCTION": "syntax.function",
    "JS.LOCAL_VARIABLE": "syntax.variable",
    "JS.PARAMETER": "syntax.variable",
    "JS.REGEXP": "syntax.regex",
    "NOT_USED_ELEMENT_ATTRIBUTES": "status.unreachable",
    "ReSharper.ASP_NET_RAZOR_TAG_HELPER_ATTRIBUTE": "syntax.attribute",
    "ReSharper.ASP_NET_RAZOR_TAG_HELPER_ELEMENT": "syntax.tag",
    "ReSharper.FORMAT_STRING_ITEM": "syntax.number",
    "ReSharper.FORMAT_STRING_ITEM_2": "syntax.number",
    "ReSharper.STRING_ESCAPE_CHARACTER_2": "syntax.number",
    "TS.TYPE_PARAMETER": "syntax.type_parameter",
    "TYPE_PARAMETER_NAME_ATTRIBUTES": "syntax.type_parameter",
    "WRONG_REFERENCES_ATTRIBUTES": "status.error",
    "XML_ATTRIBUTE_NAME": "syntax.attribute",
    "XML_CUSTOM_TAG_NAME": "syntax.tag",
    "XML_ENTITY_REFERENCE": "syntax.number",
    "XML_PROLOGUE": "syntax.attribute",
    "XML_TAG": "syntax.punctuation",
    "XML_TAG_NAME": "syntax.tag",
}

JETBRAINS_ITALIC = {
    "DEFAULT_BLOCK_COMMENT",
    "DEFAULT_DOC_COMMENT",
    "DEFAULT_DOC_COMMENT_TAG",
    "DEFAULT_DOC_COMMENT_TAG_VALUE",
    "DEFAULT_DOC_MARKUP",
    "DEFAULT_LINE_COMMENT",
    "DEFAULT_STATIC_FIELD",
    "DEFAULT_STATIC_METHOD",
    "JS.GLOBAL_VARIABLE",
}

JETBRAINS_DIAGNOSTICS = {
    "ERRORS_ATTRIBUTES": "status.error",
    "INFO_ATTRIBUTES": "status.hint",
    "WARNING_ATTRIBUTES": "status.warning",
}

JETBRAINS_CONSOLE = {
    "normal": [
        "CONSOLE_BLACK_OUTPUT",
        "CONSOLE_RED_OUTPUT",
        "CONSOLE_GREEN_OUTPUT",
        "CONSOLE_YELLOW_OUTPUT",
        "CONSOLE_BLUE_OUTPUT",
        "CONSOLE_MAGENTA_OUTPUT",
        "CONSOLE_CYAN_OUTPUT",
        "CONSOLE_GRAY_OUTPUT",
    ],
    "bright": [
        "CONSOLE_DARKGRAY_OUTPUT",
        "CONSOLE_RED_BRIGHT_OUTPUT",
        "CONSOLE_GREEN_BRIGHT_OUTPUT",
        "CONSOLE_YELLOW_BRIGHT_OUTPUT",
        "CONSOLE_BLUE_BRIGHT_OUTPUT",
        "CONSOLE_MAGENTA_BRIGHT_OUTPUT",
        "CONSOLE_CYAN_BRIGHT_OUTPUT",
        "CONSOLE_WHITE_OUTPUT",
    ],
}


def slug(palette: Palette) -> str:
    return palette["name"].lower().replace(" ", "-")


def palette_colour(palette: Palette, path: str) -> str:
    group, key = path.split(".")
    return palette[group][key]


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
        "editor.document_highlight.bracket_background": ui["highlight"],
        "editor.document_highlight.read_background": ui["highlight"],
        "editor.document_highlight.write_background": ui["highlight"],
        "editor.foreground": ui["foreground"],
        "editor.gutter.background": ui["background"],
        "editor.highlighted_line.background": ui["hover"],
        "editor.indent_guide": ui["indent"],
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
        "panel.indent_guide": ui["indent"],
        "panel.indent_guide_active": ui["indent_active"],
        "players": [
            {
                "background": ui["cursor"],
                "cursor": ui["cursor"],
                "selection": ui["selection_overlay"],
            },
        ],
        "scrollbar.thumb.background": ui["indent_active"] + SCROLLBAR_ALPHA,
        "scrollbar.thumb.hover_background": ui["muted"] + SCROLLBAR_HOVER_ALPHA,
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
        "name": FAMILY,
        "author": AUTHOR,
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


def herdr_colours(palette: Palette) -> dict[str, str]:
    ui, status = palette["ui"], palette["status"]
    normal = dict(zip(ANSI_NAMES, palette["ansi"]["normal"]))
    bright = dict(zip(ANSI_NAMES, palette["ansi"]["bright"]))
    return {
        "accent": ui["accent"],
        "active_row_bg": ui["element"],
        "blue": status["info"],
        "green": status["success"],
        "mauve": normal["magenta"],
        "overlay0": ui["quiet"],
        "overlay1": ui["muted"],
        "panel_bg": ui["panel"],
        "peach": bright["yellow"],
        "red": status["error"],
        "selection_bg": ui["selection"],
        "sidebar_bg": ui["background"],
        "subtext0": ui["muted"],
        "surface0": ui["element"],
        "surface1": ui["selection"],
        "surface_dim": ui["hover"],
        "teal": normal["cyan"],
        "text": ui["foreground"],
        "yellow": status["warning"],
    }


def herdr_table(header: str, colours: dict[str, str]) -> str:
    rows = [f'{token} = "{colour}"' for token, colour in colours.items()]
    return "\n".join([f"[{header}]", *rows]) + "\n"


def herdr(palettes: list[Palette]) -> str:
    tables = [
        herdr_table(HERDR_TABLES[p["appearance"]], herdr_colours(p)) for p in palettes
    ]
    return "[theme]\nauto_switch = true\n\n" + "\n".join(tables)


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
    overrides: list[Any] = []
    for token, path in XCODE_OVERRIDES.items():
        overrides += [
            token,
            {"color": {"_0": xcode_colour(palette_colour(palette, path))}},
        ]
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


def netnewswire_variables(palette: Palette) -> str:
    declarations = {"color-scheme": palette["appearance"]} | {
        f"--{name}": palette_colour(palette, path)
        for name, path in NETNEWSWIRE_VARIABLES.items()
    }
    body = "".join(f"\t{key}: {value};\n" for key, value in declarations.items())
    return f":root {{\n{body}}}\n"


def netnewswire_stylesheet(palettes: list[Palette]) -> str:
    default, *others = sorted(palettes, key=lambda p: p["appearance"] != "dark")
    blocks = [netnewswire_variables(default)]
    blocks += [
        f"@media (prefers-color-scheme: {p['appearance']}) {{\n"
        + textwrap.indent(netnewswire_variables(p), "\t")
        + "}\n"
        for p in others
    ]
    rules = (ROOT / "templates" / "netnewswire.css").read_text()
    return "\n".join([*blocks, rules])


def netnewswire_info() -> str:
    info = {
        "CreatorHomePage": REPOSITORY_URL,
        "CreatorName": AUTHOR,
        "Name": FAMILY,
        "ThemeIdentifier": "dev.brzz.geist-themes.netnewswire",
        "Version": 1,
    }
    return plistlib.dumps(info).decode()


def vscode_colours(palette: Palette) -> dict[str, str]:
    ui, status, ansi = palette["ui"], palette["status"], palette["ansi"]
    colours = {
        "activityBar.background": ui["panel"],
        "activityBar.border": ui["border"],
        "activityBar.foreground": ui["foreground"],
        "activityBar.inactiveForeground": ui["quiet"],
        "activityBarBadge.background": ui["accent"],
        "activityBarBadge.foreground": ui["background"],
        "badge.background": ui["element"],
        "badge.foreground": ui["foreground"],
        "button.background": ui["accent"],
        "button.foreground": ui["background"],
        "button.hoverBackground": ui["accent_strong"],
        "descriptionForeground": ui["muted"],
        "disabledForeground": ui["quiet"],
        "dropdown.background": ui["element"],
        "dropdown.border": ui["border"],
        "editor.background": ui["background"],
        "editor.findMatchBackground": ui["find"],
        "editor.findMatchHighlightBackground": ui["find"],
        "editor.foreground": ui["foreground"],
        "editor.lineHighlightBackground": ui["hover"],
        "editor.selectionBackground": ui["selection"],
        "editorBracketMatch.background": ui["highlight"],
        "editorBracketMatch.border": ui["indent_active"],
        "editorCursor.foreground": ui["cursor"],
        "editorError.foreground": status["error"],
        "editorGroup.border": ui["border"],
        "editorGroupHeader.tabsBackground": ui["panel"],
        "editorGutter.addedBackground": status["created"],
        "editorGutter.background": ui["background"],
        "editorGutter.deletedBackground": status["deleted"],
        "editorGutter.modifiedBackground": status["modified"],
        "editorHint.foreground": status["hint"],
        "editorIndentGuide.activeBackground1": ui["indent_active"],
        "editorIndentGuide.background1": ui["indent"],
        "editorInfo.foreground": status["info"],
        "editorLineNumber.activeForeground": ui["foreground"],
        "editorLineNumber.foreground": ui["quiet"],
        "editorRuler.foreground": ui["border"],
        "editorWarning.foreground": status["warning"],
        "editorWhitespace.foreground": ui["invisible"],
        "editorWidget.background": ui["panel"],
        "editorWidget.border": ui["border"],
        "focusBorder": ui["accent"],
        "foreground": ui["foreground"],
        "gitDecoration.addedResourceForeground": status["created"],
        "gitDecoration.conflictingResourceForeground": status["conflict"],
        "gitDecoration.deletedResourceForeground": status["deleted"],
        "gitDecoration.ignoredResourceForeground": status["ignored"],
        "gitDecoration.modifiedResourceForeground": status["modified"],
        "gitDecoration.renamedResourceForeground": status["renamed"],
        "gitDecoration.untrackedResourceForeground": status["created"],
        "input.background": ui["element"],
        "input.border": ui["border"],
        "input.placeholderForeground": ui["quiet"],
        "list.activeSelectionBackground": ui["selection"],
        "list.activeSelectionForeground": ui["foreground"],
        "list.errorForeground": status["error"],
        "list.focusOutline": ui["accent"],
        "list.highlightForeground": ui["accent_strong"],
        "list.hoverBackground": ui["hover"],
        "list.inactiveSelectionBackground": ui["element"],
        "list.warningForeground": status["warning"],
        "menu.background": ui["panel"],
        "menu.border": ui["border"],
        "panel.background": ui["panel"],
        "panel.border": ui["border"],
        "panelTitle.activeBorder": ui["accent"],
        "panelTitle.activeForeground": ui["foreground"],
        "panelTitle.inactiveForeground": ui["muted"],
        "problemsErrorIcon.foreground": status["error"],
        "problemsInfoIcon.foreground": status["info"],
        "problemsWarningIcon.foreground": status["warning"],
        "quickInput.background": ui["panel"],
        "scrollbarSlider.activeBackground": ui["muted"] + SCROLLBAR_HOVER_ALPHA,
        "scrollbarSlider.background": ui["indent_active"] + SCROLLBAR_ALPHA,
        "scrollbarSlider.hoverBackground": ui["muted"] + SCROLLBAR_HOVER_ALPHA,
        "selection.background": ui["selection"],
        "sideBar.background": ui["panel"],
        "sideBar.border": ui["border"],
        "sideBar.foreground": ui["foreground"],
        "sideBarSectionHeader.background": ui["panel"],
        "statusBar.background": ui["panel"],
        "statusBar.border": ui["border"],
        "statusBar.debuggingBackground": status["warning"],
        "statusBar.debuggingForeground": ui["background"],
        "statusBar.foreground": ui["muted"],
        "statusBar.noFolderBackground": ui["panel"],
        "tab.activeBackground": ui["background"],
        "tab.activeBorderTop": ui["accent"],
        "tab.activeForeground": ui["foreground"],
        "tab.border": ui["border"],
        "tab.inactiveBackground": ui["panel"],
        "tab.inactiveForeground": ui["muted"],
        "terminal.background": ui["background"],
        "terminal.foreground": ui["foreground"],
        "terminal.selectionBackground": ui["selection"],
        "terminalCursor.foreground": ui["cursor"],
        "textLink.activeForeground": ui["accent"],
        "textLink.foreground": ui["accent_strong"],
        "titleBar.activeBackground": ui["panel"],
        "titleBar.activeForeground": ui["foreground"],
        "titleBar.border": ui["border"],
        "titleBar.inactiveBackground": ui["panel"],
    }
    for index, accent in enumerate(ui["accents"], start=1):
        colours[f"editorBracketHighlight.foreground{index}"] = accent
    for index, name in enumerate(ANSI_NAMES):
        title = name.capitalize()
        colours[f"terminal.ansi{title}"] = ansi["normal"][index]
        colours[f"terminal.ansiBright{title}"] = ansi["bright"][index]
    return dict(sorted(colours.items()))


def vscode_token_settings(colour: str, style: str | None) -> dict[str, str]:
    if style is None:
        return {"foreground": colour}
    return {"foreground": colour, "fontStyle": style}


def vscode_theme(palette: Palette) -> dict[str, Any]:
    syntax = palette["syntax"]
    return {
        "name": palette["name"],
        "type": palette["appearance"],
        "semanticHighlighting": True,
        "colors": vscode_colours(palette),
        "tokenColors": [
            {"scope": scopes, "settings": vscode_token_settings(syntax[role], style)}
            for scopes, role, style in VSCODE_TOKENS
        ],
        "semanticTokenColors": {
            selector: syntax[role] for selector, role in VSCODE_SEMANTIC.items()
        },
    }


def vscode_manifest(palettes: list[Palette]) -> dict[str, Any]:
    return {
        "name": "geist-themes",
        "displayName": "Geist Themes",
        "description": "Colour themes from Vercel's Geist terminal themes.",
        "version": "1.0.0",
        "publisher": AUTHOR,
        "license": "MIT",
        "repository": REPOSITORY_URL,
        "engines": {"vscode": "^1.81.0"},
        "categories": ["Themes"],
        "files": ["LICENSE", "themes"],
        "contributes": {
            "themes": [
                {
                    "label": p["name"],
                    "uiTheme": VSCODE_UI_THEMES[p["appearance"]],
                    "path": f"./themes/{slug(p)}.json",
                }
                for p in palettes
            ],
        },
    }


def opaque(colour: str, ground: str) -> str:
    if len(colour) == OPAQUE_HEX_LENGTH:
        return colour
    alpha = int(colour[OPAQUE_HEX_LENGTH:], 16) / 255
    channels = (
        round(
            int(colour[i : i + 2], 16) * alpha
            + int(ground[i : i + 2], 16) * (1 - alpha)
        )
        for i in (1, 3, 5)
    )
    return "#" + "".join(f"{c:02x}" for c in channels)


def xml_text(root: ET.Element) -> str:
    ET.indent(root)
    return ET.tostring(root, encoding="unicode") + "\n"


def jetbrains_theme(palette: Palette) -> dict[str, Any]:
    return {
        "name": palette["name"],
        "dark": palette["appearance"] == "dark",
        "author": AUTHOR,
        "parentTheme": JETBRAINS_PARENT_THEMES[palette["appearance"]],
        "editorScheme": f"/{slug(palette)}.xml",
        "colors": {
            token: palette_colour(palette, path)
            for token, path in JETBRAINS_THEME_TOKENS.items()
        },
    }


def jetbrains_scheme(palette: Palette) -> str:
    ui = palette["ui"]

    def colour(value: str) -> str:
        return opaque(value, ui["background"])[1:]

    def path_colour(path: str) -> str:
        return colour(palette_colour(palette, path))

    link = path_colour("syntax.link")
    keyword = palette["syntax"]["keyword"]
    find = {
        "BACKGROUND": colour(ui["find"]),
        "ERROR_STRIPE_COLOR": colour(ui["find"][:OPAQUE_HEX_LENGTH]),
    }
    attributes = {
        "HYPERLINK_ATTRIBUTES": {
            "EFFECT_COLOR": link,
            "EFFECT_TYPE": JETBRAINS_EFFECT_UNDERSCORE,
            "FOREGROUND": link,
        },
        "IDENTIFIER_UNDER_CARET_ATTRIBUTES": {
            "BACKGROUND": colour(ui["element"]),
            "ERROR_STRIPE_COLOR": colour(ui["accent"]),
        },
        "SEARCH_RESULT_ATTRIBUTES": find,
        "TEXT": {
            "BACKGROUND": colour(ui["background"]),
            "FOREGROUND": colour(ui["foreground"]),
        },
        "TEXT_SEARCH_RESULT_ATTRIBUTES": find,
        # Empty drops the JavaScript plugin's green type-guard background.
        "TS.TYPE_GUARD": {},
        "WRITE_IDENTIFIER_UNDER_CARET_ATTRIBUTES": {
            "BACKGROUND": colour(keyword + JETBRAINS_TINT_ALPHA),
            "ERROR_STRIPE_COLOR": colour(keyword),
        },
    }
    for key, path in JETBRAINS_FOREGROUNDS.items():
        attributes[key] = {"FOREGROUND": path_colour(path)}
        if key in JETBRAINS_ITALIC:
            attributes[key]["FONT_TYPE"] = JETBRAINS_FONT_ITALIC
    for key, path in JETBRAINS_DIAGNOSTICS.items():
        severity = path_colour(path)
        attributes[key] = {
            "EFFECT_COLOR": severity,
            "EFFECT_TYPE": JETBRAINS_EFFECT_WAVE,
            "ERROR_STRIPE_COLOR": severity,
        }
    for shade, keys in JETBRAINS_CONSOLE.items():
        for key, value in zip(keys, palette["ansi"][shade], strict=True):
            attributes[key] = {"FOREGROUND": colour(value)}
    for shade, suffix in (("normal", ""), ("bright", "_BRIGHT")):
        for name, value in zip(ANSI_NAMES, palette["ansi"][shade], strict=True):
            attributes[f"BLOCK_TERMINAL_{name.upper()}{suffix}"] = {
                "FOREGROUND": colour(value)
            }

    scheme = ET.Element(
        "scheme",
        name=palette["name"],
        version=JETBRAINS_SCHEME_VERSION,
        parent_scheme=JETBRAINS_PARENT_SCHEMES[palette["appearance"]],
    )
    colours = ET.SubElement(scheme, "colors")
    for key, path in JETBRAINS_COLOURS.items():
        ET.SubElement(colours, "option", name=key, value=path_colour(path))
    # Empty keeps syntax colours in a selection, where the Default parent paints it white.
    ET.SubElement(colours, "option", name="SELECTION_FOREGROUND", value="")
    options = ET.SubElement(scheme, "attributes")
    for key, values in sorted(attributes.items()):
        value = ET.SubElement(ET.SubElement(options, "option", name=key), "value")
        for name, setting in sorted(values.items()):
            ET.SubElement(value, "option", name=name, value=setting)
    return xml_text(scheme)


def jetbrains_plugin(palettes: list[Palette]) -> str:
    plugin = ET.Element("idea-plugin")
    ET.SubElement(plugin, "id").text = JETBRAINS_PLUGIN_ID
    ET.SubElement(plugin, "name").text = "Geist Themes"
    ET.SubElement(plugin, "version").text = JETBRAINS_PLUGIN_DEV_VERSION
    ET.SubElement(plugin, "vendor", url=REPOSITORY_URL).text = AUTHOR
    names = " and ".join(p["name"] for p in palettes)
    ET.SubElement(plugin, "description").text = (
        f"{names}, built from the colours of Vercel's Geist terminal themes. "
        "Unofficial: not made or endorsed by Vercel."
    )
    ET.SubElement(
        plugin, "idea-version", {"since-build": JETBRAINS_ISLANDS_TOKENS_SINCE_BUILD}
    )
    ET.SubElement(plugin, "depends").text = "com.intellij.modules.platform"
    extensions = ET.SubElement(plugin, "extensions", defaultExtensionNs="com.intellij")
    for palette in palettes:
        name = slug(palette)
        ET.SubElement(extensions, "themeProvider", id=name, path=f"/{name}.theme.json")
    return xml_text(plugin)


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)
    print(path.relative_to(ROOT))


def write_json(path: Path, value: dict[str, Any]) -> None:
    write(path, json.dumps(value, indent=2) + "\n")


def main() -> None:
    palettes = [
        tomllib.loads(p.read_text()) for p in sorted((ROOT / "palettes").glob("*.toml"))
    ]
    write(ROOT / "herdr" / "geist.toml", herdr(palettes))
    write(ROOT / "jetbrains" / "META-INF" / "plugin.xml", jetbrains_plugin(palettes))
    bundle = ROOT / "netnewswire" / f"{FAMILY}.nnwtheme"
    write(bundle / "Info.plist", netnewswire_info())
    write(bundle / "stylesheet.css", netnewswire_stylesheet(palettes))
    write_json(ROOT / "vscode" / "package.json", vscode_manifest(palettes))
    write(ROOT / "vscode" / "LICENSE", (ROOT / "LICENSE").read_text())
    write_json(ROOT / "zed" / "geist.json", zed_family(palettes))
    for palette in palettes:
        name = slug(palette)
        write(ROOT / "ghostty" / name, ghostty(palette))
        write_json(ROOT / "jetbrains" / f"{name}.theme.json", jetbrains_theme(palette))
        write(ROOT / "jetbrains" / f"{name}.xml", jetbrains_scheme(palette))
        write_json(ROOT / "vscode" / "themes" / f"{name}.json", vscode_theme(palette))
        write_json(ROOT / "xcode" / f"{name}.json", xcode_recipe(palette))


if __name__ == "__main__":
    main()
