#!/usr/bin/env python3
"""
🎯 TEST MIA_IA SYSTEM OPTIMISÉ - BASÉ SUR DONNÉES RÉELLES
==========================================================

Test optimisé du système MIA_IA basé sur :
- Données IBKR confirmées (ES/NQ/VIX)
- Configuration système analysée
- Monitoring existant
- Paramètres optimaux pour Paper Trading

Auteur: MIA_IA_SYSTEM
Date: 21 Août 2025
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any, Optional

# Ajouter le chemin du projet
sys.path.append(str(Path(__file__).parent))

from core.logger import get_logger
from config.automation_config import AutomationConfig
from execution.simple_trader import MIAAutomationSystem
from core.ibkr_connector import create_ibkr_connector

logger = get_logger(__name__)

class MIA_IA_SystemTester:
    """Testeur optimisé du système MIA_IA"""
    
    def __init__(self):
        self.config = self._create_optimized_config()
        self.ibkr_connector = None
        self.trading_system = None
        self.test_results = {}
        
    def _create_optimized_config(self) -> AutomationConfig:
        """Configuration optimisée basée sur l'analyse du système"""
        
        # Configuration IBKR confirmée
        ibkr_config = {
            "host": "127.0.0.1",
            "port": 7496,  # Mode réel confirmé
            "client_id": 1,
            "timeout_seconds": 30
        }
        
        # Configuration trading optimisée
        trading_config = {
            "max_position_size": 1,           # 1 contrat ES
            "daily_loss_limit": 200.0,        # $200 limite quotidienne
            "min_signal_confidence": 0.75,    # 75% confiance minimum
            "stop_loss_ticks": 10,           # 10 ticks stop loss
            "take_profit_ratio": 2.0,        # 2:1 risk/reward
            "max_daily_trades": 20,          # 20 trades max/jour
            "primary_instrument": "ES",      # Focus ES
            "tick_size": 0.25,              # ES tick size
            "tick_value": 12.50             # ES tick value
        }
        
        # Configuration ML optimisée
        ml_config = {
            "ensemble_enabled": True,
            "gamma_cycles_enabled": True,
            "min_confidence": 0.70,
            "cache_enabled": True,
            "cache_ttl": 60
        }
        
        # Configuration OrderFlow
        orderflow_config = {
            "orderflow_enabled": True,
            "level2_data_enabled": True,
            "volume_threshold": 100,
            "delta_threshold": 0.5,
            "footprint_threshold": 0.7
        }
        
        # Créer configuration complète
        config = AutomationConfig()
        
        # Appliquer configurations
        config.ibkr.host = ibkr_config["host"]
        config.ibkr.port = ibkr_config["port"]
        config.ibkr.client_id = ibkr_config["client_id"]
        config.ibkr.timeout_seconds = ibkr_config["timeout_seconds"]
        
        config.trading.max_position_size = trading_config["max_position_size"]
        config.trading.daily_loss_limit = trading_config["daily_loss_limit"]
        config.trading.min_signal_confidence = trading_config["min_signal_confidence"]
        config.trading.stop_loss_ticks = trading_config["stop_loss_ticks"]
        config.trading.take_profit_ratio = trading_config["take_profit_ratio"]
        config.trading.max_daily_trades = trading_config["max_daily_trades"]
        config.trading.primary_instrument = trading_config["primary_instrument"]
        
        config.ml.ensemble_enabled = ml_config["ensemble_enabled"]
        config.ml.gamma_cycles_enabled = ml_config["gamma_cycles_enabled"]
        config.ml.min_confidence = ml_config["min_confidence"]
        config.ml.cache_enabled = ml_config["cache_enabled"]
        config.ml.cache_ttl = ml_config["cache_ttl"]
        
        config.orderflow_enabled = orderflow_config["orderflow_enabled"]
        config.level2_data_enabled = orderflow_config["level2_data_enabled"]
        config.volume_threshold = orderflow_config["volume_threshold"]
        config.delta_threshold = orderflow_config["delta_threshold"]
        config.footprint_threshold = orderflow_config["footprint_threshold"]
        
        return config
    
    async def test_ibkr_connection(self) -> bool:
        """Test connexion IBKR avec données confirmées"""
        try:
            logger.info("🔌 Test connexion IBKR...")
            
            # Créer connecteur IBKR
            ibkr_config = {
                "ibkr_host": self.config.ibkr.host,
                "ibkr_port": self.config.ibkr.port,
                "ibkr_client_id": self.config.ibkr.client_id,
                "simulation_mode": False,
                "require_real_data": True
            }
            
            self.ibkr_connector = create_ibkr_connector(ibkr_config)
            
            # Connexion
            connection_success = await self.ibkr_connector.connect()
            
            if connection_success:
                logger.info("✅ Connexion IBKR réussie")
                
                # Test données ES
                es_data = await self.ibkr_connector.get_market_data("ES")
                if es_data:
                    logger.info(f"✅ Données ES: {es_data.get('price', 'N/A')}")
                    self.test_results['es_data'] = es_data
                
                # Test données NQ
                nq_data = await self.ibkr_connector.get_market_data("NQ")
                if nq_data:
                    logger.info(f"✅ Données NQ: {nq_data.get('price', 'N/A')}")
                    self.test_results['nq_data'] = nq_data
                
                return True
            else:
                logger.error("❌ Échec connexion IBKR")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erreur test IBKR: {e}")
            return False
    
    async def test_trading_system(self) -> bool:
        """Test système de trading MIA_IA"""
        try:
            logger.info("🤖 Test système de trading MIA_IA...")
            
            # Créer système de trading
            self.trading_system = MIAAutomationSystem(self.config)
            
            # Initialisation
            init_success = await self.trading_system.initialize()
            
            if init_success:
                logger.info("✅ Système de trading initialisé")
                
                # Test génération signaux
                signals = await self.trading_system.generate_signals()
                if signals:
                    logger.info(f"✅ Signaux générés: {len(signals)}")
                    self.test_results['signals'] = signals
                
                # Test risk management
                risk_status = self.trading_system.get_risk_status()
                logger.info(f"✅ Risk management: {risk_status}")
                self.test_results['risk_status'] = risk_status
                
                return True
            else:
                logger.error("❌ Échec initialisation système trading")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erreur test trading: {e}")
            return False
    
    async def test_orderflow_analysis(self) -> bool:
        """Test analyse OrderFlow"""
        try:
            logger.info("📊 Test analyse OrderFlow...")
            
            if not self.ibkr_connector:
                logger.error("❌ Connecteur IBKR non disponible")
                return False
            
            # Test OrderFlow ES
            orderflow_data = await self.ibkr_connector.get_orderflow_market_data("ES")
            
            if orderflow_data:
                logger.info("✅ Données OrderFlow ES récupérées")
                logger.info(f"  📊 Volume: {orderflow_data.get('volume', 0)}")
                logger.info(f"  📈 Delta: {orderflow_data.get('delta', 0)}")
                logger.info(f"  💰 Bid Volume: {orderflow_data.get('bid_volume', 0)}")
                logger.info(f"  💰 Ask Volume: {orderflow_data.get('ask_volume', 0)}")
                
                self.test_results['orderflow_data'] = orderflow_data
                return True
            else:
                logger.warning("⚠️ Données OrderFlow non disponibles")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erreur test OrderFlow: {e}")
            return False
    
    async def test_ml_ensemble(self) -> bool:
        """Test ML Ensemble"""
        try:
            logger.info("🧠 Test ML Ensemble...")
            
            if not self.trading_system:
                logger.error("❌ Système trading non disponible")
                return False
            
            # Test features
            features = {
                "confluence_score": 0.75,
                "momentum_flow": 0.8,
                "trend_alignment": 0.7,
                "volume_profile": 0.6,
                "support_resistance": 0.5,
                "market_regime_score": 0.6,
                "volatility_regime": 0.5,
                "time_factor": 0.5
            }
            
            # Test prédiction
            prediction = await self.trading_system.predict_signal_quality(features)
            
            if prediction:
                logger.info("✅ ML Ensemble fonctionnel")
                logger.info(f"  🎯 Signal approuvé: {prediction.get('signal_approved', False)}")
                logger.info(f"  📊 Confiance: {prediction.get('confidence', 0):.3f}")
                
                self.test_results['ml_prediction'] = prediction
                return True
            else:
                logger.warning("⚠️ ML Ensemble non disponible")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erreur test ML: {e}")
            return False
    
    async def test_paper_trading_readiness(self) -> bool:
        """Test préparation Paper Trading"""
        try:
            logger.info("🎯 Test préparation Paper Trading...")
            
            # Vérifier tous les composants
            checks = {
                "IBKR Connection": self.ibkr_connector is not None,
                "Trading System": self.trading_system is not None,
                "ES Data": 'es_data' in self.test_results,
                "NQ Data": 'nq_data' in self.test_results,
                "OrderFlow": 'orderflow_data' in self.test_results,
                "ML Ensemble": 'ml_prediction' in self.test_results,
                "Risk Management": 'risk_status' in self.test_results
            }
            
            # Afficher résultats
            logger.info("📋 Vérifications Paper Trading:")
            for check, status in checks.items():
                status_icon = "✅" if status else "❌"
                logger.info(f"  {status_icon} {check}")
            
            # Calculer score de préparation
            readiness_score = sum(checks.values()) / len(checks) * 100
            
            logger.info(f"🎯 Score de préparation: {readiness_score:.1f}%")
            
            if readiness_score >= 80:
                logger.info("🚀 SYSTÈME PRÊT POUR PAPER TRADING!")
                return True
            else:
                logger.warning("⚠️ Système nécessite des ajustements")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erreur test préparation: {e}")
            return False
    
    async def run_complete_test(self) -> Dict[str, Any]:
        """Exécution test complet du système MIA_IA"""
        logger.info("🚀 === TEST COMPLET MIA_IA SYSTEM ===")
        logger.info("=" * 50)
        
        test_results = {
            "timestamp": datetime.now(timezone.utc),
            "tests": {},
            "overall_success": False
        }
        
        # Test 1: Connexion IBKR
        logger.info("\n🔌 TEST 1: Connexion IBKR")
        ibkr_success = await self.test_ibkr_connection()
        test_results["tests"]["ibkr_connection"] = ibkr_success
        
        # Test 2: Système Trading
        logger.info("\n🤖 TEST 2: Système Trading")
        trading_success = await self.test_trading_system()
        test_results["tests"]["trading_system"] = trading_success
        
        # Test 3: OrderFlow
        logger.info("\n📊 TEST 3: Analyse OrderFlow")
        orderflow_success = await self.test_orderflow_analysis()
        test_results["tests"]["orderflow"] = orderflow_success
        
        # Test 4: ML Ensemble
        logger.info("\n🧠 TEST 4: ML Ensemble")
        ml_success = await self.test_ml_ensemble()
        test_results["tests"]["ml_ensemble"] = ml_success
        
        # Test 5: Préparation Paper Trading
        logger.info("\n🎯 TEST 5: Préparation Paper Trading")
        paper_ready = await self.test_paper_trading_readiness()
        test_results["tests"]["paper_trading_ready"] = paper_ready
        
        # Résumé final
        logger.info("\n" + "=" * 50)
        logger.info("📊 RÉSUMÉ DES TESTS")
        logger.info("=" * 50)
        
        for test_name, success in test_results["tests"].items():
            status_icon = "✅" if success else "❌"
            logger.info(f"  {status_icon} {test_name}")
        
        # Score global
        success_count = sum(test_results["tests"].values())
        total_tests = len(test_results["tests"])
        success_rate = (success_count / total_tests) * 100
        
        logger.info(f"\n🎯 Score global: {success_count}/{total_tests} ({success_rate:.1f}%)")
        
        if success_rate >= 80:
            logger.info("🚀 SYSTÈME MIA_IA PRÊT POUR PAPER TRADING!")
            test_results["overall_success"] = True
        else:
            logger.warning("⚠️ Système nécessite des corrections")
        
        # Recommandations
        logger.info("\n💡 RECOMMANDATIONS:")
        if test_results["overall_success"]:
            logger.info("  🚀 Lancer Paper Trading: python launch_24_7_orderflow_trading.py --live")
            logger.info("  📊 Monitorer performance en temps réel")
            logger.info("  🛡️ Vérifier risk management")
        else:
            logger.info("  🔧 Corriger les tests échoués")
            logger.info("  🔍 Vérifier configuration IBKR")
            logger.info("  📊 Tester avec données simulées d'abord")
        
        return test_results

async def main():
    """Fonction principale"""
    try:
        # Créer testeur
        tester = MIA_IA_SystemTester()
        
        # Exécuter test complet
        results = await tester.run_complete_test()
        
        # Sauvegarder résultats
        import json
        with open("test_mia_system_results.json", "w") as f:
            json.dump(results, f, default=str, indent=2)
        
        logger.info("💾 Résultats sauvegardés dans test_mia_system_results.json")
        
    except KeyboardInterrupt:
        logger.info("🛑 Test interrompu par l'utilisateur")
    except Exception as e:
        logger.error(f"❌ Erreur test: {e}")

if __name__ == "__main__":
    asyncio.run(main())


