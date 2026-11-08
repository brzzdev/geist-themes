# Tinted fills behind syntax text

Diff lines, breakpoints, the execution point, write-usage highlights, conflict markers and status fills all sit behind syntax text, so ADR 0001's bar applies to them: every syntax role reaches 4.5:1. Rather than add an opaque palette colour for each, every such fill is a status, accent or keyword colour composited over the background at one alpha per appearance, `33` in Geist Dark and `1a` in Geist Light (`TINT_ALPHAS` in `build.py`). Those are the strongest alphas at which every tint keeps comments, always the weakest role, at 4.5:1. Geist Light's comment is only 5.27:1 on its background, so its ceiling is about `1a` (deleted lines 4.52:1), while Geist Dark has room up to `3b`. One alpha per appearance keeps a single rule across targets, and `build.py` stops the build if a tint, or any other surface behind syntax text, drops a role below 4.5:1.

JetBrains' write-usage highlight used a fixed `33` keyword tint, which left Geist Light's comments at 3.86:1 on it, so it now takes the shared tint too.

The headroom rules out a second, brighter fill for the changed words inside a changed line. VS Code paints `diffEditor.insertedTextBackground` over `insertedLineBackground`, and two Light tints stacked drop comments to about 3.97:1, so VS Code's changed text gets no fill of its own and is bordered in the status colour instead. Zed has no border for word diffs, so its word fills equal its hunk fills, and changed words inside a hunk aren't singled out. We accept losing that emphasis rather than put text below the bar.

VS Code draws decorations over the selection, and asks for translucent fills so they don't hide it. Its diff lines, stack frames, word and hover highlights, linked edits and snippet tabstops therefore take the translucent colour at alpha `80` that composites over the background to the same opaque tint or highlight, which is what `build.py` checks. Over a selection, the blend of the two isn't held to 4.5:1, the same exception ADR 0001 makes for Zed's selection over a highlight. Find matches stay opaque, as ADR 0002 decided.

| Tint | Dark (`33`), weakest role | Light (`1a`), weakest role |
| --- | --- | --- |
| accent | `#102233` (comment 5.00) | `#e4ebf3` (comment 4.54) |
| keyword | `#261830` (comment 5.17) | `#eee7f3` (comment 4.51) |
| conflict, warning | `#302003` (comment 4.87) | `#efeae1` (comment 4.55) |
| created, success | `#142717` (comment 4.87) | `#e4ede6` (comment 4.56) |
| deleted, error | `#2e0e0f` (comment 5.48) | `#f7e6e6` (comment 4.52) |
| modified, info | `#102233` (comment 5.00) | `#e4ebf3` (comment 4.54) |
