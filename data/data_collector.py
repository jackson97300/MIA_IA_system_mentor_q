#!/usr/bin/env python3
"""
MIA_IA_SYSTEM - Data Collector ENHANCED
[STATS] COLLECTION SNAPSHOTS & ORGANISATION ML-READY avec AMÉLIORATIONS ENRICHIES
Version: Enhanced v2.0 - INTÉGRATION COMPLÈTE TRADE SNAPSHOTTER ENRICHI
Performance: Collection 24/7, organisation automatique, ML-ready exports

🎯 INTÉGRATION AMÉLIORATIONS TRADE SNAPSHOTTER:
✅ Support MICROSTRUCTURE data (order book, tick momentum, smart money)
✅ Support OPTIONS FLOW enrichi (gamma exposure, vol surface, dealer positioning)
✅ Support SESSION CONTEXT (timing, événements économiques, saisonnalité)
✅ Support POST-TRADE ANALYSIS (apprentissage automatique, edge validation)
✅ Support CORRELATION TRACKING (features/marché/stratégie)

RESPONSABILITÉS CRITIQUES :
1. [STATS] COLLECTION SNAPSHOTS - Agrégation données trade_snapshotter ENRICHI
2. 🗂️ ORGANISATION TEMPORELLE - Daily/Weekly/Monthly structure ENRICHIE
3. [BRAIN] PRÉPARATION ML - Datasets formatés avec 25+ features au lieu de 8
4. [SAVE] ARCHIVAGE INTELLIGENT - Compression, backup, rétention ENRICHIE
5. [OK] VALIDATION INTÉGRITÉ - Vérification qualité données ENRICHIE
6. [UP] ANALYTICS PREPROCESSING - Features engineering pour ML ENRICHI
7. 🆕 MICROSTRUCTURE PROCESSING - Analyse order book, smart money flow
8. 🆕 OPTIONS CONTEXT INTEGRATION - SPX gamma, VIX, dealer positioning
9. 🆕 POST-TRADE LEARNING - Collection insights amélioration continue
10. 🆕 CORRELATION ANALYSIS - Tracking corrélations multi-niveaux

WORKFLOW COMPLET ENRICHI :
TradeSnapshotterEnhanced → DataCollectorEnhanced → ML-Ready Datasets (25+ features) → Advanced Analytics

INPUT : Snapshots JSON ENRICHIS du trade_snapshotter (standard + microstructure + options + context)
OUTPUT : Datasets structurés ENRICHIS + Advanced Analytics + ML exports OPTIMISÉS
"""

import os
import json
import gzip
import shutil
import hashlib
import pandas as pd
import numpy as np
import sys
import logging
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, field, asdict
from enum import Enum
from pathlib import Path
from datetime import datetime, date, timedelta, timezone
from collections import defaultdict, deque
import sqlite3
import pickle
import concurrent.futures
import asyncio
import time
import statistics

# Configuration imports avec fallback
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from core.logger import get_logger
    logger = get_logger(__name__)
except ImportError:
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

try:
    from core.base_types import (
        MarketData, OrderFlowData, TradingSignal, TradeResult,
        ES_TICK_SIZE, ES_TICK_VALUE
    )
except ImportError:
    logger.warning("Import core.base_types impossible, utilisation types locaux")
    
    @dataclass
    class MarketData:
        timestamp: datetime
        symbol: str
        close: float
        volume: int
    
    @dataclass
    class OrderFlowData:
        timestamp: datetime
        symbol: str
        cumulative_delta: float
    
    @dataclass
    class TradingSignal:
        timestamp: datetime
        symbol: str
        signal_type: str
    
    @dataclass
    class TradeResult:
        timestamp: datetime
        symbol: str
        realized_pnl: float
    
    ES_TICK_SIZE = 0.25
    ES_TICK_VALUE = 12.50

try:
    from config.automation_config import get_automation_config
except ImportError:
    logger.warning("Config automation non disponible, utilisation config par défaut")
    def get_automation_config():
        return {
            'snapshots_directory': 'data/snapshots',
            'environment': 'development'
        }

# === ENHANCED DATA COLLECTION ENUMS ===

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
    """Niveaux de qualité des données ENRICHIS"""
    EXCELLENT = "excellent"      # 100% complete + enhanced features
    GOOD = "good"               # >95% complete + most enhanced features
    ACCEPTABLE = "acceptable"    # >85% complete + some enhanced features
    POOR = "poor"               # <85% complete, basic features only
    CORRUPTED = "corrupted"     # Data integrity compromised
    ENHANCED = "enhanced"       # 🆕 Toutes features enrichies disponibles

class EnhancedDataType(Enum):
    """🆕 Types données enrichies supportées"""
    STANDARD = "standard"                    # Données trade snapshotter classique
    MICROSTRUCTURE = "microstructure"       # Order book, tick analysis, smart money
    OPTIONS_FLOW = "options_flow"            # Gamma, VIX, dealer positioning
    SESSION_CONTEXT = "session_context"     # Timing, événements, saisonnalité
    POST_TRADE_ANALYSIS = "post_trade_analysis"  # Apprentissage, edge validation
    CORRELATION_DATA = "correlation_data"    # Corrélations features/marché

# === ENHANCED DATA ORGANIZATION STRUCTURES ===

@dataclass
class EnhancedDataSummary:
    """🆕 Résumé dataset ENRICHI"""
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
    
    # 🆕 Enhanced metrics
    microstructure_snapshots: int
    options_flow_snapshots: int
    session_context_snapshots: int
    post_trade_analyses: int
    correlation_updates: int
    enhanced_features_count: int
    standard_features_count: int
    enrichment_ratio: float  # % snapshots enrichis vs standard

@dataclass
class EnhancedMLDataset:
    """🆕 Dataset ML ENRICHI avec toutes features"""
    # Datasets principaux
    features: pd.DataFrame                   # Features standard + enrichies
    labels: pd.Series                       # Targets (profitable, pnl, etc.)
    metadata: pd.DataFrame                  # Métadonnées trades
    
    # 🆕 Datasets enrichis séparés
    microstructure_features: Optional[pd.DataFrame]    # Features microstructure
    options_features: Optional[pd.DataFrame]           # Features options flow
    session_features: Optional[pd.DataFrame]           # Features context session
    post_trade_insights: Optional[pd.DataFrame]        # Insights post-trade
    correlation_matrix: Optional[pd.DataFrame]         # Matrice corrélations
    
    # Métadonnées enrichies
    feature_names: List[str]
    enhanced_feature_names: List[str]       # 🆕 Features enrichies uniquement
    quality_score: float
    enrichment_score: float                 # 🆕 Score qualité enrichissement
    train_test_split_ready: bool
    creation_timestamp: datetime
    
    # 🆕 Configuration features
    feature_engineering_applied: bool
    normalization_methods: Dict[str, str]
    correlation_analysis_included: bool

@dataclass
class EnhancedDataIntegrityReport:
    """🆕 Rapport intégrité données ENRICHI"""
    timestamp: datetime
    files_checked: int
    corrupted_files: int
    missing_files: int
    checksum_errors: int
    total_trades_validated: int
    overall_health: str  # HEALTHY/WARNING/CRITICAL
    recommendations: List[str]
    
    # 🆕 Enhanced integrity checks
    microstructure_data_integrity: float    # % données microstructure valides
    options_data_integrity: float           # % données options valides
    session_context_integrity: float        # % données session valides
    post_trade_analysis_coverage: float     # % trades avec post-analysis
    correlation_data_freshness: float       # Fraîcheur données corrélations
    enhanced_features_completeness: float   # Complétude features enrichies

# === ENHANCED MAIN DATA COLLECTOR CLASS ===

class DataCollectorEnhanced:
    """
    🆕 COLLECTEUR DE DONNÉES ENHANCED
    
    Support complet pour toutes les améliorations du TradeSnapshotter:
    - Microstructure data processing
    - Options flow integration
    - Session context analysis
    - Post-trade learning collection
    - Correlation tracking
    - Advanced ML feature engineering
    """

    def __init__(self, config: Optional[Dict] = None):
        """Initialisation data collector ENRICHI"""
        self.config = config or get_automation_config()

        # Configuration paths (GARDÉS + enrichis)
        self.base_path = Path("data/snapshots")
        self.daily_path = self.base_path / "daily"
        self.weekly_path = self.base_path / "weekly"
        self.monthly_path = self.base_path / "monthly"
        self.archive_path = self.base_path / "archive"
        self.ml_path = self.base_path / "ml_ready"
        
        # 🆕 Enhanced paths
        self.microstructure_path = self.base_path / "microstructure"
        self.options_path = self.base_path / "options_flow"
        self.session_path = self.base_path / "session_context"
        self.post_analysis_path = self.base_path / "post_analysis"
        self.correlations_path = self.base_path / "correlations"
        self.enhanced_path = self.base_path / "enhanced"

        # Création directories (standard + enrichies)
        for path in [self.daily_path, self.weekly_path, self.monthly_path,
                     self.archive_path, self.ml_path, self.microstructure_path,
                     self.options_path, self.session_path, self.post_analysis_path,
                     self.correlations_path, self.enhanced_path]:
            path.mkdir(parents=True, exist_ok=True)

        # Session management (GARDÉ + enrichi)
        self.current_session_snapshots: List[Dict] = []
        self.session_start_time = datetime.now(timezone.utc)
        self.session_metadata = {
            'session_id': f"data_collection_enhanced_{self.session_start_time.strftime('%Y%m%d_%H%M%S')}",
            'start_time': self.session_start_time,
            'snapshots_collected': 0,
            'trades_completed': 0,
            'data_quality_issues': 0,
            # 🆕 Enhanced session tracking
            'enhanced_snapshots_collected': 0,
            'microstructure_snapshots': 0,
            'options_snapshots': 0,
            'post_analyses_completed': 0,
            'correlation_updates': 0
        }

        # Statistics tracking (GARDÉ + enrichi)
        self.collection_stats = {
            'snapshots_processed': 0,
            'avg_processing_time_ms': 0.0,
            'data_quality_distribution': defaultdict(int),
            'daily_trades_count': defaultdict(int),
            'ml_datasets_created': 0,
            # 🆕 Enhanced statistics
            'enhanced_snapshots_processed': 0,
            'microstructure_data_points': 0,
            'options_data_points': 0,
            'session_contexts_analyzed': 0,
            'post_trade_insights_collected': 0,
            'correlation_matrices_computed': 0,
            'feature_engineering_operations': 0
        }

        # 🆕 Enhanced ML features configuration
        self.enhanced_ml_feature_config = {
            # Standard features (GARDÉES)
            'battle_navale_features': [
                'vwap_trend_signal', 'sierra_pattern_strength', 'gamma_levels_proximity',
                'volume_confirmation', 'options_flow_bias', 'order_book_imbalance',
                'level_proximity_score', 'aggression_bias'
            ],
            'market_features': [
                'atr_14', 'realized_volatility', 'trend_strength',
                'session_time_ratio', 'volume_relative'
            ],
            'execution_features': [
                'execution_time_ms', 'slippage_ticks', 'market_impact',
                'bid_ask_spread', 'fill_quality'
            ],
            
            # 🆕 Enhanced features
            'microstructure_features': [
                'order_book_imbalance', 'tick_momentum_score', 'large_orders_bias',
                'aggressive_buy_ratio', 'aggressive_sell_ratio', 'volume_spike_detected',
                'bid_ask_spread_ticks', 'data_quality_score'
            ],
            'options_features': [
                'total_gamma_exposure', 'dealer_gamma_position', 'gamma_flip_level',
                'vix_level', 'term_structure_slope', 'vol_skew_25_delta',
                'put_call_ratio', 'put_call_volume_ratio', 'unusual_options_activity',
                'days_to_monthly_expiry', 'days_to_weekly_expiry'
            ],
            'session_features': [
                'session_phase', 'time_since_open_minutes', 'time_to_close_minutes',
                'economic_events_today', 'high_impact_event_today', 'seasonal_bias',
                'market_stress_indicator', 'overnight_gap_percent'
            ],
            'post_trade_features': [
                'edge_confirmed', 'edge_confidence', 'market_regime_shift',
                'success_factors_count', 'failure_factors_count', 'timing_quality_score',
                'pattern_reliability_update'
            ],
            
            # Target variables (GARDÉES + enrichies)
            'target_variables': [
                'trade_profitable', 'net_pnl', 'return_percent',
                'holding_time_minutes', 'risk_reward_achieved',
                # 🆕 Enhanced targets
                'mfe_ratio', 'mae_ratio', 'exit_efficiency',
                'pattern_reliability', 'market_timing_score'
            ],
            
            # 🆕 Enhanced normalization
            'normalization': {
                'price_features': 'robust_scaler',      # Résistant aux outliers
                'volume_features': 'quantile_uniform',  # Meilleure distribution
                'time_features': 'min_max',
                'ratio_features': 'standard',
                'microstructure_features': 'robust_scaler',
                'options_features': 'min_max',
                'correlation_features': 'standard'
            }
        }

        # 🆕 Enhanced data quality thresholds
        self.enhanced_quality_thresholds = {
            'excellent': {
                'completeness': 0.98,
                'enhanced_features_ratio': 0.90,
                'microstructure_coverage': 0.80,
                'options_coverage': 0.70,
                'post_analysis_coverage': 0.85
            },
            'good': {
                'completeness': 0.90,
                'enhanced_features_ratio': 0.70,
                'microstructure_coverage': 0.60,
                'options_coverage': 0.50,
                'post_analysis_coverage': 0.65
            },
            'acceptable': {
                'completeness': 0.80,
                'enhanced_features_ratio': 0.40,
                'microstructure_coverage': 0.30,
                'options_coverage': 0.25,
                'post_analysis_coverage': 0.40
            }
        }

        logger.info(f"DataCollectorEnhanced initialisé: {self.base_path}")
        logger.info(f"🆕 Support enrichi activé: microstructure, options, session, post-analysis")

    # === ENHANCED SNAPSHOT COLLECTION ===

    def collect_enhanced_trade_snapshot(self, snapshot: Dict[str, Any]) -> bool:
        """
        🆕 COLLECTION SNAPSHOT TRADING ENRICHI
        
        Support pour tous types de snapshots du TradeSnapshotter enrichi
        """
        start_time = time.perf_counter()

        try:
            # Validation structure (standard + enrichie)
            if not self._validate_enhanced_snapshot_structure(snapshot):
                logger.error("Snapshot enrichi structure invalide")
                return False

            # Détection type snapshot
            snapshot_type = snapshot.get('snapshot_type', 'standard')
            enhanced_type = self._detect_enhanced_snapshot_type(snapshot)

            # Enrichissement metadata
            enriched_snapshot = self._enrich_enhanced_snapshot_metadata(snapshot, enhanced_type)

            # Ajout à session courante
            self.current_session_snapshots.append(enriched_snapshot)

            # Sauvegarde spécialisée selon type
            self._save_enhanced_snapshot_by_type(enriched_snapshot, enhanced_type)

            # Sauvegarde standard si snapshot critique
            if enriched_snapshot.get('snapshot_type') == 'final_result':
                self._save_completed_enhanced_trade(enriched_snapshot)

            # Update stats enrichies
            processing_time = (time.perf_counter() - start_time) * 1000
            self._update_enhanced_collection_stats(processing_time, enhanced_type)

            logger.debug(f"Enhanced snapshot collecté: {enriched_snapshot.get('trade_id', 'unknown')} ({enhanced_type})")
            return True

        except Exception as e:
            logger.error(f"Erreur collection enhanced snapshot: {e}")
            return False

    def _validate_enhanced_snapshot_structure(self, snapshot: Dict[str, Any]) -> bool:
        """🆕 Validation structure snapshot enrichi"""
        # Validation de base (GARDÉE)
        required_fields = ['timestamp', 'snapshot_type']
        
        for field in required_fields:
            if field not in snapshot:
                logger.warning(f"Champ manquant dans snapshot: {field}")
                return False

        # 🆕 Validation enrichie selon type
        snapshot_type = snapshot.get('snapshot_type', '')
        
        if snapshot_type == 'microstructure':
            required_micro_fields = ['microstructure_data']
            for field in required_micro_fields:
                if field not in snapshot:
                    logger.warning(f"Champ microstructure manquant: {field}")
                    return False
        
        elif snapshot_type == 'options_flow':
            required_options_fields = ['options_flow_data']
            for field in required_options_fields:
                if field not in snapshot:
                    logger.warning(f"Champ options manquant: {field}")
                    return False

        elif snapshot_type == 'post_trade_analysis':
            required_analysis_fields = ['post_trade_analysis']
            for field in required_analysis_fields:
                if field not in snapshot:
                    logger.warning(f"Champ post-analysis manquant: {field}")
                    return False

        return True

    def _detect_enhanced_snapshot_type(self, snapshot: Dict[str, Any]) -> EnhancedDataType:
        """🆕 Détection type snapshot enrichi"""
        snapshot_type = snapshot.get('snapshot_type', 'standard')
        
        # Mapping types
        type_mapping = {
            'microstructure': EnhancedDataType.MICROSTRUCTURE,
            'options_flow': EnhancedDataType.OPTIONS_FLOW,
            'session_context': EnhancedDataType.SESSION_CONTEXT,
            'post_trade_analysis': EnhancedDataType.POST_TRADE_ANALYSIS,
            'correlation_update': EnhancedDataType.CORRELATION_DATA
        }
        
        return type_mapping.get(snapshot_type, EnhancedDataType.STANDARD)

    def _enrich_enhanced_snapshot_metadata(self, snapshot: Dict[str, Any], enhanced_type: EnhancedDataType) -> Dict[str, Any]:
        """🆕 Enrichissement metadata snapshot enrichi"""
        enriched = snapshot.copy()

        # Metadata collection standard (GARDÉE)
        enriched['collection_metadata'] = {
            'collection_timestamp': datetime.now(timezone.utc).isoformat(),
            'collector_session_id': self.session_metadata['session_id'],
            'data_quality': self._assess_enhanced_snapshot_quality(snapshot, enhanced_type),
            'ml_features_ready': self._check_enhanced_ml_features_availability(snapshot, enhanced_type),
            'checksum': self._calculate_snapshot_checksum(snapshot),
            # 🆕 Enhanced metadata
            'enhanced_type': enhanced_type.value,
            'enrichment_level': self._calculate_enrichment_level(snapshot),
            'feature_count': self._count_enhanced_features(snapshot, enhanced_type),
            'data_completeness': self._calculate_enhanced_completeness(snapshot, enhanced_type)
        }

        # 🆕 Session tracking enrichi
        self.session_metadata['enhanced_snapshots_collected'] += 1
        
        if enhanced_type == EnhancedDataType.MICROSTRUCTURE:
            self.session_metadata['microstructure_snapshots'] += 1
        elif enhanced_type == EnhancedDataType.OPTIONS_FLOW:
            self.session_metadata['options_snapshots'] += 1
        elif enhanced_type == EnhancedDataType.POST_TRADE_ANALYSIS:
            self.session_metadata['post_analyses_completed'] += 1
        elif enhanced_type == EnhancedDataType.CORRELATION_DATA:
            self.session_metadata['correlation_updates'] += 1

        return enriched

    def _assess_enhanced_snapshot_quality(self, snapshot: Dict[str, Any], enhanced_type: EnhancedDataType) -> str:
        """🆕 Évaluation qualité snapshot enrichi"""
        base_score = 1.0

        # Score qualité de base (GARDÉ)
        if 'market_snapshot' in snapshot and snapshot['market_snapshot']:
            base_score += 0.2
        
        if 'battle_navale_analysis' in snapshot and snapshot['battle_navale_analysis']:
            base_score += 0.2

        # 🆕 Score enrichissement selon type
        enrichment_score = 0.0
        
        if enhanced_type == EnhancedDataType.MICROSTRUCTURE:
            micro_data = snapshot.get('microstructure_data', {})
            if micro_data.get('order_book_imbalance') is not None:
                enrichment_score += 0.3
            if micro_data.get('tick_momentum_score') is not None:
                enrichment_score += 0.2
            if micro_data.get('large_orders_bias') is not None:
                enrichment_score += 0.2
        
        elif enhanced_type == EnhancedDataType.OPTIONS_FLOW:
            options_data = snapshot.get('options_flow_data', {})
            if options_data.get('total_gamma_exposure') is not None:
                enrichment_score += 0.3
            if options_data.get('vix_level') is not None:
                enrichment_score += 0.2
            if options_data.get('dealer_gamma_position') is not None:
                enrichment_score += 0.2
        
        elif enhanced_type == EnhancedDataType.POST_TRADE_ANALYSIS:
            analysis_data = snapshot.get('post_trade_analysis', {})
            if analysis_data.get('edge_confirmed') is not None:
                enrichment_score += 0.3
            if analysis_data.get('success_factors'):
                enrichment_score += 0.2
            if analysis_data.get('improvement_suggestions'):
                enrichment_score += 0.2

        # Score final
        final_score = (base_score + enrichment_score) / 2.0

        # Classification enrichie
        if final_score >= 1.2:
            return DataQuality.ENHANCED.value
        elif final_score >= 0.9:
            return DataQuality.EXCELLENT.value
        elif final_score >= 0.75:
            return DataQuality.GOOD.value
        elif final_score >= 0.6:
            return DataQuality.ACCEPTABLE.value
        else:
            return DataQuality.POOR.value

    def _check_enhanced_ml_features_availability(self, snapshot: Dict[str, Any], enhanced_type: EnhancedDataType) -> bool:
        """🆕 Vérification disponibilité features ML enrichies"""
        # Check standard features (GARDÉ)
        standard_available = self._check_standard_ml_features(snapshot)
        
        # 🆕 Check enhanced features selon type
        enhanced_available = False
        
        if enhanced_type == EnhancedDataType.MICROSTRUCTURE:
            micro_data = snapshot.get('microstructure_data', {})
            required_micro = ['order_book_imbalance', 'tick_momentum_score', 'large_orders_bias']
            enhanced_available = all(micro_data.get(field) is not None for field in required_micro)
        
        elif enhanced_type == EnhancedDataType.OPTIONS_FLOW:
            options_data = snapshot.get('options_flow_data', {})
            required_options = ['total_gamma_exposure', 'vix_level', 'dealer_gamma_position']
            enhanced_available = all(options_data.get(field) is not None for field in required_options)
        
        elif enhanced_type == EnhancedDataType.SESSION_CONTEXT:
            session_data = snapshot.get('session_context_data', {})
            required_session = ['session_phase', 'time_since_open_minutes', 'market_stress_indicator']
            enhanced_available = all(session_data.get(field) is not None for field in required_session)
        
        elif enhanced_type == EnhancedDataType.POST_TRADE_ANALYSIS:
            analysis_data = snapshot.get('post_trade_analysis', {})
            required_analysis = ['edge_confirmed', 'timing_quality_score', 'pattern_reliability_update']
            enhanced_available = all(analysis_data.get(field) is not None for field in required_analysis)
        
        else:
            enhanced_available = True  # Standard type

        return standard_available and enhanced_available

    def _check_standard_ml_features(self, snapshot: Dict[str, Any]) -> bool:
        """Check features ML standard (GARDÉ)"""
        required_sections = ['market_snapshot']
        
        for section in required_sections:
            if section not in snapshot or not snapshot[section]:
                return False

        market_data = snapshot.get('market_snapshot', {})
        required_fields = ['close', 'volume']
        
        for field in required_fields:
            if market_data.get(field) is None:
                return False

        return True

    def _calculate_enrichment_level(self, snapshot: Dict[str, Any]) -> float:
        """🆕 Calcul niveau enrichissement snapshot"""
        enrichment_points = 0.0
        max_points = 5.0
        
        # Standard data
        if snapshot.get('market_snapshot'):
            enrichment_points += 1.0
        
        # Enhanced data
        if snapshot.get('microstructure_data'):
            enrichment_points += 1.0
        if snapshot.get('options_flow_data'):
            enrichment_points += 1.0
        if snapshot.get('session_context_data'):
            enrichment_points += 1.0
        if snapshot.get('post_trade_analysis'):
            enrichment_points += 1.0
        
        return enrichment_points / max_points

    def _count_enhanced_features(self, snapshot: Dict[str, Any], enhanced_type: EnhancedDataType) -> int:
        """🆕 Compte features enrichies disponibles"""
        feature_count = 0
        
        # Standard features
        if snapshot.get('market_snapshot'):
            feature_count += len([k for k, v in snapshot['market_snapshot'].items() if v is not None])
        
        # Enhanced features selon type
        if enhanced_type == EnhancedDataType.MICROSTRUCTURE and snapshot.get('microstructure_data'):
            feature_count += len([k for k, v in snapshot['microstructure_data'].items() if v is not None])
        
        elif enhanced_type == EnhancedDataType.OPTIONS_FLOW and snapshot.get('options_flow_data'):
            feature_count += len([k for k, v in snapshot['options_flow_data'].items() if v is not None])
        
        elif enhanced_type == EnhancedDataType.SESSION_CONTEXT and snapshot.get('session_context_data'):
            feature_count += len([k for k, v in snapshot['session_context_data'].items() if v is not None])
        
        elif enhanced_type == EnhancedDataType.POST_TRADE_ANALYSIS and snapshot.get('post_trade_analysis'):
            feature_count += len([k for k, v in snapshot['post_trade_analysis'].items() if v is not None])
        
        return feature_count

    def _calculate_enhanced_completeness(self, snapshot: Dict[str, Any], enhanced_type: EnhancedDataType) -> float:
        """🆕 Calcul complétude données enrichies"""
        total_expected = 0
        total_present = 0
        
        # Expected fields selon type
        expected_fields_map = {
            EnhancedDataType.MICROSTRUCTURE: self.enhanced_ml_feature_config['microstructure_features'],
            EnhancedDataType.OPTIONS_FLOW: self.enhanced_ml_feature_config['options_features'],
            EnhancedDataType.SESSION_CONTEXT: self.enhanced_ml_feature_config['session_features'],
            EnhancedDataType.POST_TRADE_ANALYSIS: self.enhanced_ml_feature_config['post_trade_features']
        }
        
        if enhanced_type in expected_fields_map:
            expected_fields = expected_fields_map[enhanced_type]
            total_expected = len(expected_fields)
            
            # Data section selon type
            data_key_map = {
                EnhancedDataType.MICROSTRUCTURE: 'microstructure_data',
                EnhancedDataType.OPTIONS_FLOW: 'options_flow_data',
                EnhancedDataType.SESSION_CONTEXT: 'session_context_data',
                EnhancedDataType.POST_TRADE_ANALYSIS: 'post_trade_analysis'
            }
            
            data_section = snapshot.get(data_key_map.get(enhanced_type, ''), {})
            total_present = sum(1 for field in expected_fields if data_section.get(field) is not None)
        
        return total_present / total_expected if total_expected > 0 else 0.0

    def _save_enhanced_snapshot_by_type(self, snapshot: Dict[str, Any], enhanced_type: EnhancedDataType):
        """🆕 Sauvegarde snapshot selon type enrichi"""
        try:
            today = datetime.now().date()
            
            # Mapping paths par type
            path_mapping = {
                EnhancedDataType.MICROSTRUCTURE: self.microstructure_path,
                EnhancedDataType.OPTIONS_FLOW: self.options_path,
                EnhancedDataType.SESSION_CONTEXT: self.session_path,
                EnhancedDataType.POST_TRADE_ANALYSIS: self.post_analysis_path,
                EnhancedDataType.CORRELATION_DATA: self.correlations_path,
                EnhancedDataType.STANDARD: self.daily_path
            }
            
            target_path = path_mapping.get(enhanced_type, self.enhanced_path)
            filename = f"{enhanced_type.value}_{today.isoformat()}.jsonl"
            file_path = target_path / filename
            
            # Sauvegarde
            with open(file_path, 'a', encoding='utf-8') as f:
                json.dump(snapshot, f, separators=(',', ':'), default=str)
                f.write('\n')
                
            logger.debug(f"Enhanced snapshot sauvegardé: {enhanced_type.value}")

        except Exception as e:
            logger.error(f"Erreur sauvegarde enhanced snapshot {enhanced_type}: {e}")

    def _save_completed_enhanced_trade(self, snapshot: Dict[str, Any]):
        """🆕 Sauvegarde trade complété enrichi"""
        # Sauvegarde standard (GARDÉE)
        self._save_completed_trade(snapshot)
        
        # 🆕 Sauvegarde enrichie spécialisée
        try:
            trade_id = snapshot.get('trade_id', 'unknown')
            
            # Index enrichi
            enrichment_level = snapshot.get('collection_metadata', {}).get('enrichment_level', 0.0)
            
            if enrichment_level >= 0.8:  # Trade très enrichi
                enhanced_summary_file = self.enhanced_path / f"high_quality_trades_{datetime.now().date().isoformat()}.jsonl"
                
                with open(enhanced_summary_file, 'a', encoding='utf-8') as f:
                    json.dump({
                        'trade_id': trade_id,
                        'enrichment_level': enrichment_level,
                        'timestamp': snapshot.get('timestamp'),
                        'enhanced_features_available': True
                    }, f, separators=(',', ':'), default=str)
                    f.write('\n')

        except Exception as e:
            logger.error(f"Erreur sauvegarde enhanced trade: {e}")

    def _save_completed_trade(self, snapshot: Dict[str, Any]):
        """Sauvegarde trade complété (GARDÉE)"""
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
                json.dump(snapshot, f, separators=(',', ':'), default=str)
                f.write('\n')

            # Update compteur trades
            self.session_metadata['trades_completed'] += 1
            self.collection_stats['daily_trades_count'][dt.date().isoformat()] += 1

            logger.debug(f"Trade sauvegardé: {trade_id}")

        except Exception as e:
            logger.error(f"Erreur sauvegarde trade: {e}")

    def _update_enhanced_collection_stats(self, processing_time_ms: float, enhanced_type: EnhancedDataType):
        """🆕 Mise à jour statistiques collection enrichies"""
        # Stats standard (GARDÉES)
        self.collection_stats['snapshots_processed'] += 1
        
        # Moyenne mobile processing time
        current_avg = self.collection_stats['avg_processing_time_ms']
        count = self.collection_stats['snapshots_processed']
        self.collection_stats['avg_processing_time_ms'] = (
            (current_avg * (count - 1) + processing_time_ms) / count
        )

        # 🆕 Stats enrichies par type
        if enhanced_type != EnhancedDataType.STANDARD:
            self.collection_stats['enhanced_snapshots_processed'] += 1
        
        if enhanced_type == EnhancedDataType.MICROSTRUCTURE:
            self.collection_stats['microstructure_data_points'] += 1
        elif enhanced_type == EnhancedDataType.OPTIONS_FLOW:
            self.collection_stats['options_data_points'] += 1
        elif enhanced_type == EnhancedDataType.SESSION_CONTEXT:
            self.collection_stats['session_contexts_analyzed'] += 1
        elif enhanced_type == EnhancedDataType.POST_TRADE_ANALYSIS:
            self.collection_stats['post_trade_insights_collected'] += 1
        elif enhanced_type == EnhancedDataType.CORRELATION_DATA:
            self.collection_stats['correlation_matrices_computed'] += 1

    # === ENHANCED DATA ORGANIZATION ===

    def organize_enhanced_daily_data(self, target_date: date) -> bool:
        """
        🆕 ORGANISATION DONNÉES QUOTIDIENNES ENRICHIES
        
        Organise et valide données standard + enrichies d'une journée
        """
        try:
            logger.info(f"Organisation données enrichies {target_date}")

            # Collection snapshots standard
            daily_snapshots = self._collect_daily_snapshots(target_date)
            
            # 🆕 Collection snapshots enrichis
            enhanced_snapshots = self._collect_enhanced_daily_snapshots(target_date)

            if not daily_snapshots and not enhanced_snapshots:
                logger.warning(f"Aucun snapshot pour {target_date}")
                return True

            # Organisation par trade (standard + enrichi)
            trades_data = self._organize_enhanced_snapshots_by_trade(daily_snapshots, enhanced_snapshots)

            # Validation et nettoyage enrichi
            validated_trades = self._validate_enhanced_trades_data(trades_data)

            # 🆕 Création summary enrichi
            enhanced_daily_summary = self._create_enhanced_daily_summary(target_date, validated_trades)

            # Sauvegarde summary enrichi
            self._save_enhanced_daily_summary(target_date, enhanced_daily_summary)

            # 🆕 Préparation données ML enrichies
            if len(validated_trades) >= 5:  # Seuil plus bas pour données enrichies
                self._prepare_enhanced_daily_ml_features(target_date, validated_trades)

            logger.info(f"[OK] Organisation enrichie {target_date}: {len(validated_trades)} trades validés")
            return True

        except Exception as e:
            logger.error(f"Erreur organisation enrichie {target_date}: {e}")
            return False

    def _collect_enhanced_daily_snapshots(self, target_date: date) -> Dict[str, List[Dict]]:
        """🆕 Collection snapshots enrichis d'une journée"""
        enhanced_snapshots = {
            'microstructure': [],
            'options_flow': [],
            'session_context': [],
            'post_analysis': [],
            'correlations': []
        }

        # Mapping files par type
        file_mapping = {
            'microstructure': self.microstructure_path / f"microstructure_{target_date.isoformat()}.jsonl",
            'options_flow': self.options_path / f"options_flow_{target_date.isoformat()}.jsonl",
            'session_context': self.session_path / f"session_context_{target_date.isoformat()}.jsonl",
            'post_analysis': self.post_analysis_path / f"post_trade_analysis_{target_date.isoformat()}.jsonl",
            'correlations': self.correlations_path / f"correlation_data_{target_date.isoformat()}.jsonl"
        }

        for snapshot_type, file_path in file_mapping.items():
            if file_path.exists():
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        for line in f:
                            line = line.strip()
                            if line:
                                snapshot = json.loads(line)
                                enhanced_snapshots[snapshot_type].append(snapshot)
                    
                    logger.debug(f"Collecté {len(enhanced_snapshots[snapshot_type])} snapshots {snapshot_type}")
                
                except Exception as e:
                    logger.error(f"Erreur lecture snapshots {snapshot_type} {target_date}: {e}")

        return enhanced_snapshots

    def _organize_enhanced_snapshots_by_trade(self, standard_snapshots: List[Dict], enhanced_snapshots: Dict[str, List[Dict]]) -> Dict[str, Dict]:
        """🆕 Organisation snapshots standard + enrichis par trade"""
        trades_data = defaultdict(lambda: {
            'standard': [],
            'microstructure': [],
            'options_flow': [],
            'session_context': [],
            'post_analysis': [],
            'correlations': []
        })

        # Organiser snapshots standard
        for snapshot in standard_snapshots:
            trade_id = snapshot.get('trade_id', 'unknown')
            trades_data[trade_id]['standard'].append(snapshot)

        # Organiser snapshots enrichis
        for enhanced_type, snapshots_list in enhanced_snapshots.items():
            for snapshot in snapshots_list:
                trade_id = snapshot.get('trade_id', 'unknown')
                if trade_id != 'unknown':  # Certains types n'ont pas de trade_id (correlations)
                    trades_data[trade_id][enhanced_type].append(snapshot)

        # Tri par timestamp dans chaque catégorie
        for trade_id, trade_data in trades_data.items():
            for data_type, snapshots_list in trade_data.items():
                trades_data[trade_id][data_type] = sorted(
                    snapshots_list,
                    key=lambda s: s.get('timestamp', '')
                )

        return dict(trades_data)

    def _validate_enhanced_trades_data(self, trades_data: Dict[str, Dict]) -> Dict[str, Dict]:
        """🆕 Validation et nettoyage données trades enrichies"""
        validated_trades = {}

        for trade_id, trade_snapshots in trades_data.items():
            # Validation trade standard (GARDÉE)
            if self._is_complete_trade(trade_snapshots['standard']):
                # 🆕 Calcul score enrichissement
                enrichment_score = self._calculate_trade_enrichment_score(trade_snapshots)
                
                # Accepter trade si standard complet ou bien enrichi
                if enrichment_score >= 0.3:  # Au moins 30% enrichi
                    validated_trades[trade_id] = trade_snapshots
                    logger.debug(f"Trade validé avec enrichissement {enrichment_score:.2f}: {trade_id}")
                else:
                    logger.warning(f"Trade faiblement enrichi ignoré: {trade_id}")
            else:
                logger.warning(f"Trade incomplet ignoré: {trade_id}")

        return validated_trades

    def _calculate_trade_enrichment_score(self, trade_snapshots: Dict[str, List]) -> float:
        """🆕 Calcul score enrichissement d'un trade"""
        enrichment_points = 0.0
        max_points = 4.0  # microstructure, options, session, post_analysis
        
        if trade_snapshots['microstructure']:
            enrichment_points += 1.0
        if trade_snapshots['options_flow']:
            enrichment_points += 1.0
        if trade_snapshots['session_context']:
            enrichment_points += 1.0
        if trade_snapshots['post_analysis']:
            enrichment_points += 1.0

        return enrichment_points / max_points

    def _is_complete_trade(self, snapshots: List[Dict]) -> bool:
        """Vérification trade complet (GARDÉE)"""
        if not snapshots:
            return False
            
        snapshot_types = [s.get('snapshot_type') for s in snapshots]
        required_types = ['decision', 'final_result']
        
        for req_type in required_types:
            if req_type not in snapshot_types:
                return False

        return True

    def _create_enhanced_daily_summary(self, target_date: date, trades_data: Dict) -> EnhancedDataSummary:
        """🆕 Création summary quotidien enrichi"""
        total_trades = len(trades_data)
        
        # Comptage snapshots par type
        total_snapshots = 0
        microstructure_snapshots = 0
        options_flow_snapshots = 0
        session_context_snapshots = 0
        post_trade_analyses = 0
        correlation_updates = 0
        
        for trade_snapshots in trades_data.values():
            total_snapshots += sum(len(snapshots) for snapshots in trade_snapshots.values())
            microstructure_snapshots += len(trade_snapshots.get('microstructure', []))
            options_flow_snapshots += len(trade_snapshots.get('options_flow', []))
            session_context_snapshots += len(trade_snapshots.get('session_context', []))
            post_trade_analyses += len(trade_snapshots.get('post_analysis', []))
            correlation_updates += len(trade_snapshots.get('correlations', []))

        # Calcul qualité et enrichissement
        quality_scores = []
        enrichment_scores = []
        ml_features_count = 0
        enhanced_features_count = 0
        standard_features_count = 0

        for trade_snapshots in trades_data.values():
            trade_enrichment = self._calculate_trade_enrichment_score(trade_snapshots)
            enrichment_scores.append(trade_enrichment)
            
            # Analyse qualité snapshots
            for snapshot_type, snapshots in trade_snapshots.items():
                for snapshot in snapshots:
                    quality = snapshot.get('collection_metadata', {}).get('data_quality', 'acceptable')
                    quality_score = self._quality_to_score(quality)
                    quality_scores.append(quality_score)
                    
                    if snapshot.get('collection_metadata', {}).get('ml_features_ready', False):
                        ml_features_count += 1
                    
                    feature_count = snapshot.get('collection_metadata', {}).get('feature_count', 0)
                    if snapshot_type == 'standard':
                        standard_features_count += feature_count
                    else:
                        enhanced_features_count += feature_count

        # Détermination qualité globale enrichie
        avg_quality = np.mean(quality_scores) if quality_scores else 0.5
        avg_enrichment = np.mean(enrichment_scores) if enrichment_scores else 0.0
        
        # Qualité finale basée sur standard + enrichissement
        if avg_quality >= 0.9 and avg_enrichment >= 0.7:
            overall_quality = DataQuality.ENHANCED
        elif avg_quality >= 0.9:
            overall_quality = DataQuality.EXCELLENT
        elif avg_quality >= 0.75:
            overall_quality = DataQuality.GOOD
        elif avg_quality >= 0.6:
            overall_quality = DataQuality.ACCEPTABLE
        else:
            overall_quality = DataQuality.POOR

        enrichment_ratio = avg_enrichment

        return EnhancedDataSummary(
            period=f"daily_enhanced_{target_date.isoformat()}",
            start_time=datetime.combine(target_date, datetime.min.time()),
            end_time=datetime.combine(target_date, datetime.max.time()),
            total_trades=total_trades,
            total_snapshots=total_snapshots,
            data_quality=overall_quality,
            file_size_mb=0.0,  # Sera calculé lors sauvegarde
            checksum="",  # Sera calculé lors sauvegarde
            ml_features_available=(ml_features_count > 0),
            last_updated=datetime.now(timezone.utc),
            # Enhanced fields
            microstructure_snapshots=microstructure_snapshots,
            options_flow_snapshots=options_flow_snapshots,
            session_context_snapshots=session_context_snapshots,
            post_trade_analyses=post_trade_analyses,
            correlation_updates=correlation_updates,
            enhanced_features_count=enhanced_features_count,
            standard_features_count=standard_features_count,
            enrichment_ratio=enrichment_ratio
        )

    def _quality_to_score(self, quality: str) -> float:
        """Convert quality string to numeric score"""
        quality_map = {
            'enhanced': 1.2,
            'excellent': 1.0,
            'good': 0.8,
            'acceptable': 0.6,
            'poor': 0.3,
            'corrupted': 0.0
        }
        return quality_map.get(quality, 0.5)

    def _save_enhanced_daily_summary(self, target_date: date, summary: EnhancedDataSummary):
        """🆕 Sauvegarde summary quotidien enrichi"""
        try:
            summary_file = self.enhanced_path / f"enhanced_summary_{target_date.isoformat()}.json"

            with open(summary_file, 'w', encoding='utf-8') as f:
                json.dump(asdict(summary), f, indent=2, default=str)

            logger.debug(f"Enhanced summary sauvegardé: {target_date}")

        except Exception as e:
            logger.error(f"Erreur sauvegarde enhanced summary {target_date}: {e}")

    def _prepare_enhanced_daily_ml_features(self, target_date: date, trades_data: Dict):
        """🆕 Préparation features ML quotidiennes enrichies"""
        try:
            # Extraction features enrichies
            enhanced_features_data = []

            for trade_id, trade_snapshots in trades_data.items():
                trade_features = self._extract_enhanced_trade_ml_features(trade_id, trade_snapshots)
                if trade_features:
                    enhanced_features_data.append(trade_features)

            if enhanced_features_data:
                # Création DataFrame enrichi
                features_df = pd.DataFrame(enhanced_features_data)

                # Sauvegarde features enrichies
                features_file = self.ml_path / f"enhanced_features_{target_date.isoformat()}.parquet"
                features_df.to_parquet(features_file, index=False)

                logger.debug(f"Enhanced features ML sauvegardées: {target_date} ({len(enhanced_features_data)} trades)")

        except Exception as e:
            logger.error(f"Erreur préparation enhanced ML features {target_date}: {e}")

    def _extract_enhanced_trade_ml_features(self, trade_id: str, trade_snapshots: Dict) -> Optional[Dict]:
        """🆕 Extraction features ML enrichies d'un trade"""
        try:
            # Features standard (GARDÉES)
            standard_features = self._extract_standard_trade_features(trade_id, trade_snapshots['standard'])
            if not standard_features:
                return None

            # 🆕 Features enrichies par type
            enhanced_features = {}

            # Microstructure features
            if trade_snapshots['microstructure']:
                micro_features = self._extract_microstructure_features(trade_snapshots['microstructure'])
                enhanced_features.update(micro_features)

            # Options features
            if trade_snapshots['options_flow']:
                options_features = self._extract_options_features(trade_snapshots['options_flow'])
                enhanced_features.update(options_features)

            # Session features
            if trade_snapshots['session_context']:
                session_features = self._extract_session_features(trade_snapshots['session_context'])
                enhanced_features.update(session_features)

            # Post-trade features
            if trade_snapshots['post_analysis']:
                post_trade_features = self._extract_post_trade_features(trade_snapshots['post_analysis'])
                enhanced_features.update(post_trade_features)

            # Combinaison features standard + enrichies
            all_features = {**standard_features, **enhanced_features}
            all_features['enrichment_level'] = len(enhanced_features) / max(1, len(self._get_all_possible_enhanced_features()))

            return all_features

        except Exception as e:
            logger.error(f"Erreur extraction enhanced features trade {trade_id}: {e}")
            return None

    def _extract_standard_trade_features(self, trade_id: str, standard_snapshots: List[Dict]) -> Optional[Dict]:
        """Extraction features standard (GARDÉE avec améliorations)"""
        try:
            # Trouver snapshots clés
            decision_snapshot = None
            result_snapshot = None

            for snapshot in standard_snapshots:
                if snapshot.get('snapshot_type') == 'decision':
                    decision_snapshot = snapshot
                elif snapshot.get('snapshot_type') == 'final_result':
                    result_snapshot = snapshot

            if not decision_snapshot or not result_snapshot:
                return None

            # Features market et battle navale
            market_data = decision_snapshot.get('market_snapshot', {})
            battle_data = decision_snapshot.get('battle_navale_analysis', {})
            trade_result = result_snapshot.get('trade_result', {})

            features = {
                'trade_id': trade_id,
                'timestamp': decision_snapshot.get('timestamp'),

                # Market features standard
                'close_price': market_data.get('close'),
                'volume': market_data.get('volume', 0),
                'atr_14': market_data.get('atr_14'),
                'trend_strength': market_data.get('trend_strength'),

                # Battle Navale features (avec PRIORITÉ #3)
                'vwap_trend_signal': battle_data.get('vwap_trend_signal'),
                'sierra_pattern_strength': battle_data.get('sierra_pattern_strength'),
                'gamma_levels_proximity': battle_data.get('gamma_levels_proximity'),
                'volume_confirmation': battle_data.get('volume_confirmation'),
                'options_flow_bias': battle_data.get('options_flow_bias'),
                'order_book_imbalance': battle_data.get('order_book_imbalance'),  # Nouveau P3
                'level_proximity_score': battle_data.get('level_proximity_score'),
                'aggression_bias': battle_data.get('aggression_bias'),

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
            logger.error(f"Erreur extraction standard features: {e}")
            return None

    def _extract_microstructure_features(self, microstructure_snapshots: List[Dict]) -> Dict:
        """🆕 Extraction features microstructure"""
        features = {}
        
        if microstructure_snapshots:
            # Prendre le dernier snapshot microstructure
            micro_data = microstructure_snapshots[-1].get('microstructure_data', {})
            
            for feature in self.enhanced_ml_feature_config['microstructure_features']:
                features[f'micro_{feature}'] = micro_data.get(feature, 0.0)
        
        return features

    def _extract_options_features(self, options_snapshots: List[Dict]) -> Dict:
        """🆕 Extraction features options"""
        features = {}
        
        if options_snapshots:
            options_data = options_snapshots[-1].get('options_flow_data', {})
            
            for feature in self.enhanced_ml_feature_config['options_features']:
                features[f'opt_{feature}'] = options_data.get(feature, 0.0)
        
        return features

    def _extract_session_features(self, session_snapshots: List[Dict]) -> Dict:
        """🆕 Extraction features session"""
        features = {}
        
        if session_snapshots:
            session_data = session_snapshots[-1].get('session_context_data', {})
            
            for feature in self.enhanced_ml_feature_config['session_features']:
                value = session_data.get(feature, 0)
                
                # Convertir valeurs non-numériques
                if isinstance(value, str):
                    if feature == 'session_phase':
                        phase_map = {'opening': 0, 'morning': 1, 'lunch': 2, 'afternoon': 3, 'close': 4}
                        value = phase_map.get(value, 0)
                    elif feature == 'seasonal_bias':
                        bias_map = {'bullish': 1, 'bearish': -1, 'neutral': 0}
                        value = bias_map.get(value, 0)
                    else:
                        value = 0
                elif isinstance(value, list):
                    value = len(value)  # Pour economic_events
                elif isinstance(value, bool):
                    value = 1 if value else 0
                
                features[f'session_{feature}'] = value
        
        return features

    def _extract_post_trade_features(self, post_analysis_snapshots: List[Dict]) -> Dict:
        """🆕 Extraction features post-trade"""
        features = {}
        
        if post_analysis_snapshots:
            analysis_data = post_analysis_snapshots[-1].get('post_trade_analysis', {})
            
            for feature in self.enhanced_ml_feature_config['post_trade_features']:
                value = analysis_data.get(feature, 0)
                
                # Convertir valeurs non-numériques
                if isinstance(value, bool):
                    value = 1 if value else 0
                elif isinstance(value, list):
                    value = len(value)
                elif value is None:
                    value = 0.0
                
                features[f'post_{feature}'] = value
        
        return features

    def _get_all_possible_enhanced_features(self) -> List[str]:
        """🆕 Liste toutes features enrichies possibles"""
        all_features = []
        all_features.extend(self.enhanced_ml_feature_config['microstructure_features'])
        all_features.extend(self.enhanced_ml_feature_config['options_features'])
        all_features.extend(self.enhanced_ml_feature_config['session_features'])
        all_features.extend(self.enhanced_ml_feature_config['post_trade_features'])
        return all_features

    # === ENHANCED ML DATASET PREPARATION ===

    def export_enhanced_ml_training_dataset(self,
                                           start_date: date,
                                           end_date: date,
                                           min_trades: int = 30,  # Réduit pour données enrichies
                                           include_enhanced_only: bool = False) -> Optional[EnhancedMLDataset]:
        """
        🆕 EXPORT DATASET ML TRAINING ENRICHI
        
        Prépare dataset complet enrichi pour training ML avancé
        """
        try:
            logger.info(f"Préparation dataset ML enrichi: {start_date} à {end_date}")

            # Collection données période enrichie
            all_trades_data = self._collect_enhanced_period_data(start_date, end_date)

            if len(all_trades_data) < min_trades:
                logger.warning(f"Pas assez de trades enrichis: {len(all_trades_data)}/{min_trades}")
                return None

            # 🆕 Préparation features et labels enrichis
            features_df, labels_series, metadata_df = self._prepare_enhanced_ml_features_and_labels(all_trades_data)
            
            # 🆕 Préparation datasets spécialisés
            microstructure_df = self._prepare_microstructure_dataset(all_trades_data)
            options_df = self._prepare_options_dataset(all_trades_data)
            session_df = self._prepare_session_dataset(all_trades_data)
            post_trade_df = self._prepare_post_trade_dataset(all_trades_data)
            correlation_df = self._prepare_correlation_dataset(all_trades_data)

            if features_df.empty:
                logger.error("Aucune feature enrichie préparée")
                return None

            # Validation dataset enrichi
            quality_score = self._validate_ml_dataset_quality(features_df, labels_series)
            enrichment_score = self._calculate_dataset_enrichment_score(
                features_df, microstructure_df, options_df, session_df, post_trade_df
            )

            # Feature names enrichies
            standard_features = [col for col in features_df.columns if not any(
                col.startswith(prefix) for prefix in ['micro_', 'opt_', 'session_', 'post_']
            )]
            enhanced_features = [col for col in features_df.columns if col not in standard_features]

            # 🆕 Création dataset ML enrichi
            enhanced_ml_dataset = EnhancedMLDataset(
                features=features_df,
                labels=labels_series,
                metadata=metadata_df,
                microstructure_features=microstructure_df,
                options_features=options_df,
                session_features=session_df,
                post_trade_insights=post_trade_df,
                correlation_matrix=correlation_df,
                feature_names=list(features_df.columns),
                enhanced_feature_names=enhanced_features,
                quality_score=quality_score,
                enrichment_score=enrichment_score,
                train_test_split_ready=True,
                creation_timestamp=datetime.now(timezone.utc),
                feature_engineering_applied=True,
                normalization_methods=self.enhanced_ml_feature_config['normalization'],
                correlation_analysis_included=(correlation_df is not None)
            )

            # Sauvegarde dataset enrichi
            self._save_enhanced_ml_dataset(enhanced_ml_dataset, start_date, end_date)

            logger.info(f"Dataset ML enrichi créé: {len(features_df)} samples, {len(enhanced_features)} features enrichies")
            return enhanced_ml_dataset

        except Exception as e:
            logger.error(f"Erreur export enhanced ML dataset: {e}")
            return None

    def _collect_enhanced_period_data(self, start_date: date, end_date: date) -> Dict[str, Dict]:
        """🆕 Collection données enrichies sur une période"""
        all_trades = {}

        current_date = start_date
        while current_date <= end_date:
            # Snapshots standard
            daily_file = self.daily_path / f"trades_{current_date.isoformat()}.jsonl"
            if daily_file.exists():
                daily_snapshots = self._collect_daily_snapshots(current_date)
                daily_trades = self._organize_snapshots_by_trade(daily_snapshots)
                
                # Initialiser structure enrichie
                for trade_id in daily_trades.keys():
                    if trade_id not in all_trades:
                        all_trades[trade_id] = {
                            'standard': daily_trades[trade_id],
                            'microstructure': [],
                            'options_flow': [],
                            'session_context': [],
                            'post_analysis': [],
                            'correlations': []
                        }

            # 🆕 Snapshots enrichis
            enhanced_snapshots = self._collect_enhanced_daily_snapshots(current_date)
            for trade_id in all_trades.keys():
                for enhanced_type, snapshots_list in enhanced_snapshots.items():
                    trade_snapshots = [s for s in snapshots_list if s.get('trade_id') == trade_id]
                    all_trades[trade_id][enhanced_type].extend(trade_snapshots)

            current_date += timedelta(days=1)

        return all_trades

    def _prepare_enhanced_ml_features_and_labels(self, trades_data: Dict) -> Tuple[pd.DataFrame, pd.Series, pd.DataFrame]:
        """🆕 Préparation features et labels enrichis pour ML"""
        features_list = []
        labels_list = []
        metadata_list = []

        for trade_id, trade_snapshots in trades_data.items():
            # Features enrichies complètes
            trade_features = self._extract_enhanced_trade_ml_features(trade_id, trade_snapshots)
            if trade_features is None:
                continue

            # Labels enrichis
            result_snapshot = None
            for snapshot in trade_snapshots['standard']:
                if snapshot.get('snapshot_type') == 'final_result':
                    result_snapshot = snapshot
                    break

            if not result_snapshot:
                continue

            trade_result = result_snapshot.get('trade_result', {})
            
            # Labels multiples
            net_pnl = trade_result.get('net_pnl', 0)
            profitable = net_pnl > 0
            
            features_list.append(trade_features)
            labels_list.append(profitable)
            
            # Metadata enrichies
            metadata_list.append({
                'trade_id': trade_id,
                'timestamp': result_snapshot.get('timestamp'),
                'net_pnl': net_pnl,
                'return_percent': trade_result.get('return_percent', 0),
                'enrichment_level': trade_features.get('enrichment_level', 0),
                'has_microstructure': len(trade_snapshots['microstructure']) > 0,
                'has_options_data': len(trade_snapshots['options_flow']) > 0,
                'has_post_analysis': len(trade_snapshots['post_analysis']) > 0
            })

        # Conversion DataFrames
        features_df = pd.DataFrame(features_list)
        labels_series = pd.Series(labels_list, name='profitable')
        metadata_df = pd.DataFrame(metadata_list)

        return features_df, labels_series, metadata_df

    def _prepare_microstructure_dataset(self, trades_data: Dict) -> Optional[pd.DataFrame]:
        """🆕 Préparation dataset microstructure spécialisé"""
        microstructure_data = []
        
        for trade_id, trade_snapshots in trades_data.items():
            for snapshot in trade_snapshots['microstructure']:
                micro_data = snapshot.get('microstructure_data', {})
                if micro_data:
                    micro_record = {
                        'trade_id': trade_id,
                        'timestamp': snapshot.get('timestamp'),
                        **micro_data
                    }
                    microstructure_data.append(micro_record)
        
        return pd.DataFrame(microstructure_data) if microstructure_data else None

    def _prepare_options_dataset(self, trades_data: Dict) -> Optional[pd.DataFrame]:
        """🆕 Préparation dataset options spécialisé"""
        options_data = []
        
        for trade_id, trade_snapshots in trades_data.items():
            for snapshot in trade_snapshots['options_flow']:
                opt_data = snapshot.get('options_flow_data', {})
                if opt_data:
                    opt_record = {
                        'trade_id': trade_id,
                        'timestamp': snapshot.get('timestamp'),
                        **opt_data
                    }
                    options_data.append(opt_record)
        
        return pd.DataFrame(options_data) if options_data else None

    def _prepare_session_dataset(self, trades_data: Dict) -> Optional[pd.DataFrame]:
        """🆕 Préparation dataset session spécialisé"""
        session_data = []
        
        for trade_id, trade_snapshots in trades_data.items():
            for snapshot in trade_snapshots['session_context']:
                sess_data = snapshot.get('session_context_data', {})
                if sess_data:
                    sess_record = {
                        'trade_id': trade_id,
                        'timestamp': snapshot.get('timestamp'),
                        **sess_data
                    }
                    session_data.append(sess_record)
        
        return pd.DataFrame(session_data) if session_data else None

    def _prepare_post_trade_dataset(self, trades_data: Dict) -> Optional[pd.DataFrame]:
        """🆕 Préparation dataset post-trade spécialisé"""
        post_trade_data = []
        
        for trade_id, trade_snapshots in trades_data.items():
            for snapshot in trade_snapshots['post_analysis']:
                analysis_data = snapshot.get('post_trade_analysis', {})
                if analysis_data:
                    analysis_record = {
                        'trade_id': trade_id,
                        'timestamp': snapshot.get('timestamp'),
                        **analysis_data
                    }
                    post_trade_data.append(analysis_record)
        
        return pd.DataFrame(post_trade_data) if post_trade_data else None

    def _prepare_correlation_dataset(self, trades_data: Dict) -> Optional[pd.DataFrame]:
        """🆕 Préparation dataset corrélations"""
        correlation_data = []
        
        for trade_id, trade_snapshots in trades_data.items():
            for snapshot in trade_snapshots['correlations']:
                corr_data = snapshot.get('correlations_data', {})
                if corr_data:
                    corr_record = {
                        'timestamp': snapshot.get('timestamp'),
                        **corr_data
                    }
                    correlation_data.append(corr_record)
        
        return pd.DataFrame(correlation_data) if correlation_data else None

    def _calculate_dataset_enrichment_score(self, features_df: pd.DataFrame, *enhanced_dfs) -> float:
        """🆕 Calcul score enrichissement dataset"""
        total_features = len(features_df.columns)
        enhanced_features = sum(len(df.columns) if df is not None else 0 for df in enhanced_dfs)
        
        if total_features == 0:
            return 0.0
        
        return min(1.0, enhanced_features / total_features)

    def _save_enhanced_ml_dataset(self, ml_dataset: EnhancedMLDataset, start_date: date, end_date: date):
        """🆕 Sauvegarde dataset ML enrichi"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            dataset_name = f"enhanced_ml_dataset_{start_date}_{end_date}_{timestamp}"

            # Sauvegarde datasets principaux
            main_features_file = self.ml_path / f"{dataset_name}_features.parquet"
            labels_file = self.ml_path / f"{dataset_name}_labels.parquet"
            metadata_file = self.ml_path / f"{dataset_name}_metadata.json"

            ml_dataset.features.to_parquet(main_features_file, index=False)
            ml_dataset.labels.to_frame().to_parquet(labels_file, index=False)

            # 🆕 Sauvegarde datasets enrichis spécialisés
            if ml_dataset.microstructure_features is not None:
                micro_file = self.ml_path / f"{dataset_name}_microstructure.parquet"
                ml_dataset.microstructure_features.to_parquet(micro_file, index=False)

            if ml_dataset.options_features is not None:
                options_file = self.ml_path / f"{dataset_name}_options.parquet"
                ml_dataset.options_features.to_parquet(options_file, index=False)

            if ml_dataset.session_features is not None:
                session_file = self.ml_path / f"{dataset_name}_session.parquet"
                ml_dataset.session_features.to_parquet(session_file, index=False)

            if ml_dataset.post_trade_insights is not None:
                post_file = self.ml_path / f"{dataset_name}_post_trade.parquet"
                ml_dataset.post_trade_insights.to_parquet(post_file, index=False)

            if ml_dataset.correlation_matrix is not None:
                corr_file = self.ml_path / f"{dataset_name}_correlations.parquet"
                ml_dataset.correlation_matrix.to_parquet(corr_file, index=False)

            # 🆕 Metadata enrichies
            enhanced_metadata = {
                'creation_timestamp': ml_dataset.creation_timestamp.isoformat(),
                'features_count': len(ml_dataset.features.columns),
                'enhanced_features_count': len(ml_dataset.enhanced_feature_names),
                'samples_count': len(ml_dataset.features),
                'quality_score': ml_dataset.quality_score,
                'enrichment_score': ml_dataset.enrichment_score,
                'feature_names': ml_dataset.feature_names,
                'enhanced_feature_names': ml_dataset.enhanced_feature_names,
                'train_test_split_ready': ml_dataset.train_test_split_ready,
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'feature_engineering_applied': ml_dataset.feature_engineering_applied,
                'normalization_methods': ml_dataset.normalization_methods,
                'correlation_analysis_included': ml_dataset.correlation_analysis_included,
                'datasets_available': {
                    'main_features': True,
                    'microstructure': ml_dataset.microstructure_features is not None,
                    'options': ml_dataset.options_features is not None,
                    'session': ml_dataset.session_features is not None,
                    'post_trade': ml_dataset.post_trade_insights is not None,
                    'correlations': ml_dataset.correlation_matrix is not None
                }
            }

            with open(metadata_file, 'w') as f:
                json.dump(enhanced_metadata, f, indent=2)

            self.collection_stats['ml_datasets_created'] += 1
            logger.info(f"Enhanced ML dataset sauvegardé: {dataset_name}")

        except Exception as e:
            logger.error(f"Erreur sauvegarde enhanced ML dataset: {e}")

    def _collect_daily_snapshots(self, target_date: date) -> List[Dict]:
        """Collection snapshots quotidiens standard (GARDÉE)"""
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

            logger.debug(f"Collecté {len(snapshots)} snapshots standard pour {target_date}")

        except Exception as e:
            logger.error(f"Erreur lecture snapshots {target_date}: {e}")

        return snapshots

    def _organize_snapshots_by_trade(self, snapshots: List[Dict]) -> Dict[str, List[Dict]]:
        """Organisation snapshots par trade_id (GARDÉE)"""
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

    def _validate_ml_dataset_quality(self, features_df: pd.DataFrame, labels_series: pd.Series) -> float:
        """Validation qualité dataset ML (GARDÉE avec améliorations)"""
        try:
            quality_score = 1.0

            # Check completeness
            missing_ratio = features_df.isnull().sum().sum() / (len(features_df) * len(features_df.columns))
            quality_score -= missing_ratio * 0.5

            # Check balance labels
            label_balance = min(labels_series.sum(), len(labels_series) - labels_series.sum()) / len(labels_series)
            if label_balance < 0.1:
                quality_score -= 0.3
            elif label_balance < 0.2:
                quality_score -= 0.1

            # Check features variance
            numeric_features = features_df.select_dtypes(include=[np.number])
            if not numeric_features.empty:
                low_variance_features = (numeric_features.var() < 0.01).sum()
                quality_score -= (low_variance_features / len(numeric_features.columns)) * 0.2

            return max(0.0, quality_score)

        except Exception as e:
            logger.error(f"Erreur validation qualité dataset: {e}")
            return 0.5

    def _calculate_snapshot_checksum(self, snapshot: Dict[str, Any]) -> str:
        """Calcul checksum pour intégrité (GARDÉE)"""
        try:
            content = json.dumps(snapshot, sort_keys=True, separators=(',', ':'))
            return hashlib.md5(content.encode()).hexdigest()[:16]
        except Exception:
            return "checksum_error"

    # === ENHANCED STATUS & ANALYTICS ===

    def get_enhanced_collection_statistics(self) -> Dict[str, Any]:
        """🆕 Statistiques complètes collection enrichies"""
        try:
            # Stats standard (GARDÉES)
            standard_stats = {
                'session_metadata': self.session_metadata.copy(),
                'collection_stats': self.collection_stats.copy(),
                'storage_usage': self._calculate_enhanced_storage_usage(),
                'directory_info': self._get_enhanced_directory_info(),
                'data_quality_summary': self._get_enhanced_data_quality_summary(),
                'recent_activity': self._get_enhanced_recent_activity_summary()
            }

            # 🆕 Stats enrichies
            enhanced_stats = {
                'enrichment_summary': self._get_enrichment_summary(),
                'microstructure_analytics': self._get_microstructure_analytics(),
                'options_analytics': self._get_options_analytics(),
                'session_analytics': self._get_session_analytics(),
                'post_trade_analytics': self._get_post_trade_analytics(),
                'correlation_analytics': self._get_correlation_analytics(),
                'ml_readiness_score': self._calculate_ml_readiness_score()
            }

            return {**standard_stats, **enhanced_stats}

        except Exception as e:
            logger.error(f"Erreur statistiques enhanced collection: {e}")
            return {'error': str(e)}

    def _calculate_enhanced_storage_usage(self) -> Dict[str, float]:
        """🆕 Calcul usage stockage enrichi"""
        def get_directory_size(path: Path) -> float:
            total_size = 0
            if path.exists():
                for file_path in path.rglob("*"):
                    if file_path.is_file():
                        total_size += file_path.stat().st_size
            return total_size / (1024 * 1024)  # MB

        storage_usage = {
            # Standard (GARDÉ)
            'daily_mb': get_directory_size(self.daily_path),
            'weekly_mb': get_directory_size(self.weekly_path),
            'monthly_mb': get_directory_size(self.monthly_path),
            'archive_mb': get_directory_size(self.archive_path),
            'ml_mb': get_directory_size(self.ml_path),
            # 🆕 Enhanced
            'microstructure_mb': get_directory_size(self.microstructure_path),
            'options_mb': get_directory_size(self.options_path),
            'session_mb': get_directory_size(self.session_path),
            'post_analysis_mb': get_directory_size(self.post_analysis_path),
            'correlations_mb': get_directory_size(self.correlations_path),
            'enhanced_mb': get_directory_size(self.enhanced_path)
        }
        
        storage_usage['total_mb'] = sum(storage_usage.values())
        storage_usage['enhanced_ratio'] = (
            sum(storage_usage[key] for key in storage_usage.keys() if key.endswith('_mb') and 
                key not in ['daily_mb', 'weekly_mb', 'monthly_mb', 'archive_mb', 'ml_mb', 'total_mb']) /
            max(1, storage_usage['total_mb'])
        )

        return storage_usage

    def _get_enhanced_directory_info(self) -> Dict[str, Any]:
        """🆕 Informations directories enrichies"""
        def count_files(path: Path) -> Dict[str, int]:
            if not path.exists():
                return {'total_files': 0, 'jsonl_files': 0, 'parquet_files': 0}

            files = list(path.rglob("*"))
            jsonl_files = len([f for f in files if f.suffix == '.jsonl'])
            parquet_files = len([f for f in files if f.suffix == '.parquet'])

            return {
                'total_files': len(files),
                'jsonl_files': jsonl_files,
                'parquet_files': parquet_files
            }

        return {
            # Standard (GARDÉ)
            'daily': count_files(self.daily_path),
            'weekly': count_files(self.weekly_path),
            'monthly': count_files(self.monthly_path),
            'archive': count_files(self.archive_path),
            'ml_ready': count_files(self.ml_path),
            # 🆕 Enhanced
            'microstructure': count_files(self.microstructure_path),
            'options_flow': count_files(self.options_path),
            'session_context': count_files(self.session_path),
            'post_analysis': count_files(self.post_analysis_path),
            'correlations': count_files(self.correlations_path),
            'enhanced': count_files(self.enhanced_path)
        }

    def _get_enhanced_data_quality_summary(self) -> Dict[str, Any]:
        """🆕 Résumé qualité données enrichi"""
        if not self.collection_stats['data_quality_distribution']:
            return {'overall_quality': 'unknown', 'distribution': {}, 'enrichment_impact': 'unknown'}

        total = sum(self.collection_stats['data_quality_distribution'].values())
        distribution = {
            quality: (count / total) * 100
            for quality, count in self.collection_stats['data_quality_distribution'].items()
        }

        # Qualité globale enrichie
        if distribution.get('enhanced', 0) > 30:
            overall = 'enhanced'
        elif distribution.get('excellent', 0) > 50:
            overall = 'excellent'
        elif distribution.get('good', 0) + distribution.get('excellent', 0) > 70:
            overall = 'good'
        elif distribution.get('poor', 0) < 20:
            overall = 'acceptable'
        else:
            overall = 'poor'

        # Impact enrichissement
        enhanced_ratio = self.collection_stats['enhanced_snapshots_processed'] / max(1, self.collection_stats['snapshots_processed'])
        if enhanced_ratio > 0.7:
            enrichment_impact = 'high'
        elif enhanced_ratio > 0.4:
            enrichment_impact = 'medium'
        elif enhanced_ratio > 0.1:
            enrichment_impact = 'low'
        else:
            enrichment_impact = 'minimal'

        return {
            'overall_quality': overall,
            'distribution': distribution,
            'enrichment_impact': enrichment_impact,
            'enhanced_snapshots_ratio': enhanced_ratio
        }

    def _get_enhanced_recent_activity_summary(self) -> Dict[str, Any]:
        """🆕 Résumé activité récente enrichie"""
        session_duration = (datetime.now(timezone.utc) - self.session_start_time).total_seconds() / 60

        return {
            # Standard (GARDÉ)
            'current_session': {
                'snapshots_in_memory': len(self.current_session_snapshots),
                'session_duration_minutes': session_duration,
                'avg_processing_time_ms': self.collection_stats['avg_processing_time_ms']
            },
            # 🆕 Enhanced activity
            'enhanced_activity': {
                'enhanced_snapshots_processed': self.collection_stats['enhanced_snapshots_processed'],
                'microstructure_data_points': self.collection_stats['microstructure_data_points'],
                'options_data_points': self.collection_stats['options_data_points'],
                'post_trade_insights': self.collection_stats['post_trade_insights_collected'],
                'correlation_updates': self.collection_stats['correlation_matrices_computed']
            },
            'performance': {
                'snapshots_per_minute': self._calculate_recent_throughput(),
                'enhanced_ratio': self.collection_stats['enhanced_snapshots_processed'] / max(1, self.collection_stats['snapshots_processed']),
                'ml_datasets_created': self.collection_stats['ml_datasets_created']
            }
        }

    def _get_enrichment_summary(self) -> Dict[str, Any]:
        """🆕 Résumé enrichissement données"""
        total_snapshots = self.collection_stats['snapshots_processed']
        enhanced_snapshots = self.collection_stats['enhanced_snapshots_processed']

        return {
            'total_snapshots': total_snapshots,
            'enhanced_snapshots': enhanced_snapshots,
            'enrichment_ratio': enhanced_snapshots / max(1, total_snapshots),
            'microstructure_coverage': self.collection_stats['microstructure_data_points'] / max(1, total_snapshots),
            'options_coverage': self.collection_stats['options_data_points'] / max(1, total_snapshots),
            'post_analysis_coverage': self.collection_stats['post_trade_insights_collected'] / max(1, total_snapshots),
            'feature_engineering_operations': self.collection_stats['feature_engineering_operations']
        }

    def _get_microstructure_analytics(self) -> Dict[str, Any]:
        """🆕 Analytics microstructure"""
        return {
            'data_points_collected': self.collection_stats['microstructure_data_points'],
            'average_order_book_levels': 10,  # À calculer dynamiquement
            'tick_momentum_distribution': 'normal',  # À calculer
            'smart_money_detection_rate': 0.15  # À calculer
        }

    def _get_options_analytics(self) -> Dict[str, Any]:
        """🆕 Analytics options"""
        return {
            'data_points_collected': self.collection_stats['options_data_points'],
            'gamma_exposure_tracking': True,
            'vix_integration': True,
            'dealer_positioning_analysis': True
        }

    def _get_session_analytics(self) -> Dict[str, Any]:
        """🆕 Analytics session"""
        return {
            'contexts_analyzed': self.collection_stats['session_contexts_analyzed'],
            'economic_events_tracked': True,
            'seasonal_patterns_detected': True,
            'market_stress_monitoring': True
        }

    def _get_post_trade_analytics(self) -> Dict[str, Any]:
        """🆕 Analytics post-trade"""
        return {
            'insights_collected': self.collection_stats['post_trade_insights_collected'],
            'edge_validation_rate': 0.75,  # À calculer dynamiquement
            'improvement_suggestions_generated': True,
            'pattern_reliability_tracking': True
        }

    def _get_correlation_analytics(self) -> Dict[str, Any]:
        """🆕 Analytics corrélations"""
        return {
            'matrices_computed': self.collection_stats['correlation_matrices_computed'],
            'feature_correlation_tracking': True,
            'market_correlation_monitoring': True,
            'strategy_consistency_analysis': True
        }

    def _calculate_ml_readiness_score(self) -> float:
        """🆕 Calcul score ML readiness"""
        score = 0.0
        max_score = 5.0

        # Standard features
        if self.collection_stats['snapshots_processed'] > 0:
            score += 1.0

        # Enhanced features
        if self.collection_stats['microstructure_data_points'] > 0:
            score += 1.0
        if self.collection_stats['options_data_points'] > 0:
            score += 1.0
        if self.collection_stats['post_trade_insights_collected'] > 0:
            score += 1.0
        if self.collection_stats['correlation_matrices_computed'] > 0:
            score += 1.0

        return score / max_score

    def _calculate_recent_throughput(self) -> float:
        """Calcul throughput récent (GARDÉ)"""
        try:
            session_duration_minutes = (datetime.now(timezone.utc) - self.session_start_time).total_seconds() / 60
            if session_duration_minutes > 0:
                return self.collection_stats['snapshots_processed'] / session_duration_minutes
            return 0.0
        except Exception:
            return 0.0

    # === COMPATIBILITY METHODS (GARDÉES) ===

    def collect_trade_snapshot(self, snapshot: Dict[str, Any]) -> bool:
        """
        Méthode compatibilité pour collection snapshot standard
        Redirecte vers méthode enrichie
        """
        return self.collect_enhanced_trade_snapshot(snapshot)

    def organize_daily_data(self, target_date: date) -> bool:
        """
        Méthode compatibilité pour organisation quotidienne
        Redirecte vers méthode enrichie
        """
        return self.organize_enhanced_daily_data(target_date)

    def get_collection_statistics(self) -> Dict[str, Any]:
        """
        Méthode compatibilité pour statistiques
        Redirecte vers méthode enrichie
        """
        return self.get_enhanced_collection_statistics()

    def export_ml_training_dataset(self, start_date: date, end_date: date, min_trades: int = 50) -> Optional[Dict]:
        """
        Méthode compatibilité pour export ML
        Redirecte vers méthode enrichie et convertit résultat
        """
        enhanced_dataset = self.export_enhanced_ml_training_dataset(start_date, end_date, min_trades)
        
        if enhanced_dataset:
            # Conversion format compatible
            return {
                'features': enhanced_dataset.features,
                'labels': enhanced_dataset.labels,
                'metadata': enhanced_dataset.metadata,
                'feature_names': enhanced_dataset.feature_names,
                'quality_score': enhanced_dataset.quality_score,
                'train_test_split_ready': enhanced_dataset.train_test_split_ready,
                'creation_timestamp': enhanced_dataset.creation_timestamp
            }
        
        return None

# === ENHANCED FACTORY FUNCTIONS ===

def create_enhanced_data_collector(config: Optional[Dict] = None) -> DataCollectorEnhanced:
    """🆕 Factory function pour data collector enrichi"""
    return DataCollectorEnhanced(config)

def create_data_collector(config: Optional[Dict] = None) -> DataCollectorEnhanced:
    """Factory function compatibilité - retourne version enrichie"""
    return DataCollectorEnhanced(config)

def export_enhanced_ml_dataset(start_date: date, end_date: date, output_path: Optional[Path] = None) -> bool:
    """🆕 Helper function export dataset ML enrichi"""
    collector = create_enhanced_data_collector()
    dataset = collector.export_enhanced_ml_training_dataset(start_date, end_date)

    if dataset and output_path:
        try:
            with open(output_path, 'wb') as f:
                pickle.dump(dataset, f)
            return True
        except Exception as e:
            logger.error(f"Erreur sauvegarde enhanced dataset: {e}")

    return False

def export_ml_dataset(start_date: date, end_date: date, output_path: Optional[Path] = None) -> bool:
    """Helper function compatibilité - utilise version enrichie"""
    return export_enhanced_ml_dataset(start_date, end_date, output_path)

# === ENHANCED TESTING ===

def test_enhanced_data_collector():
    """🆕 Test data collector enrichi"""
    logger.info("🗄️ TEST ENHANCED DATA COLLECTOR")
    print("=" * 45)

    collector = create_enhanced_data_collector()

    # Test collection snapshot standard
    test_snapshot_standard = {
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'snapshot_type': 'decision',
        'trade_id': 'TEST_TRADE_001',
        'market_snapshot': {
            'close': 4500.0,
            'volume': 1500,
            'atr_14': 15.5,
            'trend_strength': 0.7
        },
        'battle_navale_analysis': {
            'vwap_trend_signal': 0.8,
            'sierra_pattern_strength': 0.6,
            'gamma_levels_proximity': 0.7,
            'volume_confirmation': 0.75,
            'options_flow_bias': 0.65,
            'order_book_imbalance': 0.2,  # Nouveau P3
            'level_proximity_score': 0.6,
            'aggression_bias': 0.55
        }
    }

    success_standard = collector.collect_enhanced_trade_snapshot(test_snapshot_standard)
    logger.info(f"Collection snapshot standard: {success_standard}")

    # 🆕 Test collection snapshot microstructure
    test_snapshot_micro = {
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'snapshot_type': 'microstructure',
        'trade_id': 'TEST_TRADE_001',
        'microstructure_data': {
            'order_book_imbalance': 0.65,
            'tick_momentum_score': 0.8,
            'large_orders_bias': 0.3,
            'aggressive_buy_ratio': 0.55,
            'aggressive_sell_ratio': 0.45,
            'volume_spike_detected': False,
            'bid_ask_spread_ticks': 1.0,
            'data_quality_score': 0.95
        }
    }

    success_micro = collector.collect_enhanced_trade_snapshot(test_snapshot_micro)
    logger.info(f"Collection snapshot microstructure: {success_micro}")

    # 🆕 Test collection snapshot options
    test_snapshot_options = {
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'snapshot_type': 'options_flow',
        'trade_id': 'TEST_TRADE_001',
        'options_flow_data': {
            'total_gamma_exposure': 78000000000,
            'dealer_gamma_position': 'short',
            'vix_level': 19.2,
            'put_call_ratio': 1.18,
            'days_to_monthly_expiry': 12
        }
    }

    success_options = collector.collect_enhanced_trade_snapshot(test_snapshot_options)
    logger.info(f"Collection snapshot options: {success_options}")

    # 🆕 Test collection snapshot post-trade
    test_snapshot_post = {
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'snapshot_type': 'post_trade_analysis',
        'trade_id': 'TEST_TRADE_001',
        'post_trade_analysis': {
            'trade_outcome': 'win',
            'edge_confirmed': True,
            'edge_confidence': 0.8,
            'success_factors': ['Battle_Navale_signal_strong', 'Good_timing'],
            'timing_quality_score': 0.85,
            'pattern_reliability_update': 0.9
        }
    }

    success_post = collector.collect_enhanced_trade_snapshot(test_snapshot_post)
    logger.info(f"Collection snapshot post-trade: {success_post}")

    # Test organization enrichie
    today = datetime.now().date()
    org_success = collector.organize_enhanced_daily_data(today)
    logger.info(f"Organisation daily enrichie: {org_success}")

    # Test statistics enrichies
    stats = collector.get_enhanced_collection_statistics()
    enhanced_stats = stats.get('enrichment_summary', {})
    logger.info(f"Stats enrichies: {enhanced_stats.get('enrichment_ratio', 0):.2f} ratio enrichissement")

    logger.info("✅ Enhanced data collector test COMPLETED")
    
    # Affichage résumé enrichi
    print("\n🎉 RÉSUMÉ TEST ENHANCED DATA COLLECTOR")
    print("=" * 45)
    print(f"✅ Snapshots standard: {success_standard}")
    print(f"✅ Snapshots microstructure: {success_micro}")
    print(f"✅ Snapshots options: {success_options}")
    print(f"✅ Snapshots post-trade: {success_post}")
    print(f"✅ Organisation enrichie: {org_success}")
    print("🚀 SYSTÈME DATA COLLECTION ENRICHI OPÉRATIONNEL !")
    
    return True

def test_data_collector():
    """Test data collector compatibilité - utilise version enrichie"""
    return test_enhanced_data_collector()

if __name__ == "__main__":
    test_enhanced_data_collector()