#!/usr/bin/env python3
"""
Lanceur MIA en mode LIVE avec Sierra Chart
Configuration optimisée pour exécution réelle sur compte demo
"""

import sys
import os
import asyncio

# Ajouter le répertoire racine au path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from LAUNCH.launch_24_7_menthorq_final import main, FINAL_CONFIG

# Configuration LIVE optimisée
LIVE_CONFIG = FINAL_CONFIG.copy()
LIVE_CONFIG.update({
    # Sierra Chart Integration - MODE LIVE
    'sierra_enabled': True,
    'sierra_fallback_simulation': False,  # Pas de fallback
    'sierra_live_mode': True,  # Mode live activé
    
    # Performance optimisée pour mode live
    'processing_timeout_ms': 200,  # Plus strict pour mode live
    'max_signals_per_day': 8,  # Plus conservateur en live
    
    # Risk management renforcé pour mode live
    'max_risk_budget': 0.5,  # 50% du capital max
    'min_pattern_confidence': 0.75,  # Plus strict
    'min_confluence_execution': 0.80,  # Plus strict
    
    # Features optimisées
    'features_config': {
        'enable_advanced_features': True,
        'enable_menthorq_integration': True,
        'enable_smart_money_tracker': True,
        'enable_dow_theory': True  # Dow Theory activée
    }
})

async def main_live():
    """Fonction principale pour mode live"""
    print("🚀 DÉMARRAGE MIA EN MODE LIVE SIERRA CHART")
    print("=" * 60)
    print("⚠️  ATTENTION: Mode LIVE activé - Exécution réelle sur compte demo")
    print("📊 Configuration optimisée pour performance et sécurité")
    print("=" * 60)
    
    # Override de la configuration globale
    import LAUNCH.launch_24_7_menthorq_final
    LAUNCH.launch_24_7_menthorq_final.FINAL_CONFIG = LIVE_CONFIG
    
    # Lancer le système principal
    await main()

if __name__ == "__main__":
    print("🎯 MIA LIVE TRADING SYSTEM")
    print("Mode: Sierra Chart LIVE (Demo Account)")
    print("Dow Theory: ✅ Activée")
    print("Fallback: ❌ Désactivé")
    print("Performance: ⚡ Optimisée")
    print()
    
    try:
        asyncio.run(main_live())
    except KeyboardInterrupt:
        print("\n⏹️ Arrêt demandé par l'utilisateur")
    except Exception as e:
        print(f"\n❌ Erreur système: {e}")
        import traceback
        traceback.print_exc()




