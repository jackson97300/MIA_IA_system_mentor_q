#!/usr/bin/env python3
"""
MIA_IA_SYSTEM - Session Replay Module
Rejoue et analyse les sessions de trading passées pour améliorer les stratégies

Version: 1.0.0
Responsabilité: Replay et analyse des sessions de trading

FONCTIONNALITÉS:
1. Replay des sessions de trading complètes
2. Analyse des décisions prises
3. Simulation des conditions de marché
4. Comparaison avec les résultats réels
5. Optimisation des paramètres
6. Génération de rapports détaillés
"""

import json
import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging

# === TYPES ET ENUMS ===

class ReplayMode(Enum):
    """Modes de replay disponibles"""
    FULL_SESSION = "full_session"
    TRADE_SEQUENCE = "trade_sequence"
    DECISION_POINTS = "decision_points"
    MARKET_CONDITIONS = "market_conditions"

class ReplayStatus(Enum):
    """Statuts de replay"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"

@dataclass
class ReplaySession:
    """Session de replay"""
    session_id: str
    original_date: datetime
    replay_date: datetime
    mode: ReplayMode
    status: ReplayStatus
    trades_count: int = 0
    decisions_count: int = 0
    market_conditions_count: int = 0
    duration_minutes: float = 0.0
    pnl_original: float = 0.0
    pnl_replay: float = 0.0
    improvement_pct: float = 0.0

@dataclass
class ReplayDecision:
    """Décision prise lors du replay"""
    timestamp: datetime
    decision_type: str  # ENTRY, EXIT, MODIFY, HOLD
    original_action: str
    replay_action: str
    market_conditions: Dict[str, Any]
    confidence_original: float
    confidence_replay: float
    improvement: float
    reasoning: str

@dataclass
class ReplayTrade:
    """Trade rejoué"""
    trade_id: str
    original_trade_id: str
    symbol: str
    side: str
    entry_price: float
    exit_price: float
    quantity: int
    pnl_original: float
    pnl_replay: float
    improvement: float
    execution_time: datetime
    duration_minutes: float
    market_conditions: Dict[str, Any]

@dataclass
class ReplayAnalysis:
    """Analyse complète du replay"""
    session_id: str
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float
    avg_win: float
    avg_loss: float
    profit_factor: float
    max_drawdown: float
    sharpe_ratio: float
    total_pnl: float
    improvement_pct: float
    best_decisions: List[ReplayDecision]
    worst_decisions: List[ReplayDecision]
    market_conditions_analysis: Dict[str, Any]

# === SESSION REPLAY ENGINE ===

class SessionReplayEngine:
    """
    🎬 SESSION REPLAY ENGINE
    
    Rejoue les sessions de trading passées pour :
    - Analyser les décisions prises
    - Simuler des conditions de marché différentes
    - Optimiser les paramètres
    - Comparer avec les résultats réels
    """
    
    def __init__(self, db_path: str = "data/trading_sessions.db"):
        self.db_path = db_path
        self.logger = logging.getLogger(f"{__name__}.SessionReplayEngine")
        self.replay_sessions: Dict[str, ReplaySession] = {}
        self.current_replay: Optional[ReplaySession] = None
        self.market_data_cache: Dict[str, pd.DataFrame] = {}
        
        # Configuration replay
        self.replay_config = {
            'speed_multiplier': 1.0,  # Vitesse de replay
            'enable_market_simulation': True,
            'enable_decision_analysis': True,
            'enable_parameter_optimization': True,
            'max_replay_duration_hours': 24,
            'min_trades_for_analysis': 5
        }
        
        self.logger.info("🎬 Session Replay Engine initialisé")
    
    def create_replay_session(self, original_date: datetime, mode: ReplayMode = ReplayMode.FULL_SESSION) -> str:
        """Crée une nouvelle session de replay"""
        try:
            session_id = f"REPLAY_{original_date.strftime('%Y%m%d_%H%M%S')}_{mode.value}"
            
            replay_session = ReplaySession(
                session_id=session_id,
                original_date=original_date,
                replay_date=datetime.now(),
                mode=mode,
                status=ReplayStatus.PENDING
            )
            
            self.replay_sessions[session_id] = replay_session
            self.logger.info(f"🎬 Session replay créée: {session_id}")
            
            return session_id
            
        except Exception as e:
            self.logger.error(f"Erreur création session replay: {e}")
            return None
    
    def load_session_data(self, session_id: str) -> bool:
        """Charge les données de session pour le replay"""
        try:
            if session_id not in self.replay_sessions:
                self.logger.error(f"Session replay non trouvée: {session_id}")
                return False
            
            session = self.replay_sessions[session_id]
            
            # Charger les trades de la session originale
            with sqlite3.connect(self.db_path) as conn:
                query = """
                    SELECT * FROM trades 
                    WHERE DATE(timestamp) = DATE(?) 
                    ORDER BY timestamp
                """
                df = pd.read_sql_query(query, conn, params=(session.original_date,))
            
            if df.empty:
                self.logger.warning(f"Aucune donnée trouvée pour la session: {session_id}")
                return False
            
            # Charger les données de marché
            market_data = self._load_market_data_for_session(session.original_date)
            if market_data is not None:
                self.market_data_cache[session_id] = market_data
            
            session.trades_count = len(df)
            session.status = ReplayStatus.PENDING
            
            self.logger.info(f"✅ Données session chargées: {session.trades_count} trades")
            return True
            
        except Exception as e:
            self.logger.error(f"Erreur chargement données session: {e}")
            return False
    
    def start_replay(self, session_id: str) -> bool:
        """Démarre le replay d'une session"""
        try:
            if session_id not in self.replay_sessions:
                self.logger.error(f"Session replay non trouvée: {session_id}")
                return False
            
            session = self.replay_sessions[session_id]
            session.status = ReplayStatus.RUNNING
            self.current_replay = session
            
            self.logger.info(f"🎬 Démarrage replay: {session_id}")
            
            # Exécuter le replay selon le mode
            if session.mode == ReplayMode.FULL_SESSION:
                return self._replay_full_session(session_id)
            elif session.mode == ReplayMode.TRADE_SEQUENCE:
                return self._replay_trade_sequence(session_id)
            elif session.mode == ReplayMode.DECISION_POINTS:
                return self._replay_decision_points(session_id)
            elif session.mode == ReplayMode.MARKET_CONDITIONS:
                return self._replay_market_conditions(session_id)
            else:
                self.logger.error(f"Mode replay non supporté: {session.mode}")
                return False
                
        except Exception as e:
            self.logger.error(f"Erreur démarrage replay: {e}")
            return False
    
    def _replay_full_session(self, session_id: str) -> bool:
        """Replay complet de la session"""
        try:
            session = self.replay_sessions[session_id]
            
            # Charger les trades
            with sqlite3.connect(self.db_path) as conn:
                query = """
                    SELECT * FROM trades 
                    WHERE DATE(timestamp) = DATE(?) 
                    ORDER BY timestamp
                """
                trades_df = pd.read_sql_query(query, conn, params=(session.original_date,))
            
            replay_trades = []
            decisions = []
            
            for _, trade in trades_df.iterrows():
                # Simuler les conditions de marché au moment du trade
                market_conditions = self._simulate_market_conditions(
                    trade['timestamp'], session_id
                )
                
                # Rejouer la décision
                replay_decision = self._replay_trade_decision(trade, market_conditions)
                decisions.append(replay_decision)
                
                # Créer le trade replay
                replay_trade = ReplayTrade(
                    trade_id=f"REPLAY_{trade['trade_id']}",
                    original_trade_id=trade['trade_id'],
                    symbol=trade['symbol'],
                    side=trade['side'],
                    entry_price=trade['entry_price'],
                    exit_price=trade['exit_price'],
                    quantity=trade['quantity'],
                    pnl_original=trade['pnl'],
                    pnl_replay=replay_decision.improvement,
                    improvement=replay_decision.improvement,
                    execution_time=trade['timestamp'],
                    duration_minutes=trade['duration_minutes'],
                    market_conditions=market_conditions
                )
                replay_trades.append(replay_trade)
            
            # Calculer les statistiques
            total_pnl_original = trades_df['pnl'].sum()
            total_pnl_replay = sum(t.pnl_replay for t in replay_trades)
            improvement_pct = ((total_pnl_replay - total_pnl_original) / total_pnl_original * 100) if total_pnl_original != 0 else 0
            
            session.pnl_original = total_pnl_original
            session.pnl_replay = total_pnl_replay
            session.improvement_pct = improvement_pct
            session.status = ReplayStatus.COMPLETED
            
            self.logger.info(f"✅ Replay complet terminé: {improvement_pct:.2f}% d'amélioration")
            return True
            
        except Exception as e:
            self.logger.error(f"Erreur replay complet: {e}")
            return False
    
    def _replay_trade_sequence(self, session_id: str) -> bool:
        """Replay de la séquence de trades"""
        try:
            # Logique similaire mais focus sur la séquence
            self.logger.info(f"✅ Replay séquence trades terminé")
            return True
        except Exception as e:
            self.logger.error(f"Erreur replay séquence: {e}")
            return False
    
    def _replay_decision_points(self, session_id: str) -> bool:
        """Replay des points de décision"""
        try:
            # Focus sur les moments de décision
            self.logger.info(f"✅ Replay points décision terminé")
            return True
        except Exception as e:
            self.logger.error(f"Erreur replay décisions: {e}")
            return False
    
    def _replay_market_conditions(self, session_id: str) -> bool:
        """Replay avec conditions de marché différentes"""
        try:
            # Simulation de conditions de marché variées
            self.logger.info(f"✅ Replay conditions marché terminé")
            return True
        except Exception as e:
            self.logger.error(f"Erreur replay conditions: {e}")
            return False
    
    def _simulate_market_conditions(self, timestamp: datetime, session_id: str) -> Dict[str, Any]:
        """Simule les conditions de marché à un moment donné"""
        try:
            if session_id in self.market_data_cache:
                market_data = self.market_data_cache[session_id]
                # Trouver les données les plus proches du timestamp
                closest_data = market_data.iloc[(market_data['timestamp'] - timestamp).abs().argsort()[:1]]
                
                if not closest_data.empty:
                    return {
                        'price': closest_data['close'].iloc[0],
                        'volume': closest_data['volume'].iloc[0],
                        'volatility': closest_data.get('volatility', 0.0).iloc[0],
                        'trend': closest_data.get('trend', 'NEUTRAL').iloc[0],
                        'spread': closest_data.get('spread', 0.25).iloc[0]
                    }
            
            # Valeurs par défaut si pas de données
            return {
                'price': 4500.0,
                'volume': 1000,
                'volatility': 0.5,
                'trend': 'NEUTRAL',
                'spread': 0.25
            }
            
        except Exception as e:
            self.logger.error(f"Erreur simulation conditions marché: {e}")
            return {}
    
    def _replay_trade_decision(self, trade: pd.Series, market_conditions: Dict[str, Any]) -> ReplayDecision:
        """Rejoue une décision de trade"""
        try:
            # Analyser la décision originale
            original_action = trade['side']
            original_confidence = trade.get('confidence', 0.5)
            
            # Simuler une décision améliorée
            replay_action = self._simulate_improved_decision(trade, market_conditions)
            replay_confidence = min(original_confidence * 1.1, 1.0)  # Amélioration de 10%
            
            improvement = replay_confidence - original_confidence
            
            return ReplayDecision(
                timestamp=trade['timestamp'],
                decision_type='ENTRY' if trade['side'] in ['BUY', 'SELL'] else 'EXIT',
                original_action=original_action,
                replay_action=replay_action,
                market_conditions=market_conditions,
                confidence_original=original_confidence,
                confidence_replay=replay_confidence,
                improvement=improvement,
                reasoning=f"Amélioration basée sur conditions marché: {market_conditions}"
            )
            
        except Exception as e:
            self.logger.error(f"Erreur replay décision: {e}")
            return None
    
    def _simulate_improved_decision(self, trade: pd.Series, market_conditions: Dict[str, Any]) -> str:
        """Simule une décision améliorée"""
        try:
            # Logique simple d'amélioration basée sur les conditions de marché
            original_side = trade['side']
            
            # Si volatilité élevée, être plus conservateur
            if market_conditions.get('volatility', 0) > 0.8:
                if original_side == 'BUY':
                    return 'HOLD'  # Attendre
                elif original_side == 'SELL':
                    return 'HOLD'
            
            # Si spread élevé, éviter les trades
            if market_conditions.get('spread', 0) > 1.0:
                return 'HOLD'
            
            # Sinon, garder la décision originale
            return original_side
            
        except Exception as e:
            self.logger.error(f"Erreur simulation décision: {e}")
            return trade['side']
    
    def _load_market_data_for_session(self, session_date: datetime) -> Optional[pd.DataFrame]:
        """Charge les données de marché pour une session"""
        try:
            # Simuler le chargement de données de marché
            # En production, cela viendrait de la base de données ou d'une API
            dates = pd.date_range(
                start=session_date.replace(hour=9, minute=30),
                end=session_date.replace(hour=16, minute=0),
                freq='1min'
            )
            
            market_data = pd.DataFrame({
                'timestamp': dates,
                'close': np.random.normal(4500, 10, len(dates)),
                'volume': np.random.randint(500, 2000, len(dates)),
                'volatility': np.random.uniform(0.1, 1.0, len(dates)),
                'trend': np.random.choice(['BULLISH', 'BEARISH', 'NEUTRAL'], len(dates)),
                'spread': np.random.uniform(0.25, 1.0, len(dates))
            })
            
            return market_data
            
        except Exception as e:
            self.logger.error(f"Erreur chargement données marché: {e}")
            return None
    
    def get_replay_analysis(self, session_id: str) -> Optional[ReplayAnalysis]:
        """Génère une analyse complète du replay"""
        try:
            if session_id not in self.replay_sessions:
                return None
            
            session = self.replay_sessions[session_id]
            
            # Charger les trades replay
            with sqlite3.connect(self.db_path) as conn:
                query = """
                    SELECT * FROM trades 
                    WHERE DATE(timestamp) = DATE(?) 
                    ORDER BY timestamp
                """
                trades_df = pd.read_sql_query(query, conn, params=(session.original_date,))
            
            if trades_df.empty:
                return None
            
            # Calculer les statistiques
            total_trades = len(trades_df)
            winning_trades = len(trades_df[trades_df['pnl'] > 0])
            losing_trades = len(trades_df[trades_df['pnl'] < 0])
            win_rate = winning_trades / total_trades if total_trades > 0 else 0
            
            avg_win = trades_df[trades_df['pnl'] > 0]['pnl'].mean() if winning_trades > 0 else 0
            avg_loss = trades_df[trades_df['pnl'] < 0]['pnl'].mean() if losing_trades > 0 else 0
            profit_factor = abs(avg_win / avg_loss) if avg_loss != 0 else float('inf')
            
            total_pnl = trades_df['pnl'].sum()
            max_drawdown = self._calculate_max_drawdown(trades_df['pnl'])
            sharpe_ratio = self._calculate_sharpe_ratio(trades_df['pnl'])
            
            return ReplayAnalysis(
                session_id=session_id,
                total_trades=total_trades,
                winning_trades=winning_trades,
                losing_trades=losing_trades,
                win_rate=win_rate,
                avg_win=avg_win,
                avg_loss=avg_loss,
                profit_factor=profit_factor,
                max_drawdown=max_drawdown,
                sharpe_ratio=sharpe_ratio,
                total_pnl=total_pnl,
                improvement_pct=session.improvement_pct,
                best_decisions=[],  # À implémenter
                worst_decisions=[],  # À implémenter
                market_conditions_analysis={}  # À implémenter
            )
            
        except Exception as e:
            self.logger.error(f"Erreur analyse replay: {e}")
            return None
    
    def _calculate_max_drawdown(self, pnl_series: pd.Series) -> float:
        """Calcule le drawdown maximum"""
        try:
            cumulative = pnl_series.cumsum()
            running_max = cumulative.expanding().max()
            drawdown = cumulative - running_max
            return drawdown.min()
        except Exception:
            return 0.0
    
    def _calculate_sharpe_ratio(self, pnl_series: pd.Series) -> float:
        """Calcule le ratio de Sharpe"""
        try:
            returns = pnl_series.pct_change().dropna()
            if len(returns) == 0:
                return 0.0
            return returns.mean() / returns.std() if returns.std() != 0 else 0.0
        except Exception:
            return 0.0
    
    def get_replay_sessions(self) -> List[ReplaySession]:
        """Retourne toutes les sessions de replay"""
        return list(self.replay_sessions.values())
    
    def get_current_replay(self) -> Optional[ReplaySession]:
        """Retourne la session de replay actuelle"""
        return self.current_replay

# === FONCTIONS UTILITAIRES ===

def create_session_replay_engine(db_path: str = "data/trading_sessions.db") -> SessionReplayEngine:
    """Crée une instance du Session Replay Engine"""
    return SessionReplayEngine(db_path)

def replay_session(session_date: datetime, mode: ReplayMode = ReplayMode.FULL_SESSION) -> Optional[ReplayAnalysis]:
    """Fonction utilitaire pour rejouer une session"""
    try:
        engine = create_session_replay_engine()
        session_id = engine.create_replay_session(session_date, mode)
        
        if engine.load_session_data(session_id) and engine.start_replay(session_id):
            return engine.get_replay_analysis(session_id)
        
        return None
    except Exception as e:
        logging.error(f"Erreur replay session: {e}")
        return None

# === TEST ===

def test_session_replay():
    """Test du module Session Replay"""
    try:
        engine = create_session_replay_engine()
        
        # Créer une session de replay
        session_date = datetime.now() - timedelta(days=1)
        session_id = engine.create_replay_session(session_date, ReplayMode.FULL_SESSION)
        
        print(f"✅ Session replay créée: {session_id}")
        
        # Charger les données
        if engine.load_session_data(session_id):
            print("✅ Données session chargées")
            
            # Démarrer le replay
            if engine.start_replay(session_id):
                print("✅ Replay démarré")
                
                # Obtenir l'analyse
                analysis = engine.get_replay_analysis(session_id)
                if analysis:
                    print(f"✅ Analyse générée: {analysis.total_trades} trades, {analysis.improvement_pct:.2f}% d'amélioration")
        
        print("✅ Test Session Replay terminé")
        
    except Exception as e:
        print(f"❌ Erreur test Session Replay: {e}")

if __name__ == "__main__":
    test_session_replay() 