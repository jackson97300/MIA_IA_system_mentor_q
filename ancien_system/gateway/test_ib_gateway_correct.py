#!/usr/bin/env python3
"""
MIA_IA_SYSTEM - Test IB Gateway/TWS Correct
Test adapté pour IB Gateway et TWS Paper Trading
"""

import socket
import time
from datetime import datetime

def test_ports():
    """Test des ports IBKR"""
    print("🔍 Test des ports IBKR...")
    
    ports_to_test = [
        (4001, "IB Gateway Live"),
        (4002, "IB Gateway Paper"), 
        (7496, "TWS Live"),
        (7497, "TWS Paper")
    ]
    
    available_ports = []
    
    for port, description in ports_to_test:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(3)
            result = sock.connect_ex(('127.0.0.1', port))
            sock.close()
            
            if result == 0:
                print(f"✅ Port {port} accessible ({description})")
                available_ports.append((port, description))
            else:
                print(f"❌ Port {port} non accessible ({description})")
                
        except Exception as e:
            print(f"❌ Erreur test port {port}: {e}")
    
    return available_ports

def test_ibkr_connection(port, description):
    """Test connexion IBKR sur port spécifique"""
    print(f"🔧 Test connexion {description} (port {port})...")
    
    try:
        from ib_insync import IB
        
        # Test avec différents Client IDs
        for client_id in [1, 999, 1000, 2]:
            print(f"   Test Client ID {client_id}...")
            ib = IB()
            
            try:
                ib.connect('127.0.0.1', port, clientId=client_id, timeout=10)
                
                if ib.isConnected():
                    print(f"✅ Connexion {description} réussie avec Client ID {client_id}")
                    
                    # Test récupération données compte
                    try:
                        account = ib.accountSummary()
                        print(f"✅ Données compte récupérées: {len(account)} éléments")
                        
                        # Afficher infos importantes
                        for item in account:
                            if item.tag in ['NetLiquidation', 'EquityWithLoanValue', 'AvailableFunds']:
                                print(f"   - {item.tag}: {item.value} {item.currency}")
                                
                    except Exception as e:
                        print(f"⚠️ Erreur récupération compte: {e}")
                    
                    # Test récupération contrats
                    try:
                        contracts = ib.reqContractDetails(Contract(symbol='ES', secType='FUT', exchange='CME'))
                        print(f"✅ Contrats ES trouvés: {len(contracts)}")
                    except Exception as e:
                        print(f"⚠️ Erreur récupération contrats: {e}")
                    
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
        
        print(f"❌ Aucun Client ID ne fonctionne pour {description}")
        return None
        
    except ImportError:
        print("❌ ib_insync non installé")
        return None
    except Exception as e:
        print(f"❌ Erreur test connexion: {e}")
        return None

def main():
    """Test principal IBKR"""
    print("🚀 MIA_IA_SYSTEM - Test IBKR Gateway/TWS")
    print("=" * 60)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Test 1: Ports disponibles
    available_ports = test_ports()
    print()
    
    if not available_ports:
        print("❌ Aucun port IBKR accessible")
        print("💡 Vérifiez que IB Gateway ou TWS est lancé")
        return
    
    # Test 2: Connexions sur ports disponibles
    working_connections = []
    
    for port, description in available_ports:
        working_client_id = test_ibkr_connection(port, description)
        if working_client_id:
            working_connections.append((port, description, working_client_id))
        print()
    
    print("=" * 60)
    print("📊 RÉSUMÉ TEST IBKR")
    print(f"Ports disponibles: {len(available_ports)}")
    
    if working_connections:
        print("✅ Connexions fonctionnelles:")
        for port, description, client_id in working_connections:
            print(f"   - {description} (port {port}, Client ID {client_id})")
        print("🎉 IBKR opérationnel pour MIA_IA_SYSTEM !")
    else:
        print("❌ Aucune connexion fonctionnelle")
        print("💡 Vérifiez la configuration IB Gateway/TWS")
        print("💡 Vérifiez les permissions API")

if __name__ == "__main__":
    main()
















