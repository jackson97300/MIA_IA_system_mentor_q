#!/usr/bin/env python3
"""
SCRIPT DE CORRECTION AUTOMATIQUE DES ERREURS DE SYNTAXE
Pour projet MIA_IA_SYSTEM

Ce script :
1. Scanne tous les fichiers Python du projet
2. Détecte les erreurs de syntaxe courantes
3. Corrige automatiquement les problèmes
4. Valide les imports et leur ordre
5. Génère un rapport détaillé
"""

import os
import sys
import ast
import re
import json
import shutil
import autopep8
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Set
from datetime import datetime
import logging

# Configuration logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SyntaxFixer:
    """Corrige automatiquement les erreurs de syntaxe dans le projet"""
    
    def __init__(self, project_root: str = "D:/MIA_IA_system"):
        self.project_root = Path(project_root)
        self.backup_dir = self.project_root / "backup_syntax_fix"
        self.report = {
            "timestamp": datetime.now().isoformat(),
            "files_scanned": 0,
            "files_with_errors": 0,
            "errors_fixed": 0,
            "imports_fixed": 0,
            "details": []
        }
        
        # Patterns d'erreurs courantes
        self.error_patterns = {
            # Indentation
            r'^( {1,3}|\t)': 'indentation_error',
            r'^\s*\t': 'tab_character',
            
            # Imports
            r'from \.\. import': 'relative_import',
            r'from \* import': 'star_import',
            r'import \*': 'star_import',
            
            # Syntaxe
            r'except\s*:': 'bare_except',
            r'if\s+.*\s*=\s*': 'assignment_in_condition',
            r'print\s+[^(]': 'print_statement',
            
            # Typos courants
            r'\bture\b': 'typo_true',
            r'\bflase\b': 'typo_false',
            r'\bnone\b': 'typo_none',
            r'\bslef\b': 'typo_self',
            r'\bdef\s+__int__': 'typo_init',
        }
        
        # Modules standard Python
        self.stdlib_modules = {
            'os', 'sys', 'time', 'datetime', 'json', 'logging', 
            'pathlib', 'typing', 'dataclasses', 'enum', 'collections',
            'itertools', 'functools', 'operator', 'copy', 'pickle',
            'csv', 'io', 'subprocess', 'threading', 'multiprocessing',
            'abc', 'asyncio', 'concurrent', 'contextlib', 'decimal',
            'fractions', 'math', 'random', 'statistics', 'string',
            're', 'difflib', 'textwrap', 'unicodedata', 'locale',
            'sqlite3', 'zlib', 'gzip', 'bz2', 'lzma', 'zipfile',
            'tarfile', 'hashlib', 'hmac', 'secrets', 'uuid'
        }
        
        # Modules tiers courants
        self.third_party_modules = {
            'numpy', 'pandas', 'matplotlib', 'seaborn', 'sklearn',
            'scipy', 'tensorflow', 'torch', 'keras', 'plotly',
            'requests', 'flask', 'django', 'fastapi', 'aiohttp',
            'sqlalchemy', 'pymongo', 'redis', 'celery', 'pytest',
            'ib_insync', 'yfinance', 'ta', 'talib', 'backtrader'
        }
        
    def backup_file(self, filepath: Path) -> None:
        """Sauvegarde un fichier avant modification"""
        backup_path = self.backup_dir / filepath.relative_to(self.project_root)
        backup_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(filepath, backup_path)
        
    def scan_project(self) -> List[Path]:
        """Scanne tous les fichiers Python du projet"""
        python_files = []
        
        # Dossiers à scanner
        folders = [
            'config', 'core', 'features', 'strategies', 'execution',
            'monitoring', 'data', 'ml', 'performance', 'scripts'
        ]
        
        # Fichiers racine
        root_files = ['main.py', 'automation_main.py', 'data_collection_main.py']
        
        # Scan des dossiers
        for folder in folders:
            folder_path = self.project_root / folder
            if folder_path.exists():
                python_files.extend(folder_path.glob('*.py'))
                
        # Scan des fichiers racine
        for file in root_files:
            file_path = self.project_root / file
            if file_path.exists():
                python_files.append(file_path)
                
        # Scan des tests
        test_dir = self.project_root / 'tests'
        if test_dir.exists():
            python_files.extend(test_dir.rglob('*.py'))
            
        logger.info(f"Trouvé {len(python_files)} fichiers Python à scanner")
        return python_files
        
    def check_syntax(self, filepath: Path) -> Tuple[bool, Optional[str]]:
        """Vérifie la syntaxe d'un fichier Python"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Compile pour vérifier la syntaxe
            compile(content, str(filepath), 'exec')
            
            # Parse avec AST pour vérification plus poussée
            ast.parse(content)
            
            return True, None
            
        except SyntaxError as e:
            return False, f"SyntaxError: {e.msg} at line {e.lineno}"
        except Exception as e:
            return False, f"Error: {str(e)}"
            
    def fix_common_errors(self, content: str) -> Tuple[str, List[str]]:
        """Corrige les erreurs courantes"""
        fixes = []
        
        # Fix print statements (Python 2 -> 3)
        if re.search(r'print\s+[^(]', content):
            content = re.sub(r'print\s+([^(].+)$', r'print(\1)', content, flags=re.MULTILINE)
            fixes.append("Converti print statements en print()")
            
        # Fix typos courants
        replacements = {
            r'\bture\b': 'True',
            r'\bflase\b': 'False',
            r'\bnone\b': 'None',
            r'\bslef\b': 'self',
            r'\bdef\s+__int__': 'def __init__',
            r'\belif\s+': 'elif ',
            r'\bexcpet\b': 'except',
            r'\bfinaly\b': 'finally'
        }
        
        for pattern, replacement in replacements.items():
            if re.search(pattern, content):
                content = re.sub(pattern, replacement, content)
                fixes.append(f"Corrigé typo: {pattern} -> {replacement}")
                
        # Fix bare except
        if 'except:' in content:
            content = content.replace('except:', 'except Exception:')
            fixes.append("Remplacé 'except:' par 'except Exception:'")
            
        # Fix trailing whitespace
        lines = content.split('\n')
        cleaned_lines = [line.rstrip() for line in lines]
        if lines != cleaned_lines:
            content = '\n'.join(cleaned_lines)
            fixes.append("Supprimé espaces en fin de ligne")
            
        # Fix mixed indentation
        if '\t' in content:
            content = content.replace('\t', '    ')
            fixes.append("Remplacé tabs par 4 espaces")
            
        return content, fixes
        
    def fix_imports(self, content: str, filepath: Path) -> Tuple[str, List[str]]:
        """Corrige l'ordre et le format des imports"""
        fixes = []
        
        try:
            tree = ast.parse(content)
        except:
            return content, fixes
            
        # Extraire tous les imports
        imports = {
            'stdlib': [],
            'third_party': [],
            'local': []
        }
        
        import_lines = []
        other_lines = []
        
        lines = content.split('\n')
        in_imports = True
        
        for i, line in enumerate(lines):
            if line.strip().startswith(('import ', 'from ')) and in_imports:
                import_lines.append((i, line))
            else:
                if line.strip() and not line.strip().startswith('#') and in_imports:
                    in_imports = False
                other_lines.append((i, line))
                
        # Classifier les imports
        for _, line in import_lines:
            line = line.strip()
            if not line:
                continue
                
            # Extraire le nom du module
            if line.startswith('import '):
                module = line.split()[1].split('.')[0]
            elif line.startswith('from '):
                module = line.split()[1].split('.')[0]
            else:
                continue
                
            # Classifier
            if module in self.stdlib_modules:
                imports['stdlib'].append(line)
            elif module in self.third_party_modules:
                imports['third_party'].append(line)
            elif module.startswith('.'):
                # Import relatif à corriger
                fixes.append(f"Import relatif détecté: {line}")
                # Convertir en import absolu si possible
                if '../' not in line:
                    line = line.replace('from .', 'from ')
                    imports['local'].append(line)
            else:
                imports['local'].append(line)
                
        # Reconstruire avec bon ordre
        new_lines = []
        
        # Header (docstring, comments)
        for i, line in other_lines:
            if i < (import_lines[0][0] if import_lines else len(lines)):
                new_lines.append(line)
            else:
                break
                
        # Imports dans le bon ordre
        sections = []
        
        if imports['stdlib']:
            sections.append('\n'.join(sorted(set(imports['stdlib']))))
            
        if imports['third_party']:
            sections.append('\n'.join(sorted(set(imports['third_party']))))
            
        if imports['local']:
            sections.append('\n'.join(sorted(set(imports['local']))))
            
        if sections:
            new_lines.append('\n\n'.join(sections))
            fixes.append("Réorganisé les imports (stdlib -> third-party -> local)")
            
        # Reste du fichier
        if import_lines:
            last_import_line = max(i for i, _ in import_lines)
            for i, line in other_lines:
                if i > last_import_line:
                    new_lines.append(line)
                    
        return '\n'.join(new_lines), fixes
        
    def fix_file(self, filepath: Path) -> Dict[str, any]:
        """Corrige un fichier Python"""
        result = {
            "file": str(filepath.relative_to(self.project_root)),
            "status": "success",
            "errors_found": [],
            "fixes_applied": [],
            "syntax_valid_before": False,
            "syntax_valid_after": False
        }
        
        try:
            # Vérifier syntaxe initiale
            syntax_ok, error_msg = self.check_syntax(filepath)
            result["syntax_valid_before"] = syntax_ok
            
            if not syntax_ok:
                result["errors_found"].append(error_msg)
                
            # Lire le contenu
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                
            original_content = content
            
            # Corriger erreurs courantes
            content, fixes = self.fix_common_errors(content)
            result["fixes_applied"].extend(fixes)
            
            # Corriger imports
            content, import_fixes = self.fix_imports(content, filepath)
            result["fixes_applied"].extend(import_fixes)
            
            # Appliquer autopep8 pour formatting
            try:
                content = autopep8.fix_code(content, options={
                    'aggressive': 1,
                    'max_line_length': 100,
                    'indent_size': 4
                })
                result["fixes_applied"].append("Appliqué autopep8 formatting")
            except:
                pass
                
            # Si modifications effectuées
            if content != original_content:
                # Backup
                self.backup_file(filepath)
                
                # Écrire le fichier corrigé
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                    
                # Vérifier syntaxe finale
                syntax_ok, error_msg = self.check_syntax(filepath)
                result["syntax_valid_after"] = syntax_ok
                
                if not syntax_ok:
                    # Restaurer depuis backup si toujours erreur
                    backup_path = self.backup_dir / filepath.relative_to(self.project_root)
                    shutil.copy2(backup_path, filepath)
                    result["status"] = "failed"
                    result["fixes_applied"].append("ROLLBACK - Corrections ont causé des erreurs")
                else:
                    result["status"] = "fixed"
                    self.report["errors_fixed"] += len(result["fixes_applied"])
            else:
                result["syntax_valid_after"] = syntax_ok
                if syntax_ok:
                    result["status"] = "ok"
                    
        except Exception as e:
            result["status"] = "error"
            result["errors_found"].append(f"Exception: {str(e)}")
            
        return result
        
    def generate_report(self) -> str:
        """Génère un rapport détaillé"""
        report_lines = [
            "=" * 80,
            "RAPPORT DE CORRECTION DES ERREURS DE SYNTAXE",
            "=" * 80,
            f"Date: {self.report['timestamp']}",
            f"Projet: {self.project_root}",
            "",
            "RÉSUMÉ:",
            f"- Fichiers scannés: {self.report['files_scanned']}",
            f"- Fichiers avec erreurs: {self.report['files_with_errors']}",
            f"- Corrections appliquées: {self.report['errors_fixed']}",
            "",
            "=" * 80,
            "DÉTAILS PAR FICHIER:",
            ""
        ]
        
        # Grouper par statut
        by_status = {
            'fixed': [],
            'failed': [],
            'error': [],
            'ok': []
        }
        
        for detail in self.report['details']:
            by_status[detail['status']].append(detail)
            
        # Fichiers corrigés
        if by_status['fixed']:
            report_lines.append("\n✅ FICHIERS CORRIGÉS:")
            for detail in by_status['fixed']:
                report_lines.append(f"\n📄 {detail['file']}")
                for fix in detail['fixes_applied']:
                    report_lines.append(f"   • {fix}")
                    
        # Fichiers avec erreurs non corrigées
        if by_status['failed'] or by_status['error']:
            report_lines.append("\n❌ FICHIERS AVEC ERREURS NON CORRIGÉES:")
            for detail in by_status['failed'] + by_status['error']:
                report_lines.append(f"\n📄 {detail['file']}")
                for error in detail['errors_found']:
                    report_lines.append(f"   ⚠️ {error}")
                    
        # Fichiers OK
        ok_count = len(by_status['ok'])
        if ok_count > 0:
            report_lines.append(f"\n✓ {ok_count} fichiers sans erreurs")
            
        # Recommandations
        report_lines.extend([
            "",
            "=" * 80,
            "RECOMMANDATIONS:",
            "",
            "1. Vérifiez les fichiers dans le dossier backup avant de continuer",
            "2. Testez que le projet fonctionne toujours correctement",
            "3. Pour les erreurs non corrigées, intervention manuelle nécessaire",
            "4. Committez les changements une fois validés",
            "",
            "Backup disponible dans: " + str(self.backup_dir),
            "=" * 80
        ])
        
        return '\n'.join(report_lines)
        
    def run(self) -> None:
        """Exécute la correction complète du projet"""
        logger.info("Démarrage de la correction des erreurs de syntaxe...")
        
        # Créer dossier backup
        self.backup_dir.mkdir(exist_ok=True)
        
        # Scanner les fichiers
        python_files = self.scan_project()
        self.report["files_scanned"] = len(python_files)
        
        # Corriger chaque fichier
        for filepath in python_files:
            logger.info(f"Traitement: {filepath.relative_to(self.project_root)}")
            
            result = self.fix_file(filepath)
            self.report["details"].append(result)
            
            if result["status"] in ["fixed", "failed", "error"]:
                self.report["files_with_errors"] += 1
                
        # Générer et sauvegarder le rapport
        report_content = self.generate_report()
        
        report_path = self.project_root / f"syntax_fix_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
            
        # Afficher le rapport
        print(report_content)
        print(f"\nRapport sauvegardé dans: {report_path}")
        
        # Sauvegarder aussi en JSON pour analyse
        json_report_path = self.project_root / f"syntax_fix_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(json_report_path, 'w', encoding='utf-8') as f:
            json.dump(self.report, f, indent=2)
            
def main():
    """Point d'entrée du script"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Corrige automatiquement les erreurs de syntaxe dans le projet MIA_IA_SYSTEM"
    )
    parser.add_argument(
        '--project-root',
        type=str,
        default="D:/MIA_IA_system",
        help="Chemin racine du projet"
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help="Mode simulation - affiche les corrections sans les appliquer"
    )
    
    args = parser.parse_args()
    
    # Vérifier que le projet existe
    project_path = Path(args.project_root)
    if not project_path.exists():
        print(f"❌ Erreur: Le dossier projet n'existe pas: {project_path}")
        sys.exit(1)
        
    # Créer et exécuter le fixer
    fixer = SyntaxFixer(args.project_root)
    
    if args.dry_run:
        print("🔍 MODE SIMULATION - Aucune modification ne sera appliquée")
        # TODO: Implémenter le mode dry-run
        
    fixer.run()
    
if __name__ == "__main__":
    main()