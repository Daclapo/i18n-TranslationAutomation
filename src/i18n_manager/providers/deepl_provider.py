"""DeepL translation provider.

Uses the official DeepL Python library to perform translations.
Requires a valid DeepL API key (free or pro tier).

DeepL language codes:
    - Source: "ES", "EN", "PT", etc.
    - Target: "EN-US", "EN-GB", "PT-BR", "PT-PT", etc.
    For target languages, DeepL sometimes requires the regional variant.
    This provider maps common short codes to their DeepL equivalents.
"""

import deepl

from i18n_manager.providers.base import TranslationProvider


# Mapping of short language codes to DeepL-specific target codes.
# DeepL requires regional variants for certain target languages.
_TARGET_LANG_MAP = {
    "EN": "EN-US",
    "PT": "PT-BR",
}


class DeepLProvider(TranslationProvider):
    """Translation provider using the DeepL API.

    Args:
        api_key: DeepL API authentication key.
        **kwargs: Ignored (allows uniform provider construction).
    """

    def __init__(self, api_key: str, **kwargs):
        self._translator = deepl.Translator(api_key)

    def translate(self, text: str, source_lang: str, target_lang: str) -> str:
        """Translate text using DeepL.

        The method maps short language codes (e.g., "EN") to the regional
        variants that DeepL expects (e.g., "EN-US"). If the target code
        is already a regional variant, it is used as-is.

        Args:
            text: The text to translate.
            source_lang: Source language code (e.g., "ES").
            target_lang: Target language code (e.g., "EN", "PT-BR").

        Returns:
            The translated text.

        Raises:
            RuntimeError: If the DeepL API returns an error.
        """
        deepl_target = _TARGET_LANG_MAP.get(target_lang.upper(), target_lang.upper())

        try:
            result = self._translator.translate_text(
                text,
                source_lang=source_lang.upper(),
                target_lang=deepl_target,
            )
            return result.text
        except deepl.DeepLException as exc:
            raise RuntimeError(
                f"DeepL translation failed ({source_lang} -> {target_lang}): {exc}"
            ) from exc
