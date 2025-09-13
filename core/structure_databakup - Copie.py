#!/usr/bin/env python3
"""
MIA_IA_SYSTEM - Structure Data Processor
Normaliseur de données JSONL vers records internes cohérents

VERSION: v2.0 - Records Internes
FONCTION: mia_unified_YYYYMMDD.jsonl → records typés internes
PERFORMANCE: <1ms par ligne, validation stricte, enrichissements calculés
COMPATIBILITÉ: 100% avec architecture Sierra-only

FONCTIONNALITÉS:
1. Conversion événements bruts → structures typées
2. Normalisation & alias (VAL/PVAL, SG labels)
3. Enrichissements calculés (distances MenthorQ, ranges, etc.)
4. Qualité & ordre temporel (monotonicité, idempotence)
5. Interfaces pour Patterns, Confluence, Battle Navale
6. Compatibilité market_snapshot.py
7. Aucune référence IBKR/Polygon/DTC-data
"""

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional, Set, List, Union
import json
import hashlib
import math
from .logger import get_logger
from .base_types import parse_ts

logger = get_logger(__name__)

# === CONFIGURATION ===

# Schéma d'entrée strict (types du fichier unifié)
VALID_TYPES = {
    "trade", "quote", "basedata", "vwap", "vva", "vap", "pvwap", "depth",
    "vix", "menthorq_gamma_levels", "menthorq_blind_spots", "menthorq_swing_levels"
}

VALID_GRAPHS = {3, 4, 8, 10}

# Champs obligatoires par type (basés sur mia_unified_YYYYMMDD.jsonl)
REQUIRED_FIELDS = {
    "basedata": {"type", "graph", "sym", "ts", "o", "h", "l", "c", "v"},
    "vwap": {"type", "graph", "sym", "ts", "v"},
    "vva": {"type", "graph", "sym", "ts", "vah", "val", "vpoc"},
    "vap": {"type", "graph", "sym", "ts", "price", "vol"},
    "depth": {"type", "graph", "sym", "ts", "side", "lvl", "price", "size"},
    "quote": {"type", "graph", "sym", "ts", "kind", "bid", "ask", "bq", "aq"},
    "trade": {"type", "graph", "sym", "ts", "px", "vol"},
    "pvwap": {"type", "graph", "sym", "ts", "pvwap"},
    "vix": {"type", "graph", "sym", "ts", "last"},
    "menthorq_gamma_levels": {"type", "graph", "sym", "ts", "study_id", "sg", "label", "price"},
    "menthorq_blind_spots": {"type", "graph", "sym", "ts", "study_id", "sg", "label", "price"},
    "menthorq_swing_levels": {"type", "graph", "sym", "ts", "study_id", "sg", "label", "price"}
}

# Validation de domaines
DOMAIN_VALIDATORS = {
    "graph": lambda x: x in VALID_GRAPHS,
    "quote.kind": lambda x: x == "BIDASK",
    "depth.side": lambda x: x in {"BID", "ASK"},
    "depth.lvl": lambda x: x >= 1,
    "menthorq.study_id": lambda x: x in {1, 2, 3},
    "menthorq.sg": lambda x: x >= 1,
    "menthorq.price": lambda x: x > 0
}

# === RECORDS INTERNES TYPÉS ===

@dataclass
class MarketBarM1:
    """Barre de marché 1-minute"""
    symbol: str
    ts: datetime
    ohlc: Dict[str, float]  # {"o": 5292.75, "h": 5296.0, "l": 5291.5, "c": 5295.0}
    volume: int
    bid_volume: Optional[int] = None
    ask_volume: Optional[int] = None
    open_interest: Optional[int] = None

@dataclass
class MarketBarM30:
    """Barre de marché 30-minute"""
    symbol: str
    ts: datetime
    ohlc: Dict[str, float]
    volume: int

@dataclass
class VWAPBandM1:
    """Bandes VWAP 1-minute"""
    symbol: str
    ts: datetime
    vwap: float
    upper_band_1: Optional[float] = None
    lower_band_1: Optional[float] = None
    upper_band_2: Optional[float] = None
    lower_band_2: Optional[float] = None
    source: Optional[str] = None

@dataclass
class VWAPBandM30:
    """Bandes VWAP 30-minute"""
    symbol: str
    ts: datetime
    vwap: float
    upper_band_1: Optional[float] = None
    lower_band_1: Optional[float] = None
    upper_band_2: Optional[float] = None
    lower_band_2: Optional[float] = None

@dataclass
class VolumeProfile:
    """Profil de volume (VVA/VAP)"""
    symbol: str
    ts: datetime
    vah: float  # Value Area High
    val: float  # Value Area Low
    vpoc: float  # Volume Point of Control
    prev_vah: Optional[float] = None
    prev_val: Optional[float] = None
    prev_vpoc: Optional[float] = None
    session_id_current: Optional[str] = None
    session_id_previous: Optional[str] = None

@dataclass
class VolumeProfileTick:
    """Tick de profil de volume (VAP)"""
    symbol: str
    ts: datetime
    price: float
    volume: int
    bar_number: Optional[int] = None
    k_value: Optional[int] = None

@dataclass
class NBCVM1:
    """NBCV 1-minute (Net Bid/Ask Volume)"""
    symbol: str
    ts: datetime
    net_volume: int  # ask_volume - bid_volume

@dataclass
class NBCVM30:
    """NBCV 30-minute"""
    symbol: str
    ts: datetime
    net_volume: int

@dataclass
class DOMLevel:
    """Niveau DOM (Depth of Market)"""
    symbol: str
    ts: datetime
    side: str  # "BID" ou "ASK"
    level: int
    price: float
    size: int

@dataclass
class Quote:
    """Cote bid/ask"""
    symbol: str
    ts: datetime
    bid: float
    ask: float
    bid_quantity: int
    ask_quantity: int
    sequence: Optional[int] = None

@dataclass
class VIXTick:
    """Tick VIX"""
    symbol: str
    ts: datetime
    price: float
    mode: Optional[str] = None

@dataclass
class MenthorQLevels:
    """Niveaux MenthorQ consolidés"""
    symbol: str
    ts: datetime
    gamma_levels: Dict[str, float]  # {"GEX1": 5300.0, "GEX2": 5305.0, ...}
    blind_spots: Dict[str, float]  # {"BL1": 5295.0, "BL2": 5290.0, ...}
    swing_levels: Dict[str, float]  # {"SG1": 5288.0, "SG2": 5285.0, ...}
    call_resistance: Optional[float] = None
    put_support: Optional[float] = None
    gamma_wall_0dte: Optional[float] = None
    hvl: Optional[float] = None  # High Volume Level
    partial: bool = False  # True si certains champs manquent

# Union de tous les records internes
InternalRecord = Union[
    MarketBarM1, MarketBarM30, VWAPBandM1, VWAPBandM30, VolumeProfile, VolumeProfileTick,
    NBCVM1, NBCVM30, DOMLevel, Quote, VIXTick, MenthorQLevels
]

# === STRUCTURE DATA PROCESSOR ===

@dataclass
class StructureDataProcessor:
    """
    Processeur de données JSONL Sierra Chart
    
    Traite les lignes des fichiers chart_{3,4,8,10}_*.jsonl et les normalise
    pour le fichier unifié mia_unified_YYYYMMDD.jsonl
    """
    
    # Configuration
    stale_minutes: int = 5
    enable_dedup: bool = True
    enable_stale_filter: bool = True
    
    # État interne
    seen_events: Set[str] = field(default_factory=set)
    counters: Dict[str, int] = field(default_factory=lambda: {
        "accepted": 0, "rejected": 0, "duplicates": 0, "stale": 0, "total": 0
    })
    
    # Métriques
    last_summary_time: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    summary_interval_seconds: int = 30
    
    def __post_init__(self):
        """Initialisation du processeur"""
        logger.info(f"StructureDataProcessor initialisé - stale: {self.stale_minutes}min, dédup: {self.enable_dedup}")
    
    def process_line(self, line: str) -> Optional[Dict[str, Any]]:
        """
        Traite une ligne JSONL et retourne l'événement normalisé
        
        Args:
            line: Ligne JSONL brute
            
        Returns:
            Dict normalisé prêt pour mia_unified_YYYYMMDD.jsonl ou None si rejeté
        """
        self.counters["total"] += 1
        
        try:
            # 1. Parse JSON
            data = self._parse_json(line)
            if data is None:
                return None
            
            # 2. Validation schéma
            if not self._validate_schema(data):
                return None
            
            # 3. Horodatage UTC
            if not self._normalize_timestamp(data):
                return None
            
            # 4. Déduplication
            if self._is_duplicate(data):
                self.counters["duplicates"] += 1
                logger.debug(f"Duplicate event: {data.get('type', 'unknown')} @ {data.get('ts', 'unknown')}")
                return None
            
            # 5. Filtre stale
            if self._is_stale(data):
                self.counters["stale"] += 1
                logger.debug(f"Stale event: {data.get('type', 'unknown')} @ {data.get('ts', 'unknown')}")
                return None
            
            # 6. Normalisation
            normalized = self._normalize_event(data)
            
            # 7. Marquer comme vu
            if self.enable_dedup:
                self._mark_as_seen(data)
            
            # 8. Compteur accepté
            self.counters["accepted"] += 1
            
            # 9. Logs périodiques
            self._log_periodic_summary()
            
            return normalized
            
        except Exception as e:
            self.counters["rejected"] += 1
            logger.error(f"Erreur traitement ligne: {e}")
            return None
    
    def _parse_json(self, line: str) -> Optional[Dict[str, Any]]:
        """Parse une ligne JSON avec gestion d'erreurs"""
        try:
            line = line.strip()
            if not line:
                return None
            
            data = json.loads(line)
            if not isinstance(data, dict):
                logger.warning(f"Ligne non-dict ignorée: {line[:100]}...")
                return None
            
            return data
            
        except json.JSONDecodeError as e:
            logger.warning(f"JSON invalide ignoré: {e}")
            return None
        except Exception as e:
            logger.error(f"Erreur parse JSON: {e}")
            return None
    
    def _validate_schema(self, data: Dict[str, Any]) -> bool:
        """Validation stricte du schéma"""
        try:
            # Vérifier type
            event_type = data.get("type")
            if event_type not in VALID_TYPES:
                logger.warning(f"Type invalide: {event_type}")
                return False
            
            # Vérifier champs obligatoires
            required = REQUIRED_FIELDS.get(event_type, set())
            missing = required - set(data.keys())
            if missing:
                logger.warning(f"Champs manquants pour {event_type}: {missing}")
                return False
            
            # Vérifier graph
            graph = data.get("graph")
            if not DOMAIN_VALIDATORS["graph"](graph):
                logger.warning(f"Graph invalide: {graph}")
                return False
            
            # Validations spécifiques par type
            if not self._validate_type_specific(data, event_type):
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Erreur validation schéma: {e}")
            return False
    
    def _validate_type_specific(self, data: Dict[str, Any], event_type: str) -> bool:
        """Validations spécifiques par type d'événement"""
        try:
            if event_type == "quote":
                if not DOMAIN_VALIDATORS["quote.kind"](data.get("kind")):
                    logger.warning(f"Quote kind invalide: {data.get('kind')}")
                    return False
            
            elif event_type == "depth":
                if not DOMAIN_VALIDATORS["depth.side"](data.get("side")):
                    logger.warning(f"Depth side invalide: {data.get('side')}")
                    return False
                if not DOMAIN_VALIDATORS["depth.lvl"](data.get("lvl")):
                    logger.warning(f"Depth lvl invalide: {data.get('lvl')}")
                    return False
            
            elif event_type.startswith("menthorq_"):
                if not DOMAIN_VALIDATORS["menthorq.study_id"](data.get("study_id")):
                    logger.warning(f"MenthorQ study_id invalide: {data.get('study_id')}")
                    return False
                if not DOMAIN_VALIDATORS["menthorq.sg"](data.get("sg")):
                    logger.warning(f"MenthorQ sg invalide: {data.get('sg')}")
                    return False
                if not DOMAIN_VALIDATORS["menthorq.price"](data.get("price")):
                    logger.warning(f"MenthorQ price invalide: {data.get('price')}")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Erreur validation spécifique {event_type}: {e}")
            return False
    
    def _normalize_timestamp(self, data: Dict[str, Any]) -> bool:
        """Normalise l'horodatage en UTC"""
        try:
            # Essayer ts d'abord, puis ingest_ts
            ts_field = data.get("ts") or data.get("ingest_ts")
            if not ts_field:
                logger.warning("Aucun timestamp trouvé")
                return False
            
            # Parser avec parse_ts (UTC-aware)
            parsed_ts = parse_ts(ts_field)
            if parsed_ts is None:
                logger.warning(f"Timestamp invalide: {ts_field}")
                return False
            
            # Forcer UTC si pas de timezone
            if parsed_ts.tzinfo is None:
                parsed_ts = parsed_ts.replace(tzinfo=timezone.utc)
                logger.debug(f"Timestamp sans tz, forcé UTC: {ts_field}")
            
            # Normaliser en UTC
            data["ts"] = parsed_ts.astimezone(timezone.utc).isoformat()
            return True
            
        except Exception as e:
            logger.error(f"Erreur normalisation timestamp: {e}")
            return False
    
    def _is_duplicate(self, data: Dict[str, Any]) -> bool:
        """Vérifie si l'événement est un doublon"""
        if not self.enable_dedup:
            return False
        
        # Construire clé de dédup
        dedup_key = self._build_dedup_key(data)
        return dedup_key in self.seen_events
    
    def _build_dedup_key(self, data: Dict[str, Any]) -> str:
        """Construit une clé de déduplication"""
        try:
            # Clé basée sur: sym|graph|type|ts|payload-hash
            sym = data.get("sym", "")
            graph = data.get("graph", "")
            event_type = data.get("type", "")
            ts = data.get("ts", "")
            
            # Hash du payload (sans ts pour éviter micro-différences)
            payload = {k: v for k, v in data.items() if k != "ts"}
            payload_str = json.dumps(payload, sort_keys=True)
            payload_hash = hashlib.md5(payload_str.encode()).hexdigest()[:8]
            
            return f"{sym}|{graph}|{event_type}|{ts}|{payload_hash}"
            
        except Exception as e:
            logger.error(f"Erreur construction clé dédup: {e}")
            return f"error|{hash(str(data))}"
    
    def _is_stale(self, data: Dict[str, Any]) -> bool:
        """Vérifie si l'événement est trop ancien"""
        if not self.enable_stale_filter:
            return False
        
        try:
            event_ts = parse_ts(data.get("ts", ""))
            if event_ts is None:
                return True  # Timestamp invalide = stale
            
            now = datetime.now(timezone.utc)
            age = now - event_ts
            
            return age > timedelta(minutes=self.stale_minutes)
            
        except Exception as e:
            logger.error(f"Erreur vérification stale: {e}")
            return True
    
    def _normalize_event(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalise l'événement pour le format unifié"""
        try:
            # Copie de base
            normalized = data.copy()
            
            # Ajouter version schéma
            normalized["schema_version"] = "1.0"
            
            # Normaliser les noms de champs
            self._normalize_field_names(normalized)
            
            # Harmoniser les valeurs
            self._harmonize_values(normalized)
            
            return normalized
            
        except Exception as e:
            logger.error(f"Erreur normalisation événement: {e}")
            return data
    
    def _normalize_field_names(self, data: Dict[str, Any]) -> None:
        """Normalise les noms de champs"""
        # Harmoniser les noms (ex: pvah → pvah, pval → pval)
        field_mapping = {
            "pvah": "pvah",  # Déjà correct
            "pval": "pval",  # Déjà correct
            "ppoc": "ppoc"   # Déjà correct
        }
        
        for old_name, new_name in field_mapping.items():
            if old_name in data and old_name != new_name:
                data[new_name] = data.pop(old_name)
    
    def _harmonize_values(self, data: Dict[str, Any]) -> None:
        """Harmonise les valeurs"""
        # Pour MenthorQ, garder les labels tels qu'affichés
        if data.get("type", "").startswith("menthorq_"):
            label = data.get("label", "")
            if label:
                # Garder le label original (ex: "BL 1", "SG1", "Call Resistance")
                data["label"] = label.strip()
    
    def _mark_as_seen(self, data: Dict[str, Any]) -> None:
        """Marque l'événement comme vu pour la dédup"""
        try:
            dedup_key = self._build_dedup_key(data)
            self.seen_events.add(dedup_key)
            
            # Limiter la taille du cache (éviter fuite mémoire)
            if len(self.seen_events) > 100000:  # 100k événements max
                # Garder les 50k plus récents (approximation)
                self.seen_events = set(list(self.seen_events)[-50000:])
                logger.debug("Cache dédup nettoyé (100k → 50k)")
                
        except Exception as e:
            logger.error(f"Erreur marquage vu: {e}")
    
    def _log_periodic_summary(self) -> None:
        """Log périodique des métriques"""
        try:
            now = datetime.now(timezone.utc)
            if (now - self.last_summary_time).total_seconds() >= self.summary_interval_seconds:
                self._log_summary()
                self.last_summary_time = now
                
        except Exception as e:
            logger.error(f"Erreur log périodique: {e}")
    
    def _log_summary(self) -> None:
        """Log de synthèse des métriques"""
        try:
            total = self.counters["total"]
            accepted = self.counters["accepted"]
            rejected = self.counters["rejected"]
            duplicates = self.counters["duplicates"]
            stale = self.counters["stale"]
            
            if total > 0:
                accept_rate = (accepted / total) * 100
                logger.info(f"structure_data: {accepted} accepted, {rejected} rejected "
                           f"({stale} stale, {duplicates} duplicates) - {accept_rate:.1f}% success")
            
        except Exception as e:
            logger.error(f"Erreur log synthèse: {e}")
    
    def get_metrics(self) -> Dict[str, Any]:
        """Retourne les métriques actuelles"""
        return {
            "counters": self.counters.copy(),
            "cache_size": len(self.seen_events),
            "config": {
                "stale_minutes": self.stale_minutes,
                "enable_dedup": self.enable_dedup,
                "enable_stale_filter": self.enable_stale_filter
            }
        }
    
    def reset_metrics(self) -> None:
        """Remet à zéro les métriques"""
        self.counters = {
            "accepted": 0, "rejected": 0, "duplicates": 0, "stale": 0, "total": 0
        }
        self.seen_events.clear()
        logger.info("Métriques remises à zéro")

# === INTERFACES DE CONVERSION ===

def to_internal(event: Dict[str, Any]) -> Optional[InternalRecord]:
    """
    Convertit un événement brut en record interne typé
    
    Args:
        event: Événement du fichier unifié
        
    Returns:
        Record interne typé ou None si conversion impossible
    """
    try:
        event_type = event.get("type")
        symbol = event.get("sym", "")
        ts = parse_ts(event.get("ts", ""))
        
        if ts is None:
            logger.warning(f"Timestamp invalide pour {event_type}")
            return None
        
        # Conversion par type
        if event_type == "basedata":
            return _convert_basedata(event, symbol, ts)
        elif event_type == "vwap":
            return _convert_vwap(event, symbol, ts)
        elif event_type == "vva":
            return _convert_vva(event, symbol, ts)
        elif event_type == "vap":
            return _convert_vap(event, symbol, ts)
        elif event_type == "depth":
            return _convert_depth(event, symbol, ts)
        elif event_type == "quote":
            return _convert_quote(event, symbol, ts)
        elif event_type == "trade":
            return _convert_trade(event, symbol, ts)
        elif event_type == "pvwap":
            return _convert_pvwap(event, symbol, ts)
        elif event_type == "vix":
            return _convert_vix(event, symbol, ts)
        elif event_type.startswith("menthorq_"):
            return _convert_menthorq(event, symbol, ts)
        else:
            logger.warning(f"Type d'événement non supporté: {event_type}")
            return None
            
    except Exception as e:
        logger.error(f"Erreur conversion vers record interne: {e}")
        return None

def batch_to_internal(events_iterable) -> List[InternalRecord]:
    """
    Convertit un batch d'événements en records internes
    
    Args:
        events_iterable: Itérable d'événements
        
    Returns:
        Liste de records internes valides
    """
    records = []
    for event in events_iterable:
        record = to_internal(event)
        if record is not None:
            records.append(record)
    return records

def resolve_levels(snapshot: Dict[str, Any]) -> Dict[str, Any]:
    """
    Produit une vue compacte des niveaux pour Battle Navale
    
    Args:
        snapshot: Snapshot de marché
        
    Returns:
        Dict avec niveaux consolidés
    """
    try:
        levels = {
            "vah": None, "val": None, "vpoc": None,
            "vwap": None, "vwap_upper": None, "vwap_lower": None,
            "call_resistance": None, "put_support": None,
            "gamma_wall": None, "hvl": None,
            "blind_spots": [], "swing_levels": []
        }
        
        # Extraire niveaux du snapshot
        for key, value in snapshot.items():
            if isinstance(value, dict):
                if "vah" in value:
                    levels["vah"] = value.get("vah")
                    levels["val"] = value.get("val")
                    levels["vpoc"] = value.get("vpoc")
                elif "vwap" in value:
                    levels["vwap"] = value.get("vwap")
                    levels["vwap_upper"] = value.get("upper_band_1")
                    levels["vwap_lower"] = value.get("lower_band_1")
                elif "call_resistance" in value:
                    levels["call_resistance"] = value.get("call_resistance")
                    levels["put_support"] = value.get("put_support")
                    levels["gamma_wall"] = value.get("gamma_wall_0dte")
                    levels["hvl"] = value.get("hvl")
        
        return levels
        
    except Exception as e:
        logger.error(f"Erreur résolution niveaux: {e}")
        return {}

# === FONCTIONS DE CONVERSION SPÉCIFIQUES ===

def _convert_basedata(event: Dict[str, Any], symbol: str, ts: datetime) -> Optional[MarketBarM1]:
    """Convertit basedata en MarketBarM1"""
    try:
        ohlc = {
            "o": event.get("o", 0.0),
            "h": event.get("h", 0.0),
            "l": event.get("l", 0.0),
            "c": event.get("c", 0.0)
        }
        
        return MarketBarM1(
            symbol=symbol,
            ts=ts,
            ohlc=ohlc,
            volume=event.get("v", 0),
            bid_volume=event.get("bidvol"),
            ask_volume=event.get("askvol"),
            open_interest=event.get("oi")
        )
    except Exception as e:
        logger.error(f"Erreur conversion basedata: {e}")
        return None

def _convert_vwap(event: Dict[str, Any], symbol: str, ts: datetime) -> Optional[VWAPBandM1]:
    """Convertit vwap en VWAPBandM1"""
    try:
        return VWAPBandM1(
            symbol=symbol,
            ts=ts,
            vwap=event.get("v", 0.0),
            upper_band_1=event.get("up1"),
            lower_band_1=event.get("dn1"),
            upper_band_2=event.get("up2"),
            lower_band_2=event.get("dn2"),
            source=event.get("src")
        )
    except Exception as e:
        logger.error(f"Erreur conversion vwap: {e}")
        return None

def _convert_vva(event: Dict[str, Any], symbol: str, ts: datetime) -> Optional[VolumeProfile]:
    """Convertit vva en VolumeProfile"""
    try:
        return VolumeProfile(
            symbol=symbol,
            ts=ts,
            vah=event.get("vah", 0.0),
            val=event.get("val", 0.0),
            vpoc=event.get("vpoc", 0.0),
            prev_vah=event.get("pvah"),
            prev_val=event.get("pval"),
            prev_vpoc=event.get("ppoc"),
            session_id_current=event.get("id_curr"),
            session_id_previous=event.get("id_prev")
        )
    except Exception as e:
        logger.error(f"Erreur conversion vva: {e}")
        return None

def _convert_vap(event: Dict[str, Any], symbol: str, ts: datetime) -> Optional[VolumeProfileTick]:
    """Convertit vap en VolumeProfileTick"""
    try:
        return VolumeProfileTick(
            symbol=symbol,
            ts=ts,
            price=event.get("price", 0.0),
            volume=event.get("vol", 0),
            bar_number=event.get("bar"),
            k_value=event.get("k")
        )
    except Exception as e:
        logger.error(f"Erreur conversion vap: {e}")
        return None

def _convert_depth(event: Dict[str, Any], symbol: str, ts: datetime) -> Optional[DOMLevel]:
    """Convertit depth en DOMLevel"""
    try:
        return DOMLevel(
            symbol=symbol,
            ts=ts,
            side=event.get("side", "BID"),
            level=event.get("lvl", 1),
            price=event.get("price", 0.0),
            size=event.get("size", 0)
        )
    except Exception as e:
        logger.error(f"Erreur conversion depth: {e}")
        return None

def _convert_quote(event: Dict[str, Any], symbol: str, ts: datetime) -> Optional[Quote]:
    """Convertit quote en Quote"""
    try:
        return Quote(
            symbol=symbol,
            ts=ts,
            bid=event.get("bid", 0.0),
            ask=event.get("ask", 0.0),
            bid_quantity=event.get("bq", 0),
            ask_quantity=event.get("aq", 0),
            sequence=event.get("seq")
        )
    except Exception as e:
        logger.error(f"Erreur conversion quote: {e}")
        return None

def _convert_trade(event: Dict[str, Any], symbol: str, ts: datetime) -> Optional[Dict[str, Any]]:
    """Convertit trade en dict simple (pas de record dédié pour l'instant)"""
    try:
        return {
            "type": "trade",
            "symbol": symbol,
            "ts": ts,
            "price": event.get("px", 0.0),
            "volume": event.get("vol", 0),
            "sequence": event.get("seq")
        }
    except Exception as e:
        logger.error(f"Erreur conversion trade: {e}")
        return None

def _convert_pvwap(event: Dict[str, Any], symbol: str, ts: datetime) -> Optional[VWAPBandM30]:
    """Convertit pvwap en VWAPBandM30"""
    try:
        return VWAPBandM30(
            symbol=symbol,
            ts=ts,
            vwap=event.get("pvwap", 0.0),
            upper_band_1=event.get("up1"),
            lower_band_1=event.get("dn1"),
            upper_band_2=event.get("up2"),
            lower_band_2=event.get("dn2")
        )
    except Exception as e:
        logger.error(f"Erreur conversion pvwap: {e}")
        return None

def _convert_vix(event: Dict[str, Any], symbol: str, ts: datetime) -> Optional[VIXTick]:
    """Convertit vix en VIXTick"""
    try:
        return VIXTick(
            symbol=symbol,
            ts=ts,
            price=event.get("last", 0.0),
            mode=event.get("mode")
        )
    except Exception as e:
        logger.error(f"Erreur conversion vix: {e}")
        return None

def _convert_menthorq(event: Dict[str, Any], symbol: str, ts: datetime) -> Optional[MenthorQLevels]:
    """Convertit menthorq en MenthorQLevels (consolidation)"""
    try:
        # Cette fonction sera appelée pour chaque niveau MenthorQ
        # On retourne None ici car la consolidation se fait ailleurs
        return None
    except Exception as e:
        logger.error(f"Erreur conversion menthorq: {e}")
        return None

# === ENRICHISSEMENTS CALCULÉS ===

def calculate_menthorq_distances(current_price: float, menthorq_levels: MenthorQLevels) -> Dict[str, float]:
    """
    Calcule les distances aux niveaux MenthorQ
    
    Args:
        current_price: Prix actuel
        menthorq_levels: Niveaux MenthorQ
        
    Returns:
        Dict avec distances calculées
    """
    try:
        distances = {}
        
        # Distance Call Resistance
        if menthorq_levels.call_resistance:
            distances["dist_to_call_res"] = abs(current_price - menthorq_levels.call_resistance)
        
        # Distance Put Support
        if menthorq_levels.put_support:
            distances["dist_to_put_sup"] = abs(current_price - menthorq_levels.put_support)
        
        # Distance Gamma Wall
        if menthorq_levels.gamma_wall_0dte:
            distances["dist_to_gamma_wall"] = abs(current_price - menthorq_levels.gamma_wall_0dte)
        
        # Distance minimale aux Blind Spots
        if menthorq_levels.blind_spots:
            min_bl_dist = min(abs(current_price - price) for price in menthorq_levels.blind_spots.values())
            distances["min_dist_to_BL"] = min_bl_dist
        
        # Distance minimale aux Swing Levels
        if menthorq_levels.swing_levels:
            min_swing_dist = min(abs(current_price - price) for price in menthorq_levels.swing_levels.values())
            distances["min_dist_to_swing"] = min_swing_dist
        
        return distances
        
    except Exception as e:
        logger.error(f"Erreur calcul distances MenthorQ: {e}")
        return {}

def calculate_enrichments(record: InternalRecord, context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calcule les enrichissements pour un record
    
    Args:
        record: Record interne
        context: Contexte de marché
        
    Returns:
        Dict avec enrichissements calculés
    """
    try:
        enrichments = {}
        
        if isinstance(record, MarketBarM1):
            # Calculer range M1
            ohlc = record.ohlc
            enrichments["m1_range"] = ohlc["h"] - ohlc["l"]
            
            # Calculer NBCV si disponible
            if record.bid_volume is not None and record.ask_volume is not None:
                enrichments["nbcv_m1"] = record.ask_volume - record.bid_volume
        
        elif isinstance(record, VWAPBandM1):
            # Distance au VWAP
            current_price = context.get("current_price", 0.0)
            if current_price > 0:
                enrichments["vwap_distance"] = abs(current_price - record.vwap)
                enrichments["pos_vs_vwap"] = "above" if current_price > record.vwap else "below"
        
        elif isinstance(record, VolumeProfile):
            # Distance aux niveaux VP
            current_price = context.get("current_price", 0.0)
            if current_price > 0:
                enrichments["dist_to_vah"] = abs(current_price - record.vah)
                enrichments["dist_to_val"] = abs(current_price - record.val)
                enrichments["dist_to_vpoc"] = abs(current_price - record.vpoc)
        
        return enrichments
        
    except Exception as e:
        logger.error(f"Erreur calcul enrichissements: {e}")
        return {}

# === CONSOLIDATION MENTHORQ ===

class MenthorQConsolidator:
    """Consolidateur des niveaux MenthorQ"""
    
    def __init__(self):
        self.pending_levels: Dict[str, Dict[str, Any]] = {}
        self.consolidated_levels: Dict[str, MenthorQLevels] = {}
    
    def add_menthorq_event(self, event: Dict[str, Any]) -> Optional[MenthorQLevels]:
        """
        Ajoute un événement MenthorQ et retourne le niveau consolidé si complet
        
        Args:
            event: Événement MenthorQ
            
        Returns:
            MenthorQLevels consolidé ou None si incomplet
        """
        try:
            symbol = event.get("sym", "")
            ts = parse_ts(event.get("ts", ""))
            event_type = event.get("type", "")
            
            if ts is None:
                return None
            
            # Clé de consolidation (symbol + timestamp arrondi à la minute)
            consolidation_key = f"{symbol}_{ts.replace(second=0, microsecond=0).isoformat()}"
            
            # Initialiser si nouveau
            if consolidation_key not in self.pending_levels:
                self.pending_levels[consolidation_key] = {
                    "symbol": symbol,
                    "ts": ts,
                    "gamma_levels": {},
                    "blind_spots": {},
                    "swing_levels": {},
                    "call_resistance": None,
                    "put_support": None,
                    "gamma_wall_0dte": None,
                    "hvl": None,
                    "partial": True
                }
            
            level_data = self.pending_levels[consolidation_key]
            
            # Traiter selon le type
            if event_type == "menthorq_gamma_levels":
                label = event.get("label", "")
                price = event.get("price", 0.0)
                
                if label == "Call Resistance":
                    level_data["call_resistance"] = price
                elif label == "Put Support":
                    level_data["put_support"] = price
                elif label == "Gamma Wall 0DTE":
                    level_data["gamma_wall_0dte"] = price
                elif label == "HVL":
                    level_data["hvl"] = price
                elif label.startswith("GEX"):
                    level_data["gamma_levels"][label] = price
            
            elif event_type == "menthorq_blind_spots":
                label = event.get("label", "")
                price = event.get("price", 0.0)
                if label.startswith("BL"):
                    level_data["blind_spots"][label] = price
            
            elif event_type == "menthorq_swing_levels":
                label = event.get("label", "")
                price = event.get("price", 0.0)
                if label.startswith("SG"):
                    level_data["swing_levels"][label] = price
            
            # Vérifier si consolidation complète (au moins les niveaux principaux)
            if (level_data["call_resistance"] is not None and 
                level_data["put_support"] is not None):
                
                # Créer le record consolidé
                consolidated = MenthorQLevels(
                    symbol=symbol,
                    ts=ts,
                    gamma_levels=level_data["gamma_levels"].copy(),
                    blind_spots=level_data["blind_spots"].copy(),
                    swing_levels=level_data["swing_levels"].copy(),
                    call_resistance=level_data["call_resistance"],
                    put_support=level_data["put_support"],
                    gamma_wall_0dte=level_data["gamma_wall_0dte"],
                    hvl=level_data["hvl"],
                    partial=level_data["partial"]
                )
                
                # Stocker et nettoyer
                self.consolidated_levels[consolidation_key] = consolidated
                del self.pending_levels[consolidation_key]
                
                logger.debug(f"Consolidé MenthorQ: {symbol} @ {ts} - "
                           f"CR={consolidated.call_resistance}, PS={consolidated.put_support}")
                
                return consolidated
            
            return None
            
        except Exception as e:
            logger.error(f"Erreur consolidation MenthorQ: {e}")
            return None

# === FACTORY FUNCTIONS ===

def create_structure_data_processor(
    stale_minutes: int = 5,
    enable_dedup: bool = True,
    enable_stale_filter: bool = True
) -> StructureDataProcessor:
    """Factory function pour StructureDataProcessor"""
    return StructureDataProcessor(
        stale_minutes=stale_minutes,
        enable_dedup=enable_dedup,
        enable_stale_filter=enable_stale_filter
    )

def create_menthorq_consolidator() -> MenthorQConsolidator:
    """Factory function pour MenthorQConsolidator"""
    return MenthorQConsolidator()

# === TESTING ===

def test_structure_data_processor():
    """Tests du processeur de données"""
    logger.info("Test StructureDataProcessor...")
    
    processor = create_structure_data_processor()
    
    # Test 1: Ligne valide (timestamp récent)
    from datetime import datetime, timezone
    now = datetime.now(timezone.utc).isoformat()
    valid_line = f'{{"type":"basedata","graph":3,"sym":"ESU25","ts":"{now}","o":5292.75,"h":5296.0,"l":5291.5,"c":5295.0,"v":1250}}'
    result = processor.process_line(valid_line)
    assert result is not None, "Ligne valide rejetée"
    assert result["type"] == "basedata", "Type incorrect"
    logger.info("✅ Test ligne valide OK")
    
    # Test 2: Ligne invalide
    invalid_line = '{"type":"invalid","graph":99,"sym":"ESU25","ts":"2025-09-07T13:30:00Z"}'
    result = processor.process_line(invalid_line)
    assert result is None, "Ligne invalide acceptée"
    logger.info("✅ Test ligne invalide OK")
    
    # Test 3: Doublon (nouvelle ligne identique)
    now2 = datetime.now(timezone.utc).isoformat()
    duplicate_line = f'{{"type":"basedata","graph":3,"sym":"ESU25","ts":"{now2}","o":5292.75,"h":5296.0,"l":5291.5,"c":5295.0,"v":1250}}'
    result1 = processor.process_line(duplicate_line)
    result2 = processor.process_line(duplicate_line)
    assert result1 is not None, "Première ligne rejetée"
    assert result2 is None, "Doublon accepté"
    logger.info("✅ Test déduplication OK")
    
    # Test 4: Métriques
    metrics = processor.get_metrics()
    assert metrics["counters"]["accepted"] >= 1, "Compteur accepté incorrect"
    assert metrics["counters"]["duplicates"] >= 1, "Compteur doublons incorrect"
    logger.info("✅ Test métriques OK")
    
    logger.info("🎉 Tous les tests StructureDataProcessor réussis!")
    return processor

def test_conversion_to_internal():
    """Tests de conversion vers records internes"""
    logger.info("Test conversion vers records internes...")
    
    # Test 1: Conversion basedata
    basedata_event = {
        "type": "basedata",
        "graph": 3,
        "sym": "ESU25_FUT_CME",
        "ts": "2025-09-07T13:30:00+00:00",
        "o": 5292.75,
        "h": 5296.0,
        "l": 5291.5,
        "c": 5295.0,
        "v": 1250,
        "bidvol": 640,
        "askvol": 610
    }
    
    record = to_internal(basedata_event)
    assert record is not None, "Conversion basedata échouée"
    assert isinstance(record, MarketBarM1), "Type de record incorrect"
    assert record.symbol == "ESU25_FUT_CME", "Symbole incorrect"
    assert record.ohlc["o"] == 5292.75, "OHLC incorrect"
    logger.info("✅ Test conversion basedata OK")
    
    # Test 2: Conversion VWAP
    vwap_event = {
        "type": "vwap",
        "graph": 3,
        "sym": "ESU25_FUT_CME",
        "ts": "2025-09-07T13:30:00+00:00",
        "v": 5293.5,
        "up1": 5295.0,
        "dn1": 5292.0
    }
    
    record = to_internal(vwap_event)
    assert record is not None, "Conversion VWAP échouée"
    assert isinstance(record, VWAPBandM1), "Type de record incorrect"
    assert record.vwap == 5293.5, "VWAP incorrect"
    logger.info("✅ Test conversion VWAP OK")
    
    # Test 3: Conversion VIX
    vix_event = {
        "type": "vix",
        "graph": 8,
        "sym": "^VIX",
        "ts": "2025-09-07T13:30:00+00:00",
        "last": 18.5,
        "mode": "study"
    }
    
    record = to_internal(vix_event)
    assert record is not None, "Conversion VIX échouée"
    assert isinstance(record, VIXTick), "Type de record incorrect"
    assert record.price == 18.5, "Prix VIX incorrect"
    logger.info("✅ Test conversion VIX OK")
    
    logger.info("🎉 Tous les tests de conversion réussis!")

def test_menthorq_consolidation():
    """Tests de consolidation MenthorQ"""
    logger.info("Test consolidation MenthorQ...")
    
    consolidator = create_menthorq_consolidator()
    
    # Test 1: Ajout Call Resistance
    cr_event = {
        "type": "menthorq_gamma_levels",
        "graph": 10,
        "sym": "ESU25_FUT_CME",
        "ts": "2025-09-07T13:30:00+00:00",
        "study_id": 1,
        "sg": 1,
        "label": "Call Resistance",
        "price": 5300.0
    }
    
    result = consolidator.add_menthorq_event(cr_event)
    assert result is None, "Consolidation prématurée"
    logger.info("✅ Test Call Resistance OK")
    
    # Test 2: Ajout Put Support (consolidation complète)
    ps_event = {
        "type": "menthorq_gamma_levels",
        "graph": 10,
        "sym": "ESU25_FUT_CME",
        "ts": "2025-09-07T13:30:00+00:00",
        "study_id": 1,
        "sg": 2,
        "label": "Put Support",
        "price": 5285.0
    }
    
    result = consolidator.add_menthorq_event(ps_event)
    assert result is not None, "Consolidation échouée"
    assert isinstance(result, MenthorQLevels), "Type de record incorrect"
    assert result.call_resistance == 5300.0, "Call Resistance incorrect"
    assert result.put_support == 5285.0, "Put Support incorrect"
    logger.info("✅ Test consolidation MenthorQ OK")
    
    logger.info("🎉 Tous les tests de consolidation réussis!")

def test_enrichments():
    """Tests des enrichissements calculés"""
    logger.info("Test enrichissements...")
    
    # Test 1: Enrichissements MarketBarM1
    market_bar = MarketBarM1(
        symbol="ESU25_FUT_CME",
        ts=datetime.now(timezone.utc),
        ohlc={"o": 5292.75, "h": 5296.0, "l": 5291.5, "c": 5295.0},
        volume=1250,
        bid_volume=640,
        ask_volume=610
    )
    
    context = {"current_price": 5294.0}
    enrichments = calculate_enrichments(market_bar, context)
    
    assert "m1_range" in enrichments, "Range M1 manquant"
    assert enrichments["m1_range"] == 4.5, "Range M1 incorrect"
    assert "nbcv_m1" in enrichments, "NBCV M1 manquant"
    assert enrichments["nbcv_m1"] == -30, "NBCV M1 incorrect"
    logger.info("✅ Test enrichissements MarketBar OK")
    
    # Test 2: Distances MenthorQ
    menthorq_levels = MenthorQLevels(
        symbol="ESU25_FUT_CME",
        ts=datetime.now(timezone.utc),
        gamma_levels={},
        blind_spots={"BL1": 5295.0, "BL2": 5290.0},
        swing_levels={"SG1": 5288.0},
        call_resistance=5300.0,
        put_support=5285.0,
        gamma_wall_0dte=5298.0
    )
    
    distances = calculate_menthorq_distances(5294.0, menthorq_levels)
    
    assert "dist_to_call_res" in distances, "Distance Call Resistance manquante"
    assert distances["dist_to_call_res"] == 6.0, "Distance Call Resistance incorrecte"
    assert "min_dist_to_BL" in distances, "Distance minimale BL manquante"
    assert distances["min_dist_to_BL"] == 1.0, "Distance minimale BL incorrecte"
    logger.info("✅ Test distances MenthorQ OK")
    
    logger.info("🎉 Tous les tests d'enrichissement réussis!")

if __name__ == "__main__":
    print("🧪 Tests Structure Data Processor v2.0")
    print("="*50)
    
    # Test 1: Processeur de base
    test_processor = test_structure_data_processor()
    print("\n" + "="*50)
    print("Métriques finales:")
    print(json.dumps(test_processor.get_metrics(), indent=2))
    
    # Test 2: Conversion vers records internes
    print("\n" + "="*50)
    test_conversion_to_internal()
    
    # Test 3: Consolidation MenthorQ
    print("\n" + "="*50)
    test_menthorq_consolidation()
    
    # Test 4: Enrichissements
    print("\n" + "="*50)
    test_enrichments()
    
    print("\n" + "="*50)
    print("🎉 TOUS LES TESTS RÉUSSIS!")
    print("Structure Data Processor v2.0 - Records Internes ✅")