"""Translation provider implementations.

Each provider must extend the TranslationProvider base class and implement
the translate() method. See base.py for the interface definition.
"""

from i18n_manager.providers.base import TranslationProvider
from i18n_manager.providers.deepl_provider import DeepLProvider
from i18n_manager.providers.azure_provider import AzureProvider

# Registry mapping provider names to their classes.
# To add a new provider, implement TranslationProvider and register it here.
PROVIDER_REGISTRY: dict[str, type[TranslationProvider]] = {
    "deepl": DeepLProvider,
    "azure": AzureProvider,
}


def get_provider(name: str, **kwargs) -> TranslationProvider:
    """Instantiate a translation provider by its registered name.

    Args:
        name: Provider identifier (e.g., "deepl", "azure").
        **kwargs: Provider-specific configuration passed to the constructor.

    Returns:
        An initialized TranslationProvider instance.

    Raises:
        ValueError: If the provider name is not registered.
    """
    provider_class = PROVIDER_REGISTRY.get(name)
    if provider_class is None:
        available = ", ".join(sorted(PROVIDER_REGISTRY.keys()))
        raise ValueError(
            f"Unknown translation provider: '{name}'. "
            f"Available providers: {available}"
        )
    return provider_class(**kwargs)
