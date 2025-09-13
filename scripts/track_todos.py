#!/usr/bin/env python3
"""
Script pour traquer et résoudre les TODO/FIXME dans le code
"""

import os
import re
import sys
from pathlib import Path
from typing import List, Dict, Tuple
from datetime import datetime

def find_todos_in_file(file_path: Path) -> List[Dict]:
    """Trouve tous les TODO/FIXME dans un fichier"""
    todos = []
    
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
            
        for line_num, line in enumerate(lines, 1):
            # Recherche TODO, FIXME, XXX, HACK (insensible à la casse)
            match = re.search(r'(TODO|FIXME|XXX|HACK)\s*:?\s*(.+)', line, re.IGNORECASE)
            if match:
                todo_type = match.group(1).upper()
                description = match.group(2).strip()
                
                todos.append({
                    'file': str(file_path),
                    'line': line_num,
                    'type': todo_type,
                    'description': description,
                    'full_line': line.strip()
                })
                
    except Exception as e:
        print(f"Erreur lecture {file_path}: {e}")
        
    return todos

def find_all_todos(root_dir: Path) -> List[Dict]:
    """Trouve tous les TODO/FIXME dans le projet"""
    all_todos = []
    
    # Extensions de fichiers à analyser
    extensions = {'.py', '.cpp', '.hpp', '.h', '.md', '.txt', '.json', '.yaml', '.yml'}
    
    # Dossiers à ignorer
    ignore_dirs = {
        '__pycache__', '.git', 'node_modules', 'venv', 'env', 
        'archived_legacy', 'tests_old', 'backup', 'archive'
    }
    
    for file_path in root_dir.rglob('*'):
        if file_path.is_file():
            # Ignorer les dossiers spécifiés
            if any(ignore_dir in file_path.parts for ignore_dir in ignore_dirs):
                continue
                
            # Vérifier l'extension
            if file_path.suffix.lower() in extensions:
                todos = find_todos_in_file(file_path)
                all_todos.extend(todos)
    
    return all_todos

def categorize_todos(todos: List[Dict]) -> Dict[str, List[Dict]]:
    """Catégorise les TODO par type et priorité"""
    categories = {
        'TODO': [],
        'FIXME': [],
        'XXX': [],
        'HACK': []
    }
    
    for todo in todos:
        categories[todo['type']].append(todo)
    
    return categories

def prioritize_todos(todos: List[Dict]) -> List[Dict]:
    """Priorise les TODO par importance"""
    priority_keywords = {
        'CRITICAL': ['critical', 'urgent', 'crash', 'error', 'fail'],
        'HIGH': ['security', 'performance', 'memory', 'leak', 'deadlock'],
        'MEDIUM': ['optimize', 'improve', 'enhance', 'refactor'],
        'LOW': ['nice', 'future', 'later', 'maybe']
    }
    
    for todo in todos:
        description_lower = todo['description'].lower()
        priority = 'LOW'  # Par défaut
        
        for prio, keywords in priority_keywords.items():
            if any(keyword in description_lower for keyword in keywords):
                priority = prio
                break
                
        todo['priority'] = priority
    
    # Trier par priorité
    priority_order = {'CRITICAL': 0, 'HIGH': 1, 'MEDIUM': 2, 'LOW': 3}
    todos.sort(key=lambda x: priority_order.get(x['priority'], 4))
    
    return todos

def generate_report(todos: List[Dict], output_file: Path = None) -> str:
    """Génère un rapport des TODO"""
    categories = categorize_todos(todos)
    prioritized = prioritize_todos(todos)
    
    report = []
    report.append("# RAPPORT TODO/FIXME - MIA_IA_SYSTEM")
    report.append(f"Généré le: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append(f"Total: {len(todos)} TODO/FIXME trouvés")
    report.append("")
    
    # Résumé par type
    report.append("## RÉSUMÉ PAR TYPE")
    for todo_type, type_todos in categories.items():
        if type_todos:
            report.append(f"- **{todo_type}**: {len(type_todos)}")
    report.append("")
    
    # Résumé par priorité
    report.append("## RÉSUMÉ PAR PRIORITÉ")
    priority_counts = {}
    for todo in prioritized:
        priority = todo['priority']
        priority_counts[priority] = priority_counts.get(priority, 0) + 1
    
    for priority in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']:
        count = priority_counts.get(priority, 0)
        if count > 0:
            report.append(f"- **{priority}**: {count}")
    report.append("")
    
    # Détail par priorité
    for priority in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']:
        priority_todos = [t for t in prioritized if t['priority'] == priority]
        if not priority_todos:
            continue
            
        report.append(f"## {priority} PRIORITY")
        for todo in priority_todos:
            report.append(f"### {todo['type']} - {Path(todo['file']).name}:{todo['line']}")
            report.append(f"**Fichier**: `{todo['file']}`")
            report.append(f"**Ligne**: {todo['line']}")
            report.append(f"**Description**: {todo['description']}")
            report.append(f"**Code**: `{todo['full_line']}`")
            report.append("")
    
    # Détail par fichier
    report.append("## DÉTAIL PAR FICHIER")
    files = {}
    for todo in todos:
        file_path = todo['file']
        if file_path not in files:
            files[file_path] = []
        files[file_path].append(todo)
    
    for file_path, file_todos in sorted(files.items()):
        report.append(f"### {file_path}")
        for todo in file_todos:
            report.append(f"- **Ligne {todo['line']}** [{todo['type']}] {todo['description']}")
        report.append("")
    
    report_text = "\n".join(report)
    
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(report_text)
        print(f"Rapport sauvegardé: {output_file}")
    
    return report_text

def main():
    """Fonction principale"""
    if len(sys.argv) > 1 and sys.argv[1] == '--help':
        print("Usage: python scripts/track_todos.py [--report] [--fix]")
        print("  --report: Génère un rapport détaillé")
        print("  --fix: Propose des corrections automatiques")
        return
    
    root_dir = Path(__file__).parent.parent
    print(f"🔍 Recherche TODO/FIXME dans: {root_dir}")
    
    # Trouver tous les TODO
    todos = find_all_todos(root_dir)
    print(f"📊 Trouvé {len(todos)} TODO/FIXME")
    
    if not todos:
        print("✅ Aucun TODO/FIXME trouvé!")
        return
    
    # Catégoriser
    categories = categorize_todos(todos)
    for todo_type, type_todos in categories.items():
        if type_todos:
            print(f"  - {todo_type}: {len(type_todos)}")
    
    # Prioriser
    prioritized = prioritize_todos(todos)
    priority_counts = {}
    for todo in prioritized:
        priority = todo['priority']
        priority_counts[priority] = priority_counts.get(priority, 0) + 1
    
    print("\n📈 PRIORITÉS:")
    for priority in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']:
        count = priority_counts.get(priority, 0)
        if count > 0:
            print(f"  - {priority}: {count}")
    
    # Générer rapport si demandé
    if '--report' in sys.argv:
        report_file = root_dir / 'TODO_REPORT.md'
        generate_report(todos, report_file)
    
    # Afficher les plus critiques
    print("\n🚨 TODO CRITIQUES:")
    critical_todos = [t for t in prioritized if t['priority'] == 'CRITICAL']
    for todo in critical_todos[:5]:  # Top 5
        print(f"  - {Path(todo['file']).name}:{todo['line']} - {todo['description']}")
    
    if len(critical_todos) > 5:
        print(f"  ... et {len(critical_todos) - 5} autres")

if __name__ == "__main__":
    main()

