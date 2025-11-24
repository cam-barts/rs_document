"""Nox sessions for testing across multiple Python versions."""

from pathlib import Path

import nox

# Use uv as the default backend (automatically manages Python interpreters)
nox.options.default_venv_backend = "uv"

# Root directory of the project (parent of dev/)
ROOT_DIR = Path(__file__).parent.parent

# Test against all supported Python versions
nox.options.sessions = ["tests"]
PYTHON_VERSIONS = ["3.10", "3.11", "3.12", "3.13"]


@nox.session(python=PYTHON_VERSIONS)
def tests(session: nox.Session) -> None:
    """Run the test suite with pytest."""
    # Install maturin and build the extension
    session.install("maturin")

    # Build and install the package in development mode
    session.run(
        "maturin",
        "develop",
        "--release",
        "--manifest-path",
        str(ROOT_DIR / "Cargo.toml"),
    )

    # Install test dependencies
    session.install("pytest", "langchain-text-splitters", "hypothesis")

    # Run tests
    session.run("pytest", str(ROOT_DIR / "python/tests/"), "-v", *session.posargs)


@nox.session(python=PYTHON_VERSIONS)
def tests_quick(session: nox.Session) -> None:
    """Run quick tests (excluding slow performance tests)."""
    session.install("maturin")
    session.run(
        "maturin",
        "develop",
        "--release",
        "--manifest-path",
        str(ROOT_DIR / "Cargo.toml"),
    )
    session.install("pytest", "langchain-text-splitters", "hypothesis")

    # Run tests excluding performance tests
    session.run(
        "pytest",
        str(ROOT_DIR / "python/tests/"),
        "-v",
        "-m",
        "not slow",
        *session.posargs,
    )


@nox.session(python="3.11")
def lint(session: nox.Session) -> None:
    """Run linters with ruff."""
    session.install("ruff")

    # Change to root directory so ruff finds pyproject.toml
    session.chdir(str(ROOT_DIR))

    # Check Python code
    session.run("ruff", "check", "python/")

    # Check formatting
    session.run("ruff", "format", "--check", "python/")


@nox.session(python="3.11")
def format_code(session: nox.Session) -> None:
    """Format code with ruff."""
    session.install("ruff")

    # Change to root directory so ruff finds pyproject.toml
    session.chdir(str(ROOT_DIR))

    session.run("ruff", "format", "python/")
    session.run("ruff", "check", "--fix", "python/")


@nox.session(python="3.11")
def rust_lint(session: nox.Session) -> None:
    """Run Rust linters."""
    session.chdir(str(ROOT_DIR))
    session.run(
        "cargo", "clippy", "--all-targets", "--", "-D", "warnings", external=True
    )
    session.run("cargo", "fmt", "--check", external=True)


@nox.session(python="3.11")
def rust_test(session: nox.Session) -> None:
    """Run Rust tests."""
    session.chdir(str(ROOT_DIR))
    session.run("cargo", "test", external=True)


@nox.session(python="3.11")
def build(session: nox.Session) -> None:
    """Build the package."""
    session.install("maturin")
    session.run(
        "maturin",
        "build",
        "--release",
        "--out",
        "dist",
        "--manifest-path",
        str(ROOT_DIR / "Cargo.toml"),
    )


@nox.session(python="3.11")
def docs(session: nox.Session) -> None:
    """Build documentation (placeholder for future)."""
    session.log("Documentation building not yet implemented")


@nox.session(python="3.11")
def coverage(session: nox.Session) -> None:
    """Run tests with coverage reporting for Python wrapper.

    Note: This measures coverage of the Python wrapper code in python/rs_document/.
    The production Rust code in src/lib.rs is thoroughly tested via the Python
    test suite (102 tests including 20 property-based tests).

    For Rust code coverage, use cargo-llvm-cov or cargo-tarpaulin separately.
    """
    session.install("maturin")
    session.run(
        "maturin",
        "develop",
        "--release",
        "--manifest-path",
        str(ROOT_DIR / "Cargo.toml"),
    )
    session.install("pytest", "pytest-cov", "langchain-text-splitters", "hypothesis")

    session.run(
        "pytest",
        str(ROOT_DIR / "python/tests/"),
        "-m",
        "not slow",
        f"--cov={ROOT_DIR}/python/rs_document",
        "--cov-report=html",
        "--cov-report=term-missing",
        "--cov-report=json",
        *session.posargs,
    )


@nox.session(python="3.11")
def coverage_post_processors(session: nox.Session) -> None:
    """Run coverage specifically for post_processors.py reference implementation.

    The post_processors.py file is a pure Python reference implementation used
    for performance benchmarking. This session runs its tests in isolation to
    avoid PyO3 module reinitialization issues.
    """
    session.install("pytest", "pytest-cov")

    # Run in subprocess to avoid PyO3 issues
    session.chdir(str(ROOT_DIR))
    session.run(
        "bash",
        str(ROOT_DIR / "dev/run_post_processors_tests.sh"),
        external=True,
    )


@nox.session(python="3.11")
def coverage_rust(session: nox.Session) -> None:
    """Run Rust code coverage using cargo-tarpaulin.

    Requirements:
    - Rust 1.82+ toolchain
    - cargo-tarpaulin installed (script will attempt to install if missing)

    Note: This may fail on older Rust versions due to edition2024 requirements.
    Use 'coverage_rust_llvm' as an alternative.
    """
    session.log("Running Rust coverage with tarpaulin...")
    session.chdir(str(ROOT_DIR))
    session.run(
        "bash",
        str(ROOT_DIR / "dev/run_rust_coverage.sh"),
        "tarpaulin",
        external=True,
    )


@nox.session(python="3.11")
def coverage_rust_llvm(session: nox.Session) -> None:
    """Run Rust code coverage using cargo-llvm-cov.

    Requirements:
    - Rust 1.82+ toolchain with LLVM support
    - cargo-llvm-cov installed (script will attempt to install if missing)

    This is an alternative to tarpaulin and may work better on some systems.
    """
    session.log("Running Rust coverage with llvm-cov...")
    session.chdir(str(ROOT_DIR))
    session.run(
        "bash",
        str(ROOT_DIR / "dev/run_rust_coverage.sh"),
        "llvm-cov",
        external=True,
    )


@nox.session(python="3.11")
def coverage_all(session: nox.Session) -> None:
    """Run all coverage: Python wrapper, reference implementation, and Rust.

    This combines:
    - Python wrapper coverage (python/rs_document/)
    - Reference implementation coverage (post_processors.py)
    - Rust production code coverage (src/lib.rs)

    Note: Rust coverage requires Rust 1.82+ and may fail on older toolchains.
    """
    session.log("Running comprehensive coverage across all components...")

    # Python coverage
    session.log("\n=== 1/3: Python Wrapper Coverage ===")
    session.install("maturin")
    session.run(
        "maturin",
        "develop",
        "--release",
        "--manifest-path",
        str(ROOT_DIR / "Cargo.toml"),
    )
    session.install("pytest", "pytest-cov", "langchain-text-splitters", "hypothesis")
    session.run(
        "pytest",
        str(ROOT_DIR / "python/tests/"),
        f"--cov={ROOT_DIR}/python/rs_document",
        "--cov-report=html:htmlcov",
        "--cov-report=term-missing",
    )

    # Post processors coverage
    session.log("\n=== 2/3: Reference Implementation Coverage ===")
    session.chdir(str(ROOT_DIR))
    session.run(
        "bash",
        str(ROOT_DIR / "dev/run_post_processors_tests.sh"),
        external=True,
    )

    # Rust coverage (may fail, that's okay)
    session.log("\n=== 3/3: Rust Code Coverage ===")
    session.log("Attempting Rust coverage (requires Rust 1.82+)...")
    try:
        session.run(
            "bash",
            str(ROOT_DIR / "dev/run_rust_coverage.sh"),
            "tarpaulin",
            external=True,
        )
    except Exception as e:
        session.warn(f"Rust coverage failed (likely due to toolchain version): {e}")
        session.warn(
            "This is expected on Rust < 1.82. See docs/coverage.md for details."
        )

    session.log("\n=== Coverage Summary ===")
    session.log("✅ Python wrapper coverage: htmlcov/index.html")
    session.log("✅ Post processors coverage: htmlcov_post_processors/index.html")
    session.log("⚠️  Rust coverage: coverage/rust/index.html (if successful)")
