output "webhook_url" {
  description = "GitLab webhook URL endpoint"
  value       = "${aws_api_gateway_stage.webhook.invoke_url}/webhook"
}

output "api_gateway_id" {
  description = "API Gateway REST API ID"
  value       = aws_api_gateway_rest_api.webhook.id
}

output "lambda_function_name" {
  description = "Lambda function name"
  value       = aws_lambda_function.webhook_handler.function_name
}

output "lambda_function_arn" {
  description = "Lambda function ARN"
  value       = aws_lambda_function.webhook_handler.arn
}

output "secret_arn" {
  description = "Secrets Manager ARN for webhook token"
  value       = aws_secretsmanager_secret.gitlab_webhook_token.arn
}

output "cloudwatch_log_group" {
  description = "CloudWatch log group for Lambda function"
  value       = aws_cloudwatch_log_group.lambda.name
}

output "gitlab_oidc_provider_arn" {
  description = "ARN of the GitLab OIDC provider"
  value       = aws_iam_openid_connect_provider.gitlab.arn
}

output "gitlab_oidc_role_arn" {
  description = "ARN of the GitLab OIDC IAM role - Use this as AWS_ROLE_ARN in GitLab CI/CD variables"
  value       = aws_iam_role.gitlab_oidc_role.arn
}

output "gitlab_audience" {
  description = "Audience value for GitLab OIDC - Use this as AUDIENCE in GitLab CI/CD variables"
  value       = var.gitlab_audience
}

output "agentcore_runtime_arn" {
  description = "ARN of the AgentCore runtime"
  value       = aws_bedrockagentcore_agent_runtime.cloud_engineer_agent.agent_runtime_arn
}
