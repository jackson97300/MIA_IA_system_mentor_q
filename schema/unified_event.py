"""
Schémas Pydantic pour les événements unifiés MIA_IA_SYSTEM
==========================================================

Validation stricte des données JSONL du système unifié.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any, Literal, Union
from pydantic import BaseModel, Field, field_validator, model_validator
from enum import Enum


class ChartType(str, Enum):
    """Types de charts Sierra"""
    CHART_3 = "3"  # 1 minute
    CHART_4 = "4"  # 30 minutes
    CHART_8 = "8"  # VIX
    CHART_10 = "10"  # MenthorQ


class EventType(str, Enum):
    """Types d'événements"""
    BASEDATA = "basedata"
    VWAP = "vwap"
    VVA = "vva"
    VAP = "vap"
    DEPTH = "depth"
    TRADE = "trade"
    QUOTE = "quote"
    VIX = "vix"
    MENTHORQ_GAMMA_LEVELS = "menthorq_gamma_levels"
    MENTHORQ_BLIND_SPOTS = "menthorq_blind_spots"
    MENTHORQ_SWING_LEVELS = "menthorq_swing_levels"


class SymbolType(str, Enum):
    """Types de symboles"""
    ES_FUTURE = "ESU25_FUT_CME"
    NQ_FUTURE = "NQU25_FUT_CME"
    VIX_INDEX = "VIX"


class MenthorQGammaLevel(BaseModel):
    """Niveau gamma MenthorQ"""
    label: str = Field(..., description="Label du niveau (ex: SG1, SG2, etc.)")
    price: float = Field(..., description="Prix du niveau")
    type: Literal["CALL", "PUT"] = Field(..., description="Type d'option")
    strength: Optional[float] = Field(None, description="Force du niveau (0-1)")
    distance_ticks: Optional[int] = Field(None, description="Distance en ticks")


class MenthorQBlindSpot(BaseModel):
    """Blind spot MenthorQ"""
    label: str = Field(..., description="Label du blind spot (ex: BL1, BL2, etc.)")
    price: float = Field(..., description="Prix du blind spot")
    type: Literal["SUPPORT", "RESISTANCE"] = Field(..., description="Type de niveau")
    strength: Optional[float] = Field(None, description="Force du niveau (0-1)")
    distance_ticks: Optional[int] = Field(None, description="Distance en ticks")


class MenthorQSwingLevel(BaseModel):
    """Swing level MenthorQ"""
    label: str = Field(..., description="Label du swing (ex: SG1, SG2, etc.)")
    price: float = Field(..., description="Prix du swing")
    type: Literal["HIGH", "LOW"] = Field(..., description="Type de swing")
    strength: Optional[float] = Field(None, description="Force du niveau (0-1)")
    distance_ticks: Optional[int] = Field(None, description="Distance en ticks")


class BaseDataEvent(BaseModel):
    """Événement de données de base (OHLCV)"""
    ts: datetime = Field(..., description="Timestamp")
    sym: SymbolType = Field(..., description="Symbole")
    chart: ChartType = Field(..., description="Numéro de chart")
    type: Literal["basedata"] = Field("basedata", description="Type d'événement")
    open: float = Field(..., description="Prix d'ouverture")
    high: float = Field(..., description="Prix le plus haut")
    low: float = Field(..., description="Prix le plus bas")
    close: float = Field(..., description="Prix de clôture")
    volume: int = Field(..., description="Volume")
    
    @field_validator('high')
    @classmethod
    def high_must_be_highest(cls, v, info):
        if 'low' in info.data and v < info.data['low']:
            raise ValueError('High must be >= low')
        return v
    
    @field_validator('low')
    @classmethod
    def low_must_be_lowest(cls, v, info):
        if 'high' in info.data and v > info.data['high']:
            raise ValueError('Low must be <= high')
        return v


class VWAPEvent(BaseModel):
    """Événement VWAP"""
    ts: datetime = Field(..., description="Timestamp")
    sym: SymbolType = Field(..., description="Symbole")
    chart: ChartType = Field(..., description="Numéro de chart")
    type: Literal["vwap"] = Field("vwap", description="Type d'événement")
    vwap: float = Field(..., description="VWAP")
    volume: int = Field(..., description="Volume")
    sd1_up: Optional[float] = Field(None, description="Standard deviation +1")
    sd1_dn: Optional[float] = Field(None, description="Standard deviation -1")
    sd2_up: Optional[float] = Field(None, description="Standard deviation +2")
    sd2_dn: Optional[float] = Field(None, description="Standard deviation -2")


class VVAEvent(BaseModel):
    """Événement VVA (Volume-Weighted Average)"""
    ts: datetime = Field(..., description="Timestamp")
    sym: SymbolType = Field(..., description="Symbole")
    chart: ChartType = Field(..., description="Numéro de chart")
    type: Literal["vva"] = Field("vva", description="Type d'événement")
    vva: float = Field(..., description="VVA")
    volume: int = Field(..., description="Volume")


class VAPEvent(BaseModel):
    """Événement VAP (Volume-Weighted Average Price)"""
    ts: datetime = Field(..., description="Timestamp")
    sym: SymbolType = Field(..., description="Symbole")
    chart: ChartType = Field(..., description="Numéro de chart")
    type: Literal["vap"] = Field("vap", description="Type d'événement")
    vap: float = Field(..., description="VAP")
    volume: int = Field(..., description="Volume")


class DepthEvent(BaseModel):
    """Événement de profondeur du carnet d'ordres"""
    ts: datetime = Field(..., description="Timestamp")
    sym: SymbolType = Field(..., description="Symbole")
    chart: ChartType = Field(..., description="Numéro de chart")
    type: Literal["depth"] = Field("depth", description="Type d'événement")
    bids: List[Dict[str, Union[float, int]]] = Field(..., description="Ordres d'achat")
    asks: List[Dict[str, Union[float, int]]] = Field(..., description="Ordres de vente")
    
    @field_validator('bids', 'asks')
    @classmethod
    def validate_price_levels(cls, v):
        for level in v:
            if 'price' not in level or 'size' not in level:
                raise ValueError('Each price level must have price and size')
            if level['price'] <= 0:
                raise ValueError('Price must be positive')
            if level['size'] < 0:
                raise ValueError('Size must be non-negative')
        return v


class TradeEvent(BaseModel):
    """Événement de trade"""
    ts: datetime = Field(..., description="Timestamp")
    sym: SymbolType = Field(..., description="Symbole")
    chart: ChartType = Field(..., description="Numéro de chart")
    type: Literal["trade"] = Field("trade", description="Type d'événement")
    price: float = Field(..., description="Prix du trade")
    size: int = Field(..., description="Taille du trade")
    side: Optional[Literal["BUY", "SELL"]] = Field(None, description="Côté du trade")
    trade_id: Optional[str] = Field(None, description="ID du trade")


class QuoteEvent(BaseModel):
    """Événement de cotation"""
    ts: datetime = Field(..., description="Timestamp")
    sym: SymbolType = Field(..., description="Symbole")
    chart: ChartType = Field(..., description="Numéro de chart")
    type: Literal["quote"] = Field("quote", description="Type d'événement")
    bid: float = Field(..., description="Prix d'achat")
    ask: float = Field(..., description="Prix de vente")
    bid_size: int = Field(..., description="Taille d'achat")
    ask_size: int = Field(..., description="Taille de vente")
    
    @field_validator('ask')
    @classmethod
    def ask_must_be_higher_than_bid(cls, v, info):
        if 'bid' in info.data and v <= info.data['bid']:
            raise ValueError('Ask must be > bid')
        return v


class VIXEvent(BaseModel):
    """Événement VIX"""
    ts: datetime = Field(..., description="Timestamp")
    sym: Literal["VIX"] = Field("VIX", description="Symbole VIX")
    chart: Literal["8"] = Field("8", description="Chart VIX")
    type: Literal["vix"] = Field("vix", description="Type d'événement")
    last: float = Field(..., description="Dernière valeur VIX")
    policy: Literal["normal", "high", "low"] = Field(..., description="Politique VIX")
    
    @field_validator('last')
    @classmethod
    def vix_must_be_positive(cls, v):
        if v < 0:
            raise ValueError('VIX must be positive')
        return v


class MenthorQEvent(BaseModel):
    """Événement MenthorQ générique"""
    ts: datetime = Field(..., description="Timestamp")
    sym: SymbolType = Field(..., description="Symbole")
    chart: Literal["10"] = Field("10", description="Chart MenthorQ")
    type: Union[
        Literal["menthorq_gamma_levels"],
        Literal["menthorq_blind_spots"],
        Literal["menthorq_swing_levels"]
    ] = Field(..., description="Type d'événement MenthorQ")
    levels: List[Union[MenthorQGammaLevel, MenthorQBlindSpot, MenthorQSwingLevel]] = Field(
        ..., description="Liste des niveaux"
    )


# Union de tous les types d'événements
UnifiedEvent = Union[
    BaseDataEvent,
    VWAPEvent,
    VVAEvent,
    VAPEvent,
    DepthEvent,
    TradeEvent,
    QuoteEvent,
    VIXEvent,
    MenthorQEvent,
]


def validate_unified_event(data: Dict[str, Any]) -> UnifiedEvent:
    """
    Valide un événement unifié à partir d'un dictionnaire.
    
    Args:
        data: Dictionnaire contenant les données de l'événement
        
    Returns:
        Événement validé
        
    Raises:
        ValidationError: Si les données ne sont pas valides
    """
    event_type = data.get('type')
    
    if event_type == 'basedata':
        return BaseDataEvent(**data)
    elif event_type == 'vwap':
        return VWAPEvent(**data)
    elif event_type == 'vva':
        return VVAEvent(**data)
    elif event_type == 'vap':
        return VAPEvent(**data)
    elif event_type == 'depth':
        return DepthEvent(**data)
    elif event_type == 'trade':
        return TradeEvent(**data)
    elif event_type == 'quote':
        return QuoteEvent(**data)
    elif event_type == 'vix':
        return VIXEvent(**data)
    elif event_type in ['menthorq_gamma_levels', 'menthorq_blind_spots', 'menthorq_swing_levels']:
        return MenthorQEvent(**data)
    else:
        raise ValueError(f"Type d'événement non reconnu: {event_type}")


def validate_jsonl_line(line: str) -> UnifiedEvent:
    """
    Valide une ligne JSONL du fichier unifié.
    
    Args:
        line: Ligne JSONL
        
    Returns:
        Événement validé
        
    Raises:
        ValidationError: Si la ligne n'est pas valide
    """
    import json
    
    try:
        data = json.loads(line.strip())
        return validate_unified_event(data)
    except json.JSONDecodeError as e:
        raise ValueError(f"Ligne JSON invalide: {e}")
    except Exception as e:
        raise ValueError(f"Erreur de validation: {e}")
