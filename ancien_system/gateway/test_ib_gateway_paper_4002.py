#!/usr/bin/env python3
"""
MIA_IA_SYSTEM - Test IB Gateway Paper Trading (Port 4002)
Test spécifique pour IB Gateway en mode Paper Trading
"""

import socket
import time
from datetime import datetime

def test_port_4002():
    """Test du port 4002 (IB Gateway Paper Trading)"""
    print("🔍 Test port 4002 (IB Gateway Paper Trading)...")
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex(('127.0.0.1', 4002))
        sock.close()
        
        if result == 0:
            print("✅ Port 4002 accessible (IB Gateway Paper Trading)")
            return True
        else:
            print(f"❌ Port 4002 non accessible (code: {result})")
            return False
    except Exception as e:
        print(f"❌ Erreur test port 4002: {e}")
        return False

def test_ib_gateway_connection():
    """Test connexion IB Gateway Paper Trading"""
    print("🔧 Test connexion IB Gateway Paper Trading...")
    
    try:
        from ib_insync import IB
        
        # Test avec différents Client IDs
        for client_id in [1, 999, 1000]:
            print(f"   Test Client ID {client_id}...")
            ib = IB()
            
            try:
                # Connexion IB Gateway Paper Trading (port 4002)
                ib.connect('127.0.0.1', 4002, clientId=client_id, timeout=10)
                
                if ib.isConnected():
                    print(f"✅ Connexion IB Gateway réussie avec Client ID {client_id}")
                    
                    # Test récupération données compte
                    try:
                        account = ib.accountSummary()
                        print(f"✅ Données compte récupérées: {len(account)} éléments")
                        
                        # Afficher quelques infos
                        for item in account[:3]:
                            print(f"   - {item.tag}: {item.value}")
                            
                    except Exception as e:
                        print(f"⚠️ Erreur récupération compte: {e}")
                    
                    ib.disconnect()
                    return client_id
                else:
                    print(f"❌ Connexion échouée avec Client ID {client_id}")
                    ib.disconnect()
                    
            except Exception as e:
                print(f"❌ Erreur Client ID {client_id}: {e}")
                try:
                    ib.disconnect()
                except:
                    pass
                continue
        
        print("❌ Aucun Client ID ne fonctionne")
        return None
        
    except ImportError:
        print("❌ ib_insync non installé")
        return None
    except Exception as e:
        print(f"❌ Erreur test connexion: {e}")
        return None

def main():
    """Test principal IB Gateway Paper Trading"""
    print("🚀 MIA_IA_SYSTEM - Test IB Gateway Paper Trading")
    print("=" * 60)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Test 1: Port 4002
    port_ok = test_port_4002()
    print()
    
    if not port_ok:
        print("❌ Port 4002 non accessible")
        print("💡 Vérifiez que IB Gateway est lancé en mode Paper Trading")
        print("💡 Vérifiez la configuration IB Gateway")
        return
    
    # Test 2: Connexion IB Gateway
    working_client_id = test_ib_gateway_connection()
    
    print()
    print("=" * 60)
    print("📊 RÉSUMÉ TEST IB GATEWAY PAPER TRADING")
    print(f"Port 4002 accessible: {'✅' if port_ok else '❌'}")
    
    if working_client_id:
        print(f"Client ID fonctionnel: {working_client_id}")
        print("✅ IB Gateway Paper Trading opérationnel !")
        print("🎉 Prêt pour MIA_IA_SYSTEM !")
    else:
        print("❌ Aucun Client ID fonctionnel")
        print("💡 Vérifiez la configuration IB Gateway")
        print("💡 Redémarrez IB Gateway")

if __name__ == "__main__":
    main()
















