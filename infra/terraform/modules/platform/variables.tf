variable "namespace" {
  description = "Primary Kubernetes namespace for platform workloads"
  type        = string
}

variable "labels" {
  description = "Additional labels applied to the namespace"
  type        = map(string)
  default     = {}
}

variable "annotations" {
  description = "Additional annotations applied to the namespace"
  type        = map(string)
  default     = {}
}

variable "argocd_enabled" {
  description = "Toggle creation of ArgoCD project and applications"
  type        = bool
  default     = false
}

variable "argocd_namespace" {
  description = "Namespace where ArgoCD control plane is running"
  type        = string
  default     = "argocd"
}

variable "argocd_project" {
  description = "ArgoCD project definition"
  type = object({
    name         = string
    description  = string
    source_repos = list(string)
    destinations = list(object({
      namespace = string
      server    = string
    }))
  })
  nullable = true
  default  = null
}

variable "argocd_applications" {
  description = "List of ArgoCD application specifications"
  type = list(object({
    name                  = string
    repo_url              = string
    path                  = string
    target_revision       = string
    value_files           = list(string)
    destination_namespace = optional(string)
    sync_prune            = optional(bool, true)
    sync_self_heal        = optional(bool, true)
  }))
  default = []
}
