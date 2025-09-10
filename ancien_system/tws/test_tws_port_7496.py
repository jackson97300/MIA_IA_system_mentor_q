#!/usr/bin/env python3
"""
Test connexion TWS port 7496 (live)
"""
from ib_insync import *
import time
import socket

def test_port_connection():
    """Test connexion socket basique"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex(('127.0.0.1', 7496))
        sock.close()
        return result == 0
    except Exception as e:
        print(f"❌ Erreur test port: {e}")
        return False

def test_tws_port_7496():
    """Test connexion TWS port 7496"""
    print("🔌 Test connexion TWS port 7496...")
    
    # Test port d'abord
    print("📡 Test port 7496...")
    if not test_port_connection():
        print("❌ Port 7496 non accessible - TWS pas démarré ou mal configuré")
        return False
    print("✅ Port 7496 accessible")
    
    # Configuration TWS port 7496
    config = {
        'host': '127.0.0.1',
        'port': 7496,  # Port TWS live
        'client_id': 1,
        'timeout': 30
    }
    
    try:
        # Connexion TWS
        ib = IB()
        print(f"📡 Tentative connexion TWS: {config['host']}:{config['port']}")
        print("⚠️ Assurez-vous que TWS est ouvert et connecté")
        
        ib.connect(
            config['host'], 
            config['port'], 
            clientId=config['client_id'],
            timeout=10
        )
        
        print("✅ Connexion TWS réussie !")
        
        # Test données compte
        print("\n📊 Test données compte...")
        account_summary = ib.accountSummary()
        print(f"✅ Compte connecté: {len(account_summary)} éléments trouvés")
        
        # Afficher quelques détails du compte
        for item in account_summary[:3]:
            print(f"   {item.tag}: {item.value}")
        
        # Test données marché ES
        print("\n📈 Test données marché ES...")
        contract = Future('ES', '202412', 'CME')
        
        try:
            ib.qualifyContracts(contract)
            print("✅ Contrat ES qualifié")
            
            # Subscribe market data
            ib.reqMktData(contract)
            time.sleep(3)
            
            ticker = ib.ticker(contract)
            if ticker and ticker.marketName():
                print(f"✅ Données ES: {ticker.marketName()} - Bid: {ticker.bid} Ask: {ticker.ask}")
            else:
                print("⚠️ Pas de données ES en temps réel")
                
        except Exception as e:
            print(f"⚠️ Erreur données ES: {e}")
        
        # Déconnexion
        ib.disconnect()
        print("\n✅ Test TWS port 7496 terminé avec succès !")
        return True
        
    except Exception as e:
        print(f"❌ Erreur connexion TWS port 7496: {e}")
        return False

if __name__ == "__main__":
    test_tws_port_7496() 