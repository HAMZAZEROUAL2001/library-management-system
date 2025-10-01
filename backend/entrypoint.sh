#!/bin/sh

# Afficher des informations de débogage
echo "Démarrage de l'application Library Management System"
echo "Répertoire de travail actuel : $(pwd)"
echo "Contenu du répertoire :"
ls -la

# Vérifier les dépendances installées
echo "Dépendances Python installées :"
pip list

# Vérifier la présence des fichiers critiques
echo "Vérification des fichiers essentiels :"
[ -f main.py ] && echo "main.py présent" || echo "ERREUR : main.py manquant"
[ -f database.py ] && echo "database.py présent" || echo "ERREUR : database.py manquant"
[ -f requirements.txt ] && echo "requirements.txt présent" || echo "ERREUR : requirements.txt manquant"

# Vérifier les variables d'environnement
echo "Variables d'environnement :"
env

# Tenter de démarrer l'application avec des informations de débogage
echo "Démarrage de l'application Uvicorn..."
exec uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000} --log-level debug
