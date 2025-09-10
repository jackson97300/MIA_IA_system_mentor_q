#!/usr/bin/env python3
"""
Test ES avec ib-insync (API directe IBKR)
Pour récupérer le vrai prix ES (~6482)
"""

import sys
import asyncio
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

try:
    from ib_insync import *
    print("✅ ib-insync installé")
except ImportError:
    print("❌ ib-insync non installé")
    print("💡 Installez avec: pip install ib-insync")
    sys.exit(1)

async def test_ib_insync_es():
    """Test ES avec ib-insync"""
    
    print("🔍 Test ES avec ib-insync")
    print("Prix attendu: ~6482")
    print("=" * 50)
    
    ib = IB()
    
    try:
        # Connexion TWS/Gateway
        print("🔌 Connexion à TWS/Gateway...")
        await ib.connectAsync('127.0.0.1', 7497, clientId=1)
        
        if not ib.isConnected():
            print("❌ Connexion échouée")
            return False
        
        print("✅ Connecté à TWS/Gateway")
        
        # Test ES futures
        print("\n📊 Test ES futures...")
        
        # Essayer différents contrats ES
        es_contracts = [
            Future('ES', '202509', 'CME'),  # Sept 2025
            Future('ES', '202512', 'CME'),  # Dec 2025
            Future('ES', '202503', 'CME'),  # March 2025
        ]
        
        for contract in es_contracts:
            print(f"\n🔍 Test contrat: {contract}")
            
            try:
                # Qualifier le contrat
                await ib.qualifyContractsAsync(contract)
                print(f"   ✅ Contrat qualifié: {contract.localSymbol}")
                
                # Récupérer market data
                ticker = ib.reqMktData(contract, '', False, False)
                
                # Attendre données
                await asyncio.sleep(2)
                
                if ticker.last != -1:
                    print(f"   🎯 PRIX ES TROUVÉ!")
                    print(f"      Last: {ticker.last}")
                    print(f"      Bid: {ticker.bid}")
                    print(f"      Ask: {ticker.ask}")
                    print(f"      Volume: {ticker.volume}")
                    print(f"      High: {ticker.high}")
                    print(f"      Low: {ticker.low}")
                    print(f"      Open: {ticker.open}")
                    
                    # Vérifier si le prix est correct
                    if 6000 <= ticker.last <= 7000:
                        print(f"   ✅ Prix ES correct: {ticker.last}")
                        return contract
                    else:
                        print(f"   ⚠️ Prix suspect: {ticker.last}")
                
                elif ticker.bid != -1:
                    print(f"   Bid disponible: {ticker.bid}")
                    if 6000 <= ticker.bid <= 7000:
                        print(f"   ✅ Prix ES correct (bid): {ticker.bid}")
                        return contract
                
                else:
                    print(f"   ❌ Pas de données")
                
                # Annuler subscription
                ib.cancelMktData(contract)
                
            except Exception as e:
                print(f"   ❌ Erreur contrat {contract}: {e}")
        
        print("\n❌ Aucun contrat ES valide trouvé")
        return False
        
    except Exception as e:
        print(f"❌ Erreur générale: {e}")
        return False
    finally:
        if ib.isConnected():
            ib.disconnect()
            print("🔌 Déconnecté")

async def get_es_data_realtime(contract):
    """Récupérer données ES temps réel"""
    
    print(f"\n📊 Données ES temps réel pour {contract.localSymbol}")
    print("=" * 50)
    
    ib = IB()
    
    try:
        await ib.connectAsync('127.0.0.1', 7497, clientId=1)
        
        if not ib.isConnected():
            return False
        
        # Subscription market data
        ticker = ib.reqMktData(contract, '', False, False)
        
        print("🔄 Attente données temps réel...")
        
        # Attendre et afficher données
        for i in range(10):  # 10 mises à jour
            await asyncio.sleep(1)
            
            if ticker.last != -1:
                print(f"   Tick {i+1}: Last={ticker.last}, Bid={ticker.bid}, Ask={ticker.ask}, Vol={ticker.volume}")
            elif ticker.bid != -1:
                print(f"   Tick {i+1}: Bid={ticker.bid}, Ask={ticker.ask}")
            else:
                print(f"   Tick {i+1}: En attente...")
        
        # Récupérer données historiques
        print("\n📈 Données historiques...")
        bars = ib.reqHistoricalData(
            contract,
            endDateTime='',
            durationStr='1 D',
            barSizeSetting='1 min',
            whatToShow='TRADES',
            useRTH=True,
            formatDate=1
        )
        
        if bars:
            print(f"   ✅ {len(bars)} barres historiques")
            if len(bars) > 0:
                last_bar = bars[-1]
                print(f"   Dernière barre: O={last_bar.open}, H={last_bar.high}, L={last_bar.low}, C={last_bar.close}, V={last_bar.volume}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur données temps réel: {e}")
        return False
    finally:
        if ib.isConnected():
            ib.disconnect()

async def main():
    """Fonction principale"""
    
    print("🚀 Test ES avec ib-insync")
    print("=" * 60)
    
    # Test connexion et recherche contrat
    valid_contract = await test_ib_insync_es()
    
    if valid_contract:
        print(f"\n🎉 Contrat ES valide trouvé: {valid_contract.localSymbol}")
        
        # Test données temps réel
        await get_es_data_realtime(valid_contract)
        
        print(f"\n💡 Utilisez ce contrat: {valid_contract}")
        print(f"💡 Conid: {valid_contract.conId}")
        print(f"💡 Local Symbol: {valid_contract.localSymbol}")
    else:
        print("\n❌ Aucun contrat ES valide trouvé")
        print("💡 Vérifiez que TWS/Gateway est connecté")
        print("💡 Vérifiez les permissions market data")

if __name__ == "__main__":
    asyncio.run(main())

