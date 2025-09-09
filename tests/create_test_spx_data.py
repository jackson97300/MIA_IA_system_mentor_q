#!/usr/bin/env python3
"""
📊 CRÉATEUR DE DONNÉES SPX DE TEST - SESSION ASIATIQUE
=======================================================

Génère des données SPX réalistes pour tester le bot en session asiatique
quand IBKR ne fournit pas les données historiques.

Author: MIA_IA_SYSTEM
Date: Janvier 2025
"""

import asyncio
import sys
import json
from pathlib import Path
from datetime import datetime, timezone, timedelta
import random

# Ajouter le chemin du projet
sys.path.append(str(Path(__file__).parent))

from data.options_data_manager import create_options_data_manager
from core.logger import get_logger

logger = get_logger(__name__)

def create_realistic_spx_data():
    """Crée des données SPX réalistes basées sur les dernières tendances"""
    
    # 📊 Données réalistes basées sur les tendances récentes
    base_data = {
        # VIX - Niveau typique session asiatique (plus calme)
        'vix_level': random.uniform(18.5, 22.5),
        
        # Put/Call Ratio - Tendance défensive en Asie
        'put_call_ratio': random.uniform(0.75, 0.95),
        'put_call_volume_ratio': random.uniform(0.70, 0.90),
        
        # Volumes - Plus faibles en session asiatique
        'call_volume': random.randint(15000, 35000),
        'put_volume': random.randint(12000, 28000),
        'call_oi': random.randint(800000, 1200000),
        'put_oi': random.randint(600000, 1000000),
        
        # Gamma Exposure - Niveau typique
        'gamma_exposure': random.uniform(60e9, 85e9),
        
        # Dealer Position - Basé sur le gamma
        'dealer_position': random.choice(['slightly_long', 'neutral', 'slightly_short']),
        
        # Gamma Flip Level - Autour du niveau actuel ES
        'gamma_flip_level': random.uniform(5350, 5450),
        
        # Pin Levels - Niveaux clés
        'pin_levels': [5400, 5450, 5500, 5550],
        
        # Activité inhabituelle - Plus rare en Asie
        'unusual_activity': random.choice([True, False, False, False]),  # 25% de chance
        
        # Dealer Hedging - Basé sur la position
        'estimated_dealer_hedging': random.choice(['neutral', 'slight_buying', 'slight_selling'])
    }
    
    return base_data

async def create_multiple_snapshots():
    """Crée plusieurs snapshots pour simuler une journée complète"""
    
    logger.info("📊 Création de données SPX de test pour session asiatique...")
    
    try:
        # Initialiser OptionsDataManager
        options_manager = create_options_data_manager()
        
        # Créer plusieurs snapshots horaires
        timestamps = [
            datetime.now(timezone.utc) - timedelta(hours=2),  # 2h ago
            datetime.now(timezone.utc) - timedelta(hours=1),  # 1h ago
            datetime.now(timezone.utc) - timedelta(minutes=30),  # 30min ago
            datetime.now(timezone.utc) - timedelta(minutes=15),  # 15min ago
            datetime.now(timezone.utc) - timedelta(minutes=5),   # 5min ago
        ]
        
        for i, timestamp in enumerate(timestamps):
            # Créer données réalistes
            spx_data = create_realistic_spx_data()
            
            # Ajouter timestamp
            spx_data['timestamp'] = timestamp
            
            # Sauvegarder snapshot
            await options_manager.save_hourly_snapshot(spx_data)
            
            logger.info(f"   ✅ Snapshot {i+1} créé: VIX {spx_data['vix_level']:.1f}, PCR {spx_data['put_call_ratio']:.3f}")
        
        # Créer snapshot final (clôture US)
        final_data = create_realistic_spx_data()
        final_data['timestamp'] = datetime.now(timezone.utc) - timedelta(hours=6)  # Clôture US
        await options_manager.save_final_snapshot(final_data)
        
        logger.info(f"   ✅ Snapshot final créé: VIX {final_data['vix_level']:.1f}")
        
        # Vérifier les données créées
        latest_data = options_manager.get_latest_saved_data()
        if latest_data:
            logger.info(f"📊 Données de test créées avec succès!")
            logger.info(f"   📈 VIX: {latest_data.vix_level:.1f}")
            logger.info(f"   📊 Put/Call Ratio: {latest_data.put_call_ratio:.3f}")
            logger.info(f"   💰 Gamma Exposure: ${latest_data.gamma_exposure/1e9:.1f}B")
            logger.info(f"   🕐 Timestamp: {latest_data.timestamp}")
            
            return True
        else:
            logger.error("❌ Erreur: Aucune donnée créée")
            return False
            
    except Exception as e:
        logger.error(f"❌ Erreur création données de test: {e}")
        return False

def create_emergency_fallback_data():
    """Crée des données d'urgence si aucune donnée n'est disponible"""
    
    logger.info("🚨 Création données d'urgence...")
    
    emergency_data = {
        'vix_level': 20.5,  # Niveau neutre
        'put_call_ratio': 0.85,  # Légèrement défensif
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
        'estimated_dealer_hedging': 'neutral',
        'timestamp': datetime.now(timezone.utc),
        'data_source': 'emergency_test_data'
    }
    
    # Sauvegarder dans un fichier JSON
    test_file = Path("data/test_spx_emergency.json")
    test_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(test_file, 'w') as f:
        json.dump(emergency_data, f, indent=2, default=str)
    
    logger.info(f"   ✅ Données d'urgence sauvegardées: {test_file}")
    return emergency_data

if __name__ == "__main__":
    success = asyncio.run(create_multiple_snapshots())
    
    if success:
        logger.info("🎉 Données de test créées avec succès!")
        logger.info("   Le bot peut maintenant être testé en session asiatique")
    else:
        logger.warning("⚠️ Création échouée, création données d'urgence...")
        create_emergency_fallback_data()
        logger.info("🚨 Données d'urgence créées - Test possible")

