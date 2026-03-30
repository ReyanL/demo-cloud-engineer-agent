"""Cloud Engineer Agent for implementing features from GitLab issues."""

import logging
import os
import re
import sys
from datetime import datetime
from typing import Dict, Any, List
import uuid

from strands import Agent, AgentSkills
from strands.session.file_session_manager import FileSessionManager
from strands_tools import file_read, file_write, tavily


# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from .ai_models import claude_4_5_sonnet


class MockModel:
    """Mock model for testing purposes."""

    def __call__(self, *args, **kwargs):
        """Mock model call that returns a simple response."""

        class MockResponse:
            def __init__(self):
                self.message = "Mock implementation response: Feature implemented successfully using cloud engineering best practices."

        return MockResponse()


from .mcp_servers import get_mcp_tools
from .git_tools import (
    clone_branch,
    create_branch,
    push_branch,
    create_merge_request,
    get_repository_path,
    cleanup_repository,
)
from .terraform_command_tools import (
    terraform_init,
    terraform_plan,
)
from .prompts import SYSTEM_PROMPT, USER_PROMPT

# Skills directory path
SKILLS_DIR = os.path.join(os.path.dirname(__file__), "skills")


# Configure the root strands logger
logging.getLogger("strands").setLevel(logging.INFO)
# Add a handler to see the logs
logging.basicConfig(
    format="%(levelname)s | %(name)s | %(message)s", handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)


class IssueContent:
    """Structure to hold parsed issue content."""

    def __init__(self, title: str, context: str, todo: str, definition_of_done: str):
        """
        Initialize issue content structure.

        Args:
            title: Issue title
            context: Background and business context
            todo: Implementation checklist
            definition_of_done: Acceptance criteria
        """
        self.title = title
        self.context = context
        self.todo = todo
        self.definition_of_done = definition_of_done

    def validate(self) -> List[str]:
        """
        Validate that all required sections are present and non-empty.

        Returns:
            List of validation errors, empty if valid
        """
        errors = []

        if not self.title.strip():
            errors.append("Title is required and cannot be empty")

        if not self.context.strip():
            errors.append("Context section is required and cannot be empty")

        if not self.todo.strip():
            errors.append("Todo section is required and cannot be empty")

        if not self.definition_of_done.strip():
            errors.append("Definition of Done section is required and cannot be empty")

        return errors

    def to_dict(self) -> Dict[str, str]:
        """Convert to dictionary representation."""
        return {
            "title": self.title,
            "context": self.context,
            "todo": self.todo,
            "definition_of_done": self.definition_of_done,
        }


class CloudEngineerAgent:
    """Cloud Engineer Agent for implementing features based on GitLab issue content."""

    def __init__(
        self,
        test_mode: bool = False,
        session_id: str = None,
        additional_prompt: str = None,
    ):
        """
        Initialize the Cloud Engineer Agent for AWS infrastructure.

        Args:
            test_mode: If True, skip external MCP tool initialization for testing
            session_id: Session ID to continue existing session or create new one if None
            additional_prompt: Additional prompt text to append to the existing prompt
        """
        self.test_mode = test_mode
        self.session_id = session_id
        self.additional_prompt = additional_prompt

        # Initialize tools
        cloud_tools = []

        # Add custom git tools (always available, even in test mode)
        git_tools = [
            clone_branch,
            create_branch,
            push_branch,
            create_merge_request,
            get_repository_path,
            cleanup_repository,
        ]
        logger.info("Git tools enabled")

        # Add Terraform verification tools (always available, even in test mode)
        terraform_tools = [
            terraform_init,
            terraform_plan,
        ]
        logger.info("Terraform verification tools enabled")

        # Get AWS tools (only if not in test mode)
        if not test_mode:
            try:
                aws_terraform_tools = get_mcp_tools(
                    "aws_terraform", ["SearchAwsProviderDocs", "RunCheckovScan"]
                )
                aws_docs_tools = get_mcp_tools(
                    "aws_documentation", ["search_documentation", "read_documentation"]
                )
                cloud_tools.extend(aws_terraform_tools + aws_docs_tools)
                logger.info("AWS tools enabled")
            except Exception as e:
                logger.warning("Failed to load AWS tools: %s", e)

        # Initialize the agent with tools
        model = MockModel() if test_mode else claude_4_5_sonnet

        # Build tools list
        base_tools = [file_read, file_write, tavily]

        # Note: Langfuse tracing is configured in app/__init__.py at module import time
        # This ensures OTEL environment variables are set before TracerProvider initialization

        # Generate session ID - use provided session_id or create new one
        if self.session_id:
            session_id = self.session_id
            logger.info("Using provided session ID: %s", session_id)
        else:
            session_id = str(uuid.uuid4())
            logger.info("Created new session with ID: %s", session_id)

        session_manager = FileSessionManager(session_id=session_id)

        # Prepare system prompt with additional prompt if provided
        system_prompt = SYSTEM_PROMPT
        if self.additional_prompt:
            system_prompt += (
                f"\n\n## ADDITIONAL INSTRUCTIONS\n\n{self.additional_prompt}"
            )
            logger.info("Added additional prompt to system prompt")

        # Initialize skills plugin
        self.skills_plugin = AgentSkills(skills=SKILLS_DIR)
        available_skills = self.skills_plugin.get_available_skills()
        logger.info(
            "Skills plugin loaded: %s",
            [s.name if hasattr(s, "name") else s for s in available_skills],
        )

        self.agent = (
            Agent(
                model=model,
                tools=base_tools + git_tools + terraform_tools + cloud_tools,
                system_prompt=system_prompt,
                plugins=[self.skills_plugin],
                trace_attributes={
                    "user.id": os.environ["USER_ID"],
                    "session.id": session_id,
                    "langfuse.environment": "dev",  # TODO: add environment variable
                    "langfuse.tags": ["cloud-engineer-agent"],
                },
                session_manager=session_manager,
            )
            if not test_mode
            else MockModel()
        )

        logger.info("Cloud Engineer Agent initialized successfully")

    def parse_issue_content(self, description: str) -> IssueContent:
        """
        Parse issue content to extract structured sections.

        Args:
            description: Raw issue content containing title, context, todo, and definition of done

        Returns:
            IssueContent object with parsed sections

        Raises:
            ValueError: If issue content format is invalid or missing required sections
        """
        logger.info("Parsing issue content...")

        # Extract title (first line or before first heading)
        lines = description.strip().split("\n")
        title = ""
        content_start = 0

        # Look for the first heading to determine where title ends
        for i, line in enumerate(lines):
            if line.strip().startswith("#") or line.strip().lower().startswith(
                "context"
            ):
                content_start = i
                break
            if not title and line.strip():
                title = line.strip()

        if not title:
            title = lines[0].strip() if lines else ""

        # Join remaining content for section parsing
        content = "\n".join(lines[content_start:])

        # Extract sections using regex patterns
        context_pattern = r"(?i)#+\s*context\s*\n(.*?)(?=#+|\Z)"
        todo_pattern = r"(?i)#+\s*todo\s*\n(.*?)(?=#+|\Z)"
        dod_pattern = r"(?i)#+\s*definition\s+of\s+done\s*\n(.*?)(?=#+|\Z)"

        context_match = re.search(context_pattern, content, re.DOTALL)
        todo_match = re.search(todo_pattern, content, re.DOTALL)
        dod_match = re.search(dod_pattern, content, re.DOTALL)

        context = context_match.group(1).strip() if context_match else ""
        todo = todo_match.group(1).strip() if todo_match else ""
        definition_of_done = dod_match.group(1).strip() if dod_match else ""

        # Create and validate issue content
        issue = IssueContent(title, context, todo, definition_of_done)
        validation_errors = issue.validate()

        if validation_errors:
            error_msg = f"Invalid issue format: {'; '.join(validation_errors)}"
            logger.error(error_msg)
            raise ValueError(error_msg)

        logger.info("Successfully parsed issue: '%s'", title)
        return issue

    def generate_branch_name(self, issue_id: str, issue_title: str) -> str:
        """
        Generate a standardized branch name from issue ID and title.

        Args:
            issue_id: Issue identifier
            issue_title: Issue title

        Returns:
            Formatted branch name following conventions
        """
        # Clean title: lowercase, replace spaces/special chars with hyphens, limit length
        clean_title = re.sub(r"[^a-zA-Z0-9\s-]", "", issue_title.lower())
        clean_title = re.sub(r"\s+", "-", clean_title.strip())
        clean_title = clean_title[:30]  # Limit length

        branch_name = f"feature/issue-{issue_id}-{clean_title}"
        logger.info("Generated branch name: %s", branch_name)
        return branch_name

    def implement_feature(
        self,
        issue_id: str,
        description: str,
        project_name: str = None,
        target_branch: str = "dev",
    ) -> Dict[str, Any]:
        """
        Implement a cloud infrastructure feature based on GitLab issue content.

        The AI agent will handle the entire workflow including:
        - Cloning the repository
        - Creating feature branches
        - Implementing changes
        - Pushing changes
        - Creating merge requests

        Args:
            issue_id: GitLab issue ID
            description: Issue description
            project_name: GitLab project name (will use env var PROJECT_NAME if not provided)
            target_branch: Target branch name (default: dev)

        Returns:
            Dict containing implementation results and metadata

        Raises:
            ValueError: If input parameters are invalid
            Exception: If implementation fails at any stage
        """
        # Use environment variable if project_name not provided
        if project_name is None:
            project_name = os.environ.get(
                "PROJECT_NAME", "my-app"
            )
            if not project_name:
                raise ValueError("PROJECT_NAME must be provided or set in environment")

        if not all([issue_id, description]):
            raise ValueError("All parameters (issue_id, description) are required")

        logger.info(
            "Starting feature implementation for issue %s in project %s",
            issue_id,
            project_name,
        )

        try:
            # Parse and validate issue content
            logger.info("Parsing and validating issue content...")
            parsed_issue = self.parse_issue_content(description)

            # Generate suggested feature branch name
            feature_branch = self.generate_branch_name(issue_id, parsed_issue.title)
            logger.info("Suggested feature branch name: %s", feature_branch)

            # Format issue content for prompt
            issue_content_str = self._format_issue_content(parsed_issue)

            # Prepare prompt with parsed issue content and suggested branch name
            formatted_prompt = USER_PROMPT.format(
                issue_id=issue_id,
                project_name=project_name,
                target_branch=target_branch,
                feature_branch=feature_branch,
                issue_content=issue_content_str,
            )

            # Append additional prompt if provided
            if self.additional_prompt:
                formatted_prompt += (
                    f"\n\n## CRITICAL INSTRUCTIONS\n\n{self.additional_prompt}"
                )
                logger.info("Added additional prompt to user prompt")

            # Execute implementation with AI agent
            # The agent will use the git tools to handle the entire workflow
            logger.info("Executing AI agent to implement feature...")
            implementation_response = self.agent(formatted_prompt)

            # Verify skill activation after execution
            activated_skills = self._get_activated_skill_names()
            if activated_skills:
                logger.info(
                    "Skills activated during execution: %s", activated_skills
                )
            else:
                logger.warning(
                    "NO skills were activated during execution for issue %s. "
                    "Best practices may not have been followed.",
                    issue_id,
                )

            # Compile results
            result = {
                "status": "success",
                "message": f"Successfully implemented feature for issue {issue_id}",
                "issue_id": issue_id,
                "project_name": project_name,
                "target_branch": target_branch,
                "feature_branch": feature_branch,
                "issue_content": parsed_issue.to_dict(),
                "skills_activated": activated_skills,
                "agent_response": (
                    implementation_response.message
                    if hasattr(implementation_response, "message")
                    else str(implementation_response)
                ),
                "completed_at": datetime.now().isoformat(),
            }

            logger.info(
                "Feature implementation completed successfully for issue %s", issue_id
            )
            return result

        except Exception as e:
            error_msg = f"Feature implementation failed for issue {issue_id}: {str(e)}"
            logger.error(error_msg, exc_info=True)

            # Return error result
            return {
                "status": "error",
                "message": error_msg,
                "issue_id": issue_id,
                "project_name": project_name,
                "target_branch": target_branch,
                "error": str(e),
                "failed_at": datetime.now().isoformat(),
            }

    def _get_activated_skill_names(self) -> list:
        """Get list of skill names activated during agent execution."""
        try:
            activated = self.skills_plugin.get_activated_skills(self.agent)
            return [s.name if hasattr(s, "name") else s for s in activated]
        except Exception as e:
            logger.warning("Could not retrieve activated skills: %s", e)
            return []

    def _format_issue_content(self, issue: IssueContent) -> str:
        """Format issue content for prompt inclusion."""
        return f"""
Title: {issue.title}

## Context
{issue.context}

## Todo
{issue.todo}

## Definition of Done
{issue.definition_of_done}
"""

    def cleanup(self):
        """Clean up agent resources."""
        logger.info("Cleaning up Cloud Engineer Agent resources...")
        # Cleanup any MCP client connections if needed
        if hasattr(self, "agent") and not self.test_mode:
            try:
                # Close any open connections
                logger.info("Agent cleanup completed")
            except Exception as e:
                logger.warning("Error during cleanup: %s", e)
