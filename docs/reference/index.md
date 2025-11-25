---
title: API Reference Overview
description: Complete API documentation for rs_document - navigate to specific reference pages
---

# API Reference

Complete reference documentation for all public APIs in rs_document.

## Quick Navigation

### Core Components

- **[Document Class](document-class.md)** - Document constructor and attributes
    - Constructor and initialization
    - `page_content` attribute
    - `metadata` attribute

### Document Processing

- **[Cleaning Methods](cleaning-methods.md)** - Text cleaning and normalization
    - `clean()` - Run all cleaners
    - `clean_extra_whitespace()` - Normalize whitespace
    - `clean_ligatures()` - Convert typographic ligatures
    - `clean_bullets()` - Remove bullet characters
    - `clean_non_ascii_chars()` - Remove non-ASCII characters
    - `group_broken_paragraphs()` - Join split paragraphs

- **[Splitting Methods](splitting-methods.md)** - Document chunking strategies
    - `recursive_character_splitter()` - Smart splitting with overlap
    - `split_on_num_characters()` - Fixed-size splitting

### Utilities

- **[Utility Functions](utility-functions.md)** - Batch processing and helpers
    - `clean_and_split_docs()` - Parallel processing for multiple documents

### Reference Information

- **[Types and Constants](types-and-constants.md)** - Type hints, defaults, and error handling
    - Type signatures
    - Default values and constants
    - Error handling patterns
    - Compatibility notes

## Overview

rs_document is a high-performance Python library for document processing, built with Rust for speed. The library provides:

- **Document representation**: Simple, LangChain-compatible document structure
- **Text cleaning**: Normalize whitespace, remove artifacts, fix ligatures
- **Document splitting**: Split large documents into chunks for RAG applications
- **Parallel processing**: Process thousands of documents efficiently

## Basic Usage

```python
from rs_document import Document, clean_and_split_docs

# Create a document
doc = Document(
    page_content="Your text content here",
    metadata={"source": "example.txt", "page": "1"}
)

# Clean and split
doc.clean()
chunks = doc.recursive_character_splitter(chunk_size=1000)

# Or process multiple documents in parallel
documents = [doc1, doc2, doc3]
all_chunks = clean_and_split_docs(documents, chunk_size=1000)
```

## Performance

- **Fast**: 20-25x faster than pure Python implementations
- **Parallel**: Automatically uses all CPU cores for batch processing
- **Scalable**: Process ~23,000 documents per second on typical hardware

## Requirements

- Python 3.10 or higher
- Pre-built wheels available for most platforms (Linux, macOS, Windows)
