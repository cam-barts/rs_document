---
title: Batch Operations
description: Process multiple documents efficiently with parallel processing
---

# Batch Operations

Learn how to process multiple documents efficiently using rs_document's batch processing capabilities.

## Process Multiple Documents Efficiently

The `clean_and_split_docs()` function uses parallel processing:

```python
from rs_document import clean_and_split_docs, Document

# Create or load multiple documents
documents = [
    Document(page_content=f"Document {i} content " * 100, metadata={"id": str(i)})
    for i in range(1000)
)

# Process all at once (uses parallel processing)
all_chunks = clean_and_split_docs(documents, chunk_size=1000)

print(f"Processed {len(documents)} docs into {len(all_chunks)} chunks")
```

## Filter Chunks After Splitting

```python
from rs_document import clean_and_split_docs, Document

documents = [Document(page_content="content " * 100, metadata={"category": "tech"})]
chunks = clean_and_split_docs(documents, chunk_size=500)

# Filter out chunks that are too small
min_size = 100
filtered_chunks = [c for c in chunks if len(c.page_content) >= min_size]

print(f"Kept {len(filtered_chunks)} of {len(chunks)} chunks")
```

## Track Which Document Each Chunk Came From

```python
from rs_document import Document, clean_and_split_docs
from collections import defaultdict

# Add unique ID to each source document
documents = []
for i in range(10):
    doc = Document(
        page_content=f"Content of document {i} " * 500,
        metadata={
            "source_doc_id": str(i),
            "filename": f"doc_{i}.txt"
        }
    )
    documents.append(doc)

# Process
chunks = clean_and_split_docs(documents, chunk_size=1000)

# Group chunks by source document
chunks_by_doc = defaultdict(list)

for chunk in chunks:
    doc_id = chunk.metadata["source_doc_id"]
    chunks_by_doc[doc_id].append(chunk)

# See how many chunks each document produced
for doc_id, doc_chunks in chunks_by_doc.items():
    print(f"Document {doc_id}: {len(doc_chunks)} chunks")
```

## Complete RAG Processing Pipeline

```python
from pathlib import Path
from rs_document import Document, clean_and_split_docs

def process_documents_for_rag(
    directory: str,
    chunk_size: int = 1000
) -> list[Document]:
    """Complete pipeline for processing documents."""

    # 1. Load documents
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

    # 2. Clean and split (parallel processing)
    chunks = clean_and_split_docs(documents, chunk_size=chunk_size)

    # 3. Filter out very small chunks
    min_size = chunk_size // 4
    filtered = [c for c in chunks if len(c.page_content) >= min_size]

    # 4. Add chunk metadata
    for i, chunk in enumerate(filtered):
        chunk.metadata["chunk_id"] = str(i)

    return filtered

# Use it
chunks = process_documents_for_rag("./documents", chunk_size=1000)
print(f"Ready for embedding: {len(chunks)} chunks")
```

## Benchmark Your Processing

```python
import time
from rs_document import clean_and_split_docs, Document

# Create test documents
documents = [
    Document(page_content="content " * 5000, metadata={"id": str(i)})
    for i in range(1000)
]

# Time the processing
start = time.time()
chunks = clean_and_split_docs(documents, chunk_size=1000)
elapsed = time.time() - start

docs_per_second = len(documents) / elapsed
print(f"Processed {len(documents)} documents in {elapsed:.2f}s")
print(f"Speed: {docs_per_second:.0f} documents/second")
print(f"Produced {len(chunks)} chunks")
```

## Process by Category

```python
from rs_document import Document, clean_and_split_docs

# Documents with categories
documents = [
    Document(page_content="tech content", metadata={"category": "tech"}),
    Document(page_content="business content", metadata={"category": "business"}),
    Document(page_content="more tech", metadata={"category": "tech"}),
]

# Process all
chunks = clean_and_split_docs(documents, chunk_size=500)

# Group by category
tech_chunks = [c for c in chunks if c.metadata["category"] == "tech"]
business_chunks = [c for c in chunks if c.metadata["category"] == "business"]

print(f"Tech chunks: {len(tech_chunks)}")
print(f"Business chunks: {len(business_chunks)}")
```

## Next Steps

- [Prepare chunks for vector databases](vector-db-prep.md)
- [Integrate with LangChain](langchain-integration.md)
- See [Loading Documents](loading-documents.md) for input strategies
