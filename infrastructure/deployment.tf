# Deployment amélioré avec gestion d'environnements
resource "kubernetes_deployment" "library_app" {
  metadata {
    name      = "library-management-${var.environment}"
    namespace = kubernetes_namespace.library_app.metadata[0].name
    labels = {
      app         = "library-management"
      environment = var.environment
      version     = var.app_version
    }
    annotations = {
      "deployment.kubernetes.io/revision" = "1"
    }
  }

  spec {
    replicas = var.replica_count[var.environment]

    selector {
      match_labels = {
        app         = "library-management"
        environment = var.environment
      }
    }

    template {
      metadata {
        labels = {
          app         = "library-management"
          environment = var.environment
          version     = var.app_version
        }
        annotations = {
          "cluster-autoscaler.kubernetes.io/safe-to-evict" = "true"
          "prometheus.io/scrape"                           = tostring(var.monitoring_enabled[var.environment])
          "prometheus.io/port"                             = "9090"
          "prometheus.io/path"                             = "/metrics"
        }
      }

      spec {
        # Configuration de sécurité
        security_context {
          run_as_non_root = true
          run_as_user     = 1000
          fs_group        = 2000
        }

        # Service Account pour RBAC
        service_account_name = kubernetes_service_account.library_app.metadata[0].name

        container {
          name  = "library-app"
          image = "library-management-system:${var.app_version}"
          
          image_pull_policy = var.environment == "prod" ? "Always" : "IfNotPresent"

          # Ports
          port {
            name           = "http"
            container_port = 8000
            protocol       = "TCP"
          }

          dynamic "port" {
            for_each = var.monitoring_enabled[var.environment] ? [1] : []
            content {
              name           = "metrics"
              container_port = 9090
              protocol       = "TCP"
            }
          }

          # Variables d'environnement depuis ConfigMap
          env_from {
            config_map_ref {
              name = kubernetes_config_map.app_config.metadata[0].name
            }
          }

          # Variables d'environnement depuis Secrets
          env {
            name = "DATABASE_USERNAME"
            value_from {
              secret_key_ref {
                name = kubernetes_secret.database_credentials.metadata[0].name
                key  = "username"
              }
            }
          }

          env {
            name = "DATABASE_PASSWORD"
            value_from {
              secret_key_ref {
                name = kubernetes_secret.database_credentials.metadata[0].name
                key  = "password"
              }
            }
          }

          env {
            name = "SECRET_KEY"
            value_from {
              secret_key_ref {
                name = kubernetes_secret.app_secrets.metadata[0].name
                key  = "secret_key"
              }
            }
          }

          env {
            name = "JWT_SECRET_KEY"
            value_from {
              secret_key_ref {
                name = kubernetes_secret.app_secrets.metadata[0].name
                key  = "jwt_secret"
              }
            }
          }

          # Variables d'environnement statiques
          env {
            name  = "PYTHONUNBUFFERED"
            value = "1"
          }

          # Probes améliorées
          liveness_probe {
            http_get {
              path   = "/health"
              port   = 8000
              scheme = "HTTP"
            }
            initial_delay_seconds = var.environment == "prod" ? 60 : 30
            period_seconds        = 15
            timeout_seconds       = 5
            failure_threshold     = 3
            success_threshold     = 1
          }

          readiness_probe {
            http_get {
              path   = "/health/ready"
              port   = 8000
              scheme = "HTTP"
            }
            initial_delay_seconds = var.environment == "prod" ? 30 : 15
            period_seconds        = 10
            timeout_seconds       = 3
            failure_threshold     = 3
            success_threshold     = 1
          }

          # Startup probe pour applications qui mettent du temps à démarrer
          startup_probe {
            http_get {
              path   = "/health"
              port   = 8000
              scheme = "HTTP"
            }
            initial_delay_seconds = 10
            period_seconds        = 10
            timeout_seconds       = 5
            failure_threshold     = 30
            success_threshold     = 1
          }

          # Ressources configurées par environnement
          resources {
            requests = {
              cpu    = var.resource_limits[var.environment].cpu_request
              memory = var.resource_limits[var.environment].memory_request
            }
            limits = {
              cpu    = var.resource_limits[var.environment].cpu_limit
              memory = var.resource_limits[var.environment].memory_limit
            }
          }

          # Security context
          security_context {
            allow_privilege_escalation = false
            read_only_root_filesystem  = true
            run_as_non_root           = true
            run_as_user               = 1000
            capabilities {
              drop = ["ALL"]
            }
          }

          # Volume mounts
          volume_mount {
            name       = "tmp"
            mount_path = "/tmp"
          }

          volume_mount {
            name       = "logs"
            mount_path = "/app/logs"
          }
        }

        # Volumes
        volume {
          name = "tmp"
          empty_dir {}
        }

        volume {
          name = "logs"
          empty_dir {}
        }

        # Configuration avancée
        restart_policy                   = "Always"
        termination_grace_period_seconds = 30

        # Affinité et anti-affinité pour la distribution des pods
        affinity {
          pod_anti_affinity {
            preferred_during_scheduling_ignored_during_execution {
              weight = 100
              pod_affinity_term {
                label_selector {
                  match_expressions {
                    key      = "app"
                    operator = "In"
                    values   = ["library-management"]
                  }
                }
                topology_key = "kubernetes.io/hostname"
              }
            }
          }
        }

        # Tolérance aux taints
        dynamic "toleration" {
          for_each = var.environment == "prod" ? [1] : []
          content {
            key      = "node-type"
            operator = "Equal"
            value    = "production"
            effect   = "NoSchedule"
          }
        }
      }
    }

    strategy {
      type = "RollingUpdate"
      rolling_update {
        max_unavailable = var.environment == "prod" ? "25%" : "50%"
        max_surge       = var.environment == "prod" ? "25%" : "50%"
      }
    }
  }

  depends_on = [
    kubernetes_config_map.app_config,
    kubernetes_secret.database_credentials,
    kubernetes_secret.app_secrets
  ]
}

# Service Account avec RBAC
resource "kubernetes_service_account" "library_app" {
  metadata {
    name      = "library-management-sa"
    namespace = kubernetes_namespace.library_app.metadata[0].name
    labels = {
      app         = "library-management"
      environment = var.environment
    }
  }
}

# Role pour les permissions spécifiques
resource "kubernetes_role" "library_app" {
  metadata {
    name      = "library-management-role"
    namespace = kubernetes_namespace.library_app.metadata[0].name
  }

  rule {
    api_groups = [""]
    resources  = ["configmaps", "secrets"]
    verbs      = ["get", "list"]
  }

  rule {
    api_groups = [""]
    resources  = ["events"]
    verbs      = ["create"]
  }
}

# RoleBinding
resource "kubernetes_role_binding" "library_app" {
  metadata {
    name      = "library-management-binding"
    namespace = kubernetes_namespace.library_app.metadata[0].name
  }

  role_ref {
    api_group = "rbac.authorization.k8s.io"
    kind      = "Role"
    name      = kubernetes_role.library_app.metadata[0].name
  }

  subject {
    kind      = "ServiceAccount"
    name      = kubernetes_service_account.library_app.metadata[0].name
    namespace = kubernetes_namespace.library_app.metadata[0].name
  }
}