# ====================================
# GitLab OIDC Provider Configuration
# ====================================
# This configuration sets up OIDC authentication between GitLab and AWS
# allowing GitLab CI/CD pipelines to assume AWS IAM roles without static credentials

# ====================================
# OIDC Identity Provider
# ====================================
resource "aws_iam_openid_connect_provider" "gitlab" {
  url = "https://${var.gitlab_url}"

  client_id_list = [
    var.gitlab_audience,
  ]

  # GitLab's OIDC thumbprint
  # This thumbprint is for GitLab.com and most GitLab instances
  # If using self-hosted GitLab, you may need to update this
  thumbprint_list = [
    "b3dd7606d2b5a8b4a13771dbecc9ee1cecafa38a", # GitLab OIDC thumbprint
  ]

  tags = {
    Name        = "GitLab OIDC Provider"
    Environment = "production"
    ManagedBy   = "Terraform"
  }
}

# ====================================
# IAM Role for GitLab CI/CD Pipeline
# ====================================
resource "aws_iam_role" "gitlab_oidc_role" {
  name        = "GitLabCICDRole"
  description = "IAM role for GitLab CI/CD pipeline with OIDC authentication"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Federated = aws_iam_openid_connect_provider.gitlab.arn
        }
        Action = "sts:AssumeRoleWithWebIdentity"
        Condition = {
          StringEquals = {
            "${var.gitlab_url}:aud" = var.gitlab_audience
          }
          StringLike = {
            # Allow specific project and branches
            # Format: project_path:<group>/<project>:ref_type:branch:ref:<branch>
            "${var.gitlab_url}:sub" = "project_path:${var.gitlab_project_path}:ref_type:branch:ref:*"
          }
        }
      }
    ]
  })

  max_session_duration = 3600 # 1 hour

  tags = {
    Name = "GitLab OIDC Role for ${var.project}"
  }
}

# ====================================
# IAM Policy for Terraform Operations
# ====================================
resource "aws_iam_policy" "gitlab_terraform_policy" {
  name        = "GitLabTerraformPolicy"
  description = "Policy allowing GitLab CI/CD to manage AWS resources via Terraform"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      # S3 Backend Access
      {
        Sid    = "TerraformStateAccess"
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject",
          "s3:ListBucket"
        ]
        Resource = [
          "arn:aws:s3:::demo-cloud-engineer-agent-state", # Backend state bucket
          "arn:aws:s3:::demo-cloud-engineer-agent-state/*"
        ]
      },
      # Lambda Management
      {
        Sid    = "LambdaManagement"
        Effect = "Allow"
        Action = [
          "lambda:CreateFunction",
          "lambda:DeleteFunction",
          "lambda:GetFunction",
          "lambda:GetFunctionConfiguration",
          "lambda:UpdateFunctionCode",
          "lambda:UpdateFunctionConfiguration",
          "lambda:ListFunctions",
          "lambda:ListVersionsByFunction",
          "lambda:PublishVersion",
          "lambda:CreateAlias",
          "lambda:DeleteAlias",
          "lambda:UpdateAlias",
          "lambda:GetAlias",
          "lambda:AddPermission",
          "lambda:RemovePermission",
          "lambda:GetPolicy",
          "lambda:TagResource",
          "lambda:UntagResource",
          "lambda:ListTags"
        ]
        Resource = "*"
      },
      # API Gateway Management
      {
        Sid    = "APIGatewayManagement"
        Effect = "Allow"
        Action = [
          "apigateway:*"
        ]
        Resource = "*"
      },
      # S3 Management (for website hosting, etc.)
      {
        Sid    = "S3Management"
        Effect = "Allow"
        Action = [
          "s3:CreateBucket",
          "s3:DeleteBucket",
          "s3:GetBucketLocation",
          "s3:GetBucketPolicy",
          "s3:PutBucketPolicy",
          "s3:DeleteBucketPolicy",
          "s3:GetBucketAcl",
          "s3:PutBucketAcl",
          "s3:GetBucketCORS",
          "s3:PutBucketCORS",
          "s3:GetBucketWebsite",
          "s3:PutBucketWebsite",
          "s3:DeleteBucketWebsite",
          "s3:GetBucketVersioning",
          "s3:PutBucketVersioning",
          "s3:GetBucketTagging",
          "s3:PutBucketTagging",
          "s3:GetEncryptionConfiguration",
          "s3:PutEncryptionConfiguration",
          "s3:GetBucketPublicAccessBlock",
          "s3:PutBucketPublicAccessBlock",
          "s3:ListBucket",
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject"
        ]
        Resource = [
          "arn:aws:s3:::*",
          "arn:aws:s3:::*/*"
        ]
      },
      # DynamoDB Management
      {
        Sid    = "DynamoDBManagement"
        Effect = "Allow"
        Action = [
          "dynamodb:CreateTable",
          "dynamodb:DeleteTable",
          "dynamodb:DescribeTable",
          "dynamodb:UpdateTable",
          "dynamodb:ListTables",
          "dynamodb:TagResource",
          "dynamodb:UntagResource",
          "dynamodb:DescribeTimeToLive",
          "dynamodb:UpdateTimeToLive",
          "dynamodb:DescribeContinuousBackups",
          "dynamodb:UpdateContinuousBackups"
        ]
        Resource = "*"
      },
      # Cognito Management
      {
        Sid    = "CognitoManagement"
        Effect = "Allow"
        Action = [
          "cognito-idp:CreateUserPool",
          "cognito-idp:DeleteUserPool",
          "cognito-idp:DescribeUserPool",
          "cognito-idp:UpdateUserPool",
          "cognito-idp:CreateUserPoolClient",
          "cognito-idp:DeleteUserPoolClient",
          "cognito-idp:DescribeUserPoolClient",
          "cognito-idp:UpdateUserPoolClient",
          "cognito-idp:ListUserPools",
          "cognito-idp:ListUserPoolClients",
          "cognito-idp:TagResource",
          "cognito-idp:UntagResource"
        ]
        Resource = "*"
      },
      # IAM Management (for Lambda execution roles, etc.)
      {
        Sid    = "IAMManagement"
        Effect = "Allow"
        Action = [
          "iam:CreateRole",
          "iam:DeleteRole",
          "iam:GetRole",
          "iam:UpdateRole",
          "iam:ListRoles",
          "iam:CreatePolicy",
          "iam:DeletePolicy",
          "iam:GetPolicy",
          "iam:GetPolicyVersion",
          "iam:ListPolicies",
          "iam:ListPolicyVersions",
          "iam:AttachRolePolicy",
          "iam:DetachRolePolicy",
          "iam:PutRolePolicy",
          "iam:DeleteRolePolicy",
          "iam:GetRolePolicy",
          "iam:ListRolePolicies",
          "iam:ListAttachedRolePolicies",
          "iam:PassRole",
          "iam:TagRole",
          "iam:UntagRole",
          "iam:TagPolicy",
          "iam:UntagPolicy"
        ]
        Resource = "*"
      },
      # CloudWatch Logs
      {
        Sid    = "CloudWatchLogsManagement"
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:DeleteLogGroup",
          "logs:DescribeLogGroups",
          "logs:PutRetentionPolicy",
          "logs:TagLogGroup",
          "logs:UntagLogGroup"
        ]
        Resource = "*"
      },
      # CloudFront (if needed)
      {
        Sid    = "CloudFrontManagement"
        Effect = "Allow"
        Action = [
          "cloudfront:CreateDistribution",
          "cloudfront:DeleteDistribution",
          "cloudfront:GetDistribution",
          "cloudfront:UpdateDistribution",
          "cloudfront:ListDistributions",
          "cloudfront:TagResource",
          "cloudfront:UntagResource"
        ]
        Resource = "*"
      },
      # Route53 (if needed for DNS)
      {
        Sid    = "Route53Management"
        Effect = "Allow"
        Action = [
          "route53:CreateHostedZone",
          "route53:DeleteHostedZone",
          "route53:GetHostedZone",
          "route53:ListHostedZones",
          "route53:ChangeResourceRecordSets",
          "route53:GetChange",
          "route53:ListResourceRecordSets"
        ]
        Resource = "*"
      }
    ]
  })

  tags = {
    Name = "GitLab Terraform Policy for ${var.project}"
  }
}

# ====================================
# Attach Policies to Role
# ====================================
resource "aws_iam_role_policy_attachment" "gitlab_terraform" {
  role       = aws_iam_role.gitlab_oidc_role.name
  policy_arn = aws_iam_policy.gitlab_terraform_policy.arn
}

# Attach AWS AdministratorAccess managed policy for full admin access
resource "aws_iam_role_policy_attachment" "gitlab_admin_access" {
  role       = aws_iam_role.gitlab_oidc_role.name
  policy_arn = "arn:aws:iam::aws:policy/AdministratorAccess"
}
