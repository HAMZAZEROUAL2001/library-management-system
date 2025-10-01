# Gestion sécurisée des secrets avec Kubernetes Secret
resource "kubernetes_secret" "database_credentials" {
  metadata {
    name      = "database-credentials"
    namespace = kubernetes_namespace.library_app.metadata[0].name
    labels = {
      app         = "library-management"
      environment = var.environment
    }
  }

  data = {
    username = base64encode("library_user")
    password = base64encode("secure_password_${var.environment}")
  }

  type = "Opaque"
}

resource "kubernetes_secret" "app_secrets" {
  metadata {
    name      = "app-secrets"
    namespace = kubernetes_namespace.library_app.metadata[0].name
    labels = {
      app         = "library-management"
      environment = var.environment
    }
  }

  data = {
    secret_key    = base64encode("your-super-secret-key-${var.environment}")
    jwt_secret    = base64encode("jwt-secret-key-${var.environment}")
    api_key       = base64encode("external-api-key-${var.environment}")
  }

  type = "Opaque"
}

# ConfigMap pour la configuration non-sensible
resource "kubernetes_config_map" "app_config" {
  metadata {
    name      = "app-config"
    namespace = kubernetes_namespace.library_app.metadata[0].name
    labels = {
      app         = "library-management"
      environment = var.environment
    }
  }

  data = {
    environment   = var.environment
    database_host = var.database_config[var.environment].host
    database_port = tostring(var.database_config[var.environment].port)
    database_name = var.database_config[var.environment].name
    database_ssl  = var.database_config[var.environment].ssl_mode
    
    # Configuration de logging
    log_level     = var.environment == "prod" ? "INFO" : "DEBUG"
    log_format    = "json"
    
    # Configuration des cors
    cors_origins  = var.environment == "prod" ? "https://${var.ingress_host[var.environment]}" : "*"
    
    # Configuration monitoring
    monitoring_enabled = tostring(var.monitoring_enabled[var.environment])
    metrics_port      = "9090"
  }
}