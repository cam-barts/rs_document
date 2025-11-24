---
title: How-To Guides Overview
description: Task-based guides for common rs_document workflows
---

# How-To Guides Overview

This section provides focused, task-based guides for working with rs_document. Each guide covers a specific workflow or use case with practical examples.

## Getting Started

- **[Loading Documents](loading-documents.md)** - Create documents from files and manage metadata
- **[Cleaning Tasks](cleaning-tasks.md)** - Remove bullets, ligatures, and special characters
- **[Splitting Tasks](splitting-tasks.md)** - Split documents with different strategies

## Advanced Workflows

- **[Batch Operations](batch-operations.md)** - Process multiple documents efficiently
- **[Vector DB Preparation](vector-db-prep.md)** - Prepare documents for embedding and retrieval
- **[LangChain Integration](langchain-integration.md)** - Use rs_document with LangChain

## Quick Examples

### Basic Document Processing

```python
from rs_document import Document

# Create, clean, and split a document
doc = Document(
    page_content="Your text here...",
    metadata={"source": "example.txt"}
)

doc.clean()
chunks = doc.recursive_character_splitter(1000)
```

### Batch Processing

```python
from rs_document import clean_and_split_docs, Document

# Process multiple documents at once
documents = [...]  # Your documents
chunks = clean_and_split_docs(documents, chunk_size=1000)
```

## Common Use Cases

### RAG Applications

1. [Load your documents](loading-documents.md#create-documents-from-multiple-files)
2. [Clean the text](cleaning-tasks.md#clean-all-issues-at-once)
3. [Split into chunks](splitting-tasks.md#split-with-specific-chunk-size)
4. [Prepare for vector DB](vector-db-prep.md#prepare-documents-for-embedding)

### Text Processing Pipeline

1. [Create documents with metadata](loading-documents.md#create-a-document-from-a-file)
2. [Apply specific cleaners](cleaning-tasks.md#remove-specific-types-of-issues)
3. [Split with context overlap](splitting-tasks.md#split-and-maintain-context)
4. [Filter and organize chunks](batch-operations.md#filter-chunks-after-splitting)

## Need More Help?

- See the [API Reference](../index.md) for detailed method documentation
- Check the [Tutorial](../tutorial/) to learn the basics first
