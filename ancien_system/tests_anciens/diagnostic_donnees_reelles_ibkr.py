#!/usr/bin/env python3
"""
MIA_IA_SYSTEM - Diagnostic Données Réelles IBKR
Diagnostique et corrige les problèmes de données réelles
"""

import os
import sys
import json
import asyncio
from datetime import datetime, timedelta

# Ajouter le répertoire racine au path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def diagnostic_donnees_reelles():
    """Diagnostique les données réelles IBKR"""
    
    print("MIA_IA_SYSTEM - DIAGNOSTIC DONNÉES RÉELLES IBKR")
    print("=" * 60)
    
    try:
        from core.ibkr_connector import IBKRConnector
        from core.logger import get_logger
        
        logger = get_logger(__name__)
        
        # Initialiser connexion IBKR
        print("🔗 Initialisation connexion IBKR...")
        ibkr_connector = IBKRConnector()
        ibkr_connector.host = "127.0.0.1"
        ibkr_connector.port = 7497
        ibkr_connector.client_id = 1
        
        # Connecter
        await ibkr_connector.connect()
        
        if not ibkr_connector.is_connected():
            print("❌ Impossible de se connecter à IBKR")
            return
        
        print("✅ Connexion IBKR établie")
        
        # Test 1: Données ES temps réel
        print("\n📊 TEST 1: Données ES temps réel")
        print("=" * 40)
        
        for i in range(5):
            try:
                # Récupérer données ES
                market_data = await ibkr_connector.get_market_data("ES")
                
                if market_data:
                    print(f"⏰ {datetime.now().strftime('%H:%M:%S')} | "
                          f"📊 Vol: {market_data.get('volume', 'N/A')} | "
                          f"💰 Prix: {market_data.get('last', 'N/A')} | "
                          f"📈 Bid: {market_data.get('bid', 'N/A')} | "
                          f"📉 Ask: {market_data.get('ask', 'N/A')} | "
                          f"🎯 Mode: {market_data.get('mode', 'N/A')}")
                else:
                    print(f"⏰ {datetime.now().strftime('%H:%M:%S')} | ❌ Aucune donnée")
                
                await asyncio.sleep(2)
                
            except Exception as e:
                print(f"❌ Erreur données ES: {e}")
                await asyncio.sleep(2)
        
        # Test 2: Données VIX
        print("\n📊 TEST 2: Données VIX")
        print("=" * 40)
        
        try:
            # Récupérer données VIX
            vix_data = await ibkr_connector.get_market_data("VIX")
            
            if vix_data:
                print(f"📊 VIX: {vix_data.get('last', 'N/A')}")
                print(f"📈 Bid: {vix_data.get('bid', 'N/A')}")
                print(f"📉 Ask: {vix_data.get('ask', 'N/A')}")
            else:
                print("❌ Aucune donnée VIX")
                
        except Exception as e:
            print(f"❌ Erreur VIX: {e}")
        
        # Test 3: Données historiques OHLC
        print("\n📊 TEST 3: Données historiques OHLC")
        print("=" * 40)
        
        try:
            # Récupérer barres historiques
            if hasattr(ibkr_connector, 'ib_client') and ibkr_connector.ib_client:
                from ib_insync import Contract
                
                # Créer contrat ES
                es_contract = Contract()
                es_contract.symbol = 'ES'
                es_contract.secType = 'FUT'
                es_contract.exchange = 'CME'
                es_contract.currency = 'USD'
                
                # Demander barres historiques
                bars = ibkr_connector.ib_client.reqHistoricalData(
                    es_contract,
                    '',
                    '1 D',
                    '1 min',
                    'TRADES',
                    1,
                    1,
                    False
                )
                
                if bars:
                    bar = bars[0]
                    print(f"📊 OHLC: O={bar.open}, H={bar.high}, L={bar.low}, C={bar.close}")
                    print(f"📈 Volume: {bar.volume}")
                    print(f"⏰ Timestamp: {bar.date}")
                else:
                    print("❌ Aucune barre historique")
                    
        except Exception as e:
            print(f"❌ Erreur OHLC: {e}")
        
        # Test 4: Forcer refresh des données
        print("\n📊 TEST 4: Forcer refresh des données")
        print("=" * 40)
        
        try:
            # Vider le cache
            if hasattr(ibkr_connector, 'market_data_cache'):
                ibkr_connector.market_data_cache.clear()
                print("✅ Cache vidé")
            
            # Récupérer données fraîches
            fresh_data = await ibkr_connector.get_market_data("ES")
            
            if fresh_data:
                print(f"📊 Données fraîches: {fresh_data}")
            else:
                print("❌ Aucune donnée fraîche")
                
        except Exception as e:
            print(f"❌ Erreur refresh: {e}")
        
        # Test 5: Vérifier connexion temps réel
        print("\n📊 TEST 5: Connexion temps réel")
        print("=" * 40)
        
        try:
            if hasattr(ibkr_connector, 'ib_client') and ibkr_connector.ib_client:
                # Vérifier état connexion
                is_connected = ibkr_connector.ib_client.isConnected()
                print(f"🔗 Connexion active: {is_connected}")
                
                # Vérifier données temps réel
                if is_connected:
                    # Demander données temps réel
                    ticker = ibkr_connector.ib_client.reqMktData(es_contract, '', False, False)
                    await asyncio.sleep(1)
                    
                    print(f"📊 Ticker temps réel: {ticker}")
                    print(f"💰 Last: {ticker.last}")
                    print(f"📈 Bid: {ticker.bid}")
                    print(f"📉 Ask: {ticker.ask}")
                    print(f"📊 Volume: {ticker.volume}")
                    
        except Exception as e:
            print(f"❌ Erreur temps réel: {e}")
        
        # Recommandations
        print("\n💡 RECOMMANDATIONS")
        print("=" * 40)
        
        print("1. 🔧 Problème VIX: Utiliser valeur par défaut si None")
        print("2. 📊 Problème OHLC: Vérifier permissions données historiques")
        print("3. ⚡ Volume constant: Activer Level 2 complet")
        print("4. 🔄 Refresh: Vider cache régulièrement")
        print("5. 📡 Temps réel: Utiliser reqMktData au lieu de cache")
        
        # Fermer connexion
        await ibkr_connector.disconnect()
        print("\n✅ Diagnostic terminé")
        
    except ImportError as e:
        print(f"❌ Erreur import: {e}")
    except Exception as e:
        print(f"❌ Erreur diagnostic: {e}")

if __name__ == "__main__":
    asyncio.run(diagnostic_donnees_reelles())






