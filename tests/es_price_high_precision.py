#!/usr/bin/env python3
"""
Script haute précision ES pour bot de trading
Utilise mid-price et vérifications multiples pour maximiser la précision
"""

import sys
import json
import re
import requests
from datetime import datetime
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from core.ibkr_beta_connector import IBKRBetaConnector, IBKRBetaConfig

def clean_price_string(price_str):
    """Nettoyer les prix avec préfixes (C, $, etc.)"""
    if not price_str or price_str == 'N/A':
        return 0.0
    
    try:
        price_str = str(price_str).strip()
        price_str = re.sub(r'^[C$€£¥]\s*', '', price_str)
        price_str = re.sub(r'[^\d.-]', '', price_str)
        return float(price_str)
    except:
        return 0.0

def parse_volume(volume_str):
    """Parser le volume au format '56.0M', '1.2K', etc."""
    if not volume_str or volume_str == 'N/A':
        return 0
    
    try:
        volume_str = str(volume_str)
        match = re.match(r'([\d.]+)([KMB]?)', volume_str)
        if match:
            number = float(match.group(1))
            suffix = match.group(2)
            
            if suffix == 'K':
                return int(number * 1000)
            elif suffix == 'M':
                return int(number * 1000000)
            elif suffix == 'B':
                return int(number * 1000000000)
            else:
                return int(number)
        else:
            return int(float(volume_str))
    except:
        return 0

class ESPriceHighPrecision:
    """Script haute précision pour bot de trading"""
    
    def __init__(self):
        self.config = IBKRBetaConfig()
        self.connector = IBKRBetaConnector(self.config)
        self.price_factor = 28
        
    def get_high_precision_price(self):
        """Récupérer le prix ES avec haute précision"""
        
        print("🎯 Récupération prix ES haute précision")
        print("=" * 50)
        
        try:
            # Connexion
            if not self.connector.connect() or not self.connector.authenticate():
                print("❌ Connexion échouée")
                return None
            
            print("✅ Connecté et authentifié")
            
            # Récupérer données complètes
            conid = "265598"
            fields = ["31", "32", "83", "84", "86", "87", "88", "89", "90"]
            market_data = self.connector.get_market_data(conid, fields)
            
            if market_data and len(market_data) > 0:
                data = market_data[0]
                
                # Extraire tous les prix possibles
                bid_raw = clean_price_string(data.get('31', 0))  # Bid
                ask_raw = clean_price_string(data.get('32', 0))  # Ask (alternative)
                ask2_raw = clean_price_string(data.get('83', 0))  # Ask (principal)
                last_raw = clean_price_string(data.get('84', 0))  # Last
                volume_raw = data.get('86', 'N/A')
                
                print(f"📊 Données brutes reçues:")
                print(f"   Bid (31): {bid_raw}")
                print(f"   Ask (32): {ask_raw}")
                print(f"   Ask (83): {ask2_raw}")
                print(f"   Last (84): {last_raw}")
                print(f"   Volume: {volume_raw}")
                
                # Appliquer priceFactor
                bid_corrected = bid_raw * self.price_factor
                ask_corrected = ask_raw * self.price_factor
                ask2_corrected = ask2_raw * self.price_factor
                last_corrected = last_raw * self.price_factor
                
                print(f"\n📈 Prix corrigés:")
                print(f"   Bid: {bid_corrected:.2f}")
                print(f"   Ask (32): {ask_corrected:.2f}")
                print(f"   Ask (83): {ask2_corrected:.2f}")
                print(f"   Last: {last_corrected:.2f}")
                
                # Calculer mid-price (plus précis pour trading)
                if bid_corrected > 0 and ask_corrected > 0:
                    mid_price = (bid_corrected + ask_corrected) / 2
                    spread = ask_corrected - bid_corrected
                elif bid_corrected > 0 and ask2_corrected > 0:
                    mid_price = (bid_corrected + ask2_corrected) / 2
                    spread = ask2_corrected - bid_corrected
                elif last_corrected > 0:
                    mid_price = last_corrected
                    spread = 0
                else:
                    mid_price = bid_corrected
                    spread = 0
                
                print(f"\n🎯 Prix de trading recommandés:")
                print(f"   Mid-price: {mid_price:.2f}")
                print(f"   Spread: {spread:.2f}")
                print(f"   Bid: {bid_corrected:.2f}")
                print(f"   Ask: {max(ask_corrected, ask2_corrected):.2f}")
                
                # Vérifier la cohérence
                price_consistency = self.check_price_consistency(bid_corrected, ask_corrected, ask2_corrected, last_corrected)
                
                # Données OHLC
                high_raw = clean_price_string(data.get('87', 0))
                low_raw = clean_price_string(data.get('88', 0))
                open_raw = clean_price_string(data.get('89', 0))
                
                high_corrected = high_raw * self.price_factor
                low_corrected = low_raw * self.price_factor
                open_corrected = open_raw * self.price_factor
                
                volume_parsed = parse_volume(volume_raw)
                
                return {
                    'mid_price': mid_price,
                    'bid': bid_corrected,
                    'ask': max(ask_corrected, ask2_corrected),
                    'last': last_corrected,
                    'spread': spread,
                    'high': high_corrected,
                    'low': low_corrected,
                    'open': open_corrected,
                    'volume': volume_parsed,
                    'price_consistency': price_consistency,
                    'raw_data': {
                        'bid_raw': bid_raw,
                        'ask_raw': ask_raw,
                        'ask2_raw': ask2_raw,
                        'last_raw': last_raw,
                        'volume_raw': volume_raw
                    },
                    'timestamp': datetime.now().isoformat()
                }
            else:
                print("❌ Pas de données")
                return None
                
        except Exception as e:
            print(f"❌ Erreur: {e}")
            return None
    
    def check_price_consistency(self, bid, ask, ask2, last):
        """Vérifier la cohérence des prix"""
        
        prices = [p for p in [bid, ask, ask2, last] if p > 0]
        
        if len(prices) < 2:
            return {'status': 'warning', 'message': 'Peu de données de prix disponibles'}
        
        min_price = min(prices)
        max_price = max(prices)
        range_pct = ((max_price - min_price) / min_price) * 100
        
        print(f"\n🔍 Vérification cohérence:")
        print(f"   Prix min: {min_price:.2f}")
        print(f"   Prix max: {max_price:.2f}")
        print(f"   Fourchette: {range_pct:.3f}%")
        
        if range_pct < 0.1:  # Moins de 0.1%
            return {'status': 'excellent', 'message': f'Prix très cohérents (fourchette: {range_pct:.3f}%)'}
        elif range_pct < 0.5:  # Moins de 0.5%
            return {'status': 'good', 'message': f'Prix cohérents (fourchette: {range_pct:.3f}%)'}
        elif range_pct < 1.0:  # Moins de 1%
            return {'status': 'warning', 'message': f'Prix peu cohérents (fourchette: {range_pct:.3f}%)'}
        else:
            return {'status': 'error', 'message': f'Prix incohérents (fourchette: {range_pct:.3f}%)'}
    
    def get_trading_recommendations(self, price_data):
        """Recommandations pour le bot de trading"""
        
        if not price_data:
            return None
        
        mid_price = price_data['mid_price']
        spread = price_data['spread']
        consistency = price_data['price_consistency']
        
        print(f"\n🤖 Recommandations pour bot de trading:")
        print("=" * 40)
        
        # Prix recommandé
        if consistency['status'] in ['excellent', 'good']:
            recommended_price = mid_price
            print(f"✅ Prix recommandé: {recommended_price:.2f} (mid-price)")
        else:
            recommended_price = price_data['bid']  # Utiliser bid en cas d'incohérence
            print(f"⚠️ Prix recommandé: {recommended_price:.2f} (bid - incohérence détectée)")
        
        # Gestion du spread
        if spread > 1.0:
            print(f"⚠️ Spread élevé: {spread:.2f} points")
            print(f"   Considérer slippage dans les ordres")
        else:
            print(f"✅ Spread normal: {spread:.2f} points")
        
        # Recommandations spécifiques
        recommendations = {
            'entry_price': recommended_price,
            'stop_loss_buffer': max(2.0, spread * 2),  # Buffer pour stop loss
            'take_profit_buffer': max(1.0, spread),    # Buffer pour take profit
            'max_slippage': spread * 1.5,              # Slippage maximum accepté
            'confidence_level': consistency['status'],
            'warnings': []
        }
        
        if consistency['status'] == 'error':
            recommendations['warnings'].append("Prix incohérents - vérifier la connexion")
        
        if spread > 2.0:
            recommendations['warnings'].append("Spread élevé - risque de slippage")
        
        if mid_price < 6400 or mid_price > 6600:
            recommendations['warnings'].append("Prix hors de la plage normale ES")
        
        # Afficher recommandations
        print(f"\n📋 Configuration recommandée:")
        print(f"   Prix d'entrée: {recommendations['entry_price']:.2f}")
        print(f"   Buffer stop loss: ±{recommendations['stop_loss_buffer']:.2f}")
        print(f"   Buffer take profit: ±{recommendations['take_profit_buffer']:.2f}")
        print(f"   Slippage max: ±{recommendations['max_slippage']:.2f}")
        print(f"   Niveau confiance: {recommendations['confidence_level']}")
        
        if recommendations['warnings']:
            print(f"\n⚠️ Avertissements:")
            for warning in recommendations['warnings']:
                print(f"   - {warning}")
        
        return recommendations
    
    def save_trading_data(self, price_data, recommendations, filename="es_trading_data.json"):
        """Sauvegarder les données pour le bot"""
        
        trading_data = {
            'price_data': price_data,
            'trading_recommendations': recommendations,
            'retrieved_at': datetime.now().isoformat(),
            'price_factor_used': self.price_factor
        }
        
        try:
            with open(filename, 'w') as f:
                json.dump(trading_data, f, indent=2)
            print(f"\n💾 Données trading sauvegardées: {filename}")
        except Exception as e:
            print(f"❌ Erreur sauvegarde: {e}")
    
    def disconnect(self):
        """Déconnexion"""
        self.connector.disconnect()

def main():
    """Fonction principale"""
    
    print("🚀 Script haute précision ES pour bot de trading")
    print("Optimisé pour minimiser les erreurs de prix")
    print("=" * 60)
    
    util = ESPriceHighPrecision()
    
    try:
        # 1. Récupérer prix haute précision
        price_data = util.get_high_precision_price()
        
        if price_data:
            print(f"\n🎉 PRIX ES HAUTE PRÉCISION: {price_data['mid_price']:.2f}")
            
            # 2. Générer recommandations trading
            recommendations = util.get_trading_recommendations(price_data)
            
            # 3. Sauvegarder données
            util.save_trading_data(price_data, recommendations)
            
            print(f"\n💡 Résumé final:")
            print(f"   Prix ES: {price_data['mid_price']:.2f}")
            print(f"   Spread: {price_data['spread']:.2f}")
            print(f"   Cohérence: {price_data['price_consistency']['status']}")
            print(f"   Volume: {price_data['volume']:,}")
            
            print(f"\n✅ SUCCÈS! Données optimisées pour bot de trading")
            print(f"   ✅ Utilisation du mid-price pour plus de précision")
            print(f"   ✅ Vérification de cohérence des prix")
            print(f"   ✅ Recommandations de trading générées")
            
        else:
            print("\n❌ Impossible de récupérer le prix ES")
    
    except Exception as e:
        print(f"❌ Erreur générale: {e}")
    
    finally:
        util.disconnect()

if __name__ == "__main__":
    main()

