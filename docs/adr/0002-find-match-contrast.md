# Find match contrast

Geist Dark's find matches shared one translucent amber, `#f1a10d40`, which composites to `#3c2803` on the black background, where comments reach only 4.34:1, and the #12 audit measured the active match brighter still (Zed `#886e3c`, string 2.17:1; VS Code `#5d4924`, string 3.85:1). We decided that every syntax role reaches 4.5:1 on every find match, active or not, the same bar as the selection in ADR 0001. Geist Dark's matches become opaque, dark amber fills: `#1d1301` for the other matches (1.15:1 on the background) and a slightly brighter `#352303` for the active match. A fill bright enough to stand out from the selection can't keep comments at 4.5:1, so VS Code borders the active match in Geist's amber, `#f1a10d`, and the border is what sets it apart from the selection it nearly matches (1.00:1).

Geist Light keeps its look: every match is the opaque `#fce9bb` that its old `#ffb20040` composites to on the background, and the active match is bordered in `#ffb200`. The fills have to be opaque because VS Code paints its range highlight across the active match's line, and the translucent fill over that band fell to 4.27:1 for comments.

Opaque fills go against VS Code's advice for `editor.findMatchHighlightBackground`, which asks for a translucent colour so it doesn't hide the decorations beneath it. VS Code paints find decorations over the selection and word highlights, so while the find widget is open, a match inside a selection shows its find fill instead of the selection, and a word highlight under a match is hidden. We accept that: a translucent fill over the selection or a highlight would bring back the contrast shortfall this decision removes.

VS Code also paints its Search view's hits with `editor.findMatchHighlightBackground`, and Dark's `#1d1301` all but vanishes on the `#0a0a0a` sidebar (1.08:1). So Dark outlines the other matches in a translucent amber, `#f1a10d66`, which renders `#724c06` there; in the editor the active match's full `#f1a10d` border still sets it apart from the outlined others. Light's hits stand out on its white sidebar already, so its outline is transparent.

The palettes carry four keys: `find` for the other matches, `find_active` for the active match, `find_active_border` for its border and `find_border` for the other matches' outline. JetBrains reads `find` for its search results, where Dark's comments rise from 4.34:1 to 5.67:1, and `find_active_border` for their scrollbar stripe, which would otherwise turn near-black with the opaque fill.

| Syntax role | Dark before (`#3c2803`) | Dark other (`#1d1301`) | Dark active (`#352303`) | Light (`#fce9bb`) |
| --- | --- | --- | --- | --- |
| attribute | 9.31 | 12.16 | 10.00 | 7.50 |
| comment | 4.34 | 5.67 | 4.66 | 4.55 |
| comment_emphasized | 5.36 | 7.01 | 5.76 | 6.45 |
| constant | 6.58 | 8.59 | 7.07 | 5.28 |
| function | 5.66 | 7.40 | 6.09 | 5.24 |
| function_system | 8.08 | 10.56 | 8.69 | 7.35 |
| keyword | 4.85 | 6.33 | 5.21 | 5.50 |
| link | 8.08 | 10.56 | 8.69 | 7.35 |
| literal | 5.36 | 7.01 | 5.76 | 6.45 |
| namespace | 7.11 | 9.29 | 7.64 | 7.73 |
| number | 6.58 | 8.59 | 7.07 | 5.28 |
| plain | 11.98 | 15.65 | 12.88 | 12.22 |
| punctuation | 5.36 | 7.01 | 5.76 | 6.45 |
| regex | 5.35 | 6.99 | 5.75 | 5.93 |
| string | 6.29 | 8.21 | 6.76 | 5.12 |
| tag | 5.35 | 6.99 | 5.75 | 5.93 |
| type | 6.45 | 8.42 | 6.93 | 4.84 |
| type_parameter | 9.06 | 11.83 | 9.73 | 6.75 |
| type_system | 9.06 | 11.83 | 9.73 | 6.75 |
| variable | 11.98 | 15.65 | 12.88 | 12.22 |

We accept a shortfall on Zed's active match in Light. Zed selects the match it steps to and paints selections over search highlights, and while the search bar has focus it draws the selection at half of `selection_overlay`'s alpha. Measured on 2026-11-07, the active match renders `#3f3015` in Dark and `#f1e4c2` in Light. In Dark, Zed's minimum-contrast adjustment (`minimum_contrast_for_highlights`, at its default) lifts the text, so comments render `#a1a1a1` (4.94:1) and keywords `#bb92d8` (4.99:1). In Light, it leaves the text alone, so comments measure 4.32:1. Reaching 4.5:1 there would take a paler active fill that no longer reads as amber, or a fainter selection, which ADR 0001 settled.
