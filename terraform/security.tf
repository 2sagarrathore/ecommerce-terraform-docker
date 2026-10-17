# ---------------------------------------------------------------------------
# Security group for the application host.
#   * Public inbound: 80 and 3000  -> frontend
#   * Internal inbound: 3001-3004  -> backend services, restricted to members
#     of this same security group so they are not exposed to the internet.
#   * SSH: only created when var.allowed_ssh_cidr is set.
# ---------------------------------------------------------------------------

resource "aws_security_group" "app" {
  name        = "${var.project_name}-app-sg"
  description = "Public access to the frontend and internal access between services"
  vpc_id      = aws_vpc.main.id

  tags = {
    Name = "${var.project_name}-app-sg"
  }

  lifecycle {
    create_before_destroy = true
  }
}

# --- Public frontend access -------------------------------------------------

resource "aws_vpc_security_group_ingress_rule" "frontend_http" {
  security_group_id = aws_security_group.app.id
  description       = "HTTP to the frontend container"
  cidr_ipv4         = var.allowed_http_cidr
  from_port         = 80
  to_port           = 80
  ip_protocol       = "tcp"
}

resource "aws_vpc_security_group_ingress_rule" "frontend_3000" {
  security_group_id = aws_security_group.app.id
  description       = "Frontend on its native port 3000"
  cidr_ipv4         = var.allowed_http_cidr
  from_port         = 3000
  to_port           = 3000
  ip_protocol       = "tcp"
}

# --- Internal service-to-service traffic ------------------------------------
# One rule per backend port, each referencing this security group itself, so
# only workloads inside the group can reach 3001-3004.

locals {
  backend_services = {
    user     = 3001
    products = 3002
    orders   = 3003
    cart     = 3004
  }
}

resource "aws_vpc_security_group_ingress_rule" "backends_internal" {
  for_each = local.backend_services

  security_group_id            = aws_security_group.app.id
  description                  = "Internal access to the ${each.key} service"
  referenced_security_group_id = aws_security_group.app.id
  from_port                    = each.value
  to_port                      = each.value
  ip_protocol                  = "tcp"
}

# --- Optional SSH -----------------------------------------------------------

resource "aws_vpc_security_group_ingress_rule" "ssh" {
  count = var.allowed_ssh_cidr == null ? 0 : 1

  security_group_id = aws_security_group.app.id
  description       = "SSH administration"
  cidr_ipv4         = var.allowed_ssh_cidr
  from_port         = 22
  to_port           = 22
  ip_protocol       = "tcp"
}

# --- Egress -----------------------------------------------------------------
# Outbound is required to install Docker and pull the images from Docker Hub.

resource "aws_vpc_security_group_egress_rule" "all" {
  security_group_id = aws_security_group.app.id
  description       = "Allow all outbound traffic"
  cidr_ipv4         = "0.0.0.0/0"
  ip_protocol       = "-1"
}
