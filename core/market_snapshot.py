#!/usr/bin/env python3
"""
🎯 MARKET SNAPSHOT UNIFIED - MIA_IA_SYSTEM
==========================================

Assembleur de snapshot de marché unifié en mémoire à partir du flux mia_unified_YYYYMMDD.jsonl
(Charts 3/4/8/10), prêt à être consommé par les analyzers (Battle Navale, Patterns, Confluence, Risk Manager).

FONCTIONNALITÉS:
- Structure unifiée par symbole (m1/m30/vix/menthorq)
- Mise à jour incrémentale via apply_event()
- API minimale: get(), as_features()
- Gestion stale flags et buffers limités
- Dérivés utiles (m30_range, atr_proxy, spread_avg, etc.)
- Intégration session_analyzer, menthorq_battle_navale, patterns_detector
"""

import time
import json
import numpy as np
from typing import Optional, Dict, Any, List, Callable
from dataclasses import dataclass, field
from collections import deque
from datetime import datetime, timezone
from core.logger import get_logger
from config.menthorq_runtime import get_menthorq_config

logger = get_logger(__name__)

# === STRUCTURES DE DONNÉES ===

@dataclass
class OHLCVBar:
    """Barre OHLCV standard"""
    timestamp: float
    open: float
    high: float
    low: float
    close: float
    volume: int
    bid_volume: int = 0
    ask_volume: int = 0

@dataclass
class VWAPBands:
    """Bandes VWAP"""
    vwap: float
    upper1: float
    lower1: float
    upper2: float
    lower2: float

@dataclass
class NBCVData:
    """Net Buying vs Selling Volume"""
    delta: int
    cum_delta: int
    trades_count: int
    last_update: float

@dataclass
class VolumeProfileData:
    """Volume Profile / VPOC / VAH / VAL"""
    vpoc: float
    vah: float
    val: float
    pval: Optional[float] = None
    session_id: str = ""

@dataclass
class TimeAndSalesData:
    """Time & Sales lite"""
    last_trade_price: float
    last_trade_size: int
    last_trade_time: float
    spread_avg: float = 0.0

@dataclass
class DOMData:
    """DOM synthétique"""
    bid_levels: List[Dict[str, float]]
    ask_levels: List[Dict[str, float]]
    last_update: float

@dataclass
class M1Data:
    """Données 1-minute (Graph 3)"""
    current_bar: OHLCVBar
    bars_history: List[OHLCVBar] = field(default_factory=list)
    vwap: float = 0.0
    vwap_bands: Optional[VWAPBands] = None
    nbcv: Optional[NBCVData] = None
    vp: Optional[VolumeProfileData] = None
    ts_lite: Optional[TimeAndSalesData] = None

@dataclass
class M30Data:
    """Données 30-minute (Graph 4)"""
    current_bar: OHLCVBar
    bars_history: List[OHLCVBar] = field(default_factory=list)
    vwap_current: float = 0.0
    vwap_previous: float = 0.0
    nbcv_m30: Optional[NBCVData] = None
    dom_synthetic: Optional[DOMData] = None

@dataclass
class VIXData:
    """Données VIX (Graph 8)"""
    last_value: float
    timestamp: float
    regime: str = "MID"  # LOW, MID, HIGH
    policy: str = "normal"  # normal, elevated, extreme

@dataclass
class GammaData:
    """Données Gamma MenthorQ"""
    call_resistance: Optional[float] = None
    put_support: Optional[float] = None
    gamma_wall_0dte: Optional[float] = None
    hvl: Optional[float] = None
    gex_levels: List[float] = field(default_factory=list)

@dataclass
class BlindSpotsData:
    """Données Blind Spots MenthorQ"""
    blind_spots: List[float] = field(default_factory=list)
    violations: List[float] = field(default_factory=list)

@dataclass
class SwingData:
    """Données Swing Levels MenthorQ"""
    swing_levels: List[float] = field(default_factory=list)
    major_levels: List[float] = field(default_factory=list)

@dataclass
class MenthorQData:
    """Données MenthorQ (Graph 10)"""
    gamma: GammaData = field(default_factory=GammaData)
    blind_spots: BlindSpotsData = field(default_factory=BlindSpotsData)
    swing: SwingData = field(default_factory=SwingData)
    last_update: float = 0.0
    stale: bool = False

@dataclass
class MarketSnapshotUnified:
    """Snapshot unifié du marché par symbole"""
    symbol: str
    session_id: str
    tick_size: float
    file_pos: int
    ts_last_event: float
    
    # Sections de données
    m1: Optional[M1Data] = None
    m30: Optional[M30Data] = None
    vix: Optional[VIXData] = None
    menthorq: Optional[MenthorQData] = None
    
    # Dérivés calculés
    m30_range: float = 0.0
    atr_proxy: float = 0.0
    spread_avg: float = 0.0
    oflow_speed: float = 0.0
    vwap_distance: float = 0.0
    pos_vs_vwap: str = "unknown"

# === GESTIONNAIRE PRINCIPAL ===

class MarketSnapshotManager:
    """Gestionnaire de snapshots de marché unifiés"""
    
    def __init__(self):
        self.snapshots: Dict[str, MarketSnapshotUnified] = {}
        self.volatility_calc: Dict[str, VolatilityCalculator] = {}
        self.config = get_menthorq_config()
        
        logger.info("📊 MarketSnapshotManager initialisé")
    
    def apply_event(self, event: Dict[str, Any]) -> None:
        """Met à jour le snapshot avec un événement du flux JSONL"""
        try:
            # Extraire métadonnées
            symbol = event.get("sym", "")
            event_type = event.get("type", "")
            graph = event.get("graph", 0)
            timestamp = self._parse_timestamp(event.get("ts", ""))
            
            if not symbol or not event_type:
                logger.debug(f"Événement ignoré - symbol ou type manquant: {event}")
                return
            
            # Créer/obtenir snapshot pour ce symbole
            if symbol not in self.snapshots:
                self.snapshots[symbol] = self._create_empty_snapshot(symbol)
                self.volatility_calc[symbol] = VolatilityCalculator()
            
            snapshot = self.snapshots[symbol]
            snapshot.ts_last_event = timestamp
            snapshot.file_pos += 1
            
            # Router vers la bonne section
            if event_type == "basedata":
                self._process_basedata_event(event, snapshot)
            elif event_type == "vix":
                self._process_vix_event(event, snapshot)
            elif "menthorq" in event_type:
                self._process_menthorq_event(event, snapshot)
            elif event_type == "vwap":
                self._process_vwap_event(event, snapshot)
            elif event_type == "vva":
                self._process_vva_event(event, snapshot)
            elif event_type in ["quote", "trade"]:
                self._process_quote_trade_event(event, snapshot)
            
            # Calculer dérivés
            self._calculate_derived_metrics(snapshot)
            
            # Mettre à jour stale flags
            self._update_stale_flags(snapshot)
            
        except Exception as e:
            logger.error(f"Erreur traitement événement: {e} - {event}")
    
    def get(self, symbol: str) -> Optional[MarketSnapshotUnified]:
        """Retourne le snapshot complet pour un symbole"""
        return self.snapshots.get(symbol)
    
    def as_features(self, symbol: str) -> Dict[str, Any]:
        """Vue légère pour Patterns/Confluence"""
        snapshot = self.snapshots.get(symbol)
        if not snapshot:
            return {}
        
        features = {
            "symbol": symbol,
            "timestamp": snapshot.ts_last_event,
            "active_sections": self._get_active_sections(snapshot)
        }
        
        # Features M1
        if snapshot.m1:
            features.update({
                "m1_price": snapshot.m1.current_bar.close,
                "m1_volume": snapshot.m1.current_bar.volume,
                "m1_vwap": snapshot.m1.vwap,
                "m1_vwap_distance": snapshot.vwap_distance,
                "m1_pos_vs_vwap": snapshot.pos_vs_vwap,
                "m1_spread_avg": snapshot.spread_avg,
                "m1_oflow_speed": snapshot.oflow_speed
            })
        
        # Features M30
        if snapshot.m30:
            features.update({
                "m30_price": snapshot.m30.current_bar.close,
                "m30_range": snapshot.m30_range,
                "m30_atr_proxy": snapshot.atr_proxy
            })
        
        # Features VIX
        if snapshot.vix:
            features.update({
                "vix_value": snapshot.vix.last_value,
                "vix_regime": snapshot.vix.regime,
                "vix_policy": snapshot.vix.policy
            })
        
        # Features MenthorQ
        if snapshot.menthorq:
            features.update({
                "menthorq_stale": snapshot.menthorq.stale,
                "gamma_call_resistance": snapshot.menthorq.gamma.call_resistance,
                "gamma_put_support": snapshot.menthorq.gamma.put_support,
                "gamma_wall_0dte": snapshot.menthorq.gamma.gamma_wall_0dte,
                "blind_spots_count": len(snapshot.menthorq.blind_spots.blind_spots)
            })
        
        return features
    
    def get_stale_symbols(self) -> List[str]:
        """Retourne les symboles avec données stale"""
        stale_symbols = []
        for symbol, snapshot in self.snapshots.items():
            if snapshot.menthorq and snapshot.menthorq.stale:
                stale_symbols.append(symbol)
        return stale_symbols
    
    def get_active_sections(self, symbol: str) -> Dict[str, bool]:
        """Retourne quelles sections sont actives (3/4/8/10)"""
        snapshot = self.snapshots.get(symbol)
        if not snapshot:
            return {"m1": False, "m30": False, "vix": False, "menthorq": False}
        
        return {
            "m1": snapshot.m1 is not None,
            "m30": snapshot.m30 is not None,
            "vix": snapshot.vix is not None,
            "menthorq": snapshot.menthorq is not None
        }
    
    # === MÉTHODES PRIVÉES ===
    
    def _create_empty_snapshot(self, symbol: str) -> MarketSnapshotUnified:
        """Crée un snapshot vide pour un symbole"""
        return MarketSnapshotUnified(
            symbol=symbol,
            session_id=f"session_{int(time.time())}",
            tick_size=0.25 if "ES" in symbol else 0.5,  # ES=0.25, NQ=0.5
            file_pos=0,
            ts_last_event=0.0
        )
    
    def _parse_timestamp(self, ts_str: str) -> float:
        """Parse timestamp ISO en float"""
        try:
            if isinstance(ts_str, (int, float)):
                return float(ts_str)
            
            # Format ISO: 2025-09-07T13:30:00+00:00
            dt = datetime.fromisoformat(ts_str.replace('Z', '+00:00'))
            return dt.timestamp()
        except:
            return time.time()
    
    def _process_basedata_event(self, event: Dict, snapshot: MarketSnapshotUnified):
        """Traite un événement basedata (Graph 3 ou 4)"""
        graph = event.get("graph", 0)
        
        # Créer barre OHLCV
        bar = OHLCVBar(
            timestamp=self._parse_timestamp(event.get("ts", "")),
            open=event.get("o", 0.0),
            high=event.get("h", 0.0),
            low=event.get("l", 0.0),
            close=event.get("c", 0.0),
            volume=event.get("v", 0),
            bid_volume=event.get("bidvol", 0),
            ask_volume=event.get("askvol", 0)
        )
        
        if graph == 3:  # M1
            if not snapshot.m1:
                snapshot.m1 = M1Data(current_bar=bar)
            else:
                snapshot.m1.current_bar = bar
                snapshot.m1.bars_history.append(bar)
                # Limiter à 300 barres
                if len(snapshot.m1.bars_history) > 300:
                    snapshot.m1.bars_history = snapshot.m1.bars_history[-300:]
        
        elif graph == 4:  # M30
            if not snapshot.m30:
                snapshot.m30 = M30Data(current_bar=bar)
            else:
                snapshot.m30.current_bar = bar
                snapshot.m30.bars_history.append(bar)
                # Limiter à 96 barres
                if len(snapshot.m30.bars_history) > 96:
                    snapshot.m30.bars_history = snapshot.m30.bars_history[-96:]
    
    def _process_vix_event(self, event: Dict, snapshot: MarketSnapshotUnified):
        """Traite un événement VIX (Graph 8)"""
        vix_value = event.get("last", 0.0)
        regime = self._determine_vix_regime(vix_value)
        policy = self._determine_vix_policy(vix_value)
        
        snapshot.vix = VIXData(
            last_value=vix_value,
            timestamp=self._parse_timestamp(event.get("ts", "")),
            regime=regime,
            policy=policy
        )
    
    def _process_menthorq_event(self, event: Dict, snapshot: MarketSnapshotUnified):
        """Traite un événement MenthorQ (Graph 10)"""
        if not snapshot.menthorq:
            snapshot.menthorq = MenthorQData()
        
        event_type = event.get("type", "")
        sg = event.get("sg", 0)
        price = event.get("price", 0.0)
        label = event.get("label", "")
        
        if "gamma_levels" in event_type:
            self._update_gamma_data(sg, price, label, snapshot.menthorq.gamma)
        elif "blind_spots" in event_type:
            self._update_blind_spots_data(sg, price, label, snapshot.menthorq.blind_spots)
        elif "swing_levels" in event_type:
            self._update_swing_data(sg, price, label, snapshot.menthorq.swing)
        
        # Marquer comme non-stale
        snapshot.menthorq.stale = False
        snapshot.menthorq.last_update = self._parse_timestamp(event.get("ts", ""))
    
    def _process_vwap_event(self, event: Dict, snapshot: MarketSnapshotUnified):
        """Traite un événement VWAP"""
        graph = event.get("graph", 0)
        vwap_value = event.get("v", 0.0)
        
        if graph == 3 and snapshot.m1:  # M1 VWAP
            snapshot.m1.vwap = vwap_value
            snapshot.m1.vwap_bands = VWAPBands(
                vwap=vwap_value,
                upper1=event.get("up1", vwap_value),
                lower1=event.get("dn1", vwap_value),
                upper2=event.get("up2", vwap_value),
                lower2=event.get("dn2", vwap_value)
            )
        elif graph == 4 and snapshot.m30:  # M30 VWAP
            snapshot.m30.vwap_previous = snapshot.m30.vwap_current
            snapshot.m30.vwap_current = vwap_value
    
    def _process_vva_event(self, event: Dict, snapshot: MarketSnapshotUnified):
        """Traite un événement VVA (Volume Profile)"""
        if snapshot.m1:
            snapshot.m1.vp = VolumeProfileData(
                vpoc=event.get("vpoc", 0.0),
                vah=event.get("vah", 0.0),
                val=event.get("val", 0.0),
                pval=event.get("pval"),
                session_id=event.get("id_curr", "")
            )
    
    def _process_quote_trade_event(self, event: Dict, snapshot: MarketSnapshotUnified):
        """Traite événements quote/trade pour T&S lite"""
        if snapshot.m1:
            if not snapshot.m1.ts_lite:
                snapshot.m1.ts_lite = TimeAndSalesData(
                    last_trade_price=0.0,
                    last_trade_size=0,
                    last_trade_time=0.0
                )
            
            if event.get("type") == "trade":
                snapshot.m1.ts_lite.last_trade_price = event.get("price", 0.0)
                snapshot.m1.ts_lite.last_trade_size = event.get("qty", 0)
                snapshot.m1.ts_lite.last_trade_time = self._parse_timestamp(event.get("ts", ""))
            elif event.get("type") == "quote":
                bid = event.get("bid", 0.0)
                ask = event.get("ask", 0.0)
                if bid > 0 and ask > 0:
                    snapshot.m1.ts_lite.spread_avg = ask - bid
    
    def _update_gamma_data(self, sg: int, price: float, label: str, gamma: GammaData):
        """Met à jour les données gamma"""
        if sg == 1 and "Call Resistance" in label:
            gamma.call_resistance = price
        elif sg == 2 and "Put Support" in label:
            gamma.put_support = price
        elif sg == 9 and "Gamma Wall" in label:
            gamma.gamma_wall_0dte = price
        elif sg == 3 and "HVL" in label:
            gamma.hvl = price
        elif sg >= 4 and sg <= 8:  # GEX levels
            if len(gamma.gex_levels) < 10:
                gamma.gex_levels.append(price)
    
    def _update_blind_spots_data(self, sg: int, price: float, label: str, blind_spots: BlindSpotsData):
        """Met à jour les blind spots"""
        if "BL" in label and sg <= 10:
            if len(blind_spots.blind_spots) < 10:
                blind_spots.blind_spots.append(price)
    
    def _update_swing_data(self, sg: int, price: float, label: str, swing: SwingData):
        """Met à jour les swing levels"""
        if "SG" in label and sg <= 9:
            if len(swing.swing_levels) < 9:
                swing.swing_levels.append(price)
    
    def _determine_vix_regime(self, vix_value: float) -> str:
        """Détermine le régime VIX"""
        if vix_value < 15:
            return "LOW"
        elif vix_value < 25:
            return "MID"
        else:
            return "HIGH"
    
    def _determine_vix_policy(self, vix_value: float) -> str:
        """Détermine la politique VIX"""
        return self.config.get_vix_policy(vix_value)
    
    def _calculate_derived_metrics(self, snapshot: MarketSnapshotUnified):
        """Calcule les métriques dérivées"""
        # m30_range
        if snapshot.m30 and len(snapshot.m30.bars_history) >= 2:
            recent_bars = snapshot.m30.bars_history[-5:]
            highs = [bar.high for bar in recent_bars]
            lows = [bar.low for bar in recent_bars]
            snapshot.m30_range = max(highs) - min(lows)
        
        # atr_proxy (simple range EMA)
        if snapshot.m1 and len(snapshot.m1.bars_history) >= 2:
            snapshot.atr_proxy = self._calculate_atr_proxy(snapshot.m1.bars_history)
        
        # spread_avg
        if snapshot.m1 and snapshot.m1.ts_lite:
            snapshot.spread_avg = snapshot.m1.ts_lite.spread_avg
        
        # oflow_speed (trades/min)
        if snapshot.m1 and snapshot.m1.nbcv:
            snapshot.oflow_speed = self._calculate_trades_per_minute(snapshot.m1.nbcv)
        
        # vwap_distance & pos_vs_vwap
        if snapshot.m1 and snapshot.m1.vwap:
            current_price = snapshot.m1.current_bar.close
            snapshot.vwap_distance = abs(current_price - snapshot.m1.vwap)
            snapshot.pos_vs_vwap = "above" if current_price > snapshot.m1.vwap else "below"
    
    def _calculate_atr_proxy(self, bars: List[OHLCVBar]) -> float:
        """Calcule ATR proxy simple"""
        if len(bars) < 2:
            return 0.0
        
        ranges = []
        for bar in bars[-14:]:  # 14 périodes
            ranges.append(bar.high - bar.low)
        
        return np.mean(ranges) if ranges else 0.0
    
    def _calculate_trades_per_minute(self, nbcv: NBCVData) -> float:
        """Calcule trades par minute"""
        if nbcv.trades_count == 0:
            return 0.0
        
        time_elapsed = time.time() - nbcv.last_update
        if time_elapsed <= 0:
            return 0.0
        
        return (nbcv.trades_count * 60) / time_elapsed
    
    def _update_stale_flags(self, snapshot: MarketSnapshotUnified):
        """Met à jour les flags stale basés sur l'âge des données"""
        now = time.time()
        
        # MenthorQ stale (2x période selon runtime)
        if snapshot.menthorq:
            vix_value = snapshot.vix.last_value if snapshot.vix else 20.0
            expected_interval = self.config.get_update_interval(vix_value)
            stale_threshold = expected_interval * 2 * 60  # en secondes
            
            if now - snapshot.menthorq.last_update > stale_threshold:
                snapshot.menthorq.stale = True
                logger.warning(f"MenthorQ stale pour {snapshot.symbol} - {stale_threshold/60:.1f}min sans update")
    
    def _get_active_sections(self, snapshot: MarketSnapshotUnified) -> Dict[str, bool]:
        """Retourne les sections actives"""
        return {
            "m1": snapshot.m1 is not None,
            "m30": snapshot.m30 is not None,
            "vix": snapshot.vix is not None,
            "menthorq": snapshot.menthorq is not None
        }

# === CALCULATEUR DE VOLATILITÉ (CONSERVÉ) ===

class VolatilityCalculator:
    """Calculateur de volatilité avec EWMA (conservé pour compatibilité)"""
    
    def __init__(self, alpha_5s: float = 0.3, alpha_1m: float = 0.2):
        self.alpha_5s = alpha_5s
        self.alpha_1m = alpha_1m
        
        # Historiques pour calculs
        self.price_history: deque = deque(maxlen=100)
        self.returns_5s: deque = deque(maxlen=20)
        self.returns_1m: deque = deque(maxlen=60)
        
        # EWMA states
        self.ewma_5s = 0.0
        self.ewma_1m = 0.0
        self.ewma_var_5s = 0.0
        self.ewma_var_1m = 0.0
        
        # Flash move tracking
        self.last_price_3s = None
        self.last_update_3s = time.time()
    
    def update_price(self, price: float, volume: int = 0) -> None:
        """Met à jour les calculs avec un nouveau prix"""
        current_time = time.time()
        
        # Ajouter à l'historique
        self.price_history.append({
            'price': price,
            'timestamp': current_time,
            'volume': volume
        })
        
        # Calculer returns 5s (si assez de données)
        if len(self.price_history) >= 2:
            time_diff = current_time - self.price_history[-2]['timestamp']
            if time_diff >= 4.5 and time_diff <= 5.5:  # ~5s
                ret_5s = (price - self.price_history[-2]['price']) / self.price_history[-2]['price']
                self.returns_5s.append(ret_5s)
                self._update_ewma_5s(ret_5s)
        
        # Calculer returns 1m (si assez de données)
        if len(self.price_history) >= 12:
            time_diff = current_time - self.price_history[-12]['timestamp']
            if time_diff >= 55 and time_diff <= 65:  # ~1m
                ret_1m = (price - self.price_history[-12]['price']) / self.price_history[-12]['price']
                self.returns_1m.append(ret_1m)
                self._update_ewma_1m(ret_1m)
        
        # Flash move 3s
        if self.last_price_3s is not None:
            time_diff = current_time - self.last_update_3s
            if time_diff >= 2.5 and time_diff <= 3.5:  # ~3s
                self.last_price_3s = price
                self.last_update_3s = current_time
    
    def _update_ewma_5s(self, return_value: float) -> None:
        """Met à jour EWMA 5s"""
        self.ewma_5s = self.alpha_5s * return_value + (1 - self.alpha_5s) * self.ewma_5s
        self.ewma_var_5s = self.alpha_5s * (return_value - self.ewma_5s) ** 2 + (1 - self.alpha_5s) * self.ewma_var_5s
    
    def _update_ewma_1m(self, return_value: float) -> None:
        """Met à jour EWMA 1m"""
        self.ewma_1m = self.alpha_1m * return_value + (1 - self.alpha_1m) * self.ewma_1m
        self.ewma_var_1m = self.alpha_1m * (return_value - self.ewma_1m) ** 2 + (1 - self.alpha_1m) * self.ewma_var_1m
    
    def get_volatility_metrics(self) -> Dict[str, float]:
        """Retourne les métriques de volatilité actuelles"""
        ret_5s_sigma = np.sqrt(self.ewma_var_5s) if self.ewma_var_5s > 0 else 0.0
        ret_1m_sigma = np.sqrt(self.ewma_var_1m) if self.ewma_var_1m > 0 else 0.0
        
        # Flash move 3s
        move_ticks_3s = 0
        if self.last_price_3s is not None and len(self.price_history) > 0:
            current_price = self.price_history[-1]['price']
            move_ticks_3s = int(abs(current_price - self.last_price_3s) / 0.25)  # ES tick size
        
        return {
            'ret_5s_sigma': ret_5s_sigma,
            'ret_1m_sigma': ret_1m_sigma,
            'move_ticks_3s': move_ticks_3s,
            'ewma_5s': self.ewma_5s,
            'ewma_1m': self.ewma_1m
        }

# === INSTANCE GLOBALE ===

# Instance globale du gestionnaire
market_snapshot_manager = MarketSnapshotManager()

def get_market_snapshot_manager() -> MarketSnapshotManager:
    """Retourne l'instance globale du gestionnaire"""
    return market_snapshot_manager

# === FONCTIONS DE COMPATIBILITÉ (LEGACY) ===

def create_volatility_calculator() -> VolatilityCalculator:
    """Factory pour créer un calculateur de volatilité (legacy)"""
    return VolatilityCalculator()

