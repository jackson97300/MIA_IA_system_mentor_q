#!/usr/bin/env python3
"""
🔧 IV Tools - Helpers pour Volatilité Implicite
Outils pour l'intégration IV dans MIA_HYBRID_FINAL_PLUS
"""

import math
import pandas as pd
from typing import Dict, Any, Optional, Tuple
from datetime import datetime, timedelta

# ===== HELPERS IV DE BASE =====

def iv_percentile(iv_series: pd.Series) -> float:
    """
    Calcule le percentile de la dernière valeur IV
    
    Args:
        iv_series: Série pandas avec historique IV
        
    Returns:
        float: Percentile (0..1) de la dernière valeur
    """
    s = iv_series.dropna()
    if len(s) < 20: 
        return 0.5  # Valeur neutre si pas assez de données
    
    last = s.iloc[-1]
    rank = (s <= last).mean()
    return float(rank)

def expected_move(spot: float, iv_annual: float, days: int = 1) -> float:
    """
    Calcule l'expected move: EM ≈ S * IV * sqrt(T)
    
    Args:
        spot: Prix spot actuel
        iv_annual: Volatilité implicite annualisée (ex: 0.20 = 20%)
        days: Nombre de jours (défaut: 1)
        
    Returns:
        float: Expected move en points
    """
    T = max(days, 1) / 252.0
    return float(spot) * float(iv_annual) * math.sqrt(T)

def pick_iv_band(p: float) -> str:
    """
    Détermine la bande IV basée sur le percentile
    
    Args:
        p: Percentile (0..1)
        
    Returns:
        str: "LOW", "MID", ou "HIGH"
    """
    if p < 0.20: 
        return "LOW"
    if p < 0.60: 
        return "MID"
    return "HIGH"

# ===== CALCULS IV AVANCÉS =====

def calculate_iv_skew(iv_calls: float, iv_puts: float) -> Dict[str, float]:
    """
    Calcule le skew IV (puts - calls)
    
    Args:
        iv_calls: IV moyenne des calls
        iv_puts: IV moyenne des puts
        
    Returns:
        Dict avec skew et métriques
    """
    skew = iv_puts - iv_calls
    skew_bps = skew * 10000  # En basis points
    
    return {
        "skew_absolute": skew,
        "skew_bps": skew_bps,
        "skew_direction": "PUT" if skew > 0 else "CALL",
        "skew_strength": abs(skew_bps)
    }

def calculate_term_structure(iv_short: float, iv_long: float) -> Dict[str, Any]:
    """
    Calcule la structure temporelle IV
    
    Args:
        iv_short: IV court terme (ex: 30j)
        iv_long: IV long terme (ex: 90j)
        
    Returns:
        Dict avec métriques structure temporelle
    """
    spread = iv_short - iv_long
    spread_bps = spread * 10000
    
    structure = {
        "spread_absolute": spread,
        "spread_bps": spread_bps,
        "structure_type": "BACKWARDATION" if spread > 0 else "CONTANGO",
        "stress_level": "HIGH" if abs(spread_bps) > 150 else "NORMAL"
    }
    
    return structure

def calculate_iv_regime(iv_current: float, iv_history: pd.Series) -> Dict[str, Any]:
    """
    Détermine le régime IV basé sur historique
    
    Args:
        iv_current: IV actuelle
        iv_history: Historique IV
        
    Returns:
        Dict avec classification régime
    """
    if len(iv_history) < 20:
        return {"regime": "UNKNOWN", "confidence": 0.0}
    
    # Percentiles historiques
    p25 = iv_history.quantile(0.25)
    p75 = iv_history.quantile(0.75)
    
    # Classification
    if iv_current <= p25:
        regime = "LOW_VOL"
        confidence = 1.0 - (iv_current / p25)
    elif iv_current >= p75:
        regime = "HIGH_VOL"
        confidence = (iv_current - p75) / (iv_history.max() - p75)
    else:
        regime = "NORMAL_VOL"
        confidence = 0.5
    
    return {
        "regime": regime,
        "confidence": min(confidence, 1.0),
        "percentile": iv_percentile(iv_history),
        "p25": p25,
        "p75": p75
    }

# ===== INTÉGRATION CONFIGURATION =====

def apply_iv_adaptation(config: Dict[str, Any], features: Dict[str, Any]) -> Dict[str, Any]:
    """
    Applique l'adaptation IV à la configuration
    
    Args:
        config: Configuration MIA_HYBRID_FINAL_PLUS
        features: Features actuelles (prix, IV, etc.)
        
    Returns:
        Dict avec adaptations appliquées
    """
    iv_cfg = config.get("iv_adapter", {})
    if not iv_cfg.get("enabled", False):
        return {"iv_adaptation": "disabled"}
    
    # 1) Lire IV 30j depuis snapshot
    iv30 = features.get("iv30_annual", 0.20)
    iv_pct = features.get("iv30_percentile", 0.50)
    iv_band = pick_iv_band(iv_pct)
    
    # 2) Multipliers seuils
    bands = iv_cfg.get("bands", {})
    if iv_band in bands:
        b = bands[iv_band]
        fast_thr = config["workflow_modes"]["fast_track_threshold_base"] * b.get("fast_mult", 1.0)
        std_thr = config["workflow_modes"]["standard_track_threshold_base"] * b.get("std_mult", 1.0)
    else:
        fast_thr = config["workflow_modes"]["fast_track_threshold_base"]
        std_thr = config["workflow_modes"]["standard_track_threshold_base"]
    
    # 3) Votes adaptatifs
    required_votes = config["votes"]["base_required"] + b.get("votes_delta", 0)
    
    # 4) Sizing & guardrails
    sizing = iv_cfg.get("sizing", {})
    if iv_band in sizing:
        sz = sizing[iv_band]
        size_mult = sz.get("size_mult", 1.0)
        atr_mult = config["exits"]["stops"]["atr_mult"] * sz.get("atr_mult", 1.0)
        sd2_factor = min(
            config["gates"]["beyond_sd2_size_factor"],
            sz.get("beyond_sd2_size_factor", 0.5)
        )
    else:
        size_mult = 1.0
        atr_mult = config["exits"]["stops"]["atr_mult"]
        sd2_factor = config["gates"]["beyond_sd2_size_factor"]
    
    # 5) Expected move caps
    em_caps = {}
    guardrails = iv_cfg.get("guardrails", {})
    if guardrails.get("use_expected_move", False):
        spot_price = features.get("last_price", 0.0)
        em = expected_move(spot_price, iv30, guardrails.get("expected_move_days", 1))
        em_caps = {
            "tp_cap": em * guardrails.get("tp_cap_em_mult", 1.5),
            "sl_floor": em * guardrails.get("sl_floor_em_mult", 0.4),
            "expected_move": em
        }
    
    # 6) Skew bias
    skew_bias = {}
    skew_cfg = iv_cfg.get("skew_bias", {})
    if skew_cfg.get("enabled", False):
        skew_bps = features.get("skew_put25_minus_call25_bps", 0)
        threshold = skew_cfg.get("put25_minus_call25_bps", 300)
        bias_weight = skew_cfg.get("bias_weight_bump", 0.02)
        
        if skew_bps >= threshold:
            skew_bias["confluence_bias_bump_short"] = bias_weight
        elif skew_bps <= -threshold:
            skew_bias["confluence_bias_bump_long"] = bias_weight
    
    # 7) Term structure guard
    fast_track_allowed = True
    term_cfg = iv_cfg.get("term_structure", {})
    if term_cfg.get("enabled", False):
        st_short = features.get("iv30_annual", iv30)
        st_long = features.get("iv90_annual", iv30)
        threshold = term_cfg.get("short_iv_minus_long_iv_bps", 150) / 10000
        
        if (st_short - st_long) >= threshold:
            if iv_band == "HIGH" and term_cfg.get("fast_track_hard_off_in_high", False):
                fast_track_allowed = False
    
    return {
        "iv_band": iv_band,
        "iv_percentile": iv_pct,
        "iv_current": iv30,
        "fast_threshold": fast_thr,
        "standard_threshold": std_thr,
        "required_votes": required_votes,
        "size_multiplier": size_mult,
        "atr_multiplier": atr_mult,
        "sd2_factor": sd2_factor,
        "expected_move_caps": em_caps,
        "skew_bias": skew_bias,
        "fast_track_allowed": fast_track_allowed,
        "adaptation_applied": True
    }

# ===== UTILITAIRES IV =====

def extract_iv_from_snapshot(snapshot_data: Dict[str, Any], symbol: str = "SPX") -> Dict[str, float]:
    """
    Extrait les données IV depuis un snapshot options
    
    Args:
        snapshot_data: Données snapshot JSON
        symbol: Symbole (SPX/NDX)
        
    Returns:
        Dict avec métriques IV
    """
    analysis = snapshot_data.get("analysis", {})
    
    return {
        "iv30_annual": analysis.get("implied_volatility_avg", 0.20),
        "iv_calls_avg": analysis.get("iv_calls_avg", 0.20),
        "iv_puts_avg": analysis.get("iv_puts_avg", 0.20),
        "iv_skew": analysis.get("iv_skew_puts_minus_calls", 0.0),
        "vol_index": analysis.get("vix" if symbol == "SPX" else "vxn", 20.0)
    }

def calculate_iv_percentile_from_history(iv_history: pd.Series, window_days: int = 252) -> float:
    """
    Calcule le percentile IV sur une fenêtre glissante
    
    Args:
        iv_history: Historique IV
        window_days: Fenêtre en jours
        
    Returns:
        float: Percentile actuel
    """
    if len(iv_history) < window_days:
        return 0.5
    
    recent_iv = iv_history.tail(window_days)
    return iv_percentile(recent_iv)

def validate_iv_data(iv_data: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Valide les données IV
    
    Args:
        iv_data: Données IV
        
    Returns:
        Tuple (is_valid, error_message)
    """
    required_fields = ["iv30_annual", "iv_percentile"]
    
    for field in required_fields:
        if field not in iv_data:
            return False, f"Champ manquant: {field}"
        
        value = iv_data[field]
        if not isinstance(value, (int, float)) or value < 0:
            return False, f"Valeur invalide pour {field}: {value}"
    
    # Validation spécifique
    if iv_data["iv30_annual"] > 1.0:  # > 100%
        return False, f"IV trop élevée: {iv_data['iv30_annual']}"
    
    if iv_data["iv_percentile"] > 1.0:  # > 100%
        return False, f"Percentile invalide: {iv_data['iv_percentile']}"
    
    return True, "OK"

# ===== TESTS =====

def test_iv_tools():
    """Test des fonctions IV"""
    print("🧪 Test IV Tools...")
    
    # Test percentile
    test_series = pd.Series([0.15, 0.18, 0.20, 0.22, 0.25, 0.30, 0.35])
    pct = iv_percentile(test_series)
    print(f"✅ Percentile test: {pct:.3f}")
    
    # Test expected move
    em = expected_move(5000.0, 0.20, 1)
    print(f"✅ Expected move test: {em:.2f} points")
    
    # Test band selection
    bands = [pick_iv_band(0.1), pick_iv_band(0.4), pick_iv_band(0.8)]
    print(f"✅ Band selection test: {bands}")
    
    # Test skew calculation
    skew = calculate_iv_skew(0.18, 0.22)
    print(f"✅ Skew calculation test: {skew}")
    
    print("✅ Tous les tests IV passés!")

if __name__ == "__main__":
    test_iv_tools()

