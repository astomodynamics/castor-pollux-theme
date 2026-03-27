# Castor & Pollux Theme Collection

A collection of 47 premium themes for VS Code and Cursor, inspired by the twin stars of the Gemini constellation. Deep navy backgrounds, celestial color palettes, and carefully tuned contrast for long coding sessions, plus companion exports for terminal emulators and Zed.

## Themes (47 total)

### Navy & Gold (NEW)

Hand-crafted navy/blue themes with golden yellow highlights, semantic highlighting, and bracket pair colorization.

| Theme | Background | Accent | Vibe |
|-------|-----------|--------|------|
| **Castor Admiralty** | `#0a1225` Deep navy | `#e8b931` Warm gold | Naval officer, teal-blue functions |
| **Pollux Sovereign** | `#060c1f` Near-black navy | `#ffb627` Electric amber | High contrast, dramatic |
| **Castor Gilded Navy** | `#08101e` Rich navy | `#d4a528` Antique gold | Refined, Nord-inspired strings |

### School Spirit

| Theme | Background | Accent | Vibe |
|-------|-----------|--------|------|
| **Castor Georgia Tech** | `#001528` GT Navy | `#B3A369` Tech Gold | Official GT colors, teal functions |

### Earth & Patina (NEW)

| Theme | Background | Accent | Vibe |
|-------|-----------|--------|------|
| **Castor Verdant** | `#0b1411` Moss green | `#3fb87c` Fresh jade | Botanical, calm, high-legibility green |
| **Castor Kyoto** | `#161311` Charcoal brown | `#c78f55` Cedar amber | Warm Japanese ink and paper tones |
| **Pollux Dune** | `#1a1610` Sandstone dusk | `#c87850` Desert copper | Dry earth palette with soft sage support |
| **Castor Oxblood** | `#160d10` Deep oxblood | `#c85a78` Dusty rose | Dramatic wine-red contrast without neon glare |
| **Pollux Patina** | `#0f1718` Oxidized teal | `#5bb7ad` Sea-glass patina | Muted teal metals with cool terminal contrast |
| **Castor Bourbon** | `#17110d` Barrel brown | `#d08a42` Whiskey amber | Toasted oak, tobacco, and honey warmth |

### Celestial Blues

| Theme | Background | Style |
|-------|-----------|-------|
| **Castor Navy Dark** | `#050d18` | Deep navy, constellation blue + cosmic purple |
| **Pollux Cosmic Dark** | `#0d1117` | Deep space, vibrant constellation colors |
| **Castor Midnight** | `#0a0e1a` | Midnight blue, rich contrast |
| **Castor Deep Ocean** | Deep ocean | Celestial sea blues |
| **Castor Arctic** | Arctic | Cool blues, crisp whites |
| **Castor Azure** | Azure | Bright sky aesthetics |
| **Castor Cerulean** | Cerulean | Warm cerulean tones |
| **Pollux Sapphire** | Sapphire | Rich sapphire blues |
| **Pollux Indigo** | Indigo | Deep indigo, purple undertones |
| **Pollux Glacier** | Glacier | Icy blue, frozen palette |

### Dark & Dramatic

| Theme | Style |
|-------|-------|
| **Castor Eclipse** | Dramatic eclipse colors |
| **Castor Twilight** | Dusky twilight gradients |
| **Castor Cobalt** | Bold cobalt blue |
| **Pollux Nebula** | Cosmic purples and blues |
| **Pollux Solar** | Solar warmth, golden accents |
| **Pollux Steel** | Industrial steel tones |
| **Pollux Aurora** | Northern lights palette |

### Deep Navy (Zenn-inspired)

| Theme | Style |
|-------|-------|
| **Castor Zenn Dark** | Zenn-inspired deep navy |
| **Pollux Obsidian** | Obsidian black-navy |
| **Castor Slate** | Slate gray-navy |
| **Pollux Abyss** | Abyssal dark blue |
| **Castor Carbon** | Carbon-dark base |

### Navy & Blue Series

| Theme | Style |
|-------|-------|
| **Castor Prussian** | Prussian blue base |
| **Pollux Mariana** | Mariana trench depths |
| **Castor Ink** | Ink-dark navy |
| **Pollux Baltic** | Baltic sea tones |
| **Castor Storm** | Stormy blue-gray |

### Warm & Vibrant

| Theme | Style |
|-------|-------|
| **Castor Ember** | Warm ember and fire tones |
| **Castor Amethyst** | Purple amethyst crystal |
| **Castor Crimson** | Deep crimson reds |
| **Pollux Forest** | Forest green depths |
| **Pollux Copper** | Warm copper metallic |

### Light Themes

| Theme | Style |
|-------|-------|
| **Material Light** | Clean Material Design colors |
| **Aurora Light** | Soft, soothing daytime palette |
| **Pollux CLI Light** | Professional terminal-inspired light |

### Classic

| Theme | Style |
|-------|-------|
| **Nocturne Dark** | Deep blue + pastel accents, nighttime coding |
| **Castor CLI Dark** | Vibrant terminal-inspired dark |

## Installation

### Cursor

```bash
cp -r castor-pollux-theme ~/.cursor/extensions/
```

### VS Code

```bash
cp -r castor-pollux-theme ~/.vscode/extensions/
```

Then reload and select your theme:

1. `Ctrl+Shift+P` (or `Cmd+Shift+P` on macOS)
2. "Developer: Reload Window"
3. `Ctrl+Shift+P` -> "Preferences: Color Theme"
4. Pick any Castor or Pollux theme

## Companion Exports

The repo also includes companion exports for terminal emulators under [`terminal/`](terminal/).

- Alacritty
- Kitty
- Windows Terminal
- iTerm2
- Xresources
- Foot
- WezTerm
- GNOME Terminal / Tilix
- Ptyxis

For Zed, the helper script builds a single theme family file at `~/.config/zed/themes/castor-pollux.json`.

## Regenerating Exports

Run the conversion helpers from the repository root with Python 3:

```bash
python3 convert_to_terminal.py
python3 convert_to_zed.py
```

`convert_to_terminal.py` regenerates the committed files in [`terminal/`](terminal/). `convert_to_zed.py` writes the Zed theme family into your local Zed themes directory.

## Features

- 47 themes: 44 dark, 3 light
- Semantic highlighting and semantic token colors (Navy & Gold series)
- Bracket pair colorization with distinct colors
- Minimap, command center, and modern UI element styling
- Comprehensive token scopes: decorators, template strings, CSS pseudo-classes, JSON properties, escape characters
- Italic keywords and control flow for visual scanning
- Consistent git decoration, diff, and error/warning colors
- Companion terminal palettes across 9 terminal formats
- Zed theme family generation via `convert_to_zed.py`
- Designed for TypeScript, Python, Rust, Go, CSS, HTML, Markdown, and more

## About

Named after the twin stars of the Gemini constellation. Castor and Pollux represent the Dioscuri of Greek mythology - duality and harmony, dark and light.

## License

MIT
