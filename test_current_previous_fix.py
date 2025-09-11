#!/usr/bin/env python3
"""
Test pour vérifier que le fix Current/Previous fonctionne
"""

import json
import sys

def test_current_previous_fix():
    print("=" * 80)
    print("🧪 TEST FIX CURRENT/PREVIOUS")
    print("=" * 80)
    
    # Données fournies par l'utilisateur
    data_lines = [
        '{"t":45910.715069,"type":"volume_profile","chart":3,"bar":1268,"scope":"current","poc":6565.25000000,"vah":6547.50000000,"val":6507.25000000,"study_id":9}',
        '{"t":45910.715069,"type":"vva","chart":3,"i":1268,"vah":6547.50000000,"val":6507.25000000,"vpoc":6565.25000000}',
        '{"t":45910.715069,"type":"vp_signal","chart":3,"i":1268,"last":6547.75000000,"vah":6547.50000000,"val":6507.25000000,"vpoc":6565.25000000,"bias":"breakout_up","targets":[6565.25000000,6565.25000000]}',
        '{"t":45910.715069,"type":"volume_profile","chart":3,"bar":1268,"scope":"previous","poc":6565.25000000,"vah":6547.50000000,"val":6507.25000000,"study_id":8}'
    ]
    
    print("📊 ANALYSE DES DONNÉES:")
    
    current_vp = None
    previous_vp = None
    
    for i, line in enumerate(data_lines, 1):
        try:
            data = json.loads(line)
            print(f"\n{i}. {data.get('type', 'unknown')}:")
            
            if data.get('type') == 'volume_profile':
                scope = data.get('scope', 'unknown')
                print(f"   Scope: {scope}")
                print(f"   Study ID: {data.get('study_id', 'N/A')}")
                print(f"   POC: {data.get('poc', 0):.2f}")
                print(f"   VAH: {data.get('vah', 0):.2f}")
                print(f"   VAL: {data.get('val', 0):.2f}")
                print(f"   Bar: {data.get('bar', 'N/A')}")
                print(f"   Timestamp: {data.get('t', 0):.6f}")
                
                if scope == 'current':
                    current_vp = data
                elif scope == 'previous':
                    previous_vp = data
                    
            elif data.get('type') == 'vva':
                print(f"   VPOC: {data.get('vpoc', 0):.2f}")
                print(f"   VAH: {data.get('vah', 0):.2f}")
                print(f"   VAL: {data.get('val', 0):.2f}")
                print(f"   Index: {data.get('i', 'N/A')}")
                
            elif data.get('type') == 'vp_signal':
                print(f"   Bias: {data.get('bias', 'N/A')}")
                print(f"   Targets: {data.get('targets', [])}")
                print(f"   Last: {data.get('last', 0):.2f}")
                print(f"   Confidence: {data.get('confidence', 0):.3f}")
                
        except json.JSONDecodeError:
            print(f"   ❌ Erreur JSON")
    
    # Vérification Current vs Previous
    print(f"\n🔍 VÉRIFICATION CURRENT vs PREVIOUS:")
    
    if current_vp and previous_vp:
        print(f"✅ Current et Previous trouvés")
        
        # Vérifier les valeurs
        current_poc = current_vp.get('poc', 0)
        current_vah = current_vp.get('vah', 0)
        current_val = current_vp.get('val', 0)
        
        previous_poc = previous_vp.get('poc', 0)
        previous_vah = previous_vp.get('vah', 0)
        previous_val = previous_vp.get('val', 0)
        
        print(f"📊 COMPARAISON:")
        print(f"   Current:  POC={current_poc:.2f}, VAH={current_vah:.2f}, VAL={current_val:.2f}")
        print(f"   Previous: POC={previous_poc:.2f}, VAH={previous_vah:.2f}, VAL={previous_val:.2f}")
        
        # Vérifier si identiques
        if (current_poc == previous_poc and 
            current_vah == previous_vah and 
            current_val == previous_val):
            print(f"❌ PROBLÈME: Current = Previous (valeurs identiques)")
            print(f"   → Le fix n'est pas appliqué ou ne fonctionne pas")
        else:
            print(f"✅ SUCCÈS: Current ≠ Previous (valeurs différentes)")
        
        # Vérifier les Study IDs
        current_id = current_vp.get('study_id', 0)
        previous_id = previous_vp.get('study_id', 0)
        
        print(f"📋 STUDY IDs:")
        print(f"   Current: {current_id}")
        print(f"   Previous: {previous_id}")
        
        if current_id == previous_id:
            print(f"⚠️  ATTENTION: Même Study ID pour Current et Previous")
        else:
            print(f"✅ Study IDs différents")
        
        # Vérifier les timestamps
        current_t = current_vp.get('t', 0)
        previous_t = previous_vp.get('t', 0)
        
        print(f"⏰ TIMESTAMPS:")
        print(f"   Current: {current_t:.6f}")
        print(f"   Previous: {previous_t:.6f}")
        
        if current_t == previous_t:
            print(f"⚠️  ATTENTION: Même timestamp pour Current et Previous")
        else:
            print(f"✅ Timestamps différents")
    
    else:
        print(f"❌ Current ou Previous manquant")
    
    # Diagnostic
    print(f"\n🔍 DIAGNOSTIC:")
    print(f"1. 📍 Vérifier que le script MIA_VP_Fixed_Current_Previous.cpp est compilé")
    print(f"2. 📍 Vérifier que l'étude est ajoutée au Chart 3")
    print(f"3. 📍 Vérifier que les Study IDs 8,9 sont corrects")
    print(f"4. 📍 Attendre une nouvelle barre pour voir la différence")
    
    print(f"\n💡 SOLUTIONS:")
    print(f"1. ✅ Recompiler le script corrigé")
    print(f"2. ✅ Ajouter l'étude au Chart 3")
    print(f"3. ✅ Activer Debug Mode = 1 temporairement")
    print(f"4. ✅ Attendre plusieurs barres pour voir l'évolution")

if __name__ == "__main__":
    test_current_previous_fix()
