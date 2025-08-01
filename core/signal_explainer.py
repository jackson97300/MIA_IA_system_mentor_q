#!/usr/bin/env python3
"""
MIA_IA_SYSTEM - Signal Explainer
Explique pourquoi aucun signal n'est généré
Version: Simple v1.0 - Integration facile dans système existant
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from core.logger import get_logger

logger = get_logger(__name__)

@dataclass
class ExplanationReason:
    """Une raison d'absence de signal"""
    reason: str
    current_value: float
    required_value: float
    severity: str  # 'blocking', 'warning', 'info'
    
class SignalExplainer:
    """
    Explique pourquoi aucun signal Battle Navale n'est généré
    
    S'intègre facilement dans votre automation_main.py existant
    """
    
    def __init__(self):
        self.logger = get_logger(__name__)
        
        # Seuils depuis votre système existant (à ajuster selon vos vrais seuils)
        self.thresholds = {
            'confluence_min': 0.75,        # Votre seuil confluence
            'volume_min_factor': 1.2,      # Volume > moyenne * 1.2
            'price_change_min': 0.5,       # ticks minimum de mouvement
            'spread_max': 2.0,             # spread max acceptable
            'time_since_last_signal': 300, # 5 min minimum entre signaux
        }
        
        self.last_explanation_time = 0
        
    def explain_no_signal(self, 
                         market_data,
                         confluence_score: float = 0.0,
                         battle_navale_result: Optional[Dict] = None,
                         last_signal_time: float = 0) -> List[ExplanationReason]:
        """
        Explique pourquoi pas de signal
        
        Args:
            market_data: Vos données de marché existantes
            confluence_score: Score de confluence calculé
            battle_navale_result: Résultat de votre Battle Navale
            last_signal_time: Timestamp du dernier signal
            
        Returns:
            Liste des raisons (vide si signal possible)
        """
        reasons = []
        
        try:
            # 1. Check confluence (votre critère principal)
            if confluence_score < self.thresholds['confluence_min']:
                reasons.append(ExplanationReason(
                    reason=f"Confluence insuffisante",
                    current_value=confluence_score,
                    required_value=self.thresholds['confluence_min'],
                    severity='blocking'
                ))
            
            # 2. Check volume si disponible
            if hasattr(market_data, 'volume') and market_data.volume and market_data.volume > 0:
                # Volume analysis (simple)
                avg_volume = getattr(market_data, 'avg_volume', market_data.volume)
                if avg_volume and avg_volume > 0:
                    volume_ratio = market_data.volume / avg_volume
                    
                    if volume_ratio < self.thresholds['volume_min_factor']:
                        reasons.append(ExplanationReason(
                            reason="Volume trop faible",
                            current_value=volume_ratio,
                            required_value=self.thresholds['volume_min_factor'],
                            severity='warning'
                        ))
            
            # 3. Check spread si disponible
            if (hasattr(market_data, 'bid') and hasattr(market_data, 'ask') and 
                market_data.bid is not None and market_data.ask is not None):
                spread = market_data.ask - market_data.bid
                if spread > self.thresholds['spread_max']:
                    reasons.append(ExplanationReason(
                        reason="Spread trop large",
                        current_value=spread,
                        required_value=self.thresholds['spread_max'],
                        severity='blocking'
                    ))
            
            # 4. Check timing (éviter spam de signaux)
            import time
            current_time = time.time()
            time_since_last = current_time - last_signal_time
            
            if time_since_last < self.thresholds['time_since_last_signal']:
                reasons.append(ExplanationReason(
                    reason="Trop tôt depuis dernier signal",
                    current_value=time_since_last,
                    required_value=self.thresholds['time_since_last_signal'],
                    severity='info'
                ))
            
            # 5. Check Battle Navale specific
            if battle_navale_result:
                if not battle_navale_result.get('pattern_detected', False):
                    reasons.append(ExplanationReason(
                        reason="Aucun pattern Battle Navale détecté",
                        current_value=0,
                        required_value=1,
                        severity='blocking'
                    ))
                
                confidence = battle_navale_result.get('confidence', 0)
                if confidence < 0.6:  # Seuil de confiance minimum
                    reasons.append(ExplanationReason(
                        reason="Confiance Battle Navale faible",
                        current_value=confidence,
                        required_value=0.6,
                        severity='warning'
                    ))
            
            return reasons
            
        except Exception as e:
            self.logger.error(f"Erreur explain_no_signal: {e}")
            return [ExplanationReason(
                reason="Erreur analyse",
                current_value=0,
                required_value=1,
                severity='blocking'
            )]
    
    def format_explanation(self, reasons: List[ExplanationReason]) -> str:
        """
        Formate l'explication pour affichage
        
        Returns:
            String formaté pour logs ou Discord
        """
        if not reasons:
            return "✅ Conditions OK pour signal"
        
        # Grouper par sévérité
        blocking = [r for r in reasons if r.severity == 'blocking']
        warnings = [r for r in reasons if r.severity == 'warning']
        infos = [r for r in reasons if r.severity == 'info']
        
        explanation = "🚫 Pas de signal:\n"
        
        if blocking:
            explanation += "\n🔴 BLOQUANT:\n"
            for reason in blocking:
                explanation += f"  • {reason.reason}: {reason.current_value:.2f} (min: {reason.required_value:.2f})\n"
        
        if warnings:
            explanation += "\n⚠️ ATTENTION:\n"
            for reason in warnings:
                explanation += f"  • {reason.reason}: {reason.current_value:.2f} (optimal: {reason.required_value:.2f})\n"
        
        if infos:
            explanation += "\n💡 INFO:\n"
            for reason in infos:
                explanation += f"  • {reason.reason}: {reason.current_value:.0f}s (min: {reason.required_value:.0f}s)\n"
        
        return explanation.strip()
    
    def should_log_explanation(self) -> bool:
        """
        Détermine si on doit logger l'explication
        (éviter spam de logs)
        """
        import time
        current_time = time.time()
        
        # Log max 1x par minute
        if current_time - self.last_explanation_time > 60:
            self.last_explanation_time = current_time
            return True
        
        return False

# ================================
# INTÉGRATION FACILE DANS VOTRE SYSTÈME
# ================================

def create_signal_explainer() -> SignalExplainer:
    """Factory function pour créer le Signal Explainer"""
    return SignalExplainer()

# Exemple d'utilisation dans votre automation_main.py:
"""
# Dans votre classe MIAAutomationSystem, ajouter:
self.signal_explainer = create_signal_explainer()

# Dans votre méthode _generate_signal, quand pas de signal:
if not signal:
    reasons = self.signal_explainer.explain_no_signal(
        market_data=market_data,
        confluence_score=confluence_score,
        battle_navale_result=battle_navale_result,
        last_signal_time=self.last_signal_time
    )
    
    if self.signal_explainer.should_log_explanation():
        explanation = self.signal_explainer.format_explanation(reasons)
        self.logger.info(explanation)
        
        # Optionnel: Envoyer à Discord aussi
        if self.discord_notifier:
            await self.discord_notifier.send_custom_message(
                'signals_analysis',
                '🔍 Analyse Signal',
                explanation,
                color=0xFFA500  # Orange
            )
"""