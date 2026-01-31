# SEO Guidelines for JZ隨筆 Blog

This document provides SEO best practices and guidelines for content creation and optimization on the Hugo blog.

## Table of Contents

- [Title Optimization](#title-optimization)
- [Meta Description](#meta-description)
- [Heading Structure](#heading-structure)
- [Image Optimization](#image-optimization)
- [Internal Linking](#internal-linking)
- [Keyword Usage](#keyword-usage)
- [Content Checklist](#content-checklist)

## Title Optimization

### Best Practices

- **Length**: Keep titles between 50-60 characters for optimal display in search results
- **Uniqueness**: Each page should have a unique title
- **Format**: Use descriptive, keyword-rich titles that accurately represent the content
- **Structure**: For blog posts, format as: `Article Title | Site Name` (automatically handled by theme)

### Examples

✅ **Good Titles:**
- `Camino Ch1 所有的顧慮` (Clear, descriptive)
- `不公 - 新詩創作` (Concise, includes category context)

❌ **Poor Titles:**
- `Chapter 1` (Too generic, not descriptive)
- `Untitled` (No SEO value)

## Meta Description

### Best Practices

- **Length**: Aim for 150-160 characters (optimal for search result snippets)
- **Content**: Write compelling descriptions that encourage clicks
- **Keywords**: Include relevant keywords naturally
- **Uniqueness**: Each page should have a unique description
- **Call to Action**: Consider including a subtle call to action when appropriate

### How to Add Meta Descriptions

Add a `description` field to your content frontmatter:

```yaml
+++
title = "Your Article Title"
date = "2025-01-01"
description = "A compelling 150-160 character description that summarizes your article and includes relevant keywords naturally."
+++
```

### Examples

✅ **Good Description:**
```
description = "探索朝聖之路的心路歷程，從最初的顧慮到最終的完成。分享Camino de Santiago的實用資訊與個人體驗，幫助其他朝聖者準備旅程。"
```

❌ **Poor Description:**
```
description = "Chapter 1"  # Too short, not descriptive
```

## Heading Structure

### Hierarchy

Use proper heading hierarchy for better SEO and accessibility:

- **H1**: Page title (automatically generated, don't add manually)
- **H2**: Main sections
- **H3**: Subsections
- **H4+**: Further subdivisions

### Best Practices

- Use only **one H1** per page (the title)
- Maintain logical hierarchy (don't skip levels)
- Use descriptive headings that include keywords naturally
- Keep headings concise and scannable

### Example Structure

```markdown
# Title (H1 - automatic)

## Main Section (H2)

### Subsection (H3)

## Another Main Section (H2)
```

## Image Optimization

### Alt Text

**Always provide descriptive alt text for images:**

```markdown
![Descriptive alt text describing the image](image-url.jpg)
```

### Best Practices

- **Be Descriptive**: Describe what's in the image, not just "image" or "photo"
- **Include Context**: Mention relevant details that relate to the content
- **Keep It Concise**: Aim for 5-15 words
- **Use Keywords Naturally**: Include relevant keywords when appropriate, but don't keyword stuff
- **For Decorative Images**: Use empty alt text `![ ]` for purely decorative images

### Examples

✅ **Good Alt Text:**
```markdown
![庇里牛斯山脈的壯麗景色，遠山層疊，天空湛藍](https://res.cloudinary.com/.../mountain.jpg)
![Camino朝聖之路的黃色箭頭路標，指向聖地牙哥方向](https://res.cloudinary.com/.../arrow.jpg)
```

❌ **Poor Alt Text:**
```markdown
![image](photo.jpg)  # Not descriptive
![IMG_20250616_132941](photo.jpg)  # Just filename
![mountain mountain mountain beautiful](photo.jpg)  # Keyword stuffing
```

### Image Naming

- Use descriptive filenames before uploading
- Example: `camino-mountain-view.jpg` instead of `IMG_12345.jpg`
- The system will generate fallback alt text from filenames if alt text is missing

### Cloudinary Optimization

Images are automatically optimized via Cloudinary CDN. The system:
- Generates responsive images (srcset)
- Applies lazy loading
- Optimizes file sizes
- Serves WebP format when supported

## Internal Linking

### Best Practices

- **Link to Related Content**: Link to other relevant articles within your blog
- **Use Descriptive Anchor Text**: Use meaningful link text, not "click here"
- **Link Naturally**: Integrate links naturally within content flow
- **Link to Categories**: Link to category pages when relevant
- **Use Tags**: Tag articles appropriately to enable automatic related content discovery

### Examples

✅ **Good Internal Links:**
```markdown
在[Camino Ch1 所有的顧慮](/travelogue/camino/ch1/)中，我分享了出發前的各種擔心...
```

❌ **Poor Internal Links:**
```markdown
點擊[這裡](/travelogue/camino/ch1/)了解更多  # "這裡" is not descriptive
```

## Keyword Usage

### Best Practices

- **Natural Integration**: Use keywords naturally within content
- **Avoid Keyword Stuffing**: Don't repeat keywords excessively
- **Focus on User Intent**: Write for readers first, search engines second
- **Use Synonyms**: Vary your language and use related terms
- **Long-tail Keywords**: Consider targeting longer, more specific phrases

### Keyword Research

For Traditional Chinese content, consider:
- Primary keywords: 詩詞, 文學創作, 朝聖之路, etc.
- Long-tail keywords: 如何準備Camino朝聖之路, 新詩創作技巧, etc.

### Frontmatter Keywords

You can add keywords to frontmatter (optional, tags are preferred):

```yaml
+++
keywords = ["朝聖之路", "Camino", "旅行", "西班牙"]
tags = ["travelogue", "camino", "spain"]
+++
```

## Content Checklist

Before publishing new content, verify:

### Required Elements

- [ ] Unique, descriptive title (50-60 characters)
- [ ] Meta description (150-160 characters)
- [ ] Proper heading hierarchy (H1 → H2 → H3)
- [ ] Alt text for all images
- [ ] At least one internal link to related content
- [ ] Appropriate tags/categories assigned
- [ ] Content is proofread and error-free

### Recommended Elements

- [ ] Featured image (cover.image) for social sharing
- [ ] Table of contents for long articles (ShowToc enabled)
- [ ] Related content links in footer
- [ ] Breadcrumb navigation visible
- [ ] Reading time estimate accurate

### Technical SEO

- [ ] Page loads quickly (check with PageSpeed Insights)
- [ ] Images are optimized (via Cloudinary)
- [ ] Mobile-responsive design
- [ ] Canonical URL is correct
- [ ] No broken links

## Content-Specific Guidelines

### Poetry (詩詞)

- Use descriptive titles that reflect the poem's theme
- Add context in description (e.g., "一首關於...的詩")
- Tag appropriately (新詩, 絕句, 律詩, etc.)

### Travelogue (遊記)

- Include location names in titles
- Use descriptive alt text for travel photos
- Link to related chapters in series
- Add location tags when relevant

### Essays (雜感)

- Focus on clear, descriptive titles
- Use engaging descriptions that hint at the essay's perspective
- Link to related essays on similar topics

## Monitoring & Improvement

### Tools for SEO Monitoring

1. **Google Search Console**
   - Monitor search performance
   - Submit sitemap: `https://jiimmyz.github.io/sitemap.xml`
   - Check for indexing issues

2. **Google Analytics**
   - Track user behavior
   - Monitor traffic sources
   - Analyze popular content

3. **PageSpeed Insights**
   - Check Core Web Vitals
   - Monitor page load performance
   - Identify optimization opportunities

4. **Schema Markup Validator**
   - Validate structured data: https://validator.schema.org/
   - Ensure Article schema is correct

### Regular Maintenance

- Review and update old content descriptions
- Check for broken internal links
- Update alt text for images missing descriptions
- Monitor search rankings for target keywords
- Update sitemap after major content changes

## Additional Resources

- [Hugo SEO Documentation](https://gohugo.io/templates/seo/)
- [Google Search Central](https://developers.google.com/search/docs)
- [Schema.org Documentation](https://schema.org/)
- [Cloudinary Image Optimization](https://cloudinary.com/documentation/image_optimization)

---

**Last Updated**: 2026-02-01  
**Maintained By**: Project maintainers
