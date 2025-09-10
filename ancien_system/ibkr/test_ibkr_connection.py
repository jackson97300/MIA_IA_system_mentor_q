#!/usr/bin/env python3
"""
test_ibkr_connection.py

Script simple pour tester la connexion IBKR et diagnostiquer les problèmes
"""

import asyncio
import sys
import os

# Ajouter le répertoire parent au path pour les imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from features.ibkr_connector3 import create_ibkr_connector

async def test_ibkr_connection():
    """Test simple de la connexion IBKR"""
    
    print("🔍 Test de connexion IBKR...")
    print("=" * 50)
    
    # Créer le connecteur
    connector = create_ibkr_connector()
    
    try:
        print("🔗 Tentative de connexion...")
        print("📡 Port attendu: 7496 (TWS) ou 4001 (Gateway)")
        print("🌐 Host: 127.0.0.1")
        
        # Test de connexion avec timeout plus court
        connected = await asyncio.wait_for(connector.connect(), timeout=30.0)
        
        if connected:
            print("✅ Connexion IBKR réussie !")
            
            # Test simple de récupération de données
            print("📊 Test de récupération de données...")
            
            # Test SPX
            try:
                spx_data = await connector.get_market_data("SPX")
                print(f"✅ SPX: {spx_data}")
            except Exception as e:
                print(f"❌ Erreur SPX: {e}")
            
            # Test NDX
            try:
                ndx_data = await connector.get_market_data("NDX")
                print(f"✅ NDX: {ndx_data}")
            except Exception as e:
                print(f"❌ Erreur NDX: {e}")
            
        else:
            print("❌ Échec de la connexion IBKR")
            
    except asyncio.TimeoutError:
        print("⏰ TIMEOUT: La connexion a pris trop de temps")
        print("💡 Vérifiez que TWS/IB Gateway est lancé et connecté")
        print("💡 Vérifiez que l'API est activée dans TWS/Gateway")
        
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")
        print("💡 Vérifiez la configuration IBKR")
        
    finally:
        # Déconnexion
        try:
            await connector.disconnect()
            print("🔌 Déconnexion effectuée")
        except:
            pass
    
    print("=" * 50)
    print("🔍 Diagnostic terminé")

async def test_ibkr_ports():
    """Test des ports IBKR courants"""
    
    print("🔍 Test des ports IBKR courants...")
    print("=" * 50)
    
    ports_to_test = [7496, 4001, 7497, 4002]  # TWS, Gateway, Paper TWS, Paper Gateway
    
    for port in ports_to_test:
        print(f"🔗 Test du port {port}...")
        
        connector = create_ibkr_connector()
        connector.port = port  # Forcer le port
        
        try:
            connected = await asyncio.wait_for(connector.connect(), timeout=10.0)
            if connected:
                print(f"✅ Port {port} - Connexion réussie !")
                await connector.disconnect()
                break
            else:
                print(f"❌ Port {port} - Échec")
        except asyncio.TimeoutError:
            print(f"⏰ Port {port} - Timeout")
        except Exception as e:
            print(f"❌ Port {port} - Erreur: {e}")
    
    print("=" * 50)

async def main():
    """Fonction principale"""
    print("🚀 Diagnostic IBKR - Test de connexion")
    print()
    
    # Test 1: Connexion standard
    await test_ibkr_connection()
    print()
    
    # Test 2: Test des ports
    await test_ibkr_ports()
    print()
    
    print("📋 Résumé des vérifications à faire:")
    print("1. TWS/IB Gateway est-il lancé ?")
    print("2. L'API est-elle activée dans TWS/Gateway ?")
    print("3. Le port est-il correct (7496 pour TWS, 4001 pour Gateway) ?")
    print("4. Y a-t-il des pare-feu qui bloquent la connexion ?")
    print("5. TWS/Gateway est-il en mode 'Accept connections from localhost' ?")

if __name__ == "__main__":
    asyncio.run(main())
