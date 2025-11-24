---
documentation_type: tutorial
title: RS Document
description: High-performance Rust implementation of LangChain Document model
---

# RS Document

A high-performance Rust implementation of LangChain's Document model and
Unstructured.io's text cleaners, providing 15-75x performance improvements for
RAG applications.

## Quick Links

📚 **[Full Documentation](https://yourusername.github.io/rs_document)** -
Visit our documentation site for detailed guides

## Installation

```sh
pip install rs-document
```

## Quick Start

```python
from rs_document import Document, clean_and_split_docs

# Create a document
content = "A" * 4000
doc = Document(page_content=content, metadata={"source": "example"})

# Run all cleaners
doc.clean()

# Split document into chunks
chunks = doc.recursive_character_splitter(1000)
```

## Key Features

- **20-25x speedup** over pure Python implementations
- **~23,000 documents/second** processing speed
- Full compatibility with LangChain's Document model
- Reimplemented Unstructured.io text cleaners
- Parallel document processing with Rayon

## Performance

Testing shows that cleaning and splitting documents with the Rust
implementation provides:

- **20-25x speedup** over pure Python (LangChain + Unstructured.io)
- **~23,000 documents per second** processing speed
- Consistent performance across dataset sizes

## Documentation

- [Installation & Usage](https://yourusername.github.io/rs_document)
- [Contributing Guide](https://yourusername.github.io/rs_document/contributing)
- [Coverage Reports](https://yourusername.github.io/rs_document/coverage)
- [Development Setup](https://yourusername.github.io/rs_document/claude)

## Development

```bash
# Install uv for fast package management
curl -LsSf https://astral.sh/uv/install.sh | sh

# Set up development environment
uv venv
source .venv/bin/activate
uv pip install -e ".[dev]"

# Build the Rust extension
maturin develop

# Run tests
nox -c dev/noxfile.py
```

## License

See LICENSE.md for details.
