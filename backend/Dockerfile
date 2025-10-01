# Utiliser une image Python légère
FROM python:3.10-slim

# Définir le répertoire de travail
WORKDIR /app

# Installer les dépendances système
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copier les fichiers de dépendances
COPY requirements.txt .

# Installer les dépendances Python avec des informations détaillées
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt \
    && pip list

# Copier tout le code de l'application
COPY . .

# Créer un répertoire pour les logs
RUN mkdir -p /app/logs

# Variables d'environnement de débogage
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV DEBUG=true
ENV PORT=8000

# Script de démarrage avec débogage
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Exposer le port
EXPOSE 8000

# Point d'entrée avec débogage
ENTRYPOINT ["/entrypoint.sh"]

# Métadonnées
LABEL maintainer="hamza@example.com" \
      version="1.0" \
      description="Library Management System"
