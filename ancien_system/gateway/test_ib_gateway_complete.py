#!/usr/bin/env python3
"""
Test IB Gateway Complete - MIA_IA_SYSTEM
========================================

Script de test complet pour IB Gateway + Level 2 + OPRA
avec intégration Order Book Imbalance.

USAGE:
python scripts/test_ib_gateway_complete.py
"""

import sys
import os
import asyncio
from datetime import datetime
import logging

# Ajouter le répertoire parent au path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.ibkr_connector import create_ibkr_connector
from features.order_book_imbalance import OrderBookImbalanceCalculator
from core.logger import get_logger

logger = get_logger(__name__)

async def test_ib_gateway_complete():
    """Test complet IB Gateway + Level 2 + Options"""
    
    print("🚀 TEST COMPLET IB GATEWAY + LEVEL 2 + OPRA")
    print("=" * 50)
    
    connector = None
    try:
        # 1. Test Connexion
        print("\n1️⃣ Test Connexion IB Gateway...")
        connector = create_ibkr_connector()
        
        if await connector.connect():
            print("✅ Connexion IB Gateway OK")
        else:
            print("❌ Erreur connexion")
            return
        
        # 2. Test Level 2
        print("\n2️⃣ Test Level 2 Order Book...")
        try:
            level2_data = await connector.get_level2_data("ES")
            
            if level2_data:
                print(f"✅ Level 2 OK : {len(level2_data['bids'])} bids, {len(level2_data['asks'])} asks")
                print(f"   Bids: {level2_data['bids'][:3]}")
                print(f"   Asks: {level2_data['asks'][:3]}")
            else:
                print("❌ Erreur Level 2")
        except Exception as e:
            print(f"❌ Erreur Level 2: {e}")
        
        # 3. Test Options
        print("\n3️⃣ Test Options Data...")
        try:
            options_data = await connector.get_options_data("SPX")
            
            if options_data:
                print(f"✅ Options OK : {len(options_data)} contrats")
            else:
                print("❌ Erreur Options")
        except Exception as e:
            print(f"❌ Erreur Options: {e}")
        
        # 4. Test Order Book Imbalance
        print("\n4️⃣ Test Order Book Imbalance...")
        try:
            calculator = OrderBookImbalanceCalculator()
            
            if level2_data:
                imbalance = calculator.calculate_imbalance(level2_data)
                print(f"✅ Imbalance calculé : {imbalance:.4f}")
            else:
                print("❌ Pas de données Level 2 pour imbalance")
        except Exception as e:
            print(f"❌ Erreur Imbalance: {e}")
        
        # 5. Test Performance
        print("\n5️⃣ Test Performance...")
        try:
            start_time = datetime.now()
            
            for i in range(5):  # Réduit à 5 pour éviter les timeouts
                await connector.get_level2_data("ES")
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            print(f"✅ 5 requêtes Level 2 en {duration:.2f}s")
            print(f"   Latence moyenne : {duration/5:.3f}s par requête")
        except Exception as e:
            print(f"❌ Erreur Performance: {e}")
        
        # 6. Test Options Greeks
        print("\n6️⃣ Test Options Greeks...")
        try:
            if options_data:
                for option in options_data[:3]:  # Test 3 premiers contrats
                    print(f"   {option['symbol']}: Delta={option.get('delta', 'N/A')}, Gamma={option.get('gamma', 'N/A')}")
            else:
                print("❌ Pas de données options pour Greeks")
        except Exception as e:
            print(f"❌ Erreur Greeks: {e}")
        
        # 7. Test Imbalance Analysis
        print("\n7️⃣ Test Imbalance Analysis...")
        try:
            if level2_data:
                # Analyse détaillée
                bids = level2_data['bids']
                asks = level2_data['asks']
                
                if bids and asks:
                    bid_volume = sum(bid['size'] for bid in bids[:5])
                    ask_volume = sum(ask['size'] for ask in asks[:5])
                    
                    print(f"   Volume Bid (5 niveaux): {bid_volume}")
                    print(f"   Volume Ask (5 niveaux): {ask_volume}")
                    print(f"   Ratio Bid/Ask: {bid_volume/ask_volume:.3f}" if ask_volume > 0 else "   Ratio Bid/Ask: N/A")
        except Exception as e:
            print(f"❌ Erreur Analysis: {e}")
        
        # 8. Test Account Info
        print("\n8️⃣ Test Account Info...")
        try:
            account_info = await connector.get_account_info()
            
            if account_info:
                print(f"✅ Account Info OK")
                print(f"   Balance: ${account_info.get('balance', 'N/A')}")
                print(f"   Buying Power: ${account_info.get('buying_power', 'N/A')}")
            else:
                print("❌ Erreur Account Info")
        except Exception as e:
            print(f"❌ Erreur Account Info: {e}")
        
        # 9. Test Market Data
        print("\n9️⃣ Test Market Data...")
        try:
            market_data = await connector.get_market_data("ES")
            
            if market_data:
                print(f"✅ Market Data OK")
                print(f"   Last Price: {market_data.get('last_price', 'N/A')}")
                print(f"   Bid: {market_data.get('bid', 'N/A')}")
                print(f"   Ask: {market_data.get('ask', 'N/A')}")
            else:
                print("❌ Erreur Market Data")
        except Exception as e:
            print(f"❌ Erreur Market Data: {e}")
        
        # 10. Résumé final
        print("\n" + "=" * 50)
        print("📊 RÉSUMÉ DU TEST")
        print("=" * 50)
        
        try:
            status = connector.get_connection_status()
            print(f"Status: {status.get('status', 'Unknown')}")
            print(f"Connected: {status.get('connected', False)}")
            print(f"Errors: {status.get('errors', 0)}")
        except Exception as e:
            print(f"❌ Erreur Status: {e}")
        
        print("\n✅ Test complet terminé !")
        
    except Exception as e:
        print(f"❌ Erreur générale dans le test: {e}")
    finally:
        # Déconnexion propre
        if connector:
            try:
                await connector.disconnect()
            except Exception as e:
                print(f"⚠️ Erreur lors de la déconnexion: {e}")

async def test_level2_only():
    """Test rapide Level 2 uniquement"""
    print("🔍 TEST RAPIDE LEVEL 2")
    print("=" * 30)
    
    try:
        connector = create_ibkr_connector()
        
        if await connector.connect():
            print("✅ Connexion établie")
            level2_data = await connector.get_level2_data("ES")
            
            if level2_data:
                print("✅ Level 2 fonctionne")
                print(f"   Bids: {level2_data['bids'][:2]}")
                print(f"   Asks: {level2_data['asks'][:2]}")
            else:
                print("❌ Level 2 ne fonctionne pas")
        else:
            print("❌ Échec de connexion")
        
        await connector.disconnect()
        
    except Exception as e:
        print(f"❌ Erreur dans test Level 2: {e}")

async def test_options_only():
    """Test rapide Options uniquement"""
    print("🔍 TEST RAPIDE OPTIONS")
    print("=" * 30)
    
    try:
        connector = create_ibkr_connector()
        
        if await connector.connect():
            print("✅ Connexion établie")
            options_data = await connector.get_options_data("SPX")
            
            if options_data:
                print("✅ Options fonctionnent")
                print(f"   Contrats disponibles: {len(options_data)}")
            else:
                print("❌ Options ne fonctionnent pas")
        else:
            print("❌ Échec de connexion")
        
        await connector.disconnect()
        
    except Exception as e:
        print(f"❌ Erreur dans test Options: {e}")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Test IB Gateway")
    parser.add_argument("--mode", choices=["complete", "level2", "options"], 
                       default="complete", help="Mode de test")
    
    args = parser.parse_args()
    
    try:
        if args.mode == "complete":
            asyncio.run(test_ib_gateway_complete())
        elif args.mode == "level2":
            asyncio.run(test_level2_only())
        elif args.mode == "options":
            asyncio.run(test_options_only())
    except KeyboardInterrupt:
        print("\n⏹️ Test interrompu par l'utilisateur")
    except Exception as e:
        print(f"\n❌ Erreur générale: {e}") 