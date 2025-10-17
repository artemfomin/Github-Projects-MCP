# Task Completion Checklist

When completing any task in this project, follow these steps:

## 1. Code Quality Checks

### Format Code
```bash
uv run ruff format .
```
- Auto-formats all Python files according to project standards
- Fixes line length, indentation, quotes, etc.

### Lint Code
```bash
uv run ruff check .
```
- Check for style issues
- If issues found, run auto-fix:
```bash
uv run ruff check . --fix
```

### Type Check
```bash
uv run pyright
```
- Verify type hints are correct
- Fix any type errors reported

## 2. Run Tests

### Run All Tests
```bash
uv run pytest
```

### Run with Verbose Output
```bash
uv run pytest -v
```

### Run Specific Test File (if relevant)
```bash
uv run pytest tests/test_github_client.py -v
```

**IMPORTANT**: All tests must pass before marking task complete!

## 3. Verify Integration (for MCP changes)

If you modified MCP tools or server functionality:

```bash
# Test with MCP Inspector
mcp dev src/github_projects_mcp/server.py
```

- Opens web UI in browser
- Test each modified tool manually
- Verify responses are correct

## 4. Documentation Updates

- Update docstrings if function signatures changed
- Update README.md if new features added
- Update CLAUDE.md if development workflow changed

## 5. Clean Workspace

- Remove any temporary test files
- Remove any debug print statements
- Check no `.env` changes are staged (should be gitignored)

```bash
git status
```

## 6. Git Workflow (if applicable)

```bash
# Check status
git status

# Stage changes
git add .

# Commit with descriptive message
git commit -m "feat: description of changes"

# Push to branch (not main!)
git push origin feature/branch-name
```

## Quick Validation Script

Run this sequence for complete validation:

```bash
# From project root (github-projects-mcp/)
uv run ruff format . && \
uv run ruff check . --fix && \
uv run pyright && \
uv run pytest -v
```

If all commands succeed, the code is ready!

## Pre-Commit Checklist Summary

- [ ] Code formatted (`ruff format`)
- [ ] No lint errors (`ruff check`)
- [ ] Type checking passes (`pyright`)
- [ ] All tests pass (`pytest`)
- [ ] MCP tools tested (if modified)
- [ ] Documentation updated (if needed)
- [ ] No temporary files left
- [ ] Git status clean (no unwanted files)

## Common Issues & Fixes

### Type Errors
- Add missing type hints
- Fix incorrect return types
- Import types from `typing` if needed

### Test Failures
- Check `.env` has valid GitHub token
- Verify TestRepo is accessible
- Check test assertions match current behavior

### Import Errors
- Run `uv sync` to reinstall dependencies
- Check Python version is 3.10+
- Verify virtual environment is activated

## When NOT to Commit
- Tests are failing
- Type checking has errors
- Lint errors remain
- `.env` file is modified (should be gitignored)
- Temporary/debug files present
