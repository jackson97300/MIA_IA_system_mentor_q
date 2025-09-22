# 🚀 MIA IA SYSTEM - Dockerfile
# Containerisation du système de trading automatisé MIA
# Version: Production Ready v1.0

FROM python:3.11-slim

# Métadonnées
LABEL maintainer="MIA_IA_SYSTEM"
LABEL version="1.0"
LABEL description="Système de trading automatisé MIA avec ML et analyse de marché"

# Variables d'environnement
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV MIA_ENV=production
ENV MIA_LOG_LEVEL=INFO

# Répertoire de travail
WORKDIR /app

# Installation des dépendances système
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    curl \
    wget \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copie des fichiers de dépendances
COPY requirements.txt .

# Installation des dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Copie du code source
COPY . .

# Création des répertoires nécessaires
RUN mkdir -p \
    /app/logs \
    /app/data \
    /app/DATA_SIERRA_CHART \
    /app/results \
    /app/config_files \
    /app/temp

# Permissions
RUN chmod +x /app/launch_hybrid_system.py

# Ports exposés (si nécessaire pour monitoring)
EXPOSE 8080 8384

# Point d'entrée
CMD ["python", "launch_hybrid_system.py"]
