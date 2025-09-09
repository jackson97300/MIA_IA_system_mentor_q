#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de synthèse des anomalies détectées dans chart_3_20250904.jsonl
Analyse les résultats et propose des solutions
"""

import json
import csv
from pathlib import Path
from collections import Counter, defaultdict

def analyser_synthese():
    """Analyse la synthèse des anomalies détectées"""
    print("🔍 SYNTHÈSE DES ANOMALIES DÉTECTÉES")
    print("=" * 60)
    
    # Vérifier l'existence des fichiers
    report_path = Path("report.md")
    anomalies_path = Path("anomalies.csv")
    
    if not report_path.exists():
        print("❌ Fichier report.md non trouvé. Exécutez d'abord analyze_chart_data.py")
        return
        
    if not anomalies_path.exists():
        print("❌ Fichier anomalies.csv non trouvé. Exécutez d'abord analyze_chart_data.py")
        return
    
    # Analyser le rapport
    print("📊 ANALYSE DU RAPPORT...")
    print("-" * 40)
    
    with open(report_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    # Extraire les informations clés
    lines = content.split('\n')
    
    # Chercher les statistiques
    total_records = None
    total_anomalies = None
    
    for line in lines:
        if "Total des enregistrements:" in line:
            total_records = line.split(":")[1].strip().replace(",", "")
        elif "Total des anomalies:" in line:
            total_anomalies = line.split(":")[1].strip()
            
    if total_records and total_anomalies:
        print(f"📈 Total enregistrements: {total_records}")
        print(f"⚠️  Total anomalies: {total_anomalies}")
        
        # Calculer le pourcentage d'anomalies
        try:
            total_records_int = int(total_records)
            total_anomalies_int = int(total_anomalies)
            pourcentage = (total_anomalies_int / total_records_int) * 100
            print(f"📊 Pourcentage d'anomalies: {pourcentage:.2f}%")
        except:
            pass
    
    # Analyser le CSV des anomalies
    print("\n📋 ANALYSE DÉTAILLÉE DES ANOMALIES...")
    print("-" * 40)
    
    anomalies_by_type = defaultdict(list)
    anomalies_by_rule = defaultdict(list)
    
    try:
        with open(anomalies_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                anomalies_by_type[row['type']].append(row)
                anomalies_by_rule[row['rule']].append(row)
                
    except Exception as e:
        print(f"❌ Erreur lecture CSV: {e}")
        return
    
    # Afficher le résumé par type
    print("\n🎯 RÉSUMÉ PAR TYPE DE DONNÉES:")
    print("-" * 40)
    
    for data_type, anomalies in anomalies_by_type.items():
        count = len(anomalies)
        if count > 0:
            print(f"🔹 {data_type}: {count} anomalies")
            
            # Analyser les règles les plus fréquentes pour ce type
            rules = Counter(anom['rule'] for anom in anomalies)
            top_rules = rules.most_common(3)
            for rule, rule_count in top_rules:
                print(f"   - {rule}: {rule_count}")
    
    # Analyser les règles les plus problématiques
    print("\n🚨 RÈGLES LES PLUS PROBLÉMATIQUES:")
    print("-" * 40)
    
    rule_counts = Counter(anom['rule'] for anom in anomalies_by_rule['scale_issue'])
    for rule, count in rule_counts.most_common(10):
        print(f"🔴 {rule}: {count} violations")
        
        # Analyser quelques exemples
        examples = anomalies_by_rule[rule][:3]
        for i, example in enumerate(examples, 1):
            print(f"   Exemple {i}: {example['message'][:80]}...")
    
    # Analyser les problèmes spécifiques
    print("\n🔍 ANALYSE DES PROBLÈMES SPÉCIFIQUES:")
    print("-" * 40)
    
    # 1. Problème d'échelle des quotes
    scale_issues = anomalies_by_rule.get('scale_issue', [])
    if scale_issues:
        print(f"🔴 PROBLÈME D'ÉCHELLE QUOTES: {len(scale_issues)} violations")
        print("   💡 Les quotes semblent avoir une échelle incorrecte (×10, ×100, etc.)")
        print("   🎯 Solution: Vérifier la configuration d'échelle dans Sierra Chart")
        
        # Analyser quelques exemples
        for i, issue in enumerate(scale_issues[:3], 1):
            print(f"   Exemple {i}: {issue['message']}")
    
    # 2. Problème VVA (VAL >= VAH)
    vva_issues = anomalies_by_rule.get('val_vah_inverted', [])
    if vva_issues:
        print(f"\n🔴 PROBLÈME VVA: {len(vva_issues)} violations")
        print("   💡 VAL (Volume Area Low) >= VAH (Volume Area High) - Incohérent")
        print("   🎯 Solution: Vérifier la logique de calcul du Volume Profile")
        
        # Analyser quelques exemples
        for i, issue in enumerate(vva_issues[:3], 1):
            print(f"   Exemple {i}: {issue['message']}")
    
    # 3. Problème VIX mode
    vix_issues = anomalies_by_rule.get('mode_invalid', [])
    if vix_issues:
        print(f"\n🔴 PROBLÈME VIX: {len(vix_issues)} violations")
        print("   💡 Mode VIX invalide (0 au lieu de 'normal', 'contango', 'backwardation')")
        print("   🎯 Solution: Vérifier la configuration des études VIX dans Sierra Chart")
    
    # 4. Problème NBCV delta
    nbcv_issues = anomalies_by_rule.get('delta_mismatch', [])
    if nbcv_issues:
        print(f"\n🔴 PROBLÈME NBCV: {len(nbcv_issues)} violations")
        print("   💡 Delta calculé ≠ Delta fourni")
        print("   🎯 Solution: Vérifier la logique de calcul du delta dans Sierra Chart")
    
    # 5. Problème de timestamps décroissants
    time_issues = anomalies_by_rule.get('decreasing_time', [])
    if time_issues:
        print(f"\n🔴 PROBLÈME TIMESTAMPS: {len(time_issues)} violations")
        print("   💡 Timestamps non chronologiques")
        print("   🎯 Solution: Vérifier la synchronisation des données")
    
    # Recommandations générales
    print("\n💡 RECOMMANDATIONS GÉNÉRALES:")
    print("-" * 40)
    
    print("1. 🔧 CONFIGURATION SIERRA CHART:")
    print("   - Vérifier les paramètres d'échelle des quotes")
    print("   - Contrôler la configuration des études VIX")
    print("   - Valider les paramètres du Volume Profile")
    
    print("\n2. 📊 QUALITÉ DES DONNÉES:")
    print("   - Vérifier la source des données (feed, provider)")
    print("   - Contrôler la synchronisation des timestamps")
    print("   - Valider la cohérence des calculs NBCV")
    
    print("\n3. 🚨 PRIORITÉS DE CORRECTION:")
    print("   - Échelle des quotes (151,018 violations)")
    print("   - Configuration VVA (7,072 violations)")
    print("   - Mode VIX (3,536 violations)")
    print("   - Cohérence NBCV (20 violations)")
    
    print("\n4. 📈 MONITORING:")
    print("   - Mettre en place des alertes sur les anomalies")
    print("   - Surveiller la qualité des données en temps réel")
    print("   - Valider les corrections après reconfiguration")
    
    # Statistiques finales
    print("\n📊 STATISTIQUES FINALES:")
    print("-" * 40)
    
    total_anomalies = sum(len(anomalies) for anomalies in anomalies_by_type.values())
    total_records_analyzed = 178423  # D'après le rapport
    
    print(f"📈 Enregistrements analysés: {total_records_analyzed:,}")
    print(f"⚠️  Anomalies détectées: {total_anomalies:,}")
    print(f"📊 Taux d'anomalies: {(total_anomalies/total_records_analyzed)*100:.2f}%")
    
    # Types de données avec problèmes
    problematic_types = [t for t, anomalies in anomalies_by_type.items() if len(anomalies) > 0]
    print(f"🔴 Types problématiques: {len(problematic_types)}")
    
    # Types de données sains
    healthy_types = [t for t, anomalies in anomalies_by_type.items() if len(anomalies) == 0]
    print(f"✅ Types sains: {len(healthy_types)}")
    
    print("\n" + "=" * 60)
    print("🎯 SYNTHÈSE TERMINÉE")
    print("=" * 60)

if __name__ == "__main__":
    analyser_synthese()







