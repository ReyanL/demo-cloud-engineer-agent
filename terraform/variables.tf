variable "aws_region" {
  description = "AWS region for resources"
  type        = string
  default     = "us-west-2"
}

variable "project" {
  description = "Project name"
  type        = string
  default     = "cloud-engineer-agent"
}

variable "gitlab_webhook_secret" {
  description = "GitLab webhook secret token for signature verification"
  type        = string
  sensitive   = true
}

variable "lambda_timeout" {
  description = "Lambda function timeout in seconds"
  type        = number
  default     = 30
}

variable "lambda_memory_size" {
  description = "Lambda function memory size in MB"
  type        = number
  default     = 256
}

variable "log_retention_days" {
  description = "CloudWatch logs retention in days"
  type        = number
  default     = 7
}

# Variables for OIDC configuration
variable "gitlab_url" {
  description = "GitLab instance URL (without https://)"
  type        = string
  default     = "gitlab.example.com"
}

variable "gitlab_audience" {
  description = "Audience value for OIDC token validation"
  type        = string
  default     = "https://gitlab.example.com"
}

variable "gitlab_project_path" {
  description = "GitLab project path (e.g., 'group/project')"
  type        = string
  default     = "your-group/your-project"
}

variable "allowed_branches" {
  description = "List of branches allowed to assume the role"
  type        = list(string)
  default     = ["main", "dev", "feat/*", "fix/*"] # Restrict to specific branches
}

variable "user_id" {
  description = "User ID for Langfuse tracking"
  type        = string
  default     = "user@example.com"
}

# New variables for generic configuration
variable "state_bucket_name" {
  description = "S3 bucket name for Terraform state"
  type        = string
}

variable "langfuse_otlp_endpoint" {
  description = "OTLP endpoint for Langfuse/OpenTelemetry (set empty to disable)"
  type        = string
  default     = ""
}

variable "agent_bot_username" {
  description = "GitLab bot username that triggers the cloud engineer agent when assigned to issues"
  type        = string
  default     = "your-gitlab-bot-username"
}
