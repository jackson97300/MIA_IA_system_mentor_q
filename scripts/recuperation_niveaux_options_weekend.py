#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Récupération Niveaux Options Weekend - MIA_IA System
Récupère les derniers niveaux options de vendredi à la fermeture
"""

import sys
import os
import json
import time
from datetime import datetime, timedelta
import requests
import urllib3

# Désactiver les warnings SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Ajouter le chemin du projet
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.ibkr_beta_connector import IBKRBetaConnector, IBKRBetaConfig

class RecuperationNiveauxOptionsWeekend:
    def __init__(self):
        self.connector = None
        self.weekend_data = {
            'timestamp': datetime.now().isoformat(),
            'friday_close': None,
            'spx_levels': {},
            'es_levels': {},
            'gamma_exposure': {},
            'success': False,
            'errors': []
        }
    
    def get_friday_close_time(self):
        """Déterminer l'heure de fermeture du vendredi"""
        today = datetime.now()
        
        # Trouver le dernier vendredi
        days_since_friday = (today.weekday() - 4) % 7
        if days_since_friday == 0:  # Aujourd'hui est vendredi
            friday = today
        else:
            friday = today - timedelta(days=days_since_friday)
        
        # Heure de fermeture US (16:00 EST = 21:00 UTC en hiver, 20:00 UTC en été)
        friday_close = friday.replace(hour=21, minute=0, second=0, microsecond=0)
        
        print(f"📅 Dernier vendredi: {friday.strftime('%Y-%m-%d')}")
        print(f"🕐 Heure de fermeture: {friday_close.strftime('%Y-%m-%d %H:%M:%S')}")
        
        self.weekend_data['friday_close'] = friday_close.isoformat()
        return friday_close
    
    def connect_ibkr(self):
        """Connexion IBKR"""
        print("🔗 Connexion IBKR...")
        
        try:
            config = IBKRBetaConfig()
            self.connector = IBKRBetaConnector(config)
            
            if self.connector.connect():
                print("✅ Connexion IBKR réussie")
                return True
            else:
                print("❌ Échec connexion IBKR")
                return False
                
        except Exception as e:
            print(f"❌ Erreur connexion: {e}")
            self.weekend_data['errors'].append(f"Connexion: {str(e)}")
            return False
    
    def get_spx_options_levels(self):
        """Récupérer niveaux options SPX"""
        print("🎯 Récupération niveaux options SPX...")
        
        try:
            if not self.connector:
                print("❌ Connecteur non initialisé")
                return False
            
            # Récupération données options SPX
            spx_data = self.connector.get_options_data('SPX')
            
            if spx_data:
                print("✅ Données SPX récupérées")
                
                # Extraire niveaux importants
                levels = {
                    'current_price': spx_data.get('current_price'),
                    'gamma_exposure': spx_data.get('gamma_exposure', {}),
                    'put_call_ratio': spx_data.get('put_call_ratio'),
                    'implied_volatility': spx_data.get('implied_volatility'),
                    'strike_levels': spx_data.get('strike_levels', [])
                }
                
                self.weekend_data['spx_levels'] = levels
                
                print(f"   - Prix actuel: {levels['current_price']}")
                print(f"   - Put/Call Ratio: {levels['put_call_ratio']}")
                print(f"   - Niveaux strike: {len(levels['strike_levels'])}")
                
                return True
            else:
                print("❌ Données SPX non disponibles")
                return False
                
        except Exception as e:
            print(f"❌ Erreur SPX: {e}")
            self.weekend_data['errors'].append(f"SPX: {str(e)}")
            return False
    
    def get_es_options_levels(self):
        """Récupérer niveaux options ES"""
        print("📈 Récupération niveaux options ES...")
        
        try:
            if not self.connector:
                print("❌ Connecteur non initialisé")
                return False
            
            # Récupération données options ES
            es_data = self.connector.get_options_data('ES')
            
            if es_data:
                print("✅ Données ES récupérées")
                
                # Extraire niveaux importants
                levels = {
                    'current_price': es_data.get('current_price'),
                    'gamma_exposure': es_data.get('gamma_exposure', {}),
                    'put_call_ratio': es_data.get('put_call_ratio'),
                    'implied_volatility': es_data.get('implied_volatility'),
                    'strike_levels': es_data.get('strike_levels', [])
                }
                
                self.weekend_data['es_levels'] = levels
                
                print(f"   - Prix actuel: {levels['current_price']}")
                print(f"   - Put/Call Ratio: {levels['put_call_ratio']}")
                print(f"   - Niveaux strike: {len(levels['strike_levels'])}")
                
                return True
            else:
                print("❌ Données ES non disponibles")
                return False
                
        except Exception as e:
            print(f"❌ Erreur ES: {e}")
            self.weekend_data['errors'].append(f"ES: {str(e)}")
            return False
    
    def calculate_gamma_exposure(self):
        """Calculer exposition gamma"""
        print("⚡ Calcul exposition gamma...")
        
        try:
            gamma_data = {
                'spx': self.weekend_data['spx_levels'].get('gamma_exposure', {}),
                'es': self.weekend_data['es_levels'].get('gamma_exposure', {})
            }
            
            # Calculer niveaux GEX1 et GEX2
            gex_levels = {
                'gex1_spx': gamma_data['spx'].get('gex1', 'N/A'),
                'gex2_spx': gamma_data['spx'].get('gex2', 'N/A'),
                'gex1_es': gamma_data['es'].get('gex1', 'N/A'),
                'gex2_es': gamma_data['es'].get('gex2', 'N/A')
            }
            
            self.weekend_data['gamma_exposure'] = gex_levels
            
            print("✅ Exposition gamma calculée")
            print(f"   - SPX GEX1: {gex_levels['gex1_spx']}")
            print(f"   - SPX GEX2: {gex_levels['gex2_spx']}")
            print(f"   - ES GEX1: {gex_levels['gex1_es']}")
            print(f"   - ES GEX2: {gex_levels['gex2_es']}")
            
            return True
            
        except Exception as e:
            print(f"❌ Erreur gamma: {e}")
            self.weekend_data['errors'].append(f"Gamma: {str(e)}")
            return False
    
    def generate_weekend_analysis(self):
        """Générer analyse weekend"""
        print("📊 Génération analyse weekend...")
        
        try:
            analysis = {
                'market_sentiment': self.analyze_market_sentiment(),
                'key_levels': self.identify_key_levels(),
                'weekend_strategy': self.generate_weekend_strategy(),
                'risk_assessment': self.assess_weekend_risk()
            }
            
            self.weekend_data['analysis'] = analysis
            
            print("✅ Analyse weekend générée")
            print(f"   - Sentiment: {analysis['market_sentiment']}")
            print(f"   - Niveaux clés: {len(analysis['key_levels'])}")
            print(f"   - Stratégie: {analysis['weekend_strategy']['type']}")
            
            return True
            
        except Exception as e:
            print(f"❌ Erreur analyse: {e}")
            self.weekend_data['errors'].append(f"Analyse: {str(e)}")
            return False
    
    def analyze_market_sentiment(self):
        """Analyser sentiment marché"""
        try:
            spx_pcr = self.weekend_data['spx_levels'].get('put_call_ratio', 1.0)
            es_pcr = self.weekend_data['es_levels'].get('put_call_ratio', 1.0)
            
            if spx_pcr > 1.2 and es_pcr > 1.2:
                return "BEARISH"
            elif spx_pcr < 0.8 and es_pcr < 0.8:
                return "BULLISH"
            else:
                return "NEUTRAL"
                
        except:
            return "UNKNOWN"
    
    def identify_key_levels(self):
        """Identifier niveaux clés"""
        try:
            levels = []
            
            # Niveaux SPX
            spx_price = self.weekend_data['spx_levels'].get('current_price')
            if spx_price:
                levels.append({
                    'symbol': 'SPX',
                    'price': spx_price,
                    'type': 'current'
                })
            
            # Niveaux ES
            es_price = self.weekend_data['es_levels'].get('current_price')
            if es_price:
                levels.append({
                    'symbol': 'ES',
                    'price': es_price,
                    'type': 'current'
                })
            
            return levels
            
        except:
            return []
    
    def generate_weekend_strategy(self):
        """Générer stratégie weekend"""
        try:
            sentiment = self.analyze_market_sentiment()
            
            if sentiment == "BULLISH":
                return {
                    'type': 'BULLISH_BREAKOUT',
                    'description': 'Préparation breakout haussier',
                    'key_levels': 'Focus sur résistances'
                }
            elif sentiment == "BEARISH":
                return {
                    'type': 'BEARISH_BREAKDOWN',
                    'description': 'Préparation breakdown baissier',
                    'key_levels': 'Focus sur supports'
                }
            else:
                return {
                    'type': 'NEUTRAL_RANGE',
                    'description': 'Trading range prévu',
                    'key_levels': 'Support et résistance'
                }
                
        except:
            return {
                'type': 'UNKNOWN',
                'description': 'Analyse incomplète',
                'key_levels': 'N/A'
            }
    
    def assess_weekend_risk(self):
        """Évaluer risque weekend"""
        try:
            risk_factors = []
            
            # Volatilité implicite
            spx_iv = self.weekend_data['spx_levels'].get('implied_volatility', 0)
            if spx_iv > 25:
                risk_factors.append('HIGH_IV')
            
            # Put/Call Ratio
            spx_pcr = self.weekend_data['spx_levels'].get('put_call_ratio', 1.0)
            if spx_pcr > 1.5:
                risk_factors.append('HIGH_PUT_ACTIVITY')
            
            if len(risk_factors) > 1:
                return 'HIGH'
            elif len(risk_factors) == 1:
                return 'MEDIUM'
            else:
                return 'LOW'
                
        except:
            return 'UNKNOWN'
    
    def save_weekend_data(self):
        """Sauvegarder données weekend"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"data/options_snapshots/weekend_levels_{timestamp}.json"
        
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.weekend_data, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Données weekend sauvegardées: {filename}")
        return filename
    
    def run_weekend_recuperation(self):
        """Exécuter récupération weekend complète"""
        print("🏆 RÉCUPÉRATION NIVEAUX OPTIONS WEEKEND")
        print("=" * 50)
        
        # 1. Déterminer heure fermeture vendredi
        self.get_friday_close_time()
        
        # 2. Connexion IBKR
        if not self.connect_ibkr():
            print("❌ Impossible de continuer sans connexion IBKR")
            return False
        
        # 3. Récupération données
        success_count = 0
        tests = [
            ('SPX Options', self.get_spx_options_levels),
            ('ES Options', self.get_es_options_levels),
            ('Gamma Exposure', self.calculate_gamma_exposure),
            ('Weekend Analysis', self.generate_weekend_analysis)
        ]
        
        for test_name, test_func in tests:
            print(f"\n🔍 {test_name}...")
            if test_func():
                success_count += 1
            time.sleep(1)
        
        # 4. Sauvegarder résultats
        filename = self.save_weekend_data()
        
        # 5. Résultats finaux
        print("\n" + "=" * 50)
        print("📊 RÉSULTATS RÉCUPÉRATION WEEKEND")
        print("=" * 50)
        
        success_rate = (success_count / len(tests)) * 100
        print(f"✅ Tests réussis: {success_count}/{len(tests)}")
        print(f"📊 Taux de succès: {success_rate:.1f}%")
        
        if success_rate >= 75:
            print("🎉 RÉCUPÉRATION WEEKEND RÉUSSIE !")
            self.weekend_data['success'] = True
            
            # Afficher résumé
            print("\n📋 RÉSUMÉ NIVEAUX WEEKEND:")
            print(f"   - SPX Prix: {self.weekend_data['spx_levels'].get('current_price', 'N/A')}")
            print(f"   - ES Prix: {self.weekend_data['es_levels'].get('current_price', 'N/A')}")
            print(f"   - Sentiment: {self.weekend_data['analysis']['market_sentiment']}")
            print(f"   - Risque: {self.weekend_data['analysis']['risk_assessment']}")
            
        else:
            print("⚠️ Récupération incomplète")
        
        return self.weekend_data['success']

def main():
    """Fonction principale"""
    print("🏆 RÉCUPÉRATION NIVEAUX OPTIONS WEEKEND - MIA_IA SYSTEM")
    print("=" * 60)
    
    recuperator = RecuperationNiveauxOptionsWeekend()
    success = recuperator.run_weekend_recuperation()
    
    if success:
        print("\n🎉 NIVEAUX OPTIONS WEEKEND RÉCUPÉRÉS !")
        print("📋 Prêt pour l'analyse weekend et la préparation lundi")
    else:
        print("\n⚠️ Récupération incomplète - vérifier connexion IBKR")
    
    return success

if __name__ == "__main__":
    main()










