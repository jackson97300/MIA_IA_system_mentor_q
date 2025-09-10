#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚀 TEST IB GATEWAY RÉEL - MIA_IA_SYSTEM
Test connexion IB Gateway mode réel (port 4001)
"""

import socket
import time
from datetime import datetime

def test_socket_4001():
    """Test connexion socket port 4001"""
    print("🔍 Test socket port 4001 (IB Gateway Réel)...")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex(('127.0.0.1', 4001))
        sock.close()
        if result == 0:
            print("✅ Port 4001 accessible (IB Gateway Réel)")
            return True
        else:
            print("❌ Port 4001 inaccessible")
            return False
    except Exception as e:
        print(f"❌ Erreur socket: {e}")
        return False

def test_ib_insync_gateway_reel():
    """Test connexion ib_insync IB Gateway réel"""
    print("🔍 Test connexion ib_insync IB Gateway réel...")
    try:
        from ib_insync import IB
        ib = IB()
        ib.connect('127.0.0.1', 4001, clientId=1, timeout=10)
        print("✅ Connexion IB Gateway Réel établie")
        return ib
    except Exception as e:
        print(f"❌ Erreur connexion IB Gateway Réel: {e}")
        return None

def test_prix_es_gateway_reel(ib):
    """Test prix ES via IB Gateway réel"""
    print("🔍 Test prix ES IB Gateway réel...")
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

def test_compte_gateway_reel(ib):
    """Test informations compte IB Gateway réel"""
    print("🔍 Test compte IB Gateway réel...")
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
    """Test statut connexion IB Gateway"""
    print("🔍 Test statut connexion...")
    try:
        # Vérifier si connecté
        if ib.isConnected():
            print("✅ IB Gateway connecté")
            
            # Vérifier le serveur
            server = ib.serverVersion()
            print(f"📊 Version serveur: {server}")
            
            # Vérifier l'heure du serveur
            server_time = ib.reqCurrentTime()
            print(f"📊 Heure serveur: {server_time}")
            
            return True
        else:
            print("❌ IB Gateway non connecté")
            return False
            
    except Exception as e:
        print(f"❌ Erreur statut: {e}")
        return False

def main():
    print("🚀 TEST IB GATEWAY RÉEL - MIA_IA_SYSTEM")
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("🎯 Mode: RÉEL (port 4001)")
    print("=" * 50)
    
    # Test 1: Socket port 4001
    socket_ok = test_socket_4001()
    
    if not socket_ok:
        print("\n❌ IB Gateway Réel non accessible")
        print("Vérifiez que IB Gateway est ouvert en mode RÉEL")
        return
    
    # Test 2: Connexion API
    ib = test_ib_insync_gateway_reel()
    
    if ib:
        # Test 3: Statut connexion
        status_ok = test_connection_status(ib)
        
        # Test 4: Prix ES
        prix_ok = test_prix_es_gateway_reel(ib)
        
        # Test 5: Compte
        compte_ok = test_compte_gateway_reel(ib)
        
        # Déconnexion
        ib.disconnect()
        
        # Résumé
        print("\n" + "=" * 50)
        print("📊 RÉSUMÉ IB GATEWAY RÉEL")
        print(f"Socket 4001: {'✅' if socket_ok else '❌'}")
        print(f"API: {'✅' if ib else '❌'}")
        print(f"Statut: {'✅' if status_ok else '❌'}")
        print(f"Prix ES: {'✅' if prix_ok else '❌'}")
        print(f"Compte: {'✅' if compte_ok else '❌'}")
        
        if prix_ok:
            print("\n🎉 SUCCÈS ! IB Gateway Réel fonctionne parfaitement")
            print("💡 Le problème était en mode Paper Trading")
            print("📋 Configuration finale pour MIA_IA_SYSTEM:")
            print("   - Host: 127.0.0.1")
            print("   - Port: 4001")
            print("   - Client ID: 1")
            print("   - Mode: RÉEL")
        else:
            print("\n❌ Problème persiste même en mode réel")
            print("🔧 Vérifiez la configuration IB Gateway")
    else:
        print("\n❌ Impossible de se connecter à IB Gateway Réel")
        print("Vérifiez que IB Gateway est ouvert et configuré")

if __name__ == "__main__":
    main()


