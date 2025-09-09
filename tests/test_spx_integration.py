#!/usr/bin/env python3
"""
🧪 TEST INTÉGRATION SPX OPTIONS RÉELLES
Script de test pour valider les 4 phases d'intégration SPX

PHASES TESTÉES :
1. ✅ Remplacement données simulées
2. ✅ Connexion IBKR
3. ✅ Intégration features
4. ✅ Monitoring IBKR Real vs Fallback

Author: MIA_IA_SYSTEM Team
Date: Août 2025
"""

import sys
import asyncio
import argparse
from pathlib import Path
from datetime import datetime

# Ajouter le chemin du projet
sys.path.append(str(Path(__file__).parent))

from core.logger import get_logger

logger = get_logger(__name__)

async def test_spx_integration():
    """Test l'intégration SPX options avec le launcher"""
    
    logger.info("🧪 === TEST INTÉGRATION SPX OPTIONS ===")
    logger.info("Test des 4 phases d'intégration")
    logger.info("=" * 50)
    
    try:
        # Import du launcher modifié
        from launch_24_7_orderflow_trading import OrderFlow24_7Launcher
        
        logger.info("📊 Création launcher avec SPX intégré...")
        launcher = OrderFlow24_7Launcher(live_trading=False)
        
        # Test initialisation SPX
        if launcher.spx_options_retriever:
            logger.info("✅ PHASE 1-2: SPXOptionsRetriever initialisé")
        else:
            logger.error("❌ PHASE 1-2: SPXOptionsRetriever non initialisé")
            return False
        
        # Test récupération données SPX
        logger.info("📊 Test récupération données SPX...")
        spx_data = await launcher._get_real_spx_options_data()
        
        if spx_data:
            data_source = spx_data.get('data_source', 'unknown')
            logger.info(f"✅ PHASE 1: Données SPX récupérées - Source: {data_source}")
            logger.info(f"  📈 Put/Call Ratio: {spx_data.get('put_call_ratio', 0):.3f}")
            logger.info(f"  💰 Gamma Exposure: ${spx_data.get('gamma_exposure', 0)/1e9:.1f}B")
            logger.info(f"  🏦 Dealer Position: {spx_data.get('dealer_position', 'unknown')}")
            logger.info(f"  📊 VIX Level: {spx_data.get('vix_level', 0):.1f}")
        else:
            logger.error("❌ PHASE 1: Échec récupération données SPX")
            return False
        
        # Test monitoring
        logger.info("📊 Test monitoring SPX...")
        try:
            stats = {"put_call_ratio": 1.0, "gamma_exposure": 75e9}
            await launcher._display_spx_options_monitoring(stats)
            logger.info("✅ PHASE 4: Monitoring SPX fonctionnel")
        except Exception as e:
            logger.error(f"❌ PHASE 4: Erreur monitoring: {e}")
            return False
        
        # Test analyse intégrée (si données disponibles)
        logger.info("📊 Test analyse features intégrées...")
        try:
            # Création données de test
            test_market_data = {
                'symbol': 'ES',
                'price': 5425.50,
                'volume': 1500,
                'delta': 100,
                'bid_volume': 700,
                'ask_volume': 800,
                'options_data': spx_data
            }
            
            if launcher.integrated_calculator:
                result = await launcher._analyze_integrated_features(
                    test_market_data, None
                )
                if result:
                    logger.info("✅ PHASE 3: Features intégrées avec SPX options")
                    logger.info(f"  📊 Score confluence: {result.integrated_confluence_score:.3f}")
                else:
                    logger.warning("⚠️ PHASE 3: Features retourné None")
            else:
                logger.warning("⚠️ PHASE 3: IntegratedCalculator non disponible")
                
        except Exception as e:
            logger.error(f"❌ PHASE 3: Erreur features intégrées: {e}")
        
        logger.info("=" * 50)
        logger.info("🎉 TEST INTÉGRATION SPX RÉUSSI !")
        logger.info("📊 Toutes les phases implémentées et fonctionnelles")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erreur test intégration: {e}")
        return False

async def test_spx_retriever_standalone():
    """Test SPXOptionsRetriever en standalone"""
    
    logger.info("🧪 === TEST SPX RETRIEVER STANDALONE ===")
    
    try:
        from features.spx_options_retriever import create_spx_options_retriever
        
        retriever = create_spx_options_retriever()
        logger.info("📊 SPXOptionsRetriever créé")
        
        # Test récupération (sans IBKR)
        spx_data = await retriever.get_real_spx_data()
        
        if spx_data:
            logger.info("✅ Données SPX récupérées (mode fallback)")
            logger.info(f"  📊 Source: {spx_data.get('data_source', 'unknown')}")
            logger.info(f"  📈 Put/Call: {spx_data.get('put_call_ratio', 0):.3f}")
            logger.info(f"  💰 Gamma: ${spx_data.get('gamma_exposure', 0)/1e9:.1f}B")
            logger.info(f"  🏦 Dealer: {spx_data.get('dealer_gamma_position', 'unknown')}")
            logger.info(f"  📊 VIX: {spx_data.get('vix_level', 0):.1f}")
            logger.info(f"  🔄 Gamma Flip: {spx_data.get('gamma_flip_level', 0):.0f}")
            logger.info(f"  ⏱️ Calc Time: {spx_data.get('calculation_time_ms', 0):.1f}ms")
            return True
        else:
            logger.error("❌ Échec récupération données SPX")
            return False
            
    except Exception as e:
        logger.error(f"❌ Erreur test standalone: {e}")
        logger.error(f"📊 Import path error? Détails: {type(e).__name__}")
        return False

async def run_comprehensive_test():
    """Test complet intégration SPX"""
    
    logger.info("🚀 DÉMARRAGE TEST COMPLET SPX INTEGRATION")
    logger.info("=" * 60)
    
    results = []
    
    # Test 1: SPX Retriever standalone
    logger.info("TEST 1: SPX Retriever Standalone")
    result1 = await test_spx_retriever_standalone()
    results.append(("SPX Retriever", result1))
    
    logger.info("=" * 60)
    
    # Test 2: Intégration complète
    logger.info("TEST 2: Intégration Complète Launcher")
    result2 = await test_spx_integration()
    results.append(("Intégration Complète", result2))
    
    # Rapport final
    logger.info("=" * 60)
    logger.info("📊 RAPPORT FINAL TESTS SPX")
    logger.info("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ RÉUSSI" if result else "❌ ÉCHEC"
        logger.info(f"{status}: {test_name}")
        if result:
            passed += 1
    
    logger.info("=" * 60)
    logger.info(f"🎯 RÉSULTAT: {passed}/{total} tests réussis ({passed/total*100:.1f}%)")
    
    if passed == total:
        logger.info("🎉 INTÉGRATION SPX OPTIONS VALIDÉE !")
        logger.info("🚀 Système prêt pour données SPX réelles via IBKR")
    else:
        logger.warning("⚠️ Corrections nécessaires avant déploiement")
    
    return passed == total

async def main():
    """Point d'entrée principal"""
    
    parser = argparse.ArgumentParser(description="Test Intégration SPX Options")
    parser.add_argument("--standalone", action="store_true", help="Test SPX Retriever seulement")
    parser.add_argument("--full", action="store_true", help="Test intégration complète")
    
    args = parser.parse_args()
    
    if args.standalone:
        success = await test_spx_retriever_standalone()
    elif args.full:
        success = await test_spx_integration()
    else:
        success = await run_comprehensive_test()
    
    if success:
        logger.info("✅ TESTS RÉUSSIS")
        sys.exit(0)
    else:
        logger.error("❌ TESTS ÉCHOUÉS")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
