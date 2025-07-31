#!/usr/bin/env python3
"""
DEBUG DATA_COLLECTION - Diagnostic détaillé des erreurs
"""

import sys
import os
import traceback
from datetime import datetime

# Couleurs
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_success(msg):
    print(f"{Colors.OKGREEN}✅ {msg}{Colors.ENDC}")

def print_error(msg):
    print(f"{Colors.FAIL}❌ {msg}{Colors.ENDC}")

def print_info(msg):
    print(f"{Colors.OKBLUE}ℹ️  {msg}{Colors.ENDC}")

def print_warning(msg):
    print(f"{Colors.WARNING}⚠️  {msg}{Colors.ENDC}")

print(f"{Colors.BOLD}{Colors.HEADER}DIAGNOSTIC DATA_COLLECTION_MAIN{Colors.ENDC}\n")

# 1. Vérifier le fichier existe
print_info("1. Vérification du fichier data_collection_main.py...")
if os.path.exists("data_collection_main.py"):
    print_success("Fichier trouvé")
    with open("data_collection_main.py", "r", encoding="utf-8") as f:
        content = f.read()
    print_info(f"   Taille: {len(content)} caractères")
    
    # Vérifier les imports dans le fichier
    required_imports = [
        "from data.data_collector import DataCollector",
        "from data.analytics import DataAnalytics",
        "from monitoring.performance_tracker import PerformanceTracker",
        "from monitoring.alert_system import AlertSystem",
        "from config.automation_config import get_automation_config"
    ]
    
    print_info("\n2. Vérification des imports dans le fichier...")
    for imp in required_imports:
        if imp in content:
            print_success(f"   Trouvé: {imp}")
        else:
            # Vérifier variantes possibles
            if "analytics import DataAnalytics" in content:
                print_success(f"   Trouvé (variante): DataAnalytics")
            elif "analytics import Analytics" in content:
                print_error(f"   PROBLÈME: Import 'Analytics' au lieu de 'DataAnalytics'")
else:
    print_error("Fichier non trouvé!")
    sys.exit(1)

# 2. Essayer d'importer étape par étape
print_info("\n3. Test des imports individuels...")

# Test DataCollector
try:
    from data.data_collector import DataCollector, DataQuality, DataPeriod
    print_success("Import data.data_collector réussi")
except Exception as e:
    print_error(f"Erreur import data.data_collector: {e}")
    traceback.print_exc()

# Test Analytics
try:
    from data.analytics import DataAnalytics, AnalysisType, TimeFrame
    print_success("Import data.analytics réussi")
    print_info(f"   Type DataAnalytics: {DataAnalytics}")
except Exception as e:
    print_error(f"Erreur import data.analytics: {e}")
    traceback.print_exc()

# Test monitoring
try:
    from monitoring.performance_tracker import PerformanceTracker
    print_success("Import monitoring.performance_tracker réussi")
except Exception as e:
    print_error(f"Erreur import monitoring.performance_tracker: {e}")

try:
    from monitoring.alert_system import AlertSystem, AlertLevel
    print_success("Import monitoring.alert_system réussi")
except Exception as e:
    print_error(f"Erreur import monitoring.alert_system: {e}")

# Test config
try:
    from config.automation_config import get_automation_config
    print_success("Import config.automation_config réussi")
except Exception as e:
    print_error(f"Erreur import config.automation_config: {e}")
    # Essayer alternative
    try:
        from config import get_automation_config
        print_success("Import config (alternatif) réussi")
    except:
        print_error("Aucune méthode d'import config ne fonctionne")

# Test logger
try:
    from core.logger import setup_logging
    print_success("Import core.logger réussi")
except Exception as e:
    print_error(f"Erreur import core.logger: {e}")

# 3. Essayer d'importer DataCollectionManager
print_info("\n4. Test import DataCollectionManager...")
try:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from data_collection_main import DataCollectionManager
    print_success("Import DataCollectionManager réussi!")
    
    # Essayer de créer une instance
    print_info("\n5. Test création instance...")
    try:
        manager = DataCollectionManager()
        print_success("Instance créée avec succès!")
        
        # Vérifier les attributs
        print_info("\n6. Vérification des attributs...")
        attrs = ['config', 'collector', 'analytics', 'performance_tracker', 'alert_system']
        for attr in attrs:
            if hasattr(manager, attr):
                obj = getattr(manager, attr)
                print_success(f"   {attr}: {type(obj).__name__}")
            else:
                print_error(f"   {attr}: MANQUANT")
        
        # Test méthodes
        print_info("\n7. Test des méthodes...")
        methods = ['get_status', 'analyze_data_quality', 'generate_summary']
        for method in methods:
            if hasattr(manager, method):
                print_success(f"   {method}: présent")
            else:
                print_error(f"   {method}: MANQUANT")
                
    except Exception as e:
        print_error(f"Erreur création instance: {e}")
        print_info("\nDétails de l'erreur:")
        traceback.print_exc()
        
except Exception as e:
    print_error(f"Erreur import DataCollectionManager: {e}")
    print_info("\nDétails de l'erreur:")
    traceback.print_exc()
    
    # Analyser le type d'erreur
    error_str = str(e)
    if "Analytics" in error_str and "DataAnalytics" not in error_str:
        print_warning("\nPROBLÈME DÉTECTÉ: Le fichier utilise 'Analytics' au lieu de 'DataAnalytics'")
        print_info("Solution: Remplacer 'Analytics' par 'DataAnalytics' dans data_collection_main.py")
    elif "numpy" in error_str:
        print_warning("\nPROBLÈME DÉTECTÉ: numpy n'est pas importé")
        print_info("Solution: Ajouter 'import numpy as np' dans data_collection_main.py")

# 4. Vérifier les dépendances numpy/pandas
print_info("\n8. Vérification des dépendances...")
try:
    import numpy as np
    print_success("numpy installé")
except:
    print_error("numpy NON installé - pip install numpy")

try:
    import pandas as pd
    print_success("pandas installé")
except:
    print_error("pandas NON installé - pip install pandas")

print(f"\n{Colors.BOLD}Fin du diagnostic{Colors.ENDC}")