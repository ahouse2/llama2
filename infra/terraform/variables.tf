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

variable "platform_namespace" {
  description = "Primary namespace for discovery platform workloads"
  type        = string
  default     = "discovery"
}

variable "platform_namespace_labels" {
  description = "Extra labels applied to the platform namespace"
  type        = map(string)
  default     = {}
}

variable "platform_namespace_annotations" {
  description = "Extra annotations applied to the platform namespace"
  type        = map(string)
  default     = {}
}

variable "argocd_config" {
  description = "GitOps configuration for ArgoCD automation"
  type = object({
    enabled             = bool
    namespace           = string
    project_name        = string
    project_description = string
    source_repos        = list(string)
    destinations        = list(object({
      namespace = string
      server    = string
    }))
    applications = list(object({
      name                  = string
      repo_url              = string
      path                  = string
      target_revision       = string
      value_files           = list(string)
      destination_namespace = optional(string)
      sync_prune            = optional(bool, true)
      sync_self_heal        = optional(bool, true)
    }))
  })
  default = {
    enabled             = false
    namespace           = "argocd"
    project_name        = "discovery-platform"
    project_description = ""
    source_repos        = []
    destinations        = []
    applications        = []
  }
}
