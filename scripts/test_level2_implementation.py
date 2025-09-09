#!/usr/bin/env python3
"""
Test Level 2 Implementation - MIA_IA_SYSTEM
============================================

Script de test pour vérifier l'implémentation Level 2 IBKR
et l'intégration avec Order Book Imbalance.

USAGE:
python scripts/test_level2_implementation.py
"""

import sys
import os
import asyncio
from datetime import datetime
import logging

# Ajouter le répertoire parent au path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.ibkr_connector import create_ibkr_connector
from features.order_book_imbalance import (
    get_real_order_book_data,
    convert_ibkr_level2_to_orderbook,
    create_mock_order_book,
    OrderBookImbalanceCalculator
)
from core.logger import get_logger

logger = get_logger(__name__)

async def test_level2_connection():
    """Test connexion Level 2 IBKR"""
    print("🔌 Test connexion Level 2 IBKR...")
    
    try:
        # Créer connecteur IBKR
        ibkr = create_ibkr_connector({
            'ibkr_host': '127.0.0.1',
            'ibkr_port': 7497,  # Paper trading
            'ibkr_client_id': 1
        })
        
        # Connexion
        connected = await ibkr.connect()
        if not connected:
            print("❌ Échec connexion IBKR")
            return False
        
        print("✅ IBKR connecté")
        
        # Test Level 2 data
        print("📊 Test données Level 2...")
        
        symbols = ['ES', 'NQ']
        for symbol in symbols:
            print(f"\n--- Test {symbol} ---")
            
            # Récupération Level 2
            level2_data = await ibkr.get_level2_data(symbol)
            
            print(f"Mode: {level2_data.get('mode', 'unknown')}")
            print(f"Bids: {len(level2_data.get('bids', []))} niveaux")
            print(f"Asks: {len(level2_data.get('asks', []))} niveaux")
            
            if level2_data.get('bids'):
                best_bid = level2_data['bids'][0]
                print(f"Best bid: {best_bid[0]} @ {best_bid[1]} contracts")
            
            if level2_data.get('asks'):
                best_ask = level2_data['asks'][0]
                print(f"Best ask: {best_ask[0]} @ {best_ask[1]} contracts")
            
            # Test conversion OrderBookSnapshot
            order_book = convert_ibkr_level2_to_orderbook(level2_data)
            print(f"OrderBookSnapshot créé: {len(order_book.bids)} bids, {len(order_book.asks)} asks")
        
        await ibkr.disconnect()
        return True
        
    except Exception as e:
        print(f"❌ Erreur test Level 2: {e}")
        return False

async def test_order_book_imbalance():
    """Test calcul Order Book Imbalance avec vraies données"""
    print("\n🧮 Test Order Book Imbalance...")
    
    try:
        # Créer calculateur
        calculator = OrderBookImbalanceCalculator()
        
        # Test avec mock data
        print("--- Test Mock Data ---")
        mock_book = create_mock_order_book("ES", 4500.0)
        
        from core.base_types import MarketData
        market_data = MarketData(
            timestamp=datetime.now(),
            symbol="ES",
            open=4500.0,
            high=4505.0,
            low=4495.0,
            close=4502.0,
            volume=1500
        )
        
        result = calculator.calculate_imbalance(market_data, mock_book)
        
        print(f"Signal strength: {result.signal_strength:.3f}")
        print(f"Level1 imbalance: {result.level1_imbalance:.3f}")
        print(f"Depth imbalance: {result.depth_imbalance:.3f}")
        print(f"Liquidity score: {result.liquidity_score:.3f}")
        print(f"Spread bps: {result.spread_bps:.2f}")
        
        # Test avec vraies données Level 2
        print("\n--- Test Real Level 2 Data ---")
        
        ibkr = create_ibkr_connector()
        await ibkr.connect()
        
        level2_data = await ibkr.get_level2_data("ES")
        real_order_book = convert_ibkr_level2_to_orderbook(level2_data)
        
        result_real = calculator.calculate_imbalance(market_data, real_order_book)
        
        print(f"Signal strength (real): {result_real.signal_strength:.3f}")
        print(f"Level1 imbalance (real): {result_real.level1_imbalance:.3f}")
        print(f"Depth imbalance (real): {result_real.depth_imbalance:.3f}")
        print(f"Liquidity score (real): {result_real.liquidity_score:.3f}")
        
        await ibkr.disconnect()
        return True
        
    except Exception as e:
        print(f"❌ Erreur test Order Book Imbalance: {e}")
        return False

async def test_integration():
    """Test intégration complète Level 2"""
    print("\n🔗 Test intégration complète...")
    
    try:
        from features.order_book_imbalance import get_real_order_book_data
        
        # Créer connecteur
        ibkr = create_ibkr_connector()
        await ibkr.connect()
        
        # Test récupération vraies données
        real_order_book = get_real_order_book_data(ibkr, "ES")
        
        if real_order_book:
            print("✅ Données Level 2 récupérées avec succès")
            print(f"   Bids: {len(real_order_book.bids)} niveaux")
            print(f"   Asks: {len(real_order_book.asks)} niveaux")
            
            if real_order_book.bids:
                print(f"   Best bid: {real_order_book.bids[0].price} @ {real_order_book.bids[0].size}")
            if real_order_book.asks:
                print(f"   Best ask: {real_order_book.asks[0].price} @ {real_order_book.asks[0].size}")
        else:
            print("❌ Échec récupération données Level 2")
        
        await ibkr.disconnect()
        return True
        
    except Exception as e:
        print(f"❌ Erreur test intégration: {e}")
        return False

async def main():
    """Test principal Level 2"""
    print("🚀 TEST LEVEL 2 IMPLEMENTATION - MIA_IA_SYSTEM")
    print("=" * 60)
    
    tests = [
        ("Connexion Level 2", test_level2_connection),
        ("Order Book Imbalance", test_order_book_imbalance),
        ("Intégration complète", test_integration)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}...")
        try:
            result = await test_func()
            results.append((test_name, result))
            print(f"{'✅ SUCCÈS' if result else '❌ ÉCHEC'}")
        except Exception as e:
            print(f"❌ ERREUR: {e}")
            results.append((test_name, False))
    
    # Résumé
    print("\n" + "=" * 60)
    print("📊 RÉSUMÉ DES TESTS")
    print("=" * 60)
    
    success_count = sum(1 for _, result in results if result)
    total_count = len(results)
    
    for test_name, result in results:
        status = "✅ SUCCÈS" if result else "❌ ÉCHEC"
        print(f"{test_name}: {status}")
    
    print(f"\nRésultat global: {success_count}/{total_count} tests réussis")
    
    if success_count == total_count:
        print("🎉 TOUS LES TESTS RÉUSSIS - Level 2 prêt pour production!")
    else:
        print("⚠️ Certains tests ont échoué - Vérifier configuration IBKR")
    
    return success_count == total_count

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1) 