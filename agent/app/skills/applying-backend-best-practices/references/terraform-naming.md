# Terraform — Conventions de Nommage et Tagging

## Identifiants Terraform (code HCL)

Toujours en **snake_case**, descriptifs.

```hcl
# Correct
resource "aws_lambda_function" "webhook_handler" { ... }
resource "aws_iam_role" "lambda_exec" { ... }
output "api_gateway_invoke_url" { ... }

# Incorrect
resource "aws_lambda_function" "func1" { ... }      # Non descriptif
resource "aws_iam_role" "myRole" { ... }             # camelCase
```

## Noms de ressources AWS (console)

Prefixe projet avec tirets.

```hcl
resource "aws_lambda_function" "webhook_handler" {
  function_name = "${var.project}-webhook-handler"
}

resource "aws_iam_role" "lambda_exec" {
  name = "${var.project}-lambda-exec-role"
}

resource "aws_cloudwatch_log_group" "lambda" {
  name = "/aws/lambda/${local.lambda_function_name}"
}

resource "aws_secretsmanager_secret" "api_token" {
  name = "${var.project}-api-token"
}
```

## Tagging obligatoire

Via `default_tags` dans le provider :

```hcl
provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = var.project
      Environment = var.environment
      ManagedBy   = "terraform"
    }
  }
}
```

Tags supplementaires par ressource :

```hcl
resource "aws_lambda_function" "webhook_handler" {
  tags = {
    Name     = "${var.project}-webhook-handler"
    Function = "webhook-processing"
  }
}
```

## Resume

| Element | Convention | Exemple |
|---------|-----------|---------|
| Ressource Terraform | snake_case | `aws_lambda_function.webhook_handler` |
| Nom AWS | projet-kebab | `mon-projet-webhook-handler` |
| Variable | snake_case | `lambda_memory_size` |
| Output | snake_case | `lambda_function_arn` |
| Local | snake_case | `lambda_function_name` |
| Log group | /aws/service/nom | `/aws/lambda/mon-projet-handler` |
| Secret | projet-kebab | `mon-projet-api-token` |
| Tag cle | PascalCase | `Project`, `Environment` |
