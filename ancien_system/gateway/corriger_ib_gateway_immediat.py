#!/usr/bin/env python3
"""
MIA_IA_SYSTEM - Correction Immédiate IB Gateway
Solution rapide pour faire fonctionner IB Gateway
"""

import subprocess
import time
import os

def corriger_ib_gateway():
    """Correction immédiate IB Gateway"""
    print("🔧 CORRECTION IMMÉDIATE IB GATEWAY")
    print("=" * 50)
    
    print("📋 ÉTAPES À SUIVRE :")
    print()
    print("1. 🔄 REDÉMARRER IB GATEWAY")
    print("   - Fermer complètement IB Gateway")
    print("   - Attendre 10 secondes")
    print("   - Relancer IB Gateway")
    print()
    
    print("2. ⚙️ CONFIGURER API SETTINGS")
    print("   Dans IB Gateway, aller dans :")
    print("   Configurer → API → Settings")
    print()
    print("   ✅ Vérifier ces paramètres :")
    print("   - Enable ActiveX and Socket Clients : OUI")
    print("   - Socket port : 4002 (Paper Trading)")
    print("   - Master API client ID : 0")
    print("   - Read-Only API : NON")
    print("   - Download open orders on connection : OUI")
    print("   - Allow connections from localhost only : OUI")
    print()
    
    print("3. 🧪 TESTER CONNEXION")
    print("   Après configuration, lancer :")
    print("   python test_ib_gateway_optimise.py")
    print()
    
    print("4. 🚀 LANCER MIA_IA_SYSTEM")
    print("   Si connexion réussie :")
    print("   python lance_mia_ia_tws.py")
    print()

def test_connexion_rapide():
    """Test connexion rapide"""
    print("🧪 TEST CONNEXION RAPIDE")
    print("=" * 30)
    
    try:
        import socket
        
        # Test port 4002
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        result = sock.connect_ex(('127.0.0.1', 4002))
        sock.close()
        
        if result == 0:
            print("✅ Port 4002 accessible")
            
            # Test connexion Python
            try:
                from ib_insync import IB
                ib = IB()
                ib.connect('127.0.0.1', 4002, clientId=999, timeout=10)
                
                if ib.isConnected():
                    print("✅ Connexion IB Gateway réussie !")
                    account = ib.accountSummary()
                    print(f"✅ Compte: {len(account)} éléments")
                    
                    # Afficher solde
                    for item in account:
                        if item.tag == 'NetLiquidation':
                            print(f"   - NetLiquidation: {item.value} {item.currency}")
                            break
                    
                    ib.disconnect()
                    return True
                else:
                    print("❌ Connexion échouée")
                    ib.disconnect()
                    return False
                    
            except Exception as e:
                print(f"❌ Erreur connexion Python: {e}")
                return False
        else:
            print("❌ Port 4002 non accessible")
            return False
            
    except Exception as e:
        print(f"❌ Erreur test: {e}")
        return False

def lancer_mia_ia_system():
    """Lancer MIA_IA_SYSTEM"""
    print("🚀 LANCEMENT MIA_IA_SYSTEM")
    print("=" * 30)
    
    try:
        # Vérifier que le système est prêt
        print("🔍 Vérification système...")
        
        # Test composants critiques
        try:
            from core.ibkr_connector import IBKRConnector
            from strategies.signal_generator import create_signal_generator
            from execution.simple_trader import SimpleBattleNavaleTrader
            
            print("✅ Composants critiques disponibles")
            
            # Configuration IBKR
            config = {
                'ibkr_host': '127.0.0.1',
                'ibkr_port': 4002,  # IB Gateway Paper Trading
                'ibkr_client_id': 999,
                'connection_timeout': 30
            }
            
            print("🔧 Configuration IBKR :")
            print(f"   - Host: {config['ibkr_host']}")
            print(f"   - Port: {config['ibkr_port']}")
            print(f"   - Client ID: {config['ibkr_client_id']}")
            
            # Test connexion
            connector = IBKRConnector(config)
            
            print("\n🔗 Test connexion MIA_IA_SYSTEM...")
            import asyncio
            success = asyncio.run(connector.connect())
            
            if success:
                print("✅ MIA_IA_SYSTEM connecté !")
                print("🎉 Prêt pour trading !")
                
                # Afficher options
                print("\n📋 OPTIONS DE LANCEMENT :")
                print("1. 🧪 Mode test : python lance_test_2min_simple.py")
                print("2. 📊 Mode paper : python lance_mia_ia_tws.py")
                print("3. 🔄 Mode 24/7 : python launch_24_7_orderflow_trading.py")
                
                return True
            else:
                print("❌ Échec connexion MIA_IA_SYSTEM")
                return False
                
        except ImportError as e:
            print(f"❌ Module manquant: {e}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur lancement: {e}")
        return False

def main():
    """Fonction principale"""
    print("🚀 MIA_IA_SYSTEM - Correction IB Gateway")
    print("=" * 60)
    print(f"Date: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 1. Instructions correction
    corriger_ib_gateway()
    
    # 2. Test connexion
    print("Voulez-vous tester la connexion maintenant ? (o/n)")
    response = input().lower()
    
    if response in ['o', 'oui', 'y', 'yes']:
        success = test_connexion_rapide()
        
        if success:
            print("\n🎉 IB GATEWAY CORRIGÉ !")
            
            # 3. Lancer MIA_IA_SYSTEM
            print("\nVoulez-vous lancer MIA_IA_SYSTEM ? (o/n)")
            response2 = input().lower()
            
            if response2 in ['o', 'oui', 'y', 'yes']:
                lancer_mia_ia_system()
        else:
            print("\n❌ Correction nécessaire")
            print("💡 Suivez les instructions ci-dessus")
    else:
        print("\n📋 Suivez les instructions de correction")
        print("🔧 Corrigez IB Gateway puis relancez ce script")

if __name__ == "__main__":
    main()
















