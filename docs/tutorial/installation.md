---
title: Installation
description: How to install rs_document
---

# Installation

Learn how to install rs_document in your Python environment.

## Using pip

The simplest way to install rs_document:

```bash
pip install rs-document
```

## Using uv

If you're using [uv](https://github.com/astral-sh/uv) for faster package management:

```bash
uv pip install rs-document
```

## Verify Installation

Check that rs_document is installed correctly:

```python
import rs_document

# Check version
print(rs_document.__version__)

# Create a test document
doc = rs_document.Document(
    page_content="Hello, rs_document!",
    metadata={"test": "true"}
)
print(doc)
```

You should see output like:

```text
Document(page_content="Hello, rs_document!", metadata={"test": "true"})
```

## Requirements

- **Python**: 3.10 or higher
- **Platforms**: Linux, macOS, Windows (x86_64 and ARM)

## Pre-built Wheels

rs_document provides pre-built wheels for most platforms:

- **Linux**: x86_64, aarch64, armv7, i686, s390x, ppc64le
- **macOS**: x86_64 (Intel), aarch64 (Apple Silicon)
- **Windows**: x64, x86

If a wheel isn't available for your platform, pip will automatically compile from source (requires Rust toolchain).

## Installing from Source

If you need to build from source:

### Prerequisites

1. Install Rust: [https://rustup.rs](https://rustup.rs)
2. Install Python development headers

### Build

```bash
pip install maturin
git clone https://github.com/cam-barts/rs_document.git
cd rs_document
maturin develop --release
```

## Troubleshooting

### "No matching distribution found"

Make sure you're using Python 3.10 or higher:

```bash
python --version
```

### Build Errors

If building from source fails:

1. Ensure Rust is installed: `rustc --version`
2. Update Rust: `rustup update`
3. Check Python headers are installed (python3-dev on Ubuntu)

## Next Steps

Now that rs_document is installed, let's create your [first document](first-document.md)!
