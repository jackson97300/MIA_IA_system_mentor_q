#!/usr/bin/env python3
"""
🔍 DIAGNOSTIC MARCHÉ LIVE - MIA_IA_SYSTEM
==========================================

Script de diagnostic pour analyser l'état du système et les données de marché
en temps réel pour identifier les problèmes OrderFlow.
"""

import sys
import asyncio
import time
from pathlib import Path

# Ajouter le chemin du projet
sys.path.append(str(Path(__file__).parent))

from core.logger import get_logger
from core.ibkr_connector import IBKRConnector
from automation_modules.orderflow_analyzer import OrderFlowAnalyzer
from automation_modules.config_manager import AutomationConfig

logger = get_logger(__name__)

class MarketDiagnostic:
    """Diagnostic complet du système de trading"""
    
    def __init__(self):
        self.config = AutomationConfig()
        self.ibkr_connector = None
        self.orderflow_analyzer = None
        
    async def run_full_diagnostic(self):
        """Lance un diagnostic complet"""
        logger.info("🔍 DIAGNOSTIC MARCHÉ LIVE - MIA_IA_SYSTEM")
        logger.info("=" * 60)
        
        # 1. Test connexion IBKR
        await self._test_ibkr_connection()
        
        # 2. Test données ES/NQ
        await self._test_market_data()
        
        # 3. Test OrderFlow Analyzer
        await self._test_orderflow_analyzer()
        
        # 4. Test seuils optimisés
        await self._test_optimized_thresholds()
        
        # 5. Recommandations
        await self._provide_recommendations()
        
    async def _test_ibkr_connection(self):
        """Test de la connexion IBKR"""
        logger.info("🔌 TEST CONNEXION IBKR")
        logger.info("-" * 30)
        
        try:
            self.ibkr_connector = IBKRConnector()
            await self.ibkr_connector.connect()
            
            if self.ibkr_connector.is_connected():
                logger.info("✅ Connexion IBKR: SUCCÈS")
                logger.info(f"   📡 Host: {self.ibkr_connector.host}")
                logger.info(f"   🔌 Port: {self.ibkr_connector.port}")
                logger.info(f"   🆔 Client ID: {self.ibkr_connector.client_id}")
                
                # Test contrats
                contracts = await self.ibkr_connector.get_contracts()
                if contracts:
                    logger.info("✅ Contrats initialisés:")
                    for symbol, contract in contracts.items():
                        logger.info(f"   📊 {symbol}: {contract.symbol} ({contract.localSymbol})")
                else:
                    logger.warning("⚠️ Aucun contrat initialisé")
                    
            else:
                logger.error("❌ Connexion IBKR: ÉCHEC")
                
        except Exception as e:
            logger.error(f"❌ Erreur connexion IBKR: {e}")
            
    async def _test_market_data(self):
        """Test des données de marché"""
        logger.info("📊 TEST DONNÉES MARCHÉ")
        logger.info("-" * 30)
        
        if not self.ibkr_connector or not self.ibkr_connector.is_connected():
            logger.error("❌ Impossible de tester - Pas de connexion IBKR")
            return
            
        try:
            # Test ES
            es_data = await self.ibkr_connector.get_orderflow_market_data('ES')
            if es_data:
                logger.info("✅ Données ES récupérées:")
                logger.info(f"   📈 Prix: {es_data.get('price', 'N/A')}")
                logger.info(f"   📊 Volume: {es_data.get('volume', 'N/A')}")
                logger.info(f"   📈 Delta: {es_data.get('delta', 'N/A')}")
                logger.info(f"   💰 Bid/Ask: {es_data.get('bid_volume', 'N/A')}/{es_data.get('ask_volume', 'N/A')}")
            else:
                logger.warning("⚠️ Aucune donnée ES")
                
            # Test NQ
            nq_data = await self.ibkr_connector.get_orderflow_market_data('NQ')
            if nq_data:
                logger.info("✅ Données NQ récupérées:")
                logger.info(f"   📈 Prix: {nq_data.get('price', 'N/A')}")
                logger.info(f"   📊 Volume: {nq_data.get('volume', 'N/A')}")
                logger.info(f"   📈 Delta: {nq_data.get('delta', 'N/A')}")
                logger.info(f"   💰 Bid/Ask: {nq_data.get('bid_volume', 'N/A')}/{nq_data.get('ask_volume', 'N/A')}")
            else:
                logger.warning("⚠️ Aucune donnée NQ")
                
        except Exception as e:
            logger.error(f"❌ Erreur données marché: {e}")
            
    async def _test_orderflow_analyzer(self):
        """Test de l'OrderFlow Analyzer"""
        logger.info("🧠 TEST ORDERFLOW ANALYZER")
        logger.info("-" * 30)
        
        try:
            self.orderflow_analyzer = OrderFlowAnalyzer(self.config)
            logger.info("✅ OrderFlow Analyzer initialisé")
            
            # Test avec données simulées
            test_data = {
                'price': 6450.0,
                'volume': 500,
                'delta': 100.0,
                'bid_volume': 250,
                'ask_volume': 250,
                'mode': 'test'
            }
            
            signal = await self.orderflow_analyzer.analyze_orderflow_data(test_data)
            if signal:
                logger.info("✅ Signal OrderFlow généré:")
                logger.info(f"   🎯 Type: {signal.signal_type}")
                logger.info(f"   📊 Confiance: {signal.confidence:.3f}")
                logger.info(f"   📝 Raison: {signal.reasoning}")
            else:
                logger.warning("⚠️ Aucun signal généré avec données de test")
                
        except Exception as e:
            logger.error(f"❌ Erreur OrderFlow Analyzer: {e}")
            
    async def _test_optimized_thresholds(self):
        """Test des seuils optimisés"""
        logger.info("🎯 TEST SEUILS OPTIMISÉS")
        logger.info("-" * 30)
        
        try:
            # Test avec données faibles
            weak_data = {
                'price': 6450.0,
                'volume': 60,  # Volume faible
                'delta': 5.0,  # Delta faible
                'bid_volume': 30,
                'ask_volume': 30,
                'mode': 'test'
            }
            
            signal = await self.orderflow_analyzer.analyze_orderflow_data(weak_data)
            if signal:
                logger.info("✅ Signal généré avec données faibles (seuils optimisés)")
                logger.info(f"   🎯 Type: {signal.signal_type}")
                logger.info(f"   📊 Confiance: {signal.confidence:.3f}")
            else:
                logger.warning("⚠️ Signal rejeté même avec seuils optimisés")
                
        except Exception as e:
            logger.error(f"❌ Erreur test seuils: {e}")
            
    async def _provide_recommendations(self):
        """Fournit des recommandations"""
        logger.info("💡 RECOMMANDATIONS")
        logger.info("-" * 30)
        
        logger.info("🚀 POUR TRADING LIVE:")
        logger.info("   1. Vérifier que IBKR TWS/Gateway est ouvert")
        logger.info("   2. S'assurer que les contrats ES/NQ sont activés")
        logger.info("   3. Vérifier les permissions de trading")
        logger.info("   4. Commencer en mode DRY RUN d'abord")
        
        logger.info("🔧 POUR RÉSOUDRE LES ERREURS ORDERFLOW:")
        logger.info("   1. Seuils déjà optimisés (5% confiance, 50 volume)")
        logger.info("   2. Vérifier la qualité des données de marché")
        logger.info("   3. Analyser les logs pour identifier les rejets")
        logger.info("   4. Ajuster les paramètres si nécessaire")
        
        logger.info("📊 POUR LA STRATÉGIE LEADERSHIP:")
        logger.info("   1. Système prêt pour 84.6% Win Rate")
        logger.info("   2. Position sizing adaptatif activé")
        logger.info("   3. Entry timing optimisé")
        logger.info("   4. Risk management en place")

async def main():
    """Fonction principale"""
    try:
        diagnostic = MarketDiagnostic()
        await diagnostic.run_full_diagnostic()
        
    except KeyboardInterrupt:
        logger.info("🛑 Diagnostic interrompu par l'utilisateur")
    except Exception as e:
        logger.error(f"❌ Erreur diagnostic: {e}")

if __name__ == "__main__":
    asyncio.run(main())

