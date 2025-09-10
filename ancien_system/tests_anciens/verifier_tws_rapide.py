#!/usr/bin/env python3
"""
MIA_IA_SYSTEM - Vérification rapide TWS
Test rapide de l'état de TWS après redémarrage
"""

import os
import sys
import time
import socket
import subprocess
from datetime import datetime

def verifier_port_tws(port=7497, host='127.0.0.1'):
    """Vérifier si le port TWS est ouvert"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except Exception as e:
        return False

def verifier_processus_tws():
    """Vérifier si TWS est en cours d'exécution"""
    try:
        # Windows - vérifier javaw.exe
        result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq javaw.exe'], 
                              capture_output=True, text=True, shell=True)
        return 'javaw.exe' in result.stdout
    except Exception as e:
        return False

def verifier_processus_ib():
    """Vérifier les processus IB"""
    try:
        # Vérifier tous les processus liés à IB
        result = subprocess.run(['tasklist'], capture_output=True, text=True, shell=True)
        output = result.stdout.lower()
        
        ib_processes = ['javaw.exe', 'ibgateway', 'tws']
        found_processes = []
        
        for process in ib_processes:
            if process in output:
                found_processes.append(process)
        
        return found_processes
    except Exception as e:
        return []

def verifier_tws_rapide():
    """Vérification rapide de TWS"""
    
    print("🔄 MIA_IA_SYSTEM - VÉRIFICATION RAPIDE TWS")
    print("=" * 50)
    print("🔍 Test rapide après redémarrage")
    print(f"⏰ {datetime.now().strftime('%H:%M:%S')}")
    print("=" * 50)
    
    # 1. VÉRIFICATION PORT
    print("\n🔌 Vérification port TWS (7497)...")
    if verifier_port_tws():
        print("   ✅ Port 7497 ouvert")
        port_ok = True
    else:
        print("   ❌ Port 7497 fermé")
        port_ok = False
    
    # 2. VÉRIFICATION PROCESSUS
    print("\n🖥️ Vérification processus TWS...")
    if verifier_processus_tws():
        print("   ✅ Processus TWS (javaw.exe) actif")
        processus_ok = True
    else:
        print("   ❌ Processus TWS non trouvé")
        processus_ok = False
    
    # 3. VÉRIFICATION PROCESSUS IB
    print("\n🏢 Vérification processus IB...")
    ib_processes = verifier_processus_ib()
    if ib_processes:
        print(f"   ✅ Processus IB trouvés: {', '.join(ib_processes)}")
        ib_ok = True
    else:
        print("   ❌ Aucun processus IB trouvé")
        ib_ok = False
    
    # 4. ÉVALUATION GLOBALE
    print("\n📊 ÉVALUATION GLOBALE")
    print("=" * 30)
    
    tests_reussis = sum([port_ok, processus_ok, ib_ok])
    total_tests = 3
    
    print(f"✅ Tests réussis: {tests_reussis}/{total_tests}")
    print(f"📈 Taux de réussite: {(tests_reussis/total_tests)*100:.1f}%")
    
    if tests_reussis == 3:
        print("\n🟢 EXCELLENT - TWS semble fonctionnel")
        print("   • Port ouvert")
        print("   • Processus actifs")
        print("   • Prêt pour connexion")
    elif tests_reussis == 2:
        print("\n🟡 BON - TWS partiellement fonctionnel")
        print("   • La plupart des éléments OK")
        print("   • Vérification recommandée")
    elif tests_reussis == 1:
        print("\n🟠 MOYEN - TWS a des problèmes")
        print("   • Quelques éléments fonctionnels")
        print("   • Actions correctives nécessaires")
    else:
        print("\n🔴 CRITIQUE - TWS non fonctionnel")
        print("   • Aucun élément fonctionnel")
        print("   • Redémarrage nécessaire")
    
    # RECOMMANDATIONS
    print("\n🚀 RECOMMANDATIONS")
    print("=" * 30)
    
    if not port_ok:
        print("🔌 Port fermé:")
        print("   • Attendre que TWS démarre complètement")
        print("   • Vérifier les paramètres de port")
        print("   • Redémarrer TWS si nécessaire")
    
    if not processus_ok:
        print("🖥️ Processus manquant:")
        print("   • Démarrer TWS")
        print("   • Attendre le chargement complet")
        print("   • Vérifier les paramètres")
    
    if not ib_ok:
        print("🏢 Processus IB manquants:")
        print("   • Vérifier que TWS est démarré")
        print("   • Vérifier les processus système")
        print("   • Redémarrer si nécessaire")
    
    # PLAN D'ACTION
    print("\n📋 PLAN D'ACTION")
    print("=" * 30)
    
    if tests_reussis == 3:
        print("✅ TWS prêt - Aucune action requise")
        print("   • Vous pouvez maintenant lancer le système MIA")
    elif tests_reussis >= 2:
        print("⏳ Attendre - TWS en cours de démarrage")
        print("   • Attendre 1-2 minutes supplémentaires")
        print("   • Relancer cette vérification")
    else:
        print("🔄 Redémarrer - TWS nécessite un redémarrage")
        print("   • Fermer TWS complètement")
        print("   • Redémarrer TWS")
        print("   • Attendre le chargement complet")
        print("   • Relancer cette vérification")

if __name__ == "__main__":
    verifier_tws_rapide()

