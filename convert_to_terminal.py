#!/usr/bin/env python3
"""Convert VS Code themes to terminal emulator color schemes.

Supported formats:
  - Alacritty (TOML)
  - Kitty (conf)
  - Windows Terminal (JSON)
  - iTerm2 (XML plist / .itermcolors)
  - Xresources
  - Foot (INI)
  - WezTerm (TOML)
  - GNOME Terminal / Tilix (dconf)
"""

import json
import os
import xml.etree.ElementTree as ET
from pathlib import Path


def hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    """Convert #RRGGBB to (R, G, B) tuple."""
    h = hex_color.lstrip('#')[:6]
    return (int(h[0:2], 16), int(h[1:4][:2], 16), int(h[4:6], 16))


def hex_to_rgb_proper(hex_color: str) -> tuple[int, int, int]:
    h = hex_color.lstrip('#')[:6]
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


def hex_to_rgb_float(hex_color: str) -> tuple[float, float, float]:
    r, g, b = hex_to_rgb_proper(hex_color)
    return (r / 255.0, g / 255.0, b / 255.0)


def hex_to_0x(hex_color: str) -> str:
    """Convert #RRGGBB to 0xRRGGBB."""
    return '0x' + hex_color.lstrip('#')[:6]


def extract_terminal_colors(theme: dict) -> dict | None:
    """Extract terminal colors from a VS Code theme."""
    colors = theme.get('colors', {})

    required = ['terminal.background', 'terminal.foreground', 'terminal.ansiBlack']
    if not all(k in colors for k in required):
        return None

    return {
        'background': colors.get('terminal.background', colors.get('editor.background', '#000000')),
        'foreground': colors.get('terminal.foreground', colors.get('editor.foreground', '#ffffff')),
        'cursor': colors.get('terminalCursor.foreground', colors.get('editorCursor.foreground',
                  colors.get('terminal.foreground', '#ffffff'))),
        'selection': colors.get('terminal.selectionBackground',
                    colors.get('editor.selectionBackground', '#264f78')),
        'normal': {
            'black':   colors.get('terminal.ansiBlack', '#000000'),
            'red':     colors.get('terminal.ansiRed', '#cd3131'),
            'green':   colors.get('terminal.ansiGreen', '#0dbc79'),
            'yellow':  colors.get('terminal.ansiYellow', '#e5e510'),
            'blue':    colors.get('terminal.ansiBlue', '#2472c8'),
            'magenta': colors.get('terminal.ansiMagenta', '#bc3fbc'),
            'cyan':    colors.get('terminal.ansiCyan', '#11a8cd'),
            'white':   colors.get('terminal.ansiWhite', '#e5e5e5'),
        },
        'bright': {
            'black':   colors.get('terminal.ansiBrightBlack', '#666666'),
            'red':     colors.get('terminal.ansiBrightRed', '#f14c4c'),
            'green':   colors.get('terminal.ansiBrightGreen', '#23d18b'),
            'yellow':  colors.get('terminal.ansiBrightYellow', '#f5f543'),
            'blue':    colors.get('terminal.ansiBrightBlue', '#3b8eea'),
            'magenta': colors.get('terminal.ansiBrightMagenta', '#d670d6'),
            'cyan':    colors.get('terminal.ansiBrightCyan', '#29b8db'),
            'white':   colors.get('terminal.ansiBrightWhite', '#ffffff'),
        },
    }


# --- Generators ---

def gen_alacritty(name: str, tc: dict) -> str:
    """Generate Alacritty TOML color scheme."""
    lines = [f'# {name} - Castor & Pollux Theme Collection', '']
    lines.append('[colors.primary]')
    lines.append(f'background = "{tc["background"]}"')
    lines.append(f'foreground = "{tc["foreground"]}"')
    lines.append('')
    lines.append('[colors.cursor]')
    lines.append(f'text = "{tc["background"]}"')
    lines.append(f'cursor = "{tc["cursor"]}"')
    lines.append('')
    lines.append('[colors.selection]')
    lines.append(f'text = CellForeground')
    lines.append(f'background = "{tc["selection"]}"')
    lines.append('')
    lines.append('[colors.normal]')
    for color_name, value in tc['normal'].items():
        lines.append(f'{color_name} = "{value}"')
    lines.append('')
    lines.append('[colors.bright]')
    for color_name, value in tc['bright'].items():
        lines.append(f'{color_name} = "{value}"')
    lines.append('')
    return '\n'.join(lines)


def gen_kitty(name: str, tc: dict) -> str:
    """Generate Kitty terminal conf."""
    lines = [f'# {name} - Castor & Pollux Theme Collection', '']
    lines.append(f'background {tc["background"]}')
    lines.append(f'foreground {tc["foreground"]}')
    lines.append(f'cursor {tc["cursor"]}')
    lines.append(f'selection_background {tc["selection"]}')
    lines.append(f'selection_foreground {tc["background"]}')
    lines.append('')

    color_order = ['black', 'red', 'green', 'yellow', 'blue', 'magenta', 'cyan', 'white']
    for i, c in enumerate(color_order):
        lines.append(f'color{i} {tc["normal"][c]}')
    for i, c in enumerate(color_order):
        lines.append(f'color{i + 8} {tc["bright"][c]}')
    lines.append('')
    return '\n'.join(lines)


def gen_windows_terminal(name: str, tc: dict) -> dict:
    """Generate Windows Terminal JSON scheme."""
    return {
        'name': name,
        'background': tc['background'],
        'foreground': tc['foreground'],
        'cursorColor': tc['cursor'],
        'selectionBackground': tc['selection'],
        'black': tc['normal']['black'],
        'red': tc['normal']['red'],
        'green': tc['normal']['green'],
        'yellow': tc['normal']['yellow'],
        'blue': tc['normal']['blue'],
        'purple': tc['normal']['magenta'],
        'cyan': tc['normal']['cyan'],
        'white': tc['normal']['white'],
        'brightBlack': tc['bright']['black'],
        'brightRed': tc['bright']['red'],
        'brightGreen': tc['bright']['green'],
        'brightYellow': tc['bright']['yellow'],
        'brightBlue': tc['bright']['blue'],
        'brightPurple': tc['bright']['magenta'],
        'brightCyan': tc['bright']['cyan'],
        'brightWhite': tc['bright']['white'],
    }


def gen_iterm2(name: str, tc: dict) -> str:
    """Generate iTerm2 .itermcolors XML plist."""
    def color_dict(hex_color: str) -> str:
        r, g, b = hex_to_rgb_float(hex_color)
        return f'''	<dict>
		<key>Alpha Component</key>
		<real>1</real>
		<key>Blue Component</key>
		<real>{b:.6f}</real>
		<key>Color Space</key>
		<string>sRGB</string>
		<key>Green Component</key>
		<real>{g:.6f}</real>
		<key>Red Component</key>
		<real>{r:.6f}</real>
	</dict>'''

    color_order = ['black', 'red', 'green', 'yellow', 'blue', 'magenta', 'cyan', 'white']
    entries = []

    for i, c in enumerate(color_order):
        entries.append(f'	<key>Ansi {i} Color</key>')
        entries.append(color_dict(tc['normal'][c]))

    for i, c in enumerate(color_order):
        entries.append(f'	<key>Ansi {i + 8} Color</key>')
        entries.append(color_dict(tc['bright'][c]))

    entries.append('	<key>Background Color</key>')
    entries.append(color_dict(tc['background']))
    entries.append('	<key>Foreground Color</key>')
    entries.append(color_dict(tc['foreground']))
    entries.append('	<key>Cursor Color</key>')
    entries.append(color_dict(tc['cursor']))
    entries.append('	<key>Cursor Text Color</key>')
    entries.append(color_dict(tc['background']))
    entries.append('	<key>Selection Color</key>')
    entries.append(color_dict(tc['selection']))
    entries.append('	<key>Selected Text Color</key>')
    entries.append(color_dict(tc['foreground']))
    entries.append('	<key>Bold Color</key>')
    entries.append(color_dict(tc['foreground']))

    return f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
{chr(10).join(entries)}
</dict>
</plist>
'''


def gen_xresources(name: str, tc: dict) -> str:
    """Generate Xresources format."""
    lines = [f'! {name} - Castor & Pollux Theme Collection', '']
    lines.append(f'*.background: {tc["background"]}')
    lines.append(f'*.foreground: {tc["foreground"]}')
    lines.append(f'*.cursorColor: {tc["cursor"]}')
    lines.append('')

    color_order = ['black', 'red', 'green', 'yellow', 'blue', 'magenta', 'cyan', 'white']
    for i, c in enumerate(color_order):
        lines.append(f'*.color{i}: {tc["normal"][c]}')
    for i, c in enumerate(color_order):
        lines.append(f'*.color{i + 8}: {tc["bright"][c]}')
    lines.append('')
    return '\n'.join(lines)


def gen_foot(name: str, tc: dict) -> str:
    """Generate Foot terminal INI config."""
    def strip_hash(h: str) -> str:
        return h.lstrip('#')[:6]

    lines = [f'# {name} - Castor & Pollux Theme Collection', '']
    lines.append('[cursor]')
    lines.append(f'color = {strip_hash(tc["background"])} {strip_hash(tc["cursor"])}')
    lines.append('')
    lines.append('[colors]')
    lines.append(f'background = {strip_hash(tc["background"])}')
    lines.append(f'foreground = {strip_hash(tc["foreground"])}')
    lines.append(f'selection-foreground = {strip_hash(tc["foreground"])}')
    lines.append(f'selection-background = {strip_hash(tc["selection"])}')
    lines.append('')

    color_order = ['black', 'red', 'green', 'yellow', 'blue', 'magenta', 'cyan', 'white']
    lines.append('## Normal/regular colors (color palette 0-7)')
    for i, c in enumerate(color_order):
        lines.append(f'regular{i} = {strip_hash(tc["normal"][c])}')
    lines.append('')
    lines.append('## Bright colors (color palette 8-15)')
    for i, c in enumerate(color_order):
        lines.append(f'bright{i} = {strip_hash(tc["bright"][c])}')
    lines.append('')
    return '\n'.join(lines)


def gen_wezterm(name: str, tc: dict) -> str:
    """Generate WezTerm TOML color scheme."""
    lines = [f'# {name} - Castor & Pollux Theme Collection', '']
    lines.append(f'[metadata]')
    lines.append(f'name = "{name}"')
    lines.append(f'origin_url = "https://github.com/yourusername/castor-pollux-theme"')
    lines.append('')
    lines.append(f'[colors]')
    lines.append(f'background = "{tc["background"]}"')
    lines.append(f'foreground = "{tc["foreground"]}"')
    lines.append(f'cursor_bg = "{tc["cursor"]}"')
    lines.append(f'cursor_fg = "{tc["background"]}"')
    lines.append(f'cursor_border = "{tc["cursor"]}"')
    lines.append(f'selection_bg = "{tc["selection"]}"')
    lines.append(f'selection_fg = "{tc["foreground"]}"')
    lines.append('')
    lines.append(f'[colors.ansi]')
    color_order = ['black', 'red', 'green', 'yellow', 'blue', 'magenta', 'cyan', 'white']
    ansi = [tc['normal'][c] for c in color_order]
    lines.append(f'ansi = {json.dumps(ansi)}')
    brights = [tc['bright'][c] for c in color_order]
    lines.append(f'brights = {json.dumps(brights)}')
    lines.append('')
    return '\n'.join(lines)


def gen_gnome_tilix(name: str, tc: dict) -> str:
    """Generate GNOME Terminal / Tilix dconf dump."""
    color_order = ['black', 'red', 'green', 'yellow', 'blue', 'magenta', 'cyan', 'white']
    palette = []
    for c in color_order:
        palette.append(f"'{tc['normal'][c]}'")
    for c in color_order:
        palette.append(f"'{tc['bright'][c]}'")

    lines = [f'# {name} - Castor & Pollux Theme Collection']
    lines.append(f'# Apply with: dconf load /org/gnome/terminal/legacy/profiles:/:PROFILE_ID/ < this_file')
    lines.append('')
    lines.append(f"[/]")
    lines.append(f"visible-name='{name}'")
    lines.append(f"background-color='{tc['background']}'")
    lines.append(f"foreground-color='{tc['foreground']}'")
    lines.append(f"cursor-background-color='{tc['cursor']}'")
    lines.append(f"cursor-foreground-color='{tc['background']}'")
    lines.append(f"highlight-background-color='{tc['selection']}'")
    lines.append(f"highlight-foreground-color='{tc['foreground']}'")
    lines.append(f"use-theme-colors=false")
    lines.append(f"bold-is-bright=true")
    lines.append(f"palette=[{', '.join(palette)}]")
    lines.append('')
    return '\n'.join(lines)


def gen_ptyxis(name: str, tc: dict) -> str:
    """Generate Ptyxis .palette file."""
    color_order = ['black', 'red', 'green', 'yellow', 'blue', 'magenta', 'cyan', 'white']
    lines = [f'[Palette]']
    lines.append(f'Name={name}')
    lines.append(f'Background={tc["background"]}')
    lines.append(f'Foreground={tc["foreground"]}')
    lines.append(f'Cursor={tc["cursor"]}')
    for i, c in enumerate(color_order):
        lines.append(f'Color{i}={tc["normal"][c]}')
    for i, c in enumerate(color_order):
        lines.append(f'Color{i + 8}={tc["bright"][c]}')
    lines.append('')
    return '\n'.join(lines)


# --- Format registry ---

FORMATS = {
    'alacritty':         {'ext': '.toml',        'gen': gen_alacritty,         'subdir': 'alacritty'},
    'kitty':             {'ext': '.conf',         'gen': gen_kitty,             'subdir': 'kitty'},
    'windows-terminal':  {'ext': '.json',         'gen': gen_windows_terminal,  'subdir': 'windows-terminal'},
    'iterm2':            {'ext': '.itermcolors',  'gen': gen_iterm2,            'subdir': 'iterm2'},
    'xresources':        {'ext': '.Xresources',  'gen': gen_xresources,        'subdir': 'xresources'},
    'foot':              {'ext': '.ini',          'gen': gen_foot,              'subdir': 'foot'},
    'wezterm':           {'ext': '.toml',         'gen': gen_wezterm,           'subdir': 'wezterm'},
    'gnome-terminal':    {'ext': '.dconf',        'gen': gen_gnome_tilix,       'subdir': 'gnome-terminal'},
    'ptyxis':            {'ext': '.palette',      'gen': gen_ptyxis,            'subdir': 'ptyxis'},
}


def slugify(name: str) -> str:
    """Convert theme name to filename slug."""
    return name.lower().replace(' ', '-').replace('&', 'and').replace("'", '')


def main():
    themes_dir = Path('/home/astomodynamics/github/castor-pollux-theme/themes')
    output_base = Path('/home/astomodynamics/github/castor-pollux-theme/terminal')

    # Read package.json for labels
    package_path = Path('/home/astomodynamics/github/castor-pollux-theme/package.json')
    with open(package_path) as f:
        package = json.load(f)

    theme_labels = {}
    for t in package['contributes']['themes']:
        path = Path(t['path']).name
        theme_labels[path] = t['label']

    # Track stats
    stats = {fmt: 0 for fmt in FORMATS}
    skipped = []

    # Windows Terminal collects all schemes into one file
    wt_schemes = []

    for theme_file in sorted(themes_dir.glob('*.json')):
        with open(theme_file) as f:
            vscode_theme = json.load(f)

        name = theme_labels.get(theme_file.name, vscode_theme.get('name', theme_file.stem))
        tc = extract_terminal_colors(vscode_theme)

        if not tc:
            skipped.append(theme_file.name)
            continue

        slug = slugify(name)

        for fmt_key, fmt_info in FORMATS.items():
            out_dir = output_base / fmt_info['subdir']
            out_dir.mkdir(parents=True, exist_ok=True)

            content = fmt_info['gen'](name, tc)

            if fmt_key == 'windows-terminal':
                wt_schemes.append(content)
                # Write individual scheme file
                out_file = out_dir / (slug + fmt_info['ext'])
                with open(out_file, 'w') as f:
                    json.dump(content, f, indent=2)
                stats[fmt_key] += 1
                continue

            out_file = out_dir / (slug + fmt_info['ext'])
            with open(out_file, 'w') as f:
                f.write(content)
            stats[fmt_key] += 1

    # Write combined Windows Terminal file (all schemes in one)
    if wt_schemes:
        wt_dir = output_base / 'windows-terminal'
        wt_dir.mkdir(parents=True, exist_ok=True)
        wt_file = wt_dir / 'castor-pollux-all-schemes.json'
        with open(wt_file, 'w') as f:
            json.dump({'schemes': wt_schemes}, f, indent=2)

    # Print summary
    print('Castor & Pollux Terminal Theme Converter')
    print('=' * 45)
    print()
    for fmt_key, count in stats.items():
        print(f'  {fmt_key:20s}  {count} themes')
    print()
    print(f'Output: {output_base}')

    if skipped:
        print(f'\nSkipped (no terminal colors): {", ".join(skipped)}')


if __name__ == '__main__':
    main()
