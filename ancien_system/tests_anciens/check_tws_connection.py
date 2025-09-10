#!/usr/bin/env python3
"""
Vérifier la connexion TWS/Gateway
"""

import socket
import subprocess
import time

def check_port(host, port):
    """Vérifier si un port est ouvert"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except:
        return False

def check_tws_status():
    """Vérifier le statut TWS/Gateway"""
    
    print("🔍 Vérification TWS/Gateway")
    print("=" * 40)
    
    # Vérifier les ports
    ports_to_check = [
        (7497, "TWS Paper Trading"),
        (7496, "TWS Live Trading"), 
        (4001, "Gateway Paper Trading"),
        (4002, "Gateway Live Trading"),
        (5000, "Client Portal Gateway BETA")
    ]
    
    active_ports = []
    
    for port, description in ports_to_check:
        if check_port('localhost', port):
            print(f"✅ Port {port} ouvert - {description}")
            active_ports.append((port, description))
        else:
            print(f"❌ Port {port} fermé - {description}")
    
    print(f"\n📊 Résumé:")
    print(f"   Ports actifs: {len(active_ports)}")
    
    if active_ports:
        print("   Ports disponibles:")
        for port, desc in active_ports:
            print(f"     - {port}: {desc}")
    else:
        print("   ❌ Aucun port actif")
        print("   💡 Démarrez TWS ou Gateway")
    
    return active_ports

def check_processes():
    """Vérifier les processus IBKR"""
    
    print("\n🔍 Vérification processus IBKR")
    print("=" * 40)
    
    # Chercher les processus Java (TWS/Gateway)
    try:
        result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq java.exe'], 
                              capture_output=True, text=True, shell=True)
        
        if 'java.exe' in result.stdout:
            print("✅ Processus Java détecté (TWS/Gateway possible)")
            lines = result.stdout.strip().split('\n')
            for line in lines:
                if 'java.exe' in line:
                    print(f"   {line}")
        else:
            print("❌ Aucun processus Java détecté")
            
    except Exception as e:
        print(f"❌ Erreur vérification processus: {e}")

def main():
    """Fonction principale"""
    
    print("🚀 Diagnostic TWS/Gateway")
    print("=" * 50)
    
    # Vérifier ports
    active_ports = check_tws_status()
    
    # Vérifier processus
    check_processes()
    
    print("\n💡 Recommandations:")
    
    if not active_ports:
        print("   1. Démarrez TWS ou Gateway")
        print("   2. Vérifiez la configuration API")
        print("   3. Activez 'Enable ActiveX and Socket Clients'")
    else:
        print("   1. TWS/Gateway semble actif")
        print("   2. Testez la connexion avec ib-insync")
        print("   3. Vérifiez les permissions market data")
    
    print("\n🔧 Prochaines étapes:")
    print("   1. Si TWS actif: python test_ib_insync_es.py")
    print("   2. Si Gateway BETA: python debug_es_price_format.py")

if __name__ == "__main__":
    main()

