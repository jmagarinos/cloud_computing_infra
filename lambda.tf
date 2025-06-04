# Local with Lambda definitions
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
  }
}


# Single aws_lambda_function with for_each
resource "aws_lambda_function" "vianda" {
  for_each = local.vianda_lambdas

  function_name = replace(each.key, "_", "-")

  role = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:role/LabRole"

  runtime = "python3.12"

  # 🔥 Aquí está la magia:
  handler  = "${each.value.base_name}.lambda_handler"
  filename = "${path.module}/scripts/${each.value.base_name}.zip"

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
  depends_on = [aws_cognito_user_pool.main]
  layers     = [aws_lambda_layer_version.psycopg2_layer.arn]
}

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

  timeout = 30 # seconds

  vpc_config {
    subnet_ids         = [for subnet in aws_subnet.private : subnet.id]
    security_group_ids = [module.sg.security_group_id]
  }

  layers     = [aws_lambda_layer_version.psycopg2_layer.arn] # Needs psycopg2 to connect to RDS
  depends_on = [aws_db_instance.postgres]
}

resource "aws_lambda_permission" "allow_cognito_to_invoke_post_confirmation" {
  statement_id  = "AllowCognitoInvokePostConfirmationTrigger"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.cognito_post_confirmation_trigger.function_name
  principal     = "cognito-idp.amazonaws.com"
  source_arn    = aws_cognito_user_pool.main.arn
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

# Lambda para procesar imágenes en alta resolución
resource "aws_lambda_function" "process_image_high_res" {
  filename         = "${path.module}/resources/lambda/process_image_high_res.zip"
  function_name    = "process-image-high-res-${var.environment}"
  role            = aws_iam_role.lambda_role.arn
  handler         = "index.handler"
  runtime         = "nodejs18.x"
  timeout         = 30
  memory_size     = 256

  environment {
    variables = {
      BUCKET_NAME = aws_s3_bucket.website.id
      HIGH_RES_PREFIX = "images/high-res"
    }
  }

  depends_on = [
    aws_iam_role_policy_attachment.lambda_logs,
    aws_cloudwatch_log_group.process_image_high_res
  ]
}

# CloudWatch log group para la lambda de alta resolución
resource "aws_cloudwatch_log_group" "process_image_high_res" {
  name              = "/aws/lambda/process-image-high-res-${var.environment}"
  retention_in_days = 14
}

# Lambda para procesar imágenes en baja resolución
resource "aws_lambda_function" "process_image_low_res" {
  filename         = "${path.module}/resources/lambda/process_image_low_res.zip"
  function_name    = "process-image-low-res-${var.environment}"
  role            = aws_iam_role.lambda_role.arn
  handler         = "index.handler"
  runtime         = "nodejs18.x"
  timeout         = 30
  memory_size     = 256

  environment {
    variables = {
      BUCKET_NAME = aws_s3_bucket.website.id
      LOW_RES_PREFIX = "images/low-res"
    }
  }

  depends_on = [
    aws_iam_role_policy_attachment.lambda_logs,
    aws_cloudwatch_log_group.process_image_low_res
  ]
}

# CloudWatch log group para la lambda de baja resolución
resource "aws_cloudwatch_log_group" "process_image_low_res" {
  name              = "/aws/lambda/process-image-low-res-${var.environment}"
  retention_in_days = 14
}

# Permisos para que las Lambdas puedan ser invocadas por SNS
resource "aws_lambda_permission" "sns_high_res" {
  statement_id  = "AllowSNSInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.process_image_high_res.function_name
  principal     = "sns.amazonaws.com"
  source_arn    = aws_sns_topic.image_processing.arn
}

resource "aws_lambda_permission" "sns_low_res" {
  statement_id  = "AllowSNSInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.process_image_low_res.function_name
  principal     = "sns.amazonaws.com"
  source_arn    = aws_sns_topic.image_processing.arn
}

# Suscribir las Lambdas al SNS topic
resource "aws_sns_topic_subscription" "high_res" {
  topic_arn = aws_sns_topic.image_processing.arn
  protocol  = "lambda"
  endpoint  = aws_lambda_function.process_image_high_res.arn
}

resource "aws_sns_topic_subscription" "low_res" {
  topic_arn = aws_sns_topic.image_processing.arn
  protocol  = "lambda"
  endpoint  = aws_lambda_function.process_image_low_res.arn
}

# Política IAM para permitir que las Lambdas accedan a S3 y procesen imágenes
resource "aws_iam_role_policy" "lambda_s3_image_policy" {
  name = "lambda_s3_image_policy"
  role = aws_iam_role.lambda_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject",
          "s3:ListBucket"
        ]
        Resource = [
          aws_s3_bucket.website.arn,
          "${aws_s3_bucket.website.arn}/*"
        ]
      }
    ]
  })
}
