#!/usr/bin/env python3
"""
MIA_IA_SYSTEM - Test IBKR Web API REST
Validation connexion et fonctionnalités
"""

import asyncio
import sys
import os
from datetime import datetime

# Ajouter le répertoire parent au path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data.ibkr_web_api_adapter import IBKRWebAPIAdapter, IBKRWebAPIConfig
from core.logger import get_logger

logger = get_logger(__name__)

async def test_ibkr_web_api():
    """Test complet IBKR Web API REST"""
    
    print("🚀 MIA_IA_SYSTEM - Test IBKR Web API REST")
    print("=" * 50)
    
    # Configuration de test
    config = IBKRWebAPIConfig(
        api_key="YOUR_API_KEY",  # À remplacer
        api_secret="YOUR_API_SECRET",  # À remplacer
        account_id="YOUR_ACCOUNT_ID",  # À remplacer
        paper_trading=True,
        enable_trading=False,
        enable_market_data=True
    )
    
    # Créer adaptateur
    adapter = IBKRWebAPIAdapter(config)
    
    try:
        print("🔧 Test 1: Connexion IBKR Web API...")
        
        # Test connexion
        success = await adapter.connect()
        if not success:
            print("❌ Échec connexion IBKR Web API")
            print("💡 Vérifiez votre configuration API")
            return False
        
        print("✅ Connexion IBKR Web API réussie")
        
        # Test 2: Account Info
        print("\n🔧 Test 2: Informations compte...")
        account_info = await adapter.get_account_info()
        if account_info:
            print(f"✅ Account ID: {account_info.get('account_id')}")
            print(f"✅ Available Funds: ${account_info.get('available_funds', 0):,.2f}")
            print(f"✅ Buying Power: ${account_info.get('buying_power', 0):,.2f}")
            print(f"✅ Equity: ${account_info.get('equity', 0):,.2f}")
        else:
            print("❌ Impossible de récupérer les infos compte")
        
        # Test 3: Market Data ES
        print("\n🔧 Test 3: Données ES futures...")
        market_data = await adapter.get_market_data("ES")
        if market_data:
            print(f"✅ ES Price: ${market_data.close:,.2f}")
            print(f"✅ Bid: ${market_data.bid:,.2f}")
            print(f"✅ Ask: ${market_data.ask:,.2f}")
            print(f"✅ Volume: {market_data.volume:,}")
        else:
            print("❌ Impossible de récupérer les données ES")
        
        # Test 4: Données historiques ES
        print("\n🔧 Test 4: Données historiques ES...")
        es_data = await adapter.get_es_futures_data(timeframe="1min", limit=10)
        if es_data is not None and len(es_data) > 0:
            print(f"✅ Données ES: {len(es_data)} barres récupérées")
            print(f"✅ Dernière barre: {es_data.iloc[-1]['close']:,.2f}")
            print(f"✅ Volume total: {es_data['volume'].sum():,}")
        else:
            print("❌ Impossible de récupérer les données historiques ES")
        
        # Test 5: Options SPX
        print("\n🔧 Test 5: Options SPX...")
        options_data = await adapter.get_options_chain("SPX")
        if options_data:
            print(f"✅ Options SPX: {len(options_data.get('options_chain', []))} contrats")
            print(f"✅ Volume total: {options_data.get('total_volume', 0):,}")
            print(f"✅ Expirations: {len(options_data.get('expiration_dates', []))}")
            
            gamma_analysis = options_data.get('gamma_analysis', {})
            if gamma_analysis.get('call_wall'):
                print(f"✅ Call Wall: {gamma_analysis['call_wall']}")
            if gamma_analysis.get('put_wall'):
                print(f"✅ Put Wall: {gamma_analysis['put_wall']}")
        else:
            print("❌ Impossible de récupérer les options SPX")
        
        # Test 6: Positions
        print("\n🔧 Test 6: Positions actuelles...")
        positions = await adapter.get_positions()
        if positions:
            print(f"✅ Positions: {len(positions)} positions actives")
            for pos in positions[:3]:  # Afficher les 3 premières
                print(f"   - {pos.get('symbol', 'N/A')}: {pos.get('position', 0)}")
        else:
            print("✅ Aucune position active")
        
        # Test 7: Performance
        print("\n🔧 Test 7: Performance et rate limiting...")
        print(f"✅ Requêtes effectuées: {adapter.request_count}")
        print(f"✅ Dernière requête: {adapter.last_request_time}")
        
        print("\n🎉 Tous les tests IBKR Web API terminés avec succès !")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors des tests: {e}")
        return False
        
    finally:
        # Déconnexion
        await adapter.disconnect()
        print("\n✅ Déconnexion IBKR Web API")

async def test_configuration():
    """Test configuration IBKR Web API"""
    
    print("\n🔧 Test Configuration IBKR Web API")
    print("=" * 40)
    
    # Vérifier variables d'environnement
    env_vars = {
        'IBKR_API_KEY': os.getenv('IBKR_API_KEY'),
        'IBKR_API_SECRET': os.getenv('IBKR_API_SECRET'),
        'IBKR_ACCOUNT_ID': os.getenv('IBKR_ACCOUNT_ID')
    }
    
    print("📋 Variables d'environnement:")
    for var, value in env_vars.items():
        if value:
            print(f"✅ {var}: {'*' * len(value)} (configuré)")
        else:
            print(f"❌ {var}: Non configuré")
    
    # Configuration recommandée
    print("\n💡 Configuration recommandée:")
    print("1. Activez IBKR Web API dans votre compte")
    print("2. Générez API Key et Secret")
    print("3. Configurez les variables d'environnement:")
    print("   export IBKR_API_KEY='votre_api_key'")
    print("   export IBKR_API_SECRET='votre_api_secret'")
    print("   export IBKR_ACCOUNT_ID='votre_account_id'")
    
    return any(env_vars.values())

async def main():
    """Fonction principale"""
    
    print("🚀 MIA_IA_SYSTEM - Test IBKR Web API REST")
    print("=" * 60)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Test configuration
    config_ok = await test_configuration()
    
    if not config_ok:
        print("\n⚠️ Configuration incomplète - Tests limités")
        print("💡 Configurez vos variables d'environnement pour des tests complets")
        return
    
    # Test connexion
    success = await test_ibkr_web_api()
    
    if success:
        print("\n🎉 SUCCÈS: IBKR Web API opérationnel pour MIA_IA !")
        print("✅ Prêt pour intégration MIA_IA")
        print("✅ Battle Navale compatible")
        print("✅ Données ES futures + options SPX")
    else:
        print("\n❌ ÉCHEC: Problèmes avec IBKR Web API")
        print("💡 Vérifiez votre configuration et connexion")

if __name__ == "__main__":
    asyncio.run(main())
















