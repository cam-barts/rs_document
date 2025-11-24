---
title: Splitting Documents
description: Break documents into chunks for embeddings
---

# Splitting Documents

Learn how to split large documents into smaller chunks for embedding models.

## Why Split Documents?

Embedding models have token limits (e.g., 512 or 8192 tokens). Large documents must be split into chunks that:

- Fit within the model's context window
- Maintain semantic coherence
- Provide enough context for retrieval

## Recursive Character Splitting

The recommended way to split documents:

```python
from rs_document import Document

doc = Document(
    page_content="A" * 5000,  # 5000 characters
    metadata={"source": "large.txt"}
)

# Split into ~1000 character chunks
chunks = doc.recursive_character_splitter(1000)

print(f"Created {len(chunks)} chunks")
print(f"First chunk: {len(chunks[0].page_content)} chars")
print(f"Metadata preserved: {chunks[0].metadata}")
```

### How It Works

The splitter tries to split at natural boundaries:

1. **Paragraph breaks** (`\n\n`) - first choice
2. **Line breaks** (`\n`) - if paragraphs too large
3. **Word boundaries** (``) - if lines too large
4. **Character-by-character** - last resort

This respects document structure and keeps semantic units together.

### Chunk Overlap

The splitter automatically creates ~33% overlap between chunks:

```python
doc = Document(
    page_content="Paragraph one.\n\nParagraph two.\n\nParagraph three.",
    metadata={}
)

chunks = doc.recursive_character_splitter(50)

# Adjacent chunks share content for better context
for i, chunk in enumerate(chunks):
    print(f"Chunk {i}: {chunk.page_content}")
```

This overlap ensures:

- Concepts spanning chunk boundaries appear complete in at least one chunk
- Better retrieval for queries near chunk edges

### Choosing Chunk Size

Pick a chunk size based on your embedding model:

```python
# Small chunks (good for precise retrieval)
chunks = doc.recursive_character_splitter(500)

# Medium chunks (balanced)
chunks = doc.recursive_character_splitter(1000)

# Large chunks (more context)
chunks = doc.recursive_character_splitter(2000)
```

**Guidelines:**

- Check your embedding model's token limit
- ~4 characters ≈ 1 token (rough estimate)
- Leave room for the ~33% overlap
- Experiment to find what works for your use case

## Simple Character Splitting

For exact chunk sizes without overlap:

```python
from rs_document import Document

doc = Document(
    page_content="ABCDEFGHIJ",
    metadata={"id": "123"}
)

# Split exactly every 3 characters
chunks = doc.split_on_num_characters(3)

print([c.page_content for c in chunks])
# Output: ["ABC", "DEF", "GHI", "J"]
```

This splits at character boundaries, ignoring words or sentences.

**When to use:**

- You need uniform chunk sizes
- Document structure doesn't matter
- Testing or debugging

**When not to use:**

- For natural language (use recursive splitter instead)
- When context matters (no overlap)

## Complete Example

Clean and split a document:

```python
from rs_document import Document

# Load document
with open("article.txt", "r") as f:
    content = f.read()

# Create document
doc = Document(
    page_content=content,
    metadata={
        "source": "article.txt",
        "category": "tech"
    }
)

# Clean the text
doc.clean()

# Split into chunks
chunks = doc.recursive_character_splitter(1000)

# Inspect results
print(f"Original: {len(doc.page_content)} chars")
print(f"Chunks: {len(chunks)}")
print(f"\nFirst chunk:")
print(f"  Length: {len(chunks[0].page_content)}")
print(f"  Metadata: {chunks[0].metadata}")
print(f"  Preview: {chunks[0].page_content[:100]}...")
```

## Working with Chunks

### All Chunks Have Same Metadata

Every chunk gets a copy of the original metadata:

```python
doc = Document(
    page_content="text " * 1000,
    metadata={"source": "doc.txt", "author": "Jane"}
)

chunks = doc.recursive_character_splitter(500)

# All chunks have the same metadata
for chunk in chunks:
    assert chunk.metadata == {"source": "doc.txt", "author": "Jane"}
```

### Add Chunk-Specific Metadata

Track chunk position:

```python
chunks = doc.recursive_character_splitter(1000)

# Add chunk index to each
for i, chunk in enumerate(chunks):
    chunk.metadata["chunk_index"] = str(i)
    chunk.metadata["total_chunks"] = str(len(chunks))

print(chunks[0].metadata)
# {"source": "doc.txt", "chunk_index": "0", "total_chunks": "5"}
```

### Filter Chunks

Remove chunks that are too small:

```python
chunks = doc.recursive_character_splitter(1000)

# Keep only chunks >= 200 chars
min_size = 200
filtered = [c for c in chunks if len(c.page_content) >= min_size]

print(f"Kept {len(filtered)} of {len(chunks)} chunks")
```

## Common Patterns

### Split Multiple Documents

```python
documents = [doc1, doc2, doc3]  # Your documents

all_chunks = []
for doc in documents:
    doc.clean()
    chunks = doc.recursive_character_splitter(1000)
    all_chunks.extend(chunks)

print(f"Total chunks: {len(all_chunks)}")
```

### Track Source Document

```python
documents = [...]  # Your documents

# Add unique ID to each source doc
for i, doc in enumerate(documents):
    doc.metadata["doc_id"] = str(i)

# Split and chunks inherit doc_id
all_chunks = []
for doc in documents:
    chunks = doc.recursive_character_splitter(1000)
    all_chunks.extend(chunks)

# Group chunks by source
from collections import defaultdict
chunks_by_doc = defaultdict(list)

for chunk in all_chunks:
    doc_id = chunk.metadata["doc_id"]
    chunks_by_doc[doc_id].append(chunk)
```

## Important Notes

### Splitting Returns New Documents

Unlike cleaning, splitting creates new documents:

```python
doc = Document(page_content="text", metadata={})

# Creates NEW documents, doesn't modify doc
chunks = doc.recursive_character_splitter(100)

# Original document unchanged
assert doc.page_content == "text"
```

### Empty Documents

Empty documents return empty list:

```python
doc = Document(page_content="", metadata={})

chunks = doc.recursive_character_splitter(1000)

assert len(chunks) == 0
```

### Maximum Chunk Size

Chunks never exceed the requested size:

```python
chunks = doc.recursive_character_splitter(1000)

# All chunks <= 1000 characters
for chunk in chunks:
    assert len(chunk.page_content) <= 1000
```

## Next Steps

Now you know how to split documents! Let's learn how to [process multiple documents efficiently](batch-processing.md) with parallel processing.
