# Documentation du Système de Gestion de Bibliothèque

## Table des matières

1. [Vue d'ensemble](#vue-densemble)
2. [Guide d'installation](#guide-dinstallation)
3. [Guide d'utilisation](#guide-dutilisation)
4. [Documentation API](#documentation-api)
5. [Guide de déploiement](#guide-de-déploiement)
6. [Troubleshooting](#troubleshooting)
7. [Contribution](#contribution)

## Vue d'ensemble

Le Système de Gestion de Bibliothèque est une application web moderne construite avec :

- **Backend** : FastAPI (Python) avec SQLAlchemy
- **Frontend** : React avec TypeScript et Material-UI
- **Base de données** : SQLite (développement) / PostgreSQL (production)
- **Authentification** : JWT (JSON Web Tokens)
- **Conteneurisation** : Docker
- **Orchestration** : Kubernetes
- **Infrastructure** : Terraform
- **CI/CD** : GitHub Actions

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │    Backend      │    │   Database      │
│   (React)       │◄──►│   (FastAPI)     │◄──►│   (SQLite)      │
│   Port: 3000    │    │   Port: 8000    │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                │
                    ┌─────────────────┐
                    │   Kubernetes    │
                    │   (Production)  │
                    └─────────────────┘
```

## Fonctionnalités principales

### Authentification
- Inscription et connexion des utilisateurs
- Protection des routes avec JWT
- Gestion automatique des sessions

### Gestion des livres
- Ajout, modification et suppression de livres
- Recherche avancée par titre, auteur ou ISBN
- Statut de disponibilité en temps réel

### Système d'emprunts
- Emprunt de livres disponibles
- Suivi des emprunts en cours
- Retour de livres avec historique

### Tableau de bord
- Statistiques de la bibliothèque
- Vue d'ensemble des activités
- Interface utilisateur intuitive

## Guide d'installation

### Prérequis

- Python 3.10+
- Node.js 18+
- Docker et Docker Compose
- Git

### Installation locale

#### 1. Cloner le repository

```bash
git clone https://github.com/HAMZAZEROUAL2001/library-management-system.git
cd library-management-system
```

#### 2. Configuration Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows

pip install -r requirements.txt
```

#### 3. Configuration Frontend

```bash
cd ../frontend
npm install
cp .env.example .env
```

#### 4. Variables d'environnement

**Backend** (`.env` dans le dossier backend):
```
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///./library.db
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

**Frontend** (`.env` dans le dossier frontend):
```
REACT_APP_API_URL=http://localhost:8000
```

### Démarrage avec Docker Compose

```bash
# À la racine du projet
docker-compose up -d
```

L'application sera accessible sur :
- Frontend : http://localhost:3000
- Backend API : http://localhost:8000
- Documentation API : http://localhost:8000/docs

## Guide d'utilisation

### Interface utilisateur

#### 1. Connexion/Inscription
- Accédez à l'application via votre navigateur
- Créez un compte ou connectez-vous avec vos identifiants
- Le token d'authentification est géré automatiquement

#### 2. Tableau de bord
- Vue d'ensemble des statistiques de la bibliothèque
- Nombre total de livres et livres disponibles
- Statistiques des emprunts

#### 3. Gestion des livres
- **Ajouter un livre** : Cliquez sur le bouton "+" flottant
- **Rechercher** : Utilisez la barre de recherche pour trouver des livres
- **Modifier** : Cliquez sur l'icône crayon sur une carte de livre
- **Supprimer** : Cliquez sur l'icône poubelle (confirmation requise)
- **Emprunter** : Cliquez sur "Emprunter" si le livre est disponible

#### 4. Mes emprunts
- Consultez tous vos emprunts en cours et passés
- Retournez un livre en cliquant sur "Retourner le livre"
- Historique complet avec dates d'emprunt et de retour

### API REST

L'API suit les conventions REST et retourne des données au format JSON.

#### Authentification

```bash
# Inscription
POST /register
{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "securepassword"
}

# Connexion
POST /token
Form-data: username, password

# Accès aux endpoints protégés
Authorization: Bearer <your-jwt-token>
```

#### Gestion des livres

```bash
# Lister tous les livres
GET /books?skip=0&limit=100

# Rechercher des livres
GET /books/search?q=python&skip=0&limit=10

# Obtenir un livre spécifique
GET /books/{book_id}

# Ajouter un livre
POST /books
{
  "title": "Python Programming",
  "author": "John Smith",
  "isbn": "978-0123456789"
}

# Modifier un livre
PUT /books/{book_id}
{
  "title": "Advanced Python Programming",
  "author": "John Smith",
  "isbn": "978-0123456789",
  "available": true
}

# Supprimer un livre
DELETE /books/{book_id}
```

#### Gestion des emprunts

```bash
# Emprunter un livre
POST /loans
{
  "book_id": 1
}

# Mes emprunts
GET /loans/my-loans

# Tous les emprunts (admin)
GET /loans

# Retourner un livre
PATCH /loans/{loan_id}/return
```

#### Statistiques

```bash
# Statistiques de la bibliothèque
GET /stats
```

## Guide de déploiement

### Déploiement Docker

#### 1. Build des images

```bash
# Backend
docker build -t library-backend ./backend

# Frontend
docker build -t library-frontend ./frontend
```

#### 2. Déploiement avec Docker Compose

```bash
docker-compose up -d
```

### Déploiement Kubernetes

#### 1. Prérequis

- Cluster Kubernetes (minikube, kind, ou cloud)
- kubectl configuré
- Terraform installé

#### 2. Déploiement avec Terraform

```bash
cd infrastructure
terraform init
terraform plan
terraform apply
```

#### 3. Vérification du déploiement

```bash
kubectl get pods -n library-management
kubectl get services -n library-management
```

#### 4. Accès à l'application

```bash
# Obtenir l'URL d'accès
kubectl get ingress -n library-management

# Ou utiliser port-forward pour test
kubectl port-forward service/frontend-service 3000:80 -n library-management
```

### Variables d'environnement de production

#### Backend
```
SECRET_KEY=<strong-secret-key>
DATABASE_URL=postgresql://user:password@host:5432/dbname
ACCESS_TOKEN_EXPIRE_MINUTES=60
CORS_ORIGINS=["https://yourdomain.com"]
```

#### Frontend
```
REACT_APP_API_URL=https://api.yourdomain.com
```

## Troubleshooting

### Problèmes courants

#### 1. Erreur de connexion API

**Symptôme** : Frontend ne peut pas se connecter au backend

**Solutions** :
- Vérifiez que le backend est démarré sur le port 8000
- Vérifiez la variable `REACT_APP_API_URL` dans le frontend
- Contrôlez les logs : `docker-compose logs backend`

#### 2. Erreur d'authentification

**Symptôme** : "401 Unauthorized" lors des requêtes

**Solutions** :
- Vérifiez que le token JWT n'est pas expiré
- Contrôlez la configuration `SECRET_KEY`
- Reconnectez-vous pour générer un nouveau token

#### 3. Problèmes de base de données

**Symptôme** : Erreurs lors des opérations sur les données

**Solutions** :
- Vérifiez les permissions du fichier SQLite
- Contrôlez les migrations : `alembic upgrade head`
- Vérifiez les logs backend pour les erreurs SQL

#### 4. Problèmes Docker

**Symptôme** : Conteneurs qui ne démarrent pas

**Solutions** :
```bash
# Nettoyer les conteneurs
docker-compose down -v
docker system prune -f

# Rebuilder les images
docker-compose build --no-cache
docker-compose up -d
```

#### 5. Problèmes Kubernetes

**Symptôme** : Pods en erreur ou CrashLoopBackOff

**Solutions** :
```bash
# Vérifier les logs des pods
kubectl logs <pod-name> -n library-management

# Vérifier les événements
kubectl get events -n library-management

# Redémarrer un déploiement
kubectl rollout restart deployment/<deployment-name> -n library-management
```

### Logs et monitoring

#### Accès aux logs

```bash
# Docker Compose
docker-compose logs -f backend
docker-compose logs -f frontend

# Kubernetes
kubectl logs -f deployment/backend-deployment -n library-management
kubectl logs -f deployment/frontend-deployment -n library-management
```

#### Monitoring de santé

```bash
# Health check backend
curl http://localhost:8000/health

# Vérification Kubernetes
kubectl get pods -n library-management
kubectl top pods -n library-management
```

## Tests

### Tests backend

```bash
cd backend
pytest -v
pytest --cov=. --cov-report=html
```

### Tests frontend

```bash
cd frontend
npm test
npm run test:coverage
```

### Tests d'intégration

```bash
# Avec docker-compose
docker-compose -f docker-compose.test.yml up --abort-on-container-exit
```

## Sécurité

### Bonnes pratiques implémentées

1. **Authentification JWT** avec expiration
2. **Validation des données** avec Pydantic
3. **Protection CORS** configurée
4. **Headers de sécurité** dans Nginx
5. **Secrets** gérés par variables d'environnement
6. **Images Docker** non-root

### Recommandations de production

1. Utilisez HTTPS uniquement
2. Configurez un WAF (Web Application Firewall)
3. Implémentez une solution de backup pour la base de données
4. Utilisez des secrets Kubernetes pour les données sensibles
5. Activez les logs d'audit
6. Surveillez les tentatives d'intrusion

## Contribution

### Workflow de développement

1. Fork le repository
2. Créez une branche feature : `git checkout -b feature/nouvelle-fonctionnalite`
3. Committez vos changements : `git commit -m "Ajout nouvelle fonctionnalité"`
4. Poussez la branche : `git push origin feature/nouvelle-fonctionnalite`
5. Créez une Pull Request

### Standards de code

- **Backend** : Suivre PEP 8, utiliser Black pour le formatage
- **Frontend** : Utiliser ESLint et Prettier
- **Tests** : Maintenir une couverture > 80%
- **Documentation** : Documenter toutes les fonctions publiques

### Structure des commits

```
type(scope): description

feat(auth): ajouter authentification OAuth
fix(api): corriger erreur de validation
docs(readme): mettre à jour guide installation
```

## Support

- **Issues** : https://github.com/HAMZAZEROUAL2001/library-management-system/issues
- **Discussions** : https://github.com/HAMZAZEROUAL2001/library-management-system/discussions
- **Email** : hamza@example.com

---

*Documentation maintenue à jour avec la version 1.0.0*