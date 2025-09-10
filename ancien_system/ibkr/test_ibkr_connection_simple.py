#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Simple Connexion IBKR Réelle - MIA_IA System
Test avec les méthodes existantes du connecteur
"""

import sys
import os
import time
import json
import requests
from datetime import datetime
import urllib3

# Désactiver les warnings SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Ajouter le chemin du projet
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.ibkr_beta_connector import IBKRBetaConnector, IBKRBetaConfig

class TestIBKRConnectionSimple:
    def __init__(self):
        self.connector = None
        self.test_results = {
            'timestamp': datetime.now().isoformat(),
            'tests': {},
            'success': False,
            'errors': []
        }
    
    def test_gateway_connection(self):
        """Test de connexion au Gateway IBKR"""
        print("🔗 Test de connexion au Gateway IBKR...")
        
        try:
            response = requests.get('https://localhost:5000/v1/api/iserver/auth/status', 
                                  verify=False, timeout=10)
            
            if response.status_code == 200:
                print("✅ Gateway accessible")
                self.test_results['tests']['gateway'] = 'SUCCESS'
                return True
            else:
                print(f"⚠️ Gateway répond avec status: {response.status_code}")
                self.test_results['tests']['gateway'] = f'STATUS_{response.status_code}'
                return False
                
        except Exception as e:
            print(f"❌ Erreur connexion Gateway: {e}")
            self.test_results['tests']['gateway'] = f'ERROR: {str(e)}'
            self.test_results['errors'].append(f"Gateway: {str(e)}")
            return False
    
    def test_authentication(self):
        """Test d'authentification"""
        print("🔐 Test d'authentification...")
        
        try:
            config = IBKRBetaConfig()
            self.connector = IBKRBetaConnector(config)
            
            # Connexion
            if self.connector.connect():
                print("✅ Connexion réussie")
                
                # Authentification
                if self.connector.authenticate():
                    print("✅ Authentification réussie")
                    self.test_results['tests']['authentication'] = 'SUCCESS'
                    return True
                else:
                    print("❌ Échec authentification")
                    self.test_results['tests']['authentication'] = 'FAILED'
                    return False
            else:
                print("❌ Échec connexion")
                self.test_results['tests']['authentication'] = 'CONNECTION_FAILED'
                return False
                
        except Exception as e:
            print(f"❌ Erreur authentification: {e}")
            self.test_results['tests']['authentication'] = f'ERROR: {str(e)}'
            self.test_results['errors'].append(f"Auth: {str(e)}")
            return False
    
    def test_account_info(self):
        """Test récupération informations compte"""
        print("📊 Test récupération informations compte...")
        
        try:
            if not self.connector:
                print("❌ Connecteur non initialisé")
                return False
            
            # Récupération informations compte
            account_info = self.connector.get_account_info()
            
            if account_info:
                print("✅ Informations compte récupérées")
                print(f"   - Compte: {account_info.get('accountId', 'N/A')}")
                print(f"   - Type: {account_info.get('type', 'N/A')}")
                
                self.test_results['tests']['account_info'] = 'SUCCESS'
                return True
            else:
                print("❌ Informations compte non disponibles")
                self.test_results['tests']['account_info'] = 'NO_DATA'
                return False
                
        except Exception as e:
            print(f"❌ Erreur informations compte: {e}")
            self.test_results['tests']['account_info'] = f'ERROR: {str(e)}'
            self.test_results['errors'].append(f"Account Info: {str(e)}")
            return False
    
    def test_positions(self):
        """Test récupération positions"""
        print("📈 Test récupération positions...")
        
        try:
            if not self.connector:
                print("❌ Connecteur non initialisé")
                return False
            
            # Récupération positions
            positions = self.connector.get_positions()
            
            if positions is not None:
                print(f"✅ Positions récupérées: {len(positions)} position(s)")
                
                for pos in positions[:3]:  # Afficher les 3 premières
                    symbol = pos.get('contractDesc', 'N/A')
                    size = pos.get('position', 'N/A')
                    print(f"   - {symbol}: {size}")
                
                self.test_results['tests']['positions'] = f'SUCCESS: {len(positions)} positions'
                return True
            else:
                print("❌ Positions non disponibles")
                self.test_results['tests']['positions'] = 'NO_DATA'
                return False
                
        except Exception as e:
            print(f"❌ Erreur positions: {e}")
            self.test_results['tests']['positions'] = f'ERROR: {str(e)}'
            self.test_results['errors'].append(f"Positions: {str(e)}")
            return False
    
    def test_market_data_es(self):
        """Test données marché ES"""
        print("📊 Test données marché ES...")
        
        try:
            if not self.connector:
                print("❌ Connecteur non initialisé")
                return False
            
            # ConID pour ES futures (approximatif)
            es_conid = "13893091"  # ES futures
            
            # Données ES
            es_data = self.connector.get_market_data(es_conid)
            
            if es_data:
                print("✅ Données ES récupérées")
                print(f"   - Données: {len(es_data)} champs")
                
                self.test_results['tests']['es_data'] = 'SUCCESS'
                return True
            else:
                print("❌ Données ES non disponibles")
                self.test_results['tests']['es_data'] = 'NO_DATA'
                return False
                
        except Exception as e:
            print(f"❌ Erreur données ES: {e}")
            self.test_results['tests']['es_data'] = f'ERROR: {str(e)}'
            self.test_results['errors'].append(f"ES Data: {str(e)}")
            return False
    
    def test_historical_data(self):
        """Test données historiques"""
        print("📈 Test données historiques...")
        
        try:
            if not self.connector:
                print("❌ Connecteur non initialisé")
                return False
            
            # ConID pour ES futures
            es_conid = "13893091"
            
            # Données historiques
            hist_data = self.connector.get_historical_data(es_conid, period="1d", bar="1min")
            
            if hist_data:
                print(f"✅ Données historiques récupérées: {len(hist_data)} barres")
                
                if hist_data:
                    latest = hist_data[-1]
                    print(f"   - Dernière barre: {latest.get('t', 'N/A')}")
                    print(f"   - Prix: {latest.get('c', 'N/A')}")
                
                self.test_results['tests']['historical_data'] = f'SUCCESS: {len(hist_data)} barres'
                return True
            else:
                print("❌ Données historiques non disponibles")
                self.test_results['tests']['historical_data'] = 'NO_DATA'
                return False
                
        except Exception as e:
            print(f"❌ Erreur données historiques: {e}")
            self.test_results['tests']['historical_data'] = f'ERROR: {str(e)}'
            self.test_results['errors'].append(f"Historical: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Exécuter tous les tests"""
        print("🚀 DÉBUT DES TESTS IBKR SIMPLE")
        print("=" * 50)
        
        tests = [
            ('Gateway', self.test_gateway_connection),
            ('Authentication', self.test_authentication),
            ('Account Info', self.test_account_info),
            ('Positions', self.test_positions),
            ('ES Market Data', self.test_market_data_es),
            ('Historical Data', self.test_historical_data)
        ]
        
        success_count = 0
        
        for test_name, test_func in tests:
            print(f"\n🔍 Test: {test_name}")
            print("-" * 30)
            
            try:
                if test_func():
                    success_count += 1
                time.sleep(1)  # Pause entre tests
                
            except Exception as e:
                print(f"❌ Erreur critique dans {test_name}: {e}")
                self.test_results['errors'].append(f"{test_name}: {str(e)}")
        
        # Résultats finaux
        print("\n" + "=" * 50)
        print("📊 RÉSULTATS FINAUX")
        print("=" * 50)
        
        total_tests = len(tests)
        success_rate = (success_count / total_tests) * 100
        
        print(f"✅ Tests réussis: {success_count}/{total_tests}")
        print(f"📊 Taux de succès: {success_rate:.1f}%")
        
        if success_rate >= 80:
            print("🎉 CONNEXION IBKR RÉELLE VALIDÉE !")
            self.test_results['success'] = True
        else:
            print("⚠️ Connexion IBKR nécessite des ajustements")
        
        # Sauvegarder résultats
        self.save_results()
        
        return self.test_results['success']
    
    def save_results(self):
        """Sauvegarder les résultats"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"data/test_results/ibkr_simple_connection_test_{timestamp}.json"
        
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.test_results, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Résultats sauvegardés: {filename}")

def main():
    """Fonction principale"""
    print("🏆 TEST SIMPLE DE CONNEXION IBKR RÉELLE - MIA_IA SYSTEM")
    print("=" * 60)
    
    tester = TestIBKRConnectionSimple()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 PRÊT POUR LA TRANSITION VERS LES DONNÉES RÉELLES !")
        print("📋 Prochaines étapes:")
        print("   1. Test système complet avec données réelles")
        print("   2. Validation Paper Trading")
        print("   3. Optimisation paramètres")
        print("   4. Déploiement production")
    else:
        print("\n⚠️ Des ajustements sont nécessaires avant la production")
    
    return success

if __name__ == "__main__":
    main()










