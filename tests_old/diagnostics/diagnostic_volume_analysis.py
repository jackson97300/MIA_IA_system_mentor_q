#!/usr/bin/env python3
"""
🔍 DIAGNOSTIC VOLUMES NULLS - MIA_IA_SYSTEM
===========================================

Script de diagnostic pour analyser pourquoi les volumes sont nuls
et corriger les incohérences identifiées dans le système.
"""

import sys
import asyncio
import time
from pathlib import Path

# Ajouter le chemin du projet
sys.path.append(str(Path(__file__).parent))

from core.logger import get_logger
from core.ibkr_connector import IBKRConnector
from features.orderflow_analyzer import OrderFlowAnalyzer
from config.automation_config import AutomationConfig

logger = get_logger(__name__)

class VolumeDiagnostic:
    """Diagnostic complet des problèmes de volumes"""
    
    def __init__(self):
        self.config = AutomationConfig()
        self.ibkr_connector = None
        
    async def run_volume_diagnostic(self):
        """Lance un diagnostic complet des volumes"""
        logger.info("🔍 DIAGNOSTIC VOLUMES NULLS - MIA_IA_SYSTEM")
        logger.info("=" * 60)
        
        # 1. Test connexion IBKR et contrats
        await self._test_ibkr_contracts()
        
        # 2. Test données ES/NQ réelles
        await self._test_real_market_data()
        
        # 3. Test OrderFlow Analyzer avec volumes
        await self._test_orderflow_volumes()
        
        # 4. Test seuils dynamiques
        await self._test_dynamic_thresholds()
        
        # 5. Test incohérences identifiées
        await self._test_identified_issues()
        
        # 6. Recommandations de correction
        await self._provide_corrections()
        
    async def _test_ibkr_contracts(self):
        """Test des contrats IBKR"""
        logger.info("🔌 TEST CONTRATS IBKR")
        logger.info("-" * 30)
        
        try:
            self.ibkr_connector = IBKRConnector()
            await self.ibkr_connector.connect()
            
            if self.ibkr_connector.is_connected():
                logger.info("✅ Connexion IBKR: SUCCÈS")
                
                # Test contrats ES/NQ
                contracts = await self.ibkr_connector.get_contracts()
                if contracts:
                    logger.info("✅ Contrats initialisés:")
                    for symbol, contract in contracts.items():
                        logger.info(f"   📊 {symbol}: {contract.symbol} ({contract.localSymbol})")
                        logger.info(f"      Multiplier: {contract.multiplier}")
                        logger.info(f"      Exchange: {contract.exchange}")
                else:
                    logger.warning("⚠️ Aucun contrat initialisé")
                    
            else:
                logger.error("❌ Connexion IBKR: ÉCHEC")
                
        except Exception as e:
            logger.error(f"❌ Erreur contrats IBKR: {e}")
            
    async def _test_real_market_data(self):
        """Test des données de marché réelles"""
        logger.info("📊 TEST DONNÉES MARCHÉ RÉELLES")
        logger.info("-" * 30)
        
        if not self.ibkr_connector or not self.ibkr_connector.is_connected():
            logger.error("❌ Impossible de tester - Pas de connexion IBKR")
            return
            
        try:
            # Test ES avec données réelles
            logger.info("📈 Test ES (S&P 500):")
            es_data = await self.ibkr_connector.get_orderflow_market_data('ES')
            if es_data:
                logger.info("✅ Données ES récupérées:")
                logger.info(f"   📊 Volume: {es_data.get('volume', 'N/A')}")
                logger.info(f"   📈 Delta: {es_data.get('delta', 'N/A')}")
                logger.info(f"   💰 Bid Volume: {es_data.get('bid_volume', 'N/A')}")
                logger.info(f"   💰 Ask Volume: {es_data.get('ask_volume', 'N/A')}")
                logger.info(f"   💱 Prix: {es_data.get('price', 'N/A')}")
                
                # Vérification cohérence
                volume = es_data.get('volume', 0)
                bid_vol = es_data.get('bid_volume', 0)
                ask_vol = es_data.get('ask_volume', 0)
                
                if volume > 0:
                    logger.info(f"   ✅ Volume valide: {volume}")
                    if bid_vol + ask_vol > 0:
                        logger.info(f"   ✅ Bid+Ask cohérent: {bid_vol} + {ask_vol} = {bid_vol + ask_vol}")
                    else:
                        logger.warning(f"   ⚠️ Bid+Ask nul: {bid_vol} + {ask_vol}")
                else:
                    logger.error(f"   ❌ Volume nul: {volume}")
            else:
                logger.warning("⚠️ Aucune donnée ES")
                
            # Test NQ avec données réelles
            logger.info("📊 Test NQ (NASDAQ):")
            nq_data = await self.ibkr_connector.get_orderflow_market_data('NQ')
            if nq_data:
                logger.info("✅ Données NQ récupérées:")
                logger.info(f"   📊 Volume: {nq_data.get('volume', 'N/A')}")
                logger.info(f"   📈 Delta: {nq_data.get('delta', 'N/A')}")
                logger.info(f"   💰 Bid Volume: {nq_data.get('bid_volume', 'N/A')}")
                logger.info(f"   💰 Ask Volume: {nq_data.get('ask_volume', 'N/A')}")
                logger.info(f"   💱 Prix: {nq_data.get('price', 'N/A')}")
                
                # Vérification cohérence
                volume = nq_data.get('volume', 0)
                bid_vol = nq_data.get('bid_volume', 0)
                ask_vol = nq_data.get('ask_volume', 0)
                
                if volume > 0:
                    logger.info(f"   ✅ Volume valide: {volume}")
                    if bid_vol + ask_vol > 0:
                        logger.info(f"   ✅ Bid+Ask cohérent: {bid_vol} + {ask_vol} = {bid_vol + ask_vol}")
                    else:
                        logger.warning(f"   ⚠️ Bid+Ask nul: {bid_vol} + {ask_vol}")
                else:
                    logger.error(f"   ❌ Volume nul: {volume}")
            else:
                logger.warning("⚠️ Aucune donnée NQ")
                
        except Exception as e:
            logger.error(f"❌ Erreur données marché: {e}")
            
    async def _test_orderflow_volumes(self):
        """Test de l'OrderFlow Analyzer avec volumes"""
        logger.info("🧠 TEST ORDERFLOW VOLUMES")
        logger.info("-" * 30)
        
        try:
            orderflow_analyzer = OrderFlowAnalyzer(self.config)
            logger.info("✅ OrderFlow Analyzer initialisé")
            
            # Test avec volumes faibles
            test_data_weak = {
                'price': 6450.0,
                'volume': 30,  # Volume très faible
                'delta': 5.0,
                'bid_volume': 15,
                'ask_volume': 15,
                'mode': 'test'
            }
            
            logger.info(f"📊 Test volume faible: {test_data_weak['volume']}")
            signal_weak = await orderflow_analyzer.analyze_orderflow_data(test_data_weak)
            if signal_weak:
                logger.info("✅ Signal généré avec volume faible")
                logger.info(f"   🎯 Type: {signal_weak.signal_type}")
                logger.info(f"   📊 Confiance: {signal_weak.confidence:.3f}")
            else:
                logger.warning("⚠️ Signal rejeté avec volume faible")
            
            # Test avec volume nul
            test_data_zero = {
                'price': 6450.0,
                'volume': 0,  # Volume nul
                'delta': 0.0,
                'bid_volume': 0,
                'ask_volume': 0,
                'mode': 'test'
            }
            
            logger.info(f"📊 Test volume nul: {test_data_zero['volume']}")
            signal_zero = await orderflow_analyzer.analyze_orderflow_data(test_data_zero)
            if signal_zero:
                logger.warning("⚠️ Signal généré avec volume nul (problème)")
            else:
                logger.info("✅ Signal correctement rejeté avec volume nul")
                
        except Exception as e:
            logger.error(f"❌ Erreur test OrderFlow: {e}")
            
    async def _test_dynamic_thresholds(self):
        """Test des seuils dynamiques"""
        logger.info("🎯 TEST SEUILS DYNAMIQUES")
        logger.info("-" * 30)
        
        try:
            # Simulation de volumes rolling
            from collections import deque
            rolling_volumes = deque([100, 150, 200, 180, 220, 300, 250, 280, 350, 400], maxlen=10)
            
            logger.info(f"📊 Volumes rolling: {list(rolling_volumes)}")
            
            # Calcul seuil dynamique
            if rolling_volumes:
                avg_volume = sum(rolling_volumes) / len(rolling_volumes)
                dynamic_threshold = max(30, int(avg_volume * 1.01))
                logger.info(f"   📊 Volume moyen: {avg_volume:.1f}")
                logger.info(f"   🎯 Seuil dynamique: {dynamic_threshold}")
                
                # Test avec différents volumes
                test_volumes = [25, 50, 100, 200, 300]
                for vol in test_volumes:
                    status = "✅" if vol >= dynamic_threshold else "❌"
                    logger.info(f"   {status} Volume {vol}: {'ACCEPTÉ' if vol >= dynamic_threshold else 'REJETÉ'}")
            else:
                logger.warning("⚠️ Aucun volume rolling disponible")
                
        except Exception as e:
            logger.error(f"❌ Erreur test seuils: {e}")
            
    async def _test_identified_issues(self):
        """Test des incohérences identifiées"""
        logger.info("🔍 TEST INCOHÉRENCES IDENTIFIÉES")
        logger.info("-" * 30)
        
        # 1. Test convention imbalance
        logger.info("📊 Test convention imbalance:")
        bid_vol = 272
        ask_vol = 281
        imbalance_1 = ask_vol - bid_vol  # Convention 1: ask - bid
        imbalance_2 = bid_vol - ask_vol  # Convention 2: bid - ask
        
        logger.info(f"   Bid: {bid_vol}, Ask: {ask_vol}")
        logger.info(f"   Imbalance (ask-bid): {imbalance_1}")
        logger.info(f"   Imbalance (bid-ask): {imbalance_2}")
        logger.info(f"   Total (bid+ask): {bid_vol + ask_vol}")
        
        # 2. Test cohérence volume total
        logger.info("📊 Test cohérence volume total:")
        volume_total = 562
        bid_ask_sum = bid_vol + ask_vol
        difference = volume_total - bid_ask_sum
        
        logger.info(f"   Volume total: {volume_total}")
        logger.info(f"   Bid+Ask sum: {bid_ask_sum}")
        logger.info(f"   Différence: {difference}")
        
        if difference != 0:
            logger.info(f"   ℹ️ Différence normale (autres/unclassified): {difference}")
        
        # 3. Test Level2 Score
        logger.info("📊 Test Level2 Score:")
        level2_data = {
            'best_bid': 6450.0,
            'best_ask': 6450.25,
            'bid_depth': {6450.0: 100, 6449.75: 50},
            'ask_depth': {6450.25: 100, 6450.50: 50}
        }
        
        logger.info(f"   Level2 data disponible: {bool(level2_data)}")
        logger.info(f"   Bid depth: {len(level2_data['bid_depth'])} niveaux")
        logger.info(f"   Ask depth: {len(level2_data['ask_depth'])} niveaux")
        
        # 4. Test saved_data vs live
        logger.info("📊 Test saved_data vs live:")
        saved_data = {
            'price': 6450.0,
            'volume': 500,
            'mode': 'saved_data'
        }
        
        live_data = {
            'price': 6450.0,
            'volume': 500,
            'mode': 'live_real'
        }
        
        logger.info(f"   Saved data mode: {saved_data['mode']}")
        logger.info(f"   Live data mode: {live_data['mode']}")
        logger.info(f"   ⚠️ Mélange saved_data + ordres live = PROBLÈME")
        
    async def _provide_corrections(self):
        """Fournit les corrections recommandées"""
        logger.info("💡 CORRECTIONS RECOMMANDÉES")
        logger.info("-" * 30)
        
        logger.info("🔧 CORRECTIONS PRIORITAIRES:")
        logger.info("   1. INTERLOCK SAVED_DATA:")
        logger.info("      - if data_source == 'saved_data': trading_enabled = False")
        logger.info("      - Sauf mode test explicitement armé")
        
        logger.info("   2. GATING POST-MORTEM:")
        logger.info("      - Post-mortem seulement après fill confirmé")
        logger.info("      - Hook sur statut d'ordre 'Filled'")
        
        logger.info("   3. SEUILS DYNAMIQUES UNIFIÉS:")
        logger.info("      - Une seule source de vérité par itération")
        logger.info("      - Même objet/valeur au logger début et post-check")
        
        logger.info("   4. CONVENTION IMBALANCE:")
        logger.info("      - Documenter: imbalance = ask - bid")
        logger.info("      - Utiliser la même convention partout")
        
        logger.info("   5. HEALTH-CHECK LEVEL2:")
        logger.info("      - Si level2_updates == 0 sur N cycles")
        logger.info("      - Dégradé le Confluence Score ou inhiber L2")
        
        logger.info("   6. FALLBACK NQ PROPRE:")
        logger.info("      - Si NQ indisponible, exclure de la décision")
        logger.info("      - Logger 'leadership based on ES only'")
        
        logger.info("   7. LOGS EXPLICITES:")
        logger.info("      - ENV=Paper / ORDERS=Simulated / DATA=SavedData+IBKR")
        logger.info("      - Éviter confusion 'Connexion IBKR RÉELLE' + 'Paper'")

async def main():
    """Fonction principale"""
    try:
        diagnostic = VolumeDiagnostic()
        await diagnostic.run_volume_diagnostic()
        
    except KeyboardInterrupt:
        logger.info("🛑 Diagnostic interrompu par l'utilisateur")
    except Exception as e:
        logger.error(f"❌ Erreur diagnostic: {e}")

if __name__ == "__main__":
    asyncio.run(main())

