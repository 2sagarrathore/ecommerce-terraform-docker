output "frontend_url" {
  description = "Public URL of the frontend. Open this in a browser."
  value       = "http://${aws_instance.app.public_ip}"
}

output "frontend_url_port_3000" {
  description = "The frontend is also published on its native port 3000."
  value       = "http://${aws_instance.app.public_ip}:3000"
}

output "instance_public_ip" {
  description = "Public IPv4 address of the EC2 instance."
  value       = aws_instance.app.public_ip
}

output "instance_public_dns" {
  description = "Public DNS name of the EC2 instance."
  value       = aws_instance.app.public_dns
}

output "instance_id" {
  description = "EC2 instance ID."
  value       = aws_instance.app.id
}

output "vpc_id" {
  description = "ID of the VPC created for this stack."
  value       = aws_vpc.main.id
}

output "public_subnet_id" {
  description = "ID of the public subnet hosting the instance."
  value       = aws_subnet.public.id
}

output "security_group_id" {
  description = "ID of the application security group."
  value       = aws_security_group.app.id
}

output "health_endpoints" {
  description = "Aggregated health endpoint of the frontend, which reports all four backends."
  value = {
    frontend_health = "http://${aws_instance.app.public_ip}/health"
    all_services    = "http://${aws_instance.app.public_ip}/api/status"
  }
}

output "ssh_command" {
  description = "SSH command for the instance, when a key pair and SSH CIDR were configured."
  value       = var.key_pair_name == null ? "No key pair configured; set key_pair_name and allowed_ssh_cidr to enable SSH." : "ssh -i ~/.ssh/${var.key_pair_name}.pem ubuntu@${aws_instance.app.public_ip}"
}

output "verify_backends_command" {
  description = "Command that prints the on-instance smoke-test result written by user-data."
  value       = "ssh ubuntu@${aws_instance.app.public_ip} 'cat deployment-status.txt && docker ps'"
}
