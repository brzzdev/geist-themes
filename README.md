# Geist Themes

Editor and terminal themes built from the colours of Vercel's [Geist terminal themes](https://vercel.com/geist/terminal), for Ghostty, herdr, JetBrains IDEs, NetNewsWire, VS Code, Xcode 27 and Zed. Each comes in Geist Dark and Geist Light.

This is an unofficial project, not made or endorsed by Vercel. The colours belong to Vercel's Geist design system.

## Install

### Ghostty

Copy `ghostty/geist-dark` and `ghostty/geist-light` into `~/.config/ghostty/themes/`, then set `theme = geist-dark` or `theme = geist-light` in your Ghostty config. To follow the system appearance, set `theme = light:geist-light,dark:geist-dark`.

### herdr

herdr can't load a separate theme file, so paste the contents of `herdr/geist.toml` into `~/.config/herdr/config.toml`, replacing the `[theme]` table and every `[theme.custom]`, `[theme.custom.dark]` and `[theme.custom.light]` table already there. Keep any other `[theme]` keys you want, such as `name`, under the pasted `[theme]` header. Then run:

```sh
herdr server reload-config
```

The snippet turns on `auto_switch`, so herdr uses Geist Dark or Geist Light to match the colour scheme your terminal reports. Ghostty reports dark only with a conditional theme, so in Ghostty set `theme = light:geist-light,dark:geist-dark` as in the [Ghostty](#ghostty) section: with a fixed `theme = geist-dark`, Ghostty reports light and herdr picks Geist Light. Picking a theme in herdr's settings turns `auto_switch` off, which leaves Geist Dark. The snippet sets every colour herdr themes, so it looks the same whichever base theme `theme.name` picks.

### JetBrains IDEs

For Rider, IntelliJ IDEA, WebStorm and the other JetBrains IDEs, 2026.1 or later. Download the `.jar` from the [latest release](https://github.com/brzzdev/geist-themes/releases/latest), or build it from the repository root, where it reports version `0.0.0-dev`:

```sh
python3 -m zipfile -c geist-themes.jar jetbrains/*
```

Then install the jar with Settings → Plugins → ⚙ → **Install Plugin from Disk…**, and pick **Geist Dark** or **Geist Light** under Appearance & Behavior → Appearance → Theme. Each theme switches the editor to its matching colour scheme.

### NetNewsWire

With NetNewsWire running, open `netnewswire/Geist.nnwtheme` with it and accept the install prompt. If NetNewsWire isn't running, opening the file launches it without the prompt, so open the file again once it's up. Then pick **Geist** in NetNewsWire → Settings → General → Article Theme. The article view follows the system appearance between Geist Dark and Geist Light.

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

Then open Xcode → Settings → Appearance → Theme → **Choose…**, which keeps a separate list for each appearance, and pick **Geist Light** for the light appearance and **Geist Dark** for the dark one. Running it again updates the themes in place.

### Zed

Copy `zed/geist.json` into `~/.config/zed/themes/`, then pick **Geist Dark** or **Geist Light** with `cmd-k cmd-t`.

## Changing colours

Every theme is generated from `palettes/`. Edit a palette, then regenerate:

```sh
./build.py
```

Commit the palette and the generated files together. CI fails when they disagree.
