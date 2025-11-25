# RS Document

A high-performance Rust implementation of LangChain's Document model and
Unstructured.io's text cleaners, providing 15-75x performance improvements for
RAG applications.

## Quick Links

📚 **[Full Documentation](https://cam-barts.github.io/rs_document)** -
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

- [Full Documentation](https://cam-barts.github.io/rs_document) - Complete guides and API reference
- [Tutorial](https://github.com/cam-barts/rs_document/blob/main/docs/tutorial/index.md) - Get started with rs_document
- [How-To Guides](https://github.com/cam-barts/rs_document/blob/main/docs/how-to/index.md) - Task-oriented guides
- [API Reference](https://github.com/cam-barts/rs_document/blob/main/docs/reference/index.md) - Complete API documentation
- [License](https://github.com/cam-barts/rs_document/blob/main/LICENSE.md) - Project license

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

## Attribution & Credits

This project builds upon and is inspired by the following open source projects:

### LangChain

- **Source**: <https://github.com/langchain-ai/langchain>
- **Author**: LangChain AI
- **License**: MIT
- **Usage**: The Document class is designed to be compatible with LangChain's Document model. The recursive character splitter is based on LangChain's RecursiveCharacterTextSplitter algorithm, reimplemented in Rust for performance.

### Unstructured.io

- **Source**: <https://github.com/Unstructured-IO/unstructured>
- **Author**: Unstructured Technologies, Inc.
- **License**: Apache 2.0
- **Usage**: The text cleaning functions are Rust reimplementations of Unstructured.io's post-processor cleaners, maintaining compatible behavior while providing significant performance improvements.

### Diataxis

- **Source**: <https://diataxis.fr>
- **Author**: Daniele Procida
- **License**: Creative Commons
- **Usage**: Documentation structure follows the Diataxis framework for organizing technical documentation into tutorials, how-to guides, reference, and explanation sections.

## License

See LICENSE.md for details.
