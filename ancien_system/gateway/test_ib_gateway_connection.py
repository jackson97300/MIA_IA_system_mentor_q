#!/usr/bin/env python3
"""
TEST CONNEXION IB GATEWAY - MIA_IA_SYSTEM
Version: 1.0.0 - Compatible IB Gateway 2025
"""

from ib_insync import *
import asyncio
import logging
from datetime import datetime

# Configuration logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration IB Gateway
IB_GATEWAY_CONFIG = {
    'host': '127.0.0.1',
    'port': 4001,  # Port IB Gateway
    'client_id': 1,
    'timeout': 30
}

async def test_ib_gateway_connection():
    """Test de connexion IB Gateway"""
    
    print("🔌 Test de connexion IB Gateway...")
    print(f"📡 Configuration: {IB_GATEWAY_CONFIG['host']}:{IB_GATEWAY_CONFIG['port']}")
    
    # Initialisation IB
    ib = IB()
    
    try:
        # Connexion IB Gateway
        print("🔄 Connexion en cours...")
        ib.connect(
            IB_GATEWAY_CONFIG['host'], 
            IB_GATEWAY_CONFIG['port'], 
            clientId=IB_GATEWAY_CONFIG['client_id']
        )
        
        # Attendre connexion
        await asyncio.sleep(3)
        
        # Test connexion
        if ib.isConnected():
            print("✅ Connexion IB Gateway réussie!")
            
            # Test données compte
            print("📊 Récupération données compte...")
            try:
                account_summary = ib.accountSummary()
                print(f"✅ Compte: {len(account_summary)} éléments trouvés")
                
                # Afficher quelques infos compte
                for item in account_summary[:3]:
                    print(f"   - {item.tag}: {item.value}")
                    
            except Exception as e:
                print(f"⚠️ Erreur données compte: {e}")
            
            # Test données marché ES
            print("📈 Test données marché ES...")
            try:
                # Contrat ES December 2024
                contract = Future('ES', '202412', 'CME')
                ib.qualifyContracts(contract)
                
                # Subscribe market data
                ib.reqMktData(contract)
                await asyncio.sleep(2)
                
                ticker = ib.ticker(contract)
                if ticker.marketPrice():
                    print(f"✅ Prix ES: {ticker.marketPrice()}")
                    print(f"   Bid: {ticker.bid} | Ask: {ticker.ask}")
                    print(f"   Volume: {ticker.volume}")
                else:
                    print("⚠️ Pas de données marché ES")
                    
            except Exception as e:
                print(f"⚠️ Erreur données marché: {e}")
            
            # Test données historiques
            print("📊 Test données historiques...")
            try:
                bars = ib.reqHistoricalData(
                    contract,
                    endDateTime='',
                    durationStr='1 D',
                    barSizeSetting='1 min',
                    whatToShow='TRADES',
                    useRTH=True
                )
                
                if bars:
                    print(f"✅ Données historiques: {len(bars)} barres récupérées")
                    print(f"   Dernière barre: {bars[-1]}")
                else:
                    print("⚠️ Pas de données historiques")
                    
            except Exception as e:
                print(f"⚠️ Erreur données historiques: {e}")
                
        else:
            print("❌ Connexion échouée")
            
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")
        
    finally:
        # Déconnexion
        if ib.isConnected():
            ib.disconnect()
            print("🔌 Déconnexion effectuée")

def test_ib_gateway_sync():
    """Test synchrone IB Gateway"""
    
    print("🔌 Test IB Gateway (mode synchrone)...")
    
    ib = IB()
    
    try:
        # Connexion
        ib.connect('127.0.0.1', 4001, clientId=1)
        
        if ib.isConnected():
            print("✅ Connexion réussie!")
            
            # Test simple
            account = ib.accountSummary()
            print(f"✅ Compte: {len(account)} éléments")
            
        else:
            print("❌ Connexion échouée")
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
    finally:
        if ib.isConnected():
            ib.disconnect()

if __name__ == "__main__":
    print("🚀 TEST CONNEXION IB GATEWAY - MIA_IA_SYSTEM")
    print("=" * 50)
    
    # Test asynchrone
    asyncio.run(test_ib_gateway_connection())
    
    print("\n" + "=" * 50)
    print("✅ Test terminé") 