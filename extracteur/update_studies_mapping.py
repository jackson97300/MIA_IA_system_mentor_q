#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script pour mettre à jour studies_mapping.json à partir des fichiers d'inventaire
"""

import json
import os
from collections import defaultdict

def load_inventory_file(filepath):
    """Charge un fichier d'inventaire JSONL"""
    studies = []
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    studies.append(json.loads(line.strip()))
    return studies

def analyze_studies_by_chart():
    """Analyse tous les fichiers d'inventaire et organise par chart"""
    charts_data = {}
    
    # Fichiers d'inventaire disponibles
    inventory_files = [
        'study_inventory_chart_3_20250911.jsonl',
        'study_inventory_chart_4_20250911.jsonl', 
        'study_inventory_chart_10_20250911.jsonl'
    ]
    
    for filename in inventory_files:
        chart_num = int(filename.split('_')[3])  # Extrait le numéro du chart
        studies = load_inventory_file(filename)
        charts_data[chart_num] = studies
        print(f"✅ Chart {chart_num}: {len(studies)} études chargées")
    
    return charts_data

def create_updated_mapping(charts_data):
    """Crée le mapping mis à jour basé sur les données d'inventaire"""
    
    mapping = {
        "charts": {},
        "studies_by_name": {},
        "studies_by_id": {}
    }
    
    # Analyse par chart
    for chart_num, studies in charts_data.items():
        chart_key = f"chart_{chart_num}"
        mapping["charts"][chart_key] = {
            "chart_number": chart_num,
            "studies": {}
        }
        
        for study in studies:
            study_id = study["study_id"]
            study_name = study["name"]
            short_name = study.get("short", "")
            
            # Mapping par chart
            mapping["charts"][chart_key]["studies"][study_id] = {
                "name": study_name,
                "short_name": short_name,
                "subgraphs": {}
            }
            
            # Ajouter les subgraphs
            for sg in study["subgraphs"]:
                sg_index = sg["i"]
                sg_name = sg["name"]
                if sg_name:  # Seulement les subgraphs avec un nom
                    mapping["charts"][chart_key]["studies"][study_id]["subgraphs"][sg_index] = sg_name
            
            # Mapping global par nom
            if study_name not in mapping["studies_by_name"]:
                mapping["studies_by_name"][study_name] = []
            mapping["studies_by_name"][study_name].append({
                "chart": chart_num,
                "study_id": study_id,
                "short_name": short_name
            })
            
            # Mapping global par ID
            mapping["studies_by_id"][study_id] = {
                "name": study_name,
                "short_name": short_name,
                "chart": chart_num
            }
    
    return mapping

def identify_key_studies(mapping):
    """Identifie les études clés pour MIA"""
    
    key_studies = {
        "VWAP": {
            "charts": [],
            "study_ids": []
        },
        "VVA": {
            "charts": [],
            "study_ids": []
        },
        "VIX": {
            "charts": [],
            "study_ids": []
        },
        "NBCV": {
            "charts": [],
            "study_ids": []
        },
        "MenthorQ": {
            "charts": [],
            "study_ids": []
        },
        "Correlation": {
            "charts": [],
            "study_ids": []
        },
        "Cumulative_Delta": {
            "charts": [],
            "study_ids": []
        }
    }
    
    # Recherche des études clés
    for study_name, instances in mapping["studies_by_name"].items():
        name_lower = study_name.lower()
        
        if "vwap" in name_lower:
            for instance in instances:
                key_studies["VWAP"]["charts"].append(instance["chart"])
                key_studies["VWAP"]["study_ids"].append(instance["study_id"])
        
        elif "volume value area" in name_lower:
            for instance in instances:
                key_studies["VVA"]["charts"].append(instance["chart"])
                key_studies["VVA"]["study_ids"].append(instance["study_id"])
        
        elif "vix" in name_lower:
            for instance in instances:
                key_studies["VIX"]["charts"].append(instance["chart"])
                key_studies["VIX"]["study_ids"].append(instance["study_id"])
        
        elif "numbers bars calculated" in name_lower:
            for instance in instances:
                key_studies["NBCV"]["charts"].append(instance["chart"])
                key_studies["NBCV"]["study_ids"].append(instance["study_id"])
        
        elif "menthorq" in name_lower:
            for instance in instances:
                key_studies["MenthorQ"]["charts"].append(instance["chart"])
                key_studies["MenthorQ"]["study_ids"].append(instance["study_id"])
        
        elif "correlation" in name_lower:
            for instance in instances:
                key_studies["Correlation"]["charts"].append(instance["chart"])
                key_studies["Correlation"]["study_ids"].append(instance["study_id"])
        
        elif "cumulative delta" in name_lower:
            for instance in instances:
                key_studies["Cumulative_Delta"]["charts"].append(instance["chart"])
                key_studies["Cumulative_Delta"]["study_ids"].append(instance["study_id"])
    
    return key_studies

def main():
    print("🔍 Analyse des fichiers d'inventaire des études...")
    
    # Charger les données d'inventaire
    charts_data = analyze_studies_by_chart()
    
    # Créer le mapping mis à jour
    mapping = create_updated_mapping(charts_data)
    
    # Identifier les études clés
    key_studies = identify_key_studies(mapping)
    mapping["key_studies"] = key_studies
    
    # Sauvegarder le mapping mis à jour
    with open('studies_mapping_updated.json', 'w', encoding='utf-8') as f:
        json.dump(mapping, f, indent=2, ensure_ascii=False)
    
    print("\n📊 RÉSUMÉ DE L'ANALYSE:")
    print("=" * 50)
    
    for chart_key, chart_data in mapping["charts"].items():
        chart_num = chart_data["chart_number"]
        study_count = len(chart_data["studies"])
        print(f"📈 Chart {chart_num}: {study_count} études")
        
        # Afficher les études importantes
        important_studies = []
        for study_id, study_info in chart_data["studies"].items():
            name = study_info["name"].lower()
            if any(keyword in name for keyword in ["vwap", "vva", "vix", "nbcv", "menthorq", "correlation", "delta"]):
                important_studies.append(f"ID {study_id}: {study_info['name']}")
        
        if important_studies:
            for study in important_studies[:5]:  # Limiter à 5 pour la lisibilité
                print(f"   • {study}")
            if len(important_studies) > 5:
                print(f"   • ... et {len(important_studies) - 5} autres")
    
    print("\n🎯 ÉTUDES CLÉS IDENTIFIÉES:")
    print("=" * 50)
    
    for study_type, info in key_studies.items():
        if info["study_ids"]:
            charts_str = ", ".join(map(str, set(info["charts"])))
            ids_str = ", ".join(map(str, info["study_ids"]))
            print(f"✅ {study_type}: Charts [{charts_str}] - IDs [{ids_str}]")
        else:
            print(f"❌ {study_type}: Non trouvé")
    
    print(f"\n💾 Mapping sauvegardé dans: studies_mapping_updated.json")
    print(f"📁 Fichier original: studies_mapping.json")

if __name__ == "__main__":
    main()
