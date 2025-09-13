#!/usr/bin/env python3
"""
Analyse détaillée des outliers de volume dans Chart 3
"""

import pandas as pd
import numpy as np
import json
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns

def analyze_volume_outliers():
    """Analyse détaillée des outliers de volume"""
    
    print("🔍 ANALYSE DÉTAILLÉE DES OUTLIERS DE VOLUME")
    print("=" * 60)
    
    # Charger les données Chart 3
    try:
        df = pd.read_json('chart_3_basedata_20250912.jsonl', lines=True)
        print(f"✅ Données chargées : {len(df)} enregistrements")
    except Exception as e:
        print(f"❌ Erreur chargement : {e}")
        return
    
    # Analyser le volume
    volume_col = 'v' if 'v' in df.columns else 'volume'
    if volume_col not in df.columns:
        print("❌ Colonne volume non trouvée")
        return
    
    volumes = df[volume_col].dropna()
    print(f"\n📊 STATISTIQUES DE VOLUME")
    print(f"   Total enregistrements : {len(volumes)}")
    print(f"   Volume min : {volumes.min():,.0f}")
    print(f"   Volume max : {volumes.max():,.0f}")
    print(f"   Volume médian : {volumes.median():,.0f}")
    print(f"   Volume moyen : {volumes.mean():,.0f}")
    print(f"   Écart-type : {volumes.std():,.0f}")
    
    # Calculer les outliers avec différentes méthodes
    print(f"\n🎯 DÉTECTION DES OUTLIERS")
    
    # Méthode 1: Règle des 3 sigmas
    mean_vol = volumes.mean()
    std_vol = volumes.std()
    threshold_3sigma = mean_vol + 3 * std_vol
    outliers_3sigma = volumes[volumes > threshold_3sigma]
    print(f"   📈 Règle 3 sigmas (> {threshold_3sigma:,.0f}) : {len(outliers_3sigma)} outliers ({len(outliers_3sigma)/len(volumes)*100:.1f}%)")
    
    # Méthode 2: IQR (Interquartile Range)
    Q1 = volumes.quantile(0.25)
    Q3 = volumes.quantile(0.75)
    IQR = Q3 - Q1
    threshold_iqr = Q3 + 1.5 * IQR
    outliers_iqr = volumes[volumes > threshold_iqr]
    print(f"   📊 IQR 1.5x (> {threshold_iqr:,.0f}) : {len(outliers_iqr)} outliers ({len(outliers_iqr)/len(volumes)*100:.1f}%)")
    
    # Méthode 3: Percentile 95
    threshold_95 = volumes.quantile(0.95)
    outliers_95 = volumes[volumes > threshold_95]
    print(f"   📈 Percentile 95 (> {threshold_95:,.0f}) : {len(outliers_95)} outliers ({len(outliers_95)/len(volumes)*100:.1f}%)")
    
    # Analyser les valeurs extrêmes
    print(f"\n🔍 TOP 10 VOLUMES LES PLUS ÉLEVÉS")
    top_volumes = volumes.nlargest(10)
    for i, vol in enumerate(top_volumes, 1):
        print(f"   {i:2d}. {vol:,.0f}")
    
    # Analyser les volumes = 0
    zero_volumes = volumes[volumes == 0]
    print(f"\n⚠️  VOLUMES ZÉRO")
    print(f"   Nombre de volumes = 0 : {len(zero_volumes)} ({len(zero_volumes)/len(volumes)*100:.1f}%)")
    
    # Analyser la distribution par heure
    if 't' in df.columns:
        df['datetime'] = pd.to_datetime(df['t'], unit='s')
        df['hour'] = df['datetime'].dt.hour
        
        print(f"\n⏰ DISTRIBUTION PAR HEURE")
        hourly_stats = df.groupby('hour')[volume_col].agg(['count', 'mean', 'std', 'max']).round(0)
        print(hourly_stats)
        
        # Identifier les heures avec le plus d'outliers
        print(f"\n🚨 HEURES AVEC LE PLUS D'OUTLIERS")
        for hour in sorted(df['hour'].unique()):
            hour_data = df[df['hour'] == hour][volume_col]
            if len(hour_data) > 0:
                hour_outliers = hour_data[hour_data > threshold_3sigma]
                if len(hour_outliers) > 0:
                    print(f"   {hour:2d}h : {len(hour_outliers)} outliers ({len(hour_outliers)/len(hour_data)*100:.1f}%)")
    
    # Analyser les patterns temporels
    print(f"\n📈 PATTERNS TEMPORELS")
    if 't' in df.columns:
        # Regrouper par minute pour voir les pics
        df['minute'] = df['datetime'].dt.floor('T')
        minute_volumes = df.groupby('minute')[volume_col].sum()
        
        print(f"   Volume total par minute (top 10) :")
        top_minutes = minute_volumes.nlargest(10)
        for minute, vol in top_minutes.items():
            print(f"   {minute.strftime('%H:%M')} : {vol:,.0f}")
    
    # Recommandations
    print(f"\n💡 RECOMMANDATIONS")
    if len(outliers_3sigma) / len(volumes) > 0.05:  # >5%
        print("   ⚠️  TROP D'OUTLIERS - Problème probable de collecte")
        print("   🔧 Vérifier la connectivité Sierra Chart")
        print("   🔧 Implémenter des filtres de validation")
    elif len(outliers_3sigma) / len(volumes) > 0.02:  # >2%
        print("   ⚠️  OUTLIERS ÉLEVÉS - Surveillance recommandée")
        print("   📊 Monitorer en temps réel")
    else:
        print("   ✅ OUTLIERS ACCEPTABLES - Données normales")
    
    # Analyser bidvol et askvol si disponibles
    for col in ['bidvol', 'askvol']:
        if col in df.columns:
            print(f"\n📊 ANALYSE {col.upper()}")
            col_data = df[col].dropna()
            if len(col_data) > 0:
                col_outliers = col_data[col_data > col_data.mean() + 3 * col_data.std()]
                print(f"   Outliers {col} : {len(col_outliers)} ({len(col_outliers)/len(col_data)*100:.1f}%)")
                print(f"   Max {col} : {col_data.max():,.0f}")

if __name__ == "__main__":
    analyze_volume_outliers()


