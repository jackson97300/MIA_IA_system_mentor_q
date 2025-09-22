#!/usr/bin/env python3
"""
Analyse des trades générés dans unified_20250918_v9.jsonl
Extrait les décisions de trading et les exporte en CSV
"""

import json
import csv
import io
from collections import Counter

def analyze_trades():
    input_file = "unified_20250918_v9.jsonl"
    output_file = "trades_taken_v9.csv"
    
    fields = [
        "t", "action", "price", "mia", "vix", 
        "dist", "zone_min", "zone_max", "stop", "target",
        "reason", "pattern", "confidence"
    ]
    
    trades = []
    total_rows = 0
    
    print(f"🔍 Analyse de {input_file}...")
    
    with io.open(input_file, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
            if not line.strip():
                continue
                
            try:
                row = json.loads(line)
                total_rows += 1
            except Exception as e:
                print(f"⚠️ Erreur ligne {line_num}: {e}")
                continue
                
            decision = row.get("menthorq_decision") or {}
            action = decision.get("action")
            
            if action in ("long", "short"):
                basedata = row.get("basedata") or {}
                alerts = row.get("alerts") or {}
                summary = alerts.get("summary") or {}
                nearest_cluster = summary.get("nearest_cluster") or {}
                trade_plan = row.get("trade_plan") or {}
                mia = row.get("mia") or {}
                vix = row.get("vix") or {}
                
                trade = {
                    "t": row.get("t"),
                    "action": action,
                    "price": basedata.get("c"),
                    "mia": mia.get("value"),
                    "vix": vix.get("value"),
                    "dist": nearest_cluster.get("distance_ticks"),
                    "zone_min": nearest_cluster.get("zone_min"),
                    "zone_max": nearest_cluster.get("zone_max"),
                    "stop": trade_plan.get("stop_ticks"),
                    "target": trade_plan.get("target_ticks"),
                    "reason": decision.get("reason"),
                    "pattern": alerts.get("label"),
                    "confidence": alerts.get("confidence")
                }
                
                trades.append(trade)
                
    print(f"📊 Total lignes traitées: {total_rows}")
    print(f"🎯 Trades trouvés: {len(trades)}")
    
    if trades:
        # Export CSV
        with open(output_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()
            writer.writerows(trades)
        
        print(f"✅ Exporté vers {output_file}")
        
        # Analyse des trades
        actions = Counter(t["action"] for t in trades)
        patterns = Counter(t["pattern"] for t in trades)
        reasons = Counter(t["reason"] for t in trades)
        
        print(f"\n📈 Répartition des actions:")
        for action, count in actions.most_common():
            print(f"  {action}: {count}")
            
        print(f"\n🎯 Patterns détectés:")
        for pattern, count in patterns.most_common():
            print(f"  {pattern}: {count}")
            
        print(f"\n🔍 Raisons des décisions:")
        for reason, count in reasons.most_common():
            print(f"  {reason}: {count}")
            
        # Statistiques MIA
        mia_values = [t["mia"] for t in trades if t["mia"] is not None]
        if mia_values:
            print(f"\n📊 Statistiques MIA:")
            print(f"  Min: {min(mia_values):.3f}")
            print(f"  Max: {max(mia_values):.3f}")
            print(f"  Moyenne: {sum(mia_values)/len(mia_values):.3f}")
            
        # Statistiques VIX
        vix_values = [t["vix"] for t in trades if t["vix"] is not None]
        if vix_values:
            print(f"\n📊 Statistiques VIX:")
            print(f"  Min: {min(vix_values):.2f}")
            print(f"  Max: {max(vix_values):.2f}")
            print(f"  Moyenne: {sum(vix_values)/len(vix_values):.2f}")
            
        # Affichage des trades
        print(f"\n🎯 Détail des trades:")
        for i, trade in enumerate(trades, 1):
            print(f"  {i}. {trade['action'].upper()} @ {trade['price']} | MIA: {trade['mia']:.3f} | VIX: {trade['vix']:.1f} | Dist: {trade['dist']:.1f} | {trade['pattern']}")
    else:
        print("❌ Aucun trade trouvé!")
        
    return len(trades)

if __name__ == "__main__":
    analyze_trades()


