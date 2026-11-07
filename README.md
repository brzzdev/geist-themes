# Geist Themes

Editor and terminal themes built from the colours of Vercel's [Geist terminal themes](https://vercel.com/geist/terminal), for Ghostty, Xcode 27 and Zed.

This is an unofficial project, not made or endorsed by Vercel. The colours belong to Vercel's Geist design system.

## Install

### Ghostty

Copy `ghostty/geist-dark` into `~/.config/ghostty/themes/`, then set `theme = geist-dark` in your Ghostty config.

### Xcode 27

Xcode 27 keeps themes in its settings rather than in `.xccolortheme` files. Quit Xcode, then run:

```sh
./install-xcode.py
```

Then pick **Geist Dark** in Xcode → Settings → Themes. Running it again updates the theme in place.

### Zed

Copy `zed/geist.json` into `~/.config/zed/themes/`, then pick **Geist Dark** with `cmd-k cmd-t`.

## Changing colours

Every theme is generated from `palettes/`. Edit a palette, then regenerate:

```sh
./build.py
```

Commit the palette and the generated files together. CI fails when they disagree.
