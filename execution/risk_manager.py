#!/usr/bin/env python3
"""
MIA_IA_SYSTEM - Risk Manager
Gestion du risque adaptée à la méthode Bataille Navale
Version: Production Ready
Location: D:\\MIA_IA_system\\execution\risk_manager.py

Responsabilités:
- Position sizing intelligent (confiance signal + volatilité)
- Stop loss adaptatifs (trend vs range)
- Gestion limites quotidiennes (prop firm)
- Protection drawdown maximum
- Règles spéciales Bataille Navale
- Notifications Discord des violations
"""

from core.logger import get_logger
from typing import Dict, Optional, List, Tuple, Any
from dataclasses import dataclass, field
from datetime import datetime, time
from enum import Enum
import numpy as np
import asyncio

# Local imports
from core.base_types import (
    TradingSignal, SignalType, MarketRegime,
    Position, OrderType, OrderStatus,
    ES_TICK_SIZE, ES_TICK_VALUE
)

# Config sera importé dynamiquement pour éviter circular imports
logger = get_logger(__name__)

# === ENUMS ===


class RiskLevel(Enum):
    """Niveaux de risque"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    EXTREME = "extreme"


class RiskAction(Enum):
    """Actions de gestion du risque"""
    APPROVE = "approve"
    REDUCE_SIZE = "reduce_size"
    REJECT = "reject"
    CLOSE_ALL = "close_all"
    HALT_TRADING = "halt_trading"

# === DATA STRUCTURES ===


@dataclass
class RiskParameters:
    """Paramètres de risque configurables"""
    # Position sizing
    base_position_size: int = 2
    max_position_size: int = 5
    max_positions_concurrent: int = 3

    # Risk per trade
    risk_per_trade_percent: float = 1.0  # 1% du capital
    max_risk_per_trade_dollars: float = 500.0

    # Daily limits (prop firm compatible)
    daily_loss_limit: float = 500.0
    daily_profit_target: float = 1000.0
    max_daily_trades: int = 999  # Pas de limite pour collecter données!

    # Drawdown protection
    max_drawdown_percent: float = 5.0
    trailing_drawdown: bool = True

    # Bataille Navale specific
    min_base_quality_for_trade: float = 0.5  # Réduit pour plus de trades
    min_confluence_score: float = 0.55  # Réduit pour plus de trades
    min_signal_probability: float = 0.60  # NOUVEAU: Seuil de probabilité minimum
    golden_rule_strict: bool = True  # Règle rouge sous verte

    # Mode collecte de données
    data_collection_mode: bool = True  # Active le mode permissif

    # Time restrictions
    no_trade_before: time = time(9, 35)  # 5 min après ouverture
    no_trade_after: time = time(15, 45)   # 15 min avant fermeture
    reduce_size_after: time = time(15, 0)  # Réduire après 15h

    # Volatility adjustments
    high_volatility_threshold: float = 30.0  # VIX level
    reduce_size_high_vol: bool = True

    # Session-based adjustments
    session_risk_multipliers: Dict[str, float] = field(default_factory=lambda: {
        'asian': 0.5,      # Risque réduit session asiatique
        'london': 1.0,     # Normal Londres
        'ny_am': 1.2,      # Augmenté matin NY
        'ny_pm': 0.8,      # Réduit après-midi
        'close': 0.5       # Très réduit fin de journée
    })


@dataclass
class RiskMetrics:
    """Métriques de risque en temps réel"""
    # Daily metrics
    daily_pnl: float = 0.0
    daily_trades_count: int = 0
    daily_winners: int = 0
    daily_losers: int = 0

    # Position metrics
    open_positions_count: int = 0
    total_exposure: float = 0.0
    total_risk: float = 0.0

    # Drawdown tracking
    peak_equity: float = 0.0
    current_drawdown: float = 0.0
    max_drawdown_hit: bool = False

    # Bataille Navale metrics
    golden_rule_violations: int = 0
    low_quality_bases_traded: int = 0

    # Session start values
    session_start_equity: float = 0.0
    session_start_time: Optional[datetime] = None


@dataclass
class RiskDecision:
    """Décision du risk manager"""
    action: RiskAction
    approved_size: int = 0
    stop_loss_price: Optional[float] = None
    take_profit_price: Optional[float] = None
    max_loss_dollars: float = 0.0
    reason: str = ""
    risk_score: float = 0.0
    adjustments: List[str] = field(default_factory=list)

# === MAIN RISK MANAGER ===


class RiskManager:
    """
    Gestionnaire de risque intelligent pour Bataille Navale
    """

    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize risk manager

        Args:
            config: Configuration optionnelle
        """
        # Charger config
        self.config = config or self._load_default_config()
        self.params = self._load_risk_parameters()

        # État
        self.metrics = RiskMetrics()
        self.positions: Dict[str, Position] = {}
        self.trade_history: List[Dict] = []

        # Session
        self.current_session = self._determine_session()
        self.is_halted = False
        self.halt_reason = ""

        # Discord notification flag
        self.discord_notifier = None  # Sera injecté si disponible

        logger.info("RiskManager initialisé avec limites quotidiennes: "
                    f"Loss: ${self.params.daily_loss_limit}, "
                    f"Target: ${self.params.daily_profit_target}")

    def _load_default_config(self) -> Dict:
        """Charge configuration par défaut"""
        try:
            from config.trading_config import get_trading_config
            return get_trading_config()
        except Exception:
            logger.warning("Config non trouvée, utilisation défauts")
            return {}

    def _load_risk_parameters(self) -> RiskParameters:
        """Charge paramètres de risque depuis config"""
        params = RiskParameters()

        # Override depuis config si disponible
        try:
            # Gérer le cas où config est un objet ou un dict
            if hasattr(self.config, 'risk_management'):
                risk_config = getattr(self.config, 'risk_management', {})
            elif isinstance(self.config, dict) and 'risk_management' in self.config:
                risk_config = self.config['risk_management']
            else:
                risk_config = {}
            
            # Convertir en dict si nécessaire
            if hasattr(risk_config, '__dict__'):
                risk_config = risk_config.__dict__
            
            # Appliquer les paramètres
            for key, value in risk_config.items():
                if hasattr(params, key):
                    setattr(params, key, value)
                    
        except Exception as e:
            logger.warning(f"Erreur chargement config risk: {e}")
            # Utiliser les valeurs par défaut

        return params

    def evaluate_signal(self, signal: TradingSignal,
                        current_price: float,
                        account_equity: float = 100000.0) -> RiskDecision:
        """
        Évalue un signal et détermine l'action appropriée

        Args:
            signal: Signal de trading à évaluer
            current_price: Prix actuel du marché
            account_equity: Capital du compte

        Returns:
            RiskDecision avec action et paramètres
        """
        # Check si trading halté
        if self.is_halted:
            return RiskDecision(
                action=RiskAction.REJECT,
                reason=f"Trading halté: {self.halt_reason}"
            )

        # 1. Vérifications de base
        basic_check = self._check_basic_conditions()
        if basic_check.action == RiskAction.REJECT:
            return basic_check

        # 2. Vérifier qualité signal Bataille Navale
        quality_check = self._check_signal_quality(signal)
        if quality_check.action == RiskAction.REJECT:
            return quality_check

        # 3. Calculer position size
        position_size = self._calculate_position_size(
            signal, current_price, account_equity
        )

        if position_size == 0:
            return RiskDecision(
                action=RiskAction.REJECT,
                reason="Position size calculée = 0"
            )

        # 4. Calculer stop loss adaptatif
        stop_loss = self._calculate_adaptive_stop(
            signal, current_price
        )

        # 5. Calculer take profit
        take_profit = self._calculate_take_profit(
            signal, current_price, stop_loss
        )

        # 6. Vérifier risk/reward
        risk_reward = abs(take_profit - current_price) / abs(stop_loss - current_price)
        if risk_reward < 1.5:  # Minimum 1.5:1
            return RiskDecision(
                action=RiskAction.REJECT,
                reason=f"Risk/Reward insuffisant: {risk_reward:.1f}"
            )

        # 7. Calculer risk en dollars
        risk_dollars = position_size * abs(current_price - stop_loss) * ES_TICK_VALUE / ES_TICK_SIZE

        # 8. Vérifier limites
        if not self._check_risk_limits(risk_dollars):
            # Essayer de réduire la taille
            reduced_size = self._reduce_position_size(position_size, risk_dollars)
            if reduced_size > 0:
                position_size = reduced_size
                risk_dollars = position_size * \
                    abs(current_price - stop_loss) * ES_TICK_VALUE / ES_TICK_SIZE
            else:
                return RiskDecision(
                    action=RiskAction.REJECT,
                    reason="Risque trop élevé même après réduction"
                )

        # 9. Score de risque final
        risk_score = self._calculate_risk_score(signal, risk_dollars)

        # 10. Décision finale
        adjustments = []

        # Ajustements selon conditions
        if self._is_high_volatility():
            position_size = int(position_size * 0.7)
            adjustments.append("Taille réduite (haute volatilité)")

        session_multiplier = self.params.session_risk_multipliers.get(
            self.current_session, 1.0
        )
        if session_multiplier != 1.0:
            position_size = int(position_size * session_multiplier)
            adjustments.append(f"Ajustement session {self.current_session}")

        # Décision finale
        decision = RiskDecision(
            action=RiskAction.APPROVE,
            approved_size=position_size,
            stop_loss_price=stop_loss,
            take_profit_price=take_profit,
            max_loss_dollars=risk_dollars,
            reason="Signal approuvé avec gestion du risque",
            risk_score=risk_score,
            adjustments=adjustments
        )

        logger.info(f"Risk Decision: {decision.action.value} - "
                    f"Size: {position_size}, Stop: {stop_loss}, "
                    f"TP: {take_profit}, Risk: ${risk_dollars:.0f}")

        return decision

    def _check_basic_conditions(self) -> RiskDecision:
        """Vérifie conditions de base pour trader"""
        # Limite quotidienne atteinte?
        if self.metrics.daily_pnl <= -self.params.daily_loss_limit:
            self._halt_trading("Limite de perte quotidienne atteinte")
            return RiskDecision(
                action=RiskAction.HALT_TRADING,
                reason=f"Daily loss limit hit: ${self.metrics.daily_pnl:.0f}"
            )

        # Target quotidien atteint?
        if self.metrics.daily_pnl >= self.params.daily_profit_target:
            if not self.params.data_collection_mode:
                return RiskDecision(
                    action=RiskAction.REJECT,
                    reason=f"Daily target atteint: ${self.metrics.daily_pnl:.0f}"
                )
            else:
                logger.info(
                    f"Target atteint (${
                        self.metrics.daily_pnl:.0f}) mais on continue (mode data collection)")

        # Max trades quotidiens?
        if self.metrics.daily_trades_count >= self.params.max_daily_trades:
            return RiskDecision(
                action=RiskAction.REJECT,
                reason=f"Max trades quotidiens atteint: {self.metrics.daily_trades_count}"
            )

        # Positions concurrentes?
        if self.metrics.open_positions_count >= self.params.max_positions_concurrent:
            return RiskDecision(
                action=RiskAction.REJECT,
                reason=f"Max positions concurrentes: {self.metrics.open_positions_count}"
            )

        # Horaires de trading?
        current_time = datetime.now().time()
        if current_time < self.params.no_trade_before:
            return RiskDecision(
                action=RiskAction.REJECT,
                reason=f"Trop tôt pour trader (avant {self.params.no_trade_before})"
            )

        if current_time > self.params.no_trade_after:
            return RiskDecision(
                action=RiskAction.REJECT,
                reason=f"Trop tard pour trader (après {self.params.no_trade_after})"
            )

        # Drawdown check
        if self.metrics.current_drawdown >= self.params.max_drawdown_percent:
            self._halt_trading("Drawdown maximum atteint")
            return RiskDecision(
                action=RiskAction.HALT_TRADING,
                reason=f"Max drawdown hit: {self.metrics.current_drawdown:.1f}%"
            )

        return RiskDecision(action=RiskAction.APPROVE)

    def _check_signal_quality(self, signal: TradingSignal) -> RiskDecision:
        """Vérifie qualité signal selon méthode Bataille Navale"""

        # NOUVEAU: Vérifier probabilité/confiance minimum
        if hasattr(signal, 'confidence') or hasattr(signal, 'probability'):
            signal_prob = getattr(signal, 'confidence', getattr(signal, 'probability', 0))
            if signal_prob < self.params.min_signal_probability:
                return RiskDecision(
                    action=RiskAction.REJECT,
                    reason=f"Probabilité insuffisante: {
                        signal_prob:.2f} < {
                        self.params.min_signal_probability}"
                )

        # Base quality check (plus permissif en mode data collection)
        if hasattr(signal, 'base_quality'):
            if signal.base_quality < self.params.min_base_quality_for_trade:
                if not self.params.data_collection_mode:
                    return RiskDecision(
                        action=RiskAction.REJECT,
                        reason=f"Base quality insuffisante: {signal.base_quality:.2f}"
                    )
                else:
                    logger.info(
                        f"Base quality faible ({
                            signal.base_quality:.2f}) mais acceptée (mode data collection)")

        # Confluence check (plus permissif en mode data collection)
        if hasattr(signal, 'confluence_score'):
            if signal.confluence_score < self.params.min_confluence_score:
                if not self.params.data_collection_mode:
                    return RiskDecision(
                        action=RiskAction.REJECT,
                        reason=f"Confluence insuffisante: {signal.confluence_score:.2f}"
                    )
                else:
                    logger.info(
                        f"Confluence faible ({
                            signal.confluence_score:.2f}) mais acceptée (mode data collection)")

        # Golden rule check (rouge sous verte)
        if self.params.golden_rule_strict and hasattr(signal, 'golden_rule_violated'):
            if signal.golden_rule_violated:
                self.metrics.golden_rule_violations += 1
                return RiskDecision(
                    action=RiskAction.REJECT,
                    reason="Règle d'or violée (rouge sous verte)"
                )

        return RiskDecision(action=RiskAction.APPROVE)

    def _calculate_position_size(self, signal: TradingSignal,
                                 current_price: float,
                                 account_equity: float) -> int:
        """
        Calcule taille position selon confiance et conditions

        Utilise:
        - Confiance du signal
        - Volatilité actuelle
        - Session de trading
        - Performance récente
        """
        # Base size
        base_size = self.params.base_position_size

        # Ajustement selon confiance signal
        if hasattr(signal, 'confidence'):
            if signal.confidence > 0.85:
                size_multiplier = 1.5
            elif signal.confidence > 0.75:
                size_multiplier = 1.2
            elif signal.confidence > 0.65:
                size_multiplier = 1.0
            else:
                size_multiplier = 0.5
        else:
            size_multiplier = 1.0

        # Ajustement selon performance récente
        if self.metrics.daily_trades_count >= 3:
            win_rate = self.metrics.daily_winners / self.metrics.daily_trades_count
            if win_rate < 0.3:  # Win rate < 30%
                size_multiplier *= 0.5  # Réduire de moitié
            elif win_rate > 0.7:  # Win rate > 70%
                size_multiplier *= 1.2  # Augmenter légèrement

        # Calcul final
        position_size = int(base_size * size_multiplier)

        # Limites
        position_size = max(1, min(position_size, self.params.max_position_size))

        return position_size

    def _calculate_adaptive_stop(self, signal: TradingSignal,
                                 current_price: float) -> float:
        """
        Calcule stop loss adaptatif selon régime et Bataille Navale
        """
        # Distance de base en ticks
        if signal.market_regime == MarketRegime.TREND:
            base_stop_ticks = 8  # Plus large en trend
        elif signal.market_regime == MarketRegime.RANGE:
            base_stop_ticks = 4  # Plus serré en range
        else:
            base_stop_ticks = 6  # Défaut

        # Ajustement selon base quality
        if hasattr(signal, 'base_quality') and signal.base_quality > 0.8:
            # Base solide = stop plus serré
            stop_ticks = base_stop_ticks * 0.8
        else:
            stop_ticks = base_stop_ticks

        # Ajustement volatilité
        if self._is_high_volatility():
            stop_ticks *= 1.5  # Stop plus large si volatile

        # Calcul prix stop selon direction
        if signal.signal_type in [SignalType.LONG, SignalType.LONG_SETUP]:
            stop_price = current_price - (stop_ticks * ES_TICK_SIZE)

            # Si base détectée, mettre stop sous la base
            if hasattr(signal, 'base_low') and signal.base_low:
                stop_price = min(stop_price, signal.base_low - 2 * ES_TICK_SIZE)
        else:
            stop_price = current_price + (stop_ticks * ES_TICK_SIZE)

            # Si base détectée, mettre stop au-dessus de la base
            if hasattr(signal, 'base_high') and signal.base_high:
                stop_price = max(stop_price, signal.base_high + 2 * ES_TICK_SIZE)

        # Arrondir au tick
        stop_price = round(stop_price / ES_TICK_SIZE) * ES_TICK_SIZE

        return stop_price

    def _calculate_take_profit(self, signal: TradingSignal,
                               current_price: float,
                               stop_loss: float) -> float:
        """Calcule take profit avec ratio risk/reward"""
        # Distance du stop
        stop_distance = abs(current_price - stop_loss)

        # Ratio selon régime
        if signal.market_regime == MarketRegime.TREND:
            rr_ratio = 2.5  # Viser plus loin en trend
        elif signal.market_regime == MarketRegime.RANGE:
            rr_ratio = 1.5  # Plus conservateur en range
        else:
            rr_ratio = 2.0

        # Ajustement selon confluence
        if hasattr(signal, 'confluence_score') and signal.confluence_score > 0.8:
            rr_ratio *= 1.2  # Viser plus loin si forte confluence

        # Calcul TP
        if signal.signal_type in [SignalType.LONG, SignalType.LONG_SETUP]:
            tp_price = current_price + (stop_distance * rr_ratio)
        else:
            tp_price = current_price - (stop_distance * rr_ratio)

        # Arrondir au tick
        tp_price = round(tp_price / ES_TICK_SIZE) * ES_TICK_SIZE

        return tp_price

    def _check_risk_limits(self, risk_dollars: float) -> bool:
        """Vérifie si le risque respecte les limites"""
        # Risk par trade
        if risk_dollars > self.params.max_risk_per_trade_dollars:
            return False

        # Risk total ouvert
        total_risk = self.metrics.total_risk + risk_dollars
        max_total_risk = self.params.daily_loss_limit * 0.5  # Max 50% de daily limit

        if total_risk > max_total_risk:
            return False

        # Risk selon equity restante avant limite
        remaining_loss_allowed = self.params.daily_loss_limit + self.metrics.daily_pnl
        if risk_dollars > remaining_loss_allowed * 0.3:  # Max 30% du restant
            return False

        return True

    def _reduce_position_size(self, original_size: int,
                              risk_dollars: float) -> int:
        """Essaie de réduire la taille pour respecter les limites"""
        max_allowed_risk = min(
            self.params.max_risk_per_trade_dollars,
            (self.params.daily_loss_limit + self.metrics.daily_pnl) * 0.3
        )

        if risk_dollars <= 0 or max_allowed_risk <= 0:
            return 0

        reduction_factor = max_allowed_risk / risk_dollars
        reduced_size = int(original_size * reduction_factor)

        return max(0, reduced_size)

    def _calculate_risk_score(self, signal: TradingSignal,
                              risk_dollars: float) -> float:
        """Calcule score de risque global 0-100"""
        score = 50.0  # Base

        # Signal quality impact
        if hasattr(signal, 'confidence'):
            score += (signal.confidence - 0.7) * 30  # +/- 30 points

        # Risk amount impact
        risk_percent = risk_dollars / self.params.max_risk_per_trade_dollars
        score -= risk_percent * 20  # -20 points si max risk

        # Session impact
        session_mult = self.params.session_risk_multipliers.get(self.current_session, 1.0)
        score *= session_mult

        # Daily performance impact
        if self.metrics.daily_trades_count > 0:
            win_rate = self.metrics.daily_winners / self.metrics.daily_trades_count
            score += (win_rate - 0.5) * 20  # +/- 10 points

        # Clamp 0-100
        return max(0, min(100, score))

    def _is_high_volatility(self) -> bool:
        """Détermine si volatilité élevée"""
        # TODO: Implémenter avec vraie donnée VIX ou ATR
        # Pour l'instant, retourne False
        return False

    def _determine_session(self) -> str:
        """Détermine session de trading actuelle"""
        current_hour = datetime.now().hour

        if 2 <= current_hour < 8:
            return 'asian'
        elif 8 <= current_hour < 12:
            return 'london'
        elif 12 <= current_hour < 15:
            return 'ny_am'
        elif 15 <= current_hour < 20:
            return 'ny_pm'
        else:
            return 'close'

    def _halt_trading(self, reason: str):
        """Arrête le trading"""
        self.is_halted = True
        self.halt_reason = reason
        logger.error(f"⛔ TRADING HALTÉ: {reason}")

        # Notifier Discord si disponible
        if self.discord_notifier:
            asyncio.create_task(
                self.discord_notifier.send_risk_alert({
                    'alert_type': 'TRADING HALTED',
                    'message': reason,
                    'severity': 'critical',
                    'impact': 'Aucun nouveau trade autorisé',
                    'action_taken': 'Trading automatique arrêté'
                })
            )

    def update_position(self, position: Position):
        """Met à jour une position existante"""
        self.positions[position.id] = position
        self._update_metrics()

    def close_position(self, position_id: str, exit_price: float, exit_reason: str):
        """Ferme une position et met à jour les métriques"""
        if position_id not in self.positions:
            logger.warning(f"Position {position_id} non trouvée")
            return

        position = self.positions[position_id]

        # Calculer P&L
        if position.side == 'LONG':
            pnl_ticks = (exit_price - position.entry_price) / ES_TICK_SIZE
        else:
            pnl_ticks = (position.entry_price - exit_price) / ES_TICK_SIZE

        pnl_dollars = pnl_ticks * position.quantity * ES_TICK_VALUE

        # Mettre à jour métriques
        self.metrics.daily_pnl += pnl_dollars
        self.metrics.daily_trades_count += 1

        if pnl_dollars > 0:
            self.metrics.daily_winners += 1
        else:
            self.metrics.daily_losers += 1

        # Sauver dans historique
        self.trade_history.append({
            'position_id': position_id,
            'entry_time': position.entry_time,
            'exit_time': datetime.now(),
            'side': position.side,
            'quantity': position.quantity,
            'entry_price': position.entry_price,
            'exit_price': exit_price,
            'pnl_dollars': pnl_dollars,
            'exit_reason': exit_reason
        })

        # Retirer de positions actives
        del self.positions[position_id]
        self._update_metrics()

        logger.info(f"Position fermée: {position_id} - P&L: ${pnl_dollars:.2f}")

    def _update_metrics(self):
        """Met à jour les métriques globales"""
        # Positions ouvertes
        self.metrics.open_positions_count = len(self.positions)

        # Exposure totale
        total_exposure = 0
        total_risk = 0

        for position in self.positions.values():
            exposure = position.quantity * position.entry_price * ES_TICK_VALUE
            total_exposure += exposure

            # Risk basé sur stop loss
            if position.stop_loss:
                risk_ticks = abs(position.entry_price - position.stop_loss) / ES_TICK_SIZE
                risk = risk_ticks * position.quantity * ES_TICK_VALUE
                total_risk += risk

        self.metrics.total_exposure = total_exposure
        self.metrics.total_risk = total_risk

        # Update drawdown
        current_equity = self.metrics.session_start_equity + self.metrics.daily_pnl
        if current_equity > self.metrics.peak_equity:
            self.metrics.peak_equity = current_equity

        drawdown_dollars = self.metrics.peak_equity - current_equity
        self.metrics.current_drawdown = (
            drawdown_dollars / self.metrics.peak_equity) * 100 if self.metrics.peak_equity > 0 else 0

    def get_risk_status(self) -> Dict[str, Any]:
        """Retourne statut complet du risque"""
        return {
            'is_halted': self.is_halted,
            'halt_reason': self.halt_reason,
            'daily_pnl': self.metrics.daily_pnl,
            'daily_trades': self.metrics.daily_trades_count,
            'win_rate': self.metrics.daily_winners / max(self.metrics.daily_trades_count, 1),
            'open_positions': self.metrics.open_positions_count,
            'total_exposure': self.metrics.total_exposure,
            'total_risk': self.metrics.total_risk,
            'current_drawdown': f"{self.metrics.current_drawdown:.1f}%",
            'remaining_loss_allowed': self.params.daily_loss_limit + self.metrics.daily_pnl,
            'remaining_trades_allowed': self.params.max_daily_trades - self.metrics.daily_trades_count,
            'current_session': self.current_session,
            'golden_rule_violations': self.metrics.golden_rule_violations
        }

    def reset_daily_metrics(self):
        """Reset métriques quotidiennes (à appeler à minuit)"""
        logger.info(f"Reset métriques quotidiennes - P&L final: ${self.metrics.daily_pnl:.2f}")

        # Sauver résultat du jour
        daily_result = {
            'date': datetime.now().date(),
            'pnl': self.metrics.daily_pnl,
            'trades': self.metrics.daily_trades_count,
            'winners': self.metrics.daily_winners,
            'losers': self.metrics.daily_losers
        }

        # Reset
        self.metrics.daily_pnl = 0.0
        self.metrics.daily_trades_count = 0
        self.metrics.daily_winners = 0
        self.metrics.daily_losers = 0
        self.metrics.golden_rule_violations = 0
        self.is_halted = False
        self.halt_reason = ""

        # Reset session
        self.metrics.session_start_equity = self.metrics.peak_equity
        self.metrics.session_start_time = datetime.now()

        return daily_result

    def force_close_all_positions(self, reason: str = "Force close"):
        """Ferme toutes les positions (urgence)"""
        logger.warning(f"[WARN] Force close all positions: {reason}")

        positions_to_close = list(self.positions.keys())
        for position_id in positions_to_close:
            # Simuler fermeture au marché
            self.close_position(position_id, self.positions[position_id].current_price, reason)

        return len(positions_to_close)

# === FACTORY FUNCTION ===


def create_risk_manager(config: Optional[Dict] = None) -> RiskManager:
    """Factory function pour créer RiskManager"""
    return RiskManager(config)

# === TESTING ===


def test_risk_manager():
    """Test du risk manager"""
    logger.info("🧪 Test Risk Manager...")

    # Créer instance
    rm = create_risk_manager()

    # Test signal
    from core.base_types import TradingSignal, SignalType

    test_signal = TradingSignal(
        timestamp=datetime.now(),
        signal_type=SignalType.LONG_SETUP,
        symbol="ES",
        entry_price=4500.0,
        confidence=0.8,
        market_regime=MarketRegime.TREND,
        base_quality=0.75,
        confluence_score=0.85,
        golden_rule_violated=False
    )

    # Évaluer
    decision = rm.evaluate_signal(test_signal, 4500.0)

    logger.info(f"Decision: {decision.action.value}")
    logger.info(f"   Size: {decision.approved_size}")
    logger.info(f"   Stop: {decision.stop_loss_price}")
    logger.info(f"   TP: {decision.take_profit_price}")
    logger.info(f"   Risk: ${decision.max_loss_dollars:.0f}")
    logger.info(f"   Score: {decision.risk_score:.0f}")

    # Test status
    status = rm.get_risk_status()
    logger.info("\n[STATS] Risk Status:")
    for key, value in status.items():
        logger.info(f"   {key}: {value}")

    logger.info("\n[OK] Risk Manager test completed!")

    return True


if __name__ == "__main__":
    test_risk_manager()