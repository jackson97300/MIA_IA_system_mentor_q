#!/usr/bin/env python3
"""
Test prix ES actuel - MIA_IA_SYSTEM
Vérification du prix ES vs réalité (6481.50)
"""

import time
from datetime import datetime

def test_es_current_contract():
    """Test avec le contrat ES actuel"""
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
        
        # Test avec différentes dates de contrat ES
        dates_contrat = [
            '20241220',  # Décembre 2024
            '20250117',  # Janvier 2025
            '20250221',  # Février 2025
            '20250321',  # Mars 2025
            '20250418',  # Avril 2025
            '20250516',  # Mai 2025
            '20250620',  # Juin 2025
        ]
        
        for date_contrat in dates_contrat:
            print(f"\n📋 Test contrat ES {date_contrat}...")
            
            try:
                # Créer le contrat
                contract = Future('ES', date_contrat, 'CME')
                print(f"   Contrat: {contract}")
                
                # Demander le prix
                ib.reqMktData(contract)
                time.sleep(2)
                
                # Récupérer le ticker
                ticker = ib.ticker(contract)
                
                if ticker and ticker.marketPrice() and not str(ticker.marketPrice()) == 'nan':
                    price = ticker.marketPrice()
                    print(f"   ✅ Prix ES {date_contrat}: {price}")
                    
                    # Comparaison avec la réalité
                    prix_reel = 6481.50
                    diff = abs(price - prix_reel)
                    pct = (diff / prix_reel) * 100
                    
                    print(f"   🎯 Prix réel: {prix_reel}")
                    print(f"   📈 Différence: {diff:.2f}")
                    print(f"   📊 Pourcentage: {pct:.3f}%")
                    
                    if pct < 1.0:
                        print(f"   ✅ Prix cohérent pour {date_contrat}")
                        ib.disconnect()
                        return price, date_contrat
                    else:
                        print(f"   ⚠️ Prix différent pour {date_contrat}")
                else:
                    print(f"   ❌ Pas de prix pour {date_contrat}")
                    
            except Exception as e:
                print(f"   ❌ Erreur {date_contrat}: {e}")
                continue
        
        print("\n❌ Aucun contrat ES valide trouvé")
        ib.disconnect()
        return None, None
        
    except Exception as e:
        print(f"❌ Erreur générale: {e}")
        return None, None

def test_es_front_month():
    """Test avec le front month (contrat le plus proche)"""
    print("\n🔧 Test front month...")
    
    try:
        from ib_insync import IB, Future
        
        ib = IB()
        ib.connect('127.0.0.1', 7497, clientId=1, timeout=10)
        
        if not ib.isConnected():
            print("❌ Connexion échouée")
            return
        
        print("✅ Connexion établie")
        
        # Essayer avec ES sans date (front month)
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

def main():
    """Test principal"""
    print("🚀 TEST PRIX ES ACTUEL")
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("🎯 Prix réel attendu: 6481.50")
    print("=" * 50)
    
    # Test 1: Contrats avec dates
    prix, date_contrat = test_es_current_contract()
    
    # Test 2: Front month
    test_es_front_month()
    
    # Résumé
    print("\n" + "=" * 50)
    print("📊 RÉSUMÉ")
    if prix and date_contrat:
        print(f"✅ Prix ES {date_contrat}: {prix}")
        print("✅ MIA_IA_SYSTEM opérationnel")
    else:
        print("❌ Impossible de récupérer le prix")
        print("💡 Problème de données de marché")

if __name__ == "__main__":
    main()



