"""Azure Translator provider.

Uses the Azure Cognitive Services Translator REST API to perform translations.
Requires a valid Azure subscription key and region.

Azure Translator API reference:
    https://learn.microsoft.com/en-us/azure/ai-services/translator/

Language codes follow BCP-47 format (e.g., "es", "en", "pt-br").
This provider normalizes the uppercase codes used internally to lowercase
codes expected by Azure.
"""

import requests

from i18n_manager.providers.base import TranslationProvider


_AZURE_ENDPOINT = "https://api.cognitive.microsofttranslator.com"
_API_VERSION = "3.0"


class AzureProvider(TranslationProvider):
    """Translation provider using the Azure Translator API.

    Args:
        api_key: Azure Translator subscription key.
        azure_region: Azure region where the Translator resource is deployed
            (e.g., "westeurope", "eastus").
        **kwargs: Ignored (allows uniform provider construction).
    """

    def __init__(self, api_key: str, azure_region: str = "westeurope", **kwargs):
        self._api_key = api_key
        self._region = azure_region

    def translate(self, text: str, source_lang: str, target_lang: str) -> str:
        """Translate text using Azure Translator.

        Args:
            text: The text to translate.
            source_lang: Source language code (e.g., "ES").
            target_lang: Target language code (e.g., "EN", "PT-BR").

        Returns:
            The translated text.

        Raises:
            RuntimeError: If the Azure API returns an error.
            ConnectionError: If the API endpoint is unreachable.
        """
        url = f"{_AZURE_ENDPOINT}/translate"
        params = {
            "api-version": _API_VERSION,
            "from": source_lang.lower(),
            "to": target_lang.lower(),
        }
        headers = {
            "Ocp-Apim-Subscription-Key": self._api_key,
            "Ocp-Apim-Subscription-Region": self._region,
            "Content-Type": "application/json",
        }
        body = [{"text": text}]

        try:
            response = requests.post(url, params=params, headers=headers, json=body, timeout=30)
            response.raise_for_status()
        except requests.ConnectionError as exc:
            raise ConnectionError(
                f"Could not connect to Azure Translator API: {exc}"
            ) from exc
        except requests.HTTPError as exc:
            raise RuntimeError(
                f"Azure Translator API returned an error: {response.status_code} - {response.text}"
            ) from exc

        data = response.json()

        try:
            return data[0]["translations"][0]["text"]
        except (IndexError, KeyError) as exc:
            raise RuntimeError(
                f"Unexpected response format from Azure Translator: {data}"
            ) from exc
