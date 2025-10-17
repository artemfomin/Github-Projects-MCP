"""Abstract interface for task management systems."""

from abc import ABC, abstractmethod

from ..models import Comment, Label, Milestone, Ticket


class TaskManagerInterface(ABC):
    """Abstract base class for task management system clients.

    This interface defines the contract for interacting with any task management
    system (GitHub Projects, Jira, etc.). All implementations must provide these methods.
    """

    @abstractmethod
    async def create_ticket(
        self,
        title: str,
        body: str | None = None,
        labels: list[str] | None = None,
        assignee: str | None = None,
    ) -> Ticket:
        """Create a new ticket.

        Args:
            title: Ticket title (required)
            body: Ticket description/body
            labels: List of label names to add
            assignee: Username to assign the ticket to

        Returns:
            Created ticket object

        Raises:
            ValueError: If creation fails or invalid parameters
        """
        pass

    @abstractmethod
    async def get_tickets(
        self,
        status: str | None = None,
        assignee: str | None = None,
        label: str | None = None,
        milestone: str | None = None,
        limit: int = 50,
    ) -> list[Ticket]:
        """Get list of tickets with optional filtering.

        Args:
            status: Filter by ticket status
            assignee: Filter by assignee username
            label: Filter by label name
            milestone: Filter by milestone title
            limit: Maximum number of tickets to return

        Returns:
            List of tickets matching the filters
        """
        pass

    @abstractmethod
    async def get_ticket(self, ticket_id: str) -> Ticket:
        """Get a single ticket by ID.

        Args:
            ticket_id: Unique ticket identifier

        Returns:
            Ticket object with full details

        Raises:
            ValueError: If ticket not found
        """
        pass

    @abstractmethod
    async def get_comments(self, ticket_id: str) -> list[Comment]:
        """Get all comments for a ticket.

        Args:
            ticket_id: Unique ticket identifier

        Returns:
            List of comments on the ticket

        Raises:
            ValueError: If ticket not found
        """
        pass

    @abstractmethod
    async def add_comment(self, ticket_id: str, body: str) -> Comment:
        """Add a comment to a ticket.

        Args:
            ticket_id: Unique ticket identifier
            body: Comment text content

        Returns:
            Created comment object

        Raises:
            ValueError: If ticket not found
        """
        pass

    @abstractmethod
    async def get_labels(self) -> list[Label]:
        """Get all available labels.

        Returns:
            List of all labels in the project
        """
        pass

    @abstractmethod
    async def get_ticket_labels(self, ticket_id: str) -> list[Label]:
        """Get labels for a specific ticket.

        Args:
            ticket_id: Unique ticket identifier

        Returns:
            List of labels on the ticket

        Raises:
            ValueError: If ticket not found
        """
        pass

    @abstractmethod
    async def add_label(self, ticket_id: str, label_name: str) -> Ticket:
        """Add a label to a ticket.

        Args:
            ticket_id: Unique ticket identifier
            label_name: Name of the label to add

        Returns:
            Updated ticket object

        Raises:
            ValueError: If ticket or label not found
        """
        pass

    @abstractmethod
    async def update_status(
        self, ticket_id: str, status: str, project_number: int | None = None
    ) -> Ticket:
        """Update the status of a ticket.

        Args:
            ticket_id: Unique ticket identifier
            status: New status value
            project_number: Project number (optional, uses default from config)

        Returns:
            Updated ticket object

        Raises:
            ValueError: If ticket not found or invalid status
        """
        pass

    @abstractmethod
    async def add_branch(self, ticket_id: str, branch_name: str) -> Ticket:
        """Link a branch to a ticket.

        Args:
            ticket_id: Unique ticket identifier
            branch_name: Name of the git branch

        Returns:
            Updated ticket object

        Raises:
            ValueError: If ticket not found
        """
        pass

    @abstractmethod
    async def add_pull_request(self, ticket_id: str, pr_url: str) -> Ticket:
        """Link a pull request to a ticket.

        Args:
            ticket_id: Unique ticket identifier
            pr_url: URL of the pull request

        Returns:
            Updated ticket object

        Raises:
            ValueError: If ticket not found
        """
        pass

    @abstractmethod
    async def add_subtask(self, parent_id: str, subtask_id: str) -> Ticket:
        """Add a subtask relationship to a ticket.

        Args:
            parent_id: Parent ticket identifier
            subtask_id: Subtask ticket identifier

        Returns:
            Updated parent ticket object

        Raises:
            ValueError: If parent or subtask not found
        """
        pass

    @abstractmethod
    async def create_subtask(
        self,
        parent_id: str,
        title: str,
        body: str | None = None,
        labels: list[str] | None = None,
    ) -> Ticket:
        """Create a new ticket as a subtask of a parent ticket.

        Args:
            parent_id: Parent ticket identifier
            title: Subtask title (required)
            body: Subtask description/body
            labels: List of label names to add to subtask

        Returns:
            Created subtask ticket object

        Raises:
            ValueError: If parent not found or creation fails
        """
        pass

    @abstractmethod
    async def assign_ticket(self, ticket_id: str, assignee: str) -> Ticket:
        """Assign a ticket to a user.

        Args:
            ticket_id: Unique ticket identifier
            assignee: Username to assign to

        Returns:
            Updated ticket object

        Raises:
            ValueError: If ticket or user not found
        """
        pass

    @abstractmethod
    async def assign_to_self(self, ticket_id: str) -> Ticket:
        """Assign a ticket to the authenticated user.

        Args:
            ticket_id: Unique ticket identifier

        Returns:
            Updated ticket object

        Raises:
            ValueError: If ticket not found
        """
        pass

    @abstractmethod
    async def get_milestones(self) -> list[Milestone]:
        """Get all available milestones.

        Returns:
            List of all milestones in the project
        """
        pass

    @abstractmethod
    async def add_milestone(self, ticket_id: str, milestone_title: str) -> Ticket:
        """Add a ticket to a milestone.

        Args:
            ticket_id: Unique ticket identifier
            milestone_title: Title of the milestone

        Returns:
            Updated ticket object

        Raises:
            ValueError: If ticket or milestone not found
        """
        pass

    @abstractmethod
    async def add_ticket_to_project(
        self, ticket_id: str, project_number: int | None = None
    ) -> Ticket:
        """Add an existing ticket to a project board.

        Args:
            ticket_id: Unique ticket identifier
            project_number: Project number (uses default if None)

        Returns:
            Updated ticket object

        Raises:
            ValueError: If ticket or project not found
        """
        pass

    @abstractmethod
    async def add_parent(self, ticket_id: str, parent_id: str) -> Ticket:
        """Set a parent ticket relationship.

        Args:
            ticket_id: Child ticket identifier
            parent_id: Parent ticket identifier

        Returns:
            Updated child ticket object

        Raises:
            ValueError: If ticket or parent not found
        """
        pass

    @abstractmethod
    async def add_blocked_by(self, ticket_id: str, blocking_ticket_id: str) -> Ticket:
        """Mark a ticket as blocked by another ticket.

        Args:
            ticket_id: Ticket that is blocked
            blocking_ticket_id: Ticket that is blocking

        Returns:
            Updated blocked ticket object

        Raises:
            ValueError: If either ticket not found
        """
        pass

    @abstractmethod
    async def add_blocking(self, ticket_id: str, blocked_ticket_id: str) -> Ticket:
        """Mark a ticket as blocking another ticket.

        Args:
            ticket_id: Ticket that is blocking
            blocked_ticket_id: Ticket that is blocked

        Returns:
            Updated blocking ticket object

        Raises:
            ValueError: If either ticket not found
        """
        pass
