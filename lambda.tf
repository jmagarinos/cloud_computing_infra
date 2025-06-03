resource "aws_iam_role" "lambda_vianda_writer_role" {
  name = "lambda_vianda_writer_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_vianda_writer_logs" {
  role       = aws_iam_role.lambda_vianda_writer_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_lambda_function" "vianda_writer" {
  function_name = "vianda-writer"
  role          = aws_iam_role.lambda_vianda_writer_role.arn
  runtime       = "python3.12"
  handler       = "lambda_function.lambda_handler"

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
}
