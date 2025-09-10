#!/usr/bin/env python3
"""
MIA_IA_SYSTEM - Vérification IBKR Urgence
Diagnostic et correction connexion IBKR
"""

import os
import sys
import socket
import time
from datetime import datetime

# Ajouter le répertoire racine au path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def verifier_ibkr_urgence():
    """Vérification d'urgence IBKR"""
    
    print("MIA_IA_SYSTEM - VÉRIFICATION IBKR URGENCE")
    print("=" * 60)
    print("🔧 Diagnostic et correction connexion IBKR")
    print("🎯 Objectif: Résoudre timeout connexion")
    print("=" * 60)
    
    # 1. VÉRIFICATION PORTS
    print("\n📊 1. VÉRIFICATION PORTS")
    print("=" * 40)
    
    ports_to_test = [
        (7497, "TWS"),
        (4002, "Gateway"),
        (4001, "Gateway Paper"),
        (7496, "TWS Paper")
    ]
    
    active_ports = []
    
    for port, name in ports_to_test:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(3)
            result = sock.connect_ex(('127.0.0.1', port))
            sock.close()
            
            if result == 0:
                print(f"✅ {name} actif (port {port})")
                active_ports.append((port, name))
            else:
                print(f"❌ {name} inactif (port {port})")
                
        except Exception as e:
            print(f"❌ Erreur test {name}: {e}")
    
    # 2. RECOMMANDATIONS
    print("\n💡 2. RECOMMANDATIONS")
    print("=" * 40)
    
    if not active_ports:
        print("❌ AUCUN PORT ACTIF DÉTECTÉ")
        print("\n🔧 ACTIONS REQUISES:")
        print("1. Démarrer TWS ou Gateway")
        print("2. Activer l'API dans les paramètres")
        print("3. Vérifier les permissions")
        print("4. Redémarrer l'application")
        
        print("\n📋 CHECKLIST:")
        print("□ TWS/Gateway démarré")
        print("□ API activée (Global Configuration)")
        print("□ Socket clients activés")
        print("□ Ports ouverts (7497/4002)")
        print("□ Firewall désactivé")
        
    elif len(active_ports) == 1:
        port, name = active_ports[0]
        print(f"✅ {name} détecté sur port {port}")
        print(f"🎯 Utiliser port {port} pour la connexion")
        
        # Configuration recommandée
        print(f"\n🔧 CONFIGURATION RECOMMANDÉE:")
        print(f"Host: 127.0.0.1")
        print(f"Port: {port}")
        print(f"Client ID: 1")
        
    else:
        print("⚠️ MULTIPLES PORTS ACTIFS")
        for port, name in active_ports:
            print(f"   - {name}: {port}")
        
        print("\n🎯 RECOMMANDATION:")
        print("Utiliser TWS (7497) pour plus de stabilité")
    
    # 3. TEST CONNEXION RAPIDE
    print("\n📊 3. TEST CONNEXION RAPIDE")
    print("=" * 40)
    
    if active_ports:
        port, name = active_ports[0]
        print(f"🔗 Test connexion {name} (port {port})...")
        
        try:
            # Test connexion simple
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            sock.connect(('127.0.0.1', port))
            sock.close()
            print(f"✅ Connexion {name} réussie")
            
            # Recommandation finale
            print(f"\n🚀 CONFIGURATION FINALE:")
            print(f"Host: 127.0.0.1")
            print(f"Port: {port}")
            print(f"Client ID: 1")
            print(f"Timeout: 30s (réduit)")
            
        except Exception as e:
            print(f"❌ Échec connexion {name}: {e}")
    
    # 4. COMMANDES DE CORRECTION
    print("\n🔧 4. COMMANDES DE CORRECTION")
    print("=" * 40)
    
    if active_ports:
        port, name = active_ports[0]
        print("✅ Port actif détecté - Correction possible")
        print("\n💡 Scripts de correction:")
        print(f"python corriger_connexion_{port}.py")
        print("python test_connexion_rapide.py")
        print("python lance_systeme_corrige.py")
    else:
        print("❌ Aucun port actif - Correction manuelle requise")
        print("\n💡 Actions manuelles:")
        print("1. Démarrer TWS/Gateway")
        print("2. Activer API")
        print("3. Relancer diagnostic")

if __name__ == "__main__":
    verifier_ibkr_urgence()






