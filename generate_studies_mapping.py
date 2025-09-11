#!/usr/bin/env python3
"""
Générateur de mapping des études Sierra Chart
============================================

Ce script analyse le code C++ et génère une liste exhaustive de toutes les études
utilisées avec leurs Study IDs et Subgraph mappings pour éliminer les problèmes d'ID.
"""

import re
import json
from pathlib import Path

def extract_studies_mapping(cpp_file):
    """Extrait tous les mappings d'études du fichier C++"""
    
    with open(cpp_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    studies = {}
    
    # Pattern pour capturer les Study IDs
    study_id_pattern = r'Study ID.*?SetInt\((\d+)\)'
    study_matches = re.findall(study_id_pattern, content)
    
    # Pattern pour capturer les Subgraph mappings
    sg_pattern = r'SG.*?SetInt\((\d+)\)'
    sg_matches = re.findall(sg_pattern, content)
    
    # Pattern pour capturer les noms d'inputs avec leurs valeurs
    input_pattern = r'sc\.Input\[(\d+)\]\.Name\s*=\s*"([^"]+)";\s*sc\.Input\[\d+\]\.SetInt\((\d+)\)'
    input_matches = re.findall(input_pattern, content, re.MULTILINE)
    
    # Analyser les patterns spécifiques
    patterns = {
        'VWAP': {
            'study_id': r'VWAP Study ID.*?SetInt\((\d+)\)',
            'subgraphs': {
                'Main': r'VWAP SG - Main.*?SetInt\((\d+)\)',
                'UP1': r'VWAP SG - UP1.*?SetInt\((\d+)\)',
                'DN1': r'VWAP SG - DN1.*?SetInt\((\d+)\)',
                'UP2': r'VWAP SG - UP2.*?SetInt\((\d+)\)',
                'DN2': r'VWAP SG - DN2.*?SetInt\((\d+)\)',
                'UP3': r'VWAP SG - UP3.*?SetInt\((\d+)\)',
                'DN3': r'VWAP SG - DN3.*?SetInt\((\d+)\)'
            }
        },
        'VVA': {
            'current_id': r'VVA Current Study ID.*?SetInt\((\d+)\)',
            'previous_id': r'VVA Previous Study ID.*?SetInt\((\d+)\)'
        },
        'VIX': {
            'chart_number': r'VIX Chart Number.*?SetInt\((\d+)\)',
            'study_id': r'VIX Study ID.*?SetInt\((\d+)\)',
            'subgraph': r'VIX Subgraph Index.*?SetInt\((\d+)\)'
        },
        'NBCV': {
            'study_id': r'NBCV Study ID.*?SetInt\((\d+)\)',
            'subgraphs': {
                'Ask Volume': r'NBCV SG - Ask Volume Total.*?SetInt\((\d+)\)',
                'Bid Volume': r'NBCV SG - Bid Volume Total.*?SetInt\((\d+)\)',
                'Delta': r'NBCV SG - Delta.*?SetInt\((\d+)\)',
                'Trades': r'NBCV SG - Number of Trades.*?SetInt\((\d+)\)',
                'Cumulative': r'NBCV SG - Cumulative.*?SetInt\((\d+)\)'
            }
        },
        'MenthorQ': {
            'chart_number': r'MenthorQ Chart Number.*?SetInt\((\d+)\)',
            'gamma_study_id': r'Gamma Levels Study ID.*?SetInt\((\d+)\)',
            'gamma_sg_count': r'Gamma Levels Subgraphs Count.*?SetInt\((\d+)\)',
            'blind_study_id': r'Blind Spots Study ID.*?SetInt\((\d+)\)',
            'blind_sg_count': r'Blind Spots Subgraphs Count.*?SetInt\((\d+)\)',
            'swing_study_id': r'Swing Levels Study ID.*?SetInt\((\d+)\)',
            'swing_sg_count': r'Swing Levels Subgraphs Count.*?SetInt\((\d+)\)'
        },
        'Correlation': {
            'study_id': r'Correlation Coefficient Study ID.*?SetInt\((\d+)\)'
        },
        'Cumulative_Delta': {
            'study_id': r'Cumulative Delta Bars Study ID.*?SetInt\((\d+)\)'
        }
    }
    
    # Extraire les valeurs pour chaque pattern
    for category, patterns_dict in patterns.items():
        studies[category] = {}
        
        for key, pattern in patterns_dict.items():
            if isinstance(pattern, dict):
                # Sous-catégorie (comme subgraphs)
                studies[category][key] = {}
                for sub_key, sub_pattern in pattern.items():
                    match = re.search(sub_pattern, content)
                    if match:
                        studies[category][key][sub_key] = int(match.group(1))
            else:
                # Valeur simple
                match = re.search(pattern, content)
                if match:
                    studies[category][key] = int(match.group(1))
    
    return studies

def generate_mapping_documentation(studies):
    """Génère la documentation complète des mappings"""
    
    doc = """# 📋 MAPPING COMPLET DES ÉTUDES SIERRA CHART

## 🎯 **Objectif**
Liste exhaustive de toutes les études utilisées avec leurs Study IDs et Subgraph mappings, organisées par chart pour éliminer les problèmes d'ID.

---

## 📊 **ÉTUDES PAR CHART**

### **📈 CHART 3 (1 minute)**
"""
    
    # Chart 3 - VWAP
    if 'VWAP' in studies:
        vwap = studies['VWAP']
        doc += f"""
**VWAP (Volume Weighted Average Price)**:
- Study ID: Auto-résolution par nom (recommandé)
- Subgraphs:
  - SG{vwap.get('subgraphs', {}).get('Main', 1)}: VWAP Principal
  - SG{vwap.get('subgraphs', {}).get('UP1', 2)}: SD+1 Top Band 1
  - SG{vwap.get('subgraphs', {}).get('DN1', 3)}: SD-1 Bottom Band 1
  - SG{vwap.get('subgraphs', {}).get('UP2', 4)}: SD+2 Top Band 2
  - SG{vwap.get('subgraphs', {}).get('DN2', 5)}: SD-2 Bottom Band 2
  - SG{vwap.get('subgraphs', {}).get('UP3', 6)}: SD+3 Top Band 3
  - SG{vwap.get('subgraphs', {}).get('DN3', 7)}: SD-3 Bottom Band 3
"""

    # Chart 3 - VVA
    if 'VVA' in studies:
        vva = studies['VVA']
        doc += f"""
**VVA (Volume Value Area Lines)**:
- Current Study ID: {vva.get('current_id', 9)} (Volume Profile courant)
- Previous Study ID: {vva.get('previous_id', 8)} (Volume Profile précédent)
- Subgraphs:
  - SG1: POC (Point of Control)
  - SG2: VAH (Value Area High)
  - SG3: VAL (Value Area Low)
"""

    # Chart 3 - NBCV
    if 'NBCV' in studies:
        nbcv = studies['NBCV']
        subgraphs = nbcv.get('subgraphs', {})
        doc += f"""
**NBCV (Numbers Bars Calculated Values)**:
- Study ID: {nbcv.get('study_id', 33)} (Graph 3)
- Subgraphs:
  - SG{subgraphs.get('Ask Volume', 6)}: Ask Volume Total
  - SG{subgraphs.get('Bid Volume', 7)}: Bid Volume Total
  - SG{subgraphs.get('Delta', 1)}: Delta (Ask-Bid)
  - SG{subgraphs.get('Trades', 12)}: Number of Trades
  - SG{subgraphs.get('Cumulative', 10)}: Cumulative Sum Of Ask Volume Bid Volume Difference - Day
"""

    doc += """
### **📊 CHART 4 (30 minutes)**
"""
    
    # Chart 4 - Correlation
    if 'Correlation' in studies:
        corr = studies['Correlation']
        doc += f"""
**Correlation ES/NQ**:
- Study ID: {corr.get('study_id', 15)} (Graph 4)
- Subgraph: SG0 (Correlation Coefficient)
"""

    # Chart 4 - Cumulative Delta
    if 'Cumulative_Delta' in studies:
        cum_delta = studies['Cumulative_Delta']
        doc += f"""
**Cumulative Delta Bars**:
- Study ID: {cum_delta.get('study_id', 6)} (Graph 4)
- Subgraph: SG4 (Close - Cumulative Delta)
"""

    doc += """
### **📈 CHART 8 (VIX)**
"""
    
    # Chart 8 - VIX
    if 'VIX' in studies:
        vix = studies['VIX']
        doc += f"""
**VIX (Volatility Index)**:
- Chart Number: {vix.get('chart_number', 8)}
- Study ID: {vix.get('study_id', 23)} (Study/Price Overlay)
- Subgraph: SG{vix.get('subgraph', 4)} (Last)
"""

    doc += """
### **🎯 CHART 10 (MenthorQ)**
"""
    
    # Chart 10 - MenthorQ
    if 'MenthorQ' in studies:
        mq = studies['MenthorQ']
        doc += f"""
**MenthorQ Levels**:
- Chart Number: {mq.get('chart_number', 10)}

**Gamma Levels**:
- Study ID: {mq.get('gamma_study_id', 1)}
- Subgraphs Count: {mq.get('gamma_sg_count', 19)}
- SG1-19: Gamma levels (Call Resistance, Put Support, HVL, etc.)

**Blind Spots**:
- Study ID: {mq.get('blind_study_id', 3)}
- Subgraphs Count: {mq.get('blind_sg_count', 9)}
- SG1-9: Blind spot levels

**Swing Levels**:
- Study ID: {mq.get('swing_study_id', 2)}
- Subgraphs Count: {mq.get('swing_sg_count', 9)}
- SG1-9: Swing levels
"""

    doc += """
---

## 📋 **RÉSUMÉ PAR CHART**

### **Chart 3 (1m) - Données principales**
- ✅ VWAP + 6 bandes (SD±1, ±2, ±3)
- ✅ VVA (VAH/VAL/VPOC) courant et précédent
- ✅ NBCV (Ask/Bid/Delta/Trades/Cumulative)
- ✅ BaseData (OHLC/Volume)
- ✅ DOM (Depth of Market)
- ✅ Time & Sales

### **Chart 4 (30m) - Données M30**
- ✅ Correlation ES/NQ
- ✅ Cumulative Delta Bars
- ✅ Cross-chart data (OHLC, VWAP, NBCV)

### **Chart 8 (VIX) - Volatilité**
- ✅ VIX Last (SG4)
- ✅ Study/Price Overlay (ID 23)

### **Chart 10 (MenthorQ) - Niveaux**
- ✅ Gamma Levels (19 subgraphs)
- ✅ Blind Spots (9 subgraphs)
- ✅ Swing Levels (9 subgraphs)

---

## 🔧 **CONFIGURATION RECOMMANDÉE**

### **Configuration par Chart**

#### **Chart 3 (1m) - Configuration**
```cpp
// VWAP
sc.Input[4].SetInt(0);  // Auto-résolution par nom
sc.Input[39].SetInt(1); // SG1 = VWAP principal
sc.Input[40].SetInt(2); // SG2 = SD+1
sc.Input[41].SetInt(3); // SG3 = SD-1
sc.Input[42].SetInt(4); // SG4 = SD+2
sc.Input[43].SetInt(5); // SG5 = SD-2
sc.Input[44].SetInt(6); // SG6 = SD+3
sc.Input[45].SetInt(7); // SG7 = SD-3

// VVA
sc.Input[7].SetInt(9);  // Volume Profile courant
sc.Input[8].SetInt(8);  // Volume Profile précédent

// NBCV
sc.Input[20].SetInt(33); // Study ID
sc.Input[21].SetInt(6);  // SG6 - Ask Volume
sc.Input[22].SetInt(7);  // SG7 - Bid Volume
sc.Input[23].SetInt(1);  // SG1 - Delta
sc.Input[24].SetInt(12); // SG12 - Trades
sc.Input[25].SetInt(10); // SG10 - Cumulative
```

#### **Chart 4 (30m) - Configuration**
```cpp
// Correlation
sc.Input[46].SetInt(15); // Study ID

// Cumulative Delta
sc.Input[26].SetInt(6);  // Study ID
```

#### **Chart 8 (VIX) - Configuration**
```cpp
// VIX
sc.Input[16].SetInt(8); // Chart 8
sc.Input[17].SetInt(23); // Study ID
sc.Input[18].SetInt(4);  // SG4
```

#### **Chart 10 (MenthorQ) - Configuration**
```cpp
// MenthorQ
sc.Input[32].SetInt(10); // Chart 10
sc.Input[33].SetInt(1);  // Gamma Levels
sc.Input[34].SetInt(19); // Gamma SG Count
sc.Input[35].SetInt(3);  // Blind Spots
sc.Input[36].SetInt(9);  // Blind SG Count
sc.Input[37].SetInt(2);  // Swing Levels
sc.Input[38].SetInt(9);  // Swing SG Count
```

---

## 📝 **NOTES IMPORTANTES**

1. **Auto-résolution VWAP** : Utiliser `sc.GetStudyIDByName()` pour trouver automatiquement l'ID
2. **Validation des IDs** : Toujours vérifier que les Study IDs existent avant utilisation
3. **Subgraphs 0-indexés** : Les subgraphs commencent à 0 dans ACSIL
4. **Cross-chart** : Certaines études sont sur des charts différents
5. **Fallback** : Prévoir des valeurs de fallback si une étude n'est pas trouvée

---

## 🚀 **UTILISATION**

Ce mapping peut être utilisé pour :
- ✅ Configuration automatique des études
- ✅ Validation des Study IDs
- ✅ Debugging des problèmes de mapping
- ✅ Documentation pour les développeurs
- ✅ Tests automatisés
"""
    
    return doc

def main():
    """Fonction principale"""
    
    print("🔍 Génération du mapping des études Sierra Chart...")
    
    # Fichier C++ principal
    cpp_file = "MIA_Chart_Dumper_patched_VIX_NBCV_Quotes_Final_Corrected.cpp"
    
    if not Path(cpp_file).exists():
        print(f"❌ Fichier C++ non trouvé: {cpp_file}")
        return
    
    # Extraire les mappings
    studies = extract_studies_mapping(cpp_file)
    
    # Générer la documentation
    doc = generate_mapping_documentation(studies)
    
    # Sauvegarder
    output_file = "MAPPING_ETUDES_SIERRA.md"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(doc)
    
    # Sauvegarder aussi en JSON pour utilisation programmatique
    json_file = "studies_mapping.json"
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(studies, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Mapping généré avec succès!")
    print(f"   📄 Documentation: {output_file}")
    print(f"   📊 JSON: {json_file}")
    print(f"   📋 Études trouvées: {len(studies)}")

if __name__ == "__main__":
    main()
