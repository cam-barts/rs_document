---
title: Cleaning Tasks
description: Remove bullets, ligatures, and special characters from documents
---

# Cleaning Tasks

Learn how to clean text in documents using various cleaning methods available in rs_document.

## Clean All Issues at Once

The `clean()` method applies all cleaners in sequence:

```python
from rs_document import Document

doc = Document(
    page_content="Smart quotes: "hello" and 'world'\nEm dash: —\nBullets: ● Item",
    metadata={}
)

# Clean everything
doc.clean()
print(doc.page_content)
```

## Remove Specific Types of Issues

Apply individual cleaners for targeted cleaning:

```python
from rs_document import Document

# Document with various issues
doc = Document(
    page_content="●  Item 1\n● Item 2\n\næ special chars",
    metadata={}
)

# Remove just bullets
doc.clean_bullets()

# Remove just ligatures
doc.clean_ligatures()

# Chain multiple cleaners
doc.clean_extra_whitespace()
```

## Available Cleaners

Each cleaner targets specific text issues:

- `clean_bullets()` - Removes bullet points (●, •, ○, etc.)
- `clean_ligatures()` - Converts ligatures (æ, œ) to ASCII equivalents
- `clean_dashes()` - Normalizes em/en dashes to hyphens
- `clean_extra_whitespace()` - Removes excess whitespace
- `clean_headers()` - Cleans markdown-style headers
- `clean_non_ascii()` - Removes non-ASCII characters
- `clean()` - Applies all cleaners in order

## Clean Text Without Modifying Original

Create a copy if you need to preserve the original:

```python
from rs_document import Document

# Original document
original_doc = Document(
    page_content="Original text with ● bullets",
    metadata={"id": "1"}
)

# Create a copy
cleaned_doc = Document(
    page_content=original_doc.page_content,
    metadata=original_doc.metadata.copy()
)

# Clean the copy
cleaned_doc.clean()

# Now you have both versions
print("Original:", original_doc.page_content)
print("Cleaned:", cleaned_doc.page_content)
```

## Handle Documents with Special Characters

```python
from rs_document import Document

# Document with unicode and special characters
doc = Document(
    page_content="Smart quotes: "hello" and 'world'\nEm dash: —\nLigatures: æ œ",
    metadata={}
)

# Clean everything
doc.clean()

# Result will have ASCII-safe versions
print(doc.page_content)
```

## Chain Cleaning Operations

```python
from rs_document import Document

doc = Document(
    page_content="●  Extra   spaces\n\n\n● More bullets—dashes",
    metadata={}
)

# Apply cleaners in specific order
doc.clean_bullets()
doc.clean_dashes()
doc.clean_extra_whitespace()
```

## Batch Cleaning

For multiple documents, use `clean_and_split_docs()`:

```python
from rs_document import clean_and_split_docs, Document

documents = [
    Document(page_content="● Bullet text", metadata={"id": "1"}),
    Document(page_content="Smart "quotes"", metadata={"id": "2"})
]

# Clean and split in one operation
chunks = clean_and_split_docs(documents, chunk_size=1000)
```

See [Batch Operations](batch-operations.md) for more batch processing patterns.

## Next Steps

- [Split cleaned documents](splitting-tasks.md) into chunks
- [Process multiple documents](batch-operations.md) at once
- [Prepare for vector databases](vector-db-prep.md)
