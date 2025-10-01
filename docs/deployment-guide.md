# Guide de Déploiement - Library Management System

Ce guide complet vous accompagne dans le déploiement du système de gestion de bibliothèque dans différents environnements.

## 🎯 Vue d'ensemble

Le système Library Management System est conçu avec une architecture moderne utilisant:
- **Backend**: FastAPI avec SQLAlchemy
- **Frontend**: React avec TypeScript
- **Base de données**: SQLite (dev) / PostgreSQL (prod)
- **Orchestration**: Kubernetes avec Terraform
- **Monitoring**: Prometheus + Grafana
- **CI/CD**: GitHub Actions

## 🔄 Stratégie de déploiement

### Environnements

1. **Développement (dev)**
   - **But**: Développement local et tests unitaires
   - **Infrastructure**: Minikube ou Docker Desktop
   - **Configuration**: Ressources minimales, monitoring désactivé

2. **Staging (staging)**
   - **But**: Tests d'intégration et validation pré-production
   - **Infrastructure**: Cluster Kubernetes dédié
   - **Configuration**: Configuration proche de la production

3. **Production (prod)**
   - **But**: Environnement de production final
   - **Infrastructure**: Cluster Kubernetes haute disponibilité
   - **Configuration**: Sécurité maximale, monitoring complet

## 🚀 Déploiement étape par étape

### Phase 1: Préparation de l'environnement

#### 1.1 Prérequis système
```bash
# Installer les outils requis
# Kubectl
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl

# Terraform
wget https://releases.hashicorp.com/terraform/1.6.0/terraform_1.6.0_linux_amd64.zip
unzip terraform_1.6.0_linux_amd64.zip
sudo mv terraform /usr/local/bin/

# Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
```

#### 1.2 Configuration du cluster Kubernetes
```bash
# Vérifier la connectivité
kubectl cluster-info
kubectl get nodes

# Créer les namespaces de base
kubectl create namespace ingress-nginx
kubectl create namespace cert-manager
kubectl create namespace monitoring
```

#### 1.3 Installation des composants de base

**Ingress Controller (Nginx)**
```bash
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.8.0/deploy/static/provider/cloud/deploy.yaml
```

**Cert-Manager (pour HTTPS)**
```bash
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml
```

### Phase 2: Configuration des secrets

#### 2.1 Secrets d'application
```bash
# Créer les secrets manuellement pour la production
kubectl create secret generic database-credentials \
  --from-literal=username=library_user \
  --from-literal=password=secure_password_prod \
  -n library-management-prod

kubectl create secret generic app-secrets \
  --from-literal=secret_key=your-super-secret-key-prod \
  --from-literal=jwt_secret=jwt-secret-key-prod \
  --from-literal=api_key=external-api-key-prod \
  -n library-management-prod
```

#### 2.2 Certificats TLS
```yaml
# cert-issuer.yaml
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: admin@example.com
    privateKeySecretRef:
      name: letsencrypt-prod
    solvers:
    - http01:
        ingress:
          class: nginx
```

### Phase 3: Déploiement de l'application

#### 3.1 Construction et push des images
```bash
# Se positionner dans le dossier backend
cd backend

# Construction de l'image
docker build -t your-registry/library-management-system:v1.0.0 .

# Push vers le registry
docker push your-registry/library-management-system:v1.0.0
```

#### 3.2 Déploiement Terraform
```bash
cd infrastructure

# Initialisation
terraform init

# Planification pour production
terraform plan -var-file="environments/prod.tfvars" -out=tfplan-prod

# Application (après validation)
terraform apply tfplan-prod
```

### Phase 4: Vérification et tests

#### 4.1 Tests de santé
```bash
# Vérifier les pods
kubectl get pods -n library-management-prod

# Tester les endpoints de santé
curl -k https://library.example.com/health
curl -k https://library.example.com/health/ready
```

#### 4.2 Tests fonctionnels
```bash
# Test d'authentification
curl -X POST https://library.example.com/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin"}'

# Test des endpoints principaux
curl -H "Authorization: Bearer <token>" https://library.example.com/books/
```

## 🔄 Processus de mise à jour

### Rolling Update
```bash
# Mettre à jour l'image dans Terraform
# environments/prod.tfvars
app_version = "v1.1.0"

# Appliquer la mise à jour
terraform plan -var-file="environments/prod.tfvars"
terraform apply

# Suivre le déploiement
kubectl rollout status deployment/library-management-prod -n library-management-prod
```

### Rollback en cas de problème
```bash
# Rollback automatique
kubectl rollout undo deployment/library-management-prod -n library-management-prod

# Rollback vers une version spécifique
kubectl rollout undo deployment/library-management-prod --to-revision=2 -n library-management-prod
```

## 🔧 Configuration avancée

### Base de données PostgreSQL

#### Installation avec Helm
```bash
helm repo add bitnami https://charts.bitnami.com/bitnami
helm install postgresql bitnami/postgresql \
  --set auth.postgresPassword=secure_password \
  --set auth.database=library_prod \
  --namespace database \
  --create-namespace
```

#### Migration des données
```bash
# Script de migration (à adapter)
kubectl exec -it postgresql-0 -n database -- psql -U postgres -d library_prod -f /migrations/init.sql
```

### Monitoring avancé

#### Installation Prometheus + Grafana
```bash
cd monitoring
docker-compose -f docker-compose.monitoring.yml up -d
```

#### Configuration des alertes
```yaml
# Webhook pour Slack/Teams
- name: 'slack-notifications'
  slack_configs:
  - api_url: 'YOUR_SLACK_WEBHOOK_URL'
    channel: '#alerts'
    title: 'Library Management Alert'
    text: '{{ range .Alerts }}{{ .Annotations.summary }}{{ end }}'
```

## 🚨 Procédures d'urgence

### Incident majeur
1. **Évaluation rapide**
   ```bash
   kubectl get pods,svc,ingress -n library-management-prod
   kubectl logs -l app=library-management -n library-management-prod --tail=100
   ```

2. **Rollback immédiat**
   ```bash
   kubectl rollout undo deployment/library-management-prod -n library-management-prod
   ```

3. **Communication**
   - Notifier les parties prenantes
   - Documenter l'incident
   - Planifier la post-mortem

### Sauvegarde et restauration
```bash
# Sauvegarde de la base de données
kubectl exec postgresql-0 -n database -- pg_dump -U postgres library_prod > backup-$(date +%Y%m%d).sql

# Restauration
kubectl exec -i postgresql-0 -n database -- psql -U postgres library_prod < backup-20231201.sql
```

## 📊 Métriques et KPIs

### Métriques techniques
- **Disponibilité**: > 99.9%
- **Temps de réponse**: < 200ms (95e percentile)
- **Taux d'erreur**: < 0.1%
- **Utilisation CPU**: < 70%
- **Utilisation mémoire**: < 80%

### Métriques métier
- **Connexions utilisateurs**: Suivi quotidien
- **Emprunts de livres**: Tendances mensuelles
- **Recherches**: Analyse des patterns

## 🔐 Sécurité en production

### Checklist sécurité
- [ ] Secrets chiffrés et tournés régulièrement
- [ ] NetworkPolicy configurées
- [ ] PodSecurityPolicy appliquées
- [ ] RBAC avec principe du moindre privilège
- [ ] Images scannées pour les vulnérabilités
- [ ] Certificats TLS valides
- [ ] Monitoring de sécurité activé

### Audit et conformité
```bash
# Audit des permissions RBAC
kubectl auth can-i --list --as=system:serviceaccount:library-management-prod:library-management-sa

# Vérification des politiques réseau
kubectl get networkpolicy -n library-management-prod
```

## 📈 Optimisation des performances

### Tuning Kubernetes
```yaml
# Optimisation des ressources
resources:
  requests:
    memory: "512Mi"
    cpu: "500m"
  limits:
    memory: "1Gi"
    cpu: "1000m"

# Configuration JVM (si Java)
env:
- name: JAVA_OPTS
  value: "-Xmx768m -XX:+UseG1GC"
```

### Optimisation base de données
```sql
-- Index pour les requêtes fréquentes
CREATE INDEX idx_books_author ON books(author);
CREATE INDEX idx_loans_user_id ON loans(user_id);
CREATE INDEX idx_loans_book_id ON loans(book_id);

-- Statistiques et vacuum
ANALYZE;
VACUUM ANALYZE;
```

## 🧪 Tests de charge

### Tests avec K6
```javascript
import http from 'k6/http';
import { check } from 'k6';

export let options = {
  stages: [
    { duration: '2m', target: 100 },
    { duration: '5m', target: 100 },
    { duration: '2m', target: 200 },
    { duration: '5m', target: 200 },
    { duration: '2m', target: 0 },
  ],
};

export default function () {
  let response = http.get('https://library.example.com/books/');
  check(response, {
    'status is 200': (r) => r.status === 200,
    'response time < 500ms': (r) => r.timings.duration < 500,
  });
}
```

### Exécution des tests
```bash
k6 run --out influxdb=http://localhost:8086/k6 load-test.js
```

## 📋 Checklist de déploiement

### Pré-déploiement
- [ ] Tests unitaires passent
- [ ] Tests d'intégration passent
- [ ] Code review terminée
- [ ] Documentation mise à jour
- [ ] Plan de rollback préparé

### Déploiement
- [ ] Sauvegarde effectuée
- [ ] Maintenance mode activé si nécessaire
- [ ] Déploiement exécuté
- [ ] Tests de fumée passent
- [ ] Monitoring vérifié

### Post-déploiement
- [ ] Métriques normales
- [ ] Logs sans erreur
- [ ] Fonctionnalités testées
- [ ] Équipe notifiée
- [ ] Documentation déploiement mise à jour

## 🔗 Ressources utiles

- [Kubernetes Best Practices](https://kubernetes.io/docs/concepts/configuration/overview/)
- [FastAPI Deployment Guide](https://fastapi.tiangolo.com/deployment/)
- [PostgreSQL Performance Tuning](https://wiki.postgresql.org/wiki/Performance_Optimization)
- [Prometheus Monitoring](https://prometheus.io/docs/practices/naming/)
- [Grafana Dashboard Examples](https://grafana.com/grafana/dashboards/)

---

*Ce guide doit être maintenu à jour à chaque évolution de l'infrastructure ou des processus de déploiement.*