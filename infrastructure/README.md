# Infrastructure - Library Management System

Ce dossier contient toute l'infrastructure as Code (IaC) pour déployer le système de gestion de bibliothèque sur Kubernetes avec Terraform.

## 🏗️ Architecture

L'infrastructure est conçue pour supporter plusieurs environnements (dev, staging, prod) avec des configurations optimisées pour chaque cas d'usage:

- **Dev**: Configuration minimale pour le développement local
- **Staging**: Configuration intermédiaire pour les tests d'intégration
- **Prod**: Configuration complète avec haute disponibilité et sécurité renforcée

## 📁 Structure des fichiers

```
infrastructure/
├── main.tf                     # Configuration principale Terraform
├── variables.tf                # Variables et leur configuration
├── secrets.tf                  # Gestion sécurisée des secrets
├── deployment.tf               # Déploiement Kubernetes avec RBAC
├── networking.tf               # Services, Ingress, NetworkPolicy
├── monitoring.tf               # Configuration monitoring et ressources
├── outputs.tf                  # Outputs pour informations de déploiement
├── deploy.sh                   # Script de déploiement (Linux/Mac)
├── deploy.bat                  # Script de déploiement (Windows)
└── environments/
    ├── dev.tfvars             # Variables pour développement
    ├── staging.tfvars         # Variables pour staging
    └── prod.tfvars            # Variables pour production
```

## 🚀 Déploiement rapide

### Prérequis

1. **Outils requis**:
   - [Kubernetes CLI (kubectl)](https://kubernetes.io/docs/tasks/tools/)
   - [Terraform](https://www.terraform.io/downloads.html) >= 1.0.0
   - [Docker](https://docs.docker.com/get-docker/)
   - Accès à un cluster Kubernetes

2. **Configuration kubectl**:
   ```bash
   kubectl config current-context
   kubectl cluster-info
   ```

### Déploiement automatisé

#### Linux/Mac
```bash
# Rendre le script exécutable
chmod +x deploy.sh

# Déployer en développement
./deploy.sh dev

# Déployer en staging
./deploy.sh staging

# Déployer en production
./deploy.sh prod
```

#### Windows
```cmd
# Déployer en développement
deploy.bat dev

# Déployer en staging
deploy.bat staging

# Déployer en production
deploy.bat prod
```

### Déploiement manuel

```bash
# 1. Construire l'image Docker
cd ../backend
docker build -t library-management-system:latest .

# 2. Initialiser Terraform
cd ../infrastructure
terraform init

# 3. Planifier le déploiement
terraform plan -var-file="environments/dev.tfvars" -out=tfplan

# 4. Appliquer le déploiement
terraform apply tfplan

# 5. Vérifier le déploiement
kubectl get pods -n $(terraform output -raw namespace)
```

## 🔧 Configuration par environnement

### Développement (dev)
- **Réplicas**: 1
- **Ressources**: CPU 50m-100m, RAM 64Mi-128Mi
- **Monitoring**: Désactivé
- **Base de données**: SQLite locale
- **Ingress**: Désactivé (ClusterIP uniquement)

### Staging (staging)
- **Réplicas**: 2
- **Ressources**: CPU 200m-500m, RAM 256Mi-512Mi
- **Monitoring**: Activé avec Prometheus
- **Base de données**: PostgreSQL
- **Ingress**: Activé avec certificats staging
- **Autoscaling**: HPA configuré

### Production (prod)
- **Réplicas**: 3 (minimum)
- **Ressources**: CPU 500m-1000m, RAM 512Mi-1Gi
- **Monitoring**: Complet avec alertes
- **Base de données**: PostgreSQL avec SSL
- **Ingress**: HTTPS avec certificats Let's Encrypt
- **Sécurité**: NetworkPolicy, PodSecurityPolicy
- **Haute disponibilité**: PodDisruptionBudget

## 🔐 Gestion des secrets

### Secrets Kubernetes automatiques
- **database-credentials**: Identifiants base de données
- **app-secrets**: Clés secrètes de l'application (JWT, API keys)

### Configuration non-sensible
- **app-config**: ConfigMap avec configuration environnementale

### Bonnes pratiques
1. **Jamais de secrets en plain text** dans les fichiers Terraform
2. **Rotation régulière** des secrets en production
3. **Utilisation de outils externes** comme HashiCorp Vault pour la production

## 📊 Monitoring et observabilité

### Métriques Prometheus
- Métriques HTTP (taux, latence, erreurs)
- Métriques métier (utilisateurs, livres, emprunts)
- Métriques système (CPU, mémoire, disque)
- Métriques base de données

### Dashboards Grafana
- Dashboard principal avec vues d'ensemble
- Alertes configurées pour les métriques critiques

### Configuration monitoring
```yaml
# Activé automatiquement en staging/prod
monitoring_enabled = {
  dev     = false
  staging = true
  prod    = true
}
```

## 🌐 Réseau et sécurité

### Services
- **ClusterIP**: Pour dev (accès interne uniquement)
- **LoadBalancer**: Pour staging/prod

### Ingress
- **Nginx Ingress Controller** requis
- **Certificats TLS** automatiques avec cert-manager
- **Rate limiting** configuré

### Sécurité réseau
- **NetworkPolicy**: Restrictions de trafic en production
- **PodSecurityContext**: Contexte de sécurité non-root
- **RBAC**: Service Account avec permissions minimales

## 📈 Autoscaling

### Horizontal Pod Autoscaler (HPA)
```yaml
# Configuration automatique pour staging/prod
min_replicas: 2-3 (selon environnement)
max_replicas: 5-10 (selon environnement)
metrics:
  - CPU: 70% utilisation
  - Memory: 80% utilisation
```

### Comportement de scaling
- **Scale up**: Rapide (15s) si nécessaire
- **Scale down**: Progressif (5min) pour stabilité

## 🔍 Commandes utiles

### Après déploiement
```bash
# Obtenir les informations de connexion
terraform output service_urls

# Voir les pods
kubectl get pods -n $(terraform output -raw namespace)

# Suivre les logs
kubectl logs -f -l app=library-management -n $(terraform output -raw namespace)

# Port forwarding pour accès local
kubectl port-forward -n $(terraform output -raw namespace) svc/library-management-service 8080:80
```

### Debug et troubleshooting
```bash
# Événements du namespace
kubectl get events -n $(terraform output -raw namespace) --sort-by='.lastTimestamp'

# Décrire un pod problématique
kubectl describe pod <pod-name> -n $(terraform output -raw namespace)

# Accéder à un conteneur
kubectl exec -it <pod-name> -n $(terraform output -raw namespace) -- /bin/bash

# Vérifier les métriques
kubectl top pods -n $(terraform output -raw namespace)
```

## 🔄 Gestion des mises à jour

### Rolling Updates
- **Stratégie**: RollingUpdate avec max 25% unavailable
- **Health checks**: Probes configurées pour zero-downtime
- **Rollback**: `kubectl rollout undo deployment/<name>`

### Versions d'image
- **Dev**: `latest` tag
- **Staging/Prod**: Tags versionnés (ex: `v1.0.0`)

## 🧹 Nettoyage

### Suppression d'un environnement
```bash
# Supprimer les ressources Terraform
terraform destroy -var-file="environments/dev.tfvars"

# Nettoyer les images Docker locales
docker rmi library-management-system:latest
```

### Suppression complète
```bash
# Supprimer le namespace (toutes les ressources)
kubectl delete namespace library-management-dev

# Nettoyer l'état Terraform
rm terraform.tfstate*
rm .terraform.lock.hcl
rm -rf .terraform/
```

## 🔧 Personnalisation

### Modification des ressources
Éditez les fichiers `environments/*.tfvars`:

```hcl
# Exemple: augmenter les ressources
resource_limits = {
  prod = {
    cpu_request    = "1000m"
    memory_request = "1Gi"
    cpu_limit      = "2000m"
    memory_limit   = "2Gi"
  }
}
```

### Ajout d'un nouvel environnement
1. Créer `environments/nouvel-env.tfvars`
2. Configurer les variables appropriées
3. Déployer avec `./deploy.sh nouvel-env`

## 📚 Ressources supplémentaires

- [Documentation Terraform Kubernetes Provider](https://registry.terraform.io/providers/hashicorp/kubernetes/latest/docs)
- [Kubernetes Best Practices](https://kubernetes.io/docs/concepts/configuration/overview/)
- [Prometheus Monitoring](https://prometheus.io/docs/introduction/overview/)
- [Nginx Ingress Controller](https://kubernetes.github.io/ingress-nginx/)

## 🤝 Support

Pour des questions ou problèmes:
1. Vérifiez les logs avec `kubectl logs`
2. Consultez les événements avec `kubectl get events`
3. Validez la configuration avec `terraform plan`
4. Référez-vous aux outputs Terraform pour les commandes utiles