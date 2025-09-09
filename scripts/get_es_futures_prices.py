#!/usr/bin/env python3
"""
📊 Récupération des prix ES Futures via IBKR BETA API
Script pour obtenir les données de marché en temps réel des E-mini S&P 500
"""

import sys
import time
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

# Ajouter le chemin du projet
sys.path.append(str(Path(__file__).parent.parent))

from core.ibkr_beta_connector import IBKRBetaConnector, IBKRBetaConfig
from core.logger import get_logger

logger = get_logger(__name__)

class ESFuturesDataRetriever:
    """Récupérateur de données ES Futures"""
    
    def __init__(self):
        self.connector = IBKRBetaConnector()
        self.es_conid = None
        self.current_data = {}
        
        # Spécifications ES Futures selon IBKR
        self.es_specs = {
            'symbol': 'ES',
            'name': 'E-mini S&P 500',
            'exchange': 'CME',
            'tick_size': 0.25,
            'tick_value': 12.50,
            'multiplier': 50,
            'margin_initial': 13200,
            'margin_maintenance': 12000
        }
        
        logger.info("🎯 ES Futures Data Retriever initialisé")
    
    def connect_and_authenticate(self) -> bool:
        """Connexion et authentification IBKR"""
        try:
            logger.info("🔌 Connexion à IBKR BETA...")
            
            # Connexion
            if not self.connector.connect():
                logger.error("❌ Échec connexion IBKR")
                return False
            
            # Authentification
            if not self.connector.authenticate():
                logger.error("❌ Échec authentification IBKR")
                return False
            
            logger.info("✅ Connexion et authentification réussies")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur connexion: {e}")
            return False
    
    def find_es_contract(self) -> Optional[str]:
        """Trouver le contrat ES actuel"""
        try:
            logger.info("🔍 Recherche contrat ES...")
            
            # Recherche ES futures
            contracts = self.connector.search_contract("ES", "FUT")
            
            if not contracts:
                logger.error("❌ Aucun contrat ES trouvé")
                return None
            
            # Afficher les contrats trouvés
            logger.info(f"📋 {len(contracts)} contrats ES trouvés:")
            for i, contract in enumerate(contracts[:5]):  # Afficher les 5 premiers
                logger.info(f"  {i+1}. {contract.get('localSymbol', 'N/A')} - {contract.get('description', 'N/A')}")
            
            # Prendre le premier contrat (front month)
            self.es_conid = str(contracts[0].get("conid"))
            logger.info(f"✅ Contrat ES sélectionné: {contracts[0].get('localSymbol', 'N/A')} (conid: {self.es_conid})")
            
            return self.es_conid
            
        except Exception as e:
            logger.error(f"❌ Erreur recherche contrat ES: {e}")
            return None
    
    def get_current_price(self) -> Optional[Dict[str, Any]]:
        """Récupérer le prix actuel ES"""
        try:
            if not self.es_conid:
                logger.error("❌ Aucun contrat ES défini")
                return None
            
            # Champs de données de marché
            fields = [
                "31",  # bid
                "83",  # ask  
                "84",  # last
                "86",  # volume
                "6",   # high
                "7",   # low
                "8",   # open
                "9"    # close
            ]
            
            data = self.connector.get_market_data(self.es_conid, fields)
            
            if not data:
                logger.warning("⚠️ Aucune donnée de marché reçue")
                return None
            
            # Traiter les données
            market_data = {
                'symbol': 'ES',
                'conid': self.es_conid,
                'timestamp': datetime.now(),
                'bid': None,
                'ask': None,
                'last': None,
                'volume': None,
                'high': None,
                'low': None,
                'open': None,
                'close': None
            }
            
            # Parser les données selon le format IBKR
            if isinstance(data, list) and len(data) > 0:
                tick_data = data[0]
                for field in tick_data.get('31', []):  # bid
                    if field.get('f') == '31':
                        market_data['bid'] = field.get('v')
                for field in tick_data.get('83', []):  # ask
                    if field.get('f') == '83':
                        market_data['ask'] = field.get('v')
                for field in tick_data.get('84', []):  # last
                    if field.get('f') == '84':
                        market_data['last'] = field.get('v')
                for field in tick_data.get('86', []):  # volume
                    if field.get('f') == '86':
                        market_data['volume'] = field.get('v')
                for field in tick_data.get('6', []):  # high
                    if field.get('f') == '6':
                        market_data['high'] = field.get('v')
                for field in tick_data.get('7', []):  # low
                    if field.get('f') == '7':
                        market_data['low'] = field.get('v')
                for field in tick_data.get('8', []):  # open
                    if field.get('f') == '8':
                        market_data['open'] = field.get('v')
                for field in tick_data.get('9', []):  # close
                    if field.get('f') == '9':
                        market_data['close'] = field.get('v')
            
            self.current_data = market_data
            return market_data
            
        except Exception as e:
            logger.error(f"❌ Erreur récupération prix: {e}")
            return None
    
    def get_historical_data(self, period: str = "1d", bar: str = "1min") -> List[Dict]:
        """Récupérer les données historiques ES"""
        try:
            if not self.es_conid:
                logger.error("❌ Aucun contrat ES défini")
                return []
            
            logger.info(f"📈 Récupération données historiques: {period} {bar}")
            
            data = self.connector.get_historical_data(self.es_conid, period, bar)
            
            if not data:
                logger.warning("⚠️ Aucune donnée historique reçue")
                return []
            
            logger.info(f"✅ {len(data)} barres historiques récupérées")
            return data
            
        except Exception as e:
            logger.error(f"❌ Erreur données historiques: {e}")
            return []
    
    def display_current_price(self, data: Dict[str, Any]):
        """Afficher le prix actuel de manière formatée"""
        if not data:
            logger.warning("⚠️ Aucune donnée à afficher")
            return
        
        print("\n" + "="*60)
        print("📊 PRIX ES FUTURES - E-mini S&P 500")
        print("="*60)
        print(f"🕐 Timestamp: {data.get('timestamp', 'N/A')}")
        print(f"📈 Symbole: {data.get('symbol', 'N/A')}")
        print(f"🆔 ConID: {data.get('conid', 'N/A')}")
        print("-"*60)
        print(f"💰 Bid:     {data.get('bid', 'N/A'):>10}")
        print(f"💰 Ask:     {data.get('ask', 'N/A'):>10}")
        print(f"💰 Last:    {data.get('last', 'N/A'):>10}")
        print(f"📊 Spread:  {(data.get('ask', 0) - data.get('bid', 0)) if data.get('ask') and data.get('bid') else 'N/A':>10}")
        print("-"*60)
        print(f"📈 Open:    {data.get('open', 'N/A'):>10}")
        print(f"📈 High:    {data.get('high', 'N/A'):>10}")
        print(f"📈 Low:     {data.get('low', 'N/A'):>10}")
        print(f"📈 Close:   {data.get('close', 'N/A'):>10}")
        print("-"*60)
        print(f"📊 Volume:  {data.get('volume', 'N/A'):>10}")
        print("="*60)
        
        # Calculer la valeur en dollars
        if data.get('last'):
            last_price = float(data['last'])
            dollar_value = last_price * self.es_specs['multiplier']
            tick_value = self.es_specs['tick_value']
            print(f"💵 Valeur contrat: ${dollar_value:,.2f}")
            print(f"💵 Valeur tick: ${tick_value}")
        print()
    
    def monitor_prices(self, duration_minutes: int = 5, interval_seconds: int = 10):
        """Surveiller les prix en continu"""
        try:
            logger.info(f"👀 Surveillance des prix ES pendant {duration_minutes} minutes...")
            
            start_time = datetime.now()
            end_time = start_time + timedelta(minutes=duration_minutes)
            
            while datetime.now() < end_time:
                data = self.get_current_price()
                if data:
                    self.display_current_price(data)
                else:
                    logger.warning("⚠️ Impossible de récupérer les données")
                
                time.sleep(interval_seconds)
            
            logger.info("✅ Surveillance terminée")
            
        except KeyboardInterrupt:
            logger.info("⏹️ Surveillance interrompue par l'utilisateur")
        except Exception as e:
            logger.error(f"❌ Erreur surveillance: {e}")
    
    def disconnect(self):
        """Déconnexion"""
        try:
            self.connector.disconnect()
            logger.info("🔌 Déconnexion terminée")
        except Exception as e:
            logger.error(f"❌ Erreur déconnexion: {e}")

def main():
    """Fonction principale"""
    print("🚀 Démarrage récupération prix ES Futures")
    print("="*50)
    
    retriever = ESFuturesDataRetriever()
    
    try:
        # 1. Connexion et authentification
        if not retriever.connect_and_authenticate():
            print("❌ Impossible de se connecter à IBKR")
            return
        
        # 2. Trouver le contrat ES
        if not retriever.find_es_contract():
            print("❌ Impossible de trouver le contrat ES")
            return
        
        # 3. Récupérer le prix actuel
        print("\n📊 Récupération du prix actuel...")
        current_data = retriever.get_current_price()
        
        if current_data:
            retriever.display_current_price(current_data)
        else:
            print("❌ Impossible de récupérer le prix actuel")
            return
        
        # 4. Demander à l'utilisateur s'il veut surveiller
        print("\n❓ Voulez-vous surveiller les prix en continu? (y/n): ", end="")
        choice = input().lower().strip()
        
        if choice in ['y', 'yes', 'oui', 'o']:
            print("⏱️ Durée de surveillance (minutes, défaut 5): ", end="")
            duration_input = input().strip()
            duration = int(duration_input) if duration_input.isdigit() else 5
            
            retriever.monitor_prices(duration)
        
        # 5. Optionnel: données historiques
        print("\n❓ Voulez-vous récupérer des données historiques? (y/n): ", end="")
        choice = input().lower().strip()
        
        if choice in ['y', 'yes', 'oui', 'o']:
            print("📈 Récupération données historiques...")
            historical_data = retriever.get_historical_data("1d", "1min")
            
            if historical_data:
                print(f"✅ {len(historical_data)} barres récupérées")
                print("📊 Aperçu des 5 dernières barres:")
                for i, bar in enumerate(historical_data[-5:]):
                    print(f"  {i+1}. {bar}")
            else:
                print("❌ Aucune donnée historique récupérée")
    
    except Exception as e:
        logger.error(f"❌ Erreur principale: {e}")
    
    finally:
        retriever.disconnect()
        print("\n👋 Script terminé")

if __name__ == "__main__":
    main()

