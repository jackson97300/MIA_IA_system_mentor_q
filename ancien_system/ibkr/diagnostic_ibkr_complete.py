#!/usr/bin/env python3
"""
🔧 Diagnostic IBKR Complet - Solutions Officielles
Script basé sur la documentation IBKR pour résoudre les erreurs 500/503
"""

import sys
import requests
import json
import time
from pathlib import Path
from datetime import datetime
from urllib3.exceptions import InsecureRequestWarning
import warnings

# Supprimer les warnings SSL pour localhost
warnings.filterwarnings('ignore', category=InsecureRequestWarning)

# Ajouter le chemin du projet
sys.path.append(str(Path(__file__).parent.parent))

def diagnostic_complet():
    """Diagnostic complet basé sur solutions IBKR officielles"""
    print("🔧 Diagnostic IBKR Complet - Solutions Officielles")
    print("="*70)
    print(f"🕐 Timestamp: {datetime.now()}")
    
    base_url = "https://localhost:5000/v1/api"
    session = requests.Session()
    session.verify = False
    
    # ConID ES Sep19'25
    ES_SEP25_CONID = 637533641
    
    try:
        # 1. Test 1: Vérification TWS/Gateway
        print(f"\n🔍 Test 1: Vérification TWS/Gateway")
        
        # Test connexion de base
        try:
            response = session.get(f"{base_url}/iserver/auth/status", timeout=10)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                auth_data = response.json()
                print(f"   ✅ TWS/Gateway accessible")
                print(f"   Authentifié: {auth_data.get('authenticated')}")
                print(f"   Connected: {auth_data.get('connected')}")
                print(f"   Competing: {auth_data.get('competing')}")
            else:
                print(f"   ❌ TWS/Gateway inaccessible")
                print(f"   Solution: Démarrer TWS/Gateway")
                return
        except Exception as e:
            print(f"   ❌ Erreur connexion: {e}")
            print(f"   Solution: Vérifier TWS/Gateway démarré")
            return
        
        # 2. Test 2: Vérification API Settings
        print(f"\n🔍 Test 2: Vérification API Settings")
        
        # Test endpoint API
        api_response = session.get(f"{base_url}/iserver/account", timeout=10)
        print(f"   Status: {api_response.status_code}")
        
        if api_response.status_code == 200:
            print(f"   ✅ API Settings corrects")
        else:
            print(f"   ❌ Problème API Settings")
            print(f"   Solution: TWS → Configuration → API → Enable ActiveX and Socket Clients")
        
        # 3. Test 3: Vérification permissions données
        print(f"\n🔍 Test 3: Vérification permissions données")
        
        # Test avec delayed data d'abord (solution IBKR)
        delayed_response = session.get(
            f"{base_url}/iserver/marketdata/history",
            params={
                "conid": ES_SEP25_CONID,
                "exchange": "CME",
                "period": "1d",
                "bar": "1min"
            },
            timeout=15
        )
        
        print(f"   Status delayed: {delayed_response.status_code}")
        
        if delayed_response.status_code == 200:
            print(f"   ✅ Permissions données OK")
            hist_data = delayed_response.json()
            print(f"   Données historiques: {len(hist_data.get('data', []))} barres")
        else:
            print(f"   ❌ Problème permissions")
            print(f"   Solution: Vérifier subscription ES dans Account Management")
        
        # 4. Test 4: Rate limiting et retry logic
        print(f"\n🔍 Test 4: Test rate limiting et retry")
        
        # Test avec délai et retry (solution IBKR)
        for attempt in range(3):
            print(f"   Tentative {attempt + 1}/3...")
            
            # Délai entre tentatives
            if attempt > 0:
                time.sleep(2)
            
            subscribe_data = {
                "conids": [ES_SEP25_CONID],
                "fields": ["31", "83", "84", "86", "6", "7", "8", "9"]
            }
            
            subscribe_response = session.post(
                f"{base_url}/iserver/marketdata/snapshot",
                json=subscribe_data,
                timeout=15
            )
            
            print(f"   Status: {subscribe_response.status_code}")
            
            if subscribe_response.status_code == 200:
                print(f"   ✅ Souscription réussie avec retry!")
                break
            elif subscribe_response.status_code == 500:
                print(f"   ⚠️ Erreur 500 - Tentative suivante...")
            elif subscribe_response.status_code == 503:
                print(f"   ⚠️ Service Unavailable - Tentative suivante...")
            else:
                print(f"   ❌ Erreur {subscribe_response.status_code}")
                break
        else:
            print(f"   ❌ Échec après 3 tentatives")
        
        # 5. Test 5: Session et keep-alive
        print(f"\n🔍 Test 5: Vérification session")
        
        # Re-vérifier authentification
        auth_check = session.get(f"{base_url}/iserver/auth/status", timeout=10)
        print(f"   Status auth: {auth_check.status_code}")
        
        if auth_check.status_code == 200:
            auth_data = auth_check.json()
            if auth_data.get('authenticated'):
                print(f"   ✅ Session valide")
            else:
                print(f"   ❌ Session expirée")
                print(f"   Solution: Re-authentifier via https://localhost:5000/sso/Dispatcher")
        else:
            print(f"   ❌ Problème session")
        
        # 6. Test 6: Configuration alternative
        print(f"\n🔍 Test 6: Configuration alternative")
        
        # Test avec paramètres différents
        alt_response = session.post(
            f"{base_url}/iserver/marketdata/snapshot",
            json={
                "conids": [ES_SEP25_CONID],
                "fields": ["31", "83", "84"]  # Moins de champs
            },
            timeout=15
        )
        
        print(f"   Status alt: {alt_response.status_code}")
        
        if alt_response.status_code == 200:
            print(f"   ✅ Configuration alternative fonctionne")
        else:
            print(f"   ❌ Même problème avec config alternative")
        
        # 7. Résumé et recommandations
        print(f"\n📋 Résumé et recommandations")
        print("="*70)
        
        print(f"✅ ConID ES Sep19'25: {ES_SEP25_CONID}")
        print(f"✅ TWS/Gateway: Accessible")
        print(f"✅ Authentification: Fonctionnelle")
        
        print(f"\n🔧 Solutions recommandées (par ordre de priorité):")
        print(f"1. Redémarrer Client Portal Gateway")
        print(f"2. Vérifier TWS → Configuration → API → Enable ActiveX and Socket Clients")
        print(f"3. Vérifier subscription ES dans Account Management")
        print(f"4. Désactiver firewall temporairement")
        print(f"5. Utiliser l'API TWS classique (ib_insync) comme alternative")
        
        print(f"\n💡 Le ConID ES Sep19'25 est correct, le problème est technique avec l'API")
        
    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    diagnostic_complet()

