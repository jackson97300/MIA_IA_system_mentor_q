#!/usr/bin/env python3
"""
🧮 TEST DEALER POSITION - MIA_IA_SYSTEM
Test du calcul de la position dealer basé sur les données SPX
"""

import sys
import json
from pathlib import Path
from datetime import datetime

# Ajouter le chemin du projet
sys.path.append(str(Path(__file__).parent))

from core.logger import get_logger
from features.spx_options_retriever import SPXOptionsRetriever

logger = get_logger(__name__)

def test_dealer_position_calculation():
    """Test du calcul de la position dealer"""
    
    # Charger les données SPX sauvegardées
    snapshot_path = Path("data/options_snapshots/spx_snapshot_2025-08-21.json")
    if not snapshot_path.exists():
        logger.error("❌ Fichier snapshot SPX non trouvé")
        return
    
    with open(snapshot_path, 'r') as f:
        snapshot_data = json.load(f)
    
    logger.info("🧮 TEST CALCUL DEALER POSITION")
    logger.info("=" * 50)
    
    # Extraire les données
    put_call_ratio = snapshot_data.get('options_flow', {}).get('put_call_ratio', 1.15)
    vix_level = snapshot_data.get('market_data', {}).get('vix_level', 16.07)
    dealer_position = snapshot_data.get('levels', {}).get('dealer_position', 'short')
    
    logger.info(f"📊 Données SPX:")
    logger.info(f"  📈 Put/Call Ratio: {put_call_ratio}")
    logger.info(f"  📊 VIX Level: {vix_level}")
    logger.info(f"  🏦 Dealer Position (sauvegardée): {dealer_position}")
    
    # Test avec différentes valeurs PCR
    test_cases = [
        {'put_call_ratio': 0.5, 'call_volume': 100000, 'put_volume': 50000, 'expected': 'long'},
        {'put_call_ratio': 0.8, 'call_volume': 80000, 'put_volume': 64000, 'expected': 'long'},
        {'put_call_ratio': 1.0, 'call_volume': 50000, 'put_volume': 50000, 'expected': 'neutral'},
        {'put_call_ratio': 1.2, 'call_volume': 50000, 'put_volume': 60000, 'expected': 'short'},
        {'put_call_ratio': 1.5, 'call_volume': 40000, 'put_volume': 60000, 'expected': 'short'},
        {'put_call_ratio': 2.0, 'call_volume': 30000, 'put_volume': 60000, 'expected': 'short'},
    ]
    
    spx_retriever = SPXOptionsRetriever()
    
    logger.info("\n🧮 TESTS CALCUL DEALER POSITION:")
    logger.info("-" * 50)
    
    for i, test_case in enumerate(test_cases, 1):
        volume_data = {
            'put_call_ratio': test_case['put_call_ratio'],
            'call_volume': test_case['call_volume'],
            'put_volume': test_case['put_volume']
        }
        
        oi_data = {}  # Données OI simulées
        
        # Calculer la position dealer
        calculated_position = spx_retriever._infer_dealer_position(volume_data, oi_data)
        expected_position = test_case['expected']
        
        status = "✅" if calculated_position == expected_position else "❌"
        
        logger.info(f"Test {i}: PCR={test_case['put_call_ratio']:.1f}")
        logger.info(f"  📊 Call Volume: {test_case['call_volume']:,}")
        logger.info(f"  📊 Put Volume: {test_case['put_volume']:,}")
        logger.info(f"  🏦 Calculé: {calculated_position}")
        logger.info(f"  🎯 Attendu: {expected_position}")
        logger.info(f"  {status} {'PASS' if calculated_position == expected_position else 'FAIL'}")
        logger.info("")
    
    # Test avec les vraies données SPX
    logger.info("🧮 TEST AVEC DONNÉES SPX RÉELLES:")
    logger.info("-" * 50)
    
    real_volume_data = {
        'put_call_ratio': put_call_ratio,
        'call_volume': 50000,  # Estimation
        'put_volume': int(50000 * put_call_ratio)  # Calculé
    }
    
    real_position = spx_retriever._infer_dealer_position(real_volume_data, {})
    
    logger.info(f"📊 Données réelles:")
    logger.info(f"  📈 Put/Call Ratio: {put_call_ratio}")
    logger.info(f"  📊 Call Volume: {real_volume_data['call_volume']:,}")
    logger.info(f"  📊 Put Volume: {real_volume_data['put_volume']:,}")
    logger.info(f"  🏦 Position calculée: {real_position}")
    logger.info(f"  🏦 Position sauvegardée: {dealer_position}")
    
    if real_position == dealer_position:
        logger.info("✅ Position dealer cohérente!")
    else:
        logger.warning(f"⚠️ Incohérence: calculé={real_position}, sauvegardé={dealer_position}")

if __name__ == "__main__":
    test_dealer_position_calculation()


