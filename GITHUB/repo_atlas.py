#!/usr/bin/env python3
"""
Générateur d'Atlas du Repository MIA_IA_system
Analyse la structure, les imports, et génère un rapport complet
"""

import os
import ast
import argparse
from pathlib import Path
from typing import Dict, List, Set, Any
from collections import defaultdict
import json
from datetime import datetime

class RepoAtlas:
    def __init__(self, root_path: str, max_depth: int = 10):
        self.root_path = Path(root_path)
        self.max_depth = max_depth
        self.imports_graph = defaultdict(set)
        self.files_info = {}
        self.legacy_components = set()
        self.sierra_components = set()
        self.menthorq_components = set()
        
    def analyze_file(self, file_path: Path) -> Dict[str, Any]:
        """Analyse un fichier Python et extrait les informations"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            imports = []
            legacy_refs = []
            sierra_refs = []
            menthorq_refs = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)
                        self._categorize_import(alias.name, legacy_refs, sierra_refs, menthorq_refs)
                
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.append(node.module)
                        self._categorize_import(node.module, legacy_refs, sierra_refs, menthorq_refs)
            
            return {
                'path': str(file_path.relative_to(self.root_path)),
                'size': file_path.stat().st_size,
                'imports': imports,
                'legacy_refs': legacy_refs,
                'sierra_refs': sierra_refs,
                'menthorq_refs': menthorq_refs,
                'lines': len(content.splitlines())
            }
            
        except Exception as e:
            return {
                'path': str(file_path.relative_to(self.root_path)),
                'error': str(e),
                'size': file_path.stat().st_size if file_path.exists() else 0
            }
    
    def _categorize_import(self, import_name: str, legacy_refs: List, sierra_refs: List, menthorq_refs: List):
        """Catégorise les imports selon leur type"""
        import_lower = import_name.lower()
        
        # Legacy components
        if any(legacy in import_lower for legacy in ['ibkr', 'polygon', 'tws', 'gateway', 'dtc']):
            legacy_refs.append(import_name)
            self.legacy_components.add(import_name)
        
        # Sierra components
        if any(sierra in import_lower for sierra in ['sierra', 'chart', 'jsonl', 'unified']):
            sierra_refs.append(import_name)
            self.sierra_components.add(import_name)
        
        # MenthorQ components
        if any(menthorq in import_lower for menthorq in ['menthorq', 'gamma', 'blind', 'swing']):
            menthorq_refs.append(import_name)
            self.menthorq_components.add(import_name)
    
    def scan_repository(self):
        """Scanne le repository et analyse tous les fichiers Python"""
        print(f"🔍 Analyse du repository: {self.root_path}")
        
        python_files = list(self.root_path.rglob("*.py"))
        print(f"📁 {len(python_files)} fichiers Python trouvés")
        
        for file_path in python_files:
            # Skip certain directories
            if any(skip in str(file_path) for skip in ['__pycache__', '.git', 'venv', 'node_modules']):
                continue
            
            # Check depth
            depth = len(file_path.relative_to(self.root_path).parts)
            if depth > self.max_depth:
                continue
            
            info = self.analyze_file(file_path)
            self.files_info[info['path']] = info
            
            # Build imports graph
            for imp in info.get('imports', []):
                self.imports_graph[info['path']].add(imp)
        
        print(f"✅ Analyse terminée: {len(self.files_info)} fichiers analysés")
    
    def generate_atlas_report(self, output_dir: str = "reports") -> str:
        """Génère le rapport d'atlas complet"""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = output_path / f"atlas_{timestamp}.md"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(self._generate_markdown_report())
        
        # Also generate JSON for programmatic access
        json_file = output_path / f"atlas_{timestamp}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump({
                'files_info': self.files_info,
                'imports_graph': {k: list(v) for k, v in self.imports_graph.items()},
                'legacy_components': list(self.legacy_components),
                'sierra_components': list(self.sierra_components),
                'menthorq_components': list(self.menthorq_components),
                'generated_at': datetime.now().isoformat()
            }, f, indent=2, ensure_ascii=False)
        
        print(f"📊 Rapport généré: {report_file}")
        print(f"📊 JSON généré: {json_file}")
        
        return str(report_file)
    
    def _generate_markdown_report(self) -> str:
        """Génère le rapport Markdown"""
        report = []
        
        # Header
        report.append("# 🗺️ Atlas du Repository MIA_IA_system")
        report.append(f"**Généré le:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # Summary
        report.append("## 📊 Résumé")
        report.append(f"- **Fichiers analysés:** {len(self.files_info)}")
        report.append(f"- **Composants Legacy:** {len(self.legacy_components)}")
        report.append(f"- **Composants Sierra:** {len(self.sierra_components)}")
        report.append(f"- **Composants MenthorQ:** {len(self.menthorq_components)}")
        report.append("")
        
        # Legacy Components
        if self.legacy_components:
            report.append("## 🚨 Composants Legacy (À nettoyer)")
            for component in sorted(self.legacy_components):
                report.append(f"- `{component}`")
            report.append("")
        
        # Sierra Components
        if self.sierra_components:
            report.append("## 🏔️ Composants Sierra (Actifs)")
            for component in sorted(self.sierra_components):
                report.append(f"- `{component}`")
            report.append("")
        
        # MenthorQ Components
        if self.menthorq_components:
            report.append("## 🧠 Composants MenthorQ (Actifs)")
            for component in sorted(self.menthorq_components):
                report.append(f"- `{component}`")
            report.append("")
        
        # Files with Legacy References
        legacy_files = []
        for file_path, info in self.files_info.items():
            if info.get('legacy_refs'):
                legacy_files.append((file_path, info['legacy_refs']))
        
        if legacy_files:
            report.append("## 📁 Fichiers avec Références Legacy")
            for file_path, refs in sorted(legacy_files):
                report.append(f"### `{file_path}`")
                for ref in refs:
                    report.append(f"- `{ref}`")
                report.append("")
        
        # Top Files by Size
        large_files = sorted(
            [(path, info['size']) for path, info in self.files_info.items() if 'size' in info],
            key=lambda x: x[1],
            reverse=True
        )[:10]
        
        if large_files:
            report.append("## 📏 Fichiers les plus volumineux")
            for file_path, size in large_files:
                size_kb = size / 1024
                report.append(f"- `{file_path}`: {size_kb:.1f} KB")
            report.append("")
        
        # Import Graph Summary
        report.append("## 🔗 Graphique des Imports")
        report.append("```mermaid")
        report.append("graph TD")
        
        # Add nodes for main components
        for component in list(self.sierra_components)[:5]:  # Limit for readability
            report.append(f"    {component.replace('.', '_')}[{component}]")
        
        for component in list(self.menthorq_components)[:5]:
            report.append(f"    {component.replace('.', '_')}[{component}]")
        
        report.append("```")
        report.append("")
        
        # File Structure
        report.append("## 📂 Structure des Fichiers")
        self._add_file_structure(report, self.root_path, 0, 3)
        
        return "\n".join(report)
    
    def _add_file_structure(self, report: List[str], path: Path, depth: int, max_depth: int):
        """Ajoute la structure des fichiers au rapport"""
        if depth > max_depth:
            return
        
        indent = "  " * depth
        
        if path.is_dir():
            report.append(f"{indent}- 📁 {path.name}/")
            try:
                for child in sorted(path.iterdir()):
                    if child.name.startswith('.'):
                        continue
                    self._add_file_structure(report, child, depth + 1, max_depth)
            except PermissionError:
                report.append(f"{indent}  - ❌ Accès refusé")
        else:
            if path.suffix == '.py':
                report.append(f"{indent}- 🐍 {path.name}")
            elif path.suffix in ['.md', '.txt']:
                report.append(f"{indent}- 📄 {path.name}")
            elif path.suffix in ['.cpp', '.h']:
                report.append(f"{indent}- ⚙️ {path.name}")
            else:
                report.append(f"{indent}- 📄 {path.name}")

def main():
    parser = argparse.ArgumentParser(description="Générateur d'Atlas du Repository MIA_IA_system")
    parser.add_argument("--root", default=".", help="Racine du repository")
    parser.add_argument("--out", default="reports", help="Répertoire de sortie")
    parser.add_argument("--max-depth", type=int, default=10, help="Profondeur maximale d'analyse")
    
    args = parser.parse_args()
    
    atlas = RepoAtlas(args.root, args.max_depth)
    atlas.scan_repository()
    report_file = atlas.generate_atlas_report(args.out)
    
    print(f"✅ Atlas généré avec succès: {report_file}")

if __name__ == "__main__":
    main()
