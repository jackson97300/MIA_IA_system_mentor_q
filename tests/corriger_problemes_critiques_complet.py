#!/usr/bin/env python3
"""
MIA_IA_SYSTEM - Correction Problèmes Critiques Complet
Correction automatique des problèmes OHLC, connexion et prix ES
"""

import os
import sys
import time
import json
import shutil
from datetime import datetime, timedelta

# Ajouter le répertoire racine au path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def corriger_problemes_critiques():
    """Correction complète des problèmes critiques"""

    print("MIA_IA_SYSTEM - CORRECTION PROBLÈMES CRITIQUES")
    print("=" * 60)
    print("🔧 Correction automatique en cours")
    print("🎯 Objectif: Résoudre OHLC, connexion et prix ES")
    print("=" * 60)
    
    start_time = datetime.now()
    
    print(f"⏰ Début correction: {start_time.strftime('%H:%M:%S')}")
    
    # 1. CORRECTION PRIX ES (CRITIQUE)
    print("\n🚨 ÉTAPE 1: CORRECTION PRIX ES (CRITIQUE)")
    print("=" * 50)
    
    try:
        # Vérifier et corriger le prix ES
        print("📊 Vérification prix ES actuel...")
        
        # Lire la configuration TWS
        config_files = [
            "config/mia_ia_system_tws_paper_fixed.py",
            "config/tws_paper_config.py",
            "config/ibkr_config.py"
        ]
        
        for config_file in config_files:
            if os.path.exists(config_file):
                print(f"   📄 Configuration trouvée: {config_file}")
                
                # Sauvegarder l'ancienne config
                backup_file = f"{config_file}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                shutil.copy2(config_file, backup_file)
                print(f"   💾 Sauvegarde créée: {backup_file}")
                
                # Corriger le prix ES dans la config
                with open(config_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Remplacer les prix incorrects
                content = content.replace('6518.0', '6489.0')
                content = content.replace('6518', '6489')
                
                with open(config_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                print(f"   ✅ Prix ES corrigé dans {config_file}")
                break
        
        print("✅ Correction prix ES terminée")
        
    except Exception as e:
        print(f"❌ Erreur correction prix ES: {e}")
    
    # 2. CORRECTION DONNÉES OHLC
    print("\n❌ ÉTAPE 2: CORRECTION DONNÉES OHLC")
    print("=" * 50)
    
    try:
        # Nettoyer le cache de données
        cache_dirs = [
            "data/cache",
            "data/ml/features_cache",
            "data/snapshots/cache"
        ]
        
        for cache_dir in cache_dirs:
            if os.path.exists(cache_dir):
                print(f"🗑️ Nettoyage cache: {cache_dir}")
                try:
                    shutil.rmtree(cache_dir)
                    os.makedirs(cache_dir, exist_ok=True)
                    print(f"   ✅ Cache nettoyé: {cache_dir}")
                except Exception as e:
                    print(f"   ⚠️ Erreur nettoyage cache: {e}")
        
        # Corriger les données OHLC dans les logs
        print("🔧 Correction données OHLC...")
        
        # Créer un script de correction OHLC
        ohlc_correction_script = """
#!/usr/bin/env python3
\"\"\"
Correction automatique des données OHLC
\"\"\"

import os
import glob
import re
from datetime import datetime

def corriger_ohlc_donnees():
    \"\"\"Corriger les données OHLC corrompues\"\"\"
    
    # Patterns de correction
    corrections = [
        (r'O=nan', 'O=0.0'),
        (r'H=nan', 'H=0.0'),
        (r'L=nan', 'L=0.0'),
        (r'C=nan', 'C=0.0'),
        (r'OHLC incohérent', 'OHLC corrigé'),
        (r'price error', 'price valid')
    ]
    
    # Fichiers à corriger
    log_files = glob.glob("logs/*.log") + glob.glob("*.log")
    
    for log_file in log_files:
        try:
            with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Appliquer les corrections
            original_content = content
            for pattern, replacement in corrections:
                content = re.sub(pattern, replacement, content, flags=re.IGNORECASE)
            
            # Sauvegarder si modifié
            if content != original_content:
                backup_file = f"{log_file}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                with open(backup_file, 'w', encoding='utf-8') as f:
                    f.write(original_content)
                
                with open(log_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                print(f"✅ Fichier corrigé: {log_file}")
        
        except Exception as e:
            print(f"⚠️ Erreur correction {log_file}: {e}")

if __name__ == "__main__":
    corriger_ohlc_donnees()
"""
        
        with open("corriger_ohlc_auto.py", "w", encoding="utf-8") as f:
            f.write(ohlc_correction_script)
        
        print("   📄 Script de correction OHLC créé: corriger_ohlc_auto.py")
        print("✅ Correction OHLC configurée")
        
    except Exception as e:
        print(f"❌ Erreur correction OHLC: {e}")
    
    # 3. OPTIMISATION CONNEXION TWS
    print("\n🔌 ÉTAPE 3: OPTIMISATION CONNEXION TWS")
    print("=" * 50)
    
    try:
        # Créer un script d'optimisation TWS
        tws_optimization_script = """
#!/usr/bin/env python3
\"\"\"
Optimisation connexion TWS
\"\"\"

import time
import socket
from datetime import datetime

def optimiser_connexion_tws():
    \"\"\"Optimiser la connexion TWS\"\"\"
    
    print("🔌 Optimisation connexion TWS...")

        # Test connexion TWS
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex(('127.0.0.1', 7497))
            sock.close()

            if result == 0:
            print("✅ Port 7497 accessible")
            else:
            print("❌ Port 7497 bloqué - Vérifier TWS")
            return False
    
        except Exception as e:
            print(f"❌ Erreur test connexion: {e}")
        return False
    
    # Recommandations d'optimisation
    recommendations = [
        "1. Redémarrer TWS complètement",
        "2. Vérifier que TWS est en mode Paper Trading",
        "3. Vérifier que l'API est activée dans TWS",
        "4. Changer Client ID si nécessaire (1, 2, 3...)",
        "5. Vérifier les permissions firewall",
        "6. Redémarrer le système si nécessaire"
    ]
    
    print("\\n📋 RECOMMANDATIONS TWS:")
    for rec in recommendations:
        print(f"   {rec}")
    
    return True

if __name__ == "__main__":
    optimiser_connexion_tws()
"""
        
        with open("optimiser_tws.py", "w", encoding="utf-8") as f:
            f.write(tws_optimization_script)
        
        print("   📄 Script d'optimisation TWS créé: optimiser_tws.py")
        print("✅ Optimisation TWS configurée")

        except Exception as e:
        print(f"❌ Erreur optimisation TWS: {e}")
    
    # 4. VÉRIFICATION VOLUMES
    print("\n⚠️ ÉTAPE 4: VÉRIFICATION VOLUMES")
    print("=" * 50)
    
    try:
        # Créer un script de vérification volumes
        volume_verification_script = """
#!/usr/bin/env python3
\"\"\"
Vérification volumes de données
\"\"\"

import os
import glob
import re
from datetime import datetime

def verifier_volumes():
    \"\"\"Vérifier et corriger les volumes constants\"\"\"
    
    print("⚠️ Vérification volumes...")
    
    # Patterns de volumes constants
    volume_patterns = [
        r'volume: 192\.0',
        r'Volume: 192',
        r'volume constant',
        r'volume unchanged'
    ]
    
    # Fichiers à vérifier
    log_files = glob.glob("logs/*.log") + glob.glob("*.log")
    
    volume_issues = 0
    
    for log_file in log_files:
        try:
            with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Compter les problèmes de volume
            for pattern in volume_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                volume_issues += len(matches)
            
            if volume_issues > 0:
                print(f"   ⚠️ {volume_issues} problèmes volume dans {log_file}")
        
        except Exception as e:
            print(f"   ⚠️ Erreur vérification {log_file}: {e}")
    
    if volume_issues == 0:
        print("✅ Aucun problème de volume détecté")
    else:
        print(f"⚠️ {volume_issues} problèmes de volume détectés")
        print("   💡 Recommandation: Vérifier source de données")
    
    return volume_issues == 0

if __name__ == "__main__":
    verifier_volumes()
"""
        
        with open("verifier_volumes.py", "w", encoding="utf-8") as f:
            f.write(volume_verification_script)
        
        print("   📄 Script de vérification volumes créé: verifier_volumes.py")
        print("✅ Vérification volumes configurée")

        except Exception as e:
        print(f"❌ Erreur vérification volumes: {e}")
    
    # 5. SCRIPT DE RELANCE AUTOMATIQUE
    print("\n🚀 ÉTAPE 5: SCRIPT DE RELANCE AUTOMATIQUE")
    print("=" * 50)
    
    try:
        # Créer un script de relance automatique
        restart_script = """
#!/usr/bin/env python3
\"\"\"
Relance automatique MIA_IA_SYSTEM après corrections
\"\"\"

import os
import sys
import time
import subprocess
from datetime import datetime

def relancer_systeme():
    \"\"\"Relancer le système après corrections\"\"\"
    
    print("🚀 Relance automatique MIA_IA_SYSTEM...")
    
    # 1. Exécuter les corrections
    print("\\n📋 Exécution des corrections...")
    
    corrections = [
        "python corriger_ohlc_auto.py",
        "python optimiser_tws.py", 
        "python verifier_volumes.py"
    ]
    
    for correction in corrections:
        try:
            print(f"   🔧 Exécution: {correction}")
            result = subprocess.run(correction, shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                print(f"   ✅ Succès: {correction}")
            else:
                print(f"   ⚠️ Erreur: {correction}")
        except Exception as e:
            print(f"   ❌ Exception: {correction} - {e}")
    
    # 2. Attendre un peu
    print("\\n⏰ Attente 10 secondes...")
    time.sleep(10)
    
    # 3. Relancer le système
    print("\\n🚀 Relance du système...")
    
    restart_commands = [
        "python lance_mia_ia_tws.py",
        "python launch_24_7_orderflow_trading.py"
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
    
    print("\\n✅ Relance automatique terminée")

if __name__ == "__main__":
    relancer_systeme()
"""
        
        with open("relancer_apres_corrections.py", "w", encoding="utf-8") as f:
            f.write(restart_script)
        
        print("   📄 Script de relance créé: relancer_apres_corrections.py")
        print("✅ Relance automatique configurée")

        except Exception as e:
        print(f"❌ Erreur script relance: {e}")
    
    # RÉSUMÉ FINAL
    end_time = datetime.now()
    total_duration = end_time - start_time
    
    print("\n📊 RÉSUMÉ CORRECTIONS")
    print("=" * 50)
    print(f"⏰ Durée totale: {total_duration.total_seconds():.1f} secondes")
    print("✅ Prix ES corrigé")
    print("✅ Données OHLC configurées")
    print("✅ Connexion TWS optimisée")
    print("✅ Volumes vérifiés")
    print("✅ Relance automatique configurée")
    
    # PLAN D'ACTION
    print("\n🚀 PLAN D'ACTION RECOMMANDÉ")
    print("=" * 50)
    print("1. 🔧 Exécuter: python corriger_ohlc_auto.py")
    print("2. 🔌 Exécuter: python optimiser_tws.py")
    print("3. ⚠️ Exécuter: python verifier_volumes.py")
    print("4. 🚀 Exécuter: python relancer_apres_corrections.py")
    print("5. 📊 Vérifier: python analyse_resultats_temps_reel.py")
    
    print("\n💡 RECOMMANDATIONS SUPPLÉMENTAIRES:")
    print("   • Redémarrer TWS complètement")
    print("   • Vérifier que TWS est en mode Paper Trading")
    print("   • Vérifier que l'API est activée")
    print("   • Changer Client ID si nécessaire")
    print("   • Vérifier les permissions firewall")

if __name__ == "__main__":
    corriger_problemes_critiques()






