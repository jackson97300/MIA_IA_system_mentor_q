#!/usr/bin/env python3
"""
🧮 CALCUL CORRÉLATION ES/NQ RÉELLE - MIA_IA_SYSTEM
Calcule la vraie corrélation entre ES et NQ pour améliorer les signaux
Intégration avec la logique de test_ibkr_corrige.py
"""

import sys
import numpy as np
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Tuple
from collections import deque

# Ajouter le chemin du projet
sys.path.append(str(Path(__file__).parent))

from core.logger import get_logger

logger = get_logger(__name__)

class ESNQCorrelationCalculator:
    """Calculateur de corrélation ES/NQ en temps réel avec logique IBKR robuste"""
    
    def __init__(self, window_size: int = 50):
        self.window_size = window_size
        self.es_prices = deque(maxlen=window_size)
        self.nq_prices = deque(maxlen=window_size)
        self.es_returns = deque(maxlen=window_size)
        self.nq_returns = deque(maxlen=window_size)
        self.correlation_history = deque(maxlen=100)
        self.correlation_ratios = deque(maxlen=100)  # NQ/ES ratios
        
    def add_price_data(self, es_price: float, nq_price: float) -> Dict[str, float]:
        """Ajoute des données de prix et calcule la corrélation"""
        try:
            # Validation des données
            if not es_price or not nq_price or es_price <= 0 or nq_price <= 0:
                logger.warning("⚠️ Données ES/NQ invalides")
                return self._get_default_correlation()
            
            # Ajouter les prix
            self.es_prices.append(es_price)
            self.nq_prices.append(nq_price)
            
            # Calculer le ratio NQ/ES (basé sur test_ibkr_corrige.py)
            correlation_ratio = nq_price / es_price
            self.correlation_ratios.append(correlation_ratio)
            
            # Calculer les returns si on a au moins 2 points
            if len(self.es_prices) >= 2:
                es_return = (es_price - self.es_prices[-2]) / self.es_prices[-2]
                nq_return = (nq_price - self.nq_prices[-2]) / self.nq_prices[-2]
                
                self.es_returns.append(es_return)
                self.nq_returns.append(nq_return)
            
            # Calculer la corrélation
            correlation_data = self._calculate_correlation()
            
            return correlation_data
            
        except Exception as e:
            logger.error(f"❌ Erreur calcul corrélation: {e}")
            return self._get_default_correlation()
    
    def _get_default_correlation(self) -> Dict[str, float]:
        """Retourne les valeurs par défaut de corrélation"""
        return {
            'correlation': 0.85,
            'divergence': 0.0,
            'leader': 'ES',
            'strength': 0.7,
            'ratio': 3.6,
            'score': 0.7
        }
    
    def _calculate_correlation(self) -> Dict[str, float]:
        """Calcule la corrélation et les métriques associées"""
        try:
            if len(self.es_returns) < 10:
                return self._get_default_correlation()
            
            # Corrélation des returns (méthode statistique)
            es_returns_array = np.array(list(self.es_returns))
            nq_returns_array = np.array(list(self.nq_returns))
            
            correlation = np.corrcoef(es_returns_array, nq_returns_array)[0, 1]
            
            # Gérer les valeurs NaN
            if np.isnan(correlation):
                correlation = 0.85
            
            # Calculer la divergence
            divergence = self._calculate_divergence()
            
            # Déterminer le leader
            leader = self._determine_leader()
            
            # Force de la corrélation
            strength = abs(correlation)
            
            # Ratio NQ/ES actuel (basé sur test_ibkr_corrige.py)
            current_ratio = self.correlation_ratios[-1] if self.correlation_ratios else 3.6
            
            # Score de corrélation normalisé (basé sur test_ibkr_corrige.py)
            # Normalisé autour de 3.6 (ratio typique NQ/ES)
            correlation_score = min(abs(current_ratio - 3.6) / 0.5, 1.0)
            
            # Sauvegarder dans l'historique
            self.correlation_history.append(correlation)
            
            return {
                'correlation': float(correlation),
                'divergence': float(divergence),
                'leader': leader,
                'strength': float(strength),
                'ratio': float(current_ratio),
                'score': float(correlation_score)
            }
            
        except Exception as e:
            logger.error(f"❌ Erreur calcul corrélation détaillé: {e}")
            return self._get_default_correlation()
    
    def _calculate_divergence(self) -> float:
        """Calcule la divergence entre ES et NQ"""
        try:
            if len(self.es_prices) < 10 or len(self.nq_prices) < 10:
                return 0.0
            
            # Calculer les moyennes mobiles
            es_ma = np.mean(list(self.es_prices)[-10:])
            nq_ma = np.mean(list(self.nq_prices)[-10:])
            
            # Normaliser les prix
            es_normalized = (self.es_prices[-1] - es_ma) / es_ma
            nq_normalized = (self.nq_prices[-1] - nq_ma) / nq_ma
            
            # Divergence = différence entre les mouvements normalisés
            divergence = es_normalized - nq_normalized
            
            return float(divergence)
            
        except Exception as e:
            logger.error(f"❌ Erreur calcul divergence: {e}")
            return 0.0
    
    def _determine_leader(self) -> str:
        """Détermine quel instrument mène (ES ou NQ)"""
        try:
            if len(self.es_returns) < 5 or len(self.nq_returns) < 5:
                return 'ES'
            
            # Calculer la volatilité des returns
            es_vol = np.std(list(self.es_returns)[-5:])
            nq_vol = np.std(list(self.nq_returns)[-5:])
            
            # L'instrument avec la plus faible volatilité mène généralement
            if es_vol < nq_vol:
                return 'ES'
            else:
                return 'NQ'
                
        except Exception as e:
            logger.error(f"❌ Erreur détermination leader: {e}")
            return 'ES'
    
    def get_correlation_score(self) -> float:
        """Retourne un score de corrélation pour la confluence"""
        try:
            if not self.correlation_history:
                return 0.7
            
            # Moyenne des 10 dernières corrélations
            recent_corr = list(self.correlation_history)[-10:]
            avg_correlation = np.mean(recent_corr)
            
            # Score normalisé entre 0 et 1
            # Corrélation de 0.8+ = excellent, 0.6-0.8 = bon, <0.6 = faible
            if avg_correlation >= 0.8:
                return 0.9
            elif avg_correlation >= 0.6:
                return 0.7
            else:
                return 0.5
                
        except Exception as e:
            logger.error(f"❌ Erreur score corrélation: {e}")
            return 0.7
    
    def get_correlation_direction(self, es_change: float, nq_change: float) -> str:
        """Détermine la direction de corrélation (basé sur test_ibkr_corrige.py)"""
        try:
            if es_change > 0 and nq_change > 0:
                return "POSITIVE"
            elif es_change < 0 and nq_change < 0:
                return "POSITIVE"
            elif es_change > 0 and nq_change < 0:
                return "NEGATIVE"
            elif es_change < 0 and nq_change > 0:
                return "NEGATIVE"
            else:
                return "NEUTRAL"
        except Exception as e:
            logger.error(f"❌ Erreur direction corrélation: {e}")
            return "NEUTRAL"

def test_correlation_calculation():
    """Test du calcul de corrélation avec données réalistes"""
    logger.info("🧮 TEST CALCUL CORRÉLATION ES/NQ AMÉLIORÉ")
    logger.info("=" * 60)
    
    calculator = ESNQCorrelationCalculator(window_size=20)
    
    # Données de test réalistes (prix ES et NQ basés sur des valeurs réelles)
    test_data = [
        (4500.0, 18500.0),  # ES, NQ - Ratio ~4.11
        (4502.5, 18510.0),  # ES monte, NQ monte
        (4501.0, 18505.0),  # ES baisse, NQ baisse
        (4503.0, 18515.0),  # ES monte, NQ monte
        (4502.0, 18512.0),  # ES baisse, NQ baisse
        (4504.5, 18520.0),  # ES monte, NQ monte
        (4503.5, 18518.0),  # ES baisse, NQ baisse
        (4505.0, 18522.0),  # ES monte, NQ monte
        (4504.0, 18519.0),  # ES baisse, NQ baisse
        (4506.5, 18525.0),  # ES monte, NQ monte
    ]
    
    logger.info("📊 Test avec données corrélées (mouvements synchronisés):")
    for i, (es_price, nq_price) in enumerate(test_data, 1):
        result = calculator.add_price_data(es_price, nq_price)
        logger.info(f"Point {i}: ES={es_price:.1f}, NQ={nq_price:.1f}")
        logger.info(f"  📈 Corrélation: {result['correlation']:.3f}")
        logger.info(f"  📊 Divergence: {result['divergence']:.3f}")
        logger.info(f"  🎯 Leader: {result['leader']}")
        logger.info(f"  💪 Force: {result['strength']:.3f}")
        logger.info(f"  🔗 Ratio NQ/ES: {result['ratio']:.3f}")
        logger.info(f"  🎯 Score: {result['score']:.3f}")
        logger.info("")
    
    # Test avec divergence
    logger.info("📊 Test avec divergence (ES monte, NQ baisse):")
    divergent_data = [
        (4500.0, 18500.0),
        (4502.5, 18495.0),  # ES monte, NQ baisse
        (4505.0, 18490.0),  # ES monte, NQ baisse
        (4507.5, 18485.0),  # ES monte, NQ baisse
        (4510.0, 18480.0),  # ES monte, NQ baisse
    ]
    
    for i, (es_price, nq_price) in enumerate(divergent_data, 1):
        result = calculator.add_price_data(es_price, nq_price)
        logger.info(f"Point {i}: ES={es_price:.1f}, NQ={nq_price:.1f}")
        logger.info(f"  📈 Corrélation: {result['correlation']:.3f}")
        logger.info(f"  📊 Divergence: {result['divergence']:.3f}")
        logger.info(f"  🔗 Ratio NQ/ES: {result['ratio']:.3f}")
        logger.info("")
    
    # Test direction de corrélation
    logger.info("🧭 Test direction de corrélation:")
    directions = [
        (1.0, 1.0, "POSITIVE"),
        (-1.0, -1.0, "POSITIVE"),
        (1.0, -1.0, "NEGATIVE"),
        (-1.0, 1.0, "NEGATIVE"),
        (0.0, 0.0, "NEUTRAL"),
    ]
    
    for es_change, nq_change, expected in directions:
        direction = calculator.get_correlation_direction(es_change, nq_change)
        status = "✅" if direction == expected else "❌"
        logger.info(f"{status} ES:{es_change:+.1f}, NQ:{nq_change:+.1f} → {direction} (attendu: {expected})")
    
    # Score final
    final_score = calculator.get_correlation_score()
    logger.info(f"🎯 Score corrélation final: {final_score:.3f}")
    
    # Résumé des métriques
    logger.info("\n📋 RÉSUMÉ DES MÉTRIQUES:")
    if calculator.correlation_history:
        avg_corr = np.mean(list(calculator.correlation_history))
        logger.info(f"  📈 Corrélation moyenne: {avg_corr:.3f}")
    
    if calculator.correlation_ratios:
        avg_ratio = np.mean(list(calculator.correlation_ratios))
        logger.info(f"  🔗 Ratio NQ/ES moyen: {avg_ratio:.3f}")
    
    logger.info(f"  🎯 Score final: {final_score:.3f}")

if __name__ == "__main__":
    test_correlation_calculation()
