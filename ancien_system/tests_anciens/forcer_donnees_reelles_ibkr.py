#!/usr/bin/env python3
"""
MIA_IA_SYSTEM - Forcer Données Réelles IBKR
Désactive complètement la simulation et force les données réelles
"""

import os
import sys
import json
from datetime import datetime

# Ajouter le répertoire racine au path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def forcer_donnees_reelles():
    """Force l'utilisation des données réelles IBKR"""
    
    print("MIA_IA_SYSTEM - FORCER DONNÉES RÉELLES IBKR")
    print("=" * 60)
    
    try:
        # Modifier directement les fichiers de configuration
        import config.automation_config as auto_config
        
        # FORCER DONNÉES RÉELLES - Désactiver simulation
        auto_config.simulation_mode = False  # ❌ DÉSACTIVER SIMULATION
        auto_config.require_real_data = True  # ✅ FORCER DONNÉES RÉELLES
        auto_config.fallback_to_saved_data = False  # ❌ PAS DE FALLBACK
        
        # Configuration IBKR pour données réelles
        auto_config.IBKR_HOST = "127.0.0.1"
        auto_config.IBKR_PORT = 7497  # TWS Paper Trading
        auto_config.IBKR_CLIENT_ID = 1
        auto_config.USE_IB_INSYNC = True
        
        # Configuration données réelles
        auto_config.MARKET_DATA_TYPE = 1  # Données temps réel
        auto_config.ENABLE_REAL_TIME_BARS = True
        auto_config.ENABLE_TICK_DATA = True
        auto_config.ENABLE_LEVEL2_DATA = True
        
        # Validation stricte des données
        auto_config.VALIDATE_REAL_DATA = True
        auto_config.REJECT_SIMULATED_DATA = True
        auto_config.MIN_DATA_QUALITY_SCORE = 0.8
        
        # Configuration OrderFlow réelle
        auto_config.ORDERFLOW_CONFIG = {
            "use_real_volume": True,
            "use_real_delta": True,
            "use_real_bid_ask": True,
            "min_volume_change": 5.0,
            "min_delta_change": 2.0,
            "validate_data_source": True,
            "reject_static_data": True
        }
        
        print("✅ Configuration données réelles appliquée:")
        print(f"   Simulation mode: {'❌ DÉSACTIVÉ' if not auto_config.simulation_mode else '⚠️ ACTIVÉ'}")
        print(f"   Require real data: {'✅ OUI' if auto_config.require_real_data else '❌ NON'}")
        print(f"   Fallback disabled: {'✅ OUI' if not auto_config.fallback_to_saved_data else '❌ NON'}")
        print(f"   Market data type: {auto_config.MARKET_DATA_TYPE}")
        print(f"   Real-time bars: {'✅ Activé' if auto_config.ENABLE_REAL_TIME_BARS else '❌ Désactivé'}")
        print(f"   Tick data: {'✅ Activé' if auto_config.ENABLE_TICK_DATA else '❌ Désactivé'}")
        print(f"   Level 2 data: {'✅ Activé' if auto_config.ENABLE_LEVEL2_DATA else '❌ Désactivé'}")
        
        # Configuration session données réelles
        session_config = {
            "session": "london_real_data",
            "description": "Session Londres - Données Réelles IBKR",
            "trading_enabled": True,
            "data_source": "ibkr_real_data",
            "options_required": False,
            "force_trading": True,
            "skip_options_validation": True,
            "bypass_options_check": True,
            "real_data_settings": {
                "simulation_mode": False,
                "require_real_data": True,
                "fallback_disabled": True,
                "market_data_type": 1,
                "validate_data_quality": True,
                "reject_static_data": True
            }
        }
        
        # Sauvegarder la configuration
        os.makedirs("config", exist_ok=True)
        with open("config/real_data_session.json", "w") as f:
            json.dump(session_config, f, indent=2)
        
        print(f"\n💾 Configuration données réelles sauvegardée")
        
        # Monkey patch pour forcer données réelles dans IBKR connector
        print("\n🔧 Application patch IBKR connector...")
        
        # Patch pour désactiver simulation dans IBKR connector
        def patch_ibkr_connector():
            """Patch pour forcer données réelles dans IBKR connector"""
            try:
                import core.ibkr_connector as ibkr_module
                
                # Remplacer la méthode get_market_data pour forcer données réelles
                async def get_real_market_data(self, symbol_or_contract) -> Dict[str, Any]:
                    """Version patchée pour forcer données réelles"""
                    from datetime import datetime
                    import asyncio
                    
                    # DÉSACTIVER COMPLÈTEMENT LA SIMULATION
                    self.simulation_mode = False
                    
                    # Extraire le symbole
                    if isinstance(symbol_or_contract, str):
                        symbol = symbol_or_contract
                        contract = None
                    elif hasattr(symbol_or_contract, 'symbol'):
                        symbol = symbol_or_contract.symbol
                        contract = symbol_or_contract
                    elif isinstance(symbol_or_contract, dict) and 'symbol' in symbol_or_contract:
                        symbol = symbol_or_contract['symbol']
                        contract = symbol_or_contract
                    else:
                        raise ValueError(f"Symbol type not supported: {type(symbol_or_contract)}")
                    
                    # VÉRIFIER CONNEXION IBKR
                    if not self.is_connected():
                        raise ConnectionError("IBKR non connecté - données réelles requises")
                    
                    # RÉCUPÉRER DONNÉES RÉELLES
                    if self.use_ib_insync and self.ib_client:
                        # Utiliser le contrat fourni ou du cache
                        if contract is not None:
                            use_contract = contract
                        elif symbol in self.contracts:
                            use_contract = self.contracts[symbol]
                        else:
                            raise ValueError(f"Aucun contrat disponible pour {symbol}")
                        
                        # Demander données réelles avec snapshot
                        ticker = self.ib_client.reqMktData(use_contract, '', True, False)
                        
                        # Attendre données réelles
                        await asyncio.sleep(1.0)
                        
                        # Vérifier que les données sont réelles (pas -1)
                        if ticker.last == -1 and ticker.close == -1:
                            raise ValueError("Données IBKR invalides - vérifier connexion")
                        
                        return {
                            'symbol': symbol,
                            'last': ticker.last if ticker.last != -1 else ticker.close,
                            'bid': ticker.bid if ticker.bid != -1 else None,
                            'ask': ticker.ask if ticker.ask != -1 else None,
                            'volume': ticker.volume if ticker.volume != -1 else 0,
                            'open': ticker.open if ticker.open != -1 else None,
                            'high': ticker.high if ticker.high != -1 else None,
                            'low': ticker.low if ticker.low != -1 else None,
                            'close': ticker.close if ticker.close != -1 else None,
                            'timestamp': datetime.now(),
                            'mode': 'REAL_DATA_IBKR'  # Marquer comme données réelles
                        }
                    else:
                        raise ConnectionError("IBKR client non disponible")
                
                # Appliquer le patch
                ibkr_module.IBKRConnector.get_market_data = get_real_market_data
                print("✅ Patch IBKR connector appliqué (données réelles forcées)")
                
            except Exception as e:
                print(f"⚠️ Patch IBKR connector: {e}")
        
        # Appliquer le patch
        patch_ibkr_connector()
        
        print("🎯 Lancement MIA_IA_SYSTEM avec données réelles IBKR...")
        
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
    forcer_donnees_reelles()






