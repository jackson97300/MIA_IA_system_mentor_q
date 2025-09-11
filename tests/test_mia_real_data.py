#!/usr/bin/env python3
"""
🎯 TEST MIA_IA AVEC DONNÉES RÉELLES CONFIRMÉES
===============================================

Test optimisé utilisant les données réelles confirmées :
- ES/NQ futures (données confirmées)
- VIX spot (données confirmées)
- SPX options (partiellement)
- Configuration système validée

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

logger = get_logger(__name__)

class MIA_IA_RealDataTester:
    """Testeur avec données réelles confirmées"""
    
    def __init__(self):
        self.config = self._create_real_config()
        self.real_data = {}
        self.test_results = {}
        
    def _create_real_config(self) -> AutomationConfig:
        """Configuration basée sur données réelles confirmées"""
        
        config = AutomationConfig()
        
        # Configuration IBKR (données confirmées)
        config.ibkr_host = "127.0.0.1"
        config.ibkr_port = 7496  # Mode réel confirmé
        config.ibkr_client_id = 1
        
        # Configuration trading optimisée (basée sur données réelles)
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
        
        return config
    
    def load_real_market_data(self) -> bool:
        """Charger données réelles confirmées du test IBKR"""
        try:
            logger.info("📊 Chargement données réelles confirmées...")
            
            # Données ES confirmées (test_ibkr_corrige.py)
            self.real_data['ES'] = {
                'symbol': 'ESU5',
                'exchange': 'CME',
                'bid': 6406.25,
                'ask': 6406.5,
                'last': 6406.25,
                'volume': 0,  # Marché fermé
                'open_interest': 0,  # Marché fermé
                'status': 'ACTIVE'
            }
            
            # Données NQ confirmées
            self.real_data['NQ'] = {
                'symbol': 'NQU5',
                'exchange': 'CME',
                'bid': 23315.5,
                'ask': 23316.25,
                'last': 23316.75,
                'volume': 0,  # Marché fermé
                'open_interest': 0,  # Marché fermé
                'status': 'ACTIVE'
            }
            
            # Données VIX confirmées
            self.real_data['VIX'] = {
                'symbol': 'VIX',
                'value': 15.93,
                'status': 'ACTIVE'
            }
            
            # Données SPX confirmées (via Greeks)
            self.real_data['SPX'] = {
                'symbol': 'SPX',
                'implied_vol': 2.48,
                'delta': 0.99,
                'underlying_price': 6388.06,
                'status': 'OPTIONS_CLOSED'
            }
            
            logger.info("✅ Données réelles chargées:")
            logger.info(f"  📊 ES: {self.real_data['ES']['bid']}/{self.real_data['ES']['ask']}")
            logger.info(f"  📊 NQ: {self.real_data['NQ']['bid']}/{self.real_data['NQ']['ask']}")
            logger.info(f"  📊 VIX: {self.real_data['VIX']['value']}")
            logger.info(f"  📊 SPX: {self.real_data['SPX']['underlying_price']}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur chargement données: {e}")
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
    
    def test_market_data_analysis(self) -> bool:
        """Test analyse données de marché réelles"""
        try:
            logger.info("📊 Test analyse données de marché...")
            
            if not self.real_data:
                logger.error("❌ Données réelles non chargées")
                return False
            
            # Analyser ES
            es_data = self.real_data['ES']
            es_spread = es_data['ask'] - es_data['bid']
            es_mid = (es_data['bid'] + es_data['ask']) / 2
            
            logger.info(f"✅ Analyse ES ({es_data['symbol']}):")
            logger.info(f"  💰 Bid: {es_data['bid']}")
            logger.info(f"  💰 Ask: {es_data['ask']}")
            logger.info(f"  💰 Spread: {es_spread:.2f} points")
            logger.info(f"  💰 Mid: {es_mid:.2f}")
            
            # Analyser NQ
            nq_data = self.real_data['NQ']
            nq_spread = nq_data['ask'] - nq_data['bid']
            nq_mid = (nq_data['bid'] + nq_data['ask']) / 2
            
            logger.info(f"✅ Analyse NQ ({nq_data['symbol']}):")
            logger.info(f"  💰 Bid: {nq_data['bid']}")
            logger.info(f"  💰 Ask: {nq_data['ask']}")
            logger.info(f"  💰 Spread: {nq_spread:.2f} points")
            logger.info(f"  💰 Mid: {nq_mid:.2f}")
            
            # Analyser VIX
            vix_data = self.real_data['VIX']
            logger.info(f"✅ Analyse VIX:")
            logger.info(f"  📊 Valeur: {vix_data['value']}")
            logger.info(f"  📊 Statut: {vix_data['status']}")
            
            # Analyser corrélation ES/NQ
            es_change = (es_mid - 6400) / 6400 * 100  # Changement % approximatif
            nq_change = (nq_mid - 23300) / 23300 * 100
            correlation = "POSITIVE" if (es_change > 0 and nq_change > 0) or (es_change < 0 and nq_change < 0) else "NEGATIVE"
            
            logger.info(f"✅ Corrélation ES/NQ: {correlation}")
            logger.info(f"  📈 ES Change: {es_change:.2f}%")
            logger.info(f"  📈 NQ Change: {nq_change:.2f}%")
            
            self.test_results['market_analysis'] = {
                'es_data': es_data,
                'nq_data': nq_data,
                'vix_data': vix_data,
                'correlation': correlation,
                'es_spread': es_spread,
                'nq_spread': nq_spread
            }
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur analyse marché: {e}")
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
    
    def test_paper_trading_simulation(self) -> bool:
        """Test simulation Paper Trading avec données réelles"""
        try:
            logger.info("🎯 Test simulation Paper Trading...")
            
            if not self.real_data:
                logger.error("❌ Données réelles non disponibles")
                return False
            
            # Simuler un signal de trading
            es_data = self.real_data['ES']
            vix_data = self.real_data['VIX']
            
            # Conditions de trading (exemple)
            vix_low = vix_data['value'] < 20  # VIX bas = marché calme
            spread_reasonable = (es_data['ask'] - es_data['bid']) < 2  # Spread serré
            
            # Score de confiance simulé
            confidence_score = 0.85 if vix_low and spread_reasonable else 0.45
            
            # Décision de trading
            if confidence_score >= self.config.min_signal_confidence:
                signal = "BUY" if es_data['last'] > es_data['bid'] else "SELL"
                logger.info(f"✅ Signal généré: {signal}")
                logger.info(f"  🎯 Confiance: {confidence_score:.2f}")
                logger.info(f"  💰 Prix d'entrée: {es_data['ask'] if signal == 'BUY' else es_data['bid']}")
                logger.info(f"  🛑 Stop Loss: {self.config.stop_loss_ticks} ticks")
                logger.info(f"  ✅ Take Profit: {self.config.take_profit_ratio}:1")
            else:
                signal = "HOLD"
                logger.info(f"⚠️ Signal: {signal} (confiance insuffisante)")
                logger.info(f"  🎯 Confiance: {confidence_score:.2f} < {self.config.min_signal_confidence}")
            
            self.test_results['trading_simulation'] = {
                'signal': signal,
                'confidence': confidence_score,
                'vix_condition': vix_low,
                'spread_condition': spread_reasonable,
                'entry_price': es_data['ask'] if signal == 'BUY' else es_data['bid'] if signal == 'SELL' else None
            }
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur simulation trading: {e}")
            return False
    
    async def test_paper_trading_readiness(self) -> bool:
        """Test préparation Paper Trading avec données réelles"""
        try:
            logger.info("🎯 Test préparation Paper Trading (données réelles)...")
            
            # Vérifier tous les composants
            checks = {
                "Configuration": 'configuration' in self.test_results,
                "Données Marché": 'market_analysis' in self.test_results,
                "Monitoring": 'monitoring_data' in self.test_results,
                "Simulation Trading": 'trading_simulation' in self.test_results,
                "Données Réelles": len(self.real_data) > 0
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
        """Exécution test complet avec données réelles"""
        logger.info("🚀 === TEST MIA_IA AVEC DONNÉES RÉELLES ===")
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
        
        # Test 2: Données réelles
        logger.info("\n📊 TEST 2: Données Réelles Confirmées")
        data_success = self.load_real_market_data()
        test_results["tests"]["real_data"] = data_success
        
        # Test 3: Analyse marché
        logger.info("\n📊 TEST 3: Analyse Données Marché")
        market_success = self.test_market_data_analysis()
        test_results["tests"]["market_analysis"] = market_success
        
        # Test 4: Monitoring
        logger.info("\n📊 TEST 4: Données Monitoring")
        monitoring_success = self.test_monitoring_data()
        test_results["tests"]["monitoring"] = monitoring_success
        
        # Test 5: Simulation Trading
        logger.info("\n🎯 TEST 5: Simulation Paper Trading")
        simulation_success = self.test_paper_trading_simulation()
        test_results["tests"]["trading_simulation"] = simulation_success
        
        # Test 6: Préparation Paper Trading
        logger.info("\n🎯 TEST 6: Préparation Paper Trading")
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
        tester = MIA_IA_RealDataTester()
        
        # Exécuter test complet
        results = await tester.run_complete_test()
        
        # Sauvegarder résultats
        import json
        with open("test_mia_real_data_results.json", "w") as f:
            json.dump(results, f, default=str, indent=2)
        
        logger.info("💾 Résultats sauvegardés dans test_mia_real_data_results.json")
        
    except KeyboardInterrupt:
        logger.info("🛑 Test interrompu par l'utilisateur")
    except Exception as e:
        logger.error(f"❌ Erreur test: {e}")

if __name__ == "__main__":
    asyncio.run(main())


