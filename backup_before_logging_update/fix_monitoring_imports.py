#!/usr/bin/env python3
"""
Correction des erreurs d'import dans monitoring
"""

import shutil
from pathlib import Path

def fix_monitoring_config():
    """Corrige l'erreur MonitoringConfig"""
    
    print("CORRECTION 1: MonitoringConfig")
    print("="*60)
    
    # Option 1: Ajouter MonitoringConfig comme alias dans automation_config.py
    config_path = Path("config/automation_config.py")
    if config_path.exists():
        with open(config_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Si AutomationMonitoringConfig existe mais pas MonitoringConfig
        if "class AutomationMonitoringConfig" in content and "MonitoringConfig = AutomationMonitoringConfig" not in content:
            # Ajouter l'alias à la fin du fichier
            content += "\n\n# Alias pour compatibilité\nMonitoringConfig = AutomationMonitoringConfig\n"
            
            with open(config_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print("✅ Ajouté alias MonitoringConfig = AutomationMonitoringConfig")
        else:
            print("ℹ️ MonitoringConfig déjà présent ou AutomationMonitoringConfig non trouvé")

def fix_notify_discord():
    """Corrige l'erreur notify_discord_available"""
    
    print("\nCORRECTION 2: notify_discord_available")
    print("="*60)
    
    # Ajouter la fonction dans discord_notifier.py
    discord_path = Path("monitoring/discord_notifier.py")
    if discord_path.exists():
        with open(discord_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if "def notify_discord_available" not in content:
            # Ajouter la fonction
            function_code = '''
def notify_discord_available() -> bool:
    """Vérifie si Discord est disponible pour les notifications"""
    try:
        import discord
        return True
    except ImportError:
        return False
'''
            
            # Ajouter après les imports ou à la fin
            if "# === FUNCTIONS ===" in content:
                content = content.replace("# === FUNCTIONS ===", f"# === FUNCTIONS ===\n{function_code}")
            else:
                content += f"\n{function_code}"
            
            with open(discord_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print("✅ Ajouté fonction notify_discord_available dans discord_notifier.py")
    
    # Exporter dans monitoring/__init__.py
    init_path = Path("monitoring/__init__.py")
    if init_path.exists():
        with open(init_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Ajouter l'import
        if "from .discord_notifier import notify_discord_available" not in content:
            # Trouver où ajouter
            lines = content.split('\n')
            new_lines = []
            added = False
            
            for line in lines:
                new_lines.append(line)
                
                # Ajouter après les imports discord_notifier
                if "from .discord_notifier import" in line and not added:
                    new_lines.append("try:")
                    new_lines.append("    from .discord_notifier import notify_discord_available")
                    new_lines.append("    __all__.append('notify_discord_available')")
                    new_lines.append("except ImportError:")
                    new_lines.append("    logger.warning('Could not import notify_discord_available')")
                    added = True
            
            if not added:
                # Ajouter avant la fin
                insert_idx = len(new_lines) - 1
                new_lines.insert(insert_idx, "\n# Discord notification check")
                new_lines.insert(insert_idx + 1, "try:")
                new_lines.insert(insert_idx + 2, "    from .discord_notifier import notify_discord_available")
                new_lines.insert(insert_idx + 3, "except ImportError:")
                new_lines.insert(insert_idx + 4, "    notify_discord_available = lambda: False")
            
            content = '\n'.join(new_lines)
            
            with open(init_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print("✅ Ajouté export notify_discord_available dans monitoring/__init__.py")

def test_all_imports():
    """Test final de tous les imports"""
    
    print("\n" + "="*60)
    print("TEST FINAL DE TOUS LES IMPORTS")
    print("="*60)
    
    # Test 1: ML
    try:
        from ml import SimpleLinearModel, ModelTrainer, ModelValidator
        print("✅ Imports ML: OK")
    except ImportError as e:
        print(f"❌ Imports ML: {e}")
    
    # Test 2: Monitoring
    try:
        from config.automation_config import MonitoringConfig
        print("✅ Import MonitoringConfig: OK")
    except ImportError:
        try:
            from config.automation_config import AutomationMonitoringConfig as MonitoringConfig
            print("✅ Import MonitoringConfig (via alias): OK")
        except ImportError as e:
            print(f"❌ Import MonitoringConfig: {e}")
    
    # Test 3: Discord
    try:
        from monitoring.discord_notifier import notify_discord_available
        print("✅ Import notify_discord_available: OK")
    except ImportError as e:
        print(f"⚠️ Import notify_discord_available: {e} (non critique)")
    
    # Test 4: Import global
    print("\nTest import global...")
    import subprocess
    result = subprocess.run([
        'python', '-c', 
        'import config; import core; import features; import strategies; '
        'import execution; import monitoring; import ml; import data; import performance; '
        'print("✅ Tous les modules importés avec succès!")'
    ], capture_output=True, text=True)
    
    print(result.stdout)
    if result.stderr:
        print("Warnings:", result.stderr)

if __name__ == "__main__":
    # 1. Corriger ML
    from fix_ml_init_exports import fix_ml_init
    fix_ml_init()
    
    # 2. Corriger Monitoring
    fix_monitoring_config()
    fix_notify_discord()
    
    # 3. Tester
    test_all_imports()