"""
Interact with the runtime agent to get a response.

Usage:
    export AWS_PROFILE=your-profile  # optional
    export AGENT_ARN=arn:aws:bedrock-agentcore:...:runtime/...
    python agent/interact_with_runtime.py
"""
import boto3
from boto3.session import Session
import json
import os

aws_profile = os.environ.get("AWS_PROFILE")
session = Session(profile_name=aws_profile) if aws_profile else Session()
client = session.client("bedrock-agentcore")

# Example payload — replace with your actual issue content
payload = json.dumps(
    {
        "event_type": "Issue Hook",
        "object_kind": None,
        "processed": True,
        "timestamp": None,
        "issue_id": "1",
        "description": "# Example Issue\n\n## Context\n\nDescribe the background and motivation.\n\n## Todo\n\n- [ ] First task\n- [ ] Second task\n\n## Definition of Done\n\n- Acceptance criteria here",
        "action": "update",
        "state": "opened",
        "title": "Example issue title",
    }
)

agent_runtime_arn = os.environ.get("AGENT_ARN")
if not agent_runtime_arn:
    raise RuntimeError("AGENT_ARN environment variable is required")

response = client.invoke_agent_runtime(
    agentRuntimeArn=agent_runtime_arn,
    runtimeSessionId="example-session-id-must-be-at-least-33-chars",
    payload=payload,
    qualifier="DEFAULT",
)
response_body = response["response"].read()
response_data = json.loads(response_body)
print("Agent Response:", response_data)
