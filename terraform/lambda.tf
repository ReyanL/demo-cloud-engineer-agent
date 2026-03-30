# Archive Lambda function code
data "archive_file" "webhook_handler" {
  type        = "zip"
  source_file = "${path.module}/lambda_functions/webhook_handler.py"
  output_path = "${path.module}/.terraform/lambda_packages/webhook_handler.zip"
}

# Lambda function for webhook handling
resource "aws_lambda_function" "webhook_handler" {
  filename         = data.archive_file.webhook_handler.output_path
  function_name    = "gitlab-webhook-handler"
  role             = aws_iam_role.lambda_exec.arn
  handler          = "webhook_handler.lambda_handler"
  source_code_hash = data.archive_file.webhook_handler.output_base64sha256
  runtime          = "python3.12"
  timeout          = var.lambda_timeout
  memory_size      = var.lambda_memory_size

  environment {
    variables = {
      GITLAB_WEBHOOK_SECRET_ARN = aws_secretsmanager_secret.gitlab_webhook_token.arn
      LOG_LEVEL                 = "INFO"
      AGENT_ARN                 = aws_bedrockagentcore_agent_runtime.cloud_engineer_agent.agent_runtime_arn
      AGENT_BOT_USERNAME        = var.agent_bot_username
    }
  }

  tags = {
    Name = "gitlab-webhook-handler"
  }
}

# CloudWatch Log Group for Lambda
resource "aws_cloudwatch_log_group" "lambda" {
  name              = "/aws/lambda/${aws_lambda_function.webhook_handler.function_name}"
  retention_in_days = var.log_retention_days

  tags = {
    Name = "gitlab-webhook-lambda-logs"
  }
}
