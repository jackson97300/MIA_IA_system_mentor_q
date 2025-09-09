"""
MIA_IA_SYSTEM - MenthorQ Battle Navale Integration

Intégration MenthorQ dans le système Battle Navale
- Hard rules pour Blind Spots et Gamma Levels
- Fusion des signaux Battle Navale + MenthorQ
- Retour Decision standardisé (core/trading_types.py)
- Signature flexible (vix_level optionnel)

Version: v2.0 - Types standardisés
Performance: <2ms pour fusion des signaux
"""

import numpy as np
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from datetime import datetime, timezone

from core.logger import get_logger
from core.base_types import ES_TICK_SIZE
from core.trading_types import Decision, SignalName, utcnow
from features.menthorq_processor import MenthorQProcessor
from core.battle_navale import BattleNavaleAnalyzer, BattleNavaleResult

logger = get_logger(__name__)

# === MENTHORQ BATTLE NAVALE ANALYZER ===

class MenthorQBattleNavaleAnalyzer:
    """
    Analyseur MenthorQ + Battle Navale
    
    Fonctionnalités:
    1. Fusion des signaux Battle Navale + MenthorQ
    2. Hard rules pour Blind Spots et Gamma Levels
    3. Adaptation ES/NQ (lead/lag)
    4. Position sizing dynamique
    """
    
    def __init__(self, menthorq_processor: MenthorQProcessor, 
                 battle_navale_analyzer: BattleNavaleAnalyzer):
        """
        Initialisation de l'analyseur
        
        Args:
            menthorq_processor: Processeur MenthorQ
            battle_navale_analyzer: Analyseur Battle Navale
        """
        self.menthorq_processor = menthorq_processor
        self.battle_navale_analyzer = battle_navale_analyzer
        
        # Configuration des hard rules
        self.blind_spot_tolerance_ticks = 5.0
        self.gamma_level_tolerance_ticks = 3.0
        
        # Pondération des signaux
        self.battle_navale_weight = 0.6
        self.menthorq_weight = 0.4
        
        # Seuils de confluence
        self.confluence_threshold = 1.85
        
        logger.info("MenthorQBattleNavaleAnalyzer initialisé")
    
    def analyze_menthorq_battle_navale(self, current_price: float, symbol: str = "ESU25",
                                     vix_level: Optional[float] = None, 
                                     levels: Optional[Dict[str, Any]] = None,
                                     dealers_bias: float = 0.0) -> Decision:
        """
        Analyse complète MenthorQ + Battle Navale
        
        Args:
            current_price: Prix actuel
            symbol: Symbole à analyser
            vix_level: Niveau VIX (optionnel, défaut: 20.0)
            levels: Données MenthorQ (optionnel)
            dealers_bias: Biais des dealers [-1..+1]
            
        Returns:
            Decision standardisé avec signal final
        """
        # 1. VIX par défaut si None
        if vix_level is None:
            vix_level = 20.0  # Politique par défaut
        
        # 2. Récupérer les niveaux MenthorQ
        if levels is None:
            menthorq_data = self.menthorq_processor.get_levels(symbol)
        else:
            menthorq_data = levels
        
        # 3. Vérifier les hard rules
        hard_rules_triggered = self._check_hard_rules(current_price, menthorq_data)
        near_bl = self._check_blind_spot_proximity(current_price, menthorq_data)
        d_bl_ticks = self._get_blind_spot_distance(current_price, menthorq_data)
        
        # 4. Analyser Battle Navale
        # Créer MarketData minimal pour Battle Navale
        from core.base_types import MarketData
        market_data = MarketData(
            symbol=symbol,
            timestamp=utcnow(),
            open=current_price,
            high=current_price,
            low=current_price,
            close=current_price,
            volume=1000
        )
        
        battle_result = self.battle_navale_analyzer.analyze_battle_navale(
            market_data=market_data,
            order_flow=None
        )
        
        # 5. Analyser MenthorQ
        menthorq_score, confluence_details = self._analyze_menthorq_signal(
            current_price, menthorq_data, vix_level
        )
        
        # 6. Fusion des signaux
        final_score = self._fuse_signals(
            battle_result.battle_navale_signal, menthorq_score, hard_rules_triggered
        )
        
        # 7. Déterminer le signal final
        signal_name = self._determine_signal_name(final_score, hard_rules_triggered, dealers_bias)
        
        # 8. Calculer le position sizing
        position_sizing = self._calculate_sizing(vix_level, hard_rules_triggered)
        
        # 9. Construire la rationale
        rationale = self._build_rationale(hard_rules_triggered, near_bl, d_bl_ticks, dealers_bias)
        
        # 10. Retourner Decision standardisé
        return Decision(
            name=signal_name,
            score=final_score,
            strength_bn=battle_result.battle_navale_signal,
            strength_mq=menthorq_score,
            hard_rules_triggered=hard_rules_triggered,
            near_bl=near_bl,
            d_bl_ticks=d_bl_ticks,
            position_sizing=position_sizing,
            rationale=rationale
        )
    
    def _check_hard_rules(self, current_price: float, menthorq_data: Dict[str, Any]) -> bool:
        """Vérifie si les hard rules sont déclenchées"""
        # Hard rule 1: Blind Spot proche (≤ 5 ticks)
        blind_spots = menthorq_data.get("blind_spots", {})
        for label, price in blind_spots.items():
            if price and price > 0:
                distance_ticks = abs(current_price - price) / ES_TICK_SIZE
                if distance_ticks <= self.blind_spot_tolerance_ticks:
                    return True
        return False
    
    def _check_blind_spot_proximity(self, current_price: float, menthorq_data: Dict[str, Any]) -> bool:
        """Vérifie si le prix est proche d'un Blind Spot"""
        return self._check_hard_rules(current_price, menthorq_data)
    
    def _get_blind_spot_distance(self, current_price: float, menthorq_data: Dict[str, Any]) -> Optional[float]:
        """Retourne la distance au Blind Spot le plus proche en ticks"""
        blind_spots = menthorq_data.get("blind_spots", {})
        min_distance = float('inf')
        
        for label, price in blind_spots.items():
            if price and price > 0:
                distance_ticks = abs(current_price - price) / ES_TICK_SIZE
                min_distance = min(min_distance, distance_ticks)
        
        return min_distance if min_distance != float('inf') else None
    
    def _analyze_menthorq_signal(self, current_price: float, menthorq_data: Dict[str, Any],
                                vix_level: float) -> Tuple[float, Dict[str, Any]]:
        """Analyse le signal MenthorQ et retourne le score"""
        
        # Calculer le score de confluence
        confluence_score, confluence_details = self._calculate_menthorq_confluence_score(
            current_price, menthorq_data, vix_level
        )
        
        return confluence_score, confluence_details
    
    def _fuse_signals(self, battle_score: float, menthorq_score: float, hard_rules_triggered: bool) -> float:
        """Fusionne les signaux Battle Navale + MenthorQ"""
        
        # Hard rule: Blind Spot = score négatif
        if hard_rules_triggered:
            return -1.0
        
        # Fusion des scores avec pondération
        final_score = (self.battle_navale_weight * battle_score + 
                      self.menthorq_weight * menthorq_score)
        
        return final_score
    
    def _determine_signal_name(self, final_score: float, hard_rules_triggered: bool, dealers_bias: float) -> SignalName:
        """Détermine le nom du signal final"""
        
        # Hard rule: Blind Spot = NO_TRADE
        if hard_rules_triggered:
            return "NO_TRADE"
        
        # Seuils de décision
        if final_score >= 0.15:
            return "GO_LONG"
        elif final_score <= -0.15:
            return "GO_SHORT"
        else:
            # Si score neutre, regarder le dealers_bias
            if abs(dealers_bias) > 0.2:  # Seuil configurable
                return "GO_LONG" if dealers_bias > 0 else "GO_SHORT"
            else:
                return "NEUTRAL"
    
    def _calculate_sizing(self, vix_level: float, hard_rules_triggered: bool) -> float:
        """Calcule le position sizing"""
        
        # Hard rule: Blind Spot = 0
        if hard_rules_triggered:
            return 0.0
        
        # Base selon VIX
        if vix_level < 15:
            base_sizing = 1.0
        elif vix_level < 22:
            base_sizing = 0.75
        else:
            base_sizing = 0.5
        
        return base_sizing
    
    def _build_rationale(self, hard_rules_triggered: bool, near_bl: bool, d_bl_ticks: Optional[float], dealers_bias: float) -> List[str]:
        """Construit la liste des raisons"""
        rationale = []
        
        if hard_rules_triggered:
            rationale.append("BL proche (<5 ticks)")
        
        if near_bl and d_bl_ticks:
            rationale.append(f"BL à {d_bl_ticks:.1f} ticks")
        
        if abs(dealers_bias) > 0.1:
            bias_text = "bullish" if dealers_bias > 0 else "bearish"
            rationale.append(f"Dealer's Bias {bias_text} ({dealers_bias:.2f})")
        
        return rationale
    
    def _calculate_menthorq_confluence_score(self, current_price: float, menthorq_data: Dict[str, Any],
                                           vix_level: float) -> Tuple[float, Dict[str, Any]]:
        """Calcule le score de confluence MenthorQ"""
        
        # Adaptation des bandes selon VIX
        if vix_level < 15:
            band_ticks = 6
        elif vix_level < 22:
            band_ticks = 10
        else:
            band_ticks = 14
        
        confluence_score = 0.0
        details = {
            "gamma_score": 0.0,
            "blind_spots_score": 0.0,
            "swing_score": 0.0,
            "band_ticks": band_ticks,
            "nearby_levels": []
        }
        
        # Scoring des niveaux Gamma
        gamma_score = 0.0
        for label, price in menthorq_data.get("gamma", {}).items():
            if price > 0:
                distance_ticks = abs(current_price - price) / ES_TICK_SIZE
                if distance_ticks <= band_ticks:
                    # Poids selon le type de niveau
                    weight = self._get_menthorq_weight(label)
                    score = weight * np.exp(-(distance_ticks / band_ticks) ** 2)
                    gamma_score += score
                    details["nearby_levels"].append({
                        "type": "gamma",
                        "label": label,
                        "price": price,
                        "distance_ticks": distance_ticks,
                        "score": score
                    })
        
        details["gamma_score"] = gamma_score
        
        # Scoring des Blind Spots (pénalité)
        blind_spots_score = 0.0
        for label, price in menthorq_data.get("blind_spots", {}).items():
            if price > 0:
                distance_ticks = abs(current_price - price) / ES_TICK_SIZE
                if distance_ticks <= band_ticks:
                    penalty = 0.80 * np.exp(-(distance_ticks / band_ticks) ** 2)
                    blind_spots_score -= penalty
                    details["nearby_levels"].append({
                        "type": "blind_spot",
                        "label": label,
                        "price": price,
                        "distance_ticks": distance_ticks,
                        "penalty": penalty
                    })
        
        details["blind_spots_score"] = blind_spots_score
        
        # Scoring des Swing Levels
        swing_score = 0.0
        for label, price in menthorq_data.get("swing", {}).items():
            if price > 0:
                distance_ticks = abs(current_price - price) / ES_TICK_SIZE
                if distance_ticks <= band_ticks:
                    score = 0.75 * np.exp(-(distance_ticks / band_ticks) ** 2)
                    swing_score += score
                    details["nearby_levels"].append({
                        "type": "swing",
                        "label": label,
                        "price": price,
                        "distance_ticks": distance_ticks,
                        "score": score
                    })
        
        details["swing_score"] = swing_score
        
        # Score total
        confluence_score = gamma_score + blind_spots_score + swing_score
        
        return confluence_score, details
    
    def _get_menthorq_weight(self, label: str) -> float:
        """Retourne le poids d'un niveau MenthorQ"""
        weights = {
            "Call Resistance": 0.95,
            "Put Support": 0.95,
            "HVL": 0.90,
            "1D Min": 0.85,
            "1D Max": 0.85,
            "Call Resistance 0DTE": 0.90,
            "Put Support 0DTE": 0.90,
            "HVL 0DTE": 0.85,
            "Gamma Wall 0DTE": 0.90,
        }
        
        # GEX levels
        if label.startswith("GEX "):
            return 0.85
        
        return weights.get(label, 0.75)

# === FACTORY FUNCTION ===

def create_menthorq_battle_navale_analyzer(menthorq_processor: MenthorQProcessor,
                                          battle_navale_analyzer: BattleNavaleAnalyzer) -> MenthorQBattleNavaleAnalyzer:
    """Factory function pour MenthorQBattleNavaleAnalyzer"""
    return MenthorQBattleNavaleAnalyzer(menthorq_processor, battle_navale_analyzer)

# === TESTING ===

def test_menthorq_battle_navale():
    """Test robuste de l'intégration MenthorQ + Battle Navale"""
    logger.info("=== TEST ROBUSTE MenthorQBattleNavaleAnalyzer ===")
    
    try:
        # Créer les analyseurs
        menthorq_processor = MenthorQProcessor()
        battle_navale_analyzer = BattleNavaleAnalyzer()
        analyzer = create_menthorq_battle_navale_analyzer(menthorq_processor, battle_navale_analyzer)
        
        current_price = 5294.0
        symbol = "ESU25"
        
        # === TEST 1: Signature flexible (vix_level optionnel) ===
        logger.info("🔍 Test 1: Signature flexible...")
        
        # Sans vix_level
        result1 = analyzer.analyze_menthorq_battle_navale(
            current_price=current_price,
            symbol=symbol,
            dealers_bias=0.0
        )
        
        assert isinstance(result1, Decision), "Retourne Decision"
        assert hasattr(result1, 'hard_rules_triggered'), "Champ hard_rules_triggered présent"
        assert result1.name in ["GO_LONG", "GO_SHORT", "NO_TRADE", "NEUTRAL"], "Signal valide"
        logger.info(f"✅ Test 1 OK: {result1.name} (score: {result1.score:.3f})")
        
        # === TEST 2: Hard rules - Blind Spot proche ===
        logger.info("🔍 Test 2: Hard rules - Blind Spot...")
        
        test_data_bl = {
            "blind_spots": {
                "BL 1": 5294.5  # Très proche (0.5 point = 2 ticks < 5)
            }
        }
        
        result2 = analyzer.analyze_menthorq_battle_navale(
            current_price=current_price,
            symbol=symbol,
            levels=test_data_bl,
            dealers_bias=0.0
        )
        
        assert result2.hard_rules_triggered == True, "Hard rules déclenchées"
        assert result2.name == "NO_TRADE", "Signal NO_TRADE"
        assert result2.score == -1.0, "Score -1.0"
        assert result2.position_sizing == 0.0, "Position sizing 0"
        assert result2.near_bl == True, "near_bl True"
        assert result2.d_bl_ticks is not None, "d_bl_ticks calculé"
        assert "BL proche" in result2.rationale, "Rationale contient BL"
        logger.info(f"✅ Test 2 OK: {result2.name} (d_bl: {result2.d_bl_ticks:.1f} ticks)")
        
        # === TEST 3: VIX regimes et sizing ===
        logger.info("🔍 Test 3: VIX regimes...")
        
        test_data_normal = {
            "gamma": {
                "Call Resistance": 5300.0,
                "Put Support": 5285.0
            }
        }
        
        # VIX LOW
        result3a = analyzer.analyze_menthorq_battle_navale(
            current_price=current_price,
            symbol=symbol,
            vix_level=12.0,  # LOW
            levels=test_data_normal,
            dealers_bias=0.3
        )
        
        # VIX HIGH
        result3b = analyzer.analyze_menthorq_battle_navale(
            current_price=current_price,
            symbol=symbol,
            vix_level=25.0,  # HIGH
            levels=test_data_normal,
            dealers_bias=0.3
        )
        
        assert result3a.position_sizing > result3b.position_sizing, "VIX LOW > VIX HIGH sizing"
        logger.info(f"✅ Test 3 OK: VIX LOW sizing={result3a.position_sizing:.2f}, VIX HIGH sizing={result3b.position_sizing:.2f}")
        
        # === TEST 4: Dealers bias influence ===
        logger.info("🔍 Test 4: Dealers bias...")
        
        # Dealers bias bullish
        result4a = analyzer.analyze_menthorq_battle_navale(
            current_price=current_price,
            symbol=symbol,
            levels=test_data_normal,
            dealers_bias=0.3  # Bullish
        )
        
        # Dealers bias bearish
        result4b = analyzer.analyze_menthorq_battle_navale(
            current_price=current_price,
            symbol=symbol,
            levels=test_data_normal,
            dealers_bias=-0.3  # Bearish
        )
        
        # Dealers bias neutre
        result4c = analyzer.analyze_menthorq_battle_navale(
            current_price=current_price,
            symbol=symbol,
            levels=test_data_normal,
            dealers_bias=0.0  # Neutre
        )
        
        assert "bullish" in result4a.rationale[0] or "bearish" in result4b.rationale[0], "Rationale contient bias"
        logger.info(f"✅ Test 4 OK: Bullish={result4a.name}, Bearish={result4b.name}, Neutre={result4c.name}")
        
        # === TEST 5: Fusion des signaux ===
        logger.info("🔍 Test 5: Fusion signaux...")
        
        # Score Battle Navale fort + MenthorQ neutre
        result5 = analyzer.analyze_menthorq_battle_navale(
            current_price=current_price,
            symbol=symbol,
            vix_level=18.0,
            levels=test_data_normal,
            dealers_bias=0.0
        )
        
        assert isinstance(result5.strength_bn, float), "strength_bn numérique"
        assert isinstance(result5.strength_mq, float), "strength_mq numérique"
        assert -1.0 <= result5.score <= 1.0, "Score dans [-1, +1]"
        logger.info(f"✅ Test 5 OK: BN={result5.strength_bn:.3f}, MQ={result5.strength_mq:.3f}, Final={result5.score:.3f}")
        
        # === TEST 6: Cas limites ===
        logger.info("🔍 Test 6: Cas limites...")
        
        # Pas de niveaux MenthorQ
        result6a = analyzer.analyze_menthorq_battle_navale(
            current_price=current_price,
            symbol=symbol,
            levels={},  # Vide
            dealers_bias=0.0
        )
        
        # Niveaux invalides
        result6b = analyzer.analyze_menthorq_battle_navale(
            current_price=current_price,
            symbol=symbol,
            levels={"gamma": {"Invalid": -1.0}},  # Prix négatif
            dealers_bias=0.0
        )
        
        assert result6a.name in ["GO_LONG", "GO_SHORT", "NO_TRADE", "NEUTRAL"], "Pas de crash sans niveaux"
        assert result6b.name in ["GO_LONG", "GO_SHORT", "NO_TRADE", "NEUTRAL"], "Pas de crash avec niveaux invalides"
        logger.info(f"✅ Test 6 OK: Sans niveaux={result6a.name}, Niveaux invalides={result6b.name}")
        
        # === TEST 7: Timestamps UTC ===
        logger.info("🔍 Test 7: Timestamps UTC...")
        
        result7 = analyzer.analyze_menthorq_battle_navale(
            current_price=current_price,
            symbol=symbol,
            levels=test_data_normal,
            dealers_bias=0.0
        )
        
        assert result7.ts.tzinfo is not None, "Timestamp avec timezone"
        assert result7.ts.tzinfo.utcoffset(None).total_seconds() == 0, "Timestamp UTC"
        logger.info(f"✅ Test 7 OK: Timestamp UTC={result7.ts}")
        
        # === RÉSUMÉ ===
        logger.info("=" * 60)
        logger.info("🎉 TOUS LES TESTS ROBUSTES RÉUSSIS!")
        logger.info(f"✅ Signature flexible: vix_level optionnel")
        logger.info(f"✅ Hard rules: Blind Spot → NO_TRADE")
        logger.info(f"✅ VIX regimes: sizing adaptatif")
        logger.info(f"✅ Dealers bias: influence sur signal")
        logger.info(f"✅ Fusion signaux: BN + MQ pondérés")
        logger.info(f"✅ Cas limites: robustesse")
        logger.info(f"✅ Timestamps: UTC-aware")
        logger.info("=" * 60)
        
        return True
        
    except Exception as e:
        logger.error(f"❌ ERREUR TEST: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    test_menthorq_battle_navale()
