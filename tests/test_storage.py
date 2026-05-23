"""Unit tests for the storage module.

Tests cover JSON load/save operations, key conflict detection, entry addition,
backup creation, and changelog logging. All tests use temporary directories
to avoid modifying real project files.
"""

import json
from pathlib import Path

import pytest

from i18n_manager.storage import (
    add_entry,
    create_backup,
    key_exists,
    load_messages,
    log_operation,
    save_messages,
)


@pytest.fixture
def tmp_project(tmp_path):
    """Create a temporary project structure for testing."""
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    messages_path = data_dir / "messages.json"
    return tmp_path, messages_path


class TestLoadMessages:
    """Tests for loading the messages JSON file."""

    def test_load_nonexistent_file_returns_empty_dict(self, tmp_project):
        _, messages_path = tmp_project
        result = load_messages(messages_path)
        assert result == {}

    def test_load_valid_json(self, tmp_project):
        _, messages_path = tmp_project
        data = {"es": {"key1": "valor"}, "en": {"key1": "value"}}
        messages_path.write_text(json.dumps(data), encoding="utf-8")

        result = load_messages(messages_path)
        assert result == data

    def test_load_invalid_json_raises_error(self, tmp_project):
        _, messages_path = tmp_project
        messages_path.write_text("[1, 2, 3]", encoding="utf-8")

        with pytest.raises(ValueError, match="Expected a JSON object"):
            load_messages(messages_path)


class TestSaveMessages:
    """Tests for saving messages to JSON."""

    def test_save_creates_file(self, tmp_project):
        _, messages_path = tmp_project
        data = {"es": {"test": "prueba"}}
        save_messages(messages_path, data)

        assert messages_path.exists()
        loaded = json.loads(messages_path.read_text(encoding="utf-8"))
        assert loaded == data

    def test_save_creates_parent_directories(self, tmp_path):
        messages_path = tmp_path / "deep" / "nested" / "messages.json"
        data = {"es": {"key": "valor"}}
        save_messages(messages_path, data)

        assert messages_path.exists()

    def test_save_preserves_unicode(self, tmp_project):
        _, messages_path = tmp_project
        data = {"es": {"greeting": "Bienvenido"}, "pt-br": {"greeting": "Bem-vindo"}}
        save_messages(messages_path, data)

        content = messages_path.read_text(encoding="utf-8")
        assert "Bienvenido" in content
        assert "Bem-vindo" in content


class TestKeyExists:
    """Tests for key existence checking."""

    def test_key_exists_returns_true_when_present(self):
        data = {"es": {"home.title": "Inicio"}, "en": {"home.title": "Home"}}
        assert key_exists(data, "home.title") is True

    def test_key_exists_returns_false_when_absent(self):
        data = {"es": {"home.title": "Inicio"}}
        assert key_exists(data, "nonexistent.key") is False

    def test_key_exists_with_empty_data(self):
        assert key_exists({}, "any.key") is False


class TestAddEntry:
    """Tests for adding translation entries."""

    def test_add_entry_creates_language_objects_if_missing(self):
        data = {}
        translations = {"es": "Hola", "en": "Hello", "pt-br": "Ola"}
        result = add_entry(data, "greeting", translations, "ES", ["EN", "PT-BR"])

        assert "es" in result
        assert "en" in result
        assert "pt-br" in result
        assert result["es"]["greeting"] == "Hola"
        assert result["en"]["greeting"] == "Hello"
        assert result["pt-br"]["greeting"] == "Ola"

    def test_add_entry_preserves_existing_entries(self):
        data = {
            "es": {"existing": "existente"},
            "en": {"existing": "existing"},
        }
        translations = {"es": "Nuevo", "en": "New"}
        result = add_entry(data, "new_key", translations, "ES", ["EN"])

        assert result["es"]["existing"] == "existente"
        assert result["es"]["new_key"] == "Nuevo"

    def test_add_entry_overwrites_existing_key(self):
        data = {"es": {"key": "viejo"}, "en": {"key": "old"}}
        translations = {"es": "nuevo", "en": "new"}
        result = add_entry(data, "key", translations, "ES", ["EN"])

        assert result["es"]["key"] == "nuevo"
        assert result["en"]["key"] == "new"


class TestCreateBackup:
    """Tests for backup creation."""

    def test_backup_creates_file(self, tmp_project):
        project_root, messages_path = tmp_project
        messages_path.write_text('{"es": {}}', encoding="utf-8")

        backup_path = create_backup(messages_path, project_root)

        assert backup_path is not None
        assert backup_path.exists()
        assert backup_path.parent.name == "backups"

    def test_backup_returns_none_when_no_source(self, tmp_project):
        project_root, messages_path = tmp_project
        result = create_backup(messages_path, project_root)
        assert result is None

    def test_backup_contents_match_original(self, tmp_project):
        project_root, messages_path = tmp_project
        original_data = {"es": {"key": "valor"}}
        messages_path.write_text(json.dumps(original_data), encoding="utf-8")

        backup_path = create_backup(messages_path, project_root)

        backup_data = json.loads(backup_path.read_text(encoding="utf-8"))
        assert backup_data == original_data


class TestLogOperation:
    """Tests for operation logging."""

    def test_log_creates_file(self, tmp_project):
        project_root, _ = tmp_project
        log_operation(project_root, "add", ["test.key"])

        changelog_dir = project_root / "changelog"
        assert changelog_dir.exists()

        log_files = list(changelog_dir.glob("*.log"))
        assert len(log_files) == 1

    def test_log_appends_entries(self, tmp_project):
        project_root, _ = tmp_project

        log_operation(project_root, "add", ["key1"])
        log_operation(project_root, "add", ["key2"])

        log_files = list((project_root / "changelog").glob("*.log"))
        content = log_files[0].read_text(encoding="utf-8")

        assert "key1" in content
        assert "key2" in content
        assert content.count("\n") == 2
