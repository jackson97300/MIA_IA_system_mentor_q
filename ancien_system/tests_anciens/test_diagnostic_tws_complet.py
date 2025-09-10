#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔍 DIAGNOSTIC TWS COMPLET - MIA_IA_SYSTEM
Test complet de la configuration TWS et des données de marché
"""

import socket
import time
from datetime import datetime

def test_socket_connection():
    """Test connexion socket basique"""
    print("🔍 Test connexion socket...")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex(('127.0.0.1', 7497))
        sock.close()
        if result == 0:
            print("✅ Port 7497 accessible")
            return True
        else:
            print("❌ Port 7497 inaccessible")
            return False
    except Exception as e:
        print(f"❌ Erreur socket: {e}")
        return False

def test_ib_insync_connection():
    """Test connexion ib_insync"""
    print("🔍 Test connexion ib_insync...")
    try:
        from ib_insync import IB
        ib = IB()
        ib.connect('127.0.0.1', 7497, clientId=3, timeout=10)
        print("✅ Connexion ib_insync établie")
        return ib
    except Exception as e:
        print(f"❌ Erreur ib_insync: {e}")
        return None

def test_market_data_subscriptions(ib):
    """Test des souscriptions de données de marché"""
    print("🔍 Test souscriptions données de marché...")
    try:
        # Test avec différents contrats
        from ib_insync import Future, Stock
        
        # Test ES futures
        contract_es = Future('ES', '20241220', 'CME')
        print(f"📋 Test contrat ES: {contract_es}")
        
        # Test SPY (plus simple)
        contract_spy = Stock('SPY', 'SMART', 'USD')
        print(f"📋 Test contrat SPY: {contract_spy}")
        
        # Demande données pour ES
        ib.reqMktData(contract_es)
        time.sleep(3)
        
        # Demande données pour SPY
        ib.reqMktData(contract_spy)
        time.sleep(3)
        
        # Vérification des tickers
        tickers = ib.tickers()
        print(f"📊 Nombre de tickers reçus: {len(tickers)}")
        
        for ticker in tickers:
            print(f"📊 Ticker: {ticker.contract.symbol} - Prix: {ticker.marketPrice()}")
            
        return True
        
    except Exception as e:
        print(f"❌ Erreur données de marché: {e}")
        return False

def test_historical_data(ib):
    """Test données historiques"""
    print("🔍 Test données historiques...")
    try:
        from ib_insync import Future
        contract = Future('ES', '20241220', 'CME')
        
        # Demande données historiques
        bars = ib.reqHistoricalData(
            contract,
            endDateTime='',
            durationStr='1 D',
            barSizeSetting='1 min',
            whatToShow='TRADES',
            useRTH=True
        )
        
        if bars:
            print(f"✅ Données historiques reçues: {len(bars)} barres")
            print(f"📊 Dernier prix: {bars[-1].close}")
            return True
        else:
            print("❌ Aucune donnée historique reçue")
            return False
            
    except Exception as e:
        print(f"❌ Erreur données historiques: {e}")
        return False

def test_account_info(ib):
    """Test informations compte"""
    print("🔍 Test informations compte...")
    try:
        accounts = ib.managedAccounts()
        print(f"📋 Comptes: {accounts}")
        
        if accounts:
            account = accounts[0]
            portfolio = ib.portfolio()
            print(f"📊 Portfolio: {len(portfolio)} positions")
            
            return True
        else:
            print("❌ Aucun compte trouvé")
            return False
            
    except Exception as e:
        print(f"❌ Erreur compte: {e}")
        return False

def main():
    print("🚀 DIAGNOSTIC TWS COMPLET")
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    # Test 1: Socket
    socket_ok = test_socket_connection()
    
    # Test 2: ib_insync
    ib = test_ib_insync_connection()
    
    if ib:
        # Test 3: Données de marché
        market_data_ok = test_market_data_subscriptions(ib)
        
        # Test 4: Données historiques
        historical_ok = test_historical_data(ib)
        
        # Test 5: Informations compte
        account_ok = test_account_info(ib)
        
        # Déconnexion
        ib.disconnect()
        
        # Résumé
        print("\n" + "=" * 50)
        print("📊 RÉSUMÉ DIAGNOSTIC")
        print(f"Socket: {'✅' if socket_ok else '❌'}")
        print(f"API: {'✅' if ib else '❌'}")
        print(f"Données marché: {'✅' if market_data_ok else '❌'}")
        print(f"Données historiques: {'✅' if historical_ok else '❌'}")
        print(f"Compte: {'✅' if account_ok else '❌'}")
        
        if not market_data_ok:
            print("\n🔧 SOLUTION RECOMMANDÉE:")
            print("1. Dans TWS: Edit > Global Configuration")
            print("2. API > Settings > Enable ActiveX and Socket Clients")
            print("3. Market Data > Use Global Configuration")
            print("4. Market Data > Enable streaming market data")
            print("5. Redémarrez TWS")
    else:
        print("\n❌ Impossible de se connecter à TWS")
        print("Vérifiez que TWS est ouvert et configuré pour l'API")

if __name__ == "__main__":
    main()


