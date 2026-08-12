#!/usr/bin/env python3
"""Export VS Code themes as Codex app theme share strings.

The Codex app imports ``codex-theme-v1:`` strings for its chrome colors and
associates each imported palette with one of the app's built-in code themes.
VS Code TextMate token rules are therefore not part of this export format.
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent
DEFAULT_OUTPUT_DIR = REPO_ROOT / "codex-themes"
SHARE_PREFIX = "codex-theme-v1:"

BUILT_IN_CODE_THEME_VARIANTS = {
    "absolutely": {"dark", "light"},
    "ayu": {"dark"},
    "catppuccin": {"dark", "light"},
    "codex": {"dark", "light"},
    "dracula": {"dark"},
    "everforest": {"dark", "light"},
    "github": {"dark", "light"},
    "gruvbox": {"dark", "light"},
    "linear": {"dark", "light"},
    "lobster": {"dark"},
    "material": {"dark"},
    "matrix": {"dark"},
    "monokai": {"dark"},
    "night-owl": {"dark"},
    "nord": {"dark"},
    "notion": {"dark", "light"},
    "oscurange": {"dark"},
    "one": {"dark", "light"},
    "proof": {"light"},
    "raycast": {"dark", "light"},
    "rose-pine": {"dark", "light"},
    "sentry": {"dark"},
    "solarized": {"dark", "light"},
    "temple": {"dark"},
    "tokyo-night": {"dark"},
    "vercel": {"dark", "light"},
    "vscode-plus": {"dark", "light"},
    "xcode": {"dark", "light"},
}

DEFAULTS = {
    "dark": {
        "accent": "#339cff",
        "contrast": 60,
        "ink": "#ffffff",
        "surface": "#181818",
        "diffAdded": "#40c977",
        "diffRemoved": "#fa423e",
        "skill": "#ad7bf9",
    },
    "light": {
        "accent": "#339cff",
        "contrast": 45,
        "ink": "#1a1c1f",
        "surface": "#ffffff",
        "diffAdded": "#00a240",
        "diffRemoved": "#ba2623",
        "skill": "#924ff7",
    },
}

SURFACE_KEYS = (
    "editor.background",
    "sideBar.background",
    "editorGroupHeader.tabsBackground",
    "panel.background",
    "activityBar.background",
)
INK_KEYS = (
    "editor.foreground",
    "sideBarTitle.foreground",
    "sideBar.foreground",
    "foreground",
)
ACCENT_KEYS = (
    "activityBarBadge.background",
    "textLink.foreground",
    "editorCursor.foreground",
    "focusBorder",
    "button.background",
    "activityBar.activeBorder",
)
DIFF_ADDED_KEYS = (
    "gitDecoration.addedResourceForeground",
    "gitDecoration.untrackedResourceForeground",
    "terminal.ansiGreen",
    "terminal.ansiBrightGreen",
)
DIFF_REMOVED_KEYS = (
    "gitDecoration.deletedResourceForeground",
    "terminal.ansiRed",
    "terminal.ansiBrightRed",
)
SKILL_KEYS = (
    "charts.purple",
    "terminal.ansiMagenta",
    "terminal.ansiBrightMagenta",
)


@dataclass(frozen=True)
class ThemeSource:
    label: str
    slug: str
    variant: str
    source: Path
    colors: dict[str, str]


@dataclass(frozen=True)
class CodexThemeExport:
    label: str
    slug: str
    variant: str
    source: Path
    code_theme_id: str
    payload: dict[str, object]

    @property
    def share_string(self) -> str:
        return SHARE_PREFIX + json.dumps(
            self.payload,
            ensure_ascii=False,
            separators=(",", ":"),
        )


def slugify(label: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", label.lower()).strip("-")
    if not slug:
        raise ValueError(f"Cannot create a Codex theme filename for {label!r}")
    return slug


def normalize_color(value: object) -> str | None:
    """Return an opaque #rrggbb color accepted by the Codex share schema."""
    if not isinstance(value, str):
        return None
    match = re.fullmatch(r"#([0-9a-fA-F]{6})([0-9a-fA-F]{2})?", value.strip())
    if match is None:
        return None
    alpha = match.group(2)
    if alpha is not None and int(alpha, 16) < 250:
        return None
    return f"#{match.group(1).lower()}"


def first_color(colors: dict[str, str], keys: tuple[str, ...], fallback: str) -> str:
    for key in keys:
        color = normalize_color(colors.get(key))
        if color is not None:
            return color
    return fallback


def load_theme_sources() -> list[ThemeSource]:
    package = json.loads((REPO_ROOT / "package.json").read_text(encoding="utf-8"))
    sources = []
    for contribution in package["contributes"]["themes"]:
        theme_path = (REPO_ROOT / contribution["path"]).resolve()
        theme = json.loads(theme_path.read_text(encoding="utf-8"))
        variant = theme.get("type")
        if variant not in {"dark", "light"}:
            variant = "light" if contribution.get("uiTheme") == "vs" else "dark"
        label = contribution["label"]
        sources.append(
            ThemeSource(
                label=label,
                slug=slugify(label),
                variant=variant,
                source=theme_path.relative_to(REPO_ROOT),
                colors=theme.get("colors", {}),
            )
        )
    return sources


def select_theme_sources(
    sources: list[ThemeSource], labels: list[str] | None
) -> list[ThemeSource]:
    if not labels:
        return sources
    sources_by_label = {source.label: source for source in sources}
    missing = [label for label in labels if label not in sources_by_label]
    if missing:
        available = ", ".join(sorted(sources_by_label))
        raise ValueError(f"Unknown theme {missing[0]!r}. Available themes: {available}")
    return [sources_by_label[label] for label in labels]


def convert_theme(source: ThemeSource, code_theme_id: str) -> CodexThemeExport:
    variants = BUILT_IN_CODE_THEME_VARIANTS.get(code_theme_id)
    if variants is None:
        raise ValueError(f"Unsupported Codex code theme: {code_theme_id}")
    if source.variant not in variants:
        raise ValueError(
            f"Codex code theme {code_theme_id!r} does not support {source.variant} mode"
        )

    defaults = DEFAULTS[source.variant]
    colors = source.colors
    theme = {
        "accent": first_color(colors, ACCENT_KEYS, defaults["accent"]),
        "contrast": defaults["contrast"],
        "fonts": {"code": None, "ui": None},
        "ink": first_color(colors, INK_KEYS, defaults["ink"]),
        "opaqueWindows": False,
        "semanticColors": {
            "diffAdded": first_color(
                colors, DIFF_ADDED_KEYS, defaults["diffAdded"]
            ),
            "diffRemoved": first_color(
                colors, DIFF_REMOVED_KEYS, defaults["diffRemoved"]
            ),
            "skill": first_color(colors, SKILL_KEYS, defaults["skill"]),
        },
        "surface": first_color(colors, SURFACE_KEYS, defaults["surface"]),
    }
    payload = {
        "codeThemeId": code_theme_id,
        "theme": theme,
        "variant": source.variant,
    }
    return CodexThemeExport(
        label=source.label,
        slug=source.slug,
        variant=source.variant,
        source=source.source,
        code_theme_id=code_theme_id,
        payload=payload,
    )


def write_exports(exports: list[CodexThemeExport], output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "format": "codex-theme-v1",
        "generatedBy": "convert_to_codex.py",
        "themeCount": len(exports),
        "themes": [],
    }
    for export in exports:
        filename = f"{export.slug}.txt"
        (output_dir / filename).write_text(export.share_string + "\n", encoding="utf-8")
        manifest["themes"].append(
            {
                "label": export.label,
                "variant": export.variant,
                "codeThemeId": export.code_theme_id,
                "source": str(export.source),
                "file": filename,
            }
        )
    (output_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate Codex app theme share strings from VS Code themes."
    )
    parser.add_argument(
        "--theme",
        action="append",
        dest="themes",
        metavar="LABEL",
        help="Theme label to export. Repeat to select multiple themes; omit for all.",
    )
    parser.add_argument(
        "--code-theme",
        choices=BUILT_IN_CODE_THEME_VARIANTS,
        default="github",
        help="Built-in Codex syntax theme to associate with the palette (default: github).",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help=f"Output directory (default: {DEFAULT_OUTPUT_DIR})",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    sources = select_theme_sources(load_theme_sources(), args.themes)
    exports = [convert_theme(source, args.code_theme) for source in sources]
    output_dir = args.output_dir.expanduser().resolve()
    write_exports(exports, output_dir)

    print(f"Generated {len(exports)} Codex theme share string(s) in {output_dir}")
    if len(exports) == 1:
        print(exports[0].share_string)


if __name__ == "__main__":
    main()
