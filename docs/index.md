---
title: RS Document
description: High-performance document processing for RAG applications
---

# RS Document

High-performance text document cleaning and splitting for RAG (Retrieval Augmented Generation) applications.

## Overview

rs_document is a Rust-powered Python package that provides fast text processing operations for preparing documents for vector databases and embedding models. It reimplements common document processing functions from LangChain and Unstructured.io with significant performance improvements.

**Key Features:**

- 20-25x faster than pure Python implementations
- ~23,000 documents/second processing speed
- Parallel batch processing
- Compatible with LangChain's Document model
- Simple, opinionated API

## Quick Start

Install from PyPI:

```bash
pip install rs-document
```

Basic usage:

```python
from rs_document import Document, clean_and_split_docs

# Create a document
doc = Document(
    page_content="Your document text here...",
    metadata={"source": "example.txt"}
)

# Clean and split
doc.clean()
chunks = doc.recursive_character_splitter(1000)

# Or process many documents at once
documents = [doc]  # Your list of documents
chunks = clean_and_split_docs(documents, chunk_size=1000)
```

## What Can You Do?

### Clean Documents

Remove artifacts from PDFs, OCR, and web scraping:

```python
doc = Document(
    page_content="●  Text with bullets, æ ligatures, and  extra   spaces",
    metadata={}
)

doc.clean()  # Runs all cleaners
```

Available cleaners:

- Remove non-ASCII characters
- Convert ligatures (æ → ae, œ → oe)
- Remove bullet symbols
- Normalize whitespace
- Group broken paragraphs

### Split Documents

Break large documents into chunks for embeddings:

```python
# Recursive splitting (respects paragraphs/sentences/words)
chunks = doc.recursive_character_splitter(1000)

# Simple character splitting
chunks = doc.split_on_num_characters(500)
```

The recursive splitter:

- Tries to split on paragraph breaks first
- Falls back to sentences, then words, then characters
- Creates ~33% overlap between chunks for better context

### Batch Processing

Process many documents efficiently with parallel processing:

```python
from rs_document import clean_and_split_docs

# Process 1000s of documents in seconds
chunks = clean_and_split_docs(documents, chunk_size=1000)
```

## Performance

Benchmarks show consistent performance improvements:

| Operation | Documents | Python Time | rs_document Time | Speedup |
|-----------|-----------|-------------|------------------|---------|
| Clean + Split | 1,000 | 45s | 2s | 22.5x |
| Clean + Split | 10,000 | 7.5min | 20s | 22.5x |
| Clean + Split | 100,000 | 75min | 3.3min | 22.5x |

Processing rate: ~23,000 documents/second on typical hardware.

## Documentation Structure

Following the [Diataxis](https://diataxis.fr) framework:

### [Tutorial](tutorial/)

**Learning-oriented** - Start here if you're new to rs_document. Walk through basic concepts and operations with hands-on examples.

### [How-To Guides](how-to/)

**Task-oriented** - Practical solutions for specific tasks like integrating with LangChain, batch processing, or handling edge cases.

### [Reference](reference/)

**Information-oriented** - Complete API documentation for all classes, methods, and functions. Look up exact signatures and parameters.

### [Explanation](explanation/)

**Understanding-oriented** - Learn about design decisions, performance characteristics, and how the recursive splitter algorithm works.

## Use Cases

rs_document is designed for:

- **RAG pipelines** - Prepare documents for vector databases
- **Document ingestion** - Process large document collections efficiently
- **Embedding preparation** - Split documents for embedding models
- **Text normalization** - Clean messy text from various sources

Works with:

- LangChain and LlamaIndex
- OpenAI, Cohere, and other embedding providers
- Pinecone, Weaviate, Qdrant, and other vector databases
- Any Python RAG framework

## Why Rust?

Text processing in Python is slow for large-scale operations. rs_document uses Rust for:

- Compiled native code performance
- Efficient string operations
- True parallelism (no GIL)
- Memory efficiency

You get Rust's performance with Python's convenience - no Rust knowledge required.

## Compatibility

- **Python**: 3.10+
- **Platforms**: Linux, macOS, Windows (x86_64 and ARM)
- **LangChain**: Compatible with Document model (metadata must be strings)

## Project Status

rs_document is production-ready and actively maintained. It's been tested with:

- 102 test cases including property-based tests
- CI testing across Python versions
- Performance benchmarks to prevent regressions

## Contributing

This project welcomes contributions! See the developer documentation in the `dev/` directory:

- `dev/contributing.md` - Development workflow and testing
- `dev/claude.md` - Project architecture and design
- `dev/coverage.md` - Testing and coverage strategy

## Attribution & Credits

This project builds upon and is inspired by the following open source projects:

### LangChain

- **Source**: [https://github.com/langchain-ai/langchain](https://github.com/langchain-ai/langchain)
- **Author**: LangChain AI
- **License**: MIT
- **Usage**: The Document class is designed to be compatible with LangChain's Document model. The recursive character splitter is based on LangChain's RecursiveCharacterTextSplitter algorithm, reimplemented in Rust for performance.

### Unstructured.io

- **Source**: [https://github.com/Unstructured-IO/unstructured](https://github.com/Unstructured-IO/unstructured)
- **Author**: Unstructured Technologies, Inc.
- **License**: Apache 2.0
- **Usage**: The text cleaning functions are Rust reimplementations of Unstructured.io's post-processor cleaners, maintaining compatible behavior while providing significant performance improvements.

### Diataxis

- **Source**: [https://diataxis.fr](https://diataxis.fr)
- **Author**: Daniele Procida
- **License**: Creative Commons
- **Usage**: Documentation structure follows the Diataxis framework for organizing technical documentation into tutorials, how-to guides, reference, and explanation sections.

## License

See [LICENSE.md](https://github.com/cam-barts/rs_document/blob/main/LICENSE.md) for details.

## Links

- [GitHub Repository](https://github.com/cam-barts/rs_document)
- [PyPI Package](https://pypi.org/project/rs-document/)
- [Issue Tracker](https://github.com/cam-barts/rs_document/issues)
