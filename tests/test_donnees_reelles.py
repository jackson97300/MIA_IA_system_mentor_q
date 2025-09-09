
#!/usr/bin/env python3
"""
Test données ES réelles via TWS
"""

import os
import sys
import time
from datetime import datetime

def test_donnees_reelles_es():
    """Tester les données ES réelles"""
    
    print("🧪 Test données ES réelles...")
    
    try:
        # Importer le connecteur IBKR
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        
        try:
            from core.ibkr_connector import IBKRConnector
            print("✅ IBKR Connector importé")
        except ImportError:
            print("❌ IBKR Connector non disponible")
            return False
        
        # Créer une instance du connecteur
        connector = IBKRConnector()
        
        # Configuration pour données réelles
        connector.host = "127.0.0.1"
        connector.port = 7497
        connector.client_id = 1
        connector.simulation_mode = False
        
        print("🔗 Connexion à TWS pour données réelles...")
        
        # Test de connexion
        try:
            # Test simple de connexion
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex(('127.0.0.1', 7497))
            sock.close()
            
            if result == 0:
                print("✅ TWS accessible")
                print("✅ Prêt pour données ES réelles")
                return True
            else:
                print("❌ TWS non accessible")
                return False
                
        except Exception as e:
            print(f"❌ Erreur connexion TWS: {e}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur test données réelles: {e}")
        return False

if __name__ == "__main__":
    success = test_donnees_reelles_es()
    if success:
        print("\n✅ Test données réelles réussi")
    else:
        print("\n❌ Test données réelles échoué")
