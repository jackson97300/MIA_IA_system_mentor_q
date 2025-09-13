#!/usr/bin/env python3
"""
Test rapide du lanceur Sierra Chart MIA
=======================================

Teste le nouveau lanceur optimisé pour Sierra Chart
"""

import asyncio
import sys
from pathlib import Path

# Ajouter le chemin du projet
sys.path.append(str(Path(__file__).parent))

from launch_mia_sierra_chart import MIASierraChartLauncher

async def test_sierra_launcher():
    """Test du lanceur Sierra Chart"""
    print("🔍 TEST LANCEUR SIERRA CHART MIA")
    print("="*50)
    
    # Créer le lanceur en mode paper trading
    launcher = MIASierraChartLauncher(
        live_trading=False,
        simulation_mode=False,
        paper_trading=True
    )
    
    try:
        # Test initialisation Sierra Chart
        print("🔌 Test initialisation Sierra Chart...")
        sierra_ok = await launcher.initialize_sierra_chart()
        
        if sierra_ok:
            print("✅ Sierra Chart initialisé")
            
            # Test data collector
            print("📊 Test data collector...")
            launcher.initialize_data_collector()
            print("✅ Data collector initialisé")
            
            # Test trading system
            print("🎯 Test trading system...")
            launcher.initialize_trading_system()
            print("✅ Trading system initialisé")
            
            # Vérifier le statut
            status = launcher.get_status()
            print(f"📡 Statut final: {status}")
            
            # Arrêter proprement
            await launcher.stop()
            print("✅ Test terminé avec succès")
            
        else:
            print("❌ Échec initialisation Sierra Chart")
            
    except Exception as e:
        print(f"❌ Erreur test: {e}")
        await launcher.stop()

if __name__ == "__main__":
    asyncio.run(test_sierra_launcher())

