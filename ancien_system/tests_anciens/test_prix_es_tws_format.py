#!/usr/bin/env python3
"""
Test prix ES avec format TWS correct - MIA_IA_SYSTEM
Basé sur l'interface TWS: "ES Sep19'25 @CME"
"""

import time
from datetime import datetime

def test_es_tws_format():
    """Test avec le format de contrat ES de TWS"""
    print("🔍 Test format contrat ES TWS...")
    
    try:
        from ib_insync import IB, Future
        
        # Connexion
        ib = IB()
        ib.connect('127.0.0.1', 7497, clientId=1, timeout=10)
        
        if not ib.isConnected():
            print("❌ Connexion échouée")
            return None
        
        print("✅ Connexion établie")
        
        # Format TWS: "ES Sep19'25 @CME" -> Future('ES', '20250919', 'CME')
        # Test avec le contrat affiché dans TWS
        contract = Future('ES', '20250919', 'CME')
        print(f"📋 Contrat ES TWS: {contract}")
        print("   Format: ES Sep19'25 @CME -> Future('ES', '20250919', 'CME')")
        
        # Demander le prix
        print("📊 Demande prix...")
        ib.reqMktData(contract)
        time.sleep(3)
        
        # Récupérer le ticker
        ticker = ib.ticker(contract)
        print(f"📊 Ticker: {ticker}")
        
        if ticker and ticker.marketPrice() and not str(ticker.marketPrice()) == 'nan':
            price = ticker.marketPrice()
            print(f"💰 Prix ES Sep19'25: {price}")
            
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

def test_es_alternative_formats():
    """Test avec d'autres formats possibles"""
    print("\n🔧 Test formats alternatifs...")
    
    try:
        from ib_insync import IB, Future
        
        ib = IB()
        ib.connect('127.0.0.1', 7497, clientId=1, timeout=10)
        
        if not ib.isConnected():
            print("❌ Connexion échouée")
            return
        
        print("✅ Connexion établie")
        
        # Formats alternatifs basés sur TWS
        formats_test = [
            ('ES', '20250919', 'CME'),  # Format standard
            ('ES', '202509', 'CME'),    # Format court
            ('ES', 'Sep25', 'CME'),     # Format TWS court
            ('ES', '2025-09-19', 'CME'), # Format ISO
        ]
        
        for symbol, date, exchange in formats_test:
            print(f"\n📋 Test: {symbol} {date} @{exchange}")
            
            try:
                contract = Future(symbol, date, exchange)
                print(f"   Contrat: {contract}")
                
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
                        print(f"   ✅ Prix cohérent pour {symbol} {date}")
                        ib.disconnect()
                        return price
                    else:
                        print(f"   ⚠️ Prix différent: {pct:.3f}%")
                else:
                    print(f"   ❌ Pas de prix")
                    
            except Exception as e:
                print(f"   ❌ Erreur: {e}")
                continue
        
        print("\n❌ Aucun format valide trouvé")
        ib.disconnect()
        
    except Exception as e:
        print(f"❌ Erreur générale: {e}")

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
        
        # Contrat avec plus de détails
        contract = Future('ES', '20250919', 'CME')
        contract.currency = 'USD'
        contract.multiplier = '50'
        
        print(f"📋 Contrat détaillé: {contract}")
        print(f"   Currency: {contract.currency}")
        print(f"   Multiplier: {contract.multiplier}")
        
        # Qualifier le contrat
        print("🔍 Qualification du contrat...")
        ib.qualifyContracts(contract)
        time.sleep(2)
        
        print(f"📋 Contrat qualifié: {contract}")
        
        # Demander le prix
        ib.reqMktData(contract)
        time.sleep(3)
        
        ticker = ib.ticker(contract)
        if ticker and ticker.marketPrice() and not str(ticker.marketPrice()) == 'nan':
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
            print("❌ Pas de prix")
        
        ib.disconnect()
        
    except Exception as e:
        print(f"❌ Erreur: {e}")

def main():
    """Test principal"""
    print("🚀 TEST PRIX ES FORMAT TWS")
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("🎯 Prix réel attendu: 6481.50")
    print("📋 Contrat TWS: ES Sep19'25 @CME")
    print("=" * 50)
    
    # Test 1: Format TWS standard
    prix = test_es_tws_format()
    
    # Test 2: Formats alternatifs
    if not prix:
        test_es_alternative_formats()
    
    # Test 3: Avec détails contrat
    if not prix:
        test_es_with_contract_details()
    
    # Résumé
    print("\n" + "=" * 50)
    print("📊 RÉSUMÉ")
    if prix:
        print(f"✅ Prix ES: {prix}")
        print("✅ MIA_IA_SYSTEM opérationnel")
    else:
        print("❌ Impossible de récupérer le prix")
        print("💡 Vérifiez le format du contrat dans TWS")

if __name__ == "__main__":
    main()



