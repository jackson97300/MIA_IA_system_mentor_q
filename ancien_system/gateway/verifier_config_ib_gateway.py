#!/usr/bin/env python3
"""
MIA_IA_SYSTEM - Vérification Configuration IB Gateway
Diagnostic et correction des problèmes de connexion API
"""

import os
import json
from datetime import datetime

def check_ib_gateway_config():
    """Vérification configuration IB Gateway"""
    print("🔧 Vérification Configuration IB Gateway...")
    print()
    
    # Configuration requise pour API
    required_config = {
        "API Settings": {
            "Enable ActiveX and Socket Clients": "✅ REQUIS",
            "Socket port": "4002 (Paper Trading)",
            "Master API client ID": "0 (ou laissé vide)",
            "Read-Only API": "❌ DÉSACTIVÉ (pour trading)",
            "Download open orders on connection": "✅ ACTIVÉ",
            "Include FX positions in portfolio": "✅ ACTIVÉ",
            "Create API message log file": "✅ ACTIVÉ (pour debug)"
        },
        "Paper Trading": {
            "Paper Trading Account": "✅ ACTIVÉ",
            "Account": "DUM365838 (visible dans logs)",
            "Paper Trading Port": "4002"
        },
        "Connection": {
            "Auto restart": "✅ ACTIVÉ",
            "Auto restart delay": "30 secondes",
            "Connection timeout": "60 secondes"
        }
    }
    
    print("📋 CONFIGURATION REQUISE IB GATEWAY:")
    print("=" * 60)
    
    for section, settings in required_config.items():
        print(f"\n🔹 {section}:")
        for setting, value in settings.items():
            print(f"   {setting}: {value}")
    
    print()
    print("🔍 DIAGNOSTIC PROBLÈMES COMMUNS:")
    print("=" * 60)
    
    problems = [
        "❌ API non activée dans TWS/Gateway",
        "❌ Port incorrect (doit être 4002 pour Paper)",
        "❌ Client ID en conflit",
        "❌ Firewall bloque connexion",
        "❌ IB Gateway pas complètement démarré",
        "❌ Permissions API insuffisantes"
    ]
    
    for problem in problems:
        print(f"   {problem}")
    
    print()
    print("💡 SOLUTIONS RECOMMANDÉES:")
    print("=" * 60)
    
    solutions = [
        "1. 🔄 Redémarrer IB Gateway complètement",
        "2. ⚙️ Vérifier API Settings dans IB Gateway",
        "3. 🔥 Désactiver temporairement Firewall",
        "4. 🆔 Essayer Client ID différent (999, 1000, 2)",
        "5. 📝 Vérifier logs IB Gateway pour erreurs",
        "6. 🔗 Tester connexion manuelle avec TWS"
    ]
    
    for solution in solutions:
        print(f"   {solution}")

def create_ib_gateway_test():
    """Créer test IB Gateway optimisé"""
    print("\n🔧 Création test IB Gateway optimisé...")
    
    test_code = '''#!/usr/bin/env python3
"""
Test IB Gateway optimisé pour Paper Trading
"""

import socket
import time
from datetime import datetime

def test_ib_gateway_connection():
    """Test connexion IB Gateway avec paramètres optimisés"""
    print("🔧 Test IB Gateway optimisé...")
    
    try:
        from ib_insync import IB
        
        # Test avec différents paramètres
        test_configs = [
            {"port": 4002, "client_id": 999, "timeout": 60},
            {"port": 4002, "client_id": 1000, "timeout": 60},
            {"port": 4002, "client_id": 2, "timeout": 60},
            {"port": 4002, "client_id": 1, "timeout": 120}
        ]
        
        for config in test_configs:
            print(f"\\n   Test: Port {config['port']}, Client ID {config['client_id']}, Timeout {config['timeout']}s")
            
            ib = IB()
            
            try:
                # Connexion avec paramètres optimisés
                ib.connect(
                    '127.0.0.1', 
                    config['port'], 
                    clientId=config['client_id'], 
                    timeout=config['timeout']
                )
                
                if ib.isConnected():
                    print(f"✅ Connexion réussie !")
                    
                    # Test rapide
                    try:
                        account = ib.accountSummary()
                        print(f"✅ Compte: {len(account)} éléments")
                        
                        # Afficher solde
                        for item in account:
                            if item.tag == 'NetLiquidation':
                                print(f"   - NetLiquidation: {item.value} {item.currency}")
                                break
                                
                    except Exception as e:
                        print(f"⚠️ Erreur compte: {e}")
                    
                    ib.disconnect()
                    return config
                else:
                    print("❌ Connexion échouée")
                    ib.disconnect()
                    
            except Exception as e:
                print(f"❌ Erreur: {e}")
                try:
                    ib.disconnect()
                except:
                    pass
                continue
        
        print("\\n❌ Aucune configuration ne fonctionne")
        return None
        
    except ImportError:
        print("❌ ib_insync non installé")
        return None

if __name__ == "__main__":
    print("🚀 Test IB Gateway Optimisé")
    print("=" * 50)
    result = test_ib_gateway_connection()
    
    if result:
        print(f"\\n🎉 Configuration fonctionnelle trouvée !")
        print(f"   Port: {result['port']}")
        print(f"   Client ID: {result['client_id']}")
        print(f"   Timeout: {result['timeout']}s")
    else:
        print("\\n❌ Aucune configuration fonctionnelle")
'''
    
    with open('test_ib_gateway_optimise.py', 'w', encoding='utf-8') as f:
        f.write(test_code)
    
    print("✅ Test créé: test_ib_gateway_optimise.py")

def main():
    """Diagnostic principal"""
    print("🚀 MIA_IA_SYSTEM - Diagnostic IB Gateway")
    print("=" * 60)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Vérification configuration
    check_ib_gateway_config()
    
    # Création test optimisé
    create_ib_gateway_test()
    
    print()
    print("=" * 60)
    print("📋 PLAN D'ACTION:")
    print("1. 🔧 Vérifier configuration IB Gateway")
    print("2. 🔄 Redémarrer IB Gateway")
    print("3. 🧪 Lancer: python test_ib_gateway_optimise.py")
    print("4. 📊 Analyser résultats")
    print("5. 🚀 Intégrer configuration dans MIA_IA_SYSTEM")

if __name__ == "__main__":
    main()
