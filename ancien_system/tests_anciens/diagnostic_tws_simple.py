#!/usr/bin/env python3
"""
MIA_IA_SYSTEM - Diagnostic TWS Simple
Diagnostic rapide des problèmes de connexion TWS
"""

import os
import sys
import socket
import subprocess
import time
from datetime import datetime

def test_port_tws():
    """Test simple du port TWS"""
    print("🔌 Test port TWS (7497)...")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        result = sock.connect_ex(('127.0.0.1', 7497))
        sock.close()
        
        if result == 0:
            print("   ✅ Port 7497 ouvert")
            return True
        else:
            print("   ❌ Port 7497 fermé")
            return False
    except Exception as e:
        print(f"   ❌ Erreur port: {str(e)}")
        return False

def test_processus_tws():
    """Test des processus TWS"""
    print("🖥️ Test processus TWS...")
    try:
        # Vérifier tous les processus
        result = subprocess.run(['tasklist'], capture_output=True, text=True, shell=True)
        output = result.stdout.lower()
        
        # Chercher les processus IB
        ib_processes = []
        if 'javaw.exe' in output:
            ib_processes.append('javaw.exe')
        if 'tws' in output:
            ib_processes.append('tws')
        if 'ibgateway' in output:
            ib_processes.append('ibgateway')
        
        if ib_processes:
            print(f"   ✅ Processus IB trouvés: {', '.join(ib_processes)}")
            return True
        else:
            print("   ❌ Aucun processus IB trouvé")
            return False
    except Exception as e:
        print(f"   ❌ Erreur processus: {str(e)}")
        return False

def test_connexion_simple():
    """Test de connexion simple"""
    print("🌐 Test connexion simple...")
    try:
        # Test de connexion TCP simple
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        sock.connect(('127.0.0.1', 7497))
        sock.close()
        print("   ✅ Connexion TCP réussie")
        return True
    except Exception as e:
        print(f"   ❌ Erreur connexion TCP: {str(e)}")
        return False

def diagnostic_tws():
    """Diagnostic complet TWS"""
    
    print("🔄 MIA_IA_SYSTEM - DIAGNOSTIC TWS SIMPLE")
    print("=" * 50)
    print("🔍 Diagnostic rapide TWS")
    print(f"⏰ {datetime.now().strftime('%H:%M:%S')}")
    print("=" * 50)
    
    # Tests de base
    port_ok = test_port_tws()
    processus_ok = test_processus_tws()
    connexion_ok = test_connexion_simple()
    
    # Évaluation
    print("\n📊 ÉVALUATION DIAGNOSTIC")
    print("=" * 40)
    
    tests_reussis = sum([port_ok, processus_ok, connexion_ok])
    total_tests = 3
    
    print(f"✅ Tests réussis: {tests_reussis}/{total_tests}")
    print(f"📈 Taux de réussite: {(tests_reussis/total_tests)*100:.1f}%")
    
    if tests_reussis == 3:
        print("\n🟢 EXCELLENT - TWS semble fonctionnel")
        print("   • Port ouvert")
        print("   • Processus actifs")
        print("   • Connexion TCP OK")
        print("   • Problème probable: API TWS")
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
    print("=" * 40)
    
    if not port_ok:
        print("🔌 Port fermé:")
        print("   • Vérifier que TWS est démarré")
        print("   • Vérifier le port 7497")
        print("   • Redémarrer TWS")
    
    if not processus_ok:
        print("🖥️ Processus manquants:")
        print("   • Démarrer TWS")
        print("   • Vérifier les processus système")
        print("   • Redémarrer si nécessaire")
    
    if not connexion_ok:
        print("🌐 Connexion échouée:")
        print("   • Vérifier le pare-feu")
        print("   • Vérifier les paramètres réseau")
        print("   • Redémarrer TWS")
    
    if tests_reussis == 3:
        print("🔧 API TWS:")
        print("   • Le problème vient de l'API TWS")
        print("   • Vérifier les paramètres API")
        print("   • Vérifier le Client ID")
        print("   • Redémarrer TWS")
    
    # PLAN D'ACTION
    print("\n📋 PLAN D'ACTION")
    print("=" * 40)
    
    if tests_reussis == 3:
        print("✅ TWS fonctionnel - Problème API")
        print("1. 🔧 Vérifier paramètres API TWS")
        print("2. 🔄 Redémarrer TWS")
        print("3. 🆔 Vérifier Client ID")
        print("4. 🔄 Relancer test API")
    elif tests_reussis >= 2:
        print("⏳ TWS partiellement fonctionnel")
        print("1. 🔄 Attendre démarrage complet TWS")
        print("2. 🔧 Vérifier paramètres")
        print("3. 🔄 Relancer diagnostic")
    else:
        print("🔄 TWS nécessite redémarrage")
        print("1. 🔄 Fermer TWS complètement")
        print("2. 🔄 Redémarrer TWS")
        print("3. ⏳ Attendre chargement complet")
        print("4. 🔄 Relancer diagnostic")

if __name__ == "__main__":
    diagnostic_tws()

