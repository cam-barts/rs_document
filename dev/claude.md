---
documentation_type: reference
title: Claude Code Instructions
description: Guidance for Claude Code when working with this repository
---

# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a hybrid Rust/Python project that provides high-performance text processing for RAG (Retrieval Augmented Generation) applications. The core processing is implemented in Rust using PyO3 and compiled to a Python extension module via maturin. It reimplements LangChain's Document model and Unstructured.io's text cleaners with 15-75x performance improvements.

## Architecture

### Rust Core (`src/lib.rs`)

- **Document struct**: PyO3-wrapped struct with `page_content` (String) and `metadata` (HashMap<String, String>)
- **Text splitting**: Two main algorithms
    - `split_text()`: Recursively splits text by separators until chunks are below target size
    - `split_and_merge()`: Creates overlapping chunks (1/3 overlap) by splitting to 1/3 target size then merging groups of 3
- **Text cleaners**: Methods on Document struct that mutate `page_content` in-place
- **Parallel processing**: `clean_and_split_docs()` uses rayon for parallel document processing
- **PyO3 module**: Exports Document class and clean_and_split_docs function to Python

### Python Package (`python/rs_document/`)

- `__init__.py`: Re-exports the compiled Rust module
- `post_processors.py`: Pure Python reference implementation of Unstructured.io cleaners (vendored for performance testing)
- The compiled extension is `rs_document.cpython-*.so` built by maturin

### Key Design Decisions

- Metadata only supports String keys and values (HashMap<String, String>) for simplicity
- `recursive_character_splitter()` hardcodes 1/3 chunk_overlap and default separators ["\n\n", "\n", " ", ""]
- `.clean()` method runs all cleaners in sequence: whitespace → ligatures → bullets → non-ascii → paragraph grouping
- Performance target: minimum 15,000 docs/second, minimum 15x faster than Python implementation

## Development Commands

### Setup with uv (Recommended)

```bash
# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create virtual environment and install dependencies
uv venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
uv pip install -e ".[dev]"

# Build the extension
maturin develop
```

### Build and Install

```bash
# Development build and install
maturin develop

# Production build (optimized)
maturin develop --release

# Build wheels for distribution
maturin build --release --out dist
```

### Testing with nox (Multi-version Testing)

```bash
# Run tests across all Python versions (3.10-3.13)
nox

# Run only fast tests (skip slow performance tests)
nox -s tests_quick

# Run tests for specific Python version
nox -s tests-3.11

# Run with custom pytest args
nox -s tests-3.11 -- -v -k test_cleaners
```

### Testing with pytest (Single Version)

```bash
# Run all tests
pytest python/tests/ -v

# Run quick tests (excluding slow performance tests marked with @pytest.mark.slow)
pytest python/tests/ -m "not slow" -v

# Run specific test file
pytest python/tests/test_cleaners_comprehensive.py -v

# Run with coverage
pytest python/tests/ --cov=python/rs_document --cov-report=html --cov-report=term-missing
```

### Code Coverage

```bash
# Full coverage report (Python wrapper)
nox -s coverage

# post_processors.py reference implementation coverage (100%)
nox -s coverage_post_processors

# Or run directly with pytest (for main tests)
pytest python/tests/ --cov=python/rs_document --cov-report=html --cov-report=term-missing

# View HTML report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

**Coverage Status:**

- Python wrapper (`__init__.py`): 100% ✅
- Python reference (`post_processors.py`): 100% ✅ (70 tests in `test_post_processors_reference.py`)
- Rust production code: Tested via 102 Python tests (76 unit + 20 property-based + 6 performance)

For Rust-specific code coverage (requires Rust 1.82+):

```bash
cargo install cargo-llvm-cov
cargo llvm-cov --html
```

### Linting and Formatting

```bash
# Python linting with ruff
nox -s lint

# Python formatting with ruff
nox -s format_code

# Or directly:
ruff check python/
ruff format python/

# Rust linting
nox -s rust_lint

# Or directly:
cargo clippy --all-targets -- -D warnings
cargo fmt --check

# Run all checks with prek (faster pre-commit alternative)
prek run --all-files
```

### Installing Dependencies

```bash
# Development dependencies (includes pytest, hypothesis, linting, nox)
uv pip install -e ".[dev]"

# Test dependencies only (includes pytest, hypothesis, langchain-text-splitters)
uv pip install -e ".[test]"
```

## Working with the Codebase

### Modifying Cleaners

Cleaners are implemented as mutable methods on the Document struct in `src/lib.rs`. Each cleaner:

1. Takes `&mut self` to modify page_content in-place
2. Uses regex patterns or character operations for text transformation
3. Should maintain compatibility with the Python reference in `post_processors.py`

Example pattern used throughout:

```rust
fn clean_something(&mut self) {
    let text = &self.page_content;
    let cleaned_text = /* transformation */;
    self.page_content = cleaned_text;
}
```

### Modifying Splitters

Splitters return `Vec<Document>` with cloned metadata. The recursive splitter uses:

- `split_text()` for basic recursive splitting by separators
- `split_and_merge()` wrapper that creates 1/3 overlapping chunks for RAG use cases

### Testing Strategy

The project has comprehensive test coverage:

**Test Files:**

- `test_all.py`: Basic integration tests and performance benchmarks
- `test_cleaners.py`: Original cleaner tests
- `test_cleaners_comprehensive.py`: Comprehensive tests for all cleaners with edge cases
- `test_splitters_comprehensive.py`: Comprehensive tests for all splitters with edge cases
- `test_hypothesis_properties.py`: Property-based tests using Hypothesis (20 properties)

**Test Categories:**

- **Unit tests**: Each cleaner and splitter method tested individually
- **Edge case tests**: Empty strings, unicode, special characters, very long inputs
- **Property-based tests (Hypothesis)**: Automated generation of test inputs to find edge cases
    - 20 property tests in `test_hypothesis_properties.py`
    - Tests invariants like "chunks never exceed size", "metadata always preserved", "cleaners converge"
    - Found 2 critical bugs (index out of bounds, carriage return handling) that manual tests missed
    - Runs 100 examples per test by default
- **Metadata preservation tests**: Ensure metadata integrity across operations
- **Performance tests**: Marked with `@pytest.mark.slow`, require 15x speedup and 15k docs/sec
- **Multi-version tests**: nox runs tests against Python 3.10, 3.11, 3.12, 3.13

**Running Tests:**

- Quick tests: `pytest -m "not slow"` or `nox -s tests_quick`
- Full tests: `pytest` or `nox`
- Performance tests: `pytest -m slow`
- Property tests only: `pytest python/tests/test_hypothesis_properties.py -v`
- Reproduce Hypothesis failure: `pytest --hypothesis-seed=SEED_NUMBER`

### CI/CD

GitHub Actions workflow (`.github/workflows/CI.yml`) has three job groups:

**Test Job:**

- Tests against Python 3.10, 3.11, 3.12, 3.13
- Uses uv for fast environment setup
- Runs via nox for consistent testing

**Lint Job:**

- Python linting with ruff
- Rust linting with clippy and rustfmt
- Runs on Python 3.11

**Build Jobs:**

- Builds wheels for multiple platforms:
    - Linux: x86_64, x86, aarch64, armv7, s390x, ppc64le
    - Windows: x64, x86
    - macOS: x86_64, aarch64
- Releases to PyPI automatically on git tags via maturin-action

### Pre-commit Hooks with prek

The project uses [prek](https://prek.j178.dev/) (a faster Rust-based pre-commit alternative) with configuration in `.pre-commit-config.yaml`:

- Trailing whitespace and EOF fixes
- YAML/TOML validation
- Ruff linting and formatting
- Cargo fmt and clippy

**prek** is fully compatible with pre-commit configs but offers:

- Significantly faster execution (written in Rust)
- Single binary with no runtime dependencies
- Built-in uv integration for Python hooks
- Better monorepo support

Install with: `prek install` (after installing prek via `uv tool install prek` or other methods)

## Important Constraints

- **Metadata limitation**: Only string-to-string mappings supported in metadata
- **No chunk_overlap parameter**: Hardcoded to 1/3 of chunk_size
- **No custom separators**: Recursive splitter uses fixed separator list
- **Ruff configuration**: Uses very strict linting (ALL rules enabled) with max complexity 7
- **Minimum Python version**: 3.10
