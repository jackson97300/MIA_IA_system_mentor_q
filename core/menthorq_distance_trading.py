#!/usr/bin/env python3
"""
MIA_IA_SYSTEM - Méthode MenthorQ-First Basée sur les Distances

Méthode de trading robuste utilisant les distances aux niveaux MenthorQ
comme décideur principal, avec OrderFlow comme validation.

Version: MenthorQ-Distance v1.0
Performance: <3ms pour décision complète
"""

from typing import Dict, List, Optional, Any, Tuple, NamedTuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import math

from core.logger import get_logger
from core.unified_stops import calculate_unified_stops
from core.base_types import ES_TICK_SIZE
from features.menthorq_integration import MenthorQIntegration, MenthorQLevelType
from features.menthorq_dealers_bias import MenthorQDealersBiasAnalyzer
from features.leadership_zmom import LeadershipZMom

logger = get_logger(__name__)

# === TYPES DE DÉCISION ===

class TradingDirection(Enum):
    """Direction de trading"""
    LONG = "LONG"
    SHORT = "SHORT"
    NEUTRAL = "NEUTRAL"

class SignalStrength(Enum):
    """Force du signal"""
    EXTREME = "EXTREME"      # 90%+
    STRONG = "STRONG"        # 75-89%
    MODERATE = "MODERATE"    # 60-74%
    WEAK = "WEAK"           # 45-59%
    NO_SIGNAL = "NO_SIGNAL"  # <45%

@dataclass
class DistanceAnalysis:
    """Analyse des distances aux niveaux"""
    nearest_level: Optional[str] = None
    nearest_distance_ticks: float = float('inf')
    nearest_distance_points: float = float('inf')
    
    # Niveaux par proximité
    levels_within_3_ticks: List[Dict] = field(default_factory=list)
    levels_within_5_ticks: List[Dict] = field(default_factory=list)
    levels_within_10_ticks: List[Dict] = field(default_factory=list)
    levels_within_20_ticks: List[Dict] = field(default_factory=list)
    
    # Niveaux critiques
    critical_levels_nearby: List[Dict] = field(default_factory=list)
    gamma_wall_proximity: Optional[float] = None
    
    # Scores de proximité
    proximity_score: float = 0.0
    critical_proximity_score: float = 0.0

@dataclass
class MenthorQDistanceDecision:
    """Décision basée sur les distances MenthorQ"""
    direction: TradingDirection
    strength: SignalStrength
    confidence: float  # 0.0 à 1.0
    
    # Analyse des distances
    distance_analysis: DistanceAnalysis
    
    # Composantes
    proximity_score: float
    dealers_bias_score: float
    confluence_score: float
    
    # Niveaux actifs
    active_levels: List[Dict]
    critical_levels: List[Dict]
    
    # Rationale
    rationale: str
    timestamp: datetime = field(default_factory=datetime.now)

# === CONFIGURATION DISTANCE-BASED ===

class MenthorQDistanceConfig:
    """Configuration pour trading basé sur les distances"""
    
    # Seuils de distance (en ticks ES)
    DISTANCE_THRESHOLDS_TICKS = {
        "extreme_close": 2,      # 2 ticks = 0.5 points
        "very_close": 4,         # 4 ticks = 1.0 point
        "close": 8,              # 8 ticks = 2.0 points
        "moderate": 16,          # 16 ticks = 4.0 points
        "far": 32,               # 32 ticks = 8.0 points
    }
    
    # Seuils de confiance
    CONFIDENCE_THRESHOLDS = {
        "extreme": 0.90,         # 90%+ = Trade premium
        "strong": 0.75,          # 75%+ = Trade fort
        "moderate": 0.60,        # 60%+ = Trade standard
        "weak": 0.45,            # 45%+ = Trade faible
        "no_signal": 0.00,       # <45% = Pas de trade
    }
    
    # Pondération des composantes
    COMPONENT_WEIGHTS = {
        "proximity": 0.40,       # 40% - Proximité aux niveaux
        "dealers_bias": 0.35,    # 35% - Dealer's bias MenthorQ
        "confluence": 0.25,      # 25% - Confluence générale
    }
    
    # Multiplicateurs de distance par type de niveau
    DISTANCE_MULTIPLIERS = {
        # Niveaux 0DTE (poids maximum)
        MenthorQLevelType.GAMMA_WALL_0DTE: 2.0,      # Double poids
        MenthorQLevelType.CALL_RESISTANCE_0DTE: 1.8,
        MenthorQLevelType.PUT_SUPPORT_0DTE: 1.8,
        MenthorQLevelType.HVL_0DTE: 1.5,
        
        # Niveaux principaux
        MenthorQLevelType.CALL_RESISTANCE: 1.2,
        MenthorQLevelType.PUT_SUPPORT: 1.2,
        MenthorQLevelType.HVL: 1.0,
        MenthorQLevelType.ONE_D_MIN: 1.0,
        MenthorQLevelType.ONE_D_MAX: 1.0,
        
        # BL Levels (zones cachées)
        MenthorQLevelType.BL_1: 1.3,
        MenthorQLevelType.BL_2: 1.3,
        MenthorQLevelType.BL_3: 1.3,
        MenthorQLevelType.BL_4: 1.3,
        MenthorQLevelType.BL_5: 1.3,
        MenthorQLevelType.BL_6: 1.3,
        MenthorQLevelType.BL_7: 1.3,
        MenthorQLevelType.BL_8: 1.3,
        MenthorQLevelType.BL_9: 1.3,
        MenthorQLevelType.BL_10: 1.3,
        
        # GEX Levels (poids standard)
        MenthorQLevelType.GEX_1: 0.8,
        MenthorQLevelType.GEX_2: 0.8,
        MenthorQLevelType.GEX_3: 0.8,
        MenthorQLevelType.GEX_4: 0.8,
        MenthorQLevelType.GEX_5: 0.8,
        MenthorQLevelType.GEX_6: 0.8,
        MenthorQLevelType.GEX_7: 0.8,
        MenthorQLevelType.GEX_8: 0.8,
        MenthorQLevelType.GEX_9: 0.8,
        MenthorQLevelType.GEX_10: 0.8,
    }

# === CLASSE PRINCIPALE ===

class MenthorQDistanceTrader:
    """Trader basé sur les distances MenthorQ avec leadership ES/NQ"""
    
    def __init__(self):
        self.config = MenthorQDistanceConfig()
        self.menthorq_integration = MenthorQIntegration()
        
        # Initialiser le MenthorQProcessor pour le DealersBiasAnalyzer
        try:
            from features.menthorq_processor import MenthorQProcessor
            menthorq_processor = MenthorQProcessor()
            self.dealers_bias_analyzer = MenthorQDealersBiasAnalyzer(menthorq_processor)
        except ImportError:
            logger.warning("MenthorQProcessor non disponible, DealersBiasAnalyzer désactivé")
            self.dealers_bias_analyzer = None
        
        # 🆕 Leadership Z-Momentum (module unifié)
        self.leadership_engine = LeadershipZMom(
            horizons=(3, 30, 300),
            alpha=0.2,
            corr_win_points=300,
            max_delay_ms=200
        )
        
        # Cache pour performance
        self._cache = {}
        self._cache_ttl = 5  # 5 secondes
        
    def analyze_trading_opportunity(
        self,
        current_price: float,
        menthorq_levels: Dict[str, Any],
        orderflow_data: Optional[Dict] = None,
        vix_level: Optional[float] = None,
        es_data: Optional[Dict] = None,
        nq_data: Optional[Dict] = None
    ) -> MenthorQDistanceDecision:
        """
        Analyse une opportunité de trading basée sur les distances MenthorQ
        
        Args:
            current_price: Prix actuel
            menthorq_levels: Niveaux MenthorQ {gamma, blind_spots, swing, gex}
            orderflow_data: Données OrderFlow (optionnel)
            vix_level: Niveau VIX (optionnel)
            
        Returns:
            Décision de trading basée sur les distances
        """
        logger.debug(f"Analyse trading distance - Prix: {current_price}")
        
        # 1. Analyser les distances aux niveaux
        distance_analysis = self._analyze_level_distances(current_price, menthorq_levels)
        
        # 2. Calculer le score de proximité
        proximity_score = self._calculate_proximity_score(distance_analysis)
        
        # 3. Calculer le Dealer's Bias MenthorQ
        dealers_bias_score = self._calculate_dealers_bias(current_price, menthorq_levels)
        
        # 4. Calculer le score de confluence
        confluence_score = self._calculate_confluence_score(distance_analysis)
        
        # 5. Déterminer la direction et la force
        direction, strength, confidence = self._determine_trading_signal(
            proximity_score, dealers_bias_score, confluence_score, distance_analysis
        )
        
        # 6. Construire la décision
        decision = MenthorQDistanceDecision(
            direction=direction,
            strength=strength,
            confidence=confidence,
            distance_analysis=distance_analysis,
            proximity_score=proximity_score,
            dealers_bias_score=dealers_bias_score,
            confluence_score=confluence_score,
            active_levels=distance_analysis.levels_within_10_ticks,
            critical_levels=distance_analysis.critical_levels_nearby,
            rationale=self._build_rationale(direction, strength, distance_analysis)
        )
        
        logger.info(f"Décision: {direction.value} {strength.value} ({confidence:.1%})")
        return decision
    
    def _analyze_level_distances(self, current_price: float, menthorq_levels: Dict[str, Any]) -> DistanceAnalysis:
        """Analyse les distances aux niveaux MenthorQ"""
        analysis = DistanceAnalysis()
        
        all_levels = []
        
        # Collecter tous les niveaux
        for level_type, levels_data in menthorq_levels.items():
            if not levels_data:
                continue
                
            for level_name, level_price in levels_data.items():
                if isinstance(level_price, (int, float)) and level_price > 0:
                    distance_points = abs(current_price - level_price)
                    distance_ticks = distance_points / ES_TICK_SIZE
                    
                    level_info = {
                        "type": level_type,
                        "name": level_name,
                        "price": level_price,
                        "distance_points": distance_points,
                        "distance_ticks": distance_ticks
                    }
                    
                    all_levels.append(level_info)
        
        # Trier par distance
        all_levels.sort(key=lambda x: x["distance_ticks"])
        
        if all_levels:
            # Niveau le plus proche
            nearest = all_levels[0]
            analysis.nearest_level = nearest["name"]
            analysis.nearest_distance_ticks = nearest["distance_ticks"]
            analysis.nearest_distance_points = nearest["distance_points"]
        
        # Catégoriser par proximité
        for level in all_levels:
            distance_ticks = level["distance_ticks"]
            
            if distance_ticks <= 3:
                analysis.levels_within_3_ticks.append(level)
            if distance_ticks <= 5:
                analysis.levels_within_5_ticks.append(level)
            if distance_ticks <= 10:
                analysis.levels_within_10_ticks.append(level)
            if distance_ticks <= 20:
                analysis.levels_within_20_ticks.append(level)
        
        # Identifier les niveaux critiques
        analysis.critical_levels_nearby = [
            level for level in analysis.levels_within_5_ticks
            if "gamma_wall" in level["name"].lower() or "0dte" in level["name"].lower()
        ]
        
        # Proximité Gamma Wall
        gamma_walls = [level for level in all_levels if "gamma_wall" in level["name"].lower()]
        if gamma_walls:
            analysis.gamma_wall_proximity = min(level["distance_ticks"] for level in gamma_walls)
        
        return analysis
    
    def _calculate_proximity_score(self, distance_analysis: DistanceAnalysis) -> float:
        """Calcule le score de proximité basé sur les distances"""
        score = 0.0
        
        # Bonus pour niveaux très proches
        if distance_analysis.levels_within_3_ticks:
            score += 0.4 * len(distance_analysis.levels_within_3_ticks)
        
        if distance_analysis.levels_within_5_ticks:
            score += 0.3 * len(distance_analysis.levels_within_5_ticks)
        
        if distance_analysis.levels_within_10_ticks:
            score += 0.2 * len(distance_analysis.levels_within_10_ticks)
        
        # Bonus pour niveaux critiques
        if distance_analysis.critical_levels_nearby:
            score += 0.5 * len(distance_analysis.critical_levels_nearby)
        
        # Bonus pour proximité Gamma Wall
        if distance_analysis.gamma_wall_proximity is not None:
            if distance_analysis.gamma_wall_proximity <= 2:
                score += 0.6
            elif distance_analysis.gamma_wall_proximity <= 5:
                score += 0.3
        
        # Normalisation
        return min(score, 1.0)
    
    def _calculate_dealers_bias(self, current_price: float, menthorq_levels: Dict[str, Any]) -> float:
        """Calcule le Dealer's Bias MenthorQ"""
        try:
            # Convertir la structure de données au format attendu
            converted_levels = self._convert_menthorq_structure(menthorq_levels)
            
            # Utiliser l'analyzer existant
            bias_result = self.dealers_bias_analyzer.dealers_bias_with_menthorq(
                price=current_price,
                vix=20.0,  # VIX par défaut
                tick_size=0.25,  # ES tick size
                levels=converted_levels
            )
            return bias_result.get("dealers_bias_score", 0.0)
        except Exception as e:
            logger.warning(f"Erreur calcul dealers bias: {e}")
            return 0.0
    
    def _convert_menthorq_structure(self, menthorq_levels: Dict[str, Any]) -> Dict[str, Any]:
        """Convertit la structure MenthorQ au format attendu par DealersBiasAnalyzer"""
        converted = {
            "gamma": {},
            "blind_spots": {},
            "swing": {}
        }
        
        # Convertir gamma_wall -> gamma.call_resistance
        if "gamma_wall" in menthorq_levels:
            gamma_wall = menthorq_levels["gamma_wall"]
            if isinstance(gamma_wall, dict):
                # Prendre le premier niveau disponible
                for key, price in gamma_wall.items():
                    if price and price > 0:
                        converted["gamma"]["call_resistance"] = price
                        break
        
        # Convertir put_support -> gamma.put_support
        if "put_support" in menthorq_levels:
            put_support = menthorq_levels["put_support"]
            if isinstance(put_support, dict):
                for key, price in put_support.items():
                    if price and price > 0:
                        converted["gamma"]["put_support"] = price
                        break
        
        # Convertir hvl -> gamma.hvl
        if "hvl" in menthorq_levels:
            hvl = menthorq_levels["hvl"]
            if isinstance(hvl, dict):
                for key, price in hvl.items():
                    if price and price > 0:
                        converted["gamma"]["hvl"] = price
                        break
        
        # Convertir gex_levels -> gamma.gex
        if "gex_levels" in menthorq_levels:
            gex_levels = menthorq_levels["gex_levels"]
            if isinstance(gex_levels, dict):
                converted["gamma"]["gex"] = {}
                for i, (key, price) in enumerate(gex_levels.items(), 1):
                    if price and price > 0:
                        converted["gamma"]["gex"][str(i)] = price
        
        # Convertir blind_spots -> blind_spots
        if "blind_spots" in menthorq_levels:
            blind_spots = menthorq_levels["blind_spots"]
            if isinstance(blind_spots, dict):
                for i, (key, price) in enumerate(blind_spots.items(), 1):
                    if price and price > 0:
                        converted["blind_spots"][f"BL {i}"] = price
        
        return converted
    
    def _calculate_confluence_score(self, distance_analysis: DistanceAnalysis) -> float:
        """Calcule le score de confluence basé sur les distances"""
        score = 0.0
        
        # Score basé sur le nombre de niveaux proches
        nearby_count = len(distance_analysis.levels_within_10_ticks)
        if nearby_count >= 5:
            score = 1.0
        elif nearby_count >= 3:
            score = 0.7
        elif nearby_count >= 2:
            score = 0.5
        elif nearby_count >= 1:
            score = 0.3
        
        # Bonus pour confluence critique
        if distance_analysis.critical_levels_nearby:
            score += 0.2 * len(distance_analysis.critical_levels_nearby)
        
        return min(score, 1.0)
    
    def _determine_trading_signal(
        self,
        proximity_score: float,
        dealers_bias_score: float,
        confluence_score: float,
        distance_analysis: DistanceAnalysis
    ) -> Tuple[TradingDirection, SignalStrength, float]:
        """Détermine le signal de trading"""
        
        # Score composite
        composite_score = (
            proximity_score * self.config.COMPONENT_WEIGHTS["proximity"] +
            abs(dealers_bias_score) * self.config.COMPONENT_WEIGHTS["dealers_bias"] +
            confluence_score * self.config.COMPONENT_WEIGHTS["confluence"]
        )
        
        # Déterminer la force
        if composite_score >= self.config.CONFIDENCE_THRESHOLDS["extreme"]:
            strength = SignalStrength.EXTREME
        elif composite_score >= self.config.CONFIDENCE_THRESHOLDS["strong"]:
            strength = SignalStrength.STRONG
        elif composite_score >= self.config.CONFIDENCE_THRESHOLDS["moderate"]:
            strength = SignalStrength.MODERATE
        elif composite_score >= self.config.CONFIDENCE_THRESHOLDS["weak"]:
            strength = SignalStrength.WEAK
        else:
            strength = SignalStrength.NO_SIGNAL
        
        # Déterminer la direction basée sur le dealers bias
        if strength == SignalStrength.NO_SIGNAL:
            direction = TradingDirection.NEUTRAL
        elif dealers_bias_score > 0.2:
            direction = TradingDirection.LONG
        elif dealers_bias_score < -0.2:
            direction = TradingDirection.SHORT
        else:
            direction = TradingDirection.NEUTRAL
        
        return direction, strength, composite_score
    
    def _build_rationale(
        self,
        direction: TradingDirection,
        strength: SignalStrength,
        distance_analysis: DistanceAnalysis
    ) -> str:
        """Construit la rationale de la décision"""
        
        rationale_parts = []
        
        # Direction et force
        rationale_parts.append(f"Signal {direction.value} {strength.value}")
        
        # Proximité
        if distance_analysis.nearest_level:
            rationale_parts.append(
                f"Proche de {distance_analysis.nearest_level} "
                f"({distance_analysis.nearest_distance_ticks:.1f} ticks)"
            )
        
        # Niveaux critiques
        if distance_analysis.critical_levels_nearby:
            rationale_parts.append(
                f"{len(distance_analysis.critical_levels_nearby)} niveaux critiques proches"
            )
        
        # Gamma Wall
        if distance_analysis.gamma_wall_proximity is not None:
            rationale_parts.append(
                f"Gamma Wall à {distance_analysis.gamma_wall_proximity:.1f} ticks"
            )
        
        return " | ".join(rationale_parts)

    # 🆕 MÉTHODE PRINCIPALE INTÉGRÉE (Architecture MenthorQ-First + Leadership)
    
    def decide_mq_distance_integrated(
        self,
        row_es: Dict[str, Any],
        row_nq: Dict[str, Any],
        config: Optional[Dict] = None
    ) -> Optional[Dict[str, Any]]:
        print(f"🔍 DEBUG decide_mq_distance_integrated - Config reçue: {type(config)}")
        if config:
            print(f"🔍 DEBUG decide_mq_distance_integrated - Config keys: {list(config.keys()) if hasattr(config, 'keys') else 'N/A'}")
        else:
            print(f"🔍 DEBUG decide_mq_distance_integrated - Config est None, utilisation des valeurs par défaut")
        """
        Méthode principale intégrée suivant l'architecture :
        1. MenthorQ décide (décideur)
        2. MIA Bullish valide (biais interne)
        3. Leadership Z-Momentum gate + bonus
        4. OrderFlow valide (timing)
        5. Structure contextuelle
        6. Fusion des scores + modulateurs
        7. E/U/L
        
        Args:
            row_es: Ligne unified ES (mia_unifier)
            row_nq: Ligne unified NQ (mia_unifier)
            config: Configuration avec tolérances, seuils, pondérations
            
        Returns:
            Dict avec signal final ou None si pas de trade
        """
        if not config:
            config = {
                "tick_size": 0.25,
                "mq_tolerance_ticks": {"gamma_wall": 10, "hvl": 10, "gex": 10},
                "mia_threshold": 0.20,
                "entry_threshold": 0.30,
                "weights": {"mq": 0.55, "of": 0.30, "structure": 0.15}
            }
        
        tick = config.get("tick_size", 0.25)
        
        # 1) MENTHORQ-TRIGGER (décideur)
        # Support des deux formats de données
        price = row_es.get("basedata", {}).get("close") or row_es.get("price", 0)
        mq_levels = row_es.get("menthorq", {})
        
        mq_result = self._mq_gex_score(
            price=price,
            mq_levels=mq_levels,
            tick=tick,
            config=config
        )
        
        print(f"🔍 DEBUG decide_mq_distance_integrated:")
        print(f"   mq_result: {mq_result}")
        print(f"   mq_result type: {type(mq_result)}")
        if mq_result:
            print(f"   mq_result['side']: {mq_result.get('side')}")
        
        if not mq_result or mq_result["side"] is None:
            print(f"   ❌ RETOUR None: mq_result={mq_result}, side={mq_result.get('side') if mq_result else None}")
            return None  # Pas dans la tolérance MQ/GEX → no-trade
        
        best_level = mq_result["best_level"]
        mq_score = mq_result["score"]
        side = mq_result["side"]
        
        print(f"   ✅ MenthorQ validé: {side} (score: {mq_score})")
        
        # 2) MIA BULLISH (gate côté)
        print(f"   🔍 Calcul MIA Bullish...")
        mia_score = self._compute_mia_bullish_bidirectional(row_es)
        print(f"   📊 MIA Score: {mia_score}")
        
        # 🔧 CORRECTION: Utiliser la configuration MenthorQ First au lieu du seuil par défaut
        # La configuration a une structure imbriquée: menthorq_first_method -> menthorq -> mia
        print(f"   🔍 DEBUG - Config reçue: {type(config)}")
        print(f"   🔍 DEBUG - Config keys: {list(config.keys()) if hasattr(config, 'keys') else 'N/A'}")
        
        menthorq_first_config = config.get("menthorq_first_method", {})
        print(f"   🔍 DEBUG - menthorq_first_config: {menthorq_first_config}")
        
        menthorq_config = menthorq_first_config.get("menthorq", {})
        print(f"   🔍 DEBUG - menthorq_config: {menthorq_config}")
        
        mia_config = menthorq_config.get("mia", {})
        print(f"   🔍 DEBUG - mia_config: {mia_config}")
        
        # Seuils corrects depuis la configuration (valeurs par défaut moins restrictives)
        mia_threshold_long = mia_config.get("gate_long", 0.00001)   # LONG si mia ≥ +0.00001
        mia_threshold_short = mia_config.get("gate_short", -0.00001) # SHORT si mia ≤ -0.00001
        
        print(f"   🎯 MIA Threshold LONG: {mia_threshold_long}")
        print(f"   🎯 MIA Threshold SHORT: {mia_threshold_short}")
        print(f"   🔍 Validation MIA: side={side}, mia_score={mia_score}")
        
        # 🔧 CORRECTION: Logique MIA corrigée selon la configuration
        # Pour LONG: mia_score doit être >= +0.001 (bullish)
        # Pour SHORT: mia_score doit être <= -0.001 (bearish)
        if side == "LONG" and mia_score < mia_threshold_long:
            print(f"   ❌ RETOUR None: MIA gate échoué (side={side}, mia_score={mia_score}, threshold={mia_threshold_long})")
            return None
        elif side == "SHORT" and mia_score > mia_threshold_short:
            print(f"   ❌ RETOUR None: MIA gate échoué (side={side}, mia_score={mia_score}, threshold={mia_threshold_short})")
            return None
        
        print(f"   ✅ MIA Gate passé: {side} avec score {mia_score}")
        
        mia_mult = 1.05 if abs(mia_score) >= 0.35 else (1.00 if abs(mia_score) >= 0.20 else 0.95)
        print(f"   🔍 MIA Multiplier: {mia_mult}")
        
        # 3) LEADERSHIP Z-MOMENTUM (gate + bonus)
        snap = self.leadership_engine.update_from_unified_rows(row_es, row_nq)
        
        # VIX depuis l'unifier
        vix_val = None
        if row_es.get("vix"):
            vix_val = row_es["vix"].get("value") or row_es["vix"].get("close")
        
        gate = self.leadership_engine.gate_for_es(side=side, vix_value=vix_val)
        print(f"   🔍 Leadership Gate: {gate}")
        
        if not gate["allow"]:
            print(f"   ❌ RETOUR None: Leadership gate échoué - {gate}")
            return None  # Contre un leadership très fort ou corr trop faible
        
        leader_bonus = gate["bonus"]  # Multiplicateur (ex. 1.00 ou 1.05)
        extra_of = gate["extra_of"]   # +1 confirm OF en HIGH/EXTREME si LS peu marqué
        
        # 4) VALIDATION ORDERFLOW
        of_result = self._orderflow_score(row_es, extra_of)
        print(f"   🔍 OrderFlow Result: {of_result}")
        
        if not of_result["valid"]:
            print(f"   ❌ RETOUR None: OrderFlow validation échouée - {of_result}")
            return None
        
        of_score = of_result["score"]
        
        # 5) CONTEXTE STRUCTUREL
        st_score = self._structure_score(
            row_es.get("vwap", {}),
            row_es.get("vva", {}),
            price=row_es.get("basedata", {}).get("close"),
            tick=tick
        )
        
        # 6) FUSION + MODULATEURS
        weights = config.get("weights", {"mq": 0.55, "of": 0.30, "structure": 0.15})
        raw = (weights["mq"] * mq_score + 
               weights["of"] * of_score + 
               weights["structure"] * st_score)
        
        # VIX multiplier
        vix_mult = self._get_vix_multiplier(vix_val)
        
        eff = raw * vix_mult * mia_mult * leader_bonus
        
        print(f"   🔍 DEBUG Fusion - mq_score: {mq_score}, of_score: {of_score}, st_score: {st_score}")
        print(f"   🔍 DEBUG Fusion - weights: {weights}")
        print(f"   🔍 DEBUG Fusion - raw: {raw}")
        print(f"   🔍 DEBUG Fusion - vix_mult: {vix_mult}, mia_mult: {mia_mult}, leader_bonus: {leader_bonus}")
        print(f"   🔍 DEBUG Fusion - eff: {eff}")
        print(f"   🔍 DEBUG Fusion - entry_threshold: {config.get('entry_threshold', 0.70)}")
        
        # Utiliser le seuil de la configuration MenthorQ First
        entry_threshold = menthorq_config.get("thresholds", {}).get("enter_eff", 0.3)
        print(f"   🔍 DEBUG Final - eff: {eff}, entry_threshold: {entry_threshold}")
        
        if eff < entry_threshold:
            print(f"   ❌ RETOUR None: Score final {eff} < seuil {entry_threshold}")
            return None
        
        print(f"   ✅ SEUIL FINAL PASSÉ: {eff} >= {entry_threshold}")
        
        # 6.5) VÉRIFICATION "VRAIE CASSURE" (avant E/U/L)
        print(f"   🔍 Vérification vraie cassure...")
        if vix_val:
            # Les données OHLC sont directement dans row_es, pas dans basedata
            bar_data = {
                "open": row_es.get("open", 0),
                "high": row_es.get("high", 0), 
                "low": row_es.get("low", 0),
                "close": row_es.get("close", 0)
            }
            level_price = best_level.get("price", 0)
            print(f"   🔍 VIX val: {vix_val}, level_price: {level_price}, side: {side}")
            print(f"   🔍 Bar data: {bar_data}")
            
            true_break_result = self._is_true_break(bar_data, level_price, side, vix_val, tick)
            print(f"   🔍 Vraie cassure résultat: {true_break_result}")
            
            if not true_break_result:
                print(f"   ❌ RETOUR None: Pas de vraie cassure")
                return None  # Cassure non confirmée par wick tolerance
        else:
            print(f"   ⚠️ VIX val manquant, skip vraie cassure")
        
        # 7) E/U/L : stops derrière niveau MQ
        eul = self._compute_eul(
            price=row_es.get("close", 0),  # Données OHLC directement dans row_es
            mq_level=best_level,
            vix_regime=gate.get("regime", "MID"),
            tick=tick
        )
        
        # Signal final (audit friendly)
        return {
            "action": f"GO_{side}",
            "score": round(eff, 3),
            "mq_score": round(mq_score, 3),
            "of_score": round(of_score, 3),
            "st_score": round(st_score, 3),
            "mia_bullish": round(mia_score, 3),
            "vix_regime": gate.get("regime", "MID"),
            "leadership": {
                "ls": None if snap is None else snap.ls,
                "beta": None if snap is None else snap.beta,
                "roll_corr_30s": None if snap is None else snap.roll_corr_30s,
                "bonus": leader_bonus,
                "extra_of": extra_of,
                "reason": gate.get("reason", "")
            },
            "mq_level": best_level,
            "eul": eul
        }
    
    # === MÉTHODES HELPER ===
    
    def _mq_gex_score(self, price: float, mq_levels: Dict, tick: float, config: Dict) -> Optional[Dict]:
        """Calcule le score MenthorQ/GEX et détermine le side"""
        if not mq_levels or not price:
            return None
        
        best_level = None
        best_distance = float('inf')
        best_score = 0.0
        side = None
        
        # DEBUG: Vérifier les types d'entrée
        print(f"🔍 DEBUG _mq_gex_score:")
        print(f"   price: {price} (type: {type(price)})")
        print(f"   mq_levels: {type(mq_levels)}")
        print(f"   tick: {tick} (type: {type(tick)})")
        print(f"   config: {type(config)}")
        
        # Gérer la configuration (dict ou objet)
        if hasattr(config, 'get'):
            tolerances = config.get("mq_tolerance_ticks", {"gamma_wall": 3, "hvl": 5, "gex": 5})
        else:
            # Configuration par défaut si c'est un objet
            tolerances = {"gamma_wall": 3, "hvl": 5, "gex": 5}
        
        # Analyser les niveaux MenthorQ
        print(f"🔍 DEBUG - Analyse des niveaux:")
        for level_type, levels in mq_levels.items():
            # Ignorer les clés qui ne sont pas des dictionnaires de niveaux
            if not isinstance(levels, dict):
                print(f"   ⏭️ Ignoré {level_type}: {type(levels)}")
                continue
            if not levels:
                print(f"   ⏭️ Ignoré {level_type}: vide")
                continue
            
            print(f"   📊 Analyse {level_type}: {levels}")
            for level_name, level_price in levels.items():
                if not level_price or level_price <= 0:
                    print(f"      ⏭️ Ignoré {level_name}: prix invalide ({level_price})")
                    continue
                
                distance_ticks = abs(price - level_price) / tick
                print(f"      📏 {level_name}: prix={level_price}, distance={distance_ticks:.2f} ticks")
                
                # Déterminer la tolérance selon le type
                if "gamma_wall" in level_name.lower():
                    tolerance = tolerances.get("gamma_wall", 3)
                elif "hvl" in level_name.lower():
                    tolerance = tolerances.get("hvl", 5)
                else:
                    tolerance = tolerances.get("gex", 5)
                
                print(f"         🎯 Tolérance: {tolerance} ticks, Distance: {distance_ticks:.2f} ticks")
                
                # Vérifier si dans la tolérance
                if distance_ticks <= tolerance:
                    print(f"         ✅ NIVEAU VALIDE: {level_name} dans la tolérance !")
                else:
                    print(f"         ❌ Niveau hors tolérance: {level_name}")
                
                if distance_ticks <= tolerance:
                    # Calculer le score basé sur la distance
                    distance_score = max(0, 1 - (distance_ticks / tolerance))
                    print(f"         🎯 Score calculé: {distance_score:.3f}")
                    
                    if distance_score > best_score:
                        best_score = distance_score
                        best_level = {"name": level_name, "price": level_price, "type": level_type}
                        best_distance = distance_ticks
                        
                        # Déterminer le side
                        if "call" in level_name.lower() or "resistance" in level_name.lower():
                            side = "SHORT"  # Niveau de résistance
                        elif "put" in level_name.lower() or "support" in level_name.lower():
                            side = "LONG"   # Niveau de support
                        else:
                            # Pour les autres niveaux, utiliser la position
                            side = "LONG" if price < level_price else "SHORT"
                        
                        print(f"         🏆 NOUVEAU MEILLEUR: {level_name} (score: {distance_score:.3f}, side: {side})")
                    else:
                        print(f"         ⏭️ Score insuffisant: {distance_score:.3f} <= {best_score:.3f}")
        
        print(f"🔍 DEBUG - Résultat final:")
        print(f"   best_level: {best_level}")
        print(f"   best_score: {best_score}")
        print(f"   side: {side}")
        
        if best_level and best_score > 0:
            result = {
                "best_level": best_level,
                "score": best_score,
                "side": side,
                "distance_ticks": best_distance
            }
            print(f"   ✅ RETOUR: {result}")
            return result
        
        print(f"   ❌ RETOUR: None (best_level={best_level}, best_score={best_score})")
        return None
    
    def _compute_mia_bullish_bidirectional(self, row_es: Dict) -> float:
        """Calcule MIA Bullish bidirectionnel (-1 à +1)"""
        # Utiliser votre logique MIA Bullish existante mais adaptée
        # Pour l'instant, simulation basée sur les données disponibles
        
        basedata = row_es.get("basedata", {})
        vwap_data = row_es.get("vwap", {})
        vva_data = row_es.get("vva", {})
        
        # Support des deux formats de données
        close = basedata.get("close", 0) or row_es.get("close", 0) or row_es.get("price", 0)
        
        # Gérer vwap_data (dict ou float)
        if isinstance(vwap_data, dict):
            vwap = vwap_data.get("value", 0) or vwap_data.get("v", 0)
        else:
            vwap = float(vwap_data) if vwap_data else 0
        
        print(f"      🔍 MIA Debug: close={close}, vwap={vwap}")
        
        if not close or not vwap:
            print(f"      ❌ MIA: Données manquantes (close={close}, vwap={vwap})")
            return 0.0
        
        # Score basé sur la position vs VWAP
        vwap_score = (close - vwap) / vwap if vwap > 0 else 0.0
        
        # Normaliser entre -1 et +1
        return max(-1.0, min(1.0, vwap_score * 10))  # Facteur d'amplification
    
    def _orderflow_score(self, row_es: Dict, extra_of: int) -> Dict:
        """Calcule le score OrderFlow avec validation"""
        # Utiliser vos données OrderFlow existantes (corriger la clé)
        orderflow_data = row_es.get("orderflow", {})
        
        pressure = orderflow_data.get("pressure", 0)
        delta_ratio = orderflow_data.get("delta_ratio", 0.0)
        cumulative_delta = orderflow_data.get("cumulative_delta", 0.0)
        
        print(f"   🔍 DEBUG OrderFlow - pressure: {pressure}, delta_ratio: {delta_ratio}, cumulative_delta: {cumulative_delta}")
        
        # Score basé sur les indicateurs OrderFlow
        of_score = 0.0
        confirms = 0
        
        if pressure == 1:  # Bullish
            of_score += 0.4
            confirms += 1
        elif pressure == -1:  # Bearish
            of_score -= 0.4
            confirms += 1
        
        if abs(delta_ratio) > 0.1:
            of_score += delta_ratio * 0.3
            confirms += 1
        
        if abs(cumulative_delta) > 50:
            of_score += (cumulative_delta / 1000) * 0.3
            confirms += 1
        
        # Validation avec extra_of
        min_confirms = 2 + extra_of
        valid = confirms >= min_confirms
        
        return {
            "score": max(-1.0, min(1.0, of_score)),
            "confirms": confirms,
            "valid": valid
        }
    
    def _structure_score(self, vwap_data: Dict, vva_data: Dict, price: float, tick: float) -> float:
        """Calcule le score structurel (VWAP, VVA, etc.)"""
        if not price:
            return 0.0
        
        score = 0.0
        
        # VWAP position
        vwap = vwap_data.get("v", 0)
        if vwap > 0:
            vwap_dist = (price - vwap) / vwap
            score += vwap_dist * 0.5
        
        # VVA position
        vah = vva_data.get("vah", 0)
        val = vva_data.get("val", 0)
        if vah > 0 and val > 0:
            if price > vah:
                score += 0.3  # Au-dessus VAH
            elif price < val:
                score -= 0.3  # En-dessous VAL
            else:
                score += 0.1  # Dans la VA
        
        return max(-1.0, min(1.0, score))
    
    def _vix_band(self, vix_value: float) -> str:
        """Source de vérité unique pour déterminer la bande VIX"""
        if vix_value < 15:
            return "LOW"
        elif vix_value < 22:
            return "MID"
        elif vix_value < 35:
            return "HIGH"
        else:
            return "EXTREME"
    
    def _wick_tolerance_ticks(self, vix_value: float) -> int:
        """Tolérance des mèches par bande VIX (source de vérité unique)"""
        band = self._vix_band(vix_value)
        tolerance_map = {
            "LOW": 3,
            "MID": 5, 
            "HIGH": 7,
            "EXTREME": 7
        }
        return tolerance_map[band]
    
    def _get_vix_multiplier(self, vix_val: Optional[float]) -> float:
        """Calcule le multiplicateur VIX"""
        if not vix_val:
            return 1.0
        
        band = self._vix_band(vix_val)
        multiplier_map = {
            "LOW": 1.1,
            "MID": 1.0,
            "HIGH": 0.8,
            "EXTREME": 0.7
        }
        return multiplier_map[band]
    
    def _is_true_break(self, bar_data: Dict, level_price: float, side: str, vix_value: float, tick: float) -> bool:
        """
        Vérifie si c'est une vraie cassure selon la règle :
        - Clôture au-delà du niveau + mèche dans la tolérance VIX
        
        Args:
            bar_data: dict avec open/high/low/close
            level_price: prix du niveau MenthorQ
            side: 'LONG' (cassure au-dessus) ou 'SHORT' (cassure au-dessous)
            vix_value: valeur VIX pour déterminer la tolérance
            tick: taille du tick (ES = 0.25)
        """
        print(f"      🔍 DEBUG _is_true_break: bar_data={bar_data}, level_price={level_price}, side={side}, vix_value={vix_value}, tick={tick}")
        
        if not bar_data or not level_price:
            print(f"      ❌ Données manquantes: bar_data={bool(bar_data)}, level_price={level_price}")
            return False
        
        close = bar_data.get("close", 0)
        high = bar_data.get("high", 0)
        low = bar_data.get("low", 0)
        
        print(f"      🔍 OHLC: close={close}, high={high}, low={low}")
        
        if not all([close, high, low]):
            print(f"      ❌ OHLC incomplet: close={close}, high={high}, low={low}")
            return False
        
        # Tolérance des mèches selon VIX
        wick_tolerance_ticks = self._wick_tolerance_ticks(vix_value)
        wick_tolerance_price = wick_tolerance_ticks * tick
        
        print(f"      🔍 Tolérance: {wick_tolerance_ticks} ticks = {wick_tolerance_price} points")
        
        if side == "LONG":
            # Cassure au-dessus : close >= niveau ET low >= niveau - tolérance
            close_ok = close >= level_price  # Accepter l'égalité
            wick_ok = low >= (level_price - wick_tolerance_price)
            print(f"      🔍 LONG: close_ok={close_ok} ({close} >= {level_price}), wick_ok={wick_ok} ({low} >= {level_price - wick_tolerance_price})")
            return close_ok and wick_ok
        else:
            # Cassure au-dessous : close <= niveau ET high <= niveau + tolérance
            close_ok = close <= level_price  # Accepter l'égalité
            wick_ok = high <= (level_price + wick_tolerance_price)
            print(f"      🔍 SHORT: close_ok={close_ok} ({close} <= {level_price}), wick_ok={wick_ok} ({high} <= {level_price + wick_tolerance_price})")
            return close_ok and wick_ok
    
    def _compute_eul(self, price: float, mq_level: Dict, vix_regime: str, tick: float) -> Dict:
        """Calcule Entry/Stop/Target - VERSION UNIFIÉE (7 ticks partout)"""
        if not mq_level or not price:
            return {}
        
        level_price = mq_level["price"]
        
        # Déterminer le côté basé sur la position par rapport au niveau
        side = "LONG" if price > level_price else "SHORT"
        
        # Utiliser le système unifié de stops (7 ticks partout)
        unified_result = calculate_unified_stops(
            entry_price=price,
            side=side,
            level_price=level_price,
            use_fixed=True  # Force 7 ticks partout
        )
        
        if not unified_result:
            # Fallback vers l'ancienne méthode en cas d'erreur
            logger.warning("⚠️ Fallback vers ancienne méthode E/U/L")
            
            vix_mult = {"LOW": 0.8, "MID": 1.0, "HIGH": 1.2, "EXTREME": 1.5}.get(vix_regime, 1.0)
            stop_distance = 5 * tick * vix_mult
            
            if side == "LONG":
                entry = price
                stop = level_price - stop_distance
                target1 = price + (price - stop)
                target2 = price + 2 * (price - stop)
            else:
                entry = price
                stop = level_price + stop_distance
                target1 = price - (stop - price)
                target2 = price - 2 * (stop - price)
            
            return {
                "entry": round(entry, 2),
                "stop": round(stop, 2),
                "target1": round(target1, 2),
                "target2": round(target2, 2),
                "risk_ticks": round(abs(entry - stop) / tick, 1)
            }
        
        # Retourner le résultat unifié
        logger.debug(f"📊 E/U/L Unifié: {side} @ {price} → 7 ticks fixes")
        
        return {
            "entry": unified_result["entry"],
            "stop": unified_result["stop"],
            "target1": unified_result["target1"],
            "target2": unified_result["target2"],
            "risk_ticks": unified_result["risk_ticks"],
            "risk_dollars": unified_result["risk_dollars"],
            "method": "unified_7_ticks"
        }

# === FONCTION UTILITAIRE ===

def validate_with_orderflow(
    menthorq_decision: MenthorQDistanceDecision,
    orderflow_data: Dict[str, Any]
) -> bool:
    """
    Valide la décision MenthorQ avec OrderFlow
    
    Args:
        menthorq_decision: Décision MenthorQ
        orderflow_data: Données OrderFlow
        
    Returns:
        True si OrderFlow valide la décision
    """
    
    if menthorq_decision.direction == TradingDirection.NEUTRAL:
        return False
    
    # Extraire les données OrderFlow
    pressure = orderflow_data.get("pressure", 0)
    delta_ratio = orderflow_data.get("delta_ratio", 0.0)
    cumulative_delta = orderflow_data.get("cumulative_delta", 0.0)
    
    # Validation selon la direction
    if menthorq_decision.direction == TradingDirection.LONG:
        # OrderFlow doit confirmer l'achat
        return (
            pressure == 1 and
            delta_ratio > 0.1 and
            cumulative_delta > 0
        )
    
    elif menthorq_decision.direction == TradingDirection.SHORT:
        # OrderFlow doit confirmer la vente
        return (
            pressure == -1 and
            delta_ratio < -0.1 and
            cumulative_delta < 0
        )
    
    return False

# === EXEMPLE D'UTILISATION ===

def example_usage():
    """Exemple d'utilisation de la méthode MenthorQ-Distance"""
    
    # Données d'exemple
    current_price = 4500.0
    menthorq_levels = {
        "gamma": {
            "call_resistance": 4502.0,
            "put_support": 4498.0,
            "gamma_wall_0dte": 4501.0
        },
        "blind_spots": {
            "bl_1": 4503.0,
            "bl_2": 4497.0
        },
        "gex": {
            "gex_1": 4505.0,
            "gex_2": 4495.0
        }
    }
    
    orderflow_data = {
        "pressure": 1,
        "delta_ratio": 0.15,
        "cumulative_delta": 120.0
    }
    
    # Analyser
    trader = MenthorQDistanceTrader()
    decision = trader.analyze_trading_opportunity(
        current_price=current_price,
        menthorq_levels=menthorq_levels,
        orderflow_data=orderflow_data
    )
    
    # Valider avec OrderFlow
    is_validated = validate_with_orderflow(decision, orderflow_data)
    
    print(f"Décision: {decision.direction.value} {decision.strength.value}")
    print(f"Confiance: {decision.confidence:.1%}")
    print(f"OrderFlow valide: {is_validated}")
    print(f"Rationale: {decision.rationale}")

if __name__ == "__main__":
    example_usage()
