"""MCPServerConfig class and functions to create MCP clients."""

import os
from typing import Dict, List, Optional, Any
from strands.tools.mcp import MCPClient
from mcp import stdio_client, StdioServerParameters


class MCPServerConfig:
    """Configuration class for MCP servers."""

    def __init__(
        self,
        name: str,
        command: str,
        args: List[str],
        env: Optional[Dict[str, str]] = None,
        disabled: bool = False,
        auto_approve: Optional[List[str]] = None,
        default_tools: Optional[List[str]] = None,
    ):
        """Initialize MCP server configuration.

        Args:
            name: Name of the MCP server
            command: Command to run the server
            args: Arguments for the command
            env: Environment variables for the server
            disabled: Whether the server is disabled
            auto_approve: List of auto-approved actions
            default_tools: Default tools to select from this server
        """
        self.name = name
        self.command = command
        self.args = args
        self.env = env or {}
        self.disabled = disabled
        self.auto_approve = auto_approve or []
        self.default_tools = default_tools or []


# MCP Server Configurations
MCP_SERVERS: Dict[str, MCPServerConfig] = {
    "aws_terraform": MCPServerConfig(
        name="AWS Terraform",
        command="uvx",
        args=["awslabs.terraform-mcp-server@latest"],
        env={"FASTMCP_LOG_LEVEL": "ERROR"},
        disabled=False,
        auto_approve=[],
        default_tools=["SearchAwsProviderDocs", "RunCheckovScan"],
    ),
    "aws_documentation": MCPServerConfig(
        name="AWS Documentation",
        command="uvx",
        args=["awslabs.aws-documentation-mcp-server@latest"],
        env={
            "FASTMCP_LOG_LEVEL": "ERROR",
            "AWS_DOCUMENTATION_PARTITION": "aws",
        },
        default_tools=["search_documentation", "read_documentation"],
    ),
}


def create_mcp_client(server_config: MCPServerConfig) -> MCPClient:
    """Create an MCP client from server configuration.

    Args:
        server_config: Configuration for the MCP server

    Returns:
        Configured MCPClient instance
    """
    return MCPClient(
        lambda: stdio_client(
            StdioServerParameters(
                command=server_config.command,
                args=server_config.args,
                env=server_config.env,
                disabled=server_config.disabled,
                autoApprove=server_config.auto_approve,
            )
        )
    )


def get_mcp_tools(
    server_name: str, selected_tool_names: Optional[List[str]] = None
) -> List[Any]:
    """Get tools from a specific MCP server.

    Args:
        server_name: Name of the MCP server (key from MCP_SERVERS)
        selected_tool_names: List of tool names to select. If None, returns all tools.

    Returns:
        List of selected MCP tools

    Raises:
        KeyError: If server_name is not found in MCP_SERVERS
    """
    if server_name not in MCP_SERVERS:
        raise KeyError(
            f"MCP server '{server_name}' not found. Available servers: {list(MCP_SERVERS.keys())}"
        )

    server_config = MCP_SERVERS[server_name]
    mcp_client = create_mcp_client(server_config)
    mcp_client.start()

    all_tools = mcp_client.list_tools_sync()

    if selected_tool_names is None:
        return all_tools

    return [tool for tool in all_tools if tool.tool_name in selected_tool_names]


def get_mcp_tools_with_defaults(
    server_name: str, selected_tool_names: Optional[List[str]] = None
) -> List[Any]:
    """Get tools from a specific MCP server, using default tools if none specified.

    Args:
        server_name: Name of the MCP server (key from MCP_SERVERS)
        selected_tool_names: List of tool names to select. If None, uses default tools.

    Returns:
        List of selected MCP tools
    """
    if selected_tool_names is None:
        server_config = MCP_SERVERS[server_name]
        selected_tool_names = server_config.default_tools

    return get_mcp_tools(server_name, selected_tool_names)
