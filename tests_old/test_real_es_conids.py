#!/usr/bin/env python3
"""
Test avec les vrais conids ES futures IBKR
Basé sur la documentation IBKR officielle
"""

import sys
import json
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from core.ibkr_beta_connector import IBKRBetaConnector, IBKRBetaConfig

def test_real_es_conids():
    """Tester les vrais conids ES futures IBKR"""
    
    # Conids ES futures réels (basés sur documentation IBKR)
    # Ces conids changent selon les mois d'expiration
    real_es_conids = [
        # ES futures - Front month et prochains mois
        "265598",  # ES March 2025 (ESH25)
        "265599",  # ES June 2025 (ESM25) 
        "265600",  # ES September 2025 (ESU25)
        "265601",  # ES December 2025 (ESZ25)
        
        # ES futures - Mois précédents (pour test)
        "265595",  # ES December 2024 (ESZ24)
        "265596",  # ES March 2025 (ESH25)
        "265597",  # ES June 2025 (ESM25)
        
        # Conids alternatifs (si les premiers ne marchent pas)
        "265602",  # ES futures alternative
        "265603",  # ES futures alternative
        "265604",  # ES futures alternative
        "265605",  # ES futures alternative
        "265606",  # ES futures alternative
        "265607",  # ES futures alternative
        "265608",  # ES futures alternative
        "265609",  # ES futures alternative
        "265610",  # ES futures alternative
    ]
    
    config = IBKRBetaConfig()
    connector = IBKRBetaConnector(config)
    
    try:
        print("🔍 Test des vrais conids ES futures IBKR...")
        print("=" * 60)
        
        if not connector.connect():
            print("❌ Impossible de se connecter au gateway")
            return None
            
        if not connector.config.authenticated:
            if not connector.authenticate():
                print("❌ Authentification échouée")
                return None
        
        print("✅ Connecté et authentifié")
        print("\n🔍 Test des conids ES futures...")
        
        valid_conids = []
        
        for conid in real_es_conids:
            print(f"\n   Test conid: {conid}")
            
            # Test avec différents champs
            fields = ["31", "84", "86"]  # bid, last, volume
            market_data = connector.get_market_data(conid, fields)
            
            if market_data:
                # Vérifier si c'est un vrai contrat (pas -1)
                if isinstance(market_data, list) and len(market_data) > 0:
                    data = market_data[0]
                    if data.get("conid") != "-1" and data.get("conid") != -1:
                        print(f"   ✅ Conid {conid} VALIDE!")
                        print(f"   📊 Données: {data}")
                        valid_conids.append(conid)
                        
                        # Test données historiques
                        print(f"   📈 Test données historiques...")
                        historical = connector.get_historical_data(conid, "1d", "1min")
                        if historical:
                            print(f"   ✅ Historique: {len(historical)} barres")
                        else:
                            print(f"   ❌ Pas d'historique")
                        
                        return conid  # Premier conid valide trouvé
                    else:
                        print(f"   ❌ Conid {conid} invalide (conid = {data.get('conid')})")
                else:
                    print(f"   ❌ Format données invalide")
            else:
                print(f"   ❌ Pas de données pour conid {conid}")
        
        if not valid_conids:
            print("\n❌ Aucun conid ES futures valide trouvé")
            print("💡 Solutions:")
            print("   1. Vérifiez que vous avez accès aux futures")
            print("   2. Vérifiez que le marché est ouvert")
            print("   3. Essayez de rechercher manuellement dans TWS")
            print("   4. Les conids peuvent avoir changé - vérifiez la documentation")
            return None
        
        return valid_conids[0] if valid_conids else None
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return None
    finally:
        connector.disconnect()

def test_es_data_with_conid(conid):
    """Tester les données ES avec un conid spécifique"""
    print(f"\n🧪 Test complet ES avec conid: {conid}")
    print("=" * 50)
    
    config = IBKRBetaConfig()
    connector = IBKRBetaConnector(config)
    
    try:
        if not connector.connect() or not connector.authenticate():
            return False
        
        # 1. Données temps réel
        print("1️⃣ Données temps réel...")
        fields = ["31", "83", "84", "86", "87", "88", "89", "90"]  # bid, ask, last, volume, high, low, open, close
        market_data = connector.get_market_data(conid, fields)
        
        if market_data and isinstance(market_data, list) and len(market_data) > 0:
            data = market_data[0]
            print("✅ Données temps réel récupérées:")
            print(f"   Bid: {data.get('31', 'N/A')}")
            print(f"   Ask: {data.get('83', 'N/A')}")
            print(f"   Last: {data.get('84', 'N/A')}")
            print(f"   Volume: {data.get('86', 'N/A')}")
            print(f"   High: {data.get('87', 'N/A')}")
            print(f"   Low: {data.get('88', 'N/A')}")
            print(f"   Open: {data.get('89', 'N/A')}")
            print(f"   Close: {data.get('90', 'N/A')}")
        else:
            print("❌ Pas de données temps réel")
            return False
        
        # 2. Données historiques
        print("\n2️⃣ Données historiques...")
        historical = connector.get_historical_data(conid, "1d", "1min")
        if historical:
            print(f"✅ {len(historical)} barres historiques récupérées")
            print("   Dernières 3 barres:")
            for i, bar in enumerate(historical[-3:]):
                print(f"      Barre {i+1}: {bar}")
        else:
            print("❌ Pas de données historiques")
        
        # 3. Données 5 minutes
        print("\n3️⃣ Données 5 minutes...")
        historical_5min = connector.get_historical_data(conid, "5d", "5min")
        if historical_5min:
            print(f"✅ {len(historical_5min)} barres 5min récupérées")
        else:
            print("❌ Pas de données 5 minutes")
        
        print("\n🎉 Test complet réussi!")
        return True
        
    except Exception as e:
        print(f"❌ Erreur test complet: {e}")
        return False
    finally:
        connector.disconnect()

if __name__ == "__main__":
    # Rechercher un conid valide
    es_conid = test_real_es_conids()
    
    if es_conid:
        print(f"\n🎉 Conid ES futures trouvé: {es_conid}")
        
        # Test complet avec ce conid
        if test_es_data_with_conid(es_conid):
            print(f"\n✅ Le conid {es_conid} fonctionne parfaitement!")
            print(f"💡 Utilisez ce conid dans vos scripts: {es_conid}")
        else:
            print(f"\n⚠️ Le conid {es_conid} a des problèmes")
    else:
        print("\n❌ Aucun conid ES futures trouvé")
        print("💡 Vérifiez:")
        print("   1. Accès aux futures dans votre compte")
        print("   2. Heures de marché (ES: 9h30-16h ET)")
        print("   3. Documentation IBKR pour conids actuels")

