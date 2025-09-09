#!/usr/bin/env python3
"""
🧹 SCRIPT DE NETTOYAGE RACINE - MIA_IA_SYSTEM
==============================================

Script automatique pour nettoyer la racine du projet et éviter la pollution
par les fichiers de test et temporaires.

Usage:
    python scripts/cleanup_root.py --dry-run    # Simulation
    python scripts/cleanup_root.py --clean      # Nettoyage réel
    python scripts/cleanup_root.py --organize   # Réorganisation
"""

import os
import shutil
import argparse
from pathlib import Path
from datetime import datetime
from typing import List, Set

class RootCleaner:
    """Nettoyeur de racine automatique"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.cleaned_files: List[str] = []
        self.cleaned_dirs: List[str] = []
        
        # Patterns de fichiers à nettoyer
        self.test_patterns = [
            "test_*.py",
            "*_test.py", 
            "test_ibkr_*.py",
            "test_ib_gateway_*.py",
            "test_tws_*.py",
            "test_download_*.py",
            "test_backtest_*.py",
            "test_*.md",
            "GUIDE_*.md",
            "RESUME_*.md", 
            "RAPPORT_*.md",
            "ANALYSE_*.md"
        ]
        
        # Fichiers spécifiques à nettoyer
        self.specific_files = [
            "download_es_data.py",
            "download_historical_data.py", 
            "generate_*.py",
            "backtest_hybrid.py",
            "run_backtest_phase1.py",
            "backtesting_es_complete.py",
            "find_*.py",
            "verify_*.py",
            "check_*.py",
            "diagnostic_*.py",
            "config_ib_gateway_guide.md",
            "FONCTIONNALITES_DETAILLEES_MIA_IA_SYSTEM.md",
            "ARCHITECTURE_DETAILLEE_MIA_IA_SYSTEM.md",
            "ANALYSE_COMPLETE_BOT_MIA_IA_SYSTEM.md"
        ]
        
        # Dossiers à nettoyer
        self.cleanup_dirs = [
            "test_results",
            "results", 
            "reports",
            "backups",
            "encoding_fix_backup",
            "ultra_aggressive_backup",
            "syntax_fix_backup",
            "specific_fix_backup", 
            "empty_lines_fix_backup",
            "critical_fix_backup",
            "tests_15min_1hour",
            "DOCUMENT JACKSON",
            "A FAIRE",
            "__pycache__"
        ]
        
        # Dossiers à conserver
        self.keep_dirs = {
            "core", "config", "execution", "features", "strategies",
            "ml", "monitoring", "data", "performance", "models",
            "tests", "docs", "scripts", "logs", "automation_modules",
            "config_files", ".git"
        }
    
    def find_files_to_clean(self) -> Set[Path]:
        """Trouve tous les fichiers à nettoyer"""
        files_to_clean = set()
        
        # Recherche par patterns
        for pattern in self.test_patterns + self.specific_files:
            for file_path in self.project_root.glob(pattern):
                if file_path.is_file():
                    files_to_clean.add(file_path)
        
        # Recherche fichiers temporaires
        for file_path in self.project_root.iterdir():
            if file_path.is_file():
                name = file_path.name
                # Fichiers avec timestamps
                if any(char.isdigit() for char in name) and any(ext in name for ext in ['.pdf', '.json', '.csv']):
                    if '_2025' in name or '_2024' in name:
                        files_to_clean.add(file_path)
                
                # Fichiers backup
                if any(suffix in name for suffix in ['.bak', '.backup', '_backup']):
                    files_to_clean.add(file_path)
        
        return files_to_clean
    
    def find_dirs_to_clean(self) -> Set[Path]:
        """Trouve tous les dossiers à nettoyer"""
        dirs_to_clean = set()
        
        for dir_name in self.cleanup_dirs:
            dir_path = self.project_root / dir_name
            if dir_path.exists() and dir_path.is_dir():
                dirs_to_clean.add(dir_path)
        
        return dirs_to_clean
    
    def dry_run(self):
        """Simulation du nettoyage"""
        print("🔍 === SIMULATION NETTOYAGE RACINE ===")
        
        files_to_clean = self.find_files_to_clean()
        dirs_to_clean = self.find_dirs_to_clean()
        
        print(f"\n📁 Fichiers à nettoyer ({len(files_to_clean)}):")
        for file_path in sorted(files_to_clean):
            size = file_path.stat().st_size / 1024  # KB
            print(f"  ❌ {file_path.name} ({size:.1f} KB)")
        
        print(f"\n📂 Dossiers à nettoyer ({len(dirs_to_clean)}):")
        for dir_path in sorted(dirs_to_clean):
            try:
                size = sum(f.stat().st_size for f in dir_path.rglob('*') if f.is_file()) / 1024 / 1024  # MB
                print(f"  ❌ {dir_path.name}/ ({size:.1f} MB)")
            except:
                print(f"  ❌ {dir_path.name}/ (erreur calcul taille)")
        
        total_files = len(files_to_clean)
        total_dirs = len(dirs_to_clean)
        
        print(f"\n📊 RÉSUMÉ:")
        print(f"  Fichiers: {total_files}")
        print(f"  Dossiers: {total_dirs}")
        print(f"  Total: {total_files + total_dirs} éléments")
        
        if total_files + total_dirs > 0:
            print(f"\n💡 Pour nettoyer: python scripts/cleanup_root.py --clean")
        else:
            print(f"\n✅ Racine déjà propre !")
    
    def clean(self):
        """Nettoyage réel"""
        print("🧹 === NETTOYAGE RACINE ===")
        
        files_to_clean = self.find_files_to_clean()
        dirs_to_clean = self.find_dirs_to_clean()
        
        # Créer dossier backup
        backup_dir = self.project_root / f"backup_cleanup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        backup_dir.mkdir(exist_ok=True)
        
        # Nettoyer fichiers
        for file_path in files_to_clean:
            try:
                # Backup avant suppression
                backup_file = backup_dir / file_path.name
                shutil.copy2(file_path, backup_file)
                
                # Suppression
                file_path.unlink()
                self.cleaned_files.append(str(file_path))
                print(f"  ✅ Supprimé: {file_path.name}")
            except Exception as e:
                print(f"  ❌ Erreur {file_path.name}: {e}")
        
        # Nettoyer dossiers
        for dir_path in dirs_to_clean:
            try:
                # Backup avant suppression
                backup_subdir = backup_dir / dir_path.name
                shutil.copytree(dir_path, backup_subdir)
                
                # Suppression
                shutil.rmtree(dir_path)
                self.cleaned_dirs.append(str(dir_path))
                print(f"  ✅ Supprimé: {dir_path.name}/")
            except Exception as e:
                print(f"  ❌ Erreur {dir_path.name}/: {e}")
        
        print(f"\n📊 NETTOYAGE TERMINÉ:")
        print(f"  Fichiers nettoyés: {len(self.cleaned_files)}")
        print(f"  Dossiers nettoyés: {len(self.cleaned_dirs)}")
        print(f"  Backup créé: {backup_dir}")
    
    def organize_tests(self):
        """Réorganisation des tests"""
        print("📁 === RÉORGANISATION TESTS ===")
        
        # Créer structure tests
        tests_dir = self.project_root / "tests"
        tests_dir.mkdir(exist_ok=True)
        
        subdirs = ["unit", "integration", "performance", "scripts", "results"]
        for subdir in subdirs:
            (tests_dir / subdir).mkdir(exist_ok=True)
        
        # Déplacer fichiers de test
        test_files = list(self.project_root.glob("test_*.py"))
        for test_file in test_files:
            try:
                # Déterminer destination
                if "ibkr" in test_file.name or "gateway" in test_file.name:
                    dest_dir = tests_dir / "integration"
                elif "performance" in test_file.name or "latency" in test_file.name:
                    dest_dir = tests_dir / "performance"
                else:
                    dest_dir = tests_dir / "scripts"
                
                # Déplacer
                dest_file = dest_dir / test_file.name
                shutil.move(str(test_file), str(dest_file))
                print(f"  📁 Déplacé: {test_file.name} → {dest_dir.name}/")
                
            except Exception as e:
                print(f"  ❌ Erreur déplacement {test_file.name}: {e}")
        
        print(f"\n✅ Structure tests organisée dans tests/")

def main():
    parser = argparse.ArgumentParser(description="Nettoyage racine MIA_IA_SYSTEM")
    parser.add_argument("--dry-run", action="store_true", help="Simulation sans suppression")
    parser.add_argument("--clean", action="store_true", help="Nettoyage réel")
    parser.add_argument("--organize", action="store_true", help="Réorganisation tests")
    
    args = parser.parse_args()
    
    cleaner = RootCleaner()
    
    if args.dry_run:
        cleaner.dry_run()
    elif args.clean:
        cleaner.clean()
    elif args.organize:
        cleaner.organize_tests()
    else:
        print("Usage:")
        print("  python scripts/cleanup_root.py --dry-run    # Simulation")
        print("  python scripts/cleanup_root.py --clean      # Nettoyage réel")
        print("  python scripts/cleanup_root.py --organize   # Réorganisation")

if __name__ == "__main__":
    main()

