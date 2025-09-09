#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script rapide pour examiner des échantillons de données du fichier chart_3_20250904.jsonl
"""

import json
from pathlib import Path

def examine_data_samples():
    """Examine quelques échantillons de données pour comprendre la structure"""
    file_path = Path("chart_3_20250904.jsonl")
    
    if not file_path.exists():
        print(f"❌ Fichier non trouvé: {file_path}")
        return
        
    print("🔍 Analyse rapide des échantillons de données...")
    print("=" * 60)
    
    # Compteurs par type
    type_counts = {}
    samples = {}
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for i, line in enumerate(f):
                if i >= 1000:  # Limiter à 1000 lignes pour l'analyse rapide
                    break
                    
                try:
                    data = json.loads(line.strip())
                    record_type = data.get('type', 'unknown')
                    
                    # Compter les types
                    type_counts[record_type] = type_counts.get(record_type, 0) + 1
                    
                    # Stocker un échantillon de chaque type
                    if record_type not in samples:
                        samples[record_type] = data
                        
                except json.JSONDecodeError:
                    continue
                    
    except Exception as e:
        print(f"❌ Erreur lecture: {e}")
        return
        
    # Affichage des résultats
    print("📊 Types de données détectés (premiers 1000 enregistrements):")
    print("-" * 60)
    
    for record_type, count in sorted(type_counts.items()):
        print(f"🔹 {record_type}: {count} enregistrements")
        
        if record_type in samples:
            sample = samples[record_type]
            print(f"   📋 Échantillon: {list(sample.keys())}")
            
            # Afficher quelques valeurs clés
            if 't' in sample:
                print(f"   ⏰ Timestamp: {sample['t']}")
            if 'sym' in sample:
                print(f"   🏷️  Symbole: {sample['sym']}")
            if 'i' in sample:
                print(f"   📍 Index: {sample['i']}")
                
            # Afficher quelques valeurs numériques
            numeric_fields = [k for k, v in sample.items() if isinstance(v, (int, float))]
            if numeric_fields:
                print(f"   🔢 Champs numériques: {numeric_fields[:5]}")
                
            print()
            
    # Analyse des problèmes détectés
    print("⚠️  PROBLÈMES IDENTIFIÉS:")
    print("-" * 60)
    
    if 'vva' in samples:
        vva_sample = samples['vva']
        vah = vva_sample.get('vah')
        val = vva_sample.get('val')
        if vah and val and val >= vah:
            print(f"🔴 VVA: VAL ({val}) >= VAH ({vah}) - Incohérence détectée")
            
    if 'vix' in samples:
        vix_sample = samples['vix']
        mode = vix_sample.get('mode')
        if mode == 0:
            print(f"🔴 VIX: Mode invalide ({mode}) - Devrait être 'normal', 'contango', ou 'backwardation'")
            
    if 'quote' in samples:
        quote_sample = samples['quote']
        bid = quote_sample.get('bid')
        ask = quote_sample.get('ask')
        if bid and ask:
            # Vérifier l'échelle
            if bid > 10000 or ask > 10000:
                print(f"🔴 QUOTE: Échelle probablement incorrecte - bid: {bid}, ask: {ask}")
                
    print("\n✅ Analyse rapide terminée!")

if __name__ == "__main__":
    examine_data_samples()







