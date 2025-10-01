# Configuration pour l'environnement de staging
environment = "staging"
cluster_name = "staging-cluster"
app_version = "v1.0.0"

# Réplicas pour la haute disponibilité en staging
replica_count = {
  dev     = 1
  staging = 2
  prod    = 3
}

# Ressources modérées pour staging
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

# Configuration base de données staging
database_config = {
  staging = {
    host     = "postgres-staging.internal"
    port     = 5432
    name     = "library_staging"
    ssl_mode = "require"
  }
}

# Monitoring activé en staging
monitoring_enabled = {
  dev     = false
  staging = true
  prod    = true
}

# Nom d'hôte staging
ingress_host = {
  staging = "library-staging.example.com"
}