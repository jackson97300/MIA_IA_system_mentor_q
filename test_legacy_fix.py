#!/usr/bin/env python3
"""
Test de correction de compatibilité legacy
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd()))

from performance.trade_logger import TradeLogger

def test_legacy_compatibility():
    """Test de compatibilité legacy"""
    print("=== TEST COMPATIBILITÉ LEGACY ===")
    
    # Test 1: TradeLogger basique
    print("🎯 Test 1: Création TradeLogger")
    try:
        logger = TradeLogger()
        print("✅ TradeLogger créé")
    except Exception as e:
        print(f"❌ Erreur création TradeLogger: {e}")
        return
    
    # Test 2: Données legacy minimales
    print("\n🎯 Test 2: Données legacy minimales")
    legacy_data = {
        'symbol': 'NQ',
        'action': 'ENTRY', 
        'side': 'SHORT',
        'price': 15500.0,
        'quantity': 1
    }
    
    print(f"Données legacy: {legacy_data}")
    
    # Test 3: Validation
    print("\n🎯 Test 3: Validation")
    is_valid = logger._validate_trade_data(legacy_data)
    print(f"Validation: {'✅ OK' if is_valid else '❌ ÉCHEC'}")
    
    # Test 4: Log du trade
    print("\n🎯 Test 4: Log du trade")
    try:
        trade_id = logger.log_trade(legacy_data)
        if trade_id:
            print(f"✅ Trade loggé: {trade_id}")
            print(f"📊 Status: {logger.get_status()}")
        else:
            print("❌ Échec du log")
    except Exception as e:
        print(f"❌ Erreur log_trade: {e}")
    
    # Test 5: Vérification en mémoire
    print("\n🎯 Test 5: Vérification en mémoire")
    if trade_id and trade_id in logger.active_trades:
        trade_record = logger.active_trades[trade_id]
        print(f"✅ Trade trouvé en mémoire:")
        print(f"   - Symbol: {trade_record.symbol}")
        print(f"   - Action: {trade_record.action}")
        print(f"   - Price: {trade_record.price}")
        print(f"   - Final score (défaut): {trade_record.final_score}")
        print(f"   - Signal strength (défaut): {trade_record.signal_strength}")
    else:
        print("❌ Trade non trouvé en mémoire")

if __name__ == "__main__":
    test_legacy_compatibility()

