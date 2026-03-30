terraform {
  required_version = ">= 1.12"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
    docker = {
      source  = "kreuzwerker/docker"
      version = "3.0.2"
    }

  }
}

provider "aws" {
  region  = "us-west-2"
  default_tags {
    tags = {
      Project = var.project
    }
  }

}