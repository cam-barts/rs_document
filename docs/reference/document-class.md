---
title: Document Class
description: Document class constructor, attributes, and basic operations
---

# Document Class

The main class for working with text documents in rs_document.

## Constructor

### `Document(page_content, metadata)`

Create a new Document instance.

**Signature:**

```python
Document(page_content: str, metadata: dict[str, str]) -> Document
```

**Parameters:**

- **`page_content`** (`str`): The text content of the document
- **`metadata`** (`dict[str, str]`): Dictionary of string key-value pairs containing document metadata

**Returns:**

A new `Document` instance.

**Example:**

```python
from rs_document import Document

doc = Document(
    page_content="Hello, world!",
    metadata={"source": "example.txt", "page": "1"}
)
```

**Important Notes:**

- Metadata keys and values **must be strings**
- Non-string values must be converted to strings before creating the document
- Empty strings are valid for both `page_content` and metadata values

**Example with Type Conversion:**

```python
# Convert non-string metadata values
raw_metadata = {
    "id": 123,
    "page": 5,
    "active": True,
    "score": 98.6
}

doc = Document(
    page_content="Document text",
    metadata={k: str(v) for k, v in raw_metadata.items()}
)
# metadata is now {"id": "123", "page": "5", "active": "True", "score": "98.6"}
```

## Attributes

### `page_content`

The text content of the document.

**Type:** `str`

**Access:** Read and write

**Description:**

The `page_content` attribute contains the document's text. It can be read or modified directly. Changes to this attribute affect all subsequent operations on the document.

**Example:**

```python
doc = Document(page_content="Hello", metadata={})

# Read the content
print(doc.page_content)  # "Hello"

# Modify the content
doc.page_content = "Goodbye"
print(doc.page_content)  # "Goodbye"

# Content is updated
doc.clean()  # Operates on "Goodbye", not "Hello"
```

**Use Cases:**

- Accessing document text for display or analysis
- Modifying content programmatically
- Checking content length or properties before processing

### `metadata`

Dictionary containing document metadata.

**Type:** `dict[str, str]`

**Access:** Read and write

**Description:**

The `metadata` attribute stores key-value pairs about the document. All keys and values must be strings. The metadata dictionary can be read, modified, or updated like a standard Python dictionary.

**Example:**

```python
doc = Document(
    page_content="text",
    metadata={"author": "Jane", "date": "2024-01-01"}
)

# Read metadata
print(doc.metadata["author"])  # "Jane"

# Add new metadata
doc.metadata["category"] = "tech"

# Update existing metadata
doc.metadata["date"] = "2024-01-02"

# Iterate over metadata
for key, value in doc.metadata.items():
    print(f"{key}: {value}")
```

**Metadata Preservation:**

When documents are split using splitting methods, the metadata dictionary is copied to all resulting chunks:

```python
doc = Document(
    page_content="A" * 5000,
    metadata={"source": "original.txt", "section": "introduction"}
)

chunks = doc.recursive_character_splitter(1000)

# All chunks have the same metadata
for chunk in chunks:
    print(chunk.metadata)  # {"source": "original.txt", "section": "introduction"}
```

**Important Notes:**

- Only string keys and values are supported
- Attempting to store non-string values may cause errors
- Metadata is shallow-copied during splitting operations
- Empty dictionaries are valid metadata

## Instance Creation Patterns

### Basic Creation

```python
doc = Document(
    page_content="Simple text",
    metadata={"id": "1"}
)
```

### Empty Document

```python
# Valid - empty document
doc = Document(page_content="", metadata={})
```

### From File

```python
with open("document.txt", "r") as f:
    content = f.read()

doc = Document(
    page_content=content,
    metadata={"source": "document.txt", "type": "text"}
)
```

### From Multiple Sources

```python
documents = []

for filename in ["doc1.txt", "doc2.txt", "doc3.txt"]:
    with open(filename, "r") as f:
        doc = Document(
            page_content=f.read(),
            metadata={"source": filename}
        )
        documents.append(doc)
```

## LangChain Compatibility

The `Document` class is designed to be compatible with LangChain's Document model.

**Similarities:**

- Same attribute names (`page_content`, `metadata`)
- Similar API design and usage patterns
- Compatible structure for most operations

**Differences:**

- **rs_document**: Metadata values must be strings
- **LangChain**: Metadata can contain any Python object

**Converting from LangChain:**

```python
from langchain_core.documents import Document as LCDocument
from rs_document import Document as RSDocument

# LangChain document
lc_doc = LCDocument(
    page_content="text",
    metadata={"key": "value", "count": 42, "active": True}
)

# Convert to rs_document (stringify metadata)
rs_doc = RSDocument(
    page_content=lc_doc.page_content,
    metadata={k: str(v) for k, v in lc_doc.metadata.items()}
)
```

**Converting to LangChain:**

```python
from rs_document import Document as RSDocument
from langchain_core.documents import Document as LCDocument

# rs_document document
rs_doc = RSDocument(
    page_content="text",
    metadata={"id": "123", "page": "5"}
)

# Convert to LangChain (direct copy)
lc_doc = LCDocument(
    page_content=rs_doc.page_content,
    metadata=rs_doc.metadata
)
```

## See Also

- [Cleaning Methods](cleaning-methods.md) - Methods for cleaning document content
- [Splitting Methods](splitting-methods.md) - Methods for splitting documents into chunks
- [Types and Constants](types-and-constants.md) - Type signatures and error handling
