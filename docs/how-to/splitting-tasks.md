---
title: Splitting Tasks
description: Split documents using different strategies and chunk sizes
---

# Splitting Tasks

Learn how to split documents into chunks using rs_document's splitting methods.

## Split with Specific Chunk Size

The `recursive_character_splitter()` method is the primary way to split documents:

```python
from rs_document import Document

doc = Document(
    page_content="Your long document text here...",
    metadata={"source": "doc.txt"}
)

# Split into 500-character chunks
small_chunks = doc.recursive_character_splitter(500)

# Split into 2000-character chunks
large_chunks = doc.recursive_character_splitter(2000)

print(f"500-char chunks: {len(small_chunks)}")
print(f"2000-char chunks: {len(large_chunks)}")
```

## Split and Maintain Context

The recursive character splitter automatically creates ~33% overlap between chunks:

```python
from rs_document import Document

doc = Document(
    page_content="Paragraph one.\n\nParagraph two.\n\nParagraph three.",
    metadata={}
)

chunks = doc.recursive_character_splitter(50)

# Adjacent chunks will have overlapping content
for i, chunk in enumerate(chunks):
    print(f"Chunk {i}: {chunk.page_content}")
```

## Split on Exact Boundaries

Use `split_on_num_characters()` for exact splits without overlap:

```python
from rs_document import Document

doc = Document(
    page_content="ABCDEFGHIJKLMNOP",
    metadata={}
)

# Split exactly every 5 characters (no overlap)
chunks = doc.split_on_num_characters(5)

# Result: ["ABCDE", "FGHIJ", "KLMNO", "P"]
```

## How Separator Selection Works

The recursive splitter tries separators in this order:

1. Double newline (`\n\n`) - paragraph breaks
2. Single newline (`\n`) - line breaks
3. Space (``) - word boundaries
4. Empty string (`""`) - character-by-character

```python
from rs_document import Document

# Document with no paragraph breaks, only lines
doc = Document(
    page_content="Line 1\nLine 2\nLine 3\nLine 4",
    metadata={}
)

# Will split on line breaks when possible
chunks = doc.recursive_character_splitter(20)
```

## Handle Different Document Structures

### Well-Structured Text

```python
from rs_document import Document

# Document with clear paragraph breaks
doc = Document(
    page_content="First paragraph.\n\nSecond paragraph.\n\nThird paragraph.",
    metadata={}
)

# Will split on paragraph boundaries
chunks = doc.recursive_character_splitter(100)
```

### Line-Based Text

```python
from rs_document import Document

# Document with single lines
doc = Document(
    page_content="Line 1\nLine 2\nLine 3\nLine 4\nLine 5",
    metadata={}
)

# Will split on line breaks
chunks = doc.recursive_character_splitter(30)
```

### Dense Text

```python
from rs_document import Document

# Document with minimal structure
doc = Document(
    page_content="This is a long continuous paragraph with no breaks just spaces between words",
    metadata={}
)

# Will split on word boundaries
chunks = doc.recursive_character_splitter(25)
```

## Choose Appropriate Chunk Sizes

Consider your use case when selecting chunk size:

```python
from rs_document import Document

doc = Document(page_content="test " * 10000, metadata={})

# Smaller chunks: more chunks, more context overlap
small = doc.recursive_character_splitter(500)
print(f"500 chars: {len(small)} chunks")

# Larger chunks: fewer chunks, less overlap
large = doc.recursive_character_splitter(2000)
print(f"2000 chars: {len(large)} chunks")

# Choose based on:
# - Your embedding model's context window
# - Retrieval granularity needs
# - Memory constraints
```

## Next Steps

- [Process multiple documents](batch-operations.md) efficiently
- [Add chunk metadata](vector-db-prep.md#add-chunk-index-to-metadata) for tracking
- [Prepare for vector databases](vector-db-prep.md)
