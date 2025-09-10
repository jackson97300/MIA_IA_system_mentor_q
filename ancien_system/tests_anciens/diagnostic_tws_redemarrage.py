#!/usr/bin/env python3
"""
MIA_IA_SYSTEM - Diagnostic TWS Redémarrage
Diagnostic complet après redémarrage de TWS
"""

import os
import sys
import subprocess
import time
import asyncio
from datetime import datetime

# Ajouter le répertoire racine au path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def verifier_processus_tws():
    """Vérifier si TWS est en cours d'exécution"""
    print("1. VÉRIFICATION PROCESSUS TWS")
    print("-" * 30)
    
    try:
        # Vérifier processus TWS
        result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq TWS.exe'], 
                              capture_output=True, text=True, shell=True)
        
        if 'TWS.exe' in result.stdout:
            print("✅ TWS.exe détecté dans les processus")
            lines = result.stdout.strip().split('\n')
            for line in lines:
                if 'TWS.exe' in line:
                    print(f"   {line.strip()}")
        else:
            print("❌ TWS.exe non détecté")
            return False
            
        # Vérifier processus Gateway
        result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq ibgateway.exe'], 
                              capture_output=True, text=True, shell=True)
        
        if 'ibgateway.exe' in result.stdout:
            print("✅ ibgateway.exe détecté")
        else:
            print("⚠️ ibgateway.exe non détecté (normal si TWS utilisé)")
            
        return True
        
    except Exception as e:
        print(f"❌ Erreur vérification processus: {e}")
        return False

def verifier_port_7497():
    """Vérifier si le port 7497 est ouvert"""
    print("\n2. VÉRIFICATION PORT 7497")
    print("-" * 30)
    
    try:
        # Vérifier port avec netstat
        result = subprocess.run(['netstat', '-an'], 
                              capture_output=True, text=True, shell=True)
        
        if '7497' in result.stdout:
            print("✅ Port 7497 détecté dans netstat")
            lines = result.stdout.strip().split('\n')
            for line in lines:
                if '7497' in line:
                    print(f"   {line.strip()}")
        else:
            print("❌ Port 7497 non détecté")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ Erreur vérification port: {e}")
        return False

def verifier_firewall():
    """Vérifier les règles firewall"""
    print("\n3. VÉRIFICATION FIREWALL")
    print("-" * 30)
    
    try:
        # Vérifier règles firewall pour TWS
        result = subprocess.run(['netsh', 'advfirewall', 'firewall', 'show', 'rule', 'name=all'], 
                              capture_output=True, text=True, shell=True)
        
        tws_rules = []
        for line in result.stdout.split('\n'):
            if 'TWS' in line.upper() or 'INTERACTIVE' in line.upper():
                tws_rules.append(line.strip())
        
        if tws_rules:
            print("✅ Règles firewall TWS détectées:")
            for rule in tws_rules[:5]:  # Afficher les 5 premières
                print(f"   {rule}")
        else:
            print("⚠️ Aucune règle firewall TWS détectée")
            
        return True
        
    except Exception as e:
        print(f"❌ Erreur vérification firewall: {e}")
        return False

async def test_connexion_directe():
    """Test connexion directe avec ib_insync"""
    print("\n4. TEST CONNEXION DIRECTE IB_INSYNC")
    print("-" * 30)
    
    try:
        from ib_insync import IB
        
        # Test avec timeout court
        ib = IB()
        
        print("   Tentative connexion 127.0.0.1:7497 (timeout 10s)...")
        
        try:
            await asyncio.wait_for(
                ib.connectAsync('127.0.0.1', 7497, clientId=1),
                timeout=10.0
            )
            
            if ib.isConnected():
                print("✅ Connexion réussie!")
                print(f"   Status: {ib.connectionStatus()}")
                ib.disconnect()
                return True
            else:
                print("❌ Connexion échouée")
                return False
                
        except asyncio.TimeoutError:
            print("❌ Timeout connexion (10s)")
            return False
        except Exception as e:
            print(f"❌ Erreur connexion: {e}")
            return False
            
    except ImportError:
        print("❌ ib_insync non disponible")
        return False
    except Exception as e:
        print(f"❌ Erreur test: {e}")
        return False

def verifier_configuration_tws():
    """Vérifier la configuration TWS"""
    print("\n5. VÉRIFICATION CONFIGURATION TWS")
    print("-" * 30)
    
    print("🔧 VÉRIFICATIONS MANUELLES REQUISES:")
    print("1. TWS est-il complètement démarré? (pas en cours de chargement)")
    print("2. Configuration > API > Settings:")
    print("   - Enable ActiveX and Socket Clients: ✅")
    print("   - Socket port: 7497")
    print("   - Allow connections from localhost: ✅")
    print("   - Read-Only API: ❌ (désactivé)")
    print("3. Configuration > API > Precautions:")
    print("   - Bypass Order Precautions for API Orders: ✅")
    print("4. TWS est-il connecté aux marchés?")
    print("   - Status: Connected")
    print("   - Market data: Active")
    
    return True

def recommander_solutions():
    """Recommander des solutions"""
    print("\n6. RECOMMANDATIONS")
    print("-" * 30)
    
    print("🔧 SOLUTIONS À ESSAYER:")
    print("1. Attendre 2-3 minutes que TWS soit complètement démarré")
    print("2. Vérifier configuration API dans TWS")
    print("3. Redémarrer TWS en mode 'Paper Trading'")
    print("4. Vérifier que TWS est connecté aux marchés")
    print("5. Tester avec un client ID différent")
    print("6. Vérifier les logs TWS pour erreurs")
    
    print("\n📋 COMMANDES DE TEST:")
    print("python test_connexion_ibkr_simple.py")
    print("python diagnostic_connexion_ibkr.py")

async def main():
    """Fonction principale"""
    print("MIA_IA_SYSTEM - DIAGNOSTIC TWS REDÉMARRAGE")
    print("=" * 60)
    print(f"Diagnostic: {datetime.now()}")
    print("=" * 60)
    
    # Vérifications
    tws_ok = verifier_processus_tws()
    port_ok = verifier_port_7497()
    firewall_ok = verifier_firewall()
    connexion_ok = await test_connexion_directe()
    config_ok = verifier_configuration_tws()
    
    # Résultats
    print("\n" + "=" * 60)
    print("RÉSULTATS DIAGNOSTIC")
    print("=" * 60)
    
    print(f"Processus TWS: {'✅' if tws_ok else '❌'}")
    print(f"Port 7497: {'✅' if port_ok else '❌'}")
    print(f"Firewall: {'✅' if firewall_ok else '⚠️'}")
    print(f"Connexion directe: {'✅' if connexion_ok else '❌'}")
    print(f"Configuration: {'✅' if config_ok else '⚠️'}")
    
    if connexion_ok:
        print("\n🎉 SUCCÈS: TWS fonctionnel!")
        print("✅ Système prêt pour test")
    else:
        print("\n❌ PROBLÈME: Connexion IBKR échoue")
        print("🔧 Vérifications requises")
        
    recommander_solutions()
    
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())

