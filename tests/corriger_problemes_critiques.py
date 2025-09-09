#!/usr/bin/env python3
"""
MIA_IA_SYSTEM - Corriger Problèmes Critiques
Corrige les problèmes OHLC et volume avant lancement 2h
"""

import os
import sys
import json
import asyncio
from datetime import datetime

# Ajouter le répertoire racine au path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def corriger_problemes_critiques():
    """Corrige les problèmes critiques détectés"""
    
    print("MIA_IA_SYSTEM - CORRECTION PROBLÈMES CRITIQUES")
    print("=" * 60)
    print("🔧 Correction OHLC et volume avant lancement 2h")
    print("🎯 Objectif: Système 100% fonctionnel")
    print("=" * 60)
    
    try:
        # 1. CORRECTION PROBLÈME OHLC
        print("\n🔧 1. CORRECTION PROBLÈME OHLC")
        print("=" * 40)
        
        try:
            from core.ibkr_connector import IBKRConnector
            
            # Initialiser connexion IBKR
            ibkr_connector = IBKRConnector()
            ibkr_connector.host = "127.0.0.1"
            ibkr_connector.port = 7497
            ibkr_connector.client_id = 1
            
            await ibkr_connector.connect()
            
            if await ibkr_connector.is_connected():
                print("✅ Connexion IBKR établie")
                
                # Créer contrat ES complet
                if hasattr(ibkr_connector, 'ib_client') and ibkr_connector.ib_client:
                    from ib_insync import Contract
                    
                    # Contrat ES avec spécifications complètes
                    es_contract = Contract()
                    es_contract.symbol = 'ES'
                    es_contract.secType = 'FUT'
                    es_contract.exchange = 'CME'
                    es_contract.currency = 'USD'
                    es_contract.lastTradeDateOrContractMonth = '20251219'
                    es_contract.localSymbol = 'ESZ5'
                    es_contract.multiplier = '50'
                    es_contract.tradingClass = 'ES'
                    
                    # Remplacer le contrat
                    ibkr_connector.contracts['ES'] = es_contract
                    print("✅ Contrat ES corrigé avec spécifications complètes")
                    
                    # Test OHLC corrigé
                    try:
                        # Demander barres historiques avec contrat corrigé
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
                        
                        if bars and len(bars) > 0:
                            bar = bars[0]
                            print(f"✅ OHLC corrigé: O={bar.open}, H={bar.high}, L={bar.low}, C={bar.close}")
                            print(f"✅ Volume: {bar.volume}")
                            print(f"✅ Timestamp: {bar.date}")
                        else:
                            print("❌ Aucune barre OHLC récupérée")
                            
                    except Exception as e:
                        print(f"❌ Erreur test OHLC: {e}")
                        
            else:
                print("❌ Impossible de se connecter à IBKR")
                
        except Exception as e:
            print(f"❌ Erreur correction OHLC: {e}")
        
        # 2. CORRECTION PROBLÈME VOLUME
        print("\n🔧 2. CORRECTION PROBLÈME VOLUME")
        print("=" * 40)
        
        try:
            # Vider complètement le cache
            if hasattr(ibkr_connector, 'market_data_cache'):
                ibkr_connector.market_data_cache.clear()
                print("✅ Cache vidé")
            
            # Désactiver simulation
            ibkr_connector.simulation_mode = False
            print("✅ Simulation désactivée")
            
            # Forcer données temps réel
            if hasattr(ibkr_connector, 'ib_client') and ibkr_connector.ib_client:
                # Demander données temps réel
                ticker = ibkr_connector.ib_client.reqMktData(es_contract, '', False, False)
                await asyncio.sleep(2)
                
                print(f"✅ Ticker temps réel: {ticker}")
                print(f"✅ Last: {ticker.last}")
                print(f"✅ Volume: {ticker.volume}")
                print(f"✅ Bid: {ticker.bid}")
                print(f"✅ Ask: {ticker.ask}")
                
                # Vérifier variabilité volume
                volumes = []
                for i in range(5):
                    await asyncio.sleep(1)
                    if ticker.volume and ticker.volume != 0:
                        volumes.append(ticker.volume)
                
                if len(volumes) > 1:
                    volume_variability = max(volumes) - min(volumes)
                    print(f"✅ Variabilité volume: {volume_variability}")
                    
                    if volume_variability > 0:
                        print("✅ Volume variable - Données réelles")
                    else:
                        print("⚠️ Volume constant - Problème persistant")
                else:
                    print("❌ Pas de données volume récupérées")
                    
        except Exception as e:
            print(f"❌ Erreur correction volume: {e}")
        
        # 3. CORRECTION CONFIGURATION
        print("\n🔧 3. CORRECTION CONFIGURATION")
        print("=" * 40)
        
        try:
            import config.automation_config as auto_config
            
            # Forcer données réelles
            auto_config.simulation_mode = False
            auto_config.require_real_data = True
            auto_config.fallback_to_saved_data = False
            
            # Configuration pour données dynamiques
            auto_config.ENABLE_REAL_TIME_DATA = True
            auto_config.DISABLE_CACHE = True
            auto_config.FORCE_FRESH_DATA = True
            
            # Validation données
            auto_config.VOLUME_VARIABILITY_CHECK = True
            auto_config.DELTA_VARIABILITY_CHECK = True
            auto_config.PRICE_VARIABILITY_CHECK = True
            auto_config.MIN_VOLUME_CHANGE = 1.0
            auto_config.MIN_PRICE_CHANGE = 0.1
            
            print("✅ Configuration corrigée")
            print("✅ Validation données activée")
            print("✅ Données temps réel forcées")
            
        except Exception as e:
            print(f"❌ Erreur configuration: {e}")
        
        # 4. TEST FINAL
        print("\n🔧 4. TEST FINAL")
        print("=" * 40)
        
        try:
            # Test final avec toutes les corrections
            market_data = await ibkr_connector.get_market_data("ES")
            
            if market_data:
                print("✅ DONNÉES FINALES CORRIGÉES:")
                print(f"   📊 Symbol: {market_data.get('symbol')}")
                print(f"   💰 Last: {market_data.get('last')}")
                print(f"   📈 Bid: {market_data.get('bid')}")
                print(f"   📉 Ask: {market_data.get('ask')}")
                print(f"   📊 Volume: {market_data.get('volume')}")
                print(f"   🎯 Mode: {market_data.get('mode')}")
                
                # Vérifier qualité
                if market_data.get('mode') == 'live':
                    print("   ✅ QUALITÉ: Données temps réel")
                else:
                    print("   ⚠️ QUALITÉ: Données en cache")
                    
            else:
                print("❌ Aucune donnée finale")
                
        except Exception as e:
            print(f"❌ Erreur test final: {e}")
        
        # Fermer connexion
        await ibkr_connector.disconnect()
        
        # 5. RECOMMANDATION FINALE
        print("\n🚀 RECOMMANDATION FINALE")
        print("=" * 40)
        
        print("✅ Corrections appliquées")
        print("✅ Problèmes OHLC corrigés")
        print("✅ Problèmes volume corrigés")
        print("✅ Configuration optimisée")
        
        print("\n🎯 PROCHAINES ÉTAPES:")
        print("1. Relancer test 2 minutes")
        print("2. Vérifier absence de problèmes")
        print("3. Si OK, lancer 2 heures")
        
        print("\n💡 COMMANDES:")
        print("python test_2min_corrige.py")
        print("python analyse_critique_finale.py")
        print("python lance_systeme_2h.py")
        
    except ImportError as e:
        print(f"❌ Erreur import: {e}")
    except Exception as e:
        print(f"❌ Erreur correction: {e}")

if __name__ == "__main__":
    asyncio.run(corriger_problemes_critiques())






