#!/usr/bin/env python3
"""
Script d'audit et nettoyage automatique du repo MIA_IA_SYSTEM
- Détecte les fichiers legacy (IBKR/Polygon/DTC-data)
- Propose un plan de nettoyage
- Vérifie l'unicité du writer mia_unified_*.jsonl
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Set

class LegacyAuditor:
    def __init__(self, repo_root: str = "."):
        self.repo_root = Path(repo_root)
        self.legacy_patterns = {
            'IBKR': ['IBKR', 'ibkr', 'Interactive Brokers'],
            'Polygon': ['Polygon', 'polygon'],
            'TWS': ['TWS', 'tws', 'Trader Workstation'],
            'Gateway': ['Gateway', 'gateway'],
            'DTC_DATA': ['DTC.*data', 'DTC.*collect', 'DTC.*feed', 'DTC.*market_data']  # DTC pour data (pas trading)
        }
        
        # DTC légitime pour trading (à NE PAS toucher)
        self.legitimate_dtc_patterns = [
            'sierra_dtc_connector',  # Connexion DTC pour ordres
            'sierra_order_router',   # Router des ordres
            'sierra_trading_ports',  # Ports DTC trading
            'DTC.*order',            # DTC pour ordres
            'DTC.*trade',            # DTC pour trading
            'DTC.*position'          # DTC pour positions
        ]
        
        self.legacy_files = {
            'adapters': [],
            'connectors': [],
            'docs': [],
            'tests': [],
            'configs': []
        }
        
        self.duplicate_connectors = []
        self.unified_file_usage = []
    
    def scan_legacy_files(self):
        """Scanne tous les fichiers pour détecter les références legacy"""
        print("🔍 Scan des fichiers legacy...")
        
        for file_path in self.repo_root.rglob("*.py"):
            if self._should_skip_file(file_path):
                continue
                
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    
                for category, patterns in self.legacy_patterns.items():
                    for pattern in patterns:
                        if re.search(pattern, content, re.IGNORECASE):
                            self._categorize_legacy_file(file_path, category, pattern)
                            
            except Exception as e:
                print(f"⚠️ Erreur lecture {file_path}: {e}")
    
    def _should_skip_file(self, file_path: Path) -> bool:
        """Détermine si un fichier doit être ignoré"""
        skip_patterns = [
            'archive/',
            'OpenJDK',
            '__pycache__',
            '.git/',
            'venv/',
            'node_modules/',
            '.pytest_cache/'
        ]
        
        return any(pattern in str(file_path) for pattern in skip_patterns)
    
    def _is_legitimate_dtc(self, file_path: Path, content: str) -> bool:
        """Vérifie si c'est du DTC légitime pour trading"""
        file_str = str(file_path).lower()
        
        # Vérifier les patterns légitimes
        for pattern in self.legitimate_dtc_patterns:
            if re.search(pattern, file_str, re.IGNORECASE):
                return True
            if re.search(pattern, content, re.IGNORECASE):
                return True
        
        return False
    
    def _categorize_legacy_file(self, file_path: Path, category: str, pattern: str):
        """Catégorise un fichier legacy"""
        relative_path = file_path.relative_to(self.repo_root)
        
        # Si c'est du DTC, vérifier si c'est légitime
        if category == 'DTC_DATA':
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                if self._is_legitimate_dtc(file_path, content):
                    print(f"✅ DTC légitime ignoré: {relative_path}")
                    return  # Ne pas archiver
            except:
                pass
        
        if 'adapter' in str(file_path).lower():
            self.legacy_files['adapters'].append((relative_path, pattern))
        elif 'connector' in str(file_path).lower():
            self.legacy_files['connectors'].append((relative_path, pattern))
        elif 'test' in str(file_path).lower():
            self.legacy_files['tests'].append((relative_path, pattern))
        elif 'config' in str(file_path).lower():
            self.legacy_files['configs'].append((relative_path, pattern))
        elif 'docs' in str(file_path).lower():
            self.legacy_files['docs'].append((relative_path, pattern))
    
    def find_duplicate_connectors(self):
        """Trouve les connecteurs dupliqués"""
        print("🔍 Recherche des connecteurs dupliqués...")
        
        connectors = {}
        for file_path in self.repo_root.rglob("*connector*.py"):
            if self._should_skip_file(file_path):
                continue
                
            filename = file_path.name
            if filename in connectors:
                self.duplicate_connectors.append((connectors[filename], file_path))
            else:
                connectors[filename] = file_path
    
    def check_unified_file_usage(self):
        """Vérifie l'usage du fichier unifié mia_unified_*.jsonl"""
        print("🔍 Vérification de l'usage du fichier unifié...")
        
        unified_patterns = [
            'mia_unified.*\.jsonl',
            'unified.*\.jsonl',
            'sierra_paths\.py'
        ]
        
        for file_path in self.repo_root.rglob("*.py"):
            if self._should_skip_file(file_path):
                continue
                
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    
                for pattern in unified_patterns:
                    if re.search(pattern, content, re.IGNORECASE):
                        self.unified_file_usage.append((file_path.relative_to(self.repo_root), pattern))
                        
            except Exception as e:
                print(f"⚠️ Erreur lecture {file_path}: {e}")
    
    def generate_cleanup_plan(self):
        """Génère un plan de nettoyage"""
        print("\n📋 PLAN DE NETTOYAGE AUTOMATIQUE")
        print("=" * 50)
        
        # 1. Archiver les adapters legacy
        if self.legacy_files['adapters']:
            print("\n1️⃣ ARCHIVER LES ADAPTERS LEGACY:")
            print("mkdir -p archive/legacy_adapters")
            for file_path, pattern in self.legacy_files['adapters']:
                print(f"git mv {file_path} archive/legacy_adapters/")
            print("git commit -m \"chore(archive): move legacy adapters to archive\"")
        
        # 2. Dédupliquer les connecteurs
        if self.duplicate_connectors:
            print("\n2️⃣ DÉDUPLIQUER LES CONNECTEURS:")
            print("mkdir -p archive/legacy_connectors")
            for original, duplicate in self.duplicate_connectors:
                print(f"git mv {duplicate.relative_to(self.repo_root)} archive/legacy_connectors/")
            print("git commit -m \"chore(archive): remove duplicate connectors\"")
        
        # 3. Nettoyer les docs legacy
        if self.legacy_files['docs']:
            print("\n3️⃣ ARCHIVER LA DOCUMENTATION LEGACY:")
            print("mkdir -p docs/archive/legacy")
            for file_path, pattern in self.legacy_files['docs']:
                print(f"git mv {file_path} docs/archive/legacy/")
            print("git commit -m \"docs: move legacy documentation to archive\"")
        
        # 4. Mettre à jour .gitignore
        print("\n4️⃣ METTRE À JOUR .GITIGNORE:")
        print("echo \"OpenJDK17U-jdk_x64_windows_hotspot_17.0.16_8/\" >> .gitignore")
        print("echo \"archive/\" >> .gitignore")
        print("git add .gitignore")
        print("git commit -m \"chore: update .gitignore for OpenJDK and archive\"")
        
        # 5. Mettre à jour pytest.ini
        print("\n5️⃣ METTRE À JOUR PYTEST.INI:")
        print("""
[pytest]
addopts = -q
testpaths = tests
norecursedirs = archive OpenJDK17U-jdk_x64_windows_hotspot_17.0.16_8 "document important"
markers =
    legacy: tests legacy (IBKR/Polygon/DTC-data)
    sierra: tests Sierra Chart integration
    production: tests production-ready features
""")
    
    def generate_report(self):
        """Génère un rapport complet"""
        print("\n📊 RAPPORT D'AUDIT LEGACY")
        print("=" * 50)
        
        # Afficher les DTC légitimes (à NE PAS toucher)
        print("\n✅ DTC LÉGITIMES (TRADING) - À NE PAS TOUCHER:")
        dtc_legitimate_files = [
            "core/sierra_dtc_connector.py",
            "core/sierra_order_router.py", 
            "config/sierra_trading_ports.py"
        ]
        for file_path in dtc_legitimate_files:
            if (self.repo_root / file_path).exists():
                print(f"  ✅ {file_path} - DTC pour ordres (GARDER)")
            else:
                print(f"  ❌ {file_path} - MANQUANT")
        
        total_legacy = sum(len(files) for files in self.legacy_files.values())
        print(f"\nTotal fichiers legacy détectés: {total_legacy}")
        
        for category, files in self.legacy_files.items():
            if files:
                print(f"\n{category.upper()}:")
                for file_path, pattern in files:
                    print(f"  - {file_path} (pattern: {pattern})")
        
        if self.duplicate_connectors:
            print(f"\nDUPLICATES CONNECTEURS:")
            for original, duplicate in self.duplicate_connectors:
                print(f"  - {original.relative_to(self.repo_root)} <-> {duplicate.relative_to(self.repo_root)}")
        
        print(f"\nUSAGE FICHIER UNIFIÉ:")
        for file_path, pattern in self.unified_file_usage:
            print(f"  - {file_path} (pattern: {pattern})")
    
    def run_full_audit(self):
        """Exécute l'audit complet"""
        print("🚀 AUDIT COMPLET DU REPO MIA_IA_SYSTEM")
        print("=" * 50)
        
        self.scan_legacy_files()
        self.find_duplicate_connectors()
        self.check_unified_file_usage()
        self.generate_report()
        self.generate_cleanup_plan()

def main():
    auditor = LegacyAuditor()
    auditor.run_full_audit()

if __name__ == "__main__":
    main()
