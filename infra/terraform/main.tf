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

module "platform" {
  source      = "./modules/platform"
  namespace   = var.platform_namespace
  labels      = merge({ environment = var.environment }, var.platform_namespace_labels)
  annotations = var.platform_namespace_annotations

  argocd_enabled   = var.argocd_config.enabled
  argocd_namespace = var.argocd_config.namespace
  argocd_project   = {
    name         = var.argocd_config.project_name
    description  = var.argocd_config.project_description
    source_repos = var.argocd_config.source_repos
    destinations = length(var.argocd_config.destinations) > 0 ? var.argocd_config.destinations : [
      {
        namespace = var.platform_namespace
        server    = "https://kubernetes.default.svc"
      }
    ]
  }
  argocd_applications = [for app in var.argocd_config.applications : {
    name                  = app.name
    repo_url              = app.repo_url
    path                  = app.path
    target_revision       = app.target_revision
    value_files           = app.value_files
    destination_namespace = try(app.destination_namespace, null)
    sync_prune            = try(app.sync_prune, true)
    sync_self_heal        = try(app.sync_self_heal, true)
  }]
}

output "artifact_bucket" {
  description = "S3 bucket storing build artifacts"
  value       = aws_s3_bucket.artifacts.bucket
}

output "namespace" {
  description = "Kubernetes namespace for workloads"
  value       = module.platform.namespace
}

output "gitops_project" {
  description = "ArgoCD project bootstrapped for the platform"
  value       = var.argocd_config.enabled ? var.argocd_config.project_name : null
}
