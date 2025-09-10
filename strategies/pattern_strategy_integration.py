#!/usr/bin/env python3
"""
Pattern Strategy Integration Bridge
===================================

Pont d'intégration entre les 10 nouvelles pattern strategies et le système MIA principal.
Ce module adapte l'interface des pattern strategies au format attendu par le système principal.
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

# Imports des pattern strategies
from strategies.strategy_selector_integrated import (
    IntegratedStrategySelector, TradingContext, create_integrated_strategy_selector
)

logger = get_logger(__name__)

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

class PatternStrategyIntegration:
    """
    Intégration des pattern strategies dans le système MIA principal.
    
    Cette classe adapte les signaux des pattern strategies au format
    attendu par le système de trading principal.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialisation de l'intégration"""
        self.config = config or {}
        
        # Configuration des pattern strategies
        pattern_config = {
            'pattern_fire_cooldown_sec': self.config.get('pattern_cooldown_sec', 60),
            'min_pattern_confidence': self.config.get('min_pattern_confidence', 0.60),
            'min_confluence_execution': self.config.get('min_confluence_execution', 0.70),
        }
        
        # Initialisation du selector intégré
        self.selector = create_integrated_strategy_selector(pattern_config)
        
        # Statistiques
        self.stats = {
            'total_analyses': 0,
            'signals_generated': 0,
            'signals_executed': 0,
            'last_signal_time': None,
            'active_patterns': []
        }
        
        logger.info("PatternStrategyIntegration initialisé avec succès")
    
    def analyze_market_data(self, market_data: Dict[str, Any]) -> Optional[PatternSignalResult]:
        """
        Analyse les données de marché et génère un signal pattern.
        
        Args:
            market_data: Données de marché du système principal
            
        Returns:
            PatternSignalResult ou None si aucun signal
        """
        try:
            # Conversion des données de marché en TradingContext
            trading_context = self._convert_market_data_to_context(market_data)
            
            # Analyse avec le selector intégré
            result = self.selector.analyze_and_select(trading_context)
            
            # Mise à jour des statistiques
            self.stats['total_analyses'] += 1
            
            # Conversion du résultat en PatternSignalResult
            if result.signal_generated and result.final_decision.value == "execute_signal":
                pattern_signal = result.pattern_signal
                
                signal_result = PatternSignalResult(
                    signal_type="PATTERN",
                    side=pattern_signal.side,
                    confidence=pattern_signal.confidence,
                    entry_price=pattern_signal.entry,
                    stop_loss=pattern_signal.stop,
                    take_profit=pattern_signal.targets,
                    strategy_name=pattern_signal.strategy,
                    reason=pattern_signal.reason,
                    metadata={
                        'market_regime': result.market_regime,
                        'regime_confidence': result.regime_confidence,
                        'confluence_score': result.confluence_score,
                        'patterns_considered': result.patterns_considered,
                        'processing_time_ms': result.total_processing_time_ms,
                        'timestamp': result.timestamp.isoformat()
                    }
                )
                
                # Mise à jour des statistiques
                self.stats['signals_generated'] += 1
                self.stats['last_signal_time'] = datetime.now()
                self.stats['active_patterns'] = result.patterns_considered
                
                logger.info(f"Signal pattern généré: {pattern_signal.strategy} {pattern_signal.side} @ {pattern_signal.entry}")
                
                return signal_result
            
            return None
            
        except Exception as e:
            logger.error(f"Erreur analyse pattern strategies: {e}")
            return None
    
    def _convert_market_data_to_context(self, market_data: Dict[str, Any]) -> TradingContext:
        """
        Convertit les données de marché du système principal en TradingContext.
        
        Args:
            market_data: Données de marché du système principal
            
        Returns:
            TradingContext pour les pattern strategies
        """
        # Extraction des données de base
        timestamp = pd.Timestamp.now()
        symbol = market_data.get('symbol', 'ES')
        price = market_data.get('price', 4500.0)
        volume = market_data.get('volume', 1000.0)
        tick_size = market_data.get('tick_size', 0.25)
        
        # Création du contexte de base
        context = TradingContext(
            timestamp=timestamp,
            symbol=symbol,
            price=price,
            volume=volume,
            tick_size=tick_size
        )
        
        # Ajout des données optionnelles si disponibles
        if 'market_data' in market_data:
            context.market_data = market_data['market_data']
        
        if 'structure_data' in market_data:
            context.structure_data = market_data['structure_data']
        
        if 'es_nq_data' in market_data:
            context.es_nq_data = market_data['es_nq_data']
        
        if 'sierra_patterns' in market_data:
            context.sierra_patterns = market_data['sierra_patterns']
        
        return context
    
    def get_system_status(self) -> Dict[str, Any]:
        """Retourne le statut du système d'intégration"""
        selector_status = self.selector.get_system_status()
        
        return {
            'integration_status': 'ACTIVE',
            'pattern_strategies_count': selector_status['pattern_strategies_count'],
            'active_strategies': selector_status['active_strategies'],
            'total_analyses': self.stats['total_analyses'],
            'signals_generated': self.stats['signals_generated'],
            'signals_executed': self.stats['signals_executed'],
            'last_signal_time': self.stats['last_signal_time'].isoformat() if self.stats['last_signal_time'] else None,
            'active_patterns': self.stats['active_patterns'],
            'avg_processing_time_ms': selector_status['avg_processing_time_ms'],
            'system_components': selector_status['system_components']
        }
    
    def update_config(self, new_config: Dict[str, Any]) -> None:
        """Met à jour la configuration"""
        self.config.update(new_config)
        
        # Recréer le selector avec la nouvelle config
        pattern_config = {
            'pattern_fire_cooldown_sec': self.config.get('pattern_cooldown_sec', 60),
            'min_pattern_confidence': self.config.get('min_pattern_confidence', 0.60),
            'min_confluence_execution': self.config.get('min_confluence_execution', 0.70),
        }
        
        self.selector = create_integrated_strategy_selector(pattern_config)
        logger.info("Configuration mise à jour")
    
    def record_signal_execution(self, signal_result: PatternSignalResult, executed: bool) -> None:
        """Enregistre l'exécution d'un signal"""
        if executed:
            self.stats['signals_executed'] += 1
            logger.info(f"Signal exécuté: {signal_result.strategy_name} {signal_result.side}")

# === FACTORY FUNCTIONS ===

def create_pattern_strategy_integration(config: Optional[Dict[str, Any]] = None) -> PatternStrategyIntegration:
    """Factory function pour créer l'intégration des pattern strategies"""
    return PatternStrategyIntegration(config)

# === INTEGRATION HELPER FUNCTIONS ===

def convert_pattern_signal_to_main_format(pattern_signal: PatternSignalResult) -> Dict[str, Any]:
    """
    Convertit un PatternSignalResult au format attendu par le système principal.
    
    Args:
        pattern_signal: Signal des pattern strategies
        
    Returns:
        Dict au format du système principal
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
    
    Args:
        signal: Signal à valider
        min_confidence: Confiance minimale requise
        
    Returns:
        True si le signal est valide
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

def test_pattern_integration():
    """Test de l'intégration des pattern strategies"""
    logger.info("TEST PATTERN STRATEGY INTEGRATION")
    print("=" * 50)
    
    # Création de l'intégration
    config = {
        'pattern_cooldown_sec': 30,
        'min_pattern_confidence': 0.55,
        'min_confluence_execution': 0.65,
    }
    
    integration = create_pattern_strategy_integration(config)
    
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
    
    logger.info("TEST PATTERN STRATEGY INTEGRATION TERMINÉ")
    return True

if __name__ == "__main__":
    test_pattern_integration()
