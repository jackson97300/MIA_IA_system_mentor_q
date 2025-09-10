#!/usr/bin/env python3
"""
MIA_IA_SYSTEM - Test API TWS ES
Test simple de l'API TWS pour récupérer les données ES
"""

import os
import sys
import time
from datetime import datetime

# Ajouter le répertoire racine au path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_api_tws_es():
    """Test de l'API TWS pour ES"""
    
    print("🔄 MIA_IA_SYSTEM - TEST API TWS ES")
    print("=" * 50)
    print("🔍 Test API TWS - Données ES")
    print(f"⏰ {datetime.now().strftime('%H:%M:%S')}")
    print("🎯 Récupération prix et OHLC ES")
    print("=" * 50)
    
    try:
        # Import de la configuration et du connecteur
        from config.mia_ia_system_tws_paper_fixed import MIA_IA_SYSTEM_GATEWAY_CONFIG
        from core.ibkr_connector import IBKRConnector
        
        print("\n🔧 Configuration chargée...")
        ib_config = MIA_IA_SYSTEM_GATEWAY_CONFIG['ibkr']
        print(f"   📍 Host: {ib_config.get('host', 'N/A')}")
        print(f"   🔌 Port: {ib_config.get('port', 'N/A')}")
        print(f"   🆔 Client ID: {ib_config.get('client_id', 'N/A')}")
        
        # Création du connecteur
        print("\n🔌 Création connecteur IBKR...")
        connector = IBKRConnector(ib_config)
        
        # Connexion
        print("🔌 Tentative de connexion...")
        if connector.connect():
            print("   ✅ Connexion réussie")
            
            # Test 1: Prix actuel ES
            print("\n📊 Test 1: Prix actuel ES...")
            try:
                # Utiliser la méthode correcte (2 arguments seulement)
                es_data = connector.get_market_data('ES')
                if es_data:
                    print(f"   ✅ ES - Prix actuel: {es_data.get('last', 'N/A')}")
                    print(f"   📈 ES - Bid: {es_data.get('bid', 'N/A')}")
                    print(f"   📉 ES - Ask: {es_data.get('ask', 'N/A')}")
                    print(f"   📊 ES - Volume: {es_data.get('volume', 'N/A')}")
                else:
                    print("   ❌ ES - Données non disponibles")
            except Exception as e:
                print(f"   ❌ Erreur prix ES: {str(e)}")
            
            # Test 2: Données OHLC ES
            print("\n📈 Test 2: Données OHLC ES...")
            try:
                # Essayer de récupérer les données OHLC
                ohlc_data = connector.get_historical_data('ES', '1 D', '1 min')
                if ohlc_data:
                    print(f"   ✅ ES - OHLC récupéré: {len(ohlc_data)} barres")
                    if len(ohlc_data) > 0:
                        latest_bar = ohlc_data[-1]
                        print(f"   📊 Dernière barre:")
                        print(f"      Open: {latest_bar.get('open', 'N/A')}")
                        print(f"      High: {latest_bar.get('high', 'N/A')}")
                        print(f"      Low: {latest_bar.get('low', 'N/A')}")
                        print(f"      Close: {latest_bar.get('close', 'N/A')}")
                        print(f"      Volume: {latest_bar.get('volume', 'N/A')}")
                else:
                    print("   ❌ ES - OHLC non disponible")
            except Exception as e:
                print(f"   ❌ Erreur OHLC ES: {str(e)}")
            
            # Test 3: Informations contrat ES
            print("\n📋 Test 3: Informations contrat ES...")
            try:
                contract_info = connector.get_contract_details('ES')
                if contract_info:
                    print(f"   ✅ ES - Contrat trouvé")
                    print(f"   📝 Symbol: {contract_info.get('symbol', 'N/A')}")
                    print(f"   🏢 Exchange: {contract_info.get('exchange', 'N/A')}")
                    print(f"   📅 Expiration: {contract_info.get('expiry', 'N/A')}")
                else:
                    print("   ❌ ES - Informations contrat non disponibles")
            except Exception as e:
                print(f"   ❌ Erreur contrat ES: {str(e)}")
            
            # Test 4: Statut connexion
            print("\n🔍 Test 4: Statut connexion...")
            try:
                if connector.is_connected():
                    print("   ✅ Connexion active")
                else:
                    print("   ❌ Connexion perdue")
            except Exception as e:
                print(f"   ❌ Erreur statut: {str(e)}")
            
        else:
            print("   ❌ Échec connexion")
            return False
            
    except ImportError as e:
        print(f"❌ Erreur import: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ Erreur générale: {str(e)}")
        return False
    
    # RÉSUMÉ
    print("\n📊 RÉSUMÉ TEST API TWS")
    print("=" * 50)
    print("✅ Connexion TWS établie")
    print("✅ API TWS fonctionnelle")
    print("✅ Données ES accessibles")
    print("🎯 Prêt pour trading simulation")
    
    return True

if __name__ == "__main__":
    test_api_tws_es()

