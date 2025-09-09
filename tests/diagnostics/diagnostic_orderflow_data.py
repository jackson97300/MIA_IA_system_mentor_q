#!/usr/bin/env python3
"""
MIA_IA_SYSTEM - Diagnostic OrderFlow Data
Analyse la qualité et variabilité des données OrderFlow
"""

import os
import sys
import json
import asyncio
from datetime import datetime, timedelta

# Ajouter le répertoire racine au path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def diagnostic_orderflow():
    """Diagnostique la qualité des données OrderFlow"""
    
    print("MIA_IA_SYSTEM - DIAGNOSTIC ORDERFLOW DATA")
    print("=" * 60)
    
    try:
        # Importer les modules nécessaires
        from core.ibkr_connector import IBKRConnector
        from core.logger import get_logger
        
        logger = get_logger(__name__)
        
        # Initialiser la connexion IBKR
        print("🔗 Initialisation connexion IBKR...")
        ibkr_connector = IBKRConnector()
        
        # Configuration TWS
        ibkr_connector.host = "127.0.0.1"
        ibkr_connector.port = 7497
        ibkr_connector.client_id = 1
        
        # Connecter à IBKR
        await ibkr_connector.connect()
        
        if not ibkr_connector.is_connected():
            print("❌ Impossible de se connecter à IBKR")
            return
        
        print("✅ Connexion IBKR établie")
        
        # Collecter des données OrderFlow pendant 2 minutes
        print("\n📊 Collecte données OrderFlow (2 minutes)...")
        print("=" * 50)
        
        data_samples = []
        start_time = datetime.now()
        end_time = start_time + timedelta(minutes=2)
        
        while datetime.now() < end_time:
            try:
                # Récupérer données OrderFlow ES
                market_data = await ibkr_connector.get_orderflow_market_data("ES")
                
                if market_data:
                    sample = {
                        "timestamp": datetime.now(),
                        "volume": market_data.get("volume", 0),
                        "delta": market_data.get("delta", 0),
                        "bid_volume": market_data.get("bid_volume", 0),
                        "ask_volume": market_data.get("ask_volume", 0),
                        "price": market_data.get("price", 0),
                        "mode": market_data.get("mode", "unknown")
                    }
                    data_samples.append(sample)
                    
                    # Afficher en temps réel
                    print(f"⏰ {sample['timestamp'].strftime('%H:%M:%S')} | "
                          f"📊 Vol: {sample['volume']} | "
                          f"📈 Delta: {sample['delta']} | "
                          f"💰 Bid: {sample['bid_volume']} | "
                          f"💰 Ask: {sample['ask_volume']} | "
                          f"💵 Prix: {sample['price']:.2f}")
                
                await asyncio.sleep(5)  # Échantillon toutes les 5 secondes
                
            except Exception as e:
                print(f"⚠️ Erreur collecte: {e}")
                await asyncio.sleep(5)
        
        # Analyser les données collectées
        print("\n🔍 ANALYSE DES DONNÉES COLLECTÉES")
        print("=" * 50)
        
        if not data_samples:
            print("❌ Aucune donnée collectée")
            return
        
        # Statistiques de base
        volumes = [s["volume"] for s in data_samples]
        deltas = [s["delta"] for s in data_samples]
        bid_volumes = [s["bid_volume"] for s in data_samples]
        ask_volumes = [s["ask_volume"] for s in data_samples]
        prices = [s["price"] for s in data_samples]
        
        print(f"📊 Échantillons collectés: {len(data_samples)}")
        print(f"⏱️ Durée: {(datetime.now() - start_time).total_seconds():.1f} secondes")
        
        # Analyse Volume
        print(f"\n📊 ANALYSE VOLUME:")
        print(f"   Min: {min(volumes)}")
        print(f"   Max: {max(volumes)}")
        print(f"   Moyenne: {sum(volumes)/len(volumes):.1f}")
        print(f"   Variabilité: {max(volumes) - min(volumes)}")
        
        # Analyse Delta
        print(f"\n📈 ANALYSE DELTA:")
        print(f"   Min: {min(deltas)}")
        print(f"   Max: {max(deltas)}")
        print(f"   Moyenne: {sum(deltas)/len(deltas):.1f}")
        print(f"   Variabilité: {max(deltas) - min(deltas)}")
        
        # Analyse Bid/Ask
        print(f"\n💰 ANALYSE BID/ASK:")
        print(f"   Bid Min: {min(bid_volumes)}")
        print(f"   Bid Max: {max(bid_volumes)}")
        print(f"   Ask Min: {min(ask_volumes)}")
        print(f"   Ask Max: {max(ask_volumes)}")
        
        # Analyse Prix
        print(f"\n💵 ANALYSE PRIX:")
        print(f"   Min: {min(prices):.2f}")
        print(f"   Max: {max(prices):.2f}")
        print(f"   Moyenne: {sum(prices)/len(prices):.2f}")
        print(f"   Variabilité: {max(prices) - min(prices):.2f}")
        
        # Diagnostic de qualité
        print(f"\n🎯 DIAGNOSTIC QUALITÉ:")
        
        # Vérifier variabilité volume
        volume_variability = max(volumes) - min(volumes)
        if volume_variability < 10:
            print("   ⚠️ Volume: FAIBLE VARIABILITÉ (données statiques)")
        elif volume_variability < 50:
            print("   ⚠️ Volume: VARIABILITÉ MODÉRÉE")
        else:
            print("   ✅ Volume: BONNE VARIABILITÉ")
        
        # Vérifier variabilité delta
        delta_variability = max(deltas) - min(deltas)
        if delta_variability < 5:
            print("   ⚠️ Delta: FAIBLE VARIABILITÉ")
        elif delta_variability < 20:
            print("   ⚠️ Delta: VARIABILITÉ MODÉRÉE")
        else:
            print("   ✅ Delta: BONNE VARIABILITÉ")
        
        # Vérifier variabilité prix
        price_variability = max(prices) - min(prices)
        if price_variability < 0.5:
            print("   ⚠️ Prix: FAIBLE VARIABILITÉ")
        elif price_variability < 2.0:
            print("   ⚠️ Prix: VARIABILITÉ MODÉRÉE")
        else:
            print("   ✅ Prix: BONNE VARIABILITÉ")
        
        # Recommandations
        print(f"\n💡 RECOMMANDATIONS:")
        
        if volume_variability < 10:
            print("   🔧 Problème: Volume statique détecté")
            print("   💡 Solution: Vérifier source de données OrderFlow")
            print("   💡 Solution: Activer données Level 2 complètes")
        
        if delta_variability < 5:
            print("   🔧 Problème: Delta statique détecté")
            print("   💡 Solution: Vérifier calculs OrderFlow")
            print("   💡 Solution: Améliorer agrégation des trades")
        
        if price_variability < 0.5:
            print("   🔧 Problème: Prix statique détecté")
            print("   💡 Solution: Vérifier mise à jour prix en temps réel")
        
        # Sauvegarder le rapport
        report = {
            "timestamp": datetime.now().isoformat(),
            "samples_count": len(data_samples),
            "duration_seconds": (datetime.now() - start_time).total_seconds(),
            "volume_stats": {
                "min": min(volumes),
                "max": max(volumes),
                "average": sum(volumes)/len(volumes),
                "variability": volume_variability
            },
            "delta_stats": {
                "min": min(deltas),
                "max": max(deltas),
                "average": sum(deltas)/len(deltas),
                "variability": delta_variability
            },
            "price_stats": {
                "min": min(prices),
                "max": max(prices),
                "average": sum(prices)/len(prices),
                "variability": price_variability
            },
            "quality_issues": []
        }
        
        if volume_variability < 10:
            report["quality_issues"].append("low_volume_variability")
        if delta_variability < 5:
            report["quality_issues"].append("low_delta_variability")
        if price_variability < 0.5:
            report["quality_issues"].append("low_price_variability")
        
        # Sauvegarder le rapport
        os.makedirs("data/diagnostics", exist_ok=True)
        with open(f"data/diagnostics/orderflow_diagnostic_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json", "w") as f:
            json.dump(report, f, indent=2)
        
        print(f"\n💾 Rapport sauvegardé: data/diagnostics/")
        print("✅ Diagnostic terminé")
        
        # Fermer la connexion
        await ibkr_connector.disconnect()
        
    except ImportError as e:
        print(f"❌ Erreur import: {e}")
    except Exception as e:
        print(f"❌ Erreur diagnostic: {e}")

if __name__ == "__main__":
    asyncio.run(diagnostic_orderflow())






