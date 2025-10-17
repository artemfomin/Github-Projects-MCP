# Architecture Details

## Three-Layer Design Philosophy

The project uses strict separation of concerns with three distinct layers:

### Layer 1: MCP Server (`server.py`)
**Responsibility**: Expose tools to Claude Code via FastMCP

- Defines 15 `@mcp.tool()` decorated functions
- Handles user-facing API (parameters, formatting, error messages)
- Returns JSON strings for Claude consumption
- No direct dependency on GitHub - only uses `TaskManagerInterface`

**Key Functions**:
- Tool definitions (get_tickets, add_comment, etc.)
- Response formatting (model_dump to JSON)
- Context access pattern
- Error handling for user-facing messages

### Layer 2: TaskManagerInterface (`interfaces/task_manager.py`)
**Responsibility**: Define contract for any task management system

- Abstract Base Class (ABC) with 15 abstract methods
- Platform-agnostic method signatures
- Uses Pydantic models (not GitHub-specific types)
- Enables swapping implementations without changing server

**Contract**: All task managers must implement:
1. `get_tickets()` - List tickets with filters
2. `get_ticket()` - Get single ticket
3. `get_comments()` - List comments
4. `add_comment()` - Create comment
5. `get_labels()` - List available labels
6. `get_ticket_labels()` - Get ticket's labels
7. `add_label()` - Add label to ticket
8. `update_status()` - Change ticket status
9. `add_branch()` - Link branch
10. `add_pull_request()` - Link PR
11. `add_subtask()` - Create subtask relationship
12. `assign_ticket()` - Assign to user
13. `assign_to_self()` - Assign to self
14. `get_milestones()` - List milestones
15. `add_milestone()` - Add ticket to milestone

### Layer 3: GitHubProjectsClient (`github/client.py`)
**Responsibility**: Concrete GitHub implementation

- Implements all `TaskManagerInterface` methods
- Uses GitHub GraphQL API (reads) + REST API (writes)
- Parses GitHub responses into Pydantic models
- Handles GitHub-specific authentication and errors
- All GitHub knowledge isolated here

## Data Flow

```
User Request (Claude)
    ↓
MCP Tool (server.py)
    ↓
TaskManagerInterface (abstract method)
    ↓
GitHubProjectsClient (concrete implementation)
    ↓
GitHub API (GraphQL/REST)
    ↓
Pydantic Models (Ticket, Comment, etc.)
    ↓
JSON Response to Claude
```

## Server Lifecycle

### Initialization (`server_lifespan`)
```python
@asynccontextmanager
async def server_lifespan():
    # 1. Load environment variables
    settings = Settings()
    
    # 2. Initialize concrete client
    task_manager = GitHubProjectsClient(
        token=settings.github_token,
        owner=settings.github_owner,
        repo=settings.github_repo,
        project_number=settings.github_project_number,
    )
    
    # 3. Make available to all tools
    yield {"task_manager": task_manager}
```

### Context Access in Tools
```python
@mcp.tool()
async def get_tickets(ctx: Context, status: str | None = None):
    # Access injected task manager
    task_manager: TaskManagerInterface = ctx.request_context.lifespan_context.task_manager
    
    # Use interface methods (not GitHub-specific)
    tickets = await task_manager.get_tickets(status=status)
    
    # Format for Claude
    return json.dumps([t.model_dump() for t in tickets])
```

## Data Models (Platform-Agnostic)

### Ticket Model
```python
class Ticket(BaseModel):
    id: str              # Node ID or ticket number
    number: int
    title: str
    body: str | None
    status: str
    assignee: str | None
    labels: list[str]
    created_at: str
    updated_at: str
```

### Other Models
- `Comment`: id, body, author, created_at
- `Label`: name, color, description
- `Milestone`: title, description, due_date, state

## API Strategy

### GraphQL for Reads (Efficiency)
- Fetch multiple fields in single request
- Reduce over-fetching
- Better for complex queries
- Used by: `get_tickets`, `get_ticket`, `get_comments`, etc.

### REST for Writes (Simplicity)
- Simpler mutation syntax
- Better error messages
- Easier to implement
- Used by: `add_comment`, `add_label`, `update_status`, etc.

## Adding New Task Manager

To replace GitHub with Jira/Linear/etc:

### Step 1: Create Implementation
```python
# jira/client.py
class JiraClient(TaskManagerInterface):
    def __init__(self, url: str, username: str, token: str):
        self.client = JiraAPI(url, username, token)
    
    async def get_tickets(self, status: str | None = None) -> list[Ticket]:
        # Jira-specific API call
        issues = await self.client.search_issues(...)
        # Parse to Pydantic Ticket model
        return [self._parse_issue(i) for i in issues]
    
    # ... implement all 15 methods
```

### Step 2: Update Server
```python
# server.py
from .jira import JiraClient

@asynccontextmanager
async def server_lifespan():
    settings = Settings()
    task_manager = JiraClient(  # Changed from GitHubProjectsClient
        url=settings.jira_url,
        username=settings.jira_username,
        token=settings.jira_token,
    )
    yield {"task_manager": task_manager}
```

### Step 3: Update Config
```python
# config.py
class Settings(BaseSettings):
    jira_url: str
    jira_username: str
    jira_token: str
```

**No changes needed in MCP tools!** They only depend on `TaskManagerInterface`.

## Important Patterns

### Ticket ID Flexibility
```python
# Accepts both formats:
ticket = await client.get_ticket("42")           # Issue number
ticket = await client.get_ticket("I_kwDO...")    # Node ID

# Implementation handles detection
if ticket_id.isdigit():
    # Query by issue number
else:
    # Query by node ID
```

### Error Handling
```python
# GraphQL errors
if "errors" in response:
    raise ValueError(f"GraphQL error: {response['errors']}")

# HTTP errors
try:
    response = await client.post(...)
    response.raise_for_status()
except httpx.HTTPError as e:
    # Propagates to MCP tool for user-facing error
    raise
```

### Async Context Management
```python
# Client lifetime managed by httpx
async with httpx.AsyncClient() as client:
    response = await client.post(url, json=data)
    # Client automatically closed
```

## Testing Strategy

- **Integration Tests**: Test against real GitHub API
- **Test Repository**: https://github.com/artemfomin/TestRepo
- **Async Tests**: Using pytest-asyncio (auto mode)
- **Fixtures**: Shared client setup in `conftest.py`
- **Coverage**: All 15 tools + error cases

## Security Considerations

- Tokens stored in `.env` (gitignored)
- Never log or expose tokens
- Use environment variables, not hardcoded secrets
- GitHub token needs `repo` + `project` scopes only
