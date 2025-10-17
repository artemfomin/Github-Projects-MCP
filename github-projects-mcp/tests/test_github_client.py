"""Tests for GitHubProjectsClient."""

import pytest

from github_projects_mcp.github import GitHubProjectsClient
from github_projects_mcp.models import Comment, Label, Milestone, Ticket


@pytest.mark.asyncio
async def test_get_tickets(github_client: GitHubProjectsClient):
    """Test getting list of tickets."""
    tickets = await github_client.get_tickets(limit=10)

    assert isinstance(tickets, list)
    if tickets:
        ticket = tickets[0]
        assert isinstance(ticket, Ticket)
        assert ticket.id
        assert ticket.title


@pytest.mark.asyncio
async def test_get_tickets_with_filters(github_client: GitHubProjectsClient):
    """Test getting tickets with status filter."""
    open_tickets = await github_client.get_tickets(status="open", limit=5)

    assert isinstance(open_tickets, list)
    for ticket in open_tickets:
        assert isinstance(ticket, Ticket)


@pytest.mark.asyncio
async def test_get_ticket_by_number(github_client: GitHubProjectsClient):
    """Test getting a ticket by issue number."""
    # First get a ticket to have a valid number
    tickets = await github_client.get_tickets(limit=1)
    if not tickets:
        pytest.skip("No tickets available in repository")

    ticket_number = str(tickets[0].number)
    ticket = await github_client.get_ticket(ticket_number)

    assert isinstance(ticket, Ticket)
    assert ticket.number == tickets[0].number
    assert ticket.title
    assert ticket.id


@pytest.mark.asyncio
async def test_get_ticket_by_id(github_client: GitHubProjectsClient):
    """Test getting a ticket by node ID."""
    tickets = await github_client.get_tickets(limit=1)
    if not tickets:
        pytest.skip("No tickets available in repository")

    ticket_id = tickets[0].id
    ticket = await github_client.get_ticket(ticket_id)

    assert isinstance(ticket, Ticket)
    assert ticket.id == ticket_id
    assert ticket.title


@pytest.mark.asyncio
async def test_get_ticket_not_found(github_client: GitHubProjectsClient):
    """Test getting a non-existent ticket."""
    with pytest.raises(Exception):  # Should raise ValueError or similar
        await github_client.get_ticket("99999")


@pytest.mark.asyncio
async def test_get_comments(github_client: GitHubProjectsClient):
    """Test getting comments for a ticket."""
    tickets = await github_client.get_tickets(limit=5)
    if not tickets:
        pytest.skip("No tickets available in repository")

    # Try to find a ticket with comments
    for ticket in tickets:
        comments = await github_client.get_comments(str(ticket.number))
        assert isinstance(comments, list)

        if comments:
            comment = comments[0]
            assert isinstance(comment, Comment)
            assert comment.id
            assert comment.body
            assert comment.author
            break


@pytest.mark.asyncio
async def test_add_comment(github_client: GitHubProjectsClient):
    """Test adding a comment to a ticket."""
    tickets = await github_client.get_tickets(limit=1)
    if not tickets:
        pytest.skip("No tickets available in repository")

    ticket_id = str(tickets[0].number)
    comment_body = "Test comment from automated test"

    comment = await github_client.add_comment(ticket_id, comment_body)

    assert isinstance(comment, Comment)
    assert comment.body == comment_body
    assert comment.id
    assert comment.author


@pytest.mark.asyncio
async def test_get_labels(github_client: GitHubProjectsClient):
    """Test getting all labels."""
    labels = await github_client.get_labels()

    assert isinstance(labels, list)
    if labels:
        label = labels[0]
        assert isinstance(label, Label)
        assert label.id
        assert label.name


@pytest.mark.asyncio
async def test_get_ticket_labels(github_client: GitHubProjectsClient):
    """Test getting labels for a specific ticket."""
    tickets = await github_client.get_tickets(limit=10)
    if not tickets:
        pytest.skip("No tickets available in repository")

    # Find a ticket with labels
    for ticket in tickets:
        if ticket.labels:
            labels = await github_client.get_ticket_labels(str(ticket.number))
            assert isinstance(labels, list)
            assert len(labels) > 0
            assert all(isinstance(l, Label) for l in labels)
            break


@pytest.mark.asyncio
async def test_add_label(github_client: GitHubProjectsClient):
    """Test adding a label to a ticket."""
    # Get available labels
    labels = await github_client.get_labels()
    if not labels:
        pytest.skip("No labels available in repository")

    # Get a ticket
    tickets = await github_client.get_tickets(limit=1)
    if not tickets:
        pytest.skip("No tickets available in repository")

    ticket_id = str(tickets[0].number)
    label_name = labels[0].name

    # Add label
    updated_ticket = await github_client.add_label(ticket_id, label_name)

    assert isinstance(updated_ticket, Ticket)
    assert label_name in updated_ticket.labels


@pytest.mark.asyncio
async def test_update_status_open(github_client: GitHubProjectsClient):
    """Test updating ticket status to open."""
    tickets = await github_client.get_tickets(limit=1)
    if not tickets:
        pytest.skip("No tickets available in repository")

    ticket_id = str(tickets[0].number)

    updated_ticket = await github_client.update_status(ticket_id, "open")

    assert isinstance(updated_ticket, Ticket)
    # Status should reflect open state


@pytest.mark.asyncio
async def test_assign_to_self(github_client: GitHubProjectsClient):
    """Test assigning a ticket to the authenticated user."""
    tickets = await github_client.get_tickets(limit=1)
    if not tickets:
        pytest.skip("No tickets available in repository")

    ticket_id = str(tickets[0].number)

    updated_ticket = await github_client.assign_to_self(ticket_id)

    assert isinstance(updated_ticket, Ticket)
    assert len(updated_ticket.assignees) > 0


@pytest.mark.asyncio
async def test_get_milestones(github_client: GitHubProjectsClient):
    """Test getting all milestones."""
    milestones = await github_client.get_milestones()

    assert isinstance(milestones, list)
    if milestones:
        milestone = milestones[0]
        assert isinstance(milestone, Milestone)
        assert milestone.id
        assert milestone.title


@pytest.mark.asyncio
async def test_add_milestone(github_client: GitHubProjectsClient):
    """Test adding a ticket to a milestone."""
    # Get milestones
    milestones = await github_client.get_milestones()
    if not milestones:
        pytest.skip("No milestones available in repository")

    # Get a ticket
    tickets = await github_client.get_tickets(limit=1)
    if not tickets:
        pytest.skip("No tickets available in repository")

    ticket_id = str(tickets[0].number)
    milestone_title = milestones[0].title

    updated_ticket = await github_client.add_milestone(ticket_id, milestone_title)

    assert isinstance(updated_ticket, Ticket)
    assert updated_ticket.milestone == milestone_title


@pytest.mark.asyncio
async def test_add_subtask(github_client: GitHubProjectsClient):
    """Test adding a subtask relationship."""
    tickets = await github_client.get_tickets(limit=2)
    if len(tickets) < 2:
        pytest.skip("Need at least 2 tickets for subtask test")

    parent_id = str(tickets[0].number)
    subtask_id = str(tickets[1].number)

    updated_parent = await github_client.add_subtask(parent_id, subtask_id)

    assert isinstance(updated_parent, Ticket)
    assert len(updated_parent.subtasks) > 0


@pytest.mark.asyncio
async def test_client_initialization():
    """Test client initialization."""
    client = GitHubProjectsClient(
        token="test_token",
        owner="test_owner",
        repo="test_repo",
        project_number=1,
    )

    assert client.token == "test_token"
    assert client.owner == "test_owner"
    assert client.repo == "test_repo"
    assert client.project_number == 1
