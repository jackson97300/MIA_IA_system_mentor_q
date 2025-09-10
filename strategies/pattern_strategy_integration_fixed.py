#!/usr/bin/env python3
"""
Pattern Strategy Integration - Version Corrigée
==============================================

Version corrigée de l'intégration des pattern strategies qui résout les problèmes
de compatibilité avec le système existant.
"""

import sys
import os
import time
import pandas as pd
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from datetime import datetime

# Ajouter le répertoire parent au path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from core.logger import get_logger
except ImportError:
    import logging
    def get_logger(name):
        return logging.getLogger(name)

logger = get_logger(__name__)

@dataclass
class MarketData:
    """Structure de données de marché compatible avec le système existant"""
    timestamp: pd.Timestamp
    symbol: str
    price: float
    volume: float
    high: float
    low: float
    open: float
    close: float
    tick_size: float = 0.25

@dataclass
class PatternSignalResult:
    """Résultat d'un signal pattern adapté au système principal"""
    signal_type: str = "PATTERN"
    side: str = "NONE"
    confidence: float = 0.0
    entry_price: float = 0.0
    stop_loss: float = 0.0
    take_profit: List[float] = None
    strategy_name: str = ""
    reason: str = ""
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.take_profit is None:
            self.take_profit = []
        if self.metadata is None:
            self.metadata = {}

class PatternStrategyIntegrationFixed:
    """
    Intégration corrigée des pattern strategies dans le système MIA principal.
    
    Cette version résout les problèmes de compatibilité avec le système existant.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialisation de l'intégration corrigée"""
        self.config = config or {}
        
        # Configuration des pattern strategies
        self.pattern_config = {
            'pattern_cooldown_sec': self.config.get('pattern_cooldown_sec', 60),
            'min_pattern_confidence': self.config.get('min_pattern_confidence', 0.60),
            'min_confluence_execution': self.config.get('min_confluence_execution', 0.70),
        }
        
        # Import des pattern strategies individuelles
        self.pattern_strategies = self._load_pattern_strategies()
        
        # Statistiques
        self.stats = {
            'total_analyses': 0,
            'signals_generated': 0,
            'signals_executed': 0,
            'last_signal_time': None,
            'active_patterns': []
        }
        
        logger.info("PatternStrategyIntegrationFixed initialisé avec succès")
    
    def _load_pattern_strategies(self) -> List[Any]:
        """Charge les pattern strategies individuelles"""
        strategies = []
        
        try:
            from strategies.gamma_pin_reversion import GammaPinReversion
            strategies.append(GammaPinReversion())
        except ImportError:
            logger.warning("GammaPinReversion non disponible")
        
        try:
            from strategies.dealer_flip_breakout import DealerFlipBreakout
            strategies.append(DealerFlipBreakout())
        except ImportError:
            logger.warning("DealerFlipBreakout non disponible")
        
        try:
            from strategies.liquidity_sweep_reversal import LiquiditySweepReversal
            strategies.append(LiquiditySweepReversal())
        except ImportError:
            logger.warning("LiquiditySweepReversal non disponible")
        
        try:
            from strategies.stacked_imbalance_continuation import StackedImbalanceContinuation
            strategies.append(StackedImbalanceContinuation())
        except ImportError:
            logger.warning("StackedImbalanceContinuation non disponible")
        
        try:
            from strategies.iceberg_tracker_follow import IcebergTrackerFollow
            strategies.append(IcebergTrackerFollow())
        except ImportError:
            logger.warning("IcebergTrackerFollow non disponible")
        
        try:
            from strategies.cvd_divergence_trap import CvdDivergenceTrap
            strategies.append(CvdDivergenceTrap())
        except ImportError:
            logger.warning("CvdDivergenceTrap non disponible")
        
        try:
            from strategies.opening_drive_fail import OpeningDriveFail
            strategies.append(OpeningDriveFail())
        except ImportError:
            logger.warning("OpeningDriveFail non disponible")
        
        try:
            from strategies.es_nq_lead_lag_mirror import EsNqLeadLagMirror
            strategies.append(EsNqLeadLagMirror())
        except ImportError:
            logger.warning("EsNqLeadLagMirror non disponible")
        
        try:
            from strategies.vwap_band_squeeze_break import VwapBandSqueezeBreak
            strategies.append(VwapBandSqueezeBreak())
        except ImportError:
            logger.warning("VwapBandSqueezeBreak non disponible")
        
        try:
            from strategies.profile_gap_fill import ProfileGapFill
            strategies.append(ProfileGapFill())
        except ImportError:
            logger.warning("ProfileGapFill non disponible")
        
        logger.info(f"Pattern strategies chargées: {len(strategies)}/10")
        return strategies
    
    def analyze_market_data(self, market_data: Dict[str, Any]) -> Optional[PatternSignalResult]:
        """
        Analyse les données de marché et génère un signal pattern.
        
        Args:
            market_data: Données de marché du système principal
            
        Returns:
            PatternSignalResult ou None si aucun signal
        """
        try:
            # Conversion des données de marché en format compatible
            compatible_data = self._convert_to_compatible_format(market_data)
            
            # Analyse avec chaque pattern strategy
            best_signal = None
            best_score = 0.0
            
            for strategy in self.pattern_strategies:
                try:
                    # Vérification des prérequis
                    if not strategy.should_run(compatible_data):
                        continue
                    
                    # Génération du signal
                    signal = strategy.generate(compatible_data)
                    
                    if signal and isinstance(signal, dict):
                        # Calcul du score
                        score = self._calculate_signal_score(signal, compatible_data)
                        
                        if score > best_score and score >= self.pattern_config['min_pattern_confidence']:
                            best_signal = signal
                            best_score = score
                            
                except Exception as e:
                    logger.warning(f"Erreur strategy {strategy.name}: {e}")
                    continue
            
            # Mise à jour des statistiques
            self.stats['total_analyses'] += 1
            
            if best_signal:
                # Conversion en PatternSignalResult
                pattern_signal = PatternSignalResult(
                    signal_type="PATTERN",
                    side=best_signal.get("side", "NONE"),
                    confidence=best_signal.get("confidence", 0.0),
                    entry_price=best_signal.get("entry", 0.0),
                    stop_loss=best_signal.get("stop", 0.0),
                    take_profit=best_signal.get("targets", []),
                    strategy_name=best_signal.get("strategy", "unknown"),
                    reason=best_signal.get("reason", ""),
                    metadata=best_signal.get("metadata", {})
                )
                
                # Mise à jour des statistiques
                self.stats['signals_generated'] += 1
                self.stats['last_signal_time'] = datetime.now()
                self.stats['active_patterns'] = [pattern_signal.strategy_name]
                
                logger.info(f"Signal pattern généré: {pattern_signal.strategy_name} {pattern_signal.side} @ {pattern_signal.entry_price}")
                
                return pattern_signal
            
            return None
            
        except Exception as e:
            logger.error(f"Erreur analyse pattern strategies: {e}")
            return None
    
    def _convert_to_compatible_format(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convertit les données de marché en format compatible avec les pattern strategies.
        
        Args:
            market_data: Données de marché du système principal
            
        Returns:
            Dict au format attendu par les pattern strategies
        """
        # Extraction des données de base
        price = market_data.get('price', 4500.0)
        volume = market_data.get('volume', 1000.0)
        symbol = market_data.get('symbol', 'ES')
        tick_size = market_data.get('tick_size', 0.25)
        
        # Création du contexte compatible
        ctx = {
            "symbol": symbol,
            "tick_size": tick_size,
            "price": {"last": price},
            "atr": 2.0,  # Valeur par défaut
            "vwap": {
                "vwap": price - 2.0,
                "sd1_up": price + 2.0,
                "sd1_dn": price - 6.0,
                "sd2_up": price + 6.0,
                "sd2_dn": price - 10.0,
                "sd3_up": price + 10.0,
                "sd3_dn": price - 14.0,
            },
            "vva": {
                "vpoc": price - 3.0,
                "vah": price + 5.0,
                "val": price - 5.0,
                "lvn_low": price - 2.0,
                "lvn_high": price + 2.0,
            },
            "menthorq": {
                "nearest_wall": {"type": "CALL", "price": price + 6.0, "dist_ticks": 24},
                "gamma_flip": False
            },
            "orderflow": {
                "delta_burst": False,
                "delta_flip": False,
                "cvd": 0.0,
                "cvd_divergence": False,
                "stacked_imbalance": {"side": "BUY", "rows": 0},
                "absorption": None,
                "iceberg": None,
            },
            "quotes": {"speed_up": False},
            "correlation": {"es_nq": 0.9, "leader": "ES"},
            "vix": {"last": 14.0, "rising": False},
            "session": {"label": "OTHER", "time_ok": True},
            "basedata": {"last_wick_ticks": 0},
        }
        
        # Enrichissement avec les données disponibles
        if 'market_data' in market_data:
            market_info = market_data['market_data']
            if 'vwap' in market_info:
                ctx['vwap']['vwap'] = market_info['vwap']
            if 'sd1_up' in market_info:
                ctx['vwap']['sd1_up'] = market_info['sd1_up']
            if 'sd1_dn' in market_info:
                ctx['vwap']['sd1_dn'] = market_info['sd1_dn']
        
        if 'structure_data' in market_data:
            structure = market_data['structure_data']
            if 'menthorq' in structure:
                ctx['menthorq'].update(structure['menthorq'])
            if 'orderflow' in structure:
                ctx['orderflow'].update(structure['orderflow'])
        
        return ctx
    
    def _calculate_signal_score(self, signal: Dict[str, Any], ctx: Dict[str, Any]) -> float:
        """
        Calcule un score pour le signal basé sur plusieurs facteurs.
        
        Args:
            signal: Signal généré par une strategy
            ctx: Contexte de marché
            
        Returns:
            Score entre 0.0 et 1.0
        """
        base_confidence = signal.get("confidence", 0.0)
        
        # Boost basé sur le contexte de marché
        score = base_confidence
        
        # Boost si gamma flip
        if ctx.get("menthorq", {}).get("gamma_flip", False):
            score += 0.05
        
        # Boost si delta burst
        if ctx.get("orderflow", {}).get("delta_burst", False):
            score += 0.03
        
        # Boost si session favorable
        session = ctx.get("session", {}).get("label", "OTHER")
        if session in ["OPEN", "POWER"]:
            score += 0.02
        
        # Pénalité si VIX en hausse
        if ctx.get("vix", {}).get("rising", False):
            score -= 0.02
        
        return max(0.0, min(1.0, score))
    
    def get_system_status(self) -> Dict[str, Any]:
        """Retourne le statut du système d'intégration"""
        return {
            'integration_status': 'ACTIVE',
            'pattern_strategies_count': len(self.pattern_strategies),
            'active_strategies': [s.name for s in self.pattern_strategies],
            'total_analyses': self.stats['total_analyses'],
            'signals_generated': self.stats['signals_generated'],
            'signals_executed': self.stats['signals_executed'],
            'last_signal_time': self.stats['last_signal_time'].isoformat() if self.stats['last_signal_time'] else None,
            'active_patterns': self.stats['active_patterns'],
            'configuration': self.pattern_config
        }
    
    def update_config(self, new_config: Dict[str, Any]) -> None:
        """Met à jour la configuration"""
        self.config.update(new_config)
        self.pattern_config.update({
            'pattern_cooldown_sec': self.config.get('pattern_cooldown_sec', 60),
            'min_pattern_confidence': self.config.get('min_pattern_confidence', 0.60),
            'min_confluence_execution': self.config.get('min_confluence_execution', 0.70),
        })
        logger.info("Configuration mise à jour")
    
    def record_signal_execution(self, signal_result: PatternSignalResult, executed: bool) -> None:
        """Enregistre l'exécution d'un signal"""
        if executed:
            self.stats['signals_executed'] += 1
            logger.info(f"Signal exécuté: {signal_result.strategy_name} {signal_result.side}")

# === FACTORY FUNCTIONS ===

def create_pattern_strategy_integration_fixed(config: Optional[Dict[str, Any]] = None) -> PatternStrategyIntegrationFixed:
    """Factory function pour créer l'intégration corrigée"""
    return PatternStrategyIntegrationFixed(config)

# === INTEGRATION HELPER FUNCTIONS ===

def convert_pattern_signal_to_main_format(pattern_signal: PatternSignalResult) -> Dict[str, Any]:
    """
    Convertit un PatternSignalResult au format attendu par le système principal.
    """
    return {
        'type': 'PATTERN',
        'side': pattern_signal.side,
        'confidence': pattern_signal.confidence,
        'entry': pattern_signal.entry_price,
        'stop': pattern_signal.stop_loss,
        'targets': pattern_signal.take_profit,
        'strategy': pattern_signal.strategy_name,
        'reason': pattern_signal.reason,
        'metadata': pattern_signal.metadata,
        'timestamp': datetime.now().isoformat()
    }

def is_pattern_signal_valid(signal: PatternSignalResult, min_confidence: float = 0.60) -> bool:
    """
    Valide un signal pattern selon les critères du système principal.
    """
    if not signal:
        return False
    
    # Validation de la confiance
    if signal.confidence < min_confidence:
        return False
    
    # Validation du ratio R:R
    if signal.stop_loss and signal.take_profit:
        risk = abs(signal.entry_price - signal.stop_loss)
        reward = abs(max(signal.take_profit) - signal.entry_price) if signal.take_profit else 0
        
        if risk > 0 and reward / risk < 1.0:  # R:R minimum 1:1
            return False
    
    # Validation des niveaux
    if signal.entry_price <= 0 or signal.stop_loss <= 0:
        return False
    
    return True

# === TESTING ===

def test_fixed_integration():
    """Test de l'intégration corrigée"""
    logger.info("TEST PATTERN STRATEGY INTEGRATION FIXED")
    print("=" * 60)
    
    # Création de l'intégration
    config = {
        'pattern_cooldown_sec': 30,
        'min_pattern_confidence': 0.55,
        'min_confluence_execution': 0.65,
    }
    
    integration = create_pattern_strategy_integration_fixed(config)
    
    # Test avec données de marché simulées
    market_data = {
        'symbol': 'ES',
        'price': 4500.0,
        'volume': 2000.0,
        'tick_size': 0.25,
        'market_data': {
            'vwap': 4498.0,
            'sd1_up': 4502.0,
            'sd1_dn': 4494.0,
        },
        'structure_data': {
            'menthorq': {
                'nearest_wall': {'type': 'CALL', 'price': 4505.0, 'dist_ticks': 20},
                'gamma_flip': False
            },
            'orderflow': {
                'delta_burst': False,
                'stacked_imbalance': {'side': 'BUY', 'rows': 0},
                'absorption': None,
            }
        }
    }
    
    # Analyse
    signal = integration.analyze_market_data(market_data)
    
    if signal:
        print(f"✅ Signal généré: {signal.strategy_name}")
        print(f"   Side: {signal.side}")
        print(f"   Entry: {signal.entry_price}")
        print(f"   Stop: {signal.stop_loss}")
        print(f"   Targets: {signal.take_profit}")
        print(f"   Confidence: {signal.confidence}")
        print(f"   Reason: {signal.reason}")
        
        # Test de validation
        is_valid = is_pattern_signal_valid(signal)
        print(f"   Valid: {is_valid}")
        
        # Test de conversion
        main_format = convert_pattern_signal_to_main_format(signal)
        print(f"   Main format: {main_format['type']} {main_format['side']}")
    else:
        print("❌ Aucun signal généré")
    
    # Status
    status = integration.get_system_status()
    print(f"\nStatus système:")
    for key, value in status.items():
        if key != 'active_strategies':
            print(f"  • {key}: {value}")
    
    logger.info("TEST PATTERN STRATEGY INTEGRATION FIXED TERMINÉ")
    return True

if __name__ == "__main__":
    test_fixed_integration()
