"""
Translation coordinator that routes to appropriate translator.
"""

from ..translators.base_translator import BaseTranslator
from ..translators.cache import TranslationCache
from ..translators.gemini_translator import GeminiTranslator


class Translator:
    """Coordinates translation using configured translator."""

    def __init__(
        self,
        provider: str,
        api_key: str | None = None,
        model: str = "gemini-pro",
        cache_enabled: bool = True,
    ):
        """
        Initialize translator.

        Args:
            provider: Translation provider ('gemini', 'google', etc.)
            api_key: API key for translation service
            model: Model name (for Gemini)
            cache_enabled: Whether to use translation cache
        """
        self.provider = provider
        self.cache = TranslationCache() if cache_enabled else None
        self.translator = self._create_translator(provider, api_key, model)

    def _create_translator(
        self, provider: str, api_key: str | None, model: str
    ) -> BaseTranslator:
        """Create appropriate translator based on provider."""
        if provider == "gemini":
            return GeminiTranslator(api_key=api_key, model=model, cache=self.cache)
        elif provider == "google":
            # TODO: Implement Google Translate
            raise NotImplementedError("Google Translate not yet implemented")
        else:
            raise ValueError(f"Unsupported translation provider: {provider}")

    def translate_content(
        self, content: str, source_lang: str, target_lang: str, layout: str = "parallel"
    ) -> str:
        """
        Translate content with specified layout.

        Args:
            content: Content to translate
            source_lang: Source language
            target_lang: Target language
            layout: Translation layout ('parallel' or 'sequential')

        Returns:
            Translated content with layout applied
        """
        # Split content into paragraphs
        paragraphs = [p.strip() for p in content.split("\n\n") if p.strip()]

        translated_paragraphs = []

        for para in paragraphs:
            # Skip if it's just markdown syntax (images, links, etc.)
            if para.startswith("![") or para.startswith("[") or para.startswith("#"):
                translated_paragraphs.append(para)
                continue

            # Translate paragraph
            translation = self.translator.translate(para, source_lang, target_lang)

            # Apply layout
            if layout == "parallel":
                # Parallel: original followed by translation
                translated_paragraphs.append(para)
                translated_paragraphs.append(translation)
            elif layout == "sequential":
                # Sequential: all original, then all translations
                translated_paragraphs.append(para)
                # Store translation separately (would need to collect all first)
                # For now, use parallel as default
                translated_paragraphs.append(translation)
            else:
                # Default to parallel
                translated_paragraphs.append(para)
                translated_paragraphs.append(translation)

        return "\n\n".join(translated_paragraphs)
