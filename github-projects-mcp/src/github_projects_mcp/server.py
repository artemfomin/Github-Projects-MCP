"""MCP Server for GitHub Projects."""

from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import AsyncIterator

from mcp.server.fastmcp import Context, FastMCP

from .config import get_settings
from .github import GitHubProjectsClient
from .interfaces import TaskManagerInterface


@dataclass
class ServerContext:
    """Server lifecycle context with task manager client."""

    task_manager: TaskManagerInterface


@asynccontextmanager
async def server_lifespan(server: FastMCP) -> AsyncIterator[ServerContext]:
    """Manage server lifecycle and initialize clients.

    Args:
        server: FastMCP server instance

    Yields:
        ServerContext with initialized task manager client
    """
    # Load settings and initialize GitHub client
    settings = get_settings()
    task_manager = GitHubProjectsClient(
        token=settings.github_token,
        owner=settings.github_owner,
        repo=settings.github_repo,
        project_number=settings.github_project_number,
    )

    try:
        yield ServerContext(task_manager=task_manager)
    finally:
        # Cleanup if needed
        pass


# Create MCP server with lifespan
mcp = FastMCP("GitHub Projects", lifespan=server_lifespan)


@mcp.tool()
async def create_ticket(
    ctx: Context,
    title: str,
    body: str | None = None,
    labels: list[str] | None = None,
    assignee: str | None = None,
) -> str:
    """Create a new ticket.

    Args:
        ctx: MCP context
        title: Ticket title (required)
        body: Ticket description/body
        labels: List of label names to add to the ticket
        assignee: Username to assign the ticket to

    Returns:
        JSON string with created ticket details
    """
    task_manager: TaskManagerInterface = ctx.request_context.lifespan_context.task_manager
    ticket = await task_manager.create_ticket(
        title=title,
        body=body,
        labels=labels,
        assignee=assignee,
    )

    # Format output
    result = f"Ticket #{ticket.number} created successfully!\n"
    result += f"Title: {ticket.title}\n"
    result += f"Status: {ticket.status}\n"
    result += f"Labels: {', '.join(ticket.labels) if ticket.labels else 'None'}\n"
    result += f"Assignees: {', '.join(ticket.assignees) if ticket.assignees else 'Unassigned'}\n"
    result += f"URL: {ticket.url}\n"

    return result


@mcp.tool()
async def get_tickets(
    ctx: Context,
    status: str | None = None,
    assignee: str | None = None,
    label: str | None = None,
    milestone: str | None = None,
    limit: int = 50,
) -> str:
    """Get list of tickets with optional filtering.

    Args:
        ctx: MCP context
        status: Filter by ticket status (e.g., 'open', 'closed', 'Todo', 'In Progress', 'Done')
        assignee: Filter by assignee username
        label: Filter by label name
        milestone: Filter by milestone title
        limit: Maximum number of tickets to return (default: 50)

    Returns:
        JSON string with list of tickets
    """
    task_manager: TaskManagerInterface = ctx.request_context.lifespan_context.task_manager
    tickets = await task_manager.get_tickets(
        status=status, assignee=assignee, label=label, milestone=milestone, limit=limit
    )

    # Format output
    result = f"Found {len(tickets)} ticket(s):\n\n"
    for ticket in tickets:
        result += f"#{ticket.number} - {ticket.title}\n"
        result += f"  Status: {ticket.status}\n"
        result += f"  Labels: {', '.join(ticket.labels) if ticket.labels else 'None'}\n"
        result += f"  Assignees: {', '.join(ticket.assignees) if ticket.assignees else 'Unassigned'}\n"
        result += f"  Milestone: {ticket.milestone if ticket.milestone else 'None'}\n"
        result += f"  URL: {ticket.url}\n\n"

    return result


@mcp.tool()
async def get_ticket(ctx: Context, ticket_id: str) -> str:
    """Get a single ticket by ID or number.

    Args:
        ctx: MCP context
        ticket_id: Ticket ID (node ID) or issue number

    Returns:
        JSON string with ticket details
    """
    task_manager: TaskManagerInterface = ctx.request_context.lifespan_context.task_manager
    ticket = await task_manager.get_ticket(ticket_id)

    result = f"Ticket #{ticket.number}: {ticket.title}\n"
    result += f"{'=' * 50}\n\n"
    result += f"Status: {ticket.status}\n"
    result += f"Labels: {', '.join(ticket.labels) if ticket.labels else 'None'}\n"
    result += f"Assignees: {', '.join(ticket.assignees) if ticket.assignees else 'Unassigned'}\n"
    result += f"Milestone: {ticket.milestone or 'None'}\n"
    result += f"Created: {ticket.created_at}\n"
    result += f"Updated: {ticket.updated_at}\n"
    result += f"URL: {ticket.url}\n\n"
    result += f"Description:\n{ticket.body or 'No description'}\n"

    return result


@mcp.tool()
async def get_comments(ctx: Context, ticket_id: str) -> str:
    """Get all comments for a ticket.

    Args:
        ctx: MCP context
        ticket_id: Ticket ID or issue number

    Returns:
        JSON string with list of comments
    """
    task_manager: TaskManagerInterface = ctx.request_context.lifespan_context.task_manager
    comments = await task_manager.get_comments(ticket_id)

    result = f"Found {len(comments)} comment(s):\n\n"
    for i, comment in enumerate(comments, 1):
        result += f"Comment #{i} by @{comment.author}\n"
        result += f"Posted: {comment.created_at}\n"
        result += f"{'-' * 50}\n"
        result += f"{comment.body}\n"
        result += f"{'-' * 50}\n\n"

    return result


@mcp.tool()
async def add_comment(ctx: Context, ticket_id: str, body: str) -> str:
    """Add a comment to a ticket.

    Args:
        ctx: MCP context
        ticket_id: Ticket ID or issue number
        body: Comment text content

    Returns:
        Success message with comment details
    """
    task_manager: TaskManagerInterface = ctx.request_context.lifespan_context.task_manager
    comment = await task_manager.add_comment(ticket_id, body)

    return f"Comment added successfully!\nAuthor: @{comment.author}\nPosted: {comment.created_at}\nURL: {comment.url}"


@mcp.tool()
async def get_labels(ctx: Context) -> str:
    """Get all available labels in the project.

    Args:
        ctx: MCP context

    Returns:
        JSON string with list of labels
    """
    task_manager: TaskManagerInterface = ctx.request_context.lifespan_context.task_manager
    labels = await task_manager.get_labels()

    result = f"Found {len(labels)} label(s):\n\n"
    for label in labels:
        result += f"• {label.name}"
        if label.color:
            result += f" (#{label.color})"
        if label.description:
            result += f"\n  {label.description}"
        result += "\n"

    return result


@mcp.tool()
async def get_ticket_labels(ctx: Context, ticket_id: str) -> str:
    """Get labels for a specific ticket.

    Args:
        ctx: MCP context
        ticket_id: Ticket ID or issue number

    Returns:
        JSON string with list of labels on the ticket
    """
    task_manager: TaskManagerInterface = ctx.request_context.lifespan_context.task_manager
    labels = await task_manager.get_ticket_labels(ticket_id)

    result = f"Found {len(labels)} label(s) on this ticket:\n\n"
    for label in labels:
        result += f"• {label.name}\n"

    return result


@mcp.tool()
async def add_label(ctx: Context, ticket_id: str, label_name: str) -> str:
    """Add a label to a ticket.

    Args:
        ctx: MCP context
        ticket_id: Ticket ID or issue number
        label_name: Name of the label to add

    Returns:
        Success message with updated ticket info
    """
    task_manager: TaskManagerInterface = ctx.request_context.lifespan_context.task_manager
    ticket = await task_manager.add_label(ticket_id, label_name)

    return f"Label '{label_name}' added to ticket #{ticket.number}\nCurrent labels: {', '.join(ticket.labels)}"


@mcp.tool()
async def update_status(
    ctx: Context, ticket_id: str, status: str, project_number: int | None = None
) -> str:
    """Update the status of a ticket.

    Args:
        ctx: MCP context
        ticket_id: Ticket ID or issue number
        status: New status (e.g., 'open', 'closed', 'Todo', 'In Progress', 'Done')
        project_number: Project number (optional, uses default from config)

    Returns:
        Success message with updated ticket info
    """
    task_manager: TaskManagerInterface = ctx.request_context.lifespan_context.task_manager
    ticket = await task_manager.update_status(ticket_id, status, project_number)

    return f"Status updated for ticket #{ticket.number}\nNew status: {ticket.status}"


@mcp.tool()
async def add_branch(ctx: Context, ticket_id: str, branch_name: str) -> str:
    """Link a branch to a ticket.

    Args:
        ctx: MCP context
        ticket_id: Ticket ID or issue number
        branch_name: Name of the git branch

    Returns:
        Success message
    """
    task_manager: TaskManagerInterface = ctx.request_context.lifespan_context.task_manager
    ticket = await task_manager.add_branch(ticket_id, branch_name)

    return f"Branch '{branch_name}' linked to ticket #{ticket.number}"


@mcp.tool()
async def add_pull_request(ctx: Context, ticket_id: str, pr_url: str) -> str:
    """Link a pull request to a ticket.

    Args:
        ctx: MCP context
        ticket_id: Ticket ID or issue number
        pr_url: URL of the pull request

    Returns:
        Success message
    """
    task_manager: TaskManagerInterface = ctx.request_context.lifespan_context.task_manager
    ticket = await task_manager.add_pull_request(ticket_id, pr_url)

    return f"Pull request linked to ticket #{ticket.number}\nPR: {pr_url}"


@mcp.tool()
async def add_subtask(ctx: Context, parent_id: str, subtask_id: str) -> str:
    """Add a subtask relationship to a ticket.

    Args:
        ctx: MCP context
        parent_id: Parent ticket ID or issue number
        subtask_id: Subtask ticket ID or issue number

    Returns:
        Success message
    """
    task_manager: TaskManagerInterface = ctx.request_context.lifespan_context.task_manager
    parent = await task_manager.add_subtask(parent_id, subtask_id)

    return f"Subtask relationship created\nParent: #{parent.number}\nSubtask count: {len(parent.subtasks)}"


@mcp.tool()
async def create_subtask(
    ctx: Context,
    parent_id: str,
    title: str,
    body: str | None = None,
    labels: list[str] | None = None,
) -> str:
    """Create a new ticket as a subtask of a parent ticket.

    Args:
        ctx: MCP context
        parent_id: Parent ticket ID or issue number
        title: Subtask title (required)
        body: Subtask description/body
        labels: List of label names to add to the subtask

    Returns:
        JSON string with created subtask details
    """
    task_manager: TaskManagerInterface = ctx.request_context.lifespan_context.task_manager
    subtask = await task_manager.create_subtask(
        parent_id=parent_id,
        title=title,
        body=body,
        labels=labels,
    )

    # Format output
    result = f"Subtask #{subtask.number} created successfully!\n"
    result += f"Title: {subtask.title}\n"
    result += f"Parent: #{parent_id}\n"
    result += f"Status: {subtask.status}\n"
    result += f"Labels: {', '.join(subtask.labels) if subtask.labels else 'None'}\n"
    result += f"URL: {subtask.url}\n"

    return result


@mcp.tool()
async def assign_ticket(ctx: Context, ticket_id: str, assignee: str) -> str:
    """Assign a ticket to a user.

    Args:
        ctx: MCP context
        ticket_id: Ticket ID or issue number
        assignee: Username to assign to

    Returns:
        Success message with updated ticket info
    """
    task_manager: TaskManagerInterface = ctx.request_context.lifespan_context.task_manager
    ticket = await task_manager.assign_ticket(ticket_id, assignee)

    return f"Ticket #{ticket.number} assigned to @{assignee}\nCurrent assignees: {', '.join(ticket.assignees)}"


@mcp.tool()
async def assign_to_self(ctx: Context, ticket_id: str) -> str:
    """Assign a ticket to yourself (the authenticated user).

    Args:
        ctx: MCP context
        ticket_id: Ticket ID or issue number

    Returns:
        Success message with updated ticket info
    """
    task_manager: TaskManagerInterface = ctx.request_context.lifespan_context.task_manager
    ticket = await task_manager.assign_to_self(ticket_id)

    return f"Ticket #{ticket.number} assigned to you\nCurrent assignees: {', '.join(ticket.assignees)}"


@mcp.tool()
async def get_milestones(ctx: Context) -> str:
    """Get all available milestones in the project.

    Args:
        ctx: MCP context

    Returns:
        JSON string with list of milestones
    """
    task_manager: TaskManagerInterface = ctx.request_context.lifespan_context.task_manager
    milestones = await task_manager.get_milestones()

    result = f"Found {len(milestones)} milestone(s):\n\n"
    for milestone in milestones:
        result += f"• {milestone.title} ({milestone.state})\n"
        if milestone.description:
            result += f"  {milestone.description}\n"
        if milestone.due_date:
            result += f"  Due: {milestone.due_date}\n"
        result += f"  URL: {milestone.url}\n\n"

    return result


@mcp.tool()
async def add_milestone(ctx: Context, ticket_id: str, milestone_title: str) -> str:
    """Add a ticket to a milestone.

    Args:
        ctx: MCP context
        ticket_id: Ticket ID or issue number
        milestone_title: Title of the milestone

    Returns:
        Success message with updated ticket info
    """
    task_manager: TaskManagerInterface = ctx.request_context.lifespan_context.task_manager
    ticket = await task_manager.add_milestone(ticket_id, milestone_title)

    return f"Ticket #{ticket.number} added to milestone '{milestone_title}'"


@mcp.tool()
async def add_ticket_to_project(
    ctx: Context, ticket_id: str, project_number: int | None = None
) -> str:
    """Add an existing ticket to a GitHub Project V2 board.

    Args:
        ctx: MCP context
        ticket_id: Ticket ID or issue number
        project_number: Project number (optional, uses default from config)

    Returns:
        Success message with ticket info
    """
    task_manager: TaskManagerInterface = ctx.request_context.lifespan_context.task_manager
    ticket = await task_manager.add_ticket_to_project(ticket_id, project_number)

    project_msg = f" (Project #{project_number})" if project_number else ""
    return (
        f"Ticket #{ticket.number} successfully added to project board{project_msg}\n"
        f"Title: {ticket.title}\n"
        f"URL: {ticket.url}"
    )


@mcp.tool()
async def get_available_statuses(ctx: Context, project_number: int | None = None) -> str:
    """Get all available status options in the project.

    Args:
        ctx: MCP context
        project_number: Project number (optional, uses default from config)

    Returns:
        List of available status options
    """
    task_manager: TaskManagerInterface = ctx.request_context.lifespan_context.task_manager

    # Access the private method to get status field info
    if hasattr(task_manager, '_get_status_field_id'):
        try:
            field_id, options = await task_manager._get_status_field_id(project_number)

            result = f"Available status options in project:\n\n"
            for opt_name in options.keys():
                result += f"• {opt_name}\n"

            return result
        except Exception as e:
            return f"Error getting status options: {e}"
    else:
        return "Status field information not available for this task manager"


@mcp.tool()
async def add_parent(ctx: Context, ticket_id: str, parent_id: str) -> str:
    """Set a parent ticket relationship.

    Args:
        ctx: MCP context
        ticket_id: Child ticket ID or issue number
        parent_id: Parent ticket ID or issue number

    Returns:
        Success message with relationship info
    """
    task_manager: TaskManagerInterface = ctx.request_context.lifespan_context.task_manager
    child = await task_manager.add_parent(ticket_id, parent_id)

    return (
        f"Parent relationship created successfully\n"
        f"Child: #{child.number} - {child.title}\n"
        f"Parent: #{parent_id}\n"
        f"URL: {child.url}"
    )


@mcp.tool()
async def add_blocked_by(ctx: Context, ticket_id: str, blocking_ticket_id: str) -> str:
    """Mark a ticket as blocked by another ticket.

    Args:
        ctx: MCP context
        ticket_id: Ticket ID or issue number that is blocked
        blocking_ticket_id: Ticket ID or issue number that is blocking

    Returns:
        Success message with blocking info
    """
    task_manager: TaskManagerInterface = ctx.request_context.lifespan_context.task_manager
    blocked = await task_manager.add_blocked_by(ticket_id, blocking_ticket_id)

    return (
        f"Blocking relationship created successfully\n"
        f"Ticket #{blocked.number} is now blocked by #{blocking_ticket_id}\n"
        f"URL: {blocked.url}"
    )


@mcp.tool()
async def add_blocking(ctx: Context, ticket_id: str, blocked_ticket_id: str) -> str:
    """Mark a ticket as blocking another ticket.

    Args:
        ctx: MCP context
        ticket_id: Ticket ID or issue number that is blocking
        blocked_ticket_id: Ticket ID or issue number that is blocked

    Returns:
        Success message with blocking info
    """
    task_manager: TaskManagerInterface = ctx.request_context.lifespan_context.task_manager
    blocker = await task_manager.add_blocking(ticket_id, blocked_ticket_id)

    return (
        f"Blocking relationship created successfully\n"
        f"Ticket #{blocker.number} is now blocking #{blocked_ticket_id}\n"
        f"URL: {blocker.url}"
    )


def main():
    """Run the MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()
