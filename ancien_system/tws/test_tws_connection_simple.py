#!/usr/bin/env python3
"""
Test connexion TWS mode simulé
"""
from ib_insync import *
import time

def test_tws_connection():
    """Test connexion TWS mode simulé"""
    print("🔌 Test connexion TWS mode simulé...")
    
    # Configuration TWS simulé
    config = {
        'host': '127.0.0.1',
        'port': 7497,  # Port TWS simulé
        'client_id': 1,
        'timeout': 30
    }
    
    try:
        # Connexion TWS
        ib = IB()
        print(f"📡 Connexion à TWS: {config['host']}:{config['port']}")
        
        ib.connect(
            config['host'], 
            config['port'], 
            clientId=config['client_id'],
            timeout=config['timeout']
        )
        
        print("✅ Connexion TWS réussie !")
        
        # Test données compte
        print("\n📊 Test données compte...")
        account_summary = ib.accountSummary()
        print(f"✅ Compte connecté: {len(account_summary)} éléments trouvés")
        
        # Test données marché ES
        print("\n📈 Test données marché ES...")
        contract = Future('ES', '202412', 'CME')
        ib.qualifyContracts(contract)
        
        # Subscribe market data
        ib.reqMktData(contract)
        time.sleep(3)  # Attendre données
        
        ticker = ib.ticker(contract)
        if ticker and ticker.marketName():
            print(f"✅ Données ES: {ticker.marketName()} - Bid: {ticker.bid} Ask: {ticker.ask}")
        else:
            print("⚠️ Pas de données ES en temps réel (normal hors heures marché)")
        
        # Test données historiques
        print("\n📚 Test données historiques...")
        bars = ib.reqHistoricalData(
            contract,
            endDateTime='',
            durationStr='1 D',
            barSizeSetting='1 hour',
            whatToShow='TRADES',
            useRTH=True
        )
        
        if bars:
            print(f"✅ Données historiques: {len(bars)} barres trouvées")
            print(f"   Dernière barre: {bars[-1].date} - Close: {bars[-1].close}")
        else:
            print("⚠️ Pas de données historiques (vérifier permissions)")
        
        # Déconnexion
        ib.disconnect()
        print("\n✅ Test TWS terminé avec succès !")
        return True
        
    except Exception as e:
        print(f"❌ Erreur connexion TWS: {e}")
        return False

if __name__ == "__main__":
    test_tws_connection() 