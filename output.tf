# -----------------------------
# Output: Website URL
# -----------------------------
output "website_url" {
  value       = "http://${aws_s3_bucket.website.bucket}.s3-website-${var.aws_region}.amazonaws.com"
  description = "URL del sitio web estático en S3"
}

output "rds_endpoint" {
  value = aws_db_instance.postgres.endpoint
}

output "private_subnet_ids" {
  value = [for subnet in aws_subnet.private : subnet.id]
}

output "vpc_id" {
  value = module.vpc.vpc_id
}

output "rds_security_group_id" {
  value = module.sg.security_group_id
}

output "website_bucket_name" {
  value = aws_s3_bucket.website.bucket
}
