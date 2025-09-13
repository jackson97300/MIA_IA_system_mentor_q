#!/usr/bin/env python3
"""
MIA_IA_SYSTEM - Test Connexion Simulation
Test de connexion en mode simulation TWS
"""

import os
import sys
import time
import socket
from datetime import datetime

# Ajouter le répertoire racine au path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_connexion_simulation():
    """Test de connexion en mode simulation"""
    
    print("🔄 MIA_IA_SYSTEM - TEST CONNEXION SIMULATION")
    print("=" * 60)
    print("🔍 Test de connexion mode simulation TWS")
    print(f"⏰ {datetime.now().strftime('%H:%M:%S')}")
    print("🎯 Port: 7497 (Simulation)")
    print("=" * 60)
    
    # 1. VÉRIFICATION PORT SIMULATION
    print("\n🔌 Vérification port simulation (7497)...")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex(('127.0.0.1', 7497))
        sock.close()
        
        if result == 0:
            print("   ✅ Port 7497 ouvert (Simulation)")
            port_ok = True
        else:
            print("   ❌ Port 7497 fermé")
            port_ok = False
    except Exception as e:
        print(f"   ❌ Erreur port: {str(e)}")
        port_ok = False
    
    # 2. TEST CONNEXION IBKR SIMULATION
    print("\n🌐 Test connexion IBKR simulation...")
    try:
        from config.mia_ia_system_tws_paper_fixed import MIA_IA_SYSTEM_GATEWAY_CONFIG
        from core.ibkr_connector import IBKRConnector
        
        print("   🔧 Configuration simulation chargée")
        ib_config = MIA_IA_SYSTEM_GATEWAY_CONFIG['ibkr']
        print(f"   📍 Host: {ib_config.get('host', 'N/A')}")
        print(f"   🔌 Port: {ib_config.get('port', 'N/A')}")
        print(f"   🆔 Client ID: {ib_config.get('client_id', 'N/A')}")
        
        connector = IBKRConnector(ib_config)
        
        # Test de connexion
        print("   🔌 Tentative de connexion...")
        if connector.connect():
            print("   ✅ Connexion simulation réussie")
            connexion_ok = True
            
            # Test de données simulées
            print("   📊 Test données simulées...")
            try:
                # Test ES simulé
                es_data = connector.get_market_data('ES', 'ESU25')
                if es_data:
                    print(f"   ✅ ES simulé - Prix: {es_data.get('last', 'N/A')}")
                else:
                    print("   ⚠️ ES simulé - Données non disponibles")
                
                # Test SPX simulé
                spx_data = connector.get_market_data('SPX', 'SPX')
                if spx_data:
                    print(f"   ✅ SPX simulé - Prix: {spx_data.get('last', 'N/A')}")
                else:
                    print("   ⚠️ SPX simulé - Données non disponibles")
                    
            except Exception as e:
                print(f"   ⚠️ Erreur données simulées: {str(e)}")
                
        else:
            print("   ❌ Échec connexion simulation")
            connexion_ok = False
            
    except ImportError as e:
        print(f"   ❌ Erreur import: {str(e)}")
        connexion_ok = False
    except Exception as e:
        print(f"   ❌ Erreur connexion: {str(e)}")
        connexion_ok = False
    
    # 3. TEST SYSTÈME MIA
    print("\n🤖 Test système MIA...")
    try:
        # Vérifier les modules critiques
        modules_critiques = [
            'core.battle_navale',
            'core.ibkr_connector',
            'features.confluence_analyzer',
            'strategies.signal_generator'
        ]
        
        modules_ok = 0
        for module in modules_critiques:
            try:
                __import__(module)
                print(f"   ✅ {module}")
                modules_ok += 1
            except ImportError as e:
                print(f"   ❌ {module} - {str(e)}")
        
        systeme_ok = modules_ok == len(modules_critiques)
        
    except Exception as e:
        print(f"   ❌ Erreur système: {str(e)}")
        systeme_ok = False
    
    # 4. ÉVALUATION GLOBALE
    print("\n📊 ÉVALUATION GLOBALE SIMULATION")
    print("=" * 50)
    
    tests_reussis = sum([port_ok, connexion_ok, systeme_ok])
    total_tests = 3
    
    print(f"✅ Tests réussis: {tests_reussis}/{total_tests}")
    print(f"📈 Taux de réussite: {(tests_reussis/total_tests)*100:.1f}%")
    
    if tests_reussis == 3:
        print("\n🟢 EXCELLENT - Simulation fonctionnelle")
        print("   • Port simulation ouvert")
        print("   • Connexion IBKR OK")
        print("   • Système MIA opérationnel")
        print("   • Prêt pour trading simulation")
    elif tests_reussis == 2:
        print("\n🟡 BON - Simulation partiellement fonctionnelle")
        print("   • La plupart des éléments OK")
        print("   • Quelques ajustements nécessaires")
        print("   • Système utilisable en simulation")
    elif tests_reussis == 1:
        print("\n🟠 MOYEN - Simulation avec problèmes")
        print("   • Quelques éléments fonctionnels")
        print("   • Actions correctives nécessaires")
        print("   • Système partiellement utilisable")
    else:
        print("\n🔴 CRITIQUE - Simulation non fonctionnelle")
        print("   • Aucun élément fonctionnel")
        print("   • Actions correctives urgentes")
        print("   • Système non utilisable")
    
    # RECOMMANDATIONS
    print("\n🚀 RECOMMANDATIONS")
    print("=" * 50)
    
    if not port_ok:
        print("🔌 Port simulation fermé:")
        print("   • Vérifier que TWS simulation est démarré")
        print("   • Vérifier le port 7497")
        print("   • Redémarrer TWS simulation si nécessaire")
    
    if not connexion_ok:
        print("🌐 Connexion simulation échouée:")
        print("   • Vérifier les paramètres de connexion")
        print("   • Vérifier le Client ID")
        print("   • Vérifier la configuration simulation")
    
    if not systeme_ok:
        print("🤖 Système MIA défaillant:")
        print("   • Vérifier les modules Python")
        print("   • Vérifier les dépendances")
        print("   • Redémarrer le système MIA")
    
    # PLAN D'ACTION
    print("\n📋 PLAN D'ACTION")
    print("=" * 50)
    
    if tests_reussis == 3:
        print("✅ Simulation prête - Aucune action requise")
        print("   • Vous pouvez lancer le système MIA en simulation")
        print("   • Exécuter: python lance_mia_ia_tws.py")
    elif tests_reussis >= 2:
        print("⏳ Simulation presque prête")
        print("   • Corriger les problèmes mineurs")
        print("   • Relancer ce test")
        print("   • Puis lancer le système MIA")
    else:
        print("🔄 Simulation nécessite corrections")
        print("   • Corriger les problèmes identifiés")
        print("   • Redémarrer TWS simulation si nécessaire")
        print("   • Relancer ce test")
        print("   • Puis lancer le système MIA")

if __name__ == "__main__":
    test_connexion_simulation()
