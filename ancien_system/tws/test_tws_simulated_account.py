#!/usr/bin/env python3
"""
Test connexion TWS compte simulé spécifique
"""
from ib_insync import *
import time
import socket

def test_port_connection():
    """Test connexion socket basique"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex(('127.0.0.1', 7497))
        sock.close()
        return result == 0
    except Exception as e:
        print(f"❌ Erreur test port: {e}")
        return False

def test_tws_simulated_account():
    """Test connexion TWS compte simulé"""
    print("🔌 Test connexion TWS compte simulé...")
    
    # Test port d'abord
    print("📡 Test port 7497...")
    if not test_port_connection():
        print("❌ Port 7497 non accessible - TWS pas démarré ou mal configuré")
        return False
    print("✅ Port 7497 accessible")
    
    # Configuration TWS simulé
    config = {
        'host': '127.0.0.1',
        'port': 7497,  # Port TWS simulé
        'client_id': 1,
        'timeout': 30
    }
    
    try:
        # Connexion TWS avec plus de logs
        ib = IB()
        print(f"📡 Tentative connexion TWS: {config['host']}:{config['port']}")
        print("⚠️ Assurez-vous que TWS est ouvert et connecté au compte simulé")
        
        # Test connexion avec timeout court d'abord
        ib.connect(
            config['host'], 
            config['port'], 
            clientId=config['client_id'],
            timeout=10  # Timeout court pour diagnostic
        )
        
        print("✅ Connexion TWS réussie !")
        
        # Test données compte avec plus de détails
        print("\n📊 Test données compte simulé...")
        account_summary = ib.accountSummary()
        print(f"✅ Compte connecté: {len(account_summary)} éléments trouvés")
        
        # Afficher quelques détails du compte
        for item in account_summary[:3]:  # Premiers 3 éléments
            print(f"   {item.tag}: {item.value}")
        
        # Test données marché ES
        print("\n📈 Test données marché ES...")
        contract = Future('ES', '202412', 'CME')
        
        try:
            ib.qualifyContracts(contract)
            print("✅ Contrat ES qualifié")
            
            # Subscribe market data
            ib.reqMktData(contract)
            time.sleep(3)  # Attendre données
            
            ticker = ib.ticker(contract)
            if ticker and ticker.marketName():
                print(f"✅ Données ES: {ticker.marketName()} - Bid: {ticker.bid} Ask: {ticker.ask}")
            else:
                print("⚠️ Pas de données ES en temps réel (normal hors heures marché)")
                
        except Exception as e:
            print(f"⚠️ Erreur données ES: {e}")
        
        # Test données historiques
        print("\n📚 Test données historiques...")
        try:
            bars = ib.reqHistoricalData(
                contract,
                endDateTime='',
                durationStr='1 D',
                barSizeSetting='1 hour',
                whatToShow='TRADES',
                useRTH=True
            )
            
            if bars:
                print(f"✅ Données historiques: {len(bars)} barres trouvées")
                print(f"   Dernière barre: {bars[-1].date} - Close: {bars[-1].close}")
            else:
                print("⚠️ Pas de données historiques (vérifier permissions)")
                
        except Exception as e:
            print(f"⚠️ Erreur données historiques: {e}")
        
        # Déconnexion
        ib.disconnect()
        print("\n✅ Test TWS compte simulé terminé avec succès !")
        return True
        
    except Exception as e:
        print(f"❌ Erreur connexion TWS compte simulé: {e}")
        print("\n🔧 SOLUTIONS POSSIBLES:")
        print("1. Vérifiez que TWS est connecté au compte SIMULÉ")
        print("2. Vérifiez API Settings dans TWS (File → Global Configuration)")
        print("3. Vérifiez que le compte simulé a les permissions API")
        print("4. Essayez de redémarrer TWS")
        return False

if __name__ == "__main__":
    test_tws_simulated_account() 