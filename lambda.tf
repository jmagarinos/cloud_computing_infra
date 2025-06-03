resource "aws_lambda_function" "vianda_writer" {
  function_name = "vianda-writer"

  role = "arn:aws:iam::891377282035:role/LabRole"

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
