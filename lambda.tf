# Local with Lambda definitions
locals {
  vianda_lambdas = {
    vianda_writer = {
      filename = "${path.module}/scripts/lambda_vianda_create.zip"
      timeout  = 60
    }
    vianda_buy = {
      filename = "${path.module}/scripts/lambda_vianda_buy.zip"
      timeout  = 60
    }
    vianda_delete = {
      filename = "${path.module}/scripts/lambda_vianda_delete.zip"
      timeout  = 60
    }
    vianda_list = {
      filename = "${path.module}/scripts/lambda_vianda_list.zip"
      timeout  = 60
    }
    vianda_get = {
      filename = "${path.module}/scripts/lambda_vianda_get.zip"
      timeout  = 60
    }
  }
}

# Single aws_lambda_function with for_each
resource "aws_lambda_function" "vianda" {
  for_each = local.vianda_lambdas

  function_name = replace(each.key, "_", "-") # example: vianda_writer → vianda-writer

  role = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:role/LabRole"

  runtime = "python3.12"
  handler = "lambda_function.lambda_handler"

  filename = each.value.filename

  environment {
    variables = {
      DB_HOST     = aws_db_instance.postgres.address
      DB_NAME     = "lunchbox"
      DB_USER     = var.db_username
      DB_PASSWORD = var.db_password
    }
  }

  timeout = each.value.timeout

  vpc_config {
    subnet_ids         = [for subnet in aws_subnet.private : subnet.id]
    security_group_ids = [module.sg.security_group_id]
  }

  layers = [aws_lambda_layer_version.psycopg2_layer.arn]
}


resource "aws_lambda_layer_version" "psycopg2_layer" {
  layer_name          = "psycopg2-lunchbox"
  compatible_runtimes = ["python3.12"]
  description         = "psycopg2-binary for Python 3.12"

  filename = "${path.module}/layers/psycopg2-layer.zip"

  lifecycle {
    create_before_destroy = true
  }
}

data "aws_caller_identity" "current" {}
