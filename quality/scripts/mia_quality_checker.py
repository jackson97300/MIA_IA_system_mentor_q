#!/usr/bin/env python3
"""
🛡️ MIA Quality Checker - Validation rapide des données
Version: 1.0
Date: 2025-01-05

Usage:
    python mia_quality_checker.py --file mia_unified_20250105.jsonl
    python mia_quality_checker.py --file chart_3_20250105.jsonl --quick
    python mia_quality_checker.py --monitor --watch-dir .
"""

import json
import argparse
import sys
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from pathlib import Path
import yaml

class MIAQualityChecker:
    def __init__(self, config_file: str = "mia_quality_config.yml"):
        self.config = self.load_config(config_file)
        self.metrics = {
            'total_messages': 0,
            'quarantined_messages': 0,
            'corrected_messages': 0,
            'tick_alignment_violations': 0,
            'quote_sanity_violations': 0,
            'dom_shape_violations': 0,
            'vwap_band_violations': 0,
            'nbcv_consistency_violations': 0,
            'vp_corrections': 0,
            'vix_alerts': 0,
            'spread_alerts': 0,
            'price_anomalies': 0,
            'time_monotonicity_violations': 0,
            'seq_gaps': 0
        }
        self.last_timestamps = {}
        self.last_sequences = {}
        
    def load_config(self, config_file: str) -> Dict:
        """Charge la configuration depuis le fichier YAML"""
        try:
            with open(config_file, 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            print(f"⚠️  Fichier de configuration {config_file} non trouvé, utilisation des valeurs par défaut")
            return self.get_default_config()
    
    def get_default_config(self) -> Dict:
        """Configuration par défaut si le fichier n'existe pas"""
        return {
            'price': {'max_value': 100000.0, 'tick_alignment_tolerance': 1e-9, 'min_value': 0.0},
            'quotes': {'max_spread_ticks': 4, 'spread_alert_window_seconds': 2.0},
            'vix': {'min_value': 5.0, 'max_value': 100.0},
            'nbcv': {'total_tolerance_percent': 5.0, 'delta_tolerance_percent': 5.0},
            'volume_profile': {'max_corrections_percent': 2.0},
            'quality_thresholds': {
                'quarantine_rate_max': 0.1,
                'tick_alignment_min': 99.9,
                'quote_sanity_min': 99.5,
                'dom_shape_min': 99.5,
                'nbcv_consistency_min': 98.0,
                'vp_corrections_max': 2.0
            },
            'markets': {
                'ES': {'tick_size': 0.25, 'max_spread_ticks': 4},
                'NQ': {'tick_size': 0.25, 'max_spread_ticks': 4},
                'VIX': {'tick_size': 0.01, 'max_spread_ticks': 10}
            }
        }
    
    def check_file(self, file_path: str, quick_mode: bool = False) -> Dict:
        """Vérifie la qualité d'un fichier JSONL"""
        print(f"🔍 Vérification du fichier: {file_path}")
        
        if not Path(file_path).exists():
            print(f"❌ Fichier non trouvé: {file_path}")
            return {'error': 'file_not_found'}
        
        # Réinitialiser les métriques
        self.reset_metrics()
        
        # Analyser le fichier
        try:
            with open(file_path, 'r') as f:
                for line_num, line in enumerate(f, 1):
                    if quick_mode and line_num > 1000:  # Limiter à 1000 lignes en mode rapide
                        break
                    
                    try:
                        data = json.loads(line.strip())
                        self.check_message(data, line_num)
                    except json.JSONDecodeError:
                        self.metrics['quarantined_messages'] += 1
                        print(f"⚠️  Ligne {line_num}: JSON invalide")
        
        except Exception as e:
            print(f"❌ Erreur lors de la lecture du fichier: {e}")
            return {'error': str(e)}
        
        # Calculer les métriques finales
        return self.calculate_final_metrics()
    
    def check_message(self, data: Dict, line_num: int):
        """Vérifie un message individuel"""
        self.metrics['total_messages'] += 1
        
        msg_type = data.get('type', 'unknown')
        symbol = data.get('sym', 'unknown')
        
        # Vérifications communes
        self.check_timestamp(data, symbol)
        self.check_sequence(data, symbol)
        
        # Vérifications spécifiques par type
        if msg_type == 'basedata':
            self.check_basedata(data, line_num)
        elif msg_type == 'quote':
            self.check_quote(data, line_num)
        elif msg_type == 'depth':
            self.check_dom(data, line_num)
        elif msg_type in ['vwap', 'vwap_current', 'vwap_previous']:
            self.check_vwap(data, line_num)
        elif msg_type.startswith('numbers_bars_calculated_values'):
            self.check_nbcv(data, line_num)
        elif msg_type == 'volume_profile':
            self.check_volume_profile(data, line_num)
        elif msg_type == 'vix':
            self.check_vix(data, line_num)
        elif msg_type == 'trade':
            self.check_trade(data, line_num)
    
    def check_timestamp(self, data: Dict, symbol: str):
        """Vérifie la monotonie des timestamps"""
        timestamp = data.get('t', 0)
        
        if symbol in self.last_timestamps:
            if timestamp < self.last_timestamps[symbol]:
                self.metrics['time_monotonicity_violations'] += 1
        
        self.last_timestamps[symbol] = timestamp
    
    def check_sequence(self, data: Dict, symbol: str):
        """Vérifie les gaps de séquence"""
        seq = data.get('seq', 0)
        
        if symbol in self.last_sequences and seq > 0:
            gap = seq - self.last_sequences[symbol]
            if gap > self.config.get('sequence', {}).get('max_gap', 1000):
                self.metrics['seq_gaps'] += 1
        
        self.last_sequences[symbol] = seq
    
    def check_basedata(self, data: Dict, line_num: int):
        """Vérifie les données basedata"""
        # Vérification des prix
        for price_field in ['o', 'h', 'l', 'c']:
            if price_field in data:
                if not self.is_price_valid(data[price_field]):
                    self.metrics['price_anomalies'] += 1
                    print(f"⚠️  Ligne {line_num}: Prix {price_field} invalide: {data[price_field]}")
        
        # Vérification du volume
        volume = data.get('v', 0)
        if not self.is_volume_valid(volume):
            self.metrics['quarantined_messages'] += 1
            print(f"⚠️  Ligne {line_num}: Volume invalide: {volume}")
    
    def check_quote(self, data: Dict, line_num: int):
        """Vérifie les quotes"""
        bid = data.get('bid', 0)
        ask = data.get('ask', 0)
        
        # Vérification bid < ask
        if bid >= ask:
            self.metrics['quote_sanity_violations'] += 1
            print(f"⚠️  Ligne {line_num}: bid >= ask: {bid} >= {ask}")
        
        # Vérification du spread
        spread = ask - bid
        max_spread = self.config['quotes']['max_spread_ticks'] * self.config['markets']['ES']['tick_size']
        if spread > max_spread:
            self.metrics['spread_alerts'] += 1
            print(f"⚠️  Ligne {line_num}: Spread trop large: {spread} > {max_spread}")
    
    def check_dom(self, data: Dict, line_num: int):
        """Vérifie le DOM"""
        price = data.get('price', 0)
        size = data.get('size', 0)
        
        if not self.is_price_valid(price):
            self.metrics['price_anomalies'] += 1
            print(f"⚠️  Ligne {line_num}: Prix DOM invalide: {price}")
        
        if not self.is_volume_valid(size):
            self.metrics['quarantined_messages'] += 1
            print(f"⚠️  Ligne {line_num}: Taille DOM invalide: {size}")
    
    def check_vwap(self, data: Dict, line_num: int):
        """Vérifie les VWAP et bandes"""
        value = data.get('value', data.get('vwap', 0))
        
        if not self.is_price_valid(value):
            self.metrics['price_anomalies'] += 1
            print(f"⚠️  Ligne {line_num}: Valeur VWAP invalide: {value}")
        
        # Vérification des bandes
        if 'upper_band_1' in data and 'lower_band_1' in data:
            upper_1 = data['upper_band_1']
            lower_1 = data['lower_band_1']
            
            if upper_1 <= value or lower_1 >= value:
                self.metrics['vwap_band_violations'] += 1
                print(f"⚠️  Ligne {line_num}: Bandes VWAP invalides: {lower_1} >= {value} >= {upper_1}")
    
    def check_nbcv(self, data: Dict, line_num: int):
        """Vérifie les NBCV"""
        ask = data.get('ask', 0)
        bid = data.get('bid', 0)
        total = data.get('total', 0)
        delta = data.get('delta', 0)
        
        # Vérification cohérence total
        if total > 0:
            expected_total = ask + bid
            tolerance = self.config['nbcv']['total_tolerance_percent'] / 100.0
            if abs(total - expected_total) / total > tolerance:
                self.metrics['nbcv_consistency_violations'] += 1
                print(f"⚠️  Ligne {line_num}: Total NBCV incohérent: {total} vs {expected_total}")
        
        # Vérification cohérence delta
        if delta != 0:
            expected_delta = ask - bid
            tolerance = self.config['nbcv']['delta_tolerance_percent'] / 100.0
            if abs(delta - expected_delta) / abs(delta) > tolerance:
                self.metrics['nbcv_consistency_violations'] += 1
                print(f"⚠️  Ligne {line_num}: Delta NBCV incohérent: {delta} vs {expected_delta}")
    
    def check_volume_profile(self, data: Dict, line_num: int):
        """Vérifie le Volume Profile"""
        poc = data.get('poc', 0)
        vah = data.get('vah', 0)
        val = data.get('val', data.get('pval', 0))
        
        # Vérification VAH >= VAL
        if vah < val:
            self.metrics['vp_corrections'] += 1
            print(f"⚠️  Ligne {line_num}: VAH < VAL: {vah} < {val}")
        
        # Vérification POC dans [VAL, VAH]
        if poc < val or poc > vah:
            self.metrics['vp_corrections'] += 1
            print(f"⚠️  Ligne {line_num}: POC hors range: {poc} not in [{val}, {vah}]")
    
    def check_vix(self, data: Dict, line_num: int):
        """Vérifie le VIX"""
        vix_value = data.get('last', 0)
        min_vix = self.config['vix']['min_value']
        max_vix = self.config['vix']['max_value']
        
        if vix_value < min_vix or vix_value > max_vix:
            self.metrics['vix_alerts'] += 1
            print(f"⚠️  Ligne {line_num}: VIX hors range: {vix_value} not in [{min_vix}, {max_vix}]")
    
    def check_trade(self, data: Dict, line_num: int):
        """Vérifie les trades"""
        price = data.get('px', 0)
        volume = data.get('vol', data.get('qty', 0))
        
        if not self.is_price_valid(price):
            self.metrics['price_anomalies'] += 1
            print(f"⚠️  Ligne {line_num}: Prix trade invalide: {price}")
        
        if not self.is_volume_valid(volume):
            self.metrics['quarantined_messages'] += 1
            print(f"⚠️  Ligne {line_num}: Volume trade invalide: {volume}")
    
    def is_price_valid(self, price: float) -> bool:
        """Vérifie si un prix est valide"""
        if price != price or price <= 0:  # NaN ou négatif
            return False
        
        # Vérification alignement tick
        tick_size = self.config['markets']['ES']['tick_size']
        remainder = price % tick_size
        if remainder > self.config['price']['tick_alignment_tolerance']:
            self.metrics['tick_alignment_violations'] += 1
            return False
        
        return True
    
    def is_volume_valid(self, volume: int) -> bool:
        """Vérifie si un volume est valide"""
        return isinstance(volume, (int, float)) and volume >= 0
    
    def calculate_final_metrics(self) -> Dict:
        """Calcule les métriques finales"""
        total = self.metrics['total_messages']
        if total == 0:
            return {'error': 'no_messages'}
        
        # Calculer les taux
        quarantine_rate = self.metrics['quarantined_messages'] / total
        tick_alignment_rate = 100.0 - (self.metrics['tick_alignment_violations'] / total * 100.0)
        quote_sanity_rate = 100.0 - (self.metrics['quote_sanity_violations'] / total * 100.0)
        dom_shape_rate = 100.0 - (self.metrics['dom_shape_violations'] / total * 100.0)
        vwap_band_rate = 100.0 - (self.metrics['vwap_band_violations'] / total * 100.0)
        nbcv_consistency_rate = 100.0 - (self.metrics['nbcv_consistency_violations'] / total * 100.0)
        vp_corrections_rate = self.metrics['vp_corrections'] / total * 100.0
        
        # Score global
        overall_score = (tick_alignment_rate + quote_sanity_rate + dom_shape_rate + 
                        vwap_band_rate + nbcv_consistency_rate) / 5.0
        
        # Vérification production ready
        thresholds = self.config['quality_thresholds']
        is_production_ready = (
            quarantine_rate <= thresholds['quarantine_rate_max'] and
            tick_alignment_rate >= thresholds['tick_alignment_min'] and
            quote_sanity_rate >= thresholds['quote_sanity_min'] and
            dom_shape_rate >= thresholds['dom_shape_min'] and
            nbcv_consistency_rate >= thresholds['nbcv_consistency_min'] and
            vp_corrections_rate <= thresholds['vp_corrections_max']
        )
        
        return {
            'total_messages': total,
            'quarantine_rate': quarantine_rate,
            'tick_alignment_rate': tick_alignment_rate,
            'quote_sanity_rate': quote_sanity_rate,
            'dom_shape_rate': dom_shape_rate,
            'vwap_band_rate': vwap_band_rate,
            'nbcv_consistency_rate': nbcv_consistency_rate,
            'vp_corrections_rate': vp_corrections_rate,
            'overall_score': overall_score,
            'is_production_ready': is_production_ready,
            'violations': {
                'price_anomalies': self.metrics['price_anomalies'],
                'vix_alerts': self.metrics['vix_alerts'],
                'spread_alerts': self.metrics['spread_alerts'],
                'time_monotonicity_violations': self.metrics['time_monotonicity_violations'],
                'seq_gaps': self.metrics['seq_gaps']
            }
        }
    
    def reset_metrics(self):
        """Réinitialise les métriques"""
        for key in self.metrics:
            self.metrics[key] = 0
        self.last_timestamps.clear()
        self.last_sequences.clear()
    
    def print_report(self, metrics: Dict):
        """Affiche le rapport de qualité"""
        print("\n" + "="*60)
        print("🛡️  RAPPORT DE QUALITÉ MIA")
        print("="*60)
        
        if 'error' in metrics:
            print(f"❌ Erreur: {metrics['error']}")
            return
        
        print(f"📊 Messages totaux: {metrics['total_messages']:,}")
        print(f"📈 Score global: {metrics['overall_score']:.1f}/100")
        print(f"🚀 Prêt pour production: {'✅ OUI' if metrics['is_production_ready'] else '❌ NON'}")
        
        print("\n📋 Métriques de qualité:")
        print(f"  • Taux de quarantaine: {metrics['quarantine_rate']:.2%}")
        print(f"  • Alignement tick: {metrics['tick_alignment_rate']:.1f}%")
        print(f"  • Sanité quotes: {metrics['quote_sanity_rate']:.1f}%")
        print(f"  • Forme DOM: {metrics['dom_shape_rate']:.1f}%")
        print(f"  • Bandes VWAP: {metrics['vwap_band_rate']:.1f}%")
        print(f"  • Cohérence NBCV: {metrics['nbcv_consistency_rate']:.1f}%")
        print(f"  • Corrections VP: {metrics['vp_corrections_rate']:.1f}%")
        
        print("\n⚠️  Violations détectées:")
        violations = metrics['violations']
        for violation_type, count in violations.items():
            if count > 0:
                print(f"  • {violation_type}: {count}")
        
        # Recommandations
        print("\n💡 Recommandations:")
        if not metrics['is_production_ready']:
            print("  • Corriger les violations avant déploiement")
            if metrics['quarantine_rate'] > 0.1:
                print("  • Taux de quarantaine trop élevé - vérifier la source")
            if metrics['tick_alignment_rate'] < 99.9:
                print("  • Problème d'alignement tick - vérifier la normalisation")
            if metrics['quote_sanity_rate'] < 99.5:
                print("  • Problème de sanité quotes - vérifier le feed")
        else:
            print("  • ✅ Qualité excellente - prêt pour la production")
        
        print("="*60)

def main():
    parser = argparse.ArgumentParser(description="🛡️ MIA Quality Checker")
    parser.add_argument('--file', '-f', help='Fichier JSONL à vérifier')
    parser.add_argument('--quick', '-q', action='store_true', help='Mode rapide (1000 lignes max)')
    parser.add_argument('--config', '-c', default='mia_quality_config.yml', help='Fichier de configuration')
    parser.add_argument('--output', '-o', help='Fichier de sortie pour le rapport JSON')
    parser.add_argument('--monitor', '-m', action='store_true', help='Mode monitoring (à implémenter)')
    parser.add_argument('--watch-dir', '-w', default='.', help='Répertoire à surveiller en mode monitoring')
    
    args = parser.parse_args()
    
    if not args.file and not args.monitor:
        parser.print_help()
        sys.exit(1)
    
    checker = MIAQualityChecker(args.config)
    
    if args.file:
        metrics = checker.check_file(args.file, args.quick)
        checker.print_report(metrics)
        
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(metrics, f, indent=2)
            print(f"\n📄 Rapport sauvegardé: {args.output}")
    
    elif args.monitor:
        print("🔍 Mode monitoring - à implémenter")
        # TODO: Implémenter le monitoring en temps réel

if __name__ == "__main__":
    main()
