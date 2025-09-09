#!/usr/bin/env python3
"""
MIA Data Processor - Processeur de données propre pour MIA
Convertit les données brutes Sierra Chart en format structuré pour MIA
"""

import json
import sys
from datetime import datetime
from typing import Dict, List, Any, Optional
import pandas as pd

class MIADataProcessor:
    def __init__(self):
        self.clean_data = []
        self.current_bar = {}
        self.last_timestamp = None
        
    def process_file(self, input_file: str, output_file: str):
        """Traite un fichier JSONL et génère un fichier propre pour MIA"""
        print(f"🔄 Traitement de {input_file}...")
        
        with open(input_file, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                
                # Ignorer les lignes de debug
                if line.startswith('DEBUG_') or line.startswith('SG'):
                    continue
                    
                # Ignorer les lignes vides
                if not line:
                    continue
                    
                try:
                    data = json.loads(line)
                    self.process_record(data)
                except json.JSONDecodeError:
                    print(f"⚠️  Ligne {line_num} ignorée (JSON invalide): {line[:100]}...")
                    continue
                    
        self.save_clean_data(output_file)
        print(f"✅ Fichier propre généré: {output_file}")
        
    def process_record(self, data: Dict[str, Any]):
        """Traite un enregistrement de données"""
        record_type = data.get('type', '')
        timestamp = data.get('t', 0)
        
        # Grouper par timestamp pour créer des barres complètes
        if timestamp != self.last_timestamp:
            if self.current_bar:
                self.clean_data.append(self.current_bar.copy())
            self.current_bar = {
                'timestamp': timestamp,
                'datetime': self.timestamp_to_datetime(timestamp),
                'symbol': data.get('sym', ''),
                'bar_index': data.get('i', 0)
            }
            self.last_timestamp = timestamp
            
        # Traiter selon le type de données
        if record_type == 'basedata':
            self.process_basedata(data)
        elif record_type == 'numbers_bars_calculated_values_graph3':
            self.process_nbcv_graph3(data)
        elif record_type == 'numbers_bars_calculated_values_graph4':
            self.process_nbcv_graph4(data)
        elif record_type == 'vwap':
            self.process_vwap(data)
        elif record_type == 'volume_profile':
            self.process_volume_profile(data)
        elif record_type == 'vix':
            self.process_vix(data)
        elif record_type == 'depth':
            self.process_depth(data)
        elif record_type == 'trade':
            self.process_trade(data)
        elif record_type == 'quote':
            self.process_quote(data)
            
    def process_basedata(self, data: Dict[str, Any]):
        """Traite les données OHLCV de base"""
        self.current_bar.update({
            'open': data.get('o', 0),
            'high': data.get('h', 0),
            'low': data.get('l', 0),
            'close': data.get('c', 0),
            'volume': data.get('v', 0),
            'bid_volume': data.get('bidvol', 0),
            'ask_volume': data.get('askvol', 0)
        })
        
    def process_nbcv_graph3(self, data: Dict[str, Any]):
        """Traite les NBCV du Graph 3"""
        if data.get('ask', 0) > 0 or data.get('bid', 0) > 0:  # Ignorer les données vides
            self.current_bar.update({
                'nbcv_graph3_ask': data.get('ask', 0),
                'nbcv_graph3_bid': data.get('bid', 0),
                'nbcv_graph3_delta': data.get('delta', 0),
                'nbcv_graph3_trades': data.get('trades', 0),
                'nbcv_graph3_cumdelta': data.get('cumdelta', 0),
                'nbcv_graph3_total': data.get('total', 0)
            })
            
    def process_nbcv_graph4(self, data: Dict[str, Any]):
        """Traite les NBCV du Graph 4"""
        if data.get('ask', 0) > 0 or data.get('bid', 0) > 0:  # Ignorer les données vides
            self.current_bar.update({
                'nbcv_graph4_ask': data.get('ask', 0),
                'nbcv_graph4_bid': data.get('bid', 0),
                'nbcv_graph4_delta': data.get('delta', 0),
                'nbcv_graph4_trades': data.get('trades', 0),
                'nbcv_graph4_cumdelta': data.get('cumdelta', 0),
                'nbcv_graph4_total': data.get('total', 0)
            })
            
    def process_vwap(self, data: Dict[str, Any]):
        """Traite les données VWAP"""
        self.current_bar.update({
            'vwap_value': data.get('v', 0),
            'vwap_upper1': data.get('up1', 0),
            'vwap_lower1': data.get('dn1', 0),
            'vwap_upper2': data.get('up2', 0),
            'vwap_lower2': data.get('dn2', 0)
        })
        
    def process_volume_profile(self, data: Dict[str, Any]):
        """Traite les données Volume Profile"""
        self.current_bar.update({
            'vp_poc': data.get('poc', 0),
            'vp_vah': data.get('vah', 0),
            'vp_val': data.get('val', 0)
        })
        
    def process_vix(self, data: Dict[str, Any]):
        """Traite les données VIX"""
        self.current_bar['vix_value'] = data.get('last', 0)
        
    def process_depth(self, data: Dict[str, Any]):
        """Traite les données DOM (Depth of Market)"""
        side = data.get('side', '')
        level = data.get('lvl', 0)
        
        if side == 'BID':
            self.current_bar[f'dom_bid_level_{level}_price'] = data.get('price', 0)
            self.current_bar[f'dom_bid_level_{level}_size'] = data.get('size', 0)
        elif side == 'ASK':
            self.current_bar[f'dom_ask_level_{level}_price'] = data.get('price', 0)
            self.current_bar[f'dom_ask_level_{level}_size'] = data.get('size', 0)
            
    def process_trade(self, data: Dict[str, Any]):
        """Traite les données de trades"""
        if 'trades' not in self.current_bar:
            self.current_bar['trades'] = []
            
        self.current_bar['trades'].append({
            'price': data.get('px', 0),
            'quantity': data.get('qty', 0),
            'chart': data.get('chart', 0)
        })
        
    def process_quote(self, data: Dict[str, Any]):
        """Traite les données de quotes"""
        self.current_bar.update({
            'quote_bid': data.get('bid', 0),
            'quote_ask': data.get('ask', 0),
            'quote_bid_size': data.get('bq', 0),
            'quote_ask_size': data.get('aq', 0),
            'quote_spread': data.get('spread', 0),
            'quote_mid': data.get('mid', 0)
        })
        
    def timestamp_to_datetime(self, timestamp: float) -> str:
        """Convertit un timestamp en datetime lisible"""
        try:
            dt = datetime.fromtimestamp(timestamp)
            return dt.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        except:
            return str(timestamp)
            
    def save_clean_data(self, output_file: str):
        """Sauvegarde les données propres"""
        # Ajouter la dernière barre
        if self.current_bar:
            self.clean_data.append(self.current_bar)
            
        # Convertir en DataFrame pour un format plus propre
        df = pd.DataFrame(self.clean_data)
        
        # Sauvegarder en JSONL propre
        with open(output_file, 'w', encoding='utf-8') as f:
            for _, row in df.iterrows():
                # Nettoyer les valeurs NaN
                clean_row = row.dropna().to_dict()
                f.write(json.dumps(clean_row, ensure_ascii=False) + '\n')
                
        # Aussi sauvegarder en CSV pour analyse
        csv_file = output_file.replace('.jsonl', '.csv')
        df.to_csv(csv_file, index=False)
        print(f"📊 Fichier CSV généré: {csv_file}")
        
        # Statistiques
        print(f"📈 Statistiques:")
        print(f"   - Barres traitées: {len(self.clean_data)}")
        print(f"   - Colonnes: {len(df.columns)}")
        print(f"   - Taille: {len(df)} lignes")

def main():
    if len(sys.argv) != 3:
        print("Usage: python mia_data_processor.py <input_file.jsonl> <output_file.jsonl>")
        sys.exit(1)
        
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    processor = MIADataProcessor()
    processor.process_file(input_file, output_file)

if __name__ == "__main__":
    main()


