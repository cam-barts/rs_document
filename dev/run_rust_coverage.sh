#!/bin/bash
# Script to run Rust code coverage using either tarpaulin or llvm-cov
#
# Requirements:
# - Rust 1.82+ (for cargo-llvm-cov)
# - OR Rust 1.81+ (for cargo-tarpaulin, though may have issues with edition2024 dependencies)
#
# Usage:
#   ./run_rust_coverage.sh [tarpaulin|llvm-cov]
#   Default: tarpaulin

set -e  # Exit on error

COVERAGE_TOOL="${1:-tarpaulin}"

# Get the project root directory (parent of dev/)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

echo "========================================"
echo "Rust Code Coverage"
echo "========================================"
echo ""

# Check Rust version
RUST_VERSION=$(rustc --version | awk '{print $2}')
echo "Rust version: $RUST_VERSION"
echo ""

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to run tarpaulin
run_tarpaulin() {
    echo "Running cargo-tarpaulin..."
    echo ""

    if ! command_exists cargo-tarpaulin; then
        echo "❌ cargo-tarpaulin not found. Installing..."
        echo ""
        echo "Note: This requires Rust with edition2024 support."
        echo "If installation fails, try updating Rust:"
        echo "  rustup update stable"
        echo ""

        cargo install cargo-tarpaulin || {
            echo ""
            echo "❌ Failed to install cargo-tarpaulin."
            echo "This may be due to Rust version requirements."
            echo ""
            echo "Alternatives:"
            echo "1. Update Rust: rustup update stable"
            echo "2. Use llvm-cov instead: ./run_rust_coverage.sh llvm-cov"
            echo "3. Wait for Rust toolchain update"
            exit 1
        }
    fi

    echo "✅ cargo-tarpaulin is installed"
    echo ""

    # Create output directory
    mkdir -p coverage/rust

    echo "Running coverage analysis..."
    echo ""

    # Run tarpaulin with configuration from Cargo.toml
    cargo tarpaulin \
        --out Html \
        --out Json \
        --out Lcov \
        --output-dir coverage/rust \
        --timeout 300 \
        --fail-under 80 \
        --verbose

    echo ""
    echo "✅ Coverage report generated!"
    echo ""
    echo "HTML report: coverage/rust/index.html"
    echo "JSON report: coverage/rust/tarpaulin-report.json"
    echo "LCOV report: coverage/rust/lcov.info"
    echo ""
    echo "To view HTML report:"
    echo "  open coverage/rust/index.html      # macOS"
    echo "  xdg-open coverage/rust/index.html  # Linux"
}

# Function to run llvm-cov
run_llvm_cov() {
    echo "Running cargo-llvm-cov..."
    echo ""

    if ! command_exists cargo-llvm-cov; then
        echo "❌ cargo-llvm-cov not found. Installing..."
        echo ""
        echo "Note: This requires Rust 1.82+ with LLVM support."
        echo ""

        cargo install cargo-llvm-cov || {
            echo ""
            echo "❌ Failed to install cargo-llvm-cov."
            echo "This may be due to Rust version requirements."
            echo ""
            echo "Alternatives:"
            echo "1. Update Rust: rustup update stable"
            echo "2. Use tarpaulin instead: ./run_rust_coverage.sh tarpaulin"
            echo "3. Wait for Rust toolchain update"
            exit 1
        }
    fi

    echo "✅ cargo-llvm-cov is installed"
    echo ""

    # Create output directory
    mkdir -p coverage/rust-llvm

    echo "Running coverage analysis..."
    echo ""

    # Run llvm-cov
    cargo llvm-cov \
        --html \
        --output-dir coverage/rust-llvm \
        --ignore-filename-regex 'tests?\.rs$' \
        --fail-under-lines 80

    echo ""
    echo "✅ Coverage report generated!"
    echo ""
    echo "HTML report: coverage/rust-llvm/index.html"
    echo ""
    echo "To view HTML report:"
    echo "  open coverage/rust-llvm/index.html      # macOS"
    echo "  xdg-open coverage/rust-llvm/index.html  # Linux"
}

# Main execution
case "$COVERAGE_TOOL" in
    tarpaulin)
        run_tarpaulin
        ;;
    llvm-cov|llvm)
        run_llvm_cov
        ;;
    *)
        echo "❌ Unknown coverage tool: $COVERAGE_TOOL"
        echo ""
        echo "Usage: $0 [tarpaulin|llvm-cov]"
        echo ""
        echo "Examples:"
        echo "  $0              # Use tarpaulin (default)"
        echo "  $0 tarpaulin    # Use tarpaulin explicitly"
        echo "  $0 llvm-cov     # Use llvm-cov"
        exit 1
        ;;
esac

echo ""
echo "========================================"
echo "Done!"
echo "========================================"
