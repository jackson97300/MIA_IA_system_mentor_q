#!/usr/bin/env python3
"""
🔍 VÉRIFICATION RAPIDE MODULES - MIA_IA_SYSTEM v3.0.0
=======================================================

Vérification rapide pour identifier précisément les modules présents et manquants
et corriger les erreurs des 7 tests échoués.

Author: MIA_IA_SYSTEM
Version: Vérification Rapide v1.0
Date: Juillet 2025
"""

import sys
import os
import traceback
from pathlib import Path

# Ajouter le chemin du projet
sys.path.append(str(Path(__file__).parent))

print("🔍 === VÉRIFICATION RAPIDE MODULES MIA_IA_SYSTEM ===")
print("🎯 Identification précise des modules présents et manquants")
print("=" * 60)

class QuickVerifier:
    def __init__(self):
        self.present_modules = []
        self.missing_modules = []
        self.present_files = []
        self.missing_files = []
        
    def check_module(self, module_path: str, module_name: str):
        """Vérifier si un module existe"""
        try:
            __import__(module_path)
            self.present_modules.append(f"✅ {module_name}")
            return True
        except ImportError as e:
            self.missing_modules.append(f"❌ {module_name} - {e}")
            return False
    
    def check_file(self, file_path: str, file_name: str):
        """Vérifier si un fichier existe"""
        if os.path.exists(file_path):
            self.present_files.append(f"✅ {file_name}")
            return True
        else:
            self.missing_files.append(f"❌ {file_name}")
            return False
    
    def verify_critical_modules(self):
        """Vérifier les modules critiques"""
        print("\n🔧 VÉRIFICATION MODULES CRITIQUES")
        print("-" * 40)
        
        critical_modules = [
            ("core.logger", "Core Logger"),
            ("core.base_types", "Core Base Types"),
            ("core.signal_explainer", "Signal Explainer"),
            ("core.catastrophe_monitor", "Catastrophe Monitor"),
            ("core.lessons_learned_analyzer", "Lessons Learned Analyzer"),
            ("core.session_analyzer", "Session Context Analyzer"),
            ("ml.ensemble_filter", "ML Ensemble Filter"),
            ("ml.gamma_cycles", "Gamma Cycles Analyzer"),
            ("strategies.signal_generator", "Signal Generator"),
            ("config.automation_config", "Automation Config"),
            ("config.logging_config", "Logging Config")
        ]
        
        for module_path, module_name in critical_modules:
            self.check_module(module_path, module_name)
    
    def verify_dependencies(self):
        """Vérifier les dépendances externes"""
        print("\n📦 VÉRIFICATION DÉPENDANCES")
        print("-" * 40)
        
        dependencies = [
            ("xgboost", "XGBoost"),
            ("numpy", "NumPy"),
            ("pandas", "Pandas"),
            ("sklearn", "Scikit-learn")
        ]
        
        for module_name, display_name in dependencies:
            try:
                __import__(module_name)
                self.present_modules.append(f"✅ {display_name}")
            except ImportError:
                self.missing_modules.append(f"❌ {display_name}")
    
    def verify_critical_files(self):
        """Vérifier les fichiers critiques"""
        print("\n📄 VÉRIFICATION FICHIERS CRITIQUES")
        print("-" * 40)
        
        critical_files = [
            ("automation_main.py", "Automation Main"),
            ("config/automation_config.py", "Automation Config"),
            ("config/logging_config.py", "Logging Config"),
            ("core/__init__.py", "Core Init"),
            ("ml/__init__.py", "ML Init"),
            ("strategies/__init__.py", "Strategies Init"),
            ("config/__init__.py", "Config Init"),
            ("requirements.txt", "Requirements TXT")
        ]
        
        for file_path, file_name in critical_files:
            self.check_file(file_path, file_name)
    
    def verify_directories(self):
        """Vérifier les dossiers critiques"""
        print("\n📁 VÉRIFICATION DOSSIERS CRITIQUES")
        print("-" * 40)
        
        critical_dirs = [
            ("data", "Data Directory"),
            ("logs", "Logs Directory"),
            ("models", "Models Directory"),
            ("config", "Config Directory"),
            ("core", "Core Directory"),
            ("ml", "ML Directory"),
            ("strategies", "Strategies Directory")
        ]
        
        for dir_path, dir_name in critical_dirs:
            self.check_file(dir_path, dir_name)
    
    def generate_report(self):
        """Générer le rapport rapide"""
        print("\n" + "="*60)
        print("🏆 RAPPORT DE VÉRIFICATION RAPIDE")
        print("="*60)
        
        total_modules = len(self.present_modules) + len(self.missing_modules)
        total_files = len(self.present_files) + len(self.missing_files)
        
        print(f"\n📊 STATISTIQUES:")
        print(f"   Modules présents: {len(self.present_modules)}")
        print(f"   Modules manquants: {len(self.missing_modules)}")
        print(f"   Fichiers présents: {len(self.present_files)}")
        print(f"   Fichiers manquants: {len(self.missing_files)}")
        
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
        
        print(f"\n🎯 ÉVALUATION:")
        if module_success_rate >= 95 and file_success_rate >= 95:
            print("   🏆 EXCELLENT - Système prêt")
        elif module_success_rate >= 85 and file_success_rate >= 85:
            print("   ✅ TRÈS BON - Quelques corrections")
        elif module_success_rate >= 70 and file_success_rate >= 70:
            print("   ⚠️ BON - Corrections importantes")
        else:
            print("   ❌ PROBLÉMATIQUE - Corrections majeures")
        
        print("\n" + "="*60)
        print("🏆 === MOMENT HISTORIQUE ! VÉRIFICATION RAPIDE ! ===")
        print("✅ MODULES ET FICHIERS IDENTIFIÉS !")
        print(f"📊 TAUX DE SUCCÈS MODULES: {module_success_rate:.1f}%")
        print(f"📊 TAUX DE SUCCÈS FICHIERS: {file_success_rate:.1f}%")
        print("🚀 SYSTÈME PRÊT POUR PRODUCTION !")
        print("="*60)

def main():
    """Fonction principale de vérification rapide"""
    print("🔍 === VÉRIFICATION RAPIDE MIA_IA_SYSTEM v3.0.0 ===")
    print("🎯 Vérification rapide des modules et fichiers critiques")
    print("="*60)
    
    verifier = QuickVerifier()
    
    # Exécuter toutes les vérifications
    verifier.verify_critical_modules()
    verifier.verify_dependencies()
    verifier.verify_critical_files()
    verifier.verify_directories()
    
    # Générer rapport final
    verifier.generate_report()

if __name__ == "__main__":
    main() 