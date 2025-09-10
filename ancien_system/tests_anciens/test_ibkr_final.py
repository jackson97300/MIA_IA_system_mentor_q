#!/usr/bin/env python3
"""
MIA_IA_SYSTEM - Test IBKR Final
Test basé sur les logs IB Gateway fonctionnels
"""

import socket
import time
from datetime import datetime

def test_ibkr_connection():
    """Test connexion IBKR avec configuration optimisée"""
    print("🔧 Test connexion IBKR optimisé...")
    
    try:
        from ib_insync import IB, Contract
        
        # Configuration basée sur les logs IB Gateway
        ib = IB()
        
        # Test avec Client ID 1 (standard)
        print("   Test Client ID 1...")
        
        try:
            # Connexion avec timeout plus long
            ib.connect('127.0.0.1', 4002, clientId=1, timeout=30)
            
            if ib.isConnected():
                print("✅ Connexion IB Gateway réussie !")
                
                # Test récupération données compte
                try:
                    account = ib.accountSummary()
                    print(f"✅ Données compte récupérées: {len(account)} éléments")
                    
                    # Afficher infos importantes
                    for item in account:
                        if item.tag in ['NetLiquidation', 'EquityWithLoanValue', 'AvailableFunds', 'CashBalance']:
                            print(f"   - {item.tag}: {item.value} {item.currency}")
                            
                except Exception as e:
                    print(f"⚠️ Erreur récupération compte: {e}")
                
                # Test récupération contrat ES (basé sur les logs)
                try:
                    contract = Contract(
                        symbol='ES',
                        secType='FUT',
                        exchange='CME',
                        currency='USD',
                        lastTradingDay='20251219'
                    )
                    
                    # Récupération détails contrat
                    contracts = ib.reqContractDetails(contract)
                    print(f"✅ Contrats ES trouvés: {len(contracts)}")
                    
                    if contracts:
                        contract_details = contracts[0]
                        print(f"   - Contrat: {contract_details.contract.symbol}")
                        print(f"   - Exchange: {contract_details.contract.exchange}")
                        print(f"   - Trading Day: {contract_details.contract.lastTradingDay}")
                        
                        # Test market data
                        print("   - Test market data...")
                        ib.reqMktData(contract_details.contract)
                        time.sleep(2)  # Attendre données
                        
                        # Récupérer prix
                        ticker = ib.ticker(contract_details.contract)
                        if ticker and ticker.marketPrice():
                            print(f"   - Prix actuel: {ticker.marketPrice()}")
                        else:
                            print("   - Prix non disponible")
                            
                        ib.cancelMktData(contract_details.contract)
                        
                except Exception as e:
                    print(f"⚠️ Erreur récupération contrats: {e}")
                
                # Test ordres (simulation)
                try:
                    print("   - Test simulation ordres...")
                    # Vérifier permissions trading
                    account_info = ib.accountSummary()
                    can_trade = any(item.tag == 'AvailableFunds' and float(item.value) > 0 for item in account_info)
                    print(f"   - Trading autorisé: {'✅' if can_trade else '❌'}")
                    
                except Exception as e:
                    print(f"⚠️ Erreur test trading: {e}")
                
                ib.disconnect()
                return True
            else:
                print("❌ Connexion échouée")
                ib.disconnect()
                return False
                
        except Exception as e:
            print(f"❌ Erreur connexion: {e}")
            try:
                ib.disconnect()
            except:
                pass
            return False
        
    except ImportError:
        print("❌ ib_insync non installé")
        return False
    except Exception as e:
        print(f"❌ Erreur générale: {e}")
        return False

def test_ports():
    """Test des ports IBKR"""
    print("🔍 Test des ports IBKR...")
    
    ports_to_test = [
        (4001, "IB Gateway Live"),
        (4002, "IB Gateway Paper"), 
        (7496, "TWS Live"),
        (7497, "TWS Paper")
    ]
    
    available_ports = []
    
    for port, description in ports_to_test:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(3)
            result = sock.connect_ex(('127.0.0.1', port))
            sock.close()
            
            if result == 0:
                print(f"✅ Port {port} accessible ({description})")
                available_ports.append((port, description))
            else:
                print(f"❌ Port {port} non accessible ({description})")
                
        except Exception as e:
            print(f"❌ Erreur test port {port}: {e}")
    
    return available_ports

def main():
    """Test principal IBKR"""
    print("🚀 MIA_IA_SYSTEM - Test IBKR Final")
    print("=" * 60)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Test 1: Ports disponibles
    available_ports = test_ports()
    print()
    
    if not available_ports:
        print("❌ Aucun port IBKR accessible")
        print("💡 Vérifiez que IB Gateway ou TWS est lancé")
        return
    
    # Test 2: Connexion IBKR
    connection_success = test_ibkr_connection()
    
    print()
    print("=" * 60)
    print("📊 RÉSUMÉ TEST IBKR FINAL")
    print(f"Ports disponibles: {len(available_ports)}")
    
    if connection_success:
        print("✅ Connexion IBKR réussie !")
        print("🎉 IBKR opérationnel pour MIA_IA_SYSTEM !")
        print()
        print("📋 PROCHAINES ÉTAPES :")
        print("1. ✅ IBKR connecté")
        print("2. 🔄 Tester MIA_IA_SYSTEM avec IBKR")
        print("3. 🚀 Lancer automation paper trading")
    else:
        print("❌ Connexion échouée")
        print("💡 Vérifiez la configuration IB Gateway")
        print("💡 Vérifiez les permissions API")

if __name__ == "__main__":
    main()
















