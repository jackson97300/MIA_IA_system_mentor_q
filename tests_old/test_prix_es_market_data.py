#!/usr/bin/env python3
"""
Test prix ES avec activation données marché - MIA_IA_SYSTEM
Vérification et activation des données de marché dans TWS
"""

import time
from datetime import datetime

def test_es_market_data_activation():
    """Test avec activation des données de marché"""
    print("🔍 Test activation données marché...")
    
    try:
        from ib_insync import IB, Future
        
        # Connexion
        ib = IB()
        ib.connect('127.0.0.1', 7497, clientId=1, timeout=10)
        
        if not ib.isConnected():
            print("❌ Connexion échouée")
            return None
        
        print("✅ Connexion établie")
        
        # Vérifier les paramètres de connexion
        print("📋 Paramètres de connexion:")
        print(f"   Host: {ib.host}")
        print(f"   Port: {ib.port}")
        print(f"   Client ID: {ib.clientId}")
        print(f"   Connected: {ib.isConnected()}")
        
        # Créer le contrat ES actuel
        contract = Future('ES', '20241220', 'CME')  # Décembre 2024 (contrat actuel)
        contract.currency = 'USD'
        contract.multiplier = '50'
        
        print(f"📋 Contrat ES: {contract}")
        
        # Qualifier le contrat
        print("🔍 Qualification du contrat...")
        ib.qualifyContracts(contract)
        time.sleep(2)
        
        print(f"📋 Contrat qualifié: {contract}")
        
        # Demander les données de marché avec différents types
        print("📊 Demande données marché...")
        
        # Type 1: Données en temps réel
        ib.reqMktData(contract, '', False, False, [])
        time.sleep(3)
        
        ticker = ib.ticker(contract)
        if ticker and ticker.marketPrice() and not str(ticker.marketPrice()) == 'nan':
            price = ticker.marketPrice()
            print(f"💰 Prix ES (temps réel): {price}")
            
            # Comparaison
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
            print("❌ Pas de données temps réel")
            print(f"   Market Price: {ticker.marketPrice() if ticker else 'None'}")
            print(f"   Bid: {ticker.bid if ticker else 'None'}")
            print(f"   Ask: {ticker.ask if ticker else 'None'}")
        
        # Type 2: Données historiques (dernière transaction)
        print("\n📊 Demande données historiques...")
        bars = ib.reqHistoricalData(
            contract,
            '',
            '1 D',
            '1 min',
            'TRADES',
            useRTH=True,
            formatDate=1
        )
        
        if bars:
            latest_bar = bars[-1]
            price = latest_bar.close
            print(f"💰 Prix ES (historique): {price}")
            
            # Comparaison
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
            print("❌ Pas de données historiques")
        
        ib.disconnect()
        return None
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return None

def test_es_with_different_contracts():
    """Test avec différents contrats ES"""
    print("\n🔧 Test différents contrats ES...")
    
    try:
        from ib_insync import IB, Future
        
        ib = IB()
        ib.connect('127.0.0.1', 7497, clientId=1, timeout=10)
        
        if not ib.isConnected():
            print("❌ Connexion échouée")
            return
        
        print("✅ Connexion établie")
        
        # Test avec différents contrats ES
        contracts_to_test = [
            ('ES', '20241220', 'CME'),  # Décembre 2024
            ('ES', '20250117', 'CME'),  # Janvier 2025
            ('ES', '20250221', 'CME'),  # Février 2025
        ]
        
        for symbol, date, exchange in contracts_to_test:
            print(f"\n📋 Test: {symbol} {date} @{exchange}")
            
            try:
                contract = Future(symbol, date, exchange)
                contract.currency = 'USD'
                contract.multiplier = '50'
                
                # Qualifier
                ib.qualifyContracts(contract)
                time.sleep(1)
                
                print(f"   Contrat qualifié: {contract}")
                
                # Demander données
                ib.reqMktData(contract)
                time.sleep(3)
                
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
        
        print("\n❌ Aucun contrat valide trouvé")
        ib.disconnect()
        
    except Exception as e:
        print(f"❌ Erreur générale: {e}")

def check_tws_market_data_settings():
    """Guide pour vérifier les paramètres TWS"""
    print("\n🔧 GUIDE VÉRIFICATION TWS:")
    print("=" * 50)
    print("1. Ouvrez TWS")
    print("2. Allez dans Edit > Global Configuration")
    print("3. Dans l'arborescence, cliquez sur 'API > Settings'")
    print("4. Vérifiez que 'Enable ActiveX and Socket Clients' est coché")
    print("5. Vérifiez que le port 7497 est configuré")
    print("6. Allez dans 'API > Precautions'")
    print("7. Décochez 'Bypass Order Precautions for API Orders'")
    print("8. Allez dans 'Market Data'")
    print("9. Vérifiez que 'Use Global Configuration' est coché")
    print("10. Dans 'Market Data Subscriptions', vérifiez:")
    print("    - 'US Securities Snapshot and Futures Value Bundle'")
    print("    - 'US Equity and Options Add-On Streaming Bundle'")
    print("11. Cliquez sur 'OK' et redémarrez TWS")
    print("=" * 50)

def main():
    """Test principal"""
    print("🚀 TEST PRIX ES DONNÉES MARCHÉ")
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("🎯 Prix réel attendu: 6481.50")
    print("📋 Vérification données marché TWS")
    print("=" * 50)
    
    # Test 1: Activation données marché
    prix = test_es_market_data_activation()
    
    # Test 2: Différents contrats
    if not prix:
        test_es_with_different_contracts()
    
    # Guide TWS
    check_tws_market_data_settings()
    
    # Résumé
    print("\n" + "=" * 50)
    print("📊 RÉSUMÉ")
    if prix:
        print(f"✅ Prix ES: {prix}")
        print("✅ MIA_IA_SYSTEM opérationnel")
        print("🎉 SUCCÈS ! Le système peut récupérer les prix ES")
    else:
        print("❌ Impossible de récupérer le prix")
        print("💡 Problème de données de marché dans TWS")
        print("💡 Suivez le guide ci-dessus pour configurer TWS")

if __name__ == "__main__":
    main()



