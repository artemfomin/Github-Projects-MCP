# Code Style and Conventions

## Language Features
- **Python Version**: 3.10+ (use modern syntax)
- **Type Hints**: Required for all function signatures
  - Use `str | None` instead of `Optional[str]`
  - Use `list[str]` instead of `List[str]`
- **Async/Await**: All I/O operations must be async
- **Docstrings**: Google style for all public methods

## Naming Conventions
- **Files/Modules**: snake_case (e.g., `task_manager.py`)
- **Classes**: PascalCase (e.g., `GitHubProjectsClient`, `TaskManagerInterface`)
- **Functions/Methods**: snake_case (e.g., `get_tickets`, `add_comment`)
- **Constants**: UPPER_SNAKE_CASE (e.g., `GITHUB_TOKEN`)
- **Private**: Prefix with `_` (e.g., `_parse_response`)

## Code Organization
- **Line Length**: 100 characters maximum (enforced by ruff)
- **Imports**: Organized by ruff (stdlib → third-party → local)
- **Module Structure**:
  1. Module docstring
  2. Imports
  3. Constants
  4. Classes
  5. Functions
  6. Main block (if applicable)

## Type Checking
- **Tool**: pyright in "basic" mode
- **Configuration**: See `[tool.pyright]` in `pyproject.toml`
- All public APIs must have complete type hints
- Use Pydantic models for data validation

## Linting
- **Tool**: ruff
- **Selected Rules**: E, F, I, N, W, UP
  - E: pycodestyle errors
  - F: pyflakes
  - I: isort (import sorting)
  - N: pep8-naming
  - W: pycodestyle warnings
  - UP: pyupgrade (modern syntax)

## Architecture Patterns

### Abstraction Layer
- All task manager operations go through `TaskManagerInterface`
- `server.py` depends ONLY on `TaskManagerInterface`, never on concrete implementations
- GitHub-specific code isolated in `github/client.py`

### Dependency Injection
- Task manager client initialized in `server_lifespan` context manager
- Provided to tools via FastMCP context: `ctx.request_context.lifespan_context.task_manager`

### Data Models
- Use Pydantic for all data structures
- Models are platform-agnostic (work for any task manager)
- Located in `models/` directory

### Error Handling
- GraphQL errors → convert to `ValueError` with descriptive messages
- HTTP errors from httpx → raise directly
- Always include context in error messages

## Async Patterns
```python
# All I/O methods are async
async def get_tickets(self, status: str | None = None) -> list[Ticket]:
    async with httpx.AsyncClient() as client:
        response = await client.post(...)
    return tickets

# MCP tools are async
@mcp.tool()
async def get_tickets(ctx: Context, status: str | None = None):
    task_manager = ctx.request_context.lifespan_context.task_manager
    tickets = await task_manager.get_tickets(status=status)
    return json.dumps([t.model_dump() for t in tickets])
```

## Docstring Style (Google Format)
```python
async def get_ticket(self, ticket_id: str) -> Ticket:
    """Get a single ticket by ID or number.
    
    Args:
        ticket_id: Ticket ID (node ID) or issue number
        
    Returns:
        Ticket object with all details
        
    Raises:
        ValueError: If ticket not found or GraphQL error occurs
    """
    ...
```

## Testing Patterns
- Use pytest with pytest-asyncio
- Async tests automatically detected (`asyncio_mode = "auto"`)
- Test against real GitHub API (https://github.com/artemfomin/TestRepo)
- Use fixtures from `conftest.py` for common setup

## Configuration Management
- Use pydantic-settings for environment variables
- Store in `.env` file (gitignored)
- All settings in `config.py` as Pydantic model
- Never commit tokens or secrets

## Project-Specific Conventions

### Ticket ID Handling
- Accept both GitHub node IDs (`I_kwDO...`) and issue numbers (`"42"`)
- `get_ticket` method handles both formats automatically

### API Strategy
- GraphQL for reads (more efficient, batch queries)
- REST API for writes (simpler mutations, better error handling)

### Context Access Pattern
```python
@mcp.tool()
async def tool_name(ctx: Context, ...):
    task_manager: TaskManagerInterface = ctx.request_context.lifespan_context.task_manager
    # Use task_manager methods...
```
