resource "aws_lambda_function" "vianda_writer" {
  function_name = "vianda-writer"

  role = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:role/LabRole"

  runtime = "python3.12"
  handler = "lambda_function.lambda_handler"

  filename = "${path.module}/scripts/lambda_vianda_writer.zip"

  environment {
    variables = {
      DB_HOST     = aws_db_instance.postgres.address
      DB_NAME     = "lunchbox"
      DB_USER     = "lunchbox_user"
      DB_PASSWORD = var.db_password
    }
  }

  timeout = 60

  vpc_config {
    subnet_ids         = [for subnet in aws_subnet.private : subnet.id]
    security_group_ids = [module.sg.security_group_id]
  }
}



resource "aws_lambda_function" "vianda_buy" {
  function_name = "vianda-buy"

  role          = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:role/LabRole"

  runtime       = "python3.12"
  handler       = "lambda_function.lambda_handler"

  filename      = "${path.module}/scripts/lambda_vianda_buy.zip"

  

  environment {
    variables = {
      DB_HOST     = aws_db_instance.postgres.address
      DB_NAME     = "lunchbox"
      DB_USER     = "lunchbox_user"
      DB_PASSWORD = var.db_password
    }
  }

  timeout = 10

    vpc_config {
    subnet_ids         = [for subnet in aws_subnet.private : subnet.id]
    security_group_ids = [module.sg.security_group_id]
  }
}

resource "aws_lambda_function" "vianda_delete" {
  function_name = "vianda-delete"

  role          = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:role/LabRole"

  runtime       = "python3.12"
  handler       = "lambda_function.lambda_handler"

  filename      = "${path.module}/scripts/lambda_vianda_delete.zip"

  

  environment {
    variables = {
      DB_HOST     = aws_db_instance.postgres.address
      DB_NAME     = "lunchbox"
      DB_USER     = "lunchbox_user"
      DB_PASSWORD = var.db_password
    }
  }

  timeout = 10

    vpc_config {
    subnet_ids         = [for subnet in aws_subnet.private : subnet.id]
    security_group_ids = [module.sg.security_group_id]
  }
}

data "aws_caller_identity" "current" {}