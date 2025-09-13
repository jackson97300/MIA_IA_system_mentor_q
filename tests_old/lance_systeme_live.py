#!/usr/bin/env python3
"""
MIA_IA_SYSTEM - Lance Systeme LIVE
Lance le systeme de trading en mode LIVE avec TWS
"""

import os
import sys
import asyncio
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def lance_systeme_live():
    """Lance le systeme en mode LIVE"""
    
    print("MIA_IA_SYSTEM - LANCEMENT MODE LIVE")
    print("=" * 50)
    print("Lancement du systeme de trading en mode LIVE")
    print("TWS doit etre en mode LIVE (pas Paper)")
    print("=" * 50)

    try:
        # Import du lanceur principal
        from launch_24_7_orderflow_trading import OrderFlowTradingLauncher
        
        print("\n1. VERIFICATION CONFIGURATION")
        print("=" * 30)
        
        # Configuration pour mode LIVE
        config = {
            "mode": "LIVE",
            "ibkr_host": "127.0.0.1",
            "ibkr_port": 7497,  # TWS port
            "ibkr_client_id": 1,
            "timeout": 15,
            "require_real_data": True,
            "simulation_mode": False,
            "fallback_to_saved_data": False,
            "options_disabled": True,  # Temporairement desactive
            "feature_weights": {
                "volume_confirmation": 0.35,
                "vwap_trend_signal": 0.25,
                "sierra_pattern_strength": 0.20,
                "es_nq_correlation": 0.15,
                "level_proximity": 0.05,
                "gamma_levels_proximity": 0.0,  # Desactive
                "options_flow_bias": 0.0        # Desactive
            }
        }
        
        print("Configuration LIVE appliquee")
        print(f"   Mode: {config['mode']}")
        print(f"   Port: {config['ibkr_port']}")
        print(f"   Client ID: {config['ibkr_client_id']}")
        print(f"   Options: Desactivees")
        
        print("\n2. TEST CONNEXION LIVE")
        print("=" * 30)
        
        # Test connexion rapide
        from core.ibkr_connector import IBKRConnector
        
        ibkr = IBKRConnector()
        ibkr.host = config["ibkr_host"]
        ibkr.port = config["ibkr_port"]
        ibkr.client_id = config["ibkr_client_id"]
        ibkr.timeout = config["timeout"]
        
        print("Test connexion TWS LIVE...")
        await ibkr.connect()
        
        if not await ibkr.is_connected():
            print("ECHEC: Impossible de se connecter a TWS")
            print("Verifiez que TWS est en mode LIVE")
            return False
            
        print("SUCCES: Connexion TWS etablie")
        
        # Test donnees ES
        data = await ibkr.get_market_data("ES")
        if data:
            prix = data.get('last', 0)
            print(f"Prix ES: {prix}")
            
            if prix > 6500:
                print("ALERTE: Prix anormalement eleve")
                print("TWS est probablement encore en mode Paper")
                print("Veuillez configurer TWS en mode LIVE")
                await ibkr.disconnect()
                return False
            else:
                print("SUCCES: Prix ES normal (mode LIVE)")
        else:
            print("ATTENTION: Aucune donnee ES")
            await ibkr.disconnect()
            return False
            
        await ibkr.disconnect()
        
        print("\n3. LANCEMENT SYSTEME")
        print("=" * 30)
        
        # Lancement du systeme principal
        print("Lancement du systeme de trading...")
        
        launcher = OrderFlowTradingLauncher()
        
        # Configuration du launcher
        launcher.config = config
        
        # Lancement
        await launcher.start_trading()
        
        return True
        
    except Exception as e:
        print(f"ERREUR: {e}")
        return False

if __name__ == "__main__":
    print("PREREQUIS:")
    print("1. TWS doit etre en mode LIVE")
    print("2. API doit etre activee")
    print("3. Connexion etablie")
    
    response = input("\nTWS est-il en mode LIVE et connecte? (oui/non): ")
    
    if response.lower() in ['oui', 'yes', 'o', 'y']:
        print("\nLancement du systeme...")
        success = asyncio.run(lance_systeme_live())
        
        if success:
            print("\nSUCCES: Systeme lance en mode LIVE")
        else:
            print("\nECHEC: Probleme de lancement")
    else:
        print("\nVeuillez d'abord configurer TWS en mode LIVE")
        print("Puis relancez ce script")





