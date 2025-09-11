#!/usr/bin/env python3
import json
import statistics

def analyze_sentiment():
    base = r'D:\MIA_IA_system'
    nbcv_file = f'{base}\\chart_3_nbcv_20250911.jsonl'
    
    print('=== ANALYSE SENTIMENT BULLISH/BEARISH CHART 3 ===\n')
    
    try:
        with open(nbcv_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        print(f'📊 NBCV Footprint: {len(lines)} barres analysées\n')
        
        # Collecter les métriques
        deltas = []
        ask_volumes = []
        bid_volumes = []
        total_volumes = []
        ask_percents = []
        bid_percents = []
        pressure_bullish_count = 0
        pressure_bearish_count = 0
        pressure_neutral_count = 0
        
        print('📈 DÉTAIL PAR BARRE:')
        print('Bar | Delta | Ask% | Bid% | AskVol | BidVol | Total | Pressure')
        print('-' * 70)
        
        for i, line in enumerate(lines):
            try:
                data = json.loads(line.strip())
                
                bar = data.get('i', i)
                delta = data.get('delta', 0)
                ask_vol = data.get('ask_volume', 0)
                bid_vol = data.get('bid_volume', 0)
                total_vol = data.get('total_volume', 0)
                ask_pct = data.get('ask_percent', 0)
                bid_pct = data.get('bid_percent', 0)
                pressure = data.get('pressure', 0)
                
                # Collecter pour statistiques
                deltas.append(delta)
                ask_volumes.append(ask_vol)
                bid_volumes.append(bid_vol)
                total_volumes.append(total_vol)
                ask_percents.append(ask_pct)
                bid_percents.append(bid_pct)
                
                # Compter les pressions
                if pressure == 1:
                    pressure_bullish_count += 1
                elif pressure == -1:
                    pressure_bearish_count += 1
                else:
                    pressure_neutral_count += 1
                
                # Afficher détail
                pressure_str = "BULL" if pressure == 1 else "BEAR" if pressure == -1 else "NEUTRAL"
                print(f'{bar:3d} | {delta:5d} | {ask_pct:.3f} | {bid_pct:.3f} | {ask_vol:6d} | {bid_vol:6d} | {total_vol:5d} | {pressure_str}')
                
            except Exception as e:
                print(f'❌ Erreur ligne {i}: {e}')
        
        print('\n' + '='*70)
        print('📊 RÉSUMÉ SENTIMENT:')
        print('='*70)
        
        # Statistiques générales
        if deltas:
            print(f'📈 DELTA:')
            print(f'  Moyenne: {statistics.mean(deltas):.1f}')
            print(f'  Médiane: {statistics.median(deltas):.1f}')
            print(f'  Min: {min(deltas)}')
            print(f'  Max: {max(deltas)}')
            print(f'  Positif: {sum(1 for d in deltas if d > 0)} barres')
            print(f'  Négatif: {sum(1 for d in deltas if d < 0)} barres')
            print(f'  Neutre: {sum(1 for d in deltas if d == 0)} barres')
        
        if ask_percents and bid_percents:
            print(f'\n📊 VOLUME DISTRIBUTION:')
            print(f'  Ask% moyen: {statistics.mean(ask_percents)*100:.2f}%')
            print(f'  Bid% moyen: {statistics.mean(bid_percents)*100:.2f}%')
            print(f'  Ratio Ask/Bid moyen: {statistics.mean(ask_percents)/statistics.mean(bid_percents):.3f}')
        
        if total_volumes:
            print(f'\n📊 VOLUME TOTAL:')
            print(f'  Volume moyen: {statistics.mean(total_volumes):.0f}')
            print(f'  Volume total: {sum(total_volumes)}')
        
        # Sentiment final
        print(f'\n🎯 SENTIMENT FINAL:')
        print(f'  🟢 BULLISH: {pressure_bullish_count} barres ({pressure_bullish_count/len(lines)*100:.1f}%)')
        print(f'  🔴 BEARISH: {pressure_bearish_count} barres ({pressure_bearish_count/len(lines)*100:.1f}%)')
        print(f'  ⚪ NEUTRAL: {pressure_neutral_count} barres ({pressure_neutral_count/len(lines)*100:.1f}%)')
        
        # Conclusion
        if pressure_bullish_count > pressure_bearish_count:
            sentiment = "🟢 BULLISH"
            strength = pressure_bullish_count / len(lines) * 100
        elif pressure_bearish_count > pressure_bullish_count:
            sentiment = "🔴 BEARISH" 
            strength = pressure_bearish_count / len(lines) * 100
        else:
            sentiment = "⚪ NEUTRAL"
            strength = pressure_neutral_count / len(lines) * 100
            
        print(f'\n🏆 CONCLUSION: {sentiment} ({strength:.1f}% de force)')
        
        # Analyse des seuils
        print(f'\n⚙️  SEUILS CONFIGURÉS:')
        print(f'  Min Total Volume: 200 contrats')
        print(f'  Min |Delta Ratio|: 15%')
        print(f'  Min Ask/Bid Ratio: 1.6x')
        
    except Exception as e:
        print(f'❌ Erreur: {e}')

if __name__ == '__main__':
    analyze_sentiment()
