# ---------------------------------------------------------------------------
# Ubuntu 22.04 EC2 instance that runs all five containers.
# ---------------------------------------------------------------------------

data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"] # Canonical

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

resource "aws_instance" "app" {
  ami                         = data.aws_ami.ubuntu.id
  instance_type               = var.instance_type
  subnet_id                   = aws_subnet.public.id
  vpc_security_group_ids      = [aws_security_group.app.id]
  associate_public_ip_address = true
  key_name                    = var.key_pair_name

  user_data_replace_on_change = true
  user_data = templatefile("${path.module}/user_data.sh.tftpl", {
    project_name       = var.project_name
    dockerhub_username = var.dockerhub_username
    image_tag          = var.image_tag
    dockerhub_token    = var.dockerhub_token == null ? "" : var.dockerhub_token
    frontend_host_port = var.frontend_host_port
  })

  root_block_device {
    volume_size = var.root_volume_size
    volume_type = "gp3"
    encrypted   = true
  }

  metadata_options {
    http_endpoint = "enabled"
    http_tokens   = "required" # IMDSv2 only
  }

  tags = {
    Name = "${var.project_name}-app-host"
    Role = "docker-host"
  }
}
