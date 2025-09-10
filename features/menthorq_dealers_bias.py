"""
MIA_IA_SYSTEM - MenthorQ Dealer's Bias Replacement

Remplacement du Dealer's Bias Polygon.io par MenthorQ
- Calcul du Dealer's Bias basé sur les niveaux MenthorQ
- Adaptation des composantes existantes
- Interface compatible avec le système actuel

Version: Replacement Polygon.io
Performance: <5ms pour calcul complet
"""

import json
import math
import os
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum

from core.logger import get_logger
from core.base_types import ES_TICK_SIZE
from features.menthorq_processor import MenthorQProcessor
from features.data_reader import get_latest_market_data, get_menthorq_market_data
from features.config_loader import get_feature_config
from statistics import mean

logger = get_logger(__name__)

# === FONCTIONS UTILITAIRES ===

def clamp(v: float, a: float, b: float) -> float:
    """Clamp une valeur entre a et b"""
    return max(a, min(b, v))

def pct_above_below(levels: List[float], price: float) -> float:
    """Calcule le pourcentage de niveaux au-dessus du prix"""
    if not levels:
        return 0.5  # neutre si pas de GEX
    above = sum(1 for x in levels if x > price)
    below = sum(1 for x in levels if x < price)
    total = above + below
    if total == 0:
        return 0.5
    return above / total  # fraction au-dessus

def nearest_distance_ticks(price: float, levels: List[float], tick: float) -> float:
    """Calcule la distance en ticks au niveau le plus proche"""
    vals = [x for x in levels if x and x > 0]
    if not vals:
        return math.inf
    return min(abs(price - x) / tick for x in vals)

# === TYPES MENTHORQ DEALER'S BIAS ===

class MenthorQBiasDirection(Enum):
    """Direction du bias MenthorQ"""
    BULLISH = "BULLISH"
    BEARISH = "BEARISH"
    NEUTRAL = "NEUTRAL"

class MenthorQBiasStrength(Enum):
    """Force du bias MenthorQ"""
    STRONG = "STRONG"
    MODERATE = "MODERATE"
    WEAK = "WEAK"

@dataclass
class MenthorQDealersBias:
    """Dealer's Bias calculé avec MenthorQ"""
    timestamp: datetime
    symbol: str
    underlying_price: float
    
    # Score principal
    dealers_bias_score: float  # -1 à +1
    
    # Composantes MenthorQ
    gamma_resistance_bias: float
    gamma_support_bias: float
    blind_spots_bias: float
    swing_levels_bias: float
    gex_levels_bias: float
    vix_regime_bias: float
    
    # Niveaux actifs
    active_gamma_levels: List[Dict[str, Any]]
    active_blind_spots: List[Dict[str, Any]]
    active_swing_levels: List[Dict[str, Any]]
    
    # Interprétation
    direction: MenthorQBiasDirection
    strength: MenthorQBiasStrength
    
    # Qualité
    data_age_seconds: int
    quality_score: float

# === MENTHORQ DEALER'S BIAS ANALYZER ===

class MenthorQDealersBiasAnalyzer:
    """
    Analyseur Dealer's Bias basé sur MenthorQ
    
    Remplace Polygon.io avec les niveaux MenthorQ :
    1. Gamma Resistance/Support → Gamma Flip/Pins
    2. Blind Spots → Zones de danger dealers
    3. Swing Levels → Niveaux de retournement
    4. GEX Levels → Gamma Exposure
    5. VIX Regime → Adaptation volatilité
    """
    
    def __init__(self, menthorq_processor: MenthorQProcessor, ema_alpha: float = 0.2):
        """
        Initialisation de l'analyseur
        
        Args:
            menthorq_processor: Processeur MenthorQ
            ema_alpha: Coefficient EMA pour lissage (0.2 = lissage modéré)
        """
        self.menthorq_processor = menthorq_processor
        self.ema_alpha = ema_alpha
        self.last_bias = None  # Pour EMA smoothing
        
        # Configuration des seuils (depuis config/feature_config.json)
        from features.config_loader import get_feature_config
        config = get_feature_config()
        self.gamma_proximity_ticks = config.menthorq.gamma_proximity_ticks
        self.blind_spot_danger_ticks = config.menthorq.blind_spot_proximity_ticks
        self.swing_proximity_ticks = config.menthorq.swing_level_proximity_ticks
        
        # Pondérations (adaptées du système Polygon)
        self.weights = {
            'gamma_resistance': 0.25,  # Équivalent Gamma Flip
            'gamma_support': 0.20,     # Équivalent Gamma Pins
            'blind_spots': 0.20,       # Nouveau - zones de danger
            'swing_levels': 0.15,      # Équivalent PCR contrariant
            'gex_levels': 0.15,        # Équivalent GEX
            'vix_regime': 0.05         # Équivalent VIX Regime
        }
        
        logger.info("MenthorQDealersBiasAnalyzer initialisé")
    
    def dealers_bias_with_menthorq(self, 
                                  price: float, 
                                  vix: float, 
                                  tick_size: float, 
                                  levels: dict,
                                  # pondérations (peuvent être déplacées en config)
                                  W_gamma_res: float = 0.25, 
                                  W_gamma_sup: float = 0.20, 
                                  W_bl: float = 0.20, 
                                  W_swing: float = 0.15, 
                                  W_gex: float = 0.15, 
                                  W_vix: float = 0.05) -> Dict[str, Any]:
        """
        Calcul du Dealer's Bias avec MenthorQ (version plug & play)
        
        levels attendu:
        {
          "gamma": {
            "call_resistance": float|None,
            "call_resistance_0dte": float|None,
            "gamma_wall_0dte": float|None,
            "put_support": float|None,
            "put_support_0dte": float|None,
            "hvl": float|None,
            "hvl_0dte": float|None,
            "gex": {"1": float|None, ..., "10": float|None}
          },
          "blind_spots": {"BL 1": float|None, ..., "BL 10": float|None},
          "swing": {"SG1": float|None, ..., "SG9": float|None}
        }
        """
        
        gamma = levels.get("gamma", {}) or {}
        bls = levels.get("blind_spots", {}) or {}
        swing = levels.get("swing", {}) or {}
        
        # ---------- 1) Gamma Resistance (CallRes + CR 0DTE + GW 0DTE)
        res_levels = [
            gamma.get("call_resistance"),
            gamma.get("call_resistance_0dte"),
            gamma.get("gamma_wall_0dte")
        ]
        res_levels = [x for x in res_levels if x and x > 0]
        if res_levels:
            d_res = nearest_distance_ticks(price, res_levels, tick_size)
            # règle de ta spec
            if d_res <= 10:
                gamma_res = 0.2
            elif price < min(res_levels):  # sous la résistance (bearish)
                gamma_res = 0.3
            else:
                gamma_res = 0.7
        else:
            gamma_res = 0.5  # neutre si pas de data
        
        # ---------- 2) Gamma Support (PutSup + PutSup 0DTE + HVL + HVL 0DTE)
        sup_levels = [
            gamma.get("put_support"),
            gamma.get("put_support_0dte"),
            gamma.get("hvl"),
            gamma.get("hvl_0dte")
        ]
        sup_levels = [x for x in sup_levels if x and x > 0]
        if sup_levels:
            # plus proche support (au-dessus/au-dessous inclus)
            # on regarde directionnellement: si prix > support => bullish
            nearest = min(sup_levels, key=lambda L: abs(price - L))
            d_sup = abs(price - nearest) / tick_size
            if d_sup <= 10:
                gamma_sup = 0.8
            elif price > nearest:
                gamma_sup = 0.7
            else:
                gamma_sup = 0.3
        else:
            gamma_sup = 0.5
        
        # ---------- 3) Blind Spots (BL1..BL10)
        bl_vals = [v for v in bls.values() if v and v > 0]
        if bl_vals:
            d_bl = nearest_distance_ticks(price, bl_vals, tick_size)
            blind_spots = 0.1 if d_bl <= 5 else 0.5
        else:
            blind_spots = 0.5
        
        # ---------- 4) Swing Levels (SG1..SG9)
        sw_vals = [v for v in swing.values() if v and v > 0]
        swing_scores = []
        if sw_vals:
            for lv in sw_vals:
                if abs(price - lv)/tick_size <= 15:
                    swing_scores.append(0.7 if lv < price else 0.3)
            swing_levels = mean(swing_scores) if swing_scores else 0.5
        else:
            swing_levels = 0.5
        
        # ---------- 5) GEX Levels (GEX1..GEX10)
        gex_vals = []
        gex = (gamma.get("gex") or {})
        for k in list(gex.keys()):
            v = gex.get(k)
            if v and v > 0:
                gex_vals.append(v)
        if gex_vals:
            frac_above = pct_above_below(gex_vals, price)  # 0..1
            if frac_above > 0.7:
                gex_levels = 0.3
            elif frac_above < 0.3:
                gex_levels = 0.7
            else:
                gex_levels = 0.5
        else:
            gex_levels = 0.5
        
        # ---------- 6) VIX Regime
        if vix > 25:
            vix_regime = 0.5
        elif vix < 15:
            vix_regime = 0.7
        else:
            vix_regime = 0.5
        
        # ---------- Assemblage
        composite = (
            W_gamma_res * gamma_res +
            W_gamma_sup * gamma_sup +
            W_bl        * blind_spots +
            W_swing     * swing_levels +
            W_gex       * gex_levels +
            W_vix       * vix_regime
        )
        dealers_bias = 2.0 * composite - 1.0  # map [0,1] -> [-1,1]
        dealers_bias = clamp(dealers_bias, -1.0, 1.0)
        
        # EMA smoothing pour éviter les flip-flops
        if self.last_bias is not None:
            dealers_bias = self.ema_alpha * dealers_bias + (1 - self.ema_alpha) * self.last_bias
        self.last_bias = dealers_bias

        return {
            "dealers_bias": dealers_bias,
            "components": {
                "gamma_resistance": gamma_res,
                "gamma_support": gamma_sup,
                "blind_spots": blind_spots,
                "swing_levels": swing_levels,
                "gex_levels": gex_levels,
                "vix_regime": vix_regime,
                "composite_0_1": composite
            }
        }

    def calculate_menthorq_dealers_bias(self, current_price: float, symbol: str = "ESZ5",
                                      vix_level: float = 20.0, use_realtime: bool = False) -> Optional[MenthorQDealersBias]:
        """
        Calcule le Dealer's Bias avec MenthorQ (vraies données)
        
        Args:
            current_price: Prix actuel
            symbol: Symbole à analyser
            vix_level: Niveau VIX
            
        Returns:
            MenthorQDealersBias ou None si erreur
        """
        try:
            # Source: temps réel si explicitement demandé, sinon cache processor (test-safe)
            menthorq_data = None
            if use_realtime or os.getenv("MIA_MQ_USE_REALTIME") == "1":
                try:
                    from features.data_reader import get_latest_market_data
                    real_data = get_latest_market_data("ES")
                    if real_data and real_data.get('menthorq_levels'):
                        menthorq_data = self._convert_real_menthorq_data(real_data['menthorq_levels'])
                        logger.info(f"✅ {len(real_data['menthorq_levels'])} niveaux MenthorQ (realtime)")
                except Exception as e:
                    logger.warning(f"Realtime MenthorQ indisponible: {e}")
            if not menthorq_data:
                menthorq_data = self.menthorq_processor.get_levels(symbol)
                if menthorq_data.get('stale', False):
                    logger.warning("Données MenthorQ obsolètes")
                    return None
            
            # Debug: voir la structure des données
            logger.debug(f"Dealer's Bias Debug - menthorq_data structure: {list(menthorq_data.keys())}")
            logger.debug(f"Dealer's Bias Debug - gamma keys: {list(menthorq_data.get('gamma', {}).keys())}")
            logger.debug(f"Dealer's Bias Debug - blind_spots keys: {list(menthorq_data.get('blind_spots', {}).keys())}")
            
            # Calculer les composantes
            gamma_resistance_bias = self._calculate_gamma_resistance_bias(
                current_price, menthorq_data
            )
            
            gamma_support_bias = self._calculate_gamma_support_bias(
                current_price, menthorq_data
            )
            
            blind_spots_bias = self._calculate_blind_spots_bias(
                current_price, menthorq_data
            )
            
            swing_levels_bias = self._calculate_swing_levels_bias(
                current_price, menthorq_data
            )
            
            gex_levels_bias = self._calculate_gex_levels_bias(
                current_price, menthorq_data
            )
            
            vix_regime_bias = self._calculate_vix_regime_bias(vix_level)
            
            # Score final pondéré
            dealers_bias_score = (
                self.weights['gamma_resistance'] * gamma_resistance_bias +
                self.weights['gamma_support'] * gamma_support_bias +
                self.weights['blind_spots'] * blind_spots_bias +
                self.weights['swing_levels'] * swing_levels_bias +
                self.weights['gex_levels'] * gex_levels_bias +
                self.weights['vix_regime'] * vix_regime_bias
            )
            
            # Normalisation (-1 à +1)
            dealers_bias_normalized = 2 * (dealers_bias_score - 0.5)
            
            # Interprétation
            direction, strength = self._interpret_bias(dealers_bias_normalized)
            
            # Niveaux actifs
            active_gamma = self._get_active_gamma_levels(current_price, menthorq_data)
            active_blind_spots = self._get_active_blind_spots(current_price, menthorq_data)
            active_swing = self._get_active_swing_levels(current_price, menthorq_data)
            
            # Qualité des données
            data_age_seconds = self._calculate_data_age(menthorq_data)
            quality_score = self._calculate_quality_score(menthorq_data, data_age_seconds)
            
            return MenthorQDealersBias(
                timestamp=datetime.now(),
                symbol=symbol,
                underlying_price=current_price,
                dealers_bias_score=dealers_bias_normalized,
                gamma_resistance_bias=gamma_resistance_bias,
                gamma_support_bias=gamma_support_bias,
                blind_spots_bias=blind_spots_bias,
                swing_levels_bias=swing_levels_bias,
                gex_levels_bias=gex_levels_bias,
                vix_regime_bias=vix_regime_bias,
                active_gamma_levels=active_gamma,
                active_blind_spots=active_blind_spots,
                active_swing_levels=active_swing,
                direction=direction,
                strength=strength,
                data_age_seconds=data_age_seconds,
                quality_score=quality_score
            )
            
        except Exception as e:
            logger.error(f"Erreur calcul Dealer's Bias MenthorQ: {e}")
            return None
    
    def _convert_real_menthorq_data(self, menthorq_levels) -> Dict[str, Any]:
        """Convertit les vraies données MenthorQ en format compatible"""
        converted_data = {
            'gamma': {
                'call_resistance': None,
                'put_support': None,
                'hvl': None,
                '1d_min': None,
                '1d_max': None,
                'call_resistance_0dte': None,
                'put_support_0dte': None,
                'hvl_0dte': None,
                'gamma_wall_0dte': None,
                'gex_1': None, 'gex_2': None, 'gex_3': None, 'gex_4': None, 'gex_5': None,
                'gex_6': None, 'gex_7': None, 'gex_8': None, 'gex_9': None, 'gex_10': None
            },
            'blind_spots': {},
            'swing': {},
            'stale': False
        }
        
        # Gérer le cas où menthorq_levels est un dict (nouveau format)
        if isinstance(menthorq_levels, dict):
            # Cas enveloppe: {timestamp, symbol, chart, menthorq_levels: {...}}
            if 'menthorq_levels' in menthorq_levels and isinstance(menthorq_levels['menthorq_levels'], dict):
                menthorq_levels = menthorq_levels['menthorq_levels']
            for level_type, price in menthorq_levels.items():
                # Ignorer les valeurs non numériques
                if not isinstance(price, (int, float)):
                    continue
                if price is not None and price > 0:
                    # Mapping direct depuis le dict vers la structure gamma/blind_spots/swing
                    if 'call_resistance' in level_type:
                        if '0dte' in level_type:
                            converted_data['gamma']['call_resistance_0dte'] = price
                        else:
                            converted_data['gamma']['call_resistance'] = price
                    elif 'put_support' in level_type:
                        if '0dte' in level_type:
                            converted_data['gamma']['put_support_0dte'] = price
                        else:
                            converted_data['gamma']['put_support'] = price
                    elif 'hvl' in level_type:
                        if '0dte' in level_type:
                            converted_data['gamma']['hvl_0dte'] = price
                        else:
                            converted_data['gamma']['hvl'] = price
                    elif 'gamma_wall' in level_type:
                        converted_data['gamma']['gamma_wall_0dte'] = price
                    elif '1d_max' in level_type:
                        converted_data['gamma']['1d_max'] = price
                    elif '1d_min' in level_type:
                        converted_data['gamma']['1d_min'] = price
                    elif 'gex_' in level_type:
                        # Extraire le numéro GEX (ex: gex_1 -> 1)
                        gex_num = level_type.replace('gex_', '')
                        converted_data['gamma'][f'gex_{gex_num}'] = price
                    elif 'blind_spot' in level_type:
                        # Extraire le numéro BL (ex: blind_spot_1 -> BL 1)
                        bl_num = level_type.replace('blind_spot_', '')
                        converted_data['blind_spots'][f'BL {bl_num}'] = price
                    elif 'swing_lvl' in level_type:
                        # Extraire le numéro Swing (ex: swing_lvl_1 -> SG1)
                        swing_num = level_type.replace('swing_lvl_', '')
                        converted_data['swing'][f'SG{swing_num}'] = price
            return converted_data
        
        # Gérer le cas où menthorq_levels est une liste (ancien format)
        for level_data in menthorq_levels:
            # Gérer le cas où level_data est un string (données brutes)
            if isinstance(level_data, str):
                # Parser le string JSON
                try:
                    level_data = json.loads(level_data)
                except json.JSONDecodeError:
                    continue
            
            level_type = level_data.get('level_type', '') if isinstance(level_data, dict) else ''
            price = level_data.get('price', 0.0) if isinstance(level_data, dict) else 0.0
            # Ignorer les valeurs non numériques
            if not isinstance(price, (int, float)):
                continue
            
            # Mapping des types vers la structure gamma/blind_spots/swing
            if 'call_resistance' in level_type:
                if '0dte' in level_type:
                    converted_data['gamma']['call_resistance_0dte'] = price
                else:
                    converted_data['gamma']['call_resistance'] = price
            elif 'put_support' in level_type:
                if '0dte' in level_type:
                    converted_data['gamma']['put_support_0dte'] = price
                else:
                    converted_data['gamma']['put_support'] = price
            elif 'hvl' in level_type:
                if '0dte' in level_type:
                    converted_data['gamma']['hvl_0dte'] = price
                else:
                    converted_data['gamma']['hvl'] = price
            elif 'gamma_wall' in level_type:
                converted_data['gamma']['gamma_wall_0dte'] = price
            elif '1d_min' in level_type:
                converted_data['gamma']['1d_min'] = price
            elif '1d_max' in level_type:
                converted_data['gamma']['1d_max'] = price
            elif 'gex_' in level_type:
                # Extraire le numéro GEX (ex: gex_1 -> 1)
                gex_num = level_type.replace('gex_', '')
                converted_data['gamma'][f'gex_{gex_num}'] = price
            elif 'blind_spot' in level_type:
                # Extraire le numéro BL (ex: blind_spot_1 -> BL 1)
                bl_num = level_type.replace('blind_spot_', '')
                converted_data['blind_spots'][f'BL {bl_num}'] = price
            elif 'swing_lvl' in level_type:
                # Extraire le numéro Swing (ex: swing_lvl_1 -> SG1)
                swing_num = level_type.replace('swing_lvl_', '')
                converted_data['swing'][f'SG{swing_num}'] = price
        
        return converted_data
    
    def _calculate_gamma_resistance_bias(self, current_price: float, 
                                       menthorq_data: Dict[str, Any]) -> float:
        """
        Calcule le bias basé sur les résistances Gamma (équivalent Gamma Flip)
        
        Logique: Prix proche d'une résistance Gamma = bearish (dealers short gamma)
        """
        gamma_levels = menthorq_data.get("gamma", {})
        
        # Chercher les résistances Gamma (noms du fichier C++ corrigé)
        call_resistance = gamma_levels.get("call_resistance", 0)
        call_resistance_0dte = gamma_levels.get("call_resistance_0dte", 0)
        gamma_wall = gamma_levels.get("gamma_wall_0dte", 0)
        
        resistance_levels = [call_resistance, call_resistance_0dte, gamma_wall]
        resistance_levels = [level for level in resistance_levels if level is not None and level > 0]
        
        if not resistance_levels:
            return 0.5  # Neutre
        
        # Trouver la résistance la plus proche
        closest_resistance = min(resistance_levels, 
                               key=lambda x: abs(x - current_price))
        
        distance_ticks = (closest_resistance - current_price) / ES_TICK_SIZE
        
        # Logique: Plus proche de la résistance = plus bearish
        if abs(distance_ticks) <= self.gamma_proximity_ticks:
            # Très proche = bearish (dealers short gamma)
            return 0.2
        elif distance_ticks > 0:
            # Prix sous résistance = bearish
            return 0.3
        else:
            # Prix au-dessus = bullish
            return 0.7
    
    def _calculate_gamma_support_bias(self, current_price: float,
                                    menthorq_data: Dict[str, Any]) -> float:
        """
        Calcule le bias basé sur les supports Gamma (équivalent Gamma Pins)
        
        Logique: Prix proche d'un support Gamma = bullish (dealers long gamma)
        """
        gamma_levels = menthorq_data.get("gamma", {})
        
        # Chercher les supports Gamma (noms du fichier C++ corrigé)
        put_support = gamma_levels.get("put_support", 0)
        put_support_0dte = gamma_levels.get("put_support_0dte", 0)
        hvl = gamma_levels.get("hvl", 0)
        hvl_0dte = gamma_levels.get("hvl_0dte", 0)
        
        support_levels = [put_support, put_support_0dte, hvl, hvl_0dte]
        support_levels = [level for level in support_levels if level is not None and level > 0]
        
        if not support_levels:
            return 0.5  # Neutre
        
        # Trouver le support le plus proche
        closest_support = min(support_levels,
                            key=lambda x: abs(x - current_price))
        
        distance_ticks = (current_price - closest_support) / ES_TICK_SIZE
        
        # Logique: Plus proche du support = plus bullish
        if abs(distance_ticks) <= self.gamma_proximity_ticks:
            # Très proche = bullish (dealers long gamma)
            return 0.8
        elif distance_ticks > 0:
            # Prix au-dessus du support = bullish
            return 0.7
        else:
            # Prix sous support = bearish
            return 0.3
    
    def _calculate_blind_spots_bias(self, current_price: float,
                                  menthorq_data: Dict[str, Any]) -> float:
        """
        Calcule le bias basé sur les Blind Spots (nouveau - zones de danger)
        
        Logique: Prix dans un Blind Spot = très bearish (zones interdites)
        """
        blind_spots = menthorq_data.get("blind_spots", {})
        
        if not blind_spots:
            return 0.5  # Neutre
        
        # Vérifier si on est proche d'un Blind Spot
        for label, price in blind_spots.items():
            if price is not None and price > 0:
                distance_ticks = abs(current_price - price) / ES_TICK_SIZE
                
                if distance_ticks <= self.blind_spot_danger_ticks:
                    # Dans un Blind Spot = très bearish
                    return 0.1
        
        # Pas de Blind Spot proche = neutre
        return 0.5
    
    def _calculate_swing_levels_bias(self, current_price: float,
                                   menthorq_data: Dict[str, Any]) -> float:
        """
        Calcule le bias basé sur les Swing Levels (équivalent PCR contrariant)
        
        Logique: Prix proche d'un Swing Level = signal contrariant
        """
        swing_levels = menthorq_data.get("swing", {})
        
        if not swing_levels:
            return 0.5  # Neutre
        
        # Compter les Swing Levels proches
        nearby_swing_count = 0
        swing_bias_sum = 0.0
        
        for label, price in swing_levels.items():
            if price is not None and price > 0:
                distance_ticks = abs(current_price - price) / ES_TICK_SIZE
                
                if distance_ticks <= self.swing_proximity_ticks:
                    nearby_swing_count += 1
                    
                    # Logique contrariante: Swing Level au-dessus = bearish, en-dessous = bullish
                    if price > current_price:
                        swing_bias_sum += 0.3  # Bearish
                    else:
                        swing_bias_sum += 0.7  # Bullish
        
        if nearby_swing_count == 0:
            return 0.5  # Neutre
        
        # Moyenne des biais contrariants
        return swing_bias_sum / nearby_swing_count
    
    def _calculate_gex_levels_bias(self, current_price: float,
                                 menthorq_data: Dict[str, Any]) -> float:
        """
        Calcule le bias basé sur les niveaux GEX (équivalent GEX)
        
        Logique: Plus de niveaux GEX au-dessus = bearish, en-dessous = bullish
        """
        gamma_levels = menthorq_data.get("gamma", {})
        
        # Debug: voir ce qu'on a dans gamma_levels
        logger.debug(f"GEX Debug - gamma_levels keys: {list(gamma_levels.keys())}")
        logger.debug(f"GEX Debug - gamma_levels values: {[(k, v) for k, v in gamma_levels.items() if v and v > 0]}")
        
        # Compter les niveaux GEX (noms du fichier C++ corrigé)
        gex_levels = []
        for label, price in gamma_levels.items():
            if label.startswith("gex_") and price is not None and price > 0:
                gex_levels.append(price)
                logger.debug(f"GEX Debug - Found GEX level: {label} = {price}")
        
        logger.debug(f"GEX Debug - Total GEX levels found: {len(gex_levels)}")
        
        if not gex_levels:
            logger.debug("GEX Debug - No GEX levels found, returning neutral")
            return 0.5  # Neutre
        
        # Compter les GEX au-dessus et en-dessous
        gex_above = sum(1 for price in gex_levels if price > current_price)
        gex_below = sum(1 for price in gex_levels if price < current_price)
        
        total_gex = len(gex_levels)
        
        if total_gex == 0:
            return 0.5
        
        # Logique: Plus de GEX au-dessus = bearish (résistance)
        gex_ratio = gex_above / total_gex
        
        if gex_ratio > 0.7:
            return 0.3  # Bearish
        elif gex_ratio < 0.3:
            return 0.7  # Bullish
        else:
            return 0.5  # Neutre
    
    def _calculate_vix_regime_bias(self, vix_level: float) -> float:
        """
        Calcule le bias basé sur le régime VIX (identique au système Polygon)
        
        Logique: VIX élevé = neutralisation, VIX bas = amplification
        """
        if vix_level > 25:
            return 0.5  # Stress = neutralisation
        elif vix_level < 15:
            return 0.7  # Calme = amplification bullish
        else:
            return 0.5  # Neutre
    
    def _interpret_bias(self, bias_score: float) -> Tuple[MenthorQBiasDirection, MenthorQBiasStrength]:
        """Interprète le score de bias"""
        
        if abs(bias_score) < 0.15:
            direction = MenthorQBiasDirection.NEUTRAL
            strength = MenthorQBiasStrength.WEAK
        elif abs(bias_score) < 0.45:
            direction = MenthorQBiasDirection.BULLISH if bias_score > 0 else MenthorQBiasDirection.BEARISH
            strength = MenthorQBiasStrength.MODERATE
        else:
            direction = MenthorQBiasDirection.BULLISH if bias_score > 0 else MenthorQBiasDirection.BEARISH
            strength = MenthorQBiasStrength.STRONG
        
        return direction, strength
    
    def _get_active_gamma_levels(self, current_price: float, 
                               menthorq_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Retourne les niveaux Gamma actifs"""
        active_levels = []
        gamma_levels = menthorq_data.get("gamma", {})
        
        for label, price in gamma_levels.items():
            if price is not None and price > 0:
                distance_ticks = abs(current_price - price) / ES_TICK_SIZE
                if distance_ticks <= self.gamma_proximity_ticks:
                    active_levels.append({
                        "label": label,
                        "price": price,
                        "distance_ticks": distance_ticks,
                        "type": "gamma"
                    })
        
        return active_levels
    
    def _get_active_blind_spots(self, current_price: float,
                              menthorq_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Retourne les Blind Spots actifs"""
        active_spots = []
        blind_spots = menthorq_data.get("blind_spots", {})
        
        for label, price in blind_spots.items():
            if price is not None and price > 0:
                distance_ticks = abs(current_price - price) / ES_TICK_SIZE
                if distance_ticks <= self.blind_spot_danger_ticks:
                    active_spots.append({
                        "label": label,
                        "price": price,
                        "distance_ticks": distance_ticks,
                        "type": "blind_spot"
                    })
        
        return active_spots
    
    def _get_active_swing_levels(self, current_price: float,
                               menthorq_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Retourne les Swing Levels actifs"""
        active_levels = []
        swing_levels = menthorq_data.get("swing", {})
        
        for label, price in swing_levels.items():
            if price is not None and price > 0:
                distance_ticks = abs(current_price - price) / ES_TICK_SIZE
                if distance_ticks <= self.swing_proximity_ticks:
                    active_levels.append({
                        "label": label,
                        "price": price,
                        "distance_ticks": distance_ticks,
                        "type": "swing"
                    })
        
        return active_levels
    
    def _calculate_data_age(self, menthorq_data: Dict[str, Any]) -> int:
        """Calcule l'âge des données en secondes"""
        last_update = menthorq_data.get("last_update")
        if last_update:
            return int((datetime.now() - last_update).total_seconds())
        return 999999  # Très ancien
    
    def _calculate_quality_score(self, menthorq_data: Dict[str, Any], 
                               data_age_seconds: int) -> float:
        """Calcule le score de qualité des données"""
        
        # Score basé sur l'âge des données
        if data_age_seconds < 60:
            age_score = 1.0
        elif data_age_seconds < 300:
            age_score = 0.8
        elif data_age_seconds < 600:
            age_score = 0.6
        else:
            age_score = 0.2
        
        # Score basé sur le nombre de niveaux disponibles
        gamma_count = len([p for p in menthorq_data.get("gamma", {}).values() if p > 0])
        blind_count = len([p for p in menthorq_data.get("blind_spots", {}).values() if p > 0])
        swing_count = len([p for p in menthorq_data.get("swing", {}).values() if p > 0])
        
        total_levels = gamma_count + blind_count + swing_count
        levels_score = min(total_levels / 20.0, 1.0)  # Normalisé sur 20 niveaux
        
        # Score final
        return (age_score * 0.7 + levels_score * 0.3)
    
    def get_bias_summary(self, bias: MenthorQDealersBias) -> Dict[str, Any]:
        """Retourne un résumé du bias pour affichage"""
        
        return {
            "timestamp": bias.timestamp.isoformat(),
            "symbol": bias.symbol,
            "underlying_price": bias.underlying_price,
            "dealers_bias_score": bias.dealers_bias_score,
            "direction": bias.direction.value,
            "strength": bias.strength.value,
            "quality_score": bias.quality_score,
            "data_age_seconds": bias.data_age_seconds,
            "components": {
                "gamma_resistance": bias.gamma_resistance_bias,
                "gamma_support": bias.gamma_support_bias,
                "blind_spots": bias.blind_spots_bias,
                "swing_levels": bias.swing_levels_bias,
                "gex_levels": bias.gex_levels_bias,
                "vix_regime": bias.vix_regime_bias
            },
            "active_levels": {
                "gamma": len(bias.active_gamma_levels),
                "blind_spots": len(bias.active_blind_spots),
                "swing": len(bias.active_swing_levels)
            }
        }

# === FACTORY FUNCTION ===

def create_menthorq_dealers_bias_analyzer(menthorq_processor: MenthorQProcessor) -> MenthorQDealersBiasAnalyzer:
    """Factory function pour MenthorQDealersBiasAnalyzer"""
    return MenthorQDealersBiasAnalyzer(menthorq_processor)

# === TESTING ===

def test_menthorq_dealers_bias():
    """Test du Dealer's Bias MenthorQ"""
    logger.info("Test MenthorQDealersBiasAnalyzer...")
    
    # Créer le processeur et l'analyseur
    menthorq_processor = MenthorQProcessor()
    bias_analyzer = create_menthorq_dealers_bias_analyzer(menthorq_processor)
    
    # Simuler des données MenthorQ
    test_data = {
        "gamma": {
            "Call Resistance": 5300.0,
            "Put Support": 5285.0,
            "HVL": 5292.0,
            "GEX 1": 5295.0,
            "GEX 2": 5305.0
        },
        "blind_spots": {
            "BL 1": 5295.0
        },
        "swing": {
            "SG1": 5288.0,
            "SG2": 5302.0
        },
        "stale": False,
        "last_update": datetime.now()
    }
    
    # Mettre à jour le cache
    menthorq_processor.levels_cache["ESZ5"] = test_data
    
    # Calculer le bias
    current_price = 5294.0
    vix_level = 18.5
    
    bias = bias_analyzer.calculate_menthorq_dealers_bias(current_price, "ESZ5", vix_level)
    
    if bias:
        summary = bias_analyzer.get_bias_summary(bias)
        logger.info(f"Dealer's Bias MenthorQ: {summary}")
        
        print(f"Direction: {bias.direction.value}")
        print(f"Strength: {bias.strength.value}")
        print(f"Score: {bias.dealers_bias_score:.3f}")
        print(f"Quality: {bias.quality_score:.2f}")
    else:
        logger.error("Échec calcul Dealer's Bias MenthorQ")
    
    logger.info("Test MenthorQDealersBiasAnalyzer terminé")
    return True

# === FACTORY FUNCTION ===

def create_menthorq_dealers_bias_analyzer(config=None):
    """
    Factory function pour MenthorQDealersBiasAnalyzer
    
    Args:
        config: Configuration optionnelle (ignorée pour compatibilité)
        
    Returns:
        Instance de MenthorQDealersBiasAnalyzer ou None si erreur
    """
    try:
        # Créer le processeur MenthorQ
        menthorq_processor = MenthorQProcessor()
        
        # Créer l'analyseur avec le processeur
        analyzer = MenthorQDealersBiasAnalyzer(menthorq_processor)
        
        logger.info("✅ MenthorQDealersBiasAnalyzer créé avec succès")
        return analyzer
        
    except Exception as e:
        logger.error(f"❌ Erreur création MenthorQDealersBiasAnalyzer: {e}")
        return None

if __name__ == "__main__":
    test_menthorq_dealers_bias()
