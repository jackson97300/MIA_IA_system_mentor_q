#!/usr/bin/env python3
import json
import collections
from datetime import datetime

def analyze_coherence():
    base = r'D:\MIA_IA_system'
    files = [
        'chart_3_basedata_20250911.jsonl',
        'chart_3_cumulative_delta_20250911.jsonl', 
        'chart_3_depth_20250911.jsonl',
        'chart_3_nbcv_20250911.jsonl',
        'chart_3_quote_20250911.jsonl',
        'chart_3_vva_20250911.jsonl',
        'chart_3_vwap_20250911.jsonl'
    ]
    
    print('=== ANALYSE COHÉRENCE CHART 3 ===\n')
    
    for filename in files:
        filepath = f'{base}\\{filename}'
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                
            print(f'📁 {filename}: {len(lines)} lignes')
            
            # Analyse des doublons
            unique_lines = set()
            duplicates = 0
            timestamps = []
            bar_indices = []
            
            for line in lines:
                line = line.strip()
                if line in unique_lines:
                    duplicates += 1
                else:
                    unique_lines.add(line)
                
                try:
                    data = json.loads(line)
                    timestamps.append(data.get('t', 0))
                    if 'i' in data:
                        bar_indices.append(data['i'])
                except:
                    pass
            
            print(f'  🔄 Doublons: {duplicates} ({duplicates/len(lines)*100:.1f}%)')
            print(f'  📊 Lignes uniques: {len(unique_lines)}')
            
            # Analyse des timestamps
            if timestamps:
                unique_timestamps = len(set(timestamps))
                print(f'  ⏰ Timestamps uniques: {unique_timestamps}')
                
                # Détecter les barres répétées
                if bar_indices:
                    bar_counts = collections.Counter(bar_indices)
                    repeated_bars = [(bar, count) for bar, count in bar_counts.items() if count > 1]
                    if repeated_bars:
                        print(f'  📈 Barres répétées: {len(repeated_bars)}')
                        for bar, count in repeated_bars[:5]:  # Top 5
                            print(f'    Bar {bar}: {count} occurrences')
                    else:
                        print(f'  ✅ Aucune barre répétée')
            
            # Analyse des valeurs
            if filename == 'chart_3_basedata_20250911.jsonl':
                analyze_basedata_coherence(lines)
            elif filename == 'chart_3_nbcv_20250911.jsonl':
                analyze_nbcv_coherence(lines)
                
            print()
            
        except Exception as e:
            print(f'❌ Erreur {filename}: {e}\n')

def analyze_basedata_coherence(lines):
    print('  🔍 Analyse basedata:')
    
    # Vérifier la cohérence OHLCV
    for i, line in enumerate(lines[:10]):  # Premiers 10
        try:
            data = json.loads(line.strip())
            o, h, l, c = data.get('o', 0), data.get('h', 0), data.get('l', 0), data.get('c', 0)
            
            # Vérifier OHLC cohérence
            if h < max(o, c) or l > min(o, c):
                print(f'    ⚠️  Bar {data.get("i", i)}: OHLC incohérent H={h}, L={l}, O={o}, C={c}')
            else:
                print(f'    ✅ Bar {data.get("i", i)}: OHLC cohérent')
                
        except Exception as e:
            print(f'    ❌ Erreur ligne {i}: {e}')

def analyze_nbcv_coherence(lines):
    print('  🔍 Analyse NBCV:')
    
    for i, line in enumerate(lines):
        try:
            data = json.loads(line.strip())
            ask_vol = data.get('ask_volume', 0)
            bid_vol = data.get('bid_volume', 0)
            total_vol = data.get('total_volume', 0)
            delta = data.get('delta', 0)
            
            # Vérifier cohérence
            if abs(delta - (ask_vol - bid_vol)) > 0.1:
                print(f'    ⚠️  Bar {data.get("i", i)}: Delta incohérent {delta} vs {ask_vol-bid_vol}')
            else:
                print(f'    ✅ Bar {data.get("i", i)}: Delta cohérent')
                
            if abs(total_vol - (ask_vol + bid_vol)) > 0.1:
                print(f'    ⚠️  Bar {data.get("i", i)}: Total volume incohérent {total_vol} vs {ask_vol+bid_vol}')
            else:
                print(f'    ✅ Bar {data.get("i", i)}: Total volume cohérent')
                
        except Exception as e:
            print(f'    ❌ Erreur ligne {i}: {e}')

if __name__ == '__main__':
    analyze_coherence()
