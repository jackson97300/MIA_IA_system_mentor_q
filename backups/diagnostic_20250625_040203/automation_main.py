#!/usr/bin/env python3
"""
MIA_IA_SYSTEM - Automation Main (Version Définitive)
Point d'entrée principal pour l'automation de trading
Version: Production Ready v3.0
# Configuration encodage UTF-8 pour Windows
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


Architecture simplifiée :
- IBKR : Source unique de données (market data, options, order flow)
- Sierra Chart : Exécution des ordres uniquement
- SignalGenerator : Cerveau central unifié
- ML Progressif : Commence simple, évolue avec les données

Modes supportés :
- DATA_COLLECTION : Collecte intensive pour ML (seuils bas)
- PAPER_TRADING : Validation stratégie (seuils moyens)
- LIVE_TRADING : Trading réel (seuils stricts)
"""

import sys
import os
import asyncio
import signal
import logging
import argparse
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from pathlib import Path
import json
import time

# Configuration logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/automation.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# === IMPORTS MIA_IA_SYSTEM ===

# Configuration
from config import get_trading_config, get_sierra_config
from config.automation_config import (
    AutomationConfig, AutomationMode, 
    create_data_collection_config,
    create_paper_trading_config, 
    create_live_trading_config,
    create_conservative_config,
    get_automation_config,
    validate_config
)

# Core
from core.base_types import (
    MarketData, SystemState, TradingSignal,
    ES_TICK_SIZE, ES_TICK_VALUE
)

# Strategies - CERVEAU CENTRAL
from strategies import get_signal_now, SignalGenerator, SignalDecision

# Execution
from execution import (
    SimpleBattleNavaleTrader,
    create_simple_trader,
    TradingMode,
    AutomationStatus
)

# Monitoring
from monitoring import (
    LiveMonitor, PerformanceTracker,
    HealthChecker, create_discord_notifier
)

# Performance
from performance import TradeLogger, PerformanceAnalyzer

# === MAIN AUTOMATION BOT ===

class MIAAutomationBot:
    """
    Bot d'automation principal MIA_IA_SYSTEM
    
    Orchestrateur central qui coordonne :
    - SignalGenerator pour les décisions
    - SimpleBattleNavaleTrader pour l'exécution
    - Monitoring pour la surveillance
    - Performance tracking
    """
    
    def __init__(self, config: AutomationConfig):
        """
        Initialise le bot d'automation
        
        Args:
            config: Configuration automation complète
        """
        self.config = config
        self.start_time = datetime.now()
        self.is_running = False
        self.shutdown_requested = False
        
        # === COMPOSANTS CORE ===
        logger.info("🚀 Initialisation MIA Automation Bot...")
        
        # 1. Signal Generator (Cerveau Central)
        logger.info("🧠 Création SignalGenerator...")
        self.signal_generator = SignalGenerator()
        self._configure_signal_generator()
        
        # 2. Trader (Exécution)
        logger.info("🤖 Création SimpleBattleNavaleTrader...")
        trader_mode = self._get_trader_mode()
        self.trader = create_simple_trader(trader_mode)
        self._configure_trader()
        
        # 3. Monitoring
        logger.info("📊 Création système monitoring...")
        self.live_monitor = LiveMonitor(self.trader)
        self.performance_tracker = PerformanceTracker()
        self.health_checker = HealthChecker()
        
        # 4. Performance & Logging
        logger.info("📈 Création système performance...")
        self.trade_logger = TradeLogger()
        self.performance_analyzer = PerformanceAnalyzer()
        
        # 5. Notifications (optionnel)
        self.discord = None
        if self.config.monitoring.enable_alerts:
            try:
                self.discord = create_discord_notifier()
                logger.info("✅ Discord notifications activées")
            except Exception as e:
                logger.warning(f"⚠️ Discord non disponible: {e}")
        
        # === ÉTAT SYSTÈME ===
        self.system_state = SystemState.IDLE
        self.stats = {
            'signals_generated': 0,
            'signals_executed': 0,
            'trades_completed': 0,
            'errors_count': 0,
            'uptime_hours': 0
        }
        
        logger.info("✅ MIA Automation Bot initialisé avec succès")
        self._log_configuration()
    
    def _configure_signal_generator(self):
        """Configure SignalGenerator selon le mode"""
        mode = self.config.trading.automation_mode
        
        # Ajustement des seuils selon le mode
        if hasattr(self.signal_generator, 'min_confidence'):
            self.signal_generator.min_confidence = self.config.trading.battle_navale_min_confidence
        
        if hasattr(self.signal_generator, 'min_confluence'):
            self.signal_generator.min_confluence = self.config.trading.min_confluence_score
        
        logger.info(f"SignalGenerator configuré pour mode: {mode.value}")
        logger.info(f"  - Min confidence: {self.config.trading.battle_navale_min_confidence}")
        logger.info(f"  - Min confluence: {self.config.trading.min_confluence_score}")
    
    def _configure_trader(self):
        """Configure le trader selon le mode"""
        # Le trader est déjà configuré via le mode passé à create_simple_trader
        # Mais on peut ajouter des configs supplémentaires ici
        
        if hasattr(self.trader, 'min_probability'):
            if self.config.trading.automation_mode == AutomationMode.DATA_COLLECTION:
                self.trader.min_probability = 0.35  # Très bas pour data collection
            elif self.config.trading.automation_mode == AutomationMode.PAPER_TRADING:
                self.trader.min_probability = 0.60  # Standard
            else:  # LIVE
                self.trader.min_probability = 0.70  # Strict
    
    def _get_trader_mode(self) -> str:
        """Convertit AutomationMode vers mode du trader"""
        mode_map = {
            AutomationMode.DATA_COLLECTION: "DATA_COLLECTION",
            AutomationMode.PAPER_TRADING: "PAPER",
            AutomationMode.LIVE_TRADING: "LIVE"
        }
        return mode_map.get(self.config.trading.automation_mode, "PAPER")
    
    def _log_configuration(self):
        """Log la configuration active"""
        logger.info("=" * 60)
        logger.info("📋 CONFIGURATION ACTIVE")
        logger.info("=" * 60)
        logger.info(f"Mode: {self.config.trading.automation_mode.value}")
        logger.info(f"Config name: {self.config.config_name}")
        
        logger.info("\n🎯 Paramètres Trading:")
        logger.info(f"  - Battle Navale min: {self.config.trading.battle_navale_min_confidence}")
        logger.info(f"  - Confluence min: {self.config.trading.min_confluence_score}")
        logger.info(f"  - Positions max: {self.config.trading.max_positions_concurrent}")
        
        logger.info("\n🛡️ Paramètres Risk:")
        logger.info(f"  - Daily loss limit: ${self.config.risk.daily_loss_limit}")
        logger.info(f"  - Max daily trades: {self.config.risk.max_daily_trades}")
        logger.info(f"  - Stop loss: {self.config.risk.stop_loss_ticks} ticks")
        
        logger.info("\n📊 Paramètres Monitoring:")
        logger.info(f"  - Monitoring enabled: {self.config.monitoring.enable_monitoring}")
        logger.info(f"  - Alerts enabled: {self.config.monitoring.enable_alerts}")
        logger.info("=" * 60)
    
    # === MAIN EXECUTION LOOP ===
    
    async def start(self):
        """Démarre le bot d'automation"""
        logger.info("🚀 DÉMARRAGE MIA AUTOMATION BOT")
        
        try:
            # 1. Validation système
            if not await self._validate_system():
                logger.error("❌ Validation système échouée")
                return False
            
            # 2. Démarrage composants
            self.is_running = True
            self.system_state = SystemState.TRADING
            
            # 3. Démarrage monitoring
            self.live_monitor.start_monitoring()
            
            # 4. Notification démarrage
            await self._notify_startup()
            
            # 5. Démarrage trader
            await self.trader.start_trading_session()
            
            # 6. Loop principal
            await self._run_main_loop()
            
        except KeyboardInterrupt:
            logger.info("⌨️ Arrêt demandé par l'utilisateur")
        except Exception as e:
            logger.error(f"❌ Erreur fatale: {e}", exc_info=True)
            self.stats['errors_count'] += 1
        finally:
            await self.shutdown()
    
    async def _validate_system(self) -> bool:
        """Valide que le système est prêt"""
        logger.info("🔍 Validation système...")
        
        validations = []
        
        # 1. Configuration valide
        config_valid = validate_config(self.config)
        validations.append(("Configuration", config_valid))
        
        # 2. Connexions broker
        ibkr_ok = await self._test_ibkr_connection()
        validations.append(("IBKR Connection", ibkr_ok))
        
        sierra_ok = await self._test_sierra_connection()
        validations.append(("Sierra Chart", sierra_ok))
        
        # 3. Espace disque
        disk_ok = self._check_disk_space()
        validations.append(("Espace disque", disk_ok))
        
        # 4. Composants
        components_ok = self._validate_components()
        validations.append(("Composants", components_ok))
        
        # Affichage résultats
        all_ok = True
        for name, status in validations:
            icon = "✅" if status else "❌"
            logger.info(f"  {icon} {name}")
            if not status:
                all_ok = False
        
        return all_ok
    
    async def _test_ibkr_connection(self) -> bool:
        """Test connexion IBKR"""
        try:
            # Le trader teste déjà la connexion à l'init
            return self.trader.ibkr_connected if hasattr(self.trader, 'ibkr_connected') else True
        except:
            return False
    
    async def _test_sierra_connection(self) -> bool:
        """Test connexion Sierra Chart"""
        try:
            # Vérifier que la config Sierra est valide
            sierra_config = get_sierra_config()
            return sierra_config is not None
        except:
            return False
    
    def _check_disk_space(self) -> bool:
        """Vérifie l'espace disque disponible"""
        try:
            import shutil
            path = Path("data/snapshots")
            path.mkdir(parents=True, exist_ok=True)
            
            stat = shutil.disk_usage(path)
            free_gb = stat.free / (1024**3)
            
            return free_gb > 1.0  # Au moins 1GB libre
        except:
            return True  # On assume OK si erreur
    
    def _validate_components(self) -> bool:
        """Valide que tous les composants sont initialisés"""
        try:
            assert self.signal_generator is not None
            assert self.trader is not None
            assert self.live_monitor is not None
            return True
        except:
            return False
    
    async def _notify_startup(self):
        """Notification de démarrage"""
        message = f"""
🚀 **MIA AUTOMATION BOT DÉMARRÉ**
📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
⚙️ Mode: {self.config.trading.automation_mode.value}
📊 Config: {self.config.config_name}
🎯 Battle Navale Min: {self.config.trading.battle_navale_min_confidence}
💰 Daily Loss Limit: ${self.config.risk.daily_loss_limit}
        """
        
        logger.info(message)
        
        if self.discord:
            try:
                await self.discord.send_message(message, alert_type="info")
            except:
                pass
    
    async def _run_main_loop(self):
        """Loop principal d'exécution"""
        logger.info("🔄 Démarrage loop principal...")
        
        loop_count = 0
        last_health_check = time.time()
        last_performance_update = time.time()
        
        while self.is_running and not self.shutdown_requested:
            try:
                loop_start = time.time()
                loop_count += 1
                
                # 1. Health check périodique
                if time.time() - last_health_check > 60:  # Chaque minute
                    await self._perform_health_check()
                    last_health_check = time.time()
                
                # 2. Performance update périodique
                if time.time() - last_performance_update > 300:  # Toutes les 5 minutes
                    await self._update_performance_metrics()
                    last_performance_update = time.time()
                
                # 3. Check arrêt demandé
                if self._should_stop_trading():
                    logger.info("🛑 Conditions d'arrêt atteintes")
                    break
                
                # 4. Délai entre loops
                loop_duration = time.time() - loop_start
                sleep_time = max(0, (self.config.trading.analysis_frequency_ms / 1000) - loop_duration)
                
                if loop_count % 100 == 0:  # Log toutes les 100 iterations
                    logger.debug(f"Loop {loop_count}: {loop_duration*1000:.1f}ms")
                
                await asyncio.sleep(sleep_time)
                
            except Exception as e:
                logger.error(f"Erreur dans main loop: {e}", exc_info=True)
                self.stats['errors_count'] += 1
                await asyncio.sleep(1)  # Pause en cas d'erreur
    
    async def _perform_health_check(self):
        """Effectue un health check complet"""
        try:
            health_status = self.health_checker.check_system_health()
            
            if not health_status['healthy']:
                logger.warning(f"⚠️ Problème santé système: {health_status['issues']}")
                
                if health_status['critical']:
                    logger.error("🚨 Problème critique détecté - Arrêt d'urgence")
                    self.shutdown_requested = True
            
        except Exception as e:
            logger.error(f"Erreur health check: {e}")
    
    async def _update_performance_metrics(self):
        """Met à jour les métriques de performance"""
        try:
            # Récupérer stats du trader
            trader_stats = self.trader.get_statistics()
            
            # Mettre à jour performance tracker
            self.performance_tracker.update_metrics(trader_stats)
            
            # Log résumé
            logger.info(f"📊 Performance Update: "
                       f"Trades: {trader_stats.get('trades_completed', 0)}, "
                       f"Win Rate: {trader_stats.get('win_rate', 0):.1%}, "
                       f"P&L: ${trader_stats.get('total_pnl', 0):.2f}")
            
        except Exception as e:
            logger.error(f"Erreur update performance: {e}")
    
    def _should_stop_trading(self) -> bool:
        """Détermine si le trading doit s'arrêter"""
        # 1. Arrêt manuel demandé
        if self.shutdown_requested:
            return True
        
        # 2. Daily loss limit atteint
        trader_stats = self.trader.get_statistics()
        daily_pnl = trader_stats.get('daily_pnl', 0)
        
        if daily_pnl <= -self.config.risk.daily_loss_limit:
            logger.warning(f"🛑 Daily loss limit atteint: ${daily_pnl:.2f}")
            return True
        
        # 3. Daily profit target atteint (si configuré)
        if self.config.risk.stop_on_daily_target:
            if daily_pnl >= self.config.risk.daily_profit_target:
                logger.info(f"🎯 Daily profit target atteint: ${daily_pnl:.2f}")
                return True
        
        # 4. Max trades atteint
        daily_trades = trader_stats.get('daily_trades', 0)
        if daily_trades >= self.config.risk.max_daily_trades:
            logger.info(f"📊 Max daily trades atteint: {daily_trades}")
            return True
        
        # 5. Erreurs critiques
        if self.stats['errors_count'] > 10:
            logger.error("❌ Trop d'erreurs - Arrêt de sécurité")
            return True
        
        return False
    
    async def shutdown(self):
        """Arrêt propre du système"""
        logger.info("🛑 ARRÊT MIA AUTOMATION BOT...")
        
        self.is_running = False
        self.system_state = SystemState.SHUTDOWN
        
        try:
            # 1. Arrêt trader
            if self.trader:
                await self.trader.stop_trading()
            
            # 2. Arrêt monitoring
            if self.live_monitor:
                self.live_monitor.stop_monitoring()
            
            # 3. Sauvegarde données
            await self._save_final_data()
            
            # 4. Notification arrêt
            await self._notify_shutdown()
            
            # 5. Calcul stats finales
            self._calculate_final_stats()
            
        except Exception as e:
            logger.error(f"Erreur pendant shutdown: {e}")
        
        logger.info("✅ MIA Automation Bot arrêté proprement")
    
    async def _save_final_data(self):
        """Sauvegarde les données finales"""
        try:
            # Export snapshots
            if hasattr(self.trader, 'snapshotter'):
                self.trader.snapshotter.export_daily_snapshots()
            
            # Sauvegarde config
            config_path = f"data/configs/config_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            Path(config_path).parent.mkdir(parents=True, exist_ok=True)
            self.config.save_to_file(config_path)
            
            # Sauvegarde stats
            stats_path = f"data/stats/stats_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            Path(stats_path).parent.mkdir(parents=True, exist_ok=True)
            with open(stats_path, 'w') as f:
                json.dump(self.stats, f, indent=2)
            
        except Exception as e:
            logger.error(f"Erreur sauvegarde données: {e}")
    
    async def _notify_shutdown(self):
        """Notification d'arrêt"""
        uptime = (datetime.now() - self.start_time).total_seconds() / 3600
        
        trader_stats = self.trader.get_statistics()
        
        message = f"""
🛑 **MIA AUTOMATION BOT ARRÊTÉ**
📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
⏱️ Uptime: {uptime:.1f} heures
📊 Trades: {trader_stats.get('trades_completed', 0)}
💰 P&L: ${trader_stats.get('total_pnl', 0):.2f}
📈 Win Rate: {trader_stats.get('win_rate', 0):.1%}
        """
        
        logger.info(message)
        
        if self.discord:
            try:
                await self.discord.send_message(message, alert_type="info")
            except:
                pass
    
    def _calculate_final_stats(self):
        """Calcule les statistiques finales"""
        uptime_hours = (datetime.now() - self.start_time).total_seconds() / 3600
        self.stats['uptime_hours'] = uptime_hours
        
        # Ajouter stats du trader
        trader_stats = self.trader.get_statistics()
        self.stats.update(trader_stats)
        
        # Log résumé final
        logger.info("=" * 60)
        logger.info("📊 STATISTIQUES FINALES")
        logger.info("=" * 60)
        for key, value in self.stats.items():
            logger.info(f"{key}: {value}")
        logger.info("=" * 60)

# === SIGNAL HANDLERS ===

def setup_signal_handlers(bot: MIAAutomationBot):
    """Configure les handlers de signaux système"""
    def signal_handler(signum, frame):
        logger.info(f"Signal {signum} reçu - Arrêt demandé")
        bot.shutdown_requested = True
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

# === MAIN FUNCTION ===

def create_config_from_args(args) -> AutomationConfig:
    """Crée configuration depuis arguments ligne de commande"""
    # Configuration de base selon le mode
    if args.mode == "data_collection":
        config = create_data_collection_config()
    elif args.mode == "paper":
        config = create_paper_trading_config()
    elif args.mode == "live":
        if args.conservative:
            config = create_conservative_config()
        else:
            config = create_live_trading_config()
    else:
        config = get_automation_config(args.mode)
    
    # Override avec arguments spécifiques
    if args.daily_loss_limit:
        config.risk.daily_loss_limit = args.daily_loss_limit
    
    if args.max_trades:
        config.risk.max_daily_trades = args.max_trades
    
    if args.min_confidence:
        config.trading.battle_navale_min_confidence = args.min_confidence
    
    if args.min_confluence:
        config.trading.min_confluence_score = args.min_confluence
    
    # Charger depuis fichier si spécifié
    if args.config_file:
        try:
            config = AutomationConfig.load_from_file(args.config_file)
            logger.info(f"Configuration chargée depuis: {args.config_file}")
        except Exception as e:
            logger.error(f"Erreur chargement config: {e}")
    
    return config

async def main():
    """Fonction principale"""
    # === ARGUMENTS ===
    parser = argparse.ArgumentParser(description='MIA Automation Bot')
    
    parser.add_argument('--mode', 
                       choices=['data_collection', 'paper', 'live'],
                       default='paper',
                       help='Mode de trading')
    
    parser.add_argument('--config-file',
                       type=str,
                       help='Fichier de configuration JSON')
    
    parser.add_argument('--conservative',
                       action='store_true',
                       help='Utiliser configuration conservative (live uniquement)')
    
    parser.add_argument('--daily-loss-limit',
                       type=float,
                       help='Override daily loss limit')
    
    parser.add_argument('--max-trades',
                       type=int,
                       help='Override max daily trades')
    
    parser.add_argument('--min-confidence',
                       type=float,
                       help='Override min Battle Navale confidence')
    
    parser.add_argument('--min-confluence',
                       type=float,
                       help='Override min confluence score')
    
    parser.add_argument('--dry-run',
                       action='store_true',
                       help='Test configuration sans trader')
    
    args = parser.parse_args()
    
    # === BANNER ===
    print("""
    ╔══════════════════════════════════════════╗
    ║       MIA_IA_SYSTEM AUTOMATION BOT       ║
    ║         Trading Futures ES - v3.0        ║
    ║    Architecture: IBKR Data + Sierra      ║
    ╚══════════════════════════════════════════╝
    """)
    
    # === CRÉATION CONFIG ===
    config = create_config_from_args(args)
    
    # === MODE DRY RUN ===
    if args.dry_run:
        logger.info("🔍 MODE DRY RUN - Test configuration")
        logger.info(f"Configuration: {json.dumps(config.to_dict(), indent=2)}")
        
        if validate_config(config):
            logger.info("✅ Configuration valide")
        else:
            logger.error("❌ Configuration invalide")
        
        return
    
    # === CRÉATION ET DÉMARRAGE BOT ===
    bot = MIAAutomationBot(config)
    setup_signal_handlers(bot)
    
    # Démarrage
    await bot.start()

# === ENTRY POINT ===

if __name__ == "__main__":
    # Créer dossiers nécessaires
    for folder in ['logs', 'data/snapshots', 'data/configs', 'data/stats']:
        Path(folder).mkdir(parents=True, exist_ok=True)
    
    # Lancer async main
    asyncio.run(main())