# Guide de déploiement

Ce guide couvre tous les aspects du déploiement du système de gestion de bibliothèque, du développement à la production.

## Sommaire

1. [Stratégies de déploiement](#stratégies-de-déploiement)
2. [Déploiement local](#déploiement-local)
3. [Déploiement Docker](#déploiement-docker)
4. [Déploiement Kubernetes](#déploiement-kubernetes)
5. [Déploiement cloud](#déploiement-cloud)
6. [CI/CD](#cicd)
7. [Monitoring et logs](#monitoring-et-logs)
8. [Sécurité](#sécurité)
9. [Maintenance](#maintenance)

## Stratégies de déploiement

### Environnements

| Environnement | Usage | Configuration |
|---------------|--------|---------------|
| **Development** | Développement local | SQLite, debug activé |
| **Staging** | Tests pré-production | PostgreSQL, configuration proche production |
| **Production** | Utilisateurs finaux | PostgreSQL, optimisations performance |

### Types de déploiement

1. **Rolling Deployment** : Mise à jour progressive sans interruption
2. **Blue-Green Deployment** : Deux environnements identiques
3. **Canary Deployment** : Déploiement graduel sur un sous-ensemble

## Déploiement local

### Configuration développement

```bash
# Backend
cd backend
cp .env.example .env
# Modifier DATABASE_URL, SECRET_KEY, etc.

# Frontend
cd frontend
cp .env.example .env
# Modifier REACT_APP_API_URL
```

### Démarrage manuel

```bash
# Terminal 1 - Backend
cd backend
source venv/bin/activate
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2 - Frontend
cd frontend
npm start
```

### Script de démarrage automatique

**start-dev.sh** :
```bash
#!/bin/bash
set -e

echo "🚀 Démarrage du système de gestion de bibliothèque"

# Vérifier les dépendances
command -v python3 >/dev/null 2>&1 || { echo "Python3 requis"; exit 1; }
command -v node >/dev/null 2>&1 || { echo "Node.js requis"; exit 1; }

# Backend
echo "📚 Démarrage du backend..."
cd backend
if [ ! -d "venv" ]; then
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

uvicorn main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# Frontend
echo "🎨 Démarrage du frontend..."
cd ../frontend
if [ ! -d "node_modules" ]; then
    npm install
fi

npm start &
FRONTEND_PID=$!

echo "✅ Services démarrés:"
echo "   Backend: http://localhost:8000"
echo "   Frontend: http://localhost:3000"
echo "   API Docs: http://localhost:8000/docs"

# Attendre l'arrêt
trap "kill $BACKEND_PID $FRONTEND_PID" EXIT
wait
```

## Déploiement Docker

### Configuration Docker Compose

**docker-compose.yml** :
```yaml
version: '3.8'

services:
  backend:
    build: 
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - SECRET_KEY=${SECRET_KEY:-changeme}
      - DATABASE_URL=postgresql://postgres:password@db:5432/library
    depends_on:
      - db
    volumes:
      - ./backend/logs:/app/logs
    restart: unless-stopped

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "3000:80"
    environment:
      - REACT_APP_API_URL=http://localhost:8000
    depends_on:
      - backend
    restart: unless-stopped

  db:
    image: postgres:13
    environment:
      - POSTGRES_DB=library
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./database/init.sql:/docker-entrypoint-initdb.d/init.sql
    restart: unless-stopped

volumes:
  postgres_data:
```

### Configuration production

**docker-compose.prod.yml** :
```yaml
version: '3.8'

services:
  backend:
    build: 
      context: ./backend
      dockerfile: Dockerfile.prod
    environment:
      - SECRET_KEY=${SECRET_KEY}
      - DATABASE_URL=${DATABASE_URL}
      - CORS_ORIGINS=${CORS_ORIGINS}
    deploy:
      replicas: 2
      resources:
        limits:
          cpus: '0.5'
          memory: 512M
    restart: always

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.prod
      args:
        - REACT_APP_API_URL=${FRONTEND_API_URL}
    deploy:
      replicas: 2
      resources:
        limits:
          cpus: '0.25'
          memory: 256M
    restart: always

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./nginx/ssl:/etc/nginx/ssl
    depends_on:
      - backend
      - frontend
    restart: always
```

### Scripts de déploiement Docker

**deploy-docker.sh** :
```bash
#!/bin/bash
set -e

ENVIRONMENT=${1:-development}

echo "🐳 Déploiement Docker - Environnement: $ENVIRONMENT"

# Vérifier Docker
command -v docker >/dev/null 2>&1 || { echo "Docker requis"; exit 1; }
command -v docker-compose >/dev/null 2>&1 || { echo "Docker Compose requis"; exit 1; }

# Arrêter les services existants
echo "🛑 Arrêt des services existants..."
docker-compose down

# Build des images
echo "🔨 Build des images..."
docker-compose build --no-cache

# Variables d'environnement
if [ "$ENVIRONMENT" = "production" ]; then
    if [ ! -f ".env.prod" ]; then
        echo "❌ Fichier .env.prod requis pour la production"
        exit 1
    fi
    export $(cat .env.prod | xargs)
    COMPOSE_FILE="docker-compose.yml:docker-compose.prod.yml"
else
    export $(cat .env.example | xargs)
    COMPOSE_FILE="docker-compose.yml"
fi

# Démarrage
echo "🚀 Démarrage des services..."
docker-compose -f $COMPOSE_FILE up -d

# Vérification
echo "🔍 Vérification des services..."
sleep 10
docker-compose ps

echo "✅ Déploiement terminé!"
echo "   Backend: http://localhost:8000"
echo "   Frontend: http://localhost:3000"
```

## Déploiement Kubernetes

### Prérequis

```bash
# Installer kubectl
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
chmod +x kubectl
sudo mv kubectl /usr/local/bin/

# Installer Helm
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
```

### Configuration Terraform

**infrastructure/main.tf** :
```hcl
terraform {
  required_providers {
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.0"
    }
  }
}

provider "kubernetes" {
  config_path = "~/.kube/config"
}

# Namespace
resource "kubernetes_namespace" "library" {
  metadata {
    name = "library-management"
    labels = {
      app = "library-system"
    }
  }
}

# ConfigMap
resource "kubernetes_config_map" "app_config" {
  metadata {
    name      = "app-config"
    namespace = kubernetes_namespace.library.metadata[0].name
  }

  data = {
    DATABASE_URL = var.database_url
    CORS_ORIGINS = var.cors_origins
  }
}

# Secret
resource "kubernetes_secret" "app_secrets" {
  metadata {
    name      = "app-secrets"
    namespace = kubernetes_namespace.library.metadata[0].name
  }

  data = {
    SECRET_KEY = base64encode(var.secret_key)
  }
}

# Backend Deployment
resource "kubernetes_deployment" "backend" {
  metadata {
    name      = "backend-deployment"
    namespace = kubernetes_namespace.library.metadata[0].name
  }

  spec {
    replicas = 2

    selector {
      match_labels = {
        app = "backend"
      }
    }

    template {
      metadata {
        labels = {
          app = "backend"
        }
      }

      spec {
        container {
          image = "library-backend:latest"
          name  = "backend"
          
          port {
            container_port = 8000
          }

          env_from {
            config_map_ref {
              name = kubernetes_config_map.app_config.metadata[0].name
            }
          }

          env_from {
            secret_ref {
              name = kubernetes_secret.app_secrets.metadata[0].name
            }
          }

          resources {
            limits = {
              cpu    = "500m"
              memory = "512Mi"
            }
            requests = {
              cpu    = "250m"
              memory = "256Mi"
            }
          }

          liveness_probe {
            http_get {
              path = "/health"
              port = 8000
            }
            initial_delay_seconds = 30
            period_seconds        = 10
          }

          readiness_probe {
            http_get {
              path = "/health"
              port = 8000
            }
            initial_delay_seconds = 5
            period_seconds        = 5
          }
        }
      }
    }
  }
}

# Backend Service
resource "kubernetes_service" "backend" {
  metadata {
    name      = "backend-service"
    namespace = kubernetes_namespace.library.metadata[0].name
  }

  spec {
    selector = {
      app = "backend"
    }

    port {
      port        = 8000
      target_port = 8000
    }

    type = "ClusterIP"
  }
}

# Frontend Deployment
resource "kubernetes_deployment" "frontend" {
  metadata {
    name      = "frontend-deployment"
    namespace = kubernetes_namespace.library.metadata[0].name
  }

  spec {
    replicas = 2

    selector {
      match_labels = {
        app = "frontend"
      }
    }

    template {
      metadata {
        labels = {
          app = "frontend"
        }
      }

      spec {
        container {
          image = "library-frontend:latest"
          name  = "frontend"
          
          port {
            container_port = 80
          }

          resources {
            limits = {
              cpu    = "250m"
              memory = "256Mi"
            }
            requests = {
              cpu    = "100m"
              memory = "128Mi"
            }
          }

          liveness_probe {
            http_get {
              path = "/"
              port = 80
            }
            initial_delay_seconds = 30
            period_seconds        = 10
          }
        }
      }
    }
  }
}

# Frontend Service
resource "kubernetes_service" "frontend" {
  metadata {
    name      = "frontend-service"
    namespace = kubernetes_namespace.library.metadata[0].name
  }

  spec {
    selector = {
      app = "frontend"
    }

    port {
      port        = 80
      target_port = 80
    }

    type = "LoadBalancer"
  }
}

# Ingress
resource "kubernetes_ingress_v1" "app_ingress" {
  metadata {
    name      = "app-ingress"
    namespace = kubernetes_namespace.library.metadata[0].name
    annotations = {
      "kubernetes.io/ingress.class" = "nginx"
      "cert-manager.io/cluster-issuer" = "letsencrypt-prod"
    }
  }

  spec {
    tls {
      hosts       = [var.domain_name]
      secret_name = "app-tls"
    }

    rule {
      host = var.domain_name
      
      http {
        path {
          path      = "/api"
          path_type = "Prefix"
          
          backend {
            service {
              name = kubernetes_service.backend.metadata[0].name
              port {
                number = 8000
              }
            }
          }
        }

        path {
          path      = "/"
          path_type = "Prefix"
          
          backend {
            service {
              name = kubernetes_service.frontend.metadata[0].name
              port {
                number = 80
              }
            }
          }
        }
      }
    }
  }
}
```

### Variables Terraform

**infrastructure/variables.tf** :
```hcl
variable "secret_key" {
  description = "Secret key for JWT"
  type        = string
  sensitive   = true
}

variable "database_url" {
  description = "Database connection URL"
  type        = string
  sensitive   = true
}

variable "cors_origins" {
  description = "CORS allowed origins"
  type        = string
  default     = '["*"]'
}

variable "domain_name" {
  description = "Domain name for the application"
  type        = string
}
```

### Déploiement Kubernetes

**deploy-k8s.sh** :
```bash
#!/bin/bash
set -e

ENVIRONMENT=${1:-staging}

echo "☸️  Déploiement Kubernetes - Environnement: $ENVIRONMENT"

# Vérifier les outils
command -v kubectl >/dev/null 2>&1 || { echo "kubectl requis"; exit 1; }
command -v terraform >/dev/null 2>&1 || { echo "terraform requis"; exit 1; }

# Build et push des images
echo "🔨 Build des images Docker..."
docker build -t library-backend:latest ./backend
docker build -t library-frontend:latest ./frontend

# Pour Minikube, charger les images
if command -v minikube >/dev/null 2>&1; then
    echo "📦 Chargement des images dans Minikube..."
    minikube image load library-backend:latest
    minikube image load library-frontend:latest
fi

# Terraform
echo "🏗️  Déploiement avec Terraform..."
cd infrastructure

terraform init
terraform plan -var-file="environments/${ENVIRONMENT}.tfvars"
terraform apply -var-file="environments/${ENVIRONMENT}.tfvars" -auto-approve

cd ..

# Vérification
echo "🔍 Vérification du déploiement..."
kubectl get pods -n library-management
kubectl get services -n library-management

# Attendre que les pods soient prêts
kubectl wait --for=condition=ready pod -l app=backend -n library-management --timeout=300s
kubectl wait --for=condition=ready pod -l app=frontend -n library-management --timeout=300s

echo "✅ Déploiement terminé!"

# Afficher l'URL d'accès
if command -v minikube >/dev/null 2>&1; then
    echo "🌐 URL d'accès:"
    minikube service frontend-service -n library-management --url
fi
```

## Déploiement cloud

### AWS EKS

**infrastructure/aws-eks.tf** :
```hcl
# EKS Cluster
resource "aws_eks_cluster" "library" {
  name     = "library-management"
  role_arn = aws_iam_role.cluster.arn
  version  = "1.24"

  vpc_config {
    subnet_ids = aws_subnet.private[*].id
    endpoint_private_access = true
    endpoint_public_access  = true
  }

  depends_on = [
    aws_iam_role_policy_attachment.cluster-AmazonEKSClusterPolicy,
  ]
}

# Node Group
resource "aws_eks_node_group" "library" {
  cluster_name    = aws_eks_cluster.library.name
  node_group_name = "library-nodes"
  node_role_arn   = aws_iam_role.node.arn
  subnet_ids      = aws_subnet.private[*].id

  scaling_config {
    desired_size = 2
    max_size     = 4
    min_size     = 1
  }

  instance_types = ["t3.medium"]

  depends_on = [
    aws_iam_role_policy_attachment.node-AmazonEKSWorkerNodePolicy,
    aws_iam_role_policy_attachment.node-AmazonEKS_CNI_Policy,
    aws_iam_role_policy_attachment.node-AmazonEC2ContainerRegistryReadOnly,
  ]
}

# RDS Database
resource "aws_db_instance" "library" {
  identifier = "library-db"
  
  engine         = "postgres"
  engine_version = "13.7"
  instance_class = "db.t3.micro"
  
  allocated_storage     = 20
  max_allocated_storage = 100
  
  db_name  = "library"
  username = "postgres"
  password = var.db_password
  
  vpc_security_group_ids = [aws_security_group.rds.id]
  db_subnet_group_name   = aws_db_subnet_group.library.name
  
  backup_retention_period = 7
  backup_window          = "03:00-04:00"
  maintenance_window     = "sun:04:00-sun:05:00"
  
  skip_final_snapshot = true
  deletion_protection = false
}
```

### Google Cloud GKE

```bash
# Créer un cluster GKE
gcloud container clusters create library-cluster \
  --num-nodes=2 \
  --machine-type=e2-medium \
  --zone=europe-west1-b

# Obtenir les credentials
gcloud container clusters get-credentials library-cluster \
  --zone=europe-west1-b

# Déployer l'application
kubectl apply -f k8s/
```

### Azure AKS

```bash
# Créer un groupe de ressources
az group create --name library-rg --location westeurope

# Créer un cluster AKS
az aks create \
  --resource-group library-rg \
  --name library-cluster \
  --node-count 2 \
  --node-vm-size Standard_B2s \
  --generate-ssh-keys

# Obtenir les credentials
az aks get-credentials --resource-group library-rg --name library-cluster

# Déployer l'application
kubectl apply -f k8s/
```

## CI/CD

### GitHub Actions

**.github/workflows/deploy.yml** :
```yaml
name: Deploy to Production

on:
  push:
    branches: [ main ]
  workflow_dispatch:

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v3
      with:
        python-version: '3.10'
    
    - name: Run backend tests
      run: |
        cd backend
        pip install -r requirements.txt
        pytest
    
    - name: Set up Node.js
      uses: actions/setup-node@v3
      with:
        node-version: '18'
    
    - name: Run frontend tests
      run: |
        cd frontend
        npm install
        npm test -- --coverage --watchAll=false

  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Build and push Docker images
      run: |
        echo ${{ secrets.DOCKER_PASSWORD }} | docker login -u ${{ secrets.DOCKER_USERNAME }} --password-stdin
        
        # Backend
        docker build -t ${{ secrets.DOCKER_USERNAME }}/library-backend:${{ github.sha }} ./backend
        docker push ${{ secrets.DOCKER_USERNAME }}/library-backend:${{ github.sha }}
        
        # Frontend
        docker build -t ${{ secrets.DOCKER_USERNAME }}/library-frontend:${{ github.sha }} ./frontend
        docker push ${{ secrets.DOCKER_USERNAME }}/library-frontend:${{ github.sha }}

  deploy:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
    - uses: actions/checkout@v3
    
    - name: Deploy to Kubernetes
      run: |
        # Configuration kubectl
        echo "${{ secrets.KUBECONFIG }}" | base64 -d > kubeconfig
        export KUBECONFIG=kubeconfig
        
        # Mise à jour des images
        kubectl set image deployment/backend-deployment \
          backend=${{ secrets.DOCKER_USERNAME }}/library-backend:${{ github.sha }} \
          -n library-management
        
        kubectl set image deployment/frontend-deployment \
          frontend=${{ secrets.DOCKER_USERNAME }}/library-frontend:${{ github.sha }} \
          -n library-management
        
        # Attendre le rollout
        kubectl rollout status deployment/backend-deployment -n library-management
        kubectl rollout status deployment/frontend-deployment -n library-management
```

### GitLab CI

**.gitlab-ci.yml** :
```yaml
stages:
  - test
  - build
  - deploy

variables:
  DOCKER_DRIVER: overlay2
  BACKEND_IMAGE: $CI_REGISTRY_IMAGE/backend
  FRONTEND_IMAGE: $CI_REGISTRY_IMAGE/frontend

test:backend:
  stage: test
  image: python:3.10
  script:
    - cd backend
    - pip install -r requirements.txt
    - pytest --cov=.

test:frontend:
  stage: test
  image: node:18
  script:
    - cd frontend
    - npm install
    - npm test -- --coverage --watchAll=false

build:
  stage: build
  image: docker:latest
  services:
    - docker:dind
  before_script:
    - docker login -u $CI_REGISTRY_USER -p $CI_REGISTRY_PASSWORD $CI_REGISTRY
  script:
    - docker build -t $BACKEND_IMAGE:$CI_COMMIT_SHA ./backend
    - docker push $BACKEND_IMAGE:$CI_COMMIT_SHA
    - docker build -t $FRONTEND_IMAGE:$CI_COMMIT_SHA ./frontend
    - docker push $FRONTEND_IMAGE:$CI_COMMIT_SHA
  only:
    - main

deploy:production:
  stage: deploy
  image: bitnami/kubectl:latest
  script:
    - kubectl config use-context $KUBE_CONTEXT
    - kubectl set image deployment/backend-deployment backend=$BACKEND_IMAGE:$CI_COMMIT_SHA -n library-management
    - kubectl set image deployment/frontend-deployment frontend=$FRONTEND_IMAGE:$CI_COMMIT_SHA -n library-management
    - kubectl rollout status deployment/backend-deployment -n library-management
    - kubectl rollout status deployment/frontend-deployment -n library-management
  only:
    - main
  when: manual
```

## Monitoring et logs

### Prometheus et Grafana

**monitoring/prometheus.yml** :
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: prometheus-config
  namespace: monitoring
data:
  prometheus.yml: |
    global:
      scrape_interval: 15s
    
    scrape_configs:
      - job_name: 'library-backend'
        static_configs:
          - targets: ['backend-service:8000']
        metrics_path: /metrics
        
      - job_name: 'kubernetes-pods'
        kubernetes_sd_configs:
          - role: pod
        relabel_configs:
          - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_scrape]
            action: keep
            regex: true
```

### Installation avec Helm

```bash
# Ajouter les repos Helm
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo add grafana https://grafana.github.io/helm-charts
helm repo update

# Installer Prometheus
helm install prometheus prometheus-community/prometheus \
  --namespace monitoring \
  --create-namespace

# Installer Grafana
helm install grafana grafana/grafana \
  --namespace monitoring \
  --set adminPassword=admin123

# Port-forward pour accéder
kubectl port-forward service/prometheus-server 9090:80 -n monitoring
kubectl port-forward service/grafana 3001:80 -n monitoring
```

### Logs centralisés avec ELK

**logging/filebeat.yml** :
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: filebeat-config
  namespace: logging
data:
  filebeat.yml: |
    filebeat.inputs:
    - type: container
      paths:
        - /var/log/containers/*library*.log
      processors:
        - add_kubernetes_metadata:
            in_cluster: true
    
    output.elasticsearch:
      hosts: ["elasticsearch:9200"]
    
    setup.kibana:
      host: "kibana:5601"
```

## Sécurité

### TLS/SSL

```bash
# Installer cert-manager
kubectl apply -f https://github.com/jetstack/cert-manager/releases/download/v1.8.0/cert-manager.yaml

# ClusterIssuer pour Let's Encrypt
kubectl apply -f - <<EOF
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: admin@yourdomain.com
    privateKeySecretRef:
      name: letsencrypt-prod
    solvers:
    - http01:
        ingress:
          class: nginx
EOF
```

### Network Policies

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: library-network-policy
  namespace: library-management
spec:
  podSelector:
    matchLabels:
      app: backend
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: frontend
    ports:
    - protocol: TCP
      port: 8000
  egress:
  - to:
    - namespaceSelector:
        matchLabels:
          name: database
    ports:
    - protocol: TCP
      port: 5432
```

### Secrets management

```bash
# Créer des secrets
kubectl create secret generic app-secrets \
  --from-literal=SECRET_KEY="your-secret-key" \
  --from-literal=DATABASE_PASSWORD="your-db-password" \
  --namespace library-management

# Utiliser des secrets externes (AWS Secrets Manager)
kubectl apply -f - <<EOF
apiVersion: external-secrets.io/v1beta1
kind: SecretStore
metadata:
  name: aws-secrets-manager
  namespace: library-management
spec:
  provider:
    aws:
      service: SecretsManager
      region: us-west-2
      auth:
        secretRef:
          accessKeyID:
            name: aws-credentials
            key: access-key-id
          secretAccessKey:
            name: aws-credentials
            key: secret-access-key
EOF
```

## Maintenance

### Backup automatique

**backup/cronjob-backup.yml** :
```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: database-backup
  namespace: library-management
spec:
  schedule: "0 2 * * *"  # Tous les jours à 2h
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: postgres-backup
            image: postgres:13
            command:
            - /bin/bash
            - -c
            - |
              BACKUP_FILE="/backups/backup-$(date +%Y%m%d-%H%M%S).sql"
              pg_dump $DATABASE_URL > $BACKUP_FILE
              aws s3 cp $BACKUP_FILE s3://your-backup-bucket/
            env:
            - name: DATABASE_URL
              valueFrom:
                secretKeyRef:
                  name: app-secrets
                  key: database-url
            volumeMounts:
            - name: backup-storage
              mountPath: /backups
          volumes:
          - name: backup-storage
            emptyDir: {}
          restartPolicy: OnFailure
```

### Mise à jour rolling

```bash
# Mise à jour de l'image backend
kubectl set image deployment/backend-deployment \
  backend=library-backend:v2.0.0 \
  -n library-management

# Surveiller le rollout
kubectl rollout status deployment/backend-deployment -n library-management

# Rollback si nécessaire
kubectl rollout undo deployment/backend-deployment -n library-management
```

### Scaling automatique

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: backend-hpa
  namespace: library-management
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: backend-deployment
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

---

*Guide de déploiement v1.0 - Dernière mise à jour : Septembre 2024*