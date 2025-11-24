---
title: Batch Processing
description: Process multiple documents efficiently
---

# Batch Processing

Learn how to process many documents efficiently with parallel processing.

## The clean_and_split_docs Function

Process multiple documents with one function call:

```python
from rs_document import Document, clean_and_split_docs

# Create multiple documents
documents = [
    Document(
        page_content=f"Document {i} content " * 100,
        metadata={"doc_id": str(i)}
    )
    for i in range(100)
]

# Clean and split all at once
chunks = clean_and_split_docs(documents, chunk_size=1000)

print(f"Processed {len(documents)} documents")
print(f"Created {len(chunks)} chunks")
```

### What It Does

`clean_and_split_docs` performs these steps **in parallel**:

1. Runs `.clean()` on each document
2. Splits each with `.recursive_character_splitter(chunk_size)`
3. Returns a flat list of all chunks

## Why Use Batch Processing?

### Performance

Processing documents individually:

```python
# Slow - processes sequentially
all_chunks = []
for doc in documents:
    doc.clean()
    chunks = doc.recursive_character_splitter(1000)
    all_chunks.extend(chunks)
```

Using batch processing:

```python
# Fast - processes in parallel
chunks = clean_and_split_docs(documents, chunk_size=1000)
```

**Result**: 20-25x faster, processing ~23,000 documents/second on typical hardware.

### Simplicity

One function call instead of a loop:

```python
# Before
all_chunks = []
for doc in documents:
    doc.clean()
    chunks = doc.recursive_character_splitter(1000)
    all_chunks.extend(chunks)

# After
chunks = clean_and_split_docs(documents, chunk_size=1000)
```

## Complete Example

Process a directory of text files:

```python
from pathlib import Path
from rs_document import Document, clean_and_split_docs

# Load all text files
documents = []
for file_path in Path("./documents").glob("*.txt"):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    doc = Document(
        page_content=content,
        metadata={
            "source": file_path.name,
            "path": str(file_path)
        }
    )
    documents.append(doc)

print(f"Loaded {len(documents)} documents")

# Process all at once
chunks = clean_and_split_docs(documents, chunk_size=1000)

print(f"Created {len(chunks)} chunks")
print(f"Average chunks per doc: {len(chunks) / len(documents):.1f}")
```

## Tracking Progress

For large batches, show progress:

```python
from rs_document import Document, clean_and_split_docs
import time

documents = [...]  # Your documents

print(f"Processing {len(documents)} documents...")
start_time = time.time()

chunks = clean_and_split_docs(documents, chunk_size=1000)

elapsed = time.time() - start_time
docs_per_sec = len(documents) / elapsed

print(f"Done in {elapsed:.2f}s ({docs_per_sec:.0f} docs/sec)")
print(f"Created {len(chunks)} chunks")
```

## Working with Results

### Group Chunks by Source

Track which chunks came from which document:

```python
from collections import defaultdict

# Add unique IDs before processing
for i, doc in enumerate(documents):
    doc.metadata["doc_id"] = str(i)

# Process
chunks = clean_and_split_docs(documents, chunk_size=1000)

# Group by source
chunks_by_doc = defaultdict(list)
for chunk in chunks:
    doc_id = chunk.metadata["doc_id"]
    chunks_by_doc[doc_id].append(chunk)

# See distribution
for doc_id, doc_chunks in chunks_by_doc.items():
    print(f"Document {doc_id}: {len(doc_chunks)} chunks")
```

### Filter Small Chunks

Remove chunks below a minimum size:

```python
chunks = clean_and_split_docs(documents, chunk_size=1000)

# Keep only chunks >= 200 characters
min_size = 200
filtered = [c for c in chunks if len(c.page_content) >= min_size]

print(f"Kept {len(filtered)} of {len(chunks)} chunks")
```

### Add Global Metadata

Add metadata to all chunks:

```python
chunks = clean_and_split_docs(documents, chunk_size=1000)

# Add processing info to all chunks
batch_id = "batch_001"
for chunk in chunks:
    chunk.metadata["batch_id"] = batch_id
    chunk.metadata["processed_at"] = "2024-01-01"
```

## Performance Considerations

### Optimal Batch Size

Process documents in batches for best performance:

```python
from rs_document import clean_and_split_docs

def process_in_batches(documents, chunk_size=1000, batch_size=1000):
    """Process documents in batches."""
    all_chunks = []

    for i in range(0, len(documents), batch_size):
        batch = documents[i:i + batch_size]
        chunks = clean_and_split_docs(batch, chunk_size=chunk_size)
        all_chunks.extend(chunks)

        print(f"Processed batch {i//batch_size + 1}: {len(chunks)} chunks")

    return all_chunks

# Process 10,000 documents in batches of 1,000
documents = [...]  # Your 10,000 documents
chunks = process_in_batches(documents, chunk_size=1000, batch_size=1000)
```

### Memory Management

For very large datasets:

```python
def process_and_save(documents, output_file, chunk_size=1000):
    """Process documents and save chunks incrementally."""
    import json

    with open(output_file, "w") as f:
        batch_size = 1000

        for i in range(0, len(documents), batch_size):
            batch = documents[i:i + batch_size]
            chunks = clean_and_split_docs(batch, chunk_size=chunk_size)

            # Save chunks to file
            for chunk in chunks:
                data = {
                    "content": chunk.page_content,
                    "metadata": chunk.metadata
                }
                f.write(json.dumps(data) + "\n")

            print(f"Saved {len(chunks)} chunks from batch {i//batch_size + 1}")

# Use it
documents = [...]  # Large list
process_and_save(documents, "chunks.jsonl", chunk_size=1000)
```

## Integration Example

Complete pipeline for RAG:

```python
from pathlib import Path
from rs_document import Document, clean_and_split_docs

def prepare_documents_for_rag(directory, chunk_size=1000):
    """Load, clean, split, and prepare documents for RAG."""

    # 1. Load documents
    print("Loading documents...")
    documents = []
    for file_path in Path(directory).glob("**/*.txt"):
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        doc = Document(
            page_content=content,
            metadata={
                "source": file_path.name,
                "path": str(file_path),
                "category": file_path.parent.name
            }
        )
        documents.append(doc)

    print(f"Loaded {len(documents)} documents")

    # 2. Clean and split
    print("Processing...")
    chunks = clean_and_split_docs(documents, chunk_size=chunk_size)

    # 3. Filter small chunks
    min_size = chunk_size // 4
    filtered = [c for c in chunks if len(c.page_content) >= min_size]

    # 4. Add chunk IDs
    for i, chunk in enumerate(filtered):
        chunk.metadata["chunk_id"] = str(i)

    print(f"Created {len(filtered)} chunks")
    return filtered

# Use it
chunks = prepare_documents_for_rag("./my_documents", chunk_size=1000)

# Ready for embedding
texts = [c.page_content for c in chunks]
metadatas = [c.metadata for c in chunks]
```

## Benchmarking

Measure your processing speed:

```python
import time
from rs_document import Document, clean_and_split_docs

# Create test documents
num_docs = 1000
documents = [
    Document(
        page_content="test content " * 500,
        metadata={"id": str(i)}
    )
    for i in range(num_docs)
]

# Benchmark
start = time.time()
chunks = clean_and_split_docs(documents, chunk_size=1000)
elapsed = time.time() - start

# Results
docs_per_sec = num_docs / elapsed
print(f"Processed {num_docs} documents in {elapsed:.2f}s")
print(f"Speed: {docs_per_sec:.0f} documents/second")
print(f"Created {len(chunks)} chunks")
```

## Summary

You've learned:

- ✅ How to use `clean_and_split_docs` for batch processing
- ✅ Why batch processing is faster (parallel processing)
- ✅ How to track and group chunks by source
- ✅ Performance optimization techniques
- ✅ Complete RAG pipeline example

## Next Steps

You've completed the tutorial! Here's what to explore next:

- **[How-To Guides](../how-to/index.md)** - Solve specific problems
- **[API Reference](../reference/index.md)** - Look up exact method signatures
- **[Explanation](../explanation/index.md)** - Understand design decisions

Happy document processing! 🚀
