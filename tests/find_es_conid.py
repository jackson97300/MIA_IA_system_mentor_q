#!/usr/bin/env python3
"""
Script pour trouver le bon conid ES futures
"""

import sys
import json
from pathlib import Path

# Ajouter le répertoire parent au path
sys.path.append(str(Path(__file__).parent))

from core.ibkr_beta_connector import IBKRBetaConnector, IBKRBetaConfig

def find_es_conid():
    """Trouver le bon conid pour ES futures"""
    
    print("🔍 Recherche du conid ES futures")
    print("=" * 50)
    
    # Configuration
    config = IBKRBetaConfig()
    connector = IBKRBetaConnector(config)
    
    try:
        # Connexion
        if not connector.connect():
            print("❌ Impossible de se connecter")
            return None
        
        # Authentification
        if not connector.config.authenticated:
            if not connector.authenticate():
                print("❌ Authentification échouée")
                return None
        
        print("✅ Connecté et authentifié")
        
        # Recherche ES futures
        print("\n🔍 Recherche contrats ES...")
        
        # Essayer différents symboles
        symbols_to_try = [
            "ES",
            "ES1!",
            "ESZ4",
            "ESM4",
            "ESU4",
            "ESH5",
            "ESM5"
        ]
        
        for symbol in symbols_to_try:
            print(f"\n   Recherche: {symbol}")
            contracts = connector.search_contract(symbol, "FUT")
            
            if contracts:
                print(f"   ✅ {len(contracts)} contrat(s) trouvé(s)")
                
                # Afficher les détails des contrats
                for i, contract in enumerate(contracts[:5]):  # Limiter à 5
                    print(f"      Contrat {i+1}:")
                    print(f"         Conid: {contract.get('conid')}")
                    print(f"         Header: {contract.get('companyHeader', 'N/A')}")
                    print(f"         Description: {contract.get('description', 'N/A')}")
                    print(f"         Symbol: {contract.get('symbol', 'N/A')}")
                    print(f"         SecType: {contract.get('secType', 'N/A')}")
                    
                    # Vérifier si c'est un vrai contrat ES futures
                    contract_info = str(contract.get('companyHeader', '')) + str(contract.get('description', ''))
                    if 'ES' in contract_info and ('future' in contract_info.lower() or 'e-mini' in contract_info.lower()):
                        conid = contract.get('conid')
                        if conid and conid != "-1":
                            print(f"         🎯 CONTRAT ES FUTURES TROUVÉ!")
                            print(f"         📋 Conid à utiliser: {conid}")
                            return conid
            else:
                print(f"   ❌ Aucun contrat trouvé")
        
        print("\n❌ Aucun contrat ES futures valide trouvé")
        return None
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return None
        
    finally:
        connector.disconnect()

def test_conid(conid):
    """Tester un conid spécifique"""
    print(f"\n🧪 Test du conid: {conid}")
    
    config = IBKRBetaConfig()
    connector = IBKRBetaConnector(config)
    
    try:
        if not connector.connect() or not connector.authenticate():
            return False
        
        # Test données de marché
        market_data = connector.get_market_data(conid, ["31", "84"])  # bid, last
        if market_data:
            print(f"✅ Conid {conid} valide - données récupérées")
            print(f"   Données: {market_data}")
            return True
        else:
            print(f"❌ Conid {conid} invalide")
            return False
            
    except Exception as e:
        print(f"❌ Erreur test conid {conid}: {e}")
        return False
        
    finally:
        connector.disconnect()

if __name__ == "__main__":
    # Rechercher le conid
    es_conid = find_es_conid()
    
    if es_conid:
        print(f"\n🎉 Conid ES futures trouvé: {es_conid}")
        
        # Tester le conid
        if test_conid(es_conid):
            print(f"\n✅ Le conid {es_conid} fonctionne correctement!")
            print(f"💡 Utilisez ce conid dans vos scripts: {es_conid}")
        else:
            print(f"\n⚠️ Le conid {es_conid} ne fonctionne pas")
    else:
        print("\n❌ Aucun conid ES futures trouvé")
        print("💡 Essayez de:")
        print("   1. Vérifier que vous avez accès aux futures")
        print("   2. Rechercher manuellement dans TWS")
        print("   3. Vérifier que le marché est ouvert")

