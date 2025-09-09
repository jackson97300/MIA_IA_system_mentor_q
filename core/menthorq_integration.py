#!/usr/bin/env python3
"""
MIA_IA_SYSTEM - MenthorQ Integration
Orchestrateur principal : Battle Navale + MenthorQ + Dealer's Bias + VIX

Version: Production Ready v1.0
Responsabilité: Fusion des signaux et décision finale
"""

from typing import Dict, List, Optional, Any, Tuple
from core.logger import get_logger
from core.trading_types import Decision, VIXRegime, SignalName, utcnow
from core.menthorq_execution_rules import evaluate_execution_rules, ExecutionRulesResult

logger = get_logger(__name__)

# === CONSTANTS ===

DEFAULT_WEIGHTS = {
    'BN': 0.6,      # Battle Navale 60%
    'MQ': 0.4       # MenthorQ 40%
}

DEFAULT_THRESHOLDS = {
    'LONG': 0.25,
    'SHORT': -0.25
}

DEFAULT_BASE_SIZE = 1.0
DEFAULT_VIX_CAPS = {
    "LOW": 1.0,
    "MID": 0.6,
    "HIGH": 0.4
}

# === MAIN FUNCTION ===

def analyze_menthorq_integration(
    symbol: str,
    current_price: float,
    vix_level: Optional[float] = None,
    levels: Optional[Dict[str, Any]] = None,
    dealers_bias: float = 0.0,
    bn_result: Optional[Any] = None,
    runtime: Optional[Any] = None
) -> Decision:
    """
    Analyse complète MenthorQ + Battle Navale + Dealers Bias + VIX
    
    Args:
        symbol: Symbole à analyser
        current_price: Prix actuel
        vix_level: Niveau VIX (optionnel, défaut: 20.0)
        levels: Niveaux MenthorQ {gamma, blind_spots, swing, last_update, stale}
        dealers_bias: Biais des dealers [-1..+1]
        bn_result: Résultat Battle Navale (optionnel)
        runtime: Configuration runtime (optionnel)
        
    Returns:
        Decision standardisé avec signal final
    """
    logger.debug(f"Analyse MenthorQ Integration - {symbol} @ {current_price}, VIX: {vix_level}, Dealers: {dealers_bias:.3f}")
    
    # 1. VIX par défaut et régime
    if vix_level is None:
        vix_level = 20.0  # Politique par défaut
    
    vix_regime = _determine_vix_regime(vix_level, runtime)
    
    # 2. Niveaux MenthorQ par défaut
    if levels is None:
        levels = {}
    
    # 3. Évaluer les hard rules EN PREMIER
    execution_result = evaluate_execution_rules(
        current_price=current_price,
        levels=levels,
        vix_regime=vix_regime,
        dealers_bias=dealers_bias,
        runtime=runtime,
        context=None  # TODO: Ajouter contexte si disponible
    )
    
    # Si hard block, retourner immédiatement
    if execution_result.hard_block:
        return Decision(
            name="NO_TRADE",
            score=-1.0,
            strength_bn=0.0,
            strength_mq=0.0,
            hard_rules_triggered=True,
            near_bl=True,
            d_bl_ticks=0.0,
            position_sizing=0.0,
            rationale=execution_result.reasons,
            ts=utcnow()
        )
    
    # 4. Analyser Battle Navale
    bn_score, bn_strength = _analyze_battle_navale(bn_result, current_price, symbol)
    
    # 5. Analyser MenthorQ
    mq_score, mq_strength = _analyze_menthorq_signal(current_price, levels, vix_level, dealers_bias)
    
    # 6. Fusion des signaux
    final_score = _fuse_signals(bn_score, mq_score, dealers_bias, runtime)
    
    # 7. Déterminer le signal final
    signal_name = _determine_signal_name(final_score, runtime)
    
    # 8. Calculer le position sizing
    position_sizing = _calculate_position_sizing(
        base_size=DEFAULT_BASE_SIZE,
        vix_regime=vix_regime,
        execution_result=execution_result,
        levels=levels,
        current_price=current_price,
        runtime=runtime
    )
    
    # 9. Construire la rationale
    rationale = _build_rationale(
        signal_name=signal_name,
        final_score=final_score,
        bn_score=bn_score,
        mq_score=mq_score,
        dealers_bias=dealers_bias,
        vix_regime=vix_regime,
        execution_result=execution_result,
        position_sizing=position_sizing
    )
    
    # 10. Retourner Decision standardisé
    return Decision(
        name=signal_name,
        score=final_score,
        strength_bn=bn_strength,
        strength_mq=mq_strength,
        hard_rules_triggered=False,
        near_bl=_check_blind_spot_proximity(current_price, levels),
        d_bl_ticks=_get_blind_spot_distance(current_price, levels),
        position_sizing=position_sizing,
        rationale=rationale,
        ts=utcnow()
    )

# === HELPER FUNCTIONS ===

def _determine_vix_regime(vix_level: float, runtime: Optional[Any]) -> VIXRegime:
    """Détermine le régime VIX"""
    vix_low = 15.0
    vix_high = 25.0
    
    if runtime:
        vix_low = getattr(runtime, 'VIX_LOW_THRESHOLD', vix_low)
        vix_high = getattr(runtime, 'VIX_HIGH_THRESHOLD', vix_high)
    
    if vix_level <= vix_low:
        return "LOW"
    elif vix_level >= vix_high:
        return "HIGH"
    else:
        return "MID"

def _analyze_battle_navale(bn_result: Optional[Any], current_price: float, symbol: str) -> Tuple[float, float]:
    """Analyse Battle Navale"""
    if bn_result is not None:
        score = getattr(bn_result, 'battle_navale_signal', 0.5) - 0.5  # Convertir [0,1] vers [-0.5,+0.5]
        strength = getattr(bn_result, 'battle_strength', 0.0)
        return score, strength
    else:
        logger.warning(f"Pas de résultat Battle Navale pour {symbol}")
        return 0.0, 0.0

def _analyze_menthorq_signal(current_price: float, levels: Dict[str, Any], vix_level: float, dealers_bias: float) -> Tuple[float, float]:
    """Analyse signal MenthorQ"""
    if not levels:
        return 0.0, 0.0
    
    gamma_score = _calculate_gamma_score(current_price, levels.get('gamma', {}))
    blind_spots_score = _calculate_blind_spots_score(current_price, levels.get('blind_spots', {}))
    swing_score = _calculate_swing_score(current_price, levels.get('swing', {}))
    
    mq_score = (gamma_score + blind_spots_score + swing_score) / 3.0
    mq_score *= (1.0 + dealers_bias * 0.5)  # Dealers bias influence le score MQ
    mq_score = max(-1.0, min(1.0, mq_score))
    
    mq_strength = min(1.0, abs(mq_score) * 2.0)
    
    return mq_score, mq_strength

def _calculate_gamma_score(current_price: float, gamma: Dict[str, float]) -> float:
    """Calcule le score basé sur la proximité aux niveaux Gamma"""
    if not gamma:
        return 0.0
    
    score = 0.0
    for label, price in gamma.items():
        if price > 0:
            distance = abs(current_price - price) * 4  # 4 ticks par point
            if distance <= 5:  # Proche
                if 'call' in label.lower() and price > current_price:
                    score += 0.3  # Call resistance au-dessus = bearish
                elif 'put' in label.lower() and price < current_price:
                    score += 0.3  # Put support en-dessous = bullish
                elif 'wall' in label.lower():
                    score += 0.2  # Gamma wall = neutre mais important
    
    return max(-1.0, min(1.0, score))

def _calculate_blind_spots_score(current_price: float, blind_spots: Dict[str, float]) -> float:
    """Calcule le score basé sur la proximité aux Blind Spots"""
    if not blind_spots:
        return 0.0
    
    min_distance = float('inf')
    for price in blind_spots.values():
        if price > 0:
            distance = abs(current_price - price) * 4  # 4 ticks par point
            min_distance = min(min_distance, distance)
    
    if min_distance <= 5:
        return -0.5  # BL proche = bearish
    elif min_distance <= 10:
        return -0.2  # BL moyennement proche = légèrement bearish
    else:
        return 0.0  # BL loin = neutre

def _calculate_swing_score(current_price: float, swing: Dict[str, float]) -> float:
    """Calcule le score basé sur la proximité aux niveaux Swing"""
    if not swing:
        return 0.0
    
    score = 0.0
    for price in swing.values():
        if price > 0:
            distance = abs(current_price - price) * 4  # 4 ticks par point
            if distance <= 8:  # Proche
                if price > current_price:
                    score -= 0.3  # Swing au-dessus = bearish
                else:
                    score += 0.3  # Swing en-dessous = bullish
    
    return max(-1.0, min(1.0, score))

def _fuse_signals(bn_score: float, mq_score: float, dealers_bias: float, runtime: Optional[Any]) -> float:
    """Fusion des signaux BN + MQ + Dealers Bias"""
    weights = DEFAULT_WEIGHTS
    if runtime:
        weights = {
            'BN': getattr(runtime, 'BN_WEIGHT', DEFAULT_WEIGHTS['BN']),
            'MQ': getattr(runtime, 'MQ_WEIGHT', DEFAULT_WEIGHTS['MQ'])
        }
    
    weighted_score = (bn_score * weights['BN']) + (mq_score * weights['MQ'])
    final_score = weighted_score * (1.0 + dealers_bias * 0.3)
    
    return max(-1.0, min(1.0, final_score))

def _determine_signal_name(final_score: float, runtime: Optional[Any]) -> SignalName:
    """Détermine le signal final basé sur le score"""
    thresholds = DEFAULT_THRESHOLDS
    if runtime:
        thresholds = {
            'LONG': getattr(runtime, 'LONG_THRESHOLD', DEFAULT_THRESHOLDS['LONG']),
            'SHORT': getattr(runtime, 'SHORT_THRESHOLD', DEFAULT_THRESHOLDS['SHORT'])
        }
    
    if final_score >= thresholds['LONG']:
        return "GO_LONG"
    elif final_score <= thresholds['SHORT']:
        return "GO_SHORT"
    else:
        return "NEUTRAL"

def _calculate_position_sizing(
    base_size: float,
    vix_regime: VIXRegime,
    execution_result: ExecutionRulesResult,
    levels: Dict[str, Any],
    current_price: float,
    runtime: Optional[Any]
) -> float:
    """Calcule le position sizing final"""
    sizing = base_size
    sizing *= execution_result.size_multiplier
    
    vix_caps = DEFAULT_VIX_CAPS
    if runtime:
        vix_caps = getattr(runtime, 'VIX_CAPS', DEFAULT_VIX_CAPS)
    
    vix_cap = vix_caps.get(vix_regime, 1.0)
    sizing = min(sizing, vix_cap)
    
    gamma_distance = _get_gamma_distance(current_price, levels)
    if gamma_distance is not None and gamma_distance <= 3:
        sizing *= 0.5
    
    swing_adverse = _check_swing_adverse(current_price, levels)
    if swing_adverse:
        sizing *= 0.7
    
    return max(0.0, min(1.0, sizing))

def _build_rationale(
    signal_name: SignalName,
    final_score: float,
    bn_score: float,
    mq_score: float,
    dealers_bias: float,
    vix_regime: VIXRegime,
    execution_result: ExecutionRulesResult,
    position_sizing: float
) -> List[str]:
    """Construit la rationale détaillée"""
    rationale = []
    
    rationale.append(f"Signal: {signal_name} (score: {final_score:.3f})")
    rationale.append(f"BN: {bn_score:.3f}, MQ: {mq_score:.3f}")
    
    if abs(dealers_bias) > 0.1:
        bias_desc = "bullish" if dealers_bias > 0 else "bearish"
        rationale.append(f"Dealers bias {bias_desc}: {dealers_bias:.3f}")
    
    rationale.append(f"VIX regime: {vix_regime}")
    
    if execution_result.reasons:
        rationale.extend(execution_result.reasons)
    
    rationale.append(f"Position sizing: {position_sizing:.2f}")
    
    return rationale

def _check_blind_spot_proximity(current_price: float, levels: Dict[str, Any]) -> bool:
    """Vérifie si un Blind Spot est proche"""
    blind_spots = levels.get('blind_spots', {})
    if not blind_spots:
        return False
    
    for price in blind_spots.values():
        if price > 0:
            distance = abs(current_price - price) * 4  # 4 ticks par point
            if distance <= 5:
                return True
    
    return False

def _get_blind_spot_distance(current_price: float, levels: Dict[str, Any]) -> Optional[float]:
    """Retourne la distance au Blind Spot le plus proche en ticks"""
    blind_spots = levels.get('blind_spots', {})
    if not blind_spots:
        return None
    
    min_distance = float('inf')
    for price in blind_spots.values():
        if price > 0:
            distance = abs(current_price - price) * 4  # 4 ticks par point
            min_distance = min(min_distance, distance)
    
    return min_distance if min_distance != float('inf') else None

def _get_gamma_distance(current_price: float, levels: Dict[str, Any]) -> Optional[float]:
    """Retourne la distance à la Gamma Wall la plus proche en ticks"""
    gamma = levels.get('gamma', {})
    if not gamma:
        return None
    
    min_distance = float('inf')
    for label, price in gamma.items():
        if price > 0 and 'wall' in label.lower():
            distance = abs(current_price - price) * 4  # 4 ticks par point
            min_distance = min(min_distance, distance)
    
    return min_distance if min_distance != float('inf') else None

def _check_swing_adverse(current_price: float, levels: Dict[str, Any]) -> bool:
    """Vérifie si un swing est adverse"""
    swing = levels.get('swing', {})
    if not swing:
        return False
    
    for price in swing.values():
        if price > 0:
            distance = abs(current_price - price) * 4  # 4 ticks par point
            if distance <= 8:  # Proche
                return True
    
    return False

# === FACTORY FUNCTION ===

def create_menthorq_integration() -> Any:
    """Factory function pour créer l'intégration MenthorQ"""
    return analyze_menthorq_integration

# === TESTING ===

def test_menthorq_integration():
    """Test de l'intégration MenthorQ"""
    logger.info("=== TEST MenthorQ Integration ===")
    
    try:
        # Test 1: Hard rule (BL proche)
        levels_bl = {
            'blind_spots': {'BL 1': 5294.5},  # 2 ticks de distance
            'gamma': {},
            'swing': {},
            'stale': False
        }
        
        result1 = analyze_menthorq_integration(
            symbol="ESU25",
            current_price=5294.0,
            levels=levels_bl,
            dealers_bias=0.0
        )
        
        assert result1.name == "NO_TRADE", "BL proche doit donner NO_TRADE"
        assert result1.hard_rules_triggered == True, "Hard rules doivent être déclenchées"
        assert result1.position_sizing == 0.0, "Position sizing doit être 0"
        logger.info(f"✅ Test 1 OK: BL proche → {result1.name}")
        
        # Test 2: Signal normal
        levels_normal = {
            'blind_spots': {},
            'gamma': {'Call Resistance': 5300.0, 'Put Support': 5285.0},
            'swing': {'SG1': 5288.0},
            'stale': False
        }
        
        result2 = analyze_menthorq_integration(
            symbol="ESU25",
            current_price=5294.0,
            vix_level=18.0,
            levels=levels_normal,
            dealers_bias=0.2
        )
        
        assert result2.name in ["GO_LONG", "GO_SHORT", "NEUTRAL"], "Signal valide"
        assert result2.hard_rules_triggered == False, "Pas de hard rules"
        assert 0.0 <= result2.position_sizing <= 1.0, "Position sizing valide"
        logger.info(f"✅ Test 2 OK: Signal normal → {result2.name} (sizing: {result2.position_sizing:.2f})")
        
        # Test 3: VIX HIGH
        result3 = analyze_menthorq_integration(
            symbol="ESU25",
            current_price=5294.0,
            vix_level=30.0,  # HIGH
            levels=levels_normal,
            dealers_bias=0.0
        )
        
        assert result3.position_sizing <= 0.4, "VIX HIGH doit limiter le sizing"
        logger.info(f"✅ Test 3 OK: VIX HIGH → sizing: {result3.position_sizing:.2f}")
        
        logger.info("🎉 Tous les tests MenthorQ Integration réussis!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erreur test: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    test_menthorq_integration()