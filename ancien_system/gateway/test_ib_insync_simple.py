#!/usr/bin/env python3
"""
Test simple avec IB_insync (plus stable)
"""

import asyncio
import time

async def test_ib_insync():
    """Test avec IB_insync"""
    print("🚀 TEST IB_INSYNC - SOLUTION ALTERNATIVE")
    print("=" * 50)
    
    try:
        from ib_insync import IB, util
        
        # Créer client IB_insync
        ib = IB()
        
        print("🔗 Connexion IB_insync...")
        print("   Host: 127.0.0.1")
        print("   Port: 4002 (IB Gateway)")
        print("   Client ID: 1")
        
        # Connexion
        await ib.connectAsync(
            host='127.0.0.1',
            port=4002,
            clientId=1,
            timeout=10
        )
        
        if ib.isConnected():
            print("✅ CONNEXION RÉUSSIE avec IB_insync!")
            
            # Test données de base
            try:
                # Récupérer info compte
                account = ib.accountSummary()
                print(f"📊 Compte: {len(account)} éléments")
                
                for item in account[:3]:  # Afficher 3 premiers
                    print(f"   - {item.tag}: {item.value} {item.currency}")
                
                # Test contrats ES
                contracts = ib.reqContractDetails(util.Contract(symbol='ES', secType='FUT', exchange='CME'))
                print(f"📈 Contrats ES: {len(contracts)} trouvés")
                
                if contracts:
                    es_contract = contracts[0].contract
                    print(f"   - ES Contract: {es_contract.localSymbol}")
                    
                    # Test données marché
                    tickers = ib.reqMktData(es_contract)
                    await asyncio.sleep(2)
                    
                    if tickers:
                        ticker = tickers[0]
                        print(f"   - ES Price: {ticker.marketPrice()}")
                        print(f"   - ES Bid: {ticker.bid}")
                        print(f"   - ES Ask: {ticker.ask}")
                
            except Exception as e:
                print(f"⚠️ Erreur données: {e}")
            
            # Déconnexion
            ib.disconnect()
            print("✅ Test IB_insync terminé avec succès")
            
            # Configuration recommandée
            config = {
                "ibkr_host": "127.0.0.1",
                "ibkr_port": 4002,
                "ibkr_client_id": 1,
                "use_ib_insync": True,
                "connection_timeout": 20
            }
            
            print(f"\n🔧 Configuration MIA_IA_SYSTEM (IB_insync):")
            print(f"   Host: {config['ibkr_host']}")
            print(f"   Port: {config['ibkr_port']}")
            print(f"   Client ID: {config['ibkr_client_id']}")
            print(f"   IB_insync: {config['use_ib_insync']}")
            
            return True
            
        else:
            print("❌ ÉCHEC CONNEXION IB_insync")
            return False
            
    except ImportError:
        print("❌ IB_insync non installé")
        print("💡 Installez avec: pip install ib_insync")
        return False
    except Exception as e:
        print(f"❌ Erreur IB_insync: {e}")
        return False

async def main():
    """Fonction principale"""
    success = await test_ib_insync()
    
    if success:
        print("\n🎉 SUCCÈS - IB_insync fonctionne!")
        print("💡 Utilisez IB_insync au lieu de l'API native")
    else:
        print("\n❌ ÉCHEC - Vérifiez la configuration API IB Gateway")

if __name__ == "__main__":
    asyncio.run(main())






