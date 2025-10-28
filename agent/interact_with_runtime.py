"""
Interact with the runtime agent to get a response.
"""
import boto3
from boto3.session import Session
import json
import os

aws_profile = os.environ.get("AWS_PROFILE")
session = Session(profile_name=aws_profile) if aws_profile else Session()
client = session.client("bedrock-agentcore")
payload = json.dumps(
    {
        "event_type": "Issue Hook",
        "object_kind": None,
        "processed": True,
        "timestamp": None,
        "issue_id": "16875",
        "description": "# Change Website Background Color from White to Dark Blue\n\n## Context\n\nThe website currently uses a white background (`#FFFFFF`) which creates poor contrast with our dark-themed UI elements. Users have reported difficulty reading content due to the harsh white background.\n\nWe need to change the background color to dark blue (`#1a365d`) to improve readability and align with our brand colors. This change affects the `body` element in `styles.css` and will be applied to all pages.\n\n## Todo\n\n- [ ] Update `body` background-color in `website/styles.css` from `#FFFFFF` to `#1a765d`\n- [ ] Verify text color contrast ratio meets WCAG AA standards (4.5:1 minimum)\n- [ ] Test on `index.html` and `error.html` pages\n- [ ] Confirm no layout shifts or visual regressions\n\n## Definition of Done\n\n- Background color changed to `#1a365d` in `styles.css`\n- Text remains readable with contrast ratio ≥ 4.5:1\n- Change visible on both `index.html` and `error.html`\n- No broken layouts or overlapping elements\n- Change deployed to production",
        "action": "update",
        "state": "opened",
        "title": "64367",
    }
)

agent_runtime_arn = os.environ.get("AGENT_ARN")
if not agent_runtime_arn:
    raise RuntimeError("AGENT_ARN environment variable is required")

response = client.invoke_agent_runtime(
    agentRuntimeArn=agent_runtime_arn,
    runtimeSessionId="dfmeoagmreaklgrahrgqgeafremoigrmtesogmtrskhmtkrlshmt",  # Must be 33+ chars
    payload=payload,
    qualifier="DEFAULT",  # Optional
)
response_body = response["response"].read()
response_data = json.loads(response_body)
print("Agent Response:", response_data)
