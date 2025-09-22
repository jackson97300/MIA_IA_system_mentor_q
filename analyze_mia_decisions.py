#!/usr/bin/env python3
"""
Analyse des décisions MIA pour comprendre pourquoi aucune décision n'est prise
"""
import json

def analyze_mia_data():
    """Analyse les données MIA dans le fichier unifié"""
    print("🔍 ANALYSE DES DONNÉES MIA")
    print("=" * 50)
    
    # Charger les données
    data = []
    with open('unified_20250918.jsonl', 'r') as f:
        for line in f:
            data.append(json.loads(line))
    
    print(f"📊 Total lignes: {len(data)}")
    
    # Analyser les valeurs MIA
    mia_values = []
    mia_present = 0
    
    for row in data:
        mia_data = row.get('mia', {})
        if mia_data and 'value' in mia_data:
            mia_present += 1
            mia_values.append(mia_data['value'])
    
    print(f"📈 MIA values trouvées: {mia_present}")
    
    if mia_values:
        print(f"📊 MIA min: {min(mia_values):.4f}")
        print(f"📊 MIA max: {max(mia_values):.4f}")
        print(f"📊 MIA > 0.10: {sum(1 for v in mia_values if v > 0.10)}")
        print(f"📊 MIA < -0.10: {sum(1 for v in mia_values if v < -0.10)}")
        print(f"📊 MIA > 0.05: {sum(1 for v in mia_values if v > 0.05)}")
        print(f"📊 MIA < -0.05: {sum(1 for v in mia_values if v < -0.05)}")
        
        # Afficher quelques exemples
        print(f"\n🔍 Exemples de valeurs MIA:")
        for i, v in enumerate(mia_values[:10]):
            print(f"   {i+1}. {v:.4f}")
    else:
        print("❌ Aucune valeur MIA trouvée !")
    
    # Vérifier les autres conditions
    print(f"\n🔍 AUTRES CONDITIONS:")
    
    # Vérifier les niveaux MenthorQ
    menthorq_levels = 0
    for row in data:
        if row.get('menthorq_levels'):
            menthorq_levels += 1
    
    print(f"📊 Lignes avec niveaux MenthorQ: {menthorq_levels}")
    
    # Vérifier les prix
    price_present = 0
    for row in data:
        if row.get('basedata', {}).get('c') or row.get('trade', {}).get('px'):
            price_present += 1
    
    print(f"📊 Lignes avec prix: {price_present}")
    
    # Vérifier les alertes
    alerts_present = 0
    for row in data:
        if row.get('alerts'):
            alerts_present += 1
    
    print(f"📊 Lignes avec alertes: {alerts_present}")

if __name__ == "__main__":
    analyze_mia_data()
