# Geist Themes

Editor and terminal themes built from the colours of Vercel's [Geist terminal themes](https://vercel.com/geist/terminal), for Ghostty, herdr, NetNewsWire, VS Code, Xcode 27 and Zed. Each comes in Geist Dark and Geist Light.

This is an unofficial project, not made or endorsed by Vercel. The colours belong to Vercel's Geist design system.

## Install

### Ghostty

Copy `ghostty/geist-dark` and `ghostty/geist-light` into `~/.config/ghostty/themes/`, then set `theme = geist-dark` or `theme = geist-light` in your Ghostty config. To follow the system appearance, set `theme = light:geist-light,dark:geist-dark`.

### herdr

herdr can't load a separate theme file, so paste the contents of `herdr/geist.toml` into `~/.config/herdr/config.toml`, replacing the `[theme]` table and every `[theme.custom]`, `[theme.custom.dark]` and `[theme.custom.light]` table already there. Keep any other `[theme]` keys you want, such as `name`, under the pasted `[theme]` header. Then run:

```sh
herdr server reload-config
```

The snippet turns on `auto_switch`, so herdr uses Geist Dark or Geist Light to match your terminal's appearance. Picking a theme in herdr's settings turns `auto_switch` off, which leaves Geist Dark. The snippet sets every colour herdr themes, so it looks the same whichever base theme `theme.name` picks.

### NetNewsWire

Open `netnewswire/Geist.nnwtheme` with NetNewsWire, then pick **Geist** in NetNewsWire → Settings → General → Article Theme. The article view follows the system appearance between Geist Dark and Geist Light.

### VS Code

Package the extension with Node installed:

```sh
cd vscode && npx --yes @vscode/vsce package -o geist-themes.vsix
```

In VS Code (or a fork such as Cursor), run **Extensions: Install from VSIX…** and pick `vscode/geist-themes.vsix`, then choose **Geist Dark** or **Geist Light** with **Preferences: Color Theme**.

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
