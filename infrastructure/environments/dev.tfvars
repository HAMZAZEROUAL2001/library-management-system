# Configuration pour l'environnement de développement
environment = "dev"
cluster_name = "minikube"
app_version = "latest"

# Un seul replica pour le dev
replica_count = {
  dev     = 1
  staging = 2
  prod    = 3
}

# Ressources minimales pour le dev
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

# Configuration base de données locale pour le dev
database_config = {
  dev = {
    host     = "localhost"
    port     = 5432
    name     = "library_dev"
    ssl_mode = "disable"
  }
}

# Monitoring désactivé en dev
monitoring_enabled = {
  dev     = false
  staging = true
  prod    = true
}

# Nom d'hôte local
ingress_host = {
  dev = "library-dev.local"
}