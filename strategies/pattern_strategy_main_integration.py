#!/usr/bin/env python3
"""
Pattern Strategy Main System Integration
========================================

Intégration complète des 10 pattern strategies dans le système MIA principal.
Ce module remplace/étend le signal generator existant avec les nouvelles stratégies.
"""

import sys
import os
import time
import asyncio
import pandas as pd
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging

# Ajouter le répertoire parent au path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from core.logger import get_logger
except ImportError:
    import logging
    def get_logger(name):
        return logging.getLogger(name)

# Import de l'intégration des pattern strategies
from strategies.pattern_strategy_integration import (
    PatternStrategyIntegration, PatternSignalResult, 
    create_pattern_strategy_integration, convert_pattern_signal_to_main_format,
    is_pattern_signal_valid
)

logger = get_logger(__name__)

class PatternStrategyMainIntegration:
    """
    Intégration principale des pattern strategies dans le système MIA.
    
    Cette classe remplace/étend le signal generator existant et s'intègre
    parfaitement dans le pipeline de trading principal.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialisation de l'intégration principale"""
        self.config = config or {}
        
        # Configuration des pattern strategies
        pattern_config = {
            'pattern_cooldown_sec': self.config.get('pattern_cooldown_sec', 60),
            'min_pattern_confidence': self.config.get('min_pattern_confidence', 0.60),
            'min_confluence_execution': self.config.get('min_confluence_execution', 0.70),
            'max_daily_signals': self.config.get('max_daily_signals', 10),
            'risk_per_trade': self.config.get('risk_per_trade', 0.02),  # 2% du capital
        }
        
        # Initialisation de l'intégration des pattern strategies
        self.pattern_integration = create_pattern_strategy_integration(pattern_config)
        
        # Statistiques et monitoring
        self.stats = {
            'total_analyses': 0,
            'signals_generated': 0,
            'signals_executed': 0,
            'signals_rejected': 0,
            'daily_signals': 0,
            'last_signal_time': None,
            'last_reset_date': datetime.now().date(),
            'performance_metrics': {
                'win_rate': 0.0,
                'profit_factor': 0.0,
                'avg_rr_ratio': 0.0,
                'max_drawdown': 0.0,
            }
        }
        
        # Cache pour éviter les recalculs
        self.last_analysis_time = None
        self.analysis_cache = {}
        self.cache_duration_sec = 5  # Cache de 5 secondes
        
        logger.info("PatternStrategyMainIntegration initialisé avec succès")
    
    async def generate_signal(self, market_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Génère un signal de trading en utilisant les pattern strategies.
        
        Args:
            market_data: Données de marché du système principal
            
        Returns:
            Dict contenant le signal ou None si aucun signal
        """
        try:
            # Vérification du cache
            if self._is_cache_valid():
                cached_signal = self._get_cached_signal(market_data)
                if cached_signal:
                    return cached_signal
            
            # Vérification des limites quotidiennes
            if not self._check_daily_limits():
                logger.info("Limite quotidienne de signaux atteinte")
                return None
            
            # Analyse avec les pattern strategies
            pattern_signal = self.pattern_integration.analyze_market_data(market_data)
            
            # Mise à jour des statistiques
            self.stats['total_analyses'] += 1
            
            if pattern_signal:
                # Validation du signal
                if not is_pattern_signal_valid(pattern_signal, self.config.get('min_pattern_confidence', 0.60)):
                    self.stats['signals_rejected'] += 1
                    logger.info(f"Signal rejeté: {pattern_signal.strategy_name} - validation échouée")
                    return None
                
                # Conversion au format du système principal
                main_signal = convert_pattern_signal_to_main_format(pattern_signal)
                
                # Enrichissement avec des métadonnées système
                main_signal.update({
                    'source': 'PATTERN_STRATEGIES',
                    'integration_version': '1.0.0',
                    'generation_time': datetime.now().isoformat(),
                    'system_confidence': self._calculate_system_confidence(pattern_signal),
                    'risk_metrics': self._calculate_risk_metrics(pattern_signal),
                    'market_context': self._extract_market_context(market_data),
                })
                
                # Mise à jour des statistiques
                self.stats['signals_generated'] += 1
                self.stats['daily_signals'] += 1
                self.stats['last_signal_time'] = datetime.now()
                
                # Mise en cache
                self._cache_signal(market_data, main_signal)
                
                logger.info(f"Signal pattern généré: {pattern_signal.strategy_name} {pattern_signal.side} @ {pattern_signal.entry_price}")
                
                return main_signal
            
            return None
            
        except Exception as e:
            logger.error(f"Erreur génération signal pattern: {e}")
            return None
    
    def _is_cache_valid(self) -> bool:
        """Vérifie si le cache est encore valide"""
        if not self.last_analysis_time:
            return False
        
        return (datetime.now() - self.last_analysis_time).total_seconds() < self.cache_duration_sec
    
    def _get_cached_signal(self, market_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Récupère un signal depuis le cache"""
        # Clé de cache basée sur les données de marché principales
        cache_key = self._generate_cache_key(market_data)
        return self.analysis_cache.get(cache_key)
    
    def _cache_signal(self, market_data: Dict[str, Any], signal: Dict[str, Any]) -> None:
        """Met en cache un signal"""
        cache_key = self._generate_cache_key(market_data)
        self.analysis_cache[cache_key] = signal
        self.last_analysis_time = datetime.now()
    
    def _generate_cache_key(self, market_data: Dict[str, Any]) -> str:
        """Génère une clé de cache basée sur les données de marché"""
        price = market_data.get('price', 0)
        volume = market_data.get('volume', 0)
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        return f"{price}_{volume}_{timestamp}"
    
    def _check_daily_limits(self) -> bool:
        """Vérifie les limites quotidiennes"""
        today = datetime.now().date()
        
        # Reset quotidien
        if self.stats['last_reset_date'] != today:
            self.stats['daily_signals'] = 0
            self.stats['last_reset_date'] = today
        
        # Vérification de la limite
        max_daily = self.config.get('max_daily_signals', 10)
        return self.stats['daily_signals'] < max_daily
    
    def _calculate_system_confidence(self, pattern_signal: PatternSignalResult) -> float:
        """Calcule la confiance système basée sur plusieurs facteurs"""
        base_confidence = pattern_signal.confidence
        
        # Boost basé sur les performances historiques
        performance_boost = min(0.1, self.stats['performance_metrics']['win_rate'] * 0.1)
        
        # Boost basé sur la fréquence d'utilisation
        frequency_boost = min(0.05, self.stats['signals_generated'] * 0.001)
        
        # Pénalité si trop de signaux récents
        recent_penalty = 0.0
        if self.stats['last_signal_time']:
            time_since_last = (datetime.now() - self.stats['last_signal_time']).total_seconds()
            if time_since_last < 300:  # 5 minutes
                recent_penalty = 0.05
        
        system_confidence = base_confidence + performance_boost + frequency_boost - recent_penalty
        return max(0.0, min(1.0, system_confidence))
    
    def _calculate_risk_metrics(self, pattern_signal: PatternSignalResult) -> Dict[str, Any]:
        """Calcule les métriques de risque"""
        risk = abs(pattern_signal.entry_price - pattern_signal.stop_loss)
        reward = 0.0
        
        if pattern_signal.take_profit:
            max_target = max(pattern_signal.take_profit)
            reward = abs(max_target - pattern_signal.entry_price)
        
        rr_ratio = reward / risk if risk > 0 else 0.0
        
        return {
            'risk_points': risk,
            'reward_points': reward,
            'rr_ratio': rr_ratio,
            'risk_percentage': self.config.get('risk_per_trade', 0.02),
            'position_size_suggestion': self._calculate_position_size(risk),
        }
    
    def _calculate_position_size(self, risk_points: float) -> int:
        """Calcule la taille de position suggérée"""
        if risk_points <= 0:
            return 1
        
        # Calcul basé sur le risque par trade
        risk_per_trade = self.config.get('risk_per_trade', 0.02)
        account_value = self.config.get('account_value', 100000)  # Valeur par défaut
        
        max_risk_amount = account_value * risk_per_trade
        position_size = int(max_risk_amount / risk_points)
        
        # Limites de position
        min_size = 1
        max_size = self.config.get('max_position_size', 10)
        
        return max(min_size, min(max_size, position_size))
    
    def _extract_market_context(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extrait le contexte de marché pour les métadonnées"""
        return {
            'symbol': market_data.get('symbol', 'ES'),
            'price': market_data.get('price', 0),
            'volume': market_data.get('volume', 0),
            'timestamp': datetime.now().isoformat(),
            'market_session': self._get_market_session(),
            'volatility_regime': self._get_volatility_regime(market_data),
        }
    
    def _get_market_session(self) -> str:
        """Détermine la session de marché actuelle"""
        now = datetime.now()
        hour = now.hour
        
        if 9 <= hour < 12:
            return 'OPEN'
        elif 12 <= hour < 14:
            return 'LUNCH'
        elif 14 <= hour < 16:
            return 'POWER'
        else:
            return 'OTHER'
    
    def _get_volatility_regime(self, market_data: Dict[str, Any]) -> str:
        """Détermine le régime de volatilité"""
        # Logique simplifiée - à adapter selon vos données
        volume = market_data.get('volume', 0)
        
        if volume > 2000:
            return 'HIGH'
        elif volume > 1000:
            return 'MEDIUM'
        else:
            return 'LOW'
    
    async def record_trade_result(self, signal: Dict[str, Any], result: Dict[str, Any]) -> None:
        """Enregistre le résultat d'un trade pour les statistiques"""
        try:
            # Mise à jour des statistiques de performance
            if result.get('executed', False):
                self.stats['signals_executed'] += 1
                
                # Calcul des métriques de performance
                pnl = result.get('pnl', 0)
                win = pnl > 0
                
                # Mise à jour du win rate (moyenne mobile)
                current_win_rate = self.stats['performance_metrics']['win_rate']
                new_win_rate = (current_win_rate * 0.9) + (1.0 if win else 0.0) * 0.1
                self.stats['performance_metrics']['win_rate'] = new_win_rate
                
                # Mise à jour du profit factor
                if 'total_profit' not in self.stats['performance_metrics']:
                    self.stats['performance_metrics']['total_profit'] = 0
                    self.stats['performance_metrics']['total_loss'] = 0
                
                if pnl > 0:
                    self.stats['performance_metrics']['total_profit'] += pnl
                else:
                    self.stats['performance_metrics']['total_loss'] += abs(pnl)
                
                total_profit = self.stats['performance_metrics']['total_profit']
                total_loss = self.stats['performance_metrics']['total_loss']
                
                if total_loss > 0:
                    self.stats['performance_metrics']['profit_factor'] = total_profit / total_loss
                
                logger.info(f"Trade enregistré: {signal.get('strategy', 'unknown')} - PnL: {pnl}")
            
        except Exception as e:
            logger.error(f"Erreur enregistrement trade: {e}")
    
    def get_system_status(self) -> Dict[str, Any]:
        """Retourne le statut complet du système"""
        pattern_status = self.pattern_integration.get_system_status()
        
        return {
            'integration_status': 'ACTIVE',
            'pattern_strategies': pattern_status,
            'main_integration_stats': self.stats,
            'configuration': {
                'pattern_cooldown_sec': self.config.get('pattern_cooldown_sec', 60),
                'min_pattern_confidence': self.config.get('min_pattern_confidence', 0.60),
                'max_daily_signals': self.config.get('max_daily_signals', 10),
                'risk_per_trade': self.config.get('risk_per_trade', 0.02),
            },
            'cache_status': {
                'cache_duration_sec': self.cache_duration_sec,
                'last_analysis_time': self.last_analysis_time.isoformat() if self.last_analysis_time else None,
                'cache_size': len(self.analysis_cache),
            }
        }
    
    def update_config(self, new_config: Dict[str, Any]) -> None:
        """Met à jour la configuration"""
        self.config.update(new_config)
        self.pattern_integration.update_config(new_config)
        logger.info("Configuration mise à jour")
    
    def reset_daily_stats(self) -> None:
        """Reset les statistiques quotidiennes"""
        self.stats['daily_signals'] = 0
        self.stats['last_reset_date'] = datetime.now().date()
        logger.info("Statistiques quotidiennes réinitialisées")

# === FACTORY FUNCTIONS ===

def create_pattern_strategy_main_integration(config: Optional[Dict[str, Any]] = None) -> PatternStrategyMainIntegration:
    """Factory function pour créer l'intégration principale"""
    return PatternStrategyMainIntegration(config)

# === INTEGRATION HELPER FUNCTIONS ===

def create_main_system_config() -> Dict[str, Any]:
    """Crée une configuration optimisée pour le système principal"""
    return {
        'pattern_cooldown_sec': 60,
        'min_pattern_confidence': 0.65,
        'min_confluence_execution': 0.70,
        'max_daily_signals': 8,
        'risk_per_trade': 0.02,
        'max_position_size': 5,
        'account_value': 100000,
        'cache_duration_sec': 5,
    }

# === TESTING ===

async def test_main_integration():
    """Test de l'intégration principale"""
    logger.info("TEST PATTERN STRATEGY MAIN INTEGRATION")
    print("=" * 60)
    
    # Création de l'intégration
    config = create_main_system_config()
    integration = create_pattern_strategy_main_integration(config)
    
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
    
    # Génération de signal
    signal = await integration.generate_signal(market_data)
    
    if signal:
        print(f"✅ Signal généré: {signal['strategy']}")
        print(f"   Type: {signal['type']}")
        print(f"   Side: {signal['side']}")
        print(f"   Entry: {signal['entry']}")
        print(f"   Stop: {signal['stop']}")
        print(f"   Targets: {signal['targets']}")
        print(f"   Confidence: {signal['confidence']}")
        print(f"   System Confidence: {signal['system_confidence']}")
        print(f"   Risk Metrics: {signal['risk_metrics']}")
        print(f"   Market Context: {signal['market_context']}")
        
        # Test d'enregistrement de trade
        trade_result = {
            'executed': True,
            'pnl': 150.0,
            'exit_price': 4505.0,
            'exit_time': datetime.now().isoformat()
        }
        
        await integration.record_trade_result(signal, trade_result)
        print(f"   Trade enregistré: PnL = {trade_result['pnl']}")
    else:
        print("❌ Aucun signal généré")
    
    # Status
    status = integration.get_system_status()
    print(f"\nStatus système:")
    print(f"  • Intégration: {status['integration_status']}")
    print(f"  • Analyses totales: {status['main_integration_stats']['total_analyses']}")
    print(f"  • Signaux générés: {status['main_integration_stats']['signals_generated']}")
    print(f"  • Signaux exécutés: {status['main_integration_stats']['signals_executed']}")
    print(f"  • Win rate: {status['main_integration_stats']['performance_metrics']['win_rate']:.2%}")
    print(f"  • Profit factor: {status['main_integration_stats']['performance_metrics']['profit_factor']:.2f}")
    
    logger.info("TEST PATTERN STRATEGY MAIN INTEGRATION TERMINÉ")
    return True

if __name__ == "__main__":
    asyncio.run(test_main_integration())


