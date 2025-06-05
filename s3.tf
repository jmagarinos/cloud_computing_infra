# -----------------------------
# S3 Bucket
# -----------------------------
resource "aws_s3_bucket" "website" {
  bucket        = "website-lunchbox-dev-${formatdate("YYYYMMDDHHmmss", timestamp())}-x42f9"
  force_destroy = true

  # lifecycle {
  #   prevent_destroy = true
  # }

  tags = {
    Name        = format("website-%s", var.environment)
    Environment = var.environment
  }
}


# -----------------------------
# Public Access Configuration
# -----------------------------
resource "aws_s3_bucket_public_access_block" "website_block" {
  bucket = aws_s3_bucket.website.id

  block_public_acls       = false
  block_public_policy     = false
  ignore_public_acls      = false
  restrict_public_buckets = false
}

resource "aws_s3_bucket_ownership_controls" "website_ownership" {
  bucket = aws_s3_bucket.website.id

  rule {
    object_ownership = "ObjectWriter"
  }
}

resource "aws_s3_bucket_acl" "website_acl" {
  depends_on = [aws_s3_bucket_ownership_controls.website_ownership]
  bucket     = aws_s3_bucket.website.id
  acl        = "public-read"
}

resource "aws_s3_bucket_policy" "website_policy" {
  bucket = aws_s3_bucket.website.id

  depends_on = [aws_s3_bucket_public_access_block.website_block]

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Sid       = "PublicReadGetObject",
        Effect    = "Allow",
        Principal = "*",
        Action    = "s3:GetObject",
        Resource  = "${aws_s3_bucket.website.arn}/*"
      }
    ]
  })
}

# -----------------------------
# Website Hosting Configuration
# -----------------------------
resource "aws_s3_bucket_website_configuration" "website_config" {
  bucket = aws_s3_bucket.website.id

  index_document {
    suffix = "index.html"
  }

  error_document {
    key = "error.html"
  }
}

# -----------------------------
# Upload Website Files
# -----------------------------
resource "aws_s3_object" "index" {
  bucket       = aws_s3_bucket.website.id
  key          = "index.html"
  source       = "${path.module}/resources/index.html"
  content_type = "text/html"
  etag         = filemd5("${path.module}/resources/index.html")
}

resource "aws_s3_object" "vianda_detail" {
  bucket       = aws_s3_bucket.website.id
  key          = "vianda-detail.html"
  source       = "${path.module}/resources/vianda-detail.html"
  content_type = "text/html"
  etag         = filemd5("${path.module}/resources/vianda-detail.html")
}

resource "aws_s3_object" "login" {
  bucket       = aws_s3_bucket.website.id
  key          = "login.html"
  source       = "${path.module}/resources/login.html"
  content_type = "text/html"
  etag         = filemd5("${path.module}/resources/login.html")
}

resource "aws_s3_object" "error" {
  bucket       = aws_s3_bucket.website.id
  key          = "error.html"
  source       = "${path.module}/resources/error.html"
  content_type = "text/html"
  etag         = filemd5("${path.module}/resources/error.html")
}

resource "aws_s3_object" "signup" {
  bucket       = aws_s3_bucket.website.id
  key          = "signup.html"
  source       = "${path.module}/resources/signup.html"
  content_type = "text/html"
  etag         = filemd5("${path.module}/resources/signup.html")
}

resource "aws_s3_object" "confirm" {
  bucket       = aws_s3_bucket.website.id
  key          = "confirm.html"
  source       = "${path.module}/resources/confirm.html"
  content_type = "text/html"
  etag         = filemd5("${path.module}/resources/confirm.html")
}

resource "aws_s3_object" "profile" {
  bucket       = aws_s3_bucket.website.id
  key          = "profile.html"
  source       = "${path.module}/resources/profile.html"
  content_type = "text/html"
  etag         = filemd5("${path.module}/resources/profile.html")
}

resource "aws_s3_object" "auth_js" {
  bucket       = aws_s3_bucket.website.id
  key          = "js/auth.js"
  source       = "${path.module}/resources/js/auth.js"
  etag         = filemd5("${path.module}/resources/js/auth.js")
  content_type = "application/javascript"
}

resource "aws_s3_object" "api_js" {
  bucket       = aws_s3_bucket.website.id
  key          = "js/api.js"
  source       = "${path.module}/resources/js/api.js"
  etag         = filemd5("${path.module}/resources/js/api.js")
  content_type = "application/javascript"
}

resource "aws_s3_object" "config_js" {
  bucket       = aws_s3_bucket.website.id
  key          = "js/config.js"
  content      = <<-EOF
    // Configuración de Cognito
    const cognitoConfig = {
      userPoolId: "${aws_cognito_user_pool.main.id}",
      clientId: "${aws_cognito_user_pool_client.web_client.id}"
    };

    // Configuración de la API
    const apiConfig = {
      apiUrl: "${aws_apigatewayv2_stage.vianda_api_stage.invoke_url}"
    };
  EOF
  content_type = "application/javascript"
}

resource "aws_s3_object" "write_vianda" {
  bucket       = aws_s3_bucket.website.id
  key          = "write_vianda.html"
  source       = "${path.module}/resources/write_vianda.html"
  content_type = "text/html"
  etag         = filemd5("${path.module}/resources/write_vianda.html")
}
