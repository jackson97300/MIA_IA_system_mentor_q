#!/usr/bin/env python3
"""
Script de lancement amélioré pour automation_main.py
Gère correctement l'encodage UTF-8 sur Windows
"""

import os
import sys
import subprocess
import locale
import logging

# Configure logging
logger = logging.getLogger(__name__)

def setup_utf8_environment():
    """Configure l'environnement pour UTF-8"""
    # Forcer UTF-8
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    os.environ['PYTHONLEGACYWINDOWSSTDIO'] = 'utf-8'
    
    # Essayer de configurer la console Windows
    if sys.platform == 'win32':
        try:
            # Changer la page de code en UTF-8
            subprocess.run(['chcp', '65001'], shell=True, capture_output=True)
        except:
            pass

def launch_automation():
    """Lance automation_main.py avec le bon encodage"""
    
    # Configurer UTF-8
    setup_utf8_environment()
    
    # Récupérer les arguments
    args = sys.argv[1:] if len(sys.argv) > 1 else ['--mode', 'paper', '--dry-run']
    
    # Construire la commande
    cmd = [sys.executable, '-X', 'utf8', 'automation_main.py'] + args
    
    logger.info("🚀 Lancement MIA Automation Bot...")
    logger.info("📋 Commande: {' '.join(cmd)}")
    print("=" * 60)
    
    # D'abord, corriger l'erreur de syntaxe si nécessaire
    logger.info("🔧 Vérification de simple_trader.py...")
    fix_result = subprocess.run(
        [sys.executable, 'fix_simple_trader.py'],
        capture_output=True,
        text=True,
        encoding='utf-8'
    )
    
    if fix_result.returncode != 0 and "non trouvé" not in fix_result.stdout:
        logger.warning("Problème avec simple_trader.py")
    
    # Lancer le processus principal
    try:
        # Utiliser un environnement Python propre
        env = os.environ.copy()
        env['PYTHONIOENCODING'] = 'utf-8'
        
        # Pour Windows, utiliser un wrapper qui force UTF-8
        if sys.platform == 'win32':
            # Créer un wrapper temporaire
            wrapper_code = f'''
import sys

# Forcer UTF-8 sur stdout et stderr

# Importer et lancer le script principal
sys.argv = {['automation_main.py'] + args}
exec(open('automation_main.py', encoding='utf-8').read())
'''
            
            # Exécuter via le wrapper
            process = subprocess.Popen(
                [sys.executable, '-c', wrapper_code],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                encoding='utf-8',
                errors='replace',
                env=env
            )
        else:
            # Unix/Linux - plus simple
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                encoding='utf-8',
                errors='replace',
                env=env
            )
        
        # Afficher la sortie en temps réel
        for line in process.stdout:
            # Remplacer les emojis par du texte si problème persiste
            line = line.replace('🚀', '[START]')
            line = line.replace('✅', '[OK]')
            line = line.replace('❌', '[ERROR]')
            line = line.replace('📊', '[STATS]')
            line = line.replace('🧠', '[BRAIN]')
            line = line.replace('⚡', '[CACHE]')
            line = line.replace('📋', '[INFO]')
            line = line.replace('🔧', '[FIX]')
            line = line.replace('⚠️', '[WARN]')
            
            print(line, end='')
        
        # Attendre la fin
        return_code = process.wait()
        
        if return_code != 0:
            logger.info("\n[ERROR] Code de sortie: {return_code}")
        else:
            logger.info("\n[OK] Terminé avec succès")
            
        return return_code
        
    except KeyboardInterrupt:
        logger.info("\n[STOP] Arrêt demandé par l'utilisateur")
        return 1
    except Exception as e:
        logger.info("\n[ERROR] Erreur: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(launch_automation())