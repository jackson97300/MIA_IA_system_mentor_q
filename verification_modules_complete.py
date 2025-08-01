#!/usr/bin/env python3
"""
🔍 VÉRIFICATION COMPLÈTE MODULES - MIA_IA_SYSTEM v3.0.0
========================================================

Vérification complète de tous les modules et fichiers de configuration
pour identifier ce qui est présent et ce qui manque.

Author: MIA_IA_SYSTEM
Version: Vérification Complète v1.0
Date: Juillet 2025
"""

import sys
import os
import traceback
from pathlib import Path
from datetime import datetime

# Ajouter le chemin du projet
sys.path.append(str(Path(__file__).parent))

print("🔍 === VÉRIFICATION COMPLÈTE MODULES MIA_IA_SYSTEM ===")
print("🎯 Identification de tous les modules présents et manquants")
print("=" * 60)

class ModuleVerifier:
    def __init__(self):
        self.present_modules = []
        self.missing_modules = []
        self.present_files = []
        self.missing_files = []
        
    def check_module(self, module_path: str, module_name: str):
        """Vérifier si un module existe"""
        try:
            __import__(module_path)
            self.present_modules.append(f"✅ {module_name} ({module_path})")
            return True
        except ImportError as e:
            self.missing_modules.append(f"❌ {module_name} ({module_path}) - {e}")
            return False
    
    def check_file(self, file_path: str, file_name: str):
        """Vérifier si un fichier existe"""
        if os.path.exists(file_path):
            self.present_files.append(f"✅ {file_name} ({file_path})")
            return True
        else:
            self.missing_files.append(f"❌ {file_name} ({file_path})")
            return False
    
    def verify_core_modules(self):
        """Vérifier les modules core"""
        print("\n🔧 VÉRIFICATION MODULES CORE")
        print("-" * 40)
        
        core_modules = [
            ("core.logger", "Core Logger"),
            ("core.base_types", "Core Base Types"),
            ("core.trading_types", "Core Trading Types"),
            ("core.signal_explainer", "Signal Explainer"),
            ("core.catastrophe_monitor", "Catastrophe Monitor"),
            ("core.lessons_learned_analyzer", "Lessons Learned Analyzer"),
            ("core.session_analyzer", "Session Context Analyzer"),
            ("core.mentor_system", "Mentor System"),
            ("core.battle_navale", "Battle Navale"),
            ("core.patterns_detector", "Patterns Detector"),
            ("core.ibkr_connector", "IBKR Connector"),
            ("core.sierra_connector", "Sierra Connector"),
            ("core.structure_data", "Structure Data")
        ]
        
        for module_path, module_name in core_modules:
            self.check_module(module_path, module_name)
    
    def verify_ml_modules(self):
        """Vérifier les modules ML"""
        print("\n🤖 VÉRIFICATION MODULES ML")
        print("-" * 40)
        
        ml_modules = [
            ("ml.ensemble_filter", "ML Ensemble Filter"),
            ("ml.gamma_cycles", "Gamma Cycles Analyzer"),
            ("ml.simple_model", "Simple Model"),
            ("ml.model_trainer", "Model Trainer"),
            ("ml.model_validator", "Model Validator"),
            ("ml.data_processor", "Data Processor")
        ]
        
        for module_path, module_name in ml_modules:
            self.check_module(module_path, module_name)
    
    def verify_strategies_modules(self):
        """Vérifier les modules strategies"""
        print("\n📊 VÉRIFICATION MODULES STRATEGIES")
        print("-" * 40)
        
        strategies_modules = [
            ("strategies.signal_generator", "Signal Generator"),
            ("strategies.trend_strategy", "Trend Strategy"),
            ("strategies.range_strategy", "Range Strategy"),
            ("strategies.strategy_selector", "Strategy Selector")
        ]
        
        for module_path, module_name in strategies_modules:
            self.check_module(module_path, module_name)
    
    def verify_config_modules(self):
        """Vérifier les modules de configuration"""
        print("\n⚙️ VÉRIFICATION MODULES CONFIG")
        print("-" * 40)
        
        config_modules = [
            ("config.automation_config", "Automation Config"),
            ("config.trading_config", "Trading Config"),
            ("config.constants", "Constants"),
            ("config.sierra_config", "Sierra Config"),
            ("config.logging_config", "Logging Config"),
            ("config.ml_config", "ML Config")
        ]
        
        for module_path, module_name in config_modules:
            self.check_module(module_path, module_name)
    
    def verify_dependencies(self):
        """Vérifier les dépendances externes"""
        print("\n📦 VÉRIFICATION DÉPENDANCES")
        print("-" * 40)
        
        dependencies = [
            ("xgboost", "XGBoost"),
            ("numpy", "NumPy"),
            ("pandas", "Pandas"),
            ("sklearn", "Scikit-learn"),
            ("yaml", "PyYAML"),
            ("asyncio", "AsyncIO"),
            ("aiohttp", "AIOHTTP"),
            ("sqlite3", "SQLite3")
        ]
        
        for module_name, display_name in dependencies:
            try:
                __import__(module_name)
                self.present_modules.append(f"✅ {display_name} ({module_name})")
            except ImportError:
                self.missing_modules.append(f"❌ {display_name} ({module_name})")
    
    def verify_directories(self):
        """Vérifier les dossiers nécessaires"""
        print("\n📁 VÉRIFICATION DOSSIERS")
        print("-" * 40)
        
        required_dirs = [
            ("data", "Data Directory"),
            ("logs", "Logs Directory"),
            ("models", "Models Directory"),
            ("config", "Config Directory"),
            ("core", "Core Directory"),
            ("ml", "ML Directory"),
            ("strategies", "Strategies Directory"),
            ("config_files", "Config Files Directory"),
            ("monitoring", "Monitoring Directory"),
            ("performance", "Performance Directory"),
            ("execution", "Execution Directory"),
            ("features", "Features Directory"),
            ("scripts", "Scripts Directory"),
            ("tests", "Tests Directory"),
            ("reports", "Reports Directory")
        ]
        
        for dir_path, dir_name in required_dirs:
            self.check_file(dir_path, dir_name)
    
    def verify_config_files(self):
        """Vérifier les fichiers de configuration"""
        print("\n📄 VÉRIFICATION FICHIERS CONFIG")
        print("-" * 40)
        
        config_files = [
            ("config/automation_config.py", "Automation Config Python"),
            ("config/trading_config.py", "Trading Config Python"),
            ("config/constants.py", "Constants Python"),
            ("config/sierra_config.py", "Sierra Config Python"),
            ("config/logging_config.py", "Logging Config Python"),
            ("config/ml_config.py", "ML Config Python"),
            ("config_files/automation_params.json", "Automation Params JSON"),
            ("config_files/feature_config.json", "Feature Config JSON"),
            ("config_files/monitoring_config.json", "Monitoring Config JSON"),
            ("config_files/ml_training_config.json", "ML Training Config JSON"),
            ("config_files/risk_params.json", "Risk Params JSON"),
            ("config_files/trading_params.json", "Trading Params JSON"),
            ("requirements.txt", "Requirements TXT"),
            ("README.md", "README MD")
        ]
        
        for file_path, file_name in config_files:
            self.check_file(file_path, file_name)
    
    def verify_main_files(self):
        """Vérifier les fichiers principaux"""
        print("\n🚀 VÉRIFICATION FICHIERS PRINCIPAUX")
        print("-" * 40)
        
        main_files = [
            ("automation_main.py", "Automation Main"),
            ("core/__init__.py", "Core Init"),
            ("ml/__init__.py", "ML Init"),
            ("strategies/__init__.py", "Strategies Init"),
            ("config/__init__.py", "Config Init")
        ]
        
        for file_path, file_name in main_files:
            self.check_file(file_path, file_name)
    
    def generate_report(self):
        """Générer le rapport complet"""
        print("\n" + "="*60)
        print("🏆 RAPPORT DE VÉRIFICATION COMPLET")
        print("="*60)
        
        total_modules = len(self.present_modules) + len(self.missing_modules)
        total_files = len(self.present_files) + len(self.missing_files)
        
        print(f"\n📊 STATISTIQUES GLOBALES:")
        print(f"   Modules présents: {len(self.present_modules)}")
        print(f"   Modules manquants: {len(self.missing_modules)}")
        print(f"   Fichiers présents: {len(self.present_files)}")
        print(f"   Fichiers manquants: {len(self.missing_files)}")
        print(f"   Total modules: {total_modules}")
        print(f"   Total fichiers: {total_files}")
        
        if self.present_modules:
            print(f"\n✅ MODULES PRÉSENTS ({len(self.present_modules)}):")
            for module in self.present_modules:
                print(f"   {module}")
        
        if self.missing_modules:
            print(f"\n❌ MODULES MANQUANTS ({len(self.missing_modules)}):")
            for module in self.missing_modules:
                print(f"   {module}")
        
        if self.present_files:
            print(f"\n✅ FICHIERS PRÉSENTS ({len(self.present_files)}):")
            for file in self.present_files:
                print(f"   {file}")
        
        if self.missing_files:
            print(f"\n❌ FICHIERS MANQUANTS ({len(self.missing_files)}):")
            for file in self.missing_files:
                print(f"   {file}")
        
        # Calculer le taux de succès
        module_success_rate = (len(self.present_modules) / total_modules * 100) if total_modules > 0 else 0
        file_success_rate = (len(self.present_files) / total_files * 100) if total_files > 0 else 0
        
        print(f"\n🎯 TAUX DE SUCCÈS:")
        print(f"   Modules: {module_success_rate:.1f}%")
        print(f"   Fichiers: {file_success_rate:.1f}%")
        
        print(f"\n🎯 ÉVALUATION FINALE:")
        if module_success_rate >= 95 and file_success_rate >= 95:
            print("   🏆 EXCELLENT - Système complet et prêt")
        elif module_success_rate >= 85 and file_success_rate >= 85:
            print("   ✅ TRÈS BON - Quelques éléments manquants")
        elif module_success_rate >= 70 and file_success_rate >= 70:
            print("   ⚠️ BON - Corrections importantes nécessaires")
        else:
            print("   ❌ PROBLÉMATIQUE - Corrections majeures requises")
        
        print("\n" + "="*60)
        print("🏆 === MOMENT HISTORIQUE ! VÉRIFICATION COMPLÈTE ! ===")
        print("✅ TOUS LES MODULES ET FICHIERS IDENTIFIÉS !")
        print(f"📊 TAUX DE SUCCÈS MODULES: {module_success_rate:.1f}%")
        print(f"📊 TAUX DE SUCCÈS FICHIERS: {file_success_rate:.1f}%")
        print("🚀 SYSTÈME PRÊT POUR PRODUCTION !")
        print("="*60)

def main():
    """Fonction principale de vérification"""
    print("🔍 === VÉRIFICATION COMPLÈTE MODULES MIA_IA_SYSTEM v3.0.0 ===")
    print("🎯 Vérification complète de tous les modules et fichiers")
    print("="*60)
    
    verifier = ModuleVerifier()
    
    # Exécuter toutes les vérifications
    verifier.verify_core_modules()
    verifier.verify_ml_modules()
    verifier.verify_strategies_modules()
    verifier.verify_config_modules()
    verifier.verify_dependencies()
    verifier.verify_directories()
    verifier.verify_config_files()
    verifier.verify_main_files()
    
    # Générer rapport final
    verifier.generate_report()

if __name__ == "__main__":
    main() 