# IAM role for Lambda execution
resource "aws_iam_role" "lambda_exec" {
  name = "gitlab-webhook-lambda-exec-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    Name = "gitlab-webhook-lambda-exec-role"
  }
}

# IAM policy for Lambda execution
resource "aws_iam_role_policy" "lambda_exec_policy" {
  name = "gitlab-webhook-lambda-exec-policy"
  role = aws_iam_role.lambda_exec.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "arn:aws:logs:*:*:*"
      },
      {
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue"
        ]
        Resource = aws_secretsmanager_secret.gitlab_webhook_token.arn
      },
      {
        Effect = "Allow"
        Action = [
          "bedrock-agentcore:InvokeAgent",
          "bedrock-agentcore:InvokeAgentStream",
          "bedrock-agentcore:GetAgentRuntime",
          "bedrock-agentcore:InvokeAgentRuntime",
          "bedrock-agentcore:DescribeAgentRuntime"
        ]
        Resource = "arn:aws:bedrock-agentcore:*:*:runtime/*"
      }
    ]
  })
}

# Attach AWS managed policy for Lambda basic execution
resource "aws_iam_role_policy_attachment" "lambda_basic" {
  role       = aws_iam_role.lambda_exec.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# Attach AWS X-Ray write permissions for tracing
resource "aws_iam_role_policy_attachment" "lambda_xray" {
  role       = aws_iam_role.lambda_exec.name
  policy_arn = "arn:aws:iam::aws:policy/AWSXRayDaemonWriteAccess"
}
