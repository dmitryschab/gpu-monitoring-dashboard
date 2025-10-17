# GPU Monitoring Dashboard - Terraform Infrastructure
# 100% AWS Free Tier Compliant Configuration

terraform {
  required_version = ">= 1.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = "gpu-monitoring-dashboard"
      Environment = var.environment
      ManagedBy   = "terraform"
    }
  }
}

# S3 Bucket for GPU-Z Logs (Raw)
resource "aws_s3_bucket" "gpu_logs_raw" {
  bucket = "${var.project_name}-raw-logs-${var.environment}"

  tags = {
    Name        = "GPU Logs Raw Storage"
    Description = "Stores raw GPU-Z sensor logs"
  }
}

# S3 Bucket for Processed Data
resource "aws_s3_bucket" "gpu_logs_processed" {
  bucket = "${var.project_name}-processed-logs-${var.environment}"

  tags = {
    Name        = "GPU Logs Processed Storage"
    Description = "Stores processed GPU metrics"
  }
}

# Enable versioning for raw logs (disaster recovery)
resource "aws_s3_bucket_versioning" "raw_versioning" {
  bucket = aws_s3_bucket.gpu_logs_raw.id

  versioning_configuration {
    status = "Enabled"
  }
}

# S3 Lifecycle Policy - Move old data to cheaper storage (stay free)
resource "aws_s3_bucket_lifecycle_configuration" "raw_lifecycle" {
  bucket = aws_s3_bucket.gpu_logs_raw.id

  rule {
    id     = "archive-old-logs"
    status = "Enabled"

    # Apply to all objects
    filter {}

    # Delete old versions after 7 days to save space
    noncurrent_version_expiration {
      noncurrent_days = 7
    }

    # Move to Intelligent-Tiering after 30 days (free tier friendly)
    transition {
      days          = 30
      storage_class = "INTELLIGENT_TIERING"
    }

    # Delete after 90 days (optional - adjust as needed)
    expiration {
      days = 90
    }
  }
}

# Block public access (security best practice)
resource "aws_s3_bucket_public_access_block" "raw_bucket_pab" {
  bucket = aws_s3_bucket.gpu_logs_raw.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_public_access_block" "processed_bucket_pab" {
  bucket = aws_s3_bucket.gpu_logs_processed.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Server-side encryption (free, security best practice)
resource "aws_s3_bucket_server_side_encryption_configuration" "raw_encryption" {
  bucket = aws_s3_bucket.gpu_logs_raw.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "processed_encryption" {
  bucket = aws_s3_bucket.gpu_logs_processed.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# IAM Role for Lambda Execution
resource "aws_iam_role" "lambda_execution_role" {
  name = "${var.project_name}-lambda-role-${var.environment}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "lambda.amazonaws.com"
      }
    }]
  })
}

# IAM Policy for Lambda (minimal permissions)
resource "aws_iam_role_policy" "lambda_policy" {
  name = "${var.project_name}-lambda-policy"
  role = aws_iam_role.lambda_execution_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:ListBucket"
        ]
        Resource = [
          aws_s3_bucket.gpu_logs_raw.arn,
          "${aws_s3_bucket.gpu_logs_raw.arn}/*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "s3:PutObject"
        ]
        Resource = [
          "${aws_s3_bucket.gpu_logs_processed.arn}/*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "arn:aws:logs:*:*:*"
      }
    ]
  })
}

# CloudWatch Log Group with retention (free tier friendly)
resource "aws_cloudwatch_log_group" "lambda_log_group" {
  name              = "/aws/lambda/${var.project_name}-processor-${var.environment}"
  retention_in_days = 7  # Keep logs for 7 days only to stay within free tier

  tags = {
    Name = "Lambda Log Group"
  }
}

# Lambda Function - GPU Log Processor
resource "aws_lambda_function" "gpu_log_processor" {
  filename         = "${path.module}/lambda/gpu_processor.zip"
  function_name    = "${var.project_name}-processor-${var.environment}"
  role            = aws_iam_role.lambda_execution_role.arn
  handler         = "processor.lambda_handler"
  source_code_hash = filebase64sha256("${path.module}/lambda/gpu_processor.zip")
  runtime         = "python3.11"
  timeout         = 60  # 60 seconds max
  memory_size     = 256 # 256 MB (free tier friendly)

  environment {
    variables = {
      PROCESSED_BUCKET = aws_s3_bucket.gpu_logs_processed.id
      KAFKA_ENDPOINT   = var.kafka_endpoint
      KAFKA_TOPIC      = var.kafka_topic
      LOG_LEVEL        = "INFO"
    }
  }

  depends_on = [
    aws_cloudwatch_log_group.lambda_log_group,
    aws_iam_role_policy.lambda_policy
  ]

  tags = {
    Name = "GPU Log Processor Lambda"
  }
}

# S3 Event Notification to Lambda
resource "aws_s3_bucket_notification" "raw_bucket_notification" {
  bucket = aws_s3_bucket.gpu_logs_raw.id

  lambda_function {
    lambda_function_arn = aws_lambda_function.gpu_log_processor.arn
    events              = ["s3:ObjectCreated:*"]
    filter_suffix       = ".gz"
  }

  depends_on = [aws_lambda_permission.allow_s3_invoke]
}

# Lambda Permission - Allow S3 to invoke Lambda
resource "aws_lambda_permission" "allow_s3_invoke" {
  statement_id  = "AllowExecutionFromS3"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.gpu_log_processor.function_name
  principal     = "s3.amazonaws.com"
  source_arn    = aws_s3_bucket.gpu_logs_raw.arn
}

# CloudWatch Alarm for Lambda Errors (free tier: 10 alarms)
resource "aws_cloudwatch_metric_alarm" "lambda_errors" {
  alarm_name          = "${var.project_name}-lambda-errors-${var.environment}"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 1
  metric_name         = "Errors"
  namespace           = "AWS/Lambda"
  period              = 300  # 5 minutes
  statistic           = "Sum"
  threshold           = 5
  alarm_description   = "Alert when Lambda has more than 5 errors in 5 minutes"
  treat_missing_data  = "notBreaching"

  dimensions = {
    FunctionName = aws_lambda_function.gpu_log_processor.function_name
  }

  tags = {
    Name = "Lambda Error Alarm"
  }
}
