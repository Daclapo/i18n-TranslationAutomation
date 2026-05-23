"""Abstract base class for translation providers.

All translation providers must extend TranslationProvider and implement the
translate() method. This allows the system to support multiple translation
APIs (DeepL, Azure, etc.) through a unified interface.

To add a custom provider:
    1. Create a new file in src/i18n_manager/providers/
    2. Define a class extending TranslationProvider
    3. Implement the translate() method
    4. Register the class in providers/__init__.py PROVIDER_REGISTRY
"""

from abc import ABC, abstractmethod


class TranslationProvider(ABC):
    """Base interface that all translation providers must implement.

    Each provider is responsible for translating a single text string
    from a source language to a target language. The provider handles
    its own authentication and API communication.
    """

    @abstractmethod
    def translate(self, text: str, source_lang: str, target_lang: str) -> str:
        """Translate a text string from one language to another.

        Args:
            text: The text to translate.
            source_lang: ISO language code of the source language (e.g., "ES").
            target_lang: ISO language code of the target language (e.g., "EN", "PT-BR").

        Returns:
            The translated text as a string.

        Raises:
            ConnectionError: If the API is unreachable.
            RuntimeError: If the translation fails for any reason.
        """
        ...
