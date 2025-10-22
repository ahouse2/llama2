locals {
  namespace_labels      = merge({
    "app.kubernetes.io/managed-by" = "terraform"
    "app.kubernetes.io/part-of"    = "discovery-platform"
  }, var.labels)
  namespace_annotations = var.annotations
}

resource "kubernetes_namespace" "this" {
  metadata {
    name        = var.namespace
    labels      = local.namespace_labels
    annotations = local.namespace_annotations
  }
}

resource "kubernetes_manifest" "argocd_project" {
  count = var.argocd_enabled ? 1 : 0

  manifest = {
    apiVersion = "argoproj.io/v1alpha1"
    kind       = "AppProject"
    metadata = {
      name      = var.argocd_project.name
      namespace = var.argocd_namespace
      labels = {
        "app.kubernetes.io/managed-by" = "terraform"
        "app.kubernetes.io/part-of"    = "discovery-platform"
      }
    }
    spec = {
      description  = var.argocd_project.description
      sourceRepos  = var.argocd_project.source_repos
      destinations = [for dest in var.argocd_project.destinations : {
        namespace = dest.namespace
        server    = dest.server
      }]
      clusterResourceWhitelist = [
        {
          group = "*"
          kind  = "*"
        }
      ]
    }
  }

  depends_on = [kubernetes_namespace.this]
}

resource "kubernetes_manifest" "argocd_application" {
  for_each = var.argocd_enabled ? { for app in var.argocd_applications : app.name => app } : {}

  manifest = {
    apiVersion = "argoproj.io/v1alpha1"
    kind       = "Application"
    metadata = {
      name      = each.value.name
      namespace = var.argocd_namespace
      labels = {
        "app.kubernetes.io/managed-by" = "terraform"
        "app.kubernetes.io/part-of"    = "discovery-platform"
      }
    }
    spec = {
      project = var.argocd_project.name
      source = merge({
        repoURL        = each.value.repo_url
        path           = each.value.path
        targetRevision = each.value.target_revision
      }, length(each.value.value_files) > 0 ? {
        helm = {
          valueFiles = each.value.value_files
        }
      } : {})
      destination = {
        namespace = coalesce(each.value.destination_namespace, var.namespace)
        server    = var.argocd_project.destinations[0].server
      }
      syncPolicy = {
        automated = {
          prune    = each.value.sync_prune
          selfHeal = each.value.sync_self_heal
        }
        syncOptions = [
          "CreateNamespace=true",
          "RespectIgnoreDifferences=true"
        ]
      }
    }
  }

  depends_on = [kubernetes_manifest.argocd_project]
}

output "namespace" {
  description = "Namespace created for discovery workloads"
  value       = kubernetes_namespace.this.metadata[0].name
}
