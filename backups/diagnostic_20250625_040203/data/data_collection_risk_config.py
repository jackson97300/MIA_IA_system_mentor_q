#!/usr/bin/env python3
"""
MIA_IA_SYSTEM - Data Collection Risk Configuration
Configuration spécialisée pour collecter 500-1000 trades rapidement
Version: Production Ready
Location: D:\MIA_IA_system\config\data_collection_risk_config.py

OBJECTIF: Paramètres optimisés pour collecter un maximum de données
- Mode DATA_COLLECTION: Seuils réduits pour plus de trades
- Mode PAPER: Paramètres standards de validation
- Mode LIVE: Paramètres stricts pour trading réel
"""

from dataclasses import dataclass, field
from datetime import time
from typing import Dict
from execution.risk_manager import RiskParameters
import logging

# Configure logging
logger = logging.getLogger(__name__)


# === DATA COLLECTION MODE (500-1000 TRADES) ===

DATA_COLLECTION_RISK_PARAMS = RiskParameters(
    # Position sizing - Plus agressif pour collecter
    base_position_size=1,                    # Taille base réduite
    max_position_size=3,                     # Max 3 contrats
    max_positions_concurrent=2,              # 2 positions simultanées
    
    # Risk per trade - Réduit pour plus de trades
    risk_per_trade_percent=0.5,             # 0.5% du capital (vs 1% normal)
    max_risk_per_trade_dollars=250.0,       # $250 max par trade
    
    # Daily limits - Optimisé pour collecte données
    daily_loss_limit=1000.0,                # $1000 limite perte (SEULE VRAIE LIMITE)
    daily_profit_target=5000.0,             # $5000 target (très élevé = pas d'arrêt)
    max_daily_trades=999,                   # Pas de limite trades!
    
    # Drawdown - Permissif
    max_drawdown_percent=8.0,               # 8% drawdown max
    trailing_drawdown=True,
    
    # Bataille Navale - SEUILS RÉDUITS pour plus de trades
    min_base_quality_for_trade=0.4,         # 0.4 vs 0.6 normal (40% plus de trades)
    min_confluence_score=0.45,              # 0.45 vs 0.65 normal (35% plus de trades)
    min_signal_probability=0.55,            # 55% probabilité minimum (vs 70% normal)
    golden_rule_strict=False,               # Désactivé pour plus de trades
    
    # Mode collecte activé
    data_collection_mode=True,              # MODE SPÉCIAL ACTIVÉ
    
    # Time restrictions - Étendues pour plus d'opportunités
    no_trade_before=time(9, 31),           # 1 min après ouverture (vs 5 min)
    no_trade_after=time(15, 55),           # 5 min avant fermeture (vs 15 min)
    reduce_size_after=time(15, 30),        # Réduction plus tardive
    
    # Volatility - Moins restrictif
    high_volatility_threshold=40.0,         # Seuil VIX plus élevé
    reduce_size_high_vol=False,            # Pas de réduction volatilité
    
    # Session multipliers - Plus agressifs
    session_risk_multipliers={
        'asian': 0.8,      # Moins de réduction Asie
        'london': 1.2,     # Boost Londres  
        'ny_am': 1.5,      # BOOST matin NY (meilleur moment)
        'ny_pm': 1.0,      # Normal après-midi
        'close': 0.7       # Réduit fin journée
    }
)

# === PAPER TRADING MODE (VALIDATION) ===

PAPER_TRADING_RISK_PARAMS = RiskParameters(
    # Position sizing - Standard
    base_position_size=2,
    max_position_size=4,
    max_positions_concurrent=2,
    
    # Risk per trade - Standard
    risk_per_trade_percent=1.0,             # 1% standard
    max_risk_per_trade_dollars=500.0,
    
    # Daily limits - Standards
    daily_loss_limit=800.0,                 # $800 perte quotidienne
    daily_profit_target=1200.0,             # $1200 target
    max_daily_trades=50,                    # 50 trades max/jour
    
    # Drawdown - Standard
    max_drawdown_percent=5.0,
    trailing_drawdown=True,
    
    # Bataille Navale - Standards
    min_base_quality_for_trade=0.6,         # 60% qualité base
    min_confluence_score=0.65,              # 65% confluence
    min_signal_probability=0.70,            # 70% probabilité
    golden_rule_strict=True,                # Règle rouge/verte active
    
    # Mode normal
    data_collection_mode=False,
    
    # Time restrictions - Standards
    no_trade_before=time(9, 35),
    no_trade_after=time(15, 45),
    reduce_size_after=time(15, 0),
    
    # Volatility - Standard
    high_volatility_threshold=30.0,
    reduce_size_high_vol=True,
    
    # Session multipliers - Standards
    session_risk_multipliers={
        'asian': 0.5,
        'london': 1.0,
        'ny_am': 1.2,
        'ny_pm': 0.8,
        'close': 0.5
    }
)

# === LIVE TRADING MODE (PRODUCTION) ===

LIVE_TRADING_RISK_PARAMS = RiskParameters(
    # Position sizing - Conservateur
    base_position_size=1,                    # Plus petit en live
    max_position_size=3,
    max_positions_concurrent=1,              # 1 seule position en live!
    
    # Risk per trade - Très conservateur
    risk_per_trade_percent=0.75,            # 0.75% seulement
    max_risk_per_trade_dollars=400.0,       # $400 max
    
    # Daily limits - Stricts (prop firm)
    daily_loss_limit=600.0,                 # $600 limite STRICTE
    daily_profit_target=800.0,              # $800 target
    max_daily_trades=30,                    # 30 trades max
    
    # Drawdown - Très strict
    max_drawdown_percent=3.0,               # 3% seulement!
    trailing_drawdown=True,
    
    # Bataille Navale - Très sélectif
    min_base_quality_for_trade=0.75,        # 75% qualité minimum
    min_confluence_score=0.80,              # 80% confluence minimum
    min_signal_probability=0.80,            # 80% probabilité minimum
    golden_rule_strict=True,                # Règle STRICTE
    
    # Mode production
    data_collection_mode=False,
    
    # Time restrictions - Conservatrices
    no_trade_before=time(9, 40),           # 10 min après ouverture
    no_trade_after=time(15, 30),           # 30 min avant fermeture
    reduce_size_after=time(14, 30),        # Réduction précoce
    
    # Volatility - Très conservateur
    high_volatility_threshold=25.0,         # Seuil VIX bas
    reduce_size_high_vol=True,
    
    # Session multipliers - Conservateurs
    session_risk_multipliers={
        'asian': 0.3,      # Très réduit Asie
        'london': 0.8,     # Réduit Londres
        'ny_am': 1.0,      # Normal matin NY
        'ny_pm': 0.6,      # Très réduit après-midi
        'close': 0.2       # Quasi-arrêt fin journée
    }
)

# === FACTORY FUNCTION ===

def get_risk_params_for_mode(mode: str) -> RiskParameters:
    """
    Retourne les paramètres de risque selon le mode
    
    Args:
        mode: "data_collection", "paper", "live"
        
    Returns:
        RiskParameters configurés pour le mode
    """
    mode = mode.lower().strip()
    
    if mode in ["data_collection", "collect", "data"]:
        return DATA_COLLECTION_RISK_PARAMS
    elif mode in ["paper", "paper_trading", "simulation"]:
        return PAPER_TRADING_RISK_PARAMS  
    elif mode in ["live", "live_trading", "production"]:
        return LIVE_TRADING_RISK_PARAMS
    else:
        # Défaut = paper trading
        logger.warning("Mode inconnu '{mode}', utilisation PAPER_TRADING")
        return PAPER_TRADING_RISK_PARAMS

# === COMPARAISON MODES ===

def compare_risk_modes():
    """Compare les différents modes de risque"""
    
    modes = {
        "DATA_COLLECTION": DATA_COLLECTION_RISK_PARAMS,
        "PAPER_TRADING": PAPER_TRADING_RISK_PARAMS,
        "LIVE_TRADING": LIVE_TRADING_RISK_PARAMS
    }
    
    logger.info("📊 COMPARAISON MODES DE RISQUE")
    print("=" * 80)
    
    # Headers
    logger.info("{'PARAMÈTRE':<30} {'DATA_COLLECT':<15} {'PAPER':<15} {'LIVE':<15}")
    print("-" * 80)
    
    # Comparaisons clés
    comparisons = [
        ("Min Signal Probability", "min_signal_probability"),
        ("Min Base Quality", "min_base_quality_for_trade"),
        ("Min Confluence", "min_confluence_score"),
        ("Daily Loss Limit", "daily_loss_limit"),
        ("Max Daily Trades", "max_daily_trades"),
        ("Max Position Size", "max_position_size"),
        ("Max Concurrent Pos", "max_positions_concurrent"),
        ("Golden Rule Strict", "golden_rule_strict"),
        ("Data Collection Mode", "data_collection_mode")
    ]
    
    for label, attr in comparisons:
        values = []
        for mode_name, params in modes.items():
            val = getattr(params, attr)
            if isinstance(val, float):
                val_str = f"{val:.2f}"
            elif isinstance(val, bool):
                val_str = "✅" if val else "❌"
            else:
                val_str = str(val)
            values.append(val_str)
        
        logger.info("{label:<30} {values[0]:<15} {values[1]:<15} {values[2]:<15}")
    
    print("=" * 80)
    
    # Analyse des différences
    logger.info("\n🎯 ANALYSE MODES:")
    logger.info("DATA_COLLECTION:")
    logger.info("  ✅ Seuils réduits pour maximum de trades")
    logger.info("  ✅ Limites étendues (sauf daily loss)")
    logger.info("  ✅ Golden rule désactivée")
    logger.info("  ✅ Objectif: 500-1000 trades/jour")
    
    logger.info("\nPAPER_TRADING:")
    logger.info("  ⚖️ Paramètres équilibrés")
    logger.info("  ⚖️ Validation système et stratégies")
    logger.info("  ⚖️ Proche conditions réelles")
    
    logger.info("\nLIVE_TRADING:")
    logger.info("  🛡️ Maximum de sécurité")
    logger.info("  🛡️ Seuils très élevés")
    logger.info("  🛡️ Une seule position à la fois")
    logger.info("  🛡️ Optimisé prop firm")

# === VALIDATION ===

def validate_all_configs():
    """Valide toutes les configurations"""
    
    configs = {
        "DATA_COLLECTION": DATA_COLLECTION_RISK_PARAMS,
        "PAPER": PAPER_TRADING_RISK_PARAMS,
        "LIVE": LIVE_TRADING_RISK_PARAMS
    }
    
    logger.debug("VALIDATION CONFIGURATIONS...")
    
    all_valid = True
    for name, config in configs.items():
        # Vérifications de base
        valid = True
        errors = []
        
        # Daily loss doit être positif
        if config.daily_loss_limit <= 0:
            errors.append("Daily loss limit <= 0")
            valid = False
        
        # Risk per trade < daily loss
        if config.max_risk_per_trade_dollars > config.daily_loss_limit:
            errors.append("Risk per trade > daily loss")
            valid = False
        
        # Seuils probabilité valides
        if not (0 <= config.min_signal_probability <= 1):
            errors.append("Signal probability hors range [0,1]")
            valid = False
        
        # Position size cohérente
        if config.max_position_size < config.base_position_size:
            errors.append("Max position < base position")
            valid = False
        
        # Résultat
        status = "✅ VALIDE" if valid else "❌ ERREURS"
        logger.info("{name:<20} {status}")
        
        if errors:
            for error in errors:
                logger.info("  - {error}")
            all_valid = False
    
    logger.info("\n🎯 RÉSULTAT GLOBAL: {'✅ TOUTES VALIDES' if all_valid else '❌ ERREURS DÉTECTÉES'}")
    return all_valid

# === TESTING ===

def test_risk_config():
    """Test complet du système de configuration"""
    logger.info("🧪 TEST CONFIGURATION RISQUE...")
    
    # Test factory function
    logger.info("\n1. Test factory function:")
    for mode in ["data_collection", "paper", "live", "unknown"]:
        params = get_risk_params_for_mode(mode)
        logger.info("  {mode}: {params.data_collection_mode}")
    
    # Test validation
    logger.info("\n2. Test validation:")
    validate_all_configs()
    
    # Test comparaison
    logger.info("\n3. Comparaison modes:")
    compare_risk_modes()
    
    logger.info("\n✅ Test configuration terminé!")
    return True

if __name__ == "__main__":
    test_risk_config()