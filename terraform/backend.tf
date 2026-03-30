terraform {
  backend "s3" {
    # Configure via -backend-config flags or backend.hcl file:
    #   terraform init \
    #     -backend-config="bucket=<your-state-bucket>" \
    #     -backend-config="key=cloud-engineer-agent" \
    #     -backend-config="region=<your-region>"
    bucket       = "<your-state-bucket>"
    key          = "cloud-engineer-agent"
    region       = "us-west-2"
    use_lockfile = true
  }
}