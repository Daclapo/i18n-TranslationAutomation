"""CLI entry point for i18n Manager.

Provides the following commands:
    i18n setup      - Interactive first-time configuration
    i18n add        - Add a single translation entry
    i18n import     - Bulk import from CSV or JSON file
    i18n interactive - Interactive console mode for continuous entry
"""

import csv
import json
import sys
from pathlib import Path

import click

from i18n_manager.config import Config, load_config, save_config
from i18n_manager.providers import PROVIDER_REGISTRY
from i18n_manager.storage import (
    add_entry,
    create_backup,
    key_exists,
    load_messages,
    log_operation,
    save_messages,
)
from i18n_manager.translator import Translator


def _resolve_project_root() -> Path:
    """Determine the project root directory.

    Uses the current working directory as the project root.
    """
    return Path.cwd()


def _get_messages_path(config: Config) -> Path:
    """Build the absolute path to the messages file.

    Args:
        config: The application configuration.

    Returns:
        Absolute path to the messages JSON file.
    """
    return config.project_root / config.messages_file


# ---------------------------------------------------------------------------
# CLI Group
# ---------------------------------------------------------------------------

@click.group()
@click.version_option(package_name="i18n-manager")
def main():
    """i18n Manager - Manage internationalized translations from the command line."""
    pass


# ---------------------------------------------------------------------------
# Setup Command
# ---------------------------------------------------------------------------

@main.command()
def setup():
    """Configure the translation provider, API key, and target languages.

    Creates (or overwrites) the config.yaml file with the chosen settings.
    Validates the API key by performing a test translation.
    """
    project_root = _resolve_project_root()

    click.echo("i18n Manager - Initial Configuration")
    click.echo("=" * 40)
    click.echo()

    # Provider selection.
    available_providers = ", ".join(sorted(PROVIDER_REGISTRY.keys()))
    provider = click.prompt(
        f"Translation provider ({available_providers})",
        default="deepl",
        type=click.Choice(sorted(PROVIDER_REGISTRY.keys()), case_sensitive=False),
    )

    # API key.
    click.echo()
    click.echo("You can enter the API key directly, or use 'env:VARIABLE_NAME'")
    click.echo("to reference an environment variable (e.g., 'env:DEEPL_API_KEY').")
    api_key = click.prompt("API key", type=str)

    # Azure-specific: region.
    azure_region = "westeurope"
    if provider == "azure":
        azure_region = click.prompt("Azure region", default="westeurope", type=str)

    # Source language.
    click.echo()
    source_language = click.prompt(
        "Source language code (e.g., ES, EN, FR)",
        default="ES",
        type=str,
    )

    # Target languages.
    target_input = click.prompt(
        "Target language codes, comma-separated (e.g., EN,PT-BR,FR)",
        default="EN,PT-BR",
        type=str,
    )
    target_languages = [lang.strip().upper() for lang in target_input.split(",") if lang.strip()]

    # Messages file path.
    messages_file = click.prompt(
        "Path to messages file (relative to project root)",
        default="data/messages.json",
        type=str,
    )

    config = Config(
        provider=provider,
        api_key=api_key,
        source_language=source_language.upper(),
        target_languages=target_languages,
        messages_file=messages_file,
        azure_region=azure_region,
        project_root=project_root,
    )

    # Validate API key with a test translation.
    click.echo()
    click.echo("Validating API key with a test translation...")
    try:
        translator = Translator(config)
        test_result = translator.translate_text("Prueba de conexion")
        click.echo("Validation successful. Test translations:")
        for lang, text in test_result.items():
            click.echo(f"  {lang}: {text}")
    except Exception as exc:
        click.echo(f"Validation failed: {exc}", err=True)
        if not click.confirm("Save configuration anyway?", default=False):
            click.echo("Configuration cancelled.")
            sys.exit(1)

    # Save configuration.
    config_path = save_config(config)
    click.echo()
    click.echo(f"Configuration saved to '{config_path}'.")
    click.echo("You can now use 'i18n add', 'i18n import', or 'i18n interactive'.")


# ---------------------------------------------------------------------------
# Add Command
# ---------------------------------------------------------------------------

@main.command()
@click.argument("key", type=str)
@click.argument("text", type=str)
@click.option("--dry-run", is_flag=True, default=False, help="Show what would be added without writing.")
@click.option("--force", is_flag=True, default=False, help="Overwrite existing key without confirmation.")
def add(key: str, text: str, dry_run: bool, force: bool):
    """Add a single translation entry.

    KEY is the translation identifier (e.g., "home.title").
    TEXT is the source text in the configured source language.

    Example: i18n add home.title "Bienvenido a mi web"
    """
    project_root = _resolve_project_root()

    try:
        config = load_config(project_root)
    except FileNotFoundError as exc:
        click.echo(str(exc), err=True)
        sys.exit(1)

    messages_path = _get_messages_path(config)

    # Validate input.
    if not key.strip():
        click.echo("Error: Key cannot be empty.", err=True)
        sys.exit(1)

    if not text.strip():
        click.echo("Error: Text cannot be empty.", err=True)
        sys.exit(1)

    # Load existing data.
    data = load_messages(messages_path)

    # Check for duplicate key.
    if key_exists(data, key) and not force:
        click.echo(f"Error: Key '{key}' already exists. Use --force to overwrite.", err=True)
        sys.exit(1)

    # Translate.
    click.echo(f"Translating '{key}'...")
    try:
        translator = Translator(config)
        translations = translator.translate_text(text)
    except RuntimeError as exc:
        click.echo(f"Translation error: {exc}", err=True)
        sys.exit(1)

    # Show results.
    click.echo("Translations:")
    for lang, translated_text in translations.items():
        click.echo(f"  {lang}: {translated_text}")

    if dry_run:
        click.echo()
        click.echo("[Dry run] No changes written to disk.")
        return

    # Save.
    create_backup(messages_path, project_root)
    data = add_entry(data, key, translations, config.source_language, config.target_languages)
    save_messages(messages_path, data)
    log_operation(project_root, "add", [key])

    click.echo(f"Entry '{key}' added successfully.")


# ---------------------------------------------------------------------------
# Import Command
# ---------------------------------------------------------------------------

@main.command(name="import")
@click.argument("file_path", type=click.Path(exists=True))
@click.option("--dry-run", is_flag=True, default=False, help="Show what would be added without writing.")
@click.option("--force", is_flag=True, default=False, help="Overwrite existing keys without confirmation.")
def import_file(file_path: str, dry_run: bool, force: bool):
    """Bulk import translations from a CSV or JSON file.

    FILE_PATH is the path to the import file.

    CSV format: Two columns with headers 'key' and 'es' (or source language code).
    JSON format: A flat object mapping keys to source-language texts.

    Example: i18n import translations.csv
    """
    project_root = _resolve_project_root()

    try:
        config = load_config(project_root)
    except FileNotFoundError as exc:
        click.echo(str(exc), err=True)
        sys.exit(1)

    messages_path = _get_messages_path(config)
    source = Path(file_path)

    # Parse the input file.
    entries = _parse_import_file(source, config.source_language)
    if not entries:
        click.echo("No valid entries found in the file.")
        return

    click.echo(f"Found {len(entries)} entries to process.")

    # Load existing data.
    data = load_messages(messages_path)

    translator = Translator(config)
    added_keys = []
    skipped_keys = []
    error_keys = []

    for i, (entry_key, entry_text) in enumerate(entries, start=1):
        prefix = f"  [{i}/{len(entries)}]"

        # Validate.
        if not entry_key.strip() or not entry_text.strip():
            click.echo(f"{prefix} Skipped: empty key or text.")
            skipped_keys.append(entry_key)
            continue

        # Check duplicates.
        if key_exists(data, entry_key) and not force:
            click.echo(f"{prefix} Skipped '{entry_key}': key already exists.")
            skipped_keys.append(entry_key)
            continue

        # Translate.
        try:
            translations = translator.translate_text(entry_text)
        except RuntimeError as exc:
            click.echo(f"{prefix} Error translating '{entry_key}': {exc}")
            error_keys.append(entry_key)
            continue

        if not dry_run:
            data = add_entry(data, entry_key, translations, config.source_language, config.target_languages)

        added_keys.append(entry_key)
        click.echo(f"{prefix} Added '{entry_key}'.")

    # Save if not dry-run.
    if not dry_run and added_keys:
        create_backup(messages_path, project_root)
        save_messages(messages_path, data)
        log_operation(project_root, "import", added_keys)

    # Summary.
    click.echo()
    click.echo("Import summary:")
    click.echo(f"  Added:   {len(added_keys)}")
    click.echo(f"  Skipped: {len(skipped_keys)}")
    click.echo(f"  Errors:  {len(error_keys)}")

    if dry_run:
        click.echo()
        click.echo("[Dry run] No changes written to disk.")


def _parse_import_file(file_path: Path, source_language: str) -> list[tuple[str, str]]:
    """Parse a CSV or JSON file into a list of (key, text) tuples.

    The file type is determined by the file extension.

    Args:
        file_path: Path to the input file.
        source_language: The source language code (for CSV column matching).

    Returns:
        A list of (key, source_text) tuples.

    Raises:
        click.ClickException: If the file format is unsupported or malformed.
    """
    suffix = file_path.suffix.lower()

    if suffix == ".csv":
        return _parse_csv(file_path, source_language)
    elif suffix == ".json":
        return _parse_json(file_path)
    else:
        raise click.ClickException(
            f"Unsupported file format: '{suffix}'. Use .csv or .json."
        )


def _parse_csv(file_path: Path, source_language: str) -> list[tuple[str, str]]:
    """Parse a CSV file with 'key' and source language columns.

    Supports both the language code (e.g., 'es') and the literal word 'value'
    as the second column header.
    """
    entries = []
    source_lower = source_language.lower()

    with open(file_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        headers = [h.lower().strip() for h in (reader.fieldnames or [])]

        if "key" not in headers:
            raise click.ClickException(
                f"CSV file must contain a 'key' column. Found: {headers}"
            )

        # Accept the source language code or 'value' as the text column.
        text_column = None
        for candidate in [source_lower, "value", "text"]:
            if candidate in headers:
                text_column = candidate
                break

        if text_column is None:
            raise click.ClickException(
                f"CSV file must contain a '{source_lower}', 'value', or 'text' column. "
                f"Found: {headers}"
            )

        for row in reader:
            # Normalize row keys to lowercase.
            normalized = {k.lower().strip(): v for k, v in row.items()}
            entry_key = normalized.get("key", "").strip()
            entry_text = normalized.get(text_column, "").strip()
            if entry_key:
                entries.append((entry_key, entry_text))

    return entries


def _parse_json(file_path: Path) -> list[tuple[str, str]]:
    """Parse a JSON file as a flat key-value object."""
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, dict):
        raise click.ClickException(
            "JSON import file must contain a flat object mapping keys to texts."
        )

    entries = []
    for entry_key, entry_text in data.items():
        if isinstance(entry_text, str):
            entries.append((entry_key.strip(), entry_text.strip()))
        else:
            click.echo(f"  Warning: Skipping key '{entry_key}' (value is not a string).")

    return entries


# ---------------------------------------------------------------------------
# Interactive Command
# ---------------------------------------------------------------------------

@main.command()
def interactive():
    """Enter interactive mode for continuous translation entry.

    Prompts for a key and source text in a loop. Each entry is validated,
    translated, and saved immediately. Press Ctrl+C or enter an empty key
    to exit.
    """
    project_root = _resolve_project_root()

    try:
        config = load_config(project_root)
    except FileNotFoundError as exc:
        click.echo(str(exc), err=True)
        sys.exit(1)

    messages_path = _get_messages_path(config)
    translator = Translator(config)

    click.echo("i18n Manager - Interactive Mode")
    click.echo("Enter translation key and text. Press Ctrl+C or leave key empty to exit.")
    click.echo("-" * 40)

    entries_added = 0

    try:
        while True:
            click.echo()
            entry_key = click.prompt("Key", default="", show_default=False).strip()

            if not entry_key:
                click.echo("Empty key received. Exiting interactive mode.")
                break

            entry_text = click.prompt("Text", default="", show_default=False).strip()

            if not entry_text:
                click.echo("Error: Text cannot be empty. Skipping this entry.")
                continue

            # Load current data (reload each iteration for safety).
            data = load_messages(messages_path)

            if key_exists(data, entry_key):
                if not click.confirm(f"Key '{entry_key}' already exists. Overwrite?", default=False):
                    click.echo("Skipped.")
                    continue

            # Translate.
            click.echo("Translating...")
            try:
                translations = translator.translate_text(entry_text)
            except RuntimeError as exc:
                click.echo(f"Translation error: {exc}")
                continue

            # Show translations.
            for lang, translated_text in translations.items():
                click.echo(f"  {lang}: {translated_text}")

            # Save immediately.
            create_backup(messages_path, project_root)
            data = add_entry(data, entry_key, translations, config.source_language, config.target_languages)
            save_messages(messages_path, data)
            log_operation(project_root, "interactive-add", [entry_key])

            entries_added += 1
            click.echo(f"Entry '{entry_key}' saved.")

    except (KeyboardInterrupt, EOFError):
        click.echo()
        click.echo("Interrupted. Exiting interactive mode.")

    click.echo(f"Total entries added in this session: {entries_added}")
