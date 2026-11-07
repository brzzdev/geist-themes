# Geist Themes

Editor and terminal themes built from the colours of Vercel's [Geist terminal themes](https://vercel.com/geist/terminal), for Ghostty, Xcode 27 and Zed. Each comes in Geist Dark and Geist Light.

This is an unofficial project, not made or endorsed by Vercel. The colours belong to Vercel's Geist design system.

## Install

### Ghostty

Copy `ghostty/geist-dark` and `ghostty/geist-light` into `~/.config/ghostty/themes/`, then set `theme = geist-dark` or `theme = geist-light` in your Ghostty config. To follow the system appearance, set `theme = light:geist-light,dark:geist-dark`.

### Xcode 27

Xcode 27 keeps themes in its settings rather than in `.xccolortheme` files. Quit Xcode, then run:

```sh
./install-xcode.py
```

Then pick **Geist Dark** or **Geist Light** in Xcode → Settings → Themes. Running it again updates the themes in place.

### Zed

Copy `zed/geist.json` into `~/.config/zed/themes/`, then pick **Geist Dark** or **Geist Light** with `cmd-k cmd-t`.

## Changing colours

Every theme is generated from `palettes/`. Edit a palette, then regenerate:

```sh
./build.py
```

Commit the palette and the generated files together. CI fails when they disagree.
