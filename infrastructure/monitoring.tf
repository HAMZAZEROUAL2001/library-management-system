# Configuration de monitoring avec Prometheus et Grafana
resource "kubernetes_namespace" "monitoring" {
  count = var.monitoring_enabled[var.environment] ? 1 : 0

  metadata {
    name = "monitoring"
    labels = {
      name = "monitoring"
    }
  }
}

# ServiceMonitor pour Prometheus Operator
resource "kubernetes_manifest" "service_monitor" {
  count = var.monitoring_enabled[var.environment] ? 1 : 0

  manifest = {
    apiVersion = "monitoring.coreos.com/v1"
    kind       = "ServiceMonitor"
    metadata = {
      name      = "library-management-metrics"
      namespace = kubernetes_namespace.monitoring[0].metadata[0].name
      labels = {
        app         = "library-management"
        environment = var.environment
      }
    }
    spec = {
      selector = {
        matchLabels = {
          app         = "library-management"
          environment = var.environment
        }
      }
      namespaceSelector = {
        matchNames = [kubernetes_namespace.library_app.metadata[0].name]
      }
      endpoints = [
        {
          port     = "metrics"
          interval = "30s"
          path     = "/metrics"
        }
      ]
    }
  }
}

# PodDisruptionBudget pour la haute disponibilité
resource "kubernetes_pod_disruption_budget_v1" "library_app" {
  count = var.environment == "prod" ? 1 : 0

  metadata {
    name      = "library-management-pdb"
    namespace = kubernetes_namespace.library_app.metadata[0].name
    labels = {
      app         = "library-management"
      environment = var.environment
    }
  }

  spec {
    min_available = "50%"
    selector {
      match_labels = {
        app         = "library-management"
        environment = var.environment
      }
    }
  }
}

# ResourceQuota pour limiter l'utilisation des ressources
resource "kubernetes_resource_quota" "library_app" {
  metadata {
    name      = "library-management-quota"
    namespace = kubernetes_namespace.library_app.metadata[0].name
  }

  spec = {
    hard = {
      "requests.cpu"       = var.environment == "prod" ? "2" : "1"
      "requests.memory"    = var.environment == "prod" ? "4Gi" : "2Gi"
      "limits.cpu"         = var.environment == "prod" ? "4" : "2"
      "limits.memory"      = var.environment == "prod" ? "8Gi" : "4Gi"
      "persistentvolumeclaims" = "2"
      "pods"               = var.environment == "prod" ? "20" : "10"
      "services"           = "5"
      "secrets"            = "10"
      "configmaps"         = "10"
    }
  }
}

# LimitRange pour définir les limites par défaut
resource "kubernetes_limit_range" "library_app" {
  metadata {
    name      = "library-management-limits"
    namespace = kubernetes_namespace.library_app.metadata[0].name
  }

  spec {
    limit {
      type = "Container"
      default = {
        cpu    = var.resource_limits[var.environment].cpu_limit
        memory = var.resource_limits[var.environment].memory_limit
      }
      default_request = {
        cpu    = var.resource_limits[var.environment].cpu_request
        memory = var.resource_limits[var.environment].memory_request
      }
    }
  }
}