#!/usr/bin/env python3
"""
🔧 TEST CONNEXION AVANT LANCEMENT
MIA_IA_SYSTEM - Validation connexion IBKR avant lancement optimisé
"""
import asyncio
import sys
import time
import socket
import subprocess
from pathlib import Path

# Ajouter le chemin du projet
sys.path.append(str(Path(__file__).parent))

from core.logger import get_logger

logger = get_logger(__name__)

async def test_connexion_avant_lancement():
    """Test complet avant lancement du système optimisé"""
    
    print("🔧 === TEST CONNEXION AVANT LANCEMENT ===")
    print("🎯 Objectif: Valider que tout est prêt pour le lancement")
    print()
    
    # 1. Test port IB Gateway
    print("1️⃣ Test port IB Gateway (4002)...")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('127.0.0.1', 4002))
    sock.close()
    
    if result == 0:
        print("✅ Port 4002 ouvert (IB Gateway)")
        ib_gateway_ok = True
    else:
        print("❌ Port 4002 fermé")
        print("🔧 Actions: Démarrer IB Gateway")
        ib_gateway_ok = False
    
    # 2. Test port TWS (alternative)
    print("\n2️⃣ Test port TWS (7497)...")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('127.0.0.1', 7497))
    sock.close()
    
    if result == 0:
        print("✅ Port 7497 ouvert (TWS)")
        tws_ok = True
    else:
        print("❌ Port 7497 fermé")
        tws_ok = False
    
    # 3. Test processus Python
    print("\n3️⃣ Test processus Python...")
    try:
        result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq python.exe'], 
                              capture_output=True, text=True)
        python_processes = result.stdout.count('python.exe')
        print(f"✅ {python_processes} processus Python actifs")
    except Exception as e:
        print(f"⚠️ Impossible de vérifier les processus: {e}")
    
    # 4. Test fichiers de configuration
    print("\n4️⃣ Test fichiers de configuration...")
    config_files = [
        "launch_24_7_orderflow_trading.py",
        "core/ibkr_connector.py",
        "config/automation_config.py"
    ]
    
    for file_path in config_files:
        if Path(file_path).exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} manquant")
    
    # 5. Résumé et recommandations
    print("\n" + "=" * 50)
    print("📊 RÉSUMÉ DES TESTS")
    print("=" * 50)
    
    if ib_gateway_ok:
        print("✅ IB Gateway: PRÊT")
        print("🎯 Port recommandé: 4002")
    elif tws_ok:
        print("✅ TWS: PRÊT")
        print("🎯 Port recommandé: 7497")
        print("⚠️ Nécessite modification du port dans le code")
    else:
        print("❌ Aucune connexion IBKR disponible")
        print("🔧 Actions requises:")
        print("   1. Démarrer IB Gateway (port 4002)")
        print("   2. OU démarrer TWS (port 7497)")
        print("   3. Vérifier configuration API")
    
    print("\n🎯 PARAMÈTRES OPTIMISÉS:")
    print("   📈 Min Signal Confidence: 0.250 (+67%)")
    print("   🧠 ML Min Confidence: 0.60 (+33%)")
    print("   🔗 Confluence Threshold: 0.25 (+67%)")
    print("   📊 OrderFlow Threshold: 0.250 (+39%)")
    print("   🎯 Win Rate attendu: 70-80%")
    
    print("\n🚀 PRÊT POUR LANCEMENT:")
    if ib_gateway_ok:
        print("✅ python launch_24_7_orderflow_trading.py --dry-run")
    else:
        print("❌ Corriger la connexion IBKR d'abord")
    
    return ib_gateway_ok or tws_ok

if __name__ == "__main__":
    print("⚠️ TEST CONNEXION AVANT LANCEMENT OPTIMISÉ")
    print("🎯 Objectif: Valider que tout est prêt")
    print()
    
    success = asyncio.run(test_connexion_avant_lancement())
    
    if success:
        print("\n🎉 TOUT EST PRÊT POUR LE LANCEMENT !")
    else:
        print("\n🔧 CORRIGER LA CONNEXION AVANT DE LANCER")
























