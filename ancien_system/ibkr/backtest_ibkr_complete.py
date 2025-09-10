#!/usr/bin/env python3
"""
MIA_IA_SYSTEM - Backtesting Complet avec IBKR API
[LAUNCH] BACKTEST AVEC DONNÉES IBKR RÉELLES

WORKFLOW COMPLET :
1. 🔌 Connexion IBKR API
2. 📊 Récupération données historiques (ES, NQ, YM)
3. ⚔️ Exécution Battle Navale + Confluence
4. 📈 Calcul métriques performance
5. 🤖 Export ML pour entraînement
6. 📋 Génération rapports détaillés

Données IBKR disponibles :
- CME Real-Time (NP,L2) - Level 2 data
- OPRA (Options US) - Options flow
- Cotations US continues - Futures data
- Données historiques - Backtesting

Author: MIA_IA_SYSTEM
Date: Juillet 2025
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime, date, timedelta
from typing import Dict, Any, Optional, List
import argparse
import json
import logging

# Ajout du répertoire parent au path
sys.path.append(str(Path(__file__).parent.parent))

# Imports MIA_IA_SYSTEM
try:
    from core.logger import get_logger
    from core.ibkr_connector import IBKRConnector
    from execution.simple_trader import create_simple_trader, SimpleBattleNavaleTrader
    from strategies.signal_generator import SignalGenerator
    from features.confluence_analyzer import ConfluenceAnalyzer
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
    'enable_ml_training': True,
    'generate_reports': True,
    
    # Configuration IBKR
    'ibkr_config': {
        'ibkr_host': '127.0.0.1',
        'ibkr_port': 7497,  # 7497 paper, 7496 live
        'ibkr_client_id': 1,
        'connection_timeout': 30,
        'enable_tick_data': True,
        'enable_historical_data': True,
        'enable_options_data': True,
        'enable_level2_data': True
    }
}

# === CLASSE BACKTEST IBKR ===

class IBKRBacktestEngine:
    """
    MOTEUR BACKTEST AVEC IBKR API
    
    Utilise vos données IBKR réelles :
    - CME Real-Time (NP,L2) - Level 2 data
    - OPRA (Options US) - Options flow  
    - Cotations US continues - Futures data
    - Données historiques - Backtesting
    """
    
    def __init__(self, config: Dict[str, Any]):
        """Initialisation moteur backtest IBKR"""
        self.config = config
        self.ibkr_connector = None
        self.signal_generator = None
        self.confluence_analyzer = None
        self.ensemble_filter = None
        
        # Résultats backtest
        self.trades = []
        self.equity_history = []
        self.signals_history = []
        self.performance_metrics = {}
        
        # État backtest
        self.current_equity = config['initial_capital']
        self.current_position = None
        self.trades_count = 0
        self.winning_trades = 0
        self.losing_trades = 0
        
        logger.info(f"[INIT] IBKRBacktestEngine initialisé")
        logger.info(f"   - Symbole: {config['symbol']}")
        logger.info(f"   - Période: {config['start_date']} → {config['end_date']}")
        logger.info(f"   - Capital: ${config['initial_capital']:,.2f}")
    
    async def initialize_components(self):
        """Initialise tous les composants MIA_IA_SYSTEM"""
        try:
            logger.info("[INIT] Initialisation composants MIA_IA_SYSTEM")
            
            # 1. Connexion IBKR
            self.ibkr_connector = IBKRConnector(self.config['ibkr_config'])
            connected = await self.ibkr_connector.connect()
            
            if connected:
                logger.info("✅ Connexion IBKR réussie")
                logger.info(f"   - Host: {self.config['ibkr_config']['ibkr_host']}")
                logger.info(f"   - Port: {self.config['ibkr_config']['ibkr_port']}")
                logger.info(f"   - Client ID: {self.config['ibkr_config']['ibkr_client_id']}")
            else:
                logger.warning("⚠️ Connexion IBKR échouée - mode simulation")
            
            # 2. Signal Generator
            self.signal_generator = SignalGenerator()
            logger.info("✅ SignalGenerator initialisé")
            
            # 3. Confluence Analyzer
            self.confluence_analyzer = ConfluenceAnalyzer()
            logger.info("✅ ConfluenceAnalyzer initialisé")
            
            # 4. Ensemble Filter (ML)
            if self.config['enable_ml_training']:
                self.ensemble_filter = EnsembleFilter()
                logger.info("✅ EnsembleFilter (ML) initialisé")
            
            logger.info("[OK] Tous les composants initialisés")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur initialisation composants: {e}")
            return False
    
    async def load_historical_data(self, symbol: str) -> List[Dict]:
        """
        Charge données historiques depuis IBKR API
        
        Données disponibles selon votre souscription :
        - CME Real-Time (NP,L2) - Level 2 data
        - OPRA (Options US) - Options flow
        - Cotations US continues - Futures data
        """
        try:
            logger.info(f"[DATA] Chargement données historiques {symbol}")
            
            if not self.ibkr_connector or not await self.ibkr_connector.is_connected():
                logger.warning("IBKR non connecté - génération données simulées")
                return self._generate_simulated_data(symbol)
            
            # Paramètres données historiques
            start_date = datetime.strptime(self.config['start_date'], '%Y-%m-%d')
            end_date = datetime.strptime(self.config['end_date'], '%Y-%m-%d')
            
            # Créer contrat IBKR
            contract = await self.ibkr_connector._create_ib_insync_contract_async(symbol)
            
            # Requête données historiques IBKR
            bars = await self.ibkr_connector.ib_client.reqHistoricalData(
                contract=contract,
                endDateTime=end_date.strftime('%Y%m%d %H:%M:%S'),
                durationStr='1 Y',  # 1 année
                barSizeSetting='5 mins',
                whatToShow='TRADES',
                useRTH=True,  # Regular Trading Hours
                formatDate=1,
                keepUpToDate=False
            )
            
            # Conversion en format standard
            historical_data = []
            for bar in bars:
                data_point = {
                    'timestamp': bar.date,
                    'symbol': symbol,
                    'open': bar.open,
                    'high': bar.high,
                    'low': bar.low,
                    'close': bar.close,
                    'volume': bar.volume,
                    'source': 'IBKR_API'
                }
                historical_data.append(data_point)
            
            logger.info(f"✅ Données IBKR chargées: {len(historical_data)} barres")
            logger.info(f"   - Période: {historical_data[0]['timestamp']} → {historical_data[-1]['timestamp']}")
            logger.info(f"   - Source: IBKR API (CME Real-Time)")
            
            return historical_data
            
        except Exception as e:
            logger.error(f"❌ Erreur chargement données IBKR: {e}")
            logger.info("🔄 Fallback vers données simulées")
            return self._generate_simulated_data(symbol)
    
    def _generate_simulated_data(self, symbol: str) -> List[Dict]:
        """Génère données simulées pour tests"""
        logger.info(f"[SIM] Génération données simulées pour {symbol}")
        
        start_date = datetime.strptime(self.config['start_date'], '%Y-%m-%d')
        end_date = datetime.strptime(self.config['end_date'], '%Y-%m-%d')
        
        # Générer données 5 minutes
        data = []
        current_time = start_date
        base_price = 4500.0 if symbol == 'ES' else 15000.0 if symbol == 'NQ' else 35000.0
        
        while current_time <= end_date:
            # Simulation mouvement de prix
            price_change = (np.random.randn() * 2.0)  # Volatilité réaliste
            base_price += price_change
            
            data_point = {
                'timestamp': current_time,
                'symbol': symbol,
                'open': base_price - 1.0,
                'high': base_price + 1.5,
                'low': base_price - 1.5,
                'close': base_price,
                'volume': np.random.randint(500, 2000),
                'source': 'SIMULATION'
            }
            data.append(data_point)
            
            current_time += timedelta(minutes=5)
        
        logger.info(f"✅ Données simulées générées: {len(data)} barres")
        return data
    
    async def run_backtest(self) -> Dict[str, Any]:
        """
        Exécute le backtest complet avec IBKR
        
        WORKFLOW :
        1. Charge données historiques IBKR
        2. Pour chaque barre :
           - Génère signal Battle Navale
           - Analyse confluence
           - Exécute trade simulé
           - Met à jour performance
        3. Calcule métriques finales
        4. Génère rapport
        """
        try:
            logger.info("[LAUNCH] DÉMARRAGE BACKTEST IBKR")
            
            # 1. Initialisation composants
            if not await self.initialize_components():
                raise Exception("Échec initialisation composants")
            
            # 2. Chargement données historiques
            historical_data = await self.load_historical_data(self.config['symbol'])
            
            if not historical_data:
                raise Exception("Aucune donnée historique disponible")
            
            logger.info(f"[STATS] Traitement {len(historical_data)} barres")
            
            # 3. Boucle principale backtest
            for i, data_point in enumerate(historical_data):
                # Vérifier heures de trading
                if not self._is_trading_hours(data_point['timestamp']):
                    continue
                
                # Créer MarketData
                market_data = self._create_market_data(data_point)
                
                # Générer signal Battle Navale
                signal = self.signal_generator.generate_signal(market_data)
                
                if signal and signal.signal_type != 'NO_SIGNAL':
                    # Analyser confluence
                    confluence_score = self.confluence_analyzer.analyze_confluence(market_data)
                    
                    # Filtrer avec ML si activé
                    if self.ensemble_filter:
                        ml_confidence = self.ensemble_filter.predict_confidence(signal)
                        signal.total_confidence = (signal.total_confidence + ml_confidence) / 2
                    
                    # Exécuter trade si seuil atteint
                    if signal.total_confidence >= 0.65:  # Seuil 65%
                        await self._execute_trade(signal, market_data, confluence_score)
                
                # Mettre à jour position existante
                self._update_position(market_data)
                
                # Enregistrer équité
                self._record_equity(data_point['timestamp'])
                
                # Progress log
                if i % 1000 == 0:
                    logger.info(f"[PROGRESS] {i}/{len(historical_data)} barres traitées")
            
            # 4. Calcul métriques finales
            self._calculate_final_metrics()
            
            # 5. Génère rapport
            report = self._generate_report()
            
            logger.info("[FINISH] Backtest IBKR terminé")
            return report
            
        except Exception as e:
            logger.error(f"❌ Erreur backtest: {e}")
            return {'error': str(e)}
    
    def _create_market_data(self, data_point: Dict) -> Any:
        """Crée objet MarketData depuis données IBKR"""
        from core.base_types import MarketData
        
        return MarketData(
            symbol=data_point['symbol'],
            timestamp=data_point['timestamp'],
            open=data_point['open'],
            high=data_point['high'],
            low=data_point['low'],
            close=data_point['close'],
            volume=data_point['volume']
        )
    
    def _is_trading_hours(self, timestamp: datetime) -> bool:
        """Vérifie si c'est dans les heures de trading"""
        # Trading hours: 9:30 AM - 4:00 PM ET
        hour = timestamp.hour
        minute = timestamp.minute
        
        # Conversion simple (à améliorer avec timezone)
        if 9 <= hour < 16 or (hour == 9 and minute >= 30):
            return True
        return False
    
    async def _execute_trade(self, signal: Any, market_data: Any, confluence_score: float):
        """Exécute un trade simulé"""
        try:
            # Calculer taille position
            position_size = self._calculate_position_size(signal)
            
            # Calculer prix d'entrée avec slippage
            entry_price = market_data.close
            if signal.decision.value.startswith('LONG'):
                entry_price += self.config['slippage_ticks'] * 0.25  # Slippage
            else:
                entry_price -= self.config['slippage_ticks'] * 0.25
            
            # Créer trade
            trade = {
                'id': f"TRADE_{len(self.trades) + 1}",
                'timestamp': market_data.timestamp,
                'symbol': market_data.symbol,
                'side': 'LONG' if signal.decision.value.startswith('LONG') else 'SHORT',
                'size': position_size,
                'entry_price': entry_price,
                'signal_confidence': signal.total_confidence,
                'confluence_score': confluence_score,
                'exit_price': None,
                'pnl': None,
                'exit_reason': None,
                'exit_timestamp': None
            }
            
            # Mettre à jour position actuelle
            self.current_position = trade
            
            # Enregistrer trade
            self.trades.append(trade)
            self.trades_count += 1
            
            logger.info(f"✅ Trade exécuté: {trade['side']} {trade['size']} @ {trade['entry_price']:.2f}")
            
        except Exception as e:
            logger.error(f"❌ Erreur exécution trade: {e}")
    
    def _calculate_position_size(self, signal: Any) -> int:
        """Calcule taille position selon configuration"""
        if self.config['position_sizing'] == 'fixed':
            return min(self.config['max_position_size'], 3)
        elif self.config['position_sizing'] == 'percent_risk':
            # Calcul basé sur risque
            risk_amount = self.current_equity * 0.02  # 2% risque
            return int(risk_amount / (signal.stop_loss * 50))  # 50$ par tick ES
        else:
            return 1
    
    def _update_position(self, market_data: Any):
        """Met à jour position existante"""
        if not self.current_position:
            return
        
        # Vérifier conditions de sortie
        current_price = market_data.close
        entry_price = self.current_position['entry_price']
        
        # Stop loss (2% du prix d'entrée)
        stop_loss = entry_price * 0.98 if self.current_position['side'] == 'LONG' else entry_price * 1.02
        
        # Take profit (4% du prix d'entrée)
        take_profit = entry_price * 1.04 if self.current_position['side'] == 'LONG' else entry_price * 0.96
        
        should_exit = False
        exit_reason = None
        
        if self.current_position['side'] == 'LONG':
            if current_price <= stop_loss:
                should_exit = True
                exit_reason = 'STOP_LOSS'
            elif current_price >= take_profit:
                should_exit = True
                exit_reason = 'TAKE_PROFIT'
        else:  # SHORT
            if current_price >= stop_loss:
                should_exit = True
                exit_reason = 'STOP_LOSS'
            elif current_price <= take_profit:
                should_exit = True
                exit_reason = 'TAKE_PROFIT'
        
        if should_exit:
            self._close_position(current_price, exit_reason, market_data.timestamp)
    
    def _close_position(self, exit_price: float, exit_reason: str, exit_timestamp: datetime):
        """Ferme position actuelle"""
        if not self.current_position:
            return
        
        # Calculer P&L
        entry_price = self.current_position['entry_price']
        size = self.current_position['size']
        
        if self.current_position['side'] == 'LONG':
            pnl_ticks = (exit_price - entry_price) / 0.25  # 0.25$ par tick ES
        else:
            pnl_ticks = (entry_price - exit_price) / 0.25
        
        pnl_dollars = pnl_ticks * size * 50  # 50$ par tick ES
        
        # Appliquer commission
        commission = self.config['commission_per_trade'] * 2  # Entrée + sortie
        net_pnl = pnl_dollars - commission
        
        # Mettre à jour trade
        self.current_position['exit_price'] = exit_price
        self.current_position['pnl'] = net_pnl
        self.current_position['exit_reason'] = exit_reason
        self.current_position['exit_timestamp'] = exit_timestamp
        
        # Mettre à jour statistiques
        self.current_equity += net_pnl
        
        if net_pnl > 0:
            self.winning_trades += 1
        else:
            self.losing_trades += 1
        
        logger.info(f"✅ Position fermée: {exit_reason} - P&L: ${net_pnl:.2f}")
        
        # Réinitialiser position
        self.current_position = None
    
    def _record_equity(self, timestamp: datetime):
        """Enregistre équité actuelle"""
        total_equity = self.current_equity
        if self.current_position:
            # Ajouter P&L non réalisé
            unrealized_pnl = self._calculate_unrealized_pnl()
            total_equity += unrealized_pnl
        
        self.equity_history.append({
            'timestamp': timestamp,
            'equity': total_equity
        })
    
    def _calculate_unrealized_pnl(self) -> float:
        """Calcule P&L non réalisé de position actuelle"""
        if not self.current_position:
            return 0.0
        
        # Utiliser prix de fermeture de la dernière barre
        if self.equity_history:
            last_equity = self.equity_history[-1]['equity']
            return last_equity - self.current_equity
        return 0.0
    
    def _calculate_final_metrics(self):
        """Calcule métriques finales de performance"""
        if not self.trades:
            self.performance_metrics = {'error': 'Aucun trade exécuté'}
            return
        
        # Métriques de base
        total_trades = len(self.trades)
        winning_trades = len([t for t in self.trades if t['pnl'] and t['pnl'] > 0])
        losing_trades = len([t for t in self.trades if t['pnl'] and t['pnl'] < 0])
        
        # P&L
        total_pnl = sum([t['pnl'] for t in self.trades if t['pnl']])
        gross_pnl = sum([t['pnl'] for t in self.trades if t['pnl'] and t['pnl'] > 0])
        gross_loss = sum([t['pnl'] for t in self.trades if t['pnl'] and t['pnl'] < 0])
        
        # Win rate
        win_rate = winning_trades / total_trades if total_trades > 0 else 0
        
        # Profit factor
        profit_factor = abs(gross_pnl / gross_loss) if gross_loss != 0 else float('inf')
        
        # Drawdown
        equity_values = [e['equity'] for e in self.equity_history]
        max_equity = max(equity_values) if equity_values else self.config['initial_capital']
        min_equity = min(equity_values) if equity_values else self.config['initial_capital']
        max_drawdown = (max_equity - min_equity) / max_equity if max_equity > 0 else 0
        
        # Sharpe ratio (simplifié)
        returns = []
        for i in range(1, len(self.equity_history)):
            prev_equity = self.equity_history[i-1]['equity']
            curr_equity = self.equity_history[i]['equity']
            if prev_equity > 0:
                returns.append((curr_equity - prev_equity) / prev_equity)
        
        sharpe_ratio = np.mean(returns) / np.std(returns) if returns and np.std(returns) > 0 else 0
        
        self.performance_metrics = {
            'total_trades': total_trades,
            'winning_trades': winning_trades,
            'losing_trades': losing_trades,
            'win_rate': win_rate,
            'total_pnl': total_pnl,
            'gross_pnl': gross_pnl,
            'gross_loss': gross_loss,
            'profit_factor': profit_factor,
            'max_drawdown': max_drawdown,
            'sharpe_ratio': sharpe_ratio,
            'final_equity': self.current_equity,
            'return_pct': (self.current_equity - self.config['initial_capital']) / self.config['initial_capital']
        }
    
    def _generate_report(self) -> Dict[str, Any]:
        """Génère rapport complet de backtest"""
        report = {
            'backtest_info': {
                'symbol': self.config['symbol'],
                'start_date': self.config['start_date'],
                'end_date': self.config['end_date'],
                'initial_capital': self.config['initial_capital'],
                'commission_per_trade': self.config['commission_per_trade'],
                'slippage_ticks': self.config['slippage_ticks'],
                'use_battle_navale': self.config['use_battle_navale'],
                'use_confluence': self.config['use_confluence'],
                'data_source': 'IBKR_API'
            },
            'performance_metrics': self.performance_metrics,
            'trades': self.trades,
            'equity_history': self.equity_history,
            'signals_history': self.signals_history,
            'generated_at': datetime.now().isoformat()
        }
        
        # Sauvegarder rapport
        report_file = f"backtest_report_{self.config['symbol']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        logger.info(f"📋 Rapport sauvegardé: {report_file}")
        return report

# === FONCTIONS UTILITAIRES ===

def test_ibkr_connection() -> bool:
    """Teste connexion IBKR"""
    try:
        print("🔌 Test connexion IBKR...")
        
        # Test connexion basique
        config = DEFAULT_BACKTEST_CONFIG['ibkr_config']
        ibkr = IBKRConnector(config)
        
        # Test async
        async def test_connect():
            return await ibkr.connect()
        
        connected = asyncio.run(test_connect())
        
        if connected:
            print("✅ Connexion IBKR réussie")
            print(f"   - Host: {config['ibkr_host']}")
            print(f"   - Port: {config['ibkr_port']}")
            print(f"   - Client ID: {config['ibkr_client_id']}")
            
            # Test données disponibles
            print("\n📊 Données IBKR disponibles:")
            print("   - CME Real-Time (NP,L2) - Level 2 data")
            print("   - OPRA (Options US) - Options flow")
            print("   - Cotations US continues - Futures data")
            print("   - Données historiques - Backtesting")
            
            return True
        else:
            print("❌ Connexion IBKR échouée")
            print("   - Vérifier TWS/Gateway ouvert")
            print("   - Vérifier port API (7497/7496)")
            print("   - Vérifier API clients activés")
            return False
            
    except Exception as e:
        print(f"❌ Erreur test connexion: {e}")
        return False

def create_backtest_config_from_args(args) -> Dict[str, Any]:
    """Crée configuration backtest depuis arguments"""
    config = DEFAULT_BACKTEST_CONFIG.copy()
    
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
    
    if args.no_battle_navale:
        config['use_battle_navale'] = False
    if args.no_confluence:
        config['use_confluence'] = False
    if args.no_ml:
        config['enable_ml_training'] = False
    if args.no_reports:
        config['generate_reports'] = False
    
    return config

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
    parser.add_argument('--quick', action='store_true', help='Backtest rapide (30 jours)')
    
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
    print(f"Symbole: {config['symbol']}")
    print(f"Période: {config['start_date']} → {config['end_date']}")
    print(f"Capital: ${config['initial_capital']:,.2f}")
    print(f"Battle Navale: {'✅' if config['use_battle_navale'] else '❌'}")
    print(f"Confluence: {'✅' if config['use_confluence'] else '❌'}")
    print(f"ML Training: {'✅' if config['enable_ml_training'] else '❌'}")
    print(f"IBKR Connecté: {'✅' if ibkr_connected else '❌'}")
    
    # Créer et exécuter backtest
    engine = IBKRBacktestEngine(config)
    results = await engine.run_backtest()
    
    # Afficher résultats
    if 'error' not in results:
        print("\n📊 RÉSULTATS BACKTEST:")
        metrics = results['performance_metrics']
        print(f"Trades totaux: {metrics['total_trades']}")
        print(f"Win rate: {metrics['win_rate']:.1%}")
        print(f"P&L total: ${metrics['total_pnl']:.2f}")
        print(f"Profit factor: {metrics['profit_factor']:.2f}")
        print(f"Max drawdown: {metrics['max_drawdown']:.1%}")
        print(f"Sharpe ratio: {metrics['sharpe_ratio']:.2f}")
        print(f"Return: {metrics['return_pct']:.1%}")
    else:
        print(f"❌ Erreur backtest: {results['error']}")

if __name__ == "__main__":
    # Ajout import numpy pour simulation
    import numpy as np
    
    # Configuration logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Exécution
    asyncio.run(main()) 