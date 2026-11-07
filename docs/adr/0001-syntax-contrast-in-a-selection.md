# Syntax contrast in a selection

Syntax colours are tuned for the editor background, so on the old selections 12 of 20 syntax roles fell below 4.5:1 in Geist Dark (`#454545`) and 2 in Geist Light (`#dce3ec`). We decided that every syntax role, comments included, reaches 4.5:1 on the selection in both themes, with no exemptions. We get there by moving the selection, not by setting a selection foreground: syntax colours stay inside a selection in every editor, the JetBrains and VS Code selection foregrounds stay unset, and Ghostty keeps its existing terminal selection foreground. Exempting comments in Geist Dark would have allowed only `#303030` instead of a darker selection, and that still collides with the whitespace marks. Keeping `#454545` and accepting the shortfall was rejected because it fails most of the syntax roles, not just comments.

Geist Dark's selection goes darker, to `#262626`, and its whitespace marks and indent guides go lighter, to `#454545`, so they sit above the selection (1.58:1 on it) instead of below it. `#262626` is off Geist's grey scale on purpose. `#1f1f1f`, the nearest scale step that passes, is almost identical to the inactive selection (`#1a1a1a`, 1.06:1), and `#282828` passes by only 4.56:1. Geist Light's selection lightens along its tint to `#e6ebf1`. As a result, its active and inactive selections differ only by tint, and indent guides inside a selection fade slightly further outside Zed (about 1.08:1 before, 1.01:1 now). Document highlights sit just below the selection in both themes: Geist Dark's moves to `#1f1f1f` (1.27:1 on the background, against the selection's 1.39:1) and Geist Light's to `#ebeef2` (1.12:1, against 1.16:1). Every syntax role reaches 4.5:1 on them too, with comments weakest at 5.10:1 in Dark and 4.69:1 in Light. Dark's highlight takes the `#1f1f1f` the selection turned down, which is safe because the inactive selection it nearly matches (`ui.element`) never shares a surface with it: JetBrains doesn't read `ui.highlight`, and VS Code's inactive selection from it is the list one, not the editor's. In Light, a highlight on the cursor line is barely distinct from it (1.04:1). The 4.5:1 bar covers the selection over the background, not over a document highlight: Zed blends its translucent selection over a highlight to `#3a3a3a` in Dark (comment 3.52:1) and `#dce3ec` in Light (type 4.49:1), though both are higher than over the old highlights.

| Syntax role | Dark before (`#454545`) | Dark after (`#262626`) | Light before (`#dce3ec`) | Light after (`#e6ebf1`) |
| --- | --- | --- | --- | --- |
| attribute | 6.36 | 10.04 | 6.95 | 7.50 |
| comment | 2.96 | 4.68 | 4.22 | 4.55 |
| comment_emphasized | 3.67 | 5.79 | 5.98 | 6.45 |
| constant | 4.49 | 7.09 | 4.90 | 5.28 |
| function | 3.87 | 6.11 | 4.86 | 5.25 |
| function_system | 5.53 | 8.72 | 6.81 | 7.35 |
| keyword | 3.31 | 5.23 | 5.10 | 5.50 |
| link | 5.53 | 8.72 | 6.81 | 7.35 |
| literal | 3.67 | 5.79 | 5.98 | 6.45 |
| namespace | 4.86 | 7.67 | 7.17 | 7.73 |
| number | 4.49 | 7.09 | 4.90 | 5.28 |
| plain | 8.19 | 12.93 | 11.33 | 12.22 |
| punctuation | 3.67 | 5.79 | 5.98 | 6.45 |
| regex | 3.66 | 5.77 | 5.50 | 5.93 |
| string | 4.30 | 6.78 | 4.75 | 5.13 |
| tag | 3.66 | 5.77 | 5.50 | 5.93 |
| type | 4.41 | 6.95 | 4.49 | 4.84 |
| type_parameter | 6.19 | 9.77 | 6.26 | 6.75 |
| type_system | 6.19 | 9.77 | 6.26 | 6.75 |
| variable | 8.19 | 12.93 | 11.33 | 12.22 |
