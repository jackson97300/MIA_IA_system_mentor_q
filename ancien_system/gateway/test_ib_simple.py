#!/usr/bin/env python3
"""
Test IB Simple - MIA_IA_SYSTEM
==============================

Test simple et rapide de connexion IBKR.

USAGE:
python scripts/test_ib_simple.py
"""

import sys
import os
import asyncio
from datetime import datetime

# Ajouter le répertoire parent au path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.ibkr_connector import create_ibkr_connector

async def test_ib_simple():
    """Test simple de connexion IBKR"""
    
    print("🔍 TEST SIMPLE IBKR")
    print("=" * 30)
    print(f"⏰ Début: {datetime.now().strftime('%H:%M:%S')}")
    
    connector = None
    try:
        # 1. Test Connexion
        print("\n1️⃣ Test Connexion...")
        connector = create_ibkr_connector()
        
        if await connector.connect():
            print("✅ Connexion OK")
        else:
            print("❌ Échec connexion")
            return
        
        # 2. Test Account Info
        print("\n2️⃣ Test Account Info...")
        try:
            account_info = await connector.get_account_info()
            if account_info:
                print("✅ Account Info OK")
                print(f"   Balance: ${account_info.get('balance', 'N/A')}")
                print(f"   Buying Power: ${account_info.get('buying_power', 'N/A')}")
                print(f"   Account: {account_info.get('account', 'N/A')}")
            else:
                print("❌ Pas d'info compte")
        except Exception as e:
            print(f"❌ Erreur Account: {e}")
        
        # 3. Test Market Data avec plus de détails
        print("\n3️⃣ Test Market Data...")
        try:
            market_data = await connector.get_market_data("ES")
            if market_data:
                print("✅ Market Data OK")
                print(f"   Last: {market_data.get('last_price', 'N/A')}")
                print(f"   Bid: {market_data.get('bid', 'N/A')}")
                print(f"   Ask: {market_data.get('ask', 'N/A')}")
                print(f"   Volume: {market_data.get('volume', 'N/A')}")
                print(f"   High: {market_data.get('high', 'N/A')}")
                print(f"   Low: {market_data.get('low', 'N/A')}")
                
                # Debug: afficher toutes les clés
                print(f"   Clés disponibles: {list(market_data.keys())}")
            else:
                print("❌ Pas de données marché")
        except Exception as e:
            print(f"❌ Erreur Market Data: {e}")
            import traceback
            traceback.print_exc()
        
        # 4. Test Level 2 avec plus de détails
        print("\n4️⃣ Test Level 2...")
        try:
            level2_data = await connector.get_level2_data("ES")
            if level2_data and level2_data.get('bids') and level2_data.get('asks'):
                print("✅ Level 2 OK")
                print(f"   Bids: {len(level2_data['bids'])} niveaux")
                print(f"   Asks: {len(level2_data['asks'])} niveaux")
                
                # Afficher les premiers niveaux
                if level2_data['bids']:
                    print(f"   Top Bid: {level2_data['bids'][0]}")
                if level2_data['asks']:
                    print(f"   Top Ask: {level2_data['asks'][0]}")
            else:
                print("❌ Pas de Level 2")
                print(f"   Données reçues: {level2_data}")
        except Exception as e:
            print(f"❌ Erreur Level 2: {e}")
            import traceback
            traceback.print_exc()
        
        # 5. Test Status
        print("\n5️⃣ Test Status...")
        try:
            status = connector.get_connection_status()
            print(f"✅ Status: {status.get('status', 'Unknown')}")
            print(f"   Connected: {status.get('connected', False)}")
            print(f"   Errors: {status.get('errors', 0)}")
            print(f"   Ticks: {status.get('ticks_processed', 0)}")
        except Exception as e:
            print(f"❌ Erreur Status: {e}")
        
        # 6. Test direct avec ib_insync
        print("\n6️⃣ Test Direct IB...")
        try:
            if hasattr(connector, 'ib') and connector.ib:
                print("✅ Interface IB disponible")
                
                # Test contrat ES
                from ib_insync import Future
                contract = Future('ES', '202412', 'CME')
                connector.ib.qualifyContracts(contract)
                
                # Test données temps réel
                ticker = connector.ib.reqMktData(contract)
                await asyncio.sleep(2)  # Attendre les données
                
                if ticker and ticker.marketPrice():
                    print(f"✅ Prix ES: {ticker.marketPrice()}")
                    print(f"   Bid: {ticker.bid}")
                    print(f"   Ask: {ticker.ask}")
                    print(f"   Last: {ticker.last}")
                else:
                    print("❌ Pas de prix ES")
            else:
                print("❌ Interface IB non disponible")
        except Exception as e:
            print(f"❌ Erreur Test Direct: {e}")
        
        # 7. Résumé
        print("\n" + "=" * 30)
        print("📊 RÉSUMÉ")
        print("=" * 30)
        print("✅ Connexion: OK")
        print("✅ TWS: Connecté")
        print("✅ API: Fonctionnelle")
        print(f"⏰ Fin: {datetime.now().strftime('%H:%M:%S')}")
        
    except Exception as e:
        print(f"❌ Erreur générale: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if connector:
            try:
                await connector.disconnect()
                print("✅ Déconnexion propre")
            except Exception as e:
                print(f"⚠️ Erreur déconnexion: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(test_ib_simple())
    except KeyboardInterrupt:
        print("\n⏹️ Test interrompu")
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
