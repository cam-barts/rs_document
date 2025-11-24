---
title: Your First Document
description: Create and work with Document objects
---

# Your First Document

Learn how to create and work with Document objects in rs_document.

## Creating a Document

A `Document` has two parts:

1. **page_content**: The text content
2. **metadata**: String key-value pairs for tracking information

Let's create one:

```python
from rs_document import Document

doc = Document(
    page_content="This is my first document with some text content.",
    metadata={"source": "tutorial.txt", "page": "1"}
)

print(doc)
```

Output:

```text
Document(page_content="This is my first document...", metadata={"source": "tutorial.txt", "page": "1"})
```

## Understanding Document Components

### Page Content

The text content of your document:

```python
doc = Document(
    page_content="Hello, world!",
    metadata={}
)

# Access the content
print(doc.page_content)  # "Hello, world!"

# Modify it
doc.page_content = "Goodbye, world!"
print(doc.page_content)  # "Goodbye, world!"
```

### Metadata

Metadata stores information about the document:

```python
doc = Document(
    page_content="Document text",
    metadata={
        "source": "article.txt",
        "author": "Jane Doe",
        "date": "2024-01-01",
        "category": "tutorial"
    }
)

# Access metadata
print(doc.metadata["source"])  # "article.txt"

# Add more metadata
doc.metadata["page"] = "5"

# View all metadata
print(doc.metadata)
```

**Important**: Metadata values must be strings. Convert other types:

```python
# Wrong - will cause errors
metadata = {"page": 5, "score": 0.95}

# Correct - convert to strings
metadata = {"page": "5", "score": "0.95"}

doc = Document(page_content="text", metadata=metadata)
```

## Creating Documents from Files

Load content from a text file:

```python
from rs_document import Document

# Read file
with open("document.txt", "r", encoding="utf-8") as f:
    content = f.read()

# Create document
doc = Document(
    page_content=content,
    metadata={
        "source": "document.txt",
        "path": "/path/to/document.txt"
    }
)
```

## Working with Multiple Documents

Create a list of documents:

```python
from rs_document import Document

documents = []

for i in range(5):
    doc = Document(
        page_content=f"Content of document {i}",
        metadata={"doc_id": str(i)}
    )
    documents.append(doc)

print(f"Created {len(documents)} documents")
```

## Viewing Documents

Documents have a helpful string representation:

```python
doc = Document(
    page_content="Short content",
    metadata={"id": "123"}
)

# Print the document
print(doc)

# Convert to string
doc_string = str(doc)
```

## Common Patterns

### Document from User Input

```python
user_text = input("Enter your text: ")

doc = Document(
    page_content=user_text,
    metadata={"source": "user_input"}
)
```

### Document with Timestamps

```python
from datetime import datetime

doc = Document(
    page_content="Current content",
    metadata={
        "created_at": datetime.now().isoformat(),
        "source": "app"
    }
)
```

### Empty Document

```python
# Empty document (useful as placeholder)
doc = Document(page_content="", metadata={})

# Check if empty
if not doc.page_content:
    print("Document is empty")
```

## Next Steps

Now that you know how to create documents, let's learn how to [clean text](cleaning.md) to remove artifacts and normalize formatting!
