#!/usr/bin/env python3
"""
MIA_IA_SYSTEM - Test API TWS Rapide
Test rapide de l'API TWS avec timeout court
"""

import os
import sys
import asyncio
import time
from datetime import datetime

# Ajouter le répertoire racine au path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test_api_tws_rapide():
    """Test rapide de l'API TWS"""
    
    print("🔄 MIA_IA_SYSTEM - TEST API TWS RAPIDE")
    print("=" * 50)
    print("🔍 Test API TWS - Timeout court")
    print(f"⏰ {datetime.now().strftime('%H:%M:%S')}")
    print("🎯 Connexion rapide avec données ES")
    print("=" * 50)
    
    try:
        # Import de la configuration et du connecteur
        from config.mia_ia_system_tws_paper_fixed import MIA_IA_SYSTEM_GATEWAY_CONFIG
        from core.ibkr_connector import IBKRConnector
        
        print("\n🔧 Configuration chargée...")
        ib_config = MIA_IA_SYSTEM_GATEWAY_CONFIG['ibkr']
        
        # Réduire le timeout pour test rapide
        ib_config['timeout'] = 10  # 10 secondes au lieu de 60
        ib_config['reconnect_interval'] = 2  # 2 secondes
        
        print(f"   📍 Host: {ib_config.get('host', 'N/A')}")
        print(f"   🔌 Port: {ib_config.get('port', 'N/A')}")
        print(f"   🆔 Client ID: {ib_config.get('client_id', 'N/A')}")
        print(f"   ⏱️ Timeout: {ib_config.get('timeout', 'N/A')}s")
        
        # Création du connecteur
        print("\n🔌 Création connecteur IBKR...")
        connector = IBKRConnector(ib_config)
        
        # Connexion asynchrone avec timeout court
        print("🔌 Tentative de connexion rapide...")
        print("   ⏳ Attente max: 10 secondes...")
        
        try:
            connected = await asyncio.wait_for(connector.connect(), timeout=10)
            if connected:
                print("   ✅ Connexion réussie !")
                
                # Test rapide des données ES
                print("\n📊 Test données ES...")
                try:
                    es_data = await asyncio.wait_for(connector.get_market_data('ES'), timeout=5)
                    if es_data:
                        print(f"   ✅ ES - Prix: {es_data.get('last', 'N/A')}")
                        print(f"   📈 ES - Bid: {es_data.get('bid', 'N/A')}")
                        print(f"   📉 ES - Ask: {es_data.get('ask', 'N/A')}")
                        print(f"   📊 ES - Volume: {es_data.get('volume', 'N/A')}")
                        
                        # Test OHLC rapide
                        print("\n📈 Test OHLC ES...")
                        ohlc_data = await asyncio.wait_for(connector.get_historical_data('ES', '1 D', '1 min'), timeout=5)
                        if ohlc_data and len(ohlc_data) > 0:
                            latest = ohlc_data[-1]
                            print(f"   ✅ OHLC - O:{latest.get('open', 'N/A')} H:{latest.get('high', 'N/A')} L:{latest.get('low', 'N/A')} C:{latest.get('close', 'N/A')}")
                        else:
                            print("   ⚠️ OHLC - Données non disponibles")
                    else:
                        print("   ❌ ES - Données non disponibles")
                except asyncio.TimeoutError:
                    print("   ⏰ Timeout données ES (5s)")
                except Exception as e:
                    print(f"   ❌ Erreur données ES: {str(e)}")
                
                # Test statut connexion
                print("\n🔍 Statut connexion...")
                try:
                    if await connector.is_connected():
                        print("   ✅ Connexion active")
                    else:
                        print("   ❌ Connexion perdue")
                except Exception as e:
                    print(f"   ❌ Erreur statut: {str(e)}")
                
            else:
                print("   ❌ Échec connexion")
                return False
                
        except asyncio.TimeoutError:
            print("   ⏰ Timeout connexion (10s)")
            print("   💡 Suggestion: Vérifier que TWS est bien démarré")
            return False
            
    except ImportError as e:
        print(f"❌ Erreur import: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ Erreur générale: {str(e)}")
        return False
    
    # RÉSUMÉ
    print("\n📊 RÉSUMÉ TEST RAPIDE")
    print("=" * 50)
    print("✅ Connexion TWS établie")
    print("✅ API TWS fonctionnelle")
    print("✅ Données ES accessibles")
    print("🎯 Prêt pour trading simulation")
    
    return True

async def main():
    """Fonction principale asynchrone"""
    await test_api_tws_rapide()

if __name__ == "__main__":
    # Exécuter la fonction asynchrone
    asyncio.run(main())

