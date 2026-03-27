#!/usr/bin/env python3
"""Convert VS Code themes to Zed editor format."""

import json
import os
import re
from pathlib import Path


def normalize_color(color: str) -> str:
    """Normalize color to 8-digit hex format (RRGGBBAA)."""
    if not color:
        return None

    color = color.strip()
    if not color.startswith('#'):
        return None

    # Remove #
    hex_color = color[1:]

    # Handle different formats
    if len(hex_color) == 3:  # #RGB -> #RRGGBBFF
        hex_color = ''.join([c*2 for c in hex_color]) + 'ff'
    elif len(hex_color) == 4:  # #RGBA -> #RRGGBBAA
        hex_color = ''.join([c*2 for c in hex_color[:3]]) + hex_color[3]*2
    elif len(hex_color) == 6:  # #RRGGBB -> #RRGGBBFF
        hex_color = hex_color + 'ff'
    elif len(hex_color) == 8:  # Already #RRGGBBAA
        pass
    else:
        return None

    return '#' + hex_color.lower()


def get_vscode_color(colors: dict, key: str, default: str = None) -> str:
    """Get a VS Code color and normalize it."""
    color = colors.get(key)
    if color:
        return normalize_color(color)
    return normalize_color(default) if default else None


def convert_token_colors(token_colors: list) -> dict:
    """Convert VS Code tokenColors to Zed syntax highlighting."""
    syntax = {}

    # Mapping from VS Code scopes to Zed syntax keys
    scope_mapping = {
        'comment': 'comment',
        'punctuation.definition.comment': 'comment',
        'string': 'string',
        'string.quoted': 'string',
        'string.regexp': 'string.regex',
        'constant.numeric': 'number',
        'constant.language': 'constant',
        'constant.character': 'constant',
        'constant.other': 'constant',
        'variable': 'variable',
        'variable.other': 'variable',
        'variable.language': 'variable.special',
        'variable.parameter': 'function.parameter',
        'keyword': 'keyword',
        'storage.type': 'keyword',
        'storage.modifier': 'keyword',
        'keyword.control': 'keyword',
        'keyword.operator': 'operator',
        'entity.name.function': 'function',
        'meta.function-call': 'function',
        'support.function': 'function',
        'entity.name.type': 'type',
        'entity.name.class': 'type',
        'support.type': 'type',
        'support.class': 'type',
        'entity.other.inherited-class': 'type',
        'entity.other.attribute-name': 'attribute',
        'entity.name.tag': 'tag',
        'punctuation.definition.tag': 'punctuation.bracket',
        'markup.heading': 'title',
        'markup.italic': 'emphasis',
        'markup.bold': 'emphasis.strong',
        'markup.inline.raw': 'text.literal',
        'markup.fenced_code': 'text.literal',
        'markup.underline.link': 'link_uri',
        'markup.list': 'punctuation.list_marker',
        'markup.quote': 'comment.doc',
        'support.variable': 'variable',
        'support.constant': 'constant',
        'invalid': 'hint',
        'invalid.deprecated': 'hint',
        'meta.diff': 'comment',
        'meta.diff.header': 'comment',
        'markup.inserted': 'string',
        'markup.deleted': 'emphasis',
        'markup.changed': 'keyword',
        'punctuation.section.embedded': 'embedded',
        'meta.import': 'keyword',
        'meta.export': 'keyword',
        'punctuation': 'punctuation',
        'punctuation.bracket': 'punctuation.bracket',
        'punctuation.delimiter': 'punctuation.delimiter',
    }

    for token in token_colors:
        scopes = token.get('scope', [])
        if isinstance(scopes, str):
            scopes = [s.strip() for s in scopes.split(',')]

        settings = token.get('settings', {})
        color = settings.get('foreground')
        font_style = settings.get('fontStyle', '')

        for scope in scopes:
            scope = scope.strip()
            zed_key = scope_mapping.get(scope)

            if zed_key and zed_key not in syntax:
                style = {}
                if color:
                    style['color'] = normalize_color(color)
                if 'italic' in font_style:
                    style['font_style'] = 'italic'
                if 'bold' in font_style:
                    style['font_weight'] = 700

                if style:
                    syntax[zed_key] = style

    return syntax


def convert_theme(vscode_theme: dict, theme_name: str) -> dict:
    """Convert a single VS Code theme to Zed format."""
    colors = vscode_theme.get('colors', {})
    token_colors = vscode_theme.get('tokenColors', [])
    theme_type = vscode_theme.get('type', 'dark')

    # Core colors
    bg = get_vscode_color(colors, 'editor.background', '#1e1e1e')
    fg = get_vscode_color(colors, 'editor.foreground', '#d4d4d4')
    sidebar_bg = get_vscode_color(colors, 'sideBar.background', bg)
    panel_bg = get_vscode_color(colors, 'panel.background', bg)

    # Accent colors
    accent = get_vscode_color(colors, 'activityBarBadge.background') or \
             get_vscode_color(colors, 'button.background') or \
             get_vscode_color(colors, 'tab.activeBorder', '#007acc')

    # Border colors
    border = get_vscode_color(colors, 'sideBar.border') or \
             get_vscode_color(colors, 'panel.border') or \
             get_vscode_color(colors, 'editorGroup.border', '#444444')

    # Selection and highlight colors
    selection = get_vscode_color(colors, 'editor.selectionBackground', '#264f78')
    line_highlight = get_vscode_color(colors, 'editor.lineHighlightBackground', '#2a2a2a')

    # Status colors
    error = get_vscode_color(colors, 'editorError.foreground', '#f44747')
    warning = get_vscode_color(colors, 'editorWarning.foreground', '#cca700')
    info = get_vscode_color(colors, 'editorInfo.foreground', '#3794ff')
    hint = get_vscode_color(colors, 'editorHint.foreground', '#75beff')

    # Git colors
    added = get_vscode_color(colors, 'editorGutter.addedBackground') or \
            get_vscode_color(colors, 'gitDecoration.untrackedResourceForeground', '#81b88b')
    modified = get_vscode_color(colors, 'editorGutter.modifiedBackground') or \
               get_vscode_color(colors, 'gitDecoration.modifiedResourceForeground', '#e2c08d')
    deleted = get_vscode_color(colors, 'editorGutter.deletedBackground') or \
              get_vscode_color(colors, 'gitDecoration.deletedResourceForeground', '#c74e39')

    # Tab colors
    tab_bar_bg = get_vscode_color(colors, 'editorGroupHeader.tabsBackground', sidebar_bg)
    tab_active_bg = get_vscode_color(colors, 'tab.activeBackground', bg)
    tab_inactive_bg = get_vscode_color(colors, 'tab.inactiveBackground', sidebar_bg)

    # Input colors
    input_bg = get_vscode_color(colors, 'input.background', '#3c3c3c')

    # Scrollbar
    scrollbar_thumb = get_vscode_color(colors, 'scrollbarSlider.background', '#79797966')
    scrollbar_thumb_hover = get_vscode_color(colors, 'scrollbarSlider.hoverBackground', '#646464b3')

    # Button colors
    button_bg = get_vscode_color(colors, 'button.background', accent)

    # Text colors
    text_muted = get_vscode_color(colors, 'tab.inactiveForeground') or \
                 get_vscode_color(colors, 'sideBar.foreground', '#969696')
    text_placeholder = get_vscode_color(colors, 'input.placeholderForeground', '#a6a6a6')

    # Line numbers
    line_number = get_vscode_color(colors, 'editorLineNumber.foreground', '#858585')
    line_number_active = get_vscode_color(colors, 'editorLineNumber.activeForeground', fg)

    # Cursor
    cursor = get_vscode_color(colors, 'editorCursor.foreground', fg)

    # Build Zed theme style
    style = {
        # Backgrounds
        'background': sidebar_bg,
        'elevated_surface.background': get_vscode_color(colors, 'editorWidget.background', panel_bg),
        'surface.background': panel_bg,

        # Borders
        'border': border,
        'border.variant': border,
        'border.focused': accent,
        'border.selected': accent,
        'border.transparent': normalize_color('#00000000'),
        'border.disabled': border,

        # Elements
        'element.background': input_bg,
        'element.hover': get_vscode_color(colors, 'list.hoverBackground', '#2a2d2e'),
        'element.active': get_vscode_color(colors, 'list.activeSelectionBackground', '#094771'),
        'element.selected': get_vscode_color(colors, 'list.inactiveSelectionBackground', '#37373d'),
        'element.disabled': get_vscode_color(colors, 'list.inactiveSelectionBackground', '#37373d'),

        'ghost_element.background': normalize_color('#00000000'),
        'ghost_element.hover': get_vscode_color(colors, 'list.hoverBackground', '#2a2d2e'),
        'ghost_element.active': get_vscode_color(colors, 'list.activeSelectionBackground', '#094771'),
        'ghost_element.selected': get_vscode_color(colors, 'list.inactiveSelectionBackground', '#37373d'),
        'ghost_element.disabled': get_vscode_color(colors, 'list.inactiveSelectionBackground', '#37373d'),

        # Text
        'text': fg,
        'text.muted': text_muted,
        'text.placeholder': text_placeholder,
        'text.disabled': text_placeholder,
        'text.accent': accent,

        # Icons
        'icon': fg,
        'icon.muted': text_muted,
        'icon.disabled': text_placeholder,
        'icon.placeholder': text_placeholder,
        'icon.accent': accent,

        # Status bar
        'status_bar.background': get_vscode_color(colors, 'statusBar.background', sidebar_bg),

        # Title bar
        'title_bar.background': get_vscode_color(colors, 'titleBar.activeBackground', sidebar_bg),
        'title_bar.inactive_background': get_vscode_color(colors, 'titleBar.inactiveBackground', sidebar_bg),

        # Toolbar
        'toolbar.background': sidebar_bg,

        # Tab bar
        'tab_bar.background': tab_bar_bg,
        'tab.inactive_background': tab_inactive_bg,
        'tab.active_background': tab_active_bg,

        # Search
        'search.match_background': get_vscode_color(colors, 'editor.findMatchHighlightBackground', '#ea5c0055'),

        # Panel
        'panel.background': panel_bg,
        'panel.focused_border': accent,

        # Pane
        'pane.focused_border': accent,

        # Scrollbar
        'scrollbar.thumb.background': scrollbar_thumb,
        'scrollbar.thumb.hover_background': scrollbar_thumb_hover,
        'scrollbar.thumb.border': normalize_color('#00000000'),
        'scrollbar.track.background': normalize_color('#00000000'),
        'scrollbar.track.border': normalize_color('#00000000'),

        # Editor
        'editor.foreground': fg,
        'editor.background': bg,
        'editor.gutter.background': bg,
        'editor.subheader.background': sidebar_bg,
        'editor.active_line.background': line_highlight,
        'editor.highlighted_line.background': line_highlight,
        'editor.line_number': line_number,
        'editor.active_line_number': line_number_active,
        'editor.invisible': get_vscode_color(colors, 'editorWhitespace.foreground', '#3b3b3b'),
        'editor.wrap_guide': get_vscode_color(colors, 'editorRuler.foreground', '#5a5a5a'),
        'editor.active_wrap_guide': get_vscode_color(colors, 'editorRuler.foreground', '#5a5a5a'),
        'editor.document_highlight.read_background': get_vscode_color(colors, 'editor.wordHighlightBackground', '#575757b8'),
        'editor.document_highlight.write_background': get_vscode_color(colors, 'editor.wordHighlightStrongBackground', '#004972b8'),

        # Terminal
        'terminal.background': get_vscode_color(colors, 'terminal.background', bg),
        'terminal.foreground': get_vscode_color(colors, 'terminal.foreground', fg),
        'terminal.bright_foreground': fg,
        'terminal.dim_foreground': text_muted,
        'terminal.ansi.black': get_vscode_color(colors, 'terminal.ansiBlack', '#000000'),
        'terminal.ansi.bright_black': get_vscode_color(colors, 'terminal.ansiBrightBlack', '#666666'),
        'terminal.ansi.dim_black': get_vscode_color(colors, 'terminal.ansiBlack', '#000000'),
        'terminal.ansi.red': get_vscode_color(colors, 'terminal.ansiRed', '#cd3131'),
        'terminal.ansi.bright_red': get_vscode_color(colors, 'terminal.ansiBrightRed', '#f14c4c'),
        'terminal.ansi.dim_red': get_vscode_color(colors, 'terminal.ansiRed', '#cd3131'),
        'terminal.ansi.green': get_vscode_color(colors, 'terminal.ansiGreen', '#0dbc79'),
        'terminal.ansi.bright_green': get_vscode_color(colors, 'terminal.ansiBrightGreen', '#23d18b'),
        'terminal.ansi.dim_green': get_vscode_color(colors, 'terminal.ansiGreen', '#0dbc79'),
        'terminal.ansi.yellow': get_vscode_color(colors, 'terminal.ansiYellow', '#e5e510'),
        'terminal.ansi.bright_yellow': get_vscode_color(colors, 'terminal.ansiBrightYellow', '#f5f543'),
        'terminal.ansi.dim_yellow': get_vscode_color(colors, 'terminal.ansiYellow', '#e5e510'),
        'terminal.ansi.blue': get_vscode_color(colors, 'terminal.ansiBlue', '#2472c8'),
        'terminal.ansi.bright_blue': get_vscode_color(colors, 'terminal.ansiBrightBlue', '#3b8eea'),
        'terminal.ansi.dim_blue': get_vscode_color(colors, 'terminal.ansiBlue', '#2472c8'),
        'terminal.ansi.magenta': get_vscode_color(colors, 'terminal.ansiMagenta', '#bc3fbc'),
        'terminal.ansi.bright_magenta': get_vscode_color(colors, 'terminal.ansiBrightMagenta', '#d670d6'),
        'terminal.ansi.dim_magenta': get_vscode_color(colors, 'terminal.ansiMagenta', '#bc3fbc'),
        'terminal.ansi.cyan': get_vscode_color(colors, 'terminal.ansiCyan', '#11a8cd'),
        'terminal.ansi.bright_cyan': get_vscode_color(colors, 'terminal.ansiBrightCyan', '#29b8db'),
        'terminal.ansi.dim_cyan': get_vscode_color(colors, 'terminal.ansiCyan', '#11a8cd'),
        'terminal.ansi.white': get_vscode_color(colors, 'terminal.ansiWhite', '#e5e5e5'),
        'terminal.ansi.bright_white': get_vscode_color(colors, 'terminal.ansiBrightWhite', '#ffffff'),
        'terminal.ansi.dim_white': get_vscode_color(colors, 'terminal.ansiWhite', '#e5e5e5'),

        # Link
        'link_text.hover': get_vscode_color(colors, 'editorLink.activeForeground', accent),

        # Status colors
        'error': error,
        'error.background': get_vscode_color(colors, 'inputValidation.errorBackground', '#5a1d1d'),
        'error.border': get_vscode_color(colors, 'inputValidation.errorBorder', error),
        'warning': warning,
        'warning.background': get_vscode_color(colors, 'inputValidation.warningBackground', '#352a05'),
        'warning.border': get_vscode_color(colors, 'inputValidation.warningBorder', warning),
        'success': added,
        'success.background': normalize_color('#1d3f1d'),
        'success.border': added,
        'info': info,
        'info.background': get_vscode_color(colors, 'inputValidation.infoBackground', '#063b49'),
        'info.border': get_vscode_color(colors, 'inputValidation.infoBorder', info),
        'hint': hint,
        'hint.background': normalize_color('#2d2d3d'),
        'hint.border': hint,

        # VCS
        'created': added,
        'created.background': normalize_color('#1d3f1d'),
        'created.border': added,
        'modified': modified,
        'modified.background': normalize_color('#3f3f1d'),
        'modified.border': modified,
        'deleted': deleted,
        'deleted.background': normalize_color('#3f1d1d'),
        'deleted.border': deleted,
        'conflict': get_vscode_color(colors, 'gitDecoration.conflictingResourceForeground', warning),
        'conflict.background': normalize_color('#3f3f1d'),
        'conflict.border': get_vscode_color(colors, 'gitDecoration.conflictingResourceForeground', warning),
        'hidden': get_vscode_color(colors, 'gitDecoration.ignoredResourceForeground', text_muted),
        'hidden.background': normalize_color('#00000000'),
        'hidden.border': normalize_color('#00000000'),
        'ignored': get_vscode_color(colors, 'gitDecoration.ignoredResourceForeground', text_muted),
        'ignored.background': normalize_color('#00000000'),
        'ignored.border': normalize_color('#00000000'),
        'renamed': get_vscode_color(colors, 'gitDecoration.renamedResourceForeground', info),
        'renamed.background': normalize_color('#1d3f3f'),
        'renamed.border': get_vscode_color(colors, 'gitDecoration.renamedResourceForeground', info),

        # Predictive (for AI suggestions)
        'predictive': text_muted,
        'predictive.background': normalize_color('#00000000'),
        'predictive.border': normalize_color('#00000000'),

        # Unreachable
        'unreachable': text_muted,
        'unreachable.background': normalize_color('#00000000'),
        'unreachable.border': normalize_color('#00000000'),

        # Players (for collaboration)
        'players': [
            {
                'cursor': accent,
                'background': accent,
                'selection': selection
            }
        ],
    }

    # Add syntax highlighting
    syntax = convert_token_colors(token_colors)
    if syntax:
        style['syntax'] = syntax

    # Remove None values
    style = {k: v for k, v in style.items() if v is not None}

    return {
        'name': theme_name,
        'appearance': 'light' if theme_type == 'light' else 'dark',
        'style': style
    }


def main():
    """Main conversion function."""
    themes_dir = Path('/home/astomodynamics/github/castor-pollux-theme/themes')
    output_dir = Path('/home/astomodynamics/.config/zed/themes')

    # Ensure output directory exists
    output_dir.mkdir(parents=True, exist_ok=True)

    # Read package.json for theme metadata
    package_path = Path('/home/astomodynamics/github/castor-pollux-theme/package.json')
    with open(package_path) as f:
        package = json.load(f)

    # Create theme name mapping from package.json
    theme_labels = {}
    for theme in package['contributes']['themes']:
        path = Path(theme['path']).name
        theme_labels[path] = theme['label']

    # Collect all converted themes
    zed_themes = []

    # Process each theme file
    for theme_file in themes_dir.glob('*.json'):
        print(f"Converting: {theme_file.name}")

        with open(theme_file) as f:
            vscode_theme = json.load(f)

        # Get theme name from package.json or file
        theme_name = theme_labels.get(theme_file.name, vscode_theme.get('name', theme_file.stem))

        zed_theme = convert_theme(vscode_theme, theme_name)
        zed_themes.append(zed_theme)

    # Create single Zed theme family file
    zed_family = {
        '$schema': 'https://zed.dev/schema/themes/v0.2.0.json',
        'name': 'Castor & Pollux',
        'author': 'Castor Pollux Theme Collection',
        'themes': zed_themes
    }

    # Write output file
    output_file = output_dir / 'castor-pollux.json'
    with open(output_file, 'w') as f:
        json.dump(zed_family, f, indent=2)

    print(f"\nCreated Zed theme family with {len(zed_themes)} themes at:")
    print(f"  {output_file}")
    print("\nThemes included:")
    for theme in zed_themes:
        print(f"  - {theme['name']} ({theme['appearance']})")


if __name__ == '__main__':
    main()
