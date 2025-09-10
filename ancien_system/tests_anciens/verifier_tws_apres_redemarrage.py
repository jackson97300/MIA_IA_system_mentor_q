#!/usr/bin/env python3
"""
MIA_IA_SYSTEM - Vérification TWS après redémarrage
Diagnostic complet de l'état de TWS après redémarrage
"""

import os
import sys
import time
import json
import socket
import subprocess
from datetime import datetime, timedelta

# Ajouter le répertoire racine au path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def verifier_port_tws(port=7497, host='127.0.0.1'):
    """Vérifier si le port TWS est ouvert"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except Exception as e:
        return False

def verifier_processus_tws():
    """Vérifier si TWS est en cours d'exécution"""
    try:
        # Windows
        result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq javaw.exe'], 
                              capture_output=True, text=True, shell=True)
        return 'javaw.exe' in result.stdout
    except Exception as e:
        return False

def verifier_connexion_ibkr():
    """Vérifier la connexion IBKR"""
    try:
        from config.mia_ia_system_tws_paper_fixed import IB_CONFIG
        from core.ibkr_connector import IBKRConnector
        
        print("🔌 Test de connexion IBKR...")
        connector = IBKRConnector(IB_CONFIG)
        
        # Test de connexion
        if connector.connect():
            print("   ✅ Connexion IBKR réussie")
            
            # Test de données ES
            print("📊 Test de données ES...")
            es_data = connector.get_market_data('ES', 'ESU25')
            if es_data and 'last' in es_data:
                print(f"   ✅ Données ES OK - Prix: {es_data['last']}")
                return True
            else:
                print("   ❌ Données ES non disponibles")
                return False
        else:
            print("   ❌ Échec connexion IBKR")
            return False
            
    except Exception as e:
        print(f"   ❌ Erreur connexion: {str(e)}")
        return False

def verifier_donnees_critiques():
    """Vérifier les données critiques"""
    try:
        from config.mia_ia_system_tws_paper_fixed import IB_CONFIG
        from core.ibkr_connector import IBKRConnector
        
        connector = IBKRConnector(IB_CONFIG)
        
        if not connector.connect():
            return False
            
        print("📊 Vérification données critiques...")
        
        # Test ES
        es_data = connector.get_market_data('ES', 'ESU25')
        if es_data:
            print(f"   ✅ ES - Prix: {es_data.get('last', 'N/A')} | Volume: {es_data.get('volume', 'N/A')}")
        else:
            print("   ❌ ES - Données non disponibles")
            
        # Test SPX
        spx_data = connector.get_market_data('SPX', 'SPX')
        if spx_data:
            print(f"   ✅ SPX - Prix: {spx_data.get('last', 'N/A')} | Volume: {spx_data.get('volume', 'N/A')}")
        else:
            print("   ❌ SPX - Données non disponibles")
            
        # Test options SPX
        print("   🔍 Test options SPX...")
        options_data = connector.get_options_chain('SPX')
        if options_data:
            print(f"   ✅ Options SPX - {len(options_data)} contrats disponibles")
        else:
            print("   ❌ Options SPX - Aucun contrat disponible")
            
        return True
        
    except Exception as e:
        print(f"   ❌ Erreur données: {str(e)}")
        return False

def verifier_systeme_mia():
    """Vérifier le système MIA"""
    try:
        print("🤖 Test système MIA...")
        
        # Vérifier les modules critiques
        modules_critiques = [
            'core.battle_navale',
            'core.ibkr_connector', 
            'features.confluence_analyzer',
            'strategies.signal_generator'
        ]
        
        for module in modules_critiques:
            try:
                __import__(module)
                print(f"   ✅ {module}")
            except ImportError as e:
                print(f"   ❌ {module} - {str(e)}")
                
        return True
        
    except Exception as e:
        print(f"   ❌ Erreur système MIA: {str(e)}")
        return False

def verifier_tws_apres_redemarrage():
    """Vérification complète de TWS après redémarrage"""
    
    print("🔄 MIA_IA_SYSTEM - VÉRIFICATION TWS APRÈS REDÉMARRAGE")
    print("=" * 70)
    print("🔍 Diagnostic complet de l'état de TWS")
    print("⏰ Durée: 2 minutes")
    print("🎯 Objectif: Validation du redémarrage")
    print("=" * 70)
    
    start_time = datetime.now()
    verification_duration = timedelta(minutes=2)
    
    # Variables de suivi
    tests_reussis = 0
    tests_echecs = 0
    problemes_detectes = []
    
    print(f"⏰ Début vérification: {start_time.strftime('%H:%M:%S')}")
    print(f"⏰ Fin prévue: {(start_time + verification_duration).strftime('%H:%M:%S')}")
    
    print("\n🔍 VÉRIFICATIONS EN COURS:")
    print("=" * 50)
    
    try:
        while datetime.now() < start_time + verification_duration:
            current_time = datetime.now()
            elapsed = current_time - start_time
            remaining = verification_duration - elapsed
            
            print(f"\n⏰ {current_time.strftime('%H:%M:%S')} | "
                  f"Écoulé: {elapsed.total_seconds():.0f}s | "
                  f"Reste: {remaining.total_seconds():.0f}s")
            
            # 1. VÉRIFICATION PORT TWS
            print("\n🔌 Vérification port TWS...")
            if verifier_port_tws():
                print("   ✅ Port 7497 ouvert")
                tests_reussis += 1
            else:
                print("   ❌ Port 7497 fermé")
                tests_echecs += 1
                problemes_detectes.append("Port TWS fermé")
            
            # 2. VÉRIFICATION PROCESSUS TWS
            print("🖥️ Vérification processus TWS...")
            if verifier_processus_tws():
                print("   ✅ Processus TWS actif")
                tests_reussis += 1
            else:
                print("   ❌ Processus TWS non trouvé")
                tests_echecs += 1
                problemes_detectes.append("Processus TWS manquant")
            
            # 3. VÉRIFICATION CONNEXION IBKR
            print("🌐 Vérification connexion IBKR...")
            if verifier_connexion_ibkr():
                print("   ✅ Connexion IBKR OK")
                tests_reussis += 1
            else:
                print("   ❌ Connexion IBKR échouée")
                tests_echecs += 1
                problemes_detectes.append("Connexion IBKR échouée")
            
            # 4. VÉRIFICATION DONNÉES CRITIQUES
            print("📊 Vérification données critiques...")
            if verifier_donnees_critiques():
                print("   ✅ Données critiques OK")
                tests_reussis += 1
            else:
                print("   ❌ Données critiques manquantes")
                tests_echecs += 1
                problemes_detectes.append("Données critiques manquantes")
            
            # 5. VÉRIFICATION SYSTÈME MIA
            print("🤖 Vérification système MIA...")
            if verifier_systeme_mia():
                print("   ✅ Système MIA OK")
                tests_reussis += 1
            else:
                print("   ❌ Système MIA défaillant")
                tests_echecs += 1
                problemes_detectes.append("Système MIA défaillant")
            
            # STATISTIQUES ACTUELLES
            print(f"\n📊 STATISTIQUES TESTS:")
            print(f"   ✅ Tests réussis: {tests_reussis}")
            print(f"   ❌ Tests échecs: {tests_echecs}")
            print(f"   📈 Taux de réussite: {(tests_reussis/(tests_reussis+tests_echecs)*100):.1f}%" if (tests_reussis+tests_echecs) > 0 else "   📈 Taux de réussite: 0%")
            
            # Attendre avant prochaine vérification
            time.sleep(30)
            
    except KeyboardInterrupt:
        print("\n🛑 Vérification arrêtée par l'utilisateur")
    
    # RAPPORT FINAL
    end_time = datetime.now()
    total_duration = end_time - start_time
    
    print("\n📊 RAPPORT FINAL TWS")
    print("=" * 50)
    print(f"⏰ Durée totale: {total_duration.total_seconds():.1f} secondes")
    print(f"✅ Tests réussis: {tests_reussis}")
    print(f"❌ Tests échecs: {tests_echecs}")
    print(f"📈 Taux de réussite: {(tests_reussis/(tests_reussis+tests_echecs)*100):.1f}%" if (tests_reussis+tests_echecs) > 0 else "📈 Taux de réussite: 0%")
    
    # ÉVALUATION GLOBALE
    print("\n🎯 ÉVALUATION GLOBALE")
    print("=" * 50)
    
    if tests_echecs == 0:
        print("🟢 EXCELLENT - TWS fonctionne parfaitement")
        print("   • Tous les tests réussis")
        print("   • Système prêt pour le trading")
        print("   • Aucune action requise")
    elif tests_echecs <= 2:
        print("🟡 BON - TWS fonctionne avec quelques problèmes mineurs")
        print("   • La plupart des fonctionnalités OK")
        print("   • Quelques ajustements nécessaires")
        print("   • Système utilisable")
    elif tests_echecs <= 4:
        print("🟠 MOYEN - TWS a des problèmes significatifs")
        print("   • Plusieurs fonctionnalités défaillantes")
        print("   • Actions correctives nécessaires")
        print("   • Système partiellement utilisable")
    else:
        print("🔴 CRITIQUE - TWS a des problèmes majeurs")
        print("   • Nombreux échecs de tests")
        print("   • Actions correctives urgentes")
        print("   • Système non utilisable")
    
    # PROBLÈMES DÉTECTÉS
    if problemes_detectes:
        print("\n🚨 PROBLÈMES DÉTECTÉS")
        print("=" * 50)
        for i, probleme in enumerate(set(problemes_detectes), 1):
            print(f"{i}. {probleme}")
    
    # RECOMMANDATIONS
    print("\n🚀 RECOMMANDATIONS")
    print("=" * 50)
    
    if "Port TWS fermé" in problemes_detectes:
        print("🔌 Port TWS fermé:")
        print("   • Vérifier que TWS est démarré")
        print("   • Vérifier le port 7497")
        print("   • Redémarrer TWS si nécessaire")
    
    if "Processus TWS manquant" in problemes_detectes:
        print("🖥️ Processus TWS manquant:")
        print("   • Démarrer TWS")
        print("   • Vérifier les paramètres de connexion")
        print("   • Attendre le chargement complet")
    
    if "Connexion IBKR échouée" in problemes_detectes:
        print("🌐 Connexion IBKR échouée:")
        print("   • Vérifier les paramètres de connexion")
        print("   • Vérifier le Client ID")
        print("   • Redémarrer TWS")
    
    if "Données critiques manquantes" in problemes_detectes:
        print("📊 Données critiques manquantes:")
        print("   • Vérifier les souscriptions de marché")
        print("   • Attendre la réception des données")
        print("   • Vérifier les contrats")
    
    if "Système MIA défaillant" in problemes_detectes:
        print("🤖 Système MIA défaillant:")
        print("   • Vérifier les modules Python")
        print("   • Redémarrer le système MIA")
        print("   • Vérifier les dépendances")
    
    # PLAN D'ACTION
    print("\n📋 PLAN D'ACTION")
    print("=" * 50)
    
    if tests_echecs == 0:
        print("✅ Aucune action requise - TWS fonctionne parfaitement")
    else:
        print("1. 🔌 Vérifier et corriger les problèmes de connexion")
        print("2. 📊 Vérifier les données de marché")
        print("3. 🤖 Vérifier le système MIA")
        print("4. 🔄 Relancer la vérification")
        print("5. ✅ Confirmer le bon fonctionnement")

if __name__ == "__main__":
    verifier_tws_apres_redemarrage()

