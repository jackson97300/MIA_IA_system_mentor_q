#!/usr/bin/env python3
"""
MIA Data Consolidator - Consolide toutes les données MIA en un seul JSON structuré
Version: 1.0
Objectif: Transformer les lignes JSON séparées en un seul objet JSON consolidé par timestamp
"""

import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Any, Optional
from collections import defaultdict

class MIADataConsolidator:
    """Consolide les données MIA depuis le format JSONL vers un JSON structuré"""
    
    def __init__(self, input_file: str):
        self.input_file = input_file
        self.consolidated_data = defaultdict(dict)
        
    def parse_jsonl(self) -> List[Dict[str, Any]]:
        """Lit le fichier JSONL et parse chaque ligne"""
        data_lines = []
        
        try:
            with open(self.input_file, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line:
                        continue
                    
                    try:
                        data = json.loads(line)
                        data_lines.append(data)
                    except json.JSONDecodeError as e:
                        print(f"⚠️ Erreur ligne {line_num}: {e}")
                        continue
                        
        except FileNotFoundError:
            print(f"❌ Fichier non trouvé: {self.input_file}")
            return []
        except Exception as e:
            print(f"❌ Erreur lecture fichier: {e}")
            return []
            
        print(f"✅ {len(data_lines)} lignes JSON parsées")
        return data_lines
    
    def consolidate_by_timestamp(self, data_lines: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Consolide toutes les données par timestamp"""
        
        for data in data_lines:
            timestamp = data.get('t', 0)
            if not timestamp:
                continue
                
            # Initialiser la structure si pas encore créée
            if timestamp not in self.consolidated_data:
                self.consolidated_data[timestamp] = {
                    'timestamp': timestamp,
                    'symbol': data.get('sym', ''),
                    'bar': data.get('bar', data.get('i', 0)),
                    'seq': data.get('seq', 0),
                    'data_types': []
                }
            
            # Ajouter le type de données
            data_type = data.get('type', 'unknown')
            self.consolidated_data[timestamp]['data_types'].append(data_type)
            
            # Consolider selon le type
            if data_type == 'basedata':
                self._consolidate_basedata(timestamp, data)
            elif data_type == 'ohlc_graph4':
                self._consolidate_ohlc_graph4(timestamp, data)
            elif data_type == 'volume_profile':
                self._consolidate_volume_profile(timestamp, data)
            elif data_type == 'vva':
                self._consolidate_vva(timestamp, data)
            elif data_type == 'volume_profile_previous':
                self._consolidate_volume_profile_previous(timestamp, data)
            elif data_type == 'vwap_current':
                self._consolidate_vwap_current(timestamp, data)
            elif data_type == 'vwap_previous':
                self._consolidate_vwap_previous(timestamp, data)
            elif data_type == 'volume_profile_graph3':
                self._consolidate_volume_profile_graph3(timestamp, data)
            elif data_type == 'vva_graph3':
                self._consolidate_vva_graph3(timestamp, data)
            elif data_type == 'volume_profile_previous_graph3':
                self._consolidate_volume_profile_previous_graph3(timestamp, data)
            elif data_type == 'nbcv':
                self._consolidate_nbcv(timestamp, data)
            elif data_type == 'quote':
                self._consolidate_quote(timestamp, data)
            elif data_type == 'trade':
                self._consolidate_trade(timestamp, data)
            elif data_type == 'vap':
                self._consolidate_vap(timestamp, data)
            elif data_type == 'depth':
                self._consolidate_depth(timestamp, data)
            elif data_type == 'pvwap':
                self._consolidate_pvwap(timestamp, data)
            elif data_type == 'vix':
                self._consolidate_vix(timestamp, data)
        
        return dict(self.consolidated_data)
    
    def _consolidate_basedata(self, timestamp: float, data: Dict[str, Any]):
        """Consolide les données de base"""
        self.consolidated_data[timestamp]['basedata'] = {
            'open': data.get('o', 0),
            'high': data.get('h', 0),
            'low': data.get('l', 0),
            'close': data.get('c', 0),
            'volume': data.get('v', 0),
            'bidvol': data.get('bidvol', 0),
            'askvol': data.get('askvol', 0)
        }
    
    def _consolidate_ohlc_graph4(self, timestamp: float, data: Dict[str, Any]):
        """Consolide les données OHLC du Graph 4"""
        self.consolidated_data[timestamp]['graph4'] = {
            'dt': data.get('dt_g4', 0),
            'open': data.get('open', 0),
            'high': data.get('high', 0),
            'low': data.get('low', 0),
            'close': data.get('close', 0)
        }
    
    def _consolidate_volume_profile(self, timestamp: float, data: Dict[str, Any]):
        """Consolide le Volume Profile du Graph 4"""
        self.consolidated_data[timestamp]['vp_g4'] = {
            'poc': data.get('poc', 0),
            'vah': data.get('vah', 0),
            'val': data.get('val', 0),
            'study_id': data.get('study_id', 0),
            'corrected': data.get('corrected', False),
            'corrections': data.get('corrections', 'none')
        }
    
    def _consolidate_vva(self, timestamp: float, data: Dict[str, Any]):
        """Consolide le VVA du Graph 4"""
        self.consolidated_data[timestamp]['vva_g4'] = {
            'vah': data.get('vah', 0),
            'val': data.get('val', 0),
            'vpoc': data.get('vpoc', 0),
            'corrected': data.get('corrected', False)
        }
    
    def _consolidate_volume_profile_previous(self, timestamp: float, data: Dict[str, Any]):
        """Consolide le Volume Profile précédent du Graph 4"""
        self.consolidated_data[timestamp]['vpp_g4'] = {
            'ppoc': data.get('ppoc', 0),
            'pvah': data.get('pvah', 0),
            'pval': data.get('pval', 0),
            'study_id': data.get('study_id', 0),
            'corrected': data.get('corrected', False),
            'corrections': data.get('corrections', 'none')
        }
    
    def _consolidate_vwap_current(self, timestamp: float, data: Dict[str, Any]):
        """Consolide le VWAP actuel du Graph 4"""
        self.consolidated_data[timestamp]['vwap_g4'] = {
            'vwap': data.get('vwap', 0),
            's_plus_1': data.get('s_plus_1', 0),
            's_minus_1': data.get('s_minus_1', 0),
            's_plus_2': data.get('s_plus_2', 0),
            's_minus_2': data.get('s_minus_2', 0),
            'study_id': data.get('study_id', 0)
        }
    
    def _consolidate_vwap_previous(self, timestamp: float, data: Dict[str, Any]):
        """Consolide le VWAP précédent"""
        self.consolidated_data[timestamp]['vwap_previous'] = {
            'pvwap': data.get('pvwap', 0),
            'psd_plus_1': data.get('psd_plus_1', 0),
            'psd_minus_1': data.get('psd_minus_1', 0),
            'up1': data.get('up1', 0),
            'dn1': data.get('dn1', 0),
            'study_id': data.get('study_id', 0)
        }
    
    def _consolidate_volume_profile_graph3(self, timestamp: float, data: Dict[str, Any]):
        """Consolide le Volume Profile du Graph 3"""
        if 'graph3' not in self.consolidated_data[timestamp]:
            self.consolidated_data[timestamp]['graph3'] = {}
            
        self.consolidated_data[timestamp]['graph3']['vp'] = {
            'poc': data.get('poc', 0),
            'vah': data.get('vah', 0),
            'val': data.get('pval', 0),
            'study_id': data.get('study_id', 0),
            'corrected': data.get('corrected', False),
            'corrections': data.get('corrections', 'none')
        }
    
    def _consolidate_vva_graph3(self, timestamp: float, data: Dict[str, Any]):
        """Consolide le VVA du Graph 3"""
        if 'graph3' not in self.consolidated_data[timestamp]:
            self.consolidated_data[timestamp]['graph3'] = {}
            
        self.consolidated_data[timestamp]['graph3']['vva'] = {
            'vah': data.get('vah', 0),
            'val': data.get('pval', 0),
            'vpoc': data.get('vpoc', 0),
            'corrected': data.get('corrected', False)
        }
    
    def _consolidate_volume_profile_previous_graph3(self, timestamp: float, data: Dict[str, Any]):
        """Consolide le Volume Profile précédent du Graph 3"""
        if 'graph3' not in self.consolidated_data[timestamp]:
            self.consolidated_data[timestamp]['graph3'] = {}
            
        self.consolidated_data[timestamp]['graph3']['vpp'] = {
            'ppoc': data.get('ppoc', 0),
            'pvah': data.get('pvah', 0),
            'pval': data.get('pval', 0),
            'study_id': data.get('study_id', 0),
            'corrected': data.get('corrected', False),
            'corrections': data.get('corrections', 'none')
        }
    
    def _consolidate_nbcv(self, timestamp: float, data: Dict[str, Any]):
        """Consolide les données NBCV"""
        self.consolidated_data[timestamp]['nbcv'] = {
            'ask': data.get('ask', 0),
            'bid': data.get('bid', 0),
            'delta': data.get('delta', 0),
            'trades': data.get('trades', 0),
            'cumdelta': data.get('cumdelta', 0),
            'total': data.get('total', 0)
        }
    
    def _consolidate_quote(self, timestamp: float, data: Dict[str, Any]):
        """Consolide les quotes"""
        self.consolidated_data[timestamp]['quote'] = {
            'bid': data.get('bid', 0),
            'ask': data.get('ask', 0),
            'spread': data.get('spread', 0),
            'mid': data.get('mid', 0),
            'bq': data.get('bq', 0),
            'aq': data.get('aq', 0),
            'kind': data.get('kind', ''),
            'chart': data.get('chart', 0)
        }
    
    def _consolidate_trade(self, timestamp: float, data: Dict[str, Any]):
        """Consolide les trades"""
        self.consolidated_data[timestamp]['trade'] = {
            'px': data.get('px', 0),
            'qty': data.get('qty', 0),
            'source': data.get('source', ''),
            'chart': data.get('chart', 0)
        }
    
    def _consolidate_vap(self, timestamp: float, data: Dict[str, Any]):
        """Consolide les données VAP"""
        if 'vap' not in self.consolidated_data[timestamp]:
            self.consolidated_data[timestamp]['vap'] = []
            
        self.consolidated_data[timestamp]['vap'].append({
            'price': data.get('price', 0),
            'vol': data.get('vol', 0),
            'bar': data.get('bar', 0),
            'k': data.get('k', 0)
        })
    
    def _consolidate_depth(self, timestamp: float, data: Dict[str, Any]):
        """Consolide les données de profondeur (DOM)"""
        if 'depth' not in self.consolidated_data[timestamp]:
            self.consolidated_data[timestamp]['depth'] = []
            
        self.consolidated_data[timestamp]['depth'].append({
            'side': data.get('side', ''),
            'lvl': data.get('lvl', 0),
            'price': data.get('price', 0),
            'size': data.get('size', 0),
            'group': data.get('group', 0)
        })
    
    def _consolidate_pvwap(self, timestamp: float, data: Dict[str, Any]):
        """Consolide le PVWAP"""
        self.consolidated_data[timestamp]['pvwap'] = {
            'pvwap': data.get('pvwap', 0),
            'prev_start': data.get('prev_start', 0),
            'prev_end': data.get('prev_end', 0),
            'up1': data.get('up1', 0),
            'dn1': data.get('dn1', 0),
            'up2': data.get('up2', 0),
            'dn2': data.get('dn2', 0),
            'up3': data.get('up3', 0),
            'dn3': data.get('dn3', 0),
            'up4': data.get('up4', 0),
            'dn4': data.get('dn4', 0)
        }
    
    def _consolidate_vix(self, timestamp: float, data: Dict[str, Any]):
        """Consolide les données VIX"""
        self.consolidated_data[timestamp]['vix'] = {
            'last': data.get('last', 0),
            'chart': data.get('chart', 0)
        }
    
    def save_consolidated_json(self, output_file: str):
        """Sauvegarde les données consolidées en JSON"""
        try:
            # Convertir en liste et trier par timestamp
            consolidated_list = list(self.consolidated_data.values())
            consolidated_list.sort(key=lambda x: x['timestamp'])
            
            # Créer la structure finale
            final_data = {
                'metadata': {
                    'generated_at': datetime.now().isoformat(),
                    'source_file': self.input_file,
                    'total_records': len(consolidated_list),
                    'data_types_found': list(set([dt for record in consolidated_list for dt in record.get('data_types', [])]))
                },
                'data': consolidated_list
            }
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(final_data, f, indent=2, ensure_ascii=False)
                
            print(f"✅ Données consolidées sauvegardées: {output_file}")
            print(f"📊 {len(consolidated_list)} enregistrements consolidés")
            
        except Exception as e:
            print(f"❌ Erreur sauvegarde: {e}")
    
    def process(self, output_file: str):
        """Traite le fichier et génère la sortie consolidée"""
        print(f"🔄 Traitement du fichier: {self.input_file}")
        
        # Lire et parser le JSONL
        data_lines = self.parse_jsonl()
        if not data_lines:
            return False
        
        # Consolider par timestamp
        print("🔄 Consolidation des données par timestamp...")
        consolidated = self.consolidate_by_timestamp(data_lines)
        
        # Sauvegarder
        self.save_consolidated_json(output_file)
        return True

def main():
    """Fonction principale"""
    if len(sys.argv) != 2:
        print("Usage: python consolidate_mia_data.py <fichier_jsonl>")
        print("Exemple: python consolidate_mia_data.py chart_4_20250109.jsonl")
        sys.exit(1)
    
    input_file = sys.argv[1]
    
    if not os.path.exists(input_file):
        print(f"❌ Fichier non trouvé: {input_file}")
        sys.exit(1)
    
    # Créer le nom de sortie
    base_name = os.path.splitext(input_file)[0]
    output_file = f"{base_name}_consolidated.json"
    
    # Traiter
    consolidator = MIADataConsolidator(input_file)
    success = consolidator.process(output_file)
    
    if success:
        print(f"\n🎉 Consolidation terminée avec succès!")
        print(f"📁 Fichier de sortie: {output_file}")
    else:
        print("\n❌ Échec de la consolidation")
        sys.exit(1)

if __name__ == "__main__":
    main()




