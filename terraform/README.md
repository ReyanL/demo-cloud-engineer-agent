# GitLab Webhook Handler

Serverless GitLab webhook handler on AWS with signature verification, payload validation, and monitoring.

## Architecture

- **API Gateway**: REST API endpoint for webhooks
- **Lambda**: Processes events with signature verification
- **Secrets Manager**: Stores webhook secret token
- **CloudWatch**: Logging and X-Ray tracing

## Quick Start

```bash
# Initialize
cd terraform
terraform init

# Set your webhook secret (default: see variables.tf)
# Optional: Create terraform.tfvars with custom values

# Deploy
terraform apply

# Get webhook URL
terraform output webhook_url
```

## Configure GitLab

1. Go to your GitLab project → **Settings → Webhooks**
2. Enter webhook URL from terraform output
3. Enter secret token (must match value in AWS Secrets Manager)
4. Select events to trigger
5. Test the webhook

## Configuration

### Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `aws_region` | `us-west-2` | AWS region |
| `project` | `demo-cloud-engineer-agent` | Project name |
| `gitlab_webhook_secret` | (see variables.tf) | Webhook secret token |
| `lambda_timeout` | `30` | Lambda timeout (seconds) |
| `lambda_memory_size` | `256` | Lambda memory (MB) |
| `log_retention_days` | `7` | Log retention (days) |

### Outputs

- `webhook_url` - GitLab webhook endpoint
- `lambda_function_name` - Lambda function name
- `secret_arn` - Secrets Manager ARN
- `cloudwatch_log_group` - Log group name

## Resources

- [GitLab Webhooks Documentation](https://docs.gitlab.com/ee/user/project/integrations/webhooks.html)
- [AWS Lambda Best Practices](https://docs.aws.amazon.com/lambda/latest/dg/best-practices.html)

<!-- BEGIN_TF_DOCS -->
## Requirements

| Name | Version |
|------|---------|
| <a name="requirement_terraform"></a> [terraform](#requirement\_terraform) | >= 1.12 |
| <a name="requirement_aws"></a> [aws](#requirement\_aws) | ~> 6.0 |

## Providers

| Name | Version |
|------|---------|
| <a name="provider_archive"></a> [archive](#provider\_archive) | 2.7.1 |
| <a name="provider_aws"></a> [aws](#provider\_aws) | 6.14.1 |

## Modules

No modules.

## Resources

| Name | Type |
|------|------|
| [aws_api_gateway_account.main](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/api_gateway_account) | resource |
| [aws_api_gateway_deployment.webhook](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/api_gateway_deployment) | resource |
| [aws_api_gateway_integration.webhook_lambda](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/api_gateway_integration) | resource |
| [aws_api_gateway_method.webhook_post](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/api_gateway_method) | resource |
| [aws_api_gateway_method_settings.webhook](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/api_gateway_method_settings) | resource |
| [aws_api_gateway_resource.webhook](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/api_gateway_resource) | resource |
| [aws_api_gateway_rest_api.webhook](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/api_gateway_rest_api) | resource |
| [aws_api_gateway_stage.webhook](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/api_gateway_stage) | resource |
| [aws_cloudwatch_log_group.api_gateway](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/cloudwatch_log_group) | resource |
| [aws_cloudwatch_log_group.lambda](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/cloudwatch_log_group) | resource |
| [aws_iam_role.api_gateway_cloudwatch](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role) | resource |
| [aws_iam_role.lambda_exec](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role) | resource |
| [aws_iam_role_policy.lambda_exec_policy](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role_policy) | resource |
| [aws_iam_role_policy_attachment.api_gateway_cloudwatch](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role_policy_attachment) | resource |
| [aws_iam_role_policy_attachment.lambda_basic](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role_policy_attachment) | resource |
| [aws_iam_role_policy_attachment.lambda_xray](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role_policy_attachment) | resource |
| [aws_lambda_function.webhook_handler](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/lambda_function) | resource |
| [aws_lambda_permission.api_gateway](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/lambda_permission) | resource |
| [aws_secretsmanager_secret.gitlab_webhook_token](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/secretsmanager_secret) | resource |
| [aws_secretsmanager_secret_version.gitlab_webhook_token](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/secretsmanager_secret_version) | resource |
| [archive_file.webhook_handler](https://registry.terraform.io/providers/hashicorp/archive/latest/docs/data-sources/file) | data source |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_aws_region"></a> [aws\_region](#input\_aws\_region) | AWS region for resources | `string` | `"us-west-2"` | no |
| <a name="input_gitlab_webhook_secret"></a> [gitlab\_webhook\_secret](#input\_gitlab\_webhook\_secret) | GitLab webhook secret token for signature verification | `string` | n/a | yes |
| <a name="input_lambda_memory_size"></a> [lambda\_memory\_size](#input\_lambda\_memory\_size) | Lambda function memory size in MB | `number` | `256` | no |
| <a name="input_lambda_timeout"></a> [lambda\_timeout](#input\_lambda\_timeout) | Lambda function timeout in seconds | `number` | `30` | no |
| <a name="input_log_retention_days"></a> [log\_retention\_days](#input\_log\_retention\_days) | CloudWatch logs retention in days | `number` | `7` | no |
| <a name="input_project"></a> [project](#input\_project) | Project name | `string` | `"demo-cloud-engineer-agent"` | no |

## Outputs

| Name | Description |
|------|-------------|
| <a name="output_api_gateway_id"></a> [api\_gateway\_id](#output\_api\_gateway\_id) | API Gateway REST API ID |
| <a name="output_cloudwatch_log_group"></a> [cloudwatch\_log\_group](#output\_cloudwatch\_log\_group) | CloudWatch log group for Lambda function |
| <a name="output_lambda_function_arn"></a> [lambda\_function\_arn](#output\_lambda\_function\_arn) | Lambda function ARN |
| <a name="output_lambda_function_name"></a> [lambda\_function\_name](#output\_lambda\_function\_name) | Lambda function name |
| <a name="output_secret_arn"></a> [secret\_arn](#output\_secret\_arn) | Secrets Manager ARN for webhook token |
| <a name="output_webhook_url"></a> [webhook\_url](#output\_webhook\_url) | GitLab webhook URL endpoint |
<!-- END_TF_DOCS -->