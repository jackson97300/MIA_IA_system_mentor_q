#!/usr/bin/env python3
"""
🔍 TEST DIAGNOSTIC SIMPLE - MIA_IA_SYSTEM
Test de diagnostic pour identifier les problèmes
"""

import sys
import asyncio
from pathlib import Path
from datetime import datetime

# Ajouter le chemin du projet
sys.path.append(str(Path(__file__).parent))

from core.logger import get_logger
from automation_modules import AutomationConfig, TradingSignal
from automation_modules.optimized_trading_system import OptimizedTradingSystem

logger = get_logger(__name__)

async def test_diagnostic():
    """Test de diagnostic simple"""
    logger.info("🔍 DÉMARRAGE DIAGNOSTIC")
    
    try:
        # 1. Test création config
        logger.info("1️⃣ Test création config...")
        config = AutomationConfig()
        logger.info("✅ Config créée")
        
        # 2. Test création système
        logger.info("2️⃣ Test création système...")
        trading_system = OptimizedTradingSystem(config)
        logger.info("✅ Système créé")
        
        # 3. Test connexion Sierra
        logger.info("3️⃣ Test connexion Sierra...")
        connected = await trading_system.sierra.connect()
        logger.info(f"✅ Connexion Sierra: {connected}")
        
        # 4. Test optimisation
        logger.info("4️⃣ Test optimisation...")
        optimized = await trading_system.optimizer.optimize_connection()
        logger.info(f"✅ Optimisation: {optimized}")
        
        # 5. Test latence
        logger.info("5️⃣ Test latence...")
        latency = await trading_system._test_current_latency()
        logger.info(f"✅ Latence: {latency:.2f}ms")
        
        # 6. Test signal
        logger.info("6️⃣ Test création signal...")
        signal = TradingSignal(
            direction="LONG",
            confidence=0.90,
            price=4500.0,
            timestamp=datetime.now(),
            confluence=0.85,
            stop_loss=4495.0,
            take_profit=4510.0
        )
        signal.symbol = "ES"
        signal.quantity = 1
        logger.info("✅ Signal créé")
        
        # 7. Test exécution scalping
        logger.info("7️⃣ Test exécution scalping...")
        order_id = await trading_system.execute_scalping_trade(signal)
        logger.info(f"✅ Scalping exécuté: {order_id}")
        
        logger.info("🎉 DIAGNOSTIC RÉUSSI")
        return True
        
    except Exception as e:
        logger.error(f"❌ ERREUR DIAGNOSTIC: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Fonction principale"""
    success = asyncio.run(test_diagnostic())
    if success:
        logger.info("✅ DIAGNOSTIC COMPLET - SYSTÈME OPÉRATIONNEL")
    else:
        logger.error("❌ DIAGNOSTIC ÉCHOUÉ - PROBLÈME IDENTIFIÉ")

if __name__ == "__main__":
    main() 