"""JSON storage management for translation entries.

Handles all read/write operations on the messages.json file, including
atomic saves, backup creation, and operation logging. The JSON file uses
the following structure:

    {
        "es": {"key": "texto en espanol", ...},
        "en": {"key": "text in english", ...},
        "pt-br": {"key": "texto em portugues", ...}
    }

Language codes in the JSON are stored in lowercase to maintain consistency.
"""

import json
import shutil
from datetime import datetime
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Optional


def _ensure_dir(path: Path) -> None:
    """Create directory and parents if they do not exist."""
    path.mkdir(parents=True, exist_ok=True)


def load_messages(messages_path: Path) -> dict:
    """Load the messages JSON file.

    If the file does not exist, returns an empty dictionary. The caller
    is responsible for ensuring the required language keys are present.

    Args:
        messages_path: Absolute path to the messages.json file.

    Returns:
        The parsed JSON content as a dictionary.
    """
    if not messages_path.exists():
        return {}

    with open(messages_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, dict):
        raise ValueError(
            f"Expected a JSON object at the root of '{messages_path}', "
            f"but found {type(data).__name__}."
        )

    return data


def save_messages(messages_path: Path, data: dict) -> None:
    """Save translation data to the messages JSON file atomically.

    Writes to a temporary file first, then renames it to the target path.
    This prevents data corruption if the process is interrupted mid-write.

    Args:
        messages_path: Absolute path to the messages.json file.
        data: The complete translation data dictionary to save.
    """
    _ensure_dir(messages_path.parent)

    # Write to a temporary file in the same directory, then rename.
    # Using the same directory ensures the rename is atomic on the same filesystem.
    with NamedTemporaryFile(
        mode="w",
        suffix=".json",
        dir=messages_path.parent,
        delete=False,
        encoding="utf-8",
    ) as tmp:
        json.dump(data, tmp, ensure_ascii=False, indent=2, sort_keys=False)
        tmp.write("\n")
        tmp_path = Path(tmp.name)

    tmp_path.replace(messages_path)


def key_exists(data: dict, key: str) -> bool:
    """Check if a translation key already exists in any language object.

    Args:
        data: The loaded messages dictionary.
        key: The translation key to check.

    Returns:
        True if the key exists in at least one language object.
    """
    for lang_data in data.values():
        if isinstance(lang_data, dict) and key in lang_data:
            return True
    return False


def add_entry(
    data: dict,
    key: str,
    translations: dict[str, str],
    source_language: str,
    target_languages: list[str],
) -> dict:
    """Add a translation entry to the data dictionary.

    Ensures that all configured language objects exist and inserts the
    translations for the given key.

    Args:
        data: The current messages dictionary (modified in place and returned).
        key: The translation key (e.g., "home.title").
        translations: Mapping of language code to translated text
            (e.g., {"es": "Hola", "en": "Hello", "pt-br": "Ola"}).
        source_language: The source language code.
        target_languages: List of target language codes.

    Returns:
        The updated data dictionary.
    """
    all_languages = [source_language.lower()] + [lang.lower() for lang in target_languages]

    for lang in all_languages:
        if lang not in data:
            data[lang] = {}

    for lang, text in translations.items():
        lang_lower = lang.lower()
        if lang_lower in data:
            data[lang_lower][key] = text

    return data


def create_backup(messages_path: Path, project_root: Path) -> Optional[Path]:
    """Create a timestamped backup of the messages file.

    Backups are stored in the 'backups/' directory at the project root.
    If the messages file does not exist, no backup is created.

    Args:
        messages_path: Absolute path to the messages.json file.
        project_root: Absolute path to the project root directory.

    Returns:
        Path to the created backup file, or None if no backup was needed.
    """
    if not messages_path.exists():
        return None

    backup_dir = project_root / "backups"
    _ensure_dir(backup_dir)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_filename = f"messages_{timestamp}.json"
    backup_path = backup_dir / backup_filename

    shutil.copy2(messages_path, backup_path)
    return backup_path


def log_operation(
    project_root: Path,
    operation: str,
    keys: list[str],
) -> None:
    """Log a translation operation to the changelog.

    Logs are stored in monthly files within the 'changelog/' directory
    at the project root. Each line contains a timestamp, the operation
    type, and the list of affected keys.

    Args:
        project_root: Absolute path to the project root directory.
        operation: Description of the operation (e.g., "add", "import").
        keys: List of translation keys affected by the operation.
    """
    changelog_dir = project_root / "changelog"
    _ensure_dir(changelog_dir)

    now = datetime.now()
    log_filename = f"{now.strftime('%Y-%m')}.log"
    log_path = changelog_dir / log_filename

    timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
    keys_str = ", ".join(keys)
    log_line = f"[{timestamp}] {operation}: {keys_str}\n"

    with open(log_path, "a", encoding="utf-8") as f:
        f.write(log_line)
