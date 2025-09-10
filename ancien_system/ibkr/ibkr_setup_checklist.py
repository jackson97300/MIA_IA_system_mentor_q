#!/usr/bin/env python3
"""
Checklist de configuration IBKR TWS/Gateway
"""

import subprocess
import socket
import time
from datetime import datetime

def check_tws_gateway_status():
    """Vérifier le statut TWS/Gateway"""
    print("🔍 VÉRIFICATION TWS/IB GATEWAY")
    print("=" * 50)
    
    # Ports à vérifier
    ports = {
        'TWS Paper': 7497,
        'TWS Live': 7496,
        'Gateway Paper': 4002,
        'Gateway Live': 4001
    }
    
    print("📋 PORTS À VÉRIFIER:")
    print("-" * 30)
    
    for name, port in ports.items():
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex(('127.0.0.1', port))
            sock.close()
            
            if result == 0:
                print(f"✅ {name} (Port {port}): ACTIF")
            else:
                print(f"❌ {name} (Port {port}): INACTIF")
                
        except Exception as e:
            print(f"❌ {name} (Port {port}): ERREUR - {e}")
    
    return ports

def generate_setup_instructions():
    """Générer les instructions de setup"""
    print("\n📋 INSTRUCTIONS DE SETUP TWS/GATEWAY")
    print("=" * 50)
    
    instructions = [
        "1. FERMER TOUT:",
        "   - Fermez TWS et IB Gateway",
        "   - Fermez tous les processus Python",
        "",
        "2. RELANCER EN PAPER:",
        "   - Lancez TWS ou IB Gateway",
        "   - Sélectionnez 'Paper Trading'",
        "",
        "3. CONFIGURATION API:",
        "   - Menu: API → Paramètres",
        "   - ☑️ Enable ActiveX and Socket Clients",
        "   - ☑️ Download open orders",
        "   - ☑️ Send status updates for API orders",
        "   - 🔒 Trusted IPs: ajoutez 127.0.0.1",
        "   - ❌ Read-Only API: DÉSACTIVÉ",
        "",
        "4. PORTS:",
        "   - TWS Paper: 7497",
        "   - Gateway Paper: 4002",
        "",
        "5. PARE-FEU WINDOWS:",
        "   - Autorisez le port 7497 (ou 4002)",
        "",
        "6. TEST CONNEXION:",
        "   - PowerShell: Test-NetConnection 127.0.0.1 -Port 7497"
    ]
    
    for instruction in instructions:
        print(instruction)
    
    return instructions

def check_abonnements_data():
    """Vérifier les abonnements data nécessaires"""
    print("\n📊 ABONNEMENTS DATA NÉCESSAIRES")
    print("=" * 50)
    
    abonnements = [
        {
            'nom': 'CME L1',
            'description': 'Futures ES - Quotes L1',
            'requis': 'OUI',
            'erreur_sans': 'No market data permissions'
        },
        {
            'nom': 'CME Depth',
            'description': 'Futures ES - DOM L2',
            'requis': 'OUI',
            'erreur_sans': 'DOM L2 vide'
        },
        {
            'nom': 'OPRA',
            'description': 'Options SPX - Quotes + Greeks',
            'requis': 'OUI',
            'erreur_sans': 'SPX options non disponibles'
        },
        {
            'nom': 'CFE',
            'description': 'VIX futures',
            'requis': 'OUI',
            'erreur_sans': 'VIX futures non disponibles'
        }
    ]
    
    print("📋 ABONNEMENTS REQUIS:")
    print("-" * 30)
    
    for abo in abonnements:
        print(f"✅ {abo['nom']}")
        print(f"   Description: {abo['description']}")
        print(f"   Requis: {abo['requis']}")
        print(f"   Erreur sans: {abo['erreur_sans']}")
        print()
    
    return abonnements

def generate_test_script():
    """Générer le script de test minimal"""
    print("\n🐍 SCRIPT DE TEST MINIMAL")
    print("=" * 50)
    
    script_content = '''#!/usr/bin/env python3
"""
Script de test minimal IBKR
"""

from ib_insync import *

def test_ibkr_connection():
    """Test de connexion IBKR"""
    print("🚀 TEST CONNEXION IBKR")
    print("=" * 30)
    
    # 1. Connexion Paper
    ib = IB()
    try:
        ib.connect('127.0.0.1', 7497, clientId=7)
        print("✅ Connexion réussie")
        print(f"TWS time: {ib.reqCurrentTime()}")
        
        # 2. Test ES Futures
        print("\\n📊 TEST ES FUTURES:")
        es = ContFuture('ES', exchange='GLOBEX')
        ib.qualifyContracts(es)
        
        # Quotes L1
        tkr_es = ib.reqMktData(es, '', False, False)
        ib.sleep(2)
        print(f"ES L1: Bid={tkr_es.bid}, Ask={tkr_es.ask}, Last={tkr_es.last}")
        
        # DOM L2
        try:
            dom = ib.reqMktDepth(es, numRows=10)
            ib.sleep(2)
            print(f"ES DOM Bids: {[(l.price, l.size) for l in dom[0].domBids[:3]]}")
            print(f"ES DOM Asks: {[(l.price, l.size) for l in dom[0].domAsks[:3]]}")
        except Exception as e:
            print(f"❌ DOM L2: {e}")
        
        # 3. Test SPX Options
        print("\\n📈 TEST SPX OPTIONS:")
        opt = Option(symbol='SPX', lastTradeDateOrContractMonth='20250920',
                    strike=5000, right='C', exchange='SMART', currency='USD')
        ib.qualifyContracts(opt)
        
        tkr_opt = ib.reqMktData(opt, genericTickList='106', snapshot=False)
        ib.sleep(3)
        print(f"SPX Greeks: {tkr_opt.modelGreeks}")
        
        # 4. Test VIX
        print("\\n📊 TEST VIX:")
        vix_idx = Index('VIX', 'CBOE')
        ib.qualifyContracts(vix_idx)
        tkr_vix = ib.reqMktData(vix_idx, '', False)
        ib.sleep(2)
        print(f"VIX spot: {tkr_vix.last}")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        print("\\n🔧 SOLUTIONS:")
        print("1. Vérifiez que TWS/Gateway est lancé")
        print("2. Vérifiez le port (7497 pour Paper)")
        print("3. Vérifiez les abonnements data")
        print("4. Changez clientId si nécessaire")
    
    finally:
        ib.disconnect()
        print("\\n✅ Test terminé")

if __name__ == "__main__":
    test_ibkr_connection()
'''
    
    print("📝 Script de test à sauvegarder dans 'test_ibkr_minimal.py':")
    print("-" * 50)
    print(script_content)
    
    return script_content

def main():
    """Fonction principale"""
    print("🚀 CHECKLIST CONFIGURATION IBKR")
    print("=" * 60)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Vérifier statut
    ports = check_tws_gateway_status()
    
    # Instructions de setup
    generate_setup_instructions()
    
    # Abonnements data
    check_abonnements_data()
    
    # Script de test
    generate_test_script()
    
    print("\n✅ Checklist terminée!")
    print("\\n🎯 PROCHAINES ÉTAPES:")
    print("1. Suivez les instructions de setup")
    print("2. Lancez le script de test")
    print("3. Envoyez-moi les erreurs exactes")

if __name__ == "__main__":
    main()







