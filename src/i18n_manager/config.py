"""Configuration management for i18n Manager.

Handles loading, saving, and validating the project configuration
stored in config.yaml. Also supports reading API keys from environment
variables or .env files.

Configuration file structure (config.yaml):
    provider: deepl
    api_key: <key or "env:DEEPL_API_KEY">
    source_language: ES
    target_languages:
        - EN
        - PT-BR
    messages_file: data/messages.json
    azure_region: westeurope  # Only required for Azure provider
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import yaml
from dotenv import dotenv_values


# Default path for the configuration file, relative to the project root.
_DEFAULT_CONFIG_FILENAME = "config.yaml"

# Default path for the messages file, relative to the project root.
_DEFAULT_MESSAGES_FILE = "data/messages.json"


@dataclass
class Config:
    """Application configuration.

    Attributes:
        provider: Name of the translation provider ("deepl", "azure").
        api_key: API authentication key (resolved value, not the env reference).
        source_language: ISO code for the source language (e.g., "ES").
        target_languages: List of ISO codes for target languages.
        messages_file: Path to the messages JSON file.
        azure_region: Azure region (only used with the Azure provider).
        project_root: Absolute path to the project root directory.
    """
    provider: str = "deepl"
    api_key: str = ""
    source_language: str = "ES"
    target_languages: list[str] = field(default_factory=lambda: ["EN", "PT-BR"])
    messages_file: str = _DEFAULT_MESSAGES_FILE
    azure_region: str = "westeurope"
    project_root: Path = field(default_factory=lambda: Path.cwd())


def _resolve_api_key(raw_value: str, project_root: Path) -> str:
    """Resolve an API key value that may reference an environment variable.

    If the value starts with "env:", the remainder is treated as the name
    of an environment variable. The variable is looked up first in the
    .env file at the project root, then in the system environment.

    Args:
        raw_value: The raw API key string from config.yaml.
        project_root: Path to the project root (for locating .env).

    Returns:
        The resolved API key string.

    Raises:
        ValueError: If the environment variable is referenced but not set.
    """
    if not raw_value.startswith("env:"):
        return raw_value

    env_var_name = raw_value[4:].strip()

    # Attempt to load from .env file first.
    env_file = project_root / ".env"
    if env_file.exists():
        env_values = dotenv_values(env_file)
        value = env_values.get(env_var_name)
        if value:
            return value.strip().strip("'\"")

    # Fall back to system environment.
    import os
    value = os.environ.get(env_var_name)
    if value:
        return value.strip()

    raise ValueError(
        f"API key references environment variable '{env_var_name}', "
        f"but it is not set in .env or system environment."
    )


def load_config(project_root: Optional[Path] = None) -> Config:
    """Load configuration from config.yaml.

    Args:
        project_root: Path to the project root directory. Defaults to
            the current working directory.

    Returns:
        A populated Config instance.

    Raises:
        FileNotFoundError: If config.yaml does not exist. The user should
            run 'i18n setup' to create it.
        ValueError: If required configuration values are missing or invalid.
    """
    if project_root is None:
        project_root = Path.cwd()

    config_path = project_root / _DEFAULT_CONFIG_FILENAME

    if not config_path.exists():
        raise FileNotFoundError(
            f"Configuration file not found at '{config_path}'. "
            f"Run 'i18n setup' to create one."
        )

    with open(config_path, "r", encoding="utf-8") as f:
        raw = yaml.safe_load(f)

    if not isinstance(raw, dict):
        raise ValueError(f"Invalid configuration format in '{config_path}'.")

    provider = raw.get("provider", "deepl")
    raw_api_key = raw.get("api_key", "")
    source_language = raw.get("source_language", "ES")
    target_languages = raw.get("target_languages", ["EN", "PT-BR"])
    messages_file = raw.get("messages_file", _DEFAULT_MESSAGES_FILE)
    azure_region = raw.get("azure_region", "westeurope")

    api_key = _resolve_api_key(str(raw_api_key), project_root)

    if not api_key:
        raise ValueError(
            "API key is empty. Update 'api_key' in config.yaml or set the "
            "corresponding environment variable."
        )

    if not target_languages:
        raise ValueError("At least one target language must be configured.")

    return Config(
        provider=provider,
        api_key=api_key,
        source_language=source_language.upper(),
        target_languages=[lang.upper() for lang in target_languages],
        messages_file=messages_file,
        azure_region=azure_region,
        project_root=project_root,
    )


def save_config(config: Config) -> Path:
    """Save configuration to config.yaml.

    Args:
        config: The Config instance to persist.

    Returns:
        The path to the saved configuration file.
    """
    config_path = config.project_root / _DEFAULT_CONFIG_FILENAME

    data = {
        "provider": config.provider,
        "api_key": config.api_key,
        "source_language": config.source_language,
        "target_languages": config.target_languages,
        "messages_file": config.messages_file,
    }

    # Include Azure-specific settings only when relevant.
    if config.provider == "azure":
        data["azure_region"] = config.azure_region

    with open(config_path, "w", encoding="utf-8") as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

    return config_path
