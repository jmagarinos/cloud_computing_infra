output "frontend_url" {
  description = "URL pública de tu frontend (S3 Static Website)"
  value       = "http://${aws_s3_bucket_website_configuration.website_config.website_endpoint}"
}
