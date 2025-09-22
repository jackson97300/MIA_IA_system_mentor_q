#!/bin/bash
# 🚀 MIA IA SYSTEM - Script de Déploiement
# Script automatisé pour déployer le système MIA
# Version: Production Ready v1.0

set -e  # Arrêter en cas d'erreur

# Couleurs pour les logs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Fonction de logging
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Vérification des prérequis
check_prerequisites() {
    log "🔍 Vérification des prérequis..."
    
    # Vérifier Docker
    if ! command -v docker &> /dev/null; then
        error "Docker n'est pas installé. Veuillez l'installer d'abord."
        exit 1
    fi
    
    # Vérifier Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        error "Docker Compose n'est pas installé. Veuillez l'installer d'abord."
        exit 1
    fi
    
    # Vérifier Python
    if ! command -v python3 &> /dev/null; then
        error "Python 3 n'est pas installé."
        exit 1
    fi
    
    success "Tous les prérequis sont satisfaits"
}

# Création des répertoires nécessaires
create_directories() {
    log "📁 Création des répertoires nécessaires..."
    
    mkdir -p {data,logs,DATA_SIERRA_CHART,results,config_files,temp,syncthing/{config,data},monitoring,MIA_SHARED}
    
    success "Répertoires créés"
}

# Configuration des permissions
setup_permissions() {
    log "🔐 Configuration des permissions..."
    
    # Permissions pour les répertoires
    chmod 755 data logs results config_files temp
    chmod 700 syncthing/config
    
    success "Permissions configurées"
}

# Construction de l'image Docker
build_docker_image() {
    log "🐳 Construction de l'image Docker..."
    
    docker-compose build --no-cache
    
    success "Image Docker construite"
}

# Démarrage des services
start_services() {
    log "🚀 Démarrage des services..."
    
    # Arrêter les services existants
    docker-compose down 2>/dev/null || true
    
    # Démarrer les services
    docker-compose up -d
    
    success "Services démarrés"
}

# Vérification du statut
check_status() {
    log "📊 Vérification du statut des services..."
    
    # Attendre que les services soient prêts
    sleep 10
    
    # Vérifier MIA Bot
    if docker-compose ps mia-bot | grep -q "Up"; then
        success "MIA Bot est en cours d'exécution"
    else
        error "MIA Bot n'est pas en cours d'exécution"
        docker-compose logs mia-bot
    fi
    
    # Vérifier Syncthing
    if docker-compose ps syncthing | grep -q "Up"; then
        success "Syncthing est en cours d'exécution"
        log "Interface Syncthing disponible sur: http://localhost:8384"
    else
        warning "Syncthing n'est pas en cours d'exécution"
    fi
}

# Configuration initiale
initial_setup() {
    log "⚙️ Configuration initiale..."
    
    # Copier les fichiers de configuration par défaut si nécessaire
    if [ ! -f "config_files/automation_params.json" ]; then
        warning "Fichier de configuration manquant. Veuillez le créer."
    fi
    
    # Créer le fichier .env si nécessaire
    if [ ! -f ".env" ]; then
        cat > .env << EOF
# Configuration MIA IA System
MIA_ENV=production
MIA_LOG_LEVEL=INFO
TZ=Europe/Paris
EOF
        success "Fichier .env créé"
    fi
}

# Fonction principale
main() {
    echo "🚀 === DÉPLOIEMENT MIA IA SYSTEM ==="
    echo "Système de trading automatisé avec ML"
    echo "======================================"
    
    check_prerequisites
    create_directories
    setup_permissions
    initial_setup
    build_docker_image
    start_services
    check_status
    
    echo ""
    success "🎉 Déploiement terminé avec succès!"
    echo ""
    echo "📋 Services disponibles:"
    echo "  - MIA Bot: http://localhost:8080 (si configuré)"
    echo "  - Syncthing: http://localhost:8384"
    echo "  - Monitoring: http://localhost:9090 (si activé)"
    echo ""
    echo "📁 Dossier partagé: ./MIA_SHARED/"
    echo ""
    echo "🔧 Commandes utiles:"
    echo "  - Voir les logs: docker-compose logs -f"
    echo "  - Arrêter: docker-compose down"
    echo "  - Redémarrer: docker-compose restart"
    echo "  - Statut: docker-compose ps"
}

# Gestion des arguments
case "${1:-}" in
    "start")
        start_services
        check_status
        ;;
    "stop")
        log "🛑 Arrêt des services..."
        docker-compose down
        success "Services arrêtés"
        ;;
    "restart")
        log "🔄 Redémarrage des services..."
        docker-compose restart
        check_status
        ;;
    "logs")
        docker-compose logs -f
        ;;
    "status")
        docker-compose ps
        ;;
    "clean")
        log "🧹 Nettoyage..."
        docker-compose down -v
        docker system prune -f
        success "Nettoyage terminé"
        ;;
    *)
        main
        ;;
esac
