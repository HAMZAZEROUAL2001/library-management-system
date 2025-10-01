#!/bin/bash
# Script pour démarrer le serveur FastAPI dans WSL

echo "🚀 Démarrage du serveur FastAPI..."
echo "📁 Répertoire: $(pwd)"

# Activer l'environnement virtuel
source ~/library_env/bin/activate

# Vérifier que nous sommes dans le bon répertoire
if [ ! -f "main.py" ]; then
    echo "❌ Erreur: main.py non trouvé. Changement de répertoire..."
    cd /mnt/d/devopswithcursor/library-management-system/backend
fi

# Tester l'importation
echo "🧪 Test d'importation du module main..."
python -c "import main; print('✅ Module main importé avec succès')" || {
    echo "❌ Erreur lors de l'importation de main.py"
    exit 1
}

# Démarrer le serveur
echo "🌐 Démarrage d'uvicorn sur http://127.0.0.1:8000..."
uvicorn main:app --host 127.0.0.1 --port 8000 --reload