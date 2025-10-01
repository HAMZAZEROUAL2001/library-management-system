# Guide WSL pour Library Management System

Ce guide vous aide à configurer et utiliser WSL (Windows Subsystem for Linux) pour le développement, les tests et Docker avec le système de gestion de bibliothèque.

## 🐧 Configuration WSL

### Installation WSL 2
```powershell
# Dans PowerShell en tant qu'administrateur
dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart
dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart

# Redémarrer Windows, puis installer une distribution
wsl --install -d Ubuntu-22.04

# Définir WSL 2 comme version par défaut
wsl --set-default-version 2
```

### Vérification de l'installation
```bash
# Dans WSL
wsl --list --verbose
wsl --status
```

## 🐳 Configuration Docker avec WSL

### Installation Docker Desktop avec WSL Backend
1. **Télécharger Docker Desktop** avec support WSL 2
2. **Configurer Docker** pour utiliser WSL 2 backend
3. **Activer l'intégration WSL** dans les distributions souhaitées

### Configuration optimale
```bash
# Dans WSL Ubuntu
# Mettre à jour le système
sudo apt update && sudo apt upgrade -y

# Installer les dépendances
sudo apt install -y curl wget git build-essential

# Vérifier Docker depuis WSL
docker --version
docker-compose --version
```

## 🔧 Configuration du projet dans WSL

### Structure recommandée
```bash
# Créer un dossier de travail dans WSL
mkdir -p ~/projects
cd ~/projects

# Cloner ou accéder au projet
# Option 1: Cloner directement dans WSL
git clone <repository-url> library-management-system

# Option 2: Accéder au projet Windows depuis WSL
cd /mnt/d/devopswithcursor/library-management-system
```

### Variables d'environnement WSL
```bash
# ~/.bashrc ou ~/.zshrc
export DOCKER_HOST=unix:///var/run/docker.sock
export COMPOSE_DOCKER_CLI_BUILD=1
export DOCKER_BUILDKIT=1

# Recharger le shell
source ~/.bashrc
```

## 🧪 Exécution des tests avec WSL

### Backend Python
```bash
# Dans WSL, se positionner dans le projet
cd ~/projects/library-management-system/backend

# Créer un environnement virtuel
python3 -m venv venv
source venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt

# Exécuter les tests
pytest tests/ -v --cov=.

# Tests d'intégration avec Docker
python tests/test_integration.py

# Tests de charge
python tests/test_load.py
```

### Tests avec Docker Compose
```bash
# Dans WSL, racine du projet
cd ~/projects/library-management-system

# Lancer les tests avec Docker
docker-compose -f docker-compose.test.yml up --build

# Tests d'intégration complets
docker-compose -f backend/docker-compose.test.yml up --abort-on-container-exit
```

### Frontend React
```bash
# Installation Node.js dans WSL
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Dans le dossier frontend
cd ~/projects/library-management-system/frontend

# Installation des dépendances
npm install

# Exécution des tests
npm test

# Tests avec couverture
npm run test:coverage
```

## 🚀 Développement avec WSL

### Script de développement optimisé
```bash
#!/bin/bash
# dev-setup.sh - Configuration développement WSL

set -e

PROJECT_DIR="$HOME/projects/library-management-system"
BACKEND_DIR="$PROJECT_DIR/backend"
FRONTEND_DIR="$PROJECT_DIR/frontend"

echo "🚀 Configuration environnement de développement WSL"

# Backend
echo "📦 Configuration Backend..."
cd $BACKEND_DIR

if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ Environnement virtuel créé"
fi

source venv/bin/activate
pip install -r requirements.txt
echo "✅ Dépendances backend installées"

# Frontend
echo "🌐 Configuration Frontend..."
cd $FRONTEND_DIR

if [ ! -d "node_modules" ]; then
    npm install
    echo "✅ Dépendances frontend installées"
fi

# Monitoring
echo "📊 Démarrage monitoring..."
cd $PROJECT_DIR/monitoring
docker-compose -f docker-compose.monitoring.yml up -d
echo "✅ Stack monitoring démarrée"

echo "🎉 Environnement prêt !"
echo "Backend: uvicorn main:app --reload --host 0.0.0.0"
echo "Frontend: npm start"
echo "Grafana: http://localhost:3001"
```

### Scripts de test automatisés
```bash
#!/bin/bash
# run-tests-wsl.sh - Tests automatisés avec WSL

set -e

PROJECT_DIR="$HOME/projects/library-management-system"

echo "🧪 Lancement des tests complets"

# Tests Backend
echo "🐍 Tests Backend Python..."
cd $PROJECT_DIR/backend
source venv/bin/activate

# Tests unitaires
pytest tests/test_unit.py -v

# Tests d'intégration
pytest tests/test_integration.py -v

# Tests de charge
python tests/test_load.py

echo "✅ Tests backend terminés"

# Tests Frontend
echo "⚛️ Tests Frontend React..."
cd $PROJECT_DIR/frontend
npm test -- --coverage --watchAll=false

echo "✅ Tests frontend terminés"

# Tests Docker
echo "🐳 Tests avec Docker..."
cd $PROJECT_DIR
docker-compose -f docker-compose.test.yml up --build --abort-on-container-exit

echo "✅ Tests Docker terminés"

echo "🎉 Tous les tests sont passés !"
```

## 🔄 Intégration CI/CD avec WSL

### GitHub Actions avec WSL
```yaml
# .github/workflows/wsl-tests.yml
name: WSL Tests

on: [push, pull_request]

jobs:
  test-wsl:
    runs-on: windows-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Setup WSL
      uses: Vampire/setup-wsl@v1
      with:
        distribution: Ubuntu-22.04
    
    - name: Install dependencies in WSL
      run: |
        wsl bash -c "
          cd /mnt/d/a/library-management-system/library-management-system &&
          sudo apt update &&
          sudo apt install -y python3 python3-pip python3-venv nodejs npm &&
          cd backend &&
          python3 -m venv venv &&
          source venv/bin/activate &&
          pip install -r requirements.txt
        "
    
    - name: Run tests in WSL
      run: |
        wsl bash -c "
          cd /mnt/d/a/library-management-system/library-management-system/backend &&
          source venv/bin/activate &&
          pytest tests/ -v --cov=.
        "
```

### Script de build avec WSL
```bash
#!/bin/bash
# build-wsl.sh - Build optimisé avec WSL

set -e

PROJECT_DIR="$HOME/projects/library-management-system"

echo "🏗️ Build avec WSL et Docker"

# Build Backend
echo "🔧 Build Backend..."
cd $PROJECT_DIR/backend
docker build -t library-management-backend:latest .

# Build Frontend
echo "🎨 Build Frontend..."
cd $PROJECT_DIR/frontend
npm run build
docker build -t library-management-frontend:latest .

# Tests d'intégration
echo "🧪 Tests d'intégration..."
cd $PROJECT_DIR
docker-compose up --build -d
sleep 30

# Health checks
curl -f http://localhost:8000/health || exit 1
curl -f http://localhost:3000 || exit 1

echo "✅ Build et tests réussis !"
```

## 🛠️ Outils de développement WSL

### Extensions VS Code recommandées
```json
{
  "recommendations": [
    "ms-vscode-remote.remote-wsl",
    "ms-python.python",
    "bradlc.vscode-tailwindcss",
    "ms-vscode.vscode-typescript-next",
    "hashicorp.terraform",
    "ms-kubernetes-tools.vscode-kubernetes-tools"
  ]
}
```

### Configuration VS Code pour WSL
```json
{
  "python.defaultInterpreterPath": "/home/username/projects/library-management-system/backend/venv/bin/python",
  "python.terminal.activateEnvironment": true,
  "terminal.integrated.defaultProfile.windows": "WSL",
  "docker.host": "unix:///var/run/docker.sock"
}
```

## 📊 Monitoring avec WSL

### Prometheus et Grafana
```bash
# Démarrer le monitoring depuis WSL
cd ~/projects/library-management-system/monitoring
docker-compose -f docker-compose.monitoring.yml up -d

# Vérifier les services
docker ps
curl http://localhost:9090  # Prometheus
curl http://localhost:3001  # Grafana
```

### Métriques système WSL
```bash
# Surveiller les ressources WSL
wsl --list --running
wsl --status

# Métriques dans WSL
htop
iotop
nethogs
```

## 🚨 Troubleshooting WSL

### Problèmes courants

**Docker ne démarre pas**
```bash
# Redémarrer le service Docker dans WSL
sudo service docker start
sudo service docker status

# Vérifier les permissions
sudo usermod -aG docker $USER
newgrp docker
```

**Performance lente**
```bash
# Optimiser WSL 2
echo "[wsl2]
memory=8GB
processors=4" > /mnt/c/Users/$USER/.wslconfig

# Redémarrer WSL
wsl --shutdown
```

**Problèmes de réseau**
```bash
# Reset réseau WSL
wsl --shutdown
netsh int ip reset
netsh winsock reset
```

## 🔧 Scripts utilitaires

### Synchronisation de fichiers
```bash
#!/bin/bash
# sync-project.sh - Synchroniser entre Windows et WSL

WINDOWS_PATH="/mnt/d/devopswithcursor/library-management-system"
WSL_PATH="$HOME/projects/library-management-system"

# Synchroniser vers WSL
rsync -av --exclude 'node_modules' --exclude '.git' --exclude 'venv' \
  $WINDOWS_PATH/ $WSL_PATH/

echo "✅ Projet synchronisé vers WSL"
```

### Nettoyage WSL
```bash
#!/bin/bash
# cleanup-wsl.sh - Nettoyage de l'environnement WSL

echo "🧹 Nettoyage WSL..."

# Arrêter les conteneurs
docker stop $(docker ps -aq)
docker rm $(docker ps -aq)

# Nettoyer les images
docker image prune -f
docker volume prune -f

# Nettoyer APT
sudo apt autoremove -y
sudo apt autoclean

echo "✅ Nettoyage terminé"
```

## 📝 Bonnes pratiques WSL

### Performance
- Utiliser WSL 2 pour de meilleures performances Docker
- Garder les fichiers dans le système de fichiers WSL
- Utiliser .wslconfig pour optimiser les ressources

### Sécurité
- Maintenir WSL à jour avec `sudo apt update && sudo apt upgrade`
- Utiliser des environnements virtuels Python
- Séparer les environnements de dev/test/prod

### Workflow
- Utiliser VS Code avec l'extension Remote-WSL
- Configurer des alias pour les commandes fréquentes
- Automatiser avec des scripts bash

---

Avec cette configuration WSL, vous pouvez maintenant développer, tester et déployer efficacement votre système de gestion de bibliothèque dans un environnement Linux optimisé sur Windows ! 🚀