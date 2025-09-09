#!/usr/bin/env python3
"""
Test prix ES configuration finale - MIA_IA_SYSTEM
Basé sur les souscriptions activées dans IBKR Account Management
"""

import time
from datetime import datetime

def test_es_with_correct_config():
    """Test avec la configuration correcte"""
    print("🔍 Test configuration finale...")
    
    try:
        from ib_insync import IB, Future
        
        # Connexion avec Client ID 3 (éviter tous les conflits)
        ib = IB()
        ib.connect('127.0.0.1', 7497, clientId=3, timeout=15)
        
        if not ib.isConnected():
            print("❌ Connexion échouée")
            return None
        
        print("✅ Connexion établie")
        print(f"   Client ID: 3")
        print("   Souscriptions activées: CME Real-Time + US Securities Bundle")
        
        # Créer le contrat ES avec tous les détails
        contract = Future('ES', '20241220', 'CME')
        contract.currency = 'USD'
        contract.multiplier = '50'
        contract.includeExpired = False
        
        print(f"📋 Contrat ES: {contract}")
        
        # Qualifier le contrat
        print("🔍 Qualification du contrat...")
        ib.qualifyContracts(contract)
        time.sleep(3)
        
        print(f"📋 Contrat qualifié: {contract}")
        
        # Demander les données de marché avec le bon format
        print("📊 Demande données marché CME...")
        
        # Utiliser le format CME Real-Time
        ib.reqMktData(contract, '', False, False, [])
        time.sleep(8)  # Attendre plus longtemps pour CME
        
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
            print(f"   High: {ticker.high if ticker else 'None'}")
            print(f"   Low: {ticker.low if ticker else 'None'}")
        
        ib.disconnect()
        return None
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return None

def test_es_alternative_method():
    """Test avec méthode alternative"""
    print("\n🔧 Test méthode alternative...")
    
    try:
        from ib_insync import IB, Future
        
        ib = IB()
        ib.connect('127.0.0.1', 7497, clientId=4, timeout=15)
        
        if not ib.isConnected():
            print("❌ Connexion échouée")
            return
        
        print("✅ Connexion établie")
        
        # Essayer avec le contrat ES sans date (front month)
        contract = Future('ES', '', 'CME')
        contract.currency = 'USD'
        contract.multiplier = '50'
        
        print(f"📋 Contrat ES front month: {contract}")
        
        # Demander données
        ib.reqMktData(contract)
        time.sleep(8)
        
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

def check_tws_final_settings():
    """Guide final pour TWS"""
    print("\n🔧 GUIDE FINAL TWS:")
    print("=" * 50)
    print("✅ VOS SOUSCRIPTIONS SONT ACTIVÉES:")
    print("   - CME Real-Time (NP,L2)")
    print("   - US Securities Snapshot and Futures Value Bundle")
    print("   - API Market Data activée")
    print("\n🔧 CONFIGURATION TWS REQUISE:")
    print("1. Ouvrez TWS")
    print("2. Edit > Global Configuration")
    print("3. API > Settings:")
    print("   ✓ Enable ActiveX and Socket Clients")
    print("   ✓ Socket port: 7497")
    print("   ✓ Allow connections from localhost")
    print("4. API > Precautions:")
    print("   ✓ Bypass Order Precautions for API Orders")
    print("5. Market Data:")
    print("   ✓ Use Global Configuration")
    print("   ✓ Enable streaming market data")
    print("6. Cliquez 'OK' et redémarrez TWS")
    print("7. Vérifiez que TWS affiche des prix ES en temps réel")
    print("=" * 50)

def main():
    """Test principal"""
    print("🚀 TEST PRIX ES CONFIGURATION FINALE")
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("🎯 Prix réel attendu: 6481.50")
    print("📋 Souscriptions IBKR: ACTIVÉES")
    print("📋 Configuration TWS: À VÉRIFIER")
    print("=" * 50)
    
    # Test 1: Configuration correcte
    prix = test_es_with_correct_config()
    
    # Test 2: Méthode alternative
    if not prix:
        test_es_alternative_method()
    
    # Guide final
    check_tws_final_settings()
    
    # Résumé
    print("\n" + "=" * 50)
    print("📊 RÉSUMÉ")
    if prix:
        print(f"✅ Prix ES: {prix}")
        print("✅ MIA_IA_SYSTEM opérationnel")
        print("🎉 SUCCÈS ! Le système peut récupérer les prix ES")
    else:
        print("❌ Impossible de récupérer le prix")
        print("💡 PROBLÈME: Configuration TWS incomplète")
        print("💡 SOLUTION: Suivez le guide TWS ci-dessus")
        print("💡 Vérifiez que TWS affiche des prix ES en temps réel")

if __name__ == "__main__":
    main()



