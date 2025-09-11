#!/usr/bin/env python3
import os, json, glob, collections

def analyze_chart3():
    base = r'D:\MIA_IA_system'
    files = sorted(glob.glob(os.path.join(base, 'chart_3_*.jsonl')))
    
    print('=== ANALYSE CHART 3 ===')
    print(f'Fichiers trouvés: {len(files)}')
    
    for f in files:
        try:
            with open(f, 'r', encoding='utf-8') as fh:
                cnt = 0
                types = collections.Counter()
                sample = []
                
                for line in fh:
                    cnt += 1
                    try:
                        o = json.loads(line)
                        t = o.get('type','?')
                        types[t]+=1
                        if len(sample)<2:
                            sample.append(o)
                    except Exception:
                        pass
                
                print(f'\n{os.path.basename(f)}: {cnt} lignes')
                print(f'  Types: {dict(types)}')
                
                for i, s in enumerate(sample):
                    keys = list(s.keys())[:8]
                    print(f'  Exemple {i+1}: {dict((k,s[k]) for k in keys)}')
                    
        except Exception as e:
            print(f'ERR {f}: {e}')

if __name__ == '__main__':
    analyze_chart3()
