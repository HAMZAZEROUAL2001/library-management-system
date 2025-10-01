@echo off
setlocal enabledelayedexpansion

REM Script de configuration WSL pour Windows
REM Usage: setup-wsl.bat

echo.
echo ==========================================
echo  Configuration WSL Library Management 
echo ==========================================
echo.

REM Vérifier si WSL est installé
wsl --list >nul 2>&1
if errorlevel 1 (
    echo [ERROR] WSL n'est pas installé ou configuré
    echo.
    echo Pour installer WSL, exécutez en tant qu'administrateur:
    echo   wsl --install -d Ubuntu-22.04
    echo.
    echo Puis redémarrez Windows et relancez ce script.
    pause
    exit /b 1
)

echo [INFO] WSL détecté, vérification de la distribution...
wsl --list --verbose

echo.
echo [INFO] Lancement de la configuration dans WSL...
echo.

REM Vérifier si le projet existe
set PROJECT_PATH=d:\devopswithcursor\library-management-system
if not exist "%PROJECT_PATH%" (
    echo [ERROR] Projet non trouvé à %PROJECT_PATH%
    pause
    exit /b 1
)

REM Exécuter le script de configuration dans WSL
wsl bash -c "
# Navigation vers le projet Windows depuis WSL
cd /mnt/d/devopswithcursor/library-management-system

# Rendre le script exécutable
chmod +x scripts/setup-wsl.sh

# Exécuter la configuration
./scripts/setup-wsl.sh
"

if errorlevel 1 (
    echo [ERROR] Erreur lors de la configuration WSL
    pause
    exit /b 1
)

echo.
echo [SUCCESS] Configuration WSL terminée !
echo.
echo Prochaines étapes:
echo 1. Ouvrir WSL: wsl
echo 2. Aller au projet: cd ~/projects/library-management-system
echo 3. Charger les alias: source ~/.bashrc
echo 4. Démarrer le dev: lms-dev
echo.
pause