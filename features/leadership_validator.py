#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Leadership Validator – version patchée
- Gestion NaN → 0.0
- Corrélation ES/NQ NaN‑safe + synchro stricte
- Mode calibration: seuils adoucis + SOFT_DOWNGRADE
- Multiplicateur de risque continu (borné)
- Logging aligné sur tes traces
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Dict, Any, Tuple
import numpy as np
import pandas as pd
import math

try:
    from core.logger import get_logger
    logger = get_logger(__name__)
except Exception:
    import logging
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    logger = logging.getLogger("features.leadership_validator")

@dataclass
class ValidationResult:
    is_valid: bool
    risk_multiplier: float
    reason: str
    decision_code: str  # "PASS", "HARD_REJECT", "SOFT_DOWNGRADE"
    leader: Optional[str]
    leader_strength: float
    persisted: bool
    corr_es_nq: float

def _nan_to_num(x: float) -> float:
    if x is None:
        return 0.0
    if isinstance(x, (float, int)):
        try:
            if math.isnan(float(x)) or math.isinf(float(x)):
                return 0.0
            return float(x)
        except Exception:
            return 0.0
    try:
        xf = float(x)
        return 0.0 if (math.isnan(xf) or math.isinf(xf)) else xf
    except Exception:
        return 0.0

def _sync_prices(es: pd.DataFrame, nq: pd.DataFrame) -> Tuple[pd.Series, pd.Series]:
    if es is None or nq is None or not len(es) or not len(nq):
        return pd.Series(dtype=float), pd.Series(dtype=float)
    es = es.copy()
    nq = nq.copy()
    for df in (es, nq):
        if not isinstance(df.index, pd.DatetimeIndex):
            df.index = pd.to_datetime(df.index, errors="coerce")

    # colonne de close
    col = None
    for candidate in ("close", "Close", "last", "price"):
        if candidate in es.columns and candidate in nq.columns:
            col = candidate
            break
    if col is None:
        def first_num(cdf):
            for c in cdf.columns:
                if pd.api.types.is_numeric_dtype(cdf[c]):
                    return c
            return None
        c_es = first_num(es)
        c_nq = first_num(nq)
        if c_es is None or c_nq is None:
            return pd.Series(dtype=float), pd.Series(dtype=float)
        es_col, nq_col = c_es, c_nq
    else:
        es_col = nq_col = col

    idx = es.index.intersection(nq.index)
    if len(idx) == 0:
        return pd.Series(dtype=float), pd.Series(dtype=float)

    es_c = es.loc[idx, es_col].astype(float)
    nq_c = nq.loc[idx, nq_col].astype(float)
    es_c = es_c.replace([np.inf, -np.inf], np.nan).dropna()
    nq_c = nq_c.replace([np.inf, -np.inf], np.nan).dropna()
    idx2 = es_c.index.intersection(nq_c.index)
    return es_c.loc[idx2], nq_c.loc[idx2]

def _corr_es_nq(es: pd.DataFrame, nq: pd.DataFrame, lookback: int = 20) -> float:
    es_c, nq_c = _sync_prices(es, nq)
    if len(es_c) < 2 or len(nq_c) < 2:
        return 0.0
    es_tail = es_c.tail(lookback)
    nq_tail = nq_c.tail(lookback)
    if len(es_tail) != len(nq_tail) or len(es_tail) < 2:
        return 0.0
    corr = float(np.corrcoef(es_tail.values, nq_tail.values)[0, 1])
    if math.isnan(corr) or math.isinf(corr):
        return 0.0
    return max(-1.0, min(1.0, corr))

class LeadershipValidator:
    """
    Valide un biais/instrument en s’appuyant sur ES/NQ et quelques règles.
    """
    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        cfg = config or {}
        # 🎯 Seuils resserrés pour validation plus stricte
        self.corr_min = float(cfg.get("corr_min", 0.15))  # 0.01 → 0.15 (15x plus strict)
        self.leader_strength_min = float(cfg.get("leader_strength_min", 0.25))  # 0.05 → 0.25 (5x plus strict)
        self.calibration_mode = bool(cfg.get("calibration_mode", False))
        
        # 🎯 Seuils additionnels pour validation renforcée
        self.min_correlation_quality = float(cfg.get("min_correlation_quality", 0.3))  # Qualité corrélation
        self.min_leadership_consistency = float(cfg.get("min_leadership_consistency", 0.4))  # Consistance leadership
        self.max_risk_threshold = float(cfg.get("max_risk_threshold", 0.8))  # Seuil risque max

    def validate(
        self,
        *,
        bias: str,
        instrument: str,
        es_df: Optional[pd.DataFrame],
        nq_df: Optional[pd.DataFrame],
        leader_hint: Optional[str] = None,
        lookback: int = 20,
    ) -> ValidationResult:
        bias = (bias or "").lower().strip()
        instrument = (instrument or "").upper().strip()

        # Corrélation NaN-safe
        corr = _corr_es_nq(es_df, nq_df, lookback=lookback)
        corr_intensity = abs(corr)

        # Détermination leader “naïve” (tu peux brancher ta logique réelle ici)
        leader = leader_hint
        if not leader:
            if instrument in ("ES", "MES"):
                leader = "ES"
            elif instrument in ("NQ", "MNQ"):
                leader = "NQ"
            else:
                leader = None

        # Force du leader (proxy simple sur corrélation)
        leader_strength = corr_intensity

        # Seuils (adoucis si calibration)
        corr_min = self.corr_min
        strength_min = self.leader_strength_min
        decision_code = "PASS"
        reason = ""

        if self.calibration_mode:
            corr_min = max(0.0, self.corr_min * 0.5)
            strength_min = max(0.0, self.leader_strength_min * 0.5)

        # 🎯 Validation renforcée avec seuils resserrés
        is_valid = True
        validation_issues = []
        
        # 1. Validation corrélation de base
        if corr_intensity < corr_min:
            is_valid = False
            validation_issues.append(f"Corrélation insuffisante ({corr_intensity:.3f} < {corr_min:.2f})")
        
        # 2. Validation force du leader
        if leader_strength < strength_min:
            is_valid = False
            validation_issues.append(f"Leader trop faible ({leader_strength:.3f} < {strength_min:.2f})")
        
        # 3. 🎯 Validation qualité corrélation (nouveau)
        if corr_intensity < self.min_correlation_quality:
            is_valid = False
            validation_issues.append(f"Qualité corrélation insuffisante ({corr_intensity:.3f} < {self.min_correlation_quality:.2f})")
        
        # 4. 🎯 Validation consistance leadership (nouveau)
        if leader_strength < self.min_leadership_consistency:
            is_valid = False
            validation_issues.append(f"Consistance leadership insuffisante ({leader_strength:.3f} < {self.min_leadership_consistency:.2f})")
        
        # 5. 🎯 Validation cohérence instrument/leader
        if instrument in ("ES", "MES") and leader == "NQ":
            is_valid = False
            validation_issues.append("Incohérence: trading ES mais leader=NQ")
        elif instrument in ("NQ", "MNQ") and leader == "ES":
            is_valid = False
            validation_issues.append("Incohérence: trading NQ mais leader=ES")
        
        # Compiler la raison
        reason = "; ".join(validation_issues) if validation_issues else "Validation OK"

        # Multiplicateur de risque continu
        # map |corr|∈[0,1] → risk∈[0.0,1.0] avec un “dead‑zone” doux sur corr_min
        if corr_intensity <= corr_min:
            risk = 0.0
        else:
            # démarre à 0.2 au seuil puis grimpe
            span = max(1e-6, 1.0 - corr_min)
            risk = 0.2 + 0.8 * ((corr_intensity - corr_min) / span)
        risk = max(0.0, min(1.0, risk))

        # 🎯 Validation seuil de risque maximum
        if risk > self.max_risk_threshold:
            is_valid = False
            validation_issues.append(f"Risque trop élevé ({risk:.3f} > {self.max_risk_threshold:.2f})")
            reason = "; ".join(validation_issues) if validation_issues else "Validation OK"
        
        # Décision finale
        if not is_valid:
            if self.calibration_mode:
                # On évite de bloquer dur pendant la calibration
                decision_code = "SOFT_DOWNGRADE"
                # on conserve un petit risque pour laisser passer la confluence si elle est forte
                risk = min(risk, 0.15)
            else:
                decision_code = "HARD_REJECT"
                risk = 0.0

        # Log formaté comme tes traces
        logger.info(
            "❌ REJECT | Bias=%s | Instrument=%s | Leader=%s | Reason: %s"
            if decision_code != "PASS" else
            "✅ PASS | Bias=%s | Instrument=%s | Leader=%s | Risk=%.3f",
            bias, instrument, leader, reason if decision_code != "PASS" else risk
        )

        return ValidationResult(
            is_valid=is_valid and decision_code == "PASS",
            risk_multiplier=float(risk),
            reason=reason,
            decision_code=decision_code,
            leader=leader,
            leader_strength=float(leader_strength),
            persisted=False,
            corr_es_nq=float(corr),
        )
    
    def get_validation_thresholds(self) -> Dict[str, float]:
        """🎯 Retourne les seuils de validation actuels"""
        return {
            'corr_min': self.corr_min,
            'leader_strength_min': self.leader_strength_min,
            'min_correlation_quality': self.min_correlation_quality,
            'min_leadership_consistency': self.min_leadership_consistency,
            'max_risk_threshold': self.max_risk_threshold,
            'calibration_mode': self.calibration_mode
        }
    
    def update_thresholds(self, new_thresholds: Dict[str, float]) -> None:
        """🎯 Met à jour les seuils de validation"""
        for key, value in new_thresholds.items():
            if hasattr(self, key) and isinstance(value, (int, float)):
                setattr(self, key, float(value))
                logger.info(f"🎯 Seuil {key} mis à jour: {value}")
    
    def reset_to_defaults(self) -> None:
        """🎯 Remet les seuils par défaut"""
        self.corr_min = 0.15
        self.leader_strength_min = 0.25
        self.min_correlation_quality = 0.3
        self.min_leadership_consistency = 0.4
        self.max_risk_threshold = 0.8
        logger.info("🎯 Seuils remis par défaut")
