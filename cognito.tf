# -----------------------------
# Cognito User Pool
# -----------------------------

resource "aws_cognito_user_pool" "main" {
  name                = format("user-pool-%s", var.environment)
  username_attributes = ["email"]
  password_policy {
    minimum_length    = 8
    require_numbers   = true
    require_symbols   = false
    require_uppercase = true
    require_lowercase = true
  }

  auto_verified_attributes = ["email"]

  lambda_config {
    post_confirmation = aws_lambda_function.cognito_post_confirmation_trigger.arn
  }
}

resource "aws_cognito_user_pool_client" "web_client" {
  name         = format("user-pool-client-%s", var.environment)
  user_pool_id = aws_cognito_user_pool.main.id

  generate_secret = false

  allowed_oauth_flows_user_pool_client = true
  allowed_oauth_flows                  = ["code", "implicit"]
  allowed_oauth_scopes                 = ["email", "openid", "profile"]

  callback_urls = [
    var.cognito_callback_url
  ]

  logout_urls = [
    var.cognito_logout_url
  ]
}

resource "aws_cognito_user_pool_domain" "main" {
  domain       = format("%s-%s-login-%s", var.project_name, var.environment, formatdate("YYYYMMDDHHmmss", timestamp()))
  user_pool_id = aws_cognito_user_pool.main.id
}
