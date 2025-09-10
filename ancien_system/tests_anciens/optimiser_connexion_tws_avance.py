#!/usr/bin/env python3
"""
MIA_IA_SYSTEM - Optimisation Connexion TWS Avancée
Optimisation spécifique des problèmes de connexion (94 détectés)
"""

import os
import sys
import time
import socket
import subprocess
from datetime import datetime

def optimiser_connexion_tws_avance():
    """Optimisation avancée de la connexion TWS"""
    
    print("🔌 MIA_IA_SYSTEM - OPTIMISATION CONNEXION TWS AVANCÉE")
    print("=" * 60)
    print("🎯 Objectif: Réduire les 94 problèmes connexion")
    print("=" * 60)
    
    start_time = datetime.now()
    
    # 1. DIAGNOSTIC CONNEXION ACTUELLE
    print("\n🔍 ÉTAPE 1: DIAGNOSTIC CONNEXION ACTUELLE")
    print("=" * 50)
    
    # Test port TWS
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex(('127.0.0.1', 7497))
        sock.close()
        
        if result == 0:
            print("✅ Port 7497 (TWS) accessible")
            tws_status = "CONNECTED"
        else:
            print("❌ Port 7497 (TWS) bloqué")
            tws_status = "BLOCKED"
    except Exception as e:
        print(f"❌ Erreur test TWS: {e}")
        tws_status = "ERROR"
    
    # Test port Gateway
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex(('127.0.0.1', 4002))
        sock.close()
        
        if result == 0:
            print("✅ Port 4002 (Gateway) accessible")
            gateway_status = "CONNECTED"
        else:
            print("❌ Port 4002 (Gateway) bloqué")
            gateway_status = "BLOCKED"
    except Exception as e:
        print(f"❌ Erreur test Gateway: {e}")
        gateway_status = "ERROR"
    
    # 2. OPTIMISATION CONFIGURATION TWS
    print("\n🔧 ÉTAPE 2: OPTIMISATION CONFIGURATION TWS")
    print("=" * 50)
    
    # Créer script de configuration TWS optimisée
    tws_config_script = """
#!/usr/bin/env python3
\"\"\"
Configuration TWS optimisée pour MIA_IA_SYSTEM
\"\"\"

import os
import sys
from datetime import datetime

def configurer_tws_optimise():
    \"\"\"Configurer TWS pour performance optimale\"\"\"
    
    print("🔧 Configuration TWS optimisée...")
    
    # Paramètres de connexion optimisés
    config_optimisations = {
        'IBKR_HOST': '127.0.0.1',
        'IBKR_PORT': 7497,
        'IBKR_CLIENT_ID': 1,
        'IBKR_TIMEOUT': 60,  # Augmenté de 30 à 60
        'IBKR_RETRY_ATTEMPTS': 5,  # Augmenté de 3 à 5
        'IBKR_RETRY_DELAY': 10,  # Augmenté de 5 à 10
        'IBKR_HEARTBEAT_INTERVAL': 30,  # Nouveau paramètre
        'IBKR_CONNECTION_TIMEOUT': 120,  # Nouveau paramètre
        'IBKR_MAX_RECONNECT_ATTEMPTS': 10,  # Nouveau paramètre
        'IBKR_RECONNECT_DELAY': 15,  # Nouveau paramètre
        'ENABLE_CONNECTION_MONITORING': True,  # Nouveau paramètre
        'CONNECTION_HEALTH_CHECK_INTERVAL': 30,  # Nouveau paramètre
        'AUTO_RECONNECT_ON_FAILURE': True,  # Nouveau paramètre
        'LOG_CONNECTION_EVENTS': True,  # Nouveau paramètre
        'VALIDATE_CONNECTION_BEFORE_TRADE': True,  # Nouveau paramètre
    }
    
    # Fichiers de configuration à mettre à jour
    config_files = [
        "config/mia_ia_system_tws_paper_fixed.py",
        "config/tws_paper_config.py",
        "config/ibkr_config.py",
        "config/automation_config.py"
    ]
    
    for config_file in config_files:
        if os.path.exists(config_file):
            print(f"   📄 Mise à jour: {config_file}")
            
            # Sauvegarder l'ancienne config
            backup_file = f"{config_file}.backup_optimisation_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            with open(config_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            with open(backup_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Appliquer les optimisations
            for key, value in config_optimisations.items():
                if isinstance(value, str):
                    content = content.replace(f"{key} = ", f"{key} = '{value}'  # OPTIMISÉ")
                else:
                    content = content.replace(f"{key} = ", f"{key} = {value}  # OPTIMISÉ")
            
            with open(config_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"   ✅ Configuration optimisée: {config_file}")
    
    print("✅ Configuration TWS optimisée terminée")

if __name__ == "__main__":
    configurer_tws_optimise()
"""
    
    with open("configurer_tws_optimise.py", "w", encoding="utf-8") as f:
        f.write(tws_config_script)
    
    print("   📄 Script de configuration TWS créé: configurer_tws_optimise.py")
    
    # 3. SCRIPT DE MONITORING CONNEXION
    print("\n📊 ÉTAPE 3: SCRIPT DE MONITORING CONNEXION")
    print("=" * 50)
    
    monitoring_script = """
#!/usr/bin/env python3
\"\"\"
Monitoring connexion TWS en temps réel
\"\"\"

import time
import socket
import threading
from datetime import datetime

class TWSConnectionMonitor:
    \"\"\"Moniteur de connexion TWS en temps réel\"\"\"
    
    def __init__(self):
        self.is_monitoring = False
        self.connection_issues = 0
        self.last_check = None
        self.check_interval = 30  # secondes
        
    def start_monitoring(self):
        \"\"\"Démarrer le monitoring\"\"\"
        self.is_monitoring = True
        print("📊 Monitoring connexion TWS démarré...")
        
        while self.is_monitoring:
            try:
                self.check_connection()
                time.sleep(self.check_interval)
            except KeyboardInterrupt:
                print("\\n🛑 Monitoring arrêté")
                break
            except Exception as e:
                print(f"❌ Erreur monitoring: {e}")
                time.sleep(5)
    
    def check_connection(self):
        \"\"\"Vérifier la connexion TWS\"\"\"
        current_time = datetime.now()
        
        try:
            # Test connexion TWS
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10)
            result = sock.connect_ex(('127.0.0.1', 7497))
            sock.close()
            
            if result == 0:
                status = "✅ CONNECTÉ"
                if self.connection_issues > 0:
                    print(f"🔄 Reconnexion réussie à {current_time.strftime('%H:%M:%S')}")
                    self.connection_issues = 0
            else:
                status = "❌ DÉCONNECTÉ"
                self.connection_issues += 1
                print(f"⚠️ Problème connexion #{self.connection_issues} à {current_time.strftime('%H:%M:%S')}")
            
            self.last_check = current_time
            
        except Exception as e:
            status = f"❌ ERREUR: {e}"
            self.connection_issues += 1
        
        # Afficher statut toutes les 5 minutes
        if not self.last_check or (current_time - self.last_check).seconds >= 300:
            print(f"📊 {current_time.strftime('%H:%M:%S')} - TWS: {status}")

if __name__ == "__main__":
    monitor = TWSConnectionMonitor()
    monitor.start_monitoring()
"""
    
    with open("monitor_connexion_tws.py", "w", encoding="utf-8") as f:
        f.write(monitoring_script)
    
    print("   📄 Script de monitoring créé: monitor_connexion_tws.py")
    
    # 4. RECOMMANDATIONS SPÉCIFIQUES
    print("\n💡 ÉTAPE 4: RECOMMANDATIONS SPÉCIFIQUES")
    print("=" * 50)
    
    recommendations = [
        "🚨 ACTIONS IMMÉDIATES:",
        "   1. Redémarrer TWS complètement",
        "   2. Vérifier que TWS est en mode Paper Trading",
        "   3. Vérifier que l'API est activée dans TWS",
        "   4. Changer Client ID si nécessaire (1, 2, 3...)",
        "",
        "🔧 OPTIMISATIONS CONFIGURATION:",
        "   5. Exécuter: python configurer_tws_optimise.py",
        "   6. Augmenter timeout de 30s à 60s",
        "   7. Augmenter retry attempts de 3 à 5",
        "   8. Activer monitoring connexion",
        "",
        "📊 MONITORING CONTINU:",
        "   9. Lancer: python monitor_connexion_tws.py",
        "   10. Surveiller les reconnexions automatiques",
        "",
        "🛡️ SÉCURITÉ RÉSEAU:",
        "   11. Vérifier les permissions firewall",
        "   12. Désactiver antivirus temporairement",
        "   13. Vérifier qu'aucun autre logiciel utilise le port 7497"
    ]
    
    for rec in recommendations:
        print(rec)
    
    # 5. PLAN D'ACTION FINAL
    print("\n🚀 PLAN D'ACTION FINAL")
    print("=" * 50)
    print("1. 🔧 Exécuter: python configurer_tws_optimise.py")
    print("2. 🔄 Redémarrer TWS manuellement")
    print("3. 📊 Lancer: python monitor_connexion_tws.py")
    print("4. 🚀 Relancer: python relancer_apres_corrections.py")
    print("5. ✅ Vérifier: python analyse_resultats_temps_reel.py")
    
    # RÉSUMÉ
    end_time = datetime.now()
    total_duration = end_time - start_time
    
    print(f"\n📊 RÉSUMÉ OPTIMISATION")
    print("=" * 50)
    print(f"⏰ Durée: {total_duration.total_seconds():.1f} secondes")
    print(f"🔌 TWS Status: {tws_status}")
    print(f"🔌 Gateway Status: {gateway_status}")
    print("✅ Scripts d'optimisation créés")
    print("✅ Monitoring configuré")
    print("✅ Recommandations fournies")

if __name__ == "__main__":
    optimiser_connexion_tws_avance()


