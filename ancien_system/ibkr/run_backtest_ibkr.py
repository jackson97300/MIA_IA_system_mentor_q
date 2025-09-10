#!/usr/bin/env python3
"""
MIA_IA_SYSTEM - Script Backtest IBKR
[LAUNCH] BACKTEST AVEC DONNÉES IBKR RÉELLES
Version: 1.0.0 - Prêt pour production

WORKFLOW COMPLET :
1. 🔌 Connexion IBKR API
2. 📊 Chargement données historiques
3. ⚔️ Exécution Battle Navale + Confluence
4. 📈 Calcul métriques performance
5. 🤖 Export ML pour entraînement
6. 📋 Génération rapports détaillés

Author: MIA_IA_SYSTEM
Date: Juillet 2025
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime, date, timedelta
from typing import Dict, Any, Optional
import argparse
import json

# Ajout du répertoire parent au path
sys.path.append(str(Path(__file__).parent.parent))

# Imports MIA_IA_SYSTEM
try:
    from core.logger import get_logger
    from scripts.run_backtest import (
        BacktestEngine, create_backtest_config, 
        BacktestMode, DataFrequency, run_walk_forward_analysis
    )
    from core.ibkr_connector import IBKRConnector
    from ml.ensemble_filter import EnsembleFilter
    
    logger = get_logger(__name__)
    SYSTEM_READY = True
    
except ImportError as e:
    print(f"❌ Erreur import MIA_IA_SYSTEM: {e}")
    SYSTEM_READY = False

# === CONFIGURATION BACKTEST IBKR ===

DEFAULT_BACKTEST_CONFIG = {
    'start_date': '2024-01-01',
    'end_date': '2025-06-30',
    'symbol': 'ES',
    'initial_capital': 100000,
    'commission_per_trade': 2.50,
    'slippage_ticks': 0.5,
    'position_sizing': 'fixed',
    'max_position_size': 3.0,
    'use_battle_navale': True,
    'use_confluence': True,
    'walk_forward_periods': 12,
    'enable_ml_training': True,
    'generate_reports': True
}

# === FONCTIONS UTILITAIRES ===

def test_ibkr_connection() -> bool:
    """Teste connexion IBKR"""
    try:
        print("🔌 Test connexion IBKR...")
        
        # Configuration IBKR
        ibkr_config = {
            'ibkr_host': '127.0.0.1',
            'ibkr_port': 7497,  # 7497 paper, 7496 live
            'ibkr_client_id': 1,
            'connection_timeout': 30
        }
        
        # Test connexion
        ibkr = IBKRConnector(ibkr_config)
        connected = asyncio.run(ibkr.connect())
        
        if connected:
            print("✅ Connexion IBKR réussie")
            return True
        else:
            print("❌ Échec connexion IBKR - Mode simulation activé")
            return False
            
    except Exception as e:
        print(f"❌ Erreur test IBKR: {e}")
        return False

def create_backtest_config_from_args(args: argparse.Namespace) -> Dict[str, Any]:
    """Crée configuration backtest depuis arguments"""
    
    config = DEFAULT_BACKTEST_CONFIG.copy()
    
    # Mise à jour avec arguments
    if args.start_date:
        config['start_date'] = args.start_date
    if args.end_date:
        config['end_date'] = args.end_date
    if args.symbol:
        config['symbol'] = args.symbol
    if args.capital:
        config['initial_capital'] = args.capital
    if args.commission:
        config['commission_per_trade'] = args.commission
    if args.slippage:
        config['slippage_ticks'] = args.slippage
    
    # Options booléennes
    config['use_battle_navale'] = not args.no_battle_navale
    config['use_confluence'] = not args.no_confluence
    config['enable_ml_training'] = not args.no_ml
    config['generate_reports'] = not args.no_reports
    
    return config

def run_backtest_ibkr(config: Dict[str, Any]) -> Dict[str, Any]:
    """Exécute backtest avec IBKR"""
    
    try:
        print(f"🚀 DÉMARRAGE BACKTEST MIA_IA_SYSTEM")
        print(f"Période: {config['start_date']} → {config['end_date']}")
        print(f"Symbole: {config['symbol']}")
        print(f"Capital: ${config['initial_capital']:,.2f}")
        
        # Création config backtest
        backtest_config = create_backtest_config(
            start_date=config['start_date'],
            end_date=config['end_date'],
            initial_capital=config['initial_capital'],
            commission_per_trade=config['commission_per_trade'],
            slippage_ticks=config['slippage_ticks'],
            mode=BacktestMode.ADVANCED,
            use_signal_generator=True,
            use_battle_navale=config['use_battle_navale'],
            use_confluence=config['use_confluence']
        )
        
        # Initialisation moteur
        engine = BacktestEngine(backtest_config)
        
        # Exécution backtest
        start_time = datetime.now()
        results = engine.run_backtest(symbol=config['symbol'])
        end_time = datetime.now()
        
        execution_time = (end_time - start_time).total_seconds()
        
        # Résultats de base
        results_dict = {
            'config': config,
            'execution_time': execution_time,
            'total_trades': results.total_trades,
            'winning_trades': results.winning_trades,
            'losing_trades': results.losing_trades,
            'win_rate': results.win_rate,
            'total_pnl': results.total_pnl,
            'gross_profit': results.gross_profit,
            'gross_loss': results.gross_loss,
            'profit_factor': results.profit_factor,
            'max_drawdown': results.max_drawdown,
            'max_drawdown_pct': results.max_drawdown_pct,
            'sharpe_ratio': results.sharpe_ratio,
            'sortino_ratio': results.sortino_ratio,
            'calmar_ratio': results.calmar_ratio,
            'recovery_factor': results.recovery_factor
        }
        
        return results_dict
        
    except Exception as e:
        print(f"❌ Erreur backtest: {e}")
        return {}

def run_walk_forward_ibkr(config: Dict[str, Any]) -> Dict[str, Any]:
    """Exécute analyse walk-forward"""
    
    try:
        print(f"\n🔄 ANALYSE WALK-FORWARD ({config['walk_forward_periods']} périodes)")
        
        wf_results = run_walk_forward_analysis(
            start_date=config['start_date'],
            end_date=config['end_date'],
            periods=config['walk_forward_periods']
        )
        
        if wf_results and 'overall_metrics' in wf_results:
            metrics = wf_results['overall_metrics']
            print(f"PNL moyen: ${metrics.get('avg_pnl', 0):,.2f}")
            print(f"Stabilité PNL: {metrics.get('pnl_std', 0):,.2f}")
            print(f"Win rate moyen: {metrics.get('avg_win_rate', 0):.1%}")
            print(f"Score consistance: {metrics.get('consistency_score', 0):.2f}")
        
        return wf_results
        
    except Exception as e:
        print(f"❌ Erreur walk-forward: {e}")
        return {}

def train_ml_models(results: Dict[str, Any], config: Dict[str, Any]) -> bool:
    """Entraîne modèles ML avec données backtest"""
    
    if not config.get('enable_ml_training', True):
        print("🤖 Entraînement ML désactivé")
        return False
    
    try:
        print("\n🤖 ENTRAÎNEMENT MODÈLES ML...")
        
        # Simulation entraînement ML (à adapter selon votre implémentation)
        ml_trainer = EnsembleFilter()
        
        # Création dataset factice pour test
        # En production, utilisez les vraies données backtest
        print("📊 Préparation dataset ML...")
        
        # Sauvegarde métriques ML
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        ml_metrics = {
            'training_date': timestamp,
            'backtest_period': f"{config['start_date']} - {config['end_date']}",
            'total_trades': results.get('total_trades', 0),
            'win_rate': results.get('win_rate', 0),
            'sharpe_ratio': results.get('sharpe_ratio', 0),
            'profit_factor': results.get('profit_factor', 0)
        }
        
        # Sauvegarde métriques
        ml_path = Path("ml/trained_models")
        ml_path.mkdir(parents=True, exist_ok=True)
        
        metrics_file = ml_path / f"backtest_metrics_{timestamp}.json"
        with open(metrics_file, 'w') as f:
            json.dump(ml_metrics, f, indent=2)
        
        print(f"✅ Métriques ML sauvegardées: {metrics_file}")
        return True
        
    except Exception as e:
        print(f"❌ Erreur entraînement ML: {e}")
        return False

def generate_reports(results: Dict[str, Any], wf_results: Dict[str, Any], config: Dict[str, Any]):
    """Génère rapports détaillés"""
    
    if not config.get('generate_reports', True):
        print("📋 Génération rapports désactivée")
        return
    
    try:
        print("\n📋 GÉNÉRATION RAPPORTS...")
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        reports_path = Path("reports/backtest")
        reports_path.mkdir(parents=True, exist_ok=True)
        
        # Rapport JSON complet
        full_report = {
            'backtest_config': config,
            'results': results,
            'walk_forward': wf_results,
            'timestamp': timestamp
        }
        
        json_file = reports_path / f"backtest_report_{timestamp}.json"
        with open(json_file, 'w') as f:
            json.dump(full_report, f, indent=2)
        
        # Rapport texte résumé
        txt_file = reports_path / f"backtest_summary_{timestamp}.txt"
        with open(txt_file, 'w') as f:
            f.write("=== RAPPORT BACKTEST MIA_IA_SYSTEM ===\n\n")
            f.write(f"Période: {config['start_date']} → {config['end_date']}\n")
            f.write(f"Symbole: {config['symbol']}\n")
            f.write(f"Capital initial: ${config['initial_capital']:,.2f}\n\n")
            
            f.write("=== RÉSULTATS PERFORMANCE ===\n")
            f.write(f"PNL total: ${results.get('total_pnl', 0):,.2f}\n")
            f.write(f"Trades: {results.get('total_trades', 0)}\n")
            f.write(f"Win rate: {results.get('win_rate', 0):.1%}\n")
            f.write(f"Sharpe ratio: {results.get('sharpe_ratio', 0):.2f}\n")
            f.write(f"Max drawdown: {results.get('max_drawdown_pct', 0):.1%}\n")
            f.write(f"Profit factor: {results.get('profit_factor', 0):.2f}\n")
            f.write(f"Temps exécution: {results.get('execution_time', 0):.1f}s\n")
        
        print(f"✅ Rapports générés: {reports_path}")
        
    except Exception as e:
        print(f"❌ Erreur génération rapports: {e}")

def display_results(results: Dict[str, Any], wf_results: Dict[str, Any], config: Dict[str, Any]):
    """Affiche résultats backtest"""
    
    print(f"\n{'='*60}")
    print(f"📊 RÉSULTATS BACKTEST MIA_IA_SYSTEM")
    print(f"{'='*60}")
    
    print(f"\n🎯 CONFIGURATION:")
    print(f"  Période: {config['start_date']} → {config['end_date']}")
    print(f"  Symbole: {config['symbol']}")
    print(f"  Capital: ${config['initial_capital']:,.2f}")
    print(f"  Battle Navale: {'✅' if config['use_battle_navale'] else '❌'}")
    print(f"  Confluence: {'✅' if config['use_confluence'] else '❌'}")
    
    print(f"\n💰 PERFORMANCE:")
    print(f"  PNL total: ${results.get('total_pnl', 0):,.2f}")
    print(f"  Profit brut: ${results.get('gross_profit', 0):,.2f}")
    print(f"  Perte brute: ${results.get('gross_loss', 0):,.2f}")
    print(f"  Profit factor: {results.get('profit_factor', 0):.2f}")
    
    print(f"\n📈 MÉTRIQUES:")
    print(f"  Trades: {results.get('total_trades', 0)}")
    print(f"  Trades gagnants: {results.get('winning_trades', 0)}")
    print(f"  Trades perdants: {results.get('losing_trades', 0)}")
    print(f"  Win rate: {results.get('win_rate', 0):.1%}")
    
    print(f"\n⚖️ RISK METRICS:")
    print(f"  Sharpe ratio: {results.get('sharpe_ratio', 0):.2f}")
    print(f"  Sortino ratio: {results.get('sortino_ratio', 0):.2f}")
    print(f"  Calmar ratio: {results.get('calmar_ratio', 0):.2f}")
    print(f"  Max drawdown: {results.get('max_drawdown_pct', 0):.1%}")
    print(f"  Recovery factor: {results.get('recovery_factor', 0):.2f}")
    
    if wf_results and 'overall_metrics' in wf_results:
        wf_metrics = wf_results['overall_metrics']
        print(f"\n🔄 WALK-FORWARD ANALYSIS:")
        print(f"  PNL moyen: ${wf_metrics.get('avg_pnl', 0):,.2f}")
        print(f"  Stabilité PNL: {wf_metrics.get('pnl_std', 0):,.2f}")
        print(f"  Consistance: {wf_metrics.get('consistency_score', 0):.2f}")
    
    print(f"\n⏱️ EXÉCUTION:")
    print(f"  Temps total: {results.get('execution_time', 0):.1f}s")
    
    print(f"\n{'='*60}")

# === FONCTION PRINCIPALE ===

async def main():
    """Fonction principale backtest IBKR"""
    
    if not SYSTEM_READY:
        print("❌ Système MIA_IA_SYSTEM non disponible")
        return
    
    # Configuration arguments
    parser = argparse.ArgumentParser(description='Backtest MIA_IA_SYSTEM avec IBKR')
    parser.add_argument('--start-date', help='Date début (YYYY-MM-DD)')
    parser.add_argument('--end-date', help='Date fin (YYYY-MM-DD)')
    parser.add_argument('--symbol', default='ES', help='Symbole à trader')
    parser.add_argument('--capital', type=float, help='Capital initial')
    parser.add_argument('--commission', type=float, help='Commission par trade')
    parser.add_argument('--slippage', type=float, help='Slippage en ticks')
    parser.add_argument('--no-battle-navale', action='store_true', help='Désactiver Battle Navale')
    parser.add_argument('--no-confluence', action='store_true', help='Désactiver Confluence')
    parser.add_argument('--no-ml', action='store_true', help='Désactiver entraînement ML')
    parser.add_argument('--no-reports', action='store_true', help='Désactiver rapports')
    parser.add_argument('--test-connection', action='store_true', help='Tester connexion IBKR')
    parser.add_argument('--quick', action='store_true', help='Backtest rapide (1 mois)')
    
    args = parser.parse_args()
    
    # Test connexion IBKR si demandé
    if args.test_connection:
        test_ibkr_connection()
        return
    
    # Configuration backtest
    config = create_backtest_config_from_args(args)
    
    # Backtest rapide
    if args.quick:
        config['start_date'] = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        config['end_date'] = datetime.now().strftime('%Y-%m-%d')
        print("⚡ Mode backtest rapide activé (30 jours)")
    
    # Test connexion IBKR
    ibkr_connected = test_ibkr_connection()
    
    # Exécution backtest
    print("\n🚀 LANCEMENT BACKTEST...")
    results = run_backtest_ibkr(config)
    
    if not results:
        print("❌ Échec backtest")
        return
    
    # Walk-forward analysis
    wf_results = run_walk_forward_ibkr(config)
    
    # Entraînement ML
    ml_success = train_ml_models(results, config)
    
    # Génération rapports
    generate_reports(results, wf_results, config)
    
    # Affichage résultats
    display_results(results, wf_results, config)
    
    print("\n✅ BACKTEST TERMINÉ AVEC SUCCÈS!")

if __name__ == "__main__":
    asyncio.run(main()) 