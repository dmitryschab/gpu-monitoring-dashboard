# Terraform Outputs

output "s3_raw_bucket_name" {
  description = "Name of the S3 bucket for raw GPU logs"
  value       = aws_s3_bucket.gpu_logs_raw.id
}

output "s3_raw_bucket_arn" {
  description = "ARN of the S3 bucket for raw GPU logs"
  value       = aws_s3_bucket.gpu_logs_raw.arn
}

output "s3_processed_bucket_name" {
  description = "Name of the S3 bucket for processed logs"
  value       = aws_s3_bucket.gpu_logs_processed.id
}

output "lambda_function_name" {
  description = "Name of the Lambda function"
  value       = aws_lambda_function.gpu_log_processor.function_name
}

output "lambda_function_arn" {
  description = "ARN of the Lambda function"
  value       = aws_lambda_function.gpu_log_processor.arn
}

output "cloudwatch_log_group" {
  description = "CloudWatch log group for Lambda"
  value       = aws_cloudwatch_log_group.lambda_log_group.name
}

output "upload_command" {
  description = "AWS CLI command to upload GPU-Z logs"
  value       = "aws s3 cp \"data/GPU-Z Sensor Log.txt\" s3://${aws_s3_bucket.gpu_logs_raw.id}/logs/$(date +%Y%m%d_%H%M%S).txt"
}

output "free_tier_summary" {
  description = "Summary of free tier usage"
  value = <<-EOT

  ========================================
  AWS FREE TIER USAGE SUMMARY
  ========================================

  S3 Storage (5 GB free):
    - Expected: ~3 GB/month
    - Status: ✅ WITHIN FREE TIER

  S3 PUT Requests (2,000 free):
    - Expected: ~8,640/month (5-min batches)
    - Status: ⚠️  EXCEEDS - Use upload script batching

  Lambda Invocations (1M free):
    - Expected: ~8,640/month
    - Status: ✅ WITHIN FREE TIER

  Lambda Compute (400K GB-sec free):
    - Expected: ~4,320 GB-sec/month
    - Status: ✅ WITHIN FREE TIER (1% usage)

  CloudWatch Logs (5 GB free):
    - Expected: ~500 MB/month
    - Status: ✅ WITHIN FREE TIER

  Data Transfer OUT (100 GB free):
    - Expected: ~5-10 GB/month
    - Status: ✅ WITHIN FREE TIER

  ========================================
  TOTAL ESTIMATED COST: $0.00/month
  ========================================

  EOT
}
