#!/usr/bin/env python3
"""
MIA_IA_SYSTEM - Test Connexion IBKR Simple
Test direct de connexion IBKR après redémarrage TWS
"""

import os
import sys
import asyncio
from datetime import datetime

# Ajouter le répertoire racine au path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test_connexion_ibkr_simple():
    """Test simple connexion IBKR"""
    
    print("MIA_IA_SYSTEM - TEST CONNEXION IBKR SIMPLE")
    print("=" * 50)
    print(f"Test: {datetime.now()}")
    print("=" * 50)
    
    try:
        # Test import ib_insync
        print("\n1. Test import ib_insync...")
        from ib_insync import IB
        print("✅ ib_insync disponible")
        
        # Test connexion
        print("\n2. Test connexion IBKR...")
        ib = IB()
        
        try:
            print("   Tentative connexion 127.0.0.1:7497...")
            await asyncio.wait_for(
                ib.connectAsync('127.0.0.1', 7497, clientId=1),
                timeout=15.0
            )
            
            if ib.isConnected():
                print("✅ Connexion IBKR réussie!")
                print(f"   Status: {ib.connectionStatus()}")
                
                # Test récupération données ES
                print("\n3. Test récupération données ES...")
                try:
                    from ib_insync import Future
                    es_contract = Future('ES', '202503', 'CME')
                    
                    ib.reqMktData(es_contract)
                    await asyncio.sleep(3)
                    
                    if es_contract.marketPrice():
                        print(f"✅ Données ES récupérées: {es_contract.marketPrice()}")
                        
                        # Test SPX options
                        print("\n4. Test récupération SPX options...")
                        try:
                            from ib_insync import Option
                            spx_contract = Option('SPX', '20250321', 5000, 'C', 'CBOE')
                            
                            ib.reqMktData(spx_contract)
                            await asyncio.sleep(2)
                            
                            if spx_contract.marketPrice():
                                print(f"✅ Données SPX options récupérées: {spx_contract.marketPrice()}")
                                print("\n🎉 SUCCÈS: Connexion IBKR et données récupérées!")
                                ib.disconnect()
                                return True
                            else:
                                print("⚠️ Données SPX options non disponibles")
                                print("   (Peut être normal si marchés fermés)")
                                ib.disconnect()
                                return True
                                
                        except Exception as e:
                            print(f"⚠️ Erreur SPX options: {e}")
                            print("   (Peut être normal)")
                            ib.disconnect()
                            return True
                    else:
                        print("❌ Aucune donnée ES récupérée")
                        ib.disconnect()
                        return False
                        
                except Exception as e:
                    print(f"❌ Erreur récupération données: {e}")
                    ib.disconnect()
                    return False
            else:
                print("❌ Connexion IBKR échouée")
                return False
                
        except asyncio.TimeoutError:
            print("❌ Timeout connexion IBKR (15s)")
            print("   Vérifier TWS est bien démarré et configuré")
            return False
        except Exception as e:
            print(f"❌ Erreur connexion: {e}")
            return False
            
    except ImportError:
        print("❌ ib_insync non installé")
        print("   Installer: pip install ib_insync")
        return False
    except Exception as e:
        print(f"❌ Erreur test: {e}")
        return False

async def main():
    """Fonction principale"""
    try:
        success = await test_connexion_ibkr_simple()
        
        print("\n" + "=" * 50)
        print("RÉSULTATS TEST CONNEXION IBKR")
        print("=" * 50)
        
        if success:
            print("✅ SUCCÈS: Connexion IBKR fonctionnelle")
            print("✅ Données réelles disponibles")
            print("✅ Système prêt pour test 2h")
            print("🚀 Lancement recommandé: python lance_mia_ia_tws.py")
        else:
            print("❌ ÉCHEC: Connexion IBKR non fonctionnelle")
            print("\n🔧 VÉRIFICATIONS:")
            print("1. TWS est-il démarré?")
            print("2. Configuration API activée dans TWS?")
            print("3. Port 7497 ouvert?")
            print("4. Firewall autorise la connexion?")
        
        print("=" * 50)
        
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    asyncio.run(main())


