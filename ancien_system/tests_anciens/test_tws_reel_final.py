#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚀 TEST TWS RÉEL FINAL - MIA_IA_SYSTEM
Test connexion TWS mode réel (port 7496)
"""

import socket
import time
from datetime import datetime

def test_socket_7496():
    """Test connexion socket port 7496"""
    print("🔍 Test socket port 7496 (TWS Réel)...")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex(('127.0.0.1', 7496))
        sock.close()
        if result == 0:
            print("✅ Port 7496 accessible (TWS Réel)")
            return True
        else:
            print("❌ Port 7496 inaccessible")
            return False
    except Exception as e:
        print(f"❌ Erreur socket: {e}")
        return False

def test_ib_insync_tws_reel():
    """Test connexion ib_insync TWS réel"""
    print("🔍 Test connexion ib_insync TWS réel...")
    try:
        from ib_insync import IB
        ib = IB()
        ib.connect('127.0.0.1', 7496, clientId=1, timeout=15)
        print("✅ Connexion TWS Réel établie")
        return ib
    except Exception as e:
        print(f"❌ Erreur connexion TWS Réel: {e}")
        return None

def test_prix_es_tws_reel(ib):
    """Test prix ES via TWS réel"""
    print("🔍 Test prix ES TWS réel...")
    try:
        from ib_insync import Future
        
        # Contrat ES actuel
        contract = Future('ES', '20241220', 'CME')
        print(f"📋 Contrat ES: {contract}")
        
        # Demande prix
        ib.reqMktData(contract)
        time.sleep(5)  # Plus de temps pour les données réelles
        
        # Vérification ticker
        tickers = ib.tickers()
        for ticker in tickers:
            if ticker.contract.symbol == 'ES':
                prix = ticker.marketPrice()
                bid = ticker.bid
                ask = ticker.ask
                
                print(f"📊 Prix ES: {prix}")
                print(f"📊 Bid: {bid}")
                print(f"📊 Ask: {ask}")
                
                if prix and prix > 0:
                    print("✅ Prix ES récupéré avec succès !")
                    return True
                else:
                    print("❌ Prix ES non disponible")
                    return False
        
        print("❌ Aucun ticker ES trouvé")
        return False
        
    except Exception as e:
        print(f"❌ Erreur prix ES: {e}")
        return False

def test_compte_tws_reel(ib):
    """Test informations compte TWS réel"""
    print("🔍 Test compte TWS réel...")
    try:
        accounts = ib.managedAccounts()
        print(f"📋 Comptes: {accounts}")
        
        if accounts:
            account = accounts[0]
            print(f"📊 Compte principal: {account}")
            
            # Portfolio
            portfolio = ib.portfolio()
            print(f"📊 Positions: {len(portfolio)}")
            
            return True
        else:
            print("❌ Aucun compte trouvé")
            return False
            
    except Exception as e:
        print(f"❌ Erreur compte: {e}")
        return False

def test_connection_status(ib):
    """Test statut connexion TWS"""
    print("🔍 Test statut connexion...")
    try:
        # Vérifier si connecté
        if ib.isConnected():
            print("✅ TWS connecté")
            
            # Vérifier le serveur
            server = ib.serverVersion()
            print(f"📊 Version serveur: {server}")
            
            return True
        else:
            print("❌ TWS non connecté")
            return False
            
    except Exception as e:
        print(f"❌ Erreur statut: {e}")
        return False

def main():
    print("🚀 TEST TWS RÉEL FINAL - MIA_IA_SYSTEM")
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("🎯 Mode: RÉEL (port 7496)")
    print("=" * 50)
    
    # Test 1: Socket port 7496
    socket_ok = test_socket_7496()
    
    if not socket_ok:
        print("\n❌ TWS Réel non accessible")
        print("Vérifiez que TWS est ouvert en mode RÉEL")
        print("🔧 Configuration TWS requise:")
        print("   1. Edit > Global Configuration")
        print("   2. API > Settings > Enable ActiveX and Socket Clients")
        print("   3. API > Settings > Socket port: 7496")
        print("   4. API > Settings > Allow connections from localhost")
        return
    
    # Test 2: Connexion API
    ib = test_ib_insync_tws_reel()
    
    if ib:
        # Test 3: Statut connexion
        status_ok = test_connection_status(ib)
        
        # Test 4: Prix ES
        prix_ok = test_prix_es_tws_reel(ib)
        
        # Test 5: Compte
        compte_ok = test_compte_tws_reel(ib)
        
        # Déconnexion
        ib.disconnect()
        
        # Résumé
        print("\n" + "=" * 50)
        print("📊 RÉSUMÉ TWS RÉEL")
        print(f"Socket 7496: {'✅' if socket_ok else '❌'}")
        print(f"API: {'✅' if ib else '❌'}")
        print(f"Statut: {'✅' if status_ok else '❌'}")
        print(f"Prix ES: {'✅' if prix_ok else '❌'}")
        print(f"Compte: {'✅' if compte_ok else '❌'}")
        
        if prix_ok:
            print("\n🎉 SUCCÈS ! TWS Réel fonctionne parfaitement")
            print("📋 Configuration finale pour MIA_IA_SYSTEM:")
            print("   - Host: 127.0.0.1")
            print("   - Port: 7496")
            print("   - Client ID: 1")
            print("   - Mode: RÉEL")
        else:
            print("\n⚠️ Connexion OK mais pas de prix ES")
            print("🔧 Vérifiez les souscriptions de données de marché dans IBKR")
    else:
        print("\n❌ Impossible de se connecter à TWS Réel")
        print("🔧 Vérifiez la configuration API dans TWS")

if __name__ == "__main__":
    main()


