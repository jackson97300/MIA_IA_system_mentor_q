#!/usr/bin/env python3
"""
Test prix ES ultra-simple - MIA_IA_SYSTEM
Vérification du prix ES vs réalité (6481.50)
"""

import time
from datetime import datetime

def test_es_price_ultra_simple():
    """Test ultra-simple du prix ES"""
    print("🔍 Test ultra-simple prix ES...")
    
    try:
        from ib_insync import IB, Future
        
        # Connexion
        ib = IB()
        ib.connect('127.0.0.1', 7497, clientId=1, timeout=10)
        
        if not ib.isConnected():
            print("❌ Connexion échouée")
            return None
        
        print("✅ Connexion établie")
        
        # Créer le contrat ES
        contract = Future('ES', '20241220', 'CME')
        print(f"📋 Contrat ES: {contract}")
        
        # Utiliser la méthode simple d'ib_insync
        print("📊 Demande prix...")
        ib.reqMktData(contract)
        
        # Attendre
        time.sleep(3)
        
        # Récupérer le ticker
        ticker = ib.ticker(contract)
        print(f"📊 Ticker: {ticker}")
        
        if ticker and ticker.marketPrice():
            price = ticker.marketPrice()
            print(f"💰 Prix ES: {price}")
            
            # Comparaison
            prix_reel = 6481.50
            diff = abs(price - prix_reel)
            pct = (diff / prix_reel) * 100
            
            print(f"🎯 Prix réel: {prix_reel}")
            print(f"📈 Différence: {diff:.2f}")
            print(f"📊 Pourcentage: {pct:.3f}%")
            
            if pct < 1.0:
                print("✅ Prix cohérent")
            else:
                print("⚠️ Prix différent")
            
            ib.disconnect()
            return price
        else:
            print("❌ Pas de prix")
            ib.disconnect()
            return None
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return None

def test_es_with_qualify():
    """Test avec qualification du contrat"""
    print("\n🔧 Test avec qualification...")
    
    try:
        from ib_insync import IB, Future
        
        ib = IB()
        ib.connect('127.0.0.1', 7497, clientId=1, timeout=10)
        
        if not ib.isConnected():
            print("❌ Connexion échouée")
            return
        
        print("✅ Connexion établie")
        
        # Créer et qualifier le contrat
        contract = Future('ES', '20241220', 'CME')
        print(f"📋 Contrat initial: {contract}")
        
        # Qualifier le contrat
        ib.qualifyContracts(contract)
        time.sleep(2)
        
        print(f"📋 Contrat qualifié: {contract}")
        
        # Demander le prix
        ib.reqMktData(contract)
        time.sleep(3)
        
        ticker = ib.ticker(contract)
        if ticker:
            print("📊 Données reçues:")
            print(f"   Prix: {ticker.marketPrice()}")
            print(f"   Bid: {ticker.bid}")
            print(f"   Ask: {ticker.ask}")
        else:
            print("❌ Pas de données")
        
        ib.disconnect()
        
    except Exception as e:
        print(f"❌ Erreur: {e}")

def main():
    """Test principal"""
    print("🚀 TEST PRIX ES ULTRA-SIMPLE")
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("🎯 Prix réel attendu: 6481.50")
    print("=" * 50)
    
    # Test 1: Ultra-simple
    prix = test_es_price_ultra_simple()
    
    # Test 2: Avec qualification
    test_es_with_qualify()
    
    # Résumé
    print("\n" + "=" * 50)
    print("📊 RÉSUMÉ")
    if prix:
        print(f"✅ Prix ES: {prix}")
        print("✅ MIA_IA_SYSTEM opérationnel")
    else:
        print("❌ Impossible de récupérer le prix")
        print("💡 Problème de données de marché")

if __name__ == "__main__":
    main()



