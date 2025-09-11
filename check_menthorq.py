#!/usr/bin/env python3
"""
Script pour vérifier les données MenthorQ dans le fichier unifié
"""

import json

def check_menthorq_data():
    """Vérifie les données MenthorQ dans le fichier unifié"""
    print("🔍 VÉRIFICATION DES DONNÉES MENTHORQ")
    print("=" * 50)
    
    try:
        with open('mia_unified_20250907.jsonl', 'r') as f:
            lines = f.readlines()
        
        print(f"📁 Total lignes dans le fichier: {len(lines)}")
        
        # Chercher les lignes MenthorQ
        menthorq_lines = []
        for line in lines:
            if 'menthorq' in line.lower():
                menthorq_lines.append(line)
        
        print(f"🎯 Lignes MenthorQ trouvées: {len(menthorq_lines)}")
        
        if menthorq_lines:
            print("\n📊 PREMIÈRES LIGNES MENTHORQ:")
            for i, line in enumerate(menthorq_lines[:5]):
                try:
                    data = json.loads(line)
                    print(f"  {i+1}. Chart: {data.get('graph', 'N/A')}, Type: {data.get('type', 'N/A')}, Symbol: {data.get('sym', 'N/A')}")
                except:
                    print(f"  {i+1}. Erreur parsing JSON")
        else:
            print("❌ AUCUNE DONNÉE MENTHORQ TROUVÉE")
            
            # Vérifier les types de données disponibles
            print("\n📋 TYPES DE DONNÉES DISPONIBLES:")
            types = set()
            for line in lines[:100]:  # Vérifier les 100 premières lignes
                try:
                    data = json.loads(line)
                    types.add(data.get('type', 'N/A'))
                except:
                    pass
            
            for t in sorted(types):
                print(f"  - {t}")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    check_menthorq_data()



