# Guide d'installation complète

Ce guide vous accompagne étape par étape pour installer et configurer le système de gestion de bibliothèque.

## Sommaire
1. [Prérequis](#prérequis)
2. [Installation locale](#installation-locale)
3. [Installation avec Docker](#installation-avec-docker)
4. [Installation Kubernetes](#installation-kubernetes)
5. [Configuration](#configuration)
6. [Vérification](#vérification)

## Prérequis

### Outils requis

#### Pour développement local
- **Python 3.10+** : [Télécharger Python](https://www.python.org/downloads/)
- **Node.js 18+** : [Télécharger Node.js](https://nodejs.org/)
- **Git** : [Télécharger Git](https://git-scm.com/)

#### Pour déploiement conteneurisé
- **Docker** : [Installer Docker](https://docs.docker.com/get-docker/)
- **Docker Compose** : Inclus avec Docker Desktop

#### Pour déploiement Kubernetes
- **kubectl** : [Installer kubectl](https://kubernetes.io/docs/tasks/tools/)
- **Terraform** : [Installer Terraform](https://developer.hashicorp.com/terraform/downloads)
- **Minikube** ou cluster Kubernetes

### Vérification des prérequis

```bash
# Vérifier les versions
python --version    # >= 3.10
node --version      # >= 18
npm --version
git --version
docker --version
docker-compose --version
kubectl version --client
terraform --version
```

## Installation locale

### 1. Cloner le repository

```bash
git clone https://github.com/HAMZAZEROUAL2001/library-management-system.git
cd library-management-system
```

### 2. Configuration du Backend

```bash
# Naviguer vers le dossier backend
cd backend

# Créer un environnement virtuel
python -m venv venv

# Activer l'environnement virtuel
# Sur Linux/Mac :
source venv/bin/activate
# Sur Windows :
venv\Scripts\activate

# Installer les dépendances
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Configuration du Frontend

```bash
# Naviguer vers le dossier frontend (depuis la racine)
cd ../frontend

# Installer les dépendances
npm install

# Copier le fichier de configuration
cp .env.example .env
```

### 4. Configuration des variables d'environnement

#### Backend (.env dans backend/)
```bash
# Créer le fichier .env
cat > .env << EOL
SECRET_KEY=your-super-secret-key-change-in-production
DATABASE_URL=sqlite:///./library.db
ACCESS_TOKEN_EXPIRE_MINUTES=30
DEBUG=true
EOL
```

#### Frontend (.env dans frontend/)
```bash
# Le fichier .env devrait contenir :
REACT_APP_API_URL=http://localhost:8000
REACT_APP_APP_NAME=Système de Gestion de Bibliothèque
```

### 5. Initialisation de la base de données

```bash
# Depuis le dossier backend
cd ../backend
python -c "from database import engine; from models import Base; Base.metadata.create_all(bind=engine)"
```

### 6. Démarrage des services

#### Terminal 1 - Backend
```bash
cd backend
source venv/bin/activate  # Si pas déjà activé
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### Terminal 2 - Frontend
```bash
cd frontend
npm start
```

### 7. Accès à l'application

- **Frontend** : http://localhost:3000
- **Backend API** : http://localhost:8000
- **Documentation API** : http://localhost:8000/docs

## Installation avec Docker

### 1. Méthode rapide avec Docker Compose

```bash
# Depuis la racine du projet
docker-compose up -d
```

### 2. Build manuel des images

```bash
# Backend
docker build -t library-backend ./backend

# Frontend
docker build -t library-frontend ./frontend

# Démarrage avec docker-compose
docker-compose up -d
```

### 3. Configuration avancée

#### Fichier docker-compose.override.yml (optionnel)
```yaml
version: '3.8'
services:
  backend:
    environment:
      - DEBUG=true
      - SECRET_KEY=dev-secret-key
    volumes:
      - ./backend:/app
    command: uvicorn main:app --reload --host 0.0.0.0 --port 8000
  
  frontend:
    environment:
      - REACT_APP_API_URL=http://localhost:8000
    volumes:
      - ./frontend/src:/app/src
```

### 4. Commandes utiles Docker

```bash
# Voir les logs
docker-compose logs -f

# Redémarrer un service
docker-compose restart backend

# Stopper tous les services
docker-compose down

# Nettoyer (supprime volumes et images)
docker-compose down -v --rmi all
```

## Installation Kubernetes

### 1. Prérequis Kubernetes

#### Démarrer Minikube (développement)
```bash
minikube start --driver=docker
minikube addons enable ingress
```

#### Ou utiliser un cluster existant
```bash
# Vérifier la connexion
kubectl cluster-info
kubectl get nodes
```

### 2. Build et chargement des images

```bash
# Build des images
docker build -t library-backend:latest ./backend
docker build -t library-frontend:latest ./frontend

# Pour Minikube, charger les images
minikube image load library-backend:latest
minikube image load library-frontend:latest
```

### 3. Déploiement avec Terraform

```bash
cd infrastructure

# Initialiser Terraform
terraform init

# Planifier le déploiement
terraform plan

# Appliquer la configuration
terraform apply
```

### 4. Déploiement manuel avec kubectl

```bash
# Créer le namespace
kubectl create namespace library-management

# Appliquer les manifests (si vous les créez)
kubectl apply -f k8s/ -n library-management
```

### 5. Vérification du déploiement

```bash
# Vérifier les pods
kubectl get pods -n library-management

# Vérifier les services
kubectl get services -n library-management

# Vérifier les ingress
kubectl get ingress -n library-management

# Voir les logs
kubectl logs -f deployment/backend-deployment -n library-management
```

### 6. Accès à l'application

```bash
# Avec Minikube
minikube service frontend-service -n library-management

# Ou port-forward pour test
kubectl port-forward service/frontend-service 3000:80 -n library-management
```

## Configuration

### Variables d'environnement

#### Backend
| Variable | Description | Défaut | Requis |
|----------|-------------|---------|---------|
| `SECRET_KEY` | Clé secrète pour JWT | - | ✅ |
| `DATABASE_URL` | URL de la base de données | `sqlite:///./library.db` | ❌ |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Durée de vie du token | `30` | ❌ |
| `DEBUG` | Mode debug | `false` | ❌ |
| `CORS_ORIGINS` | Origines CORS autorisées | `["*"]` | ❌ |

#### Frontend
| Variable | Description | Défaut | Requis |
|----------|-------------|---------|---------|
| `REACT_APP_API_URL` | URL de l'API backend | `http://localhost:8000` | ✅ |
| `REACT_APP_APP_NAME` | Nom de l'application | `Library System` | ❌ |

### Configuration de la base de données

#### SQLite (développement)
```bash
DATABASE_URL=sqlite:///./library.db
```

#### PostgreSQL (production)
```bash
DATABASE_URL=postgresql://username:password@localhost:5432/library_db
```

#### MySQL (alternative)
```bash
DATABASE_URL=mysql+pymysql://username:password@localhost:3306/library_db
```

### Configuration CORS

Pour la production, limitez les origines CORS :

```python
# Dans backend/main.py
CORS_ORIGINS = [
    "https://yourdomain.com",
    "https://www.yourdomain.com"
]
```

## Vérification

### Tests de santé

#### Backend
```bash
# Test de base
curl http://localhost:8000/

# Documentation API
curl http://localhost:8000/docs

# Health check
curl http://localhost:8000/health
```

#### Frontend
```bash
# Test d'accès
curl http://localhost:3000

# Vérifier les assets
curl http://localhost:3000/static/js/main.*.js
```

### Tests fonctionnels

#### 1. Test d'inscription
```bash
curl -X POST "http://localhost:8000/register" \
-H "Content-Type: application/json" \
-d '{
  "username": "testuser",
  "email": "test@example.com",
  "password": "testpassword"
}'
```

#### 2. Test de connexion
```bash
curl -X POST "http://localhost:8000/token" \
-H "Content-Type: application/x-www-form-urlencoded" \
-d "username=testuser&password=testpassword"
```

#### 3. Test API avec token
```bash
TOKEN="your-jwt-token-here"
curl -X GET "http://localhost:8000/books" \
-H "Authorization: Bearer $TOKEN"
```

### Diagnostic des problèmes

#### Logs détaillés
```bash
# Docker Compose
docker-compose logs -f backend frontend

# Kubernetes
kubectl logs -f deployment/backend-deployment -n library-management
kubectl logs -f deployment/frontend-deployment -n library-management
```

#### Vérification des ports
```bash
# Vérifier que les ports sont ouverts
netstat -tlnp | grep :8000  # Backend
netstat -tlnp | grep :3000  # Frontend
```

#### Test de connectivité
```bash
# Test depuis le frontend vers le backend
docker-compose exec frontend curl http://backend:8000/

# Test depuis l'extérieur
curl -I http://localhost:8000/
curl -I http://localhost:3000/
```

## Étapes suivantes

1. **Créer un utilisateur admin** via l'interface web
2. **Ajouter quelques livres** pour tester les fonctionnalités
3. **Configurer un reverse proxy** (Nginx) pour la production
4. **Mettre en place la sauvegarde** de la base de données
5. **Configurer le monitoring** avec Prometheus/Grafana

## Support

Si vous rencontrez des problèmes :

1. Consultez les [logs](#diagnostic-des-problèmes)
2. Vérifiez la [section troubleshooting](troubleshooting.md)
3. Ouvrez une [issue sur GitHub](https://github.com/HAMZAZEROUAL2001/library-management-system/issues)

---

*Guide d'installation v1.0 - Dernière mise à jour : Septembre 2024*