#!/usr/bin/env python3
"""
📊 UNIFIED STOPS - MIA_IA_SYSTEM
===============================

Module unifié pour la gestion des stops-loss et take-profits
Standardise tous les stops à 7 ticks partout selon les préférences utilisateur

Remplace les implémentations VIX-adaptatives par une approche simple et cohérente :
- Stop fixe : 7 ticks ($87.50)
- Take Profit : 2R (14 ticks, $175.00)
- Cohérent avec l'expérience utilisateur
"""

from typing import Dict, Any, Optional, Tuple
from core.base_types import ES_TICK_SIZE, ES_TICK_VALUE
from core.logger import get_logger

logger = get_logger(__name__)

# === CONSTANTES UNIFIÉES ===

# Configuration des stops unifiés (entrée 4 ticks, stop 7 ticks)
UNIFIED_STOP_CONFIG = {
    "entry_tolerance_ticks": 4,      # 4 ticks pour l'entrée
    "fixed_stop_ticks": 7,           # 7 ticks pour le stop (inchangé)
    "fixed_stop_dollars": 7 * ES_TICK_VALUE,  # $87.50
    "risk_reward_ratio": 2.0,
    "take_profit_ticks": 14,  # 2R (inchangé)
    "take_profit_dollars": 14 * ES_TICK_VALUE,  # $175.00
    "description": "Entrée 4 ticks, Stop 7 ticks - Simple et cohérent"
}

# === FONCTIONS UNIFIÉES ===

def calculate_unified_stops(
    entry_price: float,
    side: str,
    level_price: Optional[float] = None,
    vix_value: Optional[float] = None,
    use_fixed: bool = True
) -> Dict[str, Any]:
    """
    Calcule les niveaux E/U/L unifiés avec stops fixes
    
    Args:
        entry_price: Prix d'entrée
        side: 'LONG' ou 'SHORT'
        level_price: Prix du niveau MenthorQ (optionnel)
        vix_value: Valeur VIX (ignorée si use_fixed=True)
        use_fixed: True pour 7 ticks partout, False pour VIX-adaptatif (déprécié)
        
    Returns:
        Dict avec entry, stop, target1, target2, risk_ticks, risk_dollars
    """
    try:
        if use_fixed:
            # === APPROCHE FIXE : ENTRÉE 4 TICKS, STOP 7 TICKS ===
            stop_ticks = UNIFIED_STOP_CONFIG["fixed_stop_ticks"]  # 7 ticks pour stop
            tp_ticks = UNIFIED_STOP_CONFIG["take_profit_ticks"]   # 14 ticks pour TP
            
            logger.debug(f"📊 Unified Stops: Entrée 4 ticks, Stop 7 ticks (entry={entry_price}, side={side})")
            
        else:
            # === APPROCHE VIX-ADAPTATIVE (DÉPRÉCIÉE) ===
            logger.warning("⚠️ VIX-adaptatif déprécié, utilisation des stops fixes recommandée")
            
            if vix_value is None:
                vix_value = 20.0  # Valeur par défaut
            
            # Mapping VIX déprécié (conservé pour compatibilité)
            if vix_value < 15:
                stop_ticks = 3
            elif vix_value < 22:
                stop_ticks = 4
            elif vix_value < 35:
                stop_ticks = 6
            else:
                stop_ticks = 8
                
            tp_ticks = stop_ticks * 2  # 2R
        
        # Calculs des prix
        stop_distance = stop_ticks * ES_TICK_SIZE
        tp_distance = tp_ticks * ES_TICK_SIZE
        
        if side.upper() in ['LONG', 'GO_LONG']:
            stop_price = entry_price - stop_distance
            target1 = entry_price + tp_distance
            target2 = entry_price + (tp_distance * 1.5)  # 3R
            
        else:  # SHORT
            stop_price = entry_price + stop_distance
            target1 = entry_price - tp_distance
            target2 = entry_price - (tp_distance * 1.5)  # 3R
        
        # Calcul des risques
        risk_dollars = stop_ticks * ES_TICK_VALUE
        
        result = {
            "entry": round(entry_price, 2),
            "stop": round(stop_price, 2),
            "target1": round(target1, 2),
            "target2": round(target2, 2),
            "risk_ticks": stop_ticks,
            "risk_dollars": risk_dollars,
            "reward_ticks": tp_ticks,
            "reward_dollars": tp_ticks * ES_TICK_VALUE,
            "risk_reward_ratio": tp_ticks / stop_ticks,
            "method": "entry_4_stop_7_ticks" if use_fixed else "vix_adaptive"
        }
        
        logger.info(f"✅ Unified Stops calculés: {side} @ {entry_price} → "
                   f"Stop={stop_price} ({stop_ticks}T), TP={target1} ({tp_ticks}T), "
                   f"Risk=${risk_dollars:.2f}")
        
        return result
        
    except Exception as e:
        logger.error(f"❌ Erreur calcul Unified Stops: {e}")
        return {}

def validate_stop_levels(
    entry: float,
    stop: float,
    target: float,
    side: str,
    min_risk_reward: float = 1.5
) -> Dict[str, Any]:
    """
    Valide la cohérence des niveaux de stop et target
    
    Args:
        entry: Prix d'entrée
        stop: Prix de stop
        target: Prix de target
        side: 'LONG' ou 'SHORT'
        min_risk_reward: Ratio R/R minimum accepté
        
    Returns:
        Dict avec is_valid, issues, risk_reward_ratio
    """
    issues = []
    
    try:
        # Calcul des distances
        if side.upper() in ['LONG', 'GO_LONG']:
            risk_distance = entry - stop
            reward_distance = target - entry
            
            if stop >= entry:
                issues.append("Stop >= Entry pour LONG")
            if target <= entry:
                issues.append("Target <= Entry pour LONG")
                
        else:  # SHORT
            risk_distance = stop - entry
            reward_distance = entry - target
            
            if stop <= entry:
                issues.append("Stop <= Entry pour SHORT")
            if target >= entry:
                issues.append("Target >= Entry pour SHORT")
        
        # Validation des distances
        if risk_distance <= 0:
            issues.append("Distance de risque invalide")
        if reward_distance <= 0:
            issues.append("Distance de reward invalide")
        
        # Calcul ratio R/R
        risk_reward_ratio = reward_distance / risk_distance if risk_distance > 0 else 0
        
        if risk_reward_ratio < min_risk_reward:
            issues.append(f"Ratio R/R trop faible: {risk_reward_ratio:.2f} < {min_risk_reward}")
        
        is_valid = len(issues) == 0
        
        if is_valid:
            logger.debug(f"✅ Niveaux validés: {side} R/R={risk_reward_ratio:.2f}")
        else:
            logger.warning(f"⚠️ Niveaux invalides: {', '.join(issues)}")
        
        return {
            "is_valid": is_valid,
            "issues": issues,
            "risk_reward_ratio": round(risk_reward_ratio, 2),
            "risk_distance": round(risk_distance, 2),
            "reward_distance": round(reward_distance, 2),
            "risk_ticks": round(risk_distance / ES_TICK_SIZE, 1),
            "reward_ticks": round(reward_distance / ES_TICK_SIZE, 1)
        }
        
    except Exception as e:
        logger.error(f"❌ Erreur validation stops: {e}")
        return {
            "is_valid": False,
            "issues": [f"Erreur validation: {e}"],
            "risk_reward_ratio": 0
        }

def migrate_legacy_stops(old_config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Migre les anciennes configurations de stops vers le système unifié
    
    Args:
        old_config: Ancienne configuration (VIX-adaptative ou autre)
        
    Returns:
        Nouvelle configuration unifiée
    """
    try:
        # Détecter le type d'ancienne config
        if "stop_ticks" in old_config:
            old_method = "simple"
            old_stop_ticks = old_config["stop_ticks"]
        elif "LOW" in str(old_config):
            old_method = "vix_adaptive"
            old_stop_ticks = "variable"
        else:
            old_method = "unknown"
            old_stop_ticks = "unknown"
        
        logger.info(f"🔄 Migration stops: {old_method} (stop={old_stop_ticks}) → "
                   f"unified_7_ticks")
        
        # Nouvelle config unifiée
        new_config = UNIFIED_STOP_CONFIG.copy()
        new_config.update({
            "migration_info": {
                "old_method": old_method,
                "old_stop_ticks": old_stop_ticks,
                "migrated_at": "2025-01-01",
                "reason": "Standardisation 7 ticks partout selon préférences utilisateur"
            }
        })
        
        return new_config
        
    except Exception as e:
        logger.error(f"❌ Erreur migration stops: {e}")
        return UNIFIED_STOP_CONFIG

# === HELPERS DE COMPATIBILITÉ ===

def get_stop_ticks_for_vix(vix_value: float) -> int:
    """
    Helper de compatibilité - retourne toujours 7 ticks
    (ancienne logique VIX-adaptative dépréciée)
    """
    logger.debug(f"📊 get_stop_ticks_for_vix({vix_value}) → 7 ticks (unified)")
    return UNIFIED_STOP_CONFIG["fixed_stop_ticks"]

def get_legacy_vix_stops(vix_value: float) -> Dict[str, int]:
    """
    Retourne l'ancien mapping VIX pour compatibilité
    (déprécié - utiliser calculate_unified_stops)
    """
    logger.warning("⚠️ get_legacy_vix_stops déprécié - utiliser calculate_unified_stops")
    
    return {
        "LOW": 7,    # Unifié
        "MID": 7,    # Unifié
        "HIGH": 7,   # Unifié
        "EXTREME": 7 # Unifié
    }

# === EXPORTS ===

__all__ = [
    'UNIFIED_STOP_CONFIG',
    'calculate_unified_stops',
    'validate_stop_levels',
    'migrate_legacy_stops',
    'get_stop_ticks_for_vix',
    'get_legacy_vix_stops'
]

# === TEST ===

def test_unified_stops():
    """Test du système de stops unifiés"""
    logger.info("🧪 Test Unified Stops...")
    
    # Test LONG
    long_result = calculate_unified_stops(4500.0, "LONG", use_fixed=True)
    logger.info(f"LONG Test: {long_result}")
    
    # Test SHORT  
    short_result = calculate_unified_stops(4500.0, "SHORT", use_fixed=True)
    logger.info(f"SHORT Test: {short_result}")
    
    # Test validation
    validation = validate_stop_levels(4500.0, 4498.25, 4503.50, "LONG")
    logger.info(f"Validation: {validation}")
    
    logger.info("✅ Test Unified Stops terminé")

if __name__ == "__main__":
    test_unified_stops()

