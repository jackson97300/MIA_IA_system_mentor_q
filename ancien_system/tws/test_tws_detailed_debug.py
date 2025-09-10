#!/usr/bin/env python3
"""
Debug détaillé TWS - Identification problème exact
"""
from ib_insync import *
import time
import socket
import logging

def test_tws_detailed_debug():
    """Debug détaillé de la connexion TWS"""
    print("🔍 DEBUG DÉTAILLÉ TWS")
    print("=" * 50)
    
    # Activer les logs détaillés
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger('ib_insync')
    
    print("\n📡 Test 1: Connexion socket brute")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        print("Tentative connexion socket: 127.0.0.1:7496")
        sock.connect(('127.0.0.1', 7496))
        print("✅ Connexion socket réussie")
        
        # Envoyer un message de test
        test_message = b"API\0"
        sock.send(test_message)
        print("✅ Message de test envoyé")
        
        # Attendre réponse
        response = sock.recv(1024)
        print(f"✅ Réponse reçue: {response}")
        
        sock.close()
        
    except Exception as e:
        print(f"❌ Erreur socket: {e}")
    
    print("\n📡 Test 2: Connexion IB avec logs détaillés")
    try:
        ib = IB()
        
        # Configuration détaillée
        print("Configuration IB:")
        print(f"  - Host: 127.0.0.1")
        print(f"  - Port: 7496")
        print(f"  - Client ID: 999")
        print(f"  - Timeout: 20 secondes")
        
        # Connexion avec timeout plus long
        ib.connect(
            '127.0.0.1', 
            7496, 
            clientId=999,
            timeout=20
        )
        
        print("✅ Connexion IB réussie !")
        
        # Test simple
        print("\n📊 Test données compte...")
        account_summary = ib.accountSummary()
        print(f"✅ Compte: {len(account_summary)} éléments")
        
        ib.disconnect()
        return True
        
    except Exception as e:
        print(f"❌ Erreur connexion IB: {e}")
        print(f"Type d'erreur: {type(e).__name__}")
        
        # Diagnostic spécifique
        if "TimeoutError" in str(e):
            print("\n🔧 DIAGNOSTIC TIMEOUT:")
            print("1. TWS peut être en mode 'Read-Only'")
            print("2. API Settings incomplets")
            print("3. Firewall bloque la connexion")
            print("4. TWS pas complètement démarré")
        
        return False

def check_tws_api_settings():
    """Vérification des paramètres API TWS"""
    print("\n📋 VÉRIFICATION PARAMÈTRES API TWS")
    print("=" * 50)
    
    print("✅ PARAMÈTRES À VÉRIFIER DANS TWS:")
    print("   File → Global Configuration → API → Settings:")
    print("   - Enable ActiveX and Socket Clients: ✅")
    print("   - Socket port: 7496 ✅")
    print("   - Master API client ID: 0 ✅")
    print("   - Read-Only API: ❌ (DÉCOCHER pour test)")
    print("   - Download open orders on connection: ✅")
    print("   - Create API order log file: ✅")
    print("   - Inclure les données de marché dans le journal API: ✅")
    
    print("\n⚠️ PARAMÈTRES CRITIQUES:")
    print("   File → Global Configuration → API → Précautions:")
    print("   - Bypass Order Precautions for API Orders: ✅")
    print("   - Bypass Bond warning for API Orders: ✅")
    print("   - Bypass negative yield to worst confirmations for API Orders: ✅")
    print("   - Bypass Called Bond warning for API Orders: ✅")
    print("   - Bypass 'same action per trade' warning for API orders: ✅")
    print("   - Bypass price-based validity risk warning for API Orders: ✅")
    print("   - Bypass Redirect Order warning for Stock API Orders: ✅")
    print("   - Bypass No Overfill protection precaution for destinations where implied natively: ✅")

if __name__ == "__main__":
    print("🔍 DEBUG DÉTAILLÉ TWS - IDENTIFICATION PROBLÈME")
    print("=" * 60)
    
    # Debug détaillé
    success = test_tws_detailed_debug()
    
    # Vérification paramètres
    check_tws_api_settings()
    
    if success:
        print("\n🎉 PROBLÈME RÉSOLU !")
    else:
        print("\n❌ PROBLÈME PERSISTANT")
        print("Vérifiez les paramètres API dans TWS") 