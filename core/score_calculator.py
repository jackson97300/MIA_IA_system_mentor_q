#!/usr/bin/env python3
"""
🎯 SCORE CALCULATOR - MIA_IA_SYSTEM
===================================

Calculateur de score centralisé avec traces détaillées par composant.
Utilise la configuration centralisée pour les poids et seuils.
"""

import sys
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum

# Ajouter le répertoire parent au PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.logger import get_logger

# Import configuration centralisée
try:
    from config.menthorq_rules_loader import get_menthorq_rules, get_score_weight, get_level_weight
    MENTHORQ_RULES_AVAILABLE = True
except ImportError:
    MENTHORQ_RULES_AVAILABLE = False

logger = get_logger(__name__)

class ScoreComponent(Enum):
    """Composants du score de trading"""
    MENTHORQ = "menthorq_score"
    BATTLE_NAVALE = "battle_navale_score"
    VIX_REGIME = "vix_regime_score"

@dataclass
class ComponentTrace:
    """Trace détaillée d'un composant de score"""
    component: ScoreComponent
    raw_score: float
    weighted_score: float
    weight: float
    sub_components: Dict[str, float] = field(default_factory=dict)
    calculation_time_ms: float = 0.0
    data_quality: str = "GOOD"  # GOOD, WARNING, CRITICAL
    details: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ScoreResult:
    """Résultat complet du calcul de score"""
    final_score: float
    components: List[ComponentTrace]
    total_calculation_time_ms: float
    timestamp: datetime
    data_quality_overall: str
    confidence_level: float
    signal_strength: str
    audit_trail: Dict[str, Any]

class ScoreCalculator:
    """Calculateur de score centralisé avec traces détaillées"""
    
    def __init__(self):
        """Initialisation du calculateur de score"""
        self.calculation_history: List[ScoreResult] = []
        self.max_history_size = 1000
        
        # Poids par défaut (fallback si config non disponible)
        self.default_weights = {
            ScoreComponent.MENTHORQ: 0.40,
            ScoreComponent.BATTLE_NAVALE: 0.35,
            ScoreComponent.VIX_REGIME: 0.25
        }
        
        logger.info(f"🎯 ScoreCalculator initialisé (config_available: {MENTHORQ_RULES_AVAILABLE})")
    
    def calculate_trading_score(self, 
                              menthorq_data: Dict[str, Any],
                              battle_navale_data: Dict[str, Any],
                              vix_data: Dict[str, Any],
                              market_context: Optional[Dict[str, Any]] = None) -> ScoreResult:
        """
        Calcule le score de trading avec traces détaillées
        
        Args:
            menthorq_data: Données MenthorQ (niveaux, distances, staleness)
            battle_navale_data: Données Battle Navale (confluence, volume profile)
            vix_data: Données VIX (niveau, régime, policy)
            market_context: Contexte marché (session, volatilité, etc.)
            
        Returns:
            ScoreResult: Résultat complet avec traces
        """
        start_time = datetime.now(timezone.utc)
        calculation_start = datetime.now()
        
        components = []
        total_weighted_score = 0.0
        total_weight = 0.0
        data_quality_issues = []
        
        try:
            # 1. Calculer le score MenthorQ
            menthorq_trace = self._calculate_menthorq_score(menthorq_data)
            components.append(menthorq_trace)
            total_weighted_score += menthorq_trace.weighted_score
            total_weight += menthorq_trace.weight
            
            if menthorq_trace.data_quality != "GOOD":
                data_quality_issues.append(f"MenthorQ: {menthorq_trace.data_quality}")
            
            # 2. Calculer le score Battle Navale
            battle_navale_trace = self._calculate_battle_navale_score(battle_navale_data)
            components.append(battle_navale_trace)
            total_weighted_score += battle_navale_trace.weighted_score
            total_weight += battle_navale_trace.weight
            
            if battle_navale_trace.data_quality != "GOOD":
                data_quality_issues.append(f"Battle Navale: {battle_navale_trace.data_quality}")
            
            # 3. Calculer le score VIX Regime
            vix_trace = self._calculate_vix_regime_score(vix_data)
            components.append(vix_trace)
            total_weighted_score += vix_trace.weighted_score
            total_weight += vix_trace.weight
            
            if vix_trace.data_quality != "GOOD":
                data_quality_issues.append(f"VIX: {vix_trace.data_quality}")
            
            # 4. Calculer le score final
            if total_weight > 0:
                final_score = total_weighted_score / total_weight
            else:
                final_score = 0.5  # Score neutre si pas de poids
            
            # 5. Déterminer la qualité globale des données
            if not data_quality_issues:
                data_quality_overall = "GOOD"
            elif len(data_quality_issues) == 1:
                data_quality_overall = "WARNING"
            else:
                data_quality_overall = "CRITICAL"
            
            # 6. Calculer le niveau de confiance
            confidence_level = self._calculate_confidence_level(components, data_quality_overall)
            
            # 7. Déterminer la force du signal
            signal_strength = self._determine_signal_strength(final_score, confidence_level)
            
            # 8. Créer l'audit trail
            audit_trail = self._create_audit_trail(components, market_context, data_quality_issues)
            
            # 9. Calculer le temps total
            calculation_end = datetime.now()
            total_calculation_time_ms = (calculation_end - calculation_start).total_seconds() * 1000
            
            # 10. Créer le résultat
            result = ScoreResult(
                final_score=final_score,
                components=components,
                total_calculation_time_ms=total_calculation_time_ms,
                timestamp=start_time,
                data_quality_overall=data_quality_overall,
                confidence_level=confidence_level,
                signal_strength=signal_strength,
                audit_trail=audit_trail
            )
            
            # 11. Sauvegarder dans l'historique
            self._save_to_history(result)
            
            logger.info(f"🎯 Score calculé: {final_score:.3f} (confiance: {confidence_level:.1%}, force: {signal_strength})")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Erreur calcul score: {e}")
            return self._create_error_result(str(e), start_time)
    
    def _calculate_menthorq_score(self, menthorq_data: Dict[str, Any]) -> ComponentTrace:
        """Calcule le score MenthorQ avec traces détaillées"""
        start_time = datetime.now()
        
        try:
            # Récupérer le poids depuis la configuration
            weight = self._get_component_weight(ScoreComponent.MENTHORQ)
            
            # Extraire les données MenthorQ
            gamma_levels = menthorq_data.get('gamma_levels', {})
            blind_spots = menthorq_data.get('blind_spots', {})
            swing_levels = menthorq_data.get('swing_levels', {})
            current_price = menthorq_data.get('current_price', 0.0)
            staleness = menthorq_data.get('staleness', {})
            
            sub_components = {}
            data_quality = "GOOD"
            details = {}
            
            # 1. Score Gamma Levels (40% du score MenthorQ)
            gamma_score = self._calculate_gamma_score(gamma_levels, current_price)
            sub_components['gamma_levels'] = gamma_score
            details['gamma_levels'] = {
                'count': len(gamma_levels),
                'score': gamma_score,
                'levels': list(gamma_levels.keys())[:5]  # Limiter pour les logs
            }
            
            # 2. Score Blind Spots (30% du score MenthorQ)
            blind_spots_score = self._calculate_blind_spots_score(blind_spots, current_price)
            sub_components['blind_spots'] = blind_spots_score
            details['blind_spots'] = {
                'count': len(blind_spots),
                'score': blind_spots_score,
                'nearby_count': len([p for p in blind_spots.values() if abs(p - current_price) < 2.0])
            }
            
            # 3. Score Swing Levels (20% du score MenthorQ)
            swing_score = self._calculate_swing_score(swing_levels, current_price)
            sub_components['swing_levels'] = swing_score
            details['swing_levels'] = {
                'count': len(swing_levels),
                'score': swing_score
            }
            
            # 4. Score Dealers Bias (10% du score MenthorQ)
            dealers_bias_score = menthorq_data.get('dealers_bias_score', 0.5)
            sub_components['dealers_bias'] = dealers_bias_score
            details['dealers_bias'] = {
                'score': dealers_bias_score,
                'direction': menthorq_data.get('dealers_bias_direction', 'NEUTRAL')
            }
            
            # 5. Vérifier la qualité des données
            if staleness.get('is_stale', False):
                data_quality = "WARNING"
                details['staleness_warning'] = "Données MenthorQ obsolètes"
            
            if len(gamma_levels) == 0 and len(blind_spots) == 0:
                data_quality = "CRITICAL"
                details['data_critical'] = "Aucun niveau MenthorQ disponible"
            
            # 6. Calculer le score final MenthorQ
            raw_score = (
                0.40 * gamma_score +
                0.30 * blind_spots_score +
                0.20 * swing_score +
                0.10 * dealers_bias_score
            )
            
            weighted_score = raw_score * weight
            
            # 7. Calculer le temps de calcul
            calculation_time_ms = (datetime.now() - start_time).total_seconds() * 1000
            
            return ComponentTrace(
                component=ScoreComponent.MENTHORQ,
                raw_score=raw_score,
                weighted_score=weighted_score,
                weight=weight,
                sub_components=sub_components,
                calculation_time_ms=calculation_time_ms,
                data_quality=data_quality,
                details=details
            )
            
        except Exception as e:
            logger.error(f"❌ Erreur calcul score MenthorQ: {e}")
            return ComponentTrace(
                component=ScoreComponent.MENTHORQ,
                raw_score=0.5,
                weighted_score=0.5 * self._get_component_weight(ScoreComponent.MENTHORQ),
                weight=self._get_component_weight(ScoreComponent.MENTHORQ),
                data_quality="CRITICAL",
                details={'error': str(e)}
            )
    
    def _calculate_battle_navale_score(self, battle_navale_data: Dict[str, Any]) -> ComponentTrace:
        """Calcule le score Battle Navale avec traces détaillées"""
        start_time = datetime.now()
        
        try:
            weight = self._get_component_weight(ScoreComponent.BATTLE_NAVALE)
            
            sub_components = {}
            data_quality = "GOOD"
            details = {}
            
            # 1. Score Volume Profile (40% du score Battle Navale)
            volume_profile_score = self._calculate_volume_profile_score(battle_navale_data)
            sub_components['volume_profile'] = volume_profile_score
            details['volume_profile'] = {
                'score': volume_profile_score,
                'vpoc': battle_navale_data.get('vpoc', 0.0),
                'vah': battle_navale_data.get('vah', 0.0),
                'val': battle_navale_data.get('val', 0.0)
            }
            
            # 2. Score VWAP Analysis (30% du score Battle Navale)
            vwap_score = self._calculate_vwap_score(battle_navale_data)
            sub_components['vwap'] = vwap_score
            details['vwap'] = {
                'score': vwap_score,
                'position': battle_navale_data.get('vwap_position', 'unknown')
            }
            
            # 3. Score NBCV Order Flow (20% du score Battle Navale)
            nbcv_score = self._calculate_nbcv_score(battle_navale_data)
            sub_components['nbcv'] = nbcv_score
            details['nbcv'] = {
                'score': nbcv_score,
                'delta_ratio': battle_navale_data.get('delta_ratio', 0.0)
            }
            
            # 4. Score Confluence (10% du score Battle Navale)
            confluence_score = battle_navale_data.get('confluence_score', 0.5)
            sub_components['confluence'] = confluence_score
            details['confluence'] = {
                'score': confluence_score,
                'components_count': battle_navale_data.get('confluence_components', 0)
            }
            
            # Calculer le score final Battle Navale
            raw_score = (
                0.40 * volume_profile_score +
                0.30 * vwap_score +
                0.20 * nbcv_score +
                0.10 * confluence_score
            )
            
            weighted_score = raw_score * weight
            calculation_time_ms = (datetime.now() - start_time).total_seconds() * 1000
            
            return ComponentTrace(
                component=ScoreComponent.BATTLE_NAVALE,
                raw_score=raw_score,
                weighted_score=weighted_score,
                weight=weight,
                sub_components=sub_components,
                calculation_time_ms=calculation_time_ms,
                data_quality=data_quality,
                details=details
            )
            
        except Exception as e:
            logger.error(f"❌ Erreur calcul score Battle Navale: {e}")
            return ComponentTrace(
                component=ScoreComponent.BATTLE_NAVALE,
                raw_score=0.5,
                weighted_score=0.5 * self._get_component_weight(ScoreComponent.BATTLE_NAVALE),
                weight=self._get_component_weight(ScoreComponent.BATTLE_NAVALE),
                data_quality="CRITICAL",
                details={'error': str(e)}
            )
    
    def _calculate_vix_regime_score(self, vix_data: Dict[str, Any]) -> ComponentTrace:
        """Calcule le score VIX Regime avec traces détaillées"""
        start_time = datetime.now()
        
        try:
            weight = self._get_component_weight(ScoreComponent.VIX_REGIME)
            
            vix_level = vix_data.get('vix_level', 20.0)
            vix_regime = vix_data.get('vix_regime', 'normal')
            policy = vix_data.get('policy', 'normal')
            
            sub_components = {}
            details = {}
            
            # 1. Score VIX Level (60% du score VIX Regime)
            vix_level_score = self._calculate_vix_level_score(vix_level)
            sub_components['vix_level'] = vix_level_score
            details['vix_level'] = {
                'level': vix_level,
                'score': vix_level_score,
                'regime': vix_regime
            }
            
            # 2. Score Policy (40% du score VIX Regime)
            policy_score = self._calculate_policy_score(policy)
            sub_components['policy'] = policy_score
            details['policy'] = {
                'policy': policy,
                'score': policy_score
            }
            
            # Calculer le score final VIX Regime
            raw_score = 0.60 * vix_level_score + 0.40 * policy_score
            weighted_score = raw_score * weight
            calculation_time_ms = (datetime.now() - start_time).total_seconds() * 1000
            
            return ComponentTrace(
                component=ScoreComponent.VIX_REGIME,
                raw_score=raw_score,
                weighted_score=weighted_score,
                weight=weight,
                sub_components=sub_components,
                calculation_time_ms=calculation_time_ms,
                data_quality="GOOD",
                details=details
            )
            
        except Exception as e:
            logger.error(f"❌ Erreur calcul score VIX Regime: {e}")
            return ComponentTrace(
                component=ScoreComponent.VIX_REGIME,
                raw_score=0.5,
                weighted_score=0.5 * self._get_component_weight(ScoreComponent.VIX_REGIME),
                weight=self._get_component_weight(ScoreComponent.VIX_REGIME),
                data_quality="CRITICAL",
                details={'error': str(e)}
            )
    
    def _get_component_weight(self, component: ScoreComponent) -> float:
        """Récupère le poids d'un composant depuis la configuration"""
        if MENTHORQ_RULES_AVAILABLE:
            try:
                return get_score_weight(component.value)
            except Exception as e:
                logger.warning(f"⚠️ Erreur lecture poids {component.value}: {e}")
        
        return self.default_weights.get(component, 0.33)
    
    def _calculate_gamma_score(self, gamma_levels: Dict[str, float], current_price: float) -> float:
        """Calcule le score des niveaux Gamma"""
        if not gamma_levels or current_price <= 0:
            return 0.5
        
        # Logique simplifiée : plus on est proche d'un niveau, plus le score est élevé
        min_distance = min(abs(price - current_price) for price in gamma_levels.values() if price > 0)
        if min_distance < 1.0:  # Très proche
            return 0.9
        elif min_distance < 5.0:  # Proche
            return 0.7
        elif min_distance < 10.0:  # Modéré
            return 0.5
        else:  # Loin
            return 0.3
    
    def _calculate_blind_spots_score(self, blind_spots: Dict[str, float], current_price: float) -> float:
        """Calcule le score des Blind Spots"""
        if not blind_spots or current_price <= 0:
            return 0.5
        
        # Logique inversée : plus on est proche d'un Blind Spot, plus le score est faible
        min_distance = min(abs(price - current_price) for price in blind_spots.values() if price > 0)
        if min_distance < 1.0:  # Très proche = dangereux
            return 0.1
        elif min_distance < 3.0:  # Proche = risqué
            return 0.3
        elif min_distance < 8.0:  # Modéré
            return 0.6
        else:  # Loin = sûr
            return 0.8
    
    def _calculate_swing_score(self, swing_levels: Dict[str, float], current_price: float) -> float:
        """Calcule le score des niveaux Swing"""
        if not swing_levels or current_price <= 0:
            return 0.5
        
        # Logique similaire aux niveaux Gamma
        min_distance = min(abs(price - current_price) for price in swing_levels.values() if price > 0)
        if min_distance < 2.0:
            return 0.8
        elif min_distance < 8.0:
            return 0.6
        else:
            return 0.4
    
    def _calculate_volume_profile_score(self, battle_navale_data: Dict[str, Any]) -> float:
        """Calcule le score Volume Profile"""
        current_price = battle_navale_data.get('current_price', 0.0)
        vpoc = battle_navale_data.get('vpoc', 0.0)
        vah = battle_navale_data.get('vah', 0.0)
        val = battle_navale_data.get('val', 0.0)
        
        if not all([current_price, vpoc, vah, val]):
            return 0.5
        
        # Score basé sur la position par rapport à la Value Area
        if current_price > vah:
            return 0.8  # Au-dessus de VAH = bullish
        elif current_price < val:
            return 0.2  # En-dessous de VAL = bearish
        else:
            return 0.5  # Dans la Value Area = neutre
    
    def _calculate_vwap_score(self, battle_navale_data: Dict[str, Any]) -> float:
        """Calcule le score VWAP"""
        current_price = battle_navale_data.get('current_price', 0.0)
        vwap = battle_navale_data.get('vwap', 0.0)
        
        if not current_price or not vwap:
            return 0.5
        
        # Score basé sur la position par rapport au VWAP
        if current_price > vwap * 1.001:  # 0.1% au-dessus
            return 0.8
        elif current_price < vwap * 0.999:  # 0.1% en-dessous
            return 0.2
        else:
            return 0.5
    
    def _calculate_nbcv_score(self, battle_navale_data: Dict[str, Any]) -> float:
        """Calcule le score NBCV"""
        delta_ratio = battle_navale_data.get('delta_ratio', 0.5)
        
        # Score basé sur le ratio delta
        if delta_ratio > 0.6:
            return 0.8  # Forte pression acheteuse
        elif delta_ratio < 0.4:
            return 0.2  # Forte pression vendeuse
        else:
            return 0.5  # Équilibré
    
    def _calculate_vix_level_score(self, vix_level: float) -> float:
        """Calcule le score basé sur le niveau VIX"""
        if vix_level <= 15:
            return 0.9  # VIX bas = bon pour le trading
        elif vix_level <= 25:
            return 0.7  # VIX normal
        elif vix_level <= 35:
            return 0.5  # VIX élevé
        else:
            return 0.3  # VIX très élevé = risqué
    
    def _calculate_policy_score(self, policy: str) -> float:
        """Calcule le score basé sur la policy VIX"""
        policy_scores = {
            'normal': 0.8,
            'low': 0.9,
            'high': 0.4,
            'extreme': 0.2
        }
        return policy_scores.get(policy, 0.5)
    
    def _calculate_confidence_level(self, components: List[ComponentTrace], data_quality: str) -> float:
        """Calcule le niveau de confiance global"""
        base_confidence = 0.8
        
        # Réduire la confiance si qualité des données dégradée
        if data_quality == "WARNING":
            base_confidence *= 0.8
        elif data_quality == "CRITICAL":
            base_confidence *= 0.5
        
        # Réduire la confiance si composants manquants
        missing_components = 3 - len(components)
        if missing_components > 0:
            base_confidence *= (1.0 - missing_components * 0.2)
        
        return max(0.1, min(1.0, base_confidence))
    
    def _determine_signal_strength(self, final_score: float, confidence_level: float) -> str:
        """Détermine la force du signal"""
        # Ajuster le score selon la confiance
        adjusted_score = final_score * confidence_level
        
        if adjusted_score >= 0.8:
            return "VERY_STRONG"
        elif adjusted_score >= 0.7:
            return "STRONG"
        elif adjusted_score >= 0.6:
            return "MODERATE"
        elif adjusted_score >= 0.4:
            return "WEAK"
        else:
            return "VERY_WEAK"
    
    def _create_audit_trail(self, components: List[ComponentTrace], 
                          market_context: Optional[Dict[str, Any]], 
                          data_quality_issues: List[str]) -> Dict[str, Any]:
        """Crée l'audit trail complet"""
        return {
            "calculation_version": "1.0",
            "components_count": len(components),
            "data_quality_issues": data_quality_issues,
            "market_context": market_context or {},
            "component_details": {
                comp.component.value: {
                    "raw_score": comp.raw_score,
                    "weight": comp.weight,
                    "weighted_score": comp.weighted_score,
                    "calculation_time_ms": comp.calculation_time_ms,
                    "data_quality": comp.data_quality,
                    "sub_components": comp.sub_components
                }
                for comp in components
            }
        }
    
    def _save_to_history(self, result: ScoreResult) -> None:
        """Sauvegarde le résultat dans l'historique"""
        self.calculation_history.append(result)
        
        # Limiter la taille de l'historique
        if len(self.calculation_history) > self.max_history_size:
            self.calculation_history = self.calculation_history[-self.max_history_size:]
    
    def _create_error_result(self, error_message: str, timestamp: datetime) -> ScoreResult:
        """Crée un résultat d'erreur"""
        return ScoreResult(
            final_score=0.5,
            components=[],
            total_calculation_time_ms=0.0,
            timestamp=timestamp,
            data_quality_overall="CRITICAL",
            confidence_level=0.0,
            signal_strength="ERROR",
            audit_trail={"error": error_message}
        )
    
    def get_score_statistics(self) -> Dict[str, Any]:
        """Retourne les statistiques des scores calculés"""
        if not self.calculation_history:
            return {"total_calculations": 0}
        
        recent_results = self.calculation_history[-100:]  # 100 derniers
        
        return {
            "total_calculations": len(self.calculation_history),
            "recent_calculations": len(recent_results),
            "avg_final_score": sum(r.final_score for r in recent_results) / len(recent_results),
            "avg_confidence": sum(r.confidence_level for r in recent_results) / len(recent_results),
            "avg_calculation_time_ms": sum(r.total_calculation_time_ms for r in recent_results) / len(recent_results),
            "signal_strength_distribution": {
                strength: sum(1 for r in recent_results if r.signal_strength == strength)
                for strength in ["VERY_STRONG", "STRONG", "MODERATE", "WEAK", "VERY_WEAK"]
            },
            "data_quality_distribution": {
                quality: sum(1 for r in recent_results if r.data_quality_overall == quality)
                for quality in ["GOOD", "WARNING", "CRITICAL"]
            }
        }

# === INSTANCE GLOBALE ===

_global_score_calculator: Optional[ScoreCalculator] = None

def get_score_calculator() -> ScoreCalculator:
    """Retourne l'instance globale du calculateur de score"""
    global _global_score_calculator
    if _global_score_calculator is None:
        _global_score_calculator = ScoreCalculator()
    return _global_score_calculator

# === FONCTIONS UTILITAIRES ===

def calculate_trading_score(menthorq_data: Dict[str, Any],
                          battle_navale_data: Dict[str, Any],
                          vix_data: Dict[str, Any],
                          market_context: Optional[Dict[str, Any]] = None) -> ScoreResult:
    """Calcule le score de trading avec l'instance globale"""
    calculator = get_score_calculator()
    return calculator.calculate_trading_score(menthorq_data, battle_navale_data, vix_data, market_context)

# === TEST ===

def test_score_calculator():
    """Test du calculateur de score"""
    logger.info("=== TEST SCORE CALCULATOR ===")
    
    try:
        calculator = ScoreCalculator()
        
        # Test 1: Données complètes
        menthorq_data = {
            'gamma_levels': {'Call Resistance': 5300.0, 'Put Support': 5285.0},
            'blind_spots': {'BL 1': 5294.5, 'BL 2': 5296.0},
            'swing_levels': {'SG1': 5288.0, 'SG2': 5302.0},
            'current_price': 5294.0,
            'dealers_bias_score': 0.7,
            'dealers_bias_direction': 'BULLISH',
            'staleness': {'is_stale': False}
        }
        
        battle_navale_data = {
            'current_price': 5294.0,
            'vpoc': 5290.0,
            'vah': 5295.0,
            'val': 5285.0,
            'vwap': 5292.0,
            'vwap_position': 'above',
            'delta_ratio': 0.65,
            'confluence_score': 0.8,
            'confluence_components': 3
        }
        
        vix_data = {
            'vix_level': 18.5,
            'vix_regime': 'normal',
            'policy': 'normal'
        }
        
        market_context = {
            'session': 'us_session',
            'volatility': 'normal'
        }
        
        result = calculator.calculate_trading_score(menthorq_data, battle_navale_data, vix_data, market_context)
        
        assert result.final_score > 0, "Score final doit être > 0"
        assert len(result.components) == 3, "Doit avoir 3 composants"
        assert result.confidence_level > 0, "Confiance doit être > 0"
        assert result.signal_strength in ["VERY_STRONG", "STRONG", "MODERATE", "WEAK", "VERY_WEAK"], "Force du signal invalide"
        
        logger.info("✅ Test 1 OK: Calcul score complet")
        
        # Test 2: Données partielles
        partial_menthorq = {'current_price': 5294.0, 'staleness': {'is_stale': True}}
        partial_battle_navale = {'current_price': 5294.0}
        partial_vix = {'vix_level': 25.0}
        
        result2 = calculator.calculate_trading_score(partial_menthorq, partial_battle_navale, partial_vix)
        
        assert result2.final_score > 0, "Score final doit être > 0 même avec données partielles"
        assert result2.data_quality_overall in ["WARNING", "CRITICAL"], "Qualité des données doit être dégradée"
        
        logger.info("✅ Test 2 OK: Calcul score avec données partielles")
        
        # Test 3: Statistiques
        stats = calculator.get_score_statistics()
        assert stats["total_calculations"] >= 2, "Doit avoir au moins 2 calculs"
        assert "avg_final_score" in stats, "Statistiques manquantes"
        
        logger.info("✅ Test 3 OK: Statistiques")
        
        logger.info("🎉 Tous les tests Score Calculator réussis!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erreur test: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    test_score_calculator()

