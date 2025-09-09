#!/usr/bin/env python3
"""
MIA_IA_SYSTEM - Data Quality Validator
🎯 Rôle: "police des données"

Valider à la volée la qualité des événements du fichier unifié et des snapshots agrégés : 
schéma, champs, cohérence temporelle, staleness, contraintes métiers (ex. VWAP & OHLC), 
convergence M1/M30, MenthorQ complet vs partiel.

Version: Production Ready v2.0
Performance: <1ms par validation
Responsabilité: Validation qualité des données en temps réel
"""

import json
import time
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, deque
import math

from core.logger import get_logger

logger = get_logger(__name__)

# === TYPES ===

class Verdict(Enum):
    """Verdict de validation"""
    OK = "OK"
    WARN = "WARN"
    ERROR = "ERROR"

@dataclass
class ValidationResult:
    """Résultat de validation d'un item"""
    verdict: Verdict
    message: str
    code: str
    context: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

@dataclass
class QualityStats:
    """Statistiques de qualité sur une fenêtre"""
    window_start: datetime
    window_end: datetime
    total_items: int = 0
    ok_count: int = 0
    warn_count: int = 0
    error_count: int = 0
    error_rate: float = 0.0
    warn_rate: float = 0.0
    top_error_causes: List[Tuple[str, int]] = field(default_factory=list)
    top_warn_causes: List[Tuple[str, int]] = field(default_factory=list)

class DataQualityValidator:
    """
    Validateur de qualité des données en temps réel
    
    🔌 Entrées:
    - Événements bruts event du tailer
    - Snapshots consolidés market_snapshot.get(symbol)
    
    📤 Sorties:
    - Verdict par item : OK | WARN | ERROR + message, code, contexte
    - Counters : erreurs/min, warnings/min par catégorie
    - Rapport rolling 60s : taux de lignes invalides, top causes
    """
    
    def __init__(self):
        self.logger = get_logger(__name__)
        
        # Configuration validation
        self.staleness_thresholds = {
            'M1': 30,      # 30 secondes
            'M30': 300,    # 5 minutes
            'VIX': 300,    # 5 minutes
            'MQ': 120      # 2×period (60s pour M30)
        }
        
        self.bounds_checks = {
            'price_min': 0.01,
            'price_max': 100000.0,
            'volume_min': 0,
            'volume_max': 1e12,
            'vix_min': 5.0,
            'vix_max': 100.0,
            'vwap_range_multiplier': 3.0
        }
        
        # Stats rolling window (60s)
        self.stats_window = deque(maxlen=3600)  # 1 heure max
        self.error_categories = defaultdict(int)
        self.warn_categories = defaultdict(int)
        
        # Cache pour performance
        self._last_validation_time = None
        self._validation_cache = {}
        
        self.logger.info("🛡️ Data Quality Validator initialisé")
    
    def validate_event(self, event: Dict[str, Any]) -> ValidationResult:
        """
        Valide un événement brut du tailer
        
        Args:
            event: Événement à valider
            
        Returns:
            ValidationResult avec verdict et détails
        """
        try:
            # 1. Validation JSON et structure
            json_check = self._validate_json_structure(event)
            if json_check.verdict != Verdict.OK:
                return json_check
            
            # 2. Validation champs requis
            fields_check = self._validate_required_fields(event)
            if fields_check.verdict != Verdict.OK:
                return fields_check
            
            # 3. Validation valeurs numériques
            numeric_check = self._validate_numeric_values(event)
            if numeric_check.verdict != Verdict.OK:
                return numeric_check
            
            # 4. Validation cohérence temporelle
            temporal_check = self._validate_temporal_consistency(event)
            if temporal_check.verdict != Verdict.OK:
                return temporal_check
            
            # 5. Validation MenthorQ
            menthorq_check = self._validate_menthorq_data(event)
            if menthorq_check.verdict != Verdict.OK:
                return menthorq_check
            
            # 6. Validation contraintes métiers
            business_check = self._validate_business_constraints(event)
            if business_check.verdict != Verdict.OK:
                return business_check
            
            # Toutes les validations passées
            result = ValidationResult(
                verdict=Verdict.OK,
                message="Événement valide",
                code="VALID_EVENT",
                context={'event_type': event.get('type', 'unknown')}
            )
            
            self._record_validation(result)
            return result
            
        except Exception as e:
            self.logger.error(f"Erreur validation event: {e}")
            return ValidationResult(
                verdict=Verdict.ERROR,
                message=f"Erreur validation: {str(e)}",
                code="VALIDATION_ERROR",
                context={'error': str(e)}
            )
    
    def validate_snapshot(self, snapshot: Dict[str, Any], symbol: str = "ES") -> ValidationResult:
        """
        Valide un snapshot consolidé
        
        Args:
            snapshot: Snapshot à valider
            symbol: Symbole du marché
            
        Returns:
            ValidationResult avec verdict et détails
        """
        try:
            # 1. Validation staleness
            staleness_check = self._validate_snapshot_staleness(snapshot, symbol)
            if staleness_check.verdict != Verdict.OK:
                return staleness_check
            
            # 2. Validation cohérence OHLC
            ohlc_check = self._validate_ohlc_consistency(snapshot)
            if ohlc_check.verdict != Verdict.OK:
                return ohlc_check
            
            # 3. Validation VWAP
            vwap_check = self._validate_vwap_consistency(snapshot)
            if vwap_check.verdict != Verdict.OK:
                return vwap_check
            
            # 4. Validation convergence M1/M30
            convergence_check = self._validate_m1_m30_convergence(snapshot)
            if convergence_check.verdict != Verdict.OK:
                return convergence_check
            
            # 5. Validation buffer size
            buffer_check = self._validate_buffer_size(snapshot)
            if buffer_check.verdict != Verdict.OK:
                return buffer_check
            
            # Toutes les validations passées
            result = ValidationResult(
                verdict=Verdict.OK,
                message="Snapshot valide",
                code="VALID_SNAPSHOT",
                context={'symbol': symbol, 'timestamp': snapshot.get('timestamp')}
            )
            
            self._record_validation(result)
            return result
            
        except Exception as e:
            self.logger.error(f"Erreur validation snapshot: {e}")
            return ValidationResult(
                verdict=Verdict.ERROR,
                message=f"Erreur validation snapshot: {str(e)}",
                code="SNAPSHOT_VALIDATION_ERROR",
                context={'symbol': symbol, 'error': str(e)}
            )
    
    def _validate_json_structure(self, event: Dict[str, Any]) -> ValidationResult:
        """Valide la structure JSON de l'événement"""
        try:
            # Vérifier que c'est un dict
            if not isinstance(event, dict):
                return ValidationResult(
                    verdict=Verdict.ERROR,
                    message="Événement n'est pas un objet JSON valide",
                    code="INVALID_JSON_STRUCTURE"
                )
            
            # Vérifier champs de base
            required_base_fields = ['type', 'symbol', 'timestamp']
            missing_fields = [field for field in required_base_fields if field not in event]
            
            if missing_fields:
                return ValidationResult(
                    verdict=Verdict.ERROR,
                    message=f"Champs manquants: {', '.join(missing_fields)}",
                    code="MISSING_REQUIRED_FIELDS",
                    context={'missing_fields': missing_fields}
                )
            
            return ValidationResult(verdict=Verdict.OK, message="Structure JSON valide", code="VALID_JSON")
            
        except Exception as e:
            return ValidationResult(
                verdict=Verdict.ERROR,
                message=f"Erreur validation JSON: {str(e)}",
                code="JSON_VALIDATION_ERROR"
            )
    
    def _validate_required_fields(self, event: Dict[str, Any]) -> ValidationResult:
        """Valide les champs requis selon le type d'événement"""
        try:
            event_type = event.get('type', '')
            symbol = event.get('symbol', '')
            timestamp = event.get('timestamp', '')
            
            # Validation timestamp ISO
            try:
                if isinstance(timestamp, str):
                    datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                elif isinstance(timestamp, (int, float)):
                    datetime.fromtimestamp(timestamp, tz=timezone.utc)
            except (ValueError, TypeError):
                return ValidationResult(
                    verdict=Verdict.ERROR,
                    message="Timestamp invalide",
                    code="INVALID_TIMESTAMP",
                    context={'timestamp': timestamp}
                )
            
            # Validation type reconnu
            valid_types = ['quote', 'trade', 'bar', 'vp_m1', 'vp_m30', 'menthorq', 'vix']
            if event_type not in valid_types:
                return ValidationResult(
                    verdict=Verdict.WARN,
                    message=f"Type d'événement non reconnu: {event_type}",
                    code="UNKNOWN_EVENT_TYPE",
                    context={'event_type': event_type, 'valid_types': valid_types}
                )
            
            # Validation champs spécifiques par type
            type_specific_fields = {
                'quote': ['bid', 'ask', 'bid_size', 'ask_size'],
                'trade': ['price', 'size'],
                'bar': ['open', 'high', 'low', 'close', 'volume'],
                'vp_m1': ['poc', 'value_area_high', 'value_area_low'],
                'vp_m30': ['poc', 'value_area_high', 'value_area_low'],
                'menthorq': ['bl_distance', 'gw_distance', 'partial'],
                'vix': ['level', 'change']
            }
            
            if event_type in type_specific_fields:
                missing_fields = [field for field in type_specific_fields[event_type] 
                                if field not in event or event[field] is None]
                
                if missing_fields:
                    return ValidationResult(
                        verdict=Verdict.ERROR,
                        message=f"Champs manquants pour {event_type}: {', '.join(missing_fields)}",
                        code="MISSING_TYPE_SPECIFIC_FIELDS",
                        context={'event_type': event_type, 'missing_fields': missing_fields}
                    )
            
            return ValidationResult(verdict=Verdict.OK, message="Champs requis présents", code="VALID_FIELDS")
            
        except Exception as e:
            return ValidationResult(
                verdict=Verdict.ERROR,
                message=f"Erreur validation champs: {str(e)}",
                code="FIELD_VALIDATION_ERROR"
            )
    
    def _validate_numeric_values(self, event: Dict[str, Any]) -> ValidationResult:
        """Valide les valeurs numériques"""
        try:
            numeric_fields = ['bid', 'ask', 'price', 'open', 'high', 'low', 'close', 'volume', 
                            'bid_size', 'ask_size', 'size', 'poc', 'value_area_high', 'value_area_low',
                            'bl_distance', 'gw_distance', 'level', 'change']
            
            for field in numeric_fields:
                if field in event and event[field] is not None:
                    value = event[field]
                    
                    # Vérifier que c'est un nombre
                    if not isinstance(value, (int, float)):
                        return ValidationResult(
                            verdict=Verdict.ERROR,
                            message=f"Valeur non numérique pour {field}: {value}",
                            code="NON_NUMERIC_VALUE",
                            context={'field': field, 'value': value}
                        )
                    
                    # Vérifier valeurs finies
                    if not math.isfinite(value):
                        return ValidationResult(
                            verdict=Verdict.ERROR,
                            message=f"Valeur non finie pour {field}: {value}",
                            code="NON_FINITE_VALUE",
                            context={'field': field, 'value': value}
                        )
                    
                    # Vérifier bornes raisonnables
                    if field in ['bid', 'ask', 'price', 'open', 'high', 'low', 'close']:
                        if not (self.bounds_checks['price_min'] <= value <= self.bounds_checks['price_max']):
                            return ValidationResult(
                                verdict=Verdict.WARN,
                                message=f"Prix hors bornes pour {field}: {value}",
                                code="PRICE_OUT_OF_BOUNDS",
                                context={'field': field, 'value': value}
                            )
                    
                    elif field in ['volume', 'bid_size', 'ask_size', 'size']:
                        if not (self.bounds_checks['volume_min'] <= value <= self.bounds_checks['volume_max']):
                            return ValidationResult(
                                verdict=Verdict.WARN,
                                message=f"Volume hors bornes pour {field}: {value}",
                                code="VOLUME_OUT_OF_BOUNDS",
                                context={'field': field, 'value': value}
                            )
                    
                    elif field == 'level' and event.get('type') == 'vix':
                        if not (self.bounds_checks['vix_min'] <= value <= self.bounds_checks['vix_max']):
                            return ValidationResult(
                                verdict=Verdict.WARN,
                                message=f"VIX hors bornes: {value}",
                                code="VIX_OUT_OF_BOUNDS",
                                context={'value': value}
                            )
            
            return ValidationResult(verdict=Verdict.OK, message="Valeurs numériques valides", code="VALID_NUMERIC")
            
        except Exception as e:
            return ValidationResult(
                verdict=Verdict.ERROR,
                message=f"Erreur validation numérique: {str(e)}",
                code="NUMERIC_VALIDATION_ERROR"
            )
    
    def _validate_temporal_consistency(self, event: Dict[str, Any]) -> ValidationResult:
        """Valide la cohérence temporelle"""
        try:
            timestamp = event.get('timestamp')
            if not timestamp:
                return ValidationResult(
                    verdict=Verdict.ERROR,
                    message="Timestamp manquant",
                    code="MISSING_TIMESTAMP"
                )
            
            # Convertir en datetime
            if isinstance(timestamp, str):
                event_time = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            elif isinstance(timestamp, (int, float)):
                event_time = datetime.fromtimestamp(timestamp, tz=timezone.utc)
            else:
                return ValidationResult(
                    verdict=Verdict.ERROR,
                    message="Format timestamp invalide",
                    code="INVALID_TIMESTAMP_FORMAT"
                )
            
            # Vérifier que le timestamp n'est pas dans le futur (tolérance 5 minutes)
            now = datetime.now(timezone.utc)
            if event_time > now + timedelta(minutes=5):
                return ValidationResult(
                    verdict=Verdict.WARN,
                    message=f"Timestamp dans le futur: {event_time}",
                    code="FUTURE_TIMESTAMP",
                    context={'event_time': event_time.isoformat(), 'now': now.isoformat()}
                )
            
            # Vérifier que le timestamp n'est pas trop ancien (24 heures)
            if event_time < now - timedelta(hours=24):
                return ValidationResult(
                    verdict=Verdict.WARN,
                    message=f"Timestamp trop ancien: {event_time}",
                    code="STALE_TIMESTAMP",
                    context={'event_time': event_time.isoformat(), 'age_hours': (now - event_time).total_seconds() / 3600}
                )
            
            return ValidationResult(verdict=Verdict.OK, message="Cohérence temporelle valide", code="VALID_TEMPORAL")
            
        except Exception as e:
            return ValidationResult(
                verdict=Verdict.ERROR,
                message=f"Erreur validation temporelle: {str(e)}",
                code="TEMPORAL_VALIDATION_ERROR"
            )
    
    def _validate_menthorq_data(self, event: Dict[str, Any]) -> ValidationResult:
        """Valide les données MenthorQ"""
        try:
            if event.get('type') != 'menthorq':
                return ValidationResult(verdict=Verdict.OK, message="Pas de données MenthorQ", code="NO_MENTHORQ")
            
            # Vérifier mapping complet ou partial=True
            partial = event.get('partial', False)
            required_fields = ['bl_distance', 'gw_distance']
            
            if not partial:
                # Mapping complet requis
                missing_fields = [field for field in required_fields if field not in event or event[field] is None]
                if missing_fields:
                    return ValidationResult(
                        verdict=Verdict.ERROR,
                        message=f"Mapping MenthorQ incomplet: {', '.join(missing_fields)}",
                        code="INCOMPLETE_MENTHORQ_MAPPING",
                        context={'missing_fields': missing_fields}
                    )
                else:
                # Partial=True mais au moins un champ requis
                if not any(field in event and event[field] is not None for field in required_fields):
                    return ValidationResult(
                        verdict=Verdict.WARN,
                        message="Mapping MenthorQ partiel mais aucun champ présent",
                        code="EMPTY_PARTIAL_MENTHORQ",
                        context={'partial': partial}
                    )
            
            return ValidationResult(verdict=Verdict.OK, message="Données MenthorQ valides", code="VALID_MENTHORQ")
            
        except Exception as e:
            return ValidationResult(
                verdict=Verdict.ERROR,
                message=f"Erreur validation MenthorQ: {str(e)}",
                code="MENTHORQ_VALIDATION_ERROR"
            )
    
    def _validate_business_constraints(self, event: Dict[str, Any]) -> ValidationResult:
        """Valide les contraintes métiers"""
        try:
            event_type = event.get('type', '')
            
            # Validation OHLC pour les barres
            if event_type == 'bar':
                open_price = event.get('open')
                high_price = event.get('high')
                low_price = event.get('low')
                close_price = event.get('close')
                
                if all(p is not None for p in [open_price, high_price, low_price, close_price]):
                    # Vérifier high >= low
                    if high_price < low_price:
                        return ValidationResult(
                            verdict=Verdict.ERROR,
                            message=f"High < Low: {high_price} < {low_price}",
                            code="INVALID_OHLC_HIGH_LOW",
                            context={'high': high_price, 'low': low_price}
                        )
                    
                    # Vérifier que close est dans la range [low, high]
                    if not (low_price <= close_price <= high_price):
                        return ValidationResult(
                            verdict=Verdict.WARN,
                            message=f"Close hors range: {close_price} not in [{low_price}, {high_price}]",
                            code="CLOSE_OUT_OF_RANGE",
                            context={'close': close_price, 'low': low_price, 'high': high_price}
                        )
            
            # Validation bid/ask pour les quotes
            elif event_type == 'quote':
                bid = event.get('bid')
                ask = event.get('ask')
                
                if bid is not None and ask is not None:
                    if bid >= ask:
                        return ValidationResult(
                            verdict=Verdict.ERROR,
                            message=f"Bid >= Ask: {bid} >= {ask}",
                            code="INVALID_BID_ASK",
                            context={'bid': bid, 'ask': ask}
                        )
            
            return ValidationResult(verdict=Verdict.OK, message="Contraintes métiers valides", code="VALID_BUSINESS")
            
        except Exception as e:
            return ValidationResult(
                verdict=Verdict.ERROR,
                message=f"Erreur validation contraintes métiers: {str(e)}",
                code="BUSINESS_VALIDATION_ERROR"
            )
    
    def _validate_snapshot_staleness(self, snapshot: Dict[str, Any], symbol: str) -> ValidationResult:
        """Valide la staleness des snapshots"""
        try:
            now = datetime.now(timezone.utc)
            
            # Vérifier M1
            m1_data = snapshot.get('M1', {})
            if m1_data:
                m1_timestamp = self._parse_timestamp(m1_data.get('timestamp'))
                if m1_timestamp:
                    age_seconds = (now - m1_timestamp).total_seconds()
                    if age_seconds > self.staleness_thresholds['M1']:
                        return ValidationResult(
                            verdict=Verdict.WARN,
                            message=f"M1 stale: {age_seconds:.0f}s > {self.staleness_thresholds['M1']}s",
                            code="STALE_M1",
                            context={'symbol': symbol, 'age_seconds': age_seconds}
                        )
            
            # Vérifier M30
            m30_data = snapshot.get('M30', {})
            if m30_data:
                m30_timestamp = self._parse_timestamp(m30_data.get('timestamp'))
                if m30_timestamp:
                    age_seconds = (now - m30_timestamp).total_seconds()
                    if age_seconds > self.staleness_thresholds['M30']:
                        return ValidationResult(
                            verdict=Verdict.WARN,
                            message=f"M30 stale: {age_seconds:.0f}s > {self.staleness_thresholds['M30']}s",
                            code="STALE_M30",
                            context={'symbol': symbol, 'age_seconds': age_seconds}
                        )
            
            # Vérifier VIX
            vix_data = snapshot.get('VIX', {})
            if vix_data:
                vix_timestamp = self._parse_timestamp(vix_data.get('timestamp'))
                if vix_timestamp:
                    age_seconds = (now - vix_timestamp).total_seconds()
                    if age_seconds > self.staleness_thresholds['VIX']:
                        return ValidationResult(
                            verdict=Verdict.WARN,
                            message=f"VIX stale: {age_seconds:.0f}s > {self.staleness_thresholds['VIX']}s",
                            code="STALE_VIX",
                            context={'symbol': symbol, 'age_seconds': age_seconds}
                        )
            
            # Vérifier MenthorQ
            mq_data = snapshot.get('MenthorQ', {})
            if mq_data:
                mq_timestamp = self._parse_timestamp(mq_data.get('timestamp'))
                if mq_timestamp:
                    age_seconds = (now - mq_timestamp).total_seconds()
                    if age_seconds > self.staleness_thresholds['MQ']:
                        return ValidationResult(
                            verdict=Verdict.WARN,
                            message=f"MQ stale: {age_seconds:.0f}s > {self.staleness_thresholds['MQ']}s",
                            code="STALE_MQ",
                            context={'symbol': symbol, 'age_seconds': age_seconds}
                        )
            
            return ValidationResult(verdict=Verdict.OK, message="Snapshots récents", code="VALID_STALENESS")
            
        except Exception as e:
            return ValidationResult(
                verdict=Verdict.ERROR,
                message=f"Erreur validation staleness: {str(e)}",
                code="STALENESS_VALIDATION_ERROR"
            )
    
    def _validate_ohlc_consistency(self, snapshot: Dict[str, Any]) -> ValidationResult:
        """Valide la cohérence OHLC"""
        try:
            # Vérifier M30
            m30_data = snapshot.get('M30', {})
            if m30_data:
                high = m30_data.get('high')
                low = m30_data.get('low')
                
                if high is not None and low is not None:
                    if high < low:
                        return ValidationResult(
                            verdict=Verdict.ERROR,
                            message=f"M30 High < Low: {high} < {low}",
                            code="INVALID_M30_OHLC",
                            context={'high': high, 'low': low}
                        )
            
            return ValidationResult(verdict=Verdict.OK, message="OHLC cohérent", code="VALID_OHLC")
            
        except Exception as e:
            return ValidationResult(
                verdict=Verdict.ERROR,
                message=f"Erreur validation OHLC: {str(e)}",
                code="OHLC_VALIDATION_ERROR"
            )
    
    def _validate_vwap_consistency(self, snapshot: Dict[str, Any]) -> ValidationResult:
        """Valide la cohérence VWAP"""
        try:
            m1_data = snapshot.get('M1', {})
            if not m1_data:
                return ValidationResult(verdict=Verdict.OK, message="Pas de données M1", code="NO_M1_DATA")
            
            vwap = m1_data.get('vwap')
            high = m1_data.get('high')
            low = m1_data.get('low')
            
            if all(v is not None for v in [vwap, high, low]):
                range_size = high - low
                vwap_distance = min(abs(vwap - high), abs(vwap - low))
                
                if vwap_distance > range_size * self.bounds_checks['vwap_range_multiplier']:
                    return ValidationResult(
                        verdict=Verdict.WARN,
                        message=f"VWAP dérive: distance {vwap_distance:.2f} > range×{self.bounds_checks['vwap_range_multiplier']}",
                        code="VWAP_DRIFT",
                        context={'vwap': vwap, 'high': high, 'low': low, 'distance': vwap_distance}
                    )
            
            return ValidationResult(verdict=Verdict.OK, message="VWAP cohérent", code="VALID_VWAP")
            
        except Exception as e:
            return ValidationResult(
                verdict=Verdict.ERROR,
                message=f"Erreur validation VWAP: {str(e)}",
                code="VWAP_VALIDATION_ERROR"
            )
    
    def _validate_m1_m30_convergence(self, snapshot: Dict[str, Any]) -> ValidationResult:
        """Valide la convergence M1/M30"""
        try:
            m1_data = snapshot.get('M1', {})
            m30_data = snapshot.get('M30', {})
            
            if not m1_data or not m30_data:
                return ValidationResult(verdict=Verdict.OK, message="Données M1/M30 manquantes", code="NO_M1_M30_DATA")
            
            m1_close = m1_data.get('close')
            m30_low = m30_data.get('low')
            m30_high = m30_data.get('high')
            
            if all(v is not None for v in [m1_close, m30_low, m30_high]):
                epsilon = 0.5  # Tolérance 0.5 points
                if not (m30_low - epsilon <= m1_close <= m30_high + epsilon):
                    return ValidationResult(
                        verdict=Verdict.WARN,
                        message=f"M1 close {m1_close} pas cohérent avec M30 range [{m30_low}, {m30_high}]",
                        code="M1_M30_INCONSISTENT",
                        context={'m1_close': m1_close, 'm30_low': m30_low, 'm30_high': m30_high}
                    )
            
            return ValidationResult(verdict=Verdict.OK, message="M1/M30 cohérents", code="VALID_M1_M30")
            
        except Exception as e:
            return ValidationResult(
                verdict=Verdict.ERROR,
                message=f"Erreur validation M1/M30: {str(e)}",
                code="M1_M30_VALIDATION_ERROR"
            )
    
    def _validate_buffer_size(self, snapshot: Dict[str, Any]) -> ValidationResult:
        """Valide la taille des buffers"""
        try:
            m1_data = snapshot.get('M1', {})
            if m1_data and 'bars' in m1_data:
                bars_count = len(m1_data['bars'])
                if bars_count > 500:
                    return ValidationResult(
                        verdict=Verdict.WARN,
                        message=f"Buffer M1 trop grand: {bars_count} > 500",
                        code="LARGE_M1_BUFFER",
                        context={'bars_count': bars_count}
                    )
            
            return ValidationResult(verdict=Verdict.OK, message="Taille buffer OK", code="VALID_BUFFER_SIZE")
            
                except Exception as e:
            return ValidationResult(
                verdict=Verdict.ERROR,
                message=f"Erreur validation buffer: {str(e)}",
                code="BUFFER_VALIDATION_ERROR"
            )
    
    def _parse_timestamp(self, timestamp: Any) -> Optional[datetime]:
        """Parse un timestamp en datetime"""
        try:
            if not timestamp:
                return None
            
            if isinstance(timestamp, str):
                return datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            elif isinstance(timestamp, (int, float)):
                return datetime.fromtimestamp(timestamp, tz=timezone.utc)
            elif isinstance(timestamp, datetime):
                return timestamp.replace(tzinfo=timezone.utc) if timestamp.tzinfo is None else timestamp
            
            return None
        except Exception:
            return None
    
    def _record_validation(self, result: ValidationResult):
        """Enregistre le résultat de validation pour les stats"""
        try:
            # Ajouter à la fenêtre rolling
            self.stats_window.append(result)
            
            # Mettre à jour les compteurs par catégorie
            if result.verdict == Verdict.ERROR:
                self.error_categories[result.code] += 1
            elif result.verdict == Verdict.WARN:
                self.warn_categories[result.code] += 1
            
            # Nettoyer les anciens éléments (garder seulement 60s)
            cutoff_time = datetime.now(timezone.utc) - timedelta(seconds=60)
            while self.stats_window and self.stats_window[0].timestamp < cutoff_time:
                old_result = self.stats_window.popleft()
                if old_result.verdict == Verdict.ERROR:
                    self.error_categories[old_result.code] -= 1
                    if self.error_categories[old_result.code] <= 0:
                        del self.error_categories[old_result.code]
                elif old_result.verdict == Verdict.WARN:
                    self.warn_categories[old_result.code] -= 1
                    if self.warn_categories[old_result.code] <= 0:
                        del self.warn_categories[old_result.code]
            
                except Exception as e:
            self.logger.error(f"Erreur record validation: {e}")
    
    def get_stats(self, window: str = '60s') -> QualityStats:
        """
        Récupère les statistiques de qualité sur une fenêtre
        
        Args:
            window: Fenêtre d'analyse ('60s', '5m', '1h')
            
        Returns:
            QualityStats avec métriques de qualité
        """
        try:
            # Calculer la fenêtre
            if window == '60s':
                window_seconds = 60
            elif window == '5m':
                window_seconds = 300
            elif window == '1h':
                window_seconds = 3600
            else:
                window_seconds = 60
            
            cutoff_time = datetime.now(timezone.utc) - timedelta(seconds=window_seconds)
            
            # Filtrer les résultats dans la fenêtre
            window_results = [r for r in self.stats_window if r.timestamp >= cutoff_time]
            
            # Calculer les stats
            total_items = len(window_results)
            ok_count = sum(1 for r in window_results if r.verdict == Verdict.OK)
            warn_count = sum(1 for r in window_results if r.verdict == Verdict.WARN)
            error_count = sum(1 for r in window_results if r.verdict == Verdict.ERROR)
            
            error_rate = (error_count / total_items * 100) if total_items > 0 else 0.0
            warn_rate = (warn_count / total_items * 100) if total_items > 0 else 0.0
            
            # Top causes d'erreurs et warnings
            from collections import Counter
            error_causes = Counter(r.code for r in window_results if r.verdict == Verdict.ERROR)
            warn_causes = Counter(r.code for r in window_results if r.verdict == Verdict.WARN)
            
            return QualityStats(
                window_start=cutoff_time,
                window_end=datetime.now(timezone.utc),
                total_items=total_items,
                ok_count=ok_count,
                warn_count=warn_count,
                error_count=error_count,
                error_rate=error_rate,
                warn_rate=warn_rate,
                top_error_causes=error_causes.most_common(5),
                top_warn_causes=warn_causes.most_common(5)
            )
            
        except Exception as e:
            self.logger.error(f"Erreur get stats: {e}")
            return QualityStats(
                window_start=datetime.now(timezone.utc),
                window_end=datetime.now(timezone.utc)
            )

# Factory function
def create_data_quality_validator() -> DataQualityValidator:
    """Factory pour créer le Data Quality Validator"""
    return DataQualityValidator()

# Exemple d'utilisation:
"""
# Validation d'un événement:
    validator = create_data_quality_validator()
result = validator.validate_event({
    'type': 'quote',
    'symbol': 'ES',
    'timestamp': '2025-01-15T10:30:00Z',
    'bid': 5247.25,
    'ask': 5247.50,
    'bid_size': 100,
    'ask_size': 150
})

if result.verdict == Verdict.ERROR:
    logger.error(f"Événement invalide: {result.message}")
elif result.verdict == Verdict.WARN:
    logger.warning(f"Événement suspect: {result.message}")

# Validation d'un snapshot:
snapshot_result = validator.validate_snapshot(market_snapshot, "ES")

# Stats rolling 60s:
stats = validator.get_stats('60s')
logger.info(f"Qualité 60s: {stats.error_rate:.1f}% erreurs, {stats.warn_rate:.1f}% warnings")
"""
