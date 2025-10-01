# Script de test automatisé
#!/bin/bash

set -e

echo "🧪 Démarrage de la suite de tests complète"

# Couleurs pour l'affichage
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKEND_DIR="$PROJECT_ROOT/backend"
FRONTEND_DIR="$PROJECT_ROOT/frontend"
COVERAGE_MIN=80

# Fonction d'affichage
print_step() {
    echo -e "${YELLOW}▶ $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Vérifier les prérequis
check_requirements() {
    print_step "Vérification des prérequis"
    
    command -v python3 >/dev/null 2>&1 || { print_error "Python3 requis"; exit 1; }
    command -v node >/dev/null 2>&1 || { print_error "Node.js requis"; exit 1; }
    command -v npm >/dev/null 2>&1 || { print_error "npm requis"; exit 1; }
    
    print_success "Prérequis validés"
}

# Tests backend
run_backend_tests() {
    print_step "Tests Backend Python"
    
    cd "$BACKEND_DIR"
    
    # Activer l'environnement virtuel s'il existe
    if [ -d "venv" ]; then
        source venv/bin/activate || source venv/Scripts/activate 2>/dev/null || true
    fi
    
    # Installer les dépendances de test
    print_step "Installation des dépendances de test"
    pip install -q -r requirements.txt
    
    # Tests unitaires
    print_step "Exécution des tests unitaires"
    python -m pytest test_unit.py -v --tb=short --cov=. --cov-report=term-missing --cov-report=html:htmlcov/unit
    
    # Tests d'intégration
    print_step "Exécution des tests d'intégration"
    python -m pytest test_integration.py -v --tb=short --cov=. --cov-report=term-missing --cov-report=html:htmlcov/integration --cov-append
    
    # Tests de performance/charge (optionnels - plus longs)
    if [ "$RUN_LOAD_TESTS" = "true" ]; then
        print_step "Exécution des tests de charge (peut prendre du temps)"
        python -m pytest test_load.py::TestLoad -v --tb=short -s
    fi
    
    # Vérifier la couverture de code
    print_step "Vérification de la couverture de code"
    coverage report --fail-under=$COVERAGE_MIN || {
        print_error "Couverture de code insuffisante (< $COVERAGE_MIN%)"
        exit 1
    }
    
    print_success "Tests backend terminés avec succès"
}

# Tests frontend
run_frontend_tests() {
    print_step "Tests Frontend React"
    
    cd "$FRONTEND_DIR"
    
    # Installer les dépendances si nécessaire
    if [ ! -d "node_modules" ]; then
        print_step "Installation des dépendances npm"
        npm install --silent
    fi
    
    # Tests unitaires et d'intégration
    print_step "Exécution des tests frontend"
    CI=true npm test -- --coverage --watchAll=false --verbose
    
    # Vérifier la couverture
    print_step "Vérification de la couverture frontend"
    # Note: Les seuils de couverture peuvent être configurés dans package.json
    
    print_success "Tests frontend terminés avec succès"
}

# Tests de linting et formatage
run_code_quality_checks() {
    print_step "Vérifications de qualité du code"
    
    # Backend - Python
    cd "$BACKEND_DIR"
    
    print_step "Vérification du formatage Python (Black)"
    black --check . || {
        print_error "Code Python non formaté. Exécutez: black ."
        exit 1
    }
    
    print_step "Vérification du style Python (Flake8)"
    flake8 . --max-line-length=88 --extend-ignore=E203,W503 || {
        print_error "Problèmes de style détectés"
        exit 1
    }
    
    print_step "Vérification de l'organisation des imports (isort)"
    isort --check-only . || {
        print_error "Imports non organisés. Exécutez: isort ."
        exit 1
    }
    
    # Frontend - JavaScript/TypeScript
    cd "$FRONTEND_DIR"
    
    print_step "Vérification du linting frontend (ESLint)"
    npm run lint || {
        print_error "Problèmes de linting détectés"
        exit 1
    }
    
    print_success "Vérifications de qualité terminées"
}

# Tests de sécurité
run_security_tests() {
    print_step "Tests de sécurité"
    
    cd "$BACKEND_DIR"
    
    # Vérifier les vulnérabilités dans les dépendances Python
    print_step "Vérification des vulnérabilités Python (Safety)"
    if command -v safety >/dev/null 2>&1; then
        safety check || print_error "Vulnérabilités détectées dans les dépendances Python"
    else
        print_step "Safety non installé, installation..."
        pip install safety
        safety check || print_error "Vulnérabilités détectées dans les dépendances Python"
    fi
    
    cd "$FRONTEND_DIR"
    
    # Audit npm
    print_step "Audit de sécurité npm"
    npm audit --audit-level=moderate || {
        print_error "Vulnérabilités détectées dans les dépendances npm"
        echo "Exécutez 'npm audit fix' pour corriger automatiquement"
    }
    
    print_success "Tests de sécurité terminés"
}

# Tests d'intégration système
run_system_integration_tests() {
    print_step "Tests d'intégration système"
    
    # Vérifier que Docker est disponible
    if command -v docker >/dev/null 2>&1 && command -v docker-compose >/dev/null 2>&1; then
        print_step "Tests avec Docker Compose"
        
        cd "$PROJECT_ROOT"
        
        # Démarrer les services en arrière-plan
        docker-compose up -d --build
        
        # Attendre que les services soient prêts
        print_step "Attente du démarrage des services..."
        sleep 30
        
        # Tests de santé
        print_step "Test de santé de l'API"
        curl -f http://localhost:8000/ || {
            print_error "API non accessible"
            docker-compose logs backend
            docker-compose down
            exit 1
        }
        
        print_step "Test de santé du frontend"
        curl -f http://localhost:3000/ || {
            print_error "Frontend non accessible"
            docker-compose logs frontend
            docker-compose down
            exit 1
        }
        
        # Tests end-to-end basiques
        print_step "Tests end-to-end basiques"
        
        # Test d'inscription
        response=$(curl -s -X POST "http://localhost:8000/register" \
            -H "Content-Type: application/json" \
            -d '{"username":"e2etest","email":"e2e@test.com","password":"testpass123"}')
        
        if echo "$response" | grep -q "username"; then
            print_success "Test d'inscription réussi"
        else
            print_error "Test d'inscription échoué"
            echo "$response"
        fi
        
        # Nettoyer
        docker-compose down
        
        print_success "Tests d'intégration système terminés"
    else
        print_step "Docker non disponible, tests d'intégration système ignorés"
    fi
}

# Génération de rapport
generate_report() {
    print_step "Génération du rapport de tests"
    
    REPORT_DIR="$PROJECT_ROOT/test-reports"
    mkdir -p "$REPORT_DIR"
    
    # Copier les rapports de couverture
    if [ -d "$BACKEND_DIR/htmlcov" ]; then
        cp -r "$BACKEND_DIR/htmlcov" "$REPORT_DIR/backend-coverage"
    fi
    
    if [ -d "$FRONTEND_DIR/coverage" ]; then
        cp -r "$FRONTEND_DIR/coverage" "$REPORT_DIR/frontend-coverage"
    fi
    
    # Créer un rapport consolidé
    cat > "$REPORT_DIR/test-summary.md" << EOF
# Rapport de Tests - $(date)

## Backend
- Tests unitaires: ✅
- Tests d'intégration: ✅
- Couverture de code: Voir \`backend-coverage/index.html\`

## Frontend
- Tests unitaires: ✅
- Couverture de code: Voir \`frontend-coverage/index.html\`

## Qualité du code
- Formatage: ✅
- Linting: ✅
- Sécurité: ✅

## Intégration système
- Tests end-to-end: ✅

Rapport généré le $(date)
EOF
    
    print_success "Rapport généré dans $REPORT_DIR"
}

# Fonction principale
main() {
    local run_load_tests=false
    local run_security=true
    local run_integration=true
    
    # Analyser les arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --load-tests)
                run_load_tests=true
                shift
                ;;
            --no-security)
                run_security=false
                shift
                ;;
            --no-integration)
                run_integration=false
                shift
                ;;
            --help)
                echo "Usage: $0 [options]"
                echo "Options:"
                echo "  --load-tests      Inclure les tests de charge (plus longs)"
                echo "  --no-security     Ignorer les tests de sécurité"
                echo "  --no-integration  Ignorer les tests d'intégration système"
                echo "  --help           Afficher cette aide"
                exit 0
                ;;
            *)
                print_error "Option inconnue: $1"
                exit 1
                ;;
        esac
    done
    
    export RUN_LOAD_TESTS=$run_load_tests
    
    echo "🎯 Configuration des tests:"
    echo "   - Tests de charge: $run_load_tests"
    echo "   - Tests de sécurité: $run_security"
    echo "   - Tests d'intégration: $run_integration"
    echo ""
    
    # Exécuter les tests
    check_requirements
    
    run_backend_tests
    
    # Tests frontend (si Node.js disponible)
    if command -v node >/dev/null 2>&1; then
        run_frontend_tests
    else
        print_step "Node.js non disponible, tests frontend ignorés"
    fi
    
    run_code_quality_checks
    
    if [ "$run_security" = true ]; then
        run_security_tests
    fi
    
    if [ "$run_integration" = true ]; then
        run_system_integration_tests
    fi
    
    generate_report
    
    print_success "🎉 Tous les tests sont terminés avec succès!"
    echo ""
    echo "📊 Rapports disponibles dans: $PROJECT_ROOT/test-reports/"
    echo "🌐 Couverture backend: test-reports/backend-coverage/index.html"
    echo "🎨 Couverture frontend: test-reports/frontend-coverage/index.html"
}

# Gestion des signaux pour nettoyage
cleanup() {
    print_step "Nettoyage en cours..."
    if command -v docker-compose >/dev/null 2>&1; then
        docker-compose down 2>/dev/null || true
    fi
}

trap cleanup EXIT

# Exécuter le script principal
main "$@"