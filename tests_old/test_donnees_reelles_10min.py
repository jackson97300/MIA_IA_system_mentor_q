#!/usr/bin/env python3
"""
MIA_IA_SYSTEM - Test Données Réelles 10 Minutes
Vérifie que MIA fonctionne avec les données réelles
"""

import os
import sys
import time
import json
import glob
from datetime import datetime, timedelta
import subprocess
import threading

# Ajouter le répertoire racine au path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_donnees_reelles_10min():
    """Test de 10 minutes avec données réelles"""
    
    print("MIA_IA_SYSTEM - TEST DONNÉES RÉELLES 10 MINUTES")
    print("=" * 60)
    print("🔍 Test système avec données réelles")
    print("⏰ Durée: 10 minutes")
    print("🎯 Objectif: Confirmer données réelles + fonctionnement MIA")
    print("=" * 60)
    
    start_time = datetime.now()
    test_duration = timedelta(minutes=10)
    
    print(f"⏰ Début test: {start_time.strftime('%H:%M:%S')}")
    print(f"⏰ Fin prévue: {(start_time + test_duration).strftime('%H:%M:%S')}")
    
    # Variables de suivi
    real_data_confirmations = 0
    mia_activities = 0
    trades_detected = 0
    signals_detected = 0
    connection_checks = 0
    price_checks = 0
    
    print("\n📊 MONITORING DONNÉES RÉELLES:")
    print("=" * 40)
    
    try:
        while datetime.now() < start_time + test_duration:
            current_time = datetime.now()
            elapsed = current_time - start_time
            remaining = test_duration - elapsed
            
            print(f"\n⏰ {current_time.strftime('%H:%M:%S')} | "
                  f"Écoulé: {elapsed.total_seconds():.0f}s | "
                  f"Reste: {remaining.total_seconds():.0f}s")
            
            # 1. VÉRIFIER CONFIGURATION DONNÉES RÉELLES
            print("🔍 Vérification configuration données réelles...")
            
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
                    except Exception as e:
                        print(f"   ❌ Erreur lecture {config_file}: {e}")
            
            # 2. VÉRIFIER CONNEXION TWS
            print("\n🔌 Vérification connexion TWS...")
            try:
                # Vérifier si TWS est connecté
                result = subprocess.run(['netstat', '-an'], capture_output=True, text=True)
                if '127.0.0.1:7497' in result.stdout:
                    print("   ✅ TWS connecté sur port 7497")
                    connection_checks += 1
                else:
                    print("   ❌ TWS non connecté sur port 7497")
            except Exception as e:
                print(f"   ❌ Erreur vérification TWS: {e}")
            
            # 3. ANALYSER LOGS RÉCENTS
            print("\n📄 Analyse logs récents...")
            
            log_files = []
            for pattern in ["logs/*.log", "*.log"]:
                log_files.extend(glob.glob(pattern))
            
            for log_file in log_files:
                try:
                    with open(log_file, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                    
                    # Analyser les dernières lignes
                    recent_lines = lines[-50:] if len(lines) > 50 else lines
                    
                    for line in recent_lines:
                        line = line.strip()
                        
                        # Vérifier données réelles
                        if "REAL_DATA" in line or "IBKR" in line or "TWS" in line:
                            if "connected" in line.lower() or "success" in line.lower():
                                print(f"   ✅ Données réelles: {line[:80]}...")
                                real_data_confirmations += 1
                        
                        # Vérifier activité MIA
                        if "MIA" in line or "TRADE" in line or "SIGNAL" in line:
                            print(f"   🎯 Activité MIA: {line[:80]}...")
                            mia_activities += 1
                            
                            if "TRADE" in line:
                                trades_detected += 1
                            if "SIGNAL" in line:
                                signals_detected += 1
                        
                        # Vérifier prix ES
                        if "ES" in line and any(char.isdigit() for char in line):
                            if "648" in line or "649" in line:  # Prix ES actuel
                                print(f"   💰 Prix ES réel: {line[:80]}...")
                                price_checks += 1
                
                except Exception as e:
                    print(f"   ❌ Erreur lecture {log_file}: {e}")
            
            # 4. VÉRIFIER PROCESSUS MIA
            print("\n🔄 Vérification processus MIA...")
            try:
                result = subprocess.run(['tasklist'], capture_output=True, text=True)
                if 'python' in result.stdout.lower():
                    print("   ✅ Processus Python actif")
                    mia_activities += 1
                else:
                    print("   ❌ Aucun processus Python détecté")
            except Exception as e:
                print(f"   ❌ Erreur vérification processus: {e}")
            
            # Attendre 30 secondes avant prochaine vérification
            time.sleep(30)
            
    except KeyboardInterrupt:
        print("\n⏹️ Test interrompu par l'utilisateur")
    
    # RÉSULTATS FINAUX
    end_time = datetime.now()
    total_duration = end_time - start_time
    
    print("\n" + "=" * 60)
    print("📊 RÉSULTATS TEST DONNÉES RÉELLES")
    print("=" * 60)
    print(f"⏰ Durée totale: {total_duration}")
    print(f"🔍 Confirmations données réelles: {real_data_confirmations}")
    print(f"🔄 Activités MIA détectées: {mia_activities}")
    print(f"🎯 Trades détectés: {trades_detected}")
    print(f"📡 Signaux détectés: {signals_detected}")
    print(f"🔌 Vérifications connexion: {connection_checks}")
    print(f"💰 Vérifications prix: {price_checks}")
    
    # ÉVALUATION
    print("\n💡 ÉVALUATION:")
    if real_data_confirmations >= 10:
        print("   ✅ Données réelles confirmées")
    else:
        print("   ❌ Données réelles insuffisantes")
    
    if mia_activities >= 5:
        print("   ✅ MIA fonctionne correctement")
    else:
        print("   ❌ Activité MIA faible")
    
    if connection_checks >= 1:
        print("   ✅ Connexion TWS stable")
    else:
        print("   ❌ Problèmes connexion TWS")
    
    if price_checks >= 1:
        print("   ✅ Prix ES réels détectés")
    else:
        print("   ❌ Prix ES non détectés")
    
    print("\n🎯 RECOMMANDATION:")
    if real_data_confirmations >= 10 and mia_activities >= 5:
        print("   ✅ Système prêt pour test 2h - Données réelles confirmées")
    else:
        print("   ❌ Problèmes détectés - Correction nécessaire")
    
    print("=" * 60)

if __name__ == "__main__":
    test_donnees_reelles_10min()


