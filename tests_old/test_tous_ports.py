#!/usr/bin/env python3
"""
Test tous les ports et Client IDs - MIA_IA_SYSTEM
Test automatique de toutes les configurations possibles
"""

import time
from datetime import datetime

def test_port_client_id(port, client_id, timeout=3):
    """Test un port et Client ID spécifique"""
    try:
        from ib_insync import IB
        
        ib = IB()
        ib.connect('127.0.0.1', port, clientId=client_id, timeout=timeout)
        
        if ib.isConnected():
            print(f"✅ PORT {port} + CLIENT ID {client_id} = SUCCÈS !")
            ib.disconnect()
            return True
        else:
            ib.disconnect()
            return False
            
    except Exception as e:
        return False

def test_tous_ports():
    """Test tous les ports et Client IDs"""
    print("🚀 TEST AUTOMATIQUE - TOUS LES PORTS")
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Ports à tester
    ports = [7497, 7496, 4001, 4002]
    client_ids = [1, 2, 3, 10, 100]
    
    solutions = []
    
    for port in ports:
        print(f"\n🔍 Test port {port}...")
        
        for client_id in client_ids:
            print(f"   Test Client ID {client_id}...", end=" ")
            
            if test_port_client_id(port, client_id):
                solutions.append((port, client_id))
                print("✅")
            else:
                print("❌")
    
    # Résumé
    print("\n" + "=" * 60)
    print("📊 RÉSUMÉ DES TESTS")
    
    if solutions:
        print("🎉 SOLUTIONS TROUVÉES !")
        for port, client_id in solutions:
            print(f"✅ Port {port} + Client ID {client_id}")
        
        print("\n💡 CONFIGURATION RECOMMANDÉE:")
        port, client_id = solutions[0]
        print(f"   - Host: 127.0.0.1")
        print(f"   - Port: {port}")
        print(f"   - Client ID: {client_id}")
        
    else:
        print("❌ AUCUNE SOLUTION TROUVÉE")
        print("💡 Suivez le guide de résolution")
        print("📋 Vérifiez la configuration TWS")

if __name__ == "__main__":
    test_tous_ports()



