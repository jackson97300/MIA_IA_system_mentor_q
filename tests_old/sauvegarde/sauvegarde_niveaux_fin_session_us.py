#!/usr/bin/env python3
"""
SAUVEGARDE NIVEAUX OPTIONS - FIN SESSION US
MIA_IA_SYSTEM - Sauvegarde niveaux calculés pendant session US
"""
import os
import shutil
import json
import pandas as pd
from datetime import datetime, time
from pathlib import Path
import asyncio
import sys

sys.path.append(str(Path(__file__).parent))

from features.spx_options_retriever import create_spx_options_retriever
from core.ibkr_connector import IBKRConnector

def is_us_session_closing():
    """Vérifie si la session US va bientôt fermer"""
    now = datetime.now().time()
    
    # Session US ferme à 16:00 EST (22:00 CET)
    us_close = time(22, 0)  # 22:00 CET
    warning_time = time(21, 30)  # 21:30 CET (30min avant fermeture)
    
    return warning_time <= now <= us_close

async def sauvegarde_niveaux_fin_session_us():
    """Sauvegarde les niveaux options calculés pendant la session US"""
    
    print("📊 SAUVEGARDE NIVEAUX OPTIONS - FIN SESSION US")
    print("=" * 60)
    
    # Vérifier si on approche de la fermeture US
    if not is_us_session_closing():
        print("⚠️ Session US encore ouverte")
        print("📅 Sauvegarde recommandée: 21:30-22:00 CET")
        print("⏰ Heure actuelle:", datetime.now().strftime("%H:%M:%S"))
        return False
    
    print("✅ Session US se termine - Sauvegarde niveaux...")
    
    # Configuration IB Gateway
    config = {
        'ibkr_host': '127.0.0.1',
        'ibkr_port': 4002,
        'ibkr_client_id': 1,
        'connection_timeout': 30,
        'simulation_mode': False,
        'require_real_data': True,
        'use_ib_insync': True
    }
    
    try:
        # Connexion IB Gateway
        connector = IBKRConnector(config)
        success = await connector.connect()
        
        if success:
            print("✅ CONNEXION IB GATEWAY RÉUSSIE!")
            
            # Créer SPX Options Retriever
            spx_retriever = create_spx_options_retriever(connector)
            
            # Récupérer derniers niveaux calculés
            print("📊 Récupération derniers niveaux calculés...")
            spx_data = await spx_retriever.get_real_spx_data()
            
            if spx_data:
                print("✅ NIVEAUX OPTIONS RÉCUPÉRÉS!")
                
                # Afficher niveaux finaux
                afficher_niveaux_finaux(spx_data)
                
                # Sauvegarder pour Asia/London
                await sauvegarder_pour_asia_london(spx_data)
                
                # Sauvegarder automatiquement
                await spx_retriever._save_spx_data_automatically(spx_data)
                print("💾 Niveaux sauvegardés automatiquement")
                
            else:
                print("⚠️ Pas de niveaux récupérés")
            
            # Déconnexion
            await connector.disconnect()
            
        else:
            print("❌ ÉCHEC CONNEXION IB GATEWAY")
            
    except Exception as e:
        print(f"❌ ERREUR: {e}")

def afficher_niveaux_finaux(spx_data):
    """Affiche les niveaux options finaux de la session US"""
    print("\n🎯 NIVEAUX OPTIONS FINAUX - SESSION US:")
    print("-" * 40)
    print(f"📈 VIX Level: {spx_data.get('vix_level', 'N/A')}")
    print(f"⚖️ Put/Call Ratio: {spx_data.get('put_call_ratio', 'N/A')}")
    print(f"🏗️ Gamma Exposure: ${spx_data.get('total_gamma_exposure', 0)/1e9:.1f}B")
    print(f"🔄 Gamma Flip Level: {spx_data.get('gamma_flip_level', 'N/A')}")
    print(f"🎯 Call Wall: {spx_data.get('call_wall', 'N/A')}")
    print(f"🎯 Put Wall: {spx_data.get('put_wall', 'N/A')}")
    print(f"📊 Dealer Position: {spx_data.get('dealer_position', 'N/A')}")
    print(f"🎯 Pin Levels: {spx_data.get('pin_levels', 'N/A')}")
    
    # Calculer biais gamma
    calculer_biais_gamma_final(spx_data)

def calculer_biais_gamma_final(spx_data):
    """Calcule le biais gamma final pour Asia/London"""
    gamma_flip = spx_data.get('gamma_flip_level')
    current_price = spx_data.get('current_price', 4500)
    
    if gamma_flip and current_price:
        if current_price > gamma_flip:
            bias = "BULLISH"
            direction = "📈"
        else:
            bias = "BEARISH"
            direction = "📉"
        
        print(f"🎯 Biais Gamma Final: {bias} {direction}")
        print(f"   Distance Flip: {abs(current_price - gamma_flip):.1f} points")
        print(f"   📋 Utilisable pour Asia/London demain")

async def sauvegarder_pour_asia_london(spx_data):
    """Sauvegarde les niveaux pour les sessions Asia/London"""
    timestamp = datetime.now()
    backup_dir = f"data/backups/options_fin_us_{timestamp.strftime('%Y%m%d_%H%M%S')}/"
    
    os.makedirs(backup_dir, exist_ok=True)
    
    # Sauvegarder données SPX
    spx_file = os.path.join(backup_dir, "spx_fin_session_us.json")
    
    # Ajouter métadonnées
    spx_data['backup_timestamp'] = timestamp.isoformat()
    spx_data['session'] = 'FIN_US_SESSION'
    spx_data['source'] = 'IB_GATEWAY'
    spx_data['usage'] = 'ASIA_LONDON_TOMORROW'
    
    with open(spx_file, 'w', encoding='utf-8') as f:
        json.dump(spx_data, f, indent=2, ensure_ascii=False)
    
    # Créer métadonnées
    metadata_file = os.path.join(backup_dir, "metadata_fin_us.txt")
    with open(metadata_file, 'w', encoding='utf-8') as f:
        f.write("SAUVEGARDE NIVEAUX OPTIONS - FIN SESSION US\n")
        f.write("=" * 50 + "\n")
        f.write(f"Date: {timestamp.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Session: Fin US\n")
        f.write(f"Usage: Asia/London demain\n\n")
        f.write("NIVEAUX CALCULÉS PENDANT SESSION US:\n")
        f.write("-" * 40 + "\n")
        f.write("🏗️ Gamma Exposure (Calculé en temps réel)\n")
        f.write("🎯 Call/Put Walls (Niveaux détectés)\n")
        f.write("🔄 Gamma Flip (Point pivot identifié)\n")
        f.write("📈 VIX (Niveau final session)\n")
        f.write("⚖️ Put/Call Ratio (Sentiment final)\n")
        f.write("🎯 Pin Risk (Zones identifiées)\n")
        f.write("🏦 Dealer Position (Position finale)\n\n")
        f.write("UTILISATION ASIA/LONDON:\n")
        f.write("-" * 25 + "\n")
        f.write("1. Niveaux de référence pour demain\n")
        f.write("2. Biais gamma établi\n")
        f.write("3. Zones de trading identifiées\n")
        f.write("4. Risk management basé sur dealer position\n")
    
    print(f"💾 Sauvegarde fin US: {backup_dir}")
    print(f"📋 Métadonnées: {metadata_file}")
    
    return backup_dir

if __name__ == "__main__":
    print("📊 SAUVEGARDE NIVEAUX - FIN SESSION US")
    print("=" * 50)
    
    success = asyncio.run(sauvegarde_niveaux_fin_session_us())
    
    if success:
        print("\n🎉 SUCCÈS! Niveaux sauvegardés pour Asia/London")
        print("📋 Utilisable demain pour sessions Asia/London")
    else:
        print("\n⚠️ Vérifier timing ou connexion")























