#!/usr/bin/env python3
"""
MIA_IA_SYSTEM - Fix Trend Strategy Deque
Correction IMMÉDIATE du problème deque dans trend_strategy.py
"""

import shutil
from pathlib import Path

def fix_trend_strategy_deque():
    """Correction précise du problème deque dans trend_strategy.py"""
    
    logger.info("🎯 FIX: trend_strategy.py - Missing deque import")
    print("="*55)
    
    trend_path = Path("strategies/trend_strategy.py")
    
    if not trend_path.exists():
        logger.error("strategies/trend_strategy.py n'existe pas!")
        return False
    
    # Backup
    backup_path = Path("strategies/trend_strategy.py.backup_deque")
    shutil.copy2(trend_path, backup_path)
    logger.info("Backup créé: {backup_path}")
    
    # Lire le fichier
    with open(trend_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Vérifier si deque import manque
    if 'from collections import deque' in content:
        logger.info("Import deque déjà présent - problème ailleurs")
        return True
    
    logger.info("🔧 Ajout de l'import deque manquant...")
    
    lines = content.split('\n')
    
    # Trouver où insérer l'import
    insert_index = -1
    
    # Chercher après les imports pandas/numpy mais avant les imports locaux
    for i, line in enumerate(lines):
        if line.strip().startswith('import logging'):

# Configure logging
logger = logging.getLogger(__name__)
            insert_index = i
            break
        elif line.strip().startswith('from collections import'):
            # Ajouter deque à un import collections existant
            if 'deque' not in line:
                lines[i] = line.replace('from collections import', 'from collections import deque,')
                logger.info("Ajouté deque à l'import existant ligne {i+1}")
                insert_index = -2  # Signal que c'est fait
                break
    
    # Si pas d'import collections existant, ajouter un nouvel import
    if insert_index >= 0:
        lines.insert(insert_index, 'from collections import deque')
        logger.info("Nouvel import deque ajouté ligne {insert_index+1}")
    elif insert_index == -1:
        # Ajouter au début des imports
        for i, line in enumerate(lines):
            if line.strip().startswith('import') or line.strip().startswith('from'):
                lines.insert(i, 'from collections import deque')
                logger.info("Import deque ajouté au début des imports ligne {i+1}")
                break
    
    # Écrire le fichier corrigé
    corrected_content = '\n'.join(lines)
    with open(trend_path, 'w', encoding='utf-8') as f:
        f.write(corrected_content)
    
    logger.info("trend_strategy.py corrigé")
    return True

def test_correction():
    """Test de la correction"""
    
    logger.info("\n🔍 TEST DE LA CORRECTION")
    print("="*40)
    
    try:
        # Nettoyer cache
        import sys
        modules_to_clean = [k for k in sys.modules.keys() if k.startswith('strategies')]
        for mod in modules_to_clean:
            del sys.modules[mod]
        logger.info("🧹 Cache nettoyé")
        
        # Test import
        from strategies.trend_strategy import create_trend_strategy
        logger.info("Import create_trend_strategy OK")
        
        # Test instantiation (là où ça plantait)
        trend_strategy = create_trend_strategy()
        logger.info("create_trend_strategy() - SUCCESS!")
        logger.info("Problème deque RÉSOLU!")
        
        # Test complet strategies
        from strategies import create_trend_strategy, create_range_strategy
        logger.info("Import strategies complet OK")
        
        return True
        
    except Exception as e:
        logger.error("Erreur persistante: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Correction principale"""
    
    logger.info("🚨 CORRECTION CIBLÉE: trend_strategy.py missing deque import")
    logger.info("📄 Fichier: strategies/trend_strategy.py")
    logger.info("📍 Ligne: 187 - self.price_history: deque = deque(maxlen=100)")
    logger.info("🔧 Solution: Ajouter 'from collections import deque'")
    print()
    
    # Appliquer correction
    success = fix_trend_strategy_deque()
    
    if success:
        # Tester correction
        if test_correction():
            logger.info("\n🎉 PROBLÈME COMPLÈTEMENT RÉSOLU!")
            logger.info("Import deque ajouté dans trend_strategy.py")
            logger.info("create_trend_strategy() fonctionne")
            logger.info("Tous les imports strategies OK")
            print()
            logger.info("🚀 RELANCEZ MAINTENANT:")
            logger.info("   python test_phase2_integration.py")
        else:
            logger.info("\n⚠️ Correction appliquée mais problèmes persistants")
    else:
        logger.info("\n❌ Échec correction")

if __name__ == "__main__":
    main()