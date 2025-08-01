#!/usr/bin/env python3
"""
🚀 TRADING ENGINE - MIA_IA_SYSTEM
Moteur de trading principal optimisé et modulaire
"""

import sys
import asyncio
import time
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

# Ajouter le chemin du projet
sys.path.append(str(Path(__file__).parent.parent))

from core.logger import get_logger
from .config_manager import AutomationConfig
from .performance_tracker import PerformanceTracker, TradingStats
from .risk_manager import RiskManager
from .confluence_calculator import EnhancedConfluenceCalculator

logger = get_logger(__name__)

class MIAAutomationSystem:
    """Système d'automation principal optimisé"""
    
    def __init__(self, config: AutomationConfig):
        self.config = config
        self.is_running = False
        self.is_connected = False
        
        # Modules spécialisés
        self.performance_tracker = PerformanceTracker()
        self.risk_manager = RiskManager(config)
        self.confluence_calculator = EnhancedConfluenceCalculator()
        
        # État système
        self.current_positions = 0
        self.account_balance = 10000.0  # Simulation
        self.last_health_check = datetime.now()
        self.last_performance_update = datetime.now()
        
        # Validation config
        if not config.validate():
            raise ValueError("Configuration invalide")
        
        logger.info("✅ MIA Automation System initialisé")
    
    async def start(self) -> None:
        """Démarre le système"""
        try:
            logger.info("🚀 Démarrage MIA Automation System")
            
            # Validation pré-trading
            await self._validate_config()
            await self._pre_trading_checks()
            
            # Démarrage boucle principale
            self.is_running = True
            await self._main_trading_loop()
            
        except Exception as e:
            logger.error(f"❌ Erreur démarrage système: {e}")
            await self.emergency_shutdown()
    
    async def stop(self) -> None:
        """Arrête le système"""
        logger.info("🛑 Arrêt MIA Automation System")
        self.is_running = False
        await self._close_all_positions()
    
    async def _validate_config(self) -> None:
        """Valide la configuration"""
        try:
            logger.info("🔧 Validation configuration...")
            
            # Vérifications de base
            assert self.config.max_position_size > 0
            assert self.config.daily_loss_limit > 0
            assert 0.5 <= self.config.min_signal_confidence <= 1.0
            
            logger.info("✅ Configuration validée")
            
        except Exception as e:
            logger.error(f"❌ Configuration invalide: {e}")
            raise
    
    async def _pre_trading_checks(self) -> None:
        """Vérifications pré-trading"""
        try:
            logger.info("🔧 Vérifications pré-trading...")
            
            # Vérification heures trading
            if not self.risk_manager.check_trading_hours():
                logger.warning("⚠️ Hors heures de trading")
                return
            
            # Vérification limites quotidiennes
            if not self.risk_manager.check_daily_loss_limit():
                logger.warning("⚠️ Limite de perte quotidienne atteinte")
                return
            
            if not self.risk_manager.check_daily_trade_limit():
                logger.warning("⚠️ Limite de trades quotidiens atteinte")
                return
            
            logger.info("✅ Vérifications pré-trading OK")
            
        except Exception as e:
            logger.error(f"❌ Erreur vérifications pré-trading: {e}")
            raise
    
    async def _main_trading_loop(self) -> None:
        """Boucle principale de trading"""
        logger.info("🔄 Démarrage boucle principale de trading")
        
        while self.is_running:
            try:
                # Vérification santé système
                await self._health_check()
                
                # Mise à jour performances
                await self._update_performance_stats()
                
                # Récupération données marché
                market_data = await self._get_market_data()
                if market_data is None:
                    await asyncio.sleep(1)
                    continue
                
                # Génération signal
                signal = await self._generate_signal(market_data)
                if signal is None:
                    await self._explain_no_signal(market_data)
                    await asyncio.sleep(1)
                    continue
                
                # Application filtres
                if not await self._apply_filters(signal, market_data):
                    logger.info("⚠️ Signal filtré")
                    await asyncio.sleep(1)
                    continue
                
                # Vérification gestion des risques
                if not self._risk_management_check(signal):
                    logger.info("⚠️ Signal rejeté par risk management")
                    await asyncio.sleep(1)
                    continue
                
                # Exécution trade
                await self._execute_trade(signal, market_data)
                
                # Pause entre cycles
                await asyncio.sleep(1)
                
            except Exception as e:
                logger.error(f"❌ Erreur boucle principale: {e}")
                await asyncio.sleep(5)
    
    async def _generate_signal(self, market_data) -> Optional[object]:
        """Génère un signal de trading"""
        try:
            # Calcul confluence
            confluence = self.confluence_calculator.calculate_enhanced_confluence(market_data)
            
            # Vérification seuil confluence
            if confluence < self.config.confluence_threshold:
                return None
            
            # Création signal
            signal = {
                'direction': 'LONG' if confluence > 0.6 else 'SHORT',
                'confidence': confluence,
                'timestamp': datetime.now(),
                'price': market_data.price,
                'confluence': confluence
            }
            
            self.performance_tracker.add_signal()
            logger.info(f"🎯 Signal généré: {signal['direction']}, Confiance={confluence:.3f}")
            
            return signal
            
        except Exception as e:
            logger.error(f"❌ Erreur génération signal: {e}")
            return None
    
    async def _apply_filters(self, signal, market_data) -> bool:
        """Applique les filtres au signal"""
        try:
            # Filtre confiance
            if not self.risk_manager.check_signal_confidence(signal['confidence']):
                return False
            
            # Filtre ML (simulation)
            if self.config.ml_ensemble_enabled:
                ml_confidence = 0.7 + (signal['confidence'] - 0.5) * 0.6  # Simulation
                if ml_confidence < self.config.ml_min_confidence:
                    self.performance_tracker.add_signal(ml_approved=False)
                    return False
                self.performance_tracker.add_signal(ml_approved=True)
            
            # Filtre Gamma Cycles (simulation)
            if self.config.gamma_cycles_enabled:
                gamma_score = 0.6 + random.uniform(-0.2, 0.2)  # Simulation
                if gamma_score < 0.5:
                    return False
                self.performance_tracker.add_signal(gamma_optimized=True)
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur application filtres: {e}")
            return False
    
    def _risk_management_check(self, signal) -> bool:
        """Vérification gestion des risques"""
        try:
            # Vérification limites
            if not self.risk_manager.check_position_limit():
                return False
            
            if not self.risk_manager.check_daily_loss_limit():
                return False
            
            if not self.risk_manager.check_daily_trade_limit():
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur risk management: {e}")
            return False
    
    async def _execute_trade(self, signal, market_data) -> None:
        """Exécute un trade"""
        try:
            logger.info(f"📈 Exécution trade: {signal['direction']} @ {signal['price']:.2f}")
            
            # Calcul position size
            position_size = self.risk_manager.calculate_position_size(self.account_balance)
            
            # Calcul stop loss et take profit
            stop_loss = self.risk_manager.calculate_stop_loss(signal['price'], signal['direction'])
            take_profit = self.risk_manager.calculate_take_profit(signal['price'], stop_loss, signal['direction'])
            
            # Simulation résultat trade
            self._simulate_trade_result(signal, market_data)
            
            # Mise à jour stats
            self.risk_manager.add_position()
            self.current_positions += 1
            
            logger.info(f"✅ Trade exécuté: Size={position_size}, SL={stop_loss:.2f}, TP={take_profit:.2f}")
            
        except Exception as e:
            logger.error(f"❌ Erreur exécution trade: {e}")
    
    def _simulate_trade_result(self, signal, market_data) -> None:
        """Simule le résultat d'un trade"""
        try:
            # Simulation PnL
            if signal['direction'] == 'LONG':
                pnl = random.uniform(-50, 100)  # Simulation
            else:
                pnl = random.uniform(-50, 100)  # Simulation
            
            is_win = pnl > 0
            
            # Mise à jour stats
            self.performance_tracker.add_trade(pnl, is_win)
            self.risk_manager.add_trade_result(pnl)
            self.risk_manager.remove_position()
            self.current_positions = max(0, self.current_positions - 1)
            
            logger.info(f"📊 Résultat trade: PnL={pnl:.2f}, Win={is_win}")
            
        except Exception as e:
            logger.error(f"❌ Erreur simulation trade: {e}")
    
    async def _get_market_data(self) -> Optional[object]:
        """Récupère les données marché"""
        try:
            # Simulation données marché
            class MarketData:
                def __init__(self):
                    self.price = 4500.0 + random.uniform(-5.0, 5.0)
                    self.volume = random.randint(500, 1500)
                    self.timestamp = datetime.now()
            
            return MarketData()
            
        except Exception as e:
            logger.error(f"❌ Erreur récupération données marché: {e}")
            return None
    
    async def _health_check(self) -> None:
        """Vérification santé système"""
        try:
            now = datetime.now()
            if (now - self.last_health_check).seconds >= self.config.health_check_interval:
                
                # Vérifications de base
                if not self.is_running:
                    logger.warning("⚠️ Système non en cours d'exécution")
                
                if self.current_positions > self.config.max_position_size:
                    logger.warning(f"⚠️ Trop de positions: {self.current_positions}")
                
                self.last_health_check = now
                logger.debug("✅ Health check OK")
                
        except Exception as e:
            logger.error(f"❌ Erreur health check: {e}")
    
    async def _update_performance_stats(self) -> None:
        """Mise à jour des statistiques de performance"""
        try:
            now = datetime.now()
            if (now - self.last_performance_update).seconds >= self.config.performance_update_interval:
                
                summary = self.performance_tracker.get_summary()
                logger.info(f"📊 Performance: WinRate={summary['win_rate']:.1f}%, "
                           f"PnL={summary['total_pnl']:.2f}, Trades={summary['total_trades']}")
                
                self.last_performance_update = now
                
        except Exception as e:
            logger.error(f"❌ Erreur mise à jour performance: {e}")
    
    async def _explain_no_signal(self, market_data) -> None:
        """Explique pourquoi aucun signal"""
        try:
            confluence = self.confluence_calculator.calculate_enhanced_confluence(market_data)
            
            if confluence < self.config.confluence_threshold:
                logger.debug(f"🔍 Pas de signal: Confluence={confluence:.3f} < {self.config.confluence_threshold}")
            
        except Exception as e:
            logger.error(f"❌ Erreur explication signal: {e}")
    
    async def _close_all_positions(self) -> None:
        """Ferme toutes les positions"""
        try:
            if self.current_positions > 0:
                logger.info(f"🛑 Fermeture de {self.current_positions} positions")
                self.current_positions = 0
                self.risk_manager.current_positions = 0
            
        except Exception as e:
            logger.error(f"❌ Erreur fermeture positions: {e}")
    
    async def emergency_shutdown(self) -> None:
        """Arrêt d'urgence"""
        logger.error("🚨 ARRÊT D'URGENCE")
        self.is_running = False
        await self._close_all_positions()
    
    def get_system_status(self) -> Dict[str, Any]:
        """Retourne le statut du système"""
        return {
            'is_running': self.is_running,
            'is_connected': self.is_connected,
            'current_positions': self.current_positions,
            'account_balance': self.account_balance,
            'performance_summary': self.performance_tracker.get_summary(),
            'risk_summary': self.risk_manager.get_risk_summary()
        } 