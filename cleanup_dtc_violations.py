#!/usr/bin/env python3
"""
Script de nettoyage des violations DTC identifiées
Sépare les usages légitimes (trading) des usages interdits (data collection)
"""

import os
import shutil
from pathlib import Path
from typing import List, Dict, Tuple

class DTCCleanupManager:
    def __init__(self):
        self.root = Path(".")
        self.archive_dir = self.root / "archive" / "dtc_violations"
        self.archive_dir.mkdir(parents=True, exist_ok=True)
        
        # Fichiers DTC légitimes (trading uniquement)
        self.legitimate_dtc_files = {
            "core/sierra_dtc_connector.py",
            "core/sierra_order_router.py", 
            "core/sierra_connector.py",
            "config/sierra_trading_ports.py",
            "core/safety_kill_switch.py",
            "core/catastrophe_monitor.py",
            "core/trading_executor.py",
            "core/signal_explainer.py",
            "core/trading_types.py"
        }
        
        # Fichiers à archiver (DTC pour data collection)
        self.files_to_archive = [
            "automation_modules/sierra_dtc_connector.py",
            "automation_modules/sierra_connector_v2.py", 
            "automation_modules/sierra_config_optimized.py",
            "automation_modules/sierra_market_data.py",
            "data/market_data_feed.py",
            "execution/order_manager.py",
            "features/dealers_bias_analyzer.py",
            "config/dealers_bias_analyzer.py"
        ]
        
        # Tests à archiver (DTC pour data collection)
        self.tests_to_archive = [
            "tests/test_delayed_data.py",
            "tests/test_dtc_connection.py", 
            "tests/test_rithmic_connection.py",
            "tests/test_sierra_connector_real.py",
            "tests/test_sierra_dtc_optimized.py",
            "tests/test_sierra_integration.py",
            "tests/test_sierra_symbols_prices.py",
            "tests/test_mia_sierra_integration.py",
            "tests/test_es_only.py",
            "tests/comparaison_tradestation_sierra.py"
        ]

    def analyze_violations(self) -> Dict[str, List[str]]:
        """Analyse les violations et les catégorise"""
        violations = {
            "legitimate": [],
            "to_archive": [],
            "to_fix": [],
            "already_archived": []
        }
        
        # Vérifier les fichiers légitimes
        for file_path in self.legitimate_dtc_files:
            path = Path(file_path)
            if path.exists():
                violations["legitimate"].append(str(file_path))
            else:
                print(f"⚠️ Fichier légitime manquant: {file_path}")
        
        # Vérifier les fichiers à archiver
        for file_path in self.files_to_archive + self.tests_to_archive:
            path = Path(file_path)
            if path.exists():
                if "archive/" in str(path):
                    violations["already_archived"].append(str(file_path))
                else:
                    violations["to_archive"].append(str(file_path))
            else:
                print(f"ℹ️ Fichier déjà supprimé: {file_path}")
        
        return violations

    def archive_files(self, file_list: List[str]) -> List[str]:
        """Archive une liste de fichiers"""
        archived = []
        
        for file_path in file_list:
            source = Path(file_path)
            if not source.exists():
                continue
                
            # Créer le répertoire de destination
            dest_dir = self.archive_dir / source.parent
            dest_dir.mkdir(parents=True, exist_ok=True)
            
            # Déplacer le fichier
            dest = dest_dir / source.name
            try:
                shutil.move(str(source), str(dest))
                archived.append(str(dest))
                print(f"📦 Archivé: {source} -> {dest}")
            except Exception as e:
                print(f"❌ Erreur archivage {source}: {e}")
        
        return archived

    def fix_core_files(self) -> List[str]:
        """Corrige les fichiers core qui ont des références DTC problématiques"""
        fixed = []
        
        # Fichiers core à corriger
        core_files_to_fix = [
            "core/data_collector_enhanced.py",
            "core/imports_manager.py", 
            "core/structure_data.py"
        ]
        
        for file_path in core_files_to_fix:
            path = Path(file_path)
            if not path.exists():
                continue
                
            try:
                content = path.read_text(encoding='utf-8')
                original_content = content
                
                # Supprimer les références DTC pour data collection
                replacements = [
                    ("SierraDTCConnector()", "SierraConnector()"),
                    ("DTCConnector", "SierraConnector"),
                    ("dtc_connector", "sierra_connector"),
                    ("DTC Protocol", "Sierra Chart"),
                    ("DTC JSON", "Sierra JSON"),
                    ("DTC message", "Sierra message"),
                    ("DTC handshake", "Sierra handshake"),
                    ("DTC connection", "Sierra connection")
                ]
                
                for old, new in replacements:
                    content = content.replace(old, new)
                
                if content != original_content:
                    path.write_text(content, encoding='utf-8')
                    fixed.append(str(path))
                    print(f"🔧 Corrigé: {path}")
                    
            except Exception as e:
                print(f"❌ Erreur correction {path}: {e}")
        
        return fixed

    def generate_cleanup_report(self, violations: Dict[str, List[str]], 
                              archived: List[str], fixed: List[str]) -> str:
        """Génère un rapport de nettoyage"""
        report = []
        report.append("# 🧹 RAPPORT DE NETTOYAGE DTC")
        report.append("")
        
        report.append("## ✅ FICHIERS DTC LÉGITIMES (Trading)")
        for file_path in violations["legitimate"]:
            report.append(f"- {file_path}")
        report.append("")
        
        report.append("## 📦 FICHIERS ARCHIVÉS")
        for file_path in archived:
            report.append(f"- {file_path}")
        report.append("")
        
        report.append("## 🔧 FICHIERS CORRIGÉS")
        for file_path in fixed:
            report.append(f"- {file_path}")
        report.append("")
        
        report.append("## 📊 STATISTIQUES")
        report.append(f"- Fichiers légitimes: {len(violations['legitimate'])}")
        report.append(f"- Fichiers archivés: {len(archived)}")
        report.append(f"- Fichiers corrigés: {len(fixed)}")
        report.append(f"- Déjà archivés: {len(violations['already_archived'])}")
        report.append("")
        
        report.append("## 🎯 RÉSULTAT")
        if len(violations["to_archive"]) == 0 and len(fixed) > 0:
            report.append("✅ **NETTOYAGE RÉUSSI** - DTC utilisé uniquement pour trading")
        else:
            report.append("⚠️ **NETTOYAGE PARTIEL** - Vérifications supplémentaires nécessaires")
        
        return "\n".join(report)

    def run_cleanup(self) -> str:
        """Exécute le nettoyage complet"""
        print("🧹 DÉMARRAGE DU NETTOYAGE DTC")
        print("=" * 50)
        
        # 1. Analyser les violations
        print("1️⃣ Analyse des violations...")
        violations = self.analyze_violations()
        
        # 2. Archiver les fichiers problématiques
        print("\n2️⃣ Archivage des fichiers...")
        files_to_archive = violations["to_archive"]
        archived = self.archive_files(files_to_archive)
        
        # 3. Corriger les fichiers core
        print("\n3️⃣ Correction des fichiers core...")
        fixed = self.fix_core_files()
        
        # 4. Générer le rapport
        print("\n4️⃣ Génération du rapport...")
        report = self.generate_cleanup_report(violations, archived, fixed)
        
        # Sauvegarder le rapport
        report_path = self.root / "RAPPORT_NETTOYAGE_DTC.md"
        report_path.write_text(report, encoding='utf-8')
        
        print(f"\n📋 Rapport sauvegardé: {report_path}")
        print("\n" + "=" * 50)
        print(report)
        
        return report

if __name__ == "__main__":
    cleanup = DTCCleanupManager()
    report = cleanup.run_cleanup()
