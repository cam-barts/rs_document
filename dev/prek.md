---
documentation_type: how-to
title: Using prek for Pre-commit Hooks
description: Guide to using prek in this project
---

# Using prek for Pre-commit Hooks

This project uses [prek](https://prek.j178.dev/) instead of the traditional `pre-commit` tool.

## What is prek?

prek is a reimagined version of pre-commit, built in Rust. It's designed to be a faster, dependency-free, and drop-in alternative.

## Why prek over pre-commit?

1. **Faster Performance** 🚀
   - Written in Rust for maximum speed
   - Significantly faster than Python-based pre-commit
   - Smaller disk footprint

2. **No Dependencies** 📦
   - Single binary with no runtime dependencies
   - No Python installation required for the tool itself
   - Easier to install and maintain

3. **Built-in uv Integration** 🔧
   - Native support for uv package manager
   - Better Python environment handling
   - Faster hook execution for Python-based tools

4. **Drop-in Compatible** ✅
   - Uses the same `.pre-commit-config.yaml` format
   - No configuration changes needed
   - All existing hooks work as-is

5. **Monorepo Support** 🏗️
   - Built-in workspace mode
   - Better handling of multi-project repositories

## Installation

### Via uv (Recommended for this project)

```bash
uv tool install prek
```

### Via dev dependencies

```bash
# Already included when you run:
uv pip install -e ".[dev]"
```

### Via Homebrew (macOS/Linux)

```bash
brew install prek
```

### Via Standalone Installer

```bash
# Linux/macOS
curl --proto '=https' --tlsv1.2 -LsSf \
  https://github.com/j178/prek/releases/download/v0.2.18/prek-installer.sh | sh

# Windows (PowerShell)
# See https://prek.j178.dev/installation/
```

### Other Methods

- npm: `npm add -D @j178/prek`
- conda: `conda install conda-forge::prek`
- cargo: `cargo install --locked prek`
- See full list: <https://prek.j178.dev/installation/>

## Usage

### Initial Setup

```bash
# Install hooks in your local repository
prek install
```

### Running Hooks

```bash
# Run all hooks on all files
prek run --all-files

# Run all hooks on staged files (automatic on commit)
prek run

# Run specific hook
prek run ruff
prek run cargo-fmt

# Run on specific files
prek run --files python/tests/test_all.py

# Run hooks from last commit
prek run --last-commit
```

### Listing Hooks

```bash
# List all configured hooks with descriptions
prek list
```

### Updating

```bash
# If installed via standalone installer
prek self update

# If installed via uv tool
uv tool upgrade prek
```

## Configuration

This project's hooks are configured in `.pre-commit-config.yaml`. The configuration is identical to what pre-commit uses:

```yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      # ... more hooks

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.15
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format

  - repo: local
    hooks:
      - id: cargo-fmt
        name: cargo fmt
        entry: cargo fmt
        # ... Rust-specific hooks
```

## Hooks in This Project

1. **Standard Pre-commit Hooks**
   - `trailing-whitespace`: Remove trailing whitespace
   - `end-of-file-fixer`: Ensure files end with newline
   - `check-yaml`: Validate YAML files
   - `check-toml`: Validate TOML files
   - `check-added-large-files`: Prevent large files
   - `check-merge-conflict`: Check for merge conflicts
   - `mixed-line-ending`: Ensure consistent line endings

2. **Ruff (Python Linting & Formatting)**
   - `ruff`: Lint Python code with auto-fix
   - `ruff-format`: Format Python code

3. **Rust Tooling**
   - `cargo-fmt`: Format Rust code
   - `cargo-clippy`: Lint Rust code

## Troubleshooting

### Hook fails with "command not found"

Make sure the required tools are installed:

- Rust: `rustup` should be installed
- Python tools: Install dev dependencies with `uv pip install -e ".[dev]"`

### Hooks run slowly

prek should be faster than pre-commit, but if you experience slowness:

- Ensure you're using the latest version: `prek self update`
- Check if hooks are downloading dependencies (first run is slower)

### Skip hooks temporarily

```bash
# Skip all hooks for a commit
git commit --no-verify

# Skip specific hook
SKIP=cargo-clippy git commit
```

## Comparison with pre-commit

| Feature          | pre-commit              | prek                  |
|------------------|-------------------------|-----------------------|
| Language         | Python                  | Rust                  |
| Speed            | Moderate                | Fast                  |
| Dependencies     | Python + deps           | Single binary         |
| Config format    | .pre-commit-config.yaml | Same                  |
| Compatibility    | Standard                | Drop-in replacement   |
| uv integration   | No                      | Built-in              |
| Monorepo support | Limited                 | Built-in              |

## Resources

- Official site: <https://prek.j178.dev/>
- GitHub: <https://github.com/j178/prek>
- Installation guide: <https://prek.j178.dev/installation/>
- Configuration: <https://prek.j178.dev/configuration/>
