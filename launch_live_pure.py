#!/usr/bin/env python3
"""
Lanceur MIA en mode LIVE PUR avec Sierra Chart
Pas de fallback fichiers - Lecture directe des données Sierra Chart
"""

import sys
import os
import asyncio

# Ajouter le répertoire racine au path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from LAUNCH.launch_24_7_menthorq_final import main, FINAL_CONFIG

# Configuration LIVE PUR (sans fallback)
LIVE_PURE_CONFIG = FINAL_CONFIG.copy()
LIVE_PURE_CONFIG.update({
    # Sierra Chart Integration - MODE LIVE PUR
    'sierra_enabled': True,
    'sierra_fallback_simulation': False,  # Pas de fallback
    'sierra_live_mode': True,  # Mode live pur activé
    
    # Performance optimisée pour mode live pur
    'processing_timeout_ms': 100,  # Très strict pour mode live
    'max_signals_per_day': 6,  # Très conservateur en live pur
    
    # Risk management ultra-renforcé pour mode live pur
    'max_risk_budget': 0.3,  # 30% du capital max
    'min_pattern_confidence': 0.85,  # Très strict
    'min_confluence_execution': 0.90,  # Très strict
    
    # Features optimisées
    'features_config': {
        'enable_advanced_features': True,
        'enable_menthorq_integration': True,
        'enable_smart_money_tracker': True,
        'enable_dow_theory': True,  # Dow Theory activée
        'enable_live_data_only': True  # Données live uniquement
    }
})

async def main_live_pure():
    """Fonction principale pour mode live pur"""
    print("🚀 DÉMARRAGE MIA EN MODE LIVE PUR SIERRA CHART")
    print("=" * 60)
    print("⚠️  ATTENTION: Mode LIVE PUR activé - Exécution réelle")
    print("📊 Lecture directe des données Sierra Chart (pas de fichiers)")
    print("🛡️ Risk management ultra-renforcé")
    print("=" * 60)
    
    # Override de la configuration globale
    import LAUNCH.launch_24_7_menthorq_final
    LAUNCH.launch_24_7_menthorq_final.FINAL_CONFIG = LIVE_PURE_CONFIG
    
    # Lancer le système principal
    await main()

if __name__ == "__main__":
    print("🎯 MIA LIVE PURE TRADING SYSTEM")
    print("Mode: Sierra Chart LIVE PUR (Demo Account)")
    print("Dow Theory: ✅ Activée")
    print("Fallback: ❌ Désactivé")
    print("Données: 📊 Live uniquement")
    print("Performance: ⚡ Ultra-optimisée")
    print("Risk: 🛡️ Ultra-renforcé")
    print()
    
    try:
        asyncio.run(main_live_pure())
    except KeyboardInterrupt:
        print("\n⏹️ Arrêt demandé par l'utilisateur")
    except Exception as e:
        print(f"\n❌ Erreur système: {e}")
        import traceback
        traceback.print_exc()




