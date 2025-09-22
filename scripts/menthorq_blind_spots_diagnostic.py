#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de diagnostic et test pour les MenthorQ Blind Spots Levels
Chart 10 - Focus sur l'étude ID 3
"""

import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import glob

class MenthorQBlindSpotsDiagnostic:
    def __init__(self, chart_number: int = 10):
        self.chart_number = chart_number
        self.blind_spots_study_id = 3
        self.gamma_study_id = 1
        self.correlation_study_id = 4
        
    def analyze_menthorq_file(self, file_path: str) -> Dict:
        """Analyse un fichier JSONL MenthorQ et extrait les statistiques"""
        stats = {
            'total_lines': 0,
            'menthorq_levels': 0,
            'menthorq_diag': 0,
            'correlation': 0,
            'blind_spots': 0,
            'gamma_levels': 0,
            'study_ids': {},
            'level_types': {},
            'timestamps': [],
            'errors': []
        }
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line:
                        continue
                        
                    stats['total_lines'] += 1
                    
                    try:
                        data = json.loads(line)
                        stats['timestamps'].append(data.get('t', 0))
                        
                        # Analyser par type
                        msg_type = data.get('type', '')
                        if msg_type == 'menthorq_level':
                            stats['menthorq_levels'] += 1
                            study_id = data.get('study_id', 0)
                            level_type = data.get('level_type', '')
                            
                            # Compter par study_id
                            if study_id not in stats['study_ids']:
                                stats['study_ids'][study_id] = 0
                            stats['study_ids'][study_id] += 1
                            
                            # Compter par level_type
                            if level_type not in stats['level_types']:
                                stats['level_types'][level_type] = 0
                            stats['level_types'][level_type] += 1
                            
                            # Blind Spots spécifiques
                            if study_id == self.blind_spots_study_id:
                                stats['blind_spots'] += 1
                            elif study_id == self.gamma_study_id:
                                stats['gamma_levels'] += 1
                                
                        elif msg_type == 'menthorq_diag':
                            stats['menthorq_diag'] += 1
                            
                        elif msg_type == 'correlation':
                            stats['correlation'] += 1
                            
                    except json.JSONDecodeError as e:
                        stats['errors'].append(f"Ligne {line_num}: JSON invalide - {e}")
                        
        except FileNotFoundError:
            stats['errors'].append(f"Fichier non trouvé: {file_path}")
        except Exception as e:
            stats['errors'].append(f"Erreur lors de la lecture: {e}")
            
        return stats
    
    def find_latest_menthorq_file(self) -> Optional[str]:
        """Trouve le fichier MenthorQ le plus récent pour le chart"""
        pattern = f"chart_{self.chart_number}_menthorq_*.jsonl"
        files = glob.glob(pattern)
        
        if not files:
            return None
            
        # Trier par date de modification
        files.sort(key=os.path.getmtime, reverse=True)
        return files[0]
    
    def generate_blind_spots_test_data(self, count: int = 10) -> List[Dict]:
        """Génère des données de test pour les Blind Spots"""
        test_data = []
        base_time = 45917.700000  # Timestamp de base
        base_price = 6650.0
        
        for i in range(count):
            timestamp = base_time + (i * 0.001)  # Incrément de 1ms
            
            blind_spot_data = {
                "t": timestamp,
                "sym": "ESZ25_FUT_CME",
                "type": "menthorq_level",
                "level_type": f"blind_spot_{i+1}",
                "price": base_price + (i * 5.0),  # Prix incrémental
                "subgraph": i,
                "study_id": self.blind_spots_study_id,
                "i": 14600 + i,
                "chart": self.chart_number
            }
            test_data.append(blind_spot_data)
            
        return test_data
    
    def write_test_file(self, test_data: List[Dict], filename: str = None) -> str:
        """Écrit les données de test dans un fichier"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"chart_{self.chart_number}_blind_spots_test_{timestamp}.jsonl"
            
        with open(filename, 'w', encoding='utf-8') as f:
            for data in test_data:
                f.write(json.dumps(data) + '\n')
                
        return filename
    
    def check_sierra_config(self) -> Dict:
        """Vérifie la configuration Sierra attendue"""
        config = {
            'chart_number': self.chart_number,
            'required_studies': {
                'MenthorQ Gamma Levels': {
                    'study_id': self.gamma_study_id,
                    'subgraphs_count': 19,
                    'status': 'unknown'
                },
                'MenthorQ Blind Spots Levels': {
                    'study_id': self.blind_spots_study_id,
                    'subgraphs_count': 10,
                    'status': 'unknown'
                },
                'Correlation Coefficient': {
                    'study_id': self.correlation_study_id,
                    'subgraphs_count': 1,
                    'status': 'unknown'
                }
            },
            'dumper_config': {
                'export_menthorq': 1,
                'gamma_study_id': self.gamma_study_id,
                'blind_spots_study_id': self.blind_spots_study_id,
                'correlation_study_id': self.correlation_study_id,
                'on_new_bar_only': 1,
                'blind_spots_emit_last_non_zero': 0,
                'debug_mode': 1
            }
        }
        return config
    
    def print_diagnostic_report(self, stats: Dict):
        """Affiche un rapport de diagnostic complet"""
        print("=" * 80)
        print(f"DIAGNOSTIC MENTHORQ BLIND SPOTS - CHART {self.chart_number}")
        print("=" * 80)
        
        print(f"\n📊 STATISTIQUES GÉNÉRALES:")
        print(f"   Total lignes: {stats['total_lines']}")
        print(f"   MenthorQ Levels: {stats['menthorq_levels']}")
        print(f"   Diagnostics: {stats['menthorq_diag']}")
        print(f"   Corrélations: {stats['correlation']}")
        
        print(f"\n🎯 BLIND SPOTS (Study ID {self.blind_spots_study_id}):")
        print(f"   Nombre d'événements: {stats['blind_spots']}")
        if stats['blind_spots'] == 0:
            print("   ❌ PROBLÈME: Aucun Blind Spot détecté!")
        else:
            print("   ✅ Blind Spots détectés")
            
        print(f"\n📈 GAMMA LEVELS (Study ID {self.gamma_study_id}):")
        print(f"   Nombre d'événements: {stats['gamma_levels']}")
        
        print(f"\n🔍 RÉPARTITION PAR STUDY ID:")
        for study_id, count in sorted(stats['study_ids'].items()):
            study_name = {
                1: "MenthorQ Gamma Levels",
                3: "MenthorQ Blind Spots Levels", 
                4: "Correlation Coefficient"
            }.get(study_id, f"Study ID {study_id}")
            print(f"   {study_id}: {count} événements ({study_name})")
            
        print(f"\n📋 TYPES DE NIVEAUX DÉTECTÉS:")
        for level_type, count in sorted(stats['level_types'].items()):
            print(f"   {level_type}: {count}")
            
        if stats['errors']:
            print(f"\n❌ ERREURS DÉTECTÉES:")
            for error in stats['errors']:
                print(f"   {error}")
                
        print(f"\n⏰ PÉRIODE:")
        if stats['timestamps']:
            min_time = min(stats['timestamps'])
            max_time = max(stats['timestamps'])
            print(f"   De: {min_time}")
            print(f"   À: {max_time}")
            
    def suggest_fixes(self, stats: Dict) -> List[str]:
        """Suggère des corrections basées sur l'analyse"""
        suggestions = []
        
        if stats['blind_spots'] == 0:
            suggestions.extend([
                "1. Vérifier que l'étude 'MenthorQ Blind Spots Levels' est présente sur le Chart 10",
                "2. S'assurer que le Study ID est configuré à 3 dans Sierra",
                "3. Vérifier que les 10 subgraphs BL1-BL10 ont des valeurs non nulles",
                "4. Activer 'Blind Spots Emit Last Non-Zero' dans le dumper G10",
                "5. Activer le mode Debug pour voir les détails internes"
            ])
            
        if stats['menthorq_diag'] > 10:
            suggestions.append("6. Le spam de diagnostics indique des valeurs manquantes - vérifier la configuration des études")
            
        if stats['gamma_levels'] == 0:
            suggestions.append("7. Aucun niveau Gamma détecté - vérifier l'étude MenthorQ Gamma Levels")
            
        return suggestions

def main():
    """Fonction principale"""
    print("🔍 DIAGNOSTIC MENTHORQ BLIND SPOTS LEVELS")
    print("=" * 50)
    
    diagnostic = MenthorQBlindSpotsDiagnostic(chart_number=10)
    
    # 1. Trouver le fichier le plus récent
    latest_file = diagnostic.find_latest_menthorq_file()
    if not latest_file:
        print("❌ Aucun fichier MenthorQ trouvé pour le Chart 10")
        return
        
    print(f"📁 Fichier analysé: {latest_file}")
    
    # 2. Analyser le fichier
    stats = diagnostic.analyze_menthorq_file(latest_file)
    
    # 3. Afficher le rapport
    diagnostic.print_diagnostic_report(stats)
    
    # 4. Suggestions
    suggestions = diagnostic.suggest_fixes(stats)
    if suggestions:
        print(f"\n💡 SUGGESTIONS DE CORRECTION:")
        for suggestion in suggestions:
            print(f"   {suggestion}")
    
    # 5. Configuration attendue
    config = diagnostic.check_sierra_config()
    print(f"\n⚙️ CONFIGURATION SIERRA ATTENDUE:")
    print(f"   Chart: {config['chart_number']}")
    for study_name, study_config in config['required_studies'].items():
        print(f"   {study_name}: ID {study_config['study_id']}, {study_config['subgraphs_count']} subgraphs")
    
    # 6. Option de génération de test
    if stats['blind_spots'] == 0:
        print(f"\n🧪 GÉNÉRATION DE DONNÉES DE TEST:")
        response = input("Voulez-vous générer un fichier de test pour les Blind Spots? (o/n): ")
        if response.lower() in ['o', 'oui', 'y', 'yes']:
            test_data = diagnostic.generate_blind_spots_test_data()
            test_file = diagnostic.write_test_file(test_data)
            print(f"✅ Fichier de test créé: {test_file}")
            print("   Vous pouvez l'utiliser pour tester votre pipeline de traitement")

if __name__ == "__main__":
    main()



