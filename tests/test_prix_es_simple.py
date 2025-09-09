#!/usr/bin/env python3
"""
Test prix ES simple - MIA_IA_SYSTEM
Vérification du prix ES vs réalité (6481.50)
"""

import time
from datetime import datetime

def get_es_price_simple():
    """Récupère le prix actuel de ES (version simple)"""
    print("🔍 Récupération prix ES...")
    
    try:
        from ib_insync import IB, Future
        
        # Connexion avec la configuration validée
        ib = IB()
        ib.connect('127.0.0.1', 7497, clientId=1, timeout=10)
        
        if not ib.isConnected():
            print("❌ Connexion échouée")
            return None
        
        print("✅ Connexion établie")
        
        # Créer le contrat ES (syntaxe corrigée)
        contract = Future('ES', '20241220', 'CME')
        print(f"📋 Contrat ES: {contract}")
        
        # Demander le prix de marché
        print("📊 Demande prix de marché...")
        ib.reqMktData(1, contract)
        
        # Attendre les données
        time.sleep(5)
        
        # Récupérer le prix
        ticker = ib.ticker(contract)
        print(f"📊 Ticker reçu: {ticker}")
        
        if ticker and hasattr(ticker, 'marketPrice') and ticker.marketPrice():
            price = ticker.marketPrice()
            print(f"💰 Prix ES actuel: {price}")
            
            # Comparaison avec la réalité
            prix_reel = 6481.50
            difference = abs(price - prix_reel)
            pourcentage = (difference / prix_reel) * 100
            
            print(f"🎯 Prix réel attendu: {prix_reel}")
            print(f"📈 Différence: {difference:.2f}")
            print(f"📊 Pourcentage: {pourcentage:.3f}%")
            
            if pourcentage < 1.0:
                print("✅ Prix cohérent avec la réalité")
            else:
                print("⚠️ Prix différent de la réalité")
            
            ib.disconnect()
            return price
        else:
            print("❌ Impossible de récupérer le prix")
            print(f"Ticker: {ticker}")
            if ticker:
                print(f"Market Price: {ticker.marketPrice()}")
                print(f"Bid: {ticker.bid}")
                print(f"Ask: {ticker.ask}")
            ib.disconnect()
            return None
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_es_with_contract_details():
    """Test avec détails du contrat"""
    print("\n🔧 Test avec détails contrat...")
    
    try:
        from ib_insync import IB, Future
        
        ib = IB()
        ib.connect('127.0.0.1', 7497, clientId=1, timeout=10)
        
        if not ib.isConnected():
            print("❌ Connexion échouée")
            return
        
        print("✅ Connexion établie")
        
        # Créer le contrat ES avec plus de détails
        contract = Future('ES', '20241220', 'CME')
        contract.currency = 'USD'
        print(f"📋 Contrat ES détaillé: {contract}")
        
        # Demander les détails du contrat
        print("📋 Demande détails contrat...")
        ib.reqContractDetails(1, contract)
        time.sleep(2)
        
        # Demander le prix
        print("📊 Demande prix...")
        ib.reqMktData(2, contract)
        time.sleep(3)
        
        ticker = ib.ticker(contract)
        if ticker:
            print("📊 Données ES reçues:")
            print(f"   Prix de marché: {ticker.marketPrice()}")
            print(f"   Bid: {ticker.bid}")
            print(f"   Ask: {ticker.ask}")
            print(f"   Volume: {ticker.volume}")
            print(f"   Heure: {ticker.time}")
        else:
            print("❌ Aucune donnée reçue")
        
        ib.disconnect()
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Test principal"""
    print("🚀 TEST PRIX ES SIMPLE")
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("🎯 Prix réel attendu: 6481.50")
    print("=" * 50)
    
    # Test 1: Prix simple
    prix_es = get_es_price_simple()
    
    # Test 2: Avec détails contrat
    test_es_with_contract_details()
    
    # Résumé
    print("\n" + "=" * 50)
    print("📊 RÉSUMÉ")
    if prix_es:
        print(f"✅ Prix ES récupéré: {prix_es}")
        print("✅ MIA_IA_SYSTEM peut accéder aux données")
    else:
        print("❌ Impossible de récupérer le prix")
        print("💡 Vérifiez la connexion TWS")

if __name__ == "__main__":
    main()



