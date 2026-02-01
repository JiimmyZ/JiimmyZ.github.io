"""Cover page generation as Markdown."""


def generate_cover_markdown(title_zh: str, title_en: str) -> str:
    """Generate cover page as Markdown."""
    # Use HTML divs with classes for proper styling
    return f"""<div class="cover-page">

<div class="cover-title-zh">{title_zh}</div>

<div class="cover-divider"></div>

<div class="cover-title-en">{title_en}</div>

</div>

---
"""
