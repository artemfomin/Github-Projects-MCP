# GitHub Projects MCP Server - Project Overview

## Purpose
MCP (Model Context Protocol) server for GitHub Projects with extensible architecture for replacing GitHub with other task managers (Jira, etc.). Provides 15 tools for managing GitHub issues, comments, labels, milestones, and project workflows through Claude Code.

## Key Design Principle
**Loose coupling through `TaskManagerInterface` abstraction layer** - all GitHub-specific implementation is isolated in `github/client.py`, enabling easy replacement with other task management systems.

## Tech Stack
- **Language**: Python 3.10+
- **MCP Framework**: FastMCP (mcp[cli] >=1.0.0)
- **HTTP Client**: httpx (async)
- **Data Validation**: Pydantic 2.0+
- **Config**: python-dotenv
- **Testing**: pytest, pytest-asyncio, pytest-mock
- **Code Quality**: ruff (linting/formatting), pyright (type checking)
- **Package Manager**: uv (recommended) or pip

## Architecture (3 Layers)

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

## Project Structure
```
github-projects-mcp/
├── src/github_projects_mcp/
│   ├── server.py              # MCP tools (15 functions)
│   ├── config.py              # Environment variables
│   ├── interfaces/
│   │   └── task_manager.py    # Abstract interface
│   ├── models/                # Pydantic models (platform-agnostic)
│   │   ├── ticket.py
│   │   ├── comment.py
│   │   ├── label.py
│   │   └── milestone.py
│   └── github/                # GitHub implementation
│       └── client.py          # GraphQL + REST API calls
├── tests/
│   ├── conftest.py
│   └── test_github_client.py
├── .env                       # Local config (gitignored)
├── pyproject.toml             # Dependencies & tooling config
└── README.md
```

## 15 MCP Tools Provided
1. `get_tickets` - List tickets with filters
2. `get_ticket` - Get single ticket by ID/number
3. `get_comments` - Get ticket comments
4. `add_comment` - Add comment to ticket
5. `get_labels` - List all available labels
6. `get_ticket_labels` - Get labels for ticket
7. `add_label` - Add label to ticket
8. `update_status` - Change ticket status
9. `add_branch` - Link branch to ticket
10. `add_pull_request` - Link PR to ticket
11. `add_subtask` - Add subtask relationship
12. `assign_ticket` - Assign to user
13. `assign_to_self` - Assign to authenticated user
14. `get_milestones` - List milestones
15. `add_milestone` - Add ticket to milestone

## Test Repository
Tests use https://github.com/artemfomin/TestRepo

## Environment Variables (Required)
- `GITHUB_TOKEN` - Personal Access Token (repo + project permissions)
- `GITHUB_OWNER` - Repository owner (e.g., "artemfomin")
- `GITHUB_REPO` - Repository name (e.g., "TestRepo")
- `GITHUB_PROJECT_NUMBER` - Project number (optional)

## System Information
- **Platform**: Windows
- **Working Directory**: C:\Projects\MCP\GithubProjects\github-projects-mcp
