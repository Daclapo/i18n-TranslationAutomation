"""Unit tests for the translator module.

Tests verify provider instantiation, translation orchestration, and error
handling. All translation API calls are mocked to avoid external dependencies.
"""

import pytest
from unittest.mock import MagicMock, patch

from i18n_manager.config import Config
from i18n_manager.translator import Translator
from i18n_manager.providers.base import TranslationProvider


class MockProvider(TranslationProvider):
    """A mock translation provider for testing purposes.

    Returns a predictable string indicating the target language.
    """

    def translate(self, text: str, source_lang: str, target_lang: str) -> str:
        return f"[{target_lang}] {text}"


class TestTranslator:
    """Tests for the Translator orchestration class."""

    def _make_config(self, **overrides) -> Config:
        """Create a Config instance with sensible defaults for testing."""
        defaults = {
            "provider": "deepl",
            "api_key": "test-key",
            "source_language": "ES",
            "target_languages": ["EN", "PT-BR"],
            "messages_file": "data/messages.json",
        }
        defaults.update(overrides)
        return Config(**defaults)

    @patch("i18n_manager.translator.get_provider")
    def test_translate_text_returns_all_languages(self, mock_get_provider):
        mock_get_provider.return_value = MockProvider()
        config = self._make_config()
        translator = Translator(config)

        result = translator.translate_text("Hola mundo")

        assert "es" in result
        assert result["es"] == "Hola mundo"
        assert "en" in result
        assert "[EN] Hola mundo" == result["en"]
        assert "pt-br" in result
        assert "[PT-BR] Hola mundo" == result["pt-br"]

    @patch("i18n_manager.translator.get_provider")
    def test_translate_text_with_single_target(self, mock_get_provider):
        mock_get_provider.return_value = MockProvider()
        config = self._make_config(target_languages=["EN"])
        translator = Translator(config)

        result = translator.translate_text("Prueba")

        assert len(result) == 2
        assert "es" in result
        assert "en" in result

    @patch("i18n_manager.translator.get_provider")
    def test_translate_text_propagates_provider_error(self, mock_get_provider):
        failing_provider = MagicMock(spec=TranslationProvider)
        failing_provider.translate.side_effect = RuntimeError("API quota exceeded")
        mock_get_provider.return_value = failing_provider

        config = self._make_config()
        translator = Translator(config)

        with pytest.raises(RuntimeError, match="API quota exceeded"):
            translator.translate_text("Este texto fallara")

    @patch("i18n_manager.translator.get_provider")
    def test_translate_text_with_multiple_targets(self, mock_get_provider):
        mock_get_provider.return_value = MockProvider()
        config = self._make_config(target_languages=["EN", "PT-BR", "FR", "DE"])
        translator = Translator(config)

        result = translator.translate_text("Texto")

        assert len(result) == 5  # source + 4 targets
        for lang in ["es", "en", "pt-br", "fr", "de"]:
            assert lang in result
