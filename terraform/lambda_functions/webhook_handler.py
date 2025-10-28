"""
GitLab Webhook Handler Lambda Function

This function receives and processes GitLab webhook events with:
- Signature verification for security
- Payload parsing and validation
- Error handling and retry logic
- Structured logging
"""

import json
import os
import hmac
import logging
import traceback
from typing import Dict, Any, Optional, Tuple
import boto3
from botocore.exceptions import ClientError
import uuid

# Configure logging
logger = logging.getLogger()
log_level = os.environ.get("LOG_LEVEL", "INFO")
logger.setLevel(getattr(logging, log_level))

# AWS clients
secrets_client = boto3.client("secretsmanager")

# Environment variables
WEBHOOK_SECRET_ARN = os.environ.get("GITLAB_WEBHOOK_SECRET_ARN")

# Cache for webhook secret
_webhook_secret_cache: Optional[str] = None


def get_webhook_secret() -> str:
    """
    Retrieve GitLab webhook secret from AWS Secrets Manager.
    Uses caching to minimize API calls.

    Returns:
        str: The webhook secret token

    Raises:
        RuntimeError: If secret cannot be retrieved
    """
    global _webhook_secret_cache

    if _webhook_secret_cache:
        return _webhook_secret_cache

    if not WEBHOOK_SECRET_ARN:
        raise RuntimeError("GITLAB_WEBHOOK_SECRET_ARN environment variable not set")

    try:
        response = secrets_client.get_secret_value(SecretId=WEBHOOK_SECRET_ARN)
        _webhook_secret_cache = response["SecretString"]
        return _webhook_secret_cache
    except ClientError as e:
        logger.error(f"Failed to retrieve webhook secret: {e}")
        raise RuntimeError(f"Failed to retrieve webhook secret: {e}")


def verify_gitlab_signature(payload: str, signature: Optional[str]) -> bool:
    """
    Verify GitLab webhook signature using HMAC-SHA256.

    Args:
        payload: Raw webhook payload as string
        signature: X-Gitlab-Token header value

    Returns:
        bool: True if signature is valid, False otherwise
    """
    if not signature:
        logger.warning("Missing X-Gitlab-Token header")
        return False

    try:
        secret = get_webhook_secret()

        # GitLab uses simple token comparison (not HMAC)
        # For GitLab, X-Gitlab-Token should match the secret token exactly
        is_valid = hmac.compare_digest(signature, secret)

        if not is_valid:
            logger.warning("Webhook signature verification failed")

        return is_valid
    except Exception as e:
        logger.error(f"Error during signature verification: {e}")
        return False


def invoke_cloud_engineer_agent(issue_payload: dict) -> dict:
    """
    Invoke the Bedrock agent runtime to process an issue event.

    Args:
        issue_payload: The dict containing issue information suitable for the Agent

    Returns:
        Dict with the parsed agent response
    """
    agent_runtime_arn = os.environ["AGENT_ARN"]
    if not agent_runtime_arn:
        raise RuntimeError("AGENT_ARN environment variable not set")

    client = boto3.client("bedrock-agentcore")

    # Use a unique session ID of 33+ chars (include issue id if possible, else uuid)
    issue_id = issue_payload.get("issue_id")
    base_id = str(issue_id) if issue_id is not None else str(uuid.uuid4())
    base_id = base_id.replace("-", "")
    runtime_session_id = (base_id + str(uuid.uuid4()).replace("-", ""))[:35]

    # Convert payload to JSON string
    payload = json.dumps(issue_payload)

    response = client.invoke_agent_runtime(
        agentRuntimeArn=agent_runtime_arn,
        runtimeSessionId=runtime_session_id,
        payload=payload,
        qualifier="DEFAULT",
    )

    # Read and parse the response stream
    response_body = response["response"].read()
    response_data = json.loads(response_body)

    logger.info(f"Agent Response: {response_data}")

    return response_data


def parse_gitlab_event(headers: Dict[str, str]) -> Tuple[Optional[str], Optional[str]]:
    """
    Extract GitLab event type and object kind from headers.

    Args:
        headers: API Gateway event headers

    Returns:
        Tuple of (event_type, object_kind)
    """
    # GitLab sends event type in X-Gitlab-Event header
    event_type = headers.get("X-Gitlab-Event") or headers.get("x-gitlab-event")

    # Some events also include object kind
    object_kind = headers.get("X-Gitlab-Object-Kind") or headers.get(
        "x-gitlab-object-kind"
    )

    return event_type, object_kind


def validate_webhook_payload(
    payload: Dict[str, Any], event_type: str
) -> Tuple[bool, Optional[str]]:
    """
    Validate GitLab webhook payload structure.

    Args:
        payload: Parsed JSON payload
        event_type: GitLab event type

    Returns:
        Tuple of (is_valid, error_message)
    """
    # Common required fields for most GitLab events
    if not isinstance(payload, dict):
        return False, "Payload must be a JSON object"

    # Validate based on event type
    if event_type == "Push Hook":
        required_fields = ["object_kind", "ref", "project"]
        for field in required_fields:
            if field not in payload:
                return False, f"Missing required field: {field}"

    elif event_type == "Merge Request Hook":
        required_fields = ["object_kind", "object_attributes", "project"]
        for field in required_fields:
            if field not in payload:
                return False, f"Missing required field: {field}"

    elif event_type == "Issue Hook":
        required_fields = ["object_kind", "object_attributes", "project"]
        for field in required_fields:
            if field not in payload:
                return False, f"Missing required field: {field}"

    elif event_type == "Pipeline Hook":
        required_fields = ["object_kind", "object_attributes", "project"]
        for field in required_fields:
            if field not in payload:
                return False, f"Missing required field: {field}"

    # Add more event types as needed

    return True, None


def process_webhook_event(
    payload: Dict[str, Any], event_type: str, object_kind: Optional[str]
) -> Dict[str, Any]:
    """
    Process the GitLab webhook event.

    Args:
        payload: Validated webhook payload
        event_type: GitLab event type
        object_kind: Object kind (if available)

    Returns:
        Dict containing processing results
    """
    logger.info(f"Processing GitLab event: {event_type}")

    result = {
        "event_type": event_type,
        "object_kind": object_kind,
        "processed": True,
        "timestamp": payload.get("created_at") or payload.get("timestamp"),
    }

    # Extract relevant information based on event type
    if event_type == "Push Hook":
        result["ref"] = payload.get("ref")
        result["project_id"] = payload.get("project", {}).get("id")
        result["commits_count"] = len(payload.get("commits", []))
        logger.info(f"Push to {result['ref']} with {result['commits_count']} commits")

    elif event_type == "Merge Request Hook":
        attrs = payload.get("object_attributes", {})
        result["merge_request_id"] = attrs.get("id")
        result["action"] = attrs.get("action")
        result["state"] = attrs.get("state")
        result["source_branch"] = attrs.get("source_branch")
        result["target_branch"] = attrs.get("target_branch")
        logger.info(
            f"Merge Request {result['action']}: {result['source_branch']} -> {result['target_branch']}"
        )

    elif event_type == "Issue Hook":
        attrs = payload.get("object_attributes", {})
        print(f"{attrs=}")
        result["issue_id"] = attrs.get("iid")
        result["description"] = attrs.get("description")
        result["action"] = attrs.get("action")
        result["state"] = attrs.get("state")
        result["title"] = attrs.get("title")
        print(f"Triggering agent with {result=}")
        invoke_cloud_engineer_agent(result)

    elif event_type == "Pipeline Hook":
        attrs = payload.get("object_attributes", {})
        result["pipeline_id"] = attrs.get("id")
        result["status"] = attrs.get("status")
        result["ref"] = attrs.get("ref")
        logger.info(f"Pipeline {result['status']} on {result['ref']}")

    # Add custom processing logic here
    # For example: trigger CI/CD, update databases, send notifications, etc.

    return result


def create_response(status_code: int, body: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create API Gateway response object.

    Args:
        status_code: HTTP status code
        body: Response body dictionary

    Returns:
        API Gateway response object
    """
    return {
        "statusCode": status_code,
        "headers": {"Content-Type": "application/json", "X-Powered-By": "AWS Lambda"},
        "body": json.dumps(body),
    }


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Lambda handler for GitLab webhooks.

    Args:
        event: API Gateway event
        context: Lambda context

    Returns:
        API Gateway response
    """
    print(f"{event=}")
    request_id = context.aws_request_id
    logger.info(f"Processing webhook request: {request_id}")

    try:
        # Extract headers (handle case-insensitive headers from API Gateway)
        headers = event.get("headers", {})

        # Get GitLab signature token
        gitlab_token = headers.get("X-Gitlab-Token") or headers.get("x-gitlab-token")

        # Get request body
        body = event.get("body", "")
        if not body:
            logger.warning("Empty request body")
            return create_response(
                400, {"error": "Bad Request", "message": "Empty request body"}
            )

        # Verify webhook signature
        if not verify_gitlab_signature(body, gitlab_token):
            logger.error("Webhook signature verification failed")
            return create_response(
                401, {"error": "Unauthorized", "message": "Invalid webhook signature"}
            )

        # Parse GitLab event information
        event_type, object_kind = parse_gitlab_event(headers)

        if not event_type:
            logger.warning("Missing X-Gitlab-Event header")
            return create_response(
                400,
                {"error": "Bad Request", "message": "Missing X-Gitlab-Event header"},
            )

        # Parse JSON payload
        try:
            payload = json.loads(body)
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON payload: {e}")
            return create_response(
                400, {"error": "Bad Request", "message": "Invalid JSON payload"}
            )

        # Validate payload structure
        is_valid, error_message = validate_webhook_payload(payload, event_type)
        if not is_valid:
            logger.error(f"Invalid payload: {error_message}")
            return create_response(
                400, {"error": "Bad Request", "message": error_message}
            )

        # Process the webhook event
        result = process_webhook_event(payload, event_type, object_kind)

        logger.info(f"Successfully processed webhook: {request_id}")

        return create_response(
            200,
            {
                "success": True,
                "message": "Webhook processed successfully",
                "request_id": request_id,
                "result": result,
            },
        )

    except Exception as e:
        # Comprehensive error handling
        error_details = {
            "error": "Internal Server Error",
            "message": str(e),
            "request_id": request_id,
            "type": type(e).__name__,
        }

        logger.error(f"Unexpected error processing webhook: {error_details}")
        logger.error(traceback.format_exc())

        # For 5xx errors, API Gateway will automatically retry
        return create_response(500, error_details)
