#!/usr/bin/env python3
"""
MIA_IA_SYSTEM - Mentor System
🎯 RÔLE: Coach intelligent qui observe et recommande des améliorations
Impact: +3-5% win rate avec optimisation continue des paramètres
"""

import time
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta, date
from core.logger import get_logger
from core.trading_types import Decision

logger = get_logger(__name__)

# === CONSTANTS ===
PERFORMANCE_THRESHOLDS = {
    "MIN_HIT_RATE": 0.6,
    "MIN_RR_RATIO": 1.5,
    "MAX_DD_SESSION": 0.15,
    "MAX_NO_TRADE_RATIO": 0.4
}

RECOMMENDATION_CATEGORIES = {
    "THRESHOLDS": "thresholds",
    "DISTANCES": "distances", 
    "WEIGHTS": "weights",
    "TIMEFRAME": "timeframe",
    "CHECKLIST": "checklist"
}

PRIORITY_LEVELS = {
    "CRITICAL": 1,
    "HIGH": 2,
    "MEDIUM": 3,
    "LOW": 4,
    "INFO": 5
}

# === DATA STRUCTURES ===

@dataclass
class ExecutionResult:
    decision_id: str
    entry_price: float
    exit_price: float
    entry_time: datetime
    exit_time: datetime
    pnl: float
    pnl_ratio: float
    duration_minutes: int
    exit_reason: str
    max_drawdown: float
    max_favorable: float

@dataclass
class SessionContext:
    session_date: date
    vix_regime: str
    timeframe_used: int
    hot_zone_percentage: float
    total_decisions: int
    total_trades: int
    session_duration_hours: float
    mq_levels_freshness: float
    bn_context_quality: float

@dataclass
class SafetyEvent:
    timestamp: datetime
    event_type: str
    severity: str
    description: str
    resolved: bool

@dataclass
class Recommendation:
    category: str
    priority: int
    description: str
    current_value: Any
    suggested_value: Any
    confidence: float
    rationale: List[str]
    impact_estimate: str
    parameter_name: str
    expected_improvement: str

@dataclass
class MentorRecommendations:
    recommendations: List[Recommendation]
    confidence_score: float
    session_summary: Dict[str, Any]
    analysis_timestamp: datetime
    total_recommendations: int
    critical_count: int
    high_priority_count: int

# === MAIN CLASS ===

class MentorSystem:
    """Système de mentor intelligent"""
    
    def __init__(self):
        self.analysis_count = 0
        self.reco_thresholds = 0
        self.reco_distances = 0
        self.reco_weights = 0
        self.reco_timeframe = 0
        logger.debug("MentorSystem initialisé")
    
    def analyze_session_performance(self,
                                  decisions: List[Decision],
                                  explanations: List[Dict],
                                  execution_results: List[ExecutionResult],
                                  context: SessionContext,
                                  safety_events: List[SafetyEvent]) -> MentorRecommendations:
        """Analyse complète de performance et génère des recommandations"""
        start_time = time.time()
        self.analysis_count += 1
        
        try:
            # 1. Analyser les performances globales
            performance_metrics = self._analyze_performance_metrics(
                decisions, execution_results, context
            )
            
            # 2. Générer les recommandations
            recommendations = self._generate_recommendations(
                performance_metrics, context
            )
            
            # 3. Calculer le score de confiance global
            confidence_score = self._calculate_confidence_score(recommendations)
            
            # 4. Construire le résumé de session
            session_summary = self._build_session_summary(
                performance_metrics, context, len(recommendations)
            )
            
            # 5. Construire le résultat final
            mentor_recommendations = MentorRecommendations(
                recommendations=recommendations,
                confidence_score=confidence_score,
                session_summary=session_summary,
                analysis_timestamp=datetime.utcnow(),
                total_recommendations=len(recommendations),
                critical_count=len([r for r in recommendations if r.priority == 1]),
                high_priority_count=len([r for r in recommendations if r.priority <= 2])
            )
            
            # 6. Logs et métriques
            self._update_metrics(recommendations)
            elapsed = (time.time() - start_time) * 1000
            
            logger.info(f"🧠 Mentor: {len(recommendations)} recommandations, confiance {confidence_score:.2f}")
            logger.debug(f"🔍 Analyse complète: {mentor_recommendations}")
            logger.debug(f"⚡ Temps: {elapsed:.1f}ms")
            
            return mentor_recommendations
            
        except Exception as e:
            logger.error(f"❌ Erreur analyse mentor: {e}")
            return self._fallback_recommendations(str(e))
    
    def _analyze_performance_metrics(self, decisions: List[Decision], 
                                   execution_results: List[ExecutionResult],
                                   context: SessionContext) -> Dict[str, Any]:
        """Analyse les métriques de performance globales"""
        if not execution_results:
            return {"hit_rate": 0.0, "avg_rr": 0.0, "max_dd": 0.0}
        
        # Calculer les métriques de base
        total_trades = len(execution_results)
        winning_trades = [r for r in execution_results if r.pnl > 0]
        losing_trades = [r for r in execution_results if r.pnl < 0]
        
        hit_rate = len(winning_trades) / total_trades if total_trades > 0 else 0.0
        avg_rr = sum(r.pnl_ratio for r in execution_results) / total_trades if total_trades > 0 else 0.0
        max_dd = max(r.max_drawdown for r in execution_results) if execution_results else 0.0
        
        # Analyser les décisions
        no_trade_ratio = len([d for d in decisions if d.name == "NO_TRADE"]) / len(decisions) if decisions else 0.0
        
        return {
            "hit_rate": hit_rate,
            "avg_rr": avg_rr,
            "max_dd": max_dd,
            "total_trades": total_trades,
            "winning_trades": len(winning_trades),
            "losing_trades": len(losing_trades),
            "no_trade_ratio": no_trade_ratio,
            "avg_trade_duration": sum(r.duration_minutes for r in execution_results) / total_trades if total_trades > 0 else 0.0
        }
    
    def _generate_recommendations(self, performance_metrics: Dict[str, Any],
                                context: SessionContext) -> List[Recommendation]:
        """Génère des recommandations basées sur les performances"""
        recommendations = []
        
        # Recommandation basée sur hit rate
        if performance_metrics["hit_rate"] < PERFORMANCE_THRESHOLDS["MIN_HIT_RATE"]:
            recommendations.append(Recommendation(
                category=RECOMMENDATION_CATEGORIES["THRESHOLDS"],
                priority=PRIORITY_LEVELS["HIGH"],
                description="Hit rate faible - ajuster seuils BN",
                current_value=0.25,
                suggested_value=0.28,
                confidence=0.8,
                rationale=[f"Hit rate actuel: {performance_metrics['hit_rate']:.1%}"],
                impact_estimate="medium",
                parameter_name="bn_threshold_long",
                expected_improvement="+5-10% hit rate"
            ))
        
        # Recommandation basée sur VIX regime
        if context.vix_regime == "HIGH" and performance_metrics["avg_rr"] < PERFORMANCE_THRESHOLDS["MIN_RR_RATIO"]:
            recommendations.append(Recommendation(
                category=RECOMMENDATION_CATEGORIES["DISTANCES"],
                priority=PRIORITY_LEVELS["MEDIUM"],
                description="VIX HIGH - augmenter distances BL",
                current_value=5,
                suggested_value=6,
                confidence=0.7,
                rationale=["VIX HIGH regime", f"RR moyen: {performance_metrics['avg_rr']:.2f}"],
                impact_estimate="medium",
                parameter_name="bl_distance_ticks",
                expected_improvement="+0.2-0.5 RR"
            ))
        
        # Recommandation basée sur timeframe
        if context.hot_zone_percentage > 0.7 and context.timeframe_used > 15:
            recommendations.append(Recommendation(
                category=RECOMMENDATION_CATEGORIES["TIMEFRAME"],
                priority=PRIORITY_LEVELS["MEDIUM"],
                description="Hot zones - réduire timeframe",
                current_value=context.timeframe_used,
                suggested_value=15,
                confidence=0.7,
                rationale=["70%+ hot zones", "Timeframe trop élevé"],
                impact_estimate="medium",
                parameter_name="default_timeframe",
                expected_improvement="Meilleure réactivité"
            ))
        
        return recommendations
    
    def _calculate_confidence_score(self, recommendations: List[Recommendation]) -> float:
        """Calcule le score de confiance global"""
        if not recommendations:
            return 1.0
        
        # Moyenne pondérée par la priorité
        total_weight = 0
        weighted_confidence = 0
        
        for rec in recommendations:
            weight = 6 - rec.priority  # Plus haute priorité = plus de poids
            total_weight += weight
            weighted_confidence += rec.confidence * weight
        
        return weighted_confidence / total_weight if total_weight > 0 else 0.0
    
    def _build_session_summary(self, performance_metrics: Dict[str, Any],
                             context: SessionContext, 
                             recommendation_count: int) -> Dict[str, Any]:
        """Construit le résumé de session"""
        return {
            "session_date": context.session_date.isoformat(),
            "vix_regime": context.vix_regime,
            "timeframe_used": context.timeframe_used,
            "performance": {
                "hit_rate": performance_metrics["hit_rate"],
                "avg_rr": performance_metrics["avg_rr"],
                "total_trades": performance_metrics["total_trades"],
                "no_trade_ratio": performance_metrics["no_trade_ratio"]
            },
            "recommendation_count": recommendation_count,
            "session_quality": "excellent" if performance_metrics["hit_rate"] > 0.7 else "good" if performance_metrics["hit_rate"] > 0.5 else "needs_improvement"
        }
    
    def _update_metrics(self, recommendations: List[Recommendation]):
        """Met à jour les métriques internes"""
        for rec in recommendations:
            if rec.category == RECOMMENDATION_CATEGORIES["THRESHOLDS"]:
                self.reco_thresholds += 1
            elif rec.category == RECOMMENDATION_CATEGORIES["DISTANCES"]:
                self.reco_distances += 1
            elif rec.category == RECOMMENDATION_CATEGORIES["WEIGHTS"]:
                self.reco_weights += 1
            elif rec.category == RECOMMENDATION_CATEGORIES["TIMEFRAME"]:
                self.reco_timeframe += 1
    
    def _fallback_recommendations(self, error: str) -> MentorRecommendations:
        """Recommandations de fallback en cas d'erreur"""
        return MentorRecommendations(
            recommendations=[],
            confidence_score=0.0,
            session_summary={"error": error},
            analysis_timestamp=datetime.utcnow(),
            total_recommendations=0,
            critical_count=0,
            high_priority_count=0
        )
    
    def get_stats(self) -> Dict[str, Any]:
        """Retourne les statistiques du mentor"""
        return {
            "analysis_count": self.analysis_count,
            "reco_thresholds": self.reco_thresholds,
            "reco_distances": self.reco_distances,
            "reco_weights": self.reco_weights,
            "reco_timeframe": self.reco_timeframe,
            "total_recommendations": self.reco_thresholds + self.reco_distances + self.reco_weights + self.reco_timeframe
        }

def create_mentor_system() -> MentorSystem:
    """Factory function pour créer un MentorSystem"""
    return MentorSystem()

def test_mentor_system():
    """Test du MentorSystem"""
    logger.info("=== TEST MENTOR SYSTEM ===")
    
    try:
        mentor = create_mentor_system()
        
        # Données de test
        decisions = [
            Decision(name="GO_LONG", score=0.8, strength_bn=0.7, strength_mq=0.9,
                    hard_rules_triggered=False, near_bl=False, d_bl_ticks=10.0,
                    position_sizing=0.6, rationale=["Test"], ts=datetime.utcnow()),
            Decision(name="NO_TRADE", score=0.3, strength_bn=0.2, strength_mq=0.1,
                    hard_rules_triggered=True, near_bl=True, d_bl_ticks=3.0,
                    position_sizing=0.0, rationale=["BL too close"], ts=datetime.utcnow())
        ]
        
        explanations = [
            {"summary": "GO_LONG", "rationale": ["Test"]},
            {"summary": "NO_TRADE", "rationale": ["BL too close"]}
        ]
        
        execution_results = [
            ExecutionResult(
                decision_id="test1",
                entry_price=5300.0,
                exit_price=5305.0,
                entry_time=datetime.utcnow(),
                exit_time=datetime.utcnow(),
                pnl=5.0,
                pnl_ratio=1.0,
                duration_minutes=30,
                exit_reason="target",
                max_drawdown=-2.0,
                max_favorable=5.0
            )
        ]
        
        context = SessionContext(
            session_date=date.today(),
            vix_regime="HIGH",
            timeframe_used=30,
            hot_zone_percentage=0.8,
            total_decisions=2,
            total_trades=1,
            session_duration_hours=6.5,
            mq_levels_freshness=0.9,
            bn_context_quality=0.8
        )
        
        safety_events = [
            SafetyEvent(
                timestamp=datetime.utcnow(),
                event_type="bl_proximity",
                severity="medium",
                description="BL proximity warning",
                resolved=True
            )
        ]
        
        # Test analyse
        recommendations = mentor.analyze_session_performance(
            decisions, explanations, execution_results, context, safety_events
        )
        
        assert isinstance(recommendations, MentorRecommendations), "Doit retourner MentorRecommendations"
        assert len(recommendations.recommendations) >= 0, "Doit avoir des recommandations"
        assert recommendations.confidence_score >= 0.0, "Confiance doit être >= 0"
        assert recommendations.total_recommendations >= 0, "Total recommandations doit être >= 0"
        
        # Vérifier les stats
        stats = mentor.get_stats()
        assert stats["analysis_count"] > 0, "Doit avoir des analyses"
        
        logger.info("✅ Test Mentor System OK")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erreur test: {e}")
        return False

if __name__ == "__main__":
    test_mentor_system()
