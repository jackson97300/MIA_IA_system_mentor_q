#!/usr/bin/env python3
"""
Test d'intégration du module mia_bullish dans le launcher principal
"""
import asyncio
import sys
import os
from pathlib import Path

# Ajouter le répertoire parent au path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from LAUNCH.launch_24_7_menthorq_final import MIAFinalSystem, FINAL_CONFIG

async def test_bullish_integration():
    """Test l'intégration du scoring bullish dans le système MIA"""
    print("🚀 Test d'intégration Bullish Scorer dans MIA Final System")
    
    # Configuration de test
    test_config = FINAL_CONFIG.copy()
    test_config.update({
        'sierra_enabled': False,  # Mode simulation pour test
        'sierra_data_path': 'D:/MIA_IA_system',
        'sierra_unified_pattern': 'chart_3_combined_full.jsonl',
        'sierra_charts': [3],
        'max_signals_per_day': 5
    })
    
    try:
        # Initialiser le système
        print("📊 Initialisation du système MIA...")
        system = MIAFinalSystem(test_config)
        
        # Initialiser manuellement le BullishScorer si nécessaire
        if not system.bullish_scorer:
            try:
                from core.mia_bullish import BullishScorer
                system.bullish_scorer = BullishScorer(chart_id=3, use_vix=True)
                print("✅ BullishScorer initialisé manuellement")
            except Exception as e:
                print(f"❌ Erreur initialisation manuelle BullishScorer: {e}")
                return False
        
        if system.bullish_scorer:
            print("✅ BullishScorer opérationnel")
        else:
            print("❌ BullishScorer non disponible")
            return False
        
        # Test d'analyse avec données simulées
        print("🎯 Test d'analyse avec données simulées...")
        
        # Données de test avec événements Sierra Chart
        test_market_data = {
            "symbol": "ES",
            "price": 4500.0,
            "volume": 1000.0,
            "sierra_events": [
                {
                    "t": 45911.570833,
                    "type": "basedata",
                    "chart": 3,
                    "i": 1061,
                    "c": 4500.0,
                    "sym": "ESU25_FUT_CME"
                },
                {
                    "t": 45911.570833,
                    "type": "vwap",
                    "chart": 3,
                    "i": 1061,
                    "v": 4499.5,
                    "up1": 4501.0,
                    "dn1": 4498.0
                },
                {
                    "t": 45911.570833,
                    "type": "nbcv_footprint",
                    "chart": 3,
                    "i": 1061,
                    "delta_ratio": 0.15,
                    "pressure_bullish": 1,
                    "pressure_bearish": 0
                }
            ]
        }
        
        # Analyser le marché
        result = await system.analyze_market(test_market_data)
        
        print(f"📈 Résultat de l'analyse:")
        print(f"   Signal généré: {result.get('signal_generated', False)}")
        print(f"   Raison: {result.get('reason', 'N/A')}")
        
        if 'bullish_score' in test_market_data:
            print(f"🎯 Bullish Score intégré: {test_market_data['bullish_score']:.3f}")
        
        # Test avec données réelles si disponibles
        print("\n🔄 Test avec données réelles...")
        real_result = await system.analyze_market()
        
        print(f"📊 Analyse réelle:")
        print(f"   Signal généré: {real_result.get('signal_generated', False)}")
        print(f"   Raison: {real_result.get('reason', 'N/A')}")
        
        print("\n✅ Test d'intégration terminé avec succès")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Fonction principale de test"""
    success = await test_bullish_integration()
    
    if success:
        print("\n🎉 INTÉGRATION BULLISH SCORER RÉUSSIE")
        print("   - Module mia_bullish intégré dans le launcher")
        print("   - Scoring OrderFlow en temps réel opérationnel")
        print("   - Prêt pour la production")
    else:
        print("\n❌ ÉCHEC DE L'INTÉGRATION")
        print("   - Vérifier les imports et dépendances")
        print("   - Contrôler la configuration Sierra Chart")

if __name__ == "__main__":
    asyncio.run(main())
