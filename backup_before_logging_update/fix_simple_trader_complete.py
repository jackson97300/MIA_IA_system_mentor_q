#!/usr/bin/env python3
"""
Réparation complète de la section main dans simple_trader.py
Reconstruit proprement la structure du code
"""

from pathlib import Path
import logging

# Configure logging
logger = logging.getLogger(__name__)


def fix_simple_trader_main_section():
    """Répare la section main du fichier"""
    
    file_path = Path("execution/simple_trader.py")
    
    if not file_path.exists():
        logger.error("Fichier {file_path} non trouvé!")
        return False
    
    # Lire le contenu
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    logger.info("📄 Analyse de {len(lines)} lignes...")
    
    # Trouver le début de la section problématique
    main_section_start = None
    for i, line in enumerate(lines):
        if "if __name__ == '__main__':" in line:
            main_section_start = i
            logger.info("Trouvé section main à la ligne {i+1}")
            break
    
    if main_section_start is None:
        logger.error("Section main non trouvée!")
        return False
    
    # Reconstruire la section main proprement
    # Garder tout avant la section main
    new_lines = lines[:main_section_start]
    
    # Ajouter la section main corrigée
    main_section = '''
if __name__ == "__main__":
    """Point d'entrée principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Simple Battle Navale Trader')
    parser.add_argument('--mode', choices=['DATA_COLLECTION', 'PAPER', 'LIVE'], 
                       default='DATA_COLLECTION',
                       help='Trading mode')
    parser.add_argument('--target', type=int, default=1000,
                       help='Nombre de trades cibles pour data collection')
    parser.add_argument('--diagnose-risk', action='store_true',
                       help='Afficher diagnostics configurations risque')
    parser.add_argument('--diagnose-sierra', action='store_true',
                       help='Afficher diagnostics Sierra Chart + IBKR')
    parser.add_argument('--diagnose-all', action='store_true',
                       help='Afficher tous les diagnostics')
    
    args = parser.parse_args()
    
    # Configuration logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Diagnostics si demandés
    if args.diagnose_risk or args.diagnose_all:
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
        if args.mode == 'DATA_COLLECTION':
            logger.info(f"🎯 Lancement mode collecte données - Objectif: {args.target} trades")
            await run_data_collection_session(args.target)
        else:
            trader = create_simple_trader(args.mode.upper())
            # Afficher diagnostics au démarrage
            trader.log_risk_diagnostics()
            await trader.run()
    
    # Lancer avec asyncio
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("⌨️ Arrêt demandé par l'utilisateur")
    except Exception as e:
        logger.error(f"❌ Erreur: {e}", exc_info=True)
'''
    
    # Ajouter la section corrigée
    new_lines.extend(main_section.split('\n'))
    
    # Sauvegarder
    backup_path = file_path.with_suffix('.py.backup2')
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    logger.info("💾 Backup créé: {backup_path}")
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    
    logger.info("Section main reconstruite avec succès!")
    
    return True

def restore_from_backup():
    """Restaure depuis le backup original si disponible"""
    file_path = Path("execution/simple_trader.py")
    backup_path = file_path.with_suffix('.py.backup')
    
    if backup_path.exists():
        logger.info("🔄 Restauration depuis le backup...")
        with open(backup_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logger.info("Restauré depuis le backup")
        return True
    else:
        logger.error("Pas de backup trouvé")
        return False

def check_syntax():
    """Vérifie la syntaxe"""
    import subprocess
    
    result = subprocess.run(
        ["python", "-m", "py_compile", "execution/simple_trader.py"],
        capture_output=True,
        text=True
    )
    
    return result.returncode == 0, result.stderr

if __name__ == "__main__":
    logger.info("🔧 Réparation complète de simple_trader.py...")
    
    # D'abord, essayer de restaurer depuis le backup
    if restore_from_backup():
        # Vérifier la syntaxe du backup
        success, error = check_syntax()
        if success:
            logger.info("Le backup est valide!")
            
            # Maintenant appliquer la correction
            if fix_simple_trader_main_section():
                success, error = check_syntax()
                if success:
                    logger.info("Syntaxe valide après correction!")
                else:
                    logger.error("Erreur de syntaxe: {error}")
            else:
                logger.error("Échec de la correction")
        else:
            logger.error("Le backup a aussi des erreurs: {error}")
            logger.info("💡 Tentative de réparation directe...")
            fix_simple_trader_main_section()
            success, error = check_syntax()
            if success:
                logger.info("Réparation réussie!")
            else:
                logger.error("Erreur persistante: {error}")
    else:
        # Pas de backup, tenter la réparation directe
        logger.info("💡 Tentative de réparation sans backup...")
        fix_simple_trader_main_section()
        success, error = check_syntax()
        if success:
            logger.info("Réparation réussie!")
        else:
            logger.error("Erreur: {error}")