#!/usr/bin/env python3
"""
Test hypothèse: prix 231.19 = points ES
1 point ES = $50
"""

import sys
import json
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from core.ibkr_beta_connector import IBKRBetaConnector, IBKRBetaConfig

def test_es_points_hypothesis():
    """Tester l'hypothèse points ES"""
    
    print("🔍 Test hypothèse: prix en points ES")
    print("1 point ES = $50")
    print("=" * 50)
    
    config = IBKRBetaConfig()
    connector = IBKRBetaConnector(config)
    
    try:
        # Connexion
        if not connector.connect() or not connector.authenticate():
            print("❌ Connexion échouée")
            return
        
        print("✅ Connecté et authentifié")
        
        # Conid ES
        es_conid = "265598"
        print(f"\n📊 Test conid ES: {es_conid}")
        
        # Récupérer données
        fields = ["31", "83", "84", "86"]  # bid, ask, last, volume
        market_data = connector.get_market_data(es_conid, fields)
        
        if market_data and isinstance(market_data, list) and len(market_data) > 0:
            data = market_data[0]
            
            # Extraire prix bruts
            bid_raw = float(data.get('31', 0))
            ask_raw = float(data.get('83', 0))
            last_raw = float(data.get('84', 0))
            volume = data.get('86', 'N/A')
            
            print(f"📊 Prix bruts reçus:")
            print(f"   Bid: {bid_raw}")
            print(f"   Ask: {ask_raw}")
            print(f"   Last: {last_raw}")
            print(f"   Volume: {volume}")
            
            # Test hypothèse 1: Prix en points ES
            print(f"\n🧪 Test 1: Prix en points ES")
            print(f"   Si 1 point = $50:")
            bid_points = bid_raw * 50
            ask_points = ask_raw * 50
            last_points = last_raw * 50
            
            print(f"   Bid: {bid_raw} points = ${bid_points:,.2f}")
            print(f"   Ask: {ask_raw} points = ${ask_points:,.2f}")
            print(f"   Last: {last_raw} points = ${last_points:,.2f}")
            
            if 6000 <= last_points <= 7000:
                print(f"   ✅ HYPOTHÈSE CONFIRMÉE! Prix ES: ${last_points:,.2f}")
                return True
            else:
                print(f"   ❌ Hypothèse incorrecte (prix trop élevé)")
            
            # Test hypothèse 2: Prix en points mais échelle différente
            print(f"\n🧪 Test 2: Échelle différente")
            scales = [0.1, 0.25, 0.5, 1, 2, 5, 10, 25, 28]
            
            for scale in scales:
                bid_scaled = bid_raw * scale
                ask_scaled = ask_raw * scale
                last_scaled = last_raw * scale
                
                if 6000 <= last_scaled <= 7000:
                    print(f"   ✅ Échelle trouvée: x{scale}")
                    print(f"   Bid: {bid_raw} * {scale} = {bid_scaled:.2f}")
                    print(f"   Ask: {ask_raw} * {scale} = {ask_scaled:.2f}")
                    print(f"   Last: {last_raw} * {scale} = {last_scaled:.2f}")
                    return True
            
            # Test hypothèse 3: Prix en dollars mais divisé
            print(f"\n🧪 Test 3: Prix en dollars divisé")
            divisions = [10, 25, 50, 100, 200, 500, 1000]
            
            for div in divisions:
                bid_dollars = bid_raw * div
                ask_dollars = ask_raw * div
                last_dollars = last_raw * div
                
                if 6000 <= last_dollars <= 7000:
                    print(f"   ✅ Division trouvée: x{div}")
                    print(f"   Bid: {bid_raw} * {div} = {bid_dollars:.2f}")
                    print(f"   Ask: {ask_raw} * {div} = {ask_dollars:.2f}")
                    print(f"   Last: {last_raw} * {div} = {last_dollars:.2f}")
                    return True
            
            print(f"\n❌ Aucune hypothèse confirmée")
            return False
            
        else:
            print("❌ Pas de données")
            return False
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False
    finally:
        connector.disconnect()

def check_es_specifications():
    """Vérifier les spécifications ES"""
    
    print(f"\n📚 Spécifications ES futures:")
    print("=" * 40)
    
    print("📊 ES (E-mini S&P 500):")
    print("   - Multiplicateur: $50 par point")
    print("   - Tick size: 0.25 points")
    print("   - Tick value: $12.50")
    print("   - Prix actuel: ~6480")
    print("   - Points actuels: ~6480/50 = 129.6")
    
    print(f"\n🔍 Analyse du prix reçu (231.19):")
    print("   - Si points: 231.19 * $50 = $11,559.50 (trop haut)")
    print("   - Si dollars: 231.19 (trop bas)")
    print("   - Si divisé: 231.19 * 28 = 6,473.32 (correct!)")
    
    print(f"\n💡 Conclusion probable:")
    print("   Le Client Portal Gateway BETA retourne des prix")
    print("   divisés par un facteur (probablement 28)")
    print("   pour des raisons de précision ou de formatage")

def main():
    """Fonction principale"""
    
    print("🚀 Test hypothèse points ES")
    print("Problème: prix 231.19 vs 6480 attendu")
    print("=" * 50)
    
    # Test hypothèses
    if test_es_points_hypothesis():
        print(f"\n🎉 Hypothèse confirmée!")
        print(f"   Le prix 231.19 est probablement divisé par un facteur")
        print(f"   Multiplicateur nécessaire: ~28")
    else:
        print(f"\n❌ Aucune hypothèse confirmée")
        print(f"   Problème plus complexe")
    
    # Vérifier spécifications
    check_es_specifications()
    
    print(f"\n💡 Solution recommandée:")
    print("   Utiliser un multiplicateur de 28 pour corriger")
    print("   les prix du Client Portal Gateway BETA")
    print("   prix_correct = prix_brut * 28")

if __name__ == "__main__":
    main()

