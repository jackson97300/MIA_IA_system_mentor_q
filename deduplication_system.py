#!/usr/bin/env python3
"""
Système de déduplication robuste pour les données MIA
Résout les 90.6% de doublons détectés dans les données
"""

import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import glob
import os
import hashlib
from typing import Dict, List, Tuple, Optional, Set
from collections import defaultdict

class MIADeduplicationSystem:
    def __init__(self, data_dir: str = "."):
        self.data_dir = data_dir
        self.deduplication_stats = {}
        
    def generate_deduplication_key(self, record: Dict) -> str:
        """Génère une clé de déduplication robuste"""
        # Clé primaire : symbol + timestamp + type
        primary_key = f"{record.get('sym', '')}_{record.get('t', 0)}_{record.get('type', '')}"
        
        # Clé secondaire basée sur le contenu pour les données identiques
        content_fields = []
        
        # Champs spécifiques selon le type de données
        if record.get('type') == 'basedata':
            content_fields = ['o', 'h', 'l', 'c', 'v', 'bidvol', 'askvol']
        elif record.get('type') == 'vwap':
            content_fields = ['v', 'up1', 'dn1', 'up2', 'dn2', 'up3', 'dn3']
        elif record.get('type') == 'volume_profile':
            content_fields = ['vpoc', 'vah', 'val']
        elif record.get('type') == 'nbcv':
            content_fields = ['ask', 'bid', 'delta', 'trades']
        elif record.get('type') == 'vix':
            content_fields = ['last']
        elif record.get('type') == 'menthorq':
            content_fields = ['level_type', 'price', 'gex', 'blind_spot']
        
        # Construire la clé de contenu
        content_values = []
        for field in content_fields:
            value = record.get(field, '')
            if isinstance(value, (int, float)):
                # Arrondir les valeurs numériques pour éviter les micro-différences
                content_values.append(f"{field}:{round(value, 6)}")
            else:
                content_values.append(f"{field}:{value}")
        
        content_key = "_".join(content_values)
        
        # Combiner les clés
        full_key = f"{primary_key}_{hashlib.md5(content_key.encode()).hexdigest()[:8]}"
        
        return full_key
    
    def deduplicate_file(self, file_path: str, output_path: str = None) -> Dict:
        """Déduplique un fichier JSONL"""
        print(f"🔍 Déduplication de {os.path.basename(file_path)}...")
        
        if output_path is None:
            output_path = file_path.replace('.jsonl', '_deduplicated.jsonl')
        
        seen_keys = set()
        duplicates_count = 0
        total_count = 0
        valid_count = 0
        
        with open(file_path, 'r', encoding='utf-8') as infile, \
             open(output_path, 'w', encoding='utf-8') as outfile:
            
            for line_num, line in enumerate(infile, 1):
                total_count += 1
                
                try:
                    record = json.loads(line.strip())
                    
                    # Générer la clé de déduplication
                    dedup_key = self.generate_deduplication_key(record)
                    
                    if dedup_key not in seen_keys:
                        seen_keys.add(dedup_key)
                        outfile.write(line)
                        valid_count += 1
                    else:
                        duplicates_count += 1
                        
                except json.JSONDecodeError as e:
                    print(f"⚠️ Erreur JSON ligne {line_num}: {e}")
                    continue
                except Exception as e:
                    print(f"⚠️ Erreur ligne {line_num}: {e}")
                    continue
        
        # Statistiques
        duplicate_rate = (duplicates_count / total_count * 100) if total_count > 0 else 0
        
        stats = {
            'file': os.path.basename(file_path),
            'total_records': total_count,
            'duplicates': duplicates_count,
            'valid_records': valid_count,
            'duplicate_rate': duplicate_rate,
            'output_file': output_path
        }
        
        print(f"   📊 Total: {total_count:,} | Doublons: {duplicates_count:,} ({duplicate_rate:.1f}%) | Valides: {valid_count:,}")
        
        return stats
    
    def deduplicate_all_files(self, date_str: str = "20250912") -> Dict:
        """Déduplique tous les fichiers d'une date donnée"""
        print(f"🚀 DÉDUPLICATION COMPLÈTE - {date_str}")
        print("=" * 60)
        
        # Patterns de fichiers à dédupliquer
        patterns = [
            f"chart_3_*_{date_str}.jsonl",
            f"chart_4_*_{date_str}.jsonl", 
            f"chart_8_*_{date_str}.jsonl",
            f"chart_10_*_{date_str}.jsonl"
        ]
        
        all_stats = {}
        total_duplicates = 0
        total_records = 0
        
        for pattern in patterns:
            files = glob.glob(os.path.join(self.data_dir, pattern))
            
            for file_path in files:
                if '_deduplicated' in file_path:
                    continue  # Ignorer les fichiers déjà dédupliqués
                    
                stats = self.deduplicate_file(file_path)
                all_stats[stats['file']] = stats
                
                total_duplicates += stats['duplicates']
                total_records += stats['total_records']
        
        # Résumé global
        overall_duplicate_rate = (total_duplicates / total_records * 100) if total_records > 0 else 0
        
        summary = {
            'date': date_str,
            'total_files_processed': len(all_stats),
            'total_records': total_records,
            'total_duplicates': total_duplicates,
            'overall_duplicate_rate': overall_duplicate_rate,
            'file_stats': all_stats
        }
        
        print("\n" + "=" * 60)
        print("📋 RÉSUMÉ DÉDUPLICATION")
        print("=" * 60)
        print(f"📁 Fichiers traités: {len(all_stats)}")
        print(f"📊 Total enregistrements: {total_records:,}")
        print(f"🗑️ Total doublons: {total_duplicates:,}")
        print(f"📈 Taux de doublons: {overall_duplicate_rate:.1f}%")
        
        if overall_duplicate_rate > 50:
            print(f"❌ TAUX DE DOUBLONS CRITIQUE ({overall_duplicate_rate:.1f}%)")
        elif overall_duplicate_rate > 20:
            print(f"⚠️ TAUX DE DOUBLONS ÉLEVÉ ({overall_duplicate_rate:.1f}%)")
        else:
            print(f"✅ TAUX DE DOUBLONS ACCEPTABLE ({overall_duplicate_rate:.1f}%)")
        
        # Sauvegarder les statistiques
        with open(f'deduplication_report_{date_str}.json', 'w') as f:
            json.dump(summary, f, indent=2, default=str)
        
        print(f"\n💾 Rapport sauvegardé: deduplication_report_{date_str}.json")
        
        return summary
    
    def analyze_duplicate_patterns(self, date_str: str = "20250912") -> Dict:
        """Analyse les patterns de doublons pour identifier les causes"""
        print(f"\n🔍 ANALYSE DES PATTERNS DE DOUBLONS - {date_str}")
        print("=" * 60)
        
        patterns = [
            f"chart_3_*_{date_str}.jsonl",
            f"chart_4_*_{date_str}.jsonl",
            f"chart_8_*_{date_str}.jsonl", 
            f"chart_10_*_{date_str}.jsonl"
        ]
        
        analysis = {}
        
        for pattern in patterns:
            files = glob.glob(os.path.join(self.data_dir, pattern))
            
            for file_path in files:
                if '_deduplicated' in file_path:
                    continue
                    
                print(f"\n📄 Analyse: {os.path.basename(file_path)}")
                
                # Analyser les patterns de doublons
                timestamp_duplicates = defaultdict(int)
                content_duplicates = defaultdict(int)
                type_duplicates = defaultdict(int)
                
                seen_records = {}
                duplicate_samples = []
                
                with open(file_path, 'r', encoding='utf-8') as f:
                    for line_num, line in enumerate(f, 1):
                        try:
                            record = json.loads(line.strip())
                            
                            # Analyser par timestamp
                            timestamp = record.get('t', 0)
                            timestamp_duplicates[timestamp] += 1
                            
                            # Analyser par type
                            record_type = record.get('type', 'unknown')
                            type_duplicates[record_type] += 1
                            
                            # Analyser le contenu
                            content_key = self.generate_deduplication_key(record)
                            content_duplicates[content_key] += 1
                            
                            # Collecter des échantillons de doublons
                            if content_key in seen_records and len(duplicate_samples) < 5:
                                duplicate_samples.append({
                                    'line': line_num,
                                    'timestamp': timestamp,
                                    'type': record_type,
                                    'content_key': content_key[:20] + "...",
                                    'record': record
                                })
                            else:
                                seen_records[content_key] = record
                                
                        except Exception as e:
                            continue
                
                # Calculer les statistiques
                total_records = line_num
                unique_timestamps = len([t for t, count in timestamp_duplicates.items() if count > 1])
                unique_contents = len([c for c, count in content_duplicates.items() if count > 1])
                
                analysis[os.path.basename(file_path)] = {
                    'total_records': total_records,
                    'unique_timestamps': len(timestamp_duplicates),
                    'duplicate_timestamps': unique_timestamps,
                    'unique_contents': len(content_duplicates),
                    'duplicate_contents': unique_contents,
                    'timestamp_duplicate_rate': (unique_timestamps / len(timestamp_duplicates) * 100) if timestamp_duplicates else 0,
                    'content_duplicate_rate': (unique_contents / len(content_duplicates) * 100) if content_duplicates else 0,
                    'duplicate_samples': duplicate_samples
                }
                
                print(f"   📊 Enregistrements: {total_records:,}")
                print(f"   ⏰ Timestamps uniques: {len(timestamp_duplicates):,}")
                print(f"   🔄 Timestamps dupliqués: {unique_timestamps:,}")
                print(f"   📝 Contenus uniques: {len(content_duplicates):,}")
                print(f"   🗑️ Contenus dupliqués: {unique_contents:,}")
        
        return analysis
    
    def create_deduplication_recommendations(self, analysis: Dict) -> List[str]:
        """Crée des recommandations basées sur l'analyse des doublons"""
        recommendations = []
        
        for filename, stats in analysis.items():
            if stats['content_duplicate_rate'] > 50:
                recommendations.append(f"🚨 CRITIQUE - {filename}: {stats['content_duplicate_rate']:.1f}% de doublons de contenu")
            elif stats['content_duplicate_rate'] > 20:
                recommendations.append(f"⚠️ ÉLEVÉ - {filename}: {stats['content_duplicate_rate']:.1f}% de doublons de contenu")
            
            if stats['timestamp_duplicate_rate'] > 30:
                recommendations.append(f"⏰ TIMESTAMP - {filename}: {stats['timestamp_duplicate_rate']:.1f}% de timestamps dupliqués")
        
        # Recommandations générales
        recommendations.extend([
            "🔧 CORRECTIONS RECOMMANDÉES:",
            "  • Implémenter WriteIfChanged() dans tous les dumpeurs C++",
            "  • Ajouter une validation de contenu avant écriture",
            "  • Utiliser des clés de déduplication basées sur (symbol + timestamp + content_hash)",
            "  • Implémenter un buffer de données avec déduplication en temps réel",
            "  • Ajouter des logs de déduplication pour monitoring"
        ])
        
        return recommendations

def main():
    """Fonction principale"""
    deduplicator = MIADeduplicationSystem()
    
    # Déduplication complète
    summary = deduplicator.deduplicate_all_files("20250912")
    
    # Analyse des patterns
    analysis = deduplicator.analyze_duplicate_patterns("20250912")
    
    # Recommandations
    recommendations = deduplicator.create_deduplication_recommendations(analysis)
    
    print("\n" + "=" * 60)
    print("💡 RECOMMANDATIONS")
    print("=" * 60)
    for rec in recommendations:
        print(rec)
    
    # Sauvegarder l'analyse
    with open('duplicate_patterns_analysis_20250912.json', 'w') as f:
        json.dump(analysis, f, indent=2, default=str)
    
    print(f"\n💾 Analyse sauvegardée: duplicate_patterns_analysis_20250912.json")
    
    return 0

if __name__ == "__main__":
    exit(main())


