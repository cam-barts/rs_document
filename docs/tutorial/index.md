---
title: Tutorial
description: Learn how to use rs_document step by step
---

# Tutorial: Getting Started with RS Document

Welcome! This tutorial will teach you how to use rs_document to clean and split text documents for RAG applications.

## What You'll Learn

By the end of this tutorial, you'll know how to:

- Install and set up rs_document
- Create and work with documents
- Clean messy text from various sources
- Split documents into chunks for embeddings
- Process multiple documents efficiently

## Prerequisites

- Python 3.10 or higher
- Basic familiarity with Python
- pip or uv package manager

## Tutorial Structure

Follow these pages in order:

1. **[Installation](installation.md)** - Set up rs_document
2. **[First Document](first-document.md)** - Create and understand documents
3. **[Cleaning Text](cleaning.md)** - Remove artifacts and normalize text
4. **[Splitting Documents](splitting.md)** - Break documents into chunks
5. **[Batch Processing](batch-processing.md)** - Process multiple documents efficiently

Each page builds on the previous one, so we recommend following them in sequence if you're new to rs_document.

## Quick Start

If you want to jump right in:

```bash
pip install rs-document
```

```python
from rs_document import Document, clean_and_split_docs

# Create a document
doc = Document(
    page_content="Your text here...",
    metadata={"source": "example.txt"}
)

# Clean and split
doc.clean()
chunks = doc.recursive_character_splitter(1000)
```

Now continue to [Installation](installation.md) to get started!
