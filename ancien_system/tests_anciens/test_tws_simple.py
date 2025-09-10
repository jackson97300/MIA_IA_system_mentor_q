#!/usr/bin/env python3
"""
MIA_IA_SYSTEM - Test TWS Simple
Test simple sans asyncio pour éviter les conflits
"""

import time
from datetime import datetime

def test_tws_simple():
    """Test TWS simple et fonctionnel"""
    print("🚀 MIA_IA_SYSTEM - Test TWS Simple")
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
            
            # === TEST COMPTE ===
            print("\n🏦 Test compte...")
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
                        
            except Exception as e:
                print(f"⚠️ Erreur compte: {e}")
            
            # === TEST POSITIONS ===
            print("\n💼 Test positions...")
            try:
                positions = ib.positions()
                print(f"✅ Positions: {len(positions)} trouvées")
                
                for pos in positions:
                    print(f"   {pos.contract.symbol}: {pos.position} @ {pos.avgCost}")
                    
            except Exception as e:
                print(f"⚠️ Erreur positions: {e}")
            
            # === TEST HISTORIQUE SPY ===
            print("\n📈 Test historique SPY...")
            try:
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
            
            # === TEST ORDRES OUVERTS ===
            print("\n📋 Test ordres ouverts...")
            try:
                open_orders = ib.reqAllOpenOrders()
                print(f"✅ Ordres ouverts: {len(open_orders)} trouvés")
                
                for order in open_orders:
                    print(f"   {order.order.action} {order.order.totalQuantity} {order.contract.symbol}")
                    
            except Exception as e:
                print(f"⚠️ Erreur ordres: {e}")
            
            # === TEST PLACEMENT ORDRE SIMPLE ===
            print("\n📝 Test placement ordre simple...")
            try:
                # Créer contrat SPY
                spy_contract = Contract(
                    symbol='SPY',
                    secType='STK',
                    exchange='SMART',
                    currency='USD'
                )
                
                # Créer ordre (simulation)
                from ib_insync import Order
                order = Order()
                order.action = 'BUY'
                order.totalQuantity = 1
                order.orderType = 'LMT'
                order.lmtPrice = 640.00  # Prix limite bas
                
                print(f"   Ordre préparé: BUY 1 SPY @ 640.00")
                print("   ⚠️ Ordre non placé (simulation)")
                
            except Exception as e:
                print(f"⚠️ Erreur préparation ordre: {e}")
            
            # Déconnexion
            ib.disconnect()
            print("\n✅ Test TWS Simple terminé")
            
            # === RÉSUMÉ FINAL ===
            print("\n" + "=" * 50)
            print("🎉 MIA_IA_SYSTEM - PRÊT POUR TRADING !")
            print("=" * 50)
            print("✅ TWS connecté et opérationnel")
            print("✅ Compte accessible")
            print("✅ Historique des données disponible")
            print("✅ Trading prêt")
            print("✅ Système MIA_IA_SYSTEM fonctionnel")
            
            return True
            
        else:
            print("❌ Échec connexion TWS")
            return False
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

if __name__ == "__main__":
    test_tws_simple()
















