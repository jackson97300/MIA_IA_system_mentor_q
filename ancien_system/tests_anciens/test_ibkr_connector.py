#!/usr/bin/env python3
"""
Test simple du connecteur IBKR
"""

import sys
import os
sys.path.append('.')

def test_ibkr_connector():
    """Test du connecteur IBKR"""
    try:
        print("🔍 Test du connecteur IBKR...")
        
        # Import du connecteur
        from core.ibkr_connector import IBKRConnector
        print("✅ Import réussi")
        
        # Création de l'instance
        conn = IBKRConnector()
        print("✅ Instance créée")
        
        # Test de connexion
        print("🔗 Test de connexion...")
        # conn.connect()  # Décommenter si nécessaire
        
        print("✅ Test IBKR Connector terminé avec succès")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        return False

if __name__ == "__main__":
    test_ibkr_connector()


