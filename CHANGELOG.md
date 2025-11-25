## v0.1.3 (2025-11-25)


- fix(github-release): clean up changelog formatting in release notes
- - Remove double bullets (- -) from changelog extraction
- Remove emoji lines, Co-Authored-By, and Signed-off-by lines
- Remove empty bullet lines
- This produces cleaner, more readable release notes
- 🤖 Generated with [Claude Code](https://claude.com/claude-code)
- Co-Authored-By: Claude <noreply@anthropic.com>

## v0.1.2 (2025-11-25)


- ci(github-release): improve release notes formatting and add build artifacts
- - Extract only current version from CHANGELOG instead of entire file
- Download all wheel artifacts (Linux, Windows, macOS, sdist)
- Attach artifacts to GitHub release for easy distribution
- Improved changelog extraction logic with fallback handling
- This fixes the release page to show clean, readable notes for each release
with all platform wheels available for download.
- 🤖 Generated with [Claude Code](https://claude.com/claude-code)
- Co-Authored-By: Claude <noreply@anthropic.com>

## v0.1.1 (2025-11-25)


- build(commitizen): configure all conventional commit types to trigger version bumps
- - Switched to cz_customize plugin with custom bump patterns
- feat commits trigger MINOR bumps
- All other commit types (fix, docs, build, chore, ci, test, style, refactor, perf) trigger PATCH bumps
- This ensures every passing CI run results in a version bump and PyPI release
- 🤖 Generated with [Claude Code](https://claude.com/claude-code)
- Co-Authored-By: Claude <noreply@anthropic.com>
- build(uv.lock): add uv.lock file for reproducible builds and enable uv caching
- - Removed uv.lock from .gitignore to track dependency versions
- This enables enable-cache: true in GitHub Actions workflows
- Ensures consistent dependency resolution across CI runs
- 🤖 Generated with [Claude Code](https://claude.com/claude-code)
- Co-Authored-By: Claude <noreply@anthropic.com>
- ci(github-actions): ensure github actions always bump the version so every CI success results in new pypi project
- Signed-off-by: Cam Barts <camerond.barts@gmail.com>
- build(readme.md): removed frontmatter that messes up the pypi and githup pages
- Signed-off-by: Cam Barts <camerond.barts@gmail.com>
- docs(updated-doc-formatting): indented markdown lists to 4 spaces for mkdocs
- Signed-off-by: Cam Barts <camerond.barts@gmail.com>

## v0.1.0 (2025-11-25)

### Feat

- **claude updates**: updated tests and documentation
