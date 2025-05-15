provider "aws" {
  region = var.aws_region
}

# -----------------------------
# S3 Buckets
# -----------------------------

resource "aws_s3_bucket" "website" {
  bucket        = "tp-static-website-lunchbox"
  force_destroy = true
}

resource "aws_s3_bucket_website_configuration" "website_config" {
  bucket = aws_s3_bucket.website.id

  index_document {
    suffix = "index.html"
  }

  error_document {
    key = "error.html"
  }
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

resource "aws_s3_bucket_public_access_block" "website_block" {
  bucket = aws_s3_bucket.website.id

  block_public_acls       = false
  block_public_policy     = false
  ignore_public_acls      = false
  restrict_public_buckets = false
}
