locals {
  tags = {
    Environment = var.environment
    ManagedBy   = "terraform"
    Project     = "discovery-intelligence"
  }
}

resource "aws_s3_bucket" "artifacts" {
  bucket = var.app_bucket_name
  tags   = local.tags
}

resource "aws_s3_bucket_versioning" "artifacts" {
  bucket = aws_s3_bucket.artifacts.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "kubernetes_namespace" "discovery" {
  metadata {
    name = "discovery"
    labels = {
      "app.kubernetes.io/managed-by" = "terraform"
      "app.kubernetes.io/part-of"    = "discovery-platform"
    }
  }
}

output "artifact_bucket" {
  description = "S3 bucket storing build artifacts"
  value       = aws_s3_bucket.artifacts.bucket
}

output "namespace" {
  description = "Kubernetes namespace for workloads"
  value       = kubernetes_namespace.discovery.metadata[0].name
}
