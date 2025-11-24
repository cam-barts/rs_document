---
title: Types and Constants
description: Type signatures, constants, defaults, and error handling patterns
---

# Types and Constants

Type information, constants, default values, and error handling for rs_document.

## Type Signatures

Complete type signatures for all public APIs. These are provided for type checkers (mypy, pyright) and IDE autocompletion.

### Document Class

```python
from rs_document import Document

class Document:
    """A document with content and metadata."""

    def __init__(
        self,
        page_content: str,
        metadata: dict[str, str]
    ) -> None:
        """
        Create a new Document.

        Args:
            page_content: The text content of the document
            metadata: Dictionary of string key-value pairs
        """
        ...

    # Attributes
    page_content: str
    metadata: dict[str, str]

    # Cleaning methods
    def clean(self) -> None:
        """Run all cleaning operations."""
        ...

    def clean_non_ascii_chars(self) -> None:
        """Remove all non-ASCII characters."""
        ...

    def clean_bullets(self) -> None:
        """Remove bullet point characters."""
        ...

    def clean_ligatures(self) -> None:
        """Convert typographic ligatures to component characters."""
        ...

    def clean_extra_whitespace(self) -> None:
        """Normalize whitespace."""
        ...

    def group_broken_paragraphs(self) -> None:
        """Join paragraphs incorrectly split across lines."""
        ...

    # Splitting methods
    def recursive_character_splitter(
        self,
        chunk_size: int
    ) -> list[Document]:
        """
        Split document with recursive strategy.

        Args:
            chunk_size: Target size for each chunk in characters

        Returns:
            List of Document instances (chunks)
        """
        ...

    def split_on_num_characters(
        self,
        num_chars: int
    ) -> list[Document]:
        """
        Split document into fixed-size chunks.

        Args:
            num_chars: Number of characters per chunk

        Returns:
            List of Document instances (chunks)
        """
        ...
```

### Utility Functions

```python
from rs_document import clean_and_split_docs

def clean_and_split_docs(
    documents: list[Document],
    chunk_size: int
) -> list[Document]:
    """
    Process multiple documents in parallel: clean and split.

    Args:
        documents: List of documents to process
        chunk_size: Target size for chunks in characters

    Returns:
        Flattened list of all chunks from all documents
    """
    ...
```

## Type Checking

### Using with mypy

```python
from rs_document import Document, clean_and_split_docs

# Type checker knows the types
doc: Document = Document(
    page_content="text",
    metadata={"key": "value"}
)

# Type checker validates method calls
doc.clean()  # OK - returns None
chunks: list[Document] = doc.recursive_character_splitter(1000)  # OK

# Type checker catches errors
doc.clean_non_ascii_chars(123)  # Error: takes no arguments
bad_doc = Document(123, {})  # Error: page_content must be str
```

### Using with pyright/pylance

```python
from rs_document import Document

def process_document(doc: Document) -> list[Document]:
    """Type-safe document processing."""
    doc.clean()
    return doc.recursive_character_splitter(1000)

# IDE provides autocomplete and type checking
result = process_document(my_doc)
reveal_type(result)  # list[Document]
```

## Constants

### Recursive Splitter Separators

The `recursive_character_splitter()` method uses these separators in order of preference:

| Order | Separator | Description | Unicode |
|-------|-----------|-------------|---------|
| 1 | `"\n\n"` | Paragraph breaks (double newline) | U+000A U+000A |
| 2 | `"\n"` | Line breaks (single newline) | U+000A |
| 3 | `" "` | Word boundaries (space) | U+0020 |
| 4 | `""` | Character-by-character (fallback) | - |

**Note:** These separators are hardcoded and cannot be customized.

**Example:**

```python
from rs_document import Document

doc = Document(
    page_content="Paragraph 1\n\nParagraph 2\n\nParagraph 3",
    metadata={}
)

# Will try to split on "\n\n" first
chunks = doc.recursive_character_splitter(50)
```

### Chunk Overlap

The `recursive_character_splitter()` uses approximately **33% overlap** between consecutive chunks.

**Calculation:**

```text
overlap_size = chunk_size / 3  (integer division)
```

**Example:**

```python
# chunk_size = 1000
# overlap_size = 1000 / 3 = 333 characters

doc = Document(page_content="A" * 3000, metadata={})
chunks = doc.recursive_character_splitter(1000)

# Chunk 0: characters 0-1000
# Chunk 1: characters 667-1667 (333 char overlap with chunk 0)
# Chunk 2: characters 1334-2334 (333 char overlap with chunk 1)
# etc.
```

**Note:** The overlap percentage is hardcoded and cannot be customized.

### Cleaned Characters

#### Bullet Characters

Characters removed by `clean_bullets()`:

| Character | Description | Unicode |
|-----------|-------------|---------|
| `●` | Black Circle | U+25CF |
| `○` | White Circle | U+25CB |
| `■` | Black Square | U+25A0 |
| `□` | White Square | U+25A1 |
| `•` | Bullet | U+2022 |
| `◦` | White Bullet | U+25E6 |
| `▪` | Black Small Square | U+25AA |
| `▫` | White Small Square | U+25AB |
| `‣` | Triangular Bullet | U+2023 |
| `⁃` | Hyphen Bullet | U+2043 |

#### Ligature Conversions

Ligatures converted by `clean_ligatures()`:

| Ligature | Converts To | Unicode |
|----------|-------------|---------|
| `æ` | `ae` | U+00E6 |
| `Æ` | `AE` | U+00C6 |
| `œ` | `oe` | U+0153 |
| `Œ` | `OE` | U+0152 |
| `ﬁ` | `fi` | U+FB01 |
| `ﬂ` | `fl` | U+FB02 |
| `ﬀ` | `ff` | U+FB00 |
| `ﬃ` | `ffi` | U+FB03 |
| `ﬄ` | `ffl` | U+FB04 |
| `ﬅ` | `ft` | U+FB05 |
| `ﬆ` | `st` | U+FB06 |

## Error Handling

### Empty Documents

All methods handle empty documents gracefully without raising errors:

```python
from rs_document import Document

doc = Document(page_content="", metadata={})

# Cleaning methods - no error
doc.clean()  # No-op, returns None
doc.clean_non_ascii_chars()  # No-op, returns None
doc.clean_bullets()  # No-op, returns None
doc.clean_ligatures()  # No-op, returns None
doc.clean_extra_whitespace()  # No-op, returns None
doc.group_broken_paragraphs()  # No-op, returns None

# Splitting methods - return empty list
chunks = doc.recursive_character_splitter(1000)
print(chunks)  # []

chunks = doc.split_on_num_characters(100)
print(chunks)  # []
```

### Invalid Metadata Types

Metadata must contain only string keys and string values. Non-string values may cause errors.

**Correct Usage:**

```python
# All strings - correct
doc = Document(
    page_content="text",
    metadata={"id": "123", "count": "456", "active": "True"}
)
```

**Incorrect Usage:**

```python
# Non-string values - may cause errors
doc = Document(
    page_content="text",
    metadata={"id": 123, "active": True}  # ERROR: int and bool
)
```

**Solution - Convert to Strings:**

```python
raw_metadata = {
    "id": 123,
    "page": 5,
    "active": True,
    "score": 98.6,
    "tags": ["a", "b"],
}

# Convert all values to strings
doc = Document(
    page_content="text",
    metadata={k: str(v) for k, v in raw_metadata.items()}
)

print(doc.metadata)
# {"id": "123", "page": "5", "active": "True",
#  "score": "98.6", "tags": "['a', 'b']"}
```

### Invalid Parameters

Methods validate parameters and raise exceptions for invalid inputs:

```python
from rs_document import Document

doc = Document(page_content="text", metadata={})

# Invalid chunk_size - negative
try:
    chunks = doc.recursive_character_splitter(-100)
except ValueError as e:
    print(f"Error: {e}")

# Invalid chunk_size - zero
try:
    chunks = doc.split_on_num_characters(0)
except ValueError as e:
    print(f"Error: {e}")

# Wrong type for chunk_size
try:
    chunks = doc.recursive_character_splitter("1000")  # string instead of int
except TypeError as e:
    print(f"Error: {e}")
```

### Empty Lists

`clean_and_split_docs()` handles empty lists:

```python
from rs_document import clean_and_split_docs

# Empty list - returns empty list
chunks = clean_and_split_docs([], chunk_size=1000)
print(chunks)  # []
```

## Default Values

### Method Defaults

All cleaning and splitting methods have no optional parameters. All parameters shown are required:

```python
# Cleaning methods - no parameters
doc.clean()
doc.clean_non_ascii_chars()
doc.clean_bullets()
doc.clean_ligatures()
doc.clean_extra_whitespace()
doc.group_broken_paragraphs()

# Splitting methods - required parameters
chunks = doc.recursive_character_splitter(chunk_size=1000)  # chunk_size required
chunks = doc.split_on_num_characters(num_chars=500)  # num_chars required

# Utility function - required parameters
from rs_document import clean_and_split_docs
chunks = clean_and_split_docs(documents, chunk_size=1000)  # both required
```

### Hardcoded Values

Values that cannot be customized:

| Feature | Value | Location |
|---------|-------|----------|
| Recursive splitter separators | `["\n\n", "\n", " ", ""]` | `recursive_character_splitter()` |
| Chunk overlap | ~33% (chunk_size / 3) | `recursive_character_splitter()` |
| Cleaning order | See `clean()` method | `clean()` |
| Bullet characters | See table above | `clean_bullets()` |
| Ligatures | See table above | `clean_ligatures()` |

## Platform Support

### Python Version Requirements

- **Minimum:** Python 3.10
- **Recommended:** Python 3.11 or higher for best performance
- **Type hints:** Use modern type hint syntax (PEP 604 union types)

**Python Version Type Hints:**

```python
# Python 3.10+ syntax (used in rs_document)
def process(docs: list[Document]) -> dict[str, str]:
    ...

# Older syntax (also supported)
from typing import List, Dict
def process(docs: List[Document]) -> Dict[str, str]:
    ...
```

### Pre-built Wheels

Pre-built binary wheels are available for:

**Linux:**

- x86_64 (64-bit Intel/AMD)
- aarch64 (64-bit ARM)
- armv7 (32-bit ARM)
- i686 (32-bit Intel)
- s390x (IBM Z)
- ppc64le (PowerPC)

**macOS:**

- x86_64 (Intel Macs)
- aarch64 (Apple Silicon M1/M2/M3)

**Windows:**

- x64 (64-bit)
- x86 (32-bit)

**Installation:**

```bash
# Most platforms - uses pre-built wheel
pip install rs-document

# If wheel not available - compiles from source (requires Rust)
pip install rs-document
```

## LangChain Compatibility

### Similarities

rs_document's `Document` class is designed to be compatible with LangChain:

```python
# Both use same attribute names
from rs_document import Document as RSDocument
from langchain_core.documents import Document as LCDocument

rs_doc = RSDocument(page_content="text", metadata={"key": "value"})
lc_doc = LCDocument(page_content="text", metadata={"key": "value"})

# Both have same attributes
print(rs_doc.page_content)  # "text"
print(lc_doc.page_content)  # "text"

print(rs_doc.metadata)  # {"key": "value"}
print(lc_doc.metadata)  # {"key": "value"}
```

### Differences

| Feature | rs_document | LangChain |
|---------|-------------|-----------|
| Metadata values | Must be strings | Any Python object |
| Metadata keys | Must be strings | Any hashable object |
| Performance | High (Rust) | Standard (Python) |
| Methods | Cleaning + splitting | Minimal (constructor only) |

### Conversion

**From LangChain to rs_document:**

```python
from langchain_core.documents import Document as LCDocument
from rs_document import Document as RSDocument

lc_doc = LCDocument(
    page_content="text",
    metadata={"id": 123, "active": True, "tags": ["a", "b"]}
)

# Convert - stringify all metadata
rs_doc = RSDocument(
    page_content=lc_doc.page_content,
    metadata={k: str(v) for k, v in lc_doc.metadata.items()}
)
```

**From rs_document to LangChain:**

```python
from rs_document import Document as RSDocument
from langchain_core.documents import Document as LCDocument

rs_doc = RSDocument(
    page_content="text",
    metadata={"id": "123", "page": "5"}
)

# Convert - direct copy (already strings)
lc_doc = LCDocument(
    page_content=rs_doc.page_content,
    metadata=rs_doc.metadata
)
```

### Integration Example

```python
from langchain_core.documents import Document as LCDocument
from rs_document import Document as RSDocument, clean_and_split_docs

# Start with LangChain documents
lc_documents = [
    LCDocument(page_content=text, metadata={"source": f"doc{i}.txt"})
    for i, text in enumerate(texts)
]

# Convert to rs_document for processing
rs_documents = [
    RSDocument(
        page_content=doc.page_content,
        metadata={k: str(v) for k, v in doc.metadata.items()}
    )
    for doc in lc_documents
]

# Process with rs_document (fast)
chunks = clean_and_split_docs(rs_documents, chunk_size=1000)

# Convert back to LangChain
lc_chunks = [
    LCDocument(
        page_content=chunk.page_content,
        metadata=chunk.metadata
    )
    for chunk in chunks
]

# Now use with LangChain tools
# vectorstore.add_documents(lc_chunks)
```

## See Also

- [Document Class](document-class.md) - Document class reference
- [Cleaning Methods](cleaning-methods.md) - Cleaning method details
- [Splitting Methods](splitting-methods.md) - Splitting method details
- [Utility Functions](utility-functions.md) - Batch processing utilities
