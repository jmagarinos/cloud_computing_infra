# API HTTP para Viandas
resource "aws_apigatewayv2_api" "vianda_api" {
  name          = "vianda-api"
  description   = "API para gestión de viandas"
  protocol_type = "HTTP"

  cors_configuration {
    allow_credentials = true 
    allow_headers     = ["*"]
    allow_methods     = ["*"]
    allow_origins     = ["http://${aws_s3_bucket_website_configuration.website_config.website_endpoint}"]
    expose_headers    = ["*"]
    max_age           = 300
  }
}

# POST /viandas
resource "aws_apigatewayv2_route" "post_viandas" {
  api_id    = aws_apigatewayv2_api.vianda_api.id
  route_key = "POST /viandas"
  target    = "integrations/${aws_apigatewayv2_integration.lambda_integration.id}"
  
  authorization_type = "JWT"
  authorizer_id     = aws_apigatewayv2_authorizer.cognito_authorizer.id
}

resource "aws_apigatewayv2_integration" "lambda_integration" {
  api_id                 = aws_apigatewayv2_api.vianda_api.id
  integration_type       = "AWS_PROXY"
  integration_method     = "POST"
  integration_uri        = aws_lambda_function.vianda["vianda_writer"].invoke_arn
  payload_format_version = "2.0"
}

resource "aws_lambda_permission" "allow_api_gateway" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.vianda["vianda_writer"].function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.vianda_api.execution_arn}/*/*"
}

# GET /viandas (listar)
resource "aws_apigatewayv2_route" "get_viandas" {
  api_id    = aws_apigatewayv2_api.vianda_api.id
  route_key = "GET /viandas"
  target    = "integrations/${aws_apigatewayv2_integration.lambda_list_integration.id}"
  
  authorization_type = "JWT"
  authorizer_id     = aws_apigatewayv2_authorizer.cognito_authorizer.id
}

resource "aws_apigatewayv2_integration" "lambda_list_integration" {
  api_id                 = aws_apigatewayv2_api.vianda_api.id
  integration_type       = "AWS_PROXY"
  integration_method     = "POST"
  integration_uri        = aws_lambda_function.vianda["vianda_list"].invoke_arn
  payload_format_version = "2.0"
}

resource "aws_lambda_permission" "allow_api_gateway_list" {
  statement_id  = "AllowAPIGatewayInvokeList"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.vianda["vianda_list"].function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.vianda_api.execution_arn}/*/*"
}

# POST /comprar
resource "aws_apigatewayv2_route" "post_comprar" {
  api_id    = aws_apigatewayv2_api.vianda_api.id
  route_key = "POST /comprar"
  target    = "integrations/${aws_apigatewayv2_integration.lambda_buy_integration.id}"
  
  authorization_type = "JWT"
  authorizer_id     = aws_apigatewayv2_authorizer.cognito_authorizer.id
}

resource "aws_apigatewayv2_integration" "lambda_buy_integration" {
  api_id                 = aws_apigatewayv2_api.vianda_api.id
  integration_type       = "AWS_PROXY"
  integration_method     = "POST"
  integration_uri        = aws_lambda_function.vianda["vianda_buy"].invoke_arn
  payload_format_version = "2.0"
}

resource "aws_lambda_permission" "allow_api_gateway_buy" {
  statement_id  = "AllowAPIGatewayInvokeBuy"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.vianda["vianda_buy"].function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.vianda_api.execution_arn}/*/*"
}

# DELETE /viandas/{id}
resource "aws_apigatewayv2_route" "delete_vianda" {
  api_id    = aws_apigatewayv2_api.vianda_api.id
  route_key = "DELETE /viandas/{id}"
  target    = "integrations/${aws_apigatewayv2_integration.lambda_delete_integration.id}"
  
  authorization_type = "JWT"
  authorizer_id     = aws_apigatewayv2_authorizer.cognito_authorizer.id
}

resource "aws_apigatewayv2_integration" "lambda_delete_integration" {
  api_id                 = aws_apigatewayv2_api.vianda_api.id
  integration_type       = "AWS_PROXY"
  integration_method     = "POST"
  integration_uri        = aws_lambda_function.vianda["vianda_delete"].invoke_arn
  payload_format_version = "2.0"
}

resource "aws_lambda_permission" "allow_api_gateway_delete" {
  statement_id  = "AllowAPIGatewayInvokeDelete"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.vianda["vianda_delete"].function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.vianda_api.execution_arn}/*/*"
}

# GET /viandas/{id}
resource "aws_apigatewayv2_route" "get_vianda" {
  api_id    = aws_apigatewayv2_api.vianda_api.id
  route_key = "GET /viandas/{id}"
  target    = "integrations/${aws_apigatewayv2_integration.lambda_get_integration.id}"
  
  authorization_type = "JWT"
  authorizer_id     = aws_apigatewayv2_authorizer.cognito_authorizer.id
}

resource "aws_apigatewayv2_integration" "lambda_get_integration" {
  api_id                 = aws_apigatewayv2_api.vianda_api.id
  integration_type       = "AWS_PROXY"
  integration_method     = "POST"
  integration_uri        = aws_lambda_function.vianda["vianda_get"].invoke_arn
  payload_format_version = "2.0"
}

resource "aws_lambda_permission" "allow_api_gateway_get" {
  statement_id  = "AllowAPIGatewayInvokeGet"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.vianda["vianda_get"].function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.vianda_api.execution_arn}/*/*"
}

# GET /perfil
resource "aws_apigatewayv2_route" "get_perfil" {
  api_id    = aws_apigatewayv2_api.vianda_api.id
  route_key = "GET /perfil"
  target    = "integrations/${aws_apigatewayv2_integration.lambda_profile_integration.id}"
  
  authorization_type = "JWT"
  authorizer_id     = aws_apigatewayv2_authorizer.cognito_authorizer.id
}

resource "aws_apigatewayv2_integration" "lambda_profile_integration" {
  api_id                 = aws_apigatewayv2_api.vianda_api.id
  integration_type       = "AWS_PROXY"
  integration_method     = "POST"
  integration_uri        = aws_lambda_function.vianda["vianda_profile"].invoke_arn
  payload_format_version = "2.0"
}

resource "aws_lambda_permission" "allow_api_gateway_profile" {
  statement_id  = "AllowAPIGatewayInvokeProfile"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.vianda["vianda_profile"].function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.vianda_api.execution_arn}/*/*"
}

# PUT /perfil
resource "aws_apigatewayv2_route" "put_perfil" {
  api_id    = aws_apigatewayv2_api.vianda_api.id
  route_key = "PUT /perfil"
  target    = "integrations/${aws_apigatewayv2_integration.lambda_profile_update_integration.id}"
  
  authorization_type = "JWT"
  authorizer_id     = aws_apigatewayv2_authorizer.cognito_authorizer.id
}

resource "aws_apigatewayv2_integration" "lambda_profile_update_integration" {
  api_id                 = aws_apigatewayv2_api.vianda_api.id
  integration_type       = "AWS_PROXY"
  integration_method     = "POST"
  integration_uri        = aws_lambda_function.vianda["vianda_profile_update"].invoke_arn
  payload_format_version = "2.0"
}

resource "aws_lambda_permission" "allow_api_gateway_profile_update" {
  statement_id  = "AllowAPIGatewayInvokeProfileUpdate"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.vianda["vianda_profile_update"].function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.vianda_api.execution_arn}/*/*"
}

# Stage de la API
resource "aws_apigatewayv2_stage" "vianda_api_stage" {
  api_id      = aws_apigatewayv2_api.vianda_api.id
  name        = "dev"
  auto_deploy = true
}

resource "aws_apigatewayv2_authorizer" "cognito_authorizer" {
  api_id           = aws_apigatewayv2_api.vianda_api.id
  authorizer_type  = "JWT"
  identity_sources = ["$request.header.Authorization"]
  name             = "cognito-authorizer"

  jwt_configuration {
    audience = [aws_cognito_user_pool_client.web_client.id]
    issuer   = "https://cognito-idp.us-east-1.amazonaws.com/${aws_cognito_user_pool.main.id}"
  }
}
