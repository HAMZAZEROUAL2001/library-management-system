# Configuration pour l'environnement de production
environment = "prod"
cluster_name = "production-cluster"
app_version = "v1.0.0"

# Réplicas pour la haute disponibilité en production
replica_count = {
  dev     = 1
  staging = 2
  prod    = 3
}

# Ressources complètes pour production
resource_limits = {
  dev = {
    cpu_request    = "50m"
    memory_request = "64Mi"
    cpu_limit      = "100m"
    memory_limit   = "128Mi"
  }
  staging = {
    cpu_request    = "200m"
    memory_request = "256Mi"
    cpu_limit      = "500m"
    memory_limit   = "512Mi"
  }
  prod = {
    cpu_request    = "500m"
    memory_request = "512Mi"
    cpu_limit      = "1000m"
    memory_limit   = "1Gi"
  }
}

# Configuration base de données production
database_config = {
  prod = {
    host     = "postgres-prod.internal"
    port     = 5432
    name     = "library_prod"
    ssl_mode = "require"
  }
}

# Monitoring activé en production
monitoring_enabled = {
  dev     = false
  staging = true
  prod    = true
}

# Nom d'hôte production
ingress_host = {
  prod = "library.example.com"
}