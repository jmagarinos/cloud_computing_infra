resource "aws_api_gateway_rest_api" "vianda_api" {
  name        = "vianda-api"
  description = "API para gestión de viandas"
}

resource "aws_api_gateway_resource" "viandas" {
  rest_api_id = aws_api_gateway_rest_api.vianda_api.id
  parent_id   = aws_api_gateway_rest_api.vianda_api.root_resource_id
  path_part   = "viandas"
}

resource "aws_api_gateway_method" "post_viandas" {
  rest_api_id   = aws_api_gateway_rest_api.vianda_api.id
  resource_id   = aws_api_gateway_resource.viandas.id
  http_method   = "POST"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "lambda_integration" {
  rest_api_id = aws_api_gateway_rest_api.vianda_api.id
  resource_id = aws_api_gateway_resource.viandas.id
  http_method = aws_api_gateway_method.post_viandas.http_method

  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.vianda_writer.invoke_arn
}

resource "aws_lambda_permission" "allow_api_gateway" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.vianda_writer.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.vianda_api.execution_arn}/*/*"
}

resource "aws_api_gateway_deployment" "vianda_api_deployment" {
  depends_on = [
    aws_api_gateway_integration.lambda_integration
  ]

  rest_api_id = aws_api_gateway_rest_api.vianda_api.id
}

# Recurso para comprar vianda
resource "aws_api_gateway_resource" "comprar" {
  rest_api_id = aws_api_gateway_rest_api.vianda_api.id
  parent_id   = aws_api_gateway_rest_api.vianda_api.root_resource_id
  path_part   = "comprar"
}

resource "aws_api_gateway_method" "post_comprar" {
  rest_api_id   = aws_api_gateway_rest_api.vianda_api.id
  resource_id   = aws_api_gateway_resource.comprar.id
  http_method   = "POST"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "lambda_buy_integration" {
  rest_api_id             = aws_api_gateway_rest_api.vianda_api.id
  resource_id             = aws_api_gateway_resource.comprar.id
  http_method             = aws_api_gateway_method.post_comprar.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.vianda_buy.invoke_arn
}

resource "aws_lambda_permission" "allow_api_gateway_buy" {
  statement_id  = "AllowAPIGatewayInvokeBuy"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.vianda_buy.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.vianda_api.execution_arn}/*/*"
}

# Recurso para eliminar vianda (DELETE /viandas/{id})
resource "aws_api_gateway_resource" "vianda_id" {
  rest_api_id = aws_api_gateway_rest_api.vianda_api.id
  parent_id   = aws_api_gateway_resource.viandas.id
  path_part   = "{id}"
}

resource "aws_api_gateway_method" "delete_vianda" {
  rest_api_id   = aws_api_gateway_rest_api.vianda_api.id
  resource_id   = aws_api_gateway_resource.vianda_id.id
  http_method   = "DELETE"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "lambda_delete_integration" {
  rest_api_id             = aws_api_gateway_rest_api.vianda_api.id
  resource_id             = aws_api_gateway_resource.vianda_id.id
  http_method             = aws_api_gateway_method.delete_vianda.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.vianda_delete.invoke_arn
}

resource "aws_lambda_permission" "allow_api_gateway_delete" {
  statement_id  = "AllowAPIGatewayInvokeDelete"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.vianda_delete.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.vianda_api.execution_arn}/*/*"
}

