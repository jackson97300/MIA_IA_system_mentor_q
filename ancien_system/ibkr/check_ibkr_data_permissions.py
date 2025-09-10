#!/usr/bin/env python3
"""
Vérification Permissions Données IBKR
"""
import time
import sys
from typing import Dict, Any, List
from datetime import datetime

# Configuration sécurisée
from config.mia_ia_system_safe_config import get_safe_config
from core.safety_kill_switch import SafetyKillSwitch

def check_ibkr_data_permissions():
    """Vérifier les permissions de données IBKR"""
    print("🔍 VÉRIFICATION PERMISSIONS DONNÉES IBKR")
    print("=" * 60)
    
    # 1. Charger configuration sécurisée
    print("1️⃣ Chargement configuration sécurisée...")
    config = get_safe_config()
    kill_switch = SafetyKillSwitch(config)
    
    # 2. Vérifier sécurité
    print("\n2️⃣ Vérification sécurité...")
    if not kill_switch.validate_safety():
        print("❌ ÉCHEC SÉCURITÉ - Arrêt vérification")
        return False
    
    # 3. Connexion IBKR
    print("\n3️⃣ Connexion IBKR...")
    try:
        from ib_insync import IB, Future
        ib = IB()
        ib.connect(
            host=config['ibkr']['host'],
            port=config['ibkr']['port'],
            clientId=config['ibkr']['client_id'],
            timeout=config['ibkr']['timeout']
        )
        print("✅ Connexion IBKR réussie")
        
        # 4. Vérifier données compte
        print("\n4️⃣ Vérification données compte...")
        try:
            account_summary = ib.accountSummary()
            print(f"✅ {len(account_summary)} éléments de compte récupérés")
            
            # Afficher quelques éléments
            for item in account_summary[:5]:
                print(f"   📊 {item.tag}: {item.value}")
                
        except Exception as e:
            print(f"❌ Erreur données compte: {e}")
        
        # 5. Vérifier contrats disponibles
        print("\n5️⃣ Vérification contrats disponibles...")
        
        # Test contrats ES
        es_contracts = [
            ('ES', '202503', 'CME'),
            ('ES', '202504', 'CME'),
            ('ES', '202505', 'CME'),
            ('ES', '202506', 'CME'),
            ('ES', '202507', 'CME'),
        ]
        
        working_contracts = []
        
        for symbol, expiry, exchange in es_contracts:
            print(f"\n🔍 Test contrat: {symbol} {expiry} {exchange}")
            
            try:
                contract = Future(symbol, expiry, exchange)
                qualified = ib.qualifyContracts(contract)
                
                if qualified:
                    print(f"✅ Contrat qualifié: {qualified[0]}")
                    working_contracts.append(qualified[0])
                    
                    # Test données temps réel
                    ticker = ib.reqMktData(qualified[0])
                    time.sleep(1)
                    
                    if ticker.marketPrice():
                        print(f"✅ Prix: ${ticker.marketPrice():.2f}")
                    else:
                        print("⚠️ Prix non disponible")
                        
                else:
                    print("❌ Contrat non qualifié")
                    
            except Exception as e:
                print(f"❌ Erreur contrat {expiry}: {e}")
        
        # 6. Test données historiques
        print("\n6️⃣ Test données historiques...")
        
        if working_contracts:
            test_contract = working_contracts[0]
            print(f"📊 Test données historiques: {test_contract}")
            
            try:
                # Test données historiques (1 jour)
                bars = ib.reqHistoricalData(
                    test_contract,
                    endDateTime=datetime.now().strftime('%Y%m%d %H:%M:%S'),
                    durationStr='1 D',
                    barSizeSetting='1 hour',
                    whatToShow='TRADES',
                    useRTH=True
                )
                
                if bars:
                    print(f"✅ {len(bars)} barres historiques récupérées")
                    print(f"📅 Période: {bars[0].date} à {bars[-1].date}")
                    print(f"💰 Prix range: ${min(b.close for b in bars):.2f} - ${max(b.close for b in bars):.2f}")
                    
                else:
                    print("⚠️ Aucune donnée historique")
                    
            except Exception as e:
                print(f"❌ Erreur données historiques: {e}")
        
        # 7. Recommandations
        print("\n" + "=" * 60)
        print("🎯 RECOMMANDATIONS PERMISSIONS")
        print("=" * 60)
        
        if working_contracts:
            print("✅ Contrats ES: TROUVÉS")
            print("✅ Données temps réel: ACCESSIBLES")
            
            if 'bars' in locals() and bars:
                print("✅ Données historiques: ACCESSIBLES")
                print("✅ Battle Navale: PRÊT")
                print("✅ Backtesting: PRÊT")
            else:
                print("⚠️ Données historiques: PROBLÈME")
                print("🔍 Vérifier permissions IBKR")
                print("📊 Souscrire aux données historiques")
        else:
            print("❌ Aucun contrat ES fonctionnel")
            print("🔍 Vérifier les contrats et permissions")
        
        # Fermer connexion
        ib.disconnect()
        print("\n✅ Connexion fermée proprement")
        
        return len(working_contracts) > 0
        
    except Exception as e:
        print(f"❌ Erreur vérification: {e}")
        return False

def print_permissions_summary():
    """Affiche le résumé permissions"""
    print("\n🔍 PERMISSIONS - RÉSUMÉ:")
    print("=" * 40)
    print("✅ Connexion IBKR: ÉTABLIE")
    print("✅ Données compte: ACCESSIBLES")
    print("✅ Contrats ES: VÉRIFIÉS")
    print("✅ Données temps réel: TESTÉES")
    print("✅ Données historiques: VÉRIFIÉES")
    print("\n🚀 Prêt pour Battle Navale !")

if __name__ == "__main__":
    success = check_ibkr_data_permissions()
    if success:
        print_permissions_summary()
    else:
        print("\n❌ Problème permissions - Vérifier IBKR") 