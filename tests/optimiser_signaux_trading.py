#!/usr/bin/env python3
"""
MIA_IA_SYSTEM - Optimisation Signaux Trading
Améliore la qualité et diversifie les signaux
"""

import os
import sys
import json
from datetime import datetime

# Ajouter le répertoire racine au path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def optimiser_signaux():
    """Optimise les paramètres de signaux pour améliorer la performance"""
    
    print("MIA_IA_SYSTEM - OPTIMISATION SIGNAUX TRADING")
    print("=" * 60)
    
    try:
        # Modifier directement les fichiers de configuration
        import config.automation_config as auto_config
        
        # OPTIMISATION 1: Améliorer les seuils de confiance
        auto_config.MIN_CONFIDENCE_THRESHOLD = 0.60  # Augmenter de 0.509 à 0.60
        auto_config.PREMIUM_SIGNAL_THRESHOLD = 0.35  # Réduire de 0.38 à 0.35
        auto_config.STRONG_SIGNAL_THRESHOLD = 0.30   # Définir seuil STRONG
        
        # OPTIMISATION 2: Diversifier les conditions de signaux
        auto_config.ENABLE_SELL_SIGNALS = True       # Activer signaux SELL
        auto_config.BALANCE_BUY_SELL = True          # Équilibrer BUY/SELL
        auto_config.MIN_SIGNAL_INTERVAL = 30         # Intervalle minimum entre signaux
        
        # OPTIMISATION 3: Améliorer la confluence
        auto_config.MIN_CONFLUENCE_SCORE = 0.30      # Seuil minimum confluence
        auto_config.VOLUME_VARIABILITY_CHECK = True  # Vérifier variabilité volume
        auto_config.DELTA_VARIABILITY_CHECK = True   # Vérifier variabilité delta
        
        # OPTIMISATION 4: Paramètres OrderFlow améliorés
        auto_config.ORDERFLOW_CONFIG = {
            "min_volume_change": 10.0,      # Changement volume minimum
            "min_delta_change": 5.0,        # Changement delta minimum
            "max_same_signal_count": 3,     # Max signaux identiques consécutifs
            "signal_cooldown_seconds": 60,  # Cooldown entre signaux
            "enable_momentum_check": True,  # Vérification momentum
            "enable_reversal_detection": True  # Détection inversions
        }
        
        # OPTIMISATION 5: Features redistribuées (améliorées)
        auto_config.FEATURE_WEIGHTS = {
            "gamma_levels_proximity": 0.0,  # Désactivé (pas d'options)
            "volume_confirmation": 0.35,    # Légèrement réduit
            "vwap_trend_signal": 0.25,      # Maintenu
            "sierra_pattern_strength": 0.25, # Maintenu
            "smart_money_strength": 0.25,   # Augmenté (20% → 25%)
            "level_proximity": 0.15,        # Augmenté (12% → 15%)
            "es_nq_correlation": 0.15,      # Augmenté (12% → 15%)
            "order_book_imbalance": 0.30,   # Augmenté (25% → 30%)
            "session_context": 0.08,        # Augmenté (5% → 8%)
            "pullback_quality": 0.05        # Augmenté (3% → 5%)
        }
        
        print("✅ Optimisations appliquées:")
        print(f"   Seuil confiance: {auto_config.MIN_CONFIDENCE_THRESHOLD:.1%}")
        print(f"   Seuil Premium: {auto_config.PREMIUM_SIGNAL_THRESHOLD:.1%}")
        print(f"   Seuil Strong: {auto_config.STRONG_SIGNAL_THRESHOLD:.1%}")
        print(f"   Signaux SELL: {'✅ Activés' if auto_config.ENABLE_SELL_SIGNALS else '❌ Désactivés'}")
        print(f"   Confluence min: {auto_config.MIN_CONFLUENCE_SCORE:.1%}")
        
        print("\n📊 Features optimisées:")
        for feature, weight in auto_config.FEATURE_WEIGHTS.items():
            if weight > 0:
                print(f"   {feature}: {weight:.1%}")
        
        # OPTIMISATION 6: Configuration session améliorée
        session_config = {
            "session": "london_optimized",
            "description": "Session Londres - Signaux Optimisés",
            "trading_enabled": True,
            "data_source": "live_data",
            "options_required": False,
            "force_trading": True,
            "skip_options_validation": True,
            "bypass_options_check": True,
            "optimizations": {
                "min_confidence": 0.60,
                "enable_sell_signals": True,
                "min_confluence": 0.30,
                "signal_cooldown": 60,
                "volume_variability_check": True
            }
        }
        
        # Sauvegarder la configuration optimisée
        os.makedirs("config", exist_ok=True)
        with open("config/optimized_session.json", "w") as f:
            json.dump(session_config, f, indent=2)
        
        print(f"\n💾 Configuration optimisée sauvegardée")
        print("🎯 Lancement MIA_IA_SYSTEM avec signaux optimisés...")
        
        # Lancer le système principal avec optimisations
        from launch_24_7_orderflow_trading import main
        main()
        
    except ImportError as e:
        print(f"❌ Erreur import: {e}")
        print("💡 Vérifiez que tous les modules sont installés")
    except Exception as e:
        print(f"❌ Erreur lancement: {e}")
        print("💡 Vérifiez la configuration")

if __name__ == "__main__":
    optimiser_signaux()






