#!/bin/bash

# Script de déploiement automatisé pour Library Management System
# Usage: ./deploy.sh [dev|staging|prod]

set -e

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENVIRONMENT=${1:-dev}
VALID_ENVS="dev staging prod"

# Couleurs pour les logs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Fonctions utilitaires
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

# Validation de l'environnement
validate_environment() {
    if [[ ! " $VALID_ENVS " =~ " $ENVIRONMENT " ]]; then
        log_error "Environnement invalide: $ENVIRONMENT"
        log_info "Environnements valides: $VALID_ENVS"
        exit 1
    fi
}

# Vérification des prérequis
check_prerequisites() {
    log_info "Vérification des prérequis..."
    
    # Vérifier kubectl
    if ! command -v kubectl &> /dev/null; then
        log_error "kubectl n'est pas installé"
        exit 1
    fi
    
    # Vérifier terraform
    if ! command -v terraform &> /dev/null; then
        log_error "terraform n'est pas installé"
        exit 1
    fi
    
    # Vérifier docker
    if ! command -v docker &> /dev/null; then
        log_error "docker n'est pas installé"
        exit 1
    fi
    
    # Vérifier la connexion kubectl
    if ! kubectl cluster-info &> /dev/null; then
        log_error "Impossible de se connecter au cluster Kubernetes"
        exit 1
    fi
    
    log_success "Tous les prérequis sont satisfaits"
}

# Construction de l'image Docker
build_docker_image() {
    log_info "Construction de l'image Docker..."
    
    cd "$SCRIPT_DIR/../backend"
    
    # Tag basé sur l'environnement
    if [ "$ENVIRONMENT" = "prod" ]; then
        IMAGE_TAG="v1.0.0"
    else
        IMAGE_TAG="latest"
    fi
    
    docker build -t "library-management-system:$IMAGE_TAG" .
    
    # Pour les environnements non-locaux, pousser vers un registry
    if [ "$ENVIRONMENT" != "dev" ]; then
        log_info "Push de l'image vers le registry..."
        # docker push "your-registry/library-management-system:$IMAGE_TAG"
        log_warning "Push vers registry désactivé (à configurer)"
    fi
    
    log_success "Image Docker construite: library-management-system:$IMAGE_TAG"
}

# Initialisation Terraform
init_terraform() {
    log_info "Initialisation de Terraform..."
    
    cd "$SCRIPT_DIR"
    
    terraform init
    
    log_success "Terraform initialisé"
}

# Planification Terraform
plan_terraform() {
    log_info "Planification du déploiement Terraform..."
    
    cd "$SCRIPT_DIR"
    
    terraform plan \
        -var-file="environments/${ENVIRONMENT}.tfvars" \
        -out="tfplan-${ENVIRONMENT}"
    
    log_success "Plan Terraform généré: tfplan-${ENVIRONMENT}"
}

# Application Terraform
apply_terraform() {
    log_info "Application du déploiement Terraform..."
    
    cd "$SCRIPT_DIR"
    
    terraform apply "tfplan-${ENVIRONMENT}"
    
    log_success "Déploiement Terraform appliqué"
}

# Vérification du déploiement
verify_deployment() {
    log_info "Vérification du déploiement..."
    
    # Obtenir le namespace
    NAMESPACE=$(terraform output -raw namespace)
    
    # Attendre que les pods soient prêts
    log_info "Attente de la disponibilité des pods..."
    kubectl wait --for=condition=ready pod \
        -l app=library-management \
        -n "$NAMESPACE" \
        --timeout=300s
    
    # Vérifier le statut du déploiement
    READY_REPLICAS=$(kubectl get deployment -n "$NAMESPACE" -o jsonpath='{.items[0].status.readyReplicas}')
    DESIRED_REPLICAS=$(kubectl get deployment -n "$NAMESPACE" -o jsonpath='{.items[0].status.replicas}')
    
    if [ "$READY_REPLICAS" = "$DESIRED_REPLICAS" ]; then
        log_success "Déploiement vérifié: $READY_REPLICAS/$DESIRED_REPLICAS pods prêts"
    else
        log_error "Déploiement incomplet: $READY_REPLICAS/$DESIRED_REPLICAS pods prêts"
        exit 1
    fi
    
    # Afficher les informations de connexion
    log_info "Informations de connexion:"
    terraform output -json service_urls | jq -r '.internal, .external'
}

# Fonction de nettoyage en cas d'erreur
cleanup() {
    log_warning "Nettoyage en cours..."
    rm -f "tfplan-${ENVIRONMENT}"
}

# Trap pour le nettoyage
trap cleanup EXIT

# Fonction principale
main() {
    log_info "=== Déploiement Library Management System ==="
    log_info "Environnement: $ENVIRONMENT"
    
    validate_environment
    check_prerequisites
    build_docker_image
    init_terraform
    plan_terraform
    
    # Demander confirmation pour les environnements de production
    if [ "$ENVIRONMENT" = "prod" ]; then
        log_warning "Vous êtes sur le point de déployer en PRODUCTION!"
        read -p "Êtes-vous sûr de vouloir continuer? (yes/no): " -r
        if [[ ! $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
            log_info "Déploiement annulé"
            exit 0
        fi
    fi
    
    apply_terraform
    verify_deployment
    
    log_success "=== Déploiement terminé avec succès ==="
    log_info "Utilisez les commandes suivantes pour interagir avec l'application:"
    terraform output -json kubectl_commands | jq -r 'to_entries[] | "\(.key): \(.value)"'
}

# Exécution du script principal
main "$@"