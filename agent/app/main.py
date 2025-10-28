"""Implement a feature from a GitLab issue."""

from typing import Dict, Any
from .cloud_engineer_agent import CloudEngineerAgent


def implement_feature_from_issue(
    issue_id: str, 
    issue_content: str, 
    project_name: str = None, 
    target_branch: str = "dev"
) -> Dict[str, Any]:
    """
    Convenience function to implement a feature from a GitLab issue.

    Args:
        issue_id: GitLab issue ID
        issue_content: Issue content with structured sections
        project_name: GitLab project name (will use env var PROJECT_NAME if not provided)
        target_branch: Target branch name (default: dev)

    Returns:
        Implementation result dictionary
    """
    agent = CloudEngineerAgent()
    try:
        return agent.implement_feature(
            issue_id=issue_id, 
            description=issue_content, 
            project_name=project_name, 
            target_branch=target_branch
        )
    finally:
        agent.cleanup()
