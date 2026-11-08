# Xcode line numbers

Every other target draws line numbers in `ui.quiet`, at 6.49:1 in Geist Dark and 5.27:1 in Geist Light, which meets the 4.5:1 bar for hint and inactive text. Xcode 27 can't follow. It computes line numbers from the recipe's palette (`sourceTextSidebarNumbersColor`) and never reads `colorOverrides` for them, so no recipe key reaches them. Measured in the README screenshots, they are about `#535353` on Geist Dark's background (2.73:1) and `#b4b4b4` on Geist Light's (2.00:1). We accept the shortfall, since only Xcode can change it.

Xcode computes the inactive selection and symbol highlight the same way. Both sit behind syntax text, and neither has been measured yet. `palette.secondaryIntensity` may move all three and is untested.
