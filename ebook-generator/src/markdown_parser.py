"""Markdown parser using AST for structural integrity."""

from typing import Any

from marko import Markdown
from marko.block import Document
from marko.inline import RawText


def parse_markdown_to_ast(content: str) -> Document:
    """Parse Markdown to Abstract Syntax Tree."""
    md = Markdown()
    return md.parse(content)


def extract_text_nodes(ast: Document) -> list[tuple[Any, list[str]]]:
    """
    Extract all text nodes from AST.
    Returns: [(node, path), ...] for translation
    """
    text_nodes = []

    def traverse(node, path: list[str] = None):
        if path is None:
            path = []
        if isinstance(node, RawText):
            text_nodes.append((node, path.copy()))
        elif hasattr(node, "children"):
            for child in node.children:
                traverse(child, path + [type(node).__name__])

    traverse(ast)
    return text_nodes


def update_text_nodes(ast: Document, translation_map: dict[RawText, str]) -> Document:
    """Update AST text nodes with translations."""

    def traverse_and_replace(node):
        if isinstance(node, RawText):
            if node in translation_map:
                # Replace the text content directly
                new_text = translation_map[node]
                # RawText stores text in children attribute as list
                if hasattr(node, "children"):
                    node.children = [new_text]
                else:
                    # Fallback: create new children list
                    node.children = [new_text]
        elif hasattr(node, "children") and isinstance(node.children, list):
            # Recursively process children
            for i, child in enumerate(node.children):
                if isinstance(child, RawText) and child in translation_map:
                    # Replace the child with new RawText containing translated text
                    new_text = translation_map[child]
                    node.children[i] = RawText(new_text)
                else:
                    traverse_and_replace(child)

    traverse_and_replace(ast)
    return ast


def ast_to_markdown(ast: Document) -> str:
    """Convert AST back to Markdown string."""
    md = Markdown()
    return md.render(ast)
