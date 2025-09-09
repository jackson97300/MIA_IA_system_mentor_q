#!/usr/bin/env python3
"""
🎯 TEST MIA_IA SYSTEM SIMPLIFIÉ - BASÉ SUR DONNÉES RÉELLES
==========================================================

Test simplifié du système MIA_IA basé sur :
- Données IBKR confirmées (ES/NQ/VIX)
- Configuration système réelle
- Test direct des composants

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
from automation_modules.config_manager import AutomationConfig
from core.ibkr_connector import create_ibkr_connector

logger = get_logger(__name__)

class MIA_IA_SimpleTester:
    """Testeur simplifié du système MIA_IA"""
    
    def __init__(self):
        self.config = self._create_simple_config()
        self.ibkr_connector = None
        self.test_results = {}
        
    def _create_simple_config(self) -> AutomationConfig:
        """Configuration simplifiée basée sur la structure réelle"""
        
        config = AutomationConfig()
        
        # Configuration IBKR (attributs directs)
        config.ibkr_host = "127.0.0.1"
        config.ibkr_port = 7496  # Mode réel confirmé (corrigé)
        config.ibkr_client_id = 1
        
        # Configuration trading optimisée
        config.max_position_size = 1           # 1 contrat ES
        config.daily_loss_limit = 200.0        # $200 limite quotidienne
        config.min_signal_confidence = 0.75    # 75% confiance minimum
        config.stop_loss_ticks = 10           # 10 ticks stop loss
        config.take_profit_ratio = 2.0        # 2:1 risk/reward
        config.max_daily_trades = 20          # 20 trades max/jour
        
        # Configuration ML
        config.ml_ensemble_enabled = True
        config.ml_min_confidence = 0.70
        config.gamma_cycles_enabled = True
        
        # Configuration OrderFlow
        config.orderflow_enabled = True
        config.level2_data_enabled = True
        config.volume_threshold = 100
        config.delta_threshold = 0.5
        config.footprint_threshold = 0.7
        
        # Configuration monitoring
        config.performance_update_interval = 30
        config.health_check_interval = 15
        
        return config
    
    async def test_ibkr_connection(self) -> bool:
        """Test connexion IBKR avec données confirmées"""
        try:
            logger.info("🔌 Test connexion IBKR...")
            
            # Créer connecteur IBKR
            ibkr_config = {
                "ibkr_host": self.config.ibkr_host,
                "ibkr_port": self.config.ibkr_port,
                "ibkr_client_id": self.config.ibkr_client_id,
                "simulation_mode": False,
                "require_real_data": True
            }
            
            self.ibkr_connector = create_ibkr_connector(ibkr_config)
            
            # Connexion
            connection_success = await self.ibkr_connector.connect()
            
            if connection_success:
                logger.info("✅ Connexion IBKR réussie")
                logger.info(f"  📡 Host: {self.config.ibkr_host}:{self.config.ibkr_port}")
                logger.info(f"  🆔 Client ID: {self.config.ibkr_client_id}")
                
                # Test données ES
                try:
                    es_data = await self.ibkr_connector.get_market_data("ES")
                    if es_data:
                        logger.info(f"✅ Données ES: {es_data.get('price', 'N/A')}")
                        self.test_results['es_data'] = es_data
                    else:
                        logger.warning("⚠️ Données ES non disponibles")
                except Exception as e:
                    logger.warning(f"⚠️ Erreur données ES: {e}")
                
                # Test données NQ
                try:
                    nq_data = await self.ibkr_connector.get_market_data("NQ")
                    if nq_data:
                        logger.info(f"✅ Données NQ: {nq_data.get('price', 'N/A')}")
                        self.test_results['nq_data'] = nq_data
                    else:
                        logger.warning("⚠️ Données NQ non disponibles")
                except Exception as e:
                    logger.warning(f"⚠️ Erreur données NQ: {e}")
                
                return True
            else:
                logger.error("❌ Échec connexion IBKR")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erreur test IBKR: {e}")
            return False
    
    async def test_orderflow_analysis(self) -> bool:
        """Test analyse OrderFlow"""
        try:
            logger.info("📊 Test analyse OrderFlow...")
            
            if not self.ibkr_connector:
                logger.error("❌ Connecteur IBKR non disponible")
                return False
            
            # Test OrderFlow ES
            try:
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
                logger.warning(f"⚠️ Erreur OrderFlow: {e}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erreur test OrderFlow: {e}")
            return False
    
    def test_configuration(self) -> bool:
        """Test configuration système"""
        try:
            logger.info("⚙️ Test configuration système...")
            
            # Vérifier configuration
            config_valid = self.config.validate()
            
            if config_valid:
                logger.info("✅ Configuration validée")
                logger.info(f"  📦 Position max: {self.config.max_position_size}")
                logger.info(f"  💸 Limite quotidienne: {self.config.daily_loss_limit}$")
                logger.info(f"  🎯 Confiance min: {self.config.min_signal_confidence}")
                logger.info(f"  🛑 Stop Loss: {self.config.stop_loss_ticks} ticks")
                logger.info(f"  ✅ Take Profit: {self.config.take_profit_ratio}:1")
                logger.info(f"  📊 OrderFlow: {'Activé' if self.config.orderflow_enabled else 'Désactivé'}")
                logger.info(f"  🧠 ML Ensemble: {'Activé' if self.config.ml_ensemble_enabled else 'Désactivé'}")
                
                self.test_results['configuration'] = {
                    'max_position_size': self.config.max_position_size,
                    'daily_loss_limit': self.config.daily_loss_limit,
                    'min_signal_confidence': self.config.min_signal_confidence,
                    'stop_loss_ticks': self.config.stop_loss_ticks,
                    'take_profit_ratio': self.config.take_profit_ratio,
                    'orderflow_enabled': self.config.orderflow_enabled,
                    'ml_ensemble_enabled': self.config.ml_ensemble_enabled
                }
                
                return True
            else:
                logger.error("❌ Configuration invalide")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erreur test configuration: {e}")
            return False
    
    def test_monitoring_data(self) -> bool:
        """Test données de monitoring existantes"""
        try:
            logger.info("📊 Test données de monitoring...")
            
            # Vérifier fichier de monitoring
            monitoring_file = "mia_monitor_elite_20250821_040502.csv"
            
            if Path(monitoring_file).exists():
                logger.info(f"✅ Fichier monitoring trouvé: {monitoring_file}")
                
                # Analyser quelques lignes
                with open(monitoring_file, 'r') as f:
                    lines = f.readlines()
                
                if len(lines) > 1:
                    logger.info(f"  📈 {len(lines)-1} cycles de données")
                    
                    # Analyser dernière ligne
                    last_line = lines[-1].strip()
                    if last_line:
                        parts = last_line.split(',')
                        if len(parts) >= 8:
                            es_price = parts[2]
                            nq_price = parts[3]
                            vix_value = parts[4]
                            elite_score = parts[7]
                            signal = parts[8]
                            
                            logger.info(f"  📊 ES: {es_price}")
                            logger.info(f"  📊 NQ: {nq_price}")
                            logger.info(f"  📊 VIX: {vix_value}")
                            logger.info(f"  🎯 Elite Score: {elite_score}")
                            logger.info(f"  🚦 Signal: {signal}")
                            
                            self.test_results['monitoring_data'] = {
                                'es_price': es_price,
                                'nq_price': nq_price,
                                'vix_value': vix_value,
                                'elite_score': elite_score,
                                'signal': signal,
                                'cycles_count': len(lines)-1
                            }
                            
                            return True
                
                logger.warning("⚠️ Fichier monitoring vide ou invalide")
                return False
            else:
                logger.warning(f"⚠️ Fichier monitoring non trouvé: {monitoring_file}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erreur test monitoring: {e}")
            return False
    
    async def test_paper_trading_readiness(self) -> bool:
        """Test préparation Paper Trading"""
        try:
            logger.info("🎯 Test préparation Paper Trading...")
            
            # Vérifier tous les composants
            checks = {
                "IBKR Connection": self.ibkr_connector is not None,
                "Configuration": 'configuration' in self.test_results,
                "ES Data": 'es_data' in self.test_results,
                "NQ Data": 'nq_data' in self.test_results,
                "OrderFlow": 'orderflow_data' in self.test_results,
                "Monitoring": 'monitoring_data' in self.test_results
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
        
        # Test 1: Configuration
        logger.info("\n⚙️ TEST 1: Configuration Système")
        config_success = self.test_configuration()
        test_results["tests"]["configuration"] = config_success
        
        # Test 2: Connexion IBKR
        logger.info("\n🔌 TEST 2: Connexion IBKR")
        ibkr_success = await self.test_ibkr_connection()
        test_results["tests"]["ibkr_connection"] = ibkr_success
        
        # Test 3: OrderFlow
        logger.info("\n📊 TEST 3: Analyse OrderFlow")
        orderflow_success = await self.test_orderflow_analysis()
        test_results["tests"]["orderflow"] = orderflow_success
        
        # Test 4: Monitoring
        logger.info("\n📊 TEST 4: Données Monitoring")
        monitoring_success = self.test_monitoring_data()
        test_results["tests"]["monitoring"] = monitoring_success
        
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
        tester = MIA_IA_SimpleTester()
        
        # Exécuter test complet
        results = await tester.run_complete_test()
        
        # Sauvegarder résultats
        import json
        with open("test_mia_system_simple_results.json", "w") as f:
            json.dump(results, f, default=str, indent=2)
        
        logger.info("💾 Résultats sauvegardés dans test_mia_system_simple_results.json")
        
    except KeyboardInterrupt:
        logger.info("🛑 Test interrompu par l'utilisateur")
    except Exception as e:
        logger.error(f"❌ Erreur test: {e}")

if __name__ == "__main__":
    asyncio.run(main())
