# Suggested Commands for GitHub Projects MCP

## Environment Setup
```bash
# Change to project directory
cd github-projects-mcp

# Install dependencies (recommended - uses uv)
uv sync --frozen --dev

# Alternative with pip
pip install -e .
```

## Testing
```bash
# Run all tests
uv run pytest

# Verbose output with logs
uv run pytest -v

# Run specific test file
uv run pytest tests/test_github_client.py

# Run specific test by name pattern
uv run pytest tests/test_github_client.py -k test_get_tickets

# Watch mode for development (if available)
uv run pytest --watch
```

## Code Quality (Run before committing)
```bash
# Format code (auto-fix)
uv run ruff format .

# Check style issues
uv run ruff check .

# Auto-fix style issues
uv run ruff check . --fix

# Type checking
uv run pyright
```

## Running the MCP Server
```bash
# Direct execution (module mode)
uv run python -m github_projects_mcp.server

# Alternative (script mode)
python src/github_projects_mcp/server.py

# Development with MCP Inspector (opens web UI)
mcp dev src/github_projects_mcp/server.py
```

## Git Commands (Windows)
```bash
# Check status
git status

# Check current branch
git branch

# Create feature branch
git checkout -b feature/your-feature-name

# Stage changes
git add .

# Commit with message
git commit -m "Your message"

# Push to remote
git push origin feature/your-feature-name
```

## File Operations (Windows)
```bash
# List files
dir
ls -la  # If Git Bash is available

# Find files
dir /s /b *.py  # Windows CMD
find . -name "*.py"  # Git Bash

# View file content
type filename.txt  # Windows CMD
cat filename.txt   # Git Bash

# Copy files
copy source dest  # Windows CMD
cp source dest    # Git Bash
```

## Environment Configuration
```bash
# Edit .env file (Windows)
notepad .env

# Check environment variables loaded
uv run python -c "from github_projects_mcp.config import Settings; s=Settings(); print(s)"
```

## Development Workflow
```bash
# 1. Install dependencies
uv sync --frozen --dev

# 2. Configure .env with GitHub token
notepad .env

# 3. Run tests to verify setup
uv run pytest -v

# 4. Make changes to code

# 5. Format and lint
uv run ruff format .
uv run ruff check . --fix

# 6. Type check
uv run pyright

# 7. Run tests again
uv run pytest

# 8. Test with MCP Inspector
mcp dev src/github_projects_mcp/server.py
```

## Common Debugging Commands
```bash
# Test GitHub client directly
uv run python -c "from github_projects_mcp.github import GitHubProjectsClient; print('Import OK')"

# Check Python version
python --version

# Check uv version
uv --version

# List installed packages
uv pip list
```
