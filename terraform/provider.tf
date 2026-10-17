provider "aws" {
  region = var.aws_region

  # Every resource created by this stack carries these tags, which makes the
  # whole deployment easy to find (and to clean up) in the AWS console.
  default_tags {
    tags = {
      Project     = var.project_name
      Environment = var.environment
      ManagedBy   = "Terraform"
    }
  }
}
