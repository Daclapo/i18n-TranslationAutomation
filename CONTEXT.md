# Project Context for i18n Translation Automation

This document provides technical context for developers working on or extending this project.

## Overview

i18n Manager is a developer-time CLI tool for managing internationalized texts. It is not part of a production runtime. The tool automates the process of translating texts from a source language (Spanish by default) into multiple target languages, storing all translations in a single JSON file consumed by a frontend application.

## Architecture

The codebase follows a layered architecture:

1. **CLI layer** (`cli.py`): User-facing commands built with the `click` library. Handles argument parsing, user interaction, and output formatting. Does not contain business logic.

2. **Translation layer** (`translator.py`): Orchestrates translations by coordinating the configured provider with the source and target languages. Acts as a bridge between the CLI and the provider.

3. **Provider layer** (`providers/`): Abstract interface for translation APIs. Each provider implements a single `translate()` method. New providers are added by implementing `TranslationProvider` and registering them in `PROVIDER_REGISTRY`.

4. **Storage layer** (`storage.py`): Manages the `messages.json` file with atomic writes, backup creation, and changelog logging. All JSON operations go through this module.

5. **Configuration** (`config.py`): Loads and validates `config.yaml`. Supports referencing environment variables for API keys via `env:VARIABLE_NAME` syntax.

## Design Decisions

- **Click over argparse**: the `click` library provides cleaner subcommand support, built-in input validation, and a test runner (`CliRunner`) that simplifies CLI testing.

- **Atomic file writes**: `messages.json` is written to a temporary file first, then renamed. This prevents data corruption if the process is interrupted.

- **Monthly changelog files**: operations are logged to `changelog/YYYY-MM.log` rather than a single growing file. This keeps individual files manageable and provides natural time-based partitioning.

- **Language codes in lowercase**: language codes are stored in lowercase in `messages.json` (e.g., `"es"`, `"en"`, `"pt-br"`) for consistency, regardless of how the provider or user specifies them.

- **Provider registry pattern**: providers are registered in a simple dictionary rather than using a plugin discovery mechanism. This was chosen for simplicity; the system currently supports two providers and is not expected to require dynamic discovery.

## Known Limitations

- The system does not detect or handle text interpolation patterns (e.g., `{variable}`, `{{var}}`). Texts containing such patterns may have the variables translated or altered by the translation API.

- There is no mechanism to detect or complete placeholder translations in existing data. If the JSON contains keys with placeholder values (e.g., "area.surname"), those must be identified and corrected manually.

- Formality settings are not explicitly controlled. The translation provider uses its default formality behavior for each target language.

## Future Improvement Considerations

The following areas have been identified for potential future development. They are listed here for reference and should be evaluated once the core system is confirmed to be working correctly.

- **Batch API calls**: some providers (DeepL, Azure) support translating multiple texts in a single API request. Implementing batch translation during CSV/JSON import could reduce API call count and improve performance.

- **Key validation rules**: configurable rules for key naming conventions (e.g., requiring dot notation, maximum depth, allowed characters).

- **Update/edit mode**: a command to modify existing translations for a key (re-translate from updated source text).

- **Delete command**: remove a key from all language objects.

- **Sync/audit command**: detect keys that are missing translations in one or more languages and offer to complete them.

- **Provider-specific formality control**: expose formality settings in `config.yaml` for providers that support it (DeepL offers formal/informal modes for certain languages).

- **Rate limiting**: implement configurable delays between API calls to avoid hitting provider rate limits during large imports.
