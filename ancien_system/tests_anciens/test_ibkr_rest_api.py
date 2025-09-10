#!/usr/bin/env python3
"""
MIA_IA_SYSTEM - Test API REST IBKR
Test et comparaison avec TWS/Gateway
"""

import asyncio
import json
from datetime import datetime
from pathlib import Path

def test_ibkr_rest_api():
    """Test API REST IBKR"""
    print("🧪 Test API REST IBKR...")
    
    try:
        from core.ibkr_rest_connector import create_ibkr_rest_connector
        
        # Configuration API REST
        config = {
            'ibkr_rest_url': 'https://api.ibkr.com',
            'api_version': 'v1',
            'client_id': 'test_client'
        }
        
        connector = create_ibkr_rest_connector(config)
        
        # Test connexion
        success = asyncio.run(connector.connect())
        
        if success:
            print("✅ API REST IBKR accessible")
            
            # Test endpoints
            print("\n🔍 Test endpoints API REST...")
            
            # Test echo (sans authentification)
            try:
                import requests
                response = requests.get('https://api.ibkr.com/v1/echo/https', timeout=10)
                if response.status_code == 200:
                    print("✅ Endpoint echo accessible")
                else:
                    print(f"⚠️ Endpoint echo: {response.status_code}")
            except Exception as e:
                print(f"❌ Erreur endpoint echo: {e}")
            
            # Test documentation
            try:
                response = requests.get('https://api.ibkr.com/gw/api/v3/api-docs', timeout=10)
                if response.status_code == 200:
                    print("✅ Documentation API accessible")
                    
                    # Analyser endpoints disponibles
                    api_docs = response.json()
                    paths = api_docs.get('paths', {})
                    
                    print(f"\n📊 ENDPOINTS DISPONIBLES ({len(paths)}):")
                    
                    # Grouper par catégorie
                    categories = {}
                    for path, methods in paths.items():
                        for method, details in methods.items():
                            if isinstance(details, dict):
                                tags = details.get('tags', ['Autre'])
                                for tag in tags:
                                    if tag not in categories:
                                        categories[tag] = []
                                    categories[tag].append(f"{method.upper()} {path}")
                    
                    for category, endpoints in categories.items():
                        print(f"\n   📂 {category} ({len(endpoints)} endpoints):")
                        for endpoint in endpoints[:3]:  # Afficher les 3 premiers
                            print(f"      - {endpoint}")
                        if len(endpoints) > 3:
                            print(f"      ... et {len(endpoints) - 3} autres")
                    
                else:
                    print(f"❌ Documentation API: {response.status_code}")
            except Exception as e:
                print(f"❌ Erreur documentation API: {e}")
            
            asyncio.run(connector.disconnect())
            return True
        else:
            print("❌ API REST IBKR non accessible")
            return False
            
    except ImportError:
        print("❌ Module ibkr_rest_connector non trouvé")
        return False
    except Exception as e:
        print(f"❌ Erreur test API REST: {e}")
        return False

def compare_tws_vs_rest():
    """Comparaison TWS/Gateway vs API REST"""
    print("\n📊 COMPARAISON TWS/GATEWAY vs API REST")
    print("=" * 60)
    
    comparison = {
        "TWS/Gateway": {
            "✅ Avantages": [
                "Connexion directe aux marchés",
                "Données temps réel",
                "Trading en temps réel",
                "Support complet des ordres",
                "Historique complet"
            ],
            "❌ Inconvénients": [
                "Logiciel à installer",
                "Problèmes de connexion fréquents",
                "Configuration complexe",
                "Dépendance à TWS/Gateway",
                "Ports à configurer"
            ]
        },
        "API REST": {
            "✅ Avantages": [
                "Pas d'installation requise",
                "API moderne et stable",
                "Documentation complète",
                "Authentification OAuth/JWT",
                "Endpoints spécialisés"
            ],
            "❌ Inconvénients": [
                "Nécessite authentification",
                "Limites de rate",
                "Pas de données temps réel",
                "Fonctionnalités limitées",
                "Coûts potentiels"
        ]
    }
    
    for platform, details in comparison.items():
        print(f"\n🔹 {platform}:")
        for category, items in details.items():
            print(f"   {category}:")
            for item in items:
                print(f"      {item}")

def analyze_api_documentation():
    """Analyser la documentation API téléchargée"""
    print("\n📄 ANALYSE DOCUMENTATION API")
    print("=" * 60)
    
    # Chercher le fichier API
    api_file = Path('ibkr_api_docs.json')
    if not api_file.exists():
        print("❌ Fichier ibkr_api_docs.json non trouvé")
        return
    
    try:
        with open(api_file, 'r', encoding='utf-8') as f:
            api_docs = json.load(f)
        
        # Informations générales
        info = api_docs.get('info', {})
        print(f"📋 Titre: {info.get('title', 'N/A')}")
        print(f"📋 Version: {info.get('version', 'N/A')}")
        print(f"📋 Description: {info.get('description', 'N/A')}")
        
        # Serveurs
        servers = api_docs.get('servers', [])
        print(f"\n🌐 SERVEURS ({len(servers)}):")
        for server in servers:
            print(f"   - {server.get('description', 'N/A')}: {server.get('url')}")
        
        # Endpoints par catégorie
        paths = api_docs.get('paths', {})
        print(f"\n🔗 ENDPOINTS ({len(paths)}):")
        
        # Compter par méthode HTTP
        methods_count = {}
        for path, methods in paths.items():
            for method in methods.keys():
                methods_count[method.upper()] = methods_count.get(method.upper(), 0) + 1
        
        for method, count in methods_count.items():
            print(f"   - {method}: {count} endpoints")
        
        # Endpoints trading spécifiques
        trading_endpoints = []
        for path, methods in paths.items():
            for method, details in methods.items():
                if isinstance(details, dict):
                    tags = details.get('tags', [])
                    if any('Trading' in tag for tag in tags):
                        trading_endpoints.append(f"{method.upper()} {path}")
        
        print(f"\n🎯 ENDPOINTS TRADING ({len(trading_endpoints)}):")
        for endpoint in trading_endpoints[:10]:  # Afficher les 10 premiers
            print(f"   - {endpoint}")
        if len(trading_endpoints) > 10:
            print(f"   ... et {len(trading_endpoints) - 10} autres")
        
        print(f"\n✅ Analyse terminée")
        
    except Exception as e:
        print(f"❌ Erreur analyse: {e}")

def main():
    """Test principal"""
    print("🚀 MIA_IA_SYSTEM - Test API REST IBKR")
    print("=" * 60)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Test API REST
    rest_success = test_ibkr_rest_api()
    
    # Comparaison
    compare_tws_vs_rest()
    
    # Analyse documentation
    analyze_api_documentation()
    
    print()
    print("=" * 60)
    print("📊 RÉSUMÉ TEST API REST IBKR")
    print(f"API REST accessible: {'✅' if rest_success else '❌'}")
    
    if rest_success:
        print("🎉 API REST IBKR opérationnelle !")
        print("\n📋 RECOMMANDATIONS:")
        print("1. ✅ API REST disponible et fonctionnelle")
        print("2. 🔧 Alternative moderne à TWS/Gateway")
        print("3. 📚 Documentation complète disponible")
        print("4. 🚀 Intégration possible dans MIA_IA_SYSTEM")
        print("5. 💡 Solution de secours pour problèmes TWS")
    else:
        print("❌ API REST IBKR non accessible")
        print("💡 Continuer avec TWS/Gateway")

if __name__ == "__main__":
    main()
















