terraform {
  backend "s3" {
    bucket       = var.state_bucket_name
    key          = "cloud-engineer-agent"
    region       = var.aws_region
    use_lockfile = true
  }
}