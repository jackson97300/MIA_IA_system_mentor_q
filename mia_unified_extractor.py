#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Extracteur unifié MIA - Fusionne chart_3 et chart_4
Produit un fichier unique au format optimal pour les bots de trading
"""

import json
import sys
import os
from datetime import datetime
from collections import defaultdict

def normalize_price(price):
    """Normalise les prix anormaux"""
    if isinstance(price, (int, float)):
        # Détecter les prix anormaux (> 100000)
        if price > 100000:
            # Diviser par 100 pour corriger
            return round(price / 100, 2)
        return round(price, 2)
    return price

def process_chart_file(file_path, chart_number):
    """Traite un fichier de chart et retourne les données organisées"""
    
    print(f"📖 Traitement de {file_path} (Chart {chart_number})...")
    
    market_snapshots = defaultdict(lambda: {
        'timestamp': None,
        'symbol': None,
        'chart': chart_number,
        'bar_index': None,
        'market_data': {
            'ohlcv': {},
            'order_flow': {},
            'vwap': {},
            'volume_profile': {},
            'nbcv': {},
            'dom': {},
            'quotes': {},
            'vix': {},
            'vap': [],
            'trades': []
        }
    })
    
    processed_entries = 0
    debug_lines = 0
    price_corrections = 0
    
    if not os.path.exists(file_path):
        print(f"⚠️  Fichier non trouvé: {file_path}")
        return market_snapshots, 0, 0, 0
    
    with open(file_path, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
                
            # Ignorer les lignes de debug
            if line.startswith("DEBUG") or line.startswith("SKIP"):
                debug_lines += 1
                continue
                
            try:
                entry = json.loads(line)
                processed_entries += 1
                
                # Créer une clé unique par timestamp et symbol
                timestamp = entry.get('t')
                symbol = entry.get('sym', 'UNKNOWN')
                bar_index = entry.get('i') or entry.get('bar')
                
                key = f"{timestamp}_{symbol}"
                
                # Initialiser le snapshot
                snapshot = market_snapshots[key]
                snapshot['timestamp'] = timestamp
                snapshot['symbol'] = symbol
                snapshot['chart'] = chart_number
                snapshot['bar_index'] = bar_index
                
                # Traiter selon le type de données
                data_type = entry.get('type')
                
                if data_type == 'basedata':
                    # OHLCV + Order Flow
                    snapshot['market_data']['ohlcv'] = {
                        'open': normalize_price(entry.get('o')),
                        'high': normalize_price(entry.get('h')),
                        'low': normalize_price(entry.get('l')),
                        'close': normalize_price(entry.get('c')),
                        'volume': entry.get('v', 0)
                    }
                    snapshot['market_data']['order_flow'] = {
                        'bid_volume': entry.get('bidvol', 0),
                        'ask_volume': entry.get('askvol', 0),
                        'delta': entry.get('bidvol', 0) - entry.get('askvol', 0)
                    }
                
                elif data_type == 'vwap':
                    # VWAP + Bandes
                    snapshot['market_data']['vwap'] = {
                        'value': normalize_price(entry.get('v')),
                        'upper_band_1': normalize_price(entry.get('up1')),
                        'lower_band_1': normalize_price(entry.get('dn1')),
                        'upper_band_2': normalize_price(entry.get('up2')),
                        'lower_band_2': normalize_price(entry.get('dn2'))
                    }
                
                elif data_type == 'vwap_current':
                    # VWAP Current (Graph 4)
                    snapshot['market_data']['vwap']['current'] = {
                        'value': normalize_price(entry.get('vwap')),
                        'upper_band_1': normalize_price(entry.get('s_plus_1')),
                        'lower_band_1': normalize_price(entry.get('s_minus_1')),
                        'upper_band_2': normalize_price(entry.get('s_plus_2')),
                        'lower_band_2': normalize_price(entry.get('s_minus_2'))
                    }
                
                elif data_type == 'pvwap':
                    # VWAP Previous
                    snapshot['market_data']['vwap']['previous'] = {
                        'value': normalize_price(entry.get('pvwap')),
                        'upper_band_1': normalize_price(entry.get('up1')),
                        'lower_band_1': normalize_price(entry.get('dn1')),
                        'upper_band_2': normalize_price(entry.get('up2')),
                        'lower_band_2': normalize_price(entry.get('dn2'))
                    }
                
                elif data_type == 'volume_profile':
                    # Volume Profile
                    snapshot['market_data']['volume_profile'] = {
                        'poc': normalize_price(entry.get('poc')),
                        'vah': normalize_price(entry.get('vah')),
                        'val': normalize_price(entry.get('val'))
                    }
                
                elif data_type == 'vva':
                    # Volume Value Area
                    snapshot['market_data']['volume_profile']['vva'] = {
                        'vah': normalize_price(entry.get('vah')),
                        'val': normalize_price(entry.get('val')),
                        'vpoc': normalize_price(entry.get('vpoc'))
                    }
                
                elif data_type == 'numbers_bars_calculated_values_graph3':
                    # NBCV Graph 3
                    snapshot['market_data']['nbcv']['graph3'] = {
                        'ask_volume': entry.get('ask', 0),
                        'bid_volume': entry.get('bid', 0),
                        'delta': entry.get('delta', 0),
                        'trades': entry.get('trades', 0),
                        'cumulative_delta': entry.get('cumdelta', 0),
                        'total_volume': entry.get('total', 0)
                    }
                
                elif data_type == 'numbers_bars_calculated_values_graph4':
                    # NBCV Graph 4
                    snapshot['market_data']['nbcv']['graph4'] = {
                        'ask_volume': entry.get('ask', 0),
                        'bid_volume': entry.get('bid', 0),
                        'delta': entry.get('delta', 0),
                        'trades': entry.get('trades', 0),
                        'cumulative_delta': entry.get('cumdelta', 0),
                        'total_volume': entry.get('total', 0)
                    }
                
                elif data_type == 'depth':
                    # DOM (Depth of Market)
                    level = entry.get('lvl', 1)
                    side = entry.get('side', 'BID').lower()
                    if 'dom' not in snapshot['market_data']:
                        snapshot['market_data']['dom'] = {}
                    if side not in snapshot['market_data']['dom']:
                        snapshot['market_data']['dom'][side] = {}
                    
                    snapshot['market_data']['dom'][side][f'level_{level}'] = {
                        'price': normalize_price(entry.get('price')),
                        'size': entry.get('size', 0)
                    }
                
                elif data_type == 'quote':
                    # Quotes
                    snapshot['market_data']['quotes'] = {
                        'bid': normalize_price(entry.get('bid')),
                        'ask': normalize_price(entry.get('ask')),
                        'bid_size': entry.get('bq', 0),
                        'ask_size': entry.get('aq', 0),
                        'spread': normalize_price(entry.get('spread', 0)),
                        'mid': normalize_price(entry.get('mid', 0))
                    }
                
                elif data_type == 'vix':
                    # VIX
                    snapshot['market_data']['vix'] = {
                        'value': entry.get('last', 0),
                        'chart': entry.get('chart', 8)
                    }
                
                elif data_type == 'vap':
                    # Volume at Price
                    vap_entry = {
                        'price': normalize_price(entry.get('price')),
                        'volume': entry.get('vol', 0),
                        'level': entry.get('k', 0)
                    }
                    snapshot['market_data']['vap'].append(vap_entry)
                
                elif data_type == 'trade':
                    # Trades
                    trade_entry = {
                        'price': normalize_price(entry.get('px')),
                        'volume': entry.get('vol', entry.get('qty', 0)),
                        'chart': entry.get('chart', chart_number)
                    }
                    snapshot['market_data']['trades'].append(trade_entry)
                
                elif data_type == 'ohlc_graph4':
                    # OHLC spécifique Graph 4
                    snapshot['market_data']['ohlcv']['graph4'] = {
                        'open': normalize_price(entry.get('open')),
                        'high': normalize_price(entry.get('high')),
                        'low': normalize_price(entry.get('low')),
                        'close': normalize_price(entry.get('close'))
                    }
                
                # Compter les corrections de prix
                for field in ['o', 'h', 'l', 'c', 'px', 'bid', 'ask', 'price']:
                    if field in entry and isinstance(entry[field], (int, float)) and entry[field] > 100000:
                        price_corrections += 1
                        break
                
            except json.JSONDecodeError:
                debug_lines += 1
                continue
            
            # Afficher le progrès
            if processed_entries % 50000 == 0:
                print(f"   Traité {processed_entries} entrées...")
    
    print(f"   ✅ Chart {chart_number}: {processed_entries} entrées, {debug_lines} debug, {price_corrections} corrections prix")
    return market_snapshots, processed_entries, debug_lines, price_corrections

def merge_snapshots(snapshots_chart3, snapshots_chart4):
    """Fusionne les snapshots des deux charts"""
    
    print(f"\n🔄 Fusion des données Chart 3 et Chart 4...")
    
    # Créer un dictionnaire unifié
    unified_snapshots = defaultdict(lambda: {
        'timestamp': None,
        'symbol': None,
        'charts': [],
        'bar_index': None,
        'market_data': {
            'ohlcv': {},
            'order_flow': {},
            'vwap': {},
            'volume_profile': {},
            'nbcv': {},
            'dom': {},
            'quotes': {},
            'vix': {},
            'vap': [],
            'trades': []
        }
    })
    
    # Fusionner Chart 3
    for key, snapshot in snapshots_chart3.items():
        unified = unified_snapshots[key]
        unified['timestamp'] = snapshot['timestamp']
        unified['symbol'] = snapshot['symbol']
        unified['charts'].append(3)
        unified['bar_index'] = snapshot['bar_index']
        
        # Fusionner les données de marché
        for data_type, data in snapshot['market_data'].items():
            if data and (not isinstance(data, list) or len(data) > 0):
                if data_type in ['vap', 'trades']:
                    unified['market_data'][data_type].extend(data)
                else:
                    unified['market_data'][data_type].update(data)
    
    # Fusionner Chart 4
    for key, snapshot in snapshots_chart4.items():
        unified = unified_snapshots[key]
        if unified['timestamp'] is None:
            unified['timestamp'] = snapshot['timestamp']
            unified['symbol'] = snapshot['symbol']
            unified['bar_index'] = snapshot['bar_index']
        
        unified['charts'].append(4)
        
        # Fusionner les données de marché
        for data_type, data in snapshot['market_data'].items():
            if data and (not isinstance(data, list) or len(data) > 0):
                if data_type in ['vap', 'trades']:
                    unified['market_data'][data_type].extend(data)
                else:
                    unified['market_data'][data_type].update(data)
    
    # Trier les charts
    for snapshot in unified_snapshots.values():
        snapshot['charts'].sort()
    
    print(f"   ✅ {len(unified_snapshots)} snapshots unifiés créés")
    return unified_snapshots

def create_mia_format(unified_snapshots, output_file):
    """Crée le format final optimisé pour MIA"""
    
    print(f"\n💾 Création du format MIA...")
    
    clean_data = []
    
    for key, snapshot in unified_snapshots.items():
        # Créer le format final pour MIA
        mia_entry = {
            'timestamp': snapshot['timestamp'],
            'symbol': snapshot['symbol'],
            'data_type': 'unified_market_snapshot',
            'charts': snapshot['charts'],
            'bar_index': snapshot['bar_index'],
            'market_data': {}
        }
        
        # Ajouter seulement les données non vides
        for data_type, data in snapshot['market_data'].items():
            if data and (not isinstance(data, list) or len(data) > 0):
                mia_entry['market_data'][data_type] = data
        
        clean_data.append(mia_entry)
    
    # Trier par timestamp
    clean_data.sort(key=lambda x: x['timestamp'])
    
    # Sauvegarder en JSONL
    with open(output_file, 'w', encoding='utf-8') as f:
        for entry in clean_data:
            f.write(json.dumps(entry, ensure_ascii=False) + '\n')
    
    print(f"✅ Fichier MIA créé: {output_file}")
    print(f"   • {len(clean_data)} snapshots unifiés")
    print(f"   • Format optimisé pour les bots de trading")
    print(f"   • Données fusionnées Chart 3 + Chart 4")
    print(f"   • Prix normalisés et nettoyés")
    
    return len(clean_data)

def main():
    """Fonction principale"""
    
    print("🚀 EXTRACTEUR UNIFIÉ MIA")
    print("=" * 50)
    print("Fusionne Chart 3 et Chart 4 en un fichier propre")
    print()
    
    # Fichiers d'entrée
    chart3_file = "chart_3_20250905.jsonl"
    chart4_file = "chart_4_20250905.jsonl"
    output_file = "mia_unified_clean.jsonl"
    
    # Vérifier les fichiers d'entrée
    if not os.path.exists(chart3_file):
        print(f"❌ Fichier Chart 3 non trouvé: {chart3_file}")
        return
    
    if not os.path.exists(chart4_file):
        print(f"❌ Fichier Chart 4 non trouvé: {chart4_file}")
        return
    
    # Traiter Chart 3
    snapshots_chart3, entries3, debug3, corrections3 = process_chart_file(chart3_file, 3)
    
    # Traiter Chart 4
    snapshots_chart4, entries4, debug4, corrections4 = process_chart_file(chart4_file, 4)
    
    # Fusionner les données
    unified_snapshots = merge_snapshots(snapshots_chart3, snapshots_chart4)
    
    # Créer le format final
    count = create_mia_format(unified_snapshots, output_file)
    
    # Statistiques finales
    print(f"\n📊 STATISTIQUES FINALES:")
    print(f"   • Chart 3: {entries3} entrées, {debug3} debug, {corrections3} corrections")
    print(f"   • Chart 4: {entries4} entrées, {debug4} debug, {corrections4} corrections")
    print(f"   • Total: {entries3 + entries4} entrées traitées")
    print(f"   • Snapshots unifiés: {count}")
    print(f"   • Fichier de sortie: {output_file}")
    
    print(f"\n🎉 EXTRACTION UNIFIÉE TERMINÉE!")
    print(f"   Votre fichier MIA est prêt: {output_file}")

if __name__ == "__main__":
    main()

