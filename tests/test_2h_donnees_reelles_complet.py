#!/usr/bin/env python3
"""
MIA_IA_SYSTEM - Test 2 Heures Données Réelles Complet
Lance le système complet et surveille tous les composants critiques
"""

import os
import sys
import time
import json
import glob
import asyncio
import subprocess
import threading
from datetime import datetime, timedelta
from pathlib import Path

# Ajouter le répertoire racine au path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_2h_donnees_reelles_complet():
    """Test de 2 heures avec système complet MIA"""
    
    print("MIA_IA_SYSTEM - TEST 2 HEURES DONNÉES RÉELLES COMPLET")
    print("=" * 70)
    print("🚀 Test système complet avec données réelles")
    print("⏰ Durée: 2 heures")
    print("🎯 Objectif: Validation complète avant production")
    print("=" * 70)
    
    start_time = datetime.now()
    test_duration = timedelta(hours=2)
    
    print(f"⏰ Début test: {start_time.strftime('%H:%M:%S')}")
    print(f"⏰ Fin prévue: {(start_time + test_duration).strftime('%H:%M:%S')}")
    
    # Variables de suivi
    real_data_confirmations = 0
    mia_activities = 0
    trades_detected = 0
    signals_detected = 0
    connection_checks = 0
    price_checks = 0
    critical_errors = 0
    system_health_score = 100
    
    print("\n🔍 VÉRIFICATION PRÉ-TEST:")
    print("=" * 40)
    
    # 1. VÉRIFIER CONFIGURATION DONNÉES RÉELLES
    print("📋 Vérification configuration données réelles...")
    
    config_files = [
        "config/automation_config.py",
        "config/mia_ia_system_tws_paper_fixed.py", 
        "core/ibkr_connector.py",
        "data/market_data_feed.py"
    ]
    
    for config_file in config_files:
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Vérifier paramètres critiques
                checks = [
                    ("simulation_mode = False", "Mode simulation désactivé"),
                    ("USE_REAL_DATA = True", "Données réelles activées"),
                    ("FORCE_REAL_DATA = True", "Forçage données réelles"),
                    ("DataSource.IBKR", "Source IBKR configurée"),
                    ("port: 7497", "Port TWS correct")
                ]
                
                for check, description in checks:
                    if check in content:
                        print(f"   ✅ {description}")
                        real_data_confirmations += 1
                    else:
                        print(f"   ❌ {description} - MANQUANT")
                        critical_errors += 1
            except Exception as e:
                print(f"   ❌ Erreur lecture {config_file}: {e}")
                critical_errors += 1
    
    # 2. VÉRIFIER FICHIERS CRITIQUES
    print("\n📁 Vérification fichiers critiques...")
    
    critical_files = [
        "lance_mia_ia_tws.py",
        "launch_24_7_orderflow_trading.py",
        "config/automation_config.py",
        "core/ibkr_connector.py",
        "data/market_data_feed.py"
    ]
    
    for file_path in critical_files:
        if os.path.exists(file_path):
            print(f"   ✅ {file_path}")
        else:
            print(f"   ❌ {file_path} - MANQUANT")
            critical_errors += 1
    
    # 3. VÉRIFIER CONNEXION TWS
    print("\n🔌 Vérification connexion TWS...")
    try:
        result = subprocess.run(['netstat', '-an'], capture_output=True, text=True)
        if '127.0.0.1:7497' in result.stdout:
            print("   ✅ TWS connecté sur port 7497")
            connection_checks += 1
        else:
            print("   ❌ TWS non connecté sur port 7497")
            critical_errors += 1
    except Exception as e:
        print(f"   ❌ Erreur vérification TWS: {e}")
        critical_errors += 1
    
    # ÉVALUATION PRÉ-TEST
    print(f"\n📊 ÉVALUATION PRÉ-TEST:")
    print(f"   Confirmations données réelles: {real_data_confirmations}/20")
    print(f"   Erreurs critiques: {critical_errors}")
    print(f"   Score santé système: {max(0, 100 - critical_errors * 10)}%")
    
    if critical_errors > 0:
        print(f"\n❌ ERREURS CRITIQUES DÉTECTÉES - CORRECTION NÉCESSAIRE")
        print("💡 Veuillez corriger les erreurs avant de continuer")
        return False
    
    print(f"\n✅ PRÉ-TEST RÉUSSI - LANCEMENT SYSTÈME COMPLET")
    print("=" * 70)
    
    # LANCER LE SYSTÈME COMPLET
    print("\n🚀 LANCEMENT SYSTÈME MIA_IA_SYSTEM...")
    
    try:
        # Lancer le système en arrière-plan
        print("   📡 Démarrage lance_mia_ia_tws.py...")
        
        # Créer un processus pour le système principal
        mia_process = subprocess.Popen(
            [sys.executable, "lance_mia_ia_tws.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        print("   ✅ Système MIA lancé en arrière-plan")
        
        # MONITORING EN TEMPS RÉEL
        print("\n📊 MONITORING SYSTÈME COMPLET:")
        print("=" * 40)
        
        monitoring_start = datetime.now()
        
        try:
            while datetime.now() < start_time + test_duration:
                current_time = datetime.now()
                elapsed = current_time - start_time
                remaining = test_duration - elapsed
                
                print(f"\n⏰ {current_time.strftime('%H:%M:%S')} | "
                      f"Écoulé: {elapsed.total_seconds()/3600:.1f}h | "
                      f"Reste: {remaining.total_seconds()/3600:.1f}h")
                
                # VÉRIFIER PROCESSUS MIA
                if mia_process.poll() is None:
                    print("   ✅ Processus MIA actif")
                    mia_activities += 1
                else:
                    print("   ❌ Processus MIA arrêté")
                    critical_errors += 1
                    break
                
                # ANALYSER LOGS RÉCENTS
                print("   📄 Analyse logs récents...")
                
                log_files = []
                for pattern in ["logs/*.log", "*.log"]:
                    log_files.extend(glob.glob(pattern))
                
                for log_file in log_files:
                    try:
                        with open(log_file, 'r', encoding='utf-8') as f:
                            lines = f.readlines()
                        
                        # Analyser les dernières lignes
                        recent_lines = lines[-100:] if len(lines) > 100 else lines
                        
                        for line in recent_lines:
                            line = line.strip()
                            
                            # Vérifier données réelles
                            if "REAL_DATA" in line or "IBKR" in line or "TWS" in line:
                                if "connected" in line.lower() or "success" in line.lower():
                                    print(f"      ✅ Données réelles: {line[:60]}...")
                                    real_data_confirmations += 1
                            
                            # Vérifier activité MIA
                            if "MIA" in line or "TRADE" in line or "SIGNAL" in line:
                                print(f"      🎯 Activité MIA: {line[:60]}...")
                                mia_activities += 1
                                
                                if "TRADE" in line:
                                    trades_detected += 1
                                if "SIGNAL" in line:
                                    signals_detected += 1
                            
                            # Vérifier prix ES
                            if "ES" in line and any(char.isdigit() for char in line):
                                if "648" in line or "649" in line:  # Prix ES actuel
                                    print(f"      💰 Prix ES réel: {line[:60]}...")
                                    price_checks += 1
                            
                            # Vérifier erreurs critiques
                            if "ERROR" in line or "CRITICAL" in line or "FAILED" in line:
                                print(f"      ⚠️ Erreur détectée: {line[:60]}...")
                                critical_errors += 1
                    
                    except Exception as e:
                        print(f"      ❌ Erreur lecture {log_file}: {e}")
                
                # VÉRIFIER CONNEXION TWS
                try:
                    result = subprocess.run(['netstat', '-an'], capture_output=True, text=True)
                    if '127.0.0.1:7497' in result.stdout:
                        print("   🔌 TWS connecté")
                        connection_checks += 1
                    else:
                        print("   ❌ TWS déconnecté")
                        critical_errors += 1
                except Exception as e:
                    print(f"   ❌ Erreur vérification TWS: {e}")
                
                # CALCULER SCORE SANTÉ
                system_health_score = max(0, 100 - critical_errors * 5)
                
                print(f"   📊 Score santé: {system_health_score}%")
                print(f"   🎯 Trades: {trades_detected}")
                print(f"   📡 Signaux: {signals_detected}")
                
                # VÉRIFIER SEUILS CRITIQUES
                if critical_errors >= 5:
                    print("   🚨 TROP D'ERREURS CRITIQUES - ARRÊT TEST")
                    break
                
                if system_health_score < 50:
                    print("   🚨 SCORE SANTÉ TROP FAIBLE - ARRÊT TEST")
                    break
                
                # Attendre 2 minutes avant prochaine vérification
                time.sleep(120)
                
        except KeyboardInterrupt:
            print("\n⏹️ Test interrompu par l'utilisateur")
        
        # ARRÊTER LE SYSTÈME
        print("\n🛑 Arrêt du système MIA...")
        try:
            mia_process.terminate()
            mia_process.wait(timeout=10)
            print("   ✅ Système arrêté proprement")
        except subprocess.TimeoutExpired:
            mia_process.kill()
            print("   ⚠️ Système forcé à s'arrêter")
        
    except Exception as e:
        print(f"❌ Erreur lancement système: {e}")
        critical_errors += 1
    
    # RÉSULTATS FINAUX
    end_time = datetime.now()
    total_duration = end_time - start_time
    
    print("\n" + "=" * 70)
    print("📊 RÉSULTATS TEST 2 HEURES COMPLET")
    print("=" * 70)
    print(f"⏰ Durée totale: {total_duration}")
    print(f"🔍 Confirmations données réelles: {real_data_confirmations}")
    print(f"🔄 Activités MIA détectées: {mia_activities}")
    print(f"🎯 Trades détectés: {trades_detected}")
    print(f"📡 Signaux détectés: {signals_detected}")
    print(f"🔌 Vérifications connexion: {connection_checks}")
    print(f"💰 Vérifications prix: {price_checks}")
    print(f"❌ Erreurs critiques: {critical_errors}")
    print(f"🏥 Score santé final: {system_health_score}%")
    
    # ÉVALUATION FINALE
    print("\n💡 ÉVALUATION FINALE:")
    
    if real_data_confirmations >= 50:
        print("   ✅ Données réelles confirmées")
    else:
        print("   ❌ Données réelles insuffisantes")
    
    if mia_activities >= 20:
        print("   ✅ MIA fonctionne correctement")
    else:
        print("   ❌ Activité MIA faible")
    
    if connection_checks >= 5:
        print("   ✅ Connexion TWS stable")
    else:
        print("   ❌ Problèmes connexion TWS")
    
    if price_checks >= 5:
        print("   ✅ Prix ES réels détectés")
    else:
        print("   ❌ Prix ES non détectés")
    
    if critical_errors == 0:
        print("   ✅ Aucune erreur critique")
    else:
        print(f"   ❌ {critical_errors} erreurs critiques")
    
    if system_health_score >= 80:
        print("   ✅ Score santé excellent")
    elif system_health_score >= 60:
        print("   ⚠️ Score santé acceptable")
    else:
        print("   ❌ Score santé insuffisant")
    
    print("\n🎯 RECOMMANDATION FINALE:")
    if (real_data_confirmations >= 50 and mia_activities >= 20 and 
        connection_checks >= 5 and critical_errors == 0 and system_health_score >= 80):
        print("   ✅ SYSTÈME PRÊT POUR PRODUCTION - Test 2h réussi")
        print("   🚀 Vous pouvez maintenant lancer le trading live")
    else:
        print("   ❌ PROBLÈMES DÉTECTÉS - Correction nécessaire")
        print("   🔧 Vérifiez la configuration et les logs")
    
    print("=" * 70)
    
    return (real_data_confirmations >= 50 and mia_activities >= 20 and 
            connection_checks >= 5 and critical_errors == 0 and system_health_score >= 80)

if __name__ == "__main__":
    success = test_2h_donnees_reelles_complet()
    sys.exit(0 if success else 1)


