variable "environment" {
  description = "Deployment environment identifier"
  type        = string
}

variable "aws_region" {
  description = "AWS region for resources"
  type        = string
  default     = "us-east-1"
}

variable "app_bucket_name" {
  description = "Name of the S3 bucket for application artifacts"
  type        = string
}

variable "kubernetes_host" {
  description = "Kubernetes API server endpoint"
  type        = string
}

variable "kubernetes_cluster_ca" {
  description = "Base64 encoded cluster CA certificate"
  type        = string
}

variable "kubernetes_token" {
  description = "Service account token for cluster operations"
  type        = string
  sensitive   = true
}
