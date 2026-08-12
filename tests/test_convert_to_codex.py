import json
import tempfile
import unittest
from pathlib import Path

from convert_to_codex import (
    SHARE_PREFIX,
    convert_theme,
    load_theme_sources,
    normalize_color,
    select_theme_sources,
    write_exports,
)


class ConvertToCodexTests(unittest.TestCase):
    def test_castor_georgia_tech_share_string_matches_codex_schema(self) -> None:
        source = select_theme_sources(
            load_theme_sources(), ["Castor Georgia Tech"]
        )[0]
        export = convert_theme(source, "github")

        self.assertTrue(export.share_string.startswith(SHARE_PREFIX))
        payload = json.loads(export.share_string.removeprefix(SHARE_PREFIX))
        self.assertEqual(payload["variant"], "dark")
        self.assertEqual(payload["codeThemeId"], "github")
        self.assertEqual(
            payload["theme"],
            {
                "accent": "#b3a369",
                "contrast": 60,
                "fonts": {"code": None, "ui": None},
                "ink": "#e0e4ea",
                "opaqueWindows": False,
                "semanticColors": {
                    "diffAdded": "#6cc490",
                    "diffRemoved": "#e06070",
                    "skill": "#a080c8",
                },
                "surface": "#001528",
            },
        )

    def test_translucent_colors_are_not_used_as_opaque_theme_roles(self) -> None:
        self.assertIsNone(normalize_color("#b3a36980"))
        self.assertEqual(normalize_color("#B3A369FF"), "#b3a369")

    def test_code_theme_must_support_the_source_variant(self) -> None:
        source = select_theme_sources(load_theme_sources(), ["Aurora Light"])[0]
        with self.assertRaisesRegex(ValueError, "does not support light mode"):
            convert_theme(source, "ayu")

    def test_write_exports_creates_importable_file_and_manifest(self) -> None:
        source = select_theme_sources(
            load_theme_sources(), ["Castor Georgia Tech"]
        )[0]
        export = convert_theme(source, "github")

        with tempfile.TemporaryDirectory() as temporary_directory:
            output_dir = Path(temporary_directory)
            write_exports([export], output_dir)

            self.assertEqual(
                (output_dir / "castor-georgia-tech.txt").read_text(
                    encoding="utf-8"
                ),
                export.share_string + "\n",
            )
            manifest = json.loads(
                (output_dir / "manifest.json").read_text(encoding="utf-8")
            )
            self.assertEqual(manifest["format"], "codex-theme-v1")
            self.assertEqual(manifest["themeCount"], 1)
            self.assertEqual(manifest["themes"][0]["file"], "castor-georgia-tech.txt")


if __name__ == "__main__":
    unittest.main()
