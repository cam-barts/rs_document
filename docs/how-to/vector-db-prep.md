---
title: Vector Database Preparation
description: Prepare documents for embedding models and vector databases
---

# Vector Database Preparation

Learn how to prepare documents for embedding models and vector databases in RAG applications.

## Prepare Documents for Embedding

```python
from rs_document import clean_and_split_docs, Document

# Load your documents
documents = [...]  # Your documents here

# Clean and split for embeddings
chunks = clean_and_split_docs(documents, chunk_size=1000)

# Extract text and metadata for your vector DB
texts = [chunk.page_content for chunk in chunks]
metadatas = [chunk.metadata for chunk in chunks]

# Use with your embedding model
# embeddings = your_embedding_model.embed(texts)
```

## Add Chunk Index to Metadata

Track chunk positions within the original document:

```python
from rs_document import Document

doc = Document(
    page_content="Long content " * 1000,
    metadata={"source": "doc.txt"}
)

# Split and add chunk index
chunks = doc.recursive_character_splitter(1000)

# Add chunk position info
for i, chunk in enumerate(chunks):
    chunk.metadata["chunk_index"] = str(i)
    chunk.metadata["total_chunks"] = str(len(chunks))

# Now each chunk knows its position
print(chunks[0].metadata)
# {"source": "doc.txt", "chunk_index": "0", "total_chunks": "5"}
```

## Choose Chunk Size for Your Embedding Model

Match chunk size to your embedding model's context window:

```python
from rs_document import Document

doc = Document(page_content="test " * 10000, metadata={})

# For OpenAI text-embedding-ada-002 (8191 tokens ~= 32,000 chars)
openai_chunks = doc.recursive_character_splitter(2000)

# For smaller context windows (512 tokens ~= 2000 chars)
small_chunks = doc.recursive_character_splitter(1000)

# For larger context windows
large_chunks = doc.recursive_character_splitter(4000)
```

## Filter Chunks for Quality

Remove chunks that are too small or don't meet quality criteria:

```python
from rs_document import clean_and_split_docs, Document

documents = [...]  # Your documents
chunks = clean_and_split_docs(documents, chunk_size=1000)

# Filter out very small chunks
min_size = 100
quality_chunks = [
    c for c in chunks
    if len(c.page_content) >= min_size
]

print(f"Kept {len(quality_chunks)} of {len(chunks)} chunks")
```

## Prepare with OpenAI Embeddings

```python
from rs_document import clean_and_split_docs, Document
import openai

# Process documents
documents = [...]  # Your documents
chunks = clean_and_split_docs(documents, chunk_size=1500)

# Get texts and metadata
texts = [chunk.page_content for chunk in chunks]
metadatas = [chunk.metadata for chunk in chunks]

# Create embeddings
client = openai.OpenAI()
embeddings = []
for text in texts:
    response = client.embeddings.create(
        input=text,
        model="text-embedding-ada-002"
    )
    embeddings.append(response.data[0].embedding)
```

## Prepare with HuggingFace Embeddings

```python
from rs_document import clean_and_split_docs, Document
from sentence_transformers import SentenceTransformer

# Process documents
documents = [...]  # Your documents
chunks = clean_and_split_docs(documents, chunk_size=512)

# Get texts
texts = [chunk.page_content for chunk in chunks]

# Create embeddings
model = SentenceTransformer('all-MiniLM-L6-v2')
embeddings = model.encode(texts)
```

## Prepare for Pinecone

```python
from rs_document import clean_and_split_docs, Document
import pinecone

# Process documents
documents = [...]  # Your documents
chunks = clean_and_split_docs(documents, chunk_size=1000)

# Prepare vectors for Pinecone
vectors = []
for i, chunk in enumerate(chunks):
    vectors.append({
        "id": f"chunk-{i}",
        "values": embedding[i],  # Your embedding
        "metadata": chunk.metadata
    })

# Upsert to Pinecone
# index.upsert(vectors=vectors)
```

## Prepare for Qdrant

```python
from rs_document import clean_and_split_docs, Document
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct

# Process documents
documents = [...]  # Your documents
chunks = clean_and_split_docs(documents, chunk_size=1000)

# Prepare points for Qdrant
points = []
for i, chunk in enumerate(chunks):
    points.append(
        PointStruct(
            id=i,
            vector=embeddings[i],  # Your embedding
            payload={
                "text": chunk.page_content,
                **chunk.metadata
            }
        )
    )

# Upsert to Qdrant
# client.upsert(collection_name="documents", points=points)
```

## Prepare for ChromaDB

```python
from rs_document import clean_and_split_docs, Document
import chromadb

# Process documents
documents = [...]  # Your documents
chunks = clean_and_split_docs(documents, chunk_size=1000)

# Prepare for ChromaDB
ids = [f"chunk-{i}" for i in range(len(chunks))]
documents_text = [chunk.page_content for chunk in chunks]
metadatas = [chunk.metadata for chunk in chunks]

# Add to ChromaDB
# collection.add(
#     ids=ids,
#     documents=documents_text,
#     metadatas=metadatas
# )
```

## Complete RAG Preparation Pipeline

```python
from pathlib import Path
from rs_document import Document, clean_and_split_docs

def prepare_for_rag(
    directory: str,
    chunk_size: int = 1000,
    min_chunk_size: int = 100
) -> tuple[list[str], list[dict]]:
    """Complete pipeline for RAG preparation."""

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
            }
        )
        documents.append(doc)

    # 2. Clean and split
    chunks = clean_and_split_docs(documents, chunk_size=chunk_size)

    # 3. Filter quality
    quality_chunks = [
        c for c in chunks
        if len(c.page_content) >= min_chunk_size
    ]

    # 4. Add chunk metadata
    for i, chunk in enumerate(quality_chunks):
        chunk.metadata["chunk_id"] = str(i)

    # 5. Extract texts and metadata
    texts = [chunk.page_content for chunk in quality_chunks]
    metadatas = [chunk.metadata for chunk in quality_chunks]

    return texts, metadatas

# Use it
texts, metadatas = prepare_for_rag("./documents")
print(f"Ready: {len(texts)} chunks")
```

## Next Steps

- See [Batch Operations](batch-operations.md) for performance tips
- Check [LangChain Integration](langchain-integration.md) for LangChain workflows
- Review [Splitting Tasks](splitting-tasks.md) for chunking strategies
