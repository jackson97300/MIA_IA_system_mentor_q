#!/usr/bin/env python3
"""
MIA_IA_SYSTEM - Test TWS Complet
Test avec données de marché IBKR activées
"""

import time
from datetime import datetime

def test_tws_complet():
    """Test TWS complet avec données activées"""
    print("🚀 MIA_IA_SYSTEM - Test TWS Complet")
    print("=" * 50)
    
    try:
        from ib_insync import IB, Contract
        
        # Configuration TWS Paper Trading
        ib = IB()
        
        print("🔗 Connexion TWS Paper Trading...")
        print("   Host: 127.0.0.1")
        print("   Port: 7497 (TWS Paper)")
        print("   Client ID: 1")
        
        # Connexion
        ib.connect('127.0.0.1', 7497, clientId=1, timeout=30)
        
        if ib.isConnected():
            print("✅ TWS Paper Trading connecté !")
            
            # === TEST DONNÉES ES (FUTURES) ===
            print("\n📊 Test données ES (Futures)...")
            try:
                # Contrat ES avec expiry correct
                contract = Contract(
                    symbol='ES',
                    secType='FUT',
                    exchange='CME',
                    currency='USD',
                    lastTradingDay='202412'  # Décembre 2024
                )
                
                # Récupérer données
                ib.reqMktData(contract)
                time.sleep(3)  # Attendre données
                
                ticker = ib.ticker(contract)
                if ticker and ticker.marketPrice():
                    print(f"✅ ES Dec 2024: {ticker.marketPrice()}")
                    print(f"   Bid: {ticker.bid}")
                    print(f"   Ask: {ticker.ask}")
                    print(f"   Volume: {ticker.volume}")
                else:
                    print("⚠️ Pas de données ES (essayer autres expiries)")
                    
                    # Essayer autres expiries
                    expiries = ['202503', '202506', '202509']
                    for expiry in expiries:
                        contract.lastTradingDay = expiry
                        ib.reqMktData(contract)
                        time.sleep(2)
                        
                        ticker = ib.ticker(contract)
                        if ticker and ticker.marketPrice():
                            print(f"✅ ES {expiry}: {ticker.marketPrice()}")
                            break
                    
            except Exception as e:
                print(f"⚠️ Erreur ES: {e}")
            
            # === TEST DONNÉES SPY (ACTIONS) ===
            print("\n📊 Test données SPY (Actions)...")
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
                    print(f"   Volume: {spy_ticker.volume}")
                else:
                    print("⚠️ Pas de données SPY")
                    
            except Exception as e:
                print(f"⚠️ Erreur SPY: {e}")
            
            # === TEST COMPTE DÉTAILLÉ ===
            print("\n🏦 Test compte détaillé...")
            try:
                account = ib.accountSummary()
                print(f"✅ Compte: {len(account)} éléments")
                
                for item in account:
                    if 'NetLiquidation' in item.tag:
                        print(f"   NetLiquidation: {item.value}")
                    elif 'AvailableFunds' in item.tag:
                        print(f"   AvailableFunds: {item.value}")
                    elif 'BuyingPower' in item.tag:
                        print(f"   BuyingPower: {item.value}")
                    elif 'TotalCashValue' in item.tag:
                        print(f"   TotalCash: {item.value}")
                        
            except Exception as e:
                print(f"⚠️ Erreur compte: {e}")
            
            # === TEST POSITIONS ===
            print("\n💼 Test positions...")
            try:
                positions = ib.positions()
                print(f"✅ Positions: {len(positions)} trouvées")
                
                for pos in positions:
                    print(f"   {pos.contract.symbol}: {pos.position} @ {pos.avgCost}")
                    print(f"     Market Value: {pos.marketValue}")
                    print(f"     Unrealized PnL: {pos.unrealizedPnL}")
                    
            except Exception as e:
                print(f"⚠️ Erreur positions: {e}")
            
            # === TEST ORDRES OUVERTS ===
            print("\n📋 Test ordres ouverts...")
            try:
                open_orders = ib.reqAllOpenOrders()
                print(f"✅ Ordres ouverts: {len(open_orders)} trouvés")
                
                for order in open_orders:
                    print(f"   {order.order.action} {order.order.totalQuantity} {order.contract.symbol}")
                    
            except Exception as e:
                print(f"⚠️ Erreur ordres: {e}")
            
            # === TEST HISTORIQUE ===
            print("\n📈 Test historique...")
            try:
                # Historique SPY (plus simple)
                spy_contract = Contract(
                    symbol='SPY',
                    secType='STK',
                    exchange='SMART',
                    currency='USD'
                )
                
                # Données 1 jour, 1 minute
                bars = ib.reqHistoricalData(
                    spy_contract,
                    '',
                    '1 D',
                    '1 min',
                    'TRADES',
                    useRTH=True
                )
                
                if bars:
                    print(f"✅ Historique SPY: {len(bars)} barres")
                    latest = bars[-1]
                    print(f"   Dernière: {latest.date} - Close: {latest.close}")
                else:
                    print("⚠️ Pas d'historique disponible")
                    
            except Exception as e:
                print(f"⚠️ Erreur historique: {e}")
            
            # Déconnexion
            ib.disconnect()
            print("\n✅ Test TWS complet terminé")
            return True
            
        else:
            print("❌ Échec connexion TWS")
            return False
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

if __name__ == "__main__":
    test_tws_complet()
















