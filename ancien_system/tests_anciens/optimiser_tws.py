
#!/usr/bin/env python3
"""
Optimisation connexion TWS
"""

import time
import socket
from datetime import datetime

def optimiser_connexion_tws():
    """Optimiser la connexion TWS"""
    
    print("🔌 Optimisation connexion TWS...")
    
    # Test connexion TWS
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex(('127.0.0.1', 7497))
        sock.close()
        
        if result == 0:
            print("✅ Port 7497 accessible")
        else:
            print("❌ Port 7497 bloqué - Vérifier TWS")
            return False
    
    except Exception as e:
        print(f"❌ Erreur test connexion: {e}")
        return False
    
    # Recommandations d'optimisation
    recommendations = [
        "1. Redémarrer TWS complètement",
        "2. Vérifier que TWS est en mode Paper Trading",
        "3. Vérifier que l'API est activée dans TWS",
        "4. Changer Client ID si nécessaire (1, 2, 3...)",
        "5. Vérifier les permissions firewall",
        "6. Redémarrer le système si nécessaire"
    ]
    
    print("\n📋 RECOMMANDATIONS TWS:")
    for rec in recommendations:
        print(f"   {rec}")
    
    return True

if __name__ == "__main__":
    optimiser_connexion_tws()
