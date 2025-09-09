#!/usr/bin/env python3
"""
🚀 LANCEMENT RAPIDE SESSION ASIATIQUE - MIA_IA_SYSTEM
=====================================================

Lancement rapide du bot en mode test pour la session asiatique
avec données simulées quand IBKR ne fournit pas les données historiques.

Author: MIA_IA_SYSTEM
Date: Janvier 2025
"""

import asyncio
import sys
from pathlib import Path

# Ajouter le chemin du projet
sys.path.append(str(Path(__file__).parent))

from launch_24_7_orderflow_trading import OrderFlow24_7Launcher
from core.logger import get_logger

logger = get_logger(__name__)

async def launch_asian_session_test():
    """Lance le bot en mode test pour la session asiatique"""
    
    logger.info("🚀 LANCEMENT TEST SESSION ASIATIQUE")
    logger.info("=" * 60)
    
    try:
        # 1. Créer le lanceur en mode test
        logger.info("📊 Initialisation lanceur en mode test...")
        launcher = OrderFlow24_7Launcher(live_trading=False)
        
        # 2. Vérifier les modules Phase 3
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
        
        # 3. Vérifier session actuelle
        current_session = launcher.session_manager.get_current_session()
        session_config = launcher.session_manager.get_session_config(current_session)
        
        logger.info(f"🕐 Session détectée: {current_session.value}")
        logger.info(f"📊 Description: {session_config.description}")
        logger.info(f"🎯 Trading activé: {session_config.trading_enabled}")
        logger.info(f"📡 Source données: {session_config.data_source.value}")
        
        # 4. Créer des données de test si nécessaire
        logger.info("📊 Vérification données de test...")
        
        latest_data = launcher.options_manager.get_latest_saved_data()
        if not latest_data:
            logger.warning("⚠️ Aucune donnée sauvegardée trouvée")
            logger.info("   Création de données de test...")
            
            # Créer des données de test réalistes
            test_data = {
                'vix_level': 20.5,
                'put_call_ratio': 0.85,
                'put_call_volume_ratio': 0.80,
                'call_volume': 25000,
                'put_volume': 20000,
                'call_oi': 1000000,
                'put_oi': 800000,
                'gamma_exposure': 75e9,
                'dealer_position': 'neutral',
                'gamma_flip_level': 5400.0,
                'pin_levels': [5400, 5450, 5500],
                'unusual_activity': False,
                'estimated_dealer_hedging': 'neutral'
            }
            
            await launcher.options_manager.save_hourly_snapshot(test_data)
            logger.info("   ✅ Données de test créées")
        else:
            logger.info(f"   ✅ Données existantes trouvées: VIX {latest_data.vix_level:.1f}")
        
        # 5. Lancer le système de trading
        logger.info("🚀 Lancement système de trading...")
        
        # Initialiser le système
        if await launcher.initialize_system():
            logger.info("✅ Système initialisé avec succès")
            
            # Afficher la configuration
            launcher._display_configuration()
            
            # Lancer le trading (mode test)
            logger.info("🎯 Démarrage boucle de trading (mode test)...")
            logger.info("   ⚠️ Mode TEST - Aucun trade réel ne sera exécuté")
            logger.info("   📊 Les données de test seront utilisées")
            logger.info("   🕐 Session asiatique simulée")
            
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
        logger.error(f"❌ Erreur lancement session asiatique: {e}")
        return False

def main():
    """Fonction principale"""
    
    logger.info("🎯 MIA_IA_SYSTEM - TEST SESSION ASIATIQUE")
    logger.info("=" * 60)
    logger.info("📋 INSTRUCTIONS:")
    logger.info("   1. Ce script lance le bot en mode test")
    logger.info("   2. Utilise des données simulées pour la session asiatique")
    logger.info("   3. Aucun trade réel ne sera exécuté")
    logger.info("   4. Appuyez sur Ctrl+C pour arrêter")
    logger.info("=" * 60)
    
    # Demander confirmation
    try:
        response = input("🚀 Voulez-vous lancer le test session asiatique? (y/N): ")
        if response.lower() not in ['y', 'yes', 'oui']:
            logger.info("❌ Lancement annulé")
            return
    except KeyboardInterrupt:
        logger.info("❌ Lancement annulé")
        return
    
    # Lancer le test
    success = asyncio.run(launch_asian_session_test())
    
    if success:
        logger.info("🎉 TEST SESSION ASIATIQUE TERMINÉ AVEC SUCCÈS!")
    else:
        logger.error("❌ ÉCHEC DU TEST SESSION ASIATIQUE")

if __name__ == "__main__":
    main()

