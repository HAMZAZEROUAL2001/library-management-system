# Variables pour différents environnements
variable "environment" {
  description = "Environnement de déploiement (dev, staging, prod)"
  type        = string
  default     = "dev"
  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "L'environnement doit être dev, staging, ou prod."
  }
}

variable "cluster_name" {
  description = "Nom du cluster Kubernetes"
  type        = string
  default     = "minikube"
}

variable "app_version" {
  description = "Version de l'application"
  type        = string
  default     = "latest"
}

variable "replica_count" {
  description = "Nombre de réplicas par environnement"
  type        = map(number)
  default = {
    dev     = 1
    staging = 2
    prod    = 3
  }
}

variable "resource_limits" {
  description = "Limites de ressources par environnement"
  type = map(object({
    cpu_request    = string
    memory_request = string
    cpu_limit      = string
    memory_limit   = string
  }))
  default = {
    dev = {
      cpu_request    = "100m"
      memory_request = "128Mi"
      cpu_limit      = "200m"
      memory_limit   = "256Mi"
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
}

variable "database_config" {
  description = "Configuration de la base de données par environnement"
  type = map(object({
    host     = string
    port     = number
    name     = string
    ssl_mode = string
  }))
  default = {
    dev = {
      host     = "localhost"
      port     = 5432
      name     = "library_dev"
      ssl_mode = "disable"
    }
    staging = {
      host     = "postgres-staging.internal"
      port     = 5432
      name     = "library_staging"
      ssl_mode = "require"
    }
    prod = {
      host     = "postgres-prod.internal"
      port     = 5432
      name     = "library_prod"
      ssl_mode = "require"
    }
  }
}

variable "monitoring_enabled" {
  description = "Activer le monitoring par environnement"
  type        = map(bool)
  default = {
    dev     = false
    staging = true
    prod    = true
  }
}

variable "ingress_host" {
  description = "Nom d'hôte pour l'ingress par environnement"
  type        = map(string)
  default = {
    dev     = "library-dev.local"
    staging = "library-staging.example.com"
    prod    = "library.example.com"
  }
}