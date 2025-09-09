#!/usr/bin/env python3
"""
🛡️ SCRIPT DE PRÉVENTION POLLUTION RACINE - MIA_IA_SYSTEM
==========================================================

Script pour prévenir la création de fichiers de test dans la racine
et rediriger automatiquement vers les bons dossiers.

Usage:
    python scripts/prevent_root_pollution.py --check    # Vérification
    python scripts/prevent_root_pollution.py --move     # Déplacement automatique
"""

import os
import shutil
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List

class RootPollutionPreventer:
    """Préventeur de pollution racine"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        
        # Mapping des patterns vers dossiers
        self.pattern_mapping = {
            # Tests IBKR/Gateway
            "test_ibkr_": "tests/integration/ibkr/",
            "test_ib_gateway_": "tests/integration/ibkr/",
            "test_tws_": "tests/integration/ibkr/",
            "test_connection": "tests/integration/ibkr/",
            
            # Tests Sierra
            "test_sierra_": "tests/integration/sierra/",
            "test_order_": "tests/integration/sierra/",
            
            # Tests Automation
            "test_automation_": "tests/integration/automation/",
            "test_trader_": "tests/integration/automation/",
            
            # Tests ML
            "test_ml_": "tests/unit/ml/",
            "test_model_": "tests/unit/ml/",
            "test_ensemble_": "tests/unit/ml/",
            
            # Tests Performance
            "test_performance_": "tests/performance/",
            "test_latency_": "tests/performance/",
            "test_memory_": "tests/performance/",
            
            # Tests Core
            "test_core_": "tests/unit/core/",
            "test_battle_": "tests/unit/strategies/",
            "test_confluence_": "tests/unit/features/",
            
            # Tests Features
            "test_feature_": "tests/unit/features/",
            "test_market_": "tests/unit/features/",
            
            # Tests Execution
            "test_execution_": "tests/unit/execution/",
            "test_order_": "tests/unit/execution/",
            "test_risk_": "tests/unit/execution/",
            
            # Tests Monitoring
            "test_monitoring_": "tests/unit/monitoring/",
            "test_alert_": "tests/unit/monitoring/",
            
            # Scripts de test génériques
            "test_": "tests/scripts/",
            "verify_": "tests/scripts/",
            "check_": "tests/scripts/",
            "diagnostic_": "tests/scripts/",
            
            # Guides et documentation
            "GUIDE_": "docs/guides/",
            "RESUME_": "docs/resumes/",
            "RAPPORT_": "docs/reports/",
            "ANALYSE_": "docs/analyses/",
            
            # Données et résultats
            "download_": "data/downloads/",
            "backtest_": "data/backtests/",
            "results_": "data/results/",
            "report_": "data/reports/",
        }
        
        # Créer structure de dossiers
        self._create_directory_structure()
    
    def _create_directory_structure(self):
        """Crée la structure de dossiers pour les tests"""
        directories = [
            "tests/unit/core",
            "tests/unit/features", 
            "tests/unit/strategies",
            "tests/unit/execution",
            "tests/unit/monitoring",
            "tests/unit/ml",
            "tests/integration/ibkr",
            "tests/integration/sierra",
            "tests/integration/automation",
            "tests/performance",
            "tests/scripts",
            "tests/results",
            "docs/guides",
            "docs/resumes",
            "docs/reports",
            "docs/analyses",
            "data/downloads",
            "data/backtests",
            "data/results",
            "data/reports"
        ]
        
        for directory in directories:
            (self.project_root / directory).mkdir(parents=True, exist_ok=True)
    
    def find_misplaced_files(self) -> Dict[str, List[Path]]:
        """Trouve les fichiers mal placés dans la racine"""
        misplaced = {}
        
        for file_path in self.project_root.iterdir():
            if file_path.is_file() and file_path.name not in ['.gitignore', 'README.md', 'requirements.txt', 'pytest.ini']:
                name = file_path.name
                
                # Vérifier si le fichier devrait être déplacé
                for pattern, target_dir in self.pattern_mapping.items():
                    if pattern in name:
                        if target_dir not in misplaced:
                            misplaced[target_dir] = []
                        misplaced[target_dir].append(file_path)
                        break
        
        return misplaced
    
    def check_root_pollution(self):
        """Vérifie la pollution de la racine"""
        print("🔍 === VÉRIFICATION POLLUTION RACINE ===")
        
        misplaced = self.find_misplaced_files()
        
        if not misplaced:
            print("✅ Racine propre - Aucun fichier mal placé détecté")
            return
        
        print(f"\n❌ Fichiers mal placés détectés:")
        
        total_files = 0
        for target_dir, files in misplaced.items():
            print(f"\n📁 {target_dir} ({len(files)} fichiers):")
            for file_path in files:
                size = file_path.stat().st_size / 1024  # KB
                print(f"  📄 {file_path.name} ({size:.1f} KB)")
                total_files += 1
        
        print(f"\n📊 TOTAL: {total_files} fichiers à déplacer")
        print(f"\n💡 Pour déplacer automatiquement: python scripts/prevent_root_pollution.py --move")
    
    def move_misplaced_files(self):
        """Déplace automatiquement les fichiers mal placés"""
        print("📁 === DÉPLACEMENT AUTOMATIQUE FICHIERS ===")
        
        misplaced = self.find_misplaced_files()
        
        if not misplaced:
            print("✅ Aucun fichier à déplacer")
            return
        
        moved_count = 0
        errors = []
        
        for target_dir, files in misplaced.items():
            target_path = self.project_root / target_dir
            target_path.mkdir(parents=True, exist_ok=True)
            
            print(f"\n📁 Déplacement vers {target_dir}:")
            
            for file_path in files:
                try:
                    # Créer nom unique si conflit
                    dest_path = target_path / file_path.name
                    if dest_path.exists():
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        name_parts = file_path.stem, timestamp, file_path.suffix
                        dest_path = target_path / f"{name_parts[0]}_{name_parts[1]}{name_parts[2]}"
                    
                    # Déplacer fichier
                    shutil.move(str(file_path), str(dest_path))
                    print(f"  ✅ {file_path.name} → {target_dir}")
                    moved_count += 1
                    
                except Exception as e:
                    error_msg = f"❌ Erreur déplacement {file_path.name}: {e}"
                    print(error_msg)
                    errors.append(error_msg)
        
        print(f"\n📊 DÉPLACEMENT TERMINÉ:")
        print(f"  Fichiers déplacés: {moved_count}")
        print(f"  Erreurs: {len(errors)}")
        
        if errors:
            print(f"\n❌ Erreurs:")
            for error in errors:
                print(f"  {error}")
    
    def create_test_template(self, test_type: str, name: str):
        """Crée un template de test dans le bon dossier"""
        templates = {
            "unit": """#!/usr/bin/env python3
\"\"\"
🧪 TEST UNITAIRE - {name}
\"\"\"

import pytest
from unittest.mock import Mock, patch

class Test{name}:
    \"\"\"Tests unitaires pour {name}\"\"\"
    
    def setup_method(self):
        \"\"\"Setup avant chaque test\"\"\"
        pass
    
    def test_{name}_basic(self):
        \"\"\"Test basique\"\"\"
        assert True
    
    def test_{name}_edge_case(self):
        \"\"\"Test cas limite\"\"\"
        assert True
""",
            "integration": """#!/usr/bin/env python3
\"\"\"
🔗 TEST INTÉGRATION - {name}
\"\"\"

import pytest
import asyncio

class Test{name}Integration:
    \"\"\"Tests d'intégration pour {name}\"\"\"
    
    @pytest.fixture
    async def setup_integration(self):
        \"\"\"Setup intégration\"\"\"
        # Setup code here
        yield
        # Cleanup code here
    
    @pytest.mark.asyncio
    async def test_{name}_connection(self, setup_integration):
        \"\"\"Test connexion\"\"\"
        assert True
    
    @pytest.mark.asyncio
    async def test_{name}_data_flow(self, setup_integration):
        \"\"\"Test flux de données\"\"\"
        assert True
""",
            "performance": """#!/usr/bin/env python3
\"\"\"
⚡ TEST PERFORMANCE - {name}
\"\"\"

import pytest
import time

class Test{name}Performance:
    \"\"\"Tests de performance pour {name}\"\"\"
    
    def test_{name}_latency(self):
        \"\"\"Test latence\"\"\"
        start_time = time.time()
        # Code à tester
        end_time = time.time()
        
        latency = end_time - start_time
        assert latency < 1.0  # Moins d'1 seconde
    
    def test_{name}_memory_usage(self):
        \"\"\"Test usage mémoire\"\"\"
        import psutil
        process = psutil.Process()
        
        initial_memory = process.memory_info().rss
        # Code à tester
        final_memory = process.memory_info().rss
        
        memory_increase = final_memory - initial_memory
        assert memory_increase < 100 * 1024 * 1024  # Moins de 100MB
"""
        }
        
        if test_type not in templates:
            print(f"❌ Type de test inconnu: {test_type}")
            return
        
        # Déterminer dossier cible
        target_dir = f"tests/{test_type}"
        if test_type == "unit":
            target_dir += "/core"  # Par défaut
        
        target_path = self.project_root / target_dir
        target_path.mkdir(parents=True, exist_ok=True)
        
        # Créer fichier
        file_path = target_path / f"test_{name.lower()}.py"
        
        if file_path.exists():
            print(f"❌ Fichier existe déjà: {file_path}")
            return
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(templates[test_type].format(name=name))
        
        print(f"✅ Template créé: {file_path}")

def main():
    parser = argparse.ArgumentParser(description="Prévention pollution racine MIA_IA_SYSTEM")
    parser.add_argument("--check", action="store_true", help="Vérifier pollution")
    parser.add_argument("--move", action="store_true", help="Déplacer fichiers")
    parser.add_argument("--create-test", nargs=2, metavar=('TYPE', 'NAME'), 
                       help="Créer template test (TYPE: unit/integration/performance)")
    
    args = parser.parse_args()
    
    preventer = RootPollutionPreventer()
    
    if args.check:
        preventer.check_root_pollution()
    elif args.move:
        preventer.move_misplaced_files()
    elif args.create_test:
        test_type, name = args.create_test
        preventer.create_test_template(test_type, name)
    else:
        print("Usage:")
        print("  python scripts/prevent_root_pollution.py --check")
        print("  python scripts/prevent_root_pollution.py --move")
        print("  python scripts/prevent_root_pollution.py --create-test unit MyFeature")

if __name__ == "__main__":
    main()

