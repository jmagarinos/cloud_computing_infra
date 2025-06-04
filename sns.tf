resource "aws_sns_topic" "image_processing" {
  name = "image-processing-topic-${var.environment}"
}

# Política para permitir que S3 publique en el SNS topic
resource "aws_sns_topic_policy" "image_processing" {
  arn = aws_sns_topic.image_processing.arn

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "AllowS3ToPublishToSNS"
        Effect = "Allow"
        Principal = {
          Service = "s3.amazonaws.com"
        }
        Action   = "SNS:Publish"
        Resource = aws_sns_topic.image_processing.arn
        Condition = {
          ArnLike = {
            "aws:SourceArn": "${aws_s3_bucket.website.arn}"
          }
        }
      }
    ]
  })
} 