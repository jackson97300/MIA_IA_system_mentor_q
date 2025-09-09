#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Extracteur de données propre pour MIA
Produit un format optimisé pour les bots de trading
"""

import json
import sys
import pandas as pd
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

def extract_clean_data(input_file, output_file):
    """Extrait et nettoie les données pour MIA"""
    
    print("🧹 EXTRACTION DE DONNÉES PROPRES POUR MIA")
    print("=" * 50)
    
    # Structure pour organiser les données par timestamp
    market_snapshots = defaultdict(lambda: {
        'timestamp': None,
        'symbol': None,
        'chart': None,
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
            'vap': []
        }
    })
    
    processed_entries = 0
    debug_lines = 0
    price_corrections = 0
    
    print("📖 Lecture et nettoyage des données...")
    
    with open(input_file, 'r', encoding='utf-8') as f:
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
                
                # Créer une clé unique par timestamp et chart
                timestamp = entry.get('t')
                chart = entry.get('chart', 'unknown')
                symbol = entry.get('sym', 'UNKNOWN')
                bar_index = entry.get('i') or entry.get('bar')
                
                key = f"{timestamp}_{chart}_{symbol}"
                
                # Initialiser le snapshot
                snapshot = market_snapshots[key]
                snapshot['timestamp'] = timestamp
                snapshot['symbol'] = symbol
                snapshot['chart'] = chart
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
                
                elif data_type == 'volume_profile':
                    # Volume Profile
                    snapshot['market_data']['volume_profile'] = {
                        'poc': normalize_price(entry.get('poc')),
                        'vah': normalize_price(entry.get('vah')),
                        'val': normalize_price(entry.get('val'))
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
                
                # Compter les corrections de prix
                for field in ['o', 'h', 'l', 'c', 'px', 'bid', 'ask', 'price']:
                    if field in entry and isinstance(entry[field], (int, float)) and entry[field] > 100000:
                        price_corrections += 1
                        break
                
            except json.JSONDecodeError:
                debug_lines += 1
                continue
            
            # Afficher le progrès
            if processed_entries % 10000 == 0:
                print(f"   Traité {processed_entries} entrées...")
    
    print(f"\n📊 STATISTIQUES DE NETTOYAGE:")
    print(f"   • Entrées traitées: {processed_entries}")
    print(f"   • Lignes debug ignorées: {debug_lines}")
    print(f"   • Corrections de prix: {price_corrections}")
    print(f"   • Snapshots créés: {len(market_snapshots)}")
    
    # Convertir en format final et sauvegarder
    print(f"\n💾 Sauvegarde des données propres...")
    
    clean_data = []
    for key, snapshot in market_snapshots.items():
        # Nettoyer les données vides
        clean_snapshot = {
            'timestamp': snapshot['timestamp'],
            'symbol': snapshot['symbol'],
            'data_type': 'market_snapshot',
            'chart': snapshot['chart'],
            'bar_index': snapshot['bar_index'],
            'market_data': {}
        }
        
        # Ajouter seulement les données non vides
        for data_type, data in snapshot['market_data'].items():
            if data and (not isinstance(data, list) or len(data) > 0):
                clean_snapshot['market_data'][data_type] = data
        
        clean_data.append(clean_snapshot)
    
    # Trier par timestamp
    clean_data.sort(key=lambda x: x['timestamp'])
    
    # Sauvegarder en JSONL
    with open(output_file, 'w', encoding='utf-8') as f:
        for entry in clean_data:
            f.write(json.dumps(entry, ensure_ascii=False) + '\n')
    
    print(f"✅ Fichier propre créé: {output_file}")
    print(f"   • {len(clean_data)} snapshots de marché")
    print(f"   • Format optimisé pour MIA")
    print(f"   • Prix normalisés")
    print(f"   • Données structurées")
    
    return len(clean_data)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python mia_clean_extractor.py <input_jsonl> <output_jsonl>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    count = extract_clean_data(input_file, output_file)
    print(f"\n🎉 EXTRACTION TERMINÉE: {count} snapshots propres créés!")

