#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Analyse détaillée de chaque type de données sur les dernières lignes - Système MIA
"""

import json
from pathlib import Path
from collections import defaultdict, Counter
from datetime import datetime

def detailed_latest_analysis():
    file_path = "chart_3_20250904.jsonl"
    
    if not Path(file_path).exists():
        print(f"❌ Fichier non trouvé: {file_path}")
        return
    
    print("🔍 ANALYSE DÉTAILLÉE DES DERNIÈRES DONNÉES - SYSTÈME MIA")
    print("=" * 70)
    
    # Compter le nombre total de lignes
    total_lines = sum(1 for _ in open(file_path, 'r', encoding='utf-8'))
    print(f"📊 Total lignes dans le fichier: {total_lines:,}")
    
    # Analyser les 2000 dernières lignes
    start_line = max(0, total_lines - 2000)
    print(f"🔍 Analyse des lignes {start_line:,} à {total_lines:,} (2000 dernières)")
    
    data_types = defaultdict(list)
    data_samples = defaultdict(list)
    coherence_issues = []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f):
            if i < start_line:
                continue
                
            try:
                data = json.loads(line.strip())
                data_type = data.get('type', 'NO_TYPE')
                data_types[data_type].append(data)
                
                # Garder un échantillon de chaque type
                if len(data_samples[data_type]) < 3:
                    data_samples[data_type].append(data)
                    
            except Exception as e:
                coherence_issues.append(f"Ligne {i+1}: Erreur parsing - {e}")
    
    # Résumé global des dernières données
    print(f"\n📋 RÉSUMÉ DES DERNIÈRES DONNÉES:")
    total_recent = sum(len(data) for data in data_types.values())
    print(f"   Total enregistrements: {total_recent:,}")
    print(f"   Types de données: {len(data_types)}")
    
    # Analyser chaque type en détail
    print(f"\n🔍 ANALYSE DÉTAILLÉE PAR TYPE:")
    print("=" * 50)
    
    for data_type, data_list in sorted(data_types.items(), key=lambda x: len(x[1]), reverse=True):
        print(f"\n📊 {data_type.upper()} - {len(data_list):,} enregistrements")
        print("-" * 40)
        
        # Statistiques de base
        percentage = (len(data_list) / total_recent) * 100
        print(f"   📈 Fréquence: {percentage:.1f}% des données récentes")
        
        # Échantillons de données
        if data_samples[data_type]:
            sample = data_samples[data_type][0]
            print(f"   📝 Structure: {list(sample.keys())}")
            
            # Analyse spécifique par type
            if data_type == 'quote':
                analyze_quotes(data_list, data_samples[data_type])
            elif data_type == 'depth':
                analyze_depth(data_list, data_samples[data_type])
            elif data_type == 'vap':
                analyze_vap(data_list, data_samples[data_type])
            elif data_type == 'basedata':
                analyze_basedata(data_list, data_samples[data_type])
            elif data_type == 'vwap':
                analyze_vwap(data_list, data_samples[data_type])
            elif data_type == 'vva':
                analyze_vva(data_list, data_samples[data_type])
            elif data_type == 'vix':
                analyze_vix(data_list, data_samples[data_type])
            elif data_type == 'nbcv':
                analyze_nbcv(data_list, data_samples[data_type])
            elif data_type == 'trade':
                analyze_trade(data_list, data_samples[data_type])
            else:
                print(f"   🔍 Type non analysé spécifiquement")
        
        # Vérifier la cohérence temporelle
        check_temporal_coherence(data_type, data_list)
    
    # Résumé des problèmes détectés
    print(f"\n⚠️  PROBLÈMES DÉTECTÉS:")
    print("-" * 30)
    
    if coherence_issues:
        print(f"   🔧 Erreurs de parsing: {len(coherence_issues)}")
        for issue in coherence_issues[:3]:
            print(f"      ❌ {issue}")
    
    # Évaluation globale
    print(f"\n🎯 ÉVALUATION GLOBALE:")
    print("-" * 30)
    
    vix_count = len(data_types.get('vix', []))
    if vix_count == 0:
        print(f"   🚨 CRITIQUE: Aucun VIX dans les dernières données!")
    elif vix_count < 5:
        print(f"   ⚠️  ATTENTION: VIX très rare ({vix_count})")
    else:
        print(f"   ✅ VIX normal: {vix_count} enregistrements")
    
    print(f"\n" + "=" * 70)

def analyze_quotes(quotes, samples):
    """Analyse détaillée des quotes"""
    print(f"   💱 Quotes bid/ask - Analyse:")
    
    # Vérifier les spreads
    bid_ask_issues = 0
    for quote in quotes:
        if 'bid' in quote and 'ask' in quote:
            if quote['bid'] >= quote['ask']:
                bid_ask_issues += 1
    
    if bid_ask_issues == 0:
        print(f"      ✅ Spreads cohérents")
    else:
        print(f"      ⚠️  {bid_ask_issues} problèmes de spread détectés")
    
    # Échantillon
    if samples:
        sample = samples[0]
        print(f"      📊 Échantillon: bid={sample.get('bid', 'N/A')}, ask={sample.get('ask', 'N/A')}")

def analyze_depth(depth_data, samples):
    """Analyse détaillée de la profondeur"""
    print(f"   🏗️  Structure DOM - Analyse:")
    
    # Vérifier la structure
    structure_issues = 0
    for depth in depth_data:
        if 'levels' in depth:
            if not isinstance(depth['levels'], list) or len(depth['levels']) == 0:
                structure_issues += 1
    
    if structure_issues == 0:
        print(f"      ✅ Structure DOM cohérente")
    else:
        print(f"      ⚠️  {structure_issues} problèmes de structure")
    
    # Échantillon
    if samples:
        sample = samples[0]
        levels_count = len(sample.get('levels', []))
        print(f"      📊 Échantillon: {levels_count} niveaux de profondeur")

def analyze_vap(vap_data, samples):
    """Analyse détaillée du VAP"""
    print(f"   📊 Volume at Price - Analyse:")
    
    # Vérifier les valeurs
    value_issues = 0
    for vap in vap_data:
        if 'price' in vap and 'volume' in vap:
            if vap['price'] <= 0 or vap['volume'] <= 0:
                value_issues += 1
    
    if value_issues == 0:
        print(f"      ✅ Valeurs VAP cohérentes")
    else:
        print(f"      ⚠️  {value_issues} problèmes de valeurs")
    
    # Échantillon
    if samples:
        sample = samples[0]
        print(f"      📊 Échantillon: prix={sample.get('price', 'N/A')}, volume={sample.get('volume', 'N/A')}")

def analyze_basedata(basedata, samples):
    """Analyse détaillée des données de base"""
    print(f"   📈 Données de base OHLCV - Analyse:")
    
    # Échantillon
    if samples:
        sample = samples[0]
        print(f"      📊 Échantillon: open={sample.get('open', 'N/A')}, high={sample.get('high', 'N/A')}")
        print(f"      📊 low={sample.get('low', 'N/A')}, close={sample.get('close', 'N/A')}, volume={sample.get('volume', 'N/A')}")

def analyze_vwap(vwap_data, samples):
    """Analyse détaillée du VWAP"""
    print(f"   📊 VWAP - Analyse:")
    
    # Échantillon
    if samples:
        sample = samples[0]
        print(f"      📊 Échantillon: valeur={sample.get('value', 'N/A')}")

def analyze_vva(vva_data, samples):
    """Analyse détaillée du VVA"""
    print(f"   📊 Volume Value Area - Analyse:")
    
    # Vérifier la cohérence VAH/VAL
    structure_issues = 0
    for vva in vva_data:
        if 'vah' in vva and 'val' in vva:
            if vva['vah'] < vva['val']:
                structure_issues += 1
    
    if structure_issues == 0:
        print(f"      ✅ Structure VVA cohérente")
    else:
        print(f"      ⚠️  {structure_issues} problèmes de structure (VAH < VAL)")
    
    # Échantillon
    if samples:
        sample = samples[0]
        print(f"      📊 Échantillon: VAH={sample.get('vah', 'N/A')}, VAL={sample.get('val', 'N/A')}, VPOC={sample.get('vpoc', 'N/A')}")

def analyze_vix(vix_data, samples):
    """Analyse détaillée du VIX"""
    print(f"   🌊 VIX - Analyse:")
    
    if len(vix_data) == 0:
        print(f"      ❌ Aucun VIX trouvé!")
        return
    
    # Analyser les valeurs
    vix_values = [vix.get('last', 0) for vix in vix_data if 'last' in vix]
    if vix_values:
        print(f"      📊 Valeurs: {min(vix_values):.2f} - {max(vix_values):.2f}")
        print(f"      📊 Nombre d'enregistrements: {len(vix_data)}")
    
    # Échantillon
    if samples:
        sample = samples[0]
        print(f"      📊 Échantillon: last={sample.get('last', 'N/A')}, source={sample.get('source', 'N/A')}")

def analyze_nbcv(nbcv_data, samples):
    """Analyse détaillée du NBCV"""
    print(f"   📊 NBCV OrderFlow - Analyse:")
    
    # Échantillon
    if samples:
        sample = samples[0]
        print(f"      📊 Échantillon: ask={sample.get('ask', 'N/A')}, bid={sample.get('bid', 'N/A')}")

def analyze_trade(trade_data, samples):
    """Analyse détaillée des trades"""
    print(f"   💱 Trades - Analyse:")
    
    # Échantillon
    if samples:
        sample = samples[0]
        print(f"      📊 Échantillon: prix={sample.get('price', 'N/A')}, taille={sample.get('size', 'N/A')}")

def check_temporal_coherence(data_type, data_list):
    """Vérifie la cohérence temporelle d'un type de données"""
    if len(data_list) < 2:
        return
    
    # Extraire les timestamps
    timestamps = [d.get('t', 0) for d in data_list if 't' in d]
    if len(timestamps) < 2:
        return
    
    # Vérifier l'ordre
    sorted_timestamps = sorted(timestamps)
    if timestamps != sorted_timestamps:
        print(f"      ⚠️  Timestamps non ordonnés")

if __name__ == "__main__":
    detailed_latest_analysis()







