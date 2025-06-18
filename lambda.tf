# -----------------------------
# Lambda locals
# -----------------------------
locals {
  vianda_lambdas = {
    vianda_writer = {
      base_name = "lambda_vianda_create"
      timeout   = 60
    }
    vianda_buy = {
      base_name = "lambda_vianda_buy"
      timeout   = 60
    }
    vianda_delete = {
      base_name = "lambda_vianda_delete"
      timeout   = 60
    }
    vianda_list = {
      base_name = "lambda_vianda_list"
      timeout   = 60
    }
    vianda_get = {
      base_name = "lambda_vianda_get"
      timeout   = 60
    }
    vianda_profile = {
      base_name = "lambda_vianda_profile"
      timeout   = 60
    }
    vianda_profile_update = {
      base_name = "lambda_vianda_profile_update"
      timeout   = 60
    }
    vianda_toggle_disponibilidad = {
      base_name = "lambda_vianda_toggle_disponibilidad"
      timeout   = 60
    }
    vianda_compras = {
      base_name = "lambda_vianda_compras"
      timeout   = 60
    }
    vianda_ventas = {
      base_name = "lambda_vianda_ventas"
      timeout   = 60
    }
    vianda_list_by_user = {
      base_name = "lambda_vianda_list_by_user"
      timeout   = 60
    }
  }
}

# -----------------------------
# Lambda Vianda Actions Creation
# -----------------------------
resource "aws_lambda_function" "vianda" {
  for_each = local.vianda_lambdas

  function_name = replace(each.key, "_", "-")

  role = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:role/LabRole"

  runtime = "python3.12"

  handler  = "${each.value.base_name}.lambda_handler"
  filename = "${path.module}/scripts/${each.value.base_name}.zip"

  environment {
    variables = {
      DB_HOST         = aws_db_instance.postgres.address
      DB_NAME         = "lunchbox"
      DB_USER         = var.db_username
      DB_PASSWORD     = var.db_password
      SNS_EVENTOS_ARN = aws_sns_topic.eventos_usuario.arn
    }
  }

  timeout = each.value.timeout

  vpc_config {
    subnet_ids         = [for subnet in aws_subnet.private : subnet.id]
    security_group_ids = [module.sg.security_group_id]
  }
  depends_on = [
    aws_cognito_user_pool.main,
    aws_sns_topic.eventos_usuario
  ]

  layers = [aws_lambda_layer_version.psycopg2_layer.arn]
}

# -----------------------------
# Lambda DB Init 
# -----------------------------

resource "aws_lambda_function" "rds_init" {
  function_name = "rds-init"

  role = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:role/LabRole"

  runtime  = "python3.12"
  handler  = "lambda_rds_init.lambda_handler"
  filename = "${path.module}/scripts/lambda_rds_init.zip"

  environment {
    variables = {
      DB_HOST     = aws_db_instance.postgres.address
      DB_NAME     = "lunchbox"
      DB_USER     = var.db_username
      DB_PASSWORD = var.db_password
    }
  }

  timeout = 60

  vpc_config {
    subnet_ids         = [for subnet in aws_subnet.private : subnet.id]
    security_group_ids = [module.sg.security_group_id]
  }

  layers = [aws_lambda_layer_version.psycopg2_layer.arn]

  provisioner "local-exec" {
    command = <<EOT
      aws lambda invoke \
        --function-name ${aws_lambda_function.rds_init.function_name} \
        --region us-east-1 \
        --payload '{}' \
        /tmp/rds_init_output.json
    EOT
  }

  depends_on = [
    aws_db_instance.postgres
  ]
}

# -----------------------------
# Lambda cognito DB writer
# -----------------------------

resource "aws_lambda_function" "cognito_post_confirmation_trigger" {
  function_name = "cognito-post-confirmation-trigger"
  role          = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:role/LabRole" # Using the existing LabRole
  runtime       = "python3.12"
  handler       = "lambda_cognito_post_confirmation.lambda_handler"
  filename      = "${path.module}/scripts/lambda_cognito_post_confirmation.zip"

  environment {
    variables = {
      DB_HOST     = aws_db_instance.postgres.address
      DB_NAME     = "lunchbox"
      DB_USER     = var.db_username
      DB_PASSWORD = var.db_password
    }
  }

  timeout = 30

  vpc_config {
    subnet_ids         = [for subnet in aws_subnet.private : subnet.id]
    security_group_ids = [module.sg.security_group_id]
  }

  layers     = [aws_lambda_layer_version.psycopg2_layer.arn]
  depends_on = [aws_db_instance.postgres]
}

resource "aws_lambda_permission" "allow_cognito_to_invoke_post_confirmation" {
  statement_id  = "AllowCognitoInvokePostConfirmationTrigger"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.cognito_post_confirmation_trigger.function_name
  principal     = "cognito-idp.amazonaws.com"
  source_arn    = aws_cognito_user_pool.main.arn
}

# -----------------------------
# Lambda Layers
# -----------------------------

resource "aws_lambda_layer_version" "psycopg2_layer" {
  layer_name          = "psycopg2-lunchbox"
  compatible_runtimes = ["python3.12"]
  description         = "psycopg2-binary for Python 3.12"

  filename = "${path.module}/layers/psycopg2-layer.zip"

  lifecycle {
    create_before_destroy = true
  }
}


# resource "aws_lambda_layer_version" "jwt_layer" {
#   layer_name          = "jwt-lunchbox"
#   compatible_runtimes = ["python3.12"]
#   description         = "jwt for Python 3.12"

#   filename = "${path.module}/layers/jwt_layer.zip"

#   lifecycle {
#     create_before_destroy = true
#   }
# }

data "aws_caller_identity" "current" {}

# -----------------------------
# Lambda para guardar evento en DynamoDB
# -----------------------------

resource "aws_lambda_function" "guardar_evento" {
  function_name = "guardar_evento_dynamo"
  role          = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:role/LabRole"
  runtime       = "python3.12"
  handler       = "lambda_guardar_evento.lambda_handler"
  filename      = "${path.module}/scripts/lambda_guardar_evento.zip"

  environment {
    variables = {
      DYNAMO_TABLE = aws_dynamodb_table.eventos_usuario.name
    }
  }

  timeout = 30

  depends_on = [aws_dynamodb_table.eventos_usuario]
}

# -----------------------------
# Permiso para que SNS invoque la Lambda
# -----------------------------

resource "aws_lambda_permission" "allow_sns_to_invoke" {
  statement_id  = "AllowExecutionFromSNS"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.guardar_evento.function_name
  principal     = "sns.amazonaws.com"
  source_arn    = aws_sns_topic.eventos_usuario.arn
}

# -----------------------------
# Suscripción SNS → Lambda
# -----------------------------

resource "aws_sns_topic_subscription" "sns_to_lambda" {
  topic_arn = aws_sns_topic.eventos_usuario.arn
  protocol  = "lambda"
  endpoint  = aws_lambda_function.guardar_evento.arn
}

resource "aws_vpc_endpoint" "sns" {
  vpc_id              = module.vpc.vpc_id
  service_name        = "com.amazonaws.${var.aws_region}.sns"
  vpc_endpoint_type   = "Interface"
  private_dns_enabled = true

  subnet_ids         = [for subnet in aws_subnet.private : subnet.id]
  security_group_ids = [module.sg.security_group_id]

  tags = {
    Name = "sns-endpoint"
  }
}
