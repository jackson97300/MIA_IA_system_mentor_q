#!/usr/bin/env python3
"""
Test du statut du bot MIA_IA_SYSTEM
Script de diagnostic et correction
"""

import sys
import os
from pathlib import Path

# Ajouter le chemin du projet
sys.path.append(str(Path(__file__).parent))

def test_imports():
    """Test des imports critiques"""
    print("🔍 Test des imports...")
    
    try:
        import random
        print("✅ random importé")
    except ImportError as e:
        print(f"❌ Erreur import random: {e}")
    
    try:
        from automation_modules.trading_engine import MIAAutomationSystem
        print("✅ MIAAutomationSystem importé")
    except ImportError as e:
        print(f"❌ Erreur import MIAAutomationSystem: {e}")
    
    try:
        from automation_modules.optimized_trading_system import OptimizedTradingSystem
        print("✅ OptimizedTradingSystem importé")
    except ImportError as e:
        print(f"❌ Erreur import OptimizedTradingSystem: {e}")

def test_config():
    """Test de la configuration"""
    print("\n🔧 Test de la configuration...")
    
    try:
        from config.automation_config import create_paper_trading_config
        config = create_paper_trading_config()
        print("✅ Configuration créée")
        print(f"   - Mode: {config.automation_mode}")
        print(f"   - Max positions: {config.trading.max_positions_concurrent}")
        print(f"   - Daily loss limit: {config.trading.daily_loss_limit}")
    except Exception as e:
        print(f"❌ Erreur configuration: {e}")

def test_trading_engine():
    """Test du trading engine"""
    print("\n🚀 Test du trading engine...")
    
    try:
        from config.automation_config import create_paper_trading_config
        from automation_modules.trading_engine import MIAAutomationSystem
        
        config = create_paper_trading_config()
        engine = MIAAutomationSystem(config)
        print("✅ Trading engine créé")
        
        # Test méthode _get_market_data
        import asyncio
        async def test_market_data():
            market_data = await engine._get_market_data()
            if market_data:
                print(f"✅ Données marché: Prix={market_data.price:.2f}, Volume={market_data.volume}")
            else:
                print("❌ Pas de données marché")
        
        asyncio.run(test_market_data())
        
    except Exception as e:
        print(f"❌ Erreur trading engine: {e}")

def main():
    """Fonction principale"""
    print("🔍 DIAGNOSTIC BOT MIA_IA_SYSTEM")
    print("=" * 50)
    
    test_imports()
    test_config()
    test_trading_engine()
    
    print("\n✅ Diagnostic terminé")

if __name__ == "__main__":
    main()
