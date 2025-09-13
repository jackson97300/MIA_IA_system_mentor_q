#!/usr/bin/env python3
"""
🎯 AJUSTEMENT SEUILS PAR SESSION - MIA_IA_SYSTEM
===============================================

Ajuste automatiquement les seuils OrderFlow selon la session
pour optimiser la détection de signaux.

Author: MIA_IA_SYSTEM
Date: Janvier 2025
"""

import sys
from pathlib import Path

# Ajouter le chemin du projet
sys.path.append(str(Path(__file__).parent))

from core.session_manager import create_session_manager
from core.logger import get_logger

logger = get_logger(__name__)

def get_session_thresholds():
    """Retourne les seuils optimisés selon la session actuelle"""
    
    session_manager = create_session_manager()
    current_session = session_manager.get_current_session()
    
    logger.info(f"🎯 Ajustement seuils pour session: {current_session.value}")
    
    if current_session.value == "asia_session":
        # 🆕 SESSION ASIATIQUE - SEUILS ADAPTÉS (liquidité faible)
        thresholds = {
            "min_confidence": 0.150,    # 0.200 → 0.150
            "min_footprint": 0.075,     # 0.100 → 0.075
            "volume_threshold": 15,     # 20 → 15
            "delta_threshold": 0.10,    # 0.15 → 0.10
            "session_multiplier": 0.6,  # Position réduite
            "risk_multiplier": 1.5,     # Risque augmenté
            "confidence_threshold": 0.8  # Seuil confiance plus strict
        }
        logger.info("   📊 Seuils adaptés pour session asiatique (liquidité faible)")
        
    elif current_session.value == "london_session":
        # 🆕 SESSION LONDRES - SEUILS INTERMÉDIAIRES
        thresholds = {
            "min_confidence": 0.175,    # Intermédiaire
            "min_footprint": 0.085,     # Intermédiaire
            "volume_threshold": 17,     # Intermédiaire
            "delta_threshold": 0.12,    # Intermédiaire
            "session_multiplier": 0.8,  # Position modérée
            "risk_multiplier": 1.2,     # Risque modéré
            "confidence_threshold": 0.75 # Seuil confiance modéré
        }
        logger.info("   📊 Seuils adaptés pour session Londres (liquidité modérée)")
        
    else:
        # 🆕 SESSION US - SEUILS STANDARD (liquidité forte)
        thresholds = {
            "min_confidence": 0.200,    # Standard
            "min_footprint": 0.100,     # Standard
            "volume_threshold": 20,     # Standard
            "delta_threshold": 0.15,    # Standard
            "session_multiplier": 1.0,  # Position normale
            "risk_multiplier": 1.0,     # Risque normal
            "confidence_threshold": 0.7  # Seuil confiance normal
        }
        logger.info("   📊 Seuils standard pour session US (liquidité forte)")
    
    # Afficher les seuils
    logger.info("🎯 SEUILS OPTIMISÉS:")
    logger.info(f"   📊 Min Confidence: {thresholds['min_confidence']:.3f}")
    logger.info(f"   📈 Min Footprint: {thresholds['min_footprint']:.3f}")
    logger.info(f"   💰 Volume Threshold: {thresholds['volume_threshold']}")
    logger.info(f"   📊 Delta Threshold: {thresholds['delta_threshold']:.2f}")
    logger.info(f"   📦 Position Multiplier: {thresholds['session_multiplier']}x")
    logger.info(f"   ⚠️ Risk Multiplier: {thresholds['risk_multiplier']}x")
    logger.info(f"   🎯 Confidence Threshold: {thresholds['confidence_threshold']}")
    
    return thresholds

def apply_thresholds_to_system():
    """Applique les seuils au système en cours d'exécution"""
    
    logger.info("🔧 Application des seuils optimisés...")
    
    try:
        # Récupérer les seuils selon la session
        thresholds = get_session_thresholds()
        
        # 🆕 NOUVEAU: Créer un fichier de configuration temporaire
        config_file = Path("config/session_thresholds.json")
        config_file.parent.mkdir(parents=True, exist_ok=True)
        
        import json
        with open(config_file, 'w') as f:
            json.dump(thresholds, f, indent=2)
        
        logger.info(f"   ✅ Configuration sauvegardée: {config_file}")
        
        # Instructions pour l'utilisateur
        logger.info("📋 INSTRUCTIONS:")
        logger.info("   1. Arrêtez le système (Ctrl+C)")
        logger.info("   2. Relancez avec: python launch_direct_with_data.py")
        logger.info("   3. Les nouveaux seuils seront appliqués automatiquement")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erreur application seuils: {e}")
        return False

def test_thresholds():
    """Test des seuils avec données simulées"""
    
    logger.info("🧪 Test des seuils optimisés...")
    
    thresholds = get_session_thresholds()
    
    # Données de test (similaires aux données actuelles)
    test_data = {
        "volume": 25.0,
        "delta": -1.25,
        "bid_volume": 10.0,
        "ask_volume": 15.0
    }
    
    # Vérifier si les données passent les seuils
    volume_ok = test_data["volume"] >= thresholds["volume_threshold"]
    delta_ok = abs(test_data["delta"]) >= thresholds["delta_threshold"]
    
    logger.info("📊 RÉSULTATS TEST:")
    logger.info(f"   📈 Volume {test_data['volume']} >= {thresholds['volume_threshold']}: {'✅' if volume_ok else '❌'}")
    logger.info(f"   📊 Delta {abs(test_data['delta'])} >= {thresholds['delta_threshold']}: {'✅' if delta_ok else '❌'}")
    
    if volume_ok and delta_ok:
        logger.info("🎉 Les données de test passent les nouveaux seuils!")
        logger.info("   Le système devrait maintenant générer des signaux")
    else:
        logger.warning("⚠️ Les données ne passent toujours pas les seuils")
        logger.info("   Considérez des seuils encore plus bas pour la session asiatique")

if __name__ == "__main__":
    logger.info("🎯 DÉMARRAGE AJUSTEMENT SEUILS PAR SESSION")
    
    # 1. Afficher les seuils actuels
    thresholds = get_session_thresholds()
    
    # 2. Tester avec données simulées
    test_thresholds()
    
    # 3. Appliquer les seuils
    success = apply_thresholds_to_system()
    
    if success:
        logger.info("🎉 AJUSTEMENT RÉUSSI!")
        logger.info("   Relancez le système pour appliquer les nouveaux seuils")
    else:
        logger.error("❌ ÉCHEC DE L'AJUSTEMENT")

