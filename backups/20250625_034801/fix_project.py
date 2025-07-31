#!/usr/bin/env python3
"""
MIA_IA_SYSTEM - Script de Diagnostic et Correction Automatique
Scanne tout le projet, détecte et corrige les erreurs d'import
"""

import os
import sys
import re
import ast
import json
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Set, Tuple, Optional
import logging

# Configure logging
logger = logging.getLogger(__name__)


class ProjectFixer:
    """Diagnostique et corrige automatiquement les problèmes du projet"""
    
    def __init__(self, project_root: str = "D:\\MIA_IA_system"):
        self.project_root = Path(project_root)
        self.errors_found = []
        self.fixes_applied = []
        self.backup_dir = self.project_root / "backups" / datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Mapping des imports manquants connus
        self.known_fixes = {
            'ValidationMethod': {
                'module': 'ml.model_validator',
                'import': 'from ml.model_validator import ValidationMethod'
            },
            'ContractConfig': {
                'module': 'config.sierra_config',
                'import': 'from dataclasses import dataclass\n\n@dataclass\nclass ContractConfig:\n    """Configuration contrat trading"""\n    symbol: str = "ES"\n    exchange: str = "CME"\n    multiplier: float = 50.0\n    tick_size: float = 0.25'
            },
            'DataCollectionConfig': {
                'module': 'config.automation_config',
                'import': 'from dataclasses import dataclass\nfrom typing import List\n\n@dataclass\nclass DataCollectionConfig:\n    """Configuration collecte données"""\n    enabled: bool = True\n    symbols: List[str] = None\n    save_snapshots: bool = True\n    snapshot_interval: int = 60\n    \n    def __post_init__(self):\n        if self.symbols is None:\n            self.symbols = ["ES", "NQ"]'
            },
            'PatternsDetector': {
                'module': 'core.patterns_detector',
                'import': 'class PatternsDetector:\n    """Détecteur de patterns trading"""\n    def __init__(self):\n        self.patterns = ["battle_navale", "gamma_pin", "headfake"]\n    \n    def detect_patterns(self, data):\n        """Détecte les patterns dans les données"""\n        return []'
            }
        }
        
        # Modules à installer
        self.required_modules = ['schedule', 'pandas', 'numpy', 'discord.py', 'python-dotenv']
        
    def run_full_diagnostic(self):
        """Lance le diagnostic complet et applique les corrections"""
        logger.debug("DIAGNOSTIC COMPLET DU PROJET MIA_IA_SYSTEM")
        print("=" * 60)
        
        # 1. Créer un backup
        self.create_backup()
        
        # 2. Vérifier les modules Python manquants
        self.check_python_modules()
        
        # 3. Scanner tous les fichiers Python
        self.scan_all_files()
        
        # 4. Corriger les imports manquants
        self.fix_missing_imports()
        
        # 5. Corriger les problèmes d'encodage
        self.fix_encoding_issues()
        
        # 6. Corriger les fonctions manquantes
        self.fix_missing_functions()
        
        # 7. Générer le rapport
        self.generate_report()
        
    def create_backup(self):
        """Crée une sauvegarde du projet avant modifications"""
        logger.info("\n📦 Création d'un backup...")
        try:
            # Créer le dossier de backup
            self.backup_dir.mkdir(parents=True, exist_ok=True)
            
            # Copier les fichiers Python
            for py_file in self.project_root.rglob("*.py"):
                if "backup" not in str(py_file):
                    relative_path = py_file.relative_to(self.project_root)
                    backup_path = self.backup_dir / relative_path
                    backup_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(py_file, backup_path)
            
            logger.info("Backup créé dans: {self.backup_dir}")
        except Exception as e:
            logger.error("Erreur création backup: {e}")
            
    def check_python_modules(self):
        """Vérifie et installe les modules Python manquants"""
        logger.info("\n📋 Vérification des modules Python...")
        missing_modules = []
        
        for module in self.required_modules:
            try:
                if module == 'discord.py':
                    __import__('discord')
                else:
                    __import__(module)
                logger.info("{module} installé")
            except ImportError:
                missing_modules.append(module)
                logger.error("{module} manquant")
        
        if missing_modules:
            logger.info("\n🔧 Installation des modules manquants...")
            for module in missing_modules:
                os.system(f"pip install {module}")
                
    def scan_all_files(self):
        """Scanne tous les fichiers Python pour détecter les erreurs"""
        logger.info("\n🔍 Scan de tous les fichiers Python...")
        
        for py_file in self.project_root.rglob("*.py"):
            if any(skip in str(py_file) for skip in ["backup", "__pycache__", ".git"]):
                continue
                
            self.scan_file(py_file)
            
    def scan_file(self, filepath: Path):
        """Scanne un fichier pour détecter les problèmes"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Détecter les imports manquants
            self.detect_missing_imports(filepath, content)
            
            # Détecter les problèmes de syntaxe
            self.detect_syntax_errors(filepath, content)
            
            # Détecter les fonctions non définies
            self.detect_undefined_functions(filepath, content)
            
        except Exception as e:
            self.errors_found.append({
                'file': str(filepath),
                'error': f"Erreur lecture fichier: {e}",
                'type': 'file_error'
            })
            
    def detect_missing_imports(self, filepath: Path, content: str):
        """Détecte les imports manquants dans un fichier"""
        # Pattern pour détecter les utilisations de classes/fonctions
        usage_pattern = r'\b([A-Z][a-zA-Z0-9_]*)\b(?:\(|\.|\s*=)'
        
        # Extraire tous les noms utilisés
        used_names = set(re.findall(usage_pattern, content))
        
        # Extraire les imports existants
        import_pattern = r'(?:from\s+[\w.]+\s+)?import\s+(?:\w+(?:\s*,\s*\w+)*|\([\s\w,]+\))'
        imports = re.findall(import_pattern, content)
        imported_names = set()
        
        for imp in imports:
            # Extraire les noms importés
            names = re.findall(r'\b\w+\b', imp)
            imported_names.update(names)
            
        # Vérifier les noms manquants
        for name in used_names:
            if name not in imported_names and name in self.known_fixes:
                self.errors_found.append({
                    'file': str(filepath),
                    'error': f"Import manquant: {name}",
                    'type': 'missing_import',
                    'fix': self.known_fixes[name]
                })
                
    def detect_syntax_errors(self, filepath: Path, content: str):
        """Détecte les erreurs de syntaxe"""
        try:
            ast.parse(content)
        except SyntaxError as e:
            self.errors_found.append({
                'file': str(filepath),
                'error': f"Erreur de syntaxe ligne {e.lineno}: {e.msg}",
                'type': 'syntax_error',
                'line': e.lineno
            })
            
    def detect_undefined_functions(self, filepath: Path, content: str):
        """Détecte les fonctions non définies"""
        # Rechercher set_sierra_config qui n'existe pas
        if 'set_sierra_config' in content and 'def set_sierra_config' not in content:
            self.errors_found.append({
                'file': str(filepath),
                'error': "Fonction 'set_sierra_config' utilisée mais non définie",
                'type': 'undefined_function',
                'function': 'set_sierra_config'
            })
            
    def fix_missing_imports(self):
        """Corrige automatiquement les imports manquants"""
        logger.info("\n🔧 Correction des imports manquants...")
        
        for error in self.errors_found:
            if error['type'] == 'missing_import':
                self.apply_import_fix(error)
                
    def apply_import_fix(self, error: Dict):
        """Applique une correction d'import"""
        filepath = Path(error['file'])
        fix_info = error['fix']
        
        try:
            # Cas spécial pour ml_config.py et ValidationMethod
            if 'ml_config.py' in str(filepath) and 'ValidationMethod' in error['error']:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Ajouter l'import après les autres imports
                import_section_end = content.rfind('from')
                if import_section_end == -1:
                    import_section_end = content.rfind('import')
                    
                if import_section_end != -1:
                    # Trouver la fin de la ligne
                    line_end = content.find('\n', import_section_end)
                    if line_end != -1:
                        new_content = (
                            content[:line_end + 1] +
                            "\n# Import ajouté automatiquement\n" +
                            fix_info['import'] + "\n" +
                            content[line_end + 1:]
                        )
                        
                        with open(filepath, 'w', encoding='utf-8') as f:
                            f.write(new_content)
                            
                        self.fixes_applied.append({
                            'file': str(filepath),
                            'fix': f"Import ajouté: {fix_info['import']}"
                        })
                        logger.info("Corrigé: {filepath.name} - Import ValidationMethod ajouté")
                        
            # Cas pour les classes manquantes dans les fichiers
            elif any(missing in error['error'] for missing in ['ContractConfig', 'DataCollectionConfig', 'PatternsDetector']):
                module_path = Path(self.project_root) / fix_info['module'].replace('.', '/') + '.py'
                
                if module_path.exists():
                    with open(module_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                    # Si la classe n'existe pas, l'ajouter
                    class_name = error['error'].split(':')[1].strip()
                    if f"class {class_name}" not in content:
                        # Ajouter la classe à la fin du fichier
                        with open(module_path, 'a', encoding='utf-8') as f:
                            f.write(f"\n\n{fix_info['import']}\n")
                            
                        self.fixes_applied.append({
                            'file': str(module_path),
                            'fix': f"Classe {class_name} ajoutée"
                        })
                        logger.info("Corrigé: {module_path.name} - Classe {class_name} ajoutée")
                        
        except Exception as e:
            logger.error("Erreur correction {filepath.name}: {e}")
            
    def fix_encoding_issues(self):
        """Corrige les problèmes d'encodage (emojis)"""
        logger.info("\n🔧 Correction des problèmes d'encodage...")
        
        # Ajouter la configuration UTF-8 dans automation_main.py
        main_file = self.project_root / "automation_main.py"
        if main_file.exists():
            with open(main_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            if "sys.stdout = io.TextIOWrapper" not in content:
                # Ajouter après les imports
                import_end = content.find('\n\n')
                if import_end != -1:
                    encoding_fix = """
# Configuration encodage UTF-8 pour Windows
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
"""
                    new_content = content[:import_end] + encoding_fix + content[import_end:]
                    
                    with open(main_file, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                        
                    self.fixes_applied.append({
                        'file': str(main_file),
                        'fix': "Configuration encodage UTF-8 ajoutée"
                    })
                    logger.info("Encodage UTF-8 configuré dans automation_main.py")
                    
    def fix_missing_functions(self):
        """Corrige les fonctions manquantes"""
        logger.info("\n🔧 Correction des fonctions manquantes...")
        
        for error in self.errors_found:
            if error['type'] == 'undefined_function':
                if error['function'] == 'set_sierra_config':
                    # Retirer l'import de set_sierra_config
                    filepath = Path(error['file'])
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                    # Remplacer l'import
                    content = content.replace(
                        "from config import get_trading_config, get_sierra_config, set_sierra_config",
                        "from config import get_trading_config, get_sierra_config"
                    )
                    
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(content)
                        
                    self.fixes_applied.append({
                        'file': str(filepath),
                        'fix': "Import set_sierra_config retiré"
                    })
                    logger.info("Corrigé: {filepath.name} - Import set_sierra_config retiré")
                    
    def generate_report(self):
        """Génère un rapport détaillé des corrections"""
        print("\n" + "=" * 60)
        logger.info("📊 RAPPORT DE DIAGNOSTIC ET CORRECTIONS")
        print("=" * 60)
        
        logger.info("\n🔍 Erreurs trouvées: {len(self.errors_found)}")
        for i, error in enumerate(self.errors_found, 1):
            logger.info("{i}. {error['file']}")
            logger.info("   ❌ {error['error']}")
            
        logger.info("\n✅ Corrections appliquées: {len(self.fixes_applied)}")
        for i, fix in enumerate(self.fixes_applied, 1):
            logger.info("{i}. {fix['file']}")
            logger.info("   ✅ {fix['fix']}")
            
        # Sauvegarder le rapport
        report = {
            'timestamp': datetime.now().isoformat(),
            'errors_found': self.errors_found,
            'fixes_applied': self.fixes_applied,
            'backup_location': str(self.backup_dir)
        }
        
        report_file = self.project_root / f"diagnostic_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)
            
        logger.info("\n📄 Rapport sauvegardé: {report_file}")
        logger.info("\n🎉 DIAGNOSTIC TERMINÉ!")
        
        # Instructions finales
        logger.info("\n📌 PROCHAINES ÉTAPES:")
        logger.info("1. Installer le module schedule: pip install schedule")
        logger.info("2. Relancer automation_main.py")
        logger.info("3. Si erreurs persistent, consulter le rapport de diagnostic")
        logger.info("4. Backup disponible dans: {self.backup_dir}")


def main():
    """Point d'entrée principal"""
    logger.info("🚀 MIA_IA_SYSTEM - OUTIL DE DIAGNOSTIC ET CORRECTION")
    print("=" * 60)
    
    # Demander confirmation
    response = input("\n⚠️  Ce script va modifier vos fichiers. Un backup sera créé.\nContinuer? (o/n): ")
    if response.lower() != 'o':
        logger.error("Opération annulée")
        return
        
    # Lancer le diagnostic
    fixer = ProjectFixer()
    fixer.run_full_diagnostic()


if __name__ == "__main__":
    main()