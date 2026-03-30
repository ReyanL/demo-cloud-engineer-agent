# Securite AWS (Well-Architected Framework)

## IAM — Moindre privilege

```hcl
# Correct — permissions specifiques
resource "aws_iam_role_policy" "lambda_policy" {
  role = aws_iam_role.lambda_exec.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid      = "ReadSecrets"
        Effect   = "Allow"
        Action   = ["secretsmanager:GetSecretValue"]
        Resource = [aws_secretsmanager_secret.api_token.arn]
      },
      {
        Sid      = "WriteLogs"
        Effect   = "Allow"
        Action   = ["logs:CreateLogStream", "logs:PutLogEvents"]
        Resource = ["${aws_cloudwatch_log_group.lambda.arn}:*"]
      }
    ]
  })
}

# Incorrect — trop permissif
resource "aws_iam_role_policy" "bad" {
  policy = jsonencode({
    Statement = [{
      Effect   = "Allow"
      Action   = ["secretsmanager:*"]
      Resource = ["*"]
    }]
  })
}
```

## Conditions IAM

```hcl
{
  Sid       = "AllowAssumeRoleFromGitLab"
  Effect    = "Allow"
  Action    = "sts:AssumeRoleWithWebIdentity"
  Principal = { Federated = aws_iam_openid_connect_provider.gitlab.arn }
  Condition = {
    StringEquals = { "gitlab.example.com:aud" = var.gitlab_audience }
    StringLike   = { "gitlab.example.com:sub" = "project_path:${var.gitlab_project_path}:*" }
  }
}
```

## Chiffrement

```hcl
resource "aws_kms_key" "main" {
  description             = "${var.project} encryption key"
  deletion_window_in_days = 30
  enable_key_rotation     = true
}

# S3 avec SSE-KMS
resource "aws_s3_bucket_server_side_encryption_configuration" "state" {
  bucket = aws_s3_bucket.terraform_state.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm     = "aws:kms"
      kms_master_key_id = aws_kms_key.main.arn
    }
    bucket_key_enabled = true
  }
}

# Lambda env vars chiffrees
resource "aws_lambda_function" "handler" {
  kms_key_arn = aws_kms_key.main.arn
}
```

## Secrets Management

```hcl
resource "aws_secretsmanager_secret" "api_token" {
  name        = "${var.project}-api-token"
  description = "Token API pour le service externe"
  kms_key_id  = aws_kms_key.main.arn
}

resource "aws_secretsmanager_secret_version" "api_token" {
  secret_id     = aws_secretsmanager_secret.api_token.id
  secret_string = var.api_token  # Variable sensitive
}
```

```python
import boto3

secrets_client = boto3.client("secretsmanager")

def get_secret(secret_arn):
    return secrets_client.get_secret_value(SecretId=secret_arn)["SecretString"]
```

## Security Groups

```hcl
resource "aws_security_group" "lambda" {
  name_prefix = "${var.project}-lambda-"
  vpc_id      = aws_vpc.main.id

  egress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Sortie HTTPS vers les services AWS"
  }
}
```

## Pillier Securite — Checklist Well-Architected

1. **Identite** : Roles IAM, pas de cles d'acces, MFA pour les humains
2. **Detection** : CloudTrail, Config, GuardDuty actives
3. **Protection reseau** : VPC, Security Groups, WAF pour APIs publiques
4. **Protection donnees** : Chiffrement repos + transit, classification
5. **Reponse incidents** : Alarmes, DLQ, procedures documentees
