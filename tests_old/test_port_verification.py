#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔍 VÉRIFICATION PORT - MIA_IA_SYSTEM
Test rapide pour identifier quel port est utilisé
"""

import socket
from datetime import datetime

def test_port(port, description):
    """Test un port spécifique"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        result = sock.connect_ex(('127.0.0.1', port))
        sock.close()
        
        if result == 0:
            print(f"✅ Port {port} accessible - {description}")
            return True
        else:
            print(f"❌ Port {port} inaccessible - {description}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur port {port}: {e}")
        return False

def main():
    print("🔍 VÉRIFICATION PORT - MIA_IA_SYSTEM")
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    # Test tous les ports possibles
    ports = [
        (4001, "IB Gateway Réel"),
        (4002, "IB Gateway Paper"),
        (7496, "TWS Réel"),
        (7497, "TWS Paper")
    ]
    
    accessible_ports = []
    
    for port, description in ports:
        if test_port(port, description):
            accessible_ports.append((port, description))
    
    print("\n" + "=" * 50)
    print("📊 RÉSUMÉ")
    
    if accessible_ports:
        print(f"✅ Ports accessibles: {len(accessible_ports)}")
        for port, description in accessible_ports:
            print(f"   - Port {port}: {description}")
        
        # Recommandation
        if len(accessible_ports) == 1:
            port, description = accessible_ports[0]
            print(f"\n🎯 RECOMMANDATION: Utilisez le port {port} ({description})")
        else:
            print(f"\n⚠️ Plusieurs ports accessibles, choisissez celui qui correspond à votre configuration")
    else:
        print("❌ Aucun port accessible")
        print("Vérifiez qu'IB Gateway ou TWS est ouvert")

if __name__ == "__main__":
    main()


