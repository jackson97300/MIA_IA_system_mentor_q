#!/usr/bin/env python3
"""
MIA_IA_SYSTEM - Diagnostic TWS Complet
Diagnostic approfondi des problèmes de connexion API TWS
"""

import os
import sys
import socket
import subprocess
import time
import json
from datetime import datetime

def test_port_detaille():
    """Test détaillé du port TWS"""
    print("🔌 Test détaillé port TWS...")
    
    # Test 1: Port 7497
    print("   📍 Test port 7497...")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex(('127.0.0.1', 7497))
        sock.close()
        
        if result == 0:
            print("      ✅ Port 7497 ouvert")
            port_7497 = True
        else:
            print("      ❌ Port 7497 fermé")
            port_7497 = False
    except Exception as e:
        print(f"      ❌ Erreur port 7497: {str(e)}")
        port_7497 = False
    
    # Test 2: Port 7496 (alternative)
    print("   📍 Test port 7496...")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex(('127.0.0.1', 7496))
        sock.close()
        
        if result == 0:
            print("      ✅ Port 7496 ouvert")
            port_7496 = True
        else:
            print("      ❌ Port 7496 fermé")
            port_7496 = False
    except Exception as e:
        print(f"      ❌ Erreur port 7496: {str(e)}")
        port_7496 = False
    
    return port_7497, port_7496

def test_processus_detaille():
    """Test détaillé des processus"""
    print("🖥️ Test détaillé processus...")
    
    try:
        # Vérifier tous les processus
        result = subprocess.run(['tasklist', '/FO', 'CSV'], capture_output=True, text=True, shell=True)
        lines = result.stdout.split('\n')
        
        ib_processes = []
        java_processes = []
        
        for line in lines:
            if 'tws' in line.lower():
                ib_processes.append(line.strip())
            elif 'javaw' in line.lower():
                java_processes.append(line.strip())
            elif 'ibgateway' in line.lower():
                ib_processes.append(line.strip())
        
        print(f"   📊 Processus IB trouvés: {len(ib_processes)}")
        print(f"   📊 Processus Java trouvés: {len(java_processes)}")
        
        if ib_processes:
            print("      ✅ Processus IB actifs")
            for proc in ib_processes[:3]:  # Afficher les 3 premiers
                print(f"         - {proc}")
        else:
            print("      ❌ Aucun processus IB trouvé")
        
        if java_processes:
            print("      ✅ Processus Java actifs")
            for proc in java_processes[:3]:  # Afficher les 3 premiers
                print(f"         - {proc}")
        else:
            print("      ❌ Aucun processus Java trouvé")
        
        return len(ib_processes) > 0, len(java_processes) > 0
        
    except Exception as e:
        print(f"   ❌ Erreur processus: {str(e)}")
        return False, False

def test_connexion_api():
    """Test de connexion API simple"""
    print("🌐 Test connexion API...")
    
    try:
        # Test de connexion TCP avec envoi de données
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        sock.connect(('127.0.0.1', 7497))
        
        # Essayer d'envoyer des données de test
        test_data = b"API Test\n"
        sock.send(test_data)
        
        # Attendre une réponse
        sock.settimeout(5)
        try:
            response = sock.recv(1024)
            print("      ✅ Réponse reçue de TWS")
        except socket.timeout:
            print("      ⚠️ Pas de réponse de TWS (normal)")
        
        sock.close()
        print("      ✅ Connexion TCP réussie")
        return True
        
    except Exception as e:
        print(f"      ❌ Erreur connexion API: {str(e)}")
        return False

def test_configuration_tws():
    """Test de la configuration TWS"""
    print("⚙️ Test configuration TWS...")
    
    try:
        from config.mia_ia_system_tws_paper_fixed import MIA_IA_SYSTEM_GATEWAY_CONFIG
        
        config = MIA_IA_SYSTEM_GATEWAY_CONFIG['ibkr']
        
        print(f"   📍 Host: {config.get('host', 'N/A')}")
        print(f"   🔌 Port: {config.get('port', 'N/A')}")
        print(f"   🆔 Client ID: {config.get('client_id', 'N/A')}")
        print(f"   ⏱️ Timeout: {config.get('timeout', 'N/A')}")
        print(f"   📊 Paper Trading: {config.get('paper_trading', 'N/A')}")
        print(f"   🔒 Read Only: {config.get('read_only', 'N/A')}")
        print(f"   🔄 Auto Reconnect: {config.get('auto_reconnect', 'N/A')}")
        
        # Vérifications
        checks = []
        if config.get('host') == '127.0.0.1':
            checks.append("✅ Host local correct")
        else:
            checks.append("❌ Host incorrect")
            
        if config.get('port') in [7496, 7497]:
            checks.append("✅ Port correct")
        else:
            checks.append("❌ Port incorrect")
            
        if config.get('client_id', 0) > 0:
            checks.append("✅ Client ID valide")
        else:
            checks.append("❌ Client ID invalide")
        
        for check in checks:
            print(f"      {check}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Erreur configuration: {str(e)}")
        return False

def diagnostic_complet():
    """Diagnostic complet TWS"""
    
    print("🔄 MIA_IA_SYSTEM - DIAGNOSTIC TWS COMPLET")
    print("=" * 60)
    print("🔍 Diagnostic approfondi TWS")
    print(f"⏰ {datetime.now().strftime('%H:%M:%S')}")
    print("🎯 Identification cause exacte")
    print("=" * 60)
    
    # Tests détaillés
    port_7497, port_7496 = test_port_detaille()
    processus_ib, processus_java = test_processus_detaille()
    connexion_api = test_connexion_api()
    config_ok = test_configuration_tws()
    
    # Évaluation
    print("\n📊 ÉVALUATION DIAGNOSTIC")
    print("=" * 50)
    
    tests_reussis = sum([port_7497, processus_ib, connexion_api, config_ok])
    total_tests = 4
    
    print(f"✅ Tests réussis: {tests_reussis}/{total_tests}")
    print(f"📈 Taux de réussite: {(tests_reussis/total_tests)*100:.1f}%")
    
    # ANALYSE DES CAUSES
    print("\n🔍 ANALYSE DES CAUSES")
    print("=" * 50)
    
    if not port_7497 and not port_7496:
        print("🚨 CAUSE PRINCIPALE: Aucun port TWS ouvert")
        print("   • TWS n'est pas démarré")
        print("   • TWS n'écoute sur aucun port")
        print("   • Problème de configuration TWS")
    elif not processus_ib:
        print("🚨 CAUSE PRINCIPALE: Aucun processus IB actif")
        print("   • TWS n'est pas démarré")
        print("   • Processus TWS arrêté")
        print("   • Problème de démarrage TWS")
    elif not connexion_api:
        print("🚨 CAUSE PRINCIPALE: API TWS non accessible")
        print("   • API TWS désactivée")
        print("   • Paramètres API incorrects")
        print("   • Pare-feu bloque la connexion")
    elif not config_ok:
        print("🚨 CAUSE PRINCIPALE: Configuration incorrecte")
        print("   • Paramètres de connexion erronés")
        print("   • Client ID en conflit")
        print("   • Configuration système défaillante")
    else:
        print("✅ TWS semble fonctionnel")
        print("   • Problème probable: API TWS spécifique")
        print("   • Vérifier les paramètres API dans TWS")
    
    # RECOMMANDATIONS SPÉCIFIQUES
    print("\n🚀 RECOMMANDATIONS SPÉCIFIQUES")
    print("=" * 50)
    
    if not port_7497 and not port_7496:
        print("🔧 Actions immédiates:")
        print("   1. Démarrer TWS")
        print("   2. Vérifier que TWS se charge complètement")
        print("   3. Vérifier les paramètres de port dans TWS")
        print("   4. Redémarrer TWS si nécessaire")
    
    elif not processus_ib:
        print("🔧 Actions immédiates:")
        print("   1. Vérifier que TWS est bien démarré")
        print("   2. Vérifier les processus système")
        print("   3. Redémarrer TWS complètement")
        print("   4. Vérifier les logs TWS")
    
    elif not connexion_api:
        print("🔧 Actions immédiates:")
        print("   1. Dans TWS: File > Global Configuration > API > Settings")
        print("   2. Activer 'Enable ActiveX and Socket Clients'")
        print("   3. Vérifier le port 7497")
        print("   4. Désactiver 'Read-Only API' temporairement")
        print("   5. Redémarrer TWS")
    
    elif not config_ok:
        print("🔧 Actions immédiates:")
        print("   1. Vérifier la configuration système")
        print("   2. Changer le Client ID si nécessaire")
        print("   3. Vérifier les paramètres de connexion")
        print("   4. Corriger la configuration")
    
    else:
        print("🔧 Actions immédiates:")
        print("   1. Vérifier les paramètres API dans TWS")
        print("   2. Vérifier qu'aucun autre client n'utilise le Client ID 1")
        print("   3. Redémarrer TWS")
        print("   4. Tester avec un Client ID différent")
    
    # PLAN D'ACTION FINAL
    print("\n📋 PLAN D'ACTION FINAL")
    print("=" * 50)
    
    if tests_reussis >= 3:
        print("✅ TWS fonctionnel - Problème API spécifique")
        print("1. 🔧 Vérifier paramètres API TWS")
        print("2. 🆔 Changer Client ID si nécessaire")
        print("3. 🔄 Redémarrer TWS")
        print("4. 🔄 Relancer test API")
    elif tests_reussis >= 2:
        print("⏳ TWS partiellement fonctionnel")
        print("1. 🔧 Corriger les problèmes identifiés")
        print("2. 🔄 Redémarrer TWS")
        print("3. 🔄 Relancer diagnostic")
    else:
        print("🔄 TWS nécessite redémarrage complet")
        print("1. 🔄 Fermer TWS complètement")
        print("2. 🔄 Redémarrer TWS")
        print("3. ⏳ Attendre chargement complet")
        print("4. 🔄 Relancer diagnostic")

if __name__ == "__main__":
    diagnostic_complet()



