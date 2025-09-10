#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔧 DIAGNOSTIC IB GATEWAY CONFIG - MIA_IA_SYSTEM
Test configuration API IB Gateway
"""

import socket
import time
from datetime import datetime

def test_all_ports():
    """Test tous les ports IB Gateway possibles"""
    print("🔍 Test tous les ports IB Gateway...")
    
    ports = [
        (4001, "IB Gateway Réel"),
        (4002, "IB Gateway Paper"),
        (7496, "TWS Réel"),
        (7497, "TWS Paper")
    ]
    
    results = {}
    
    for port, description in ports:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(3)
            result = sock.connect_ex(('127.0.0.1', port))
            sock.close()
            
            if result == 0:
                print(f"✅ Port {port} accessible - {description}")
                results[port] = True
            else:
                print(f"❌ Port {port} inaccessible - {description}")
                results[port] = False
                
        except Exception as e:
            print(f"❌ Erreur port {port}: {e}")
            results[port] = False
    
    return results

def test_ib_insync_ports(accessible_ports):
    """Test connexion ib_insync sur les ports accessibles"""
    print("\n🔍 Test connexion ib_insync...")
    
    for port in accessible_ports:
        print(f"\n📋 Test port {port}...")
        try:
            from ib_insync import IB
            ib = IB()
            
            # Test avec différents Client IDs
            for client_id in [1, 2, 3, 10]:
                try:
                    print(f"   🔗 Tentative Client ID {client_id}...")
                    ib.connect('127.0.0.1', port, clientId=client_id, timeout=5)
                    
                    if ib.isConnected():
                        print(f"   ✅ Connexion réussie - Port {port}, Client ID {client_id}")
                        
                        # Test rapide prix ES
                        try:
                            from ib_insync import Future
                            contract = Future('ES', '20241220', 'CME')
                            ib.reqMktData(contract)
                            time.sleep(2)
                            
                            tickers = ib.tickers()
                            for ticker in tickers:
                                if ticker.contract.symbol == 'ES':
                                    prix = ticker.marketPrice()
                                    if prix and prix > 0:
                                        print(f"   💰 Prix ES: {prix}")
                                        print(f"   🎉 SUCCÈS COMPLET !")
                                        ib.disconnect()
                                        return port, client_id, True
                                    else:
                                        print(f"   ❌ Prix ES: {prix}")
                        except Exception as e:
                            print(f"   ⚠️ Erreur prix ES: {e}")
                        
                        ib.disconnect()
                        return port, client_id, False
                    else:
                        print(f"   ❌ Connexion échouée")
                        ib.disconnect()
                        
                except Exception as e:
                    print(f"   ❌ Erreur Client ID {client_id}: {e}")
                    try:
                        ib.disconnect()
                    except:
                        pass
                        
        except Exception as e:
            print(f"   ❌ Erreur port {port}: {e}")
    
    return None, None, False

def main():
    print("🚀 DIAGNOSTIC IB GATEWAY CONFIG")
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    # Test 1: Tous les ports
    port_results = test_all_ports()
    accessible_ports = [port for port, accessible in port_results.items() if accessible]
    
    if not accessible_ports:
        print("\n❌ Aucun port accessible")
        print("Vérifiez qu'IB Gateway ou TWS est ouvert")
        return
    
    print(f"\n📊 Ports accessibles: {accessible_ports}")
    
    # Test 2: Connexion API
    port, client_id, prix_ok = test_ib_insync_ports(accessible_ports)
    
    # Résumé
    print("\n" + "=" * 50)
    print("📊 RÉSUMÉ DIAGNOSTIC")
    
    if port and client_id:
        print(f"✅ Connexion API: Port {port}, Client ID {client_id}")
        print(f"💰 Prix ES: {'✅' if prix_ok else '❌'}")
        
        if prix_ok:
            print("\n🎉 CONFIGURATION OPTIMALE TROUVÉE !")
            print("📋 Configuration pour MIA_IA_SYSTEM:")
            print(f"   - Host: 127.0.0.1")
            print(f"   - Port: {port}")
            print(f"   - Client ID: {client_id}")
            print(f"   - Mode: {'RÉEL' if port in [4001, 7496] else 'PAPER'}")
        else:
            print("\n⚠️ Connexion OK mais pas de prix ES")
            print("🔧 Vérifiez les souscriptions de données de marché")
    else:
        print("❌ Aucune connexion API réussie")
        print("🔧 Vérifiez la configuration API dans IB Gateway/TWS")

if __name__ == "__main__":
    main()


