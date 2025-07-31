#!/usr/bin/env python3
"""
Script de lancement pour automation_main.py avec encodage UTF-8
Évite les problèmes d'affichage des emojis sur Windows
"""

import os
import sys
import subprocess
import logging

# Configure logging
logger = logging.getLogger(__name__)


def launch_automation():
    """Lance automation_main.py avec le bon encodage"""
    
    # Définir l'encodage UTF-8
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    
    # Récupérer les arguments
    args = sys.argv[1:] if len(sys.argv) > 1 else ['--mode', 'paper', '--dry-run']
    
    # Construire la commande
    cmd = [sys.executable, 'automation_main.py'] + args
    
    logger.info("🚀 Lancement MIA Automation Bot avec encodage UTF-8...")
    logger.info("📋 Commande: {' '.join(cmd)}")
    print("=" * 60)
    
    # Lancer le processus
    try:
        # Utiliser subprocess pour mieux contrôler l'encodage
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            encoding='utf-8',
            errors='replace'
        )
        
        # Afficher la sortie en temps réel
        for line in process.stdout:
            print(line, end='')
        
        # Attendre la fin
        return_code = process.wait()
        
        if return_code != 0:
            logger.info("\n❌ Erreur: code de sortie {return_code}")
        else:
            logger.info("\n✅ Terminé avec succès")
            
        return return_code
        
    except KeyboardInterrupt:
        logger.info("\n⌨️ Arrêt demandé par l'utilisateur")
        return 1
    except Exception as e:
        logger.info("\n❌ Erreur: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(launch_automation())