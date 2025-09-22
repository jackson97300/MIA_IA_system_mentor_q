#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de configuration pour le dumper Blind Spots spécialisé
"""

import os
import json
from datetime import datetime

def create_blind_spots_config():
    """Crée un fichier de configuration pour le dumper Blind Spots"""
    config = {
        "dumper_info": {
            "name": "MIA Dumper - Blind Spots Only",
            "version": "1.0",
            "description": "Dumper spécialisé uniquement pour les MenthorQ Blind Spots Levels",
            "created": datetime.now().isoformat()
        },
        "sierra_config": {
            "chart_number": 10,
            "study_id": 3,
            "subgraphs_count": 10,
            "inputs": {
                "blind_spots_study_id": 3,
                "blind_spots_subgraphs_count": 10,
                "on_new_bar_only": 1,
                "emit_last_non_zero": 1,
                "debug_mode": 1,
                "update_interval_minutes": 1
            }
        },
        "expected_output": {
            "file_pattern": "chart_10_blind_spots_YYYYMMDD.jsonl",
            "event_types": [
                "menthorq_level",
                "menthorq_diag", 
                "blind_spots_summary"
            ],
            "level_types": [
                "blind_spot_1",
                "blind_spot_2", 
                "blind_spot_3",
                "blind_spot_4",
                "blind_spot_5",
                "blind_spot_6",
                "blind_spot_7",
                "blind_spot_8",
                "blind_spot_9",
                "blind_spot_10"
            ]
        },
        "setup_instructions": [
            "1. Compiler le fichier MIA_Dumper_Blind_Spots_Only.cpp dans Sierra Chart",
            "2. Ajouter l'étude 'MIA Dumper - Blind Spots Only' au Chart 10",
            "3. Configurer les inputs selon les valeurs ci-dessus",
            "4. Vérifier que l'étude 'MenthorQ Blind Spots Levels' est présente avec Study ID = 3",
            "5. Activer le mode Debug pour voir les détails",
            "6. Vérifier la génération du fichier chart_10_blind_spots_YYYYMMDD.jsonl"
        ]
    }
    
    return config

def create_test_data():
    """Crée des données de test pour valider le dumper"""
    test_data = []
    base_time = 45917.700000
    
    for i in range(10):  # 10 Blind Spots
        timestamp = base_time + (i * 0.001)
        
        # Données de test réalistes
        blind_spot_data = {
            "t": timestamp,
            "sym": "ESZ25_FUT_CME",
            "type": "menthorq_level",
            "level_type": f"blind_spot_{i+1}",
            "price": 6650.0 + (i * 5.0),
            "subgraph": i,
            "study_id": 3,
            "i": 14600 + i,
            "chart": 10
        }
        test_data.append(blind_spot_data)
        
        # Diagnostic de test
        diag_data = {
            "t": timestamp + 0.0005,
            "type": "menthorq_diag",
            "chart": 10,
            "study_id": 3,
            "sg": i,
            "msg": f"emitted_current_{blind_spot_data['price']:.2f}"
        }
        test_data.append(diag_data)
    
    # Résumé de test
    summary_data = {
        "t": base_time + 0.01,
        "type": "blind_spots_summary",
        "chart": 10,
        "study_id": 3,
        "processed_sgs": 10,
        "bar_closed": True
    }
    test_data.append(summary_data)
    
    return test_data

def main():
    """Fonction principale"""
    print("🔧 CONFIGURATION DUMPER BLIND SPOTS SPÉCIALISÉ")
    print("=" * 60)
    
    # Créer la configuration
    config = create_blind_spots_config()
    
    # Sauvegarder la configuration
    config_file = "blind_spots_dumper_config.json"
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Configuration sauvegardée: {config_file}")
    
    # Créer les données de test
    test_data = create_test_data()
    
    # Sauvegarder les données de test
    test_file = "chart_10_blind_spots_test.jsonl"
    with open(test_file, 'w', encoding='utf-8') as f:
        for data in test_data:
            f.write(json.dumps(data) + '\n')
    
    print(f"✅ Données de test créées: {test_file}")
    
    # Afficher les instructions
    print(f"\n📋 INSTRUCTIONS DE CONFIGURATION:")
    for instruction in config["setup_instructions"]:
        print(f"   {instruction}")
    
    print(f"\n⚙️ CONFIGURATION SIERRA:")
    print(f"   Chart: {config['sierra_config']['chart_number']}")
    print(f"   Study ID: {config['sierra_config']['study_id']}")
    print(f"   Subgraphs: {config['sierra_config']['subgraphs_count']}")
    
    print(f"\n📁 FICHIER DE SORTIE ATTENDU:")
    print(f"   {config['expected_output']['file_pattern']}")
    
    print(f"\n🎯 TYPES D'ÉVÉNEMENTS ATTENDUS:")
    for event_type in config['expected_output']['event_types']:
        print(f"   - {event_type}")
    
    print(f"\n🧪 POUR TESTER:")
    print(f"   1. Compilez MIA_Dumper_Blind_Spots_Only.cpp dans Sierra")
    print(f"   2. Ajoutez l'étude au Chart 10")
    print(f"   3. Vérifiez la génération du fichier de sortie")
    print(f"   4. Comparez avec {test_file}")

if __name__ == "__main__":
    main()



