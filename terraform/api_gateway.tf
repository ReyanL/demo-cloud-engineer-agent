# API Gateway REST API
resource "aws_api_gateway_rest_api" "webhook" {
  name        = "gitlab-webhook-api"
  description = "API Gateway for GitLab webhook handler"

  endpoint_configuration {
    types = ["REGIONAL"]
  }

  binary_media_types = ["application/octet-stream"]

  tags = {
    Name = "gitlab-webhook-api"
  }
}

# API Gateway resource: /webhook
resource "aws_api_gateway_resource" "webhook" {
  rest_api_id = aws_api_gateway_rest_api.webhook.id
  parent_id   = aws_api_gateway_rest_api.webhook.root_resource_id
  path_part   = "webhook"
}

# POST method for /webhook
resource "aws_api_gateway_method" "webhook_post" {
  rest_api_id   = aws_api_gateway_rest_api.webhook.id
  resource_id   = aws_api_gateway_resource.webhook.id
  http_method   = "POST"
  authorization = "NONE"
}

# Integration with Lambda
resource "aws_api_gateway_integration" "webhook_lambda" {
  rest_api_id             = aws_api_gateway_rest_api.webhook.id
  resource_id             = aws_api_gateway_resource.webhook.id
  http_method             = aws_api_gateway_method.webhook_post.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.webhook_handler.invoke_arn
}

# Note: With AWS_PROXY integration, Lambda handles the full response format
# No need for method_response or integration_response resources

# Lambda permission for API Gateway
resource "aws_lambda_permission" "api_gateway" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.webhook_handler.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.webhook.execution_arn}/*/*"
}

# API Gateway deployment
resource "aws_api_gateway_deployment" "webhook" {

  rest_api_id = aws_api_gateway_rest_api.webhook.id

  lifecycle {
    create_before_destroy = true
  }
}

# API Gateway stage
resource "aws_api_gateway_stage" "webhook" {
  deployment_id = aws_api_gateway_deployment.webhook.id
  rest_api_id   = aws_api_gateway_rest_api.webhook.id
  stage_name    = "prod"

  xray_tracing_enabled = true

  access_log_settings {
    destination_arn = aws_cloudwatch_log_group.api_gateway.arn
    format = jsonencode({
      requestId               = "$context.requestId"
      ip                      = "$context.identity.sourceIp"
      requestTime             = "$context.requestTime"
      httpMethod              = "$context.httpMethod"
      resourcePath            = "$context.resourcePath"
      status                  = "$context.status"
      protocol                = "$context.protocol"
      responseLength          = "$context.responseLength"
      errorMessage            = "$context.error.message"
      integrationErrorMessage = "$context.integrationErrorMessage"
    })
  }

  tags = {
    Name = "gitlab-webhook-stage"
  }
}

# Method settings for detailed logging
resource "aws_api_gateway_method_settings" "webhook" {
  rest_api_id = aws_api_gateway_rest_api.webhook.id
  stage_name  = aws_api_gateway_stage.webhook.stage_name
  method_path = "*/*"

  settings {
    metrics_enabled    = true
    logging_level      = "INFO"
    data_trace_enabled = true
  }
}

# CloudWatch Log Group for API Gateway
resource "aws_cloudwatch_log_group" "api_gateway" {
  name              = "/aws/apigateway/gitlab-webhook-api"
  retention_in_days = var.log_retention_days

  tags = {
    Name = "gitlab-webhook-api-gateway-logs"
  }
}

# IAM role for API Gateway CloudWatch logging
resource "aws_iam_role" "api_gateway_cloudwatch" {
  name = "gitlab-webhook-api-gateway-cloudwatch-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "apigateway.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    Name = "gitlab-webhook-api-gateway-cloudwatch-role"
  }
}

# Attach the managed policy for API Gateway CloudWatch logging
resource "aws_iam_role_policy_attachment" "api_gateway_cloudwatch" {
  role       = aws_iam_role.api_gateway_cloudwatch.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonAPIGatewayPushToCloudWatchLogs"
}

# Set the CloudWatch role for API Gateway account settings
resource "aws_api_gateway_account" "main" {
  cloudwatch_role_arn = aws_iam_role.api_gateway_cloudwatch.arn
}

