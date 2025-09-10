# 🚀 GUIDE IBKR WEB API REST - MIA_IA_SYSTEM

## 📋 Vue d'ensemble

Ce guide détaille l'implémentation de l'**IBKR Web API REST** pour MIA_IA_SYSTEM, remplaçant l'ancien connecteur TWS/Gateway par une API REST moderne et stable.

**Avantages majeurs :**
- ✅ **Pas de TWS/Gateway** : Connexion directe HTTP
- ✅ **Plus stable** : Moins de plantages
- ✅ **Plus simple** : API REST standard
- ✅ **Moins cher** : Inclus dans votre abonnement (19.44€/mois)
- ✅ **OAuth support** : Authentification moderne

---

## 🎯 ARCHITECTURE MIA_IA AVEC IBKR WEB API

### **Architecture optimisée :**
```
IBKR Web API REST → MIA_IA → Sierra Chart → AMP Futures
```

### **Flux de données :**
1. **IBKR Web API** : Données ES futures + options SPX
2. **MIA_IA** : Analyse Battle Navale
3. **Sierra Chart** : Exécution ordres
4. **AMP Futures** : Compte de trading

---

## 🔧 CONFIGURATION IBKR WEB API

### **Étape 1 : Activation Web API**

1. **Connexion IBKR** :
   - Allez sur [IBKR Client Portal](https://www.interactivebrokers.com/portal)
   - Connectez-vous à votre compte

2. **Activation API** :
   - Allez dans **Settings** → **API Settings**
   - Activez **Web API**
   - Configurez les permissions nécessaires

3. **Génération API Keys** :
   - Créez une nouvelle **API Key**
   - Notez la **API Key** et **API Secret**
   - Configurez les **IP autorisées**

### **Étape 2 : Configuration MIA_IA**

1. **Installation dépendances** :
```bash
pip install aiohttp pandas asyncio
```

2. **Configuration fichier** :
```python
# config/ibkr_web_api_config.py
from data.ibkr_web_api_adapter import IBKRWebAPIConfig

MIA_IA_IBKR_WEB_API_CONFIG = IBKRWebAPIConfig(
    api_key="VOTRE_API_KEY",
    api_secret="VOTRE_API_SECRET", 
    account_id="VOTRE_ACCOUNT_ID",
    paper_trading=True,
    enable_trading=False,  # Désactivé pour tests
    enable_market_data=True
)
```

---

## 📊 ENDPOINTS IBKR WEB API DISPONIBLES

### **Account Management :**
- `GET /account/{accountId}/summary` : Résumé compte
- `GET /account/{accountId}/positions` : Positions actuelles
- `GET /account/{accountId}/orders` : Ordres actifs

### **Market Data :**
- `GET /market_data/{symbol}/snapshot` : Données temps réel
- `GET /market_data/{symbol}/history` : Données historiques
- `GET /market_data/{symbol}/options` : Options chain

### **Trading :**
- `POST /account/{accountId}/orders` : Placer ordre
- `PUT /account/{accountId}/orders/{orderId}` : Modifier ordre
- `DELETE /account/{accountId}/orders/{orderId}` : Annuler ordre

---

## 🎯 INTÉGRATION MIA_IA

### **Étape 1 : Remplacement connecteur**

1. **Modifier `core/ibkr_connector.py`** :
```python
# Remplacer l'ancien connecteur par le nouveau
from data.ibkr_web_api_adapter import IBKRWebAPIAdapter, IBKRWebAPIConfig

class IBKRConnector:
    def __init__(self, config: IBKRWebAPIConfig):
        self.web_api = IBKRWebAPIAdapter(config)
    
    async def connect(self) -> bool:
        return await self.web_api.connect()
    
    async def get_market_data(self, symbol: str) -> MarketData:
        return await self.web_api.get_market_data(symbol)
```

### **Étape 2 : Test connexion**

1. **Test basique** :
```python
python data/ibkr_web_api_adapter.py
```

2. **Test MIA_IA** :
```python
python lance_mia_ia_web_api.py
```

---

## 🔍 FONCTIONNALITÉS BATTLE NAVALE

### **Données ES Futures :**
- ✅ **Temps réel** : Prix, volume, bid/ask
- ✅ **Historique** : Données 1min, 5min, 15min, 1H
- ✅ **VWAP** : Volume Weighted Average Price
- ✅ **Delta** : Calcul automatique

### **Options SPX :**
- ✅ **Options chain** : Calls et puts
- ✅ **Gamma levels** : Analyse automatique
- ✅ **Call/Put walls** : Détection automatique
- ✅ **Gamma exposure** : Calcul en temps réel

### **Order Flow :**
- ⚠️ **Limité** : Pas de depth complète
- ✅ **Volume analysis** : Buy/sell pressure
- ✅ **Imbalance** : Calcul automatique

---

## 🚀 PLAN DE DÉPLOIEMENT

### **Phase 1 : Configuration (1 semaine)**
- [ ] Activation IBKR Web API
- [ ] Configuration MIA_IA
- [ ] Test connexion basique
- [ ] Validation données ES futures

### **Phase 2 : Intégration (1 semaine)**
- [ ] Remplacement connecteur TWS
- [ ] Test Battle Navale
- [ ] Validation options SPX
- [ ] Test performance

### **Phase 3 : Déploiement (1 semaine)**
- [ ] MIA_IA avec Web API
- [ ] Monitoring performance
- [ ] Optimisation paramètres
- [ ] Documentation finale

---

## 💰 AVANTAGES ÉCONOMIQUES

### **Coût réduit :**
- **IBKR Web API** : Inclus dans abonnement (19.44€/mois)
- **Pas de TWS/Gateway** : Économie ressources
- **Moins de maintenance** : API plus simple

### **Comparaison coûts :**
| Solution | Coût mensuel | Stabilité | Complexité |
|----------|-------------|-----------|------------|
| **IBKR Web API** | 19.44€ | ⭐⭐⭐⭐⭐ | ⭐⭐ |
| **Polygon.io** | 99€ | ⭐⭐⭐⭐ | ⭐⭐ |
| **TWS/Gateway** | 19.44€ | ⭐⭐ | ⭐⭐⭐⭐⭐ |

---

## 🛡️ SÉCURITÉ ET AUTHENTIFICATION

### **Méthodes d'authentification :**

1. **OAuth 2.0** (Recommandé) :
```python
auth_data = {
    "grant_type": "client_credentials",
    "client_id": api_key,
    "client_secret": api_secret
}
```

2. **API Key simple** (Fallback) :
```python
headers = {
    "Authorization": f"Bearer {api_key}"
}
```

### **Sécurité :**
- ✅ **HTTPS** : Toutes les requêtes
- ✅ **Rate limiting** : 50 requêtes/minute
- ✅ **IP restrictions** : IP autorisées uniquement
- ✅ **Token expiration** : Renouvellement automatique

---

## 📈 MONITORING ET LOGS

### **Logs automatiques :**
```python
# Exemple de logs
2025-01-XX 10:30:15 INFO ✅ IBKR Web API connecté: U123456
2025-01-XX 10:30:16 INFO ✅ Market data ES: 4850.25
2025-01-XX 10:30:17 INFO ✅ Données ES: 100 barres
2025-01-XX 10:30:18 INFO ✅ Options SPX: 150 contrats
```

### **Métriques de performance :**
- **Latence** : < 100ms
- **Uptime** : > 99.9%
- **Rate limit** : < 80% utilisation
- **Erreurs** : < 0.1%

---

## 🔧 DÉPANNAGE

### **Problèmes courants :**

1. **Erreur 401 - Non autorisé** :
   - Vérifier API key/secret
   - Vérifier IP autorisée
   - Vérifier permissions compte

2. **Erreur 429 - Rate limit** :
   - Réduire fréquence requêtes
   - Augmenter délai entre requêtes
   - Vérifier rate limiting

3. **Erreur 500 - Serveur** :
   - Réessayer après délai
   - Vérifier statut IBKR
   - Contacter support si persistant

### **Logs de debug :**
```python
# Activer debug logs
logging.getLogger('data.ibkr_web_api_adapter').setLevel(logging.DEBUG)
```

---

## 📞 SUPPORT ET CONTACT

### **Documentation IBKR :**
- [IBKR Web API Reference](https://www.interactivebrokers.com/campus/ibkr-api-page/webapi-ref/)
- [IBKR API Documentation](https://www.interactivebrokers.com/en/trading/ib-api.php)

### **Support MIA_IA :**
- **Questions techniques** : Configuration API
- **Questions intégration** : MIA_IA + Web API
- **Questions performance** : Optimisation

---

## 🎯 PROCHAINES ÉTAPES

### **Immédiat :**
1. **Activer IBKR Web API** dans votre compte
2. **Générer API keys** et configurer
3. **Tester connexion** basique

### **Court terme :**
1. **Intégrer MIA_IA** avec Web API
2. **Tester Battle Navale** avec vraies données
3. **Valider performance** et stabilité

### **Moyen terme :**
1. **Déployer MIA_IA** avec Web API
2. **Optimiser paramètres** Battle Navale
3. **Scaling** et monétisation

---

**Document créé le :** [Date]
**Version :** 1.0
**Dernière mise à jour :** [Date]
**Statut :** En cours d'implémentation

---

## 🚀 CONCLUSION

L'**IBKR Web API REST** est la solution parfaite pour MIA_IA_SYSTEM :

**✅ Avantages :**
- Plus stable que TWS/Gateway
- Plus simple à configurer
- Moins cher que Polygon
- Données complètes ES + SPX

**🎯 Résultat attendu :**
- MIA_IA opérationnel en 2-3 semaines
- Performance Battle Navale optimale
- Coût réduit de 80% vs Polygon
- Stabilité maximale

**Prêt à déployer MIA_IA avec IBKR Web API REST !** 🚀
















