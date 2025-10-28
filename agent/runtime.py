"""Implement a feature from a GitLab issue."""

import base64
import os
from bedrock_agentcore.runtime import BedrockAgentCoreApp
from app.cloud_engineer_agent import CloudEngineerAgent
from strands.telemetry import StrandsTelemetry

app = BedrockAgentCoreApp()


def initialize_telemetry():
    """
    Initialize Strands telemetry with OTLP exporter.

    When deployed via AgentCore, OTEL env vars (OTEL_EXPORTER_OTLP_ENDPOINT,
    OTEL_EXPORTER_OTLP_HEADERS) are already configured via Terraform.

    For local development, this function will construct them from individual
    Langfuse credentials if they're not already set.
    """
    # Only set OTEL env vars if not already configured (local development)
    if "OTEL_EXPORTER_OTLP_HEADERS" not in os.environ:
        if "LANGFUSE_PUBLIC_KEY" in os.environ and "LANGFUSE_SECRET_KEY" in os.environ:
            langfuse_auth_token = base64.b64encode(
                f"{os.environ['LANGFUSE_PUBLIC_KEY']}:{os.environ['LANGFUSE_SECRET_KEY']}".encode()
            ).decode()
            os.environ["OTEL_EXPORTER_OTLP_HEADERS"] = (
                f"Authorization=Basic {langfuse_auth_token}"
            )

    if "OTEL_EXPORTER_OTLP_ENDPOINT" not in os.environ:
        if "LANGFUSE_HOST" in os.environ:
            os.environ["OTEL_EXPORTER_OTLP_ENDPOINT"] = (
                os.environ["LANGFUSE_HOST"] + "/api/public/otel"
            )

    strands_telemetry = StrandsTelemetry()
    strands_telemetry.setup_otlp_exporter()


@app.entrypoint
def invoke(payload, context=None):
    """
    Invoke the cloud engineer agent to implement a feature.

    Args:
        payload: Dict containing issue_id and description
        context: AgentCore runtime context (optional)

    Returns:
        Implementation response from the agent
    """
    # Initialize telemetry for this invocation
    initialize_telemetry()

    # Extract session ID from context
    session_id = context.session_id if context else "unknown"

    # Log session info if context is provided
    if context:
        print(f"Session ID: {context.session_id}")
        print(f"Agent Runtime ID: {getattr(context, 'agent_runtime_id', 'N/A')}")

    print(f"Agent {payload=}")

    # Create agent - it will automatically create traces for the invocation
    agent = CloudEngineerAgent(session_id=session_id)

    response = agent.implement_feature(
        issue_id=payload["issue_id"],
        description=payload["description"],
    )

    return response  # response should be json serializable


if __name__ == "__main__":
    app.run()
