# Outputs for deployment information
output "namespace" {
  description = "Namespace where the application is deployed"
  value       = kubernetes_namespace.library_app.metadata[0].name
}

output "service_name" {
  description = "Name of the Kubernetes service"
  value       = kubernetes_service.library_app.metadata[0].name
}

output "deployment_name" {
  description = "Name of the Kubernetes deployment"
  value       = kubernetes_deployment.library_app.metadata[0].name
}

output "environment" {
  description = "Environment where the application is deployed"
  value       = var.environment
}

output "replicas" {
  description = "Number of replicas configured"
  value       = var.replica_count[var.environment]
}

output "ingress_host" {
  description = "Ingress host for external access"
  value       = var.environment != "dev" ? var.ingress_host[var.environment] : "N/A (ClusterIP only)"
}

output "monitoring_enabled" {
  description = "Whether monitoring is enabled"
  value       = var.monitoring_enabled[var.environment]
}

output "resource_limits" {
  description = "Resource limits configured for the environment"
  value = {
    cpu_request    = var.resource_limits[var.environment].cpu_request
    memory_request = var.resource_limits[var.environment].memory_request  
    cpu_limit      = var.resource_limits[var.environment].cpu_limit
    memory_limit   = var.resource_limits[var.environment].memory_limit
  }
  sensitive = false
}

output "service_urls" {
  description = "URLs to access the application"
  value = {
    internal = "http://${kubernetes_service.library_app.metadata[0].name}.${kubernetes_namespace.library_app.metadata[0].name}.svc.cluster.local"
    external = var.environment != "dev" ? "https://${var.ingress_host[var.environment]}" : "kubectl port-forward required"
  }
}

output "kubectl_commands" {
  description = "Useful kubectl commands for this deployment"
  value = {
    get_pods        = "kubectl get pods -n ${kubernetes_namespace.library_app.metadata[0].name}"
    get_services    = "kubectl get services -n ${kubernetes_namespace.library_app.metadata[0].name}"
    get_ingress     = var.environment != "dev" ? "kubectl get ingress -n ${kubernetes_namespace.library_app.metadata[0].name}" : "N/A"
    port_forward    = "kubectl port-forward -n ${kubernetes_namespace.library_app.metadata[0].name} svc/${kubernetes_service.library_app.metadata[0].name} 8080:80"
    view_logs       = "kubectl logs -n ${kubernetes_namespace.library_app.metadata[0].name} -l app=library-management -f"
    scale_deployment = "kubectl scale deployment ${kubernetes_deployment.library_app.metadata[0].name} --replicas=X -n ${kubernetes_namespace.library_app.metadata[0].name}"
  }
}