@echo off
setlocal enabledelayedexpansion

REM Script de déploiement automatisé pour Library Management System (Windows)
REM Usage: deploy.bat [dev|staging|prod]

set "ENVIRONMENT=%~1"
if "%ENVIRONMENT%"=="" set "ENVIRONMENT=dev"

set "SCRIPT_DIR=%~dp0"
set "VALID_ENVS=dev staging prod"

REM Validation de l'environnement
echo %VALID_ENVS% | find "%ENVIRONMENT%" >nul
if errorlevel 1 (
    echo [ERROR] Environnement invalide: %ENVIRONMENT%
    echo [INFO] Environnements valides: %VALID_ENVS%
    exit /b 1
)

echo [INFO] === Déploiement Library Management System ===
echo [INFO] Environnement: %ENVIRONMENT%

REM Vérification des prérequis
echo [INFO] Vérification des prérequis...

kubectl version --client >nul 2>&1
if errorlevel 1 (
    echo [ERROR] kubectl n'est pas installé
    exit /b 1
)

terraform version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] terraform n'est pas installé
    exit /b 1
)

docker version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] docker n'est pas installé
    exit /b 1
)

kubectl cluster-info >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Impossible de se connecter au cluster Kubernetes
    exit /b 1
)

echo [SUCCESS] Tous les prérequis sont satisfaits

REM Construction de l'image Docker
echo [INFO] Construction de l'image Docker...
cd /d "%SCRIPT_DIR%\..\backend"

if "%ENVIRONMENT%"=="prod" (
    set "IMAGE_TAG=v1.0.0"
) else (
    set "IMAGE_TAG=latest"
)

docker build -t "library-management-system:!IMAGE_TAG!" .
if errorlevel 1 (
    echo [ERROR] Échec de la construction de l'image Docker
    exit /b 1
)

echo [SUCCESS] Image Docker construite: library-management-system:!IMAGE_TAG!

REM Initialisation Terraform
echo [INFO] Initialisation de Terraform...
cd /d "%SCRIPT_DIR%"

terraform init
if errorlevel 1 (
    echo [ERROR] Échec de l'initialisation Terraform
    exit /b 1
)

echo [SUCCESS] Terraform initialisé

REM Planification Terraform
echo [INFO] Planification du déploiement Terraform...

terraform plan -var-file="environments\%ENVIRONMENT%.tfvars" -out="tfplan-%ENVIRONMENT%"
if errorlevel 1 (
    echo [ERROR] Échec de la planification Terraform
    exit /b 1
)

echo [SUCCESS] Plan Terraform généré: tfplan-%ENVIRONMENT%

REM Confirmation pour la production
if "%ENVIRONMENT%"=="prod" (
    echo [WARNING] Vous êtes sur le point de déployer en PRODUCTION!
    set /p "CONFIRM=Êtes-vous sûr de vouloir continuer? (yes/no): "
    if not "!CONFIRM!"=="yes" (
        echo [INFO] Déploiement annulé
        del "tfplan-%ENVIRONMENT%" >nul 2>&1
        exit /b 0
    )
)

REM Application Terraform
echo [INFO] Application du déploiement Terraform...

terraform apply "tfplan-%ENVIRONMENT%"
if errorlevel 1 (
    echo [ERROR] Échec de l'application Terraform
    exit /b 1
)

echo [SUCCESS] Déploiement Terraform appliqué

REM Vérification du déploiement
echo [INFO] Vérification du déploiement...

for /f "tokens=*" %%i in ('terraform output -raw namespace') do set "NAMESPACE=%%i"

echo [INFO] Attente de la disponibilité des pods...
kubectl wait --for=condition=ready pod -l app=library-management -n "%NAMESPACE%" --timeout=300s
if errorlevel 1 (
    echo [ERROR] Timeout lors de l'attente des pods
    exit /b 1
)

echo [SUCCESS] === Déploiement terminé avec succès ===
echo [INFO] Utilisez les commandes kubectl suivantes pour interagir avec l'application:

for /f "tokens=*" %%i in ('terraform output -json kubectl_commands') do (
    echo %%i
)

REM Nettoyage
del "tfplan-%ENVIRONMENT%" >nul 2>&1

endlocal