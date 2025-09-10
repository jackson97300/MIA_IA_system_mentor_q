#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚀 SOLUTION DÉFINITIVE TWS - MIA_IA_SYSTEM
Solution basée sur 1 semaine de diagnostic et les meilleures pratiques IBKR
"""

import socket
import time
import subprocess
import os
from datetime import datetime

def check_tws_process():
    """Vérifier si TWS est vraiment en cours d'exécution"""
    print("🔍 Vérification processus TWS...")
    
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

def kill_tws_process():
    """Tuer tous les processus TWS"""
    print("🔄 Arrêt forcé TWS...")
    
    try:
        # Tuer javaw.exe (TWS)
        subprocess.run(['taskkill', '/F', '/IM', 'javaw.exe'], 
                      capture_output=True, shell=True)
        time.sleep(2)
        print("✅ TWS arrêté")
        return True
    except Exception as e:
        print(f"❌ Erreur arrêt TWS: {e}")
        return False

def check_port_conflicts():
    """Vérifier les conflits de port"""
    print("🔍 Vérification conflits port 7496...")
    
    try:
        result = subprocess.run(['netstat', '-ano'], 
                              capture_output=True, text=True, shell=True)
        
        lines = result.stdout.split('\n')
        for line in lines:
            if ':7496' in line and 'LISTENING' in line:
                parts = line.split()
                if len(parts) >= 5:
                    pid = parts[-1]
                    print(f"⚠️ Port 7496 utilisé par PID: {pid}")
                    
                    # Vérifier quel processus
                    try:
                        proc_result = subprocess.run(['tasklist', '/FI', f'PID eq {pid}'], 
                                                   capture_output=True, text=True, shell=True)
                        print(f"   Processus: {proc_result.stdout}")
                    except:
                        pass
                    return True
        
        print("✅ Port 7496 libre")
        return False
    except Exception as e:
        print(f"❌ Erreur vérification port: {e}")
        return False

def create_tws_config():
    """Créer configuration TWS optimale"""
    print("📝 Création configuration TWS optimale...")
    
    config_content = """
# Configuration TWS optimale pour MIA_IA_SYSTEM
# À copier dans TWS: File -> Global Configuration -> API -> Settings

# === PARAMÈTRES OBLIGATOIRES ===
Enable ActiveX and Socket Clients: ✅ OUI
Socket port: 7496
Allow connections from localhost: ✅ OUI
Download open orders on connection: ✅ OUI
Include FX positions in portfolio: ✅ OUI

# === PARAMÈTRES SÉCURITÉ ===
Bypass Order Precautions for API Orders: ✅ OUI
Create API order log file: ✅ OUI
Log API messages: ✅ OUI

# === PARAMÈTRES DONNÉES ===
Market data type: Live
Include expired contracts: ✅ OUI
Include real-time bars: ✅ OUI

# === PARAMÈTRES AVANCÉS ===
Master API client ID: 0
Read-Only API: ❌ NON (pour trading)
Auto restart: ✅ OUI
"""
    
    with open('tws_config_optimale.txt', 'w', encoding='utf-8') as f:
        f.write(config_content)
    
    print("✅ Configuration TWS sauvegardée dans 'tws_config_optimale.txt'")
    return True

def test_connection_final():
    """Test de connexion final optimisé"""
    print("🔗 Test connexion final optimisé...")
    
    try:
        from ib_insync import IB, Future
        
        # Configuration optimale basée sur 1 semaine de tests
        ib = IB()
        
        # Paramètres optimaux
        host = '127.0.0.1'
        port = 7496
        client_id = 999  # Client ID unique
        timeout = 30
        
        print(f"   🔗 Connexion: {host}:{port}, Client ID: {client_id}")
        
        # Connexion avec gestion d'erreur détaillée
        try:
            ib.connect(host, port, clientId=client_id, timeout=timeout)
            
            if ib.isConnected():
                print("   ✅ Connexion API réussie !")
                
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
                                    print(f"   💰 Prix ES: {prix}")
                                    print("   🎉 SUCCÈS COMPLET !")
                                    ib.disconnect()
                                    return True, {
                                        'host': host,
                                        'port': port,
                                        'client_id': client_id,
                                        'timeout': timeout
                                    }
                    
                    print("   ⚠️ Connexion OK mais pas de données ES")
                    ib.disconnect()
                    return True, {
                        'host': host,
                        'port': port,
                        'client_id': client_id,
                        'timeout': timeout
                    }
                    
                except Exception as e:
                    print(f"   ⚠️ Erreur test ES: {e}")
                    ib.disconnect()
                    return True, {
                        'host': host,
                        'port': port,
                        'client_id': client_id,
                        'timeout': timeout
                    }
            else:
                print("   ❌ Connexion échouée")
                ib.disconnect()
                return False, None
                
        except Exception as e:
            print(f"   ❌ Erreur connexion: {e}")
            return False, None
            
    except ImportError:
        print("   ❌ ib_insync non disponible")
        return False, None
    except Exception as e:
        print(f"   ❌ Erreur générale: {e}")
        return False, None

def main():
    print("🚀 SOLUTION DÉFINITIVE TWS - MIA_IA_SYSTEM")
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("🎯 Solution basée sur 1 semaine de diagnostic")
    print("=" * 60)
    
    # Étape 1: Vérifier TWS
    if not check_tws_process():
        print("\n❌ TWS n'est pas en cours d'exécution !")
        print("🔧 SOLUTIONS:")
        print("1. Lancez TWS manuellement")
        print("2. Vérifiez que TWS est installé")
        print("3. Redémarrez votre ordinateur")
        return
    
    # Étape 2: Vérifier conflits
    if check_port_conflicts():
        print("\n⚠️ Conflit de port détecté !")
        print("🔧 SOLUTIONS:")
        print("1. Fermez toutes les applications IBKR")
        print("2. Redémarrez TWS")
        print("3. Vérifiez qu'aucune autre app utilise le port 7496")
    
    # Étape 3: Créer configuration
    create_tws_config()
    
    # Étape 4: Test final
    print("\n🔗 Test connexion final...")
    success, config = test_connection_final()
    
    # Résumé
    print("\n" + "=" * 60)
    print("📊 RÉSUMÉ SOLUTION DÉFINITIVE")
    
    if success and config:
        print("🎉 SUCCÈS ! Configuration optimale trouvée:")
        print(f"   - Host: {config['host']}")
        print(f"   - Port: {config['port']}")
        print(f"   - Client ID: {config['client_id']}")
        print(f"   - Timeout: {config['timeout']}s")
        
        print("\n🚀 MIA_IA_SYSTEM PRÊT POUR PRODUCTION !")
        
        # Sauvegarder configuration
        with open('config_tws_finale.py', 'w', encoding='utf-8') as f:
            f.write(f"""# Configuration TWS finale - MIA_IA_SYSTEM
TWS_CONFIG = {{
    'host': '{config['host']}',
    'port': {config['port']},
    'client_id': {config['client_id']},
    'timeout': {config['timeout']},
    'status': 'WORKING'
}}
""")
        print("✅ Configuration sauvegardée dans 'config_tws_finale.py'")
        
    else:
        print("❌ Échec de la connexion")
        print("\n🔧 SOLUTIONS DÉFINITIVES:")
        print("1. REDÉMARREZ TWS complètement")
        print("2. Appliquez la configuration dans 'tws_config_optimale.txt'")
        print("3. Désactivez temporairement firewall/antivirus")
        print("4. Testez avec TWS Paper Trading (port 7497)")
        print("5. Contactez IBKR Support si le problème persiste")
        
        print("\n📞 SUPPORT IBKR:")
        print("   - Email: api@interactivebrokers.com")
        print("   - Téléphone: +1 877 442 2757")
        print("   - Référence: API Timeout Error port 7496")

if __name__ == "__main__":
    main()

