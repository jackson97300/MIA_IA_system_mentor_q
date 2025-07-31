#!/usr/bin/env python3
"""
Script pour corriger tous les noms d'import incorrects dans le projet
"""

import os
import re
from pathlib import Path

def fix_file_imports(filepath, replacements):
    """Applique les remplacements dans un fichier"""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        original_content = content
        
        for old, new in replacements.items():
            if old in content:
                content = content.replace(old, new)
        
        if content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        return False
    except Exception as e:
        print(f"  ⚠️ Erreur avec {filepath}: {e}")
        return False

def main():
    print("🔧 CORRECTION DES NOMS D'IMPORT")
    print("=" * 50)
    
    project_root = Path("D:/MIA_IA_system")
    
    # Dictionnaire des remplacements à effectuer
    replacements = {
        # 1. SierraConfig -> SierraIBKRConfig
        "from .sierra_config import SierraIBKRConfig": "from .sierra_config import SierraIBKRConfig",
        "SierraIBKRConfig = None": "SierraIBKRConfig = None",
        "'SierraIBKRConfig': SierraIBKRConfig": "'SierraIBKRConfig': SierraIBKRConfig",
        
        # 2. MonitoringConfig -> AutomationMonitoringConfig
        "from config.automation_config import AutomationMonitoringConfig": "from config.automation_config import AutomationMonitoringConfig",
        "from .automation_config import AutomationMonitoringConfig": "from .automation_config import AutomationMonitoringConfig",
        "AutomationMonitoringConfig()": "AutomationAutomationMonitoringConfig()",
        
        # 3. MimeMultipart (correction de casse)
        "from email.mime.multipart import MIMEMultipart": "from email.mime.multipart import MIMEMultipart",
        "MIMEMultipart(": "MIMEMultipart(",
        
        # 4. MimeText (au cas où il en reste)
        "from email.mime.text import MIMEText": "from email.mime.text import MIMEText",
        "MIMEText(": "MIMEText(",
        
        # 5. SimpleLinearModel -> SimpleLinearPredictor (si c'est le bon nom)
        "from ml.simple_model import SimpleLinearPredictor": "from ml.simple_model import SimpleLinearPredictor",
        "from .simple_model import SimpleLinearPredictor": "from .simple_model import SimpleLinearPredictor",
        "SimpleLinearPredictor(": "SimpleLinearPredictor(",
        
        # 6. DiscordNotifier (vérifier son existence)
        "from monitoring.discord_notifier import DiscordNotifier": "from monitoring.discord_notifier import DiscordNotifier",
    }
    
    # Corriger tous les fichiers Python
    files_fixed = 0
    total_changes = 0
    
    for py_file in project_root.rglob("*.py"):
        if '__pycache__' in str(py_file) or '.git' in str(py_file):
            continue
        
        if fix_file_imports(py_file, replacements):
            print(f"✅ Corrigé: {py_file.relative_to(project_root)}")
            files_fixed += 1
    
    print(f"\n📊 Résumé: {files_fixed} fichiers modifiés")
    
    # Corrections spécifiques pour config/__init__.py
    print("\n📄 Correction spécifique de config/__init__.py...")
    config_init = project_root / "config/__init__.py"
    
    if config_init.exists():
        with open(config_init, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Remplacer toutes les occurrences de SierraConfig
        content = re.sub(r'\bSierraConfig\b', 'SierraIBKRConfig', content)
        
        with open(config_init, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ config/__init__.py corrigé")
    
    # Vérifier si SimpleLinearPredictor existe dans simple_model.py
    print("\n📄 Vérification de ml/simple_model.py...")
    simple_model = project_root / "ml/simple_model.py"
    
    if simple_model.exists():
        with open(simple_model, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if 'class SimpleLinearPredictor' not in content and 'class SimpleLinearModel' in content:
            # Si c'est SimpleLinearModel qui existe, inverser le remplacement
            print("  ℹ️ SimpleLinearModel existe, ajustement des imports...")
            
            # Corriger les fichiers qui importent
            for py_file in project_root.rglob("*.py"):
                if '__pycache__' in str(py_file):
                    continue
                
                try:
                    with open(py_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    if 'SimpleLinearPredictor' in content:
                        content = content.replace('SimpleLinearPredictor', 'SimpleLinearModel')
                        
                        with open(py_file, 'w', encoding='utf-8') as f:
                            f.write(content)
                        
                        print(f"  ✅ Corrigé import dans: {py_file.name}")
                except:
                    pass
    
    print("\n✅ Corrections terminées !")
    print("\nTestez à nouveau avec :")
    print('python -c "import config; import core; import features; import strategies; import execution; import monitoring; import ml; import data; import performance; print(\'✅ Tous les imports fonctionnent !\')"')

if __name__ == "__main__":
    main()