# 🛡️ VALIDATEUR DE SIGNAUX ULTRA-STRICT
# Date: 2025-08-11 - Qualité > Quantité

import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

@dataclass
class SignalQuality:
    """📊 Qualité d'un signal"""
    overall_score: float
    confidence_score: float
    confluence_score: float
    volume_score: float
    delta_score: float
    vwap_score: float
    imbalance_score: float
    is_valid: bool
    rejection_reasons: List[str]
    quality_level: str  # 'PREMIUM', 'STRONG', 'GOOD', 'WEAK', 'REJECTED'

class UltraStrictSignalValidator:
    """🛡️ Validateur de signaux ultra-strict"""
    
    def __init__(self):
        # 🎯 SEUILS ULTRA-STRICTS
        self.MIN_CONFIDENCE = 0.400        # 40% minimum
        self.MIN_CONFLUENCE = 0.350        # 35% minimum
        self.MIN_VOLUME = 100              # 100 contrats minimum
        self.MIN_DELTA = 0.150             # 15% minimum
        self.MIN_VWAP_SIGNAL = 0.200       # 20% minimum VWAP
        self.MIN_IMBALANCE = 0.500         # 50% minimum imbalance
        
        # 📊 SEUILS DE QUALITÉ
        self.PREMIUM_THRESHOLD = 0.450     # 45% pour PREMIUM
        self.STRONG_THRESHOLD = 0.400      # 40% pour STRONG
        self.GOOD_THRESHOLD = 0.350        # 35% pour GOOD
        
        # 🔍 VALIDATION MULTIPLE
        self.require_multiple_confirmations = True
        self.min_confirmations = 3         # 3 confirmations minimum
        
        logger.info("🛡️ Signal Validator ultra-strict initialisé")
        logger.info(f"   🎯 Seuils: {self.MIN_CONFIDENCE*100}% confiance, {self.MIN_CONFLUENCE*100}% confluence")
        logger.info(f"   📊 Volume: {self.MIN_VOLUME} contrats, Delta: {self.MIN_DELTA*100}%")
    
    def validate_signal(self, signal_data: Dict) -> SignalQuality:
        """🎯 Valider un signal avec critères ultra-stricts"""
        
        rejection_reasons = []
        
        # 1. Vérifier données de base
        if not self._validate_basic_data(signal_data):
            return SignalQuality(
                overall_score=0.0,
                confidence_score=0.0,
                confluence_score=0.0,
                volume_score=0.0,
                delta_score=0.0,
                vwap_score=0.0,
                imbalance_score=0.0,
                is_valid=False,
                rejection_reasons=["Données de base invalides"],
                quality_level="REJECTED"
            )
        
        # 2. Calculer scores individuels
        confidence_score = self._calculate_confidence_score(signal_data)
        confluence_score = self._calculate_confluence_score(signal_data)
        volume_score = self._calculate_volume_score(signal_data)
        delta_score = self._calculate_delta_score(signal_data)
        vwap_score = self._calculate_vwap_score(signal_data)
        imbalance_score = self._calculate_imbalance_score(signal_data)
        
        # 3. Vérifier seuils critiques
        if confidence_score < self.MIN_CONFIDENCE:
            rejection_reasons.append(f"Confiance insuffisante: {confidence_score*100:.1f}% < {self.MIN_CONFIDENCE*100}%")
        
        if confluence_score < self.MIN_CONFLUENCE:
            rejection_reasons.append(f"Confluence insuffisante: {confluence_score*100:.1f}% < {self.MIN_CONFLUENCE*100}%")
        
        if volume_score < 0.5:  # Volume trop faible
            rejection_reasons.append(f"Volume insuffisant: {signal_data.get('volume', 0)} < {self.MIN_VOLUME}")
        
        if delta_score < self.MIN_DELTA:
            rejection_reasons.append(f"Delta insuffisant: {delta_score*100:.1f}% < {self.MIN_DELTA*100}%")
        
        # 4. Calculer score global
        overall_score = self._calculate_overall_score(
            confidence_score, confluence_score, volume_score, 
            delta_score, vwap_score, imbalance_score
        )
        
        # 5. Déterminer niveau de qualité
        quality_level = self._determine_quality_level(overall_score)
        
        # 6. Validation finale
        is_valid = len(rejection_reasons) == 0 and overall_score >= self.GOOD_THRESHOLD
        
        # 7. Log détaillé
        self._log_validation_details(
            signal_data, overall_score, confidence_score, confluence_score,
            volume_score, delta_score, vwap_score, imbalance_score,
            quality_level, is_valid, rejection_reasons
        )
        
        return SignalQuality(
            overall_score=overall_score,
            confidence_score=confidence_score,
            confluence_score=confluence_score,
            volume_score=volume_score,
            delta_score=delta_score,
            vwap_score=vwap_score,
            imbalance_score=imbalance_score,
            is_valid=is_valid,
            rejection_reasons=rejection_reasons,
            quality_level=quality_level
        )
    
    def _validate_basic_data(self, signal_data: Dict) -> bool:
        """🔍 Valider données de base"""
        required_fields = ['volume', 'delta', 'confidence', 'confluence_score']
        
        for field in required_fields:
            if field not in signal_data or signal_data[field] is None:
                logger.warning(f"❌ Champ manquant: {field}")
                return False
        
        return True
    
    def _calculate_confidence_score(self, signal_data: Dict) -> float:
        """📊 Calculer score de confiance"""
        confidence = signal_data.get('confidence', 0.0)
        
        # Normaliser entre 0 et 1
        if confidence > 1.0:
            confidence = confidence / 100.0
        
        return min(1.0, max(0.0, confidence))
    
    def _calculate_confluence_score(self, signal_data: Dict) -> float:
        """📈 Calculer score de confluence"""
        confluence = signal_data.get('confluence_score', 0.0)
        
        # Normaliser entre 0 et 1
        if confluence > 1.0:
            confluence = confluence / 100.0
        
        return min(1.0, max(0.0, confluence))
    
    def _calculate_volume_score(self, signal_data: Dict) -> float:
        """📊 Calculer score de volume"""
        volume = signal_data.get('volume', 0)
        
        if volume >= 1000:
            return 1.0
        elif volume >= 500:
            return 0.8
        elif volume >= 200:
            return 0.6
        elif volume >= 100:
            return 0.4
        else:
            return 0.1
    
    def _calculate_delta_score(self, signal_data: Dict) -> float:
        """📈 Calculer score de delta"""
        delta = abs(signal_data.get('delta', 0))
        volume = signal_data.get('volume', 1)
        
        if volume == 0:
            return 0.0
        
        delta_ratio = delta / volume
        
        if delta_ratio >= 0.5:
            return 1.0
        elif delta_ratio >= 0.3:
            return 0.8
        elif delta_ratio >= 0.2:
            return 0.6
        elif delta_ratio >= 0.15:
            return 0.4
        else:
            return 0.1
    
    def _calculate_vwap_score(self, signal_data: Dict) -> float:
        """📊 Calculer score VWAP"""
        vwap_signal = signal_data.get('vwap_bands_signal', 0.0)
        
        # Normaliser entre 0 et 1
        if vwap_signal > 1.0:
            vwap_signal = vwap_signal / 100.0
        
        return min(1.0, max(0.0, vwap_signal))
    
    def _calculate_imbalance_score(self, signal_data: Dict) -> float:
        """⚖️ Calculer score d'imbalance"""
        imbalance = signal_data.get('volume_imbalance_signal', 0.0)
        
        # Normaliser entre 0 et 1
        if imbalance > 1.0:
            imbalance = imbalance / 100.0
        
        return min(1.0, max(0.0, imbalance))
    
    def _calculate_overall_score(self, confidence: float, confluence: float,
                                volume: float, delta: float, vwap: float, 
                                imbalance: float) -> float:
        """🎯 Calculer score global pondéré"""
        
        # Pondération ultra-conservatrice
        weights = {
            'confidence': 0.30,    # 30% - Confiance primordiale
            'confluence': 0.25,    # 25% - Confluence importante
            'volume': 0.20,        # 20% - Volume significatif
            'delta': 0.15,         # 15% - Delta modéré
            'vwap': 0.05,          # 5% - VWAP faible
            'imbalance': 0.05      # 5% - Imbalance faible
        }
        
        overall_score = (
            confidence * weights['confidence'] +
            confluence * weights['confluence'] +
            volume * weights['volume'] +
            delta * weights['delta'] +
            vwap * weights['vwap'] +
            imbalance * weights['imbalance']
        )
        
        return min(1.0, max(0.0, overall_score))
    
    def _determine_quality_level(self, overall_score: float) -> str:
        """🏆 Déterminer niveau de qualité"""
        if overall_score >= self.PREMIUM_THRESHOLD:
            return "PREMIUM"
        elif overall_score >= self.STRONG_THRESHOLD:
            return "STRONG"
        elif overall_score >= self.GOOD_THRESHOLD:
            return "GOOD"
        elif overall_score >= 0.25:
            return "WEAK"
        else:
            return "REJECTED"
    
    def _log_validation_details(self, signal_data: Dict, overall_score: float,
                               confidence: float, confluence: float, volume: float,
                               delta: float, vwap: float, imbalance: float,
                               quality_level: str, is_valid: bool, 
                               rejection_reasons: List[str]):
        """📝 Logger détails de validation"""
        
        logger.info("🛡️ === VALIDATION SIGNAL ULTRA-STRICTE ===")
        logger.info(f"   📊 Score Global: {overall_score*100:.1f}%")
        logger.info(f"   🎯 Niveau: {quality_level}")
        logger.info(f"   ✅ Valide: {is_valid}")
        
        logger.info("   📈 Scores Détail:")
        logger.info(f"      - Confiance: {confidence*100:.1f}%")
        logger.info(f"      - Confluence: {confluence*100:.1f}%")
        logger.info(f"      - Volume: {volume*100:.1f}%")
        logger.info(f"      - Delta: {delta*100:.1f}%")
        logger.info(f"      - VWAP: {vwap*100:.1f}%")
        logger.info(f"      - Imbalance: {imbalance*100:.1f}%")
        
        if rejection_reasons:
            logger.warning("   ❌ Raisons de rejet:")
            for reason in rejection_reasons:
                logger.warning(f"      - {reason}")
        else:
            logger.info("   ✅ Aucun rejet - Signal valide")
        
        logger.info("   📊 Données Signal:")
        logger.info(f"      - Volume: {signal_data.get('volume', 0)}")
        logger.info(f"      - Delta: {signal_data.get('delta', 0)}")
        logger.info(f"      - Prix: {signal_data.get('price', 0)}")
        logger.info("   ======================================")

# Instance globale
SIGNAL_VALIDATOR = UltraStrictSignalValidator()

# Alias attendu par les tests historiques
class SignalValidator(UltraStrictSignalValidator):
    pass

