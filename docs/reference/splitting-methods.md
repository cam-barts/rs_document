---
title: Splitting Methods
description: Document splitting methods for chunking text into smaller pieces
---

# Splitting Methods

Methods for splitting documents into smaller chunks. All splitting methods return a list of new `Document` instances, leaving the original document unchanged.

## Overview

Splitting methods create new documents from the original:

```python
from rs_document import Document

doc = Document(page_content="Long text...", metadata={"source": "file.txt"})
chunks = doc.recursive_character_splitter(1000)

# Original document is unchanged
print(doc.page_content)  # Still "Long text..."

# New documents created
print(len(chunks))  # Number of chunks
print(chunks[0].metadata)  # {"source": "file.txt"} - metadata copied
```

## Methods

### `recursive_character_splitter()`

Split document into chunks using recursive strategy with natural language boundaries.

**Signature:**

```python
doc.recursive_character_splitter(chunk_size: int) -> list[Document]
```

**Description:**

Splits a document into chunks of approximately `chunk_size` characters, attempting to split on natural language boundaries. Uses a recursive approach, trying multiple separators in order of preference.

**Parameters:**

- **`chunk_size`** (`int`): Target size for each chunk in characters. Chunks will not exceed this size.

**Returns:**

`list[Document]` - List of Document instances, each with:

- `page_content`: A chunk of the original text (≤ `chunk_size` characters)
- `metadata`: Copy of the original document's metadata

**Splitting Strategy:**

The method tries separators in this order of preference:

1. **Paragraph breaks** (`\n\n`) - Preferred for maintaining semantic coherence
2. **Line breaks** (`\n`) - If paragraphs are too large
3. **Word boundaries** (spaces) - If lines are too large
4. **Character boundaries** - Last resort if words are too large

**Chunk Overlap:**

Creates approximately **33% overlap** between consecutive chunks. This overlap is hardcoded and ensures context is preserved across chunk boundaries.

**Example:**

```python
doc = Document(
    page_content="A" * 5000,
    metadata={"source": "file.txt"}
)

chunks = doc.recursive_character_splitter(1000)

print(len(chunks))  # Number of chunks created (approximately 5-7 due to overlap)
print(len(chunks[0].page_content))  # ~1000 or less
print(len(chunks[1].page_content))  # ~1000 or less
print(chunks[0].metadata)  # {"source": "file.txt"}
print(chunks[1].metadata)  # {"source": "file.txt"}
```

**Paragraph Splitting Example:**

```python
doc = Document(
    page_content="""First paragraph with some content.

Second paragraph with more content.

Third paragraph with even more content.""",
    metadata={"doc_id": "123"}
)

chunks = doc.recursive_character_splitter(50)

# Splits on paragraph breaks when possible
for i, chunk in enumerate(chunks):
    print(f"Chunk {i}: {chunk.page_content[:30]}...")
    print(f"Length: {len(chunk.page_content)}")
```

**Overlap Demonstration:**

```python
doc = Document(
    page_content="Word " * 1000,  # 5000 characters
    metadata={}
)

chunks = doc.recursive_character_splitter(100)

# Check overlap between consecutive chunks
chunk1_end = chunks[0].page_content[-20:]
chunk2_start = chunks[1].page_content[:20]

print(f"End of chunk 1: '{chunk1_end}'")
print(f"Start of chunk 2: '{chunk2_start}'")
# Likely to see overlapping content
```

**Edge Cases:**

```python
# Empty document
doc = Document(page_content="", metadata={})
chunks = doc.recursive_character_splitter(1000)
print(chunks)  # []

# Short document (smaller than chunk_size)
doc = Document(page_content="Short", metadata={})
chunks = doc.recursive_character_splitter(1000)
print(len(chunks))  # 1
print(chunks[0].page_content)  # "Short"

# Very long single word (no spaces)
doc = Document(page_content="A" * 5000, metadata={})
chunks = doc.recursive_character_splitter(1000)
# Will split by characters as last resort
```

**Characteristics:**

- **Respects boundaries**: Prefers paragraph, then line, then word boundaries
- **Overlap**: ~33% overlap between chunks (hardcoded)
- **Metadata preservation**: All chunks receive copy of original metadata
- **Size guarantee**: No chunk exceeds `chunk_size`
- **Context preservation**: Overlap ensures semantic context across boundaries

**Use Cases:**

- **RAG applications**: When context is important for retrieval
- **Semantic search**: Maintaining paragraph coherence
- **Question answering**: Overlapping chunks help answer questions at boundaries
- **Document analysis**: Preserving document structure

**Performance:**

```python
import time
from rs_document import Document

doc = Document(page_content="A" * 1_000_000, metadata={})

start = time.time()
chunks = doc.recursive_character_splitter(1000)
elapsed = time.time() - start

print(f"Split into {len(chunks)} chunks in {elapsed:.3f} seconds")
# Fast even for large documents (Rust implementation)
```

**Comparison with `split_on_num_characters()`:**

| Feature | `recursive_character_splitter()` | `split_on_num_characters()` |
|---------|----------------------------------|------------------------------|
| Boundary respect | Yes (paragraph → line → word → char) | No (exact character positions) |
| Overlap | Yes (~33%) | No |
| Chunk size | Target (may be smaller) | Exact (except last chunk) |
| Use case | RAG, semantic applications | Uniform processing |

---

### `split_on_num_characters()`

Split document into chunks of exactly the specified size with no overlap.

**Signature:**

```python
doc.split_on_num_characters(num_chars: int) -> list[Document]
```

**Description:**

Splits a document into fixed-size chunks at exact character boundaries. Does not consider word, line, or paragraph boundaries. Creates no overlap between chunks.

**Parameters:**

- **`num_chars`** (`int`): Number of characters per chunk

**Returns:**

`list[Document]` - List of Document instances, each with:

- `page_content`: Exactly `num_chars` characters (except possibly the last chunk)
- `metadata`: Copy of the original document's metadata

**Example:**

```python
doc = Document(
    page_content="ABCDEFGHIJ",
    metadata={"id": "123"}
)

chunks = doc.split_on_num_characters(3)

print(len(chunks))  # 4
print([c.page_content for c in chunks])  # ["ABC", "DEF", "GHI", "J"]
print(chunks[0].metadata)  # {"id": "123"}
print(chunks[1].metadata)  # {"id": "123"}
```

**Longer Example:**

```python
doc = Document(
    page_content="The quick brown fox jumps over the lazy dog",
    metadata={"source": "example"}
)

chunks = doc.split_on_num_characters(10)

for i, chunk in enumerate(chunks):
    print(f"Chunk {i}: '{chunk.page_content}'")

# Output:
# Chunk 0: 'The quick '
# Chunk 1: 'brown fox '
# Chunk 2: 'jumps over'
# Chunk 3: ' the lazy '
# Chunk 4: 'dog'
```

**Edge Cases:**

```python
# Empty document
doc = Document(page_content="", metadata={})
chunks = doc.split_on_num_characters(10)
print(chunks)  # []

# Document smaller than chunk size
doc = Document(page_content="Hello", metadata={})
chunks = doc.split_on_num_characters(100)
print(len(chunks))  # 1
print(chunks[0].page_content)  # "Hello"

# Exact multiple
doc = Document(page_content="ABCDEFGHIJKL", metadata={})
chunks = doc.split_on_num_characters(4)
print([c.page_content for c in chunks])  # ["ABCD", "EFGH", "IJKL"]

# Last chunk smaller
doc = Document(page_content="ABCDEFGHIJ", metadata={})
chunks = doc.split_on_num_characters(4)
print([c.page_content for c in chunks])  # ["ABCD", "EFGH", "IJ"]
```

**Word Splitting Demonstration:**

```python
# This method WILL split words mid-character
doc = Document(
    page_content="Supercalifragilisticexpialidocious",
    metadata={}
)

chunks = doc.split_on_num_characters(10)

for chunk in chunks:
    print(chunk.page_content)

# Output:
# Supercalif
# ragilistic
# expialidoc
# ious
# Note: Words are split without regard for boundaries
```

**Characteristics:**

- **Fixed size**: All chunks exactly `num_chars` characters (except last)
- **No overlap**: Chunks are consecutive with no shared content
- **No boundary respect**: Splits at exact character positions
- **Simple**: Predictable, straightforward splitting
- **Metadata preservation**: All chunks receive copy of original metadata

**Use Cases:**

- **Fixed-size processing**: When exact chunk sizes are required
- **Token limit compliance**: Ensuring chunks fit within strict limits
- **Uniform analysis**: When all chunks should have same size
- **Simple splitting**: When semantic boundaries don't matter

**Performance:**

```python
import time
from rs_document import Document

doc = Document(page_content="X" * 1_000_000, metadata={})

start = time.time()
chunks = doc.split_on_num_characters(1000)
elapsed = time.time() - start

print(f"Split into {len(chunks)} chunks in {elapsed:.3f} seconds")
# Very fast - simpler algorithm than recursive splitter
```

**When to Use:**

Choose `split_on_num_characters()` when:

- Exact chunk sizes are required
- Semantic boundaries are not important
- You need predictable, uniform chunks
- You're processing text that doesn't have natural structure

Choose `recursive_character_splitter()` when:

- Semantic coherence matters
- You need context across chunks (overlap)
- Natural language boundaries should be preserved
- You're building RAG or search applications

---

## Method Comparison

### Feature Comparison Table

| Feature | `recursive_character_splitter()` | `split_on_num_characters()` |
|---------|----------------------------------|------------------------------|
| **Chunk Size** | Target (may be smaller) | Exact (except last chunk) |
| **Overlap** | Yes (~33% hardcoded) | No |
| **Boundary Respect** | Yes (paragraph → line → word → char) | No |
| **Speed** | Fast | Very fast |
| **Predictability** | Chunk sizes vary | Chunk sizes fixed |
| **Context Preservation** | Good (overlap) | None |
| **Use Case** | RAG, semantic search, QA | Token limits, uniform processing |
| **Best For** | Natural language text | Any text, fixed requirements |

### Visual Comparison

**`recursive_character_splitter(chunk_size=20)`:**

```text
Original: "The quick brown fox jumps over the lazy dog"

Chunk 1: "The quick brown"       (15 chars)
Chunk 2: "brown fox jumps"       (15 chars) - overlap: "brown"
Chunk 3: "jumps over the"        (14 chars) - overlap: "jumps"
Chunk 4: "the lazy dog"          (12 chars) - overlap: "the"
```

**`split_on_num_characters(num_chars=20)`:**

```text
Original: "The quick brown fox jumps over the lazy dog"

Chunk 1: "The quick brown fox "  (20 chars)
Chunk 2: "jumps over the lazy "  (20 chars)
Chunk 3: "dog"                   (3 chars)
```

## Common Patterns

### Basic Splitting

```python
from rs_document import Document

# Create document
doc = Document(page_content=long_text, metadata={"source": "doc.txt"})

# Split for RAG
chunks = doc.recursive_character_splitter(1000)

# Or split uniformly
chunks = doc.split_on_num_characters(1000)
```

### Clean Then Split

```python
doc = Document(page_content=pdf_text, metadata={"source": "doc.pdf"})

# Clean first
doc.clean()

# Then split
chunks = doc.recursive_character_splitter(1000)
```

### Preserving Original

```python
# Original document is not modified by splitting
doc = Document(page_content="Original text", metadata={})
chunks = doc.recursive_character_splitter(100)

print(doc.page_content)  # Still "Original text"
print(len(chunks))  # 1
```

### Different Chunk Sizes

```python
doc = Document(page_content=long_text, metadata={})

# Try different sizes
small_chunks = doc.recursive_character_splitter(500)   # More chunks
medium_chunks = doc.recursive_character_splitter(1000)  # Balanced
large_chunks = doc.recursive_character_splitter(2000)  # Fewer chunks

print(f"500: {len(small_chunks)} chunks")
print(f"1000: {len(medium_chunks)} chunks")
print(f"2000: {len(large_chunks)} chunks")
```

### Metadata Tracking

```python
doc = Document(
    page_content=long_text,
    metadata={"source": "doc.txt", "page": "5", "section": "intro"}
)

chunks = doc.recursive_character_splitter(1000)

# All chunks have same metadata
for i, chunk in enumerate(chunks):
    # Could add chunk index to metadata
    chunk.metadata["chunk_index"] = str(i)
    chunk.metadata["total_chunks"] = str(len(chunks))

    print(chunk.metadata)
    # {"source": "doc.txt", "page": "5", "section": "intro",
    #  "chunk_index": "0", "total_chunks": "8"}
```

### Multiple Document Splitting

```python
documents = [
    Document(page_content=text1, metadata={"id": "1"}),
    Document(page_content=text2, metadata={"id": "2"}),
    Document(page_content=text3, metadata={"id": "3"}),
]

all_chunks = []
for doc in documents:
    chunks = doc.recursive_character_splitter(1000)
    all_chunks.extend(chunks)

print(f"Split {len(documents)} documents into {len(all_chunks)} chunks")
```

**Better approach:** Use `clean_and_split_docs()` for parallel processing:

```python
from rs_document import clean_and_split_docs

all_chunks = clean_and_split_docs(documents, chunk_size=1000)
# Faster - processes in parallel
```

## See Also

- [Document Class](document-class.md) - Creating documents
- [Cleaning Methods](cleaning-methods.md) - Clean before splitting
- [Utility Functions](utility-functions.md) - Batch splitting with `clean_and_split_docs()`
- [Types and Constants](types-and-constants.md) - Splitter defaults and constants
