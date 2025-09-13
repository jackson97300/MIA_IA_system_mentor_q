#!/usr/bin/env python3
"""
Test prix ES final - MIA_IA_SYSTEM
Utilise le contrat ES trouvé: conId=637533641
"""

import time
from datetime import datetime

def test_es_with_conid():
    """Test avec le conId du contrat ES trouvé"""
    print("🔍 Test avec conId du contrat ES...")
    
    try:
        from ib_insync import IB, Future
        
        # Connexion
        ib = IB()
        ib.connect('127.0.0.1', 7497, clientId=1, timeout=10)
        
        if not ib.isConnected():
            print("❌ Connexion échouée")
            return None
        
        print("✅ Connexion établie")
        
        # Créer le contrat avec le conId trouvé
        contract = Future('ES', '20250919', 'CME')
        contract.conId = 637533641  # ConId trouvé dans le test précédent
        
        print(f"📋 Contrat ES avec conId: {contract}")
        print(f"   conId: {contract.conId}")
        print(f"   Symbol: {contract.symbol}")
        print(f"   Date: {contract.lastTradeDateOrContractMonth}")
        print(f"   Exchange: {contract.exchange}")
        
        # Demander le prix
        print("📊 Demande prix...")
        ib.reqMktData(contract)
        time.sleep(5)  # Attendre plus longtemps
        
        # Récupérer le ticker
        ticker = ib.ticker(contract)
        print(f"📊 Ticker: {ticker}")
        
        if ticker and ticker.marketPrice() and not str(ticker.marketPrice()) == 'nan':
            price = ticker.marketPrice()
            print(f"💰 Prix ES: {price}")
            
            # Comparaison avec la réalité
            prix_reel = 6481.50
            diff = abs(price - prix_reel)
            pct = (diff / prix_reel) * 100
            
            print(f"🎯 Prix réel: {prix_reel}")
            print(f"📈 Différence: {diff:.2f}")
            print(f"📊 Pourcentage: {pct:.3f}%")
            
            if pct < 1.0:
                print("✅ Prix cohérent")
                ib.disconnect()
                return price
            else:
                print("⚠️ Prix différent")
        else:
            print("❌ Pas de prix")
            print(f"   Market Price: {ticker.marketPrice() if ticker else 'None'}")
            print(f"   Bid: {ticker.bid if ticker else 'None'}")
            print(f"   Ask: {ticker.ask if ticker else 'None'}")
        
        ib.disconnect()
        return None
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return None

def test_es_direct_contract():
    """Test direct avec le contrat trouvé"""
    print("\n🔧 Test direct avec contrat...")
    
    try:
        from ib_insync import IB, Future
        
        ib = IB()
        ib.connect('127.0.0.1', 7497, clientId=1, timeout=10)
        
        if not ib.isConnected():
            print("❌ Connexion échouée")
            return
        
        print("✅ Connexion établie")
        
        # Créer le contrat exact trouvé
        contract = Future('ES', '20250919', 'CME')
        contract.conId = 637533641
        
        # Qualifier le contrat
        print("🔍 Qualification du contrat...")
        ib.qualifyContracts(contract)
        time.sleep(3)
        
        print(f"📋 Contrat qualifié: {contract}")
        
        # Demander le prix avec plus de détails
        print("📊 Demande prix détaillée...")
        ib.reqMktData(contract)
        time.sleep(5)
        
        ticker = ib.ticker(contract)
        if ticker:
            print("📊 Données reçues:")
            print(f"   Market Price: {ticker.marketPrice()}")
            print(f"   Bid: {ticker.bid}")
            print(f"   Ask: {ticker.ask}")
            print(f"   High: {ticker.high}")
            print(f"   Low: {ticker.low}")
            print(f"   Close: {ticker.close}")
            print(f"   Volume: {ticker.volume}")
            
            if ticker.marketPrice() and not str(ticker.marketPrice()) == 'nan':
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
            else:
                print("❌ Pas de prix valide")
        else:
            print("❌ Pas de ticker")
        
        ib.disconnect()
        
    except Exception as e:
        print(f"❌ Erreur: {e}")

def main():
    """Test principal"""
    print("🚀 TEST PRIX ES FINAL")
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("🎯 Prix réel attendu: 6481.50")
    print("📋 Contrat trouvé: ES 20250919 @CME (conId=637533641)")
    print("=" * 50)
    
    # Test 1: Avec conId
    prix = test_es_with_conid()
    
    # Test 2: Direct avec contrat
    if not prix:
        test_es_direct_contract()
    
    # Résumé
    print("\n" + "=" * 50)
    print("📊 RÉSUMÉ")
    if prix:
        print(f"✅ Prix ES: {prix}")
        print("✅ MIA_IA_SYSTEM opérationnel")
        print("🎉 SUCCÈS ! Le système peut récupérer les prix ES")
    else:
        print("❌ Impossible de récupérer le prix")
        print("💡 Vérifiez les paramètres de marché dans TWS")

if __name__ == "__main__":
    main()



