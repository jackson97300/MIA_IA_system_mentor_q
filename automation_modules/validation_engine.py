#!/usr/bin/env python3
"""
🔧 VALIDATION ENGINE - MIA_IA_SYSTEM
====================================

Module de validation et filtres extrait du fichier monstre
- Validation des signaux avec filtres adaptatifs
- Tracking des métriques de validation
- Seuils adaptatifs basés sur confluence
- Logging de télémetrie
"""

import sys
import random
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from collections import defaultdict
import time # Added for cooldown

# Ajouter le chemin du projet
sys.path.append(str(Path(__file__).parent.parent))

from core.logger import get_logger
from core.market_snapshot import MarketSnapshot

logger = get_logger(__name__)

class ValidationEngine:
    """Moteur de validation avec filtres adaptatifs"""
    
    def __init__(self, config=None):
        self.config = config or {}
        self._validation_stats = {
            'signals_detected': 0,
            'signals_validated': 0,
            'signals_rejected': 0,
            'rejection_reasons': {
                'volume_imbalance_low': 0,
                'confluence_score_low': 0,
                'vwap_signal_low': 0,
                'divergence_high': 0,
                'composite_score_low': 0,
                'coherence_low': 0,
                'orderflow_low': 0,
                'confidence_low': 0,
                'risk_state': 0,
                'data_source': 0,
                'leadership_misaligned': 0,
                'correlation_low': 0,
                'volatility_high': 0
            }
        }
        self._current_data_source = 'saved_data'
        self._current_leadership_alignment = 'NEUTRAL'
        self._current_es_nq_corr = 0.0
        
        logger.info("🔧 Validation Engine initialisé")
    
    def _check_volatility_guard(self, market_snapshot: MarketSnapshot, config: Dict[str, Any]) -> tuple[bool, str, str]:
        """
        Vérifie les conditions de volatilité et spread
        
        Returns:
            (is_valid, reason, detail)
        """
        try:
            if not config.get('vol_guard_enabled', True):
                return True, "vol_guard_disabled", "Volatility guard désactivé"
            
            # 1) Spread guard
            max_spread = config.get('max_spread', 1.0)
            if market_snapshot.spread_ticks > max_spread:
                return False, "spread", f"{market_snapshot.spread_ticks:.1f}t > {max_spread}t"
            
            # 2) Volatility guard (soft)
            vol_guard_1m = config.get('vol_guard_1m', 0.30)
            vol_guard_5s = config.get('vol_guard_5s', 0.12)
            
            if market_snapshot.ret_1m_sigma > vol_guard_1m:
                return False, "volatility_1m", f"σ1m={market_snapshot.ret_1m_sigma:.3f} > {vol_guard_1m}"
            
            if market_snapshot.ret_5s_sigma > vol_guard_5s:
                return False, "volatility_5s", f"σ5s={market_snapshot.ret_5s_sigma:.3f} > {vol_guard_5s}"
            
            # 3) Flash-move guard
            max_move_ticks = config.get('max_move_ticks_3s', 8)
            if abs(market_snapshot.move_ticks_3s) >= max_move_ticks:
                return False, "flash_move", f"Δ3s={market_snapshot.move_ticks_3s}t >= {max_move_ticks}t"
            
            return True, "volatility_ok", "Toutes les conditions volatilité OK"
            
        except Exception as e:
            logger.error(f"❌ Erreur vérification volatilité: {e}")
            return False, "volatility_error", f"Erreur: {e}"
    
    def validate_signal_with_enhanced_filters(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """🔧 CORRECTIFS APPLIQUÉS: Validation renforcée avec filtres adaptatifs"""
        try:
            # 🆕 AJOUT: Vérification Volatility Guard
            if 'market_snapshot' in market_data:
                vol_valid, vol_reason, vol_detail = self._check_volatility_guard(
                    market_data['market_snapshot'], 
                    self.config
                )
                
                if not vol_valid:
                    # Micro-cooldown après rejet volatilité
                    cooldown_sec = self.config.get('cooldown_after_reject_sec', 5)
                    if cooldown_sec > 0:
                        time.sleep(cooldown_sec)
                    
                    logger.warning(f"⚠️ Signal filtré | reason={vol_reason} | {vol_detail}")
                    
                    return {
                        'valid': False,
                        'reason': vol_reason,
                        'detail': vol_detail,
                        'volatility_guard': True
                    }
            
            # Validation normale (code existant)
            orderflow_data = market_data.get('orderflow', {})
            confluence_data = market_data.get('confluence', {})
            
            # Extraire les scores
            orderflow_score = orderflow_data.get('score', 0.0)
            confluence_score = confluence_data.get('score', 0.0)
            signal_confidence = market_data.get('confidence', 0.0)
            
            # Seuils adaptatifs
            min_orderflow = self.get_adaptive_threshold(0.1, confluence_score)
            min_confluence = self.get_adaptive_threshold(0.15, orderflow_score)
            min_confidence = self.get_adaptive_threshold(0.05, confluence_score)
            
            # Validation multi-critères
            validation_passed = True
            rejection_reason = "unknown"
            
            # 1. OrderFlow validation
            if orderflow_score < min_orderflow:
                validation_passed = False
                rejection_reason = 'orderflow_low'
                self._validation_stats['rejection_reasons']['orderflow_low'] += 1
            
            # 2. Confluence validation
            elif confluence_score < min_confluence:
                validation_passed = False
                rejection_reason = 'confluence_low'
                self._validation_stats['rejection_reasons']['confluence_low'] += 1
            
            # 3. Signal confidence validation
            elif signal_confidence < min_confidence:
                validation_passed = False
                rejection_reason = 'confidence_low'
                self._validation_stats['rejection_reasons']['confidence_low'] += 1
            
            # 4. Risk state validation
            elif not self.is_risk_state_ok():
                validation_passed = False
                rejection_reason = 'risk_state'
                self._validation_stats['rejection_reasons']['risk_state'] += 1
            
            # 5. Data source validation
            elif not self._validate_data_source(market_data):
                validation_passed = False
                rejection_reason = 'data_source'
                self._validation_stats['rejection_reasons']['data_source'] += 1
            
            # 6. Leadership alignment validation
            elif not self._validate_leadership_alignment(market_data):
                validation_passed = False
                rejection_reason = 'leadership_misaligned'
                self._validation_stats['rejection_reasons']['leadership_misaligned'] += 1
            
            # 7. ES/NQ correlation validation
            elif not self._validate_es_nq_correlation(market_data):
                validation_passed = False
                rejection_reason = 'correlation_low'
                self._validation_stats['rejection_reasons']['correlation_low'] += 1
            
            # Mise à jour stats
            if validation_passed:
                self._validation_stats['signals_accepted'] += 1
                self._log_validation_telemetry(market_data, "ACCEPTED")
            else:
                self._validation_stats['signals_rejected'] += 1
                self._log_validation_telemetry(market_data, f"REJECTED: {rejection_reason}")
            
            return {
                'valid': validation_passed,
                'reason': rejection_reason if not validation_passed else 'accepted',
                'orderflow_score': orderflow_score,
                'confluence_score': confluence_score,
                'signal_confidence': signal_confidence,
                'volatility_guard': False  # Pas de rejet volatilité
            }
            
        except Exception as e:
            logger.error(f"❌ Erreur validation signaux: {e}")
            return {
                'valid': False,
                'reason': 'validation_error',
                'detail': str(e),
                'volatility_guard': False
            }
    
    def track_validation_metrics(self, signal_data: Dict, validation_result: bool) -> None:
        """Track les métriques de validation"""
        try:
            # Mise à jour des métriques en temps réel
            if validation_result:
                self._validation_stats['signals_validated'] += 1
            else:
                self._validation_stats['signals_rejected'] += 1
            
            # Calcul du taux de validation
            total_signals = self._validation_stats['signals_detected']
            validated_signals = self._validation_stats['signals_validated']
            
            if total_signals > 0:
                validation_rate = (validated_signals / total_signals) * 100
                logger.debug(f"📊 Taux de validation: {validation_rate:.1f}% ({validated_signals}/{total_signals})")
            
        except Exception as e:
            logger.error(f"❌ Erreur tracking métriques: {e}")
    
    def log_validation_telemetry(self) -> None:
        """Log la télémetrie de validation"""
        try:
            total_signals = self._validation_stats['signals_detected']
            validated_signals = self._validation_stats['signals_validated']
            rejected_signals = self._validation_stats['signals_rejected']
            
            if total_signals > 0:
                validation_rate = (validated_signals / total_signals) * 100
                rejection_rate = (rejected_signals / total_signals) * 100
                
                logger.info("📊 TÉLÉMÉTRIE VALIDATION:")
                logger.info(f"  📈 Signaux détectés: {total_signals}")
                logger.info(f"  ✅ Signaux validés: {validated_signals} ({validation_rate:.1f}%)")
                logger.info(f"  ❌ Signaux rejetés: {rejected_signals} ({rejection_rate:.1f}%)")
                
                # Raisons de rejet
                logger.info("  🔍 Raisons de rejet:")
                for reason, count in self._validation_stats['rejection_reasons'].items():
                    if count > 0:
                        percentage = (count / total_signals) * 100
                        logger.info(f"    - {reason}: {count} ({percentage:.1f}%)")
            
        except Exception as e:
            logger.error(f"❌ Erreur log télémetrie: {e}")
    
    def _log_validation_telemetry(self, payload: dict, status: str = "") -> None:
        """Stub de télémétrie pour éviter l'erreur dans les tests."""
        try:
            logger.debug("📡 Telemetry (validation): %s - %s", payload, status)
        except Exception:
            pass
    
    def get_adaptive_threshold(self, base_threshold: float, confluence_score: float = 0.0) -> float:
        """Calcule un seuil adaptatif basé sur le score de confluence"""
        try:
            # Ajustement basé sur confluence
            confluence_factor = 1.0 + (confluence_score * 0.5)  # +50% max si confluence forte
            
            # Ajustement basé sur la source de données
            data_source_factor = 1.0
            if self._current_data_source in ("saved_data", "CACHED_STALE"):
                data_source_factor = 0.7  # Seuils plus permissifs pour données sauvegardées
            
            # Ajustement basé sur l'alignement leadership
            leadership_factor = 1.0
            if self._current_leadership_alignment == 'strong_leader':
                leadership_factor = 0.8  # Seuils plus permissifs pour leader fort
            elif self._current_leadership_alignment == 'weak_signal':
                leadership_factor = 1.2  # Seuils plus stricts pour signal faible
            
            # Calcul du seuil adaptatif
            adaptive_threshold = base_threshold * confluence_factor * data_source_factor * leadership_factor
            
            # Limites de sécurité
            adaptive_threshold = max(0.01, min(1.0, adaptive_threshold))
            
            logger.debug(f"🔧 Seuil adaptatif: {base_threshold:.3f} → {adaptive_threshold:.3f}")
            return adaptive_threshold
            
        except Exception as e:
            logger.error(f"❌ Erreur calcul seuil adaptatif: {e}")
            return base_threshold
    
    def is_risk_state_ok(self) -> bool:
        """Vérifie si l'état de risque est acceptable"""
        try:
            # Vérifications de base
            total_signals = self._validation_stats['signals_detected']
            rejected_signals = self._validation_stats['signals_rejected']
            
            if total_signals == 0:
                return True  # Pas de signaux = pas de risque
            
            # Taux de rejet élevé = risque
            rejection_rate = (rejected_signals / total_signals) * 100
            if rejection_rate > 90:  # Plus de 90% de rejets
                logger.warning(f"⚠️ Taux de rejet élevé: {rejection_rate:.1f}%")
                return False
            
            # Vérification des raisons de rejet
            for reason, count in self._validation_stats['rejection_reasons'].items():
                if count > 0:
                    reason_rate = (count / total_signals) * 100
                    if reason_rate > 50:  # Plus de 50% pour une raison
                        logger.warning(f"⚠️ Raison de rejet dominante: {reason} ({reason_rate:.1f}%)")
                        return False
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur vérification état risque: {e}")
            return True  # Par défaut, accepter
    
    def set_data_source(self, data_source: str) -> None:
        """Définit la source de données pour les seuils adaptatifs"""
        self._current_data_source = data_source
        logger.debug(f"📊 Data source défini: {data_source}")
    
    def set_leadership_alignment(self, alignment: str) -> None:
        """Définit l'alignement leadership pour les seuils adaptatifs"""
        self._current_leadership_alignment = alignment
        logger.debug(f"📊 Leadership alignment défini: {alignment}")
    
    def set_es_nq_correlation(self, correlation: float) -> None:
        """Définit la corrélation ES/NQ pour les seuils adaptatifs"""
        self._current_es_nq_corr = correlation
        logger.debug(f"📊 ES/NQ correlation définie: {correlation:.3f}")
    
    def get_validation_stats(self) -> Dict[str, Any]:
        """Retourne les statistiques de validation"""
        return self._validation_stats.copy()
    
    def reset_validation_stats(self) -> None:
        """Reset les statistiques de validation"""
        self._validation_stats = {
            'signals_detected': 0,
            'signals_validated': 0,
            'signals_rejected': 0,
            'rejection_reasons': {
                'volume_imbalance_low': 0,
                'confluence_score_low': 0,
                'vwap_signal_low': 0,
                'divergence_high': 0,
                'composite_score_low': 0,
                'coherence_low': 0,
                'orderflow_low': 0,
                'confidence_low': 0,
                'risk_state': 0,
                'data_source': 0,
                'leadership_misaligned': 0,
                'correlation_low': 0,
                'volatility_high': 0
            }
        }
        logger.info("🔄 Statistiques de validation resetées")

def create_validation_engine(config=None) -> ValidationEngine:
    """Factory pour créer un ValidationEngine"""
    return ValidationEngine(config)
