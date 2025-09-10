#!/usr/bin/env python3
"""
🔍 TEST DONNÉES IBKR RÉELLES - SESSION LONDRES
MIA_IA_SYSTEM - Vérification réception données live
"""
import asyncio
import sys
import time
from datetime import datetime
from pathlib import Path

# Ajouter le chemin du projet
sys.path.append(str(Path(__file__).parent))

from core.logger import get_logger
from core.ibkr_connector import IBKRConnector

logger = get_logger(__name__)

async def test_ibkr_real_data():
    """Test de réception des données IBKR réelles"""
    print("🔍 === TEST DONNÉES IBKR RÉELLES - SESSION LONDRES ===")
    print(f"⏰ Heure actuelle: {datetime.now().strftime('%H:%M:%S')}")
    print()
    
    # Initialiser connexion IBKR
    ibkr_connector = IBKRConnector(
        host="127.0.0.1",
        port=4002,
        client_id=999
    )
    
    try:
        print("🔗 Connexion à IBKR...")
        connection_success = await ibkr_connector.connect()
        
        if not connection_success:
            print("❌ Échec connexion IBKR")
            return False
        
        print("✅ Connexion IBKR réussie")
        print()
        
        # Test données ES (S&P 500)
        print("📊 === TEST DONNÉES ES (S&P 500) ===")
        es_data = await ibkr_connector.get_market_data("ES")
        
        if es_data:
            print("✅ Données ES reçues:")
            print(f"   💰 Prix: {es_data.get('last_price', 'N/A')}")
            print(f"   📊 Volume: {es_data.get('volume', 'N/A')}")
            print(f"   📈 Bid: {es_data.get('bid', 'N/A')}")
            print(f"   📉 Ask: {es_data.get('ask', 'N/A')}")
            print(f"   ⏰ Timestamp: {es_data.get('timestamp', 'N/A')}")
        else:
            print("❌ Aucune donnée ES reçue")
        
        print()
        
        # Test données NQ (NASDAQ)
        print("📱 === TEST DONNÉES NQ (NASDAQ) ===")
        nq_data = await ibkr_connector.get_market_data("NQ")
        
        if nq_data:
            print("✅ Données NQ reçues:")
            print(f"   💰 Prix: {nq_data.get('last_price', 'N/A')}")
            print(f"   📊 Volume: {nq_data.get('volume', 'N/A')}")
            print(f"   📈 Bid: {nq_data.get('bid', 'N/A')}")
            print(f"   📉 Ask: {nq_data.get('ask', 'N/A')}")
            print(f"   ⏰ Timestamp: {nq_data.get('timestamp', 'N/A')}")
        else:
            print("❌ Aucune donnée NQ reçue")
        
        print()
        
        # Test Level 2 ES
        print("📊 === TEST LEVEL 2 ES ===")
        level2_data = await ibkr_connector.get_level2_data("ES")
        
        if level2_data:
            print("✅ Level 2 ES reçu:")
            print(f"   📈 Bid Volume: {level2_data.get('bid_volume', 'N/A')}")
            print(f"   📉 Ask Volume: {level2_data.get('ask_volume', 'N/A')}")
            print(f"   ⚖️ Imbalance: {level2_data.get('imbalance', 'N/A')}")
        else:
            print("❌ Aucun Level 2 ES reçu")
        
        print()
        
        # Test données options SPX
        print("🎯 === TEST DONNÉES OPTIONS SPX ===")
        spx_options = await ibkr_connector.get_complete_options_flow("SPX")
        
        if spx_options:
            print("✅ Données SPX reçues:")
            print(f"   📊 Put/Call Ratio: {spx_options.get('put_call_ratio', 'N/A')}")
            print(f"   💰 Gamma Exposure: {spx_options.get('gamma_exposure', 'N/A')}")
            print(f"   🏦 Dealer Position: {spx_options.get('dealer_position', 'N/A')}")
        else:
            print("❌ Aucune donnée SPX reçue")
        
        print()
        
        # Test données options QQQ
        print("📱 === TEST DONNÉES OPTIONS QQQ ===")
        qqq_options = await ibkr_connector.get_complete_options_flow("QQQ")
        
        if qqq_options:
            print("✅ Données QQQ reçues:")
            print(f"   📊 Put/Call Ratio: {qqq_options.get('put_call_ratio', 'N/A')}")
            print(f"   💰 Gamma Exposure: {qqq_options.get('gamma_exposure', 'N/A')}")
            print(f"   🏦 Dealer Position: {qqq_options.get('dealer_position', 'N/A')}")
        else:
            print("❌ Aucune donnée QQQ reçue")
        
        print()
        
        # Test données compte
        print("💰 === TEST DONNÉES COMPTE ===")
        account_data = await ibkr_connector.get_account_info()
        
        if account_data:
            print("✅ Données compte reçues:")
            print(f"   💰 Equity: {account_data.get('equity', 'N/A')}")
            print(f"   💵 Available: {account_data.get('available_funds', 'N/A')}")
            print(f"   📊 Net Liquidation: {account_data.get('net_liquidation', 'N/A')}")
        else:
            print("❌ Aucune donnée compte reçue")
        
        print()
        
        # Résumé
        print("📊 === RÉSUMÉ RÉCEPTION DONNÉES ===")
        data_received = []
        
        if es_data:
            data_received.append("✅ ES")
        else:
            data_received.append("❌ ES")
        
        if nq_data:
            data_received.append("✅ NQ")
        else:
            data_received.append("❌ NQ")
        
        if level2_data:
            data_received.append("✅ Level2")
        else:
            data_received.append("❌ Level2")
        
        if spx_options:
            data_received.append("✅ SPX")
        else:
            data_received.append("❌ SPX")
        
        if qqq_options:
            data_received.append("✅ QQQ")
        else:
            data_received.append("❌ QQQ")
        
        if account_data:
            data_received.append("✅ Compte")
        else:
            data_received.append("❌ Compte")
        
        print("   " + " | ".join(data_received))
        
        # Déconnexion
        await ibkr_connector.disconnect()
        print("\n🔌 Déconnexion IBKR")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur test: {e}")
        return False

async def main():
    """Fonction principale"""
    success = await test_ibkr_real_data()
    
    if success:
        print("\n✅ === TEST TERMINÉ AVEC SUCCÈS ===")
        print("📊 Données IBKR réelles reçues")
    else:
        print("\n❌ === TEST ÉCHOUÉ ===")
        print("⚠️ Problème de réception données")

if __name__ == "__main__":
    asyncio.run(main())
























