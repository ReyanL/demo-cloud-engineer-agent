locals {
  region     = data.aws_region.current.region
  account_id = data.aws_caller_identity.current.account_id
  agent_name = "cloud-engineer-agent"

  # Parse Langfuse credentials from Secrets Manager
  langfuse_credentials = jsondecode(data.aws_secretsmanager_secret_version.langfuse_credentials.secret_string)
  langfuse_public_key  = local.langfuse_credentials["LANGFUSE_PUBLIC_KEY"]
  langfuse_secret_key  = local.langfuse_credentials["LANGFUSE_SECRET_KEY"]

  # Compute Langfuse auth header for OTLP
  langfuse_auth_header = "Authorization=Basic ${base64encode("${local.langfuse_public_key}:${local.langfuse_secret_key}")}"
}
