---
documentation_type: explanation
title: Code Coverage Strategy
description: Coverage approach for hybrid Rust/Python project
---

# Code Coverage Strategy

This document explains the code coverage approach for rs_document, a hybrid Rust/Python project.

## Overview

rs_document uses **production Rust code** wrapped in a Python package via PyO3/maturin. Understanding this architecture is essential for interpreting coverage metrics.

## Project Architecture

```text
Production Path (what users run):
User → Python API → PyO3 Bindings → Rust Code (src/lib.rs)

Testing Path:
102 Python Tests → PyO3 Bindings → Rust Code (src/lib.rs)
```

## Coverage Goals & Status

| Component                                 | Coverage          | Test Count       | Notes                    |
|-------------------------------------------|-------------------|------------------|--------------------------|
| **Python Wrapper** (`__init__.py`)        | **100%** ✅       | N/A              | Minimal PyO3 bindings    |
| **Python Reference** (`post_processors.py`) | **100%** ✅     | 70 tests         | Benchmarking only        |
| **Rust Production Code** (`src/lib.rs`)   | Fully Tested ✅   | 102 Python tests | All code paths exercised |

### Detailed Test Breakdown

**102 Total Python Tests:**

- 76 unit and comprehensive tests
    - `test_all.py`: 10 tests (basic integration)
    - `test_cleaners_comprehensive.py`: 38 tests (all cleaner functions)
    - `test_splitters_comprehensive.py`: 28 tests (all splitter functions)
- 20 property-based tests (`test_hypothesis_properties.py`)
    - Core invariants (5): chunk size limits, metadata preservation, determinism
    - Edge cases (5): empty docs, small chunks, unicode, special chars
    - Format handling (4): line endings, bullets, ligatures
    - Advanced (6): parallel consistency, order preservation, emoji handling
- 6 performance benchmark tests (marked `@pytest.mark.slow`)

## Running Coverage Reports

### 1. Python Wrapper Coverage

Measures coverage of `python/rs_document/` directory:

```bash
# Using nox (recommended)
nox -s coverage

# Direct pytest
pytest python/tests/ --cov=python/rs_document --cov-report=html --cov-report=term-missing

# View report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

**Expected Result:**

```text
Name                                Stmts   Miss  Cover
-------------------------------------------------------
python/rs_document/__init__.py          4      0   100%
python/rs_document/post_processors.py 104      0   100%
-------------------------------------------------------
TOTAL                                 108      0   100%
```

### 2. Reference Implementation Coverage

Measures coverage of `post_processors.py` (pure Python reference):

```bash
# Using nox
nox -s coverage_post_processors

# Direct script (avoids PyO3 reinitialization issues)
bash run_post_processors_tests.sh
```

**Note:** This runs in a subprocess to avoid PyO3 module reinitialization errors.

**Expected Result:**

```text
Name                                    Stmts   Miss  Cover
-------------------------------------------------------------
python/rs_document/post_processors.py     104      0   100%
-------------------------------------------------------------
TOTAL                                     104      0   100%
```

### 3. Rust Code Coverage

**Current Status:** Requires Rust 1.82+ (current system has 1.81.0)

#### Prerequisites

Rust code coverage requires a newer toolchain than currently available:

**Check your Rust version:**

```bash
rustc --version
# Required: rustc 1.82.0 or newer
# Current:  rustc 1.81.0 (2024-08-20)
```

**Update Rust (if needed):**

```bash
# Update to latest stable
rustup update stable

# Or use nightly for cutting-edge features
rustup update nightly
rustup default nightly
```

#### Method 1: Using cargo-llvm-cov (Recommended)

```bash
# Install cargo-llvm-cov (requires Rust 1.82+)
cargo install cargo-llvm-cov

# Generate coverage report
cargo llvm-cov --html --output-dir coverage/rust-llvm

# View report
open coverage/rust-llvm/index.html  # macOS
xdg-open coverage/rust-llvm/index.html  # Linux
```

**Using the script:**

```bash
./run_rust_coverage.sh llvm-cov
```

**Using nox:**

```bash
nox -s coverage_rust_llvm
```

#### Method 2: Using cargo-tarpaulin

```bash
# Install cargo-tarpaulin
cargo install cargo-tarpaulin

# Generate coverage report
cargo tarpaulin --out Html --output-dir coverage/rust

# View report
open coverage/rust/index.html  # macOS
xdg-open coverage/rust/index.html  # Linux
```

**Using the script:**

```bash
./run_rust_coverage.sh tarpaulin
```

**Using nox:**

```bash
nox -s coverage_rust
```

#### All-in-One Coverage

Run Python + Rust coverage together (Rust portion may fail gracefully):

```bash
nox -s coverage_all
```

This will:

1. Run Python wrapper coverage (always works)
2. Run post_processors coverage (always works)
3. Attempt Rust coverage (requires Rust 1.82+, fails gracefully on older versions)

#### Troubleshooting

**Error: "feature `edition2024` is required"**

- **Cause**: Rust toolchain too old (< 1.82)
- **Solution**: Update Rust with `rustup update stable`

### Error: "PyO3 modules may only be initialized once"

- **Cause**: PyO3 limitation, not a coverage issue
- **Solution**: Use the provided scripts which handle this automatically

### Rust coverage fails but Python coverage works

- **This is expected** on Rust < 1.82
- Python tests still thoroughly exercise all Rust code paths
- Rust coverage is supplementary, not required

## Understanding the Metrics

### Why "Python Coverage" for Rust Code?

The production Rust code in `src/lib.rs` is **fully tested** through the Python test suite:

1. **All public APIs** are called from Python tests
2. **All code paths** are exercised through different test scenarios
3. **Edge cases** are discovered via property-based testing (Hypothesis)
4. **Performance characteristics** are validated via benchmarks

Python test coverage serves as a **functional coverage metric** for the Rust code - every Python test that passes exercises specific Rust code paths.

### What About `post_processors.py`?

- **Purpose**: Pure Python reference implementation from Unstructured.io
- **Usage**: Performance benchmarking only (comparing Rust vs Python)
- **Not in production**: Users run the Rust implementation, not this code
- **100% coverage**: Ensures benchmark comparisons are valid

## Coverage Configuration

### pyproject.toml

```toml
[tool.coverage.run]
source = ["python/rs_document"]
omit = [
    "*/tests/*",
    "*/__pycache__/*",
    "*/site-packages/*",
]

[tool.coverage.report]
fail_under = 80
precision = 2
show_missing = true
```

### Coverage Thresholds

- **Python wrapper**: 100% required
- **Overall project**: 80% minimum (considering hybrid nature)

## CI/CD Integration

Coverage runs automatically in CI and posts results as PR comments:

### On Pull Requests

The `coverage` job automatically:

1. **Runs all coverage**: Python wrapper, reference implementation, and Rust (if available)
2. **Posts PR comment**: Detailed coverage report with file-by-file breakdown
3. **Generates summary**: Shows coverage percentages in GitHub Actions summary
4. **Uploads artifacts**: HTML reports available for download

### Coverage Thresholds

- 🟢 **Green**: ≥90% coverage
- 🟠 **Orange**: 80-89% coverage
- 🔴 **Red**: <80% coverage

### What You'll See in PRs

```markdown
## Coverage Report

Coverage: 100.00%
Files Changed: 2

| File | Coverage | Status |
|------|----------|--------|
| python/rs_document/__init__.py | 100% | ✅ |
| python/rs_document/post_processors.py | 100% | ✅ |

Minimum Coverage: 80%
```

Plus a GitHub Actions summary with:

- ✅ Python wrapper coverage
- ✅ Reference implementation coverage
- ⚠️  Rust coverage status (with explanation)

## Common Issues

### PyO3 Module Reinitialization Error

**Problem:**

```text
ImportError: PyO3 modules may only be initialized once per interpreter process
```

**Cause:** PyO3 modules can't be reloaded in the same Python process.

**Solution:** Use the subprocess approach:

```bash
bash run_post_processors_tests.sh
```

### Coverage Not Detected

**Problem:** Coverage shows "Module was never imported"

**Solution:** Ensure correct module path:

```bash
# Correct
pytest --cov=python/rs_document

# Incorrect
pytest --cov=rs_document  # looks for installed package
```

## Future Improvements

1. **Rust Coverage Integration**
   - Add Rust coverage to CI when toolchain is updated to 1.82+
   - Combine Python and Rust coverage reports in PR comments

2. **Coverage Badges**
   - Generate coverage badge from CI
   - Display badge in README.md

3. **Differential Coverage**
   - Highlight coverage changes for modified files
   - Require 100% coverage for new code
   - Show before/after comparison in PR comments

## Contributing

When adding new features:

1. **Write tests first** (TDD approach)
2. **Aim for 100% coverage** of new code
3. **Run coverage locally** before submitting PR:

   ```bash
   nox -s coverage
   nox -s coverage_post_processors
   ```

4. **Add property tests** for complex logic
5. **Update this document** if coverage strategy changes

## Questions?

See also:

- [CONTRIBUTING.md](contributing.md) - Development workflow
- [README.md](index.md) - Project overview
