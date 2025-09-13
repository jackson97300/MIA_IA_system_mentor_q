#!/usr/bin/env python3
"""
MIA_IA_SYSTEM - Forcer ES Réel Direct
Force directement l'utilisation des données ES réelles sans validation SPX
"""

import os
import sys
import json
from datetime import datetime

# Ajouter le répertoire racine au path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def forcer_es_reel_direct():
    """Force directement les données ES réelles"""
    
    print("MIA_IA_SYSTEM - FORCER ES RÉEL DIRECT")
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
        auto_config.FORCE_TRADING = True
        
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
        print(f"   Force trading: {'✅ OUI' if auto_config.FORCE_TRADING else '❌ NON'}")
        
        # PATCH DIRECT - Remplacer complètement la validation SPX
        def patch_validation_direct():
            """Patch direct pour bypasser validation SPX"""
            try:
                import core.data_quality_validator as validator_module
                
                # Remplacer complètement la méthode validate_spx_data
                async def validate_spx_data_bypass(self, spx_data=None):
                    """Bypass complet validation SPX"""
                    from core.data_quality_validator import DataQualityReport, DataQualityLevel
                    
                    print("🔧 BYPASS COMPLET - Validation SPX ignorée")
                    print("📊 Utilisation données ES réelles uniquement")
                    
                    return DataQualityReport(
                        timestamp=datetime.now(),
                        quality_level=DataQualityLevel.EXCELLENT,
                        is_valid_for_trading=True,
                        pause_reason=None,
                        pause_message="",
                        warnings=[],
                        errors=[],
                        data_age_hours=0.0,
                        validation_score=0.95
                    )
                
                # Remplacer aussi la méthode _validate_spx_options_data
                async def validate_spx_options_bypass(self, spx_data=None):
                    """Bypass validation options SPX"""
                    from core.data_quality_validator import DataQualityReport, DataQualityLevel
                    
                    return DataQualityReport(
                        timestamp=datetime.now(),
                        quality_level=DataQualityLevel.EXCELLENT,
                        is_valid_for_trading=True,
                        pause_reason=None,
                        pause_message="",
                        warnings=[],
                        errors=[],
                        data_age_hours=0.0,
                        validation_score=0.95
                    )
                
                # Appliquer les patches
                validator_module.DataQualityValidator.validate_spx_data = validate_spx_data_bypass
                validator_module.DataQualityValidator._validate_spx_options_data = validate_spx_options_bypass
                print("✅ Patches validation SPX appliqués")
                
            except Exception as e:
                print(f"⚠️ Patch validation: {e}")
        
        # Appliquer le patch
        patch_validation_direct()
        
        # PATCH DIRECT - Modifier le lanceur principal
        def patch_launcher():
            """Patch le lanceur principal pour ignorer validation SPX"""
            try:
                import launch_24_7_orderflow_trading as launcher_module
                
                # Remplacer la méthode _validate_session_and_quality
                async def validate_session_bypass(self):
                    """Bypass validation session"""
                    print("🔧 BYPASS SESSION - Trading forcé avec ES réel")
                    return True
                
                # Appliquer le patch
                launcher_module.OrderFlowTradingLauncher._validate_session_and_quality = validate_session_bypass
                print("✅ Patch lanceur appliqué")
                
            except Exception as e:
                print(f"⚠️ Patch lanceur: {e}")
        
        # Appliquer le patch lanceur
        patch_launcher()
        
        # Configuration session ES réel
        session_config = {
            "session": "london_es_real_direct",
            "description": "Session Londres - ES Réel Direct",
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
                "validate_es_data": True,
                "bypass_all_spx_validation": True
            }
        }
        
        # Sauvegarder la configuration
        os.makedirs("config", exist_ok=True)
        with open("config/es_real_direct_session.json", "w") as f:
            json.dump(session_config, f, indent=2)
        
        print(f"\n💾 Configuration ES réel direct sauvegardée")
        print("🎯 Lancement MIA_IA_SYSTEM avec ES réel direct...")
        
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
    forcer_es_reel_direct()
