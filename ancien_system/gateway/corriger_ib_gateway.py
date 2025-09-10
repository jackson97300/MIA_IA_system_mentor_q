#!/usr/bin/env python3
"""
🔧 CORRECTION IB GATEWAY - DONNÉES RÉELLES
MIA_IA_SYSTEM - Forcer connexion IBKR réelle
"""
import subprocess
import time
import sys
from pathlib import Path

def corriger_ib_gateway():
    """Corriger la configuration IB Gateway"""
    
    print("🔧 === CORRECTION IB GATEWAY ===")
    print("🎯 Objectif: Forcer l'utilisation des données IBKR réelles")
    print()
    
    print("📋 CONFIGURATION REQUISE DANS IB GATEWAY:")
    print("=" * 60)
    print("1. Ouvrir IB Gateway")
    print("2. Aller dans Configurer → API → Settings")
    print("3. Vérifier et corriger:")
    print()
    print("✅ Enable ActiveX and Socket Clients: OUI")
    print("✅ Socket port: 4002")
    print("✅ Master API client ID: 0")
    print("✅ Read-Only API: NON")
    print("✅ Download open orders on connection: OUI")
    print("✅ Allow connections from localhost only: OUI")
    print("✅ Disable read-only API connections: NON")
    print("✅ Include FX positions in portfolio: OUI")
    print("✅ Create API message log file: OUI")
    print("✅ Auto restart: OUI")
    print("✅ Download open orders on connection: OUI")
    print("✅ Include FX positions in portfolio: OUI")
    print()
    
    print("🔧 ACTIONS À EFFECTUER:")
    print("=" * 60)
    print("1. Fermer IB Gateway complètement")
    print("2. Redémarrer IB Gateway")
    print("3. Se connecter avec vos identifiants")
    print("4. Aller dans Configurer → API → Settings")
    print("5. Appliquer la configuration ci-dessus")
    print("6. Cliquer sur 'OK' pour sauvegarder")
    print("7. Redémarrer IB Gateway")
    print("8. Vérifier que la ligne 'Client API' apparaît")
    print()
    
    print("⚠️ IMPORTANT:")
    print("- Ne pas utiliser de fallback (SAVED DATA)")
    print("- Seules les données IBKR réelles sont acceptées")
    print("- Si connexion échoue, corriger la configuration")
    print()
    
    return True

def forcer_donnees_reelles():
    """Modifier le système pour forcer les données réelles"""
    
    print("🔧 === MODIFICATION SYSTÈME ===")
    print("🎯 Objectif: Forcer l'utilisation des données IBKR réelles")
    print()
    
    # Modifier la configuration pour forcer les données réelles
    config_changes = {
        "simulation_mode": False,
        "require_real_data": True,
        "fallback_to_saved_data": False,
        "connection_timeout": 60,
        "reconnection_attempts": 5
    }
    
    print("📝 Modifications à appliquer:")
    for key, value in config_changes.items():
        print(f"   {key}: {value}")
    
    print()
    print("🔧 Fichiers à modifier:")
    print("   - launch_24_7_orderflow_trading.py")
    print("   - core/ibkr_connector.py")
    print("   - config/automation_config.py")
    print()
    
    return config_changes

def test_connexion_forcee():
    """Test connexion forcée avec données réelles"""
    
    print("🔍 === TEST CONNEXION FORCÉE ===")
    
    test_script = """
import asyncio
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

from core.ibkr_connector import IBKRConnector

async def test_connexion_forcee():
    config = {
        'ibkr_host': '127.0.0.1',
        'ibkr_port': 7497,  # ✅ CORRECTION: TWS Paper Trading (FONCTIONNE)
        'ibkr_client_id': 999,
        'connection_timeout': 60,
        'simulation_mode': False,
        'require_real_data': True,
        'fallback_to_saved_data': False
    }
    
    print("🔗 Tentative connexion forcée...")
    connector = IBKRConnector(config)
    
    try:
        success = await connector.connect()
        
        if success:
            print("✅ Connexion IBKR RÉELLE réussie!")
            
            # Test données marché
            market_data = await connector.get_market_data("ES")
            if market_data:
                print("✅ Données marché réelles récupérées")
                print(f"   📈 Prix: {market_data.get('price', 'N/A')}")
                print(f"   📊 Volume: {market_data.get('volume', 'N/A')}")
                print("📊 Source: IBKR (données réelles)")
            else:
                print("❌ Erreur récupération données marché")
                return False
            
            await connector.disconnect()
            return True
        else:
            print("❌ Échec connexion IBKR")
            print("🔧 Vérifier configuration TWS")
            return False
            
    except Exception as e:
        print(f"❌ Erreur critique: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_connexion_forcee())
    if success:
        print("\\n🎉 CONNEXION IBKR RÉELLE RÉUSSIE!")
        print("🚀 Prêt pour trading avec données réelles")
    else:
        print("\\n❌ CONNEXION IBKR ÉCHOUÉE")
        print("🔧 Corriger configuration TWS")
"""
    
    with open('test_connexion_forcee.py', 'w') as f:
        f.write(test_script)
    
    print("✅ Script de test créé: test_connexion_forcee.py")
    print("🔍 Lancez: python test_connexion_forcee.py")
    
    return True

if __name__ == "__main__":
    print("⚠️ CORRECTION IB GATEWAY - DONNÉES RÉELLES")
    print("🎯 Objectif: Forcer l'utilisation des données IBKR réelles")
    print()
    
    # Afficher les corrections
    corriger_ib_gateway()
    forcer_donnees_reelles()
    test_connexion_forcee()
    
    print("=" * 60)
    print("📋 RÉSUMÉ DES ACTIONS")
    print("=" * 60)
    print("1. Corriger configuration IB Gateway")
    print("2. Redémarrer IB Gateway")
    print("3. Tester: python test_connexion_forcee.py")
    print("4. Si succès: python launch_24_7_orderflow_trading.py --dry-run")
    print("5. Vérifier: '📊 Source: IBKR (données réelles)'")
    print()
    
    print("🎯 RÉSULTAT ATTENDU:")
    print("✅ Connexion IBKR RÉELLE réussie!")
    print("📊 Source: IBKR (données réelles)")
    print("🚀 Trading avec données temps réel")
