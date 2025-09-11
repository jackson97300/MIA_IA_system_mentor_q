#!/usr/bin/env python3
"""
Test Battle Navale + Orderflow avec vraies données IBKR
Utilise les données ES réelles pour tester le système
"""

import sys
import json
import re
from datetime import datetime
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from core.ibkr_beta_connector import IBKRBetaConnector, IBKRBetaConfig
from core.battle_navale import BattleNavale
from data.orderflow import OrderFlowAnalyzer

def clean_price(price_str):
    """Nettoyer prix"""
    if not price_str or price_str == 'N/A':
        return 0.0
    try:
        price_str = str(price_str).strip()
        price_str = re.sub(r'^[C$€£¥]\s*', '', price_str)
        return float(price_str)
    except:
        return 0.0

class BattleNavaleOrderFlowTest:
    """Test Battle Navale + Orderflow avec données réelles"""
    
    def __init__(self):
        self.config = IBKRBetaConfig()
        self.connector = IBKRBetaConnector(self.config)
        self.price_factor = 28
        self.battle_navale = BattleNavale()
        self.orderflow = OrderFlowAnalyzer()
        
    def get_real_es_data(self):
        """Récupérer données ES réelles"""
        
        print("🔌 Connexion à l'API IBKR...")
        
        try:
            if not self.connector.connect() or not self.connector.authenticate():
                print("❌ Connexion échouée")
                return None
            
            print("✅ Connecté et authentifié")
            
            # Récupérer données ES
            conid = "265598"
            fields = ["31", "84", "86", "87", "88", "89", "90"]  # Bid, Last, Volume, OHLC
            market_data = self.connector.get_market_data(conid, fields)
            
            if market_data and len(market_data) > 0:
                data = market_data[0]
                
                # Nettoyer et corriger les prix
                bid_raw = clean_price(data.get('31', 0))
                last_raw = clean_price(data.get('84', 0))
                volume_raw = data.get('86', 'N/A')
                
                # Appliquer priceFactor
                bid_corrected = bid_raw * self.price_factor
                last_corrected = last_raw * self.price_factor
                
                # Prix final
                final_price = last_corrected if last_corrected > 0 else bid_corrected
                
                # Données OHLC
                high_raw = clean_price(data.get('87', 0))
                low_raw = clean_price(data.get('88', 0))
                open_raw = clean_price(data.get('89', 0))
                
                high_corrected = high_raw * self.price_factor
                low_corrected = low_raw * self.price_factor
                open_corrected = open_raw * self.price_factor
                
                # Parser volume
                volume_parsed = 0
                if volume_raw and volume_raw != 'N/A':
                    try:
                        volume_str = str(volume_raw)
                        if 'M' in volume_str:
                            volume_parsed = int(float(volume_str.replace('M', '')) * 1000000)
                        elif 'K' in volume_str:
                            volume_parsed = int(float(volume_str.replace('K', '')) * 1000)
                        else:
                            volume_parsed = int(float(volume_str))
                    except:
                        volume_parsed = 0
                
                return {
                    'price': final_price,
                    'bid': bid_corrected,
                    'last': last_corrected,
                    'high': high_corrected,
                    'low': low_corrected,
                    'open': open_corrected,
                    'volume': volume_parsed,
                    'timestamp': datetime.now().isoformat()
                }
            
            return None
            
        except Exception as e:
            print(f"❌ Erreur données: {e}")
            return None
        finally:
            self.connector.disconnect()
    
    def get_historical_data(self):
        """Récupérer données historiques pour Orderflow"""
        
        print("📈 Récupération données historiques...")
        
        try:
            if not self.connector.connect() or not self.connector.authenticate():
                return None
            
            conid = "265598"
            historical = self.connector.get_historical_data(conid, "1d", "1min")
            
            if historical and len(historical) > 0:
                print(f"✅ {len(historical)} barres récupérées")
                
                # Convertir en format Orderflow
                bars = []
                for bar in historical[-100:]:  # 100 dernières barres
                    try:
                        corrected_bar = {
                            'timestamp': bar.get('t'),
                            'open': clean_price(bar.get('o', 0)) * self.price_factor,
                            'high': clean_price(bar.get('h', 0)) * self.price_factor,
                            'low': clean_price(bar.get('l', 0)) * self.price_factor,
                            'close': clean_price(bar.get('c', 0)) * self.price_factor,
                            'volume': int(bar.get('v', 0))
                        }
                        bars.append(corrected_bar)
                    except:
                        continue
                
                return bars
            
            return None
            
        except Exception as e:
            print(f"❌ Erreur historique: {e}")
            return None
        finally:
            self.connector.disconnect()
    
    def test_battle_navale(self, es_data):
        """Tester Battle Navale avec données réelles"""
        
        print("\n🎯 Test Battle Navale avec données réelles")
        print("=" * 50)
        
        if not es_data:
            print("❌ Pas de données ES")
            return None
        
        # Créer contexte de marché
        market_context = {
            'current_price': es_data['price'],
            'bid': es_data['bid'],
            'last': es_data['last'],
            'high': es_data['high'],
            'low': es_data['low'],
            'open': es_data['open'],
            'volume': es_data['volume'],
            'timestamp': es_data['timestamp']
        }
        
        print(f"📊 Contexte marché:")
        print(f"   Prix actuel: {market_context['current_price']:.2f}")
        print(f"   Bid: {market_context['bid']:.2f}")
        print(f"   High: {market_context['high']:.2f}")
        print(f"   Low: {market_context['low']:.2f}")
        print(f"   Volume: {market_context['volume']:,}")
        
        # Analyser avec Battle Navale
        try:
            analysis = self.battle_navale.analyze_market_context(market_context)
            
            print(f"\n🎯 Analyse Battle Navale:")
            print(f"   Position: {analysis.get('position', 'N/A')}")
            print(f"   Confiance: {analysis.get('confidence', 0):.2f}")
            print(f"   Stratégie: {analysis.get('strategy', 'N/A')}")
            print(f"   Risque: {analysis.get('risk_level', 'N/A')}")
            
            return analysis
            
        except Exception as e:
            print(f"❌ Erreur Battle Navale: {e}")
            return None
    
    def test_orderflow(self, historical_data):
        """Tester Orderflow avec données historiques réelles"""
        
        print("\n📊 Test Orderflow avec données historiques")
        print("=" * 50)
        
        if not historical_data or len(historical_data) < 10:
            print("❌ Pas assez de données historiques")
            return None
        
        try:
            # Analyser Orderflow
            orderflow_analysis = self.orderflow.analyze_volume_profile(historical_data)
            
            print(f"📈 Analyse Orderflow:")
            print(f"   Barres analysées: {len(historical_data)}")
            print(f"   Volume total: {orderflow_analysis.get('total_volume', 0):,}")
            print(f"   POC (Point of Control): {orderflow_analysis.get('poc_price', 0):.2f}")
            print(f"   Value Area High: {orderflow_analysis.get('vah', 0):.2f}")
            print(f"   Value Area Low: {orderflow_analysis.get('val', 0):.2f}")
            
            # Analyser flux d'ordres
            flow_analysis = self.orderflow.analyze_order_flow(historical_data)
            
            print(f"\n🔄 Flux d'ordres:")
            print(f"   Flux net: {flow_analysis.get('net_flow', 0):.2f}")
            print(f"   Tendance: {flow_analysis.get('trend', 'N/A')}")
            print(f"   Pression acheteur: {flow_analysis.get('buying_pressure', 0):.2f}")
            print(f"   Pression vendeur: {flow_analysis.get('selling_pressure', 0):.2f}")
            
            return {
                'volume_profile': orderflow_analysis,
                'order_flow': flow_analysis
            }
            
        except Exception as e:
            print(f"❌ Erreur Orderflow: {e}")
            return None
    
    def combine_analysis(self, battle_navale_result, orderflow_result):
        """Combiner analyses Battle Navale + Orderflow"""
        
        print("\n🤝 Combinaison Battle Navale + Orderflow")
        print("=" * 50)
        
        if not battle_navale_result or not orderflow_result:
            print("❌ Analyses incomplètes")
            return None
        
        try:
            # Logique de combinaison
            bn_position = battle_navale_result.get('position', 'neutral')
            bn_confidence = battle_navale_result.get('confidence', 0)
            
            of_trend = orderflow_result['order_flow'].get('trend', 'neutral')
            of_net_flow = orderflow_result['order_flow'].get('net_flow', 0)
            
            # Score combiné
            combined_score = 0
            combined_signal = "NEUTRAL"
            
            # Battle Navale influence
            if bn_position == 'long' and bn_confidence > 0.6:
                combined_score += 1
            elif bn_position == 'short' and bn_confidence > 0.6:
                combined_score -= 1
            
            # Orderflow influence
            if of_trend == 'bullish' and of_net_flow > 0:
                combined_score += 1
            elif of_trend == 'bearish' and of_net_flow < 0:
                combined_score -= 1
            
            # Signal final
            if combined_score >= 1:
                combined_signal = "BUY"
            elif combined_score <= -1:
                combined_signal = "SELL"
            
            print(f"🎯 Signal combiné: {combined_signal}")
            print(f"   Score: {combined_score}")
            print(f"   Battle Navale: {bn_position} (conf: {bn_confidence:.2f})")
            print(f"   Orderflow: {of_trend} (flux: {of_net_flow:.2f})")
            
            return {
                'signal': combined_signal,
                'score': combined_score,
                'battle_navale': battle_navale_result,
                'orderflow': orderflow_result,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"❌ Erreur combinaison: {e}")
            return None
    
    def save_results(self, results, filename="battle_navale_orderflow_results.json"):
        """Sauvegarder résultats"""
        
        try:
            with open(filename, 'w') as f:
                json.dump(results, f, indent=2)
            print(f"\n💾 Résultats sauvegardés: {filename}")
        except Exception as e:
            print(f"❌ Erreur sauvegarde: {e}")

def main():
    """Fonction principale"""
    
    print("🚀 Test Battle Navale + Orderflow avec données réelles")
    print("IBKR API - ES Futures")
    print("=" * 60)
    
    tester = BattleNavaleOrderFlowTest()
    
    try:
        # 1. Récupérer données ES réelles
        es_data = tester.get_real_es_data()
        
        if not es_data:
            print("❌ Impossible de récupérer données ES")
            return
        
        print(f"✅ Données ES récupérées: {es_data['price']:.2f}")
        
        # 2. Récupérer données historiques
        historical_data = tester.get_historical_data()
        
        if not historical_data:
            print("❌ Impossible de récupérer données historiques")
            return
        
        # 3. Test Battle Navale
        battle_navale_result = tester.test_battle_navale(es_data)
        
        # 4. Test Orderflow
        orderflow_result = tester.test_orderflow(historical_data)
        
        # 5. Combiner analyses
        combined_result = tester.combine_analysis(battle_navale_result, orderflow_result)
        
        # 6. Sauvegarder résultats
        if combined_result:
            results = {
                'es_data': es_data,
                'historical_data_count': len(historical_data),
                'combined_analysis': combined_result,
                'test_timestamp': datetime.now().isoformat()
            }
            
            tester.save_results(results)
            
            print(f"\n🎉 TEST TERMINÉ AVEC SUCCÈS!")
            print(f"   Signal final: {combined_result['signal']}")
            print(f"   Score: {combined_result['score']}")
            print(f"   Données ES: {es_data['price']:.2f}")
            print(f"   Barres analysées: {len(historical_data)}")
        
    except Exception as e:
        print(f"❌ Erreur générale: {e}")

if __name__ == "__main__":
    main()

