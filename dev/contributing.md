---
documentation_type: how-to
title: Contributing Guide
description: How to contribute to rs_document
---

# Contributing to rs_document

Thank you for your interest in contributing to rs_document!

## Development Setup

This project uses [uv](https://github.com/astral-sh/uv) for fast Python package management and [nox](https://nox.thea.codes/) for automated testing across Python versions.

### Prerequisites

1. **Install Rust**: Follow the instructions at [rustup.rs](https://rustup.rs/)
2. **Install uv**:

   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

3. **Install nox** (optional, for multi-version testing):

   ```bash
   uv tool install nox
   ```

### Quick Start with uv

```bash
# Clone the repository
git clone https://github.com/cam-barts/rs_document.git
cd rs_document

# Create a virtual environment and install dev dependencies
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e ".[dev]"

# Build the Rust extension
maturin develop

# Run tests
pytest python/tests/

# Run quick tests (excluding slow performance tests)
pytest python/tests/ -m "not slow"
```

### Development Workflow

#### 1. Making Changes

After making changes to the Rust code in `src/lib.rs`, rebuild:

```bash
maturin develop
```

For a production-optimized build:

```bash
maturin develop --release
```

#### 2. Running Tests

```bash
# Run all tests (includes property-based tests)
pytest python/tests/ -v

# Run only fast tests (excludes slow performance tests)
pytest python/tests/ -m "not slow" -v

# Run only property-based tests with Hypothesis
pytest python/tests/test_hypothesis_properties.py -v

# Run with more examples (default is 100, increase for thorough testing)
pytest python/tests/test_hypothesis_properties.py --hypothesis-seed=random

# Reproduce a specific Hypothesis failure
pytest python/tests/test_hypothesis_properties.py --hypothesis-seed=12345

# Run with coverage
pytest python/tests/ --cov=rs_document --cov-report=html
```

**Hypothesis Testing Tips:**

- Property tests run 100 examples by default (fast enough for development)
- CI runs the same tests for consistency
- When a test fails, Hypothesis provides a seed to reproduce it
- Add `@settings(max_examples=1000)` for more thorough testing of critical properties

#### 3. Testing Across Python Versions

Use nox to test against Python 3.8 through 3.13:

```bash
# Run tests on all Python versions
nox

# Run only fast tests on all versions
nox -s tests_quick

# Run only on specific Python version
nox -s tests-3.11

# Run linting
nox -s lint

# Format code
nox -s format_code
```

#### 4. Linting and Formatting

**Python code:**

```bash
# Check with ruff
ruff check python/

# Format with ruff
ruff format python/

# Auto-fix issues
ruff check --fix python/
```

**Rust code:**

```bash
# Format
cargo fmt

# Lint
cargo clippy --all-targets -- -D warnings

# Run Rust tests (if any)
cargo test
```

#### 5. Pre-commit Hooks with prek

This project uses [prek](https://prek.j178.dev/), a faster Rust-based alternative to pre-commit.

Install prek hooks to automatically check your code before commits:

```bash
# prek is installed with dev dependencies
prek install

# Run manually on all files
prek run --all-files

# Run specific hook
prek run ruff

# List all available hooks
prek list
```

**Alternative installation methods:**

```bash
# Via uv (recommended)
uv tool install prek

# Via standalone installer
curl --proto '=https' --tlsv1.2 -LsSf https://github.com/j178/prek/releases/download/v0.2.18/prek-installer.sh | sh

# Via homebrew
brew install prek
```

## Project Structure

```text
rs_document/
├── src/
│   └── lib.rs              # Rust implementation (core logic)
├── python/
│   ├── rs_document/
│   │   ├── __init__.py     # Python package entry point
│   │   └── post_processors.py  # Pure Python reference implementation
│   └── tests/
│       ├── test_all.py     # Basic tests
│       ├── test_cleaners.py  # Original cleaner tests
│       ├── test_cleaners_comprehensive.py  # Comprehensive cleaner tests
│       └── test_splitters_comprehensive.py  # Comprehensive splitter tests
├── Cargo.toml              # Rust dependencies
├── pyproject.toml          # Python project configuration
├── noxfile.py              # Multi-version testing configuration
└── CLAUDE.md               # AI assistant guidance
```

## Testing Philosophy

This project maintains high confidence through multiple testing strategies:

### 1. **Unit Tests**

Comprehensive tests for each cleaner and splitter method with known inputs and expected outputs.

### 2. **Edge Case Testing**

Manual tests for empty inputs, unicode, special characters, and boundary conditions.

### 3. **Property-Based Testing (Hypothesis)**

Automated generation of test cases to discover edge cases humans might miss:

- Tests invariants that should always hold (e.g., "chunks never exceed size")
- Generates thousands of random inputs to find corner cases
- Provides minimal failing examples when bugs are found
- Located in `python/tests/test_hypothesis_properties.py`

**When to add property tests:**

- New cleaner functions → test idempotence and data preservation
- New splitter logic → test chunk size limits and determinism
- Changes to metadata handling → test preservation across operations
- Core invariants → test properties that must always hold

### 4. **Metadata Preservation Tests**

Ensures data integrity across all operations.

### 5. **Performance Benchmarks**

Requires 15x speedup over pure Python implementation (marked with `@pytest.mark.slow`).

### 6. **Multi-Version Compatibility**

Tests across Python 3.10, 3.11, 3.12, 3.13 using nox.

## Code Coverage

This project aims for comprehensive test coverage while recognizing its hybrid Rust/Python nature:

### Coverage Goals

- **Python wrapper code** (`python/rs_document/__init__.py`): 100% coverage ✅
- **Python reference implementation** (`python/rs_document/post_processors.py`): 100% coverage ✅
- **Rust production code** (`src/lib.rs`): Tested via 102 Python tests (including 20 property-based tests)

### Running Coverage Reports

```bash
# Python wrapper coverage
nox -s coverage

# Python reference implementation coverage
nox -s coverage_post_processors

# Rust code coverage (requires Rust 1.82+)
nox -s coverage_rust         # Using tarpaulin
nox -s coverage_rust_llvm    # Using llvm-cov (alternative)

# All coverage at once (Python + Rust)
nox -s coverage_all

# View HTML reports
open htmlcov/index.html                     # Python wrapper
open htmlcov_post_processors/index.html     # Reference implementation
open coverage/rust/index.html               # Rust (tarpaulin)
open coverage/rust-llvm/index.html          # Rust (llvm-cov)
```

### Understanding Hybrid Coverage

**Important**: This is a **Rust/Python hybrid project**:

- **Production code**: `src/lib.rs` (Rust) - what users actually run
- **Python wrapper**: `python/rs_document/__init__.py` - minimal PyO3 bindings
- **Reference implementation**: `python/rs_document/post_processors.py` - pure Python version used only for benchmarking

The Rust code is thoroughly tested through the Python test suite:

- 76 unit and comprehensive tests
- 20 property-based tests (Hypothesis)
- 6 performance benchmark tests

For Rust-specific code coverage (requires newer Rust toolchain):

```bash
# Install cargo-llvm-cov (requires Rust 1.82+)
cargo install cargo-llvm-cov

# Generate Rust coverage report
cargo llvm-cov --html

# Or use cargo-tarpaulin
cargo install cargo-tarpaulin
cargo tarpaulin --out Html
```

## Performance Requirements

When adding features or making changes:

- Must process at least 15,000 documents per second
- Must be at least 15x faster than pure Python implementation
- Run performance tests: `pytest python/tests/test_all.py -m slow`

## Submitting Changes

1. **Fork the repository** and create a feature branch
2. **Make your changes** following the project's coding style
3. **Add tests** for new functionality
4. **Run the full test suite**: `nox`
5. **Ensure linting passes**: `nox -s lint`
6. **Update documentation** if needed
7. **Submit a pull request** with a clear description

## Code Style

- **Python**: Follow PEP 8, enforced by ruff
- **Rust**: Follow Rust conventions, enforced by cargo fmt and clippy
- **Line length**: 88 characters (Black-compatible)
- **Docstrings**: NumPy style

## Questions?

Feel free to open an issue for:

- Bug reports
- Feature requests
- Questions about the codebase
- Performance concerns

Thank you for contributing!
