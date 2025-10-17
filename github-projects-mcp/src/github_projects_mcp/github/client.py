"""GitHub Projects V2 client implementation."""

from datetime import datetime
from typing import Any

import httpx

from ..interfaces import TaskManagerInterface
from ..models import Comment, Label, Milestone, Ticket, TicketStatus


class GitHubProjectsClient(TaskManagerInterface):
    """GitHub Projects V2 implementation of TaskManagerInterface.

    Uses GitHub GraphQL API to interact with Projects V2 and Issues.
    """

    def __init__(
        self,
        token: str,
        owner: str,
        repo: str,
        project_number: int | None = None,
    ):
        """Initialize GitHub Projects client.

        Args:
            token: GitHub Personal Access Token
            owner: Repository owner (user or organization)
            repo: Repository name
            project_number: Optional default project number
        """
        self.token = token
        self.owner = owner
        self.repo = repo
        self.project_number = project_number
        self.api_url = "https://api.github.com/graphql"
        self.rest_api_url = "https://api.github.com"
        self._project_id: str | None = None
        self._repo_id: str | None = None
        self._status_field_id: str | None = None

    async def _graphql_request(self, query: str, variables: dict[str, Any] | None = None) -> dict:
        """Make a GraphQL API request.

        Args:
            query: GraphQL query string
            variables: Query variables

        Returns:
            Response data dictionary

        Raises:
            httpx.HTTPError: If request fails
        """
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.api_url,
                json={"query": query, "variables": variables or {}},
                headers={
                    "Authorization": f"Bearer {self.token}",
                    "Content-Type": "application/json",
                },
                timeout=30.0,
            )
            response.raise_for_status()
            data = response.json()
            if "errors" in data:
                raise ValueError(f"GraphQL errors: {data['errors']}")
            return data["data"]

    async def _rest_request(
        self, method: str, endpoint: str, json_data: dict | None = None
    ) -> dict:
        """Make a REST API request.

        Args:
            method: HTTP method
            endpoint: API endpoint path
            json_data: Request body data

        Returns:
            Response data dictionary
        """
        async with httpx.AsyncClient() as client:
            response = await client.request(
                method,
                f"{self.rest_api_url}{endpoint}",
                json=json_data,
                headers={
                    "Authorization": f"Bearer {self.token}",
                    "Accept": "application/vnd.github+json",
                    "X-GitHub-Api-Version": "2022-11-28",
                },
                timeout=30.0,
            )
            response.raise_for_status()
            return response.json() if response.text else {}

    async def _get_repo_id(self) -> str:
        """Get repository node ID.

        Returns:
            Repository GraphQL node ID
        """
        if self._repo_id:
            return self._repo_id

        query = """
        query($owner: String!, $repo: String!) {
            repository(owner: $owner, name: $repo) {
                id
            }
        }
        """
        data = await self._graphql_request(
            query, {"owner": self.owner, "repo": self.repo}
        )
        self._repo_id = data["repository"]["id"]
        return self._repo_id

    async def _get_project_id(self, project_number: int | None = None) -> str:
        """Get project node ID.

        Args:
            project_number: Project number to fetch (uses default if None)

        Returns:
            Project GraphQL node ID
        """
        if self._project_id:
            return self._project_id

        pn = project_number or self.project_number
        if not pn:
            raise ValueError("Project number not specified")

        # Try repository first (most common case)
        try:
            query = """
            query($owner: String!, $repo: String!, $number: Int!) {
                repository(owner: $owner, name: $repo) {
                    projectV2(number: $number) {
                        id
                    }
                }
            }
            """
            data = await self._graphql_request(
                query, {"owner": self.owner, "repo": self.repo, "number": pn}
            )
            if data.get("repository") and data["repository"].get("projectV2"):
                self._project_id = data["repository"]["projectV2"]["id"]
                return self._project_id
        except ValueError:
            pass  # Project not in repository, try user/org

        # Try user project
        try:
            query = """
            query($owner: String!, $number: Int!) {
                user(login: $owner) {
                    projectV2(number: $number) {
                        id
                    }
                }
            }
            """
            data = await self._graphql_request(
                query, {"owner": self.owner, "number": pn}
            )
            if data.get("user") and data["user"].get("projectV2"):
                self._project_id = data["user"]["projectV2"]["id"]
                return self._project_id
        except ValueError:
            pass  # Project not in user, try organization

        # Try organization project
        try:
            query = """
            query($owner: String!, $number: Int!) {
                organization(login: $owner) {
                    projectV2(number: $number) {
                        id
                    }
                }
            }
            """
            data = await self._graphql_request(
                query, {"owner": self.owner, "number": pn}
            )
            if data.get("organization") and data["organization"].get("projectV2"):
                self._project_id = data["organization"]["projectV2"]["id"]
                return self._project_id
        except ValueError:
            pass  # Project not found anywhere

        raise ValueError(
            f"Project {pn} not found in repository {self.owner}/{self.repo}, "
            f"user {self.owner}, or organization {self.owner}"
        )

    def _parse_issue_to_ticket(self, issue: dict, project_item: dict | None = None) -> Ticket:
        """Parse GitHub issue data to Ticket model.

        Supports both GraphQL and REST API response formats.

        Args:
            issue: Issue data from API
            project_item: Optional project item data

        Returns:
            Ticket object
        """
        # Parse labels - handle both GraphQL (nodes) and REST (list) formats
        labels_data = issue.get("labels", [])
        if isinstance(labels_data, dict):  # GraphQL format
            labels = [label["name"] for label in labels_data.get("nodes", [])]
        else:  # REST API format
            labels = [label["name"] for label in labels_data]

        # Parse assignees - handle both GraphQL (nodes) and REST (list) formats
        assignees_data = issue.get("assignees", [])
        if isinstance(assignees_data, dict):  # GraphQL format
            assignees = [assignee["login"] for assignee in assignees_data.get("nodes", [])]
        else:  # REST API format
            assignees = [assignee["login"] for assignee in assignees_data]

        # Parse milestone
        milestone = None
        if issue.get("milestone"):
            milestone = issue["milestone"]["title"]

        # Parse status from project item if available
        status = TicketStatus.TODO.value
        if project_item and project_item.get("fieldValues"):
            for field in project_item["fieldValues"].get("nodes", []):
                if field.get("__typename") == "ProjectV2ItemFieldSingleSelectValue":
                    status = field.get("name", status)

        return Ticket(
            id=str(issue["id"]),
            number=issue.get("number"),
            title=issue["title"],
            body=issue.get("body"),
            status=status,
            labels=labels,
            assignees=assignees,
            milestone=milestone,
            created_at=(
                datetime.fromisoformat(issue["createdAt"].replace("Z", "+00:00"))
                if issue.get("createdAt")
                else None
            ),
            updated_at=(
                datetime.fromisoformat(issue["updatedAt"].replace("Z", "+00:00"))
                if issue.get("updatedAt")
                else None
            ),
            url=issue.get("url"),
            metadata={"github_node_id": issue["id"]},
        )

    async def create_ticket(
        self,
        title: str,
        body: str | None = None,
        labels: list[str] | None = None,
        assignee: str | None = None,
    ) -> Ticket:
        """Create a new ticket (GitHub issue).

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
        # Prepare request data
        data = {
            "title": title,
        }
        
        if body:
            data["body"] = body
        
        if labels:
            data["labels"] = labels
        
        if assignee:
            data["assignee"] = assignee
        
        # Create issue via REST API
        response = await self._rest_request(
            "POST",
            f"/repos/{self.owner}/{self.repo}/issues",
            json_data=data,
        )
        
        # Parse response to Ticket model
        return self._parse_issue_to_ticket(response)

    async def get_tickets(
        self,
        status: str | None = None,
        assignee: str | None = None,
        label: str | None = None,
        milestone: str | None = None,
        limit: int = 50,
    ) -> list[Ticket]:
        """Get list of tickets from repository issues."""
        # Build filter string
        filters = [f"repo:{self.owner}/{self.repo}", "is:issue"]
        if status:
            if status.lower() in ["done", "closed"]:
                filters.append("is:closed")
            else:
                filters.append("is:open")
        if assignee:
            filters.append(f"assignee:{assignee}")
        if label:
            filters.append(f"label:{label}")
        if milestone:
            filters.append(f"milestone:{milestone}")

        query_str = " ".join(filters)

        query = """
        query($query: String!, $limit: Int!) {
            search(query: $query, type: ISSUE, first: $limit) {
                nodes {
                    ... on Issue {
                        id
                        number
                        title
                        body
                        createdAt
                        updatedAt
                        url
                        labels(first: 20) {
                            nodes {
                                name
                            }
                        }
                        assignees(first: 10) {
                            nodes {
                                login
                            }
                        }
                        milestone {
                            title
                        }
                    }
                }
            }
        }
        """

        data = await self._graphql_request(query, {"query": query_str, "limit": limit})
        issues = data["search"]["nodes"]

        return [self._parse_issue_to_ticket(issue) for issue in issues if issue]

    async def get_ticket(self, ticket_id: str) -> Ticket:
        """Get a single ticket by node ID or issue number."""
        # Check if ticket_id is a number (issue number) or node ID
        if ticket_id.isdigit():
            # It's an issue number
            query = """
            query($owner: String!, $repo: String!, $number: Int!) {
                repository(owner: $owner, name: $repo) {
                    issue(number: $number) {
                        id
                        number
                        title
                        body
                        createdAt
                        updatedAt
                        url
                        labels(first: 20) {
                            nodes {
                                name
                            }
                        }
                        assignees(first: 10) {
                            nodes {
                                login
                            }
                        }
                        milestone {
                            title
                        }
                    }
                }
            }
            """
            data = await self._graphql_request(
                query,
                {"owner": self.owner, "repo": self.repo, "number": int(ticket_id)},
            )
            issue = data["repository"]["issue"]
        else:
            # It's a node ID
            query = """
            query($id: ID!) {
                node(id: $id) {
                    ... on Issue {
                        id
                        number
                        title
                        body
                        createdAt
                        updatedAt
                        url
                        labels(first: 20) {
                            nodes {
                                name
                            }
                        }
                        assignees(first: 10) {
                            nodes {
                                login
                            }
                        }
                        milestone {
                            title
                        }
                    }
                }
            }
            """
            data = await self._graphql_request(query, {"id": ticket_id})
            issue = data["node"]

        if not issue:
            raise ValueError(f"Ticket {ticket_id} not found")

        return self._parse_issue_to_ticket(issue)

    async def get_comments(self, ticket_id: str) -> list[Comment]:
        """Get all comments for a ticket."""
        ticket = await self.get_ticket(ticket_id)
        issue_number = ticket.number

        if not issue_number:
            raise ValueError(f"Could not determine issue number for ticket {ticket_id}")

        query = """
        query($owner: String!, $repo: String!, $number: Int!) {
            repository(owner: $owner, name: $repo) {
                issue(number: $number) {
                    id
                    comments(first: 100) {
                        nodes {
                            id
                            body
                            author {
                                login
                            }
                            createdAt
                            updatedAt
                            url
                        }
                    }
                }
            }
        }
        """

        data = await self._graphql_request(
            query,
            {"owner": self.owner, "repo": self.repo, "number": issue_number},
        )
        comments_data = data["repository"]["issue"]["comments"]["nodes"]

        return [
            Comment(
                id=comment["id"],
                ticket_id=ticket.id,
                author=comment["author"]["login"] if comment.get("author") else "ghost",
                body=comment["body"],
                created_at=(
                    datetime.fromisoformat(comment["createdAt"].replace("Z", "+00:00"))
                    if comment.get("createdAt")
                    else None
                ),
                updated_at=(
                    datetime.fromisoformat(comment["updatedAt"].replace("Z", "+00:00"))
                    if comment.get("updatedAt")
                    else None
                ),
                url=comment.get("url"),
            )
            for comment in comments_data
        ]

    async def add_comment(self, ticket_id: str, body: str) -> Comment:
        """Add a comment to a ticket."""
        ticket = await self.get_ticket(ticket_id)
        subject_id = ticket.id

        mutation = """
        mutation($subjectId: ID!, $body: String!) {
            addComment(input: {subjectId: $subjectId, body: $body}) {
                commentEdge {
                    node {
                        id
                        body
                        author {
                            login
                        }
                        createdAt
                        updatedAt
                        url
                    }
                }
            }
        }
        """

        data = await self._graphql_request(
            mutation, {"subjectId": subject_id, "body": body}
        )
        comment_data = data["addComment"]["commentEdge"]["node"]

        return Comment(
            id=comment_data["id"],
            ticket_id=ticket.id,
            author=comment_data["author"]["login"] if comment_data.get("author") else "ghost",
            body=comment_data["body"],
            created_at=(
                datetime.fromisoformat(comment_data["createdAt"].replace("Z", "+00:00"))
                if comment_data.get("createdAt")
                else None
            ),
            updated_at=(
                datetime.fromisoformat(comment_data["updatedAt"].replace("Z", "+00:00"))
                if comment_data.get("updatedAt")
                else None
            ),
            url=comment_data.get("url"),
        )

    async def get_labels(self) -> list[Label]:
        """Get all available labels in the repository."""
        query = """
        query($owner: String!, $repo: String!) {
            repository(owner: $owner, name: $repo) {
                labels(first: 100) {
                    nodes {
                        id
                        name
                        description
                        color
                    }
                }
            }
        }
        """

        data = await self._graphql_request(
            query, {"owner": self.owner, "repo": self.repo}
        )
        labels_data = data["repository"]["labels"]["nodes"]

        return [
            Label(
                id=label["id"],
                name=label["name"],
                description=label.get("description"),
                color=label.get("color"),
            )
            for label in labels_data
        ]

    async def get_ticket_labels(self, ticket_id: str) -> list[Label]:
        """Get labels for a specific ticket."""
        ticket = await self.get_ticket(ticket_id)
        all_labels = await self.get_labels()

        # Filter labels that are on this ticket
        return [label for label in all_labels if label.name in ticket.labels]

    async def add_label(self, ticket_id: str, label_name: str) -> Ticket:
        """Add a label to a ticket."""
        ticket = await self.get_ticket(ticket_id)
        issue_id = ticket.id

        # Get label ID
        labels = await self.get_labels()
        label = next((l for l in labels if l.name == label_name), None)
        if not label:
            raise ValueError(f"Label '{label_name}' not found")

        mutation = """
        mutation($labelableId: ID!, $labelIds: [ID!]!) {
            addLabelsToLabelable(input: {labelableId: $labelableId, labelIds: $labelIds}) {
                clientMutationId
            }
        }
        """

        await self._graphql_request(
            mutation, {"labelableId": issue_id, "labelIds": [label.id]}
        )

        return await self.get_ticket(ticket_id)

    async def _get_status_field_id(self, project_number: int | None = None) -> tuple[str, dict]:
        """Get the status field ID and available options from the project.

        Returns:
            Tuple of (field_id, options_dict) where options_dict maps option names to IDs
        """
        project_id = await self._get_project_id(project_number)

        query = """
        query($projectId: ID!) {
            node(id: $projectId) {
                ... on ProjectV2 {
                    fields(first: 20) {
                        nodes {
                            ... on ProjectV2SingleSelectField {
                                id
                                name
                                options {
                                    id
                                    name
                                }
                            }
                        }
                    }
                }
            }
        }
        """

        data = await self._graphql_request(query, {"projectId": project_id})
        fields = data["node"]["fields"]["nodes"]

        # Find the Status field
        status_field = None
        for field in fields:
            if field and field.get("name") == "Status":
                status_field = field
                break

        if not status_field:
            raise ValueError("Status field not found in project")

        # Build options dict
        options = {opt["name"]: opt["id"] for opt in status_field.get("options", [])}

        return status_field["id"], options

    async def _get_project_item_id(
        self, ticket_id: str, project_number: int | None = None
    ) -> str:
        """Get the project item ID for a ticket in a project.

        Args:
            ticket_id: Ticket identifier
            project_number: Project number (uses default if None)

        Returns:
            Project item ID

        Raises:
            ValueError: If ticket not in project
        """
        ticket = await self.get_ticket(ticket_id)
        project_id = await self._get_project_id(project_number)

        query = """
        query($projectId: ID!) {
            node(id: $projectId) {
                ... on ProjectV2 {
                    items(first: 100) {
                        nodes {
                            id
                            content {
                                ... on Issue {
                                    id
                                    number
                                }
                            }
                        }
                    }
                }
            }
        }
        """

        data = await self._graphql_request(query, {"projectId": project_id})
        items = data["node"]["items"]["nodes"]

        # Find the item matching our ticket
        for item in items:
            if item and item.get("content"):
                if item["content"]["id"] == ticket.id:
                    return item["id"]

        raise ValueError(
            f"Ticket #{ticket.number} not found in project. "
            f"Use add_ticket_to_project first."
        )

    async def update_status(
        self, ticket_id: str, status: str, project_number: int | None = None
    ) -> Ticket:
        """Update the status of a ticket in GitHub Projects V2.

        Args:
            ticket_id: Ticket identifier
            status: New status value (e.g., "Todo", "In Progress", "Done")
            project_number: Project number (optional, uses default from config)

        Returns:
            Updated ticket object

        Raises:
            ValueError: If ticket not in project or status not found
        """
        # Use provided project_number or fall back to default
        project_num = project_number or self.project_number
        
        # Get project field and option IDs
        field_id, options = await self._get_status_field_id(project_num)

        # Find matching option (case-insensitive)
        option_id = None
        for opt_name, opt_id in options.items():
            if opt_name.lower() == status.lower():
                option_id = opt_id
                break

        if not option_id:
            available = ", ".join(options.keys())
            raise ValueError(
                f"Status '{status}' not found. Available options: {available}"
            )

        # Get project item ID
        item_id = await self._get_project_item_id(ticket_id, project_num)

        # Update the status field
        mutation = """
        mutation($projectId: ID!, $itemId: ID!, $fieldId: ID!, $optionId: String!) {
            updateProjectV2ItemFieldValue(input: {
                projectId: $projectId
                itemId: $itemId
                fieldId: $fieldId
                value: {singleSelectOptionId: $optionId}
            }) {
                projectV2Item {
                    id
                }
            }
        }
        """

        project_id = await self._get_project_id(project_num)

        await self._graphql_request(
            mutation,
            {
                "projectId": project_id,
                "itemId": item_id,
                "fieldId": field_id,
                "optionId": option_id,
            },
        )

        # Get the ticket and update its status to reflect the change
        ticket = await self.get_ticket(ticket_id)
        # Override status with the actual status we just set
        # (get_ticket doesn't fetch status from Projects V2)
        for opt_name, opt_id in options.items():
            if opt_id == option_id:
                ticket.status = opt_name
                break

        return ticket

    async def add_branch(self, ticket_id: str, branch_name: str) -> Ticket:
        """Link a branch to a ticket.

        Note: GitHub doesn't have a direct API for linking branches to issues.
        This is typically done through branch naming conventions or PR references.
        """
        ticket = await self.get_ticket(ticket_id)
        # Store branch info in ticket metadata
        ticket.branch = branch_name
        return ticket

    async def add_pull_request(self, ticket_id: str, pr_url: str) -> Ticket:
        """Link a pull request to a ticket.

        This is typically done by mentioning the issue in the PR description.
        """
        ticket = await self.get_ticket(ticket_id)
        ticket.pull_requests.append(pr_url)
        return ticket

    async def add_subtask(self, parent_id: str, subtask_id: str) -> Ticket:
        """Add a subtask relationship to a ticket.

        This is implemented through issue references in the body/comments.
        """
        parent = await self.get_ticket(parent_id)
        subtask = await self.get_ticket(subtask_id)

        # Add reference in parent issue body
        await self.add_comment(
            parent_id,
            f"Subtask: #{subtask.number} {subtask.title}",
        )

        parent.subtasks.append(subtask_id)
        return parent

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
        # First, verify parent ticket exists
        parent_ticket = await self.get_ticket(parent_id)
        
        # Create subtask body with parent reference
        subtask_body = body or ""
        parent_ref = f"Part of #{parent_ticket.number}"
        if subtask_body:
            subtask_body = f"{parent_ref}\n\n{subtask_body}"
        else:
            subtask_body = parent_ref
        
        # Create the new ticket
        subtask = await self.create_ticket(
            title=title,
            body=subtask_body,
            labels=labels,
        )
        
        # Link it as subtask to parent
        await self.add_subtask(parent_id, str(subtask.number))
        
        return subtask

    async def assign_ticket(self, ticket_id: str, assignee: str) -> Ticket:
        """Assign a ticket to a user."""
        ticket = await self.get_ticket(ticket_id)
        issue_id = ticket.id

        mutation = """
        mutation($assignableId: ID!, $assigneeIds: [ID!]!) {
            addAssigneesToAssignable(input: {assignableId: $assignableId, assigneeIds: $assigneeIds}) {
                clientMutationId
            }
        }
        """

        # Get user ID
        user_query = """
        query($login: String!) {
            user(login: $login) {
                id
            }
        }
        """
        user_data = await self._graphql_request(user_query, {"login": assignee})
        user_id = user_data["user"]["id"]

        await self._graphql_request(
            mutation, {"assignableId": issue_id, "assigneeIds": [user_id]}
        )

        return await self.get_ticket(ticket_id)

    async def assign_to_self(self, ticket_id: str) -> Ticket:
        """Assign a ticket to the authenticated user."""
        # Get current user
        query = """
        query {
            viewer {
                login
            }
        }
        """
        data = await self._graphql_request(query)
        username = data["viewer"]["login"]

        return await self.assign_ticket(ticket_id, username)

    async def get_milestones(self) -> list[Milestone]:
        """Get all available milestones in the repository."""
        query = """
        query($owner: String!, $repo: String!) {
            repository(owner: $owner, name: $repo) {
                milestones(first: 100, states: [OPEN, CLOSED]) {
                    nodes {
                        id
                        title
                        description
                        state
                        dueOn
                        url
                    }
                }
            }
        }
        """

        data = await self._graphql_request(
            query, {"owner": self.owner, "repo": self.repo}
        )
        milestones_data = data["repository"]["milestones"]["nodes"]

        return [
            Milestone(
                id=milestone["id"],
                title=milestone["title"],
                description=milestone.get("description"),
                state=milestone["state"].lower(),
                due_date=(
                    datetime.fromisoformat(milestone["dueOn"].replace("Z", "+00:00"))
                    if milestone.get("dueOn")
                    else None
                ),
                url=milestone.get("url"),
            )
            for milestone in milestones_data
        ]

    async def add_milestone(self, ticket_id: str, milestone_title: str) -> Ticket:
        """Add a ticket to a milestone."""
        ticket = await self.get_ticket(ticket_id)
        issue_number = ticket.number

        if not issue_number:
            raise ValueError(f"Could not determine issue number for ticket {ticket_id}")

        # Get milestone by title
        milestones = await self.get_milestones()
        milestone = next((m for m in milestones if m.title == milestone_title), None)
        if not milestone:
            raise ValueError(f"Milestone '{milestone_title}' not found")

        # Extract milestone number from ID or use REST API
        endpoint = f"/repos/{self.owner}/{self.repo}/issues/{issue_number}"
        # GitHub REST API expects milestone number, extract from GraphQL ID if possible
        # For simplicity, we'll use the milestone title to find the number via REST
        milestones_rest = await self._rest_request(
            "GET", f"/repos/{self.owner}/{self.repo}/milestones"
        )
        milestone_number = next(
            (m["number"] for m in milestones_rest if m["title"] == milestone_title),
            None,
        )

        if not milestone_number:
            raise ValueError(f"Could not find milestone number for '{milestone_title}'")

        await self._rest_request("PATCH", endpoint, {"milestone": milestone_number})

        return await self.get_ticket(ticket_id)

    async def add_ticket_to_project(
        self, ticket_id: str, project_number: int | None = None
    ) -> Ticket:
        """Add an existing ticket (issue) to a GitHub Project V2 board.

        Args:
            ticket_id: Ticket ID or issue number
            project_number: Project number (uses default if None)

        Returns:
            Updated ticket object

        Raises:
            ValueError: If ticket or project not found
        """
        # Get the ticket to retrieve its node ID
        ticket = await self.get_ticket(ticket_id)

        if not ticket.id:
            raise ValueError(f"Could not determine node ID for ticket {ticket_id}")

        # Get project node ID
        project_id = await self._get_project_id(project_number)

        # GraphQL mutation to add item to project
        mutation = """
        mutation($projectId: ID!, $contentId: ID!) {
            addProjectV2ItemById(input: {projectId: $projectId, contentId: $contentId}) {
                item {
                    id
                }
            }
        }
        """

        try:
            await self._graphql_request(
                mutation,
                {
                    "projectId": project_id,
                    "contentId": ticket.id,
                },
            )
        except Exception as e:
            raise ValueError(f"Failed to add ticket to project: {e}")

        # Return the updated ticket
        return await self.get_ticket(ticket_id)

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
        # Get both tickets to verify they exist
        child = await self.get_ticket(ticket_id)
        parent = await self.get_ticket(parent_id)

        # Add parent reference in child issue body via comment
        await self.add_comment(
            ticket_id,
            f"Parent: #{parent.number} {parent.title}",
        )

        return await self.get_ticket(ticket_id)

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
        # Get both tickets to verify they exist
        blocked = await self.get_ticket(ticket_id)
        blocker = await self.get_ticket(blocking_ticket_id)

        # Add blocked-by reference via comment
        await self.add_comment(
            ticket_id,
            f"Blocked by: #{blocker.number} {blocker.title}",
        )

        return await self.get_ticket(ticket_id)

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
        # Get both tickets to verify they exist
        blocker = await self.get_ticket(ticket_id)
        blocked = await self.get_ticket(blocked_ticket_id)

        # Add blocking reference via comment
        await self.add_comment(
            ticket_id,
            f"Blocking: #{blocked.number} {blocked.title}",
        )

        return await self.get_ticket(ticket_id)
