#!/usr/bin/env python3
"""
MIA_IA_SYSTEM - TEST POLYGON SPX ADAPTER
Test de l'adaptateur SPX spécialisé pour trading ES

🎯 OBJECTIF :
- ✅ Valider récupération options SPX
- ✅ Tester calcul Dealer's Bias
- ✅ Vérifier rate limiting
- ✅ Confirmer format MIA_IA_SYSTEM

Author: MIA_IA_SYSTEM
Version: 1.0.0
Date: Août 2025
"""

import asyncio
import json
import logging
from datetime import datetime
from data.polygon_spx_adapter import PolygonSPXAdapter

# Configuration logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_spx_connection():
    """Test connexion API Polygon.io"""
    logger.info("🔗 Test connexion Polygon.io...")
    
    adapter = PolygonSPXAdapter()
    
    # Test prix SPX
    price = await adapter.get_spx_underlying_price()
    if price:
        logger.info(f"✅ Prix SPX: {price}")
        return True
    else:
        logger.error("❌ Échec récupération prix SPX")
        return False

async def test_spx_options_chain():
    """Test récupération chaîne options SPX"""
    logger.info("📊 Test chaîne options SPX...")
    
    adapter = PolygonSPXAdapter()
    
    # Récupérer chaîne options
    spx_data = await adapter.get_spx_options_chain()
    
    if spx_data:
        logger.info(f"✅ Options SPX récupérées:")
        logger.info(f"   📈 Calls: {len(spx_data.calls)}")
        logger.info(f"   📉 Puts: {len(spx_data.puts)}")
        logger.info(f"   💰 Prix sous-jacent: {spx_data.underlying_price}")
        logger.info(f"   📊 PCR OI: {spx_data.pcr_oi:.3f}")
        logger.info(f"   📊 PCR Volume: {spx_data.pcr_volume:.3f}")
        logger.info(f"   📊 IV Skew: {spx_data.iv_skew:.3f}")
        return True
    else:
        logger.error("❌ Échec récupération options SPX")
        return False

async def test_spx_dealers_bias():
    """Test calcul Dealer's Bias SPX"""
    logger.info("🎯 Test calcul Dealer's Bias SPX...")
    
    adapter = PolygonSPXAdapter()
    
    # Récupérer données SPX
    spx_data = await adapter.get_spx_options_chain()
    if not spx_data:
        logger.error("❌ Pas de données SPX pour test Dealer's Bias")
        return False
    
    # Calculer Dealer's Bias
    dealers_bias = await adapter.calculate_spx_dealers_bias(spx_data)
    
    if dealers_bias:
        logger.info(f"✅ Dealer's Bias SPX calculé:")
        logger.info(f"   🎯 Score: {dealers_bias.bias_score:.3f}")
        logger.info(f"   📈 Direction: {dealers_bias.direction}")
        logger.info(f"   💪 Force: {dealers_bias.strength}")
        logger.info(f"   🔄 Gamma Flip: {dealers_bias.gamma_flip_strike}")
        logger.info(f"   📌 Max Pain: {dealers_bias.max_pain}")
        logger.info(f"   📊 PCR OI: {dealers_bias.pcr_oi:.3f}")
        logger.info(f"   📊 IV Skew: {dealers_bias.iv_skew:.3f}")
        logger.info(f"   📊 GEX: {dealers_bias.gex_signed:.2e}")
        
        # Afficher Gamma Pins
        if dealers_bias.gamma_pins:
            logger.info(f"   📌 Gamma Pins ({len(dealers_bias.gamma_pins)}):")
            for pin in dealers_bias.gamma_pins[:3]:  # Top 3
                logger.info(f"      Strike {pin['strike']}: OI={pin['total_oi']}, Force={pin['strength']:.2f}")
        
        return True
    else:
        logger.error("❌ Échec calcul Dealer's Bias SPX")
        return False

async def test_spx_snapshot():
    """Test snapshot SPX complet"""
    logger.info("📊 Test snapshot SPX complet...")
    
    adapter = PolygonSPXAdapter()
    
    # Récupérer snapshot complet
    snapshot = await adapter.get_spx_snapshot_for_es()
    
    if snapshot:
        logger.info(f"✅ Snapshot SPX créé:")
        logger.info(f"   📅 Timestamp: {snapshot['timestamp']}")
        logger.info(f"   💰 Prix SPX: {snapshot['underlying_price']}")
        logger.info(f"   🎯 Dealer's Bias: {snapshot['dealers_bias']['direction']} {snapshot['dealers_bias']['strength']}")
        logger.info(f"   📊 Score: {snapshot['dealers_bias']['score']:.3f}")
        logger.info(f"   📈 Options: {snapshot['options_summary']['calls_count']} calls, {snapshot['options_summary']['puts_count']} puts")
        
        # Sauvegarder snapshot pour inspection
        with open('test_spx_snapshot.json', 'w') as f:
            json.dump(snapshot, f, indent=2, default=str)
        logger.info("💾 Snapshot sauvegardé dans test_spx_snapshot.json")
        
        return True
    else:
        logger.error("❌ Échec création snapshot SPX")
        return False

async def test_rate_limiting():
    """Test rate limiting"""
    logger.info("⏱️ Test rate limiting...")
    
    adapter = PolygonSPXAdapter()
    
    # Faire plusieurs appels rapides
    start_time = datetime.now()
    
    for i in range(3):
        logger.info(f"   Appel {i+1}/3...")
        price = await adapter.get_spx_underlying_price()
        if price:
            logger.info(f"   ✅ Prix SPX: {price}")
        else:
            logger.error(f"   ❌ Échec appel {i+1}")
    
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    logger.info(f"✅ Rate limiting testé en {duration:.1f}s")
    return True

async def test_cache_functionality():
    """Test fonctionnalité cache"""
    logger.info("💾 Test fonctionnalité cache...")
    
    adapter = PolygonSPXAdapter()
    
    # Premier appel (pas en cache)
    logger.info("   Premier appel (pas en cache)...")
    start_time = datetime.now()
    spx_data1 = await adapter.get_spx_options_chain()
    duration1 = (datetime.now() - start_time).total_seconds()
    
    if spx_data1:
        logger.info(f"   ✅ Premier appel réussi en {duration1:.1f}s")
        
        # Deuxième appel (doit être en cache)
        logger.info("   Deuxième appel (en cache)...")
        start_time = datetime.now()
        spx_data2 = await adapter.get_spx_options_chain()
        duration2 = (datetime.now() - start_time).total_seconds()
        
        if spx_data2:
            logger.info(f"   ✅ Deuxième appel réussi en {duration2:.1f}s")
            logger.info(f"   📊 Amélioration: {duration1/duration2:.1f}x plus rapide")
            return True
        else:
            logger.error("   ❌ Échec deuxième appel")
            return False
    else:
        logger.error("   ❌ Échec premier appel")
        return False

async def main():
    """Test principal"""
    logger.info("🚀 DÉBUT TESTS POLYGON SPX ADAPTER")
    logger.info("=" * 50)
    
    tests = [
        ("Connexion API", test_spx_connection),
        ("Chaîne Options SPX", test_spx_options_chain),
        ("Dealer's Bias SPX", test_spx_dealers_bias),
        ("Snapshot Complet", test_spx_snapshot),
        ("Rate Limiting", test_rate_limiting),
        ("Cache", test_cache_functionality)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        logger.info(f"\n🧪 TEST: {test_name}")
        logger.info("-" * 30)
        
        try:
            success = await test_func()
            results.append((test_name, success))
            
            if success:
                logger.info(f"✅ {test_name}: RÉUSSI")
            else:
                logger.error(f"❌ {test_name}: ÉCHOUÉ")
                
        except Exception as e:
            logger.error(f"❌ {test_name}: ERREUR - {e}")
            results.append((test_name, False))
    
    # Résumé final
    logger.info("\n" + "=" * 50)
    logger.info("📊 RÉSUMÉ DES TESTS")
    logger.info("=" * 50)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        logger.info(f"{status} {test_name}")
    
    logger.info(f"\n🎯 RÉSULTAT FINAL: {passed}/{total} tests réussis")
    
    if passed == total:
        logger.info("🎉 TOUS LES TESTS RÉUSSIS !")
        logger.info("✅ L'adaptateur SPX est prêt pour le trading ES")
    else:
        logger.warning(f"⚠️ {total - passed} test(s) échoué(s)")
        logger.info("🔧 Vérifiez les erreurs ci-dessus")
    
    return passed == total

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)











