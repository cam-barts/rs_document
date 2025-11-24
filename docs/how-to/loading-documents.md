---
title: Loading Documents
description: Create documents from files and manage metadata
---

# Loading Documents

Learn how to create `Document` objects from various sources and manage their metadata effectively.

## Create a Document from a File

```python
from rs_document import Document

# Read file content
with open("document.txt", "r", encoding="utf-8") as f:
    content = f.read()

# Create document with metadata
doc = Document(
    page_content=content,
    metadata={
        "source": "document.txt",
        "created_at": "2024-01-01"
    }
)
```

## Create Documents from Multiple Files

```python
from pathlib import Path
from rs_document import Document

def load_documents(directory: str) -> list[Document]:
    """Load all text files from a directory."""
    docs = []
    for file_path in Path(directory).glob("*.txt"):
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        doc = Document(
            page_content=content,
            metadata={
                "source": file_path.name,
                "path": str(file_path)
            }
        )
        docs.append(doc)

    return docs

# Use it
documents = load_documents("./my_documents")
```

## Load Documents Recursively

```python
from pathlib import Path
from rs_document import Document

def load_documents_recursive(directory: str) -> list[Document]:
    """Load all text files from directory and subdirectories."""
    docs = []
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
        docs.append(doc)

    return docs
```

## Preserve Metadata Through Processing

Metadata is automatically preserved through all cleaning and splitting operations:

```python
from rs_document import Document

# Create document with important metadata
doc = Document(
    page_content="Some text content",
    metadata={
        "doc_id": "12345",
        "author": "Jane Doe",
        "category": "technical"
    }
)

# Metadata is preserved through cleaning
doc.clean()
print(doc.metadata)  # All metadata still there

# And through splitting
chunks = doc.recursive_character_splitter(1000)
for chunk in chunks:
    print(chunk.metadata)  # Same metadata on every chunk
```

## Validate Metadata Types

Metadata values must be strings:

```python
from rs_document import Document

# Convert to strings to ensure compatibility
doc = Document(
    page_content="text",
    metadata={
        "id": str(123),
        "page": str(5),
        "score": str(0.95)
    }
)
```

## Handle Empty Documents

```python
from rs_document import Document

# Empty document
doc = Document(page_content="", metadata={"id": "1"})

# Cleaning works fine
doc.clean()

# Splitting returns empty list
chunks = doc.recursive_character_splitter(1000)
assert len(chunks) == 0
```

## Next Steps

- [Clean your documents](cleaning-tasks.md) to remove unwanted characters
- [Split documents](splitting-tasks.md) into manageable chunks
- [Process multiple documents](batch-operations.md) efficiently
