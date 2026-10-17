variable "aws_region" {
  description = "AWS region to deploy the stack into."
  type        = string
  default     = "ap-south-1"
}

variable "project_name" {
  description = "Name prefix applied to every resource."
  type        = string
  default     = "shopkart"
}

variable "environment" {
  description = "Environment name used in tags."
  type        = string
  default     = "dev"
}

variable "vpc_cidr" {
  description = "CIDR block for the VPC."
  type        = string
  default     = "10.20.0.0/16"
}

variable "public_subnet_cidr" {
  description = "CIDR block for the public subnet that hosts the EC2 instance."
  type        = string
  default     = "10.20.1.0/24"
}

variable "instance_type" {
  description = "EC2 instance type. t3.micro is enough for five small containers."
  type        = string
  default     = "t3.micro"
}

variable "root_volume_size" {
  description = "Size of the EC2 root EBS volume, in GiB."
  type        = number
  default     = 16
}

variable "allowed_http_cidr" {
  description = "CIDR allowed to reach the frontend on ports 80 and 3000. Narrow this for a real deployment."
  type        = string
  default     = "0.0.0.0/0"
}

variable "allowed_ssh_cidr" {
  description = "CIDR allowed to reach SSH. Leave null to create no SSH rule at all."
  type        = string
  default     = null
}

variable "key_pair_name" {
  description = "Existing EC2 key pair name for SSH access. Leave null to launch without a key pair."
  type        = string
  default     = null
}

variable "dockerhub_username" {
  description = "Docker Hub account that hosts the five service images."
  type        = string
}

variable "image_tag" {
  description = "Tag of the images to pull from Docker Hub."
  type        = string
  default     = "1.0.0"
}

variable "dockerhub_token" {
  description = <<-EOT
    Optional Docker Hub access token, only needed if the images are private.
    Note: user-data is readable from the instance metadata service, so prefer
    public images and leave this null.
  EOT
  type        = string
  default     = null
  sensitive   = true
}

variable "frontend_host_port" {
  description = "Host port that serves the frontend. Port 3000 is published alongside it as well."
  type        = number
  default     = 80
}
