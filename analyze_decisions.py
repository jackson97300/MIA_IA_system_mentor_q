#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Analyse des décisions MenthorQ dans unified_20250918.jsonl
"""

import json

def analyze_decisions():
    print("🔍 ANALYSE DES DÉCISIONS MENTHORQ")
    print("=" * 50)
    
    total_lines = 0
    decisions_count = 0
    non_flat_decisions = 0
    mia_values = []
    menthorq_levels = []
    
    with open('unified_20250918.jsonl', 'r') as f:
        for line_num, line in enumerate(f, 1):
            if not line.strip():
                continue
                
            total_lines += 1
            data = json.loads(line)
            
            # Compter les décisions
            if 'menthorq_decision' in data:
                decisions_count += 1
                decision = data['menthorq_decision']
                action = decision.get('action', 'unknown')
                
                if action != 'flat':
                    non_flat_decisions += 1
                    print(f"🎯 Décision {non_flat_decisions}: {action}")
                    print(f"   MIA: {data.get('mia', {}).get('value', 'N/A')}")
                    print(f"   Prix: {data.get('basedata', {}).get('c', 'N/A')}")
                    print(f"   Timestamp: {data.get('t', 'N/A')}")
                    print()
            
            # Collecter les valeurs MIA
            if 'mia' in data and 'value' in data['mia']:
                mia_values.append(data['mia']['value'])
            
            # Collecter les niveaux MenthorQ
            if 'menthorq_levels' in data:
                menthorq_levels.append(len(data['menthorq_levels']))
    
    print("📊 STATISTIQUES:")
    print(f"   Total lignes: {total_lines}")
    print(f"   Lignes avec décisions: {decisions_count}")
    print(f"   Décisions non-flat: {non_flat_decisions}")
    
    if mia_values:
        print(f"   MIA min/max: {min(mia_values):.3f} / {max(mia_values):.3f}")
        print(f"   MIA moyen: {sum(mia_values)/len(mia_values):.3f}")
    
    if menthorq_levels:
        print(f"   Niveaux MenthorQ moyen: {sum(menthorq_levels)/len(menthorq_levels):.1f}")
    
    print("\n🔍 ÉCHANTILLON DE DONNÉES:")
    with open('unified_20250918.jsonl', 'r') as f:
        for i, line in enumerate(f):
            if i >= 5:  # Limiter à 5 échantillons
                break
            if line.strip():
                data = json.loads(line)
                print(f"Ligne {i+1}:")
                print(f"  t: {data.get('t')}")
                print(f"  MIA: {data.get('mia', {}).get('value', 'N/A')}")
                print(f"  Décision: {data.get('menthorq_decision', {}).get('action', 'N/A')}")
                print(f"  Niveaux MenthorQ: {len(data.get('menthorq_levels', []))}")
                print()

if __name__ == "__main__":
    analyze_decisions()




