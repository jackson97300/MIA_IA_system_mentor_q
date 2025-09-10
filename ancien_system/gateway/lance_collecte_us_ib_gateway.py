#!/usr/bin/env python3
"""
LANCE COLLECTE SESSION US - IB GATEWAY
MIA_IA_SYSTEM - Collecte données temps réel session US via IB Gateway
"""
import asyncio
import sys
from datetime import datetime, time
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

from core.ibkr_connector import IBKRConnector
from data.data_collector import DataCollector

def is_us_session_open():
    """Vérifie si la session US est ouverte"""
    now = datetime.now().time()
    
    # Session US: 09:30-16:00 EST (14:30-21:00 CET)
    us_start = time(14, 30)  # 14:30 CET
    us_end = time(21, 0)     # 21:00 CET
    
    return us_start <= now <= us_end

async def lance_collecte_us_ib_gateway():
    """Lance la collecte session US via IB Gateway"""
    
    print("📊 LANCE COLLECTE SESSION US - IB GATEWAY")
    print("=" * 50)
    
    # Vérifier session US
    if not is_us_session_open():
        print("⚠️ Session US fermée")
        print("📅 Session US: 14:30-21:00 CET")
        print("⏰ Heure actuelle:", datetime.now().strftime("%H:%M:%S"))
        return False
    
    print("✅ Session US ouverte - Démarrage collecte...")
    
    # Configuration IB Gateway (Client ID 1)
    config = {
        'ibkr_host': '127.0.0.1',
        'ibkr_port': 4002,  # IB Gateway
        'ibkr_client_id': 1,  # Client ID 1 (résolu)
        'connection_timeout': 30,
        'simulation_mode': False,
        'require_real_data': True,
        'use_ib_insync': True
    }
    
    print(f"📡 Configuration IB Gateway:")
    print(f"   Host: {config['ibkr_host']}")
    print(f"   Port: {config['ibkr_port']}")
    print(f"   Client ID: {config['ibkr_client_id']}")
    
    try:
        # Connexion IB Gateway
        connector = IBKRConnector(config)
        success = await connector.connect()
        
        if success:
            print("✅ CONNEXION IB GATEWAY RÉUSSIE!")
            
            # Créer collecteur de données
            data_collector = DataCollector(connector)
            
            # Instruments à collecter
            instruments = ["ES", "SPY", "VIX"]
            
            print(f"\n📊 Démarrage collecte temps réel...")
            print(f"📈 Instruments: {instruments}")
            print(f"💾 Sauvegarde CSV: Activée")
            print(f"📁 Session: US_SESSION")
            
            # Lancer collecte temps réel
            await data_collector.start_real_time_collection(
                instruments=instruments,
                save_csv=True,
                session_name="US_SESSION",
                include_options_data=True  # Inclure données options SPX
            )
            
            print("\n🎉 COLLECTE SESSION US LANCÉE!")
            print("📋 Données collectées:")
            print("   - Prix ES temps réel")
            print("   - Volume et OrderFlow")
            print("   - Options SPX (Gamma, VIX)")
            print("   - Sauvegarde CSV automatique")
            
            return True
            
        else:
            print("❌ ÉCHEC CONNEXION IB GATEWAY")
            print("🔍 Vérifier:")
            print("   - IB Gateway démarré?")
            print("   - Client ID 1 disponible?")
            print("   - API activée?")
            return False
            
    except Exception as e:
        print(f"❌ ERREUR: {e}")
        return False

if __name__ == "__main__":
    print("📊 LANCE COLLECTE SESSION US - IB GATEWAY")
    print("=" * 50)
    
    success = asyncio.run(lance_collecte_us_ib_gateway())
    
    if success:
        print("\n🎉 SUCCÈS! Collecte US lancée avec IB Gateway")
        print("📊 Données temps réel en cours...")
        print("💾 CSVs sauvegardés automatiquement")
    else:
        print("\n❌ ÉCHEC - Vérifier configuration")























