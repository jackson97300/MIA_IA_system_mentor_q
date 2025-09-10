#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎮 TEST TWS PAPER TRADING - MIA_IA_SYSTEM
Mode simulation sans authentification en temps réel
"""

import socket
import time
import subprocess
from datetime import datetime

def check_tws_paper_process():
    """Vérifier si TWS Paper Trading est en cours d'exécution"""
    print("🔍 Vérification TWS Paper Trading...")
    
    try:
        # Vérifier les processus Java (TWS utilise Java)
        result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq javaw.exe'], 
                              capture_output=True, text=True, shell=True)
        
        if 'javaw.exe' in result.stdout:
            print("✅ TWS (javaw.exe) détecté")
            return True
        else:
            print("❌ TWS (javaw.exe) non détecté")
            return False
    except Exception as e:
        print(f"❌ Erreur vérification processus: {e}")
        return False

def test_socket_paper():
    """Test socket port 7497 (Paper Trading)"""
    print("🔍 Test socket port 7497 (Paper Trading)...")
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex(('127.0.0.1', 7497))
        
        if result == 0:
            print("✅ Socket Paper Trading accessible")
            sock.close()
            return True
        else:
            print(f"❌ Socket Paper Trading inaccessible (code: {result})")
            sock.close()
            return False
    except Exception as e:
        print(f"❌ Erreur socket Paper: {e}")
        return False

def test_ib_insync_paper():
    """Test ib_insync avec Paper Trading"""
    print("🔗 Test ib_insync Paper Trading...")
    
    try:
        from ib_insync import IB, Future
        
        ib = IB()
        
        # Configuration Paper Trading
        host = '127.0.0.1'
        port = 7497  # Port Paper Trading
        client_id = 999
        timeout = 30
        
        print(f"   🔗 Connexion Paper: {host}:{port}, Client ID: {client_id}")
        
        try:
            ib.connect(host, port, clientId=client_id, timeout=timeout)
            
            if ib.isConnected():
                print("   ✅ Connexion Paper Trading réussie !")
                
                # Test rapide ES
                try:
                    contract = Future('ES', '20241220', 'CME')
                    ib.reqMktData(contract)
                    time.sleep(3)
                    
                    tickers = ib.tickers()
                    if tickers:
                        for ticker in tickers:
                            if ticker.contract.symbol == 'ES':
                                prix = ticker.marketPrice()
                                if prix and prix > 0:
                                    print(f"   💰 Prix ES Paper: {prix}")
                                    print("   🎉 SUCCÈS Paper Trading !")
                                    ib.disconnect()
                                    return True, {
                                        'host': host,
                                        'port': port,
                                        'client_id': client_id,
                                        'timeout': timeout,
                                        'mode': 'PAPER'
                                    }
                    
                    print("   ⚠️ Connexion Paper OK mais pas de données ES")
                    ib.disconnect()
                    return True, {
                        'host': host,
                        'port': port,
                        'client_id': client_id,
                        'timeout': timeout,
                        'mode': 'PAPER'
                    }
                    
                except Exception as e:
                    print(f"   ⚠️ Erreur test ES Paper: {e}")
                    ib.disconnect()
                    return True, {
                        'host': host,
                        'port': port,
                        'client_id': client_id,
                        'timeout': timeout,
                        'mode': 'PAPER'
                    }
            else:
                print("   ❌ Connexion Paper échouée")
                ib.disconnect()
                return False, None
                
        except Exception as e:
            print(f"   ❌ Erreur connexion Paper: {e}")
            return False, None
            
    except ImportError:
        print("   ❌ ib_insync non disponible")
        return False, None
    except Exception as e:
        print(f"   ❌ Erreur générale Paper: {e}")
        return False, None

def create_paper_config():
    """Créer configuration TWS Paper Trading"""
    print("📝 Création configuration TWS Paper Trading...")
    
    config_content = """
# Configuration TWS Paper Trading pour MIA_IA_SYSTEM
# À copier dans TWS: File -> Global Configuration -> API -> Settings

# === MODE PAPER TRADING ===
✅ Paper Trading: ACTIVÉ
✅ Socket port: 7497 (Paper Trading)
✅ Enable ActiveX and Socket Clients: OUI
✅ Allow connections from localhost: OUI

# === PARAMÈTRES SÉCURITÉ ===
✅ Bypass Order Precautions for API Orders: OUI
✅ Create API order log file: OUI
✅ Log API messages: OUI

# === PARAMÈTRES DONNÉES ===
✅ Market data type: Live (même en Paper)
✅ Include expired contracts: OUI
✅ Include real-time bars: OUI

# === AVANTAGES PAPER TRADING ===
✅ Pas d'authentification 2FA requise
✅ Données marché réelles
✅ Pas de risque financier
✅ Parfait pour tests et développement
"""
    
    with open('tws_paper_config.txt', 'w', encoding='utf-8') as f:
        f.write(config_content)
    
    print("✅ Configuration Paper Trading sauvegardée")
    return True

def main():
    print("🎮 TEST TWS PAPER TRADING - MIA_IA_SYSTEM")
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("🎯 Mode simulation sans authentification 2FA")
    print("=" * 60)
    
    # Étape 1: Vérifier TWS
    if not check_tws_paper_process():
        print("\n❌ TWS n'est pas en cours d'exécution !")
        print("🔧 SOLUTIONS:")
        print("1. Lancez TWS manuellement")
        print("2. Assurez-vous qu'il est en mode PAPER TRADING")
        print("3. Port 7497 doit être configuré")
        return
    
    # Étape 2: Test socket Paper
    if not test_socket_paper():
        print("\n❌ Port 7497 (Paper Trading) inaccessible !")
        print("🔧 SOLUTIONS:")
        print("1. Vérifiez que TWS est en mode Paper Trading")
        print("2. Configurez le port 7497 dans TWS")
        print("3. Redémarrez TWS")
        return
    
    # Étape 3: Créer configuration
    create_paper_config()
    
    # Étape 4: Test connexion Paper
    print("\n🔗 Test connexion Paper Trading...")
    success, config = test_ib_insync_paper()
    
    # Résumé
    print("\n" + "=" * 60)
    print("📊 RÉSUMÉ PAPER TRADING")
    
    if success and config:
        print("🎉 SUCCÈS ! Configuration Paper Trading trouvée:")
        print(f"   - Host: {config['host']}")
        print(f"   - Port: {config['port']} (Paper Trading)")
        print(f"   - Client ID: {config['client_id']}")
        print(f"   - Mode: {config['mode']}")
        
        print("\n🚀 MIA_IA_SYSTEM PRÊT POUR DÉVELOPPEMENT !")
        
        # Sauvegarder configuration
        with open('config_tws_paper.py', 'w', encoding='utf-8') as f:
            f.write(f"""# Configuration TWS Paper Trading - MIA_IA_SYSTEM
TWS_PAPER_CONFIG = {{
    'host': '{config['host']}',
    'port': {config['port']},
    'client_id': {config['client_id']},
    'timeout': {config['timeout']},
    'mode': '{config['mode']}',
    'status': 'WORKING'
}}

# Avantages Paper Trading:
# ✅ Pas d'authentification 2FA
# ✅ Données marché réelles
# ✅ Pas de risque financier
# ✅ Parfait pour tests
""")
        print("✅ Configuration Paper sauvegardée dans 'config_tws_paper.py'")
        
    else:
        print("❌ Échec de la connexion Paper Trading")
        print("\n🔧 SOLUTIONS:")
        print("1. Lancez TWS en mode Paper Trading")
        print("2. Configurez le port 7497 dans TWS")
        print("3. Appliquez la configuration dans 'tws_paper_config.txt'")
        print("4. Redémarrez TWS complètement")

if __name__ == "__main__":
    main()

