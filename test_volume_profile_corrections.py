#!/usr/bin/env python3
"""
Test des corrections Volume Profile appliquées
Validation de l'efficacité des corrections sur les données d'hier (20250912)
"""

import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import glob
import os
from typing import Dict, List, Tuple, Optional

class VolumeProfileCorrectionTester:
    def __init__(self, data_dir: str = "."):
        self.data_dir = data_dir
        self.results = {}
        
    def load_yesterday_data(self, date_str: str = "20250912") -> Dict[str, pd.DataFrame]:
        """Charge les données d'hier pour tester les corrections"""
        print(f"🔍 Chargement des données du {date_str}...")
        
        data = {}
        
        # Patterns de fichiers pour les données d'hier
        patterns = {
            'chart4_volume_profile': f"chart_4_volume_profile_{date_str}.jsonl",
            'chart4_vva': f"chart_4_vva_previous_{date_str}.jsonl",
            'chart4_vwap': f"chart_4_pvwap_{date_str}.jsonl",
            'chart3_basedata': f"chart_3_basedata_{date_str}.jsonl"
        }
        
        for key, pattern in patterns.items():
            files = glob.glob(os.path.join(self.data_dir, pattern))
            if files:
                file_path = files[0]
                try:
                    df = pd.read_json(file_path, lines=True)
                    data[key] = df
                    print(f"✅ {key}: {len(df)} lignes chargées")
                except Exception as e:
                    print(f"❌ Erreur chargement {key}: {e}")
            else:
                print(f"⚠️ Fichier non trouvé: {pattern}")
                
        return data
    
    def test_volume_profile_consistency(self, data: Dict[str, pd.DataFrame]) -> Dict:
        """Test de cohérence VAH/POC/VAL après corrections"""
        print("\n🔍 TEST COHÉRENCE VOLUME PROFILE")
        print("=" * 50)
        
        if 'chart4_volume_profile' not in data:
            return {"error": "Données Volume Profile non disponibles"}
            
        df = data['chart4_volume_profile']
        
        # Vérifier les colonnes disponibles
        print(f"Colonnes disponibles: {list(df.columns)}")
        
        # Identifier les colonnes VAH/POC/VAL
        vah_col = None
        poc_col = None
        val_col = None
        
        for col in df.columns:
            if 'vah' in col.lower():
                vah_col = col
            elif 'poc' in col.lower() or 'vpoc' in col.lower():
                poc_col = col
            elif 'val' in col.lower():
                val_col = col
                
        print(f"Colonnes identifiées - VAH: {vah_col}, POC: {poc_col}, VAL: {val_col}")
        
        if not all([vah_col, poc_col, val_col]):
            return {"error": f"Colonnes VAH/POC/VAL non trouvées. VAH: {vah_col}, POC: {poc_col}, VAL: {val_col}"}
        
        # Test de cohérence
        total_records = len(df)
        violations = 0
        valid_records = 0
        
        violation_details = []
        
        for idx, row in df.iterrows():
            vah = row[vah_col]
            poc = row[poc_col]
            val = row[val_col]
            
            # Vérifier la cohérence VAL ≤ POC ≤ VAH
            if pd.notna(vah) and pd.notna(poc) and pd.notna(val):
                if val <= poc <= vah:
                    valid_records += 1
                else:
                    violations += 1
                    violation_details.append({
                        'index': idx,
                        'timestamp': row.get('t', 'N/A'),
                        'vah': vah,
                        'poc': poc,
                        'val': val,
                        'violation_type': 'VAL>POC' if val > poc else 'POC>VAH' if poc > vah else 'Unknown'
                    })
        
        violation_rate = (violations / total_records * 100) if total_records > 0 else 0
        
        results = {
            'total_records': total_records,
            'valid_records': valid_records,
            'violations': violations,
            'violation_rate': violation_rate,
            'improvement_needed': violation_rate > 10,  # Seuil d'acceptabilité
            'violation_details': violation_details[:10]  # Premiers 10 exemples
        }
        
        print(f"📊 RÉSULTATS COHÉRENCE:")
        print(f"   Total enregistrements: {total_records:,}")
        print(f"   Enregistrements valides: {valid_records:,}")
        print(f"   Violations: {violations:,}")
        print(f"   Taux de violation: {violation_rate:.1f}%")
        
        if violation_rate > 10:
            print(f"❌ TAUX DE VIOLATION ÉLEVÉ ({violation_rate:.1f}%) - Corrections nécessaires")
        else:
            print(f"✅ TAUX DE VIOLATION ACCEPTABLE ({violation_rate:.1f}%)")
            
        return results
    
    def test_data_quality_improvements(self, data: Dict[str, pd.DataFrame]) -> Dict:
        """Test des améliorations de qualité des données"""
        print("\n🔍 TEST QUALITÉ DES DONNÉES")
        print("=" * 50)
        
        results = {}
        
        for key, df in data.items():
            print(f"\n📊 Analyse {key}:")
            
            # Vérifier les valeurs manquantes
            missing_data = df.isnull().sum()
            missing_pct = (missing_data / len(df) * 100)
            
            # Vérifier les valeurs aberrantes (outliers)
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            outliers = {}
            
            for col in numeric_cols:
                if col in ['t', 'i', 'chart', 'study']:  # Colonnes non-prix
                    continue
                    
                Q1 = df[col].quantile(0.25)
                Q3 = df[col].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                
                outlier_count = len(df[(df[col] < lower_bound) | (df[col] > upper_bound)])
                outlier_pct = (outlier_count / len(df) * 100) if len(df) > 0 else 0
                
                if outlier_pct > 5:  # Seuil d'alerte
                    outliers[col] = {
                        'count': outlier_count,
                        'percentage': outlier_pct,
                        'bounds': [lower_bound, upper_bound]
                    }
            
            results[key] = {
                'total_records': len(df),
                'missing_data': missing_pct.to_dict(),
                'outliers': outliers,
                'quality_score': self._calculate_quality_score(len(df), missing_pct, outliers)
            }
            
            print(f"   Enregistrements: {len(df):,}")
            print(f"   Score qualité: {results[key]['quality_score']:.1f}/100")
            
            if outliers:
                print(f"   ⚠️ Outliers détectés: {list(outliers.keys())}")
            else:
                print(f"   ✅ Aucun outlier significatif")
        
        return results
    
    def _calculate_quality_score(self, total_records: int, missing_pct: pd.Series, outliers: Dict) -> float:
        """Calcule un score de qualité de 0 à 100"""
        score = 100.0
        
        # Pénalité pour données manquantes
        avg_missing = missing_pct.mean()
        score -= min(avg_missing * 2, 30)  # Max 30 points de pénalité
        
        # Pénalité pour outliers
        outlier_penalty = len(outliers) * 5
        score -= min(outlier_penalty, 20)  # Max 20 points de pénalité
        
        # Bonus pour volume de données
        if total_records > 10000:
            score += 5
        elif total_records < 1000:
            score -= 10
            
        return max(0, min(100, score))
    
    def test_signal_generation_impact(self, data: Dict[str, pd.DataFrame]) -> Dict:
        """Test de l'impact sur la génération de signaux"""
        print("\n🔍 TEST IMPACT GÉNÉRATION SIGNAUX")
        print("=" * 50)
        
        if 'chart4_volume_profile' not in data or 'chart3_basedata' not in data:
            return {"error": "Données insuffisantes pour test de signaux"}
        
        vp_df = data['chart4_volume_profile']
        base_df = data['chart3_basedata']
        
        # Simuler la génération de signaux Volume Profile
        signals = []
        
        for idx, row in vp_df.iterrows():
            if pd.notna(row.get('vah')) and pd.notna(row.get('poc')) and pd.notna(row.get('val')):
                vah = row['vah']
                poc = row['poc']
                val = row['val']
                
                # Signal basé sur la position du prix par rapport au Volume Profile
                timestamp = row.get('t', 0)
                
                # Trouver le prix correspondant
                matching_base = base_df[base_df['t'] == timestamp]
                if not matching_base.empty:
                    price = matching_base.iloc[0].get('c', 0)
                    
                    if price > 0:
                        # Calculer la position relative
                        if price > vah:
                            signal_type = "ABOVE_VAH"
                            strength = min((price - vah) / (vah - poc) * 100, 200)
                        elif price < val:
                            signal_type = "BELOW_VAL"
                            strength = min((val - price) / (poc - val) * 100, 200)
                        elif poc - val > 0:
                            signal_type = "IN_VALUE_AREA"
                            strength = 100 - abs(price - poc) / (vah - val) * 100
                        else:
                            signal_type = "INVALID_VP"
                            strength = 0
                        
                        signals.append({
                            'timestamp': timestamp,
                            'price': price,
                            'vah': vah,
                            'poc': poc,
                            'val': val,
                            'signal_type': signal_type,
                            'strength': strength
                        })
        
        # Analyser les signaux générés
        signal_df = pd.DataFrame(signals)
        
        if len(signal_df) == 0:
            return {"error": "Aucun signal généré"}
        
        signal_counts = signal_df['signal_type'].value_counts()
        avg_strength = signal_df['strength'].mean()
        
        results = {
            'total_signals': len(signal_df),
            'signal_distribution': signal_counts.to_dict(),
            'average_strength': avg_strength,
            'valid_signals_pct': (len(signal_df[signal_df['signal_type'] != 'INVALID_VP']) / len(signal_df) * 100),
            'signal_quality': 'GOOD' if avg_strength > 50 else 'POOR'
        }
        
        print(f"📊 SIGNAUX GÉNÉRÉS:")
        print(f"   Total signaux: {results['total_signals']:,}")
        print(f"   Signaux valides: {results['valid_signals_pct']:.1f}%")
        print(f"   Force moyenne: {results['average_strength']:.1f}")
        print(f"   Qualité: {results['signal_quality']}")
        
        for signal_type, count in results['signal_distribution'].items():
            print(f"   {signal_type}: {count:,}")
        
        return results
    
    def run_comprehensive_test(self, date_str: str = "20250912") -> Dict:
        """Lance le test complet des corrections"""
        print("🚀 DÉMARRAGE TEST COMPLET DES CORRECTIONS VOLUME PROFILE")
        print("=" * 70)
        
        # Charger les données
        data = self.load_yesterday_data(date_str)
        
        if not data:
            return {"error": "Aucune donnée chargée"}
        
        # Tests
        results = {
            'test_date': date_str,
            'data_loaded': list(data.keys()),
            'volume_profile_consistency': self.test_volume_profile_consistency(data),
            'data_quality': self.test_data_quality_improvements(data),
            'signal_generation': self.test_signal_generation_impact(data)
        }
        
        # Résumé final
        print("\n" + "=" * 70)
        print("📋 RÉSUMÉ FINAL DES TESTS")
        print("=" * 70)
        
        vp_test = results['volume_profile_consistency']
        if 'violation_rate' in vp_test:
            print(f"✅ Volume Profile: {vp_test['violation_rate']:.1f}% violations")
        
        quality_scores = [r['quality_score'] for r in results['data_quality'].values() if 'quality_score' in r]
        if quality_scores:
            avg_quality = np.mean(quality_scores)
            print(f"✅ Qualité données: {avg_quality:.1f}/100")
        
        signal_test = results['signal_generation']
        if 'total_signals' in signal_test:
            print(f"✅ Signaux générés: {signal_test['total_signals']:,}")
        
        # Sauvegarder les résultats
        with open(f'volume_profile_test_results_{date_str}.json', 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"\n💾 Résultats sauvegardés: volume_profile_test_results_{date_str}.json")
        
        return results

def main():
    """Fonction principale"""
    tester = VolumeProfileCorrectionTester()
    results = tester.run_comprehensive_test("20250912")
    
    if 'error' in results:
        print(f"❌ Erreur: {results['error']}")
        return 1
    
    print("\n🎯 Test terminé avec succès!")
    return 0

if __name__ == "__main__":
    exit(main())


