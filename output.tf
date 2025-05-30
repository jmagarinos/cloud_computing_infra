# -----------------------------
# Output: Website URL
# -----------------------------
output "website_url" {
  value       = "http://${aws_s3_bucket.website.bucket}.s3-website-${var.aws_region}.amazonaws.com"
  description = "URL del sitio web estático en S3"
}

output "rds_endpoint" {
  value       = aws_db_instance.postgres.endpoint
  description = "RDS PostgreSQL endpoint"
}

output "private_subnet_ids" {
  value       = [aws_subnet.private_a.id, aws_subnet.private_b.id]
  description = "Private subnet IDs"
}

output "vpc_id" {
  value       = aws_vpc.main.id
  description = "VPC ID"
}

output "rds_security_group_id" {
  value       = aws_security_group.rds_sg.id
  description = "RDS Security Group ID"
}
