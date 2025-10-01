#!/bin/bash
# Script de développement rapide avec WSL
# Usage: ./quick-dev-wsl.sh

set -e

# Configuration
PROJECT_DIR="$HOME/projects/library-management-system"
BACKEND_PORT=8000
FRONTEND_PORT=3000

echo "🚀 Démarrage rapide Library Management System avec WSL"

# Vérifier si le projet existe
if [ ! -d "$PROJECT_DIR" ]; then
    echo "❌ Projet non trouvé. Exécutez d'abord setup-wsl.sh"
    exit 1
fi

cd "$PROJECT_DIR"

# Fonction pour démarrer le backend
start_backend() {
    echo "🐍 Démarrage Backend sur port $BACKEND_PORT..."
    cd "$PROJECT_DIR/backend"
    
    # Activer l'environnement virtuel
    if [ ! -d "venv" ]; then
        echo "⚠️ Environnement virtuel non trouvé, création..."
        python3 -m venv venv
        source venv/bin/activate
        pip install -r requirements.txt
    else
        source venv/bin/activate
    fi
    
    # Vérifier si le port est libre
    if netstat -tuln | grep -q ":$BACKEND_PORT "; then
        echo "⚠️ Port $BACKEND_PORT occupé, arrêt du processus..."
        pkill -f "uvicorn main:app" || true
        sleep 2
    fi
    
    # Démarrer FastAPI
    echo "✅ Backend démarré: http://localhost:$BACKEND_PORT"
    echo "📖 Documentation: http://localhost:$BACKEND_PORT/docs"
    uvicorn main:app --reload --host 0.0.0.0 --port $BACKEND_PORT &
    BACKEND_PID=$!
}

# Fonction pour démarrer le frontend
start_frontend() {
    echo "⚛️ Démarrage Frontend sur port $FRONTEND_PORT..."
    cd "$PROJECT_DIR/frontend"
    
    # Vérifier les dépendances
    if [ ! -d "node_modules" ]; then
        echo "⚠️ node_modules non trouvé, installation..."
        npm install
    fi
    
    # Vérifier si le port est libre
    if netstat -tuln | grep -q ":$FRONTEND_PORT "; then
        echo "⚠️ Port $FRONTEND_PORT occupé, arrêt du processus..."
        pkill -f "react-scripts start" || true
        sleep 2
    fi
    
    # Démarrer React
    echo "✅ Frontend démarré: http://localhost:$FRONTEND_PORT"
    BROWSER=none npm start &
    FRONTEND_PID=$!
}

# Fonction pour démarrer le monitoring
start_monitoring() {
    echo "📊 Démarrage Monitoring..."
    cd "$PROJECT_DIR/monitoring"
    
    # Vérifier Docker
    if ! command -v docker &> /dev/null; then
        echo "⚠️ Docker non disponible, monitoring ignoré"
        return
    fi
    
    # Démarrer la stack monitoring
    docker-compose -f docker-compose.monitoring.yml up -d
    echo "✅ Monitoring démarré:"
    echo "   Grafana: http://localhost:3001 (admin/admin123)"
    echo "   Prometheus: http://localhost:9090"
}

# Fonction de nettoyage
cleanup() {
    echo "🧹 Arrêt des services..."
    
    # Arrêter les processus Python et Node
    [ ! -z "$BACKEND_PID" ] && kill $BACKEND_PID 2>/dev/null || true
    [ ! -z "$FRONTEND_PID" ] && kill $FRONTEND_PID 2>/dev/null || true
    
    # Arrêter le monitoring
    cd "$PROJECT_DIR/monitoring"
    docker-compose -f docker-compose.monitoring.yml down 2>/dev/null || true
    
    echo "✅ Services arrêtés"
    exit 0
}

# Configurer le trap pour le nettoyage
trap cleanup SIGINT SIGTERM

# Menu de sélection
echo "Sélectionnez les services à démarrer:"
echo "1) Tout (Backend + Frontend + Monitoring)"
echo "2) Backend seulement"
echo "3) Frontend seulement"
echo "4) Backend + Frontend"
echo "5) Tests rapides"
read -p "Votre choix (1-5): " choice

case $choice in
    1)
        start_backend
        sleep 5
        start_frontend
        sleep 3
        start_monitoring
        ;;
    2)
        start_backend
        ;;
    3)
        start_frontend
        ;;
    4)
        start_backend
        sleep 5
        start_frontend
        ;;
    5)
        echo "🧪 Exécution des tests rapides..."
        cd "$PROJECT_DIR/backend"
        source venv/bin/activate
        pytest tests/test_unit.py -v --tb=short
        cd "$PROJECT_DIR/frontend"
        npm test -- --watchAll=false
        echo "✅ Tests terminés"
        exit 0
        ;;
    *)
        echo "❌ Choix invalide"
        exit 1
        ;;
esac

echo ""
echo "🎉 Services démarrés avec succès !"
echo ""
echo "📍 URLs disponibles:"
echo "   🌐 Frontend:     http://localhost:$FRONTEND_PORT"
echo "   🔧 Backend:      http://localhost:$BACKEND_PORT"
echo "   📖 API Docs:     http://localhost:$BACKEND_PORT/docs"
echo "   📊 Grafana:      http://localhost:3001"
echo "   🔍 Prometheus:   http://localhost:9090"
echo ""
echo "⌨️  Appuyez sur Ctrl+C pour arrêter tous les services"
echo ""

# Attendre indéfiniment (jusqu'à Ctrl+C)
while true; do
    sleep 1
done