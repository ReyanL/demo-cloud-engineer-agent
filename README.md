## Cloud Engineer Agent

A reference implementation of an AWS Bedrock AgentCore runtime paired with a GitLab-driven workflow. It deploys infrastructure with Terraform, builds and pushes a containerized agent to Amazon ECR, provisions an AgentCore runtime, and exposes a Lambda + API Gateway webhook for GitLab events.

### Architecture Overview

The system follows a two-stage workflow:

**Stage 1: Issue to Agent Invocation**
![Cloud Engineer Agent Workflow - Stage 1](diagrams/ai-agent-workflow-1.png)

**Stage 2: Agent Processing and CI/CD Trigger**
![Cloud Engineer Agent Workflow - Stage 2](diagrams/ai-agent-workflow-2.png)

### Key Features
- Bedrock AgentCore runtime with container artifact from `agent/`
- GitLab webhook ingestion via Lambda and API Gateway
- Safe, public-ready configuration: no hardcoded account IDs, ARNs, or org URLs
- Environment-driven Python utilities for local interaction and Git operations

## Prerequisites
- AWS account and credentials (role or profile)
- Terraform >= 1.6
- Docker for building the agent image


## Configuration

### Terraform Variables
These important variables should be provided via `*.tfvars` or `-var` flags:
- `aws_region` (default: `us-west-2`)
- `state_bucket_name` (S3 bucket for remote state)
- `gitlab_url` (default: `gitlab.example.com`)
- `gitlab_audience` (default: `https://gitlab.example.com`)
- `gitlab_project_path` (default: `your-group/your-project`)
- `user_id` (default: `user@example.com`)
- `langfuse_otlp_endpoint` (default: empty to disable)

See `terraform/variables.tf` for the complete list and defaults.

### Environment Variables
Copy `agent/app/.env_example` to `.env` and set your values:
- `GITLAB_TOKEN`, `GITLAB_URI`, `GITLAB_REPO_BASE_URL`
- `LANGFUSE_PUBLIC_KEY`, `LANGFUSE_SECRET_KEY`, `LANGFUSE_HOST`
- `USER_ID`, `AGENT_ARN` (runtime ARN output after deploy)
- Optional: `AWS_PROFILE` for local utilities

Note: `.env`, `.env.*`, and `*.tfvars` are gitignored.

## Deploy

1. Initialize Terraform backend
   ```bash
   terraform -chdir=terraform init \
     -backend-config="bucket=<your-state-bucket>" \
     -backend-config="key=cloud-engineer-agent" \
     -backend-config="region=<your-region>"
   ```

2. Plan and apply
   ```bash
   terraform -chdir=terraform apply \
     -var="state_bucket_name=<your-state-bucket>" \
     -var="aws_region=<your-region>" \
     -var="gitlab_url=gitlab.example.com" \
     -var="gitlab_project_path=your-group/your-project"
   ```

3. Capture outputs (not shown here) and set `AGENT_ARN` accordingly in your environment.

## Local Utilities

### Interact with Agent Runtime
`agent/interact_with_runtime.py` uses `AWS_PROFILE` (optional) and requires `AGENT_ARN` from your deployment:
```bash
export AWS_PROFILE=your-profile
export AGENT_ARN=arn:aws:bedrock-agentcore:...:runtime/...
python agent/interact_with_runtime.py
```

### Git Tools
`agent/app/git_tools.py` reads `GITLAB_URI`, `GITLAB_TOKEN`, and optionally `GITLAB_REPO_BASE_URL`. Defaults are neutral to avoid leaking org details.

## Project Structure
- `agent/` – Dockerized agent runtime code and tooling
- `terraform/` – Infrastructure as code (ECR, AgentCore, API Gateway, Lambda, IAM)

## Contributing
Contributions are welcome. Please avoid committing secrets, ARNs, or account-specific identifiers. Use variables and environment files instead.

## License
MIT
