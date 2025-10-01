#!/bin/bash
# Script de test complet optimisé pour WSL
# Usage: ./test-wsl.sh [unit|integration|load|frontend|all]

set -e

PROJECT_DIR="$HOME/projects/library-management-system"
TEST_TYPE=${1:-all}

# Couleurs
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Vérifier si le projet existe
if [ ! -d "$PROJECT_DIR" ]; then
    log_error "Projet non trouvé à $PROJECT_DIR"
    log_info "Exécutez d'abord setup-wsl.sh"
    exit 1
fi

cd "$PROJECT_DIR"

# Tests unitaires backend
run_unit_tests() {
    log_info "🧪 Tests unitaires backend..."
    cd "$PROJECT_DIR/backend"
    
    if [ ! -d "venv" ]; then
        log_error "Environnement virtuel non trouvé"
        return 1
    fi
    
    source venv/bin/activate
    
    # Exécuter les tests unitaires
    pytest tests/test_unit.py -v --tb=short --cov=. --cov-report=term-missing
    
    if [ $? -eq 0 ]; then
        log_success "Tests unitaires réussis"
        return 0
    else
        log_error "Tests unitaires échoués"
        return 1
    fi
}

# Tests d'intégration
run_integration_tests() {
    log_info "🔗 Tests d'intégration..."
    cd "$PROJECT_DIR/backend"
    source venv/bin/activate
    
    # Démarrer une base de données temporaire avec Docker
    if command -v docker &> /dev/null; then
        log_info "Démarrage base de données test..."
        docker run -d --name test-postgres-$$ \
            -e POSTGRES_DB=library_test \
            -e POSTGRES_USER=test_user \
            -e POSTGRES_PASSWORD=test_password \
            -p 5434:5432 \
            postgres:13 > /dev/null
        
        # Attendre que la DB soit prête
        sleep 5
        
        # Configurer la variable d'environnement
        export DATABASE_URL="postgresql://test_user:test_password@localhost:5434/library_test"
        
        # Exécuter les tests
        pytest tests/test_integration.py -v --tb=short
        TEST_RESULT=$?
        
        # Nettoyer
        docker stop test-postgres-$$ > /dev/null
        docker rm test-postgres-$$ > /dev/null
        
        if [ $TEST_RESULT -eq 0 ]; then
            log_success "Tests d'intégration réussis"
            return 0
        else
            log_error "Tests d'intégration échoués"
            return 1
        fi
    else
        log_warning "Docker non disponible, tests d'intégration ignorés"
        return 0
    fi
}

# Tests de charge
run_load_tests() {
    log_info "⚡ Tests de charge..."
    cd "$PROJECT_DIR/backend"
    source venv/bin/activate
    
    # Démarrer temporairement l'application pour les tests de charge
    uvicorn main:app --host 0.0.0.0 --port 8002 > /dev/null 2>&1 &
    UVICORN_PID=$!
    
    # Attendre que l'application démarre
    sleep 5
    
    # Exécuter les tests de charge
    export API_BASE_URL="http://localhost:8002"
    python tests/test_load.py
    TEST_RESULT=$?
    
    # Arrêter l'application
    kill $UVICORN_PID 2>/dev/null || true
    
    if [ $TEST_RESULT -eq 0 ]; then
        log_success "Tests de charge réussis"
        return 0
    else
        log_error "Tests de charge échoués"
        return 1
    fi
}

# Tests frontend
run_frontend_tests() {
    log_info "⚛️ Tests frontend..."
    cd "$PROJECT_DIR/frontend"
    
    if [ ! -d "node_modules" ]; then
        log_warning "node_modules manquant, installation..."
        npm install
    fi
    
    # Exécuter les tests React
    CI=true npm test -- --coverage --watchAll=false --verbose
    
    if [ $? -eq 0 ]; then
        log_success "Tests frontend réussis"
        return 0
    else
        log_error "Tests frontend échoués"
        return 1
    fi
}

# Tests avec Docker Compose
run_docker_tests() {
    log_info "🐳 Tests avec Docker Compose..."
    cd "$PROJECT_DIR"
    
    if ! command -v docker-compose &> /dev/null; then
        log_warning "Docker Compose non disponible"
        return 0
    fi
    
    # Nettoyer les conteneurs existants
    docker-compose -f docker-compose.test.yml down > /dev/null 2>&1 || true
    
    # Exécuter les tests
    docker-compose -f docker-compose.test.yml up --build --abort-on-container-exit
    TEST_RESULT=$?
    
    # Nettoyer
    docker-compose -f docker-compose.test.yml down > /dev/null 2>&1 || true
    
    if [ $TEST_RESULT -eq 0 ]; then
        log_success "Tests Docker réussis"
        return 0
    else
        log_error "Tests Docker échoués"
        return 1
    fi
}

# Générer un rapport de test
generate_report() {
    log_info "📊 Génération du rapport de test..."
    
    REPORT_DIR="$PROJECT_DIR/test-reports"
    mkdir -p "$REPORT_DIR"
    
    REPORT_FILE="$REPORT_DIR/test-report-$(date +%Y%m%d-%H%M%S).md"
    
    cat > "$REPORT_FILE" << EOF
# Rapport de Test - Library Management System

**Date**: $(date)
**Environnement**: WSL - $(lsb_release -d | cut -f2)
**Commit**: $(git rev-parse --short HEAD 2>/dev/null || echo "N/A")

## Résultats des Tests

EOF
    
    echo "Rapport généré: $REPORT_FILE"
}

# Fonction principale
main() {
    log_info "🚀 Tests Library Management System avec WSL"
    log_info "Type de test: $TEST_TYPE"
    
    # Initialiser les compteurs
    TOTAL_TESTS=0
    PASSED_TESTS=0
    
    case $TEST_TYPE in
        "unit")
            TOTAL_TESTS=1
            run_unit_tests && PASSED_TESTS=$((PASSED_TESTS + 1))
            ;;
        "integration")
            TOTAL_TESTS=1
            run_integration_tests && PASSED_TESTS=$((PASSED_TESTS + 1))
            ;;
        "load")
            TOTAL_TESTS=1
            run_load_tests && PASSED_TESTS=$((PASSED_TESTS + 1))
            ;;
        "frontend")
            TOTAL_TESTS=1
            run_frontend_tests && PASSED_TESTS=$((PASSED_TESTS + 1))
            ;;
        "docker")
            TOTAL_TESTS=1
            run_docker_tests && PASSED_TESTS=$((PASSED_TESTS + 1))
            ;;
        "all")
            TOTAL_TESTS=5
            run_unit_tests && PASSED_TESTS=$((PASSED_TESTS + 1))
            run_integration_tests && PASSED_TESTS=$((PASSED_TESTS + 1))
            run_load_tests && PASSED_TESTS=$((PASSED_TESTS + 1))
            run_frontend_tests && PASSED_TESTS=$((PASSED_TESTS + 1))
            run_docker_tests && PASSED_TESTS=$((PASSED_TESTS + 1))
            ;;
        *)
            log_error "Type de test invalide: $TEST_TYPE"
            echo "Types disponibles: unit, integration, load, frontend, docker, all"
            exit 1
            ;;
    esac
    
    # Résumé final
    echo ""
    echo "===================="
    echo "  RÉSUMÉ DES TESTS  "
    echo "===================="
    echo "Total: $TOTAL_TESTS"
    echo "Réussis: $PASSED_TESTS"
    echo "Échoués: $((TOTAL_TESTS - PASSED_TESTS))"
    echo ""
    
    if [ $PASSED_TESTS -eq $TOTAL_TESTS ]; then
        log_success "🎉 Tous les tests sont passés !"
        generate_report
        exit 0
    else
        log_error "❌ Certains tests ont échoué"
        exit 1
    fi
}

# Afficher l'aide
if [ "$1" = "--help" ] || [ "$1" = "-h" ]; then
    echo "Usage: $0 [TYPE]"
    echo ""
    echo "Types de tests disponibles:"
    echo "  unit        - Tests unitaires backend"
    echo "  integration - Tests d'intégration"
    echo "  load        - Tests de charge"
    echo "  frontend    - Tests React"
    echo "  docker      - Tests avec Docker Compose"
    echo "  all         - Tous les tests (défaut)"
    echo ""
    echo "Exemples:"
    echo "  $0 unit"
    echo "  $0 all"
    exit 0
fi

# Exécuter la fonction principale
main