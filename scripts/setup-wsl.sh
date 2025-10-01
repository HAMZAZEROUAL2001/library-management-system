#!/bin/bash
# Script de configuration rapide WSL pour Library Management System
# Usage: ./setup-wsl.sh

set -e

# Couleurs pour les logs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Configuration
PROJECT_NAME="library-management-system"
PROJECT_DIR="$HOME/projects/$PROJECT_NAME"
WINDOWS_PROJECT="/mnt/d/devopswithcursor/$PROJECT_NAME"

log_info "🚀 Configuration WSL pour Library Management System"

# Vérifier si on est dans WSL
if [ -z "$WSL_DISTRO_NAME" ]; then
    log_error "Ce script doit être exécuté dans WSL"
    exit 1
fi

log_success "WSL détecté: $WSL_DISTRO_NAME"

# Créer la structure de projet
log_info "📁 Création de la structure de projet..."
mkdir -p ~/projects
cd ~/projects

# Copier ou lier le projet depuis Windows
if [ -d "$WINDOWS_PROJECT" ]; then
    log_info "📋 Copie du projet depuis Windows..."
    cp -r "$WINDOWS_PROJECT" "$PROJECT_DIR"
    log_success "Projet copié vers $PROJECT_DIR"
else
    log_warning "Projet Windows non trouvé à $WINDOWS_PROJECT"
    log_info "📥 Clonage du repository..."
    git clone <repository-url> "$PROJECT_DIR" || {
        log_error "Impossible de cloner le repository"
        exit 1
    }
fi

cd "$PROJECT_DIR"

# Mise à jour du système
log_info "🔄 Mise à jour du système Ubuntu..."
sudo apt update && sudo apt upgrade -y

# Installation des dépendances système
log_info "📦 Installation des dépendances système..."
sudo apt install -y \
    curl \
    wget \
    git \
    build-essential \
    software-properties-common \
    apt-transport-https \
    ca-certificates \
    gnupg \
    lsb-release \
    htop \
    tree \
    jq

# Installation Python 3.9+
log_info "🐍 Installation Python..."
sudo apt install -y python3 python3-pip python3-venv python3-dev
python3 --version

# Installation Node.js 18
log_info "📗 Installation Node.js..."
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs
node --version
npm --version

# Configuration Backend Python
log_info "🔧 Configuration Backend Python..."
cd "$PROJECT_DIR/backend"

if [ ! -d "venv" ]; then
    python3 -m venv venv
    log_success "Environnement virtuel Python créé"
fi

source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
log_success "Dépendances Python installées"

# Configuration Frontend React
log_info "⚛️ Configuration Frontend React..."
cd "$PROJECT_DIR/frontend"

if [ ! -d "node_modules" ]; then
    npm install
    log_success "Dépendances Node.js installées"
fi

# Vérification Docker
log_info "🐳 Vérification Docker..."
if ! command -v docker &> /dev/null; then
    log_error "Docker non installé. Installez Docker Desktop avec WSL 2 backend"
    exit 1
fi

docker --version
docker-compose --version
log_success "Docker configuré"

# Configuration des scripts utilitaires
log_info "🛠️ Création des scripts utilitaires..."

# Script de démarrage dev
cat > "$PROJECT_DIR/start-dev-wsl.sh" << 'EOF'
#!/bin/bash
# Script de démarrage développement WSL

set -e

PROJECT_DIR="$HOME/projects/library-management-system"

echo "🚀 Démarrage environnement de développement"

# Terminal 1: Backend
gnome-terminal --tab --title="Backend" -- bash -c "
    cd $PROJECT_DIR/backend
    source venv/bin/activate
    echo '🐍 Backend démarré sur http://localhost:8000'
    uvicorn main:app --reload --host 0.0.0.0 --port 8000
    exec bash
" &

# Terminal 2: Frontend
gnome-terminal --tab --title="Frontend" -- bash -c "
    cd $PROJECT_DIR/frontend
    echo '⚛️ Frontend démarré sur http://localhost:3000'
    npm start
    exec bash
" &

# Terminal 3: Monitoring
gnome-terminal --tab --title="Monitoring" -- bash -c "
    cd $PROJECT_DIR/monitoring
    echo '📊 Démarrage monitoring...'
    docker-compose -f docker-compose.monitoring.yml up
    exec bash
" &

echo "✅ Environnement démarré dans 3 onglets"
EOF

chmod +x "$PROJECT_DIR/start-dev-wsl.sh"

# Script de tests complets
cat > "$PROJECT_DIR/run-all-tests-wsl.sh" << 'EOF'
#!/bin/bash
# Tests complets avec WSL

set -e

PROJECT_DIR="$HOME/projects/library-management-system"
SUCCESS=0

echo "🧪 Lancement des tests complets"

# Tests Backend
echo "🐍 Tests Backend..."
cd $PROJECT_DIR/backend
source venv/bin/activate

echo "  - Tests unitaires..."
pytest tests/test_unit.py -v || SUCCESS=1

echo "  - Tests d'intégration..."
pytest tests/test_integration.py -v || SUCCESS=1

echo "  - Tests de charge..."
python tests/test_load.py || SUCCESS=1

# Tests Frontend
echo "⚛️ Tests Frontend..."
cd $PROJECT_DIR/frontend
npm test -- --coverage --watchAll=false || SUCCESS=1

# Tests Docker si disponible
if command -v docker &> /dev/null; then
    echo "🐳 Tests Docker..."
    cd $PROJECT_DIR
    docker-compose -f docker-compose.test.yml up --build --abort-on-container-exit || SUCCESS=1
fi

if [ $SUCCESS -eq 0 ]; then
    echo "✅ Tous les tests sont passés !"
else
    echo "❌ Certains tests ont échoué"
    exit 1
fi
EOF

chmod +x "$PROJECT_DIR/run-all-tests-wsl.sh"

# Script de build complet
cat > "$PROJECT_DIR/build-wsl.sh" << 'EOF'
#!/bin/bash
# Build complet avec WSL

set -e

PROJECT_DIR="$HOME/projects/library-management-system"

echo "🏗️ Build complet avec WSL"

# Build Backend
echo "🔧 Build Backend..."
cd $PROJECT_DIR/backend
docker build -t library-management-backend:latest .

# Build Frontend
echo "🎨 Build Frontend..."
cd $PROJECT_DIR/frontend
npm run build
docker build -t library-management-frontend:latest .

echo "✅ Build terminé"
echo "Images créées:"
docker images | grep library-management
EOF

chmod +x "$PROJECT_DIR/build-wsl.sh"

# Configuration des alias utiles
log_info "⚙️ Configuration des alias..."
cat >> ~/.bashrc << EOF

# Alias Library Management System
alias lms-dev='cd $PROJECT_DIR && ./start-dev-wsl.sh'
alias lms-test='cd $PROJECT_DIR && ./run-all-tests-wsl.sh'
alias lms-build='cd $PROJECT_DIR && ./build-wsl.sh'
alias lms-backend='cd $PROJECT_DIR/backend && source venv/bin/activate'
alias lms-frontend='cd $PROJECT_DIR/frontend'
alias lms-infra='cd $PROJECT_DIR/infrastructure'
alias lms-logs='cd $PROJECT_DIR && docker-compose logs -f'
EOF

# Configuration Git
log_info "📝 Configuration Git..."
git config --global core.autocrlf false
git config --global core.eol lf

# Test de l'installation
log_info "🧪 Test de l'installation..."
cd "$PROJECT_DIR/backend"
source venv/bin/activate
python -c "import fastapi, sqlalchemy, pytest; print('✅ Modules Python OK')"

cd "$PROJECT_DIR/frontend"
npm list react typescript --depth=0 && echo "✅ Modules Node.js OK" || log_warning "Vérifiez les dépendances Node.js"

# Résumé final
log_success "🎉 Configuration WSL terminée avec succès !"
echo ""
echo "📍 Projet installé dans: $PROJECT_DIR"
echo ""
echo "🚀 Commandes disponibles:"
echo "  lms-dev     - Démarrer l'environnement de développement"
echo "  lms-test    - Exécuter tous les tests"
echo "  lms-build   - Builder les images Docker"
echo "  lms-backend - Aller au backend et activer l'environnement Python"
echo "  lms-frontend- Aller au frontend"
echo ""
echo "📖 Pour utiliser les alias, rechargez le shell:"
echo "  source ~/.bashrc"
echo ""
echo "🌐 URLs de développement:"
echo "  Backend:     http://localhost:8000"
echo "  Frontend:    http://localhost:3000"
echo "  API Docs:    http://localhost:8000/docs"
echo "  Grafana:     http://localhost:3001"
echo "  Prometheus:  http://localhost:9090"