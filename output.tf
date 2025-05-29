# -----------------------------
# Output: Website URL
# -----------------------------
output "website_url" {
  value       = "http://${aws_s3_bucket.website.bucket}.s3-website-${var.aws_region}.amazonaws.com"
  description = "URL del sitio web estático en S3"
}
