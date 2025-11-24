---
title: LangChain Integration
description: Use rs_document with LangChain document loaders and processors
---

# LangChain Integration

rs_document's `Document` class is compatible with LangChain's Document model. Learn how to integrate rs_document into your LangChain workflows.

## Convert from LangChain Documents

```python
from langchain_core.documents import Document as LCDocument
from rs_document import Document as RSDocument

# LangChain document
lc_doc = LCDocument(
    page_content="Some text",
    metadata={"source": "file.txt"}
)

# Convert to rs_document (metadata must be strings)
rs_doc = RSDocument(
    page_content=lc_doc.page_content,
    metadata={k: str(v) for k, v in lc_doc.metadata.items()}
)

# Process with rs_document
rs_doc.clean()
chunks = rs_doc.recursive_character_splitter(1000)
```

## Use with LangChain Document Loaders

```python
from langchain_community.document_loaders import TextLoader
from rs_document import Document, clean_and_split_docs

# Load with LangChain
loader = TextLoader("document.txt")
lc_documents = loader.load()

# Convert to rs_document
rs_documents = [
    Document(
        page_content=doc.page_content,
        metadata={k: str(v) for k, v in doc.metadata.items()}
    )
    for doc in lc_documents
]

# Process with rs_document's fast cleaning and splitting
chunks = clean_and_split_docs(rs_documents, chunk_size=1000)
```

## Convert Back to LangChain Format

```python
from rs_document import Document as RSDocument
from langchain_core.documents import Document as LCDocument

# Process with rs_document
rs_doc = RSDocument(page_content="text", metadata={"source": "file.txt"})
rs_doc.clean()
chunks = rs_doc.recursive_character_splitter(1000)

# Convert back to LangChain
lc_chunks = [
    LCDocument(
        page_content=chunk.page_content,
        metadata=chunk.metadata
    )
    for chunk in chunks
]
```

## Use with Directory Loaders

```python
from langchain_community.document_loaders import DirectoryLoader
from rs_document import Document, clean_and_split_docs

# Load directory with LangChain
loader = DirectoryLoader("./documents", glob="**/*.txt")
lc_documents = loader.load()

# Convert and process
rs_documents = [
    Document(
        page_content=doc.page_content,
        metadata={k: str(v) for k, v in doc.metadata.items()}
    )
    for doc in lc_documents
]

chunks = clean_and_split_docs(rs_documents, chunk_size=1000)
```

## Integration with LangChain Embeddings

```python
from langchain_community.document_loaders import TextLoader
from langchain_openai import OpenAIEmbeddings
from rs_document import Document, clean_and_split_docs

# Load with LangChain
loader = TextLoader("document.txt")
lc_documents = loader.load()

# Convert and process with rs_document
rs_documents = [
    Document(
        page_content=doc.page_content,
        metadata={k: str(v) for k, v in doc.metadata.items()}
    )
    for doc in lc_documents
]

chunks = clean_and_split_docs(rs_documents, chunk_size=1000)

# Use with LangChain embeddings
embeddings = OpenAIEmbeddings()
texts = [chunk.page_content for chunk in chunks]
vectors = embeddings.embed_documents(texts)
```

## Complete LangChain + rs_document Pipeline

```python
from langchain_community.document_loaders import DirectoryLoader
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from rs_document import Document, clean_and_split_docs

# 1. Load with LangChain
loader = DirectoryLoader("./documents", glob="**/*.txt")
lc_documents = loader.load()

# 2. Convert to rs_document
rs_documents = [
    Document(
        page_content=doc.page_content,
        metadata={k: str(v) for k, v in doc.metadata.items()}
    )
    for doc in lc_documents
]

# 3. Clean and split with rs_document (fast!)
chunks = clean_and_split_docs(rs_documents, chunk_size=1000)

# 4. Convert back for vector store
from langchain_core.documents import Document as LCDocument
lc_chunks = [
    LCDocument(page_content=c.page_content, metadata=c.metadata)
    for c in chunks
]

# 5. Create vector store
embeddings = OpenAIEmbeddings()
vectorstore = FAISS.from_documents(lc_chunks, embeddings)
```

## Why Use rs_document with LangChain?

- **Performance**: rs_document uses Rust for faster text cleaning and splitting
- **Parallel Processing**: `clean_and_split_docs()` processes multiple documents in parallel
- **Specialized Cleaners**: More cleaning options than LangChain's default text splitters
- **Compatible**: Works seamlessly with LangChain's ecosystem

## Next Steps

- See [Batch Operations](batch-operations.md) for performance optimization
- Check [Vector DB Preparation](vector-db-prep.md) for embedding workflows
- Review [Splitting Tasks](splitting-tasks.md) for chunking strategies
