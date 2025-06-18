# ---------------------------------------------
# SNS Topic
# ---------------------------------------------

resource "aws_sns_topic" "eventos_usuario" {
  name = "eventos-usuario-topic"
}
