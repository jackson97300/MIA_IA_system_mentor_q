#!/usr/bin/env python3
"""
MIA_IA_SYSTEM - Data Collector
📊 COLLECTION SNAPSHOTS & ORGANISATION ML-READY
Version: Phase 3B - Data Collection & Analytics Focused
Performance: Collection 24/7, organisation automatique, ML-ready exports

RESPONSABILITÉS CRITIQUES :
1. 📊 COLLECTION SNAPSHOTS - Agrégation données trade_snapshotter
2. 🗂️ ORGANISATION TEMPORELLE - Daily/Weekly/Monthly structure
3. 🧠 PRÉPARATION ML - Datasets formatés sklearn/xgboost ready
4. 💾 ARCHIVAGE INTELLIGENT - Compression, backup, rétention
5. ✅ VALIDATION INTÉGRITÉ - Vérification qualité données
6. 📈 ANALYTICS PREPROCESSING - Features engineering pour ML

WORKFLOW COMPLET :
TradeSnapshotter → DataCollector → ML-Ready Datasets → Analytics

INPUT : Snapshots JSON du trade_snapshotter
OUTPUT : Datasets structurés + Analytics + ML exports
"""

import os
import json
import gzip
import shutil
import hashlib
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, field, asdict
from enum import Enum
from pathlib import Path
from datetime import datetime, date, timedelta, timezone
import logging
from collections import defaultdict, deque
import sqlite3
import pickle
import concurrent.futures
import asyncio
import time

# Local imports
from core.base_types import (
    MarketData, OrderFlowData, TradingSignal, TradeResult,
    ES_TICK_SIZE, ES_TICK_VALUE
)
from config.automation_config import get_automation_config

logger = logging.getLogger(__name__)

# === DATA COLLECTION ENUMS ===


class DataFormat(Enum):
    """Formats d'export des données"""
    JSON = "json"
    CSV = "csv"
    PARQUET = "parquet"
    PICKLE = "pickle"
    SQLITE = "sqlite"


class DataPeriod(Enum):
    """Périodes d'organisation des données"""
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"


class DataQuality(Enum):
    """Niveaux de qualité des données"""
    EXCELLENT = "excellent"    # 100% complete, validated
    GOOD = "good"             # >95% complete, minor issues
    ACCEPTABLE = "acceptable"  # >85% complete, usable
    POOR = "poor"             # <85% complete, quality issues
    CORRUPTED = "corrupted"   # Data integrity compromised

# === DATA ORGANIZATION STRUCTURES ===


@dataclass
class DataSummary:
    """Résumé d'un dataset"""
    period: str
    start_time: datetime
    end_time: datetime
    total_trades: int
    total_snapshots: int
    data_quality: DataQuality
    file_size_mb: float
    checksum: str
    ml_features_available: bool
    last_updated: datetime


@dataclass
class MLDataset:
    """Dataset formaté pour ML"""
    features: pd.DataFrame
    labels: pd.Series
    metadata: pd.DataFrame
    feature_names: List[str]
    quality_score: float
    train_test_split_ready: bool
    creation_timestamp: datetime


@dataclass
class DataIntegrityReport:
    """Rapport intégrité données"""
    timestamp: datetime
    files_checked: int
    corrupted_files: int
    missing_files: int
    checksum_errors: int
    total_trades_validated: int
    overall_health: str  # HEALTHY/WARNING/CRITICAL
    recommendations: List[str]

# === MAIN DATA COLLECTOR CLASS ===


class DataCollector:
    """
    COLLECTEUR DE DONNÉES MASTER

    Responsabilités :
    1. Collection snapshots depuis trade_snapshotter
    2. Organisation temporelle (daily/weekly/monthly)
    3. Validation qualité et intégrité
    4. Préparation datasets ML-ready
    5. Archivage intelligent et compression
    6. Analytics et features engineering
    """

    def __init__(self, config: Optional[Dict] = None):
        """Initialisation data collector"""
        self.config = config or get_automation_config()

        # Configuration paths
        self.base_path = Path("data/snapshots")
        self.daily_path = self.base_path / "daily"
        self.weekly_path = self.base_path / "weekly"
        self.monthly_path = self.base_path / "monthly"
        self.archive_path = self.base_path / "archive"
        self.ml_path = self.base_path / "ml_ready"

        # Création directories
        for path in [self.daily_path, self.weekly_path, self.monthly_path,
                     self.archive_path, self.ml_path]:
            path.mkdir(parents=True, exist_ok=True)

        # Session management
        self.current_session_snapshots: List[Dict] = []
        self.session_start_time = datetime.now(timezone.utc)
        self.session_metadata = {
            'session_id': f"data_collection_{self.session_start_time.strftime('%Y%m%d_%H%M%S')}",
            'start_time': self.session_start_time,
            'snapshots_collected': 0,
            'trades_completed': 0,
            'data_quality_issues': 0
        }

        # Statistics tracking
        self.collection_stats = {
            'snapshots_processed': 0,
            'avg_processing_time_ms': 0.0,
            'data_quality_distribution': defaultdict(int),
            'daily_trades_count': defaultdict(int),
            'ml_datasets_created': 0
        }

        # ML features configuration
        self.ml_feature_config = {
            'battle_navale_features': [
                'battle_navale_signal', 'battle_strength', 'confirmation_score',
                'signal_consistency', 'market_alignment'
            ],
            'market_features': [
                'atr_14', 'realized_volatility', 'trend_strength',
                'session_time_ratio', 'volume_relative'
            ],
            'execution_features': [
                'execution_time_ms', 'slippage_ticks', 'market_impact',
                'bid_ask_spread', 'fill_quality'
            ],
            'target_variables': [
                'trade_profitable', 'net_pnl', 'return_percent',
                'holding_time_minutes', 'risk_reward_achieved'
            ],
            'normalization': {
                'price_features': 'z_score',
                'volume_features': 'min_max',
                'time_features': 'standard'
            }
        }

        logger.info(f"DataCollector initialisé: {self.base_path}")

    # === SNAPSHOT COLLECTION ===

    def collect_trade_snapshot(self, snapshot: Dict[str, Any]) -> bool:
        """
        COLLECTION SNAPSHOT TRADING

        Collecte snapshot depuis trade_snapshotter et l'organise
        """
        start_time = time.perf_counter()

        try:
            # Validation snapshot
            if not self._validate_snapshot_structure(snapshot):
                logger.error("Snapshot structure invalide")
                return False

            # Enrichissement metadata
            enriched_snapshot = self._enrich_snapshot_metadata(snapshot)

            # Ajout à session courante
            self.current_session_snapshots.append(enriched_snapshot)

            # Sauvegarde immédiate si snapshot critique
            if enriched_snapshot.get('snapshot_type') == 'final_result':
                self._save_completed_trade(enriched_snapshot)

            # Update stats
            processing_time = (time.perf_counter() - start_time) * 1000
            self._update_collection_stats(processing_time)

            logger.debug(f"Snapshot collecté: {enriched_snapshot.get('trade_id', 'unknown')}")
            return True

        except Exception as e:
            logger.error(f"Erreur collection snapshot: {e}")
            return False

    def _validate_snapshot_structure(self, snapshot: Dict[str, Any]) -> bool:
        """Validation structure snapshot"""
        required_fields = ['timestamp', 'snapshot_type', 'trade_id']

        for field in required_fields:
            if field not in snapshot:
                logger.warning(f"Champ manquant dans snapshot: {field}")
                return False

        # Validation timestamp
        try:
            if isinstance(snapshot['timestamp'], str):
                datetime.fromisoformat(snapshot['timestamp'].replace('Z', '+00:00'))
        except (ValueError, TypeError):
            logger.warning("Format timestamp invalide")
            return False

        return True

    def _enrich_snapshot_metadata(self, snapshot: Dict[str, Any]) -> Dict[str, Any]:
        """Enrichissement snapshot avec metadata"""
        enriched = snapshot.copy()

        # Metadata collection
        enriched['collection_metadata'] = {
            'collection_timestamp': datetime.now(timezone.utc).isoformat(),
            'collector_session_id': self.session_metadata['session_id'],
            'data_quality': self._assess_snapshot_quality(snapshot),
            'ml_features_ready': self._check_ml_features_availability(snapshot),
            'checksum': self._calculate_snapshot_checksum(snapshot)
        }

        # Session tracking
        self.session_metadata['snapshots_collected'] += 1

        return enriched

    def _assess_snapshot_quality(self, snapshot: Dict[str, Any]) -> str:
        """Évaluation qualité snapshot"""
        score = 1.0

        # Check completeness
        expected_sections = ['market_snapshot', 'battle_navale_result']
        for section in expected_sections:
            if section not in snapshot:
                score -= 0.3
            elif not snapshot[section]:
                score -= 0.2

        # Check data types
        if 'market_snapshot' in snapshot:
            market_data = snapshot['market_snapshot']
            for key, value in market_data.items():
                if value is None:
                    score -= 0.1

        # Qualité basée sur score
        if score >= 0.9:
            return DataQuality.EXCELLENT.value
        elif score >= 0.75:
            return DataQuality.GOOD.value
        elif score >= 0.6:
            return DataQuality.ACCEPTABLE.value
        else:
            return DataQuality.POOR.value

    def _check_ml_features_availability(self, snapshot: Dict[str, Any]) -> bool:
        """Vérification disponibilité features ML"""
        required_sections = ['market_snapshot', 'battle_navale_result']

        for section in required_sections:
            if section not in snapshot or not snapshot[section]:
                return False

        # Check features spécifiques
        market_features = ['close', 'atr_14', 'trend_strength']
        battle_features = ['battle_navale_signal', 'battle_strength']

        market_data = snapshot.get('market_snapshot', {})
        battle_data = snapshot.get('battle_navale_result', {})

        for feature in market_features:
            if feature not in market_data or market_data[feature] is None:
                return False

        for feature in battle_features:
            if feature not in battle_data or battle_data[feature] is None:
                return False

        return True

    def _calculate_snapshot_checksum(self, snapshot: Dict[str, Any]) -> str:
        """Calcul checksum pour intégrité"""
        try:
            # Création string déterministe
            content = json.dumps(snapshot, sort_keys=True, separators=(',', ':'))
            return hashlib.md5(content.encode()).hexdigest()[:16]
        except Exception:
            return "checksum_error"

    def _save_completed_trade(self, snapshot: Dict[str, Any]):
        """Sauvegarde trade complété"""
        try:
            trade_id = snapshot.get('trade_id', 'unknown')
            timestamp = snapshot.get('timestamp', datetime.now(timezone.utc).isoformat())

            # Parse timestamp pour organisation
            if isinstance(timestamp, str):
                dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            else:
                dt = timestamp

            # Fichier daily
            daily_file = self.daily_path / f"trades_{dt.date().isoformat()}.jsonl"

            # Append au fichier daily
            with open(daily_file, 'a', encoding='utf-8') as f:
                json.dump(snapshot, f, separators=(',', ':'))
                f.write('\n')

            # Update compteur trades
            self.session_metadata['trades_completed'] += 1
            self.collection_stats['daily_trades_count'][dt.date().isoformat()] += 1

            logger.debug(f"Trade sauvegardé: {trade_id}")

        except Exception as e:
            logger.error(f"Erreur sauvegarde trade: {e}")

    def _update_collection_stats(self, processing_time_ms: float):
        """Mise à jour statistiques collection"""
        self.collection_stats['snapshots_processed'] += 1

        # Moyenne mobile processing time
        current_avg = self.collection_stats['avg_processing_time_ms']
        count = self.collection_stats['snapshots_processed']

        self.collection_stats['avg_processing_time_ms'] = (
            (current_avg * (count - 1) + processing_time_ms) / count
        )

    # === DATA ORGANIZATION ===

    def organize_daily_data(self, target_date: date) -> bool:
        """
        ORGANISATION DONNÉES QUOTIDIENNES

        Organise et valide données d'une journée
        """
        try:
            logger.info(f"Organisation données {target_date}")

            # Collection snapshots de la journée
            daily_snapshots = self._collect_daily_snapshots(target_date)

            if not daily_snapshots:
                logger.warning(f"Aucun snapshot pour {target_date}")
                return True

            # Organisation par trade
            trades_data = self._organize_snapshots_by_trade(daily_snapshots)

            # Validation et nettoyage
            validated_trades = self._validate_trades_data(trades_data)

            # Création summary
            daily_summary = self._create_daily_summary(target_date, validated_trades)

            # Sauvegarde summary
            self._save_daily_summary(target_date, daily_summary)

            # Préparation données ML si suffisamment de trades
            if len(validated_trades) >= 10:
                self._prepare_daily_ml_features(target_date, validated_trades)

            logger.info(f"✅ Organisation {target_date}: {len(validated_trades)} trades validés")
            return True

        except Exception as e:
            logger.error(f"Erreur organisation {target_date}: {e}")
            return False

    def _collect_daily_snapshots(self, target_date: date) -> List[Dict]:
        """Collection snapshots d'une journée"""
        daily_file = self.daily_path / f"trades_{target_date.isoformat()}.jsonl"
        snapshots = []

        if not daily_file.exists():
            return snapshots

        try:
            with open(daily_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        snapshot = json.loads(line)
                        snapshots.append(snapshot)

            logger.debug(f"Collecté {len(snapshots)} snapshots pour {target_date}")

        except Exception as e:
            logger.error(f"Erreur lecture snapshots {target_date}: {e}")

        return snapshots

    def _organize_snapshots_by_trade(self, snapshots: List[Dict]) -> Dict[str, List[Dict]]:
        """Organisation snapshots par trade_id"""
        trades_data = defaultdict(list)

        for snapshot in snapshots:
            trade_id = snapshot.get('trade_id', 'unknown')
            trades_data[trade_id].append(snapshot)

        # Tri snapshots par timestamp dans chaque trade
        for trade_id, trade_snapshots in trades_data.items():
            trades_data[trade_id] = sorted(
                trade_snapshots,
                key=lambda s: s.get('timestamp', '')
            )

        return dict(trades_data)

    def _validate_trades_data(self, trades_data: Dict[str, List[Dict]]) -> Dict[str, List[Dict]]:
        """Validation et nettoyage données trades"""
        validated_trades = {}

        for trade_id, snapshots in trades_data.items():
            # Validation trade complet
            if self._is_complete_trade(snapshots):
                validated_trades[trade_id] = snapshots
            else:
                logger.warning(f"Trade incomplet ignoré: {trade_id}")

        return validated_trades

    def _is_complete_trade(self, snapshots: List[Dict]) -> bool:
        """Vérification trade complet avec tous les snapshots"""
        snapshot_types = [s.get('snapshot_type') for s in snapshots]

        # Au minimum: decision et final_result
        required_types = ['decision', 'final_result']

        for req_type in required_types:
            if req_type not in snapshot_types:
                return False

        return True

    def _create_daily_summary(self, target_date: date, trades_data: Dict) -> DataSummary:
        """Création summary quotidien"""
        total_trades = len(trades_data)
        total_snapshots = sum(len(snapshots) for snapshots in trades_data.values())

        # Calcul qualité globale
        quality_scores = []
        ml_features_count = 0

        for trade_snapshots in trades_data.values():
            for snapshot in trade_snapshots:
                quality = snapshot.get('collection_metadata', {}).get('data_quality', 'acceptable')
                if quality == 'excellent':
                    quality_scores.append(1.0)
                elif quality == 'good':
                    quality_scores.append(0.8)
                elif quality == 'acceptable':
                    quality_scores.append(0.6)
                else:
                    quality_scores.append(0.3)

                if snapshot.get('collection_metadata', {}).get('ml_features_ready', False):
                    ml_features_count += 1

        # Détermination qualité globale
        avg_quality = np.mean(quality_scores) if quality_scores else 0.5
        if avg_quality >= 0.9:
            overall_quality = DataQuality.EXCELLENT
        elif avg_quality >= 0.75:
            overall_quality = DataQuality.GOOD
        elif avg_quality >= 0.6:
            overall_quality = DataQuality.ACCEPTABLE
        else:
            overall_quality = DataQuality.POOR

        return DataSummary(
            period=f"daily_{target_date.isoformat()}",
            start_time=datetime.combine(target_date, datetime.min.time()),
            end_time=datetime.combine(target_date, datetime.max.time()),
            total_trades=total_trades,
            total_snapshots=total_snapshots,
            data_quality=overall_quality,
            file_size_mb=0.0,  # Sera calculé lors sauvegarde
            checksum="",  # Sera calculé lors sauvegarde
            ml_features_available=(ml_features_count > 0),
            last_updated=datetime.now(timezone.utc)
        )

    def _save_daily_summary(self, target_date: date, summary: DataSummary):
        """Sauvegarde summary quotidien"""
        try:
            summary_file = self.daily_path / f"summary_{target_date.isoformat()}.json"

            with open(summary_file, 'w', encoding='utf-8') as f:
                json.dump(asdict(summary), f, indent=2, default=str)

            logger.debug(f"Summary sauvegardé: {target_date}")

        except Exception as e:
            logger.error(f"Erreur sauvegarde summary {target_date}: {e}")

    def _prepare_daily_ml_features(self, target_date: date, trades_data: Dict):
        """Préparation features ML quotidiennes"""
        try:
            # Extraction features de base
            features_data = []

            for trade_id, snapshots in trades_data.items():
                trade_features = self._extract_trade_ml_features(trade_id, snapshots)
                if trade_features:
                    features_data.append(trade_features)

            if features_data:
                # Création DataFrame
                features_df = pd.DataFrame(features_data)

                # Sauvegarde features
                features_file = self.ml_path / f"features_{target_date.isoformat()}.parquet"
                features_df.to_parquet(features_file, index=False)

                logger.debug(
                    f"Features ML sauvegardées: {target_date} ({
                        len(features_data)} trades)")

        except Exception as e:
            logger.error(f"Erreur préparation ML features {target_date}: {e}")

    def _extract_trade_ml_features(self, trade_id: str, snapshots: List[Dict]) -> Optional[Dict]:
        """Extraction features ML d'un trade"""
        try:
            # Trouver snapshots clés
            decision_snapshot = None
            result_snapshot = None

            for snapshot in snapshots:
                if snapshot.get('snapshot_type') == 'decision':
                    decision_snapshot = snapshot
                elif snapshot.get('snapshot_type') == 'final_result':
                    result_snapshot = snapshot

            if not decision_snapshot or not result_snapshot:
                return None

            # Features market
            market_data = decision_snapshot.get('market_snapshot', {})
            battle_data = decision_snapshot.get('battle_navale_result', {})
            trade_result = result_snapshot.get('trade_result', {})

            features = {
                'trade_id': trade_id,
                'timestamp': decision_snapshot.get('timestamp'),

                # Market features
                'close_price': market_data.get('close'),
                'atr_14': market_data.get('atr_14'),
                'trend_strength': market_data.get('trend_strength'),
                'volume': market_data.get('volume', 0),

                # Battle Navale features
                'battle_signal': battle_data.get('battle_navale_signal'),
                'battle_strength': battle_data.get('battle_strength'),

                # Target variables
                'net_pnl': trade_result.get('net_pnl', 0),
                'profitable': trade_result.get('net_pnl', 0) > 0,
                'return_percent': trade_result.get('return_percent', 0),
                'holding_time_minutes': trade_result.get('holding_time_minutes', 0)
            }

            # Validation features
            for key, value in features.items():
                if value is None and key not in ['trade_id', 'timestamp']:
                    return None

            return features

        except Exception as e:
            logger.error(f"Erreur extraction features trade {trade_id}: {e}")
            return None

    # === ML DATASET PREPARATION ===

    def export_ml_training_dataset(self,
                                   start_date: date,
                                   end_date: date,
                                   min_trades: int = 50) -> Optional[MLDataset]:
        """
        EXPORT DATASET ML TRAINING

        Prépare dataset complet pour training ML
        """
        try:
            logger.info(f"Préparation dataset ML: {start_date} à {end_date}")

            # Collection données période
            all_trades_data = self._collect_period_data(start_date, end_date)

            if len(all_trades_data) < min_trades:
                logger.warning(f"Pas assez de trades: {len(all_trades_data)}/{min_trades}")
                return None

            # Préparation features et labels
            features_df, labels_series, metadata_df = self._prepare_ml_features_and_labels(
                all_trades_data)

            if features_df.empty:
                logger.error("Aucune feature préparée")
                return None

            # Validation dataset
            quality_score = self._validate_ml_dataset_quality(features_df, labels_series)

            # Création dataset ML
            ml_dataset = MLDataset(
                features=features_df,
                labels=labels_series,
                metadata=metadata_df,
                feature_names=list(features_df.columns),
                quality_score=quality_score,
                train_test_split_ready=True,
                creation_timestamp=datetime.now(timezone.utc)
            )

            # Sauvegarde dataset
            self._save_ml_dataset(ml_dataset, start_date, end_date)

            logger.info(
                f"Dataset ML créé: {len(features_df)} samples, {len(features_df.columns)} features")
            return ml_dataset

        except Exception as e:
            logger.error(f"Erreur export ML dataset: {e}")
            return None

    def _collect_period_data(self, start_date: date, end_date: date) -> Dict[str, List[Dict]]:
        """Collection données sur une période"""
        all_trades = {}

        current_date = start_date
        while current_date <= end_date:
            daily_file = self.daily_path / f"trades_{current_date.isoformat()}.jsonl"

            if daily_file.exists():
                daily_snapshots = self._collect_daily_snapshots(current_date)
                daily_trades = self._organize_snapshots_by_trade(daily_snapshots)
                all_trades.update(daily_trades)

            current_date += timedelta(days=1)

        return all_trades

    def _prepare_ml_features_and_labels(
            self, trades_data: Dict) -> Tuple[pd.DataFrame, pd.Series, pd.DataFrame]:
        """Préparation features et labels pour ML"""
        features_list = []
        labels_list = []
        metadata_list = []

        for trade_id, trade_snapshots in trades_data.items():
            # Trouver snapshots décision et résultat
            decision_snapshot = None
            result_snapshot = None

            for snapshot in trade_snapshots:
                if snapshot.get('snapshot_type') == 'decision':
                    decision_snapshot = snapshot
                elif snapshot.get('snapshot_type') == 'final_result':
                    result_snapshot = snapshot

            if not decision_snapshot or not result_snapshot:
                continue

            # Extraction features
            trade_features = self._extract_comprehensive_features(
                decision_snapshot, result_snapshot)
            if trade_features is None:
                continue

            # Labels (profitable ou non)
            trade_result = result_snapshot.get('trade_result', {})
            profitable = trade_result.get('net_pnl', 0) > 0

            features_list.append(trade_features)
            labels_list.append(profitable)
            metadata_list.append({
                'trade_id': trade_id,
                'timestamp': decision_snapshot.get('timestamp'),
                'net_pnl': trade_result.get('net_pnl', 0),
                'return_percent': trade_result.get('return_percent', 0)
            })

        # Conversion en DataFrames
        features_df = pd.DataFrame(features_list)
        labels_series = pd.Series(labels_list, name='profitable')
        metadata_df = pd.DataFrame(metadata_list)

        return features_df, labels_series, metadata_df

    def _extract_comprehensive_features(
            self, decision_snapshot: Dict, result_snapshot: Dict) -> Optional[Dict]:
        """Extraction features complètes pour ML"""
        try:
            market_data = decision_snapshot.get('market_snapshot', {})
            battle_data = decision_snapshot.get('battle_navale_result', {})
            trade_result = result_snapshot.get('trade_result', {})

            features = {}

            # Battle Navale features
            for feature in self.ml_feature_config['battle_navale_features']:
                features[f'bn_{feature}'] = battle_data.get(feature)

            # Market features
            for feature in self.ml_feature_config['market_features']:
                features[f'market_{feature}'] = market_data.get(feature)

            # Features calculées
            features['price_momentum'] = self._calculate_price_momentum(market_data)
            features['volatility_ratio'] = self._calculate_volatility_ratio(market_data)
            features['signal_strength'] = self._calculate_signal_strength(battle_data)

            # Time features
            timestamp = decision_snapshot.get('timestamp')
            if timestamp:
                dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                features['hour'] = dt.hour
                features['day_of_week'] = dt.weekday()
                features['is_market_hours'] = 9 <= dt.hour <= 16  # Simplifié

            # Validation features (pas de None)
            for key, value in features.items():
                if value is None:
                    return None

            return features

        except Exception as e:
            logger.error(f"Erreur extraction features complètes: {e}")
            return None

    def _calculate_price_momentum(self, market_data: Dict) -> float:
        """Calcul momentum prix simplifié"""
        try:
            close = market_data.get('close', 0)
            high = market_data.get('high', close)
            low = market_data.get('low', close)

            if high == low:
                return 0.0

            return (close - low) / (high - low) - 0.5  # Centré sur 0

        except Exception:
            return 0.0

    def _calculate_volatility_ratio(self, market_data: Dict) -> float:
        """Calcul ratio volatilité"""
        try:
            atr = market_data.get('atr_14', 1.0)
            close = market_data.get('close', 4500.0)

            return atr / close if close > 0 else 0.0

        except Exception:
            return 0.0

    def _calculate_signal_strength(self, battle_data: Dict) -> float:
        """Calcul force signal globale"""
        try:
            signal = battle_data.get('battle_navale_signal', 0)
            strength = battle_data.get('battle_strength', 0)

            return abs(signal) * strength

        except Exception:
            return 0.0

    def _validate_ml_dataset_quality(self, features_df: pd.DataFrame,
                                     labels_series: pd.Series) -> float:
        """Validation qualité dataset ML"""
        try:
            quality_score = 1.0

            # Check completeness
            missing_ratio = features_df.isnull().sum().sum() / (len(features_df) * len(features_df.columns))
            quality_score -= missing_ratio * 0.5

            # Check balance labels
            label_balance = min(labels_series.sum(), len(labels_series) -
                                labels_series.sum()) / len(labels_series)
            if label_balance < 0.1:  # Très déséquilibré
                quality_score -= 0.3
            elif label_balance < 0.2:
                quality_score -= 0.1

            # Check features variance
            low_variance_features = (features_df.var() < 0.01).sum()
            quality_score -= (low_variance_features / len(features_df.columns)) * 0.2

            return max(0.0, quality_score)

        except Exception as e:
            logger.error(f"Erreur validation qualité dataset: {e}")
            return 0.5

    def _save_ml_dataset(self, ml_dataset: MLDataset, start_date: date, end_date: date):
        """Sauvegarde dataset ML"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

            # Nom fichier
            dataset_name = f"ml_dataset_{start_date}_{end_date}_{timestamp}"

            # Sauvegarde features et labels
            features_file = self.ml_path / f"{dataset_name}_features.parquet"
            labels_file = self.ml_path / f"{dataset_name}_labels.parquet"
            metadata_file = self.ml_path / f"{dataset_name}_metadata.json"

            ml_dataset.features.to_parquet(features_file, index=False)
            ml_dataset.labels.to_frame().to_parquet(labels_file, index=False)

            # Metadata
            metadata = {
                'creation_timestamp': ml_dataset.creation_timestamp.isoformat(),
                'features_count': len(ml_dataset.features.columns),
                'samples_count': len(ml_dataset.features),
                'quality_score': ml_dataset.quality_score,
                'feature_names': ml_dataset.feature_names,
                'train_test_split_ready': ml_dataset.train_test_split_ready,
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat()
            }

            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)

            self.collection_stats['ml_datasets_created'] += 1
            logger.info(f"Dataset ML sauvegardé: {dataset_name}")

        except Exception as e:
            logger.error(f"Erreur sauvegarde dataset ML: {e}")

    # === STATUS & ANALYTICS ===

    def get_collection_statistics(self) -> Dict[str, Any]:
        """Statistiques complètes collection"""
        try:
            return {
                'session_metadata': self.session_metadata.copy(),
                'collection_stats': self.collection_stats.copy(),
                'storage_usage': self._calculate_storage_usage(),
                'directory_info': self._get_directory_info(),
                'data_quality_summary': self._get_data_quality_summary(),
                'recent_activity': self._get_recent_activity_summary()
            }

        except Exception as e:
            logger.error(f"Erreur statistiques collection: {e}")
            return {'error': str(e)}

    def _get_directory_info(self) -> Dict[str, Any]:
        """Informations directories"""
        def count_files(path: Path) -> Dict[str, int]:
            if not path.exists():
                return {'total_files': 0, 'daily_files': 0, 'summary_files': 0}

            files = list(path.rglob("*"))
            daily_files = len([f for f in files if f.name.startswith('trades_')])
            summary_files = len([f for f in files if f.name.startswith('summary_')])

            return {
                'total_files': len(files),
                'daily_files': daily_files,
                'summary_files': summary_files
            }

        return {
            'daily': count_files(self.daily_path),
            'weekly': count_files(self.weekly_path),
            'monthly': count_files(self.monthly_path),
            'archive': count_files(self.archive_path),
            'ml_ready': count_files(self.ml_path)
        }

    def _get_data_quality_summary(self) -> Dict[str, Any]:
        """Résumé qualité données"""
        if not self.collection_stats['data_quality_distribution']:
            return {'overall_quality': 'unknown', 'distribution': {}}

        total = sum(self.collection_stats['data_quality_distribution'].values())
        distribution = {
            quality: (count / total) * 100
            for quality, count in self.collection_stats['data_quality_distribution'].items()
        }

        # Qualité globale
        if distribution.get('excellent', 0) > 50:
            overall = 'excellent'
        elif distribution.get('good', 0) + distribution.get('excellent', 0) > 70:
            overall = 'good'
        elif distribution.get('poor', 0) < 20:
            overall = 'acceptable'
        else:
            overall = 'poor'

        return {
            'overall_quality': overall,
            'distribution': distribution
        }

    def _get_recent_activity_summary(self) -> Dict[str, Any]:
        """Résumé activité récente"""
        return {
            'current_session': {
                'snapshots_in_memory': len(self.current_session_snapshots),
                'session_duration_minutes': (
                    datetime.now(timezone.utc) - self.session_start_time
                ).total_seconds() / 60,
                'avg_processing_time_ms': self.collection_stats['avg_processing_time_ms']
            },
            'recent_performance': {
                'snapshots_per_minute': self._calculate_recent_throughput(),
                'ml_datasets_created': self.collection_stats['ml_datasets_created']
            }
        }

    def _calculate_recent_throughput(self) -> float:
        """Calcul throughput récent"""
        try:
            session_duration_minutes = (
                datetime.now(timezone.utc) - self.session_start_time
            ).total_seconds() / 60

            if session_duration_minutes > 0:
                return self.collection_stats['snapshots_processed'] / session_duration_minutes

            return 0.0

        except Exception:
            return 0.0

    def _calculate_storage_usage(self) -> Dict[str, float]:
        """Calcul usage stockage"""
        def get_directory_size(path: Path) -> float:
            total_size = 0
            if path.exists():
                for file_path in path.rglob("*"):
                    if file_path.is_file():
                        total_size += file_path.stat().st_size
            return total_size / (1024 * 1024)  # MB

        return {
            'daily_mb': get_directory_size(self.daily_path),
            'weekly_mb': get_directory_size(self.weekly_path),
            'monthly_mb': get_directory_size(self.monthly_path),
            'archive_mb': get_directory_size(self.archive_path),
            'ml_mb': get_directory_size(self.ml_path),
            'total_mb': get_directory_size(self.base_path)
        }

# === FACTORY FUNCTIONS ===


def create_data_collector(config: Optional[Dict] = None) -> DataCollector:
    """Factory function pour data collector"""
    return DataCollector(config)


def export_ml_dataset(start_date: date, end_date: date, output_path: Optional[Path] = None) -> bool:
    """Helper function export dataset ML"""
    collector = create_data_collector()
    dataset = collector.export_ml_training_dataset(start_date, end_date)

    if dataset and output_path:
        try:
            with open(output_path, 'wb') as f:
                pickle.dump(dataset, f)
            return True
        except Exception as e:
            logger.error(f"Erreur sauvegarde dataset: {e}")

    return False

# === TESTING ===


def test_data_collector():
    """Test data collector"""
    logger.info("🗄️ TEST DATA COLLECTOR")
    print("=" * 35)

    collector = create_data_collector()

    # Test collection snapshot
    test_snapshot = {
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'snapshot_type': 'decision',
        'trade_id': 'TEST_TRADE_001',
        'market_snapshot': {
            'close': 4500.0,
            'atr_14': 15.5,
            'trend_strength': 0.7
        },
        'battle_navale_result': {
            'battle_navale_signal': 0.8,
            'battle_strength': 0.6
        }
    }

    success = collector.collect_trade_snapshot(test_snapshot)
    logger.info("Collection snapshot: {success}")

    # Test organization
    today = datetime.now().date()
    org_success = collector.organize_daily_data(today)
    logger.info("Organisation daily: {org_success}")

    # Test statistics
    stats = collector.get_collection_statistics()
    logger.info("Stats: {stats['collection_stats']['snapshots_processed']} snapshots")

    logger.info("🎯 Data collector test COMPLETED")
    return True


if __name__ == "__main__":
    test_data_collector()
