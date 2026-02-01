"""AST-based translation with async Gemini API calls."""

import asyncio
import hashlib
import json
from pathlib import Path

import google.generativeai as genai
from marko.block import Document

from .markdown_parser import extract_text_nodes, update_text_nodes


class ASTTranslator:
    """Translates Markdown AST by processing text nodes concurrently."""

    def __init__(
        self, api_key: str, semaphore_limit: int = 10, cache_path: Path = None
    ):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-pro")
        self.semaphore = asyncio.Semaphore(semaphore_limit)
        self.cache_path = cache_path
        self.cache = self._load_cache()

    def _load_cache(self) -> dict[str, str]:
        """Load translation cache from file."""
        if not self.cache_path or not self.cache_path.exists():
            return {}
        try:
            with open(self.cache_path, encoding="utf-8") as f:
                return json.load(f)
        except (OSError, json.JSONDecodeError):
            return {}

    def _save_cache(self):
        """Save translation cache to file."""
        if not self.cache_path:
            return
        self.cache_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.cache_path, "w", encoding="utf-8") as f:
            json.dump(self.cache, f, ensure_ascii=False, indent=2)

    async def translate_text_node(self, text: str) -> str:
        """Translate single text node with rate limiting."""
        if not text or not text.strip():
            return text

        # Check cache first
        cache_key = hashlib.md5(text.encode("utf-8")).hexdigest()
        if cache_key in self.cache:
            return self.cache[cache_key]

        async with self.semaphore:
            # Async Gemini API call
            try:
                # Use asyncio.to_thread to run synchronous API call in thread pool
                prompt = f"Translate the following Traditional Chinese text to English. Only return the translation, no explanations: {text}"
                response = await asyncio.to_thread(self.model.generate_content, prompt)
                # Access response text safely
                if hasattr(response, "text"):
                    translation = response.text.strip()
                elif hasattr(response, "candidates") and response.candidates:
                    translation = response.candidates[0].content.parts[0].text.strip()
                else:
                    print(f"Unexpected response format for text '{text[:50]}...'")
                    return text

                self.cache[cache_key] = translation
                return translation
            except Exception as e:
                print(f"Translation error for text '{text[:50]}...': {e}")
                return text  # Return original on error

    async def translate_ast(self, ast: Document) -> Document:
        """Translate AST by processing text nodes concurrently."""
        text_nodes = extract_text_nodes(ast)

        if not text_nodes:
            return ast

        # Extract text content from nodes
        text_contents = []
        node_list = []
        for node, _ in text_nodes:
            # Extract text from RawText node
            text = ""
            if (
                hasattr(node, "children")
                and isinstance(node.children, list)
                and len(node.children) > 0
            ):
                # Get first child which should be the text string
                first_child = node.children[0]
                text = first_child if isinstance(first_child, str) else str(first_child)
            # Fallback: try to get text directly from node
            if not text:
                try:
                    text = str(node)
                except Exception:
                    text = ""

            # Only translate non-empty text
            if text and text.strip():
                text_contents.append(text)
                node_list.append(node)

        if not text_contents:
            return ast

        # Batch translate all text nodes concurrently
        tasks = [self.translate_text_node(text) for text in text_contents]
        translations = await asyncio.gather(*tasks)

        # Create translation map
        translation_map = dict(zip(node_list, translations, strict=False))

        # Update AST
        updated_ast = update_text_nodes(ast, translation_map)

        # Save cache periodically
        self._save_cache()

        return updated_ast
