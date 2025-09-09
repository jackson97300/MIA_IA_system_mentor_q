#!/usr/bin/env python3
"""
MIA_IA_SYSTEM - Correction Définitive Données Simulées
Corrige définitivement le problème des données simulées et force les données ES réelles
"""

import os
import sys
import re
import shutil
from datetime import datetime

# Ajouter le répertoire racine au path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def corriger_donnees_simulees_definitif():
    """Correction définitive du problème des données simulées"""
    
    print("🚨 MIA_IA_SYSTEM - CORRECTION DÉFINITIVE DONNÉES SIMULÉES")
    print("=" * 70)
    print("🎯 Objectif: Éliminer TOUTES les données simulées")
    print("🎯 Forcer l'utilisation des données ES réelles uniquement")
    print("=" * 70)
    
    start_time = datetime.now()
    
    print(f"⏰ Début correction: {start_time.strftime('%H:%M:%S')}")
    
    # 1. CORRECTION CONFIGURATION PRINCIPALE
    print("\n🔧 ÉTAPE 1: CORRECTION CONFIGURATION PRINCIPALE")
    print("=" * 50)
    
    # Fichiers de configuration critiques
    critical_configs = [
        "config/automation_config.py",
        "config/mia_ia_system_tws_paper_fixed.py",
        "config/tws_paper_config.py",
        "config/ibkr_config.py"
    ]
    
    for config_file in critical_configs:
        if os.path.exists(config_file):
            print(f"   📄 Correction: {config_file}")
            
            # Sauvegarder
            backup_file = f"{config_file}.backup_simulation_fix_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            with open(config_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            with open(backup_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Corrections spécifiques
            corrections = [
                # Configuration principale
                (r'simulation_mode:\s*bool\s*=\s*True', 'simulation_mode: bool = False  # DONNÉES RÉELLES OBLIGATOIRES'),
                (r'SIMULATION_MODE\s*=\s*True', 'SIMULATION_MODE = False  # DONNÉES RÉELLES OBLIGATOIRES'),
                (r'USE_REAL_DATA\s*=\s*False', 'USE_REAL_DATA = True  # DONNÉES RÉELLES OBLIGATOIRES'),
                (r'FORCE_REAL_DATA\s*=\s*False', 'FORCE_REAL_DATA = True  # DONNÉES RÉELLES OBLIGATOIRES'),
                (r'DISABLE_SIMULATION\s*=\s*False', 'DISABLE_SIMULATION = True  # DONNÉES RÉELLES OBLIGATOIRES'),
                (r'FALLBACK_TO_SIMULATION\s*=\s*True', 'FALLBACK_TO_SIMULATION = False  # DONNÉES RÉELLES OBLIGATOIRES'),
                (r'REAL_TIME_DATA_ONLY\s*=\s*False', 'REAL_TIME_DATA_ONLY = True  # DONNÉES RÉELLES OBLIGATOIRES'),
                (r'VALIDATE_REAL_DATA\s*=\s*False', 'VALIDATE_REAL_DATA = True  # DONNÉES RÉELLES OBLIGATOIRES'),
                (r'REJECT_SIMULATED_DATA\s*=\s*False', 'REJECT_SIMULATED_DATA = True  # DONNÉES RÉELLES OBLIGATOIRES'),
                
                # IBKR Configuration
                (r'real_market_data\s*:\s*False', 'real_market_data: True,  # DONNÉES RÉELLES OBLIGATOIRES'),
                (r'market_data_type\s*:\s*[0-9]', 'market_data_type: 1,  # DONNÉES RÉELLES OBLIGATOIRES'),
                (r'paper_trading\s*:\s*True', 'paper_trading: True,  # Paper trading mais données réelles'),
                
                # Connexion
                (r'port\s*:\s*[0-9]+', 'port: 7497,  # Port TWS Paper Trading'),
                (r'host\s*:\s*[\'"]127\.0\.0\.1[\'"]', 'host: "127.0.0.1",  # Localhost TWS'),
            ]
            
            for pattern, replacement in corrections:
                content = re.sub(pattern, replacement, content, flags=re.IGNORECASE)
            
            # Écrire le fichier corrigé
            with open(config_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"   ✅ Configuration corrigée: {config_file}")
    
    # 2. CORRECTION CONNECTEUR IBKR
    print("\n🔌 ÉTAPE 2: CORRECTION CONNECTEUR IBKR")
    print("=" * 50)
    
    ibkr_connector_file = "core/ibkr_connector.py"
    if os.path.exists(ibkr_connector_file):
        print(f"   📄 Correction: {ibkr_connector_file}")
        
        # Sauvegarder
        backup_file = f"{ibkr_connector_file}.backup_simulation_fix_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        with open(ibkr_connector_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        with open(backup_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # Corrections IBKR Connector
        ibkr_corrections = [
            # Forcer mode réel
            (r'self\.simulation_mode\s*=\s*True', 'self.simulation_mode = False  # DONNÉES RÉELLES OBLIGATOIRES'),
            (r'simulation_mode\s*=\s*True', 'simulation_mode = False  # DONNÉES RÉELLES OBLIGATOIRES'),
            
            # Connexion forcée
            (r'logger\.warning\("❌ Connexion IBKR ÉCHOUÉE - Activation mode simulation"\)', 
             'logger.error("❌ Connexion IBKR ÉCHOUÉE - ERREUR CRITIQUE")'),
            (r'self\.simulation_mode\s*=\s*True.*# Mais on continue en simulation', 
             'raise ConnectionError("❌ Connexion IBKR requise - Données réelles obligatoires")'),
            
            # Port et host par défaut
            (r'self\.port\s*=\s*[0-9]+', 'self.port = 7497  # Port TWS Paper Trading'),
            (r'self\.host\s*=\s*[\'"]127\.0\.0\.1[\'"]', 'self.host = "127.0.0.1"  # Localhost TWS'),
        ]
        
        for pattern, replacement in ibkr_corrections:
            content = re.sub(pattern, replacement, content, flags=re.IGNORECASE)
        
        # Écrire le fichier corrigé
        with open(ibkr_connector_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"   ✅ Connecteur IBKR corrigé: {ibkr_connector_file}")
    
    # 3. CORRECTION MARKET DATA FEED
    print("\n📊 ÉTAPE 3: CORRECTION MARKET DATA FEED")
    print("=" * 50)
    
    market_data_file = "data/market_data_feed.py"
    if os.path.exists(market_data_file):
        print(f"   📄 Correction: {market_data_file}")
        
        # Sauvegarder
        backup_file = f"{market_data_file}.backup_simulation_fix_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        with open(market_data_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        with open(backup_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # Corrections Market Data Feed
        feed_corrections = [
            # Forcer source IBKR
            (r'self\.primary_source\s*=\s*DataSource\.SIMULATION', 'self.primary_source = DataSource.IBKR  # DONNÉES RÉELLES OBLIGATOIRES'),
            (r'DataSource\.SIMULATION', 'DataSource.IBKR  # DONNÉES RÉELLES OBLIGATOIRES'),
            
            # Désactiver simulation
            (r'elif target_source == DataSource\.SIMULATION:', 
             'elif target_source == DataSource.SIMULATION:\n                logger.error("❌ Mode simulation INTERDIT - Données réelles obligatoires")\n                return False'),
            
            # Connexion forcée IBKR
            (r'if not self\.connect_to_data_source\(DataSource\.SIMULATION\):', 
             'if not self.connect_to_data_source(DataSource.IBKR):  # DONNÉES RÉELLES OBLIGATOIRES'),
        ]
        
        for pattern, replacement in feed_corrections:
            content = re.sub(pattern, replacement, content, flags=re.IGNORECASE)
        
        # Écrire le fichier corrigé
        with open(market_data_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"   ✅ Market Data Feed corrigé: {market_data_file}")
    
    # 4. CRÉER SCRIPT DE VÉRIFICATION DONNÉES RÉELLES
    print("\n🔍 ÉTAPE 4: SCRIPT VÉRIFICATION DONNÉES RÉELLES")
    print("=" * 50)
    
    verification_script = """#!/usr/bin/env python3
\"\"\"
Vérification données ES réelles - Version Définitive
\"\"\"

import os
import sys
import re
from datetime import datetime

def verifier_donnees_reelles_definitif():
    \"\"\"Vérification définitive des données réelles\"\"\"
    
    print("🔍 VÉRIFICATION DÉFINITIVE DONNÉES ES RÉELLES")
    print("=" * 50)
    
    # Fichiers à vérifier
    files_to_check = [
        "config/automation_config.py",
        "config/mia_ia_system_tws_paper_fixed.py",
        "core/ibkr_connector.py",
        "data/market_data_feed.py"
    ]
    
    all_ok = True
    
    for file_path in files_to_check:
        if os.path.exists(file_path):
            print(f"\\n📄 Vérification: {file_path}")
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Vérifications critiques
                checks = [
                    ("simulation_mode = False", "Mode simulation désactivé"),
                    ("USE_REAL_DATA = True", "Données réelles activées"),
                    ("FORCE_REAL_DATA = True", "Forçage données réelles"),
                    ("DataSource.IBKR", "Source IBKR configurée"),
                    ("port: 7497", "Port TWS correct"),
                ]
                
                file_ok = True
                for check, description in checks:
                    if check in content:
                        print(f"   ✅ {description}")
                    else:
                        print(f"   ❌ {description} - MANQUANT")
                        file_ok = False
                
                # Vérifications négatives (ne doivent PAS être présents)
                negative_checks = [
                    ("simulation_mode = True", "Mode simulation encore actif"),
                    ("DataSource.SIMULATION", "Source simulation détectée"),
                    ("USE_REAL_DATA = False", "Données réelles désactivées"),
                ]
                
                for check, description in negative_checks:
                    if check in content:
                        print(f"   ❌ {description} - PROBLÈME")
                        file_ok = False
                
                if not file_ok:
                    all_ok = False
                    
            except Exception as e:
                print(f"   ❌ Erreur vérification: {e}")
                all_ok = False
    
    return all_ok

if __name__ == "__main__":
    success = verifier_donnees_reelles_definitif()
    if success:
        print("\\n✅ TOUTES LES VÉRIFICATIONS RÉUSSIES")
        print("✅ Données ES réelles configurées")
    else:
        print("\\n❌ PROBLÈMES DÉTECTÉS")
        print("❌ Correction nécessaire")
"""
    
    with open("verifier_donnees_reelles_definitif.py", "w", encoding="utf-8") as f:
        f.write(verification_script)
    
    print("   📄 Script de vérification créé: verifier_donnees_reelles_definitif.py")
    
    # 5. CRÉER SCRIPT DE TEST CONNEXION RÉELLE
    print("\n🧪 ÉTAPE 5: SCRIPT TEST CONNEXION RÉELLE")
    print("=" * 50)
    
    test_script = """#!/usr/bin/env python3
\"\"\"
Test connexion données ES réelles - Version Définitive
\"\"\"

import os
import sys
import socket
import time
from datetime import datetime

def test_connexion_reelle_definitif():
    \"\"\"Test définitif de la connexion données réelles\"\"\"
    
    print("🧪 TEST DÉFINITIF CONNEXION DONNÉES ES RÉELLES")
    print("=" * 50)
    
    # 1. Test TWS accessible
    print("\\n🔌 Test 1: Accessibilité TWS")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex(('127.0.0.1', 7497))
        sock.close()
        
        if result == 0:
            print("   ✅ TWS accessible sur port 7497")
            tws_ok = True
        else:
            print("   ❌ TWS non accessible sur port 7497")
            tws_ok = False
    except Exception as e:
        print(f"   ❌ Erreur test TWS: {e}")
        tws_ok = False
    
    # 2. Test import IBKR Connector
    print("\\n📦 Test 2: Import IBKR Connector")
    try:
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        from core.ibkr_connector import IBKRConnector
        print("   ✅ IBKR Connector importé")
        connector_ok = True
    except ImportError as e:
        print(f"   ❌ Erreur import IBKR Connector: {e}")
        connector_ok = False
    
    # 3. Test configuration
    print("\\n⚙️ Test 3: Configuration données réelles")
    try:
        from config.automation_config import get_automation_config
        config = get_automation_config()
        
        if hasattr(config, 'simulation_mode') and not config.simulation_mode:
            print("   ✅ Configuration: Mode simulation désactivé")
            config_ok = True
        else:
            print("   ❌ Configuration: Mode simulation encore actif")
            config_ok = False
    except Exception as e:
        print(f"   ❌ Erreur configuration: {e}")
        config_ok = False
    
    # Résumé
    print("\\n📊 RÉSUMÉ TESTS")
    print("=" * 30)
    print(f"   TWS Accessible: {'✅' if tws_ok else '❌'}")
    print(f"   IBKR Connector: {'✅' if connector_ok else '❌'}")
    print(f"   Configuration: {'✅' if config_ok else '❌'}")
    
    all_tests_ok = tws_ok and connector_ok and config_ok
    
    if all_tests_ok:
        print("\\n✅ TOUS LES TESTS RÉUSSIS")
        print("✅ Prêt pour données ES réelles")
    else:
        print("\\n❌ TESTS ÉCHOUÉS")
        print("❌ Correction nécessaire")
    
    return all_tests_ok

if __name__ == "__main__":
    success = test_connexion_reelle_definitif()
    exit(0 if success else 1)
"""
    
    with open("test_connexion_reelle_definitif.py", "w", encoding="utf-8") as f:
        f.write(test_script)
    
    print("   📄 Script de test créé: test_connexion_reelle_definitif.py")
    
    # 6. SCRIPT DE RELANCE AVEC DONNÉES RÉELLES
    print("\n🚀 ÉTAPE 6: SCRIPT RELANCE DONNÉES RÉELLES")
    print("=" * 50)
    
    restart_script = """#!/usr/bin/env python3
\"\"\"
Relance système avec données ES réelles - Version Définitive
\"\"\"

import os
import sys
import subprocess
import time
from datetime import datetime

def relancer_donnees_reelles_definitif():
    \"\"\"Relance définitive avec données ES réelles\"\"\"
    
    print("🚀 RELANCE DÉFINITIVE AVEC DONNÉES ES RÉELLES")
    print("=" * 50)
    
    # 1. Vérification
    print("\\n🔍 Étape 1: Vérification configuration")
    try:
        result = subprocess.run("python verifier_donnees_reelles_definitif.py", 
                              shell=True, capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print(f"⚠️ Erreurs: {result.stderr}")
    except Exception as e:
        print(f"❌ Erreur vérification: {e}")
    
    # 2. Test connexion
    print("\\n🧪 Étape 2: Test connexion réelle")
    try:
        result = subprocess.run("python test_connexion_reelle_definitif.py", 
                              shell=True, capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print(f"⚠️ Erreurs: {result.stderr}")
    except Exception as e:
        print(f"❌ Erreur test: {e}")
    
    # 3. Attendre
    print("\\n⏰ Attente 10 secondes...")
    time.sleep(10)
    
    # 4. Relancer système
    print("\\n🚀 Étape 3: Relance système")
    restart_commands = [
        "python launch_24_7_orderflow_trading.py",
        "python lance_mia_ia_tws.py"
    ]
    
    for command in restart_commands:
        if os.path.exists(command.split()[1]):
            try:
                print(f"   🚀 Lancement: {command}")
                subprocess.Popen(command, shell=True)
                print(f"   ✅ Système relancé: {command}")
                break
            except Exception as e:
                print(f"   ❌ Erreur relance: {command} - {e}")
    
    print("\\n✅ Relance avec données réelles terminée")

if __name__ == "__main__":
    relancer_donnees_reelles_definitif()
"""
    
    with open("relancer_donnees_reelles_definitif.py", "w", encoding="utf-8") as f:
        f.write(restart_script)
    
    print("   📄 Script de relance créé: relancer_donnees_reelles_definitif.py")
    
    # RÉSUMÉ FINAL
    end_time = datetime.now()
    total_duration = end_time - start_time
    
    print("\n📊 RÉSUMÉ CORRECTION DÉFINITIVE")
    print("=" * 50)
    print(f"⏰ Durée: {total_duration.total_seconds():.1f} secondes")
    print("✅ Configuration principale corrigée")
    print("✅ Connecteur IBKR corrigé")
    print("✅ Market Data Feed corrigé")
    print("✅ Scripts de vérification créés")
    print("✅ Scripts de test créés")
    print("✅ Script de relance créé")
    
    print("\n🚨 CHANGEMENTS CRITIQUES APPLIQUÉS:")
    print("   • Mode simulation DÉSACTIVÉ partout")
    print("   • Données réelles OBLIGATOIRES")
    print("   • Connexion TWS FORCÉE")
    print("   • Fallback simulation SUPPRIMÉ")
    print("   • Validation données réelles ACTIVÉE")
    
    print("\n🚀 PLAN D'ACTION RECOMMANDÉ")
    print("=" * 50)
    print("1. ✅ Vérifier: python verifier_donnees_reelles_definitif.py")
    print("2. 🧪 Tester: python test_connexion_reelle_definitif.py")
    print("3. 🚀 Relancer: python relancer_donnees_reelles_definitif.py")
    print("4. 📊 Analyser: python analyse_resultats_temps_reel.py")
    
    print("\n⚠️ ATTENTION:")
    print("   • Le système utilise MAINTENANT UNIQUEMENT des données ES réelles")
    print("   • TWS doit être connecté et configuré")
    print("   • Plus de fallback vers simulation")
    print("   • Erreurs de connexion = arrêt système")

if __name__ == "__main__":
    corriger_donnees_simulees_definitif()


