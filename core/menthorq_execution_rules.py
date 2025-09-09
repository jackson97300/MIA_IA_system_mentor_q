#!/usr/bin/env python3
"""
MIA_IA_SYSTEM - MenthorQ Execution Rules
Centralise les règles d'exécution : Hard Rules (bloquantes) et Soft Adjustments

Version: Production Ready v1.0
Responsabilité: Règles de sécurité et d'ajustement pour MenthorQ
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Any
from enum import Enum
from core.logger import get_logger
from core.trading_types import VIXRegime, utcnow

logger = get_logger(__name__)

# === TYPES ===

@dataclass
class ExecutionRulesResult:
    """Résultat des règles d'exécution"""
    hard_block: bool
    reasons: List[str]
    size_multiplier: float  # 0..1
    min_stop_ticks: Optional[int] = None
    required_confluence: List[str] = None
    
    def __post_init__(self):
        if self.required_confluence is None:
            self.required_confluence = []
        # Clamp size_multiplier
        self.size_multiplier = max(0.0, min(1.0, self.size_multiplier))

# === CONSTANTS ===

DEFAULT_BL_TICKS = 5
DEFAULT_GAMMA_TICKS = 3
DEFAULT_SWING_TICKS = 4
DEFAULT_MAX_AGE_MIN = 30
DEFAULT_COOLDOWN_MIN = 15

DEFAULT_SIZE_CAPS = {
    "LOW": 1.0,
    "MID": 0.6,
    "HIGH": 0.4
}

DEFAULT_DEALERS_BIAS_HARD = -0.5
DEFAULT_DEALERS_BIAS_SOFT = -0.3

# === MAIN FUNCTION ===

def evaluate_execution_rules(
    current_price: float,
    levels: Dict[str, Any],
    vix_regime: VIXRegime,
    dealers_bias: float,
    runtime: Optional[Any] = None,
    context: Optional[Dict[str, Any]] = None
) -> ExecutionRulesResult:
    """
    Évalue les règles d'exécution MenthorQ
    
    Args:
        current_price: Prix actuel
        levels: Niveaux MenthorQ {gamma, blind_spots, swing, last_update, stale}
        vix_regime: Régime VIX (LOW/MID/HIGH)
        dealers_bias: Biais des dealers [-1..+1]
        runtime: Configuration runtime (optionnel)
        context: Contexte additionnel (spread, time, last_trade, etc.)
        
    Returns:
        ExecutionRulesResult avec hard_block, reasons, size_multiplier, etc.
    """
    logger.debug(f"Évaluation règles exécution - Prix: {current_price}, VIX: {vix_regime}, Dealers: {dealers_bias:.3f}")
    
    # Initialisation
    hard_block = False
    reasons = []
    size_multiplier = 1.0
    min_stop_ticks = None
    required_confluence = []
    
    # Récupérer configuration runtime (avec fallbacks)
    config = _get_runtime_config(runtime)
    
    # === HARD RULES (bloquantes) ===
    
    # 1. Blind Spot proche
    bl_distance = _get_blind_spot_distance(current_price, levels)
    if bl_distance is not None and bl_distance <= config['BL_TICKS']:
        hard_block = True
        reasons.append(f"BL proche (≤{bl_distance:.1f} ticks)")
        logger.info(f"🚫 Hard rule: BL proche - {bl_distance:.1f} ticks")
    
    # 2. VIX HIGH + BL proche (durcissement)
    if vix_regime == "HIGH" and bl_distance is not None:
        hardened_threshold = config['BL_TICKS'] * 1.5
        if bl_distance <= hardened_threshold:
            hard_block = True
            reasons.append(f"VIX HIGH + BL proche (≤{bl_distance:.1f} ticks)")
            logger.info(f"🚫 Hard rule: VIX HIGH + BL proche - {bl_distance:.1f} ticks")
    
    # 3. Niveaux MenthorQ stales
    if levels.get('stale', False):
        if config.get('NO_TRADE_ON_STALE', True):
            hard_block = True
            reasons.append("Niveaux MenthorQ stales")
            logger.info("🚫 Hard rule: Niveaux MenthorQ stales")
        else:
            size_multiplier *= 0.3
            reasons.append("Niveaux stales → sizing réduit")
            logger.info("⚠️ Soft rule: Niveaux stales → sizing ×0.3")
    
    # 4. Cooldown après stop-out
    if context and context.get('last_stop_time'):
        cooldown_elapsed = _check_cooldown(context['last_stop_time'], config['COOLDOWN_MIN'])
        if not cooldown_elapsed:
            hard_block = True
            reasons.append(f"Cooldown actif ({config['COOLDOWN_MIN']}min)")
            logger.info(f"🚫 Hard rule: Cooldown actif - {config['COOLDOWN_MIN']}min")
    
    # Si hard block, retourner immédiatement
    if hard_block:
        return ExecutionRulesResult(
            hard_block=True,
            reasons=reasons,
            size_multiplier=0.0,
            min_stop_ticks=None,
            required_confluence=[]
        )
    
    # === SOFT ADJUSTMENTS (non bloquants) ===
    
    # 1. Gamma Wall proche
    gamma_distance = _get_gamma_distance(current_price, levels)
    if gamma_distance is not None and gamma_distance <= config['GAMMA_TICKS']:
        size_multiplier *= 0.5
        reasons.append(f"Gamma Wall proche ({gamma_distance:.1f} ticks)")
        logger.debug(f"📉 Soft rule: Gamma proche → sizing ×0.5")
    
    # 2. Swing adverse
    swing_adverse = _check_swing_adverse(current_price, levels, dealers_bias)
    if swing_adverse['is_adverse']:
        size_multiplier *= 0.7
        min_stop_ticks = max(min_stop_ticks or 0, swing_adverse['min_stop_ticks'])
        reasons.append(f"Swing adverse ({swing_adverse['distance']:.1f} ticks)")
        logger.debug(f"📉 Soft rule: Swing adverse → sizing ×0.7, stop {min_stop_ticks} ticks")
    
    # 3. Dealers Bias fort contre
    if dealers_bias <= config['DEALERS_BIAS_HARD']:
        required_confluence.append("BN")
        reasons.append(f"Dealers Bias très négatif ({dealers_bias:.3f})")
        logger.debug(f"⚠️ Soft rule: Dealers Bias très négatif → confluence BN requise")
    elif dealers_bias <= config['DEALERS_BIAS_SOFT']:
        size_multiplier *= 0.8
        reasons.append(f"Dealers Bias négatif ({dealers_bias:.3f})")
        logger.debug(f"📉 Soft rule: Dealers Bias négatif → sizing ×0.8")
    
    # 4. VIX cap (appliqué APRÈS les autres ajustements)
    vix_cap = config['SIZE_CAPS'].get(vix_regime, 1.0)
    if size_multiplier > vix_cap:
        size_multiplier = vix_cap
        reasons.append(f"VIX {vix_regime} → cap {vix_cap}")
        logger.debug(f"📉 Soft rule: VIX cap {vix_regime} → {vix_cap}")
    
    # 5. Spread large / faible liquidité
    if context and context.get('spread_ticks', 0) > 2:
        spread_factor = 0.8
        size_multiplier *= spread_factor
        reasons.append(f"Spread large ({context['spread_ticks']} ticks)")
        logger.debug(f"📉 Soft rule: Spread large → sizing ×{spread_factor}")
    
    # Log final
    logger.info(f"Règles exécution: hard_block={hard_block}, size_multiplier={size_multiplier:.3f}, raisons={len(reasons)}")
    
    return ExecutionRulesResult(
        hard_block=False,
        reasons=reasons,
        size_multiplier=size_multiplier,
        min_stop_ticks=min_stop_ticks,
        required_confluence=required_confluence
    )

# === HELPER FUNCTIONS ===

def _get_runtime_config(runtime: Optional[Any]) -> Dict[str, Any]:
    """Récupère la configuration runtime avec fallbacks"""
    if runtime is None:
        return {
            'BL_TICKS': DEFAULT_BL_TICKS,
            'GAMMA_TICKS': DEFAULT_GAMMA_TICKS,
            'SWING_TICKS': DEFAULT_SWING_TICKS,
            'MAX_AGE_MIN': DEFAULT_MAX_AGE_MIN,
            'COOLDOWN_MIN': DEFAULT_COOLDOWN_MIN,
            'SIZE_CAPS': DEFAULT_SIZE_CAPS,
            'DEALERS_BIAS_HARD': DEFAULT_DEALERS_BIAS_HARD,
            'DEALERS_BIAS_SOFT': DEFAULT_DEALERS_BIAS_SOFT,
            'NO_TRADE_ON_STALE': True
        }
    
    # Extraire config du runtime (à adapter selon la structure réelle)
    return {
        'BL_TICKS': getattr(runtime, 'BL_TICKS', DEFAULT_BL_TICKS),
        'GAMMA_TICKS': getattr(runtime, 'GAMMA_TICKS', DEFAULT_GAMMA_TICKS),
        'SWING_TICKS': getattr(runtime, 'SWING_TICKS', DEFAULT_SWING_TICKS),
        'MAX_AGE_MIN': getattr(runtime, 'MAX_AGE_MIN', DEFAULT_MAX_AGE_MIN),
        'COOLDOWN_MIN': getattr(runtime, 'COOLDOWN_MIN', DEFAULT_COOLDOWN_MIN),
        'SIZE_CAPS': getattr(runtime, 'SIZE_CAPS', DEFAULT_SIZE_CAPS),
        'DEALERS_BIAS_HARD': getattr(runtime, 'DEALERS_BIAS_HARD', DEFAULT_DEALERS_BIAS_HARD),
        'DEALERS_BIAS_SOFT': getattr(runtime, 'DEALERS_BIAS_SOFT', DEFAULT_DEALERS_BIAS_SOFT),
        'NO_TRADE_ON_STALE': getattr(runtime, 'NO_TRADE_ON_STALE', True)
    }

def _get_blind_spot_distance(current_price: float, levels: Dict[str, Any]) -> Optional[float]:
    """Calcule la distance au Blind Spot le plus proche en ticks"""
    blind_spots = levels.get('blind_spots', {})
    if not blind_spots:
        return None
    
    min_distance = float('inf')
    for label, price in blind_spots.items():
        if price > 0:
            distance = abs(current_price - price) * 4  # 4 ticks par point ES
            min_distance = min(min_distance, distance)
    
    return min_distance if min_distance != float('inf') else None

def _get_gamma_distance(current_price: float, levels: Dict[str, Any]) -> Optional[float]:
    """Calcule la distance à la Gamma Wall la plus proche en ticks"""
    gamma = levels.get('gamma', {})
    if not gamma:
        return None
    
    min_distance = float('inf')
    for label, price in gamma.items():
        if price > 0 and 'wall' in label.lower():
            distance = abs(current_price - price) * 4  # 4 ticks par point ES
            min_distance = min(min_distance, distance)
    
    return min_distance if min_distance != float('inf') else None

def _check_swing_adverse(current_price: float, levels: Dict[str, Any], dealers_bias: float) -> Dict[str, Any]:
    """Vérifie si un swing est adverse à la direction suggérée"""
    swing = levels.get('swing', {})
    if not swing:
        return {'is_adverse': False, 'distance': None, 'min_stop_ticks': None}
    
    # Direction suggérée par dealers_bias
    suggested_direction = 'long' if dealers_bias > 0 else 'short'
    
    min_distance = float('inf')
    adverse_swing = None
    
    for label, price in swing.items():
        if price > 0:
            distance = abs(current_price - price) * 4  # 4 ticks par point ES
            
            # Swing adverse: au-dessus pour un long, en-dessous pour un short
            is_adverse = (
                (suggested_direction == 'long' and price > current_price) or
                (suggested_direction == 'short' and price < current_price)
            )
            
            if is_adverse and distance < min_distance:
                min_distance = distance
                adverse_swing = price
    
    if adverse_swing is not None:
        return {
            'is_adverse': True,
            'distance': min_distance,
            'min_stop_ticks': max(8, int(min_distance * 1.5))  # Stop plus large
        }
    
    return {'is_adverse': False, 'distance': None, 'min_stop_ticks': None}

def _check_cooldown(last_stop_time: str, cooldown_min: int) -> bool:
    """Vérifie si le cooldown est écoulé"""
    try:
        from datetime import datetime, timezone, timedelta
        
        # Parser le timestamp
        if isinstance(last_stop_time, str):
            last_stop = datetime.fromisoformat(last_stop_time.replace('Z', '+00:00'))
        else:
            last_stop = last_stop_time
        
        # Vérifier cooldown
        now = datetime.now(timezone.utc)
        elapsed = now - last_stop
        return elapsed >= timedelta(minutes=cooldown_min)
        
    except Exception as e:
        logger.warning(f"Erreur vérification cooldown: {e}")
        return True  # En cas d'erreur, autoriser le trade

# === FACTORY FUNCTION ===

def create_menthorq_execution_rules() -> Any:
    """Factory function pour créer les règles d'exécution"""
    return evaluate_execution_rules

# === TESTING ===

def test_menthorq_execution_rules():
    """Test des règles d'exécution MenthorQ"""
    logger.info("=== TEST MenthorQ Execution Rules ===")
    
    try:
        # Test 1: BL proche (hard rule)
        levels_bl = {
            'blind_spots': {'BL 1': 5294.5},  # 2 ticks de distance
            'gamma': {},
            'swing': {},
            'stale': False
        }
        
        result1 = evaluate_execution_rules(
            current_price=5294.0,
            levels=levels_bl,
            vix_regime="MID",
            dealers_bias=0.0
        )
        
        assert result1.hard_block == True, "BL proche doit bloquer"
        assert result1.size_multiplier == 0.0, "Size multiplier doit être 0"
        assert "BL proche" in result1.reasons[0], "Raison doit mentionner BL"
        logger.info(f"✅ Test 1 OK: BL proche → hard_block={result1.hard_block}")
        
        # Test 2: Gamma proche (soft rule)
        levels_gamma = {
            'blind_spots': {},
            'gamma': {'Gamma Wall': 5294.5},  # 2 ticks de distance
            'swing': {},
            'stale': False
        }
        
        result2 = evaluate_execution_rules(
            current_price=5294.0,
            levels=levels_gamma,
            vix_regime="MID",
            dealers_bias=0.0
        )
        
        assert result2.hard_block == False, "Gamma proche ne doit pas bloquer"
        assert result2.size_multiplier == 0.5, "Size multiplier doit être 0.5"
        assert "Gamma Wall proche" in result2.reasons[0], "Raison doit mentionner Gamma"
        logger.info(f"✅ Test 2 OK: Gamma proche → size_multiplier={result2.size_multiplier}")
        
        # Test 3: VIX HIGH cap
        result3 = evaluate_execution_rules(
            current_price=5294.0,
            levels={'blind_spots': {}, 'gamma': {}, 'swing': {}, 'stale': False},
            vix_regime="HIGH",
            dealers_bias=0.0
        )
        
        assert result3.hard_block == False, "VIX HIGH ne doit pas bloquer"
        assert result3.size_multiplier == 0.4, "Size multiplier doit être 0.4 (VIX HIGH cap)"
        assert "VIX HIGH" in result3.reasons[0], "Raison doit mentionner VIX HIGH"
        logger.info(f"✅ Test 3 OK: VIX HIGH → size_multiplier={result3.size_multiplier}")
        
        # Test 4: Niveaux stales
        levels_stale = {
            'blind_spots': {},
            'gamma': {},
            'swing': {},
            'stale': True
        }
        
        result4 = evaluate_execution_rules(
            current_price=5294.0,
            levels=levels_stale,
            vix_regime="MID",
            dealers_bias=0.0
        )
        
        assert result4.hard_block == True, "Niveaux stales doivent bloquer"
        assert result4.size_multiplier == 0.0, "Size multiplier doit être 0"
        assert "stales" in result4.reasons[0], "Raison doit mentionner stales"
        logger.info(f"✅ Test 4 OK: Niveaux stales → hard_block={result4.hard_block}")
        
        # Test 5: Dealers Bias négatif
        result5 = evaluate_execution_rules(
            current_price=5294.0,
            levels={'blind_spots': {}, 'gamma': {}, 'swing': {}, 'stale': False},
            vix_regime="MID",
            dealers_bias=-0.4  # Entre SOFT et HARD
        )
        
        assert result5.hard_block == False, "Dealers Bias négatif ne doit pas bloquer"
        assert result5.size_multiplier == 0.6, "Size multiplier doit être 0.6 (VIX MID cap)"
        assert "Dealers Bias négatif" in result5.reasons[0], "Raison doit mentionner Dealers Bias"
        logger.info(f"✅ Test 5 OK: Dealers Bias négatif → size_multiplier={result5.size_multiplier}")
        
        logger.info("🎉 Tous les tests MenthorQ Execution Rules réussis!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erreur test: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    test_menthorq_execution_rules()