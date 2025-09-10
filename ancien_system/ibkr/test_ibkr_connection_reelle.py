#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test de Connexion IBKR Réelle - MIA_IA System
Test complet avec authentification réelle
"""

import sys
import os
import time
import json
import requests
from datetime import datetime, timedelta
import urllib3

# Désactiver les warnings SSL pour localhost
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Ajouter le chemin du projet
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.ibkr_beta_connector import IBKRBetaConnector, IBKRBetaConfig

class TestIBKRConnectionReelle:
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
            # Test de base
            response = requests.get('https://localhost:5000/v1/api/one/user', 
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
            auth_status = self.connector.connect()
            
            if auth_status:
                print("✅ Authentification réussie")
                self.test_results['tests']['authentication'] = 'SUCCESS'
                return True
            else:
                print("❌ Échec authentification")
                self.test_results['tests']['authentication'] = 'FAILED'
                return False
                
        except Exception as e:
            print(f"❌ Erreur authentification: {e}")
            self.test_results['tests']['authentication'] = f'ERROR: {str(e)}'
            self.test_results['errors'].append(f"Auth: {str(e)}")
            return False
    
    def test_account_data(self):
        """Test récupération données compte"""
        print("📊 Test récupération données compte...")
        
        try:
            if not self.connector:
                print("❌ Connecteur non initialisé")
                return False
            
            # Récupération comptes
            accounts = self.connector.get_accounts()
            
            if accounts:
                print(f"✅ {len(accounts)} compte(s) trouvé(s)")
                for account in accounts:
                    print(f"   - {account.get('accountId', 'N/A')} ({account.get('type', 'N/A')})")
                
                self.test_results['tests']['accounts'] = f'SUCCESS: {len(accounts)} comptes'
                return True
            else:
                print("❌ Aucun compte trouvé")
                self.test_results['tests']['accounts'] = 'NO_ACCOUNTS'
                return False
                
        except Exception as e:
            print(f"❌ Erreur données compte: {e}")
            self.test_results['tests']['accounts'] = f'ERROR: {str(e)}'
            self.test_results['errors'].append(f"Accounts: {str(e)}")
            return False
    
    def test_es_market_data(self):
        """Test données marché ES"""
        print("📈 Test données marché ES...")
        
        try:
            if not self.connector:
                print("❌ Connecteur non initialisé")
                return False
            
            # Données ES
            es_data = self.connector.get_market_data('ES')
            
            if es_data:
                print("✅ Données ES récupérées")
                print(f"   - Prix: {es_data.get('price', 'N/A')}")
                print(f"   - Volume: {es_data.get('volume', 'N/A')}")
                
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
    
    def test_options_data(self):
        """Test données options SPX"""
        print("🎯 Test données options SPX...")
        
        try:
            if not self.connector:
                print("❌ Connecteur non initialisé")
                return False
            
            # Options SPX
            options_data = self.connector.get_options_data('SPX')
            
            if options_data:
                print("✅ Données options SPX récupérées")
                print(f"   - Niveaux: {len(options_data.get('levels', []))}")
                
                self.test_results['tests']['options_data'] = 'SUCCESS'
                return True
            else:
                print("❌ Données options non disponibles")
                self.test_results['tests']['options_data'] = 'NO_DATA'
                return False
                
        except Exception as e:
            print(f"❌ Erreur options: {e}")
            self.test_results['tests']['options_data'] = f'ERROR: {str(e)}'
            self.test_results['errors'].append(f"Options: {str(e)}")
            return False
    
    def test_paper_trading(self):
        """Test Paper Trading"""
        print("📝 Test Paper Trading...")
        
        try:
            if not self.connector:
                print("❌ Connecteur non initialisé")
                return False
            
            # Vérifier si Paper Trading disponible
            accounts = self.connector.get_accounts()
            paper_accounts = [acc for acc in accounts if 'PAPER' in str(acc).upper()]
            
            if paper_accounts:
                print("✅ Compte Paper Trading trouvé")
                self.test_results['tests']['paper_trading'] = 'SUCCESS'
                return True
            else:
                print("⚠️ Aucun compte Paper Trading trouvé")
                self.test_results['tests']['paper_trading'] = 'NO_PAPER_ACCOUNT'
                return False
                
        except Exception as e:
            print(f"❌ Erreur Paper Trading: {e}")
            self.test_results['tests']['paper_trading'] = f'ERROR: {str(e)}'
            self.test_results['errors'].append(f"Paper Trading: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Exécuter tous les tests"""
        print("🚀 DÉBUT DES TESTS IBKR RÉELLE")
        print("=" * 50)
        
        tests = [
            ('Gateway', self.test_gateway_connection),
            ('Authentication', self.test_authentication),
            ('Accounts', self.test_account_data),
            ('ES Data', self.test_es_market_data),
            ('Options Data', self.test_options_data),
            ('Paper Trading', self.test_paper_trading)
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
        filename = f"data/test_results/ibkr_real_connection_test_{timestamp}.json"
        
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.test_results, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Résultats sauvegardés: {filename}")

def main():
    """Fonction principale"""
    print("🏆 TEST DE CONNEXION IBKR RÉELLE - MIA_IA SYSTEM")
    print("=" * 60)
    
    tester = TestIBKRConnectionReelle()
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










