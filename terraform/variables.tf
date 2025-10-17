# Terraform Variables Configuration

variable "aws_region" {
  description = "AWS region for resources"
  type        = string
  default     = "us-east-1"  # Virginia - typically has best free tier availability
}

variable "environment" {
  description = "Environment name (dev/staging/prod)"
  type        = string
  default     = "dev"
}

variable "project_name" {
  description = "Project name for resource naming"
  type        = string
  default     = "gpu-monitoring"
}

variable "kafka_endpoint" {
  description = "Kafka broker endpoint (local or remote)"
  type        = string
  default     = ""  # Will be provided via tfvars or env variable
}

variable "kafka_topic" {
  description = "Kafka topic name for GPU metrics"
  type        = string
  default     = "gpu-metrics"
}

variable "upload_batch_interval" {
  description = "Upload interval in minutes (to optimize free tier)"
  type        = number
  default     = 5  # Upload every 5 minutes to stay within PUT limits
}
