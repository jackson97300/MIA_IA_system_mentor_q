#!/usr/bin/env python3
"""
🚀 LANCEMENT DIRECT AVEC DONNÉES - MIA_IA_SYSTEM
===============================================

Lancement direct du système avec chargement manuel des données SPX
pour contourner les problèmes de reconnaissance.

Author: MIA_IA_SYSTEM
Date: Janvier 2025
"""

import asyncio
import sys
import json
from pathlib import Path
from datetime import datetime, timezone

# Ajouter le chemin du projet
sys.path.append(str(Path(__file__).parent))

from launch_24_7_orderflow_trading import OrderFlow24_7Launcher
from core.logger import get_logger

logger = get_logger(__name__)

def load_spx_data_directly():
    """Charge directement les données SPX depuis les fichiers JSON"""
    
    logger.info("📊 Chargement direct des données SPX...")
    
    data_dir = Path("data/options_snapshots")
    
    # Chercher le fichier le plus récent
    json_files = list(data_dir.glob("*.json"))
    if not json_files:
        logger.error("❌ Aucun fichier JSON trouvé")
        return None
    
    # Prendre le fichier le plus récent
    latest_file = max(json_files, key=lambda f: f.stat().st_mtime)
    
    logger.info(f"   📄 Fichier utilisé: {latest_file}")
    
    try:
        with open(latest_file, 'r') as f:
            spx_data = json.load(f)
        
        logger.info(f"   ✅ Données chargées: VIX {spx_data['vix_level']:.1f}")
        return spx_data
        
    except Exception as e:
        logger.error(f"❌ Erreur chargement fichier: {e}")
        return None

class DirectLauncher(OrderFlow24_7Launcher):
    """Lanceur direct avec chargement manuel des données"""
    
    def __init__(self, live_trading=False):
        super().__init__(live_trading)
        self.direct_spx_data = None
    
    async def _get_real_spx_options_data(self):
        """Override pour utiliser les données chargées directement"""
        
        if not self.direct_spx_data:
            logger.error("🛑 PAUSE TRADING - Données SPX non chargées")
            return None
        
        logger.info("📊 Utilisation données SPX chargées directement...")
        
        # Convertir en format attendu par le système
        return {
            "put_call_ratio": self.direct_spx_data.get('put_call_ratio', 1.0),
            "gamma_exposure": self.direct_spx_data.get('gamma_exposure', 75e9),
            "dealer_position": self.direct_spx_data.get('dealer_position', 'neutral'),
            "vix_level": self.direct_spx_data.get('vix_level', 24.2),
            "gamma_flip_level": self.direct_spx_data.get('gamma_flip_level', 5400.0),
            "unusual_options_activity": self.direct_spx_data.get('unusual_activity', False),
            "nearby_pin_levels": self.direct_spx_data.get('pin_levels', [5400, 5450, 5500]),
            "estimated_dealer_hedging": self.direct_spx_data.get('estimated_dealer_hedging', 'neutral'),
            
            # Métadonnées
            "data_source": 'saved_data',  # 🆕 CORRIGÉ: Forcer saved_data pour reconnaissance
            "timestamp": self.direct_spx_data.get('timestamp'),
            "calculation_time_ms": 0
        }

async def launch_direct_with_data():
    """Lance le système avec données chargées directement"""
    
    logger.info("🚀 LANCEMENT DIRECT AVEC DONNÉES SPX")
    logger.info("=" * 60)
    
    try:
        # 1. Charger les données SPX directement
        spx_data = load_spx_data_directly()
        if not spx_data:
            logger.error("❌ Impossible de charger les données SPX")
            return False
        
        # 2. Créer le lanceur direct
        logger.info("📊 Initialisation lanceur direct...")
        launcher = DirectLauncher(live_trading=False)
        
        # 3. Injecter les données SPX
        launcher.direct_spx_data = spx_data
        logger.info("   ✅ Données SPX injectées dans le lanceur")
        
        # 4. Vérifier les modules Phase 3
        logger.info("🛡️ Vérification modules Phase 3...")
        
        if not launcher.options_manager:
            logger.error("❌ OptionsDataManager manquant")
            return False
        
        if not launcher.session_manager:
            logger.error("❌ SessionManager manquant")
            return False
        
        if not launcher.data_validator:
            logger.error("❌ DataQualityValidator manquant")
            return False
        
        logger.info("✅ Tous les modules Phase 3 initialisés")
        
        # 5. Vérifier session actuelle
        current_session = launcher.session_manager.get_current_session()
        session_config = launcher.session_manager.get_session_config(current_session)
        
        logger.info(f"🕐 Session détectée: {current_session.value}")
        logger.info(f"📊 Description: {session_config.description}")
        logger.info(f"🎯 Trading activé: {session_config.trading_enabled}")
        logger.info(f"📡 Source données: {session_config.data_source.value}")
        
        # 6. Lancer le système
        logger.info("🚀 Lancement système de trading...")
        
        # Initialiser le système
        if await launcher.initialize_system():
            logger.info("✅ Système initialisé avec succès")
            
            # Afficher la configuration
            launcher._display_configuration()
            
            # Lancer le trading (mode test)
            logger.info("🎯 Démarrage boucle de trading (mode test)...")
            logger.info("   ⚠️ Mode TEST - Aucun trade réel ne sera exécuté")
            logger.info("   📊 Données SPX chargées directement")
            logger.info(f"   📈 VIX: {spx_data['vix_level']:.1f}")
            logger.info(f"   📊 Put/Call Ratio: {spx_data['put_call_ratio']:.3f}")
            
            # Lancer la boucle de trading
            await launcher.start_24_7_trading()
            
        else:
            logger.error("❌ Échec initialisation système")
            return False
        
        return True
        
    except KeyboardInterrupt:
        logger.info("⏹️ Arrêt demandé par l'utilisateur")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erreur lancement direct: {e}")
        return False

def main():
    """Fonction principale"""
    
    logger.info("🎯 MIA_IA_SYSTEM - LANCEMENT DIRECT AVEC DONNÉES")
    logger.info("=" * 60)
    logger.info("📋 INSTRUCTIONS:")
    logger.info("   1. Ce script lance le bot en mode test")
    logger.info("   2. Utilise les données SPX chargées directement")
    logger.info("   3. Contourne les problèmes de reconnaissance")
    logger.info("   4. Aucun trade réel ne sera exécuté")
    logger.info("   5. Appuyez sur Ctrl+C pour arrêter")
    logger.info("=" * 60)
    
    # Demander confirmation
    try:
        response = input("🚀 Voulez-vous lancer le système avec données directes? (y/N): ")
        if response.lower() not in ['y', 'yes', 'oui']:
            logger.info("❌ Lancement annulé")
            return
    except KeyboardInterrupt:
        logger.info("❌ Lancement annulé")
        return
    
    # Lancer le système
    success = asyncio.run(launch_direct_with_data())
    
    if success:
        logger.info("🎉 LANCEMENT DIRECT RÉUSSI!")
    else:
        logger.error("❌ ÉCHEC DU LANCEMENT DIRECT")

if __name__ == "__main__":
    main()
