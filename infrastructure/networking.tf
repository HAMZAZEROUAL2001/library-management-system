# Service principal
resource "kubernetes_service" "library_app" {
  metadata {
    name      = "library-management-service"
    namespace = kubernetes_namespace.library_app.metadata[0].name
    labels = {
      app         = "library-management"
      environment = var.environment
    }
    annotations = {
      "service.beta.kubernetes.io/aws-load-balancer-type" = "nlb"
    }
  }

  spec {
    selector = {
      app         = "library-management"
      environment = var.environment
    }

    port {
      name        = "http"
      port        = 80
      target_port = 8000
      protocol    = "TCP"
    }

    dynamic "port" {
      for_each = var.monitoring_enabled[var.environment] ? [1] : []
      content {
        name        = "metrics"
        port        = 9090
        target_port = 9090
        protocol    = "TCP"
      }
    }

    type = var.environment == "prod" ? "LoadBalancer" : "ClusterIP"
  }
}

# Ingress pour l'exposition externe
resource "kubernetes_ingress_v1" "library_app" {
  count = var.environment != "dev" ? 1 : 0

  metadata {
    name      = "library-management-ingress"
    namespace = kubernetes_namespace.library_app.metadata[0].name
    labels = {
      app         = "library-management"
      environment = var.environment
    }
    annotations = {
      "kubernetes.io/ingress.class"                       = "nginx"
      "nginx.ingress.kubernetes.io/rewrite-target"        = "/"
      "nginx.ingress.kubernetes.io/ssl-redirect"          = var.environment == "prod" ? "true" : "false"
      "cert-manager.io/cluster-issuer"                    = var.environment == "prod" ? "letsencrypt-prod" : "letsencrypt-staging"
      "nginx.ingress.kubernetes.io/rate-limit"            = "100"
      "nginx.ingress.kubernetes.io/rate-limit-window"     = "1m"
      "nginx.ingress.kubernetes.io/proxy-connect-timeout" = "30"
      "nginx.ingress.kubernetes.io/proxy-send-timeout"    = "60"
      "nginx.ingress.kubernetes.io/proxy-read-timeout"    = "60"
    }
  }

  spec {
    dynamic "tls" {
      for_each = var.environment == "prod" ? [1] : []
      content {
        hosts       = [var.ingress_host[var.environment]]
        secret_name = "library-management-tls"
      }
    }

    rule {
      host = var.ingress_host[var.environment]

      http {
        path {
          path      = "/"
          path_type = "Prefix"

          backend {
            service {
              name = kubernetes_service.library_app.metadata[0].name
              port {
                number = 80
              }
            }
          }
        }

        # Path pour les métriques si monitoring activé
        dynamic "path" {
          for_each = var.monitoring_enabled[var.environment] ? [1] : []
          content {
            path      = "/metrics"
            path_type = "Prefix"

            backend {
              service {
                name = kubernetes_service.library_app.metadata[0].name
                port {
                  number = 9090
                }
              }
            }
          }
        }
      }
    }
  }
}

# HorizontalPodAutoscaler pour l'autoscaling
resource "kubernetes_horizontal_pod_autoscaler_v2" "library_app" {
  count = var.environment != "dev" ? 1 : 0

  metadata {
    name      = "library-management-hpa"
    namespace = kubernetes_namespace.library_app.metadata[0].name
    labels = {
      app         = "library-management"
      environment = var.environment
    }
  }

  spec {
    scale_target_ref {
      api_version = "apps/v1"
      kind        = "Deployment"
      name        = kubernetes_deployment.library_app.metadata[0].name
    }

    min_replicas = var.replica_count[var.environment]
    max_replicas = var.environment == "prod" ? 10 : 5

    metric {
      type = "Resource"
      resource {
        name = "cpu"
        target {
          type                = "Utilization"
          average_utilization = 70
        }
      }
    }

    metric {
      type = "Resource"
      resource {
        name = "memory"
        target {
          type                = "Utilization"
          average_utilization = 80
        }
      }
    }

    behavior {
      scale_up {
        stabilization_window_seconds = 60
        policy {
          type          = "Percent"
          value         = 100
          period_seconds = 15
        }
      }

      scale_down {
        stabilization_window_seconds = 300
        policy {
          type          = "Percent"
          value         = 50
          period_seconds = 60
        }
      }
    }
  }
}

# NetworkPolicy pour la sécurité réseau
resource "kubernetes_network_policy" "library_app" {
  count = var.environment == "prod" ? 1 : 0

  metadata {
    name      = "library-management-netpol"
    namespace = kubernetes_namespace.library_app.metadata[0].name
    labels = {
      app         = "library-management"
      environment = var.environment
    }
  }

  spec {
    pod_selector {
      match_labels = {
        app         = "library-management"
        environment = var.environment
      }
    }

    policy_types = ["Ingress", "Egress"]

    ingress {
      from {
        namespace_selector {
          match_labels = {
            name = "ingress-nginx"
          }
        }
      }
      ports {
        port     = "8000"
        protocol = "TCP"
      }
    }

    # Autoriser le trafic vers la base de données
    egress {
      to {
        namespace_selector {
          match_labels = {
            name = "database"
          }
        }
      }
      ports {
        port     = "5432"
        protocol = "TCP"
      }
    }

    # Autoriser le trafic DNS
    egress {
      to {}
      ports {
        port     = "53"
        protocol = "UDP"
      }
    }

    # Autoriser le trafic HTTPS sortant
    egress {
      to {}
      ports {
        port     = "443"
        protocol = "TCP"
      }
    }
  }
}