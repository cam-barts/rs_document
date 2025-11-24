---
title: Cleaning Text
description: Remove artifacts and normalize text
---

# Cleaning Text

Learn how to clean messy text from PDFs, OCR, and web scraping.

## Why Clean Documents?

Documents from various sources contain artifacts that hurt embedding quality:

- **PDFs**: Ligatures (æ, ﬁ), bullet symbols, extra spaces
- **OCR**: Non-ASCII artifacts, broken paragraphs
- **Web**: HTML entities, inconsistent whitespace

Cleaning normalizes text so embeddings focus on semantic content.

## Clean Everything at Once

The easiest way to clean a document:

```python
from rs_document import Document

doc = Document(
    page_content="●  Text with bullets, æ ligatures, and  extra   spaces!",
    metadata={"source": "messy.pdf"}
)

# Run all cleaners
doc.clean()

print(doc.page_content)
# Output: "Text with bullets, ae ligatures, and extra spaces!"
```

The `.clean()` method runs all cleaners in the right order.

## Individual Cleaners

You can also use specific cleaners:

### Remove Extra Whitespace

Normalize spaces and remove trailing whitespace:

```python
doc = Document(
    page_content="ITEM 1.     BUSINESS ",
    metadata={}
)

doc.clean_extra_whitespace()

print(doc.page_content)  # "ITEM 1. BUSINESS"
```

### Convert Ligatures

Turn typographic ligatures into regular letters:

```python
doc = Document(
    page_content="The encyclopædia has œnology and ﬁsh sections",
    metadata={}
)

doc.clean_ligatures()

print(doc.page_content)
# "The encyclopaedia has oenology and fish sections"
```

Common conversions:

- æ → ae
- œ → oe
- ﬁ → fi
- ﬂ → fl

### Remove Bullets

Clean up bullet symbols from lists:

```python
doc = Document(
    page_content="●  First item\n●  Second item\n●  Third item",
    metadata={}
)

doc.clean_bullets()

print(doc.page_content)
# "First item\nSecond item\nThird item"
```

Removes: ●, ○, ■, □, •, and other bullet symbols.

### Remove Non-ASCII Characters

Strip out non-ASCII characters:

```python
doc = Document(
    page_content="Hello\x88World\x89",
    metadata={}
)

doc.clean_non_ascii_chars()

print(doc.page_content)  # "HelloWorld"
```

**Use carefully**: This also removes accented characters and emoji!

### Group Broken Paragraphs

Fix paragraphs incorrectly split across lines:

```python
doc = Document(
    page_content="This is a sentence\nthat was split\nacross lines.\n\nNew paragraph here.",
    metadata={}
)

doc.group_broken_paragraphs()

# Joins the broken paragraph while preserving the paragraph break
print(doc.page_content)
# "This is a sentence that was split across lines.\n\nNew paragraph here."
```

## Real-World Example

Cleaning a PDF document:

```python
from rs_document import Document

# Load PDF text (using your PDF library)
pdf_text = extract_text_from_pdf("document.pdf")

# Create document
doc = Document(
    page_content=pdf_text,
    metadata={"source": "document.pdf"}
)

# Clean all issues
doc.clean()

# Now the text is ready for embedding
print(f"Cleaned {len(doc.page_content)} characters")
```

## Cleaning Multiple Documents

Process a batch of documents:

```python
from rs_document import Document

documents = [
    Document(page_content="messy text 1", metadata={"id": "1"}),
    Document(page_content="messy text 2", metadata={"id": "2"}),
    # ... more documents
]

# Clean each document
for doc in documents:
    doc.clean()

print(f"Cleaned {len(documents)} documents")
```

## Understanding Cleaner Order

When you call `.clean()`, cleaners run in this order:

1. `clean_extra_whitespace` - Normalize spacing first
2. `clean_ligatures` - Convert to standard characters
3. `clean_bullets` - Remove list markers
4. `clean_non_ascii_chars` - Remove remaining non-ASCII
5. `group_broken_paragraphs` - Fix structure last

This order ensures each cleaner works with normalized input.

## Important Notes

### Cleaning Modifies In-Place

Cleaning changes the document directly:

```python
doc = Document(page_content="original text", metadata={})

# This modifies doc
doc.clean()

# Original content is gone
```

If you need the original, create a copy first:

```python
from rs_document import Document

original = Document(page_content="text", metadata={"id": "1"})

# Make a copy
cleaned = Document(
    page_content=original.page_content,
    metadata=original.metadata.copy()
)

# Clean the copy
cleaned.clean()

# Now you have both versions
```

### Metadata is Preserved

Cleaning never touches metadata:

```python
doc = Document(
    page_content="●  messy text",
    metadata={"source": "file.txt", "page": "5"}
)

doc.clean()

# Metadata unchanged
assert doc.metadata == {"source": "file.txt", "page": "5"}
```

## Next Steps

Now that your text is clean, let's learn how to [split documents](splitting.md) into chunks for embeddings!
