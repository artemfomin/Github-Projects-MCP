# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

MCP (Model Context Protocol) server for GitHub Projects with an extensible architecture for replacing GitHub with other task managers (Jira, etc.). Uses Python 3.10+ with async/await patterns.

**Key Design Principle**: Loose coupling through `TaskManagerInterface` abstraction layer - all GitHub-specific implementation is isolated in `github/client.py`.

## Development Commands

### Environment Setup
```bash
# Install dependencies (recommended - uses uv)
cd github-projects-mcp
uv sync --frozen --dev

# Alternative with pip
pip install -e .
```

### Testing
```bash
# All tests
uv run pytest

# Verbose output with logs
uv run pytest -v

# Single test
uv run pytest tests/test_github_client.py -k test_get_tickets

# Watch mode for development
uv run pytest --watch
```

### Code Quality
```bash
# Format code
uv run ruff format .

# Check style
uv run ruff check .

# Auto-fix issues
uv run ruff check . --fix

# Type checking
uv run pyright
```

### Running the MCP Server

```bash
# Direct execution
uv run python -m github_projects_mcp.server

# Alternative
python src/github_projects_mcp/server.py

# Development with MCP Inspector (opens web UI)
mcp dev src/github_projects_mcp/server.py
```

## Architecture

### Three-Layer Design

```
┌─────────────────────────────┐
│    MCP Server (FastMCP)     │  ← 15 tools exposed to Claude
│         server.py           │     (get_tickets, add_comment, etc.)
└──────────┬──────────────────┘
           │
           ▼
┌─────────────────────────────┐
│  TaskManagerInterface (ABC) │  ← Abstract contract for any task manager
│  interfaces/task_manager.py │     Enables replacing GitHub with Jira/etc.
└──────────┬──────────────────┘
           │
           ▼
┌─────────────────────────────┐
│  GitHubProjectsClient       │  ← Concrete GitHub implementation
│    github/client.py         │     Uses GraphQL + REST APIs
└─────────────────────────────┘
```

### Key Architectural Points

1. **Abstraction Layer**: `TaskManagerInterface` defines 15 abstract methods (get_tickets, add_comment, etc.) - ALL task manager implementations must provide these

2. **Dependency Flow**: `server.py` depends ONLY on `TaskManagerInterface`, never directly on `GitHubProjectsClient` - this enables swapping implementations

3. **Server Lifecycle**: `server_lifespan` context manager initializes the task manager client and provides it via FastMCP context to all tools

4. **Data Models**: Pydantic models in `models/` (Ticket, Comment, Label, Milestone) are platform-agnostic - they work for any task manager

5. **API Strategy**: GitHub client uses GraphQL for reads (more efficient) and REST API for writes (simpler mutations)

### File Responsibilities

- `server.py`: MCP tool definitions, user-facing functionality, formats responses for Claude
- `interfaces/task_manager.py`: Abstract interface contract - modify here to add new capabilities
- `github/client.py`: GitHub-specific API calls, GraphQL queries, data parsing
- `models/*.py`: Platform-agnostic data structures (Ticket, Comment, etc.)
- `config.py`: Environment variable loading via pydantic-settings

## Configuration

Environment variables (set in `.env` or passed via Claude Code config):

```bash
GITHUB_TOKEN=ghp_...           # Required: Personal Access Token (repo + project permissions)
GITHUB_OWNER=artemfomin        # Required: Repository owner
GITHUB_REPO=TestRepo           # Required: Repository name
GITHUB_PROJECT_NUMBER=1        # Optional: Default project number
```

## Testing Against Real GitHub

Tests use `https://github.com/artemfomin/TestRepo` - ensure `.env` has valid credentials before running tests.

## Adding a New Task Manager

To replace GitHub with another system (e.g., Jira):

1. Create `jira/client.py` implementing `TaskManagerInterface`
2. Implement all 15 abstract methods (get_tickets, add_comment, etc.)
3. Update `server.py` `server_lifespan` to instantiate your client instead:
   ```python
   from .jira import JiraClient
   task_manager = JiraClient(url=..., token=...)
   ```
4. Update `config.py` to load Jira-specific environment variables
5. MCP tools automatically work with new implementation - no changes needed

## MCP Tools Provided (17 total)

- **Ticket Creation**: `create_ticket`, `create_subtask`
- **Tickets**: `get_tickets`, `get_ticket`
- **Comments**: `get_comments`, `add_comment`
- **Labels**: `get_labels`, `get_ticket_labels`, `add_label`
- **Status**: `update_status`
- **Branches/PRs**: `add_branch`, `add_pull_request`
- **Subtasks**: `add_subtask`
- **Assignment**: `assign_ticket`, `assign_to_self`
- **Milestones**: `get_milestones`, `add_milestone`

## Important Patterns

### Ticket ID Handling
The client accepts both GitHub node IDs (`I_kwDO...`) and issue numbers (`"42"`). The `get_ticket` method handles both formats automatically.

### Error Handling
GraphQL errors are converted to `ValueError` with descriptive messages. HTTP errors from `httpx` are raised directly.

### Async Patterns
All methods are `async` - use `await` when calling task manager methods. FastMCP handles the async context automatically.

### Context Access in Tools
```python
@mcp.tool()
async def get_tickets(ctx: Context, ...):
    task_manager: TaskManagerInterface = ctx.request_context.lifespan_context.task_manager
    # Use task_manager methods...
```

## Code Style

- Line length: 100 characters (enforced by ruff)
- Python 3.10+ syntax (use `str | None`, not `Optional[str]`)
- Type hints required (checked by pyright in basic mode)
- Async/await for all I/O operations
- Docstrings in Google style for all public methods
