#!/usr/bin/env python3
"""
Test simple pour debug du Dealer's Bias
"""

import logging
import sys
import os

# Configuration du logging pour voir les debug
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Ajouter le répertoire courant au path
sys.path.insert(0, os.getcwd())

try:
    print("🎯 TEST DEBUG DEALER'S BIAS MENTHORQ")
    print("=" * 50)
    
    # 1. Import
    print("1. Import...")
    from features.menthorq_dealers_bias import MenthorQDealersBiasAnalyzer
    from features.menthorq_processor import MenthorQProcessor
    from features.data_reader import get_menthorq_market_data
    print("   ✅ Import OK")
    
    # 2. Récupérer les données MenthorQ
    print("2. Récupération données MenthorQ...")
    menthorq_data = get_menthorq_market_data('ES')
    print(f"   📊 Données MenthorQ: {len(menthorq_data) if menthorq_data else 0} niveaux")
    
    if menthorq_data:
        print("   📊 Clés disponibles:", list(menthorq_data.keys())[:10])
        # Afficher quelques exemples
        for i, (key, value) in enumerate(menthorq_data.items()):
            if i < 5:  # Afficher seulement les 5 premiers
                print(f"      {key}: {value}")
    
    # 3. Initialisation
    print("3. Initialisation...")
    processor = MenthorQProcessor()
    analyzer = MenthorQDealersBiasAnalyzer(processor)
    print("   ✅ Initialisation OK")
    
    # 4. Test de conversion
    print("4. Test conversion...")
    if menthorq_data:
        converted = analyzer._convert_real_menthorq_data(menthorq_data)
        print(f"   📊 Structure convertie: {list(converted.keys())}")
        print(f"   📊 Gamma keys: {list(converted.get('gamma', {}).keys())}")
        print(f"   📊 Blind spots keys: {list(converted.get('blind_spots', {}).keys())}")
        
        # Afficher quelques valeurs gamma
        gamma_data = converted.get('gamma', {})
        for key, value in gamma_data.items():
            if value and value > 0:
                print(f"      Gamma {key}: {value}")
    
    print("✅ Test debug terminé")
    
except Exception as e:
    print(f"❌ Erreur: {e}")
    import traceback
    traceback.print_exc()


