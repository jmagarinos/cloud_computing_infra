# ---------------------------------------------
# DynamoDB Table
# ---------------------------------------------

resource "aws_dynamodb_table" "eventos_usuario" {
  name         = "eventos_usuario"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "id_evento"

  attribute {
    name = "id_evento"
    type = "S"
  }

  tags = {
    Environment = "dev"
  }
}
