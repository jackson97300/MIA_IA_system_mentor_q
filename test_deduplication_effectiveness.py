#!/usr/bin/env python3
"""
🧪 TEST DÉDUPLICATION EFFECTIVENESS
===================================

Script pour tester l'efficacité de la déduplication à la source
- Analyse des fichiers de sortie après correction
- Calcul du taux de déduplication
- Vérification de la cohérence des données
"""

import json
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
from collections import defaultdict
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DeduplicationTester:
    """Testeur d'efficacité de la déduplication"""
    
    def __init__(self, data_dir: str = "D:\\MIA_IA_system"):
        self.data_dir = Path(data_dir)
        self.results = {}
        
    def analyze_file_deduplication(self, file_path: Path) -> dict:
        """Analyser la déduplication dans un fichier"""
        
        if not file_path.exists():
            return {"error": "Fichier non trouvé"}
        
        logger.info(f"📊 Analyse de {file_path.name}")
        
        # Lire le fichier
        data = []
        with open(file_path, 'r') as f:
            for line_num, line in enumerate(f, 1):
                try:
                    record = json.loads(line.strip())
                    data.append(record)
                except json.JSONDecodeError as e:
                    logger.warning(f"Ligne {line_num} invalide: {e}")
                    continue
        
        if not data:
            return {"error": "Aucune donnée valide"}
        
        # Convertir en DataFrame
        df = pd.DataFrame(data)
        
        # Analyser les doublons
        total_records = len(df)
        
        # Clé de déduplication : (t, i) ou (timestamp, index)
        if 't' in df.columns and 'i' in df.columns:
            # Nouveau format avec alias Sierra
            df['dedup_key'] = df['t'].astype(str) + '_' + df['i'].astype(str)
        elif 'timestamp' in df.columns and 'index' in df.columns:
            # Ancien format
            df['dedup_key'] = df['timestamp'].astype(str) + '_' + df['index'].astype(str)
        else:
            # Fallback : utiliser toutes les colonnes numériques
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) > 0:
                df['dedup_key'] = df[numeric_cols].astype(str).agg('_'.join, axis=1)
            else:
                return {"error": "Impossible de créer une clé de déduplication"}
        
        # Compter les doublons
        unique_records = df['dedup_key'].nunique()
        duplicate_records = total_records - unique_records
        duplication_rate = (duplicate_records / total_records * 100) if total_records > 0 else 0
        
        # Analyser les patterns de doublons
        duplicate_counts = df['dedup_key'].value_counts()
        max_duplicates = duplicate_counts.max() if len(duplicate_counts) > 0 else 0
        
        # Analyser la cohérence temporelle
        time_consistency = self._analyze_time_consistency(df)
        
        # Analyser la cohérence des valeurs
        value_consistency = self._analyze_value_consistency(df)
        
        return {
            "file_name": file_path.name,
            "total_records": total_records,
            "unique_records": unique_records,
            "duplicate_records": duplicate_records,
            "duplication_rate": duplication_rate,
            "max_duplicates": max_duplicates,
            "time_consistency": time_consistency,
            "value_consistency": value_consistency,
            "dedup_key_sample": df['dedup_key'].head(3).tolist()
        }
    
    def _analyze_time_consistency(self, df: pd.DataFrame) -> dict:
        """Analyser la cohérence temporelle"""
        
        if 't' not in df.columns:
            return {"error": "Pas de colonne timestamp"}
        
        # Vérifier la monotonie
        timestamps = df['t'].sort_values()
        time_diffs = timestamps.diff().dropna()
        
        # Détecter les gaps temporels
        gap_threshold = 5.0  # 5 secondes
        gaps = time_diffs[time_diffs > gap_threshold]
        
        return {
            "monotonic": timestamps.is_monotonic_increasing,
            "total_gaps": len(gaps),
            "max_gap_seconds": gaps.max() if len(gaps) > 0 else 0,
            "avg_gap_seconds": gaps.mean() if len(gaps) > 0 else 0,
            "min_interval_seconds": time_diffs.min() if len(time_diffs) > 0 else 0,
            "max_interval_seconds": time_diffs.max() if len(time_diffs) > 0 else 0
        }
    
    def _analyze_value_consistency(self, df: pd.DataFrame) -> dict:
        """Analyser la cohérence des valeurs"""
        
        # Analyser les colonnes numériques
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        consistency = {}
        
        for col in numeric_cols:
            if col in ['t', 'i', 'chart']:  # Ignorer les colonnes de métadonnées
                continue
                
            values = df[col].dropna()
            if len(values) == 0:
                continue
                
            # Détecter les valeurs aberrantes
            q1 = values.quantile(0.25)
            q3 = values.quantile(0.75)
            iqr = q3 - q1
            lower_bound = q1 - 1.5 * iqr
            upper_bound = q3 + 1.5 * iqr
            
            outliers = values[(values < lower_bound) | (values > upper_bound)]
            
            consistency[col] = {
                "count": len(values),
                "outliers": len(outliers),
                "outlier_rate": len(outliers) / len(values) * 100 if len(values) > 0 else 0,
                "min": values.min(),
                "max": values.max(),
                "mean": values.mean(),
                "std": values.std()
            }
        
        return consistency
    
    def test_all_files(self) -> dict:
        """Tester tous les fichiers de données"""
        
        logger.info("🚀 Démarrage du test de déduplication")
        
        # Chercher tous les fichiers JSONL
        jsonl_files = list(self.data_dir.glob("chart_*_*.jsonl"))
        
        if not jsonl_files:
            logger.error("❌ Aucun fichier JSONL trouvé")
            return {"error": "Aucun fichier trouvé"}
        
        logger.info(f"📁 {len(jsonl_files)} fichiers trouvés")
        
        # Analyser chaque fichier
        for file_path in jsonl_files:
            try:
                result = self.analyze_file_deduplication(file_path)
                self.results[file_path.name] = result
                
                # Log du résultat
                if "error" in result:
                    logger.error(f"❌ {file_path.name}: {result['error']}")
                else:
                    logger.info(f"✅ {file_path.name}: {result['duplication_rate']:.1f}% de doublons")
                    
            except Exception as e:
                logger.error(f"❌ Erreur analyse {file_path.name}: {e}")
                self.results[file_path.name] = {"error": str(e)}
        
        # Calculer les statistiques globales
        global_stats = self._calculate_global_stats()
        
        return {
            "files_analyzed": len(jsonl_files),
            "global_stats": global_stats,
            "file_results": self.results
        }
    
    def _calculate_global_stats(self) -> dict:
        """Calculer les statistiques globales"""
        
        valid_results = [r for r in self.results.values() if "error" not in r]
        
        if not valid_results:
            return {"error": "Aucun résultat valide"}
        
        total_records = sum(r["total_records"] for r in valid_results)
        total_duplicates = sum(r["duplicate_records"] for r in valid_results)
        global_duplication_rate = (total_duplicates / total_records * 100) if total_records > 0 else 0
        
        # Statistiques par chart
        chart_stats = defaultdict(lambda: {"files": 0, "total_records": 0, "duplicates": 0})
        
        for result in valid_results:
            file_name = result["file_name"]
            # Extraire le numéro de chart du nom de fichier
            if "chart_" in file_name:
                chart_num = file_name.split("_")[1]
                chart_stats[chart_num]["files"] += 1
                chart_stats[chart_num]["total_records"] += result["total_records"]
                chart_stats[chart_num]["duplicates"] += result["duplicate_records"]
        
        # Calculer les taux par chart
        for chart_num, stats in chart_stats.items():
            if stats["total_records"] > 0:
                stats["duplication_rate"] = stats["duplicates"] / stats["total_records"] * 100
            else:
                stats["duplication_rate"] = 0
        
        return {
            "total_records": total_records,
            "total_duplicates": total_duplicates,
            "global_duplication_rate": global_duplication_rate,
            "chart_stats": dict(chart_stats),
            "files_with_issues": len([r for r in self.results.values() if "error" in r]),
            "files_analyzed": len(valid_results)
        }
    
    def generate_report(self) -> str:
        """Générer un rapport détaillé"""
        
        if not self.results:
            return "❌ Aucun résultat à reporter"
        
        report = []
        report.append("🧪 RAPPORT DE TEST DE DÉDUPLICATION")
        report.append("=" * 50)
        report.append(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # Statistiques globales
        if "global_stats" in self.results:
            global_stats = self.results["global_stats"]
            if "error" not in global_stats:
                report.append("📊 STATISTIQUES GLOBALES")
                report.append("-" * 30)
                report.append(f"Fichiers analysés: {global_stats['files_analyzed']}")
                report.append(f"Total enregistrements: {global_stats['total_records']:,}")
                report.append(f"Total doublons: {global_stats['total_duplicates']:,}")
                report.append(f"Taux de duplication global: {global_stats['global_duplication_rate']:.2f}%")
                report.append("")
                
                # Statistiques par chart
                if "chart_stats" in global_stats:
                    report.append("📈 STATISTIQUES PAR CHART")
                    report.append("-" * 30)
                    for chart_num, stats in global_stats["chart_stats"].items():
                        report.append(f"Chart {chart_num}:")
                        report.append(f"  Fichiers: {stats['files']}")
                        report.append(f"  Enregistrements: {stats['total_records']:,}")
                        report.append(f"  Doublons: {stats['duplicates']:,}")
                        report.append(f"  Taux: {stats['duplication_rate']:.2f}%")
                        report.append("")
        
        # Détails par fichier
        report.append("📁 DÉTAILS PAR FICHIER")
        report.append("-" * 30)
        
        for file_name, result in self.results.items():
            if "error" in result:
                report.append(f"❌ {file_name}: {result['error']}")
            else:
                report.append(f"✅ {file_name}:")
                report.append(f"  Enregistrements: {result['total_records']:,}")
                report.append(f"  Uniques: {result['unique_records']:,}")
                report.append(f"  Doublons: {result['duplicate_records']:,}")
                report.append(f"  Taux: {result['duplication_rate']:.2f}%")
                report.append(f"  Max doublons: {result['max_duplicates']}")
                
                # Cohérence temporelle
                if "time_consistency" in result and "error" not in result["time_consistency"]:
                    tc = result["time_consistency"]
                    report.append(f"  Gaps temporels: {tc['total_gaps']}")
                    if tc['max_gap_seconds'] > 0:
                        report.append(f"  Max gap: {tc['max_gap_seconds']:.2f}s")
                
                report.append("")
        
        return "\n".join(report)
    
    def save_results(self, output_file: str = "deduplication_test_results.json"):
        """Sauvegarder les résultats"""
        
        output_path = self.data_dir / output_file
        
        with open(output_path, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        
        logger.info(f"💾 Résultats sauvegardés dans {output_path}")

def main():
    """Fonction principale"""
    
    # Créer le testeur
    tester = DeduplicationTester()
    
    # Exécuter les tests
    results = tester.test_all_files()
    
    # Générer le rapport
    report = tester.generate_report()
    print(report)
    
    # Sauvegarder les résultats
    tester.save_results()
    
    # Sauvegarder le rapport
    report_path = tester.data_dir / "deduplication_test_report.txt"
    with open(report_path, 'w') as f:
        f.write(report)
    
    logger.info(f"📄 Rapport sauvegardé dans {report_path}")

if __name__ == "__main__":
    main()


