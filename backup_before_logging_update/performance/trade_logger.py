#!/usr/bin/env python3
"""
MIA_IA_SYSTEM - Trade Logger
📝 LOG CHAQUE TRADE AVEC CONTEXTE COMPLET

Version: Phase 3B - Performance & Automation Focus
Responsabilité: Logging obsessif trades pour analyse ML & optimisation

FONCTIONNALITÉS CRITIQUES :
1. 📊 Log trade complet - Prix, time, features, signals, patterns
2. 🔄 Update outcome temps réel - P&L, exit reason, performance
3. 💾 Stockage optimisé - JSON structuré, compression, indexation
4. 🔍 Recherche rapide - Index par date, symbole, pattern
5. 📈 Préparation ML - Features formatées pour training
6. 🚨 Validation données - Contrôle qualité & cohérence

WORKFLOW LOGGING :
Signal → Log Entry → Execute → Update Outcome → Analysis Ready

STORAGE FORMAT :
- Real-time: JSON Lines pour performance
- Daily: Compressed archives avec index
- ML-Ready: Features matrices pré-calculées
"""

import os
import json
import time
import uuid
import gzip
import threading
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
from datetime import datetime, timezone, date
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
import logging

# Local imports
from core.base_types import TradingSignal, TradeResult, MarketData
from config.automation_config import get_automation_config

logger = logging.getLogger(__name__)

# === TRADE LOGGING DATA STRUCTURES ===


@dataclass
class TradeRecord:
    """Structure complète d'un trade loggé"""
    # Trade identity
    trade_id: str
    timestamp: datetime
    symbol: str

    # Trade action
    action: str                    # ENTRY/EXIT
    side: str                     # LONG/SHORT
    price: float
    quantity: int

    # Features snapshot (8D model)
    features_snapshot: Dict[str, float]

    # Strategy context
    strategy_mode: str            # TREND/RANGE/BREAKOUT
    pattern_detected: List[str]   # Battle navale, Gamma pin, etc.
    confidence_score: float       # 0.0-1.0

    # Market context
    market_regime: str            # BULL/BEAR/SIDEWAYS
    volatility_regime: str        # LOW/NORMAL/HIGH
    session_phase: str            # OPEN/MID/CLOSE

    # Outcome (filled later)
    outcome: Optional[Dict] = None

    # Metadata
    created_at: datetime = None
    updated_at: datetime = None


class TradeLogger:
    """
    TRADE LOGGER - Capture obsessive de tous les trades

    Responsabilités :
    1. Log instantané de chaque trade avec contexte complet
    2. Update résultats en temps réel
    3. Stockage optimisé pour recherche rapide
    4. Préparation données ML automatique
    """

    def __init__(self, config: Optional[Dict] = None):
        """
        Initialisation Trade Logger

        Args:
            config: Configuration optionnelle
        """
        self.config = config or get_automation_config()

        # Storage paths
        self.base_path = Path("data/performance/logs")
        self.daily_path = self.base_path / "daily"
        self.archive_path = self.base_path / "archive"
        self.index_path = self.base_path / "index"

        # Création directories
        for path in [self.daily_path, self.archive_path, self.index_path]:
            path.mkdir(parents=True, exist_ok=True)

        # Real-time storage
        self.active_trades: Dict[str, TradeRecord] = {}
        self.completed_trades: deque = deque(maxlen=1000)
        self.daily_trades: Dict[date, List[TradeRecord]] = defaultdict(list)

        # File handles
        self.current_log_file = None
        self.current_date = None

        # Threading pour async writes
        self.write_queue: deque = deque()
        self.write_thread = None
        self.is_writing = False

        # Index tracking
        self.trade_index: Dict[str, Dict] = {}
        self.pattern_index: Dict[str, List[str]] = defaultdict(list)
        self.daily_stats: Dict[date, Dict] = {}

        # Validation config
        self.validation_rules = {
            'required_features': [
                'vwap_trend_signal', 'sierra_pattern_strength',
                'dow_trend_regime', 'gamma_levels_proximity',
                'volume_profile_signal', 'level2_strength',
                'momentum_shift', 'confluence_score'
            ],
            'price_range_check': True,
            'feature_range_check': True,
            'pattern_validation': True
        }

        self._initialize_logging()
        logger.info(f"TradeLogger initialisé: {self.base_path}")

    def _initialize_logging(self):
        """Initialisation système de logging"""
        try:
            # Ouverture fichier du jour
            self._open_daily_log_file()

            # Démarrage thread écriture async
            self._start_write_thread()

            # Chargement index existant
            self._load_existing_index()

        except Exception as e:
            logger.error(f"Erreur initialisation logging: {e}")

    def log_trade(self, trade_data: Dict[str, Any]) -> str:
        """
        LOG TRADE avec contexte complet

        Args:
            trade_data: Données complètes du trade

        Returns:
            str: Trade ID généré
        """
        try:
            start_time = time.perf_counter()

            # Génération trade ID unique
            trade_id = self._generate_trade_id(trade_data)

            # Validation données d'entrée
            if not self._validate_trade_data(trade_data):
                logger.error(f"Données trade invalides: {trade_id}")
                return None

            # Création TradeRecord
            trade_record = TradeRecord(
                trade_id=trade_id,
                timestamp=datetime.now(timezone.utc),
                symbol=trade_data.get('symbol', 'ES'),

                # Action details
                action=trade_data.get('action', 'ENTRY'),
                side=trade_data.get('side', 'LONG'),
                price=float(trade_data.get('price', 0.0)),
                quantity=int(trade_data.get('quantity', 1)),

                # Features snapshot (8D model)
                features_snapshot=trade_data.get('features_8d', {}),

                # Strategy context
                strategy_mode=trade_data.get('regime', 'TREND'),
                pattern_detected=trade_data.get('patterns', []),
                confidence_score=float(trade_data.get('confidence', 0.5)),

                # Market context
                market_regime=trade_data.get('market_regime', 'SIDEWAYS'),
                volatility_regime=trade_data.get('volatility_regime', 'NORMAL'),
                session_phase=trade_data.get('session_phase', 'MID'),

                # Metadata
                created_at=datetime.now(timezone.utc)
            )

            # Stockage en mémoire
            self.active_trades[trade_id] = trade_record
            self.daily_trades[date.today()].append(trade_record)

            # Mise à jour index
            self._update_trade_index(trade_record)

            # Écriture async
            self._queue_write_operation('trade_entry', asdict(trade_record))

            # Performance timing
            log_time = (time.perf_counter() - start_time) * 1000

            logger.info(f"Trade loggé: {trade_id} ({log_time:.1f}ms)")
            return trade_id

        except Exception as e:
            logger.error(f"Erreur log_trade: {e}")
            return None

    def update_trade_outcome(self, trade_id: str, pnl: float,
                             exit_reason: str, exit_price: float = None) -> bool:
        """
        UPDATE résultat trade

        Args:
            trade_id: ID du trade
            pnl: Profit/Loss net
            exit_reason: Raison de sortie
            exit_price: Prix de sortie

        Returns:
            bool: Succès de l'update
        """
        try:
            if trade_id not in self.active_trades:
                logger.warning(f"Trade introuvable pour update: {trade_id}")
                return False

            trade_record = self.active_trades[trade_id]

            # Calcul outcome détaillé
            outcome = {
                'pnl_net': float(pnl),
                'exit_price': float(exit_price) if exit_price else trade_record.price,
                'exit_reason': exit_reason,
                'exit_timestamp': datetime.now(timezone.utc).isoformat(),
                'holding_time_seconds': (datetime.now(timezone.utc) - trade_record.timestamp).total_seconds(),
                'is_profitable': pnl > 0,
                'success_rate_contribution': 1.0 if pnl > 0 else 0.0
            }

            # Update trade record
            trade_record.outcome = outcome
            trade_record.updated_at = datetime.now(timezone.utc)

            # Déplacement vers completed
            self.completed_trades.append(trade_record)
            del self.active_trades[trade_id]

            # Mise à jour statistiques
            self._update_daily_stats(trade_record)

            # Écriture async
            self._queue_write_operation('trade_outcome', {
                'trade_id': trade_id,
                'outcome': outcome,
                'updated_at': trade_record.updated_at.isoformat()
            })

            logger.info(f"Trade outcome updated: {trade_id} (P&L: ${pnl:.2f})")
            return True

        except Exception as e:
            logger.error(f"Erreur update_trade_outcome: {e}")
            return False

    def get_status(self) -> Dict[str, Any]:
        """Status actuel du logger"""
        return {
            'active_trades': len(self.active_trades),
            'completed_trades': len(self.completed_trades),
            'daily_trades_today': len(self.daily_trades.get(date.today(), [])),
            'write_queue_size': len(self.write_queue),
            'current_log_file': str(self.current_log_file) if self.current_log_file else None,
            'is_writing': self.is_writing
        }

    # === PRIVATE METHODS ===

    def _generate_trade_id(self, trade_data: Dict) -> str:
        """Génération ID unique pour trade"""
        timestamp = int(time.time() * 1000)
        symbol = trade_data.get('symbol', 'ES')
        price = trade_data.get('price', 0)
        return f"{symbol}_{timestamp}_{abs(hash(str(price))) % 10000:04d}"

    def _validate_trade_data(self, trade_data: Dict) -> bool:
        """Validation données trade"""
        if not self.validation_rules.get('required_features'):
            return True

        features = trade_data.get('features_8d', {})
        for required_feature in self.validation_rules['required_features']:
            if required_feature not in features:
                logger.warning(f"Feature manquante: {required_feature}")
                return False

        return True

    def _open_daily_log_file(self):
        """Ouverture fichier log du jour"""
        today = date.today()
        if self.current_date != today:
            if self.current_log_file:
                self.current_log_file.close()

            log_file_path = self.daily_path / f"trades_{today.isoformat()}.jsonl"
            self.current_log_file = open(log_file_path, 'a', encoding='utf-8')
            self.current_date = today

    def _queue_write_operation(self, operation_type: str, data: Dict):
        """Ajout opération écriture à la queue"""
        write_operation = {
            'type': operation_type,
            'data': data,
            'timestamp': time.time()
        }
        self.write_queue.append(write_operation)

    def _start_write_thread(self):
        """Démarrage thread écriture asynchrone"""
        if not self.write_thread or not self.write_thread.is_alive():
            self.is_writing = True
            self.write_thread = threading.Thread(
                target=self._write_worker,
                daemon=True
            )
            self.write_thread.start()

    def _write_worker(self):
        """Worker thread pour écriture async"""
        while self.is_writing:
            try:
                if self.write_queue:
                    operation = self.write_queue.popleft()
                    self._execute_write_operation(operation)
                else:
                    time.sleep(0.1)  # Courte pause si queue vide
            except Exception as e:
                logger.error(f"Erreur write worker: {e}")
                time.sleep(1)

    def _execute_write_operation(self, operation: Dict):
        """Exécution opération d'écriture"""
        try:
            self._open_daily_log_file()

            write_data = {
                'operation': operation['type'],
                'timestamp': operation['timestamp'],
                'data': operation['data']
            }

            self.current_log_file.write(json.dumps(write_data) + '\n')
            self.current_log_file.flush()

        except Exception as e:
            logger.error(f"Erreur écriture: {e}")

    def _update_trade_index(self, trade_record: TradeRecord):
        """Mise à jour index des trades"""
        trade_id = trade_record.trade_id

        self.trade_index[trade_id] = {
            'timestamp': trade_record.timestamp.isoformat(),
            'symbol': trade_record.symbol,
            'patterns': trade_record.pattern_detected,
            'strategy_mode': trade_record.strategy_mode
        }

        # Index par pattern
        for pattern in trade_record.pattern_detected:
            self.pattern_index[pattern].append(trade_id)

    def _update_daily_stats(self, trade_record: TradeRecord):
        """Mise à jour statistiques journalières"""
        today = date.today()

        if today not in self.daily_stats:
            self.daily_stats[today] = {
                'total_trades': 0,
                'profitable_trades': 0,
                'total_pnl': 0.0,
                'patterns_count': defaultdict(int)
            }

        stats = self.daily_stats[today]
        stats['total_trades'] += 1

        if trade_record.outcome:
            if trade_record.outcome['is_profitable']:
                stats['profitable_trades'] += 1
            stats['total_pnl'] += trade_record.outcome['pnl_net']

        # Comptage patterns
        for pattern in trade_record.pattern_detected:
            stats['patterns_count'][pattern] += 1

    def _load_existing_index(self):
        """Chargement index existant"""
        # TODO: Implémentation chargement index depuis disque
        pass

# === FACTORY FUNCTION ===


def create_trade_logger(config: Optional[Dict] = None) -> TradeLogger:
    """Factory function pour TradeLogger"""
    return TradeLogger(config)

# === END MODULE ===
