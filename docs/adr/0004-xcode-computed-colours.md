# Xcode's computed colours

Every other target draws line numbers in `ui.quiet`, at 6.49:1 in Geist Dark and 5.27:1 in Geist Light, which meets the 4.5:1 bar for hint and inactive text. Xcode 27 can't follow. It computes line numbers from the recipe's palette (`sourceTextSidebarNumbersColor`) and never reads `colorOverrides` for them, so no recipe key reaches them. It computes the inactive selection and the symbol highlight the same way (`sourceTextInactiveSelectionColor`, which the symbol highlight reuses), and both sit behind syntax text.

Measured on 2026-11-08 in Xcode 27.2, in a fresh macOS 27.2 VM:

| Surface | Geist Dark | Geist Light |
| --- | --- | --- |
| Line numbers on the background | `#535353`, 2.73:1 | `#b0b1b3`, 2.07:1 |
| Inactive selection and symbol highlight | `#1e1e1e`, every syntax role 5.15:1 or more | `#e2e1e1`, comment 4.18:1, type 4.44:1, the rest 4.71:1 or more |

We accept these shortfalls, since only Xcode can change them. The Light symbol highlight covers identifiers, so in practice only type names fall short there, by a little. The inactive selection can cover comments. The other surfaces Xcode computes haven't been measured: the gutter edge, dividers, quaternary and quinary fills, the accent, and inline code in Markdown, which is text. `palette.secondaryIntensity` may move all of them and is untested.
