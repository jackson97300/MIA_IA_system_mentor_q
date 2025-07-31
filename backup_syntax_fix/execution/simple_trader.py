#!/usr/bin/env python3
"""
MIA_IA_SYSTEM - Simple Battle Navale Trader
Automation Core avec mode collecte de données
Version: Production Ready v3.0
Performance: <10ms par loop, snapshots complets

Modes disponibles:
- DATA_COLLECTION: Prend tous les trades >55% pour collecter données
- PAPER: Trading normal avec limites standards
- LIVE: Trading réel avec paramètres stricts
"""

# === STDLIB ===
import time
import logging
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import asyncio
from pathlib import Path
import json

# === THIRD-PARTY ===
import pandas as pd
import numpy as np

# === CONFIG ===
from config import get_trading_config
from config.automation_config import get_automation_config
from config.data_collection_risk_config import (
    DATA_COLLECTION_RISK_PARAMS,
    PAPER_TRADING_RISK_PARAMS,
    LIVE_TRADING_RISK_PARAMS,
    get_risk_params_for_mode
)
from config.sierra_config import (
    get_sierra_config,
    create_paper_trading_config,
    create_live_trading_config,
    create_data_collection_config,
    SierraIBKRConfig
)

# === CORE ===
from core.base_types import (
    MarketData, 
    TradingSignal, 
    SignalType,
    MarketRegime,
    ES_TICK_SIZE,
    ES_TICK_VALUE
)

# === STRATEGIES (CERVEAU CENTRAL) ===
from strategies import get_signal_now, create_signal_generator
from strategies.signal_generator import SignalGenerator

# === FEATURES ===
from features.feature_calculator import create_feature_calculator

# === EXECUTION ===
from execution.order_manager import OrderManager
from execution.risk_manager import RiskManager, RiskAction
from execution.trade_snapshotter import create_trade_snapshotter

# === MONITORING ===
from monitoring import (
    DiscordNotifier, 
    create_discord_notifier,
    notify_discord_available
)

# Logger
logger = logging.getLogger(__name__)


class AutomationStatus(Enum):
    """Statuts de l'automation"""
    STOPPED = "STOPPED"
    STARTING = "STARTING"
    RUNNING = "RUNNING"
    PAUSED = "PAUSED"
    STOPPING = "STOPPING"
    ERROR = "ERROR"


class TradingMode(Enum):
    """Modes de trading"""
    DATA_COLLECTION = "DATA_COLLECTION"
    PAPER = "PAPER"
    LIVE = "LIVE"


@dataclass
class TradingSession:
    """Session de trading automatisé"""
    session_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    mode: TradingMode = TradingMode.PAPER
    trades_count: int = 0
    signals_detected: int = 0
    signals_taken: int = 0
    pnl: float = 0.0
    max_drawdown: float = 0.0
    status: AutomationStatus = AutomationStatus.STOPPED
    target_trades: int = 0  # Pour mode data collection


@dataclass
class Position:
    """Position de trading"""
    position_id: str
    symbol: str
    side: str  # LONG ou SHORT
    size: int
    entry_price: float
    entry_time: datetime
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    current_price: float = 0.0
    unrealized_pnl: float = 0.0
    max_profit: float = 0.0
    max_loss: float = 0.0
    bars_in_trade: int = 0


class SimpleBattleNavaleTrader:
    """
    Trader automatique utilisant votre méthode Battle Navale
    Avec mode spécial pour collecter 500-1000 trades
    """
    
    def __init__(self, mode: str = "PAPER"):
        """
        Initialisation du trader
        
        Args:
            mode: "DATA_COLLECTION", "PAPER" ou "LIVE"
        """
        logger.info(f"🚀 Initialisation SimpleBattleNavaleTrader mode={mode}")
        
        # Mode et configuration
        self.mode = TradingMode(mode.upper())
        self.config = get_automation_config()
        self.trading_config = get_trading_config()
        
        # === CERVEAU CENTRAL ===
        self.signal_generator = create_signal_generator()
        logger.info("✅ SignalGenerator (cerveau central) initialisé")
        
        # === RISK MANAGEMENT - CONFIGURATION DYNAMIQUE ===
        self.risk_manager = RiskManager()
        
        # 🎯 CONFIGURATION SELON LE MODE
        risk_params = get_risk_params_for_mode(mode.lower())
        self.risk_manager.params = risk_params
        
        # Log de la configuration appliquée
        logger.info(f"✅ RiskManager configuré pour mode {mode}")
        logger.info(f"   - Min probabilité: {risk_params.min_signal_probability:.1%}")
        logger.info(f"   - Min base quality: {risk_params.min_base_quality_for_trade:.1%}")
        logger.info(f"   - Min confluence: {risk_params.min_confluence_score:.1%}")
        logger.info(f"   - Daily loss limit: ${risk_params.daily_loss_limit:.0f}")
        logger.info(f"   - Max trades/jour: {risk_params.max_daily_trades}")
        logger.info(f"   - Mode collecte: {risk_params.data_collection_mode}")
        logger.info(f"   - Golden rule: {risk_params.golden_rule_strict}")
        
        # Stocker les seuils pour usage dans la boucle
        self.min_probability = risk_params.min_signal_probability
        
        # === SIERRA CHART + IBKR CONFIGURATION ===
        self.sierra_config = self._setup_sierra_ibkr_config(mode)
        logger.info(f"✅ Sierra/IBKR configuré: {self.sierra_config.environment}")
        logger.info(f"   - Data Provider: {self.sierra_config.data_provider.value}")
        logger.info(f"   - Order Provider: {self.sierra_config.order_provider.value}")
        logger.info(f"   - IBKR Port: {self.sierra_config.ibkr.port}")
        logger.info(f"   - Sierra Trading: {self.sierra_config.sierra_chart.trading_enabled}")
        logger.info(f"   - Primary Symbol: {self.sierra_config.contracts.primary_symbol}")
        logger.info(f"   - Enabled Symbols: {self.sierra_config.contracts.enabled_symbols}")
        
        # Validation configuration Sierra/IBKR
        if not self.sierra_config.validate():
            logger.error("❌ Configuration Sierra/IBKR invalide")
            raise ValueError("Configuration Sierra/IBKR invalide")
        
        # === EXECUTION ===
        self.order_manager = OrderManager()
        self.snapshotter = create_trade_snapshotter()
        
        # === MONITORING ===
        self.discord = None
        if notify_discord_available():
            try:
                self.discord = create_discord_notifier()
                self.discord_enabled = self.config.get('enable_discord', True)
                logger.info("✅ Discord notifications activées")
            except Exception as e:
                logger.warning(f"⚠️ Discord non disponible: {e}")
                self.discord_enabled = False
        else:
            self.discord_enabled = False
        
        # === STATE MANAGEMENT ===
        self.current_session: Optional[TradingSession] = None
        self.positions: Dict[str, Position] = {}  # Multiple positions possibles
        self.active_position: Optional[Position] = None
        
        # === STATISTICS ===
        self.daily_stats = self._init_daily_stats()
        self.session_stats = {
            'signals_total': 0,
            'signals_above_threshold': 0,
            'signals_executed': 0,
            'trades_completed': 0,
            'snapshots_captured': 0
        }
        
        # === CONTROL ===
        self.status = AutomationStatus.STOPPED
        self.is_trading = False
        self.should_stop = False
        
        # === PERFORMANCE ===
        self.last_market_data: Optional[MarketData] = None
        self.execution_times: List[float] = []
        self.trade_ids: List[str] = []
        
        # === DATA COLLECTION ===
        if self.mode == TradingMode.DATA_COLLECTION:
            self.target_trades = 500  # Objectif par défaut
            logger.info(f"🎯 MODE COLLECTE DONNÉES - Objectif: {self.target_trades} trades")
            logger.info(f"📊 Seuil probabilité: {self.min_probability:.1%}")
            logger.info(f"🔥 Paramètres optimisés pour MAXIMUM de trades!")
            
            # Log des paramètres clés pour collecte
            logger.info("📋 PARAMÈTRES MODE COLLECTE:")
            logger.info(f"   - Base quality min: {risk_params.min_base_quality_for_trade:.1%} (vs 60% normal)")
            logger.info(f"   - Confluence min: {risk_params.min_confluence_score:.1%} (vs 65% normal)")
            logger.info(f"   - Golden rule: {'DÉSACTIVÉE' if not risk_params.golden_rule_strict else 'ACTIVÉE'}")
            logger.info(f"   - Positions simultanées: {risk_params.max_positions_concurrent}")
            logger.info(f"   - Limites: SEULE daily loss ${risk_params.daily_loss_limit}")
        
        logger.info("✅ SimpleBattleNavaleTrader initialisé avec succès")
    
    def update_risk_mode(self, new_mode: str):
        """
        Met à jour le mode de risque en cours de session
        
        Args:
            new_mode: "DATA_COLLECTION", "PAPER" ou "LIVE"
        """
        logger.info(f"🔄 Changement mode risque: {self.mode.value} → {new_mode}")
        
        # Mettre à jour les paramètres de risque
        risk_params = get_risk_params_for_mode(new_mode.lower())
        self.risk_manager.params = risk_params
        self.min_probability = risk_params.min_signal_probability
        
        # Mettre à jour la configuration Sierra/IBKR
        old_sierra_config = self.sierra_config
        self.sierra_config = self._setup_sierra_ibkr_config(new_mode)
        
        # Mettre à jour le mode
        self.mode = TradingMode(new_mode.upper())
        
        # Log des nouveaux paramètres
        logger.info(f"✅ Nouveau mode appliqué: {new_mode}")
        logger.info(f"   - Min probabilité: {risk_params.min_signal_probability:.1%}")
        logger.info(f"   - Daily loss limit: ${risk_params.daily_loss_limit:.0f}")
        logger.info(f"   - Mode collecte: {risk_params.data_collection_mode}")
        logger.info(f"   - Sierra/IBKR: {self.sierra_config.environment}")
        logger.info(f"   - Data Provider: {self.sierra_config.data_provider.value}")
        logger.info(f"   - Order Provider: {self.sierra_config.order_provider.value}")
        
        # Validation nouvelle configuration
        if not self.sierra_config.validate():
            logger.error("❌ Nouvelle configuration Sierra/IBKR invalide")
            # Rollback
            self.sierra_config = old_sierra_config
            logger.warning("⚠️ Rollback vers ancienne configuration")
            return False
        
        # Notifier Discord si disponible
        if self.discord_enabled:
            asyncio.create_task(
                self.discord.send_custom_message(
                    'system',
                    f"🔄 Mode Changé: {new_mode}",
                    f"Nouveaux seuils appliqués\n"
                    f"Probabilité min: {risk_params.min_signal_probability:.1%}\n"
                    f"Daily limit: ${risk_params.daily_loss_limit:.0f}\n"
                    f"Data: {self.sierra_config.data_provider.value}\n"
                    f"Orders: {self.sierra_config.order_provider.value}"
                )
            )
        
        return True
    
    def log_risk_diagnostics(self):
        """Log diagnostics des paramètres de risque actuels"""
        params = self.risk_manager.params
        
        logger.info("=" * 60)
        logger.info(f"📊 DIAGNOSTICS RISK MANAGER - MODE: {self.mode.value}")
        logger.info("-" * 60)
        logger.info(f"Signal Probability Min:    {params.min_signal_probability:.1%}")
        logger.info(f"Base Quality Min:          {params.min_base_quality_for_trade:.1%}")
        logger.info(f"Confluence Min:            {params.min_confluence_score:.1%}")
        logger.info(f"Golden Rule Strict:        {params.golden_rule_strict}")
        logger.info(f"Data Collection Mode:      {params.data_collection_mode}")
        logger.info("-" * 60)
        logger.info(f"Daily Loss Limit:          ${params.daily_loss_limit:.0f}")
        logger.info(f"Daily Profit Target:       ${params.daily_profit_target:.0f}")
        logger.info(f"Max Daily Trades:          {params.max_daily_trades}")
        logger.info(f"Max Risk Per Trade:        ${params.max_risk_per_trade_dollars:.0f}")
        logger.info(f"Max Position Size:         {params.max_position_size}")
        logger.info(f"Max Concurrent Positions:  {params.max_positions_concurrent}")
        logger.info("-" * 60)
        logger.info(f"P&L Actuel:               ${self.daily_stats['gross_pnl']:.2f}")
        logger.info(f"Trades Aujourd'hui:        {self.daily_stats['trades_count']}")
        logger.info(f"Win Rate:                  {self.daily_stats['winning_trades'] / max(self.daily_stats['trades_count'], 1):.1%}")
        logger.info("-" * 60)
        logger.info(f"📡 SIERRA CHART + IBKR CONFIG")
        logger.info(f"Environment:               {self.sierra_config.environment}")
        logger.info(f"Data Provider:             {self.sierra_config.data_provider.value}")
        logger.info(f"Order Provider:            {self.sierra_config.order_provider.value}")
        logger.info(f"IBKR Host:Port:            {self.sierra_config.ibkr.host}:{self.sierra_config.ibkr.port}")
        logger.info(f"IBKR Client ID:            {self.sierra_config.ibkr.client_id}")
        logger.info(f"Sierra Address:Port:       {self.sierra_config.sierra_chart.server_address}:{self.sierra_config.sierra_chart.server_port}")
        logger.info(f"Sierra Trading Enabled:    {self.sierra_config.sierra_chart.trading_enabled}")
        logger.info(f"Primary Symbol:            {self.sierra_config.contracts.primary_symbol}")
        logger.info(f"Enabled Symbols:           {self.sierra_config.contracts.enabled_symbols}")
        logger.info(f"Max Order Size:            {self.sierra_config.sierra_chart.max_order_size}")
        logger.info(f"Kill Switch Threshold:     ${self.sierra_config.security.kill_switch_loss_threshold:.0f}")
        logger.info("=" * 60)
    
    def _setup_sierra_ibkr_config(self, mode: str) -> SierraIBKRConfig:
        """Configure Sierra Chart + IBKR selon le mode"""
        mode_upper = mode.upper()
        
        if mode_upper == "LIVE":
            # Configuration live trading
            config = create_live_trading_config()
            
            # Personnalisation live
            config.ibkr.client_id = 1  # Client ID live
            config.sierra_chart.daily_loss_limit = self.risk_manager.params.daily_loss_limit
            config.security.kill_switch_loss_threshold = self.risk_manager.params.daily_loss_limit * 0.8
            config.security.max_gross_position = self.risk_manager.params.max_positions_concurrent * 2
            
            # Symboles selon risk params
            if self.risk_manager.params.max_position_size <= 2:
                config.contracts.primary_symbol = "MES"  # Micro si petites positions
                config.contracts.enabled_symbols = ["MES"]
            else:
                config.contracts.primary_symbol = "ES"
                config.contracts.enabled_symbols = ["ES", "MES"]
            
        elif mode_upper == "DATA_COLLECTION":
            # Configuration collecte données
            config = create_data_collection_config()
            
            # Optimisation pour collecte
            config.ibkr.client_id = 3  # ID séparé pour data collection
            config.ibkr.enable_tick_data = True
            config.ibkr.log_market_data = True
            config.ibkr.max_requests_per_second = 100
            
            # Tous les symboles pour ML
            config.contracts.enabled_symbols = ["ES", "MES", "NQ", "MNQ"]
            config.ibkr.auto_subscribe_symbols = ["ES", "MES", "NQ", "MNQ"]
            
            # Pas de trading réel
            config.sierra_chart.trading_enabled = False
            
        else:
            # Configuration paper trading (par défaut)
            config = create_paper_trading_config()
            
            # Personnalisation paper
            config.ibkr.client_id = 2  # Client ID paper
            config.sierra_chart.daily_loss_limit = self.risk_manager.params.daily_loss_limit
            config.security.kill_switch_loss_threshold = self.risk_manager.params.daily_loss_limit * 0.9
            
            # Micro contrats pour paper trading
            config.contracts.primary_symbol = "MES"
            config.contracts.enabled_symbols = ["MES"]
        
        # Application globale
        set_sierra_config(config)
        
        logger.info(f"🔧 Configuration Sierra/IBKR pour mode {mode_upper}:")
        logger.info(f"   - Environment: {config.environment}")
        logger.info(f"   - Data via: {config.data_provider.value}")
        logger.info(f"   - Orders via: {config.order_provider.value}")
        logger.info(f"   - IBKR Client ID: {config.ibkr.client_id}")
        logger.info(f"   - Sierra Port: {config.sierra_chart.server_port}")
        
        return config
    
    def log_sierra_ibkr_diagnostics(self):
        """Log diagnostics Sierra Chart + IBKR"""
        config = self.sierra_config
        
        logger.info("=" * 60)
        logger.info("🔧 DIAGNOSTICS SIERRA CHART + IBKR")
        logger.info("=" * 60)
        
        # Configuration générale
        logger.info(f"📊 CONFIGURATION GÉNÉRALE")
        logger.info(f"Environment:               {config.environment}")
        logger.info(f"Data Provider:             {config.data_provider.value}")
        logger.info(f"Order Provider:            {config.order_provider.value}")
        logger.info(f"Config Valid:              {'✅' if config.validate() else '❌'}")
        
        # IBKR Configuration
        logger.info(f"\n📡 IBKR CONFIGURATION")
        logger.info(f"Host:                      {config.ibkr.host}")
        logger.info(f"Port:                      {config.ibkr.port} ({'Live' if config.ibkr.port == 7496 else 'Paper' if config.ibkr.port == 7497 else 'Custom'})")
        logger.info(f"Client ID:                 {config.ibkr.client_id}")
        logger.info(f"Market Data Type:          {config.ibkr.market_data_type} ({'Live' if config.ibkr.market_data_type == 1 else 'Delayed' if config.ibkr.market_data_type == 3 else 'Other'})")
        logger.info(f"Auto Connect:              {'✅' if config.ibkr.auto_connect else '❌'}")
        logger.info(f"Tick Data Enabled:         {'✅' if config.ibkr.enable_tick_data else '❌'}")
        logger.info(f"Historical Data:           {'✅' if config.ibkr.enable_historical_data else '❌'}")
        logger.info(f"Auto Subscribe Symbols:    {config.ibkr.auto_subscribe_symbols}")
        
        # Sierra Chart Configuration
        logger.info(f"\n🏔️ SIERRA CHART CONFIGURATION")
        logger.info(f"Server Address:            {config.sierra_chart.server_address}")
        logger.info(f"Server Port:               {config.sierra_chart.server_port}")
        logger.info(f"Trading Enabled:           {'✅' if config.sierra_chart.trading_enabled else '❌'}")
        logger.info(f"Auto Connect:              {'✅' if config.sierra_chart.auto_connect else '❌'}")
        logger.info(f"Max Order Size:            {config.sierra_chart.max_order_size}")
        logger.info(f"Daily Loss Limit:          ${config.sierra_chart.daily_loss_limit:.0f}")
        logger.info(f"Order Validation:          {'✅' if config.sierra_chart.enable_order_validation else '❌'}")
        logger.info(f"Position Tracking:         {'✅' if config.sierra_chart.enable_position_tracking else '❌'}")
        
        # Contrats Configuration
        logger.info(f"\n📈 CONTRATS CONFIGURATION")
        logger.info(f"Primary Symbol:            {config.contracts.primary_symbol}")
        logger.info(f"Enabled Symbols:           {config.contracts.enabled_symbols}")
        logger.info(f"Auto Rollover:             {'✅' if config.contracts.enable_auto_rollover else '❌'}")
        
        # Afficher specs du contrat principal
        primary_spec = config.contracts.get_contract_spec(config.contracts.primary_symbol)
        if primary_spec:
            logger.info(f"Primary Symbol Specs:")
            logger.info(f"  - Multiplier:            {primary_spec['multiplier']}")
            logger.info(f"  - Tick Size:             {primary_spec['tick_size']}")
            logger.info(f"  - Tick Value:            ${primary_spec['tick_value']}")
            logger.info(f"  - Margin Requirement:    ${primary_spec['margin_requirement']:,}")
        
        # Sécurité Configuration
        logger.info(f"\n🛡️ SÉCURITÉ CONFIGURATION")
        logger.info(f"Order Validation:          {'✅' if config.security.enable_order_validation else '❌'}")
        logger.info(f"Max Order Value:           ${config.security.max_order_value:,.0f}")
        logger.info(f"Max Gross Position:        {config.security.max_gross_position}")
        logger.info(f"Max Net Position:          {config.security.max_net_position}")
        logger.info(f"Kill Switch Enabled:       {'✅' if config.security.enable_kill_switch else '❌'}")
        logger.info(f"Kill Switch Threshold:     ${config.security.kill_switch_loss_threshold:.0f}")
        logger.info(f"Fat Finger Protection:     {'✅' if config.security.enable_fat_finger_protection else '❌'}")
        logger.info(f"Real-time Monitoring:      {'✅' if config.security.enable_real_time_monitoring else '❌'}")
        
        # Synchronisation Configuration
        logger.info(f"\n🔄 SYNCHRONISATION CONFIGURATION")
        logger.info(f"Position Sync:             {'✅' if config.synchronization.enable_position_sync else '❌'}")
        logger.info(f"Order Sync:                {'✅' if config.synchronization.enable_order_sync else '❌'}")
        logger.info(f"Reconciliation:            {'✅' if config.synchronization.enable_reconciliation else '❌'}")
        logger.info(f"Sync Interval:             {config.synchronization.sync_interval_seconds}s")
        logger.info(f"Sierra Chart Priority:     {'✅' if config.synchronization.sierra_chart_priority else '❌'}")
        logger.info(f"IBKR Data Priority:        {'✅' if config.synchronization.ibkr_data_priority else '❌'}")
        logger.info(f"Failover Enabled:          {'✅' if config.synchronization.enable_failover else '❌'}")
        
        # Status recommandations
        logger.info(f"\n💡 RECOMMANDATIONS")
        if config.environment == "LIVE":
            logger.info("🔥 MODE LIVE - Vérifications:")
            if config.ibkr.port != 7496:
                logger.warning("   ⚠️ Port IBKR non standard pour LIVE (7496)")
            if config.ibkr.market_data_type != 1:
                logger.warning("   ⚠️ Market data non live")
            if not config.sierra_chart.trading_enabled:
                logger.warning("   ⚠️ Sierra Chart trading désactivé")
            if config.security.kill_switch_loss_threshold > 1500:
                logger.warning("   ⚠️ Kill switch threshold élevé")
                
        elif config.environment == "PAPER":
            logger.info("📝 MODE PAPER - Vérifications:")
            if config.ibkr.port != 7497:
                logger.warning("   ⚠️ Port IBKR non standard pour PAPER (7497)")
            if config.sierra_chart.trading_enabled:
                logger.info("   ✅ Sierra Chart simulation mode recommandé")
                
        elif config.environment == "DATA_COLLECTION":
            logger.info("📊 MODE DATA COLLECTION - Vérifications:")
            if config.sierra_chart.trading_enabled:
                logger.warning("   ⚠️ Sierra Chart trading activé (non recommandé)")
            if not config.ibkr.enable_tick_data:
                logger.warning("   ⚠️ Tick data désactivé")
        
        logger.info("=" * 60)
    
    async def start_trading_session(self) -> bool:
        """Démarre une session de trading"""
        try:
            logger.info(f"🎯 Démarrage session de trading mode={self.mode.value}")
            
            # Vérifications
            if not await self._pre_trading_checks():
                logger.error("❌ Échec vérifications pré-trading")
                return False
            
            # Créer session
            self.current_session = TradingSession(
                session_id=f"{self.mode.value}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                start_time=datetime.now(),
                mode=self.mode,
                status=AutomationStatus.STARTING,
                target_trades=self.target_trades if self.mode == TradingMode.DATA_COLLECTION else 0
            )
            
            # Reset stats
            self._reset_daily_stats()
            
            # Update status
            self.status = AutomationStatus.RUNNING
            self.is_trading = True
            self.should_stop = False
            
            # Notification Discord
            if self.discord_enabled:
                await self._notify_session_start()
            
            logger.info(f"✅ Session démarrée: {self.current_session.session_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur démarrage session: {e}")
            self.status = AutomationStatus.ERROR
            return False
    
    async def run_trading_loop(self):
        """
        BOUCLE PRINCIPALE - Génère signaux et exécute trades
        """
        logger.info("🔄 Démarrage boucle principale de trading")
        
        # Notification initiale
        if self.mode == TradingMode.DATA_COLLECTION and self.discord_enabled:
            await self.discord.send_custom_message(
                'signals',
                "🎯 Mode Collecte Données Activé",
                f"Objectif: {self.target_trades} trades\n"
                f"Seuil probabilité: {self.min_probability:.0%}\n"
                f"Limites désactivées sauf daily loss"
            )
        
        while self.is_trading and not self.should_stop:
            try:
                loop_start = time.time()
                
                # 1. Vérifier heures de trading (sauf mode data collection)
                if self.mode != TradingMode.DATA_COLLECTION and not self._is_trading_hours():
                    await asyncio.sleep(60)
                    continue
                
                # 2. Obtenir données marché
                market_data = await self._get_current_market_data()
                if not market_data:
                    await asyncio.sleep(5)
                    continue
                
                # 3. GÉNÉRER SIGNAL avec SignalGenerator (CERVEAU)
                signal = self.signal_generator.generate_signal(market_data)
                
                if signal:
                    self.session_stats['signals_total'] += 1
                    
                    # 4. Vérifier seuil de probabilité
                    signal_confidence = signal.total_confidence
                    
                    if signal_confidence >= self.min_probability:
                        self.session_stats['signals_above_threshold'] += 1
                        
                        # 5. Snapshot pre-analysis
                        trade_id = self.snapshotter.capture_pre_analysis_snapshot(market_data)
                        
                        # 6. Évaluer avec Risk Manager
                        decision = self.risk_manager.evaluate_signal(
                            signal, 
                            market_data.close,
                            self.get_account_equity()
                        )
                        
                        # 7. Snapshot decision
                        self.snapshotter.capture_decision_snapshot(
                            trade_id,
                            {
                                'signal': signal,
                                'decision': decision,
                                'confidence': signal_confidence,
                                'bataille_navale': signal.components.bataille_navale if hasattr(signal, 'components') else None
                            },
                            self.signal_generator.feature_calculator.last_features
                        )
                        
                        # 8. Exécuter si approuvé
                        if decision.action == RiskAction.APPROVE:
                            await self._execute_trade(signal, decision, market_data, trade_id)
                            self.session_stats['signals_executed'] += 1
                        else:
                            logger.info(f"❌ Signal rejeté: {decision.reason}")
                    else:
                        logger.debug(f"Signal sous seuil: {signal_confidence:.2%} < {self.min_probability:.2%}")
                
                # 9. Gérer positions existantes
                await self._manage_open_positions(market_data)
                
                # 10. Vérifier objectifs (mode data collection)
                if self.mode == TradingMode.DATA_COLLECTION:
                    if self.session_stats['trades_completed'] >= self.target_trades:
                        logger.info(f"🎯 OBJECTIF ATTEINT! {self.session_stats['trades_completed']} trades collectés")
                        await self._notify_objective_reached()
                        break
                
                # 11. Vérifier limites quotidiennes
                if self._check_daily_limits():
                    logger.warning("🛑 Limites quotidiennes atteintes")
                    break
                
                # 12. Performance tracking
                loop_time = time.time() - loop_start
                self.execution_times.append(loop_time)
                
                if loop_time > 0.1:
                    logger.warning(f"⚠️ Boucle lente: {loop_time:.3f}s")
                
                # 13. Progress update (toutes les 10 trades en mode data collection)
                if (self.mode == TradingMode.DATA_COLLECTION and 
                    self.session_stats['trades_completed'] % 10 == 0 and 
                    self.session_stats['trades_completed'] > 0):
                    await self._notify_progress()
                
                # Sleep
                await asyncio.sleep(1)
                
            except Exception as e:
                logger.error(f"❌ Erreur dans boucle: {e}", exc_info=True)
                await asyncio.sleep(5)
        
        logger.info("🏁 Boucle principale terminée")
        await self._end_trading_session()
    
    async def _execute_trade(self, signal: Any, decision: Any, 
                           market_data: MarketData, trade_id: str):
        """Exécute un trade approuvé"""
        try:
            # Préparer ordre
            order_details = {
                'symbol': market_data.symbol,
                'side': 'BUY' if signal.decision.value.startswith('LONG') else 'SELL',
                'size': decision.approved_size,
                'order_type': 'MKT',
                'stop_loss': decision.stop_loss_price,
                'take_profit': decision.take_profit_price,
                'signal_confidence': signal.total_confidence,
                'trade_id': trade_id
            }
            
            # Exécuter (simulé en mode paper/data collection)
            if self.mode == TradingMode.LIVE:
                order_result = await self.order_manager.submit_order(order_details)
            else:
                # Simulation pour paper/data collection
                order_result = {
                    'status': 'FILLED',
                    'fill_price': market_data.close + (0.25 if order_details['side'] == 'BUY' else -0.25),
                    'fill_time': datetime.now(),
                    'order_id': f"SIM_{trade_id}"
                }
            
            if order_result.get('status') == 'FILLED':
                # Créer position
                position = Position(
                    position_id=trade_id,
                    symbol=market_data.symbol,
                    side='LONG' if order_details['side'] == 'BUY' else 'SHORT',
                    size=decision.approved_size,
                    entry_price=order_result['fill_price'],
                    entry_time=datetime.now(),
                    stop_loss=decision.stop_loss_price,
                    take_profit=decision.take_profit_price,
                    current_price=market_data.close
                )
                
                self.positions[trade_id] = position
                self.active_position = position
                self.trade_ids.append(trade_id)
                
                # Snapshot execution
                self.snapshotter.capture_execution_snapshot(
                    trade_id,
                    order_result,
                    position.__dict__
                )
                
                # Update stats
                self.daily_stats['trades_count'] += 1
                
                # Discord notification
                if self.discord_enabled:
                    await self._notify_trade_executed(position, signal)
                
                logger.info(f"✅ Trade exécuté: {position.side} {position.size} @ {position.entry_price}")
                
        except Exception as e:
            logger.error(f"❌ Erreur exécution trade: {e}")
    
    async def _manage_open_positions(self, market_data: MarketData):
        """Gère les positions ouvertes"""
        positions_to_close = []
        
        for position_id, position in self.positions.items():
            # Update prix courant et P&L
            position.current_price = market_data.close
            position.bars_in_trade += 1
            
            if position.side == 'LONG':
                pnl_ticks = (market_data.close - position.entry_price) / ES_TICK_SIZE
            else:
                pnl_ticks = (position.entry_price - market_data.close) / ES_TICK_SIZE
            
            position.unrealized_pnl = pnl_ticks * position.size * ES_TICK_VALUE
            
            # Track max profit/loss
            position.max_profit = max(position.max_profit, position.unrealized_pnl)
            position.max_loss = min(position.max_loss, position.unrealized_pnl)
            
            # Snapshot position update
            if position.bars_in_trade % 10 == 0:  # Toutes les 10 barres
                self.snapshotter.capture_position_update(
                    position_id,
                    position.__dict__,
                    market_data
                )
            
            # Vérifier conditions de sortie
            should_exit, exit_reason = self._should_exit_position(position, market_data)
            
            if should_exit:
                positions_to_close.append((position_id, exit_reason))
        
        # Fermer les positions
        for position_id, exit_reason in positions_to_close:
            await self._close_position(position_id, exit_reason, market_data)
    
    def _should_exit_position(self, position: Position, 
                            market_data: MarketData) -> Tuple[bool, str]:
        """Détermine si on doit sortir"""
        current_price = market_data.close
        
        # Stop Loss
        if position.stop_loss:
            if (position.side == 'LONG' and current_price <= position.stop_loss) or \
               (position.side == 'SHORT' and current_price >= position.stop_loss):
                return True, "STOP_LOSS"
        
        # Take Profit
        if position.take_profit:
            if (position.side == 'LONG' and current_price >= position.take_profit) or \
               (position.side == 'SHORT' and current_price <= position.take_profit):
                return True, "TAKE_PROFIT"
        
        # Time-based exit (exemple: 50 barres max)
        if position.bars_in_trade > 50:
            return True, "TIME_EXIT"
        
        # Nouveau signal opposé
        latest_signal = self.signal_generator.get_last_signal()
        if latest_signal:
            if (position.side == 'LONG' and latest_signal.decision.value.startswith('SHORT')) or \
               (position.side == 'SHORT' and latest_signal.decision.value.startswith('LONG')):
                return True, "SIGNAL_REVERSAL"
        
        return False, ""
    
    async def _close_position(self, position_id: str, exit_reason: str, 
                            market_data: MarketData):
        """Ferme une position"""
        try:
            position = self.positions.get(position_id)
            if not position:
                return
            
            # Calculer P&L final
            exit_price = market_data.close
            
            if position.side == 'LONG':
                pnl_ticks = (exit_price - position.entry_price) / ES_TICK_SIZE
            else:
                pnl_ticks = (position.entry_price - exit_price) / ES_TICK_SIZE
            
            final_pnl = pnl_ticks * position.size * ES_TICK_VALUE
            
            # Snapshot résultat final
            trade_result = {
                'position_id': position_id,
                'entry_price': position.entry_price,
                'exit_price': exit_price,
                'pnl': final_pnl,
                'pnl_ticks': pnl_ticks,
                'exit_reason': exit_reason,
                'bars_in_trade': position.bars_in_trade,
                'max_profit': position.max_profit,
                'max_loss': position.max_loss
            }
            
            self.snapshotter.capture_trade_result(position_id, trade_result)
            
            # Update stats
            self._update_trade_statistics(final_pnl, exit_reason)
            self.session_stats['trades_completed'] += 1
            
            # Discord notification
            if self.discord_enabled:
                await self._notify_trade_closed(position, final_pnl, exit_reason)
            
            # Retirer de positions actives
            del self.positions[position_id]
            if self.active_position and self.active_position.position_id == position_id:
                self.active_position = None
            
            logger.info(f"✅ Position fermée: {exit_reason} - P&L: ${final_pnl:.2f} ({pnl_ticks:.1f} ticks)")
            
        except Exception as e:
            logger.error(f"❌ Erreur fermeture position: {e}")
    
    def _update_trade_statistics(self, pnl: float, exit_reason: str):
        """Met à jour les statistiques"""
        self.daily_stats['gross_pnl'] += pnl
        
        if pnl > 0:
            self.daily_stats['winning_trades'] += 1
            self.daily_stats['largest_win'] = max(self.daily_stats['largest_win'], pnl)
        else:
            self.daily_stats['losing_trades'] += 1
            self.daily_stats['largest_loss'] = min(self.daily_stats['largest_loss'], pnl)
        
        # Drawdown
        if self.daily_stats['gross_pnl'] < self.daily_stats['max_drawdown']:
            self.daily_stats['max_drawdown'] = self.daily_stats['gross_pnl']
    
    def _check_daily_limits(self) -> bool:
        """Vérifie limites quotidiennes selon le mode"""
        
        # Daily loss (TOUJOURS ACTIF dans tous les modes)
        if self.daily_stats['gross_pnl'] <= -self.risk_manager.params.daily_loss_limit:
            logger.warning(f"🛑 Daily loss limit: ${self.daily_stats['gross_pnl']:.2f}")
            if self.discord_enabled:
                asyncio.create_task(
                    self.discord.send_custom_message(
                        'alerts',
                        f"🚨 DAILY LOSS LIMIT",
                        f"P&L: ${self.daily_stats['gross_pnl']:.2f}\n"
                        f"Limite: ${self.risk_manager.params.daily_loss_limit:.0f}\n"
                        f"Trading automatiquement arrêté",
                        color=0xff0000
                    )
                )
            return True
        
        # 🎯 AUTRES LIMITES: seulement si PAS en mode data collection
        if self.mode != TradingMode.DATA_COLLECTION:
            
            # Profit target (mode normal seulement)
            if self.daily_stats['gross_pnl'] >= self.risk_manager.params.daily_profit_target:
                logger.info(f"🎯 Daily profit target: ${self.daily_stats['gross_pnl']:.2f}")
                if self.discord_enabled:
                    asyncio.create_task(
                        self.discord.send_custom_message(
                            'performance',
                            f"🎯 PROFIT TARGET ATTEINT",
                            f"P&L: ${self.daily_stats['gross_pnl']:.2f}\n"
                            f"Target: ${self.risk_manager.params.daily_profit_target:.0f}\n"
                            f"Session terminée avec succès!",
                            color=0x00ff00
                        )
                    )
                return True
            
            # Max trades (mode normal seulement)
            if self.daily_stats['trades_count'] >= self.risk_manager.params.max_daily_trades:
                logger.info(f"📊 Max daily trades: {self.daily_stats['trades_count']}")
                return True
        
        else:
            # 📊 MODE DATA COLLECTION: Log progress sans arrêter
            if self.daily_stats['trades_count'] % 50 == 0 and self.daily_stats['trades_count'] > 0:
                progress = self.daily_stats['trades_count'] / self.target_trades if self.target_trades > 0 else 0
                logger.info(f"📊 MODE COLLECTE - Progress: {self.daily_stats['trades_count']} trades "
                           f"({progress:.1%} de l'objectif)")
        
        return False
    
    def _is_trading_hours(self) -> bool:
        """Vérifie heures de trading"""
        now = datetime.now().time()
        # Simplification: 9h30 - 16h00 ET
        return 9 <= now.hour < 16 or (now.hour == 9 and now.minute >= 30)
    
    async def _get_current_market_data(self) -> Optional[MarketData]:
        """Obtient données marché (à implémenter avec votre feed)"""
        try:
            # TODO: Connecter à votre source de données réelle
            # Pour tests: données simulées
            if not hasattr(self, '_price_base'):
                self._price_base = 4500.0
            
            # Simulation mouvement de prix
            self._price_base += np.random.randn() * 0.5
            
            return MarketData(
                symbol="ES",
                timestamp=pd.Timestamp.now(),
                open=self._price_base - 1,
                high=self._price_base + 1,
                low=self._price_base - 1.5,
                close=self._price_base,
                volume=np.random.randint(500, 2000)
            )
            
        except Exception as e:
            logger.error(f"❌ Erreur données marché: {e}")
            return None
    
    async def _pre_trading_checks(self) -> bool:
        """Vérifications pré-trading"""
        all_ok = True
        
        # SignalGenerator
        if not self.signal_generator:
            logger.error("❌ SignalGenerator non initialisé")
            all_ok = False
        
        # Risk Manager
        if not self.risk_manager:
            logger.error("❌ RiskManager non initialisé")
            all_ok = False
        
        # Validation configuration Sierra/IBKR
        if not self.sierra_config.validate():
            logger.error("❌ Configuration Sierra/IBKR invalide")
            all_ok = False
        
        # Order Manager selon le provider
        if self.sierra_config.order_provider.value == "sierra_chart":
            if self.mode == TradingMode.LIVE and not self.order_manager.is_connected():
                logger.error("❌ OrderManager non connecté à Sierra Chart")
                all_ok = False
            
            # Vérifier que Sierra Chart trading est activé pour live
            if self.mode == TradingMode.LIVE and not self.sierra_config.sierra_chart.trading_enabled:
                logger.error("❌ Sierra Chart trading désactivé en mode LIVE")
                all_ok = False
        
        # Vérifications spécifiques par mode
        if self.mode == TradingMode.LIVE:
            # Mode live: vérifications strictes
            if self.sierra_config.ibkr.port != 7496:
                logger.warning("⚠️ Mode LIVE mais port IBKR n'est pas 7496 (live port)")
            
            if self.sierra_config.ibkr.market_data_type != 1:
                logger.warning("⚠️ Mode LIVE mais market data type n'est pas 1 (live data)")
                
        elif self.mode == TradingMode.PAPER:
            # Mode paper: vérifications paper
            if self.sierra_config.ibkr.port != 7497:
                logger.warning("⚠️ Mode PAPER mais port IBKR n'est pas 7497 (paper port)")
        
        elif self.mode == TradingMode.DATA_COLLECTION:
            # Mode data collection: vérifier que trading est désactivé
            if self.sierra_config.sierra_chart.trading_enabled:
                logger.warning("⚠️ Mode DATA_COLLECTION mais Sierra Chart trading activé")
                # Désactiver automatiquement
                self.sierra_config.sierra_chart.trading_enabled = False
                logger.info("🔧 Sierra Chart trading automatiquement désactivé")
        
        # Vérifications symboles
        if not self.sierra_config.contracts.enabled_symbols:
            logger.error("❌ Aucun symbole configuré")
            all_ok = False
        
        # Log résumé vérifications
        if all_ok:
            logger.info("✅ Toutes les vérifications pré-trading réussies")
            logger.info(f"   - Mode: {self.mode.value}")
            logger.info(f"   - Data: {self.sierra_config.data_provider.value}")
            logger.info(f"   - Orders: {self.sierra_config.order_provider.value}")
            logger.info(f"   - Symboles: {self.sierra_config.contracts.enabled_symbols}")
        else:
            logger.error("❌ Échec vérifications pré-trading")
        
        # Discord (optionnel)
        if self.discord_enabled and not self.discord:
            logger.warning("⚠️ Discord non disponible")
        
        return all_ok
    
    def _init_daily_stats(self) -> Dict:
        """Initialise stats quotidiennes"""
        return {
            'trades_count': 0,
            'winning_trades': 0,
            'losing_trades': 0,
            'gross_pnl': 0.0,
            'net_pnl': 0.0,
            'max_drawdown': 0.0,
            'largest_win': 0.0,
            'largest_loss': 0.0,
            'signals_detected': 0,
            'signals_executed': 0
        }
    
    def _reset_daily_stats(self):
        """Reset stats quotidiennes"""
        self.daily_stats = self._init_daily_stats()
        self.session_stats = {
            'signals_total': 0,
            'signals_above_threshold': 0,
            'signals_executed': 0,
            'trades_completed': 0,
            'snapshots_captured': 0
        }
    
    def get_account_equity(self) -> float:
        """Retourne equity du compte (simulé)"""
        # TODO: Connecter à votre broker pour valeur réelle
        return 100000.0 + self.daily_stats['gross_pnl']
    
    async def _end_trading_session(self):
        """Termine la session"""
        try:
            logger.info("🏁 Fin de session de trading")
            
            # Fermer positions ouvertes
            positions_to_close = list(self.positions.keys())
            for position_id in positions_to_close:
                await self._close_position(position_id, "SESSION_END", self.last_market_data)
            
            # Finaliser session
            if self.current_session:
                self.current_session.end_time = datetime.now()
                self.current_session.trades_count = self.session_stats['trades_completed']
                self.current_session.signals_detected = self.session_stats['signals_total']
                self.current_session.signals_taken = self.session_stats['signals_executed']
                self.current_session.pnl = self.daily_stats['gross_pnl']
                self.current_session.status = AutomationStatus.STOPPED
            
            # Log summary
            self._log_session_summary()
            
            # Discord notification
            if self.discord_enabled:
                await self._notify_session_end()
            
            # Update status
            self.status = AutomationStatus.STOPPED
            self.is_trading = False
            
        except Exception as e:
            logger.error(f"❌ Erreur fin session: {e}")
    
    def _log_session_summary(self):
        """Log résumé session"""
        if not self.current_session:
            return
        
        duration = (datetime.now() - self.current_session.start_time).total_seconds() / 3600
        
        logger.info("=" * 60)
        logger.info(f"📊 RÉSUMÉ SESSION {self.mode.value}")
        logger.info(f"Session: {self.current_session.session_id}")
        logger.info(f"Durée: {duration:.1f}h")
        logger.info(f"Signaux détectés: {self.session_stats['signals_total']}")
        logger.info(f"Signaux > seuil: {self.session_stats['signals_above_threshold']}")
        logger.info(f"Signaux exécutés: {self.session_stats['signals_executed']}")
        logger.info(f"Trades complétés: {self.session_stats['trades_completed']}")
        
        if self.daily_stats['trades_count'] > 0:
            win_rate = self.daily_stats['winning_trades'] / self.daily_stats['trades_count']
            logger.info(f"Win Rate: {win_rate:.1%}")
        
        logger.info(f"P&L: ${self.daily_stats['gross_pnl']:.2f}")
        logger.info(f"Max Drawdown: ${self.daily_stats['max_drawdown']:.2f}")
        
        if self.mode == TradingMode.DATA_COLLECTION:
            progress = self.session_stats['trades_completed'] / self.target_trades
            logger.info(f"Progress: {progress:.1%} ({self.session_stats['trades_completed']}/{self.target_trades})")
        
        logger.info("=" * 60)
    
    # === NOTIFICATIONS DISCORD ===
    
    async def _notify_session_start(self):
        """Notification démarrage session"""
        if not self.discord_enabled:
            return
        
        try:
            message = f"Mode: {self.mode.value}\n"
            if self.mode == TradingMode.DATA_COLLECTION:
                message += f"Objectif: {self.target_trades} trades\n"
                message += f"Seuil: {self.min_probability:.0%}"
            
            await self.discord.send_custom_message(
                'trades',
                f"🚀 Session Trading Démarrée",
                message
            )
        except Exception as e:
            logger.error(f"Erreur Discord: {e}")
    
    async def _notify_trade_executed(self, position: Position, signal: Any):
        """Notification trade exécuté"""
        if not self.discord_enabled:
            return
        
        try:
            await self.discord.send_trade_executed({
                'side': position.side,
                'quantity': position.size,
                'intended_price': position.entry_price,
                'fill_price': position.entry_price,
                'slippage_ticks': 0,
                'position_size': position.size,
                'avg_price': position.entry_price,
                'risk_dollars': abs(position.entry_price - position.stop_loss) * position.size * ES_TICK_VALUE / ES_TICK_SIZE if position.stop_loss else 0,
                'battle_status': f"Confiance: {signal.total_confidence:.1%}"
            })
        except Exception as e:
            logger.error(f"Erreur Discord: {e}")
    
    async def _notify_trade_closed(self, position: Position, pnl: float, reason: str):
        """Notification trade fermé"""
        if not self.discord_enabled:
            return
        
        try:
            await self.discord.send_trade_closed({
                'side': position.side,
                'exit_price': position.current_price,
                'pnl': pnl,
                'pnl_ticks': pnl / (position.size * ES_TICK_VALUE) * ES_TICK_SIZE,
                'roi': pnl / (position.size * position.entry_price * ES_TICK_VALUE) if position.entry_price > 0 else 0,
                'duration_minutes': position.bars_in_trade,
                'max_profit_ticks': position.max_profit / (position.size * ES_TICK_VALUE) * ES_TICK_SIZE,
                'max_loss_ticks': position.max_loss / (position.size * ES_TICK_VALUE) * ES_TICK_SIZE,
                'exit_reason': reason,
                'exit_type': reason
            })
        except Exception as e:
            logger.error(f"Erreur Discord: {e}")
    
    async def _notify_progress(self):
        """Notification progress (mode data collection)"""
        if not self.discord_enabled or self.mode != TradingMode.DATA_COLLECTION:
            return
        
        try:
            progress = self.session_stats['trades_completed'] / self.target_trades
            win_rate = self.daily_stats['winning_trades'] / max(self.daily_stats['trades_count'], 1)
            
            await self.discord.send_custom_message(
                'performance',
                f"📊 Progress: {progress:.1%}",
                f"Trades: {self.session_stats['trades_completed']}/{self.target_trades}\n"
                f"Win Rate: {win_rate:.1%}\n"
                f"P&L: ${self.daily_stats['gross_pnl']:.2f}"
            )
        except Exception as e:
            logger.error(f"Erreur Discord: {e}")
    
    async def _notify_objective_reached(self):
        """Notification objectif atteint"""
        if not self.discord_enabled:
            return
        
        try:
            await self.discord.send_custom_message(
                'alerts',
                f"🎯 OBJECTIF ATTEINT!",
                f"{self.session_stats['trades_completed']} trades collectés!\n"
                f"Données prêtes pour analyse ML",
                color=0x00ff00
            )
        except Exception as e:
            logger.error(f"Erreur Discord: {e}")
    
    async def _notify_session_end(self):
        """Notification fin session"""
        if not self.discord_enabled:
            return
        
        try:
            duration = (datetime.now() - self.current_session.start_time).total_seconds() / 3600
            win_rate = self.daily_stats['winning_trades'] / max(self.daily_stats['trades_count'], 1)
            
            report_data = {
                'date': datetime.now().strftime('%Y-%m-%d'),
                'total_pnl': self.daily_stats['gross_pnl'],
                'total_trades': self.daily_stats['trades_count'],
                'win_rate': win_rate,
                'profit_factor': abs(self.daily_stats['largest_win'] / min(self.daily_stats['largest_loss'], -0.01)) if self.daily_stats['largest_loss'] < 0 else 0,
                'signals_detected': self.session_stats['signals_total'],
                'signals_taken': self.session_stats['signals_executed'],
                'selectivity': self.session_stats['signals_executed'] / max(self.session_stats['signals_total'], 1),
                'golden_rule_respect': 1.0,  # TODO: tracker les violations
                'best_trade': self.daily_stats['largest_win'],
                'worst_trade': abs(self.daily_stats['largest_loss']),
                'avg_win': self.daily_stats['largest_win'] / max(self.daily_stats['winning_trades'], 1),
                'avg_loss': abs(self.daily_stats['largest_loss']) / max(self.daily_stats['losing_trades'], 1)
            }
            
            if self.mode == TradingMode.DATA_COLLECTION:
                report_data['ml_insights'] = [
                    f"Mode collecte: {self.session_stats['trades_completed']} trades capturés",
                    f"Durée session: {duration:.1f}h",
                    f"Trades/heure: {self.session_stats['trades_completed']/duration:.1f}",
                    f"Snapshots sauvés dans data/snapshots/"
                ]
            
            await self.discord.send_daily_report(report_data)
            
        except Exception as e:
            logger.error(f"Erreur Discord: {e}")
    
    # === MÉTHODES PUBLIQUES ===
    
    async def stop_trading(self):
        """Arrête le trading"""
        logger.info("🛑 Arrêt demandé")
        self.should_stop = True
        
        # Attendre fin de boucle
        max_wait = 30  # secondes
        waited = 0
        while self.is_trading and waited < max_wait:
            await asyncio.sleep(1)
            waited += 1
        
        if self.is_trading:
            logger.warning("⚠️ Force stop après timeout")
            self.is_trading = False
    
    def get_status(self) -> Dict[str, Any]:
        """Retourne statut système complet"""
        risk_status = self.risk_manager.get_risk_status() if self.risk_manager else None
        
        # Calculer des métriques supplémentaires
        win_rate = self.daily_stats['winning_trades'] / max(self.daily_stats['trades_count'], 1)
        
        # Progress pour mode data collection
        progress_info = {}
        if self.mode == TradingMode.DATA_COLLECTION:
            progress_info = {
                'target_trades': getattr(self, 'target_trades', 500),
                'completed_trades': self.session_stats['trades_completed'],
                'progress_percent': (self.session_stats['trades_completed'] / getattr(self, 'target_trades', 500)) * 100,
                'remaining_trades': getattr(self, 'target_trades', 500) - self.session_stats['trades_completed']
            }
        
        # Status Sierra/IBKR
        sierra_status = {
            'environment': self.sierra_config.environment,
            'data_provider': self.sierra_config.data_provider.value,
            'order_provider': self.sierra_config.order_provider.value,
            'ibkr_host': self.sierra_config.ibkr.host,
            'ibkr_port': self.sierra_config.ibkr.port,
            'ibkr_client_id': self.sierra_config.ibkr.client_id,
            'sierra_address': self.sierra_config.sierra_chart.server_address,
            'sierra_port': self.sierra_config.sierra_chart.server_port,
            'sierra_trading_enabled': self.sierra_config.sierra_chart.trading_enabled,
            'primary_symbol': self.sierra_config.contracts.primary_symbol,
            'enabled_symbols': self.sierra_config.contracts.enabled_symbols,
            'config_valid': self.sierra_config.validate()
        }
        
        return {
            'status': self.status.value,
            'mode': self.mode.value,
            'is_trading': self.is_trading,
            'session': self.current_session.__dict__ if self.current_session else None,
            'positions': len(self.positions),
            'daily_stats': {
                **self.daily_stats,
                'win_rate': win_rate,
                'trades_remaining_to_limit': self.risk_manager.params.max_daily_trades - self.daily_stats['trades_count'] if self.risk_manager else 0,
                'loss_remaining_to_limit': self.risk_manager.params.daily_loss_limit + self.daily_stats['gross_pnl'] if self.risk_manager else 0
            },
            'session_stats': self.session_stats,
            'risk_status': risk_status,
            'risk_params': {
                'min_probability': self.min_probability if hasattr(self, 'min_probability') else 0,
                'data_collection_mode': self.risk_manager.params.data_collection_mode if self.risk_manager else False,
                'golden_rule_strict': self.risk_manager.params.golden_rule_strict if self.risk_manager else True,
                'daily_loss_limit': self.risk_manager.params.daily_loss_limit if self.risk_manager else 0,
                'max_daily_trades': self.risk_manager.params.max_daily_trades if self.risk_manager else 0
            },
            'sierra_ibkr_status': sierra_status,
            'data_collection_progress': progress_info
        }


# === FACTORY & HELPERS ===

def create_simple_trader(mode: str = "PAPER") -> SimpleBattleNavaleTrader:
    """Factory pour créer trader"""
    return SimpleBattleNavaleTrader(mode)


async def run_data_collection_session(target_trades: int = 500):
    """Lance session de collecte de données"""
    trader = create_simple_trader("DATA_COLLECTION")
    trader.target_trades = target_trades
    
    # Log des paramètres de collecte
    logger.info("🎯 SESSION DE COLLECTE DE DONNÉES")
    logger.info("=" * 60)
    logger.info(f"Objectif: {target_trades} trades")
    trader.log_risk_diagnostics()
    
    try:
        if await trader.start_trading_session():
            await trader.run_trading_loop()
            return True
    except KeyboardInterrupt:
        logger.info("⌨️ Interruption utilisateur")
    except Exception as e:
        logger.error(f"❌ Erreur session: {e}")
    finally:
        await trader.stop_trading()
    
    return False


# === MAIN ===

if __name__ == "__main__":
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
    
    asyncio.run(main())

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
