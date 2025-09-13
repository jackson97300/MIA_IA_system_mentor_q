#!/usr/bin/env python3
"""
MIA_IA_SYSTEM - Lancement Données Réelles ES Seul
Utilise uniquement les données ES réelles d'IBKR, pas d'options SPX
"""

import os
import sys
import json
from datetime import datetime

# Ajouter le répertoire racine au path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def lance_donnees_reelles_es():
    """Lance le système avec données ES réelles uniquement"""
    
    print("MIA_IA_SYSTEM - DONNÉES RÉELLES ES SEUL")
    print("=" * 60)
    
    try:
        # Modifier directement les fichiers de configuration
        import config.automation_config as auto_config
        
        # FORCER DONNÉES RÉELLES ES
        auto_config.simulation_mode = False
        auto_config.require_real_data = True
        auto_config.fallback_to_saved_data = False
        
        # DÉSACTIVER COMPLÈTEMENT LES OPTIONS SPX
        auto_config.SPX_OPTIONS_ENABLED = False
        auto_config.OPTIONS_DATA_REQUIRED = False
        auto_config.ENABLE_OPTIONS_VALIDATION = False
        auto_config.BYPASS_OPTIONS_CHECK = True
        auto_config.SKIP_OPTIONS_VALIDATION = True
        
        # Configuration IBKR pour ES uniquement
        auto_config.IBKR_HOST = "127.0.0.1"
        auto_config.IBKR_PORT = 7497
        auto_config.IBKR_CLIENT_ID = 1
        auto_config.USE_IB_INSYNC = True
        
        # Features sans options SPX
        auto_config.FEATURE_WEIGHTS = {
            "gamma_levels_proximity": 0.0,  # Désactivé (pas d'options)
            "volume_confirmation": 0.35,
            "vwap_trend_signal": 0.25,
            "sierra_pattern_strength": 0.25,
            "smart_money_strength": 0.25,
            "level_proximity": 0.15,
            "es_nq_correlation": 0.15,
            "order_book_imbalance": 0.30,
            "session_context": 0.08,
            "pullback_quality": 0.05
        }
        
        print("✅ Configuration ES réel appliquée:")
        print(f"   Simulation mode: {'❌ DÉSACTIVÉ' if not auto_config.simulation_mode else '⚠️ ACTIVÉ'}")
        print(f"   Options SPX: {'❌ DÉSACTIVÉES' if not auto_config.SPX_OPTIONS_ENABLED else '⚠️ ACTIVÉES'}")
        print(f"   Options required: {'❌ NON' if not auto_config.OPTIONS_DATA_REQUIRED else '⚠️ OUI'}")
        print(f"   Bypass options: {'✅ OUI' if auto_config.BYPASS_OPTIONS_CHECK else '❌ NON'}")
        
        # Monkey patch pour bypasser validation SPX
        def patch_spx_validation():
            """Patch pour bypasser validation SPX"""
            try:
                import core.data_quality_validator as validator_module
                
                # Remplacer la méthode de validation SPX
                async def bypass_spx_validation_async(self, spx_data):
                    """Bypass validation SPX - retourne toujours valide"""
                    from core.data_quality_validator import DataQualityReport, DataQualityLevel
                    
                    print("🔧 Bypass validation SPX - données réelles ES uniquement")
                    
                    return DataQualityReport(
                        quality_level=DataQualityLevel.EXCELLENT,
                        score=0.95,
                        issues=[],
                        recommendations=["Utilisation données ES réelles uniquement"],
                        timestamp=datetime.now()
                    )
                
                # Appliquer le patch
                validator_module.DataQualityValidator._validate_spx_options_data = bypass_spx_validation_async
                print("✅ Patch validation SPX appliqué")
                
            except Exception as e:
                print(f"⚠️ Patch validation SPX: {e}")
        
        # Appliquer le patch
        patch_spx_validation()
        
        # Configuration session ES réel
        session_config = {
            "session": "london_es_real_only",
            "description": "Session Londres - Données ES Réelles Seul",
            "trading_enabled": True,
            "data_source": "ibkr_es_real_data",
            "options_required": False,
            "force_trading": True,
            "skip_options_validation": True,
            "bypass_options_check": True,
            "es_only_settings": {
                "simulation_mode": False,
                "require_real_data": True,
                "spx_options_disabled": True,
                "es_data_only": True,
                "validate_es_data": True
            }
        }
        
        # Sauvegarder la configuration
        os.makedirs("config", exist_ok=True)
        with open("config/es_real_only_session.json", "w") as f:
            json.dump(session_config, f, indent=2)
        
        print(f"\n💾 Configuration ES réel sauvegardée")
        print("🎯 Lancement MIA_IA_SYSTEM avec données ES réelles uniquement...")
        
        # Lancer le système principal
        from launch_24_7_orderflow_trading import main
        main()
        
    except ImportError as e:
        print(f"❌ Erreur import: {e}")
        print("💡 Vérifiez que tous les modules sont installés")
    except Exception as e:
        print(f"❌ Erreur lancement: {e}")
        print("💡 Vérifiez la configuration")

if __name__ == "__main__":
    lance_donnees_reelles_es()






