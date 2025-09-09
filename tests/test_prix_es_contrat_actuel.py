#!/usr/bin/env python3
"""
Test prix ES contrat actuel - MIA_IA_SYSTEM
Le contrat "ES Sep19'25" dans TWS est expiré, testons le contrat actuel
"""

import time
from datetime import datetime

def test_es_current_month():
    """Test avec le contrat ES du mois actuel"""
    print("🔍 Test contrat ES actuel...")
    
    try:
        from ib_insync import IB, Future
        
        # Connexion
        ib = IB()
        ib.connect('127.0.0.1', 7497, clientId=1, timeout=10)
        
        if not ib.isConnected():
            print("❌ Connexion échouée")
            return None
        
        print("✅ Connexion établie")
        
        # Test avec le contrat ES actuel (décembre 2024)
        # Format IBKR: YYYYMMDD
        contract = Future('ES', '20241220', 'CME')
        print(f"📋 Contrat ES actuel: {contract}")
        print("   Format: ES Dec20'24 @CME -> Future('ES', '20241220', 'CME')")
        
        # Demander le prix
        print("📊 Demande prix...")
        ib.reqMktData(contract)
        time.sleep(3)
        
        # Récupérer le ticker
        ticker = ib.ticker(contract)
        print(f"📊 Ticker: {ticker}")
        
        if ticker and ticker.marketPrice() and not str(ticker.marketPrice()) == 'nan':
            price = ticker.marketPrice()
            print(f"💰 Prix ES Dec20'24: {price}")
            
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
        
        ib.disconnect()
        return None
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return None

def test_es_front_month_simple():
    """Test avec le front month (contrat le plus proche)"""
    print("\n🔧 Test front month simple...")
    
    try:
        from ib_insync import IB, Future
        
        ib = IB()
        ib.connect('127.0.0.1', 7497, clientId=1, timeout=10)
        
        if not ib.isConnected():
            print("❌ Connexion échouée")
            return
        
        print("✅ Connexion établie")
        
        # Essayer avec ES sans date (front month automatique)
        contract = Future('ES', '', 'CME')
        print(f"📋 Contrat ES front month: {contract}")
        
        # Demander le prix
        ib.reqMktData(contract)
        time.sleep(3)
        
        ticker = ib.ticker(contract)
        if ticker and ticker.marketPrice() and not str(ticker.marketPrice()) == 'nan':
            price = ticker.marketPrice()
            print(f"💰 Prix ES front month: {price}")
            
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
            print("❌ Pas de prix front month")
        
        ib.disconnect()
        
    except Exception as e:
        print(f"❌ Erreur: {e}")

def test_es_with_symbol_lookup():
    """Test avec recherche de symbole"""
    print("\n🔧 Test avec recherche symbole...")
    
    try:
        from ib_insync import IB, Future
        
        ib = IB()
        ib.connect('127.0.0.1', 7497, clientId=1, timeout=10)
        
        if not ib.isConnected():
            print("❌ Connexion échouée")
            return
        
        print("✅ Connexion établie")
        
        # Rechercher le symbole ES
        print("🔍 Recherche symbole ES...")
        contracts = ib.reqContractDetails(Future('ES', '', 'CME'))
        
        if contracts:
            print(f"📋 {len(contracts)} contrats ES trouvés:")
            for i, contract_detail in enumerate(contracts[:5]):  # Afficher les 5 premiers
                contract = contract_detail.contract
                print(f"   {i+1}. {contract.symbol} {contract.lastTradeDateOrContractMonth} @{contract.exchange}")
                
                # Tester le premier contrat
                if i == 0:
                    print(f"   🧪 Test du contrat: {contract}")
                    ib.reqMktData(contract)
                    time.sleep(2)
                    
                    ticker = ib.ticker(contract)
                    if ticker and ticker.marketPrice() and not str(ticker.marketPrice()) == 'nan':
                        price = ticker.marketPrice()
                        print(f"   ✅ Prix: {price}")
                        
                        # Comparaison
                        prix_reel = 6481.50
                        diff = abs(price - prix_reel)
                        pct = (diff / prix_reel) * 100
                        
                        if pct < 1.0:
                            print(f"   ✅ Prix cohérent")
                        else:
                            print(f"   ⚠️ Prix différent: {pct:.3f}%")
                    else:
                        print(f"   ❌ Pas de prix")
        else:
            print("❌ Aucun contrat ES trouvé")
        
        ib.disconnect()
        
    except Exception as e:
        print(f"❌ Erreur: {e}")

def main():
    """Test principal"""
    print("🚀 TEST PRIX ES CONTRAT ACTUEL")
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("🎯 Prix réel attendu: 6481.50")
    print("📋 Contrat TWS affiché: ES Sep19'25 @CME (EXPIRÉ)")
    print("💡 Test du contrat ES actuel (Dec20'24)")
    print("=" * 50)
    
    # Test 1: Contrat actuel
    prix = test_es_current_month()
    
    # Test 2: Front month
    if not prix:
        test_es_front_month_simple()
    
    # Test 3: Recherche symbole
    if not prix:
        test_es_with_symbol_lookup()
    
    # Résumé
    print("\n" + "=" * 50)
    print("📊 RÉSUMÉ")
    if prix:
        print(f"✅ Prix ES: {prix}")
        print("✅ MIA_IA_SYSTEM opérationnel")
    else:
        print("❌ Impossible de récupérer le prix")
        print("💡 Le contrat ES Sep19'25 dans TWS est expiré")
        print("💡 Utilisez un contrat ES actuel")

if __name__ == "__main__":
    main()



