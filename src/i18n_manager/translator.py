"""Translation orchestration layer.

Coordinates between the configuration, translation provider, and storage
modules. Provides a high-level interface for translating text from the
source language into all configured target languages.
"""

from i18n_manager.config import Config
from i18n_manager.providers import get_provider
from i18n_manager.providers.base import TranslationProvider


class Translator:
    """Orchestrates translations using the configured provider.

    Attributes:
        config: The application configuration.
        provider: The instantiated translation provider.
    """

    def __init__(self, config: Config):
        """Initialize the translator with the given configuration.

        Args:
            config: Application configuration specifying the provider,
                API key, source language, and target languages.
        """
        self.config = config
        self.provider: TranslationProvider = get_provider(
            name=config.provider,
            api_key=config.api_key,
            azure_region=config.azure_region,
        )

    def translate_text(self, text: str) -> dict[str, str]:
        """Translate a text from the source language to all target languages.

        The source text is included in the returned dictionary alongside
        all generated translations.

        Args:
            text: The text in the source language.

        Returns:
            A dictionary mapping each language code to its text.
            Example: {"es": "Hola", "en": "Hello", "pt-br": "Ola"}

        Raises:
            RuntimeError: If any translation fails.
        """
        source_lang = self.config.source_language
        translations = {source_lang.lower(): text}

        for target_lang in self.config.target_languages:
            translated = self.provider.translate(
                text=text,
                source_lang=source_lang,
                target_lang=target_lang,
            )
            translations[target_lang.lower()] = translated

        return translations
