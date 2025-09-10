#!/usr/bin/env python3
"""
MIA_IA_SYSTEM - Test TWS Paper Trading Final
Test avec TWS relancé en mode Paper Trading
"""

import asyncio
import time
from datetime import datetime

def test_tws_paper_connection():
    """Test connexion TWS Paper Trading"""
    print("🧪 Test TWS Paper Trading...")
    
    try:
        from ib_insync import IB, Contract, Stock
        
        # Configuration TWS Paper Trading
        ib = IB()
        
        print("🔗 Connexion TWS Paper Trading...")
        print("   Host: 127.0.0.1")
        print("   Port: 7497 (TWS Paper)")
        print("   Client ID: 1")
        
        # Connexion avec timeout plus long
        ib.connect('127.0.0.1', 7497, clientId=1, timeout=30)
        
        if ib.isConnected():
            print("✅ TWS Paper Trading connecté !")
            
            # Test données ES
            print("\n📊 Test données ES...")
            try:
                # Créer contrat ES
                contract = Contract(
                    symbol='ES',
                    secType='FUT',
                    exchange='CME',
                    currency='USD'
                )
                
                # Récupérer données
                ib.reqMktData(contract)
                time.sleep(2)  # Attendre données
                
                ticker = ib.ticker(contract)
                if ticker and ticker.marketPrice():
                    print(f"✅ ES Prix: {ticker.marketPrice()}")
                    print(f"   Bid: {ticker.bid}")
                    print(f"   Ask: {ticker.ask}")
                    print(f"   Volume: {ticker.volume}")
                else:
                    print("⚠️ Pas de données ES disponibles")
                    
            except Exception as e:
                print(f"⚠️ Erreur données ES: {e}")
            
            # Test positions
            print("\n💼 Test positions...")
            try:
                positions = ib.positions()
                print(f"✅ Positions: {len(positions)} trouvées")
                for pos in positions:
                    print(f"   {pos.contract.symbol}: {pos.position}")
            except Exception as e:
                print(f"⚠️ Erreur positions: {e}")
            
            # Test compte
            print("\n🏦 Test compte...")
            try:
                account = ib.accountSummary()
                print(f"✅ Compte: {len(account)} éléments")
                for item in account:
                    if 'NetLiquidation' in item.tag:
                        print(f"   NetLiquidation: {item.value}")
            except Exception as e:
                print(f"⚠️ Erreur compte: {e}")
            
            # Déconnexion
            ib.disconnect()
            print("\n✅ Test TWS Paper Trading terminé")
            return True
            
        else:
            print("❌ Échec connexion TWS Paper Trading")
            return False
            
    except Exception as e:
        print(f"❌ Erreur TWS: {e}")
        return False

def test_ib_gateway_paper():
    """Test IB Gateway Paper Trading"""
    print("\n🧪 Test IB Gateway Paper Trading...")
    
    try:
        from ib_insync import IB, Contract
        
        # Configuration IB Gateway Paper
        ib = IB()
        
        print("🔗 Connexion IB Gateway Paper...")
        print("   Host: 127.0.0.1")
        print("   Port: 4002 (IB Gateway Paper)")
        print("   Client ID: 2")
        
        # Connexion
        ib.connect('127.0.0.1', 4002, clientId=2, timeout=30)
        
        if ib.isConnected():
            print("✅ IB Gateway Paper connecté !")
            
            # Test données ES
            print("\n📊 Test données ES...")
            try:
                contract = Contract(
                    symbol='ES',
                    secType='FUT',
                    exchange='CME',
                    currency='USD'
                )
                
                ib.reqMktData(contract)
                time.sleep(2)
                
                ticker = ib.ticker(contract)
                if ticker and ticker.marketPrice():
                    print(f"✅ ES Prix: {ticker.marketPrice()}")
                else:
                    print("⚠️ Pas de données ES")
                    
            except Exception as e:
                print(f"⚠️ Erreur données ES: {e}")
            
            ib.disconnect()
            print("✅ Test IB Gateway Paper terminé")
            return True
            
        else:
            print("❌ Échec connexion IB Gateway Paper")
            return False
            
    except Exception as e:
        print(f"❌ Erreur IB Gateway: {e}")
        return False

def main():
    """Test principal"""
    print("🚀 MIA_IA_SYSTEM - Test Connexions IBKR")
    print("=" * 50)
    
    # Test TWS Paper
    tws_success = test_tws_paper_connection()
    
    # Test IB Gateway Paper
    gateway_success = test_ib_gateway_paper()
    
    # Résumé
    print("\n" + "=" * 50)
    print("📋 RÉSUMÉ DES TESTS")
    print("=" * 50)
    print(f"TWS Paper Trading: {'✅ SUCCÈS' if tws_success else '❌ ÉCHEC'}")
    print(f"IB Gateway Paper: {'✅ SUCCÈS' if gateway_success else '❌ ÉCHEC'}")
    
    if tws_success or gateway_success:
        print("\n🎉 Au moins une connexion fonctionne !")
        if tws_success:
            print("💡 Recommandation: Utiliser TWS Paper Trading")
        else:
            print("💡 Recommandation: Utiliser IB Gateway Paper")
    else:
        print("\n⚠️ Aucune connexion ne fonctionne")
        print("🔧 Vérifiez que TWS/IB Gateway est bien lancé")

if __name__ == "__main__":
    main()
















