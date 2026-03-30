"""Git tools for branch management and repository operations.

These tools provide local git operations for GitLab repository management.
"""

import logging
import os
import subprocess
import shutil
from pathlib import Path
from typing import Dict, Any, Optional
from strands import tool


logger = logging.getLogger(__name__)


def _get_gitlab_repo_base_url() -> str:
    """Get GitLab Repository base URL from environment or use default.

    Default is empty to avoid leaking organization-specific URLs in public repos.
    """
    return os.environ.get("GITLAB_REPO_BASE_URL", "")


def _get_gitlab_instance_base_url() -> str:
    """Get GitLab instance base URL from environment.

    Use a neutral default suitable for documentation.
    """
    return os.environ.get("GITLAB_URI", "https://gitlab.example.com/")


def _get_gitlab_token() -> Optional[str]:
    """Get GitLab token from environment."""
    return os.environ.get("GITLAB_TOKEN")


def _construct_repo_url(project_name: str, use_token: bool = True) -> str:
    """
    Construct repository URL for GitLab.

    Args:
        project_name: GitLab project name or URL-encoded path
        use_token: Whether to include token in URL for authentication

    Returns:
        Repository URL
    """
    gitlab_url = _get_gitlab_repo_base_url()
    base_url = gitlab_url.replace("https://", "").replace("http://", "") if gitlab_url else ""

    if use_token:
        token = _get_gitlab_token()
        if token:
            return f"https://oauth2:{token}@{base_url}/{project_name}.git"

    # If no base URL provided, return project name (caller can handle)
    return f"{gitlab_url}/{project_name}.git" if gitlab_url else project_name


def _run_git_command(
    command: list[str], cwd: Optional[str] = None
) -> subprocess.CompletedProcess:
    """
    Run a git command and return the result.

    Args:
        command: Git command as list of strings
        cwd: Working directory for the command

    Returns:
        CompletedProcess result

    Raises:
        subprocess.CalledProcessError: If command fails
    """
    try:
        result = subprocess.run(
            command, cwd=cwd, capture_output=True, text=True, check=True
        )
        return result
    except subprocess.CalledProcessError as e:
        logger.error("Git command failed: %s", " ".join(command))
        logger.error("Error: %s", e.stderr)
        raise


def _check_remote_branch_exists(repo_url: str, branch: str) -> bool:
    """Check if a branch exists on the remote repository."""
    try:
        result = subprocess.run(
            ["git", "ls-remote", "--heads", repo_url, branch],
            capture_output=True, text=True, timeout=30,
        )
        return bool(result.stdout.strip())
    except (subprocess.SubprocessError, OSError):
        return False


def _list_remote_branches(repo_url: str) -> list[str]:
    """List all branches available on the remote repository."""
    try:
        result = subprocess.run(
            ["git", "ls-remote", "--heads", repo_url],
            capture_output=True, text=True, timeout=30,
        )
        branches = []
        for line in result.stdout.strip().split("\n"):
            if line.strip():
                ref = line.split("\t")[-1]
                branches.append(ref.replace("refs/heads/", ""))
        return branches
    except (subprocess.SubprocessError, OSError):
        return []


def _get_default_local_path(project_name: str) -> str:
    """
    Get default local path for repository.

    Uses /app/repos in Docker container, <cwd>/repos locally.
    Path is always absolute and within the application directory
    to ensure compatibility with MCP tools (e.g., Checkov scan).

    Args:
        project_name: GitLab project name or URL-encoded path

    Returns:
        Absolute local path for the repository
    """
    project_name = project_name.split("/")[-1]
    if os.environ.get("DOCKER_CONTAINER"):
        repos_dir = Path("/app/repos")
    else:
        repos_dir = Path.cwd() / "repos"
    repos_dir.mkdir(parents=True, exist_ok=True)
    return str(repos_dir / project_name)


@tool
def clone_branch(
    project_name: str, target_branch: str, local_path: Optional[str] = None
) -> Dict[str, Any]:
    """
    Clone the specified branch from the GitLab repository.

    If the repository is already cloned, it will fetch latest changes and checkout the branch
    instead of cloning again.

    Args:
        project_name: GitLab project name or URL-encoded path
        target_branch: Branch name to clone
        local_path: Optional local path where to clone the repository

    Returns:
        Dict containing operation status and metadata

    Raises:
        ValueError: If project_name or target_branch is empty
        subprocess.CalledProcessError: If git operations fail
    """
    if not project_name or not target_branch:
        raise ValueError("project_name and target_branch are required")

    logger.info("Cloning branch '%s' from project '%s'", target_branch, project_name)

    # Force default path within /app for MCP tool compatibility (e.g., Checkov scan)
    repo_path = _get_default_local_path(project_name)
    if local_path and local_path != repo_path:
        logger.warning(
            "Ignoring custom local_path '%s', using '%s' for MCP tool compatibility",
            local_path, repo_path,
        )

    # Construct repository URL
    repo_url = _construct_repo_url(project_name)

    # Check if repository is already cloned
    already_cloned = False
    if os.path.exists(repo_path):
        git_dir = os.path.join(repo_path, ".git")
        if os.path.isdir(git_dir):
            logger.info("Repository already cloned at %s, reusing it", repo_path)
            already_cloned = True
        else:
            logger.warning(
                "Directory exists but is not a git repository, removing: %s", repo_path
            )
            shutil.rmtree(repo_path)

    # Clone or update the repository
    try:
        if already_cloned:
            # Fetch latest changes
            logger.info("Fetching latest changes from remote")
            _run_git_command(["git", "fetch", "origin"], cwd=repo_path)

            # Check if branch exists locally
            try:
                _run_git_command(
                    ["git", "rev-parse", "--verify", target_branch], cwd=repo_path
                )
                branch_exists = True
            except subprocess.CalledProcessError:
                branch_exists = False

            # Checkout the target branch
            if branch_exists:
                logger.info("Checking out existing branch: %s", target_branch)
                _run_git_command(["git", "checkout", target_branch], cwd=repo_path)
                _run_git_command(
                    ["git", "pull", "origin", target_branch], cwd=repo_path
                )
            else:
                # Verify branch exists on remote before checking out
                remote_check = subprocess.run(
                    ["git", "ls-remote", "--heads", "origin", target_branch],
                    cwd=repo_path, capture_output=True, text=True, timeout=30,
                )
                if not remote_check.stdout.strip():
                    available = _list_remote_branches(repo_url)
                    raise RuntimeError(
                        f"Branch '{target_branch}' does not exist on remote repository "
                        f"'{project_name}'. Available branches: "
                        f"{', '.join(available) if available else 'none found'}. "
                        f"Please specify an existing branch."
                    )
                logger.info("Checking out remote branch: %s", target_branch)
                _run_git_command(
                    ["git", "checkout", "-b", target_branch, f"origin/{target_branch}"],
                    cwd=repo_path,
                )
        else:
            # Verify target branch exists on remote before cloning
            if not _check_remote_branch_exists(repo_url, target_branch):
                available = _list_remote_branches(repo_url)
                raise RuntimeError(
                    f"Branch '{target_branch}' does not exist on remote repository "
                    f"'{project_name}'. Available branches: "
                    f"{', '.join(available) if available else 'none found'}. "
                    f"Please specify an existing branch."
                )

            # Clone the repository
            logger.info("Cloning repository to %s", repo_path)
            _run_git_command(
                [
                    "git",
                    "clone",
                    "--branch",
                    target_branch,
                    "--single-branch",
                    repo_url,
                    repo_path,
                ]
            )

        # Get commit hash
        result = _run_git_command(["git", "rev-parse", "HEAD"], cwd=repo_path)
        commit_hash = result.stdout.strip()

        # Count files
        result = _run_git_command(["git", "ls-files"], cwd=repo_path)
        files_count = (
            len(result.stdout.strip().split("\n")) if result.stdout.strip() else 0
        )

        action = "reused and updated" if already_cloned else "cloned"
        success_result = {
            "status": "success",
            "message": f"Successfully {action} branch '{target_branch}' from project '{project_name}'",
            "project_name": project_name,
            "branch": target_branch,
            "local_path": repo_path,
            "commit_hash": commit_hash,
            "files_count": files_count,
            "already_cloned": already_cloned,
        }

        logger.info("Operation completed: %s", success_result["message"])
        return success_result

    except subprocess.CalledProcessError as e:
        error_msg = f"Failed to clone/update branch '{target_branch}' from project '{project_name}': {e.stderr}"
        logger.error(error_msg)
        raise RuntimeError(error_msg) from e


@tool
def create_branch(
    project_name: str,
    new_branch: str,
    source_branch: str = "dev",
    local_path: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Create a new branch in the local repository.

    Args:
        project_name: GitLab project name or URL-encoded path
        source_branch: Branch to create the new branch from (default: dev)
        new_branch: Name for the new branch
        local_path: Optional local path to the repository

    Returns:
        Dict containing operation status and branch metadata

    Raises:
        ValueError: If any required parameter is empty
        subprocess.CalledProcessError: If git branch creation fails
    """
    if not all([project_name, source_branch, new_branch]):
        raise ValueError("project_name, source_branch, and new_branch are required")

    logger.info(
        "Creating branch '%s' from '%s' in project '%s'",
        new_branch,
        source_branch,
        project_name,
    )

    # Determine local path
    repo_path = _get_default_local_path(project_name)

    if not os.path.exists(repo_path):
        error_msg = f"Repository not found at {repo_path}. Please clone it first."
        logger.error(error_msg)
        raise FileNotFoundError(error_msg)

    try:
        # Checkout source branch
        _run_git_command(["git", "checkout", source_branch], cwd=repo_path)

        # Create and checkout new branch
        _run_git_command(["git", "checkout", "-b", new_branch], cwd=repo_path)

        # Get commit hash
        result = _run_git_command(["git", "rev-parse", "HEAD"], cwd=repo_path)
        commit_hash = result.stdout.strip()

        # Get timestamp
        result = _run_git_command(["git", "log", "-1", "--format=%cI"], cwd=repo_path)
        created_at = result.stdout.strip()

        success_result = {
            "status": "success",
            "message": f"Successfully created branch '{new_branch}' from '{source_branch}'",
            "project_name": project_name,
            "source_branch": source_branch,
            "new_branch": new_branch,
            "commit_hash": commit_hash,
            "created_at": created_at,
            "local_path": repo_path,
        }

        logger.info("Branch creation completed: %s", success_result["message"])
        return success_result

    except subprocess.CalledProcessError as e:
        error_msg = (
            f"Failed to create branch '{new_branch}' from '{source_branch}': {e.stderr}"
        )
        logger.error(error_msg)
        raise RuntimeError(error_msg) from e


@tool
def push_branch(
    project_name: str,
    branch_name: str,
    commit_message: Optional[str] = None,
    local_path: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Push the branch to the GitLab repository.

    Args:
        project_name: GitLab project name or URL-encoded path
        branch_name: Name of the branch to push
        commit_message: Optional commit message for staged changes
        local_path: Optional local path to the repository

    Returns:
        Dict containing operation status and push metadata

    Raises:
        ValueError: If project_name or branch_name is empty
        subprocess.CalledProcessError: If git push fails
    """
    if not project_name or not branch_name:
        raise ValueError("project_name and branch_name are required")

    logger.info("Pushing branch '%s' to project '%s'", branch_name, project_name)

    # Determine local path
    repo_path = _get_default_local_path(project_name)

    if not os.path.exists(repo_path):
        error_msg = f"Repository not found at {repo_path}. Please clone it first."
        logger.error(error_msg)
        raise FileNotFoundError(error_msg)

    try:
        # Check if there are changes to commit
        status_result = _run_git_command(
            ["git", "status", "--porcelain"], cwd=repo_path
        )

        has_changes = bool(status_result.stdout.strip())
        commit_hash = None
        files_changed = 0

        if has_changes and commit_message:
            # Stage all changes
            _run_git_command(["git", "add", "-A"], cwd=repo_path)

            # Commit changes
            _run_git_command(["git", "commit", "-m", commit_message], cwd=repo_path)

            # Get number of changed files
            result = _run_git_command(
                ["git", "diff", "--name-only", "HEAD~1", "HEAD"], cwd=repo_path
            )
            files_changed = (
                len(result.stdout.strip().split("\n")) if result.stdout.strip() else 0
            )

        # Get current commit hash
        result = _run_git_command(["git", "rev-parse", "HEAD"], cwd=repo_path)
        commit_hash = result.stdout.strip()

        # Configure git to use token for push
        repo_url = _construct_repo_url(project_name, use_token=True)
        _run_git_command(
            ["git", "remote", "set-url", "origin", repo_url], cwd=repo_path
        )

        # Push branch to remote
        _run_git_command(["git", "push", "-u", "origin", branch_name], cwd=repo_path)

        # Get timestamp
        result = _run_git_command(["git", "log", "-1", "--format=%cI"], cwd=repo_path)
        pushed_at = result.stdout.strip()

        success_result = {
            "status": "success",
            "message": f"Successfully pushed branch '{branch_name}' to project '{project_name}'",
            "project_name": project_name,
            "branch": branch_name,
            "commit_message": commit_message or "No new commits",
            "commit_hash": commit_hash,
            "pushed_at": pushed_at,
            "files_changed": files_changed,
            "local_path": repo_path,
        }

        logger.info("Push completed: %s", success_result["message"])
        return success_result

    except subprocess.CalledProcessError as e:
        error_msg = f"Failed to push branch '{branch_name}' to project '{project_name}': {e.stderr}"
        logger.error(error_msg)
        raise RuntimeError(error_msg) from e


def _check_glab_installed() -> bool:
    """
    Check if glab CLI is installed and available.

    Returns:
        True if glab is installed, False otherwise
    """
    try:
        result = subprocess.run(
            ["glab", "--version"], capture_output=True, text=True, check=True
        )
        logger.info("glab CLI found: %s", result.stdout.strip())
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        logger.warning("glab CLI not found or not working")
        return False


def _configure_glab_auth() -> None:
    """
    Configure glab CLI authentication using environment variables.

    This function sets up glab with the GitLab instance URL and token
    from environment variables (GITLAB_URI and GITLAB_TOKEN).

    Raises:
        RuntimeError: If required environment variables are not set
    """
    gitlab_token = _get_gitlab_token()
    gitlab_uri = _get_gitlab_instance_base_url()

    if not gitlab_token:
        raise RuntimeError(
            "GITLAB_TOKEN environment variable is not set. "
            "Cannot authenticate glab CLI."
        )

    if not gitlab_uri:
        raise RuntimeError(
            "GITLAB_URI environment variable is not set. Cannot configure glab CLI."
        )

    # Remove trailing slash from GitLab URI
    gitlab_host = gitlab_uri.rstrip("/")

    logger.info("Configuring glab for GitLab instance: %s", gitlab_host)

    try:
        # Configure glab with the token and host using global configuration
        # The --global flag allows configuration outside of a git repository
        subprocess.run(
            [
                "glab",
                "config",
                "set",
                "--global",
                "token",
                gitlab_token,
                "--host",
                gitlab_host,
            ],
            capture_output=True,
            text=True,
            check=True,
        )

        # Set the default GitLab host globally
        subprocess.run(
            ["glab", "config", "set", "--global", "host", gitlab_host],
            capture_output=True,
            text=True,
            check=True,
        )

        logger.info("Successfully configured glab authentication for %s", gitlab_host)

    except subprocess.CalledProcessError as e:
        error_msg = f"Failed to configure glab authentication: {e.stderr}"
        logger.error(error_msg)
        raise RuntimeError(error_msg) from e


def _run_glab_command(
    command: list[str], cwd: Optional[str] = None
) -> subprocess.CompletedProcess:
    """
    Run a glab command and return the result.

    Args:
        command: glab command as list of strings
        cwd: Working directory for the command

    Returns:
        CompletedProcess result

    Raises:
        subprocess.CalledProcessError: If command fails
    """
    try:
        result = subprocess.run(
            command, cwd=cwd, capture_output=True, text=True, check=True
        )
        return result
    except subprocess.CalledProcessError as e:
        logger.error("glab command failed: %s", " ".join(command))
        logger.error("Error: %s", e.stderr)
        raise


@tool
def create_merge_request(
    project_name: str,
    source_branch: str,
    title: str,
    description: str,
    target_branch: str = "dev",
    assignee_id: Optional[str] = None,
    local_path: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Create a merge request in the GitLab repository using glab CLI.

    Args:
        project_name: GitLab project name or URL-encoded path
        source_branch: Branch containing the changes
        target_branch: Branch to merge into
        title: Title for the merge request
        description: Description of the changes
        assignee_id: Optional user ID to assign the merge request to
        local_path: Optional local path to the repository

    Returns:
        Dict containing merge request metadata

    Raises:
        ValueError: If any required parameter is empty
        RuntimeError: If merge request creation fails
    """
    logger.info("Environment variables loaded: %s", os.environ)
    _get_gitlab_instance_base_url()
    if not all([project_name, source_branch, target_branch, title, description]):
        raise ValueError(
            "project_name, source_branch, target_branch, title, and description are required"
        )

    logger.info(
        "Creating merge request from '%s' to '%s' in project '%s' using glab",
        source_branch,
        target_branch,
        project_name,
    )

    # Check if glab is installed
    if not _check_glab_installed():
        raise RuntimeError(
            "glab CLI is not installed. Please install glab CLI to create merge requests."
        )

    # Configure glab authentication
    _configure_glab_auth()

    # Determine local path
    repo_path = _get_default_local_path(project_name)

    if not os.path.exists(repo_path):
        error_msg = f"Repository not found at {repo_path}. Please clone it first."
        logger.error(error_msg)
        raise FileNotFoundError(error_msg)

    try:
        # Build glab command
        glab_command = [
            "glab",
            "mr",
            "create",
            "--title",
            title,
            "--description",
            description,
            "--source-branch",
            source_branch,
            "--target-branch",
            target_branch,
        ]

        # Add assignee if provided
        if assignee_id:
            glab_command.extend(["--assignee", assignee_id])

        # Execute glab command
        _result = _run_glab_command(glab_command, cwd=repo_path)

        # Parse the output to extract merge request information
        # Note: glab output format can vary, currently not parsing the result
        web_url = None
        merge_request_iid = None

        success_result = {
            "status": "success",
            "message": f"Successfully created merge request from '{source_branch}' to '{target_branch}' using glab",
            "project_name": project_name,
            "source_branch": source_branch,
            "target_branch": target_branch,
            "title": title,
            "description": description,
            "merge_request_iid": merge_request_iid,
            "web_url": web_url,
            "assignee_id": assignee_id,
            "created_at": None,  # glab doesn't provide this in create output
            "state": "opened",  # Default state for newly created MR
            "method": "glab_cli",
        }

        logger.info(
            "Merge request created using glab: %s",
            web_url or f"MR !{merge_request_iid}",
        )
        return success_result

    except subprocess.CalledProcessError as e:
        error_msg = f"Failed to create merge request using glab: {e.stderr}"
        logger.error(error_msg)
        raise RuntimeError(error_msg) from e
    except Exception as e:
        error_msg = f"Failed to create merge request from '{source_branch}' to '{target_branch}' using glab: {str(e)}"
        logger.error(error_msg)
        raise RuntimeError(error_msg) from e


@tool
def get_repository_path(project_name: str, local_path: Optional[str] = None) -> str:
    """
    Get the local path to a cloned repository.

    Args:
        project_name: GitLab project name or URL-encoded path
        local_path: Optional custom local path

    Returns:
        Local repository path
    """
    return _get_default_local_path(project_name)


@tool
def cleanup_repository(
    project_name: str, local_path: Optional[str] = None
) -> Dict[str, Any]:
    """
    Clean up a cloned repository by removing its local directory.

    Args:
        project_name: GitLab project name or URL-encoded path
        local_path: Optional custom local path to clean up

    Returns:
        Dict containing cleanup status
    """
    repo_path = _get_default_local_path(project_name)

    if os.path.exists(repo_path):
        logger.info("Cleaning up repository at %s", repo_path)
        shutil.rmtree(repo_path)
        return {
            "status": "success",
            "message": f"Successfully cleaned up repository at {repo_path}",
            "path": repo_path,
        }
    else:
        logger.info("Repository not found at %s, nothing to clean up", repo_path)
        return {
            "status": "success",
            "message": f"No repository found at {repo_path}",
            "path": repo_path,
        }
