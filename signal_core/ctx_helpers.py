#!/usr/bin/env python3
"""
MIA_IA_SYSTEM - Context Helpers
Fonctions utilitaires pour éviter la redondance de code dans les stratégies

Version: Production Ready v1.0
Performance: <0.1ms par fonction
Responsabilité: Helpers pour les stratégies de trading
"""

from typing import Dict, Optional, Tuple, Any


def get_tick_atr(ctx: Dict[str, Any], default_tick: float = 0.25) -> Tuple[float, float]:
    """
    Récupère le tick size et l'ATR depuis le contexte
    
    Args:
        ctx: Contexte de trading
        default_tick: Tick size par défaut (ES = 0.25)
        
    Returns:
        Tuple (tick_size, atr)
    """
    tick = ctx.get("tick_size", default_tick)
    atr = max(ctx.get("atr", 4 * tick), 2 * tick)
    return tick, atr


def nearest_zero_dte_wall(menthorq: Dict[str, Any], price: float) -> Tuple[Optional[str], Optional[float]]:
    """
    Trouve le mur 0DTE le plus proche du prix
    
    Args:
        menthorq: Données MenthorQ
        price: Prix actuel
        
    Returns:
        Tuple (wall_name, wall_price) ou (None, None) si pas trouvé
    """
    zero_dte = menthorq.get("zero_dte", {}) or {}
    candidates = [(k, v) for k, v in zero_dte.items() if isinstance(v, (int, float))]
    
    if not candidates:
        return None, None
    
    name, level = min(candidates, key=lambda kv: abs(price - kv[1]))
    return name, level


def nearest_gamma_wall(menthorq: Dict[str, Any], price: float) -> Optional[float]:
    """
    Trouve le mur gamma le plus proche du prix
    
    Args:
        menthorq: Données MenthorQ
        price: Prix actuel
        
    Returns:
        Prix du mur gamma ou None si pas trouvé
    """
    # Essayer d'abord zero_dte.gamma_wall
    gamma_wall = (menthorq.get("zero_dte", {}) or {}).get("gamma_wall")
    if gamma_wall:
        return gamma_wall
    
    # Essayer gamma_wall_0dte
    gamma_wall = menthorq.get("gamma_wall_0dte")
    if gamma_wall:
        return gamma_wall
    
    # Essayer dans les niveaux gamma génériques
    gamma_levels = menthorq.get("gamma_levels", [])
    if gamma_levels:
        return min(gamma_levels, key=lambda x: abs(price - x))
    
    return None


def get_gex_cluster_bounds(menthorq: Dict[str, Any]) -> Optional[Tuple[float, float, float]]:
    """
    Calcule les bornes d'un cluster GEX
    
    Args:
        menthorq: Données MenthorQ
        
    Returns:
        Tuple (low, high, span_ticks) ou None si pas de cluster
    """
    gex_levels = menthorq.get("gex_levels") or [
        x for k, x in menthorq.items() 
        if str(k).startswith("gex_") and isinstance(x, (int, float))
    ]
    
    if not gex_levels:
        return None
    
    lo, hi = min(gex_levels), max(gex_levels)
    span_ticks = hi - lo  # En points, pas en ticks
    return lo, hi, span_ticks


def get_call_put_levels(menthorq: Dict[str, Any]) -> Tuple[Optional[float], Optional[float]]:
    """
    Récupère les niveaux CALL et PUT
    
    Args:
        menthorq: Données MenthorQ
        
    Returns:
        Tuple (call_level, put_level)
    """
    zero_dte = menthorq.get("zero_dte", {}) or {}
    
    call = zero_dte.get("call") or menthorq.get("call_resistance")
    put = zero_dte.get("put") or menthorq.get("put_support")
    
    return call, put


def calculate_distance_ticks(price1: float, price2: float, tick_size: float) -> float:
    """
    Calcule la distance entre deux prix en ticks
    
    Args:
        price1: Premier prix
        price2: Deuxième prix
        tick_size: Taille du tick
        
    Returns:
        Distance en ticks
    """
    return abs(price1 - price2) / max(tick_size, 1e-9)


def is_near_level(price: float, level: float, max_distance_ticks: float, tick_size: float) -> bool:
    """
    Vérifie si un prix est proche d'un niveau
    
    Args:
        price: Prix actuel
        level: Niveau de référence
        max_distance_ticks: Distance maximale en ticks
        tick_size: Taille du tick
        
    Returns:
        True si proche, False sinon
    """
    distance_ticks = calculate_distance_ticks(price, level, tick_size)
    return distance_ticks <= max_distance_ticks


def get_target_levels(ctx: Dict[str, Any], direction: str, base_price: float, tick_size: float) -> list:
    """
    Génère des niveaux de target basés sur le contexte
    
    Args:
        ctx: Contexte de trading
        direction: "LONG" ou "SHORT"
        base_price: Prix de base
        tick_size: Taille du tick
        
    Returns:
        Liste des niveaux de target
    """
    targets = []
    
    # VWAP levels
    vwap = ctx.get("vwap", {})
    if direction == "LONG":
        if vwap.get("sd1_up"):
            targets.append(vwap["sd1_up"])
        if vwap.get("sd2_up"):
            targets.append(vwap["sd2_up"])
    else:  # SHORT
        if vwap.get("sd1_dn"):
            targets.append(vwap["sd1_dn"])
        if vwap.get("sd2_dn"):
            targets.append(vwap["sd2_dn"])
    
    # VPOC
    vpoc = ctx.get("vva", {}).get("vpoc")
    if vpoc:
        targets.append(vpoc)
    
    # Fallback targets
    if not targets:
        if direction == "LONG":
            targets = [base_price + 4 * tick_size, base_price + 8 * tick_size]
        else:
            targets = [base_price - 4 * tick_size, base_price - 8 * tick_size]
    
    return targets


def validate_signal_risk_reward(entry: float, stop: float, targets: list, min_rr: float = 1.0) -> bool:
    """
    Valide qu'un signal a un ratio risque/récompense acceptable
    
    Args:
        entry: Prix d'entrée
        stop: Prix de stop
        targets: Liste des targets
        min_rr: Ratio risque/récompense minimum
        
    Returns:
        True si le R:R est acceptable, False sinon
    """
    if not targets:
        return False
    
    risk = abs(entry - stop)
    if risk <= 0:
        return False
    
    # Prendre le premier target comme référence
    target = targets[0]
    reward = abs(target - entry)
    
    if reward <= 0:
        return False
    
    rr_ratio = reward / risk
    return rr_ratio >= min_rr


def get_session_context(ctx: Dict[str, Any]) -> Dict[str, Any]:
    """
    Récupère le contexte de session depuis le contexte global
    
    Args:
        ctx: Contexte de trading
        
    Returns:
        Dictionnaire avec les informations de session
    """
    session = ctx.get("session", {})
    return {
        "label": session.get("label", "OTHER"),
        "time_ok": session.get("time_ok", True),
        "is_open": session.get("label") == "OPEN",
        "is_power_hour": session.get("label") == "POWER",
        "is_lunch": session.get("label") == "LUNCH"
    }


def get_vix_context(ctx: Dict[str, Any]) -> Dict[str, Any]:
    """
    Récupère le contexte VIX depuis le contexte global
    
    Args:
        ctx: Contexte de trading
        
    Returns:
        Dictionnaire avec les informations VIX
    """
    vix = ctx.get("vix", {})
    return {
        "last": vix.get("last", 20.0),
        "rising": vix.get("rising", False),
        "regime": "HIGH" if vix.get("last", 20) > 25 else "LOW" if vix.get("last", 20) < 15 else "MID"
    }


def get_orderflow_context(ctx: Dict[str, Any]) -> Dict[str, Any]:
    """
    Récupère le contexte orderflow depuis le contexte global
    
    Args:
        ctx: Contexte de trading
        
    Returns:
        Dictionnaire avec les informations orderflow
    """
    of = ctx.get("orderflow", {})
    return {
        "delta_burst": of.get("delta_burst", False),
        "delta_flip": of.get("delta_flip", False),
        "cvd_divergence": of.get("cvd_divergence", False),
        "stacked_imbalance": of.get("stacked_imbalance", {}),
        "absorption": of.get("absorption", {}),
        "iceberg": of.get("iceberg", {})
    }


def get_menthorq_context(ctx: Dict[str, Any]) -> Dict[str, Any]:
    """
    Récupère le contexte MenthorQ depuis le contexte global
    
    Args:
        ctx: Contexte de trading
        
    Returns:
        Dictionnaire avec les informations MenthorQ
    """
    mq = ctx.get("menthorq", {})
    return {
        "gamma_flip": mq.get("gamma_flip", False),
        "zero_dte": mq.get("zero_dte", {}),
        "hvl": mq.get("hvl"),
        "d1max": mq.get("d1max"),
        "d1min": mq.get("d1min"),
        "gex_levels": mq.get("gex_levels", []),
        "call_resistance": mq.get("call_resistance"),
        "put_support": mq.get("put_support")
    }


# === CONSTANTS ===

# Seuils par défaut pour les stratégies
DEFAULT_THRESHOLDS = {
    "max_dist_ticks": 8,
    "min_wick_ticks": 6,
    "min_channel_ticks": 20,
    "cluster_span_ticks": 16,
    "atr_mult_sl": 1.0,
    "min_conf": 0.60,
    "min_rr_ratio": 1.0
}

# Tags de famille pour le dédoublonnage
FAMILY_TAGS = {
    "zero_dte_wall_sweep_reversal": "REVERSAL",
    "gamma_wall_break_and_go": "BREAKOUT",
    "hvl_magnet_fade": "MEAN_REVERT",
    "d1_extreme_trap": "TRAP",
    "gex_cluster_mean_revert": "MEAN_REVERT",
    "call_put_channel_rotation": "RANGE_ROTATION",
    # Existing strategies
    "dealer_flip_breakout": "BREAKOUT",
    "vwap_band_squeeze_break": "BREAKOUT",
    "liquidity_sweep_reversal": "REVERSAL",
    "gamma_pin_reversion": "REVERSAL",
    "profile_gap_fill": "MEAN_REVERT",
    "cvd_divergence_trap": "TRAP",
    "stacked_imbalance_continuation": "CONTINUATION",
    "iceberg_tracker_follow": "FOLLOW",
    "opening_drive_fail": "REVERSAL",
    "es_nq_lead_lag_mirror": "CORRELATION",
}

