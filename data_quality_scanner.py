#!/usr/bin/env python3
"""
🔍 SCANNER DE QUALITÉ DES DONNÉES - SYSTÈME MIA
================================================

Scanner complet pour analyser :
1. Gaps temporels dans les données
2. Valeurs aberrantes (outliers)
3. Anomalies MenthorQ spécifiques
4. Cohérence des données entre charts
5. Problèmes de synchronisation

Auteur: MIA_IA_SYSTEM
Date: 13 septembre 2025
"""

import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Tuple, Optional
import matplotlib.pyplot as plt
import seaborn as sns
from collections import defaultdict, Counter
import warnings
warnings.filterwarnings('ignore')

class DataQualityScanner:
    """Scanner de qualité des données MIA"""
    
    def __init__(self, data_path: str = "."):
        self.data_path = Path(data_path)
        self.results = {
            "gaps": {},
            "outliers": {},
            "menthorq_anomalies": {},
            "synchronization_issues": {},
            "data_consistency": {},
            "summary": {}
        }
        
    def scan_all_data(self) -> Dict[str, Any]:
        """Scanner complet de toutes les données"""
        print("🔍 DÉMARRAGE DU SCAN DE QUALITÉ DES DONNÉES")
        print("=" * 60)
        
        # 1. Scanner les gaps temporels
        print("\n📊 1. ANALYSE DES GAPS TEMPORELS")
        self.scan_temporal_gaps()
        
        # 2. Scanner les valeurs aberrantes
        print("\n📊 2. ANALYSE DES VALEURS ABERRANTES")
        self.scan_outliers()
        
        # 3. Scanner les anomalies MenthorQ
        print("\n📊 3. ANALYSE DES ANOMALIES MENTHORQ")
        self.scan_menthorq_anomalies()
        
        # 4. Scanner les problèmes de synchronisation
        print("\n📊 4. ANALYSE DE LA SYNCHRONISATION")
        self.scan_synchronization_issues()
        
        # 5. Scanner la cohérence des données
        print("\n📊 5. ANALYSE DE LA COHÉRENCE")
        self.scan_data_consistency()
        
        # 6. Générer le résumé
        print("\n📊 6. GÉNÉRATION DU RÉSUMÉ")
        self.generate_summary()
        
        return self.results
    
    def scan_temporal_gaps(self):
        """Scanner les gaps temporels"""
        chart_files = {
            3: ["chart_3_basedata_20250912.jsonl", "chart_3_vwap_20250912.jsonl", 
                "chart_3_vva_20250912.jsonl", "chart_3_nbcv_20250912.jsonl"],
            4: ["chart_4_ohlc_20250912.jsonl", "chart_4_volume_profile_20250912.jsonl"],
            8: ["chart_8_vix_20250912.jsonl"],
            10: ["chart_10_menthorq_20250912.jsonl"]
        }
        
        for chart_id, files in chart_files.items():
            print(f"\n  📈 CHART {chart_id}:")
            chart_gaps = {}
            
            for file in files:
                file_path = self.data_path / file
                if not file_path.exists():
                    print(f"    ⚠️  Fichier manquant: {file}")
                    continue
                    
                gaps = self._analyze_file_gaps(file_path, chart_id)
                if gaps:
                    chart_gaps[file] = gaps
                    print(f"    📄 {file}: {gaps['total_gaps']} gaps détectés")
                    if gaps['max_gap_seconds'] > 30:
                        print(f"      🚨 Gap max: {gaps['max_gap_seconds']}s")
            
            self.results["gaps"][f"chart_{chart_id}"] = chart_gaps
    
    def _analyze_file_gaps(self, file_path: Path, chart_id: int) -> Optional[Dict]:
        """Analyser les gaps d'un fichier"""
        try:
            data = []
            with open(file_path, 'r') as f:
                for line in f:
                    try:
                        record = json.loads(line.strip())
                        if 't' in record:
                            data.append(record['t'])
                    except:
                        continue
            
            if len(data) < 2:
                return None
                
            # Convertir en timestamps et trier
            timestamps = sorted([float(ts) for ts in data])
            
            # Calculer les gaps
            gaps = []
            for i in range(1, len(timestamps)):
                gap = timestamps[i] - timestamps[i-1]
                if gap > 1.0:  # Gap > 1 seconde
                    gaps.append(gap)
            
            return {
                "total_gaps": len(gaps),
                "max_gap_seconds": max(gaps) if gaps else 0,
                "avg_gap_seconds": np.mean(gaps) if gaps else 0,
                "total_records": len(timestamps),
                "time_span_hours": (timestamps[-1] - timestamps[0]) / 3600
            }
            
        except Exception as e:
            print(f"    ❌ Erreur analyse {file_path}: {e}")
            return None
    
    def scan_outliers(self):
        """Scanner les valeurs aberrantes"""
        print("  🔍 Analyse des valeurs aberrantes par chart...")
        
        # Chart 3 - BaseData
        self._scan_chart3_outliers()
        
        # Chart 4 - Volume Profile
        self._scan_chart4_outliers()
        
        # Chart 8 - VIX
        self._scan_chart8_outliers()
        
        # Chart 10 - MenthorQ
        self._scan_chart10_outliers()
    
    def _scan_chart3_outliers(self):
        """Scanner les outliers Chart 3"""
        file_path = self.data_path / "chart_3_basedata_20250912.jsonl"
        if not file_path.exists():
            return
            
        try:
            data = []
            with open(file_path, 'r') as f:
                for line in f:
                    try:
                        record = json.loads(line.strip())
                        if record.get('type') == 'basedata':
                            data.append(record)
                    except:
                        continue
            
            if not data:
                return
                
            df = pd.DataFrame(data)
            
            # Analyser les prix OHLC
            price_columns = ['o', 'h', 'l', 'c']
            outliers = {}
            
            for col in price_columns:
                if col in df.columns:
                    values = pd.to_numeric(df[col], errors='coerce')
                    q1 = values.quantile(0.25)
                    q3 = values.quantile(0.75)
                    iqr = q3 - q1
                    lower_bound = q1 - 1.5 * iqr
                    upper_bound = q3 + 1.5 * iqr
                    
                    outliers_count = len(values[(values < lower_bound) | (values > upper_bound)])
                    outliers[col] = {
                        "count": outliers_count,
                        "percentage": (outliers_count / len(values)) * 100,
                        "bounds": [lower_bound, upper_bound]
                    }
            
            # Analyser les volumes
            volume_columns = ['v', 'bidvol', 'askvol']
            for col in volume_columns:
                if col in df.columns:
                    values = pd.to_numeric(df[col], errors='coerce')
                    # Pour les volumes, utiliser un seuil plus strict
                    threshold = values.quantile(0.95)
                    outliers_count = len(values[values > threshold])
                    outliers[col] = {
                        "count": outliers_count,
                        "percentage": (outliers_count / len(values)) * 100,
                        "threshold": threshold
                    }
            
            self.results["outliers"]["chart_3_basedata"] = outliers
            
        except Exception as e:
            print(f"    ❌ Erreur analyse outliers Chart 3: {e}")
    
    def _scan_chart4_outliers(self):
        """Scanner les outliers Chart 4"""
        file_path = self.data_path / "chart_4_volume_profile_20250912.jsonl"
        if not file_path.exists():
            return
            
        try:
            data = []
            with open(file_path, 'r') as f:
                for line in f:
                    try:
                        record = json.loads(line.strip())
                        data.append(record)
                    except:
                        continue
            
            if not data:
                return
                
            df = pd.DataFrame(data)
            
            # Analyser les niveaux de volume profile
            vp_columns = ['vpoc', 'vah', 'val']
            outliers = {}
            
            for col in vp_columns:
                if col in df.columns:
                    values = pd.to_numeric(df[col], errors='coerce')
                    if len(values.dropna()) > 0:
                        q1 = values.quantile(0.25)
                        q3 = values.quantile(0.75)
                        iqr = q3 - q1
                        lower_bound = q1 - 1.5 * iqr
                        upper_bound = q3 + 1.5 * iqr
                        
                        outliers_count = len(values[(values < lower_bound) | (values > upper_bound)])
                        outliers[col] = {
                            "count": outliers_count,
                            "percentage": (outliers_count / len(values)) * 100,
                            "bounds": [lower_bound, upper_bound]
                        }
            
            self.results["outliers"]["chart_4_volume_profile"] = outliers
            
        except Exception as e:
            print(f"    ❌ Erreur analyse outliers Chart 4: {e}")
    
    def _scan_chart8_outliers(self):
        """Scanner les outliers Chart 8 (VIX)"""
        file_path = self.data_path / "chart_8_vix_20250912.jsonl"
        if not file_path.exists():
            return
            
        try:
            data = []
            with open(file_path, 'r') as f:
                for line in f:
                    try:
                        record = json.loads(line.strip())
                        if record.get('type') == 'vix':
                            data.append(record)
                    except:
                        continue
            
            if not data:
                return
                
            df = pd.DataFrame(data)
            
            if 'last' in df.columns:
                vix_values = pd.to_numeric(df['last'], errors='coerce')
                
                # VIX devrait être entre 5 et 150
                valid_range = (vix_values >= 5) & (vix_values <= 150)
                outliers_count = len(vix_values[~valid_range])
                
                outliers = {
                    "vix": {
                        "count": outliers_count,
                        "percentage": (outliers_count / len(vix_values)) * 100,
                        "valid_range": [5, 150],
                        "min_value": vix_values.min(),
                        "max_value": vix_values.max()
                    }
                }
                
                self.results["outliers"]["chart_8_vix"] = outliers
                
        except Exception as e:
            print(f"    ❌ Erreur analyse outliers Chart 8: {e}")
    
    def _scan_chart10_outliers(self):
        """Scanner les outliers Chart 10 (MenthorQ)"""
        file_path = self.data_path / "chart_10_menthorq_20250912.jsonl"
        if not file_path.exists():
            return
            
        try:
            data = []
            with open(file_path, 'r') as f:
                for line in f:
                    try:
                        record = json.loads(line.strip())
                        data.append(record)
                    except:
                        continue
            
            if not data:
                return
                
            df = pd.DataFrame(data)
            
            # Analyser les prix des niveaux MenthorQ
            if 'price' in df.columns:
                prices = pd.to_numeric(df['price'], errors='coerce')
                prices = prices.dropna()
                
                if len(prices) > 0:
                    # Les prix ES devraient être dans une plage raisonnable
                    es_range = (prices >= 6000) & (prices <= 7000)
                    outliers_count = len(prices[~es_range])
                    
                    outliers = {
                        "price": {
                            "count": outliers_count,
                            "percentage": (outliers_count / len(prices)) * 100,
                            "expected_range": [6000, 7000],
                            "min_value": prices.min(),
                            "max_value": prices.max()
                        }
                    }
                    
                    self.results["outliers"]["chart_10_menthorq"] = outliers
            
        except Exception as e:
            print(f"    ❌ Erreur analyse outliers Chart 10: {e}")
    
    def scan_menthorq_anomalies(self):
        """Scanner les anomalies spécifiques MenthorQ"""
        print("  🔍 Analyse des anomalies MenthorQ...")
        
        file_path = self.data_path / "chart_10_menthorq_20250912.jsonl"
        if not file_path.exists():
            print("    ⚠️  Fichier MenthorQ manquant")
            return
            
        try:
            data = []
            with open(file_path, 'r') as f:
                for line in f:
                    try:
                        record = json.loads(line.strip())
                        data.append(record)
                    except:
                        continue
            
            if not data:
                print("    ⚠️  Aucune donnée MenthorQ trouvée")
                return
                
            df = pd.DataFrame(data)
            
            anomalies = {}
            
            # 1. Données manquantes
            missing_data = {}
            for col in ['sym', 'level_type', 'price', 'subgraph', 'study_id', 'bar']:
                if col in df.columns:
                    missing_count = df[col].isna().sum()
                    missing_data[col] = {
                        "count": missing_count,
                        "percentage": (missing_count / len(df)) * 100
                    }
            
            anomalies["missing_data"] = missing_data
            
            # 2. Types de niveaux incohérents
            if 'level_type' in df.columns:
                level_types = df['level_type'].value_counts()
                anomalies["level_types"] = level_types.to_dict()
            
            # 3. Prix incohérents
            if 'price' in df.columns:
                prices = pd.to_numeric(df['price'], errors='coerce')
                prices = prices.dropna()
                
                if len(prices) > 0:
                    anomalies["price_stats"] = {
                        "count": len(prices),
                        "min": prices.min(),
                        "max": prices.max(),
                        "mean": prices.mean(),
                        "std": prices.std()
                    }
            
            self.results["menthorq_anomalies"] = anomalies
            
        except Exception as e:
            print(f"    ❌ Erreur analyse anomalies MenthorQ: {e}")
    
    def scan_synchronization_issues(self):
        """Scanner les problèmes de synchronisation entre charts"""
        print("  🔍 Analyse de la synchronisation entre charts...")
        
        # Comparer les timestamps entre charts
        charts_data = {}
        
        for chart_id in [3, 4, 8, 10]:
            files = {
                3: "chart_3_basedata_20250912.jsonl",
                4: "chart_4_ohlc_20250912.jsonl", 
                8: "chart_8_vix_20250912.jsonl",
                10: "chart_10_menthorq_20250912.jsonl"
            }
            
            file_path = self.data_path / files[chart_id]
            if file_path.exists():
                timestamps = []
                with open(file_path, 'r') as f:
                    for line in f:
                        try:
                            record = json.loads(line.strip())
                            if 't' in record:
                                timestamps.append(float(record['t']))
                        except:
                            continue
                
                if timestamps:
                    charts_data[chart_id] = {
                        "min_ts": min(timestamps),
                        "max_ts": max(timestamps),
                        "count": len(timestamps)
                    }
        
        # Analyser les décalages temporels
        sync_issues = {}
        if len(charts_data) > 1:
            base_chart = 3  # Chart 3 comme référence
            if base_chart in charts_data:
                base_min = charts_data[base_chart]["min_ts"]
                base_max = charts_data[base_chart]["max_ts"]
                
                for chart_id, data in charts_data.items():
                    if chart_id != base_chart:
                        time_diff_min = data["min_ts"] - base_min
                        time_diff_max = data["max_ts"] - base_max
                        
                        sync_issues[f"chart_{chart_id}_vs_chart_{base_chart}"] = {
                            "start_offset_seconds": time_diff_min,
                            "end_offset_seconds": time_diff_max,
                            "data_count": data["count"]
                        }
        
        self.results["synchronization_issues"] = sync_issues
    
    def scan_data_consistency(self):
        """Scanner la cohérence des données"""
        print("  🔍 Analyse de la cohérence des données...")
        
        consistency_issues = {}
        
        # 1. Vérifier la cohérence VAH/POC/VAL
        self._check_vah_poc_val_consistency(consistency_issues)
        
        # 2. Vérifier la cohérence VWAP vs prix
        self._check_vwap_price_consistency(consistency_issues)
        
        # 3. Vérifier la cohérence des volumes
        self._check_volume_consistency(consistency_issues)
        
        self.results["data_consistency"] = consistency_issues
    
    def _check_vah_poc_val_consistency(self, issues: Dict):
        """Vérifier la cohérence VAH/POC/VAL"""
        file_path = self.data_path / "chart_4_volume_profile_20250912.jsonl"
        if not file_path.exists():
            return
            
        try:
            data = []
            with open(file_path, 'r') as f:
                for line in f:
                    try:
                        record = json.loads(line.strip())
                        data.append(record)
                    except:
                        continue
            
            if not data:
                return
                
            df = pd.DataFrame(data)
            
            # Vérifier VAL ≤ POC ≤ VAH
            violations = 0
            total_records = 0
            
            for _, row in df.iterrows():
                try:
                    val = float(row.get('val', 0))
                    poc = float(row.get('vpoc', 0))
                    vah = float(row.get('vah', 0))
                    
                    if val > 0 and poc > 0 and vah > 0:
                        total_records += 1
                        if not (val <= poc <= vah):
                            violations += 1
                except:
                    continue
            
            if total_records > 0:
                issues["vah_poc_val"] = {
                    "violations": violations,
                    "total_records": total_records,
                    "violation_rate": (violations / total_records) * 100
                }
                
        except Exception as e:
            print(f"    ❌ Erreur vérification VAH/POC/VAL: {e}")
    
    def _check_vwap_price_consistency(self, issues: Dict):
        """Vérifier la cohérence VWAP vs prix"""
        # Charger les données VWAP
        vwap_file = self.data_path / "chart_3_vwap_20250912.jsonl"
        basedata_file = self.data_path / "chart_3_basedata_20250912.jsonl"
        
        if not vwap_file.exists() or not basedata_file.exists():
            return
            
        try:
            # Charger VWAP
            vwap_data = []
            with open(vwap_file, 'r') as f:
                for line in f:
                    try:
                        record = json.loads(line.strip())
                        if record.get('type') == 'vwap':
                            vwap_data.append(record)
                    except:
                        continue
            
            # Charger BaseData
            basedata = []
            with open(basedata_file, 'r') as f:
                for line in f:
                    try:
                        record = json.loads(line.strip())
                        if record.get('type') == 'basedata':
                            basedata.append(record)
                    except:
                        continue
            
            if not vwap_data or not basedata:
                return
                
            # Analyser la cohérence
            vwap_df = pd.DataFrame(vwap_data)
            base_df = pd.DataFrame(basedata)
            
            # Fusionner sur l'index
            merged = pd.merge(vwap_df, base_df, on='i', how='inner')
            
            if len(merged) > 0:
                vwap_values = pd.to_numeric(merged['v'], errors='coerce')
                price_values = pd.to_numeric(merged['c'], errors='coerce')
                
                # VWAP ne devrait pas être trop éloigné du prix
                price_diff = abs(vwap_values - price_values)
                price_ratio = price_diff / price_values
                
                # Seuil de 5% d'écart
                threshold = 0.05
                outliers = len(price_ratio[price_ratio > threshold])
                
                issues["vwap_price"] = {
                    "outliers": outliers,
                    "total_records": len(merged),
                    "outlier_rate": (outliers / len(merged)) * 100,
                    "max_deviation": price_ratio.max() * 100
                }
                
        except Exception as e:
            print(f"    ❌ Erreur vérification VWAP/prix: {e}")
    
    def _check_volume_consistency(self, issues: Dict):
        """Vérifier la cohérence des volumes"""
        file_path = self.data_path / "chart_3_basedata_20250912.jsonl"
        if not file_path.exists():
            return
            
        try:
            data = []
            with open(file_path, 'r') as f:
                for line in f:
                    try:
                        record = json.loads(line.strip())
                        if record.get('type') == 'basedata':
                            data.append(record)
                    except:
                        continue
            
            if not data:
                return
                
            df = pd.DataFrame(data)
            
            # Vérifier que bidvol + askvol ≈ total volume
            if 'bidvol' in df.columns and 'askvol' in df.columns and 'v' in df.columns:
                bidvol = pd.to_numeric(df['bidvol'], errors='coerce')
                askvol = pd.to_numeric(df['askvol'], errors='coerce')
                total_vol = pd.to_numeric(df['v'], errors='coerce')
                
                # Calculer la différence
                vol_sum = bidvol + askvol
                vol_diff = abs(vol_sum - total_vol)
                vol_ratio = vol_diff / total_vol
                
                # Seuil de 10% d'écart
                threshold = 0.1
                outliers = len(vol_ratio[vol_ratio > threshold])
                
                issues["volume_consistency"] = {
                    "outliers": outliers,
                    "total_records": len(df),
                    "outlier_rate": (outliers / len(df)) * 100,
                    "max_deviation": vol_ratio.max() * 100
                }
                
        except Exception as e:
            print(f"    ❌ Erreur vérification volumes: {e}")
    
    def generate_summary(self):
        """Générer un résumé des problèmes détectés"""
        print("  📊 Génération du résumé...")
        
        summary = {
            "total_issues": 0,
            "critical_issues": [],
            "warnings": [],
            "recommendations": []
        }
        
        # Analyser les gaps
        for chart, files in self.results["gaps"].items():
            for file, gaps in files.items():
                if gaps["max_gap_seconds"] > 60:
                    summary["critical_issues"].append(f"Gap critique {gaps['max_gap_seconds']}s dans {file}")
                elif gaps["max_gap_seconds"] > 30:
                    summary["warnings"].append(f"Gap important {gaps['max_gap_seconds']}s dans {file}")
        
        # Analyser les outliers
        for chart, outliers in self.results["outliers"].items():
            for col, data in outliers.items():
                if data["percentage"] > 10:
                    summary["critical_issues"].append(f"Trop d'outliers {data['percentage']:.1f}% dans {chart}.{col}")
                elif data["percentage"] > 5:
                    summary["warnings"].append(f"Outliers élevés {data['percentage']:.1f}% dans {chart}.{col}")
        
        # Analyser les anomalies MenthorQ
        if "menthorq_anomalies" in self.results:
            missing_data = self.results["menthorq_anomalies"].get("missing_data", {})
            for col, data in missing_data.items():
                if data["percentage"] > 50:
                    summary["critical_issues"].append(f"Données manquantes critiques {data['percentage']:.1f}% dans MenthorQ.{col}")
        
        # Analyser la cohérence
        for check, data in self.results["data_consistency"].items():
            if "violation_rate" in data and data["violation_rate"] > 10:
                summary["critical_issues"].append(f"Violations de cohérence {data['violation_rate']:.1f}% dans {check}")
        
        summary["total_issues"] = len(summary["critical_issues"]) + len(summary["warnings"])
        
        # Générer des recommandations
        if summary["critical_issues"]:
            summary["recommendations"].append("🔧 CORRECTION URGENTE REQUISE - Problèmes critiques détectés")
        if summary["warnings"]:
            summary["recommendations"].append("⚠️  AMÉLIORATION RECOMMANDÉE - Problèmes mineurs détectés")
        
        summary["recommendations"].extend([
            "📊 Implémenter un système de monitoring en temps réel",
            "🔄 Ajouter un système de reconnection automatique Sierra Chart",
            "🛡️  Mettre en place des filtres de validation des données",
            "📈 Créer un dashboard de qualité des données"
        ])
        
        self.results["summary"] = summary
    
    def save_report(self, output_file: str = "data_quality_scan_report.json"):
        """Sauvegarder le rapport"""
        output_path = self.data_path / output_file
        with open(output_path, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        
        print(f"\n✅ Rapport sauvegardé: {output_path}")
        
        # Afficher le résumé
        summary = self.results["summary"]
        print(f"\n📊 RÉSUMÉ DU SCAN:")
        print(f"   Total d'issues: {summary['total_issues']}")
        print(f"   Issues critiques: {len(summary['critical_issues'])}")
        print(f"   Warnings: {len(summary['warnings'])}")
        
        if summary["critical_issues"]:
            print(f"\n🚨 ISSUES CRITIQUES:")
            for issue in summary["critical_issues"]:
                print(f"   • {issue}")
        
        if summary["warnings"]:
            print(f"\n⚠️  WARNINGS:")
            for warning in summary["warnings"]:
                print(f"   • {warning}")
        
        if summary["recommendations"]:
            print(f"\n💡 RECOMMANDATIONS:")
            for rec in summary["recommendations"]:
                print(f"   • {rec}")

def main():
    """Fonction principale"""
    scanner = DataQualityScanner()
    results = scanner.scan_all_data()
    scanner.save_report()
    
    return results

if __name__ == "__main__":
    main()


