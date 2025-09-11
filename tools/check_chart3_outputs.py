import os
import json
import glob
import collections

BASE_DIR = r"D:\MIA_IA_system"

def main() -> None:
    files = sorted(glob.glob(os.path.join(BASE_DIR, 'chart_3_*.jsonl')))
    print(f"FICHIERS: {len(files)}")
    if not files:
        return

    totals = collections.Counter()
    nbcv_fields = collections.Counter()
    have_cumdelta = False

    for fpath in files[-12:]:
        cnt = 0
        types = collections.Counter()
        samples = []
        try:
            with open(fpath, 'r', encoding='utf-8') as fh:
                for line in fh:
                    cnt += 1
                    try:
                        o = json.loads(line)
                    except Exception:
                        continue
                    t = o.get('type', '?')
                    types[t] += 1
                    totals[t] += 1
                    if t == 'nbcv_footprint':
                        for k in ('ask_volume','bid_volume','delta','total_volume','delta_ratio','ask_percent','bid_percent'):
                            if k in o:
                                nbcv_fields[k] += 1
                    if t == 'cumulative_delta':
                        have_cumdelta = True
                    if len(samples) < 2:
                        samples.append(o)
        except Exception as e:
            print("ERR", os.path.basename(fpath), e)
            continue

        print(os.path.basename(fpath), 'lignes=', cnt, 'types=', dict(types))
        for s in samples:
            # Affiche jusqu'à 10 clés pour aperçu
            keys = list(s.keys())[:10]
            short = {k: s.get(k) for k in keys}
            print('  ex:', short)

    print('\n=== RÉCAP GLOBAL (derniers fichiers) ===')
    print('Types totaux:', dict(totals))
    if totals.get('nbcv_footprint'):
        print('Champs NBCV présents (compteur de lignes ayant la clé):', dict(nbcv_fields))
    print('Cumulative Delta présent:', have_cumdelta)

if __name__ == '__main__':
    main()


