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

output "cognito_user_pool_id" {
  value = aws_cognito_user_pool.main.id
}

output "cognito_user_pool_client_id" {
  value = aws_cognito_user_pool_client.web_client.id
}

output "cognito_hosted_ui_url" {
  value = format("https://%s.auth.%s.amazoncognito.com/login?client_id=%s&response_type=code&scope=email+openid+profile&redirect_uri=%s",
    aws_cognito_user_pool_domain.main.domain,
    var.aws_region,
    aws_cognito_user_pool_client.web_client.id,
    var.cognito_callback_url
  )
}

output "frontend_url" {
  description = "URL pública de tu frontend (S3 Static Website)"
  value       = "http://${aws_s3_bucket_website_configuration.website_config.website_endpoint}"
}

output "vianda_api_invoke_url" {
  value = aws_apigatewayv2_stage.vianda_api_stage.invoke_url
  description = "URL de invocación de la API HTTP de viandas"
}
