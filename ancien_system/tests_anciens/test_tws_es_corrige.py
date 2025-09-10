#!/usr/bin/env python3
"""
MIA_IA_SYSTEM - Test TWS ES Corrigé
Test ES avec expiry spécifié
"""

import time
from datetime import datetime

def test_tws_es_corrige():
    """Test TWS ES avec expiry"""
    print("🧪 Test TWS ES Corrigé...")
    
    try:
        from ib_insync import IB, Contract
        
        # Configuration TWS Paper Trading
        ib = IB()
        
        print("🔗 Connexion TWS Paper Trading...")
        ib.connect('127.0.0.1', 7497, clientId=1, timeout=30)
        
        if ib.isConnected():
            print("✅ TWS Paper Trading connecté !")
            
            # Test ES avec différents expiries
            expiries = ['202412', '202503', '202506', '202509', '202512']
            
            for expiry in expiries:
                print(f"\n📊 Test ES {expiry}...")
                try:
                    # Créer contrat ES avec expiry
                    contract = Contract(
                        symbol='ES',
                        secType='FUT',
                        exchange='CME',
                        currency='USD',
                        lastTradingDay=expiry  # Expiry spécifié
                    )
                    
                    # Récupérer données
                    ib.reqMktData(contract)
                    time.sleep(3)  # Attendre données
                    
                    ticker = ib.ticker(contract)
                    if ticker and ticker.marketPrice():
                        print(f"✅ ES {expiry}: {ticker.marketPrice()}")
                        print(f"   Bid: {ticker.bid}")
                        print(f"   Ask: {ticker.ask}")
                        print(f"   Volume: {ticker.volume}")
                        
                        # Arrêter après le premier succès
                        break
                    else:
                        print(f"⚠️ Pas de données pour ES {expiry}")
                        
                except Exception as e:
                    print(f"⚠️ Erreur ES {expiry}: {e}")
            
            # Test SPY (alternative)
            print("\n📊 Test SPY...")
            try:
                spy_contract = Contract(
                    symbol='SPY',
                    secType='STK',
                    exchange='SMART',
                    currency='USD'
                )
                
                ib.reqMktData(spy_contract)
                time.sleep(2)
                
                spy_ticker = ib.ticker(spy_contract)
                if spy_ticker and spy_ticker.marketPrice():
                    print(f"✅ SPY: {spy_ticker.marketPrice()}")
                    print(f"   Bid: {spy_ticker.bid}")
                    print(f"   Ask: {spy_ticker.ask}")
                else:
                    print("⚠️ Pas de données SPY")
                    
            except Exception as e:
                print(f"⚠️ Erreur SPY: {e}")
            
            # Test compte détaillé
            print("\n🏦 Test compte détaillé...")
            try:
                account = ib.accountSummary()
                for item in account:
                    if 'NetLiquidation' in item.tag:
                        print(f"   NetLiquidation: {item.value}")
                    elif 'AvailableFunds' in item.tag:
                        print(f"   AvailableFunds: {item.value}")
                    elif 'BuyingPower' in item.tag:
                        print(f"   BuyingPower: {item.value}")
                        
            except Exception as e:
                print(f"⚠️ Erreur compte: {e}")
            
            # Déconnexion
            ib.disconnect()
            print("\n✅ Test TWS ES terminé")
            return True
            
        else:
            print("❌ Échec connexion TWS")
            return False
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

if __name__ == "__main__":
    test_tws_es_corrige()
















