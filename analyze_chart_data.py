#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Analyseur de données de marché pour chart_3_20250904.jsonl
Vérifie la cohérence et détecte les anomalies selon les règles métiers
"""

import json
import csv
import math
from datetime import datetime
from pathlib import Path
from collections import defaultdict, Counter
from typing import Dict, List, Any, Tuple, Optional

# Constantes de tolérance
VOL_TOL = 2
VAP_MATCH_TOL = 0.05
QUOTE_SCALE_CANDIDATES = [1, 0.1, 0.01, 10, 100]
PRICE_TOL = 0.01

class ChartDataAnalyzer:
    def __init__(self, file_path: str):
        self.file_path = Path(file_path)
        self.stats = defaultdict(lambda: {
            'count': 0,
            'timestamps': [],
            'indices': [],
            'fields': defaultdict(list)
        })
        self.anomalies = []
        self.current_bar_data = {}
        self.session_start = None
        
    def analyze_file(self):
        """Analyse le fichier JSONL ligne par ligne"""
        print(f"🔍 Analyse du fichier: {self.file_path}")
        print(f"📊 Début de l'analyse...")
        
        line_count = 0
        corrupted_lines = 0
        
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line_count += 1
                    
                    if line_count % 10000 == 0:
                        print(f"   Traité {line_count:,} lignes...")
                    
                    # Filtre des lignes non-JSON (solution au problème "processing")
                    line = line.strip()
                    if not (line.startswith("{") and line.endswith("}")):
                        continue
                        
                    try:
                        data = json.loads(line)
                        self.process_record(data, line_num)
                    except json.JSONDecodeError:
                        corrupted_lines += 1
                        self.anomalies.append({
                            't': None,
                            'type': 'corrupted',
                            'rule': 'json_parse',
                            'message': f'Ligne {line_num} corrompue JSON',
                            'snippet': line[:100] + '...' if len(line) > 100 else line
                        })
                    except Exception as e:
                        corrupted_lines += 1
                        self.anomalies.append({
                            't': None,
                            'type': 'error',
                            'rule': 'processing',
                            'message': f'Erreur traitement ligne {line_num}: {str(e)}',
                            'snippet': line[:100] + '...' if len(line) > 100 else line
                        })
                        
        except FileNotFoundError:
            print(f"❌ Fichier non trouvé: {self.file_path}")
            return
        except Exception as e:
            print(f"❌ Erreur lecture fichier: {e}")
            return
            
        print(f"✅ Analyse terminée: {line_count:,} lignes traitées, {corrupted_lines} corrompues")
        
    def process_record(self, data: Dict[str, Any], line_num: int):
        """Traite un enregistrement individuel"""
        if not isinstance(data, dict):
            return
            
        record_type = data.get('type', 'unknown')
        timestamp = data.get('t')
        index = data.get('i')
        
        # Statistiques de base
        self.stats[record_type]['count'] += 1
        if timestamp:
            self.stats[record_type]['timestamps'].append(timestamp)
        if index is not None:
            self.stats[record_type]['indices'].append(index)
            
        # Collecte des champs pour analyse
        for key, value in data.items():
            if isinstance(value, (int, float)):
                self.stats[record_type]['fields'][key].append(value)
                
        # Vérifications de cohérence selon le type
        if record_type == 'basedata':
            self.check_basedata_coherence(data, line_num)
        elif record_type == 'nbcv':
            self.check_nbcv_coherence(data, line_num)
        elif record_type == 'quote':
            self.check_quote_coherence(data, line_num)
        elif record_type == 'depth':
            self.check_depth_coherence(data, line_num)
        elif record_type == 'vwap':
            self.check_vwap_coherence(data, line_num)
        elif record_type == 'pvwap':
            self.check_pvwap_coherence(data, line_num)
        elif record_type == 'vva':
            self.check_vva_coherence(data, line_num)
        elif record_type == 'vap':
            self.check_vap_coherence(data, line_num)
        elif record_type == 'trade':
            self.check_trade_coherence(data, line_num)
        elif record_type == 'vix':
            self.check_vix_coherence(data, line_num)
            
        # Vérifications générales
        self.check_timestamp_coherence(record_type, timestamp, index, line_num)
        
    def check_basedata_coherence(self, data: Dict[str, Any], line_num: int):
        """Vérifie la cohérence des données OHLCV"""
        o, h, l, c, v = data.get('o'), data.get('h'), data.get('l'), data.get('c'), data.get('v')
        bidvol, askvol = data.get('bidvol', 0), data.get('askvol', 0)
        
        if all(x is not None for x in [o, h, l, c, v]):
            # Vérification OHLC
            if h < o:
                self.add_anomaly(data, 'basedata', 'ohlc_high_low', 
                                f'High ({h}) < Open ({o})', line_num)
            if l > o:
                self.add_anomaly(data, 'basedata', 'ohlc_low_high', 
                                f'Low ({l}) > Open ({o})', line_num)
            if h < c:
                self.add_anomaly(data, 'basedata', 'ohlc_high_close', 
                                f'High ({h}) < Close ({c})', line_num)
            if l > c:
                self.add_anomaly(data, 'basedata', 'ohlc_low_close', 
                                f'Low ({l}) > Close ({c})', line_num)
            if v < 0:
                self.add_anomaly(data, 'basedata', 'volume_negative', 
                                f'Volume négatif: {v}', line_num)
                
            # Vérification bidvol + askvol
            if bidvol + askvol > v + VOL_TOL:
                self.add_anomaly(data, 'basedata', 'volume_mismatch', 
                                f'bidvol({bidvol}) + askvol({askvol}) > volume({v})', line_num)
                                
            # Stockage pour vérifications croisées
            self.current_bar_data[data.get('i', 0)] = {
                'o': o, 'h': h, 'l': l, 'c': c, 'v': v,
                't': data.get('t')
            }
            
    def check_nbcv_coherence(self, data: Dict[str, Any], line_num: int):
        """Vérifie la cohérence des données NBCV"""
        ask, bid, delta, trades, cumdelta, total = (
            data.get('ask'), data.get('bid'), data.get('delta'), 
            data.get('trades'), data.get('cumdelta'), data.get('total')
        )
        
        if all(x is not None for x in [ask, bid, delta]):
            # Vérification delta
            delta_calc = ask - bid
            if abs(delta_calc - delta) > 0:
                self.add_anomaly(data, 'nbcv', 'delta_mismatch', 
                                f'Delta calculé ({delta_calc}) ≠ delta ({delta})', line_num)
                                
            # Vérification total
            if total is not None and abs(total - (ask + bid)) > VOL_TOL:
                self.add_anomaly(data, 'nbcv', 'total_mismatch', 
                                f'Total ({total}) ≠ ask({ask}) + bid({bid})', line_num)
                                
        if trades is not None and trades < 0:
            self.add_anomaly(data, 'nbcv', 'trades_negative', 
                            f'Trades négatif: {trades}', line_num)
                            
        # Vérification cumdelta (redémarrage quotidien)
        if cumdelta is not None:
            current_time = data.get('t')
            if current_time:
                current_date = datetime.fromtimestamp(current_time).date()
                if self.session_start is None:
                    self.session_start = current_date
                elif current_date != self.session_start:
                    # Nouvelle session, cumdelta devrait redémarrer
                    if cumdelta != 0:
                        self.add_anomaly(data, 'nbcv', 'cumdelta_session', 
                                        f'Cumdelta ({cumdelta}) non nul en début de session', line_num)
                    self.session_start = current_date
                    
    def check_quote_coherence(self, data: Dict[str, Any], line_num: int):
        """Vérifie la cohérence des quotes"""
        bid, ask, spread, mid = data.get('bid'), data.get('ask'), data.get('spread'), data.get('mid')
        
        if all(x is not None for x in [bid, ask]):
            # Vérification bid <= ask
            if ask < bid:
                self.add_anomaly(data, 'quote', 'bid_ask_inverted', 
                                f'Ask ({ask}) < Bid ({bid})', line_num)
                                
            # Vérification spread
            if spread is not None:
                spread_calc = ask - bid
                if abs(spread_calc - spread) > PRICE_TOL:
                    self.add_anomaly(data, 'quote', 'spread_mismatch', 
                                    f'Spread calculé ({spread_calc}) ≠ spread ({spread})', line_num)
                                    
            # Vérification mid
            if mid is not None:
                mid_calc = (ask + bid) / 2
                if abs(mid_calc - mid) > PRICE_TOL:
                    self.add_anomaly(data, 'quote', 'mid_mismatch', 
                                    f'Mid calculé ({mid_calc}) ≠ mid ({mid})', line_num)
                                    
            # Détection d'échelle incohérente
            self.detect_quote_scale_issue(data, line_num)
            
    def detect_quote_scale_issue(self, data: Dict[str, Any], line_num: int):
        """Détecte les problèmes d'échelle des quotes"""
        bid, ask = data.get('bid'), data.get('ask')
        
        if bid is None or ask is None:
            return
            
        # Détection directe des prix ×100 (problème principal identifié)
        if bid > 100000 or ask > 100000:
            self.add_anomaly(data, 'quote', 'scale_issue', 
                            f'Prix ×100 détecté (bid: {bid}, ask: {ask})', line_num)
            return
            
        # Comparaison avec les prix des barres pour détecter l'échelle
        for bar_data in self.current_bar_data.values():
            bar_price = bar_data['c']  # Close price
            if bar_price > 0:
                for scale in QUOTE_SCALE_CANDIDATES:
                    scaled_bid = bid * scale
                    scaled_ask = ask * scale
                    
                    # Vérifier si l'échelle correspond
                    if (abs(scaled_bid - bar_price) < bar_price * 0.1 or 
                        abs(scaled_ask - bar_price) < bar_price * 0.1):
                        if scale != 1:
                            self.add_anomaly(data, 'quote', 'scale_issue', 
                                            f'Échelle probable: {scale}x (bid: {bid}, ask: {ask})', line_num)
                        break
                        
    def check_depth_coherence(self, data: Dict[str, Any], line_num: int):
        """Vérifie la cohérence de la profondeur"""
        side, lvl, price, size = (
            data.get('side'), data.get('lvl'), data.get('price'), data.get('size')
        )
        
        if size is not None and size < 0:
            self.add_anomaly(data, 'depth', 'size_negative', 
                            f'Taille négative: {size}', line_num)
                            
        # Stockage pour vérification de monotonie
        if not hasattr(self, 'depth_levels'):
            self.depth_levels = {'bid': [], 'ask': []}
            
        if all(x is not None for x in [side, lvl, price, size]):
            self.depth_levels[side].append((lvl, price, size))
            
    def check_vwap_coherence(self, data: Dict[str, Any], line_num: int):
        """Vérifie la cohérence des VWAP"""
        vwap = data.get('vwap')
        up1, dn1, up2, dn2 = (
            data.get('up1'), data.get('dn1'), data.get('up2'), data.get('dn2')
        )
        
        # Vérification des bandes VWAP
        if all(x is not None for x in [vwap, up1, dn1]):
            if up1 <= vwap:
                self.add_anomaly(data, 'vwap', 'band_up1_low', 
                                f'Bande up1 ({up1}) <= VWAP ({vwap})', line_num)
            if dn1 >= vwap:
                self.add_anomaly(data, 'vwap', 'band_dn1_high', 
                                f'Bande dn1 ({dn1}) >= VWAP ({vwap})', line_num)
                                
        if all(x is not None for x in [up1, up2]):
            if up1 >= up2:
                self.add_anomaly(data, 'vwap', 'band_order', 
                                f'up1 ({up1}) >= up2 ({up2})', line_num)
                                
        if all(x is not None for x in [dn1, dn2]):
            if dn1 <= dn2:
                self.add_anomaly(data, 'vwap', 'band_order', 
                                f'dn1 ({dn1}) <= dn2 ({dn2})', line_num)
                                
    def check_pvwap_coherence(self, data: Dict[str, Any], line_num: int):
        """Vérifie la cohérence des PVWAP"""
        pvwap = data.get('pvwap')
        
        # Vérification que PVWAP est proche des prix des barres
        if pvwap is not None:
            for bar_data in self.current_bar_data.values():
                bar_price = bar_data['c']
                if abs(pvwap - bar_price) > bar_price * 0.1:  # 10% de tolérance
                    self.add_anomaly(data, 'pvwap', 'price_mismatch', 
                                    f'PVWAP ({pvwap}) éloigné du prix ({bar_price})', line_num)
                    break
                    
    def check_vva_coherence(self, data: Dict[str, Any], line_num: int):
        """Vérifie la cohérence des VVA"""
        vah, val, vpoc = data.get('vah'), data.get('val'), data.get('vpoc')
        
        if all(x is not None for x in [vah, val]):
            if val >= vah:
                self.add_anomaly(data, 'vva', 'val_vah_inverted', 
                                f'VAL ({val}) >= VAH ({vah})', line_num)
                                
        # Vérification VPOC dans la fourchette VAH/VAL (plus logique)
        if all(x is not None for x in [vpoc, vah, val]):
            if vpoc < val or vpoc > vah:
                self.add_anomaly(data, 'vva', 'vpoc_out_of_range', 
                                f'VPOC ({vpoc}) hors fourchette VAH/VAL [{val}, {vah}]', line_num)
        # Fallback: vérification dans la fourchette des barres si VAH/VAL non disponibles
        elif vpoc is not None:
            for bar_data in self.current_bar_data.values():
                h, l = bar_data['h'], bar_data['l']
                if vpoc < l or vpoc > h:
                    self.add_anomaly(data, 'vva', 'vpoc_out_of_range', 
                                    f'VPOC ({vpoc}) hors fourchette barres [{l}, {h}]', line_num)
                    break
                    
    def check_vap_coherence(self, data: Dict[str, Any], line_num: int):
        """Vérifie la cohérence des VAP"""
        bar, price, vol = data.get('bar'), data.get('price'), data.get('vol')
        
        if vol is not None and vol < 0:
            self.add_anomaly(data, 'vap', 'volume_negative', 
                            f'Volume VAP négatif: {vol}', line_num)
                            
        # Agrégation par barre pour vérifier la correspondance avec basedata
        if not hasattr(self, 'vap_by_bar'):
            self.vap_by_bar = defaultdict(list)
            
        if all(x is not None for x in [bar, price, vol]):
            self.vap_by_bar[bar].append((price, vol))
            
    def check_trade_coherence(self, data: Dict[str, Any], line_num: int):
        """Vérifie la cohérence des trades"""
        px, qty = data.get('px'), data.get('qty')
        
        if qty is not None and qty <= 0:
            self.add_anomaly(data, 'trade', 'qty_invalid', 
                            f'Quantité invalide: {qty}', line_num)
                            
        # Vérification que le prix est dans la fourchette de la barre courante
        if px is not None:
            for bar_data in self.current_bar_data.values():
                h, l = bar_data['h'], bar_data['l']
                if px < l or px > h:
                    self.add_anomaly(data, 'trade', 'price_out_of_range', 
                                    f'Prix trade ({px}) hors fourchette [{l}, {h}]', line_num)
                    break
                    
    def check_vix_coherence(self, data: Dict[str, Any], line_num: int):
        """Vérifie la cohérence des données VIX"""
        last, mode = data.get('last'), data.get('mode')
        
        if last is not None and last < 0:
            self.add_anomaly(data, 'vix', 'last_negative', 
                            f'VIX last négatif: {last}', line_num)
                            
        if mode is not None and mode not in ['normal', 'contango', 'backwardation', 0, 1, 2]:
            self.add_anomaly(data, 'vix', 'mode_invalid', 
                            f'Mode VIX invalide: {mode}', line_num)
                            
    def check_timestamp_coherence(self, record_type: str, timestamp: Optional[float], 
                                 index: Optional[int], line_num: int):
        """Vérifie la cohérence des timestamps et indices"""
        if not hasattr(self, 'last_timestamps'):
            self.last_timestamps = {}
            self.last_indices = {}
            
        # Vérification timestamp non décroissant par type
        if timestamp is not None:
            if record_type in self.last_timestamps:
                if timestamp < self.last_timestamps[record_type]:
                    self.add_anomaly({
                        't': timestamp,
                        'type': record_type
                    }, 'timestamp', 'decreasing_time', 
                    f'Timestamp décroissant: {timestamp} < {self.last_timestamps[record_type]}', line_num)
            self.last_timestamps[record_type] = timestamp
            
        # Vérification index non décroissant pour les séries
        if index is not None:
            if record_type in self.last_indices:
                if index < self.last_indices[record_type]:
                    self.add_anomaly({
                        't': timestamp,
                        'type': record_type,
                        'i': index
                    }, 'index', 'decreasing_index', 
                    f'Index décroissant: {index} < {self.last_indices[record_type]}', line_num)
            self.last_indices[record_type] = index
            
    def add_anomaly(self, data: Dict[str, Any], rule_type: str, rule: str, 
                    message: str, line_num: int):
        """Ajoute une anomalie détectée"""
        self.anomalies.append({
            't': data.get('t'),
            'type': rule_type,
            'rule': rule,
            'message': message,
            'snippet': str(data)[:200] + '...' if len(str(data)) > 200 else str(data)
        })
        
    def generate_report(self):
        """Génère le rapport d'analyse"""
        print("📝 Génération du rapport...")
        
        # Rapport Markdown
        self.generate_markdown_report()
        
        # CSV des anomalies
        self.generate_anomalies_csv()
        
        # Résumé console
        self.print_console_summary()
        
    def generate_markdown_report(self):
        """Génère le rapport Markdown"""
        report_path = Path('report.md')
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("# 📊 Rapport d'Analyse - chart_3_20250904.jsonl\n\n")
            f.write(f"**Date d'analyse:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            # Inventaire des types
            f.write("## 📋 Inventaire des Types de Données\n\n")
            f.write("| Type | Nombre | Premier Timestamp | Dernier Timestamp |\n")
            f.write("|------|--------|-------------------|-------------------|\n")
            
            for record_type, stats in self.stats.items():
                if stats['count'] > 0:
                    first_ts = min(stats['timestamps']) if stats['timestamps'] else 'N/A'
                    last_ts = max(stats['timestamps']) if stats['timestamps'] else 'N/A'
                    f.write(f"| {record_type} | {stats['count']:,} | {first_ts} | {last_ts} |\n")
                    
            # Statistiques par type
            f.write("\n## 📈 Statistiques par Type\n\n")
            for record_type, stats in self.stats.items():
                if stats['count'] > 0:
                    f.write(f"### {record_type.upper()}\n")
                    f.write(f"- **Nombre total:** {stats['count']:,}\n")
                    
                    # Statistiques des champs numériques
                    for field, values in stats['fields'].items():
                        if values:
                            f.write(f"- **{field}:** min={min(values):.4f}, avg={sum(values)/len(values):.4f}, max={max(values):.4f}\n")
                    f.write("\n")
                    
            # Top 10 anomalies par règle
            f.write("## ⚠️ Top 10 Anomalies par Règle\n\n")
            rule_counts = Counter(anom['rule'] for anom in self.anomalies)
            
            for rule, count in rule_counts.most_common(10):
                f.write(f"### {rule} ({count} anomalies)\n")
                rule_anomalies = [a for a in self.anomalies if a['rule'] == rule]
                
                for i, anom in enumerate(rule_anomalies[:5], 1):
                    f.write(f"{i}. **{anom['message']}**\n")
                    f.write(f"   - Type: {anom['type']}\n")
                    f.write(f"   - Timestamp: {anom['t']}\n")
                    f.write(f"   - Données: {anom['snippet'][:100]}...\n\n")
                    
            # Résumé par famille
            f.write("## 🎯 Résumé par Famille\n\n")
            f.write("| Famille | Status | Nombre d'Anomalies |\n")
            f.write("|---------|--------|-------------------|\n")
            
            for record_type in self.stats.keys():
                if self.stats[record_type]['count'] > 0:
                    type_anomalies = [a for a in self.anomalies if a['type'] == record_type]
                    count = len(type_anomalies)
                    
                    if count == 0:
                        status = "✅ OK"
                    elif count < 10:
                        status = "⚠️ Warnings"
                    else:
                        status = "❌ Errors"
                        
                    f.write(f"| {record_type} | {status} | {count} |\n")
                    
        print(f"📄 Rapport Markdown généré: {report_path}")
        
    def generate_anomalies_csv(self):
        """Génère le CSV des anomalies"""
        csv_path = Path('anomalies.csv')
        
        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['t', 'type', 'rule', 'message', 'snippet'])
            
            for anom in self.anomalies:
                writer.writerow([
                    anom['t'],
                    anom['type'],
                    anom['rule'],
                    anom['message'],
                    anom['snippet']
                ])
                
        print(f"📊 CSV des anomalies généré: {csv_path}")
        
    def print_console_summary(self):
        """Affiche le résumé console"""
        print("\n" + "="*60)
        print("📊 RÉSUMÉ DE L'ANALYSE")
        print("="*60)
        
        total_records = sum(stats['count'] for stats in self.stats.values())
        total_anomalies = len(self.anomalies)
        
        print(f"📈 Total des enregistrements: {total_records:,}")
        print(f"⚠️  Total des anomalies: {total_anomalies}")
        print(f"📁 Types de données détectés: {len(self.stats)}")
        
        print("\n🔍 Répartition des anomalies par règle:")
        rule_counts = Counter(anom['rule'] for anom in self.anomalies)
        for rule, count in rule_counts.most_common():
            print(f"   {rule}: {count}")
            
        print("\n📋 Types de données analysés:")
        for record_type, stats in self.stats.items():
            if stats['count'] > 0:
                anomalies_count = len([a for a in self.anomalies if a['type'] == record_type])
                status = "✅" if anomalies_count == 0 else f"⚠️({anomalies_count})"
                print(f"   {status} {record_type}: {stats['count']:,} enregistrements")
                
        print("\n" + "="*60)
        print("🎯 ANALYSE TERMINÉE")
        print("="*60)

def main():
    """Fonction principale"""
    print("🚀 Analyseur de Données de Marché - MIA System")
    print("=" * 60)
    
    # Vérification du fichier
    file_path = "chart_3_20250904.jsonl"
    if not Path(file_path).exists():
        print(f"❌ Fichier non trouvé: {file_path}")
        print("💡 Assurez-vous que le fichier est dans le répertoire courant")
        return
        
    # Création de l'analyseur et exécution
    analyzer = ChartDataAnalyzer(file_path)
    analyzer.analyze_file()
    analyzer.generate_report()
    
    print("\n✅ Analyse terminée avec succès!")
    print("📁 Fichiers générés:")
    print("   - report.md (rapport détaillé)")
    print("   - anomalies.csv (liste des anomalies)")

if __name__ == "__main__":
    main()
