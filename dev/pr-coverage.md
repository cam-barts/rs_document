---
documentation_type: explanation
title: Pull Request Coverage Comments
description: How coverage reports are posted to PRs
---

# Pull Request Coverage Comments

This repository automatically posts coverage reports as PR comments using GitHub
Actions.

## How It Works

When you create a pull request, the `coverage` job in `.github/workflows/CI.yml`:

1. **Runs coverage analysis** on Python code (wrapper + reference implementation)
2. **Generates coverage report** with file-by-file breakdown
3. **Posts comment to PR** with detailed coverage information
4. **Updates comment** on subsequent pushes to the same PR
5. **Shows summary** in GitHub Actions tab

## What You'll See

### PR Comment Format

The bot will post a comment like this:

```markdown
## Coverage Report

**Overall Coverage: 100.00%** ✅

### Coverage by File

| File | Stmts | Miss | Cover |
|------|-------|------|-------|
| python/rs_document/__init__.py | 4 | 0 | 100% |
| python/rs_document/post_processors.py | 104 | 0 | 100% |

**Coverage threshold**: 80% minimum (90% for green status)

### Rust Coverage

⚠️ Rust coverage requires toolchain 1.82+ (currently 1.81.0)

_Note: Rust code is thoroughly tested via 102 Python tests including 20
property-based tests_
```

### GitHub Actions Summary

In addition to the PR comment, the Actions summary shows:

- ✅ **100%** - Python wrapper (python/rs_document/)
- ✅ **100%** - post_processors.py reference
- ⚠️  Rust coverage not available (requires Rust 1.82+)

## Coverage Thresholds

| Status     | Coverage | Indicator         |
|------------|----------|-------------------|
| 🟢 Green   | ≥90%     | Excellent         |
| 🟠 Orange  | 80-89%   | Good              |
| 🔴 Red     | <80%     | Needs improvement |

## Viewing Detailed Reports

HTML coverage reports are uploaded as artifacts on every run:

1. Go to the **Actions** tab
2. Click on the workflow run for your PR
3. Scroll to **Artifacts** section
4. Download `coverage-reports.zip`
5. Extract and open `htmlcov/index.html` in a browser

## Troubleshooting

### "Coverage comment not posted"

**Possible causes:**

- PR is from a fork (GitHub security limitation)
- Workflow doesn't have `pull-requests: write` permission
- Coverage files weren't generated

**Solution:** Check the Actions logs for the coverage job

### "Coverage decreased"

If coverage drops below the threshold:

- Review the PR comment to see which files have missing coverage
- Add tests for uncovered lines
- Run `nox -s coverage` locally to verify

### "Rust coverage failed"

This is expected on Rust < 1.82. The CI job continues even if Rust coverage
fails:

- Python coverage still runs and reports
- Rust code is tested via Python tests
- No action needed unless you want to update Rust toolchain

## Configuration

Coverage comment behavior is configured in `.github/workflows/CI.yml`:

```yaml
- name: Comment coverage on PR
  if: github.event_name == 'pull_request'
  uses: py-cov-action/python-coverage-comment-action@v3
  with:
    GITHUB_TOKEN: ${{ github.token }}
    MINIMUM_GREEN: 90   # Green status at 90%+
    MINIMUM_ORANGE: 80  # Orange status at 80-89%
```

## Local Testing

To generate the same coverage report locally:

```bash
# Run coverage
nox -s coverage

# View report
open htmlcov/index.html
```

## No External Services

**Important:** This project does NOT use external coverage services (like
Codecov):

- All coverage is computed in GitHub Actions
- Reports are posted as PR comments
- No data leaves GitHub
- No API keys or tokens needed

This keeps your coverage data private and integrated with your workflow.
