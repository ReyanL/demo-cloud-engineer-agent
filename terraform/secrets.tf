# Secrets Manager secret for GitLab webhook token
resource "aws_secretsmanager_secret" "gitlab_webhook_token" {
  name                    = "${var.project}-webhook-token"
  description             = "GitLab webhook secret token for signature verification"
  recovery_window_in_days = 7

  tags = {
    Name = "${var.project}-webhook-token"
  }
}

# Secret version - only create if webhook secret is provided
resource "aws_secretsmanager_secret_version" "gitlab_webhook_token" {
  count         = var.gitlab_webhook_secret != "" ? 1 : 0
  secret_id     = aws_secretsmanager_secret.gitlab_webhook_token.id
  secret_string = var.gitlab_webhook_secret
}

# Data source to read existing Langfuse credentials from Secrets Manager
data "aws_secretsmanager_secret" "langfuse_credentials" {
  name = "langfuse/api-key"
}

data "aws_secretsmanager_secret_version" "langfuse_credentials" {
  secret_id = data.aws_secretsmanager_secret.langfuse_credentials.id
}

