"""Integration tests for the CLI commands.

Tests verify the CLI interface, argument parsing, and command behavior.
All translation API calls are mocked. Tests use click's CliRunner for
isolated command invocation.
"""

import json
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest
from click.testing import CliRunner

from i18n_manager.cli import main
from i18n_manager.config import Config


def _mock_translations(text: str) -> dict[str, str]:
    """Generate mock translations for testing."""
    return {
        "es": text,
        "en": f"[EN] {text}",
        "pt-br": f"[PT-BR] {text}",
    }


def _create_config_file(project_dir: Path) -> None:
    """Create a minimal config.yaml in the given directory."""
    config_content = (
        "provider: deepl\n"
        "api_key: test-api-key\n"
        "source_language: ES\n"
        "target_languages:\n"
        "  - EN\n"
        "  - PT-BR\n"
        "messages_file: data/messages.json\n"
    )
    (project_dir / "config.yaml").write_text(config_content, encoding="utf-8")


def _create_messages_file(project_dir: Path, data: dict = None) -> Path:
    """Create the messages.json file with optional initial data."""
    messages_dir = project_dir / "data"
    messages_dir.mkdir(parents=True, exist_ok=True)
    messages_path = messages_dir / "messages.json"

    if data is None:
        data = {"es": {}, "en": {}, "pt-br": {}}

    messages_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return messages_path


class TestAddCommand:
    """Tests for the 'i18n add' command."""

    @patch("i18n_manager.cli.Translator")
    def test_add_single_entry(self, MockTranslator, tmp_path):
        mock_instance = MockTranslator.return_value
        mock_instance.translate_text.return_value = _mock_translations("Bienvenido")

        _create_config_file(tmp_path)
        messages_path = _create_messages_file(tmp_path)

        runner = CliRunner()
        with runner.isolated_filesystem(temp_dir=tmp_path):
            # We need to run from the tmp_path directory.
            import os
            os.chdir(tmp_path)

            result = runner.invoke(main, ["add", "home.title", "Bienvenido"])

        assert result.exit_code == 0
        assert "home.title" in result.output

        # Verify the JSON was updated.
        data = json.loads(messages_path.read_text(encoding="utf-8"))
        assert data["es"]["home.title"] == "Bienvenido"
        assert data["en"]["home.title"] == "[EN] Bienvenido"
        assert data["pt-br"]["home.title"] == "[PT-BR] Bienvenido"

    @patch("i18n_manager.cli.Translator")
    def test_add_duplicate_key_aborts(self, MockTranslator, tmp_path):
        _create_config_file(tmp_path)
        existing = {
            "es": {"home.title": "Existente"},
            "en": {"home.title": "Existing"},
        }
        _create_messages_file(tmp_path, existing)

        runner = CliRunner()
        import os
        os.chdir(tmp_path)
        result = runner.invoke(main, ["add", "home.title", "Nuevo texto"])

        assert result.exit_code != 0
        assert "already exists" in result.output

    @patch("i18n_manager.cli.Translator")
    def test_add_dry_run_does_not_write(self, MockTranslator, tmp_path):
        mock_instance = MockTranslator.return_value
        mock_instance.translate_text.return_value = _mock_translations("Prueba")

        _create_config_file(tmp_path)
        messages_path = _create_messages_file(tmp_path)
        original_content = messages_path.read_text(encoding="utf-8")

        runner = CliRunner()
        import os
        os.chdir(tmp_path)
        result = runner.invoke(main, ["add", "test.key", "Prueba", "--dry-run"])

        assert result.exit_code == 0
        assert "Dry run" in result.output

        # File should be unchanged.
        assert messages_path.read_text(encoding="utf-8") == original_content

    @patch("i18n_manager.cli.Translator")
    def test_add_force_overwrites(self, MockTranslator, tmp_path):
        mock_instance = MockTranslator.return_value
        mock_instance.translate_text.return_value = _mock_translations("Nuevo valor")

        _create_config_file(tmp_path)
        existing = {"es": {"key": "viejo"}, "en": {"key": "old"}, "pt-br": {"key": "antigo"}}
        messages_path = _create_messages_file(tmp_path, existing)

        runner = CliRunner()
        import os
        os.chdir(tmp_path)
        result = runner.invoke(main, ["add", "key", "Nuevo valor", "--force"])

        assert result.exit_code == 0

        data = json.loads(messages_path.read_text(encoding="utf-8"))
        assert data["es"]["key"] == "Nuevo valor"


class TestImportCommand:
    """Tests for the 'i18n import' command."""

    @patch("i18n_manager.cli.Translator")
    def test_import_csv(self, MockTranslator, tmp_path):
        mock_instance = MockTranslator.return_value
        mock_instance.translate_text.side_effect = lambda text: _mock_translations(text)

        _create_config_file(tmp_path)
        messages_path = _create_messages_file(tmp_path)

        # Create a CSV file.
        csv_path = tmp_path / "test_import.csv"
        csv_path.write_text("key,es\nnav.home,Inicio\nnav.about,Acerca de\n", encoding="utf-8")

        runner = CliRunner()
        import os
        os.chdir(tmp_path)
        result = runner.invoke(main, ["import", str(csv_path)])

        assert result.exit_code == 0
        assert "Added:   2" in result.output

        data = json.loads(messages_path.read_text(encoding="utf-8"))
        assert "nav.home" in data["es"]
        assert "nav.about" in data["es"]

    @patch("i18n_manager.cli.Translator")
    def test_import_json(self, MockTranslator, tmp_path):
        mock_instance = MockTranslator.return_value
        mock_instance.translate_text.side_effect = lambda text: _mock_translations(text)

        _create_config_file(tmp_path)
        messages_path = _create_messages_file(tmp_path)

        # Create a JSON import file.
        json_import = {"footer.copyright": "Derechos reservados", "footer.privacy": "Privacidad"}
        import_path = tmp_path / "test_import.json"
        import_path.write_text(json.dumps(json_import), encoding="utf-8")

        runner = CliRunner()
        import os
        os.chdir(tmp_path)
        result = runner.invoke(main, ["import", str(import_path)])

        assert result.exit_code == 0
        assert "Added:   2" in result.output

    @patch("i18n_manager.cli.Translator")
    def test_import_skips_existing_keys(self, MockTranslator, tmp_path):
        mock_instance = MockTranslator.return_value
        mock_instance.translate_text.side_effect = lambda text: _mock_translations(text)

        _create_config_file(tmp_path)
        existing = {"es": {"nav.home": "Inicio"}, "en": {"nav.home": "Home"}, "pt-br": {}}
        _create_messages_file(tmp_path, existing)

        csv_path = tmp_path / "test_import.csv"
        csv_path.write_text("key,es\nnav.home,Inicio\nnav.about,Acerca de\n", encoding="utf-8")

        runner = CliRunner()
        import os
        os.chdir(tmp_path)
        result = runner.invoke(main, ["import", str(csv_path)])

        assert result.exit_code == 0
        assert "Skipped: 1" in result.output
        assert "Added:   1" in result.output


class TestSetupCommand:
    """Tests for the 'i18n setup' command."""

    @patch("i18n_manager.cli.Translator")
    def test_setup_creates_config_file(self, MockTranslator, tmp_path):
        mock_instance = MockTranslator.return_value
        mock_instance.translate_text.return_value = {"es": "Prueba", "en": "Test"}

        runner = CliRunner()
        import os
        os.chdir(tmp_path)

        # Simulate user input for setup prompts.
        user_input = "deepl\ntest-api-key\nES\nEN,PT-BR\ndata/messages.json\n"

        result = runner.invoke(main, ["setup"], input=user_input)

        assert result.exit_code == 0

        config_path = tmp_path / "config.yaml"
        assert config_path.exists()
