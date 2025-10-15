environment       = "dev"
aws_region        = "us-east-1"
app_bucket_name   = "discovery-intelligence-dev-artifacts"
kubernetes_host   = "https://kubernetes.dev.discovery.local"
kubernetes_cluster_ca = "LS0tLS1CRUdJTiBDRVJUSUZJQ0FURS0tLS0t"
kubernetes_token  = "eyJhbGciOiJSUzI1NiIsImtpZCI6ImRldi1jbHVzdGVyIn0.dev-token-signature"
platform_namespace = "discovery-dev"
platform_namespace_labels = {
  environment = "dev"
}
argocd_config = {
  enabled             = true
  namespace           = "argocd"
  project_name        = "discovery-platform-dev"
  project_description = "GitOps project for discovery dev workloads"
  source_repos        = ["https://github.com/example/discovery.git"]
  destinations = [
    {
      namespace = "discovery-dev"
      server    = "https://kubernetes.default.svc"
    }
  ]
  applications = [
    {
      name                  = "discovery-platform-dev"
      repo_url              = "https://github.com/example/discovery.git"
      path                  = "infra/helm/platform"
      target_revision       = "develop"
      value_files           = ["values-dev.yaml"]
      destination_namespace = "discovery-dev"
      sync_prune            = true
      sync_self_heal        = true
    }
  ]
}
