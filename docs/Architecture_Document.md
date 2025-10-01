# Architecture du Système de Gestion de Bibliothèque

**Version:** 1.0  
**Date:** Octobre 2025  
**Auteur:** Système DevOps avec Cursor  

---

## Table des Matières

1. [Vue d'ensemble](#vue-densemble)
2. [Architecture Technique](#architecture-technique)
3. [Composants du Système](#composants-du-système)
4. [Infrastructure et Déploiement](#infrastructure-et-déploiement)
5. [Sécurité](#sécurité)
6. [Monitoring et Observabilité](#monitoring-et-observabilité)
7. [Tests et Qualité](#tests-et-qualité)
8. [Déploiement et DevOps](#déploiement-et-devops)
9. [Guide d'Installation](#guide-dinstallation)
10. [Maintenance et Support](#maintenance-et-support)

---

## Vue d'ensemble

### Description du Projet

Le **Système de Gestion de Bibliothèque** est une application web moderne développée selon les meilleures pratiques DevOps. Elle permet la gestion complète d'une bibliothèque avec :

- **Gestion des livres** : Ajout, modification, suppression, recherche
- **Gestion des utilisateurs** : Inscription, authentification, profils
- **Système d'emprunts** : Emprunter, retourner, historique
- **Tableau de bord** : Statistiques et monitoring
- **API REST** : Interface complète pour intégrations tierces

### Objectifs Architecturaux

1. **Scalabilité** : Architecture microservices containerisée
2. **Fiabilité** : Tests automatisés et monitoring complet
3. **Sécurité** : Authentification JWT et validation des données
4. **Maintenabilité** : Code modulaire et documentation complète
5. **Performance** : Optimisations base de données et caching

---

## Architecture Technique

### Architecture Globale

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│                 │    │                 │    │                 │
│   Frontend      │    │   Backend       │    │   Database      │
│   React/TS      │◄──►│   FastAPI       │◄──►│   PostgreSQL    │
│   Port: 3000    │    │   Port: 8000    │    │   Port: 5432    │
│                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         ▲                       ▲                       ▲
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│                 │    │                 │    │                 │
│   Nginx         │    │   Monitoring    │    │   Infrastructure│
│   Reverse Proxy │    │   Prometheus    │    │   Kubernetes    │
│   Port: 80      │    │   Grafana       │    │   Terraform     │
│                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Technologies Utilisées

#### Frontend
- **React 18** : Framework JavaScript moderne
- **TypeScript** : Typage statique pour JavaScript
- **Material-UI** : Composants UI professionnels
- **Axios** : Client HTTP pour API calls
- **React Router** : Navigation côté client

#### Backend
- **FastAPI** : Framework Python haute performance
- **SQLAlchemy** : ORM Python pour base de données
- **Pydantic** : Validation des données
- **JWT** : Authentification stateless
- **Uvicorn** : Serveur ASGI haute performance

#### Base de Données
- **PostgreSQL 15** : Base de données relationnelle
- **Alembic** : Migrations de base de données
- **pgAdmin** : Interface d'administration

#### Infrastructure
- **Docker** : Containerisation
- **Docker Compose** : Orchestration locale
- **Kubernetes** : Orchestration production
- **Terraform** : Infrastructure as Code
- **Nginx** : Reverse proxy et load balancer

---

## Composants du Système

### 1. Frontend React

**Localisation :** `/frontend/`

#### Structure des Composants

```
frontend/
├── public/
│   ├── index.html
│   └── favicon.ico
├── src/
│   ├── components/
│   │   ├── common/
│   │   │   ├── Header.tsx
│   │   │   ├── Footer.tsx
│   │   │   └── Layout.tsx
│   │   ├── books/
│   │   │   ├── BookList.tsx
│   │   │   ├── BookCard.tsx
│   │   │   ├── BookForm.tsx
│   │   │   └── BookSearch.tsx
│   │   ├── loans/
│   │   │   ├── LoanList.tsx
│   │   │   ├── LoanCard.tsx
│   │   │   └── LoanHistory.tsx
│   │   └── auth/
│   │       ├── Login.tsx
│   │       ├── Register.tsx
│   │       └── Profile.tsx
│   ├── services/
│   │   ├── api.ts
│   │   ├── auth.ts
│   │   └── types.ts
│   ├── utils/
│   │   ├── constants.ts
│   │   └── helpers.ts
│   ├── App.tsx
│   └── index.tsx
├── package.json
└── tsconfig.json
```

#### Fonctionnalités Principales

1. **Interface Utilisateur Moderne**
   - Design responsive Material-UI
   - Navigation intuitive
   - Feedback utilisateur en temps réel

2. **Gestion d'État**
   - État local avec React Hooks
   - Gestion des sessions utilisateur
   - Cache des données API

3. **Sécurité Frontend**
   - Validation des formulaires
   - Protection des routes
   - Gestion des tokens JWT

### 2. Backend FastAPI

**Localisation :** `/backend/`

#### Structure de l'API

```
backend/
├── main.py              # Point d'entrée de l'application
├── models.py            # Modèles SQLAlchemy
├── database.py          # Configuration base de données
├── auth.py              # Authentification et autorisation
├── monitoring.py        # Métriques Prometheus
├── logging_config.py    # Configuration des logs
├── requirements.txt     # Dépendances Python
├── Dockerfile          # Image Docker
├── entrypoint.sh       # Script de démarrage
└── tests/
    ├── test_main.py
    ├── test_unit.py
    ├── test_integration.py
    └── test_load.py
```

#### Endpoints API

| Méthode | Endpoint | Description | Authentification |
|---------|----------|-------------|-----------------|
| POST | `/users/` | Créer un utilisateur | Non |
| POST | `/token` | Authentification | Non |
| GET | `/books` | Lister les livres | Oui |
| POST | `/books` | Créer un livre | Admin |
| GET | `/books/{isbn}` | Détail d'un livre | Oui |
| PUT | `/books/{isbn}` | Modifier un livre | Admin |
| DELETE | `/books/{isbn}` | Supprimer un livre | Admin |
| GET | `/books/search` | Rechercher des livres | Oui |
| GET | `/books/stats` | Statistiques livres | Admin |
| GET | `/loans` | Lister les emprunts | Oui |
| POST | `/loans` | Créer un emprunt | Oui |
| PUT | `/loans/return` | Retourner un livre | Oui |
| GET | `/loans/user` | Emprunts utilisateur | Oui |
| GET | `/loans/overdue` | Emprunts en retard | Admin |
| GET | `/health` | Santé de l'API | Non |

#### Modèles de Données

```python
# Utilisateur
class User:
    id: int
    username: str
    email: str
    is_admin: bool
    created_at: datetime

# Livre
class Book:
    id: int
    isbn: str
    title: str
    author: str
    genre: str
    publication_year: int
    copies_total: int
    copies_available: int

# Emprunt
class Loan:
    id: int
    user_id: int
    book_id: int
    loan_date: datetime
    due_date: datetime
    return_date: Optional[datetime]
    is_returned: bool
```

### 3. Base de Données PostgreSQL

**Configuration :** 
- **Version :** PostgreSQL 15
- **Port :** 5432
- **Authentification :** username/password
- **Persistence :** Volume Docker

#### Schéma de Base de Données

```sql
-- Table des utilisateurs
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    is_admin BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table des livres
CREATE TABLE books (
    id SERIAL PRIMARY KEY,
    isbn VARCHAR(13) UNIQUE NOT NULL,
    title VARCHAR(200) NOT NULL,
    author VARCHAR(100) NOT NULL,
    genre VARCHAR(50),
    publication_year INTEGER,
    copies_total INTEGER DEFAULT 1,
    copies_available INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table des emprunts
CREATE TABLE loans (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    book_id INTEGER REFERENCES books(id),
    loan_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    due_date TIMESTAMP NOT NULL,
    return_date TIMESTAMP,
    is_returned BOOLEAN DEFAULT FALSE
);

-- Index pour les performances
CREATE INDEX idx_loans_user_id ON loans(user_id);
CREATE INDEX idx_loans_book_id ON loans(book_id);
CREATE INDEX idx_loans_due_date ON loans(due_date);
```

---

## Infrastructure et Déploiement

### Docker Compose

**Fichier :** `docker-compose.yml`

La stack complète est orchestrée avec Docker Compose :

```yaml
services:
  database:
    image: postgres:15
    environment:
      POSTGRES_DB: library_management
      POSTGRES_USER: library_user
      POSTGRES_PASSWORD: library_pass
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  backend:
    build: ./backend
    environment:
      DATABASE_URL: postgresql://library_user:library_pass@database:5432/library_management
      SECRET_KEY: changeme_in_production
    ports:
      - "8000:8000"
    depends_on:
      - database

  frontend:
    build: ./frontend
    ports:
      - "3000:80"

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/conf.d/default.conf
    depends_on:
      - frontend
      - backend
```

### Kubernetes

**Localisation :** `/infrastructure/k8s/`

#### Composants Kubernetes

1. **Namespaces**
   ```yaml
   apiVersion: v1
   kind: Namespace
   metadata:
     name: library-system
   ```

2. **Deployments**
   - Backend FastAPI (3 replicas)
   - Frontend React (2 replicas)
   - Base de données PostgreSQL (1 replica + volume persistant)

3. **Services**
   - Service backend (ClusterIP)
   - Service frontend (ClusterIP)
   - Service database (ClusterIP)
   - Service nginx (LoadBalancer)

4. **ConfigMaps et Secrets**
   - Configuration application
   - Secrets base de données
   - Variables d'environnement

### Terraform

**Localisation :** `/infrastructure/`

Infrastructure as Code pour :
- Cluster Kubernetes local (kind/minikube)
- Volumes persistants
- Réseau et sécurité
- Monitoring stack

---

## Sécurité

### Authentification et Autorisation

1. **JWT (JSON Web Tokens)**
   ```python
   # Génération du token
   def create_access_token(data: dict, expires_delta: timedelta = None):
       to_encode = data.copy()
       expire = datetime.utcnow() + expires_delta
       to_encode.update({"exp": expire})
       return jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")
   ```

2. **Hachage des Mots de Passe**
   ```python
   # Utilisation de SHA256 pour le hachage
   def hash_password(password: str) -> str:
       return hashlib.sha256(password.encode()).hexdigest()
   ```

3. **Rôles et Permissions**
   - **Utilisateur** : Consulter livres, emprunter, voir ses emprunts
   - **Administrateur** : Toutes les actions + gestion des livres

### Sécurité Réseau

1. **Reverse Proxy Nginx**
   - Protection contre les attaques DDoS
   - Compression et cache
   - Headers de sécurité

2. **CORS (Cross-Origin Resource Sharing)**
   ```python
   app.add_middleware(
       CORSMiddleware,
       allow_origins=["http://localhost:3000"],
       allow_credentials=True,
       allow_methods=["*"],
       allow_headers=["*"],
   )
   ```

### Validation des Données

```python
# Exemple de validation Pydantic
class BookCreate(BaseModel):
    isbn: str = Field(..., regex=r'^\d{13}$')
    title: str = Field(..., min_length=1, max_length=200)
    author: str = Field(..., min_length=1, max_length=100)
    genre: Optional[str] = Field(None, max_length=50)
    publication_year: int = Field(..., ge=1000, le=2030)
```

---

## Monitoring et Observabilité

### Métriques Prometheus

**Localisation :** `/backend/monitoring.py`

```python
# Métriques collectées
- http_requests_total : Nombre total de requêtes HTTP
- http_request_duration_seconds : Durée des requêtes
- database_connections : Connexions base de données actives
- active_loans : Nombre d'emprunts actifs
- book_operations_total : Opérations sur les livres
```

### Dashboards Grafana

1. **Dashboard Application**
   - Métriques API (latence, erreurs, throughput)
   - Métriques métier (emprunts, livres)
   - Santé des services

2. **Dashboard Infrastructure**
   - CPU, mémoire, disque
   - Réseau et base de données
   - Logs d'erreurs

### Logs Structurés

```python
# Configuration logging
import logging
import sys

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/app/logs/app.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
```

---

## Tests et Qualité

### Tests Automatisés

**Localisation :** `/backend/tests/`

#### 1. Tests Unitaires (`test_unit.py`)
```python
def test_hash_password():
    password = "test123"
    hashed = hash_password(password)
    assert len(hashed) == 64  # SHA256 hash length
    assert hashed != password

def test_verify_password():
    password = "test123"
    hashed = hash_password(password)
    assert verify_password(password, hashed) == True
```

#### 2. Tests d'Intégration (`test_integration.py`)
```python
def test_create_user_and_login():
    # Créer un utilisateur
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "password123"
    }
    response = client.post("/users/", json=user_data)
    assert response.status_code == 200
    
    # Se connecter
    login_data = {
        "username": "testuser",
        "password": "password123"
    }
    response = client.post("/token", data=login_data)
    assert response.status_code == 200
    assert "access_token" in response.json()
```

#### 3. Tests de Charge (`test_load.py`)
```python
# Tests avec Locust
class LibraryUser(HttpUser):
    wait_time = between(1, 3)
    
    def on_start(self):
        # Se connecter
        self.login()
    
    @task(3)
    def view_books(self):
        self.client.get("/books")
    
    @task(1)
    def search_books(self):
        self.client.get("/books/search?query=python")
```

#### 4. Tests End-to-End (`test_e2e.py`)
Test complet du système via les APIs publiques.

### Couverture de Code

```bash
# Générer le rapport de couverture
pytest --cov=. --cov-report=html
# Couverture cible : > 80%
```

### Qualité du Code

1. **Linting**
   ```bash
   flake8 .              # Style Python
   black .               # Formatage automatique
   isort .               # Organisation des imports
   mypy .                # Vérification des types
   ```

2. **Sécurité**
   ```bash
   bandit -r .           # Vulnérabilités de sécurité
   safety check          # Vulnérabilités des dépendances
   ```

---

## Déploiement et DevOps

### Pipeline CI/CD

**Fichier :** `.github/workflows/ci-cd.yml`

```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'
    
    - name: Install dependencies
      run: |
        cd backend
        pip install -r requirements.txt
    
    - name: Run tests
      run: |
        cd backend
        pytest --cov=. --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3

  build:
    needs: test
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Build Docker images
      run: |
        docker build -t library-backend ./backend
        docker build -t library-frontend ./frontend
    
    - name: Test Docker containers
      run: |
        docker-compose up -d
        sleep 30
        curl -f http://localhost:8000/health
        docker-compose down

  deploy:
    needs: [test, build]
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
    - name: Deploy to production
      run: |
        # Scripts de déploiement Kubernetes
        kubectl apply -f infrastructure/k8s/
```

### Environments

1. **Développement**
   - Docker Compose local
   - Hot reload activé
   - Debug mode activé

2. **Test**
   - Kubernetes local (minikube)
   - Base de données temporaire
   - Tests automatiques

3. **Production**
   - Cluster Kubernetes
   - Base de données persistante
   - Monitoring complet
   - Sauvegarde automatique

---

## Guide d'Installation

### Prérequis

- **Docker** >= 20.0
- **Docker Compose** >= 2.0
- **Python** >= 3.10 (pour développement)
- **Node.js** >= 18 (pour développement)
- **Git**

### Installation Rapide

```bash
# 1. Cloner le projet
git clone https://github.com/username/library-management-system.git
cd library-management-system

# 2. Lancer avec Docker Compose
docker compose up -d

# 3. Vérifier le déploiement
curl http://localhost/api/health
```

### Installation pour Développement

```bash
# 1. Préparer l'environnement Python
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows
pip install -r requirements.txt

# 2. Préparer l'environnement Node.js
cd ../frontend
npm install

# 3. Démarrer la base de données
docker run -d \
  --name postgres-dev \
  -e POSTGRES_DB=library_management \
  -e POSTGRES_USER=library_user \
  -e POSTGRES_PASSWORD=library_pass \
  -p 5432:5432 \
  postgres:15

# 4. Initialiser la base de données
cd ../backend
python init_db.py

# 5. Démarrer les services
# Terminal 1 - Backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2 - Frontend
cd ../frontend
npm start
```

### Variables d'Environnement

```bash
# Backend (.env)
DATABASE_URL=postgresql://library_user:library_pass@localhost:5432/library_management
SECRET_KEY=your-super-secret-key-change-in-production
DEBUG=true
ENVIRONMENT=development

# Frontend (.env)
REACT_APP_API_URL=http://localhost:8000
REACT_APP_ENVIRONMENT=development
```

---

## Maintenance et Support

### Opérations Courantes

#### 1. Sauvegarde Base de Données
```bash
# Sauvegarde
docker exec postgres-container pg_dump -U library_user library_management > backup.sql

# Restauration
docker exec -i postgres-container psql -U library_user library_management < backup.sql
```

#### 2. Mise à Jour de l'Application
```bash
# 1. Sauvegarder les données
docker compose exec database pg_dump -U library_user library_management > backup.sql

# 2. Arrêter les services
docker compose down

# 3. Mettre à jour le code
git pull origin main

# 4. Reconstruire et relancer
docker compose up -d --build

# 5. Vérifier le déploiement
curl http://localhost/api/health
```

#### 3. Monitoring et Logs
```bash
# Voir les logs en temps réel
docker compose logs -f backend

# Métriques Prometheus
curl http://localhost:8000/metrics

# Santé des services
curl http://localhost/api/health
```

### Troubleshooting

#### Problèmes Courants

1. **Erreur de connexion base de données**
   ```bash
   # Vérifier que PostgreSQL est démarré
   docker compose ps database
   
   # Vérifier les logs
   docker compose logs database
   ```

2. **Frontend ne se connecte pas au backend**
   ```bash
   # Vérifier la configuration CORS
   # Vérifier les variables d'environnement
   echo $REACT_APP_API_URL
   ```

3. **Authentification échoue**
   ```bash
   # Vérifier la configuration JWT
   # Vérifier le hachage des mots de passe
   ```

### Support et Documentation

- **Code Source :** GitHub Repository
- **Documentation API :** http://localhost:8000/docs
- **Monitoring :** Grafana Dashboard
- **Logs :** Centralisés via Docker

---

## Conclusion

Ce système de gestion de bibliothèque représente une implémentation complète d'une architecture moderne avec :

✅ **Architecture microservices** scalable et maintenable  
✅ **Stack technologique moderne** (React, FastAPI, PostgreSQL)  
✅ **Containerisation Docker** pour la portabilité  
✅ **Tests automatisés** pour la qualité  
✅ **Monitoring complet** pour l'observabilité  
✅ **Infrastructure as Code** pour la reproductibilité  
✅ **Documentation complète** pour la maintenance  

Le projet est prêt pour un déploiement en production et peut servir de base pour des systèmes plus complexes.

---

**Contacts et Support :**
- Documentation : http://localhost:8000/docs
- Monitoring : http://localhost:3000 (Grafana)
- Métriques : http://localhost:8000/metrics
- Santé : http://localhost/api/health