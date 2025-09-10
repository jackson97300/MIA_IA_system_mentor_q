#!/usr/bin/env python3
"""
Test TWS avec Client ID 999 pour éviter les conflits
"""
from ib_insync import *
import time

def test_tws_client_999():
    """Test connexion TWS avec Client ID 999"""
    print("🔌 Test connexion TWS avec Client ID 999...")
    
    try:
        # Connexion TWS avec Client ID 999
        ib = IB()
        print("📡 Tentative connexion TWS: 127.0.0.1:7496 (Client ID: 999)")
        
        ib.connect(
            '127.0.0.1', 
            7496, 
            clientId=999,  # Client ID différent
            timeout=15
        )
        
        print("✅ Connexion TWS réussie avec Client ID 999 !")
        
        # Test données compte
        print("\n📊 Test données compte...")
        account_summary = ib.accountSummary()
        print(f"✅ Compte connecté: {len(account_summary)} éléments trouvés")
        
        # Afficher quelques détails
        for item in account_summary[:3]:
            print(f"   {item.tag}: {item.value}")
        
        # Déconnexion
        ib.disconnect()
        print("\n✅ Test TWS Client ID 999 terminé avec succès !")
        return True
        
    except Exception as e:
        print(f"❌ Erreur connexion TWS Client ID 999: {e}")
        return False

if __name__ == "__main__":
    test_tws_client_999() 