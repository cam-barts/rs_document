---
title: Cleaning Methods
description: Document cleaning methods for text normalization and artifact removal
---

# Cleaning Methods

All cleaning methods modify the document in-place and return `None`. They are designed to clean and normalize text extracted from PDFs, web pages, and other sources.

## Overview

Cleaning methods are called on `Document` instances:

```python
from rs_document import Document

doc = Document(page_content="Raw text", metadata={})
doc.clean()  # Modifies doc.page_content in-place
```

**Important:** All cleaning methods modify the document's `page_content` directly. The original content is not preserved. If you need to keep the original, create a copy first.

## Methods

### `clean()`

Run all available cleaners in sequence.

**Signature:**

```python
doc.clean() -> None
```

**Description:**

Applies all cleaning operations in a specific order. This is the most convenient method for general-purpose cleaning.

**Execution Order:**

1. `clean_extra_whitespace()` - Normalize whitespace
2. `clean_ligatures()` - Convert typographic ligatures
3. `clean_bullets()` - Remove bullet characters
4. `clean_non_ascii_chars()` - Remove non-ASCII characters
5. `group_broken_paragraphs()` - Join split paragraphs

**Parameters:**

None.

**Returns:**

`None` - Modifies the document in-place.

**Example:**

```python
doc = Document(
    page_content="●  Text with   spaces and æ ligatures\x88",
    metadata={}
)

doc.clean()

# All cleaning operations applied:
# - Extra whitespace normalized
# - Ligature 'æ' converted to 'ae'
# - Bullet '●' removed
# - Non-ASCII character '\x88' removed
print(doc.page_content)  # "Text with spaces and ae ligatures"
```

**Use Cases:**

- General-purpose document cleaning
- Preparing text for analysis or embedding
- Sanitizing text from unknown sources

**Note:** The order is fixed and cannot be customized. If you need a different order or subset of operations, call individual cleaning methods directly.

---

### `clean_extra_whitespace()`

Normalize whitespace in the document.

**Signature:**

```python
doc.clean_extra_whitespace() -> None
```

**Description:**

Normalizes all whitespace in the document by:

- Replacing multiple consecutive spaces with a single space
- Removing leading and trailing whitespace from lines
- Preserving newlines and paragraph structure

**Parameters:**

None.

**Returns:**

`None` - Modifies the document in-place.

**Example:**

```python
doc = Document(
    page_content="ITEM 1.     BUSINESS ",
    metadata={}
)

doc.clean_extra_whitespace()

print(doc.page_content)  # "ITEM 1. BUSINESS"
print(repr(doc.page_content))  # Shows no trailing or extra spaces
```

**Complex Example:**

```python
doc = Document(
    page_content="Line 1    with    spaces\n   Line 2   \n\nLine 3  ",
    metadata={}
)

doc.clean_extra_whitespace()

print(doc.page_content)
# "Line 1 with spaces\nLine 2\n\nLine 3"
# - Multiple spaces reduced to one
# - Leading/trailing spaces removed from each line
# - Newlines preserved
```

**What is Preserved:**

- Single newlines (`\n`)
- Paragraph breaks (double newlines `\n\n`)
- Document structure

**What is Removed:**

- Multiple consecutive spaces
- Leading spaces on lines
- Trailing spaces on lines
- Tabs are converted to spaces

**Use Cases:**

- Cleaning up OCR output
- Normalizing text from PDFs with poor formatting
- Removing formatting artifacts from copied text
- Preparing text for tokenization or analysis

---

### `clean_ligatures()`

Convert typographic ligatures to their component characters.

**Signature:**

```python
doc.clean_ligatures() -> None
```

**Description:**

Replaces typographic ligatures with their expanded character sequences. Ligatures are single characters representing multiple letters, commonly found in typeset documents and PDFs.

**Parameters:**

None.

**Returns:**

`None` - Modifies the document in-place.

**Ligature Conversions:**

| Ligature | Converted To | Unicode |
|----------|--------------|---------|
| `æ` | `ae` | U+00E6 |
| `Æ` | `AE` | U+00C6 |
| `œ` | `oe` | U+0153 |
| `Œ` | `OE` | U+0152 |
| `ﬁ` | `fi` | U+FB01 |
| `ﬂ` | `fl` | U+FB02 |
| `ﬀ` | `ff` | U+FB00 |
| `ﬃ` | `ffi` | U+FB03 |
| `ﬄ` | `ffl` | U+FB04 |
| `ﬅ` | `ft` | U+FB05 |
| `ﬆ` | `st` | U+FB06 |

**Example:**

```python
doc = Document(
    page_content="The encyclopædia has œnology section",
    metadata={}
)

doc.clean_ligatures()

print(doc.page_content)  # "The encyclopaedia has oenology section"
```

**PDF Example:**

```python
# Text extracted from a PDF may contain ligatures
doc = Document(
    page_content="The ofﬁce ﬂoor has ﬁne ﬁnishes",
    metadata={"source": "document.pdf"}
)

doc.clean_ligatures()

print(doc.page_content)  # "The office floor has fine finishes"
```

**Use Cases:**

- Normalizing text from PDFs
- Cleaning text from typeset documents
- Improving search and matching (ligatures may not match regular searches)
- Preparing text for NLP or embedding models

**Note:** This only affects actual ligature characters. Regular letter combinations (like "ae" or "fi") are not modified.

---

### `clean_bullets()`

Remove bullet point characters from the text.

**Signature:**

```python
doc.clean_bullets() -> None
```

**Description:**

Removes common bullet point characters used in lists. The bullet characters are deleted completely (not replaced with anything).

**Parameters:**

None.

**Returns:**

`None` - Modifies the document in-place.

**Removed Characters:**

- `●` (U+25CF - Black Circle)
- `○` (U+25CB - White Circle)
- `■` (U+25A0 - Black Square)
- `□` (U+25A1 - White Square)
- `•` (U+2022 - Bullet)
- `◦` (U+25E6 - White Bullet)
- `▪` (U+25AA - Black Small Square)
- `▫` (U+25AB - White Small Square)

**Example:**

```python
doc = Document(
    page_content="● First item\n● Second item\n● Third item",
    metadata={}
)

doc.clean_bullets()

print(doc.page_content)
# "First item\nSecond item\nThird item"
```

**PDF List Example:**

```python
# Common in PDF extractions
doc = Document(
    page_content="Key Points:\n■ Point one\n■ Point two\n□ Sub-point",
    metadata={}
)

doc.clean_bullets()

print(doc.page_content)
# "Key Points:\nPoint one\nPoint two\nSub-point"
```

**Combined with Whitespace Cleaning:**

```python
doc = Document(
    page_content="●  Item with extra spaces",
    metadata={}
)

doc.clean_bullets()
doc.clean_extra_whitespace()

print(doc.page_content)  # "Item with extra spaces"
```

**Use Cases:**

- Cleaning bulleted lists from PDFs
- Removing formatting artifacts from web content
- Preparing text for analysis where bullets are not needed
- Normalizing list formatting

**Note:** This only removes the bullet characters themselves. List structure (newlines and indentation) is preserved.

---

### `clean_non_ascii_chars()`

Remove all non-ASCII characters from the document.

**Signature:**

```python
doc.clean_non_ascii_chars() -> None
```

**Description:**

Removes any character with an ASCII value greater than 127. This includes:

- Extended Unicode characters
- Accented letters (é, ñ, ü, etc.)
- Special symbols and emoji
- Control characters beyond basic ASCII

**What is Kept:**

Standard ASCII characters (0-127):

- Letters: `a-z`, `A-Z`
- Numbers: `0-9`
- Punctuation: `. , ! ? ; : ' " -` etc.
- Whitespace: space, tab, newline
- Basic symbols: `@ # $ % & * ( ) [ ] { } < > / \` etc.

**Parameters:**

None.

**Returns:**

`None` - Modifies the document in-place.

**Example:**

```python
doc = Document(
    page_content="Hello\x88World\x89",
    metadata={}
)

doc.clean_non_ascii_chars()

print(doc.page_content)  # "HelloWorld"
```

**Complex Example:**

```python
doc = Document(
    page_content="Café résumé 中文 emoji😀 special™ characters©",
    metadata={}
)

doc.clean_non_ascii_chars()

print(doc.page_content)
# "Caf rsum  emoji special characters"
# All non-ASCII characters removed
```

**PDF Artifacts Example:**

```python
# PDFs often contain non-ASCII control characters
doc = Document(
    page_content="Text\x00with\x01hidden\x02control\x88chars",
    metadata={}
)

doc.clean_non_ascii_chars()

print(doc.page_content)  # "Textwith\x01hidden\x02controlchars"
# Note: Only chars > 127 removed; ASCII control chars (0-31) remain
```

**Use Cases:**

- Sanitizing text for ASCII-only systems
- Removing PDF extraction artifacts
- Cleaning text for systems with poor Unicode support
- Removing special characters before processing

**Warning:** This is a destructive operation that removes all accented characters and non-English text. Use with caution:

```python
doc = Document(page_content="Résumé: José García", metadata={})
doc.clean_non_ascii_chars()
print(doc.page_content)  # "Rsum: Jos Garca" - information lost!
```

**Alternative:** Consider `clean_ligatures()` for preserving character information while normalizing ligatures specifically.

---

### `group_broken_paragraphs()`

Join paragraphs that were incorrectly split across multiple lines.

**Signature:**

```python
doc.group_broken_paragraphs() -> None
```

**Description:**

Identifies and joins lines that should be part of the same paragraph. This is especially useful for text extracted from PDFs, where line breaks often don't correspond to semantic paragraph boundaries.

**What it Does:**

- Identifies lines that are part of the same paragraph
- Joins them with appropriate spacing
- Preserves intentional paragraph breaks (double newlines)
- Maintains document structure

**Parameters:**

None.

**Returns:**

`None` - Modifies the document in-place.

**Example:**

```python
doc = Document(
    page_content="This is a sentence\nthat was split\nacross lines.\n\nNew paragraph.",
    metadata={}
)

doc.group_broken_paragraphs()

# The first paragraph is joined, but the paragraph break is preserved
print(doc.page_content)
# "This is a sentence that was split across lines.\n\nNew paragraph."
```

**PDF Extraction Example:**

```python
# Common issue with PDF extraction
doc = Document(
    page_content="""The quick brown fox jumps
over the lazy dog. This is
a continuous paragraph that
was split by page width.

This is a new paragraph after
a blank line.""",
    metadata={"source": "document.pdf"}
)

doc.group_broken_paragraphs()

print(doc.page_content)
# "The quick brown fox jumps over the lazy dog. This is a continuous
# paragraph that was split by page width.
#
# This is a new paragraph after a blank line."
```

**What is Preserved:**

- Paragraph breaks (double newlines or blank lines)
- Document structure and sections
- Intentional formatting

**What is Modified:**

- Single newlines within paragraphs are converted to spaces
- Lines are joined when they appear to be part of the same thought
- Broken sentences are reassembled

**Use Cases:**

- Fixing text extracted from PDFs where line breaks don't match semantic structure
- Cleaning documents with arbitrary line wrapping
- Improving readability of extracted text
- Preparing documents for semantic analysis or embedding

**Combined Usage:**

```python
# Typical cleaning sequence for PDF text
doc = Document(page_content=pdf_text, metadata={"source": "doc.pdf"})

doc.clean_extra_whitespace()    # First, normalize spacing
doc.group_broken_paragraphs()   # Then, join broken paragraphs
doc.clean_ligatures()            # Finally, convert ligatures

# Or just use clean() for all operations
doc.clean()
```

---

## Method Comparison

| Method | Purpose | Preserves Structure | Typical Use |
|--------|---------|---------------------|-------------|
| `clean()` | Apply all cleaners | Mostly | General cleaning |
| `clean_extra_whitespace()` | Normalize spaces | Yes | OCR cleanup |
| `clean_ligatures()` | Expand ligatures | Yes | PDF normalization |
| `clean_bullets()` | Remove bullets | Yes | List cleaning |
| `clean_non_ascii_chars()` | ASCII only | Yes | Sanitization |
| `group_broken_paragraphs()` | Join paragraphs | Partial | PDF paragraph fixing |

## Common Patterns

### Full Cleaning Pipeline

```python
from rs_document import Document

doc = Document(page_content=raw_text, metadata={"source": "file.pdf"})
doc.clean()  # Run all cleaners in optimal order
```

### Selective Cleaning

```python
# Only specific operations needed
doc = Document(page_content=text, metadata={})
doc.clean_extra_whitespace()
doc.clean_ligatures()
# Skip bullet/ASCII cleaning
```

### Preserve Original

```python
# Keep original content
original_content = doc.page_content
doc.clean()
# Can still access original_content variable
```

### Custom Order

```python
# Different order than clean() method
doc = Document(page_content=text, metadata={})
doc.group_broken_paragraphs()  # First, fix structure
doc.clean_extra_whitespace()   # Then, normalize
doc.clean_bullets()             # Then, remove bullets
# Skip ligatures and non-ASCII
```

## See Also

- [Document Class](document-class.md) - Document creation and attributes
- [Splitting Methods](splitting-methods.md) - Split documents after cleaning
- [Utility Functions](utility-functions.md) - Batch processing with cleaning
