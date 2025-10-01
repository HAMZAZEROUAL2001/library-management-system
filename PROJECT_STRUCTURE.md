# Library Management System - Documentation DevOps

## 1. Présentation du projet

Ce projet est une application de gestion de bibliothèque développée en Python avec FastAPI, conteneurisée avec Docker, déployée sur Kubernetes (Minikube) et gérée via Terraform. Il intègre les bonnes pratiques DevOps (CI/CD, infrastructure as code, monitoring, etc.).

---

## 2. Structure du projet

```
library-management-system/
├── backend/
│   ├── main.py              # Point d'entrée FastAPI
│   ├── database.py          # Configuration SQLAlchemy
│   ├── models.py            # Modèles ORM et Pydantic
│   ├── auth.py              # Authentification JWT
│   ├── requirements.txt     # Dépendances Python
│   ├── Dockerfile           # Image Docker de l'app
│   ├── entrypoint.sh        # Script de démarrage/debug
│   └── ...
├── infrastructure/
│   ├── main.tf              # Déploiement Kubernetes (Terraform)
│   └── .terraform.lock.hcl  # Verrouillage des providers
├── docker-compose.yml       # Déploiement local multi-service
├── .github/
│   └── workflows/ci.yml     # Pipeline CI GitHub Actions
├── README.md                # Documentation utilisateur
└── PROJECT_STRUCTURE.md     # (ce document)
```

---

## 3. Technologies utilisées

- **Backend** : Python, FastAPI, SQLAlchemy, Pydantic
- **Base de données** : SQLite (dev), SQLAlchemy ORM
- **Authentification** : JWT, passlib
- **Tests** : pytest, httpx
- **Conteneurisation** : Docker
- **Orchestration** : Kubernetes (Minikube)
- **Infrastructure as Code** : Terraform
- **CI/CD** : GitHub Actions
- **Monitoring** : (optionnel) Prometheus, Grafana

---

## 4. Workflows DevOps

### a) Build & Test
- `docker build -t library-management-system:latest ./backend`
- `pytest` (tests unitaires)
- Linting/formatage via GitHub Actions

### b) Déploiement local
- `docker-compose up -d`
- Accès à l’API sur `localhost:8000`

### c) Déploiement Kubernetes (Minikube)
- `minikube start`
- `docker build -t library-management-system:latest ./backend`
- `minikube image load library-management-system:latest`
- `cd infrastructure && terraform init && terraform apply`
- Accès via le service Kubernetes (`kubectl get svc -n library-management`)

### d) CI/CD (GitHub Actions)
- Build, test, push image Docker, déploiement automatisé (voir `.github/workflows/ci.yml`)

---

## 5. Schéma d’architecture (ASCII)

```
+-------------------+
| Utilisateur       |
+--------+----------+
         |
         v
+--------+----------+
|  Ingress/Service  |
+--------+----------+
         |
         v
+--------+----------+
|  Pod Kubernetes   |
|  (FastAPI + DB)   |
+--------+----------+
         |
         v
+--------+----------+
|  Volume/Logs/DB   |
+-------------------+
```

---

## 6. Bonnes pratiques DevOps appliquées

- **Versioning** : tout est dans Git
- **CI/CD** : pipeline automatisé
- **Infrastructure as Code** : Terraform pour K8s
- **Conteneurisation** : Dockerfile optimisé
- **Sécurité** : secrets, non-root, dépendances à jour
- **Observabilité** : logs, monitoring possible
- **Rollback** : possible via `kubectl rollout undo`

---

## 7. Commandes clés

### Build & Test
```bash
cd backend
pip install -r requirements.txt
pytest
```

### Build Docker
```bash
docker build -t library-management-system:latest .
```

### Déploiement local
```bash
docker-compose up -d
```

### Déploiement Kubernetes
```bash
minikube start
docker build -t library-management-system:latest ./backend
minikube image load library-management-system:latest
cd infrastructure
terraform init
terraform apply
```

### Monitoring (optionnel)
```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm install prometheus prometheus-community/kube-prometheus-stack --namespace monitoring --create-namespace
```

---

## 8. Pour aller plus loin
- Ajouter Prometheus/Grafana pour la supervision
- Mettre en place un pipeline de déploiement continu
- Déployer sur un vrai cloud (AWS, GCP, Azure)
- Sécuriser les secrets avec Vault ou SealedSecrets
- Ajouter des tests d’intégration et de charge

---

*Document généré automatiquement pour l’apprentissage DevOps.*
