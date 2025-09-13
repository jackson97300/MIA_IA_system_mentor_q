#!/usr/bin/env python3
"""
Test prix ES simple final - MIA_IA_SYSTEM
Test simple avec Client ID différent
"""

import time
from datetime import datetime

def test_es_simple():
    """Test simple du prix ES"""
    print("🔍 Test simple prix ES...")
    
    try:
        from ib_insync import IB, Future
        
        # Connexion avec Client ID 2 (éviter le conflit)
        ib = IB()
        ib.connect('127.0.0.1', 7497, clientId=2, timeout=10)
        
        if not ib.isConnected():
            print("❌ Connexion échouée")
            return None
        
        print("✅ Connexion établie")
        print(f"   Client ID: 2")
        
        # Créer le contrat ES actuel
        contract = Future('ES', '20241220', 'CME')
        print(f"📋 Contrat ES: {contract}")
        
        # Demander le prix
        print("📊 Demande prix...")
        ib.reqMktData(contract)
        time.sleep(5)
        
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

def main():
    """Test principal"""
    print("🚀 TEST PRIX ES SIMPLE FINAL")
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("🎯 Prix réel attendu: 6481.50")
    print("📋 Client ID: 2 (évite conflit)")
    print("=" * 50)
    
    # Test simple
    prix = test_es_simple()
    
    # Résumé
    print("\n" + "=" * 50)
    print("📊 RÉSUMÉ")
    if prix:
        print(f"✅ Prix ES: {prix}")
        print("✅ MIA_IA_SYSTEM opérationnel")
        print("🎉 SUCCÈS ! Le système peut récupérer les prix ES")
    else:
        print("❌ Impossible de récupérer le prix")
        print("💡 PROBLÈME IDENTIFIÉ: Données de marché non activées dans TWS")
        print("\n🔧 SOLUTION:")
        print("1. Dans TWS, allez dans Edit > Global Configuration")
        print("2. Cliquez sur 'Market Data'")
        print("3. Vérifiez que 'Use Global Configuration' est coché")
        print("4. Dans 'Market Data Subscriptions', activez:")
        print("   - 'US Securities Snapshot and Futures Value Bundle'")
        print("   - 'US Equity and Options Add-On Streaming Bundle'")
        print("5. Cliquez sur 'OK' et redémarrez TWS")
        print("6. Relancez ce test")

if __name__ == "__main__":
    main()



