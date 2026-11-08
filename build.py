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
# Fills behind syntax text: see docs/adr/0003-tinted-fills-behind-syntax.md.
TINT_ALPHAS = {"dark": "33", "light": "1a"}
TRANSPARENT = "#00000000"
ZED_SCHEMA = "https://zed.dev/schema/themes/v0.2.0.json"
# Zed keeps its own players past the ones a theme gives; the last is the agent.
ZED_PLAYERS = 8
OPAQUE_HEX_LENGTH = len("#rrggbb")
ANSI_NAMES = ["black", "red", "green", "yellow", "blue", "magenta", "cyan", "white"]
# libm differs by an ulp between macOS and Linux, so unrounded output drifts across platforms.
OKLCH_DECIMALS = 6
CARD_CELL_WIDTH = 210
CARD_COLUMNS = 4
CARD_FONT = "ui-monospace, SFMono-Regular, Menlo, monospace"
CARD_HEADING_BASELINE = 20
CARD_HEX_BASELINE = 29
CARD_LABEL_GAP = 10
CARD_PADDING = 24
CARD_ROLE_BASELINE = 13
CARD_ROW_HEIGHT = 44
CARD_SWATCH = 32

# Every syntax role reaches 4.5:1 on these, as do hint and inactive text on their grounds.
MINIMUM_CONTRAST = 4.5
SYNTAX_GROUNDS = [
    "background",
    "find",
    "find_active",
    "highlight",
    "hover",
    "panel",
    "selection",
]
TINTED_STATUSES = [
    "conflict",
    "created",
    "deleted",
    "error",
    "modified",
    "success",
    "warning",
]
HINT_PAIRS = [
    ("status.hint", "ui.background"),
    ("status.hint", "ui.element"),
    ("status.hint", "ui.hover"),
    ("status.predictive", "ui.background"),
    ("status.predictive", "ui.hover"),
    ("ui.quiet", "ui.background"),
    ("ui.quiet", "ui.element"),
    ("ui.quiet", "ui.panel"),
]

type Palette = dict[str, Any]

# Dark takes the unsuffixed table, the one herdr keeps when auto_switch is off.
HERDR_TABLES = {"dark": "theme.custom", "light": "theme.custom.light"}

ZED_SYNTAX = {
    "attribute": ("attribute", None),
    "boolean": ("constant", None),
    "comment": ("comment", "italic"),
    "comment.doc": ("comment", "italic"),
    "concept": ("type", None),
    "constant": ("constant", None),
    "constructor": ("type", None),
    "diff.delta": ("function", None),
    "diff.minus": ("tag", None),
    "diff.plus": ("string", None),
    "emphasis": ("plain", "italic"),
    "emphasis.strong": ("plain", "bold"),
    "enum": ("type", None),
    "function": ("function", None),
    "function.builtin": ("function_system", None),
    "function.macro": ("attribute", None),
    "keyword": ("keyword", None),
    "label": ("attribute", None),
    "lifetime": ("type_parameter", None),
    "link_text": ("link", None),
    "link_uri": ("link", None),
    "markup.heading": ("plain", "bold"),
    "module": ("namespace", None),
    "namespace": ("namespace", None),
    "number": ("number", None),
    "operator": ("punctuation", None),
    "preproc": ("attribute", None),
    "property": ("variable", None),
    "punctuation": ("punctuation", None),
    "selector": ("attribute", None),
    "string": ("string", None),
    "string.escape": ("number", None),
    "string.regex": ("regex", None),
    "string.special": ("string", None),
    "string.special.symbol": ("constant", None),
    "tag": ("tag", None),
    "text.literal": ("literal", None),
    "title": ("plain", "bold"),
    "type": ("type", None),
    "type.builtin": ("type_system", None),
    "type.parameter": ("type_parameter", None),
    "variable": ("variable", None),
    "variable.builtin": ("keyword", None),
    "variable.parameter": ("variable", None),
    "variable.special": ("keyword", None),
    "variant": ("constant", None),
}

NETNEWSWIRE_VARIABLES = {
    "accent": "ui.accent",
    "background": "ui.background",
    "border": "ui.border",
    "border-variant": "ui.border_variant",
    "code-background": "ui.element",
    "find": "ui.find",
    "foreground": "ui.foreground",
    "link": "syntax.link",
    "muted": "ui.muted",
    "panel": "ui.panel",
    "quiet": "ui.quiet",
    "selection": "ui.selection",
}

XCODE_OVERRIDES = {
    "codeFoldingRibbon": "ui.hover",
    "comment": "syntax.comment",
    "commentEmphasized": "syntax.comment_emphasized",
    "consoleBackground": "ui.background",
    "currentLineHighlight": "ui.hover",
    "debugger": "ui.accent",
    "diffAddition": "status.created",
    "diffDeletion": "status.deleted",
    "insertionPointColor": "ui.cursor",
    "invisibles": "ui.invisible",
    "keyword": "syntax.keyword",
    "keyword.attribute": "syntax.attribute",
    "link": "syntax.link",
    "markdown": "syntax.literal",
    "markdownEmphasized": "syntax.plain",
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
    "scopeGuides": "ui.indent",
    "selectedTextBackgroundColor": "ui.selection",
    "string": "syntax.string",
    "string.regex": "syntax.regex",
    "typeDeclaration": "syntax.type",
}


# The selection colour at this alpha keeps syntax at or above its contrast on the selection.
VSCODE_RANGE_ALPHA = "60"
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
VCS_ANNOTATION_SHADES = 5
JETBRAINS_EFFECT_BOXED = "0"
JETBRAINS_EFFECT_UNDERSCORE = "1"
JETBRAINS_EFFECT_WAVE = "2"
JETBRAINS_EFFECT_STRIKEOUT = "3"
JETBRAINS_EFFECT_BOLD_DOTTED = "5"
JETBRAINS_FONT_BOLD = "1"
JETBRAINS_FONT_ITALIC = "2"

# 2026.1 names the container tokens `container-*`; 2026.2 dropped the prefix.
JETBRAINS_THEME_TOKENS = {
    "accent-brand-bg": "ui.accent",
    "accent-brand-border": "ui.accent",
    "accent-brand-border-secondary": "ui.accent",
    "accent-error-bg": "status.error",
    "accent-error-border": "status.error",
    "accent-error-border-secondary": "status.error",
    "accent-neutral-bg": "ui.element",
    "accent-success-bg": "status.success",
    "accent-success-border": "status.success",
    "accent-success-border-secondary": "status.success",
    "accent-warning-bg": "status.warning",
    "accent-warning-border": "status.warning",
    "accent-warning-border-secondary": "status.warning",
    "container-dialog-bg": "ui.panel",
    "container-dialog-bg-inline": "ui.hover",
    "container-dialog-border": "ui.border",
    "container-editor-bg": "ui.background",
    "container-editor-bg-inline": "ui.panel",
    "container-editor-border": "ui.border",
    "container-editor-border-alt": "ui.border",
    "container-editor-border-inline": "ui.border",
    "container-main-window-bg": "ui.element",
    "container-main-window-bg-alt": "ui.element",
    "container-main-window-border": "ui.border",
    "container-popup-bg": "ui.panel",
    "container-popup-bg-inline": "ui.panel",
    "container-popup-border": "ui.border",
    "container-popup-border-inline": "ui.border",
    "container-popup-border-windows": "ui.border",
    "container-tool-window-bg": "ui.panel",
    "container-tool-window-bg-alt": "ui.panel",
    "container-tool-window-bg-inline": "ui.hover",
    "container-tool-window-border": "ui.border",
    "container-tool-window-border-inline": "ui.border",
    "control-bg-raised": "ui.element",
    "control-bg-small": "ui.border",
    "control-bg-small-disabled": "ui.border_variant",
    "control-border": "ui.border",
    "control-border-disabled": "ui.border_variant",
    "control-border-over-accent": "ui.border",
    "control-border-raised": "ui.invisible",
    "control-border-small": "ui.invisible",
    "control-error-border-secondary": "status.error",
    "control-warning-border-secondary": "status.warning",
    "core-bg-transparent-hovered": "ui.hover",
    "core-bg-transparent-pressed": "ui.element",
    "core-border-transparent": "ui.border",
    "dialog-bg": "ui.panel",
    "dialog-bg-inline": "ui.hover",
    "dialog-border": "ui.border",
    "editor-bg": "ui.background",
    "editor-bg-inline": "ui.panel",
    "editor-border": "ui.border",
    "editor-border-alt": "ui.border",
    "editor-border-inline": "ui.border",
    "editor-floating-toolbar-bg": "ui.element",
    "editor-text": "ui.foreground",
    "feedback-bg": "ui.element",
    "feedback-bg-inline": "ui.panel",
    "feedback-border": "ui.border",
    "got-it-bg": "ui.element",
    "got-it-border": "ui.accent",
    "got-it-code-border": "ui.border",
    "got-it-contrast-button-bg": "ui.selection",
    "got-it-shortcut-bg": "ui.selection",
    "got-it-text-link": "ui.accent_strong",
    "got-it-text-step": "ui.quiet",
    "icon-default-stroke": "ui.foreground",
    "icon-green-stroke": "status.success",
    "icon-over-accent": "ui.background",
    "inlay-bg": "ui.element",
    "inlay-border": "ui.border",
    "layer-0-bg": "ui.panel",
    "layer-0-bg-inline": "ui.hover",
    "layer-0-border": "ui.border",
    "layer-0-border-inline": "ui.border",
    "layer-1-bg": "ui.element",
    "layer-1-bg-inline": "ui.element",
    "layer-1-border": "ui.border",
    "layer-1-border-inline": "ui.border",
    "layer-2-bg": "ui.element",
    "layer-2-bg-inline": "ui.selection",
    "layer-2-border": "ui.border",
    "layer-2-border-inline": "ui.border",
    "main-window-bg": "ui.element",
    "main-window-bg-alt": "ui.element",
    "main-window-border": "ui.border",
    "popup-bg": "ui.panel",
    "popup-bg-inline": "ui.panel",
    "popup-border": "ui.border",
    "popup-border-inline": "ui.border",
    "popup-completion-match-text": "ui.accent_strong",
    "presentation-assistant-bg": "ui.element",
    "search-match-bg": "ui.find_active_border",
    "selection-bg-active": "ui.selection",
    "selection-bg-active-muted": "ui.element",
    "selection-bg-hovered": "ui.hover",
    "selection-bg-inactive": "ui.element",
    "tab-selected-bg-active": "ui.selection",
    "tab-selected-bg-inactive": "ui.element",
    "tab-selected-border-active": "ui.accent",
    "tab-selected-border-inactive": "ui.border",
    "text-default": "ui.foreground",
    "text-disabled": "ui.quiet",
    "text-error": "status.error",
    "text-link": "ui.accent",
    "text-muted": "ui.muted",
    "text-over-accent": "ui.background",
    "text-over-accent-inverted": "ui.foreground",
    "text-secondary": "ui.quiet",
    "text-success": "status.success",
    "text-warning": "status.warning",
    "toggle-border": "ui.invisible",
    "toggle-button-bg": "ui.muted",
    "toggle-off-bg": "ui.element",
    "tool-window-bg": "ui.panel",
    "tool-window-bg-alt": "ui.panel",
    "tool-window-bg-inline": "ui.hover",
    "tool-window-border": "ui.border",
    "tool-window-border-inline": "ui.border",
    "toolbar-run-bg-hovered": "status.success",
    "toolbar-stop-bg-hovered": "status.error",
    "tree-indent-guide-border": "ui.indent",
}

# Islands sets these to fixed colours rather than tokens.
JETBRAINS_UI = {
    "Badge.blueBackground": "ui.accent",
    "Badge.blueForeground": "ui.background",
    "Badge.blueSecondaryForeground": "ui.accent_strong",
    "Badge.disabledBackground": "ui.element",
    "Badge.disabledForeground": "ui.quiet",
    "Badge.graySecondaryBackground": "ui.element",
    "Badge.graySecondaryForeground": "ui.muted",
    "Badge.greenBackground": "status.success",
    "Badge.greenForeground": "ui.background",
    "Badge.greenSecondaryForeground": "status.success",
    "Badge.purpleSecondaryForeground": "syntax.keyword",
    "Bookmark.MnemonicCurrent.foreground": "ui.background",
    "Debugger.Variables.changedValueForeground": "ui.accent",
    "Debugger.Variables.collectingDataForeground": "ui.quiet",
    "Debugger.Variables.errorMessageForeground": "status.error",
    "Debugger.Variables.evaluatingExpressionForeground": "ui.quiet",
    "Debugger.Variables.exceptionForeground": "status.error",
    "Debugger.Variables.modifyingValueForeground": "ui.accent",
    "Debugger.Variables.typeForeground": "ui.quiet",
    "Debugger.Variables.valueForeground": "syntax.constant",
    "Editor.ToolTip.foreground": "ui.foreground",
    "Editor.ToolTip.selectionBackground": "ui.selection",
    "GotItTooltip.animationBackground": "ui.element",
    "List.Tag.background": "ui.element",
    "List.Tag.foreground": "ui.muted",
    "MainWindow.FullScreeControl.Background": "ui.element",
    "MainWindow.Tab.background": "ui.panel",
    "MainWindow.Tab.borderColor": "ui.border",
    "MainWindow.Tab.hoverForeground": "ui.foreground",
    "MainWindow.Tab.selectedForeground": "ui.foreground",
    "MainWindow.Tab.selectedInactiveBackground": "ui.element",
    "MemoryIndicator.allocatedBackground": "ui.element",
    "Menu.borderColor.os.windows": "ui.border",
    "ParameterInfo.background": "ui.panel",
    "ParameterInfo.borderColor": "ui.border",
    "ParameterInfo.currentOverloadBackground": "ui.selection",
    "ParameterInfo.disabledForeground": "ui.quiet",
    "ParameterInfo.foreground": "ui.foreground",
    "ParameterInfo.infoForeground": "ui.muted",
    "ParameterInfo.lineSeparatorColor": "ui.border",
    "Plugins.background": "ui.panel",
    "Plugins.tagBackground": "ui.element",
    "Popup.borderColor": "ui.border",
    "PresentationAssistant.Bright.keymapLabel": "ui.quiet",
    "PresentationAssistant.Pale.Popup.border": "ui.border",
    "PresentationAssistant.Pale.PopupBackground": "ui.element",
    "PresentationAssistant.Pale.keymapLabel": "ui.quiet",
    "ProgressBar.failedColor": "status.error",
    "ProgressBar.failedEndColor": "status.error",
    "ProgressBar.failedendcolor": "status.error",
    "ProgressBar.indeterminateEndColor": "ui.accent",
    "ProgressBar.indeterminateStartColor": "ui.accent_strong",
    "ProgressBar.passedColor": "status.success",
    "ProgressBar.passedEndColor": "status.success",
    "ProgressBar.passedendcolor": "status.success",
    "ProgressBar.progressCounterBackground": "ui.accent",
    "ProgressBar.progressCounterForeground": "ui.background",
    "Review.Branch.Background": "ui.element",
    "Review.Branch.Background.Hover": "ui.selection",
    "Review.ChatItem.Hover": "ui.hover",
    "Review.State.Background": "ui.element",
    "Review.State.Foreground": "ui.muted",
    "RunWidget.foreground": "ui.foreground",
    "RunWidget.hoverBackground": "ui.hover",
    "RunWidget.pressedBackground": "ui.selection",
    "Slider.buttonBorderColor": "ui.border",
    "Slider.buttonColor": "ui.muted",
    "Slider.tickColor": "ui.quiet",
    "Slider.trackColor": "ui.border",
    "StatusBar.Breadcrumbs.floatingBackground": "ui.panel",
    "Table.stripeColor": "ui.hover",
    "Tag.background": "ui.element",
    "ToolWindow.Button.DragAndDrop.stripeBackground": "ui.panel",
    "ToolWindow.Button.hoverBackground": "ui.hover",
    "Tooltip.Learning.codeBorderColor": "ui.border",
    "Tooltip.Learning.linkUnderlineDefaultColor": "ui.accent_strong",
    "Tooltip.Learning.linkUnderlineHoveredColor": "ui.accent_strong",
    "Tooltip.Learning.secondaryActionForeground": "ui.accent_strong",
    "Tooltip.Learning.spanBackground": "ui.selection",
    "Tooltip.Learning.stepNumberForeground": "ui.quiet",
    "VersionControl.GitLog.headIconColor": "status.warning",
    "VersionControl.GitLog.localBranchIconColor": "status.success",
    "VersionControl.GitLog.otherIconColor": "ui.quiet",
    "VersionControl.GitLog.remoteBranchIconColor": "syntax.keyword",
    "VersionControl.GitLog.tagIconColor": "ui.quiet",
    "VersionControl.Log.Commit.Reference.foreground": "ui.quiet",
    "VersionControl.Log.Commit.hoveredBackground": "ui.hover",
    "VersionControl.Log.Commit.unmatchedForeground": "ui.quiet",
    "VersionControl.MarkerPopup.borderColor": "ui.border",
    "VersionControl.Merge.Status.NoConflicts.foreground": "status.success",
    "WelcomeScreen.Projects.actions.background": "ui.element",
}

# These read `text-over-accent` or `icon-over-accent` but sit on a surface, not the accent.
JETBRAINS_OFF_ACCENT_FOREGROUNDS = [
    "GotItTooltip.iconBorderColor",
    "ParameterInfo.currentParameterForeground",
    "PresentationAssistant.Bright.Popup.foreground",
    "PresentationAssistant.Pale.Popup.foreground",
    "SearchEverywhere.Tab.selectedForeground",
    "ToolWindow.Button.selectedForeground",
    "Tooltip.Learning.iconBorderColor",
]

JETBRAINS_COLOURS = {
    "ADDED_LINES_COLOR": "status.created",
    "ANNOTATIONS_COLOR": "ui.quiet",
    "ActionButton.hoverBackground": "ui.element",
    "ActionButton.iconTextForeground": "ui.foreground",
    "ActionButton.pressedBackground": "ui.selection",
    "BLOCK_TERMINAL_BLOCK_BACKGROUND_END": "ui.hover",
    "BLOCK_TERMINAL_BLOCK_BACKGROUND_START": "ui.hover",
    "BLOCK_TERMINAL_DEFAULT_BACKGROUND": "ui.background",
    "BLOCK_TERMINAL_DEFAULT_FOREGROUND": "ui.foreground",
    "BLOCK_TERMINAL_ERROR_BLOCK_STROKE_COLOR": "status.error",
    "BLOCK_TERMINAL_GENERATE_COMMAND_CARET_COLOR": "ui.cursor",
    "BLOCK_TERMINAL_GENERATE_COMMAND_PLACEHOLDER_FOREGROUND": "ui.quiet",
    "BLOCK_TERMINAL_HOVERED_BLOCK_BACKGROUND_END": "ui.element",
    "BLOCK_TERMINAL_HOVERED_BLOCK_BACKGROUND_START": "ui.element",
    "BLOCK_TERMINAL_INACTIVE_SELECTED_BLOCK_BACKGROUND": "ui.element",
    "BLOCK_TERMINAL_INACTIVE_SELECTED_BLOCK_STROKE_COLOR": "ui.border",
    "BLOCK_TERMINAL_PROMPT_SEPARATOR_COLOR": "ui.border",
    "BLOCK_TERMINAL_SELECTED_BLOCK_BACKGROUND": "ui.selection",
    "BLOCK_TERMINAL_SELECTED_BLOCK_STROKE_COLOR": "ui.accent",
    "Bookmark.Mnemonic.iconBackground": "ui.element",
    "Bookmark.Mnemonic.iconBorderColor": "status.warning",
    "Bookmark.Mnemonic.iconForeground": "ui.foreground",
    "Bookmark.iconBackground": "status.warning",
    "CARET_COLOR": "ui.cursor",
    "CARET_ROW_COLOR": "ui.hover",
    "CONSOLE_BACKGROUND_KEY": "ui.background",
    "DELETED_LINES_COLOR": "status.deleted",
    "DIFF_SEPARATOR_WAVE": "ui.border",
    "DOCUMENTATION_COLOR": "ui.panel",
    "DOC_COMMENT_GUIDE": "ui.indent",
    "DOC_COMMENT_LINK": "syntax.link",
    "FILESTATUS_ADDED": "status.created",
    "FILESTATUS_COPIED": "status.created",
    "FILESTATUS_DELETED": "status.deleted",
    "FILESTATUS_HIJACKED": "status.modified",
    "FILESTATUS_IDEA_FILESTATUS_DELETED_FROM_FILE_SYSTEM": "status.deleted",
    "FILESTATUS_IDEA_FILESTATUS_IGNORED": "status.ignored",
    "FILESTATUS_IDEA_FILESTATUS_MERGED_WITH_BOTH_CONFLICTS": "status.conflict",
    "FILESTATUS_IDEA_FILESTATUS_MERGED_WITH_CONFLICTS": "status.conflict",
    "FILESTATUS_IDEA_FILESTATUS_MERGED_WITH_PROPERTY_CONFLICTS": "status.conflict",
    "FILESTATUS_MERGED": "status.modified",
    "FILESTATUS_MODIFIED": "status.modified",
    "FILESTATUS_NOT_CHANGED_IMMEDIATE": "status.modified",
    "FILESTATUS_NOT_CHANGED_RECURSIVE": "status.modified",
    "FILESTATUS_OBSOLETE": "status.ignored",
    "FILESTATUS_RENAMED": "status.renamed",
    "FILESTATUS_SWITCHED": "status.renamed",
    "FILESTATUS_UNKNOWN": "status.created",
    "FILESTATUS_addedOutside": "status.created",
    "FILESTATUS_changelistConflict": "status.conflict",
    "FILESTATUS_modifiedOutside": "status.modified",
    "FOLDED_TEXT_BORDER_COLOR": "ui.border",
    "GRID_STRIPE_COLOR": "ui.hover",
    "GUTTER_BACKGROUND": "ui.background",
    "IGNORED_ADDED_LINES_BORDER_COLOR": "status.created",
    "IGNORED_DELETED_LINES_BORDER_COLOR": "status.deleted",
    "IGNORED_MODIFIED_LINES_BORDER_COLOR": "status.modified",
    "INDENT_GUIDE": "ui.indent",
    "INLINE_REFACTORING_SETTINGS_DEFAULT": "ui.element",
    "INLINE_REFACTORING_SETTINGS_FOCUSED": "ui.selection",
    "INLINE_REFACTORING_SETTINGS_HOVERED": "ui.selection",
    "LINE_NUMBERS_COLOR": "ui.quiet",
    "LINE_NUMBER_ON_CARET_ROW_COLOR": "ui.foreground",
    "LOOKUP_COLOR": "ui.panel",
    "METHOD_SEPARATORS_COLOR": "ui.border",
    "MODIFIED_LINES_COLOR": "status.modified",
    "MODIFIED_TAB_ICON": "status.modified",
    "NOTIFICATION_BACKGROUND": "ui.element",
    "READONLY_FRAGMENT_BACKGROUND": "ui.highlight",
    "RECENT_LOCATIONS_SELECTION": "ui.selection",
    "RIGHT_MARGIN_COLOR": "ui.border",
    "ScrollBar.background": "ui.background",
    "SELECTED_INDENT_GUIDE": "ui.indent_active",
    "SELECTED_TEARLINE_COLOR": "ui.indent_active",
    "SELECTION_BACKGROUND": "ui.selection",
    "SOFT_WRAP_SIGN_COLOR": "ui.invisible",
    "STRING_CONTENT_INDENT_GUIDE": "ui.indent",
    "TEARLINE_COLOR": "ui.border",
    "Table.hoverBackground": "ui.hover",
    "VISUAL_INDENT_GUIDE": "ui.indent",
    "WHITESPACES": "ui.invisible",
    "WHITESPACES_MODIFIED_LINES_COLOR": "status.modified",
}

# Read by the editor scheme and the UI theme alike; the transparent variants stay hidden at rest.
JETBRAINS_SCROLLBAR_THUMBS = [
    "ScrollBar.Mac.thumbBorderColor",
    "ScrollBar.Mac.thumbColor",
    "ScrollBar.Transparent.thumbBorderColor",
    "ScrollBar.Transparent.thumbColor",
    "ScrollBar.thumbBorderColor",
    "ScrollBar.thumbColor",
    "Scrollbar.Tabs.ThumbColor",
]
JETBRAINS_SCROLLBAR_HOVER_THUMBS = [
    "ScrollBar.Mac.Transparent.hoverThumbBorderColor",
    "ScrollBar.Mac.Transparent.hoverThumbColor",
    "ScrollBar.Mac.hoverThumbBorderColor",
    "ScrollBar.Mac.hoverThumbColor",
    "ScrollBar.Transparent.hoverThumbBorderColor",
    "ScrollBar.Transparent.hoverThumbColor",
    "ScrollBar.hoverThumbBorderColor",
    "ScrollBar.hoverThumbColor",
    "Scrollbar.Tabs.HoveredThumbColor",
]

JETBRAINS_FOREGROUNDS = {
    "ANNOTATION_ATTRIBUTE_NAME_ATTRIBUTES": "syntax.variable",
    "ANNOTATION_NAME_ATTRIBUTES": "syntax.attribute",
    "BLOCK_TERMINAL_COMMAND": "ui.foreground",
    "BLOCK_TERMINAL_GENERATE_COMMAND_PROMPT_TEXT": "ui.accent",
    "BREADCRUMBS_DEFAULT": "ui.muted",
    "BREADCRUMBS_INACTIVE": "ui.quiet",
    "CODE_VISION_DEFAULT": "status.hint",
    "CODE_VISION_HOVERED": "ui.accent",
    "CONSOLE_ERROR_OUTPUT": "status.error",
    "CONSOLE_NORMAL_OUTPUT": "ui.foreground",
    "CONSOLE_SYSTEM_OUTPUT": "ui.muted",
    "CONSOLE_USER_INPUT": "status.success",
    "CSS.COLOR": "syntax.number",
    "CSS.IMPORTANT": "syntax.keyword",
    "CSS.URL": "syntax.link",
    "CUSTOM_KEYWORD1_ATTRIBUTES": "syntax.keyword",
    "CUSTOM_KEYWORD2_ATTRIBUTES": "syntax.function",
    "CUSTOM_KEYWORD3_ATTRIBUTES": "syntax.type",
    "CUSTOM_KEYWORD4_ATTRIBUTES": "syntax.attribute",
    "CUSTOM_LINE_COMMENT_ATTRIBUTES": "syntax.comment",
    "CUSTOM_MULTI_LINE_COMMENT_ATTRIBUTES": "syntax.comment",
    "CUSTOM_NUMBER_ATTRIBUTES": "syntax.number",
    "CUSTOM_STRING_ATTRIBUTES": "syntax.string",
    "CUSTOM_VALID_STRING_ESCAPE_ATTRIBUTES": "syntax.number",
    "DEBUGGER_INLINED_VALUES": "status.hint",
    "DEBUGGER_INLINED_VALUES_EXECUTION_LINE": "status.hint",
    "DEBUGGER_INLINED_VALUES_MODIFIED": "status.warning",
    "DEBUG_THREAD_LABEL": "ui.muted",
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
    "GD_ANNOTATION": "syntax.attribute",
    "GD_BAD_CHARACTER": "status.error",
    "GD_BASE_TYPE": "syntax.type_system",
    "GD_CLASS_TYPE": "syntax.type",
    "GD_COMMENT": "syntax.comment",
    "GD_DANGER": "status.error",
    "GD_DOC_COMMENT": "syntax.comment",
    "GD_ENGINE_TYPE": "syntax.type_system",
    "GD_FLOW_KEYWORDS": "syntax.keyword",
    "GD_GLOBAL_FUNCTION": "syntax.function_system",
    "GD_GLOBAL_VARIABLE_AUTOLOAD": "syntax.variable",
    "GD_GLOBAL_VARIABLE_BUILT_IN": "syntax.variable",
    "GD_KEYWORD": "syntax.keyword",
    "GD_MEMBER": "syntax.variable",
    "GD_METHOD_CALL": "syntax.function",
    "GD_METHOD_DECLARATION": "syntax.function",
    "GD_NODE_PATH": "syntax.string",
    "GD_NODE_STRING_PATH": "syntax.string",
    "GD_NOTE": "status.hint",
    "GD_NUMBER": "syntax.number",
    "GD_STATIC_METHOD_CALL": "syntax.function",
    "GD_STRING": "syntax.string",
    "GD_STRING_FORMAT": "syntax.number",
    "GD_STRING_NAME": "syntax.string",
    "GD_WARNING": "status.warning",
    "HAML_CLASS": "syntax.attribute",
    "HAML_COMMENT": "syntax.comment",
    "HAML_ID": "syntax.attribute",
    "HAML_TAG": "syntax.tag",
    "HTML_ATTRIBUTE_NAME": "syntax.attribute",
    "HTML_ATTRIBUTE_VALUE": "syntax.string",
    "HTML_CUSTOM_TAG_NAME": "syntax.tag",
    "HTML_ENTITY_REFERENCE": "syntax.number",
    "HTML_TAG": "syntax.punctuation",
    "HTML_TAG_NAME": "syntax.tag",
    "HTTP_REQUEST_MULTIPART_BOUNDARY": "syntax.comment",
    "HTTP_REQUEST_PARAMETER_NAME": "syntax.variable",
    "HTTP_REQUEST_PARAMETER_VALUE": "syntax.string",
    "IMPLICIT_ANONYMOUS_CLASS_PARAMETER_ATTRIBUTES": "syntax.variable",
    "INLAY_BUTTON_HINT": "ui.quiet",
    "INLAY_TEXT_WITHOUT_BACKGROUND": "status.hint",
    "INLINE_PROMPT": "ui.accent",
    "INLINE_SUGGESTION": "status.predictive",
    "INSTANCE_FIELD_ATTRIBUTES": "syntax.variable",
    "JADE_FILE_PATH": "syntax.string",
    "JADE_FILTER_NAME": "syntax.function",
    "JADE_JS_BLOCK": "syntax.plain",
    "JADE_STATEMENTS": "syntax.keyword",
    "JS.GLOBAL_FUNCTION": "syntax.function",
    "JS.GLOBAL_VARIABLE": "syntax.variable",
    "JS.INSTANCE_MEMBER_FUNCTION": "syntax.function",
    "JS.LOCAL_VARIABLE": "syntax.variable",
    "JS.PARAMETER": "syntax.variable",
    "JS.REGEXP": "syntax.regex",
    "JSP_DIRECTIVE_NAME": "syntax.keyword",
    "LESS_VARIABLE": "syntax.variable",
    "LINE_FULL_COVERAGE": "status.created",
    "LINE_NONE_COVERAGE": "status.deleted",
    "LINE_PARTIAL_COVERAGE": "status.warning",
    "LOG_DEBUG_OUTPUT": "ui.muted",
    "LOG_ERROR_OUTPUT": "status.error",
    "LOG_EXPIRED_ENTRY": "status.unreachable",
    "LOG_INFO_OUTPUT": "status.info",
    "LOG_VERBOSE_OUTPUT": "ui.quiet",
    "LOG_WARNING_OUTPUT": "status.warning",
    "MARKDOWN_HEADER": "syntax.plain",
    "NG.SIGNAL": "syntax.function",
    "NOT_USED_ELEMENT_ATTRIBUTES": "status.unreachable",
    "PROPERTIES.KEY": "syntax.keyword",
    "PROPERTIES.KEY_VALUE_SEPARATOR": "syntax.punctuation",
    "RAINBOW_COLOR0": "syntax.function",
    "RAINBOW_COLOR1": "syntax.keyword",
    "RAINBOW_COLOR2": "syntax.string",
    "RAINBOW_COLOR3": "syntax.type",
    "RAINBOW_COLOR4": "syntax.constant",
    "REGEXP.BRACES": "syntax.punctuation",
    "REGEXP.BRACKETS": "syntax.punctuation",
    "REGEXP.CHAR_CLASS": "syntax.constant",
    "REGEXP.ESC_CHARACTER": "syntax.number",
    "REGEXP.META": "syntax.keyword",
    "REGEXP.PARENTHS": "syntax.punctuation",
    "REGEXP.QUOTE_CHARACTER": "syntax.number",
    "REGEXP.REDUNDANT_ESCAPE": "syntax.comment",
    "ReSharper.ASP_NET_RAZOR_TAG_HELPER_ATTRIBUTE": "syntax.attribute",
    "ReSharper.ASP_NET_RAZOR_TAG_HELPER_ELEMENT": "syntax.tag",
    "ReSharper.FORMAT_STRING_ITEM": "syntax.number",
    "ReSharper.FORMAT_STRING_ITEM_2": "syntax.number",
    "ReSharper.ReSharper.ShaderLab_DISABLED_SHADER_KEYWORD": "status.unreachable",
    "ReSharper.ReSharper.ShaderLab_IMPLICITLY_ENABLED_SHADER_KEYWORD": (
        "syntax.keyword"
    ),
    "ReSharper.ST_METHOD": "syntax.function",
    "ReSharper.ST_TYPE": "syntax.type",
    "ReSharper.STRING_ESCAPE_CHARACTER_2": "syntax.number",
    "SASS_ATTRIBUTE": "syntax.variable",
    "SASS_COMMENT": "syntax.comment",
    "SASS_CONSTANT": "syntax.constant",
    "SASS_DIRECTIVE": "syntax.keyword",
    "SASS_MIXIN": "syntax.function",
    "SASS_RULE": "syntax.tag",
    "SASS_VARIABLE": "syntax.variable",
    "SQL_SYNTHETIC_ENTITY": "syntax.type",
    "STATIC_FIELD_ATTRIBUTES": "syntax.variable",
    "STATIC_FINAL_FIELD_ATTRIBUTES": "syntax.constant",
    "STATIC_METHOD_ATTRIBUTES": "syntax.function",
    "Scala Type Alias": "syntax.type",
    "Scala Type parameter": "syntax.type_parameter",
    "Static method access": "syntax.function",
    "TEMPLATE_VARIABLE_ATTRIBUTES": "syntax.constant",
    "TS.TYPE_PARAMETER": "syntax.type_parameter",
    "TSCN_ATTRIBUTES": "syntax.attribute",
    "TSCN_MEMBER_REF": "syntax.variable",
    "TSCN_NODE_RESOURCE": "syntax.string",
    "TSCN_NODE_TYPE": "syntax.type",
    "TSCN_RES_STRING": "syntax.string",
    "TSCN_STRING": "syntax.string",
    "TYPE_PARAMETER_NAME_ATTRIBUTES": "syntax.type_parameter",
    "UNMATCHED_BRACE_ATTRIBUTES": "status.error",
    "VELOCITY_DIRECTIVE": "syntax.attribute",
    "VELOCITY_KEYWORD": "syntax.keyword",
    "VELOCITY_REFERENCE": "syntax.variable",
    "WRONG_REFERENCES_ATTRIBUTES": "status.error",
    "XML_ATTRIBUTE_NAME": "syntax.attribute",
    "XML_CUSTOM_TAG_NAME": "syntax.tag",
    "XML_ENTITY_REFERENCE": "syntax.number",
    "XML_PROLOGUE": "syntax.attribute",
    "XML_TAG": "syntax.punctuation",
    "XML_TAG_NAME": "syntax.tag",
    "XPATH.FUNCTION": "syntax.function",
    "XPATH.KEYWORD": "syntax.keyword",
    "XPATH.XPATH_NAME": "syntax.tag",
    "XPATH.XPATH_VARIABLE": "syntax.variable",
    "YAML_ANCHOR": "syntax.attribute",
    "com.jetbrains.cmake.COMMAND": "syntax.function",
    "osmorc.attributeName": "syntax.attribute",
    "osmorc.directiveName": "syntax.keyword",
    "osmorc.headerName": "syntax.keyword",
}

JETBRAINS_BOLD = {"BLOCK_TERMINAL_COMMAND", "MARKDOWN_HEADER"}

JETBRAINS_ITALIC = {
    "CONSOLE_USER_INPUT",
    "CUSTOM_LINE_COMMENT_ATTRIBUTES",
    "CUSTOM_MULTI_LINE_COMMENT_ATTRIBUTES",
    "DEBUGGER_INLINED_VALUES",
    "DEBUGGER_INLINED_VALUES_EXECUTION_LINE",
    "DEBUGGER_INLINED_VALUES_MODIFIED",
    "DEFAULT_BLOCK_COMMENT",
    "DEFAULT_DOC_COMMENT",
    "DEFAULT_DOC_COMMENT_TAG",
    "DEFAULT_DOC_COMMENT_TAG_VALUE",
    "DEFAULT_DOC_MARKUP",
    "DEFAULT_LINE_COMMENT",
    "DEFAULT_STATIC_FIELD",
    "DEFAULT_STATIC_METHOD",
    "GD_COMMENT",
    "GD_DOC_COMMENT",
    "HAML_COMMENT",
    "JS.GLOBAL_VARIABLE",
    "SASS_COMMENT",
    "STATIC_FIELD_ATTRIBUTES",
    "STATIC_FINAL_FIELD_ATTRIBUTES",
    "STATIC_METHOD_ATTRIBUTES",
    "Static method access",
    "TODO_DEFAULT_ATTRIBUTES",
}

JETBRAINS_BACKGROUNDS = {
    "DEBUGGER_SMART_STEP_INTO_TARGET": "ui.highlight",
    "DIFF_ABSENT": "ui.hover",
    "EVALUATED_EXPRESSION_ATTRIBUTES": "ui.highlight",
    "EVALUATED_EXPRESSION_EXECUTION_LINE_ATTRIBUTES": "ui.highlight",
    "INLINE_STACK_FRAMES": "ui.element",
    "NOT_TOP_FRAME_ATTRIBUTES": "ui.highlight",
    "REGEXP_MATCHED_GROUPS": "ui.highlight",
    "TERMINAL_COMMAND_TO_RUN_USING_IDE": "ui.highlight",
}

# A diff or debugger fill keyed to a status colour, with that colour as its stripe.
JETBRAINS_TINTS = {
    "BREAKPOINT_ATTRIBUTES": "status.error",
    "DEBUGGER_PREDICTED_VALUE_FALSE": "status.error",
    "DEBUGGER_PREDICTED_VALUE_FALSE_ALT": "status.error",
    "DEBUGGER_PREDICTED_VALUE_TRUE": "status.success",
    "DEBUGGER_PREDICTED_VALUE_TRUE_ALT": "status.success",
    "DIFF_CONFLICT": "status.conflict",
    "DIFF_DELETED": "status.deleted",
    "DIFF_INSERTED": "status.created",
    "DIFF_MODIFIED": "status.modified",
    "EXECUTIONPOINT_ATTRIBUTES": "ui.accent",
    "ReSharper.UNITY_PERFORMANCE_COSTLY_METHOD_HIGHLIGHTER": "status.warning",
}

JETBRAINS_EFFECTS = {
    "AI_INLAY_BUTTON_DEFAULT": ("ui.accent", JETBRAINS_EFFECT_BOXED),
    "AI_INLAY_BUTTON_FOCUSED": ("ui.accent", JETBRAINS_EFFECT_BOXED),
    "AI_INLAY_BUTTON_HOVERED": ("ui.accent", JETBRAINS_EFFECT_BOXED),
    "BAD_CHARACTER": ("status.error", JETBRAINS_EFFECT_WAVE),
    "BLINKING_HIGHLIGHTS_ATTRIBUTES": ("ui.indent_active", JETBRAINS_EFFECT_BOXED),
    "CODE_LENS_BORDER_COLOR": ("ui.border", JETBRAINS_EFFECT_BOXED),
    "CONSOLE_RANGE_TO_EXECUTE": ("ui.accent", JETBRAINS_EFFECT_BOXED),
    "DEBUGGER_PREDICTED_EXCEPTION": ("ui.accent", JETBRAINS_EFFECT_WAVE),
    "DEBUGGER_PREDICTED_FLOW": ("ui.accent", JETBRAINS_EFFECT_BOXED),
    "DEBUGGER_PREDICTED_SCOPE": ("ui.accent", JETBRAINS_EFFECT_WAVE),
    "DEFAULT_HIGHLIGHTED_REFERENCE": ("ui.quiet", JETBRAINS_EFFECT_UNDERSCORE),
    "DEFAULT_REASSIGNED_LOCAL_VARIABLE": ("ui.quiet", JETBRAINS_EFFECT_UNDERSCORE),
    "DEFAULT_REASSIGNED_PARAMETER": ("ui.quiet", JETBRAINS_EFFECT_UNDERSCORE),
    "DEPRECATED_ATTRIBUTES": ("ui.muted", JETBRAINS_EFFECT_STRIKEOUT),
    "GRAMMAR_ERROR": ("status.error", JETBRAINS_EFFECT_WAVE),
    "INACTIVE_HYPERLINK_ATTRIBUTES": ("ui.quiet", JETBRAINS_EFFECT_UNDERSCORE),
    "INLAY_BUTTON_DEFAULT": ("ui.border", JETBRAINS_EFFECT_BOXED),
    "INLAY_BUTTON_FOCUSED": ("ui.indent_active", JETBRAINS_EFFECT_BOXED),
    "INLAY_BUTTON_HOVERED": ("ui.indent_active", JETBRAINS_EFFECT_BOXED),
    "LIVE_TEMPLATE_ATTRIBUTES": ("ui.accent", JETBRAINS_EFFECT_BOXED),
    "LIVE_TEMPLATE_INACTIVE_SEGMENT": ("ui.invisible", JETBRAINS_EFFECT_BOXED),
    "MARKED_FOR_REMOVAL_ATTRIBUTES": ("status.error", JETBRAINS_EFFECT_STRIKEOUT),
    "ReSharper.UNITY_PERFORMANCE_CAMERA_MAIN": (
        "status.warning",
        JETBRAINS_EFFECT_UNDERSCORE,
    ),
    "ReSharper.UNITY_PERFORMANCE_COSTLY_METHOD_INVOCATION": (
        "status.warning",
        JETBRAINS_EFFECT_UNDERSCORE,
    ),
    "ReSharper.UNITY_PERFORMANCE_NULL_COMPARISON": (
        "status.warning",
        JETBRAINS_EFFECT_UNDERSCORE,
    ),
    "TERMINAL_CLASS_NAME_LOG_REFERENCE": ("ui.quiet", JETBRAINS_EFFECT_BOLD_DOTTED),
    "TEXT_STYLE_ERROR": ("status.error", JETBRAINS_EFFECT_BOLD_DOTTED),
    "TEXT_STYLE_SUGGESTION": ("status.info", JETBRAINS_EFFECT_BOLD_DOTTED),
    "TEXT_STYLE_WARNING": ("status.warning", JETBRAINS_EFFECT_BOLD_DOTTED),
    "TYPO": ("status.info", JETBRAINS_EFFECT_WAVE),
}

JETBRAINS_INLAY_BUTTONS = [
    "AI_INLAY_BUTTON_DEFAULT",
    "AI_INLAY_BUTTON_FOCUSED",
    "AI_INLAY_BUTTON_HOVERED",
    "INLAY_BUTTON_DEFAULT",
    "INLAY_BUTTON_FOCUSED",
    "INLAY_BUTTON_HOVERED",
]

# An effect in the severity's colour, which also marks the error stripe.
JETBRAINS_DIAGNOSTICS = {
    "ERRORS_ATTRIBUTES": ("status.error", JETBRAINS_EFFECT_WAVE),
    "FILESTATUS_ERRORS": ("status.error", JETBRAINS_EFFECT_WAVE),
    "GENERIC_SERVER_ERROR_OR_WARNING": ("status.warning", JETBRAINS_EFFECT_UNDERSCORE),
    "INFO_ATTRIBUTES": ("status.hint", JETBRAINS_EFFECT_WAVE),
    "RUNTIME_ERROR": ("status.error", JETBRAINS_EFFECT_BOLD_DOTTED),
    "SUGGESTION": ("status.info", JETBRAINS_EFFECT_WAVE),
    "WARNING_ATTRIBUTES": ("status.warning", JETBRAINS_EFFECT_WAVE),
}

JETBRAINS_STRIPES = {
    "BOOKMARKS_ATTRIBUTES": "status.warning",
    "DO_NOT_SHOW": "status.hint",
    "NO_ANALYSIS": "ui.quiet",
}

# Empty drops the base scheme's fill, which would sit behind syntax text.
JETBRAINS_CLEARED = [
    "CONSOLE_OUTPUT",
    "HAML_RUBY_CODE",
    "INJECTED_LANGUAGE_FRAGMENT",
    "TS.TYPE_GUARD",
    "VELOCITY_SCRIPTING_BACKGROUND",
]

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
    status = palette["status"]
    style = {
        "accents": ui["accents"],
        "background": ui["panel"],
        "border": ui["border"],
        "border.disabled": ui["border"],
        "border.focused": ui["accent"],
        "border.selected": ui["accent"],
        "border.transparent": TRANSPARENT,
        "border.variant": ui["border_variant"],
        "debugger.accent": status["error"],
        "drop_target.background": ui["selection_overlay"],
        "drop_target.border": ui["foreground"],
        "editor.active_line.background": ui["hover"],
        "editor.active_line_number": ui["foreground"],
        "editor.active_wrap_guide": ui["border"],
        "editor.background": ui["background"],
        "editor.debugger_active_line.background": tint(palette, ui["accent"]),
        "editor.diff_hunk.added.background": tint(palette, status["created"]),
        "editor.diff_hunk.deleted.background": tint(palette, status["deleted"]),
        "editor.document_highlight.bracket_background": ui["highlight"],
        "editor.document_highlight.read_background": ui["highlight"],
        "editor.document_highlight.write_background": ui["highlight"],
        "editor.foreground": ui["foreground"],
        "editor.gutter.background": ui["background"],
        "editor.highlighted_line.background": ui["hover"],
        "editor.hover_line_number": ui["foreground"],
        "editor.indent_guide": ui["indent"],
        "editor.indent_guide_active": ui["indent_active"],
        "editor.invisible": ui["invisible"],
        "editor.line_number": ui["quiet"],
        "editor.subheader.background": ui["panel"],
        "editor.wrap_guide": ui["border"],
        "element.active": ui["selection"],
        "element.background": ui["element"],
        "element.disabled": ui["element"],
        "element.hover": ui["hover"],
        "element.selected": ui["selection"],
        "elevated_surface.background": ui["background"],
        "ghost_element.active": ui["selection"],
        "ghost_element.background": TRANSPARENT,
        "ghost_element.disabled": ui["element"],
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
        "panel.indent_guide_hover": ui["indent_active"],
        "players": zed_players(palette),
        "scrollbar.thumb.active_background": ui["muted"] + SCROLLBAR_HOVER_ALPHA,
        "scrollbar.thumb.background": ui["indent_active"] + SCROLLBAR_ALPHA,
        "scrollbar.thumb.hover_background": ui["muted"] + SCROLLBAR_HOVER_ALPHA,
        "scrollbar.track.background": TRANSPARENT,
        "scrollbar.track.border": TRANSPARENT,
        "search.active_match_background": ui["find_active"],
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
        "terminal.ansi.background": ui["background"],
        "terminal.background": ui["background"],
        "terminal.bright_foreground": ansi["bright"][7],
        "terminal.dim_foreground": ui["quiet"],
        "terminal.foreground": ui["foreground"],
        "text": ui["foreground"],
        "text.accent": ui["accent_strong"],
        "text.disabled": ui["quiet"],
        "text.muted": ui["muted"],
        "text.placeholder": ui["quiet"],
        "title_bar.background": ui["panel"],
        "title_bar.inactive_background": ui["panel"],
        "toolbar.background": ui["background"],
        "version_control.conflict": status["conflict"],
        "version_control.conflict_marker.ours": tint(palette, status["created"]),
        "version_control.conflict_marker.theirs": tint(palette, status["info"]),
        "version_control.word_added": tint(palette, status["created"]),
        "version_control.word_deleted": tint(palette, status["deleted"]),
    }
    for name, colour in palette["status"].items():
        style[name] = colour
        style[f"{name}.background"] = tint(palette, colour)
        style[f"{name}.border"] = colour
    # The inlay hint pill, opaque like the other editors' so hint text keeps 4.5:1.
    style["hint.background"] = ui["element"]
    for index, name in enumerate(ANSI_NAMES):
        style[f"terminal.ansi.{name}"] = ansi["normal"][index]
        style[f"terminal.ansi.bright_{name}"] = ansi["bright"][index]
        style[f"terminal.ansi.dim_{name}"] = ansi["normal"][index]
    style["terminal.ansi.dim_white"] = ui["quiet"]
    return dict(sorted(style.items()))


def zed_players(palette: Palette) -> list[dict[str, str]]:
    ui = palette["ui"]
    *others, agent = ui["accents"]
    collaborators = [others[i % len(others)] for i in range(ZED_PLAYERS - 2)]
    return [
        {"background": cursor, "cursor": cursor, "selection": ui["selection_overlay"]}
        for cursor in [ui["cursor"], *collaborators, agent]
    ]


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
        f"search-background = {ui['find']}",
        f"search-foreground = {ui['foreground']}",
        f"search-selected-background = {ui['find_active_border']}",
        f"search-selected-foreground = {ansi['normal'][0]}",
        f"split-divider-color = {ui['border']}",
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
    syntax = palette["syntax"]
    colours = {
        "activityBar.background": ui["panel"],
        "activityBar.border": ui["border"],
        "activityBar.foreground": ui["foreground"],
        "activityBar.inactiveForeground": ui["quiet"],
        "activityBarBadge.background": ui["accent"],
        "activityBarBadge.foreground": ui["background"],
        "activityBarTop.foreground": ui["foreground"],
        "activityBarTop.inactiveForeground": ui["quiet"],
        "activityErrorBadge.background": status["error"],
        "activityErrorBadge.foreground": ui["background"],
        "activityWarningBadge.background": status["warning"],
        "activityWarningBadge.foreground": ui["background"],
        "badge.background": ui["element"],
        "badge.foreground": ui["foreground"],
        "button.background": ui["accent"],
        "button.foreground": ui["background"],
        "button.hoverBackground": ui["accent_strong"],
        "commandCenter.activeBackground": ui["element"],
        "commandCenter.background": ui["hover"],
        "debugExceptionWidget.background": tint(palette, status["error"]),
        "debugExceptionWidget.border": status["error"],
        "debugIcon.breakpointCurrentStackframeForeground": status["warning"],
        "debugIcon.breakpointDisabledForeground": ui["quiet"],
        "debugIcon.breakpointForeground": status["error"],
        "debugIcon.breakpointStackframeForeground": status["success"],
        "debugIcon.breakpointUnverifiedForeground": ui["quiet"],
        "debugIcon.continueForeground": ui["accent"],
        "debugIcon.disconnectForeground": status["error"],
        "debugIcon.pauseForeground": ui["accent"],
        "debugIcon.restartForeground": status["success"],
        "debugIcon.startForeground": status["success"],
        "debugIcon.stepBackForeground": ui["accent"],
        "debugIcon.stepIntoForeground": ui["accent"],
        "debugIcon.stepOutForeground": ui["accent"],
        "debugIcon.stepOverForeground": ui["accent"],
        "debugIcon.stopForeground": status["error"],
        "debugTokenExpression.boolean": syntax["constant"],
        "debugTokenExpression.error": status["error"],
        "debugTokenExpression.name": syntax["variable"],
        "debugTokenExpression.number": syntax["number"],
        "debugTokenExpression.string": syntax["string"],
        "debugTokenExpression.type": syntax["type"],
        "debugTokenExpression.value": ui["muted"],
        "debugToolBar.background": ui["element"],
        "debugView.exceptionLabelBackground": status["error"],
        "debugView.exceptionLabelForeground": ui["background"],
        "debugView.stateLabelBackground": ui["element"],
        "debugView.valueChangedHighlight": ui["accent"],
        "descriptionForeground": ui["muted"],
        "diffEditor.diagonalFill": ui["border"],
        "diffEditor.insertedLineBackground": tint(palette, status["created"]),
        "diffEditor.insertedTextBackground": TRANSPARENT,
        "diffEditor.insertedTextBorder": status["created"],
        "diffEditor.moveActive.border": status["warning"],
        "diffEditor.removedLineBackground": tint(palette, status["deleted"]),
        "diffEditor.removedTextBackground": TRANSPARENT,
        "diffEditor.removedTextBorder": status["deleted"],
        "disabledForeground": ui["quiet"],
        "dropdown.background": ui["element"],
        "dropdown.border": ui["border"],
        "dropdown.foreground": ui["foreground"],
        "editor.background": ui["background"],
        "editor.findMatchBackground": ui["find_active"],
        "editor.findMatchBorder": ui["find_active_border"],
        "editor.findMatchHighlightBackground": ui["find"],
        "editor.findMatchHighlightBorder": ui["find_border"],
        "editor.findRangeHighlightBackground": ui["selection"] + VSCODE_RANGE_ALPHA,
        "editor.focusedStackFrameHighlightBackground": tint(palette, ui["accent"]),
        "editor.foldPlaceholderForeground": ui["quiet"],
        "editor.foreground": ui["foreground"],
        "editor.hoverHighlightBackground": ui["highlight"],
        "editor.inlineValuesBackground": ui["element"],
        "editor.inlineValuesForeground": status["hint"],
        "editor.lineHighlightBackground": ui["hover"],
        "editor.lineHighlightBorder": ui["hover"],
        "editor.linkedEditingBackground": ui["highlight"],
        "editor.rangeHighlightBackground": ui["selection"] + VSCODE_RANGE_ALPHA,
        "editor.selectionBackground": ui["selection"],
        "editor.snippetFinalTabstopHighlightBorder": ui["indent_active"],
        "editor.snippetTabstopHighlightBackground": ui["highlight"],
        "editor.stackFrameHighlightBackground": ui["highlight"],
        "editor.wordHighlightBackground": ui["highlight"],
        "editor.wordHighlightStrongBackground": tint(palette, syntax["keyword"]),
        "editorBracketHighlight.unexpectedBracket.foreground": syntax["regex"],
        "editorBracketMatch.background": ui["highlight"],
        "editorBracketMatch.border": ui["indent_active"],
        "editorCodeLens.foreground": status["hint"],
        "editorCursor.foreground": ui["cursor"],
        "editorError.foreground": status["error"],
        "editorGhostText.foreground": status["predictive"],
        "editorGroup.border": ui["border"],
        "editorGroup.dropBackground": ui["selection_overlay"],
        "editorGroupHeader.tabsBackground": ui["panel"],
        "editorGutter.addedBackground": status["created"],
        "editorGutter.background": ui["background"],
        "editorGutter.deletedBackground": status["deleted"],
        "editorGutter.modifiedBackground": status["modified"],
        "editorHint.foreground": status["hint"],
        "editorIndentGuide.activeBackground1": ui["indent_active"],
        "editorIndentGuide.background1": ui["indent"],
        "editorInfo.foreground": status["info"],
        "editorInlayHint.background": ui["element"],
        "editorInlayHint.foreground": status["hint"],
        "editorLightBulb.foreground": status["warning"],
        "editorLightBulbAutoFix.foreground": status["info"],
        "editorLineNumber.activeForeground": ui["foreground"],
        "editorLineNumber.foreground": ui["quiet"],
        "editorLink.activeForeground": syntax["link"],
        "editorOverviewRuler.border": ui["border"],
        "editorOverviewRuler.errorForeground": status["error"],
        "editorOverviewRuler.findMatchForeground": ui["find_active_border"],
        "editorOverviewRuler.rangeHighlightForeground": ui["accent"],
        "editorOverviewRuler.wordHighlightStrongForeground": syntax["keyword"],
        "editorRuler.foreground": ui["border"],
        "editorStickyScrollHover.background": ui["hover"],
        "editorSuggestWidgetStatus.foreground": status["hint"],
        "editorWarning.foreground": status["warning"],
        "editorWhitespace.foreground": ui["invisible"],
        "editorWidget.background": ui["panel"],
        "editorWidget.border": ui["border"],
        "errorForeground": status["error"],
        "focusBorder": ui["accent"],
        "foreground": ui["foreground"],
        "gitDecoration.addedResourceForeground": status["created"],
        "gitDecoration.conflictingResourceForeground": status["conflict"],
        "gitDecoration.deletedResourceForeground": status["deleted"],
        "gitDecoration.ignoredResourceForeground": status["ignored"],
        "gitDecoration.modifiedResourceForeground": status["modified"],
        "gitDecoration.renamedResourceForeground": status["renamed"],
        "gitDecoration.stageDeletedResourceForeground": status["deleted"],
        "gitDecoration.stageModifiedResourceForeground": status["modified"],
        "gitDecoration.submoduleResourceForeground": ui["accent_strong"],
        "gitDecoration.untrackedResourceForeground": status["created"],
        "icon.foreground": ui["muted"],
        "input.background": ui["element"],
        "input.border": ui["border"],
        "input.placeholderForeground": ui["quiet"],
        "inputOption.activeBorder": ui["accent"],
        "inputOption.activeForeground": ui["foreground"],
        "inputOption.hoverBackground": ui["selection"],
        "inputValidation.errorBackground": ui["panel"],
        "inputValidation.errorBorder": status["error"],
        "inputValidation.infoBackground": ui["panel"],
        "inputValidation.infoBorder": status["info"],
        "inputValidation.warningBackground": ui["panel"],
        "inputValidation.warningBorder": status["warning"],
        "keybindingLabel.background": ui["element"],
        "keybindingLabel.border": ui["border"],
        "keybindingLabel.bottomBorder": ui["border"],
        "keybindingLabel.foreground": ui["foreground"],
        "list.activeSelectionBackground": ui["selection"],
        "list.activeSelectionForeground": ui["foreground"],
        "list.deemphasizedForeground": ui["quiet"],
        "list.dropBackground": ui["highlight"],
        "list.errorForeground": status["error"],
        "list.focusOutline": ui["accent"],
        "list.highlightForeground": ui["accent_strong"],
        "list.hoverBackground": ui["hover"],
        "list.inactiveSelectionBackground": ui["element"],
        "list.invalidItemForeground": status["warning"],
        "list.warningForeground": status["warning"],
        "listFilterWidget.noMatchesOutline": status["error"],
        "markdownAlert.important.foreground": syntax["keyword"],
        "markdownAlert.tip.foreground": status["success"],
        "menu.background": ui["panel"],
        "menu.border": ui["border"],
        "minimap.errorHighlight": status["error"],
        "multiDiffEditor.border": ui["border"],
        "multiDiffEditor.headerBackground": ui["panel"],
        "panel.background": ui["panel"],
        "panel.border": ui["border"],
        "panelInput.border": ui["border"],
        "panelSectionHeader.background": ui["panel"],
        "panelTitle.activeBorder": ui["accent"],
        "panelTitle.activeForeground": ui["foreground"],
        "panelTitle.inactiveForeground": ui["muted"],
        "peekViewEditor.background": ui["panel"],
        "peekViewEditor.matchHighlightBackground": ui["find"],
        "peekViewResult.background": ui["panel"],
        "peekViewResult.fileForeground": ui["foreground"],
        "peekViewResult.lineForeground": ui["muted"],
        "peekViewResult.matchHighlightBackground": ui["find"],
        "peekViewResult.selectionBackground": ui["selection"],
        "peekViewResult.selectionForeground": ui["foreground"],
        "peekViewTitle.background": ui["panel"],
        "peekViewTitleDescription.foreground": ui["muted"],
        "peekViewTitleLabel.foreground": ui["foreground"],
        "pickerGroup.border": ui["border"],
        "pickerGroup.foreground": ui["accent"],
        "problemsErrorIcon.foreground": status["error"],
        "problemsInfoIcon.foreground": status["info"],
        "problemsWarningIcon.foreground": status["warning"],
        "progressBar.background": ui["accent"],
        "quickInput.background": ui["panel"],
        "quickInputTitle.background": ui["element"],
        "scrollbarSlider.activeBackground": ui["muted"] + SCROLLBAR_HOVER_ALPHA,
        "scrollbarSlider.background": ui["indent_active"] + SCROLLBAR_ALPHA,
        "scrollbarSlider.hoverBackground": ui["muted"] + SCROLLBAR_HOVER_ALPHA,
        "selection.background": ui["selection"],
        "settings.headerForeground": ui["foreground"],
        "settings.modifiedItemIndicator": status["modified"],
        "sideBar.background": ui["panel"],
        "sideBar.border": ui["border"],
        "sideBar.foreground": ui["foreground"],
        "sideBarSectionHeader.background": ui["panel"],
        "simpleFindWidget.sashBorder": ui["border"],
        "statusBar.background": ui["panel"],
        "statusBar.border": ui["border"],
        "statusBar.debuggingBackground": status["warning"],
        "statusBar.debuggingForeground": ui["background"],
        "statusBar.foreground": ui["muted"],
        "statusBar.noFolderBackground": ui["panel"],
        "statusBarItem.activeBackground": ui["selection"],
        "statusBarItem.compactHoverBackground": ui["element"],
        "statusBarItem.errorBackground": status["error"],
        "statusBarItem.errorForeground": ui["background"],
        "statusBarItem.hoverBackground": ui["element"],
        "statusBarItem.offlineBackground": status["error"],
        "statusBarItem.prominentBackground": ui["element"],
        "statusBarItem.warningBackground": status["warning"],
        "statusBarItem.warningForeground": ui["background"],
        "strongForeground": ui["foreground"],
        "symbolIcon.classForeground": syntax["type"],
        "symbolIcon.constructorForeground": syntax["function"],
        "symbolIcon.enumeratorForeground": syntax["type"],
        "symbolIcon.enumeratorMemberForeground": syntax["constant"],
        "symbolIcon.eventForeground": syntax["attribute"],
        "symbolIcon.fieldForeground": syntax["variable"],
        "symbolIcon.functionForeground": syntax["function"],
        "symbolIcon.interfaceForeground": syntax["type"],
        "symbolIcon.methodForeground": syntax["function"],
        "symbolIcon.variableForeground": syntax["variable"],
        "tab.activeBackground": ui["background"],
        "tab.activeBorderTop": ui["accent"],
        "tab.activeForeground": ui["foreground"],
        "tab.activeModifiedBorder": status["modified"],
        "tab.border": ui["border"],
        "tab.inactiveBackground": ui["panel"],
        "tab.inactiveForeground": ui["muted"],
        "tab.unfocusedInactiveForeground": ui["quiet"],
        "terminal.background": ui["background"],
        "terminal.findMatchBackground": ui["find_terminal_active"],
        "terminal.findMatchBorder": ui["find_active_border"],
        "terminal.findMatchHighlightBackground": ui["find_terminal"],
        "terminal.findMatchHighlightBorder": ui["find_border"],
        "terminal.foreground": ui["foreground"],
        "terminal.initialHintForeground": status["hint"],
        "terminal.selectionBackground": ui["selection"],
        "terminalCommandDecoration.defaultBackground": ui["quiet"],
        "terminalCommandDecoration.errorBackground": status["error"],
        "terminalCommandDecoration.successBackground": status["info"],
        "terminalCursor.foreground": ui["cursor"],
        "terminalStickyScrollHover.background": ui["hover"],
        "textBlockQuote.background": ui["element"],
        "textBlockQuote.border": ui["indent_active"],
        "textCodeBlock.background": ui["highlight"],
        "textLink.activeForeground": ui["accent"],
        "textLink.foreground": ui["accent_strong"],
        "textPreformat.background": ui["element"],
        "textPreformat.foreground": ui["foreground"],
        "textSeparator.foreground": ui["border"],
        "titleBar.activeBackground": ui["panel"],
        "titleBar.activeForeground": ui["foreground"],
        "titleBar.border": ui["border"],
        "titleBar.inactiveBackground": ui["panel"],
        "titleBar.inactiveForeground": ui["quiet"],
        "toolbar.hoverBackground": ui["element"],
        "tree.indentGuidesStroke": ui["indent"],
        "tree.tableColumnsBorder": ui["border"],
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


def tint(palette: Palette, colour: str) -> str:
    alpha = TINT_ALPHAS[palette["appearance"]]
    return opaque(colour + alpha, palette["ui"]["background"])


def luminance(hex_colour: str) -> float:
    def linear(channel: str) -> float:
        c = int(channel, 16) / 255
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4

    r, g, b = (linear(hex_colour[i : i + 2]) for i in (1, 3, 5))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(text: str, ground: str) -> float:
    light, dark = sorted((luminance(text), luminance(ground)), reverse=True)
    return (light + 0.05) / (dark + 0.05)


def syntax_grounds(palette: Palette) -> dict[str, str]:
    ui, status = palette["ui"], palette["status"]
    grounds = {key: ui[key] for key in SYNTAX_GROUNDS}
    grounds |= {f"{key} tint": tint(palette, status[key]) for key in TINTED_STATUSES}
    grounds |= {
        "accent tint": tint(palette, ui["accent"]),
        "keyword tint": tint(palette, palette["syntax"]["keyword"]),
    }
    return grounds


def contrast_failures(palette: Palette) -> list[str]:
    pairs = [
        (f"syntax.{role} on {name}", colour, ground)
        for name, ground in syntax_grounds(palette).items()
        for role, colour in palette["syntax"].items()
    ]
    pairs += [
        (
            f"{text} on {ground}",
            palette_colour(palette, text),
            palette_colour(palette, ground),
        )
        for text, ground in HINT_PAIRS
    ]
    return [
        f"{palette['name']}: {label} is {contrast(text, ground):.2f}:1"
        for label, text, ground in pairs
        if contrast(text, ground) < MINIMUM_CONTRAST
    ]


def xml_text(root: ET.Element) -> str:
    ET.indent(root)
    return ET.tostring(root, encoding="unicode") + "\n"


def jetbrains_theme(palette: Palette) -> dict[str, Any]:
    ui = palette["ui"]
    accent = tint(palette, ui["accent"])
    colours = {
        token: palette_colour(palette, path)
        for token, path in JETBRAINS_THEME_TOKENS.items()
    }
    colours |= {
        "accent-brand-bg-secondary": accent,
        "accent-error-bg-secondary": tint(palette, palette["status"]["error"]),
        "accent-success-bg-secondary": tint(palette, palette["status"]["success"]),
        "accent-warning-bg-secondary": tint(palette, palette["status"]["warning"]),
        "tab-file-color-mask-bg": ui["background"] + SCROLLBAR_HOVER_ALPHA,
        "toolbar-selected-bg": accent,
        "toolbar-selected-bg-hovered": tint(palette, ui["accent_strong"]),
    }
    overrides = {
        key: palette_colour(palette, path) for key, path in JETBRAINS_UI.items()
    }
    overrides |= {key: ui["foreground"] for key in JETBRAINS_OFF_ACCENT_FOREGROUNDS}
    overrides |= jetbrains_scrollbars(palette)
    overrides |= {
        "Badge.blueSecondaryBackground": accent,
        "Badge.greenSecondaryBackground": tint(palette, palette["status"]["success"]),
        "Badge.purpleSecondaryBackground": tint(palette, palette["syntax"]["keyword"]),
        "DragAndDrop.areaBackground": accent,
        "DragAndDrop.rowBackground": accent,
        "MemoryIndicator.usedBackground": accent,
        "ToolWindow.Button.DragAndDrop.buttonDropBackground": accent,
        "ToolWindow.DragAndDrop.areaBackground": accent,
        "VersionControl.FileHistory.Commit.selectedBranchBackground": accent,
        "VersionControl.Log.Commit.currentBranchBackground": accent,
    }
    return {
        "name": palette["name"],
        "dark": palette["appearance"] == "dark",
        "author": AUTHOR,
        "parentTheme": JETBRAINS_PARENT_THEMES[palette["appearance"]],
        "editorScheme": f"/{slug(palette)}.xml",
        "colors": dict(sorted(colours.items())),
        "ui": dict(sorted(overrides.items())),
    }


def jetbrains_scrollbars(palette: Palette) -> dict[str, str]:
    ui = palette["ui"]
    thumb = ui["indent_active"] + SCROLLBAR_ALPHA
    hover = ui["muted"] + SCROLLBAR_HOVER_ALPHA
    return {key: thumb for key in JETBRAINS_SCROLLBAR_THUMBS} | {
        key: hover for key in JETBRAINS_SCROLLBAR_HOVER_THUMBS
    }


def jetbrains_scheme(palette: Palette) -> str:
    ui = palette["ui"]

    def colour(value: str) -> str:
        return opaque(value, ui["background"])[1:]

    def path_colour(path: str) -> str:
        return colour(palette_colour(palette, path))

    def path_tint(path: str) -> str:
        return tint(palette, palette_colour(palette, path))[1:]

    link = path_colour("syntax.link")
    hyperlink = {
        "EFFECT_COLOR": link,
        "EFFECT_TYPE": JETBRAINS_EFFECT_UNDERSCORE,
        "FOREGROUND": link,
    }
    find = {
        "BACKGROUND": colour(ui["find"]),
        "ERROR_STRIPE_COLOR": colour(ui["find_active_border"]),
    }
    terminal_find = {
        "BACKGROUND": colour(ui["find"]),
        "FOREGROUND": colour(ui["foreground"]),
    }
    hint = path_colour("status.hint")
    inlay = {"BACKGROUND": colour(ui["element"]), "FOREGROUND": hint}
    current_hint = {
        "BACKGROUND": path_tint("ui.accent"),
        "FOREGROUND": colour(ui["foreground"]),
    }
    invalid_escape = {
        "EFFECT_COLOR": path_colour("status.error"),
        "EFFECT_TYPE": JETBRAINS_EFFECT_WAVE,
        "FOREGROUND": path_colour("syntax.string"),
    }
    unreachable = path_colour("status.unreachable")
    keyword = path_colour("syntax.keyword")
    attributes = {
        "BLOCK_TERMINAL_CURRENT_SEARCH_ENTRY": terminal_find
        | {
            "BACKGROUND": colour(ui["find_active"]),
            "EFFECT_COLOR": colour(ui["find_active_border"]),
            "EFFECT_TYPE": JETBRAINS_EFFECT_BOXED,
        },
        "BLOCK_TERMINAL_SEARCH_ENTRY": terminal_find,
        "BREADCRUMBS_CURRENT": {
            "BACKGROUND": colour(ui["element"]),
            "FOREGROUND": colour(ui["foreground"]),
        },
        "BREADCRUMBS_HOVERED": {
            "BACKGROUND": colour(ui["hover"]),
            "FOREGROUND": colour(ui["foreground"]),
        },
        "CTRL_CLICKABLE": hyperlink,
        "CUSTOM_INVALID_STRING_ESCAPE_ATTRIBUTES": invalid_escape,
        "DEBUGGER_SMART_STEP_INTO_SELECTION": {
            "BACKGROUND": colour(ui["selection"]),
            "EFFECT_COLOR": colour(ui["accent"]),
            "EFFECT_TYPE": JETBRAINS_EFFECT_BOXED,
        },
        "DEBUGGER_UNREACHABLE_DECORATION": {
            "EFFECT_COLOR": unreachable,
            "EFFECT_TYPE": JETBRAINS_EFFECT_STRIKEOUT,
            "FOREGROUND": unreachable,
        },
        "DEFAULT_INVALID_STRING_ESCAPE": invalid_escape,
        "DELETED_TEXT_ATTRIBUTES": {
            "BACKGROUND": path_tint("status.deleted"),
            "EFFECT_COLOR": colour(ui["muted"]),
            "EFFECT_TYPE": JETBRAINS_EFFECT_STRIKEOUT,
            "FOREGROUND": colour(ui["muted"]),
        },
        "DOC_TIPS_SHORTCUT": {
            "EFFECT_COLOR": colour(ui["border"]),
            "EFFECT_TYPE": JETBRAINS_EFFECT_BOXED,
            "FOREGROUND": colour(ui["muted"]),
        },
        "FOLDED_TEXT_ATTRIBUTES": {
            "BACKGROUND": colour(ui["element"]),
            "FOREGROUND": colour(ui["muted"]),
        },
        "FOLLOWED_HYPERLINK_ATTRIBUTES": hyperlink,
        "HYPERLINK_ATTRIBUTES": hyperlink,
        "IDENTIFIER_UNDER_CARET_ATTRIBUTES": {
            "BACKGROUND": colour(ui["element"]),
            "ERROR_STRIPE_COLOR": colour(ui["accent"]),
        },
        "INLAY_DEFAULT": inlay,
        "INLINE_PARAMETER_HINT": inlay,
        "INLINE_PARAMETER_HINT_CURRENT": current_hint,
        "INLINE_PARAMETER_HINT_HIGHLIGHTED": current_hint,
        "MATCHED_BRACE_ATTRIBUTES": {
            "BACKGROUND": colour(ui["highlight"]),
            "EFFECT_COLOR": colour(ui["indent_active"]),
            "EFFECT_TYPE": JETBRAINS_EFFECT_BOXED,
        },
        "PROPERTIES.INVALID_STRING_ESCAPE": invalid_escape,
        "ReSharper.ReSharper.ShaderLab_ENABLED_SHADER_KEYWORD": {
            "EFFECT_COLOR": keyword,
            "EFFECT_TYPE": JETBRAINS_EFFECT_UNDERSCORE,
            "FOREGROUND": keyword,
        },
        "ReSharper.ReSharper.ShaderLab_SUPPRESSED_SHADER_KEYWORD": {
            "EFFECT_COLOR": unreachable,
            "EFFECT_TYPE": JETBRAINS_EFFECT_STRIKEOUT,
            "FOREGROUND": unreachable,
        },
        "SEARCH_RESULT_ATTRIBUTES": find,
        "SQL_OUTER_QUERY_COLUMN": {
            "EFFECT_COLOR": colour(ui["quiet"]),
            "EFFECT_TYPE": JETBRAINS_EFFECT_UNDERSCORE,
            "FOREGROUND": path_colour("syntax.variable"),
        },
        "TEXT": {
            "BACKGROUND": colour(ui["background"]),
            "FOREGROUND": colour(ui["foreground"]),
        },
        "TEXT_SEARCH_RESULT_ATTRIBUTES": find,
        "TODO_DEFAULT_ATTRIBUTES": {
            "ERROR_STRIPE_COLOR": colour(ui["accent"]),
            "FONT_TYPE": JETBRAINS_FONT_ITALIC,
            "FOREGROUND": path_colour("syntax.comment_emphasized"),
        },
        "WRITE_IDENTIFIER_UNDER_CARET_ATTRIBUTES": {
            "BACKGROUND": path_tint("syntax.keyword"),
            "ERROR_STRIPE_COLOR": keyword,
        },
        "WRITE_SEARCH_RESULT_ATTRIBUTES": find,
    }
    for key, path in JETBRAINS_FOREGROUNDS.items():
        attributes[key] = {"FOREGROUND": path_colour(path)}
        if key in JETBRAINS_BOLD:
            attributes[key]["FONT_TYPE"] = JETBRAINS_FONT_BOLD
        if key in JETBRAINS_ITALIC:
            attributes[key]["FONT_TYPE"] = JETBRAINS_FONT_ITALIC
    for key, path in JETBRAINS_BACKGROUNDS.items():
        attributes[key] = {"BACKGROUND": path_colour(path)}
    for key, path in JETBRAINS_TINTS.items():
        attributes[key] = {
            "BACKGROUND": path_tint(path),
            "ERROR_STRIPE_COLOR": path_colour(path),
        }
    for key, (path, effect) in JETBRAINS_EFFECTS.items():
        attributes[key] = {"EFFECT_COLOR": path_colour(path), "EFFECT_TYPE": effect}
    for key, (path, effect) in JETBRAINS_DIAGNOSTICS.items():
        severity = path_colour(path)
        attributes[key] = {
            "EFFECT_COLOR": severity,
            "EFFECT_TYPE": effect,
            "ERROR_STRIPE_COLOR": severity,
        }
    for key, path in JETBRAINS_STRIPES.items():
        attributes[key] = {"ERROR_STRIPE_COLOR": path_colour(path)}
    for key in JETBRAINS_INLAY_BUTTONS:
        attributes[key]["FOREGROUND"] = hint
    attributes |= {key: {} for key in JETBRAINS_CLEARED}
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
    for key, value in jetbrains_scrollbars(palette).items():
        ET.SubElement(colours, "option", name=key, value=colour(value))
    for index, accent in enumerate(ui["accents"][:VCS_ANNOTATION_SHADES], start=1):
        name = f"VCS_ANNOTATIONS_COLOR_{index}"
        ET.SubElement(colours, "option", name=name, value=tint(palette, accent)[1:])
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


def palette_card(palette: Palette) -> str:
    ui, ansi = palette["ui"], palette["ansi"]
    sections = [
        ("UI", [(key, ui[key]) for key in ("background", "foreground", "accent")]),
        ("Syntax", sorted(palette["syntax"].items())),
        (
            "ANSI",
            [
                (f"{prefix}{name}", colour)
                for shade, prefix in (("normal", ""), ("bright", "bright "))
                for name, colour in zip(ANSI_NAMES, ansi[shade], strict=True)
            ],
        ),
    ]
    svg = ET.Element("svg", xmlns="http://www.w3.org/2000/svg")

    def element(tag: str, text: str | None = None, **attributes: object) -> None:
        ET.SubElement(svg, tag, {k: str(v) for k, v in attributes.items()}).text = text

    element("title", f"{palette['name']} palette")
    element("rect", width="100%", height="100%", rx=12, fill=ui["background"])
    y = CARD_PADDING
    for heading, swatches in sections:
        element(
            "text",
            heading,
            x=CARD_PADDING,
            y=y + CARD_HEADING_BASELINE,
            fill=ui["muted"],
        )
        y += CARD_ROW_HEIGHT
        for index, (role, colour) in enumerate(swatches):
            row, column = divmod(index, CARD_COLUMNS)
            x = CARD_PADDING + column * CARD_CELL_WIDTH
            top = y + row * CARD_ROW_HEIGHT
            label_x = x + CARD_SWATCH + CARD_LABEL_GAP
            element(
                "rect",
                x=x,
                y=top,
                width=CARD_SWATCH,
                height=CARD_SWATCH,
                rx=6,
                fill=colour,
                stroke=ui["border"],
            )
            element(
                "text",
                role,
                x=label_x,
                y=top + CARD_ROLE_BASELINE,
                fill=ui["foreground"],
            )
            element(
                "text", colour, x=label_x, y=top + CARD_HEX_BASELINE, fill=ui["muted"]
            )
        y += math.ceil(len(swatches) / CARD_COLUMNS) * CARD_ROW_HEIGHT
    width = 2 * CARD_PADDING + CARD_COLUMNS * CARD_CELL_WIDTH
    height = y + CARD_PADDING
    svg.attrib |= {
        "width": str(width),
        "height": str(height),
        "viewBox": f"0 0 {width} {height}",
        "style": f"font-family: {CARD_FONT}; font-size: 13px",
    }
    return xml_text(svg)


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
    if failures := [f for p in palettes for f in contrast_failures(p)]:
        raise SystemExit("\n".join(failures))
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
        write(ROOT / "ghostty" / palette["name"], ghostty(palette))
        write_json(ROOT / "jetbrains" / f"{name}.theme.json", jetbrains_theme(palette))
        write(ROOT / "jetbrains" / f"{name}.xml", jetbrains_scheme(palette))
        write_json(ROOT / "vscode" / "themes" / f"{name}.json", vscode_theme(palette))
        write_json(ROOT / "xcode" / f"{name}.json", xcode_recipe(palette))
        write(
            ROOT / "docs" / f"palette-{palette['appearance']}.svg",
            palette_card(palette),
        )


if __name__ == "__main__":
    main()
