#!/usr/bin/env python3
"""
MIA_IA_SYSTEM - Test Client ID Différent
Test avec différents Client ID pour résoudre le conflit
"""

import os
import sys
import asyncio
import time
from datetime import datetime

# Ajouter le répertoire racine au path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test_client_ids():
    """Test avec différents Client ID"""
    
    print("🔄 MIA_IA_SYSTEM - TEST CLIENT ID DIFFÉRENTS")
    print("=" * 60)
    print("🔍 Test avec différents Client ID")
    print(f"⏰ {datetime.now().strftime('%H:%M:%S')}")
    print("🎯 Résolution conflit Client ID")
    print("=" * 60)
    
    # Liste des Client ID à tester
    client_ids = [999, 1000, 1001, 1002, 1003]
    
    for client_id in client_ids:
        print(f"\n🔍 Test Client ID: {client_id}")
        print("-" * 40)
        
        try:
            # Import de la configuration
            from config.mia_ia_system_tws_paper_fixed import MIA_IA_SYSTEM_GATEWAY_CONFIG
            from core.ibkr_connector import IBKRConnector
            
            # Modifier le Client ID
            ib_config = MIA_IA_SYSTEM_GATEWAY_CONFIG['ibkr'].copy()
            ib_config['client_id'] = client_id
            ib_config['timeout'] = 15  # Timeout plus court
            
            print(f"   📍 Host: {ib_config.get('host', 'N/A')}")
            print(f"   🔌 Port: {ib_config.get('port', 'N/A')}")
            print(f"   🆔 Client ID: {ib_config.get('client_id', 'N/A')}")
            print(f"   ⏱️ Timeout: {ib_config.get('timeout', 'N/A')}s")
            
            # Création du connecteur
            connector = IBKRConnector(ib_config)
            
            # Test de connexion
            print("   🔌 Tentative de connexion...")
            try:
                connected = await asyncio.wait_for(connector.connect(), timeout=15)
                if connected:
                    print("   ✅ Connexion réussie !")
                    
                    # Test rapide des données ES
                    print("   📊 Test données ES...")
                    try:
                        es_data = await asyncio.wait_for(connector.get_market_data('ES'), timeout=5)
                        if es_data:
                            print(f"   ✅ ES - Prix: {es_data.get('last', 'N/A')}")
                            print(f"   📈 ES - Bid: {es_data.get('bid', 'N/A')}")
                            print(f"   📉 ES - Ask: {es_data.get('ask', 'N/A')}")
                            
                            # SUCCÈS ! Trouvé un Client ID qui fonctionne
                            print(f"\n🎉 SUCCÈS ! Client ID {client_id} fonctionne")
                            print("=" * 50)
                            print("✅ Connexion TWS établie")
                            print("✅ API TWS fonctionnelle")
                            print("✅ Données ES accessibles")
                            print(f"🎯 Client ID optimal: {client_id}")
                            
                            # Recommandation de mise à jour
                            print(f"\n💡 RECOMMANDATION:")
                            print(f"   Mettre à jour la configuration avec Client ID: {client_id}")
                            print(f"   Dans config/mia_ia_system_tws_paper_fixed.py")
                            print(f"   Changer 'client_id': 1 en 'client_id': {client_id}")
                            
                            return client_id
                        else:
                            print("   ❌ ES - Données non disponibles")
                    except asyncio.TimeoutError:
                        print("   ⏰ Timeout données ES")
                    except Exception as e:
                        print(f"   ❌ Erreur données ES: {str(e)}")
                    
                    # Test statut connexion
                    try:
                        if await connector.is_connected():
                            print("   ✅ Connexion active")
                        else:
                            print("   ❌ Connexion perdue")
                    except Exception as e:
                        print(f"   ❌ Erreur statut: {str(e)}")
                    
                else:
                    print("   ❌ Échec connexion")
                    
            except asyncio.TimeoutError:
                print("   ⏰ Timeout connexion (15s)")
            except Exception as e:
                print(f"   ❌ Erreur connexion: {str(e)}")
                
        except Exception as e:
            print(f"   ❌ Erreur générale: {str(e)}")
        
        # Attendre avant le prochain test
        await asyncio.sleep(2)
    
    # Aucun Client ID n'a fonctionné
    print(f"\n❌ Aucun Client ID n'a fonctionné")
    print("=" * 50)
    print("🔧 Actions recommandées:")
    print("   1. Vérifier les paramètres API dans TWS")
    print("   2. Redémarrer TWS complètement")
    print("   3. Vérifier qu'aucun autre client n'est connecté")
    print("   4. Tester avec IB Gateway au lieu de TWS")
    
    return None

async def main():
    """Fonction principale asynchrone"""
    working_client_id = await test_client_ids()
    
    if working_client_id:
        print(f"\n📋 PLAN D'ACTION:")
        print(f"1. ✅ Client ID {working_client_id} fonctionne")
        print(f"2. 🔧 Mettre à jour la configuration")
        print(f"3. 🔄 Relancer le système MIA")
        print(f"4. 🎯 Prêt pour trading simulation")
    else:
        print(f"\n📋 PLAN D'ACTION:")
        print(f"1. 🔧 Vérifier paramètres API TWS")
        print(f"2. 🔄 Redémarrer TWS")
        print(f"3. 🔄 Tester avec IB Gateway")
        print(f"4. 🔄 Relancer diagnostic")

if __name__ == "__main__":
    # Exécuter la fonction asynchrone
    asyncio.run(main())

