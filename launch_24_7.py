#!/usr/bin/env python3
"""
🚀 LANCEUR 24/7 MIA_IA_SYSTEM - SYSTÈME DE TRADING AUTOMATISÉ
=============================================================

Lanceur principal pour le système de trading automatisé 24/7 avec :
- Intégration complète des modules core/ (nouveaux)
- Gestion intelligente des horaires de marché
- Paper Trading avec données réelles IBKR
- ML Ensemble + Gamma Cycles intégrés
- Risk Management avancé
- Monitoring temps réel

Auteur: MIA_IA_SYSTEM
Version: 3.0.0 Final
Date: Janvier 2025
"""

import asyncio
import sys
import argparse
import signal
import time
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any, Optional
import pytz

# Ajouter le chemin du projet
sys.path.append(str(Path(__file__).parent))

# ✅ IMPORTS NOUVEAUX MODULES CORE/
from core.logger import get_logger
from core.config_manager import AutomationConfig, create_paper_trading_config, create_production_config

# ✅ IMPORTS CORE MODULES AVEC GESTION D'ERREURS
try:
    from core.signal_explainer import create_signal_explainer
    SIGNAL_EXPLAINER_AVAILABLE = True
except ImportError:
    SIGNAL_EXPLAINER_AVAILABLE = False
    print("⚠️ Signal Explainer non disponible")

try:
    from core.catastrophe_monitor import create_catastrophe_monitor
    CATASTROPHE_MONITOR_AVAILABLE = True
    print("✅ Catastrophe Monitor disponible")
except ImportError:
    CATASTROPHE_MONITOR_AVAILABLE = False
    print("⚠️ Catastrophe Monitor non disponible")

try:
    from core.lessons_learned_analyzer import create_lessons_learned_analyzer
    LESSONS_LEARNED_AVAILABLE = True
except ImportError:
    LESSONS_LEARNED_AVAILABLE = False
    print("⚠️ Lessons Learned Analyzer non disponible")

try:
    from core.session_analyzer import create_session_analyzer
    SESSION_ANALYZER_AVAILABLE = True
except ImportError:
    SESSION_ANALYZER_AVAILABLE = False
    print("⚠️ Session Analyzer non disponible")

try:
    from core.mentor_system import create_mentor_system
    MENTOR_SYSTEM_AVAILABLE = True
except ImportError:
    MENTOR_SYSTEM_AVAILABLE = False
    print("⚠️ Mentor System non disponible")

# ✅ IBKR SUPPRIMÉ - Mode simulation uniquement
print("📊 Mode simulation - IBKR complètement supprimé du système")

# ✅ IMPORTS MODULES EXISTANTS
try:
    from strategies.signal_generator import SignalGenerator, get_signal_now
    SIGNAL_GENERATOR_AVAILABLE = True
except ImportError:
    SIGNAL_GENERATOR_AVAILABLE = False
    print("⚠️ SignalGenerator non disponible")

try:
    from ml.ensemble_filter import MLEnsembleFilter
    ML_ENSEMBLE_AVAILABLE = True
except ImportError:
    ML_ENSEMBLE_AVAILABLE = False
    print("⚠️ ML Ensemble Filter non disponible")

try:
    from ml.gamma_cycles import GammaCyclesAnalyzer, GammaCycleConfig
    GAMMA_CYCLES_AVAILABLE = True
except ImportError:
    GAMMA_CYCLES_AVAILABLE = False
    print("⚠️ Gamma Cycles Analyzer non disponible")

try:
    from features.confluence_analyzer import ConfluenceAnalyzer
    CONFLUENCE_AVAILABLE = True
except ImportError:
    CONFLUENCE_AVAILABLE = False
    print("⚠️ Confluence Analyzer non disponible")

logger = get_logger(__name__)

class Launch24_7System:
    """
    🚀 SYSTÈME LANCEUR 24/7 COMPLET
    Intégration de tous les modules core/ mis à jour
    """
    
    def __init__(self, config: AutomationConfig):
        self.config = config
        self.is_running = False
        self.shutdown_requested = False
        
        # Setup logging
        self.logger = get_logger("Launch24_7")
        
        # Initialize core modules
        self._initialize_core_modules()
        
        # Initialize trading modules
        self._initialize_trading_modules()
        
        # Setup signal handlers
        self._setup_signal_handlers()
        
        self.logger.info("🚀 Launch24_7System initialisé avec modules core/")
    
    def _initialize_core_modules(self):
        """Initialisation des modules core/"""
        # Signal Explainer
        if SIGNAL_EXPLAINER_AVAILABLE:
            try:
                self.signal_explainer = create_signal_explainer()
                self.logger.info("✅ Signal Explainer initialisé")
            except Exception as e:
                self.logger.warning(f"⚠️ Erreur init Signal Explainer: {e}")
                self.signal_explainer = None
        else:
            self.signal_explainer = None
        
        # Catastrophe Monitor
        if CATASTROPHE_MONITOR_AVAILABLE:
            try:
                catastrophe_config = {
                    'daily_loss_limit': getattr(self.config, 'daily_loss_limit', 500.0),
                    'max_position_size': getattr(self.config, 'max_position_size', 2),
                    'max_consecutive_losses': 5,
                    'account_balance_min': 1000.0
                }
                self.catastrophe_monitor = create_catastrophe_monitor(catastrophe_config)
                self.logger.info("✅ Catastrophe Monitor initialisé")
            except Exception as e:
                self.logger.warning(f"⚠️ Erreur init Catastrophe Monitor: {e}")
                self.catastrophe_monitor = None
        else:
            self.catastrophe_monitor = None
        
        # Lessons Learned Analyzer
        if LESSONS_LEARNED_AVAILABLE:
            try:
                self.lessons_learned_analyzer = create_lessons_learned_analyzer()
                self.logger.info("✅ Lessons Learned Analyzer initialisé")
            except Exception as e:
                self.logger.warning(f"⚠️ Erreur init Lessons Learned Analyzer: {e}")
                self.lessons_learned_analyzer = None
        else:
            self.lessons_learned_analyzer = None
        
        # Session Analyzer
        if SESSION_ANALYZER_AVAILABLE:
            try:
                self.session_analyzer = create_session_analyzer()
                self.logger.info("✅ Session Analyzer initialisé")
            except Exception as e:
                self.logger.warning(f"⚠️ Erreur init Session Analyzer: {e}")
                self.session_analyzer = None
        else:
            self.session_analyzer = None
        
        # Data Integrity Validator (pas encore implémenté)
        self.data_validator = None
        
        # Mentor System
        if MENTOR_SYSTEM_AVAILABLE:
            try:
                discord_webhook_url = "https://discordapp.com/api/webhooks/1389206555282640987/v0WvrD3ntDkwGJIyxRh0EEAFNoh1NpSY8Oloxy8tWMZjsFGRed_OYpG1zaSdP2dWH2j7"
                self.mentor_system = create_mentor_system(discord_webhook_url)
                self.logger.info("✅ Mentor System initialisé")
            except Exception as e:
                self.logger.warning(f"⚠️ Erreur init Mentor System: {e}")
                self.mentor_system = None
        else:
            self.mentor_system = None
    
    def _initialize_trading_modules(self):
        """Initialisation des modules de trading"""
        # Signal Generator
        if SIGNAL_GENERATOR_AVAILABLE:
            self.signal_generator = SignalGenerator()
            self.logger.info("✅ Signal Generator initialisé")
        else:
            self.signal_generator = None
            self.logger.warning("⚠️ Signal Generator non disponible")
        
        # ML Ensemble Filter
        if ML_ENSEMBLE_AVAILABLE:
            try:
                self.ml_filter = MLEnsembleFilter()
                self.logger.info("✅ ML Ensemble Filter initialisé")
            except Exception as e:
                self.logger.warning(f"⚠️ Erreur init ML Ensemble: {e}")
                self.ml_filter = None
        else:
            self.ml_filter = None
        
        # Gamma Cycles Analyzer
        if GAMMA_CYCLES_AVAILABLE:
            try:
                gamma_config = GammaCycleConfig()
                self.gamma_analyzer = GammaCyclesAnalyzer(gamma_config)
                self.logger.info("✅ Gamma Cycles Analyzer initialisé")
            except Exception as e:
                self.logger.warning(f"⚠️ Erreur init Gamma Cycles: {e}")
                self.gamma_analyzer = None
        else:
            self.gamma_analyzer = None
        
        # Confluence Analyzer
        if CONFLUENCE_AVAILABLE:
            try:
                self.confluence_analyzer = ConfluenceAnalyzer()
                self.logger.info("✅ Confluence Analyzer initialisé")
            except Exception as e:
                self.logger.warning(f"⚠️ Erreur init Confluence: {e}")
                self.confluence_analyzer = None
        else:
            self.confluence_analyzer = None
    
    def _setup_signal_handlers(self):
        """Configuration des gestionnaires de signaux"""
        def signal_handler(signum, frame):
            self.logger.info(f"🛑 Signal {signum} reçu - Arrêt demandé")
            self.shutdown_requested = True
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    def _ny_hours_open(self) -> bool:
        """Vérifier si les heures de marché NY sont ouvertes"""
        try:
            ny = pytz.timezone("America/New_York")
            now = datetime.now(ny)
            market_start = now.replace(hour=9, minute=30, second=0, microsecond=0)
            market_end = now.replace(hour=16, minute=0, second=0, microsecond=0)
            
            return market_start <= now <= market_end
        except Exception as e:
            self.logger.warning(f"⚠️ Erreur vérification horaires NY: {e}")
            return False
    
    def _is_weekend(self) -> bool:
        """Vérifier si c'est le weekend"""
        ny = pytz.timezone("America/New_York")
        now = datetime.now(ny)
        return now.weekday() >= 5
    
    def _get_market_status(self) -> str:
        """Déterminer le statut du marché"""
        if self._is_weekend():
            return "WEEKEND"
        elif not self._ny_hours_open():
            return "AFTER_HOURS"
        else:
            return "OPEN"
    
    async def _connect_ibkr(self) -> bool:
        """IBKR supprimé - Mode simulation uniquement"""
        self.logger.info("📊 IBKR supprimé - Mode simulation uniquement")
        self.ibkr = None
        return False
    
    async def _validate_system(self) -> bool:
        """Validation complète du système"""
        self.logger.info("🔍 Validation système...")
        
        # Vérifier modules core
        core_modules = [
            ("Signal Explainer", self.signal_explainer),
            ("Catastrophe Monitor", self.catastrophe_monitor),
            ("Lessons Learned", self.lessons_learned_analyzer),
            ("Session Analyzer", self.session_analyzer),
            ("Data Validator", self.data_validator),
            ("Mentor System", self.mentor_system)
        ]
        
        for name, module in core_modules:
            if module:
                self.logger.info(f"  ✅ {name}")
            else:
                self.logger.warning(f"  ⚠️ {name} non disponible")
        
        # Vérifier modules trading
        trading_modules = [
            ("Signal Generator", self.signal_generator),
            ("ML Ensemble", self.ml_filter),
            ("Gamma Cycles", self.gamma_analyzer),
            ("Confluence Analyzer", self.confluence_analyzer)
        ]
        
        for name, module in trading_modules:
            if module:
                self.logger.info(f"  ✅ {name}")
            else:
                self.logger.warning(f"  ⚠️ {name} non disponible")
        
        # Vérifier statut marché
        market_status = self._get_market_status()
        self.logger.info(f"  📊 Statut marché: {market_status}")
        
        return True
    
    async def _run_trading_loop(self):
        """Boucle principale de trading"""
        self.logger.info("🔄 Démarrage boucle trading 24/7...")
        
        last_health_check = time.time()
        last_stats_update = time.time()
        
        while self.is_running and not self.shutdown_requested:
            try:
                current_time = time.time()
                
                # Health check périodique
                if current_time - last_health_check > 30:  # 30 secondes
                    await self._health_check()
                    last_health_check = current_time
                
                # Update stats périodique
                if current_time - last_stats_update > 60:  # 1 minute
                    await self._update_stats()
                    last_stats_update = current_time
                
                # Vérifier statut marché
                market_status = self._get_market_status()
                
                if market_status == "WEEKEND":
                    self.logger.info("📅 Weekend - Mode simulation")
                    await asyncio.sleep(60)
                    continue
                
                # Récupérer données marché
                market_data = await self._get_market_data()
                if not market_data:
                    await asyncio.sleep(1)
                    continue
                
                # Validation données
                if self.data_validator:
                    issues = self.data_validator.validate_market_data(market_data)
                    critical_issues = [i for i in issues if i.severity == 'critical']
                    if critical_issues:
                        self.logger.warning(f"🚨 Données corrompues: {len(critical_issues)} erreurs")
                        await asyncio.sleep(1)
                        continue
                
                # Générer signal
                signal = await self._generate_signal(market_data)
                if not signal:
                    await asyncio.sleep(0.1)
                    continue
                
                # Appliquer filtres
                if not await self._apply_filters(signal, market_data):
                    await asyncio.sleep(0.1)
                    continue
                
                # Exécuter trade
                await self._execute_trade(signal, market_data)
                
                # Pause courte
                await asyncio.sleep(0.05)
                
            except Exception as e:
                self.logger.error(f"❌ Erreur boucle trading: {e}")
                await asyncio.sleep(1)
    
    async def _get_market_data(self):
        """Récupération données marché"""
        try:
            if self.ibkr:
                # Données réelles IBKR
                tick_data = await self.ibkr.get_market_data("ES")
                return tick_data
            else:
                # Simulation
                return {
                    'symbol': 'ES',
                    'last': 4500.0 + (time.time() % 10 - 5),
                    'bid': 4499.75,
                    'ask': 4500.25,
                    'volume': 1000,
                    'timestamp': datetime.now()
                }
        except Exception as e:
            self.logger.error(f"Erreur récupération données: {e}")
            return None
    
    async def _generate_signal(self, market_data):
        """Génération signal"""
        try:
            if self.signal_generator:
                return self.signal_generator.generate_signal(market_data)
            else:
                # Simulation basique
                import random
                if random.random() > 0.8:  # 20% chance de signal
                    return {
                        'signal_type': 'LONG' if random.random() > 0.5 else 'SHORT',
                        'confidence': random.uniform(0.6, 0.9),
                        'timestamp': datetime.now()
                    }
                return None
        except Exception as e:
            self.logger.error(f"Erreur génération signal: {e}")
            return None
    
    async def _apply_filters(self, signal, market_data):
        """Application des filtres"""
        try:
            # Filtre ML
            if self.ml_filter:
                features = {
                    'confluence_score': signal.get('confidence', 0.5),
                    'momentum_flow': 0.5,
                    'trend_alignment': 0.5,
                    'volume_profile': 0.5
                }
                ml_result = self.ml_filter.predict_signal_quality(features)
                if not ml_result.signal_approved:
                    return False
            
            # Filtre Gamma Cycles
            if self.gamma_analyzer:
                gamma_analysis = self.gamma_analyzer.analyze_gamma_cycle()
                if gamma_analysis.adjustment_factor < 0.8:
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Erreur application filtres: {e}")
            return False
    
    async def _execute_trade(self, signal, market_data):
        """Exécution trade"""
        try:
            signal_type = signal.get('signal_type', 'NO_SIGNAL')
            confidence = signal.get('confidence', 0.0)
            
            self.logger.info(f"📈 Signal: {signal_type} @ {market_data.get('last', 0):.2f} "
                           f"(conf: {confidence:.2f})")
            
            if not self.ibkr:
                self.logger.info("⚠️ Mode simulation - pas d'exécution réelle")
                return
            
            # Exécution réelle IBKR
            action = "BUY" if signal_type == "LONG" else "SELL"
            order_result = await self.ibkr.place_order(
                symbol="ES",
                action=action,
                quantity=1,
                order_type="MKT"
            )
            
            if order_result.success:
                self.logger.info(f"✅ Trade exécuté: {order_result.order_id}")
            else:
                self.logger.error(f"❌ Échec exécution: {order_result.error}")
                
        except Exception as e:
            self.logger.error(f"Erreur exécution trade: {e}")
    
    async def _health_check(self):
        """Health check système"""
        try:
            # Vérifier connexion IBKR
            if self.ibkr:
                is_connected = await self.ibkr.is_connected()
                if not is_connected:
                    self.logger.warning("⚠️ Connexion IBKR perdue")
            
            # Vérifier modules
            if not self.signal_generator:
                self.logger.warning("⚠️ Signal Generator indisponible")
            
        except Exception as e:
            self.logger.error(f"Erreur health check: {e}")
    
    async def _update_stats(self):
        """Mise à jour statistiques"""
        try:
            market_status = self._get_market_status()
            self.logger.info(f"📊 Stats: Marché={market_status}, "
                           f"Modules={sum([bool(m) for m in [self.signal_generator, self.ml_filter, self.gamma_analyzer]])}/3")
        except Exception as e:
            self.logger.error(f"Erreur update stats: {e}")
    
    async def start(self):
        """Démarrage système"""
        try:
            self.logger.info("🚀 === DÉMARRAGE LANCEUR 24/7 ===")
            
            # Validation système
            await self._validate_system()
            
            # IBKR supprimé - Mode simulation uniquement
            await self._connect_ibkr()
            self.logger.info("📊 Mode simulation - IBKR complètement supprimé")
            
            # Démarrage boucle principale
            self.is_running = True
            await self._run_trading_loop()
            
        except Exception as e:
            self.logger.error(f"❌ Erreur démarrage: {e}")
            raise
    
    async def stop(self):
        """Arrêt système"""
        self.logger.info("🛑 Arrêt système...")
        self.shutdown_requested = True
        self.is_running = False
        
        # IBKR supprimé - rien à fermer
        
        self.logger.info("✅ Système arrêté")

async def main():
    """Fonction principale"""
    parser = argparse.ArgumentParser(description="Lanceur 24/7 MIA_IA_SYSTEM")
    parser.add_argument("--mode", choices=["paper", "live"], default="paper",
                       help="Mode de trading (paper/live)")
    parser.add_argument("--config", type=str, help="Fichier de configuration")
    
    args = parser.parse_args()
    
    print("🚀 === LANCEUR 24/7 MIA_IA_SYSTEM v3.0.0 ===")
    print("💡 Système de trading automatisé avec modules core/")
    print("=" * 50)
    
    # Configuration - Mode simulation uniquement (IBKR supprimé)
    config = create_paper_trading_config()
    print("✅ Mode Simulation activé - IBKR complètement supprimé")
    
    # Création système
    system = Launch24_7System(config)
    
    try:
        # Démarrage
        await system.start()
        
    except KeyboardInterrupt:
        print("\n🛑 Arrêt demandé par utilisateur")
        
    except Exception as e:
        print(f"❌ Erreur système: {e}")
        
    finally:
        # Arrêt propre
        await system.stop()

if __name__ == "__main__":
    asyncio.run(main())
