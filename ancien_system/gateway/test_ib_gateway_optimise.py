#!/usr/bin/env python3
"""
Test IB Gateway optimisé pour Paper Trading
"""

import socket
import time
from datetime import datetime

def test_ib_gateway_connection():
    """Test connexion IB Gateway avec paramètres optimisés"""
    print("🔧 Test IB Gateway optimisé...")
    
    try:
        from ib_insync import IB
        
        # Test avec différents paramètres
        test_configs = [
            {"port": 4002, "client_id": 999, "timeout": 60},
            {"port": 4002, "client_id": 1000, "timeout": 60},
            {"port": 4002, "client_id": 2, "timeout": 60},
            {"port": 4002, "client_id": 1, "timeout": 120}
        ]
        
        for config in test_configs:
            print(f"\n   Test: Port {config['port']}, Client ID {config['client_id']}, Timeout {config['timeout']}s")
            
            ib = IB()
            
            try:
                # Connexion avec paramètres optimisés
                ib.connect(
                    '127.0.0.1', 
                    config['port'], 
                    clientId=config['client_id'], 
                    timeout=config['timeout']
                )
                
                if ib.isConnected():
                    print(f"✅ Connexion réussie !")
                    
                    # Test rapide
                    try:
                        account = ib.accountSummary()
                        print(f"✅ Compte: {len(account)} éléments")
                        
                        # Afficher solde
                        for item in account:
                            if item.tag == 'NetLiquidation':
                                print(f"   - NetLiquidation: {item.value} {item.currency}")
                                break
                                
                    except Exception as e:
                        print(f"⚠️ Erreur compte: {e}")
                    
                    ib.disconnect()
                    return config
                else:
                    print("❌ Connexion échouée")
                    ib.disconnect()
                    
            except Exception as e:
                print(f"❌ Erreur: {e}")
                try:
                    ib.disconnect()
                except:
                    pass
                continue
        
        print("\n❌ Aucune configuration ne fonctionne")
        return None
        
    except ImportError:
        print("❌ ib_insync non installé")
        return None

if __name__ == "__main__":
    print("🚀 Test IB Gateway Optimisé")
    print("=" * 50)
    result = test_ib_gateway_connection()
    
    if result:
        print(f"\n🎉 Configuration fonctionnelle trouvée !")
        print(f"   Port: {result['port']}")
        print(f"   Client ID: {result['client_id']}")
        print(f"   Timeout: {result['timeout']}s")
    else:
        print("\n❌ Aucune configuration fonctionnelle")
