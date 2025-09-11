#!/usr/bin/env python3
"""
Test pour vérifier que Chart 4 génère des sorties VP avec Study IDs 8-9
"""

import json
import os
from datetime import datetime

def test_chart4_vp():
    print("=" * 80)
    print("🧪 TEST CHART 4 - VOLUME PROFILE OUTPUT")
    print("=" * 80)
    
    # Chercher les fichiers Chart 4 récents
    chart4_files = []
    for file in os.listdir('.'):
        if file.startswith('chart_4_') and file.endswith('.jsonl'):
            chart4_files.append(file)
    
    chart4_files.sort(reverse=True)  # Plus récent en premier
    
    print(f"📁 Fichiers Chart 4 trouvés: {chart4_files}")
    
    if not chart4_files:
        print("❌ Aucun fichier Chart 4 trouvé")
        return
    
    # Analyser le fichier le plus récent
    latest_file = chart4_files[0]
    print(f"\n📊 ANALYSE: {latest_file}")
    
    try:
        with open(latest_file, 'r') as f:
            lines = f.readlines()
        
        print(f"📈 Total lignes: {len(lines)}")
        
        if len(lines) == 0:
            print("❌ Fichier vide")
            return
        
        # Analyser les types de données
        types = {}
        vp_data = []
        vva_data = []
        signal_data = []
        debug_data = []
        
        for line_num, line in enumerate(lines, 1):
            try:
                data = json.loads(line.strip())
                dtype = data.get('type', 'unknown')
                types[dtype] = types.get(dtype, 0) + 1
                
                if dtype == 'volume_profile':
                    vp_data.append(data)
                elif dtype == 'vva':
                    vva_data.append(data)
                elif dtype == 'vp_signal':
                    signal_data.append(data)
                elif dtype == 'debug':
                    debug_data.append(data)
                    
            except json.JSONDecodeError:
                print(f"⚠️  Erreur JSON ligne {line_num}: {line.strip()[:100]}...")
                continue
        
        print(f"\n📋 TYPES DE DONNÉES:")
        for dtype, count in sorted(types.items()):
            print(f"  • {dtype}: {count}")
        
        # Analyser Volume Profile
        if vp_data:
            print(f"\n🎯 VOLUME PROFILE: {len(vp_data)} entrées")
            
            current_vp = [d for d in vp_data if d.get('scope') == 'current']
            previous_vp = [d for d in vp_data if d.get('scope') == 'previous']
            
            print(f"  • Current: {len(current_vp)}")
            print(f"  • Previous: {len(previous_vp)}")
            
            # Vérifier les valeurs
            if current_vp:
                poc_values = [d.get('poc', 0) for d in current_vp]
                vah_values = [d.get('vah', 0) for d in current_vp]
                val_values = [d.get('val', 0) for d in current_vp]
                
                poc_zero = sum(1 for v in poc_values if v == 0)
                vah_zero = sum(1 for v in vah_values if v == 0)
                val_zero = sum(1 for v in val_values if v == 0)
                
                print(f"\n📊 VALEURS CURRENT VP:")
                print(f"  • POC: {min(poc_values):.2f} - {max(poc_values):.2f} (zéros: {poc_zero}/{len(current_vp)})")
                print(f"  • VAH: {min(vah_values):.2f} - {max(vah_values):.2f} (zéros: {vah_zero}/{len(current_vp)})")
                print(f"  • VAL: {min(val_values):.2f} - {max(val_values):.2f} (zéros: {val_zero}/{len(current_vp)})")
                
                if val_zero == len(current_vp):
                    print("  ⚠️  ATTENTION: Toutes les valeurs VAL sont à 0!")
                elif val_zero > 0:
                    print(f"  ⚠️  ATTENTION: {val_zero} valeurs VAL sont à 0")
                else:
                    print("  ✅ Toutes les valeurs VAL sont non-nulles")
        
        # Analyser VVA
        if vva_data:
            print(f"\n🎯 VVA: {len(vva_data)} entrées")
            
            vpoc_values = [d.get('vpoc', 0) for d in vva_data]
            vah_values = [d.get('vah', 0) for d in vva_data]
            val_values = [d.get('val', 0) for d in vva_data]
            
            vpoc_zero = sum(1 for v in vpoc_values if v == 0)
            vah_zero = sum(1 for v in vah_values if v == 0)
            val_zero = sum(1 for v in val_values if v == 0)
            
            print(f"  • VPOC: {min(vpoc_values):.2f} - {max(vpoc_values):.2f} (zéros: {vpoc_zero}/{len(vva_data)})")
            print(f"  • VAH: {min(vah_values):.2f} - {max(vah_values):.2f} (zéros: {vah_zero}/{len(vva_data)})")
            print(f"  • VAL: {min(val_values):.2f} - {max(val_values):.2f} (zéros: {val_zero}/{len(vva_data)})")
        
        # Analyser les signaux VP
        if signal_data:
            print(f"\n🎯 VP SIGNALS: {len(signal_data)} entrées")
            
            biases = {}
            for d in signal_data:
                bias = d.get('bias', 'unknown')
                biases[bias] = biases.get(bias, 0) + 1
            
            print(f"  • Biases: {biases}")
            
            # Échantillon de signaux
            print(f"  📝 Échantillon (premières 3):")
            for i, d in enumerate(signal_data[:3]):
                print(f"    {i+1}. Bias: {d.get('bias', 'N/A')}, Targets: {d.get('targets', [])}, Conf: {d.get('confidence', 0):.3f}")
        
        # Analyser les logs debug
        if debug_data:
            print(f"\n🎯 DEBUG: {len(debug_data)} entrées")
            
            messages = {}
            for d in debug_data:
                msg = d.get('msg', 'unknown')
                messages[msg] = messages.get(msg, 0) + 1
            
            print(f"  • Messages: {messages}")
        
        # Diagnostic final
        print(f"\n🔍 DIAGNOSTIC FINAL:")
        
        if len(vp_data) == 0 and len(vva_data) == 0:
            print("  ❌ PROBLÈME: Aucune donnée VP/VVA générée")
            print("     → Vérifier que l'étude MIA_VP_Signals_C3C4_Minimal est ajoutée")
            print("     → Vérifier les Study IDs sur Chart 4")
            print("     → Activer Debug Mode temporairement")
        elif len(vp_data) > 0 or len(vva_data) > 0:
            print("  ✅ SUCCÈS: Données VP/VVA générées")
            
            if len(signal_data) > 0:
                print("  ✅ SUCCÈS: Signaux VP générés")
            else:
                print("  ⚠️  ATTENTION: Pas de signaux VP (normal si pas de données current)")
        
        # Échantillon de données
        if vp_data or vva_data:
            print(f"\n📋 ÉCHANTILLON DE DONNÉES:")
            sample_data = (vp_data + vva_data + signal_data)[:3]
            for i, d in enumerate(sample_data):
                print(f"  {i+1}. {json.dumps(d, indent=2)}")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    test_chart4_vp()
