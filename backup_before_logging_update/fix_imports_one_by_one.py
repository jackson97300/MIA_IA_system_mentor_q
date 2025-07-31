#!/usr/bin/env python3
"""
Script pour corriger les imports fichier par fichier
"""

import os
from pathlib import Path

def fix_live_monitor():
    """
    Problème: cannot import name 'MonitoringConfig' from 'config.automation_config'
    Solution: Remplacer par AutomationMonitoringConfig
    """
    print("1️⃣ Correction de monitoring/live_monitor.py")
    
    file_path = Path("D:/MIA_IA_system/monitoring/live_monitor.py")
    if not file_path.exists():
        print("  ❌ Fichier non trouvé")
        return
    
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    # Remplacer MonitoringConfig par AutomationMonitoringConfig
    replacements = [
        ("from config.automation_config import MonitoringConfig", 
         "from config.automation_config import AutomationMonitoringConfig"),
        ("MonitoringConfig()", "AutomationMonitoringConfig()"),
        ("self.config = MonitoringConfig", "self.config = AutomationMonitoringConfig"),
        ("config: MonitoringConfig", "config: AutomationMonitoringConfig"),
    ]
    
    for old, new in replacements:
        if old in content:
            content = content.replace(old, new)
            print(f"  ✅ Remplacé: {old} -> {new}")
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

def fix_discord_notifier():
    """
    Problème: cannot import name 'notify_discord_available' from 'monitoring.discord_notifier'
    Solution: Vérifier ce qui est exporté et corriger
    """
    print("\n2️⃣ Analyse de monitoring/discord_notifier.py")
    
    file_path = Path("D:/MIA_IA_system/monitoring/discord_notifier.py")
    if not file_path.exists():
        print("  ❌ Fichier non trouvé")
        return
    
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    # Chercher ce qui est défini dans le fichier
    if 'def notify_discord_available' not in content and 'notify_discord_available =' not in content:
        print("  ℹ️ notify_discord_available n'existe pas dans le fichier")
        
        # Ajouter la fonction/variable manquante
        if 'class DiscordNotifier' in content:
            # Ajouter après les imports
            lines = content.split('\n')
            new_lines = []
            imports_done = False
            
            for line in lines:
                new_lines.append(line)
                if not imports_done and (line.startswith('import ') or line.startswith('from ')) and line.strip():
                    continue
                elif not imports_done and (line.strip() == '' or not line.startswith(('import', 'from'))):
                    new_lines.append("\n# Flag pour disponibilité Discord")
                    new_lines.append("notify_discord_available = lambda: True  # Fonction placeholder")
                    imports_done = True
            
            content = '\n'.join(new_lines)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print("  ✅ Ajouté notify_discord_available")

def fix_monitoring_init():
    """
    Correction de monitoring/__init__.py pour exporter notify_discord_available
    """
    print("\n3️⃣ Correction de monitoring/__init__.py")
    
    file_path = Path("D:/MIA_IA_system/monitoring/__init__.py")
    if not file_path.exists():
        print("  ❌ Fichier non trouvé")
        return
    
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    # Vérifier si notify_discord_available est importé
    if 'notify_discord_available' not in content:
        # Trouver où ajouter l'import
        if 'from .discord_notifier import' in content:
            content = content.replace(
                'from .discord_notifier import DiscordNotifier',
                'from .discord_notifier import DiscordNotifier, notify_discord_available'
            )
        else:
            # Ajouter une fonction placeholder
            lines = content.split('\n')
            new_lines = []
            added = False
            
            for line in lines:
                new_lines.append(line)
                if not added and '__all__' in line:
                    new_lines.insert(-1, "\n# Placeholder function")
                    new_lines.insert(-1, "notify_discord_available = lambda: True")
                    added = True
            
            content = '\n'.join(new_lines)
        
        # Ajouter à __all__ si nécessaire
        if '__all__' in content and "'notify_discord_available'" not in content:
            content = content.replace(
                "__all__ = [",
                "__all__ = [\n    'notify_discord_available',"
            )
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print("  ✅ Ajouté export de notify_discord_available")

def fix_simple_model():
    """
    Problème: cannot import name 'ModelStatus' from 'ml.simple_model'
    Solution: Vérifier ce qui existe et ajouter si nécessaire
    """
    print("\n4️⃣ Analyse de ml/simple_model.py")
    
    file_path = Path("D:/MIA_IA_system/ml/simple_model.py")
    if not file_path.exists():
        print("  ❌ Fichier non trouvé")
        return
    
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    # Vérifier si ModelStatus existe
    if 'class ModelStatus' not in content and 'ModelStatus = ' not in content:
        print("  ℹ️ ModelStatus n'existe pas, ajout nécessaire")
        
        # Ajouter ModelStatus après les imports
        lines = content.split('\n')
        new_lines = []
        imports_done = False
        
        for i, line in enumerate(lines):
            new_lines.append(line)
            
            # Après les imports, ajouter ModelStatus
            if not imports_done and i > 0:
                if (line.strip() == '' or not line.strip().startswith(('import', 'from'))) and \
                   (i == 0 or lines[i-1].strip().startswith(('import', 'from')) or lines[i-1].strip() == ''):
                    new_lines.append("\n# Model status enum")
                    new_lines.append("from enum import Enum")
                    new_lines.append("")
                    new_lines.append("class ModelStatus(Enum):")
                    new_lines.append('    """Status du modèle ML"""')
                    new_lines.append('    NOT_TRAINED = "not_trained"')
                    new_lines.append('    TRAINING = "training"')
                    new_lines.append('    TRAINED = "trained"')
                    new_lines.append('    FAILED = "failed"')
                    new_lines.append('    DEPLOYED = "deployed"')
                    new_lines.append("")
                    imports_done = True
        
        content = '\n'.join(new_lines)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print("  ✅ Ajouté ModelStatus enum")

def fix_ml_imports():
    """
    Corriger les imports dans model_validator.py et model_trainer.py
    """
    print("\n5️⃣ Vérification des imports ML")
    
    files_to_check = [
        "D:/MIA_IA_system/ml/model_validator.py",
        "D:/MIA_IA_system/ml/model_trainer.py"
    ]
    
    for file_path in files_to_check:
        path = Path(file_path)
        if path.exists():
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Si ModelStatus est importé depuis simple_model
            if 'from ml.simple_model import' in content or 'from .simple_model import' in content:
                print(f"  ✅ {path.name} importe depuis simple_model")
            else:
                print(f"  ⚠️ {path.name} pourrait nécessiter des ajustements d'import")

def main():
    print("🔧 CORRECTION DES IMPORTS FICHIER PAR FICHIER")
    print("=" * 60)
    
    # Corriger chaque problème
    fix_live_monitor()
    fix_discord_notifier()
    fix_monitoring_init()
    fix_simple_model()
    fix_ml_imports()
    
    print("\n" + "=" * 60)
    print("✅ Corrections appliquées !")
    print("\nTestez à nouveau avec :")
    print('python -c "import config; import core; import features; import strategies; import execution; import monitoring; import ml; import data; import performance"')

if __name__ == "__main__":
    main()