# IAM role for Agent Runtime
resource "awscc_iam_role" "agent_runtime_role" {
  role_name = "bedrock-agent-runtime-role"
  assume_role_policy_document = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "bedrock-agentcore.amazonaws.com"
        }
      }
    ]
  })

  tags = [{
    key   = "Project"
    value = "cloud-engineer-agent"
  }]
}

# IAM policy for Agent Runtime
resource "awscc_iam_role_policy" "agent_runtime_policy" {
  role_name   = awscc_iam_role.agent_runtime_role.role_name
  policy_name = "bedrock-agent-runtime-policy"
  policy_document = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "ECRImageAccess"
        Effect = "Allow"
        Action = [
          "ecr:BatchGetImage",
          "ecr:GetDownloadUrlForLayer"
        ]
        Resource = [
          "arn:aws:ecr:${var.aws_region}:${data.aws_caller_identity.current.account_id}:repository/*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "logs:DescribeLogStreams",
          "logs:CreateLogGroup"
        ]
        Resource = [
          "arn:aws:logs:${var.aws_region}:${data.aws_caller_identity.current.account_id}:log-group:/aws/bedrock-agentcore/runtimes/*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "logs:DescribeLogGroups"
        ]
        Resource = [
          "arn:aws:logs:${var.aws_region}:${data.aws_caller_identity.current.account_id}:log-group:*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = [
          "arn:aws:logs:${var.aws_region}:${data.aws_caller_identity.current.account_id}:log-group:/aws/bedrock-agentcore/runtimes/*:log-stream:*"
        ]
      },
      {
        Sid    = "ECRTokenAccess"
        Effect = "Allow"
        Action = [
          "ecr:GetAuthorizationToken"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "xray:PutTraceSegments",
          "xray:PutTelemetryRecords",
          "xray:GetSamplingRules",
          "xray:GetSamplingTargets"
        ]
        Resource = ["*"]
      },
      {
        Effect   = "Allow"
        Action   = "cloudwatch:PutMetricData"
        Resource = "*"
        Condition = {
          StringEquals = {
            "cloudwatch:namespace" = "bedrock-agentcore"
          }
        }
      },
      {
        Sid    = "BedrockAgentCoreRuntime"
        Effect = "Allow"
        Action = [
          "bedrock-agentcore:InvokeAgentRuntime"
        ]
        Resource = [
          "arn:aws:bedrock-agentcore:${var.aws_region}:${data.aws_caller_identity.current.account_id}:runtime/*"
        ]
      },
      {
        Sid    = "BedrockAgentCoreMemoryCreateMemory"
        Effect = "Allow"
        Action = [
          "bedrock-agentcore:CreateMemory"
        ]
        Resource = "*"
      },
      {
        Sid    = "BedrockAgentCoreMemory"
        Effect = "Allow"
        Action = [
          "bedrock-agentcore:CreateEvent",
          "bedrock-agentcore:GetEvent",
          "bedrock-agentcore:GetMemory",
          "bedrock-agentcore:GetMemoryRecord",
          "bedrock-agentcore:ListActors",
          "bedrock-agentcore:ListEvents",
          "bedrock-agentcore:ListMemoryRecords",
          "bedrock-agentcore:ListSessions",
          "bedrock-agentcore:DeleteEvent",
          "bedrock-agentcore:DeleteMemoryRecord",
          "bedrock-agentcore:RetrieveMemoryRecords"
        ]
        Resource = [
          "arn:aws:bedrock-agentcore:${var.aws_region}:${data.aws_caller_identity.current.account_id}:memory/*"
        ]
      },
      {
        Sid    = "BedrockAgentCoreIdentityGetResourceApiKey"
        Effect = "Allow"
        Action = [
          "bedrock-agentcore:GetResourceApiKey"
        ]
        Resource = [
          "arn:aws:bedrock-agentcore:${var.aws_region}:${data.aws_caller_identity.current.account_id}:token-vault/default",
          "arn:aws:bedrock-agentcore:${var.aws_region}:${data.aws_caller_identity.current.account_id}:token-vault/default/apikeycredentialprovider/*",
          "arn:aws:bedrock-agentcore:${var.aws_region}:${data.aws_caller_identity.current.account_id}:workload-identity-directory/default",
          "arn:aws:bedrock-agentcore:${var.aws_region}:${data.aws_caller_identity.current.account_id}:workload-identity-directory/default/workload-identity/cloud_engineer_agent-*"
        ]
      },
      {
        Sid    = "BedrockAgentCoreIdentityGetCredentialProviderClientSecret"
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue"
        ]
        Resource = [
          "arn:aws:secretsmanager:${var.aws_region}:${data.aws_caller_identity.current.account_id}:secret:bedrock-agentcore-identity!default/oauth2/*"
        ]
      },
      {
        Sid    = "LangfuseCredentialsAccess"
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue"
        ]
        Resource = [
          data.aws_secretsmanager_secret.langfuse_credentials.arn
        ]
      },
      {
        Sid    = "BedrockAgentCoreIdentityGetResourceOauth2Token"
        Effect = "Allow"
        Action = [
          "bedrock-agentcore:GetResourceOauth2Token"
        ]
        Resource = [
          "arn:aws:bedrock-agentcore:${var.aws_region}:${data.aws_caller_identity.current.account_id}:token-vault/default",
          "arn:aws:bedrock-agentcore:${var.aws_region}:${data.aws_caller_identity.current.account_id}:token-vault/default/oauth2credentialprovider/*",
          "arn:aws:bedrock-agentcore:${var.aws_region}:${data.aws_caller_identity.current.account_id}:workload-identity-directory/default",
          "arn:aws:bedrock-agentcore:${var.aws_region}:${data.aws_caller_identity.current.account_id}:workload-identity-directory/default/workload-identity/cloud_engineer_agent-*"
        ]
      },
      {
        Sid    = "BedrockAgentCoreIdentityGetWorkloadAccessToken"
        Effect = "Allow"
        Action = [
          "bedrock-agentcore:GetWorkloadAccessToken",
          "bedrock-agentcore:GetWorkloadAccessTokenForJWT",
          "bedrock-agentcore:GetWorkloadAccessTokenForUserId"
        ]
        Resource = [
          "arn:aws:bedrock-agentcore:${var.aws_region}:${data.aws_caller_identity.current.account_id}:workload-identity-directory/default",
          "arn:aws:bedrock-agentcore:${var.aws_region}:${data.aws_caller_identity.current.account_id}:workload-identity-directory/default/workload-identity/cloud_engineer_agent-*"
        ]
      },
      {
        Sid    = "BedrockModelInvocation"
        Effect = "Allow"
        Action = [
          "bedrock:InvokeModel",
          "bedrock:InvokeModelWithResponseStream",
          "bedrock:ApplyGuardrail"
        ]
        Resource = [
          "arn:aws:bedrock:*::foundation-model/*",
          "arn:aws:bedrock:*:*:inference-profile/*",
          "arn:aws:bedrock:${var.aws_region}:${data.aws_caller_identity.current.account_id}:*"
        ]
      },
      {
        Sid    = "BedrockAgentCoreCodeInterpreter"
        Effect = "Allow"
        Action = [
          "bedrock-agentcore:CreateCodeInterpreter",
          "bedrock-agentcore:StartCodeInterpreterSession",
          "bedrock-agentcore:InvokeCodeInterpreter",
          "bedrock-agentcore:StopCodeInterpreterSession",
          "bedrock-agentcore:DeleteCodeInterpreter",
          "bedrock-agentcore:ListCodeInterpreters",
          "bedrock-agentcore:GetCodeInterpreter",
          "bedrock-agentcore:GetCodeInterpreterSession",
          "bedrock-agentcore:ListCodeInterpreterSessions"
        ]
        Resource = [
          "arn:aws:bedrock-agentcore:${var.aws_region}:aws:code-interpreter/*",
          "arn:aws:bedrock-agentcore:${var.aws_region}:${data.aws_caller_identity.current.account_id}:code-interpreter/*",
          "arn:aws:bedrock-agentcore:${var.aws_region}:${data.aws_caller_identity.current.account_id}:code-interpreter-custom/*"
        ]
      },
      {
        Sid    = "TerraformStateS3Access"
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject"
        ]
        Resource = [
          "arn:aws:s3:::${var.state_bucket_name}/*"
        ]
      },
      {
        Sid    = "TerraformStateS3BucketAccess"
        Effect = "Allow"
        Action = [
          "s3:ListBucket"
        ]
        Resource = [
          "arn:aws:s3:::${var.state_bucket_name}"
        ]
      },
      {
        Sid    = "TerraformReadPermissions"
        Effect = "Allow"
        Action = [
          "lambda:GetFunction",
          "lambda:GetFunctionConfiguration",
          "lambda:ListFunctions",
          "lambda:GetPolicy",
          "lambda:ListTags",
          "apigateway:GET",
          "s3:GetBucketLocation",
          "s3:GetBucketPolicy",
          "s3:GetBucketAcl",
          "s3:GetBucketCORS",
          "s3:GetBucketWebsite",
          "s3:GetBucketVersioning",
          "s3:GetBucketTagging",
          "s3:GetEncryptionConfiguration",
          "s3:GetBucketPublicAccessBlock",
          "s3:GetBucketLogging",
          "s3:GetBucketObjectLockConfiguration",
          "s3:GetBucketRequestPayment",
          "s3:GetAccelerateConfiguration",
          "s3:GetLifecycleConfiguration",
          "s3:GetReplicationConfiguration",
          "s3:ListBucket",
          "s3:ListAllMyBuckets",
          "dynamodb:DescribeTable",
          "dynamodb:ListTables",
          "dynamodb:ListTagsOfResource",
          "dynamodb:DescribeTimeToLive",
          "dynamodb:DescribeContinuousBackups",
          "cognito-idp:DescribeUserPool",
          "cognito-idp:DescribeUserPoolClient",
          "cognito-idp:ListUserPools",
          "cognito-idp:ListUserPoolClients",
          "cognito-idp:ListTagsForResource",
          "iam:GetRole",
          "iam:GetRolePolicy",
          "iam:ListRolePolicies",
          "iam:ListAttachedRolePolicies",
          "iam:GetPolicy",
          "iam:GetPolicyVersion",
          "iam:ListPolicies",
          "iam:ListRoles",
          "logs:DescribeLogGroups",
          "logs:ListTagsLogGroup",
          "ecr:DescribeRepositories",
          "ecr:ListTagsForResource",
          "cloudfront:GetDistribution",
          "cloudfront:ListDistributions",
          "cloudfront:ListTagsForResource",
          "route53:GetHostedZone",
          "route53:ListHostedZones",
          "route53:ListResourceRecordSets",
          "route53:ListTagsForResource",
          "secretsmanager:DescribeSecret",
          "secretsmanager:ListSecrets",
          "secretsmanager:GetResourcePolicy",
          "*" #TODO: implement all permissions
        ]
        Resource = "*"
      }
    ]
  })
}


# create ecr repo
resource "aws_ecr_repository" "cloud_engineer_agent" {
  name = local.agent_name
}

# get authorization credentials to push to ecr
data "aws_ecr_authorization_token" "token" {}

# configure docker provider
provider "docker" {
  registry_auth {
    address  = data.aws_ecr_authorization_token.token.proxy_endpoint
    username = data.aws_ecr_authorization_token.token.user_name
    password = data.aws_ecr_authorization_token.token.password
  }
}

# build docker image
resource "docker_image" "cloud_engineer_agent" {
  name = "${replace(data.aws_ecr_authorization_token.token.proxy_endpoint, "https://", "")}/${local.agent_name}:latest"
  build {
    context = "../agent"
  }
  platform = "linux/arm64"

  # Force rebuild when source files change
  triggers = {
    dir_sha1 = sha1(join("", [
      for f in fileset("../agent", "**") : filesha1("../agent/${f}")
    ]))
  }
}

# push image to ecr repo
resource "docker_registry_image" "cloud_engineer_agent" {
  name = docker_image.cloud_engineer_agent.name
}

# Agent Runtime
resource "awscc_bedrockagentcore_runtime" "cloud_engineer_agent" {
  agent_runtime_name = "cloud_engineer_agent"
  description        = "Cloud Engineer Agent"
  role_arn           = awscc_iam_role.agent_runtime_role.arn

  agent_runtime_artifact = {
    container_configuration = {
      container_uri = "${replace(data.aws_ecr_authorization_token.token.proxy_endpoint, "https://", "")}/${local.agent_name}:latest"
    }
  }
  environment_variables = {
    "DISABLE_ADOT_OBSERVABILITY"  = "true"
    "OTEL_EXPORTER_OTLP_ENDPOINT" = var.langfuse_otlp_endpoint
    "OTEL_EXPORTER_OTLP_PROTOCOL" = "http/protobuf"
    "OTEL_EXPORTER_OTLP_HEADERS"  = local.langfuse_auth_header
    "USER_ID"                     = var.user_id
    "BYPASS_TOOL_CONSENT"         = "true"
  }

  network_configuration = {
    network_mode = "PUBLIC"
  }


  tags = {
    key   = "Project"
    value = local.agent_name
  }
  # TODO: add missing parameter observability:enabled: false & change timeout to 10 minutes

  lifecycle {
    replace_triggered_by = [
      docker_image.cloud_engineer_agent
    ]
  }
}
