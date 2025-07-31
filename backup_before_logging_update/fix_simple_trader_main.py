#!/usr/bin/env python3
"""
Script pour corriger la section main de simple_trader.py
Corrige les problèmes d'indentation
"""

from pathlib import Path
import logging

# Configure logging
logger = logging.getLogger(__name__)


def fix_main_section():
    """Corrige la section main avec la bonne indentation"""
    
    file_path = Path("execution/simple_trader.py")
    
    if not file_path.exists():
        logger.error("Fichier {file_path} non trouvé!")
        return False
    
    # Lire le contenu
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Trouver la section problématique et la remplacer
    # On va remplacer toute la section après "if __name__ == "__main__":"
    
    main_section_correct = '''if __name__ == "__main__":
    import argparse
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Arguments
    parser = argparse.ArgumentParser(description='MIA Trading Bot')
    parser.add_argument('--mode', choices=['data_collection', 'paper', 'live'], 
                       default='paper', help='Trading mode')
    parser.add_argument('--target', type=int, default=500, 
                       help='Target trades for data collection')
    parser.add_argument('--diagnose', action='store_true',
                       help='Show risk configuration diagnostics')
    parser.add_argument('--diagnose-sierra', action='store_true',
                       help='Show Sierra Chart + IBKR diagnostics')
    parser.add_argument('--diagnose-all', action='store_true',
                       help='Show all diagnostics (risk + sierra/ibkr)')
    args = parser.parse_args()
    
    # Diagnostics si demandé
    if args.diagnose or args.diagnose_all:
        from config.data_collection_risk_config import compare_risk_modes, validate_all_configs
        logger.info("🔍 DIAGNOSTICS CONFIGURATIONS RISQUE")
        compare_risk_modes()
        validate_all_configs()
        if not args.diagnose_all:
            sys.exit(0)
    
    if args.diagnose_sierra or args.diagnose_all:
        # Créer trader temporaire pour diagnostics
        temp_trader = create_simple_trader(args.mode.upper())
        logger.info("🔧 DIAGNOSTICS SIERRA CHART + IBKR")
        temp_trader.log_sierra_ibkr_diagnostics()
        if not args.diagnose_all:
            sys.exit(0)
    
    # Run
    async def main():
        if args.mode == 'data_collection':
            logger.info(f"🎯 Lancement mode collecte données - Objectif: {args.target} trades")
            await run_data_collection_session(args.target)
        else:
            trader = create_simple_trader(args.mode.upper())
            # Afficher diagnostics au démarrage
            trader.log_risk_diagnostics()
            if await trader.start_trading_session():
                await trader.run_trading_loop()
    
    asyncio.run(main())'''
    
    # Trouver où insérer
    main_start = content.find('if __name__ == "__main__":')
    
    if main_start == -1:
        logger.error("Section main non trouvée!")
        return False
    
    # Garder tout avant la section main
    new_content = content[:main_start] + main_section_correct
    
    # Ajouter les commentaires finaux s'ils existent
    comments_section = '''

# === NOUVELLES FONCTIONNALITÉS AJOUTÉES ===

# 1. CONFIGURATION SIERRA CHART + IBKR INTÉGRÉE
# - Configuration automatique selon le mode (paper/live/data_collection)
# - Validation complète des paramètres
# - Synchronisation avec risk manager

# 2. DIAGNOSTICS ÉTENDUS
# - python simple_trader.py --diagnose              # Risk config
# - python simple_trader.py --diagnose-sierra       # Sierra/IBKR config  
# - python simple_trader.py --diagnose-all          # Tout

# 3. MODES OPTIMISÉS
# - PAPER: MES contracts, IBKR port 7497, simulation
# - LIVE: ES contracts, IBKR port 7496, Sierra Chart trading
# - DATA_COLLECTION: Multi-symbols, tick data, no trading

# 4. SÉCURITÉ RENFORCÉE
# - Kill switch automatique selon daily loss limit
# - Validation croisée IBKR/Sierra Chart
# - Fat finger protection
# - Position limits dynamiques

# 5. STATUS ENRICHI
# trader.get_status() inclut maintenant:
# - sierra_ibkr_status: Statut complet connexions
# - Config validation en temps réel
# - Recommandations par mode

# 6. CHANGEMENT MODE À CHAUD
# trader.update_risk_mode("LIVE")  # Met à jour risk + sierra/ibkr

# EXEMPLE D'USAGE COMPLET:
# 
# # 1. Paper trading avec diagnostics
# python simple_trader.py --mode paper --diagnose-all
#
# # 2. Data collection 1000 trades 
# python simple_trader.py --mode data_collection --target 1000
#
# # 3. Live trading production
# python simple_trader.py --mode live
#
# # 4. Diagnostics seulement
# python simple_trader.py --diagnose-sierra
'''
    
    new_content += comments_section
    
    # Sauvegarder
    backup_path = file_path.with_suffix('.py.backup_indent')
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(content)
    logger.info("💾 Backup créé: {backup_path}")
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    logger.info("Section main corrigée avec succès!")
    return True

def check_syntax():
    """Vérifie la syntaxe"""
    import subprocess
    
    result = subprocess.run(
        ["python", "-m", "py_compile", "execution/simple_trader.py"],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        logger.info("Syntaxe valide!")
        return True
    else:
        logger.error("Erreur de syntaxe:\n{result.stderr}")
        return False

if __name__ == "__main__":
    logger.info("🔧 Correction de l'indentation dans simple_trader.py...")
    
    if fix_main_section():
        logger.info("\n🔍 Vérification de la syntaxe...")
        if check_syntax():
            logger.info("\n✨ Fichier corrigé avec succès!")
            logger.info("\nVous pouvez maintenant lancer:")
            logger.info("python automation_main.py --mode paper --dry-run")
        else:
            logger.info("\n⚠️ Il reste des erreurs à corriger")
    else:
        logger.info("\n❌ Échec de la correction")