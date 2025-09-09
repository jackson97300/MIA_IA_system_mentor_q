# MIA_IA_SYSTEM - GUIDE D'INSTALLATION ET CONFIGURATION

## 📋 TABLE DES MATIÈRES

1. [Prérequis](#prérequis)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [Intégration IBKR](#intégration-ibkr)
5. [Configuration Discord](#configuration-discord)
6. [Premier démarrage](#premier-démarrage)
7. [Tests et validation](#tests-et-validation)
8. [Dépannage](#dépannage)

---

## 🔧 PRÉREQUIS

### Système d'exploitation
- **Windows 10/11** (recommandé)
- **Linux Ubuntu 20.04+** (compatible)
- **macOS 10.15+** (compatible)

### Spécifications matérielles
- **CPU :** Intel i5/AMD Ryzen 5 ou supérieur
- **RAM :** 8 GB minimum, 16 GB recommandé
- **Stockage :** 50 GB d'espace libre
- **Connexion :** Internet stable (fibre recommandée)

### Logiciels requis
- **Python 3.9+** (3.11 recommandé)
- **Git** (pour cloner le repository)
- **IBKR TWS/Gateway** (pour trading)
- **Discord** (pour notifications)

---

## 📦 INSTALLATION

### 1. Cloner le repository

```bash
# Cloner le repository
git clone https://github.com/votre-username/MIA_IA_SYSTEM.git
cd MIA_IA_SYSTEM

# Créer environnement virtuel
python -m venv venv

# Activer environnement virtuel
# Windows
venv\Scripts\activate
# Linux/macOS
source venv/bin/activate
```

### 2. Installer les dépendances

```bash
# Installer les dépendances principales
pip install -r requirements.txt

# Installer les dépendances supplémentaires
pip install psutil discord.py ib_insync pandas numpy scikit-learn xgboost
```

### 3. Vérifier l'installation

```bash
# Tester l'import des modules principaux
python -c "import automation_main; print('✅ Installation réussie')"

# Tester le monitoring
python -c "import monitoring_continu; print('✅ Monitoring installé')"

# Tester les modules ML
python -c "import ml.ensemble_filter; print('✅ ML installé')"
```

---

## ⚙️ CONFIGURATION

### 1. Configuration de base

Créer le fichier `config/local_config.py` :

```python
# Configuration locale MIA_IA_SYSTEM
import os
from pathlib import Path

# Chemins de base
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"
MODELS_DIR = BASE_DIR / "models"

# Créer les répertoires nécessaires
for directory in [DATA_DIR, LOGS_DIR, MODELS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Configuration IBKR
IBKR_CONFIG = {
    "host": "localhost",
    "port": 7497,  # 7497 pour TWS, 4001 pour Gateway
    "client_id": 1,
    "timeout": 20,
    "retry_interval": 5
}

# Configuration Discord
DISCORD_CONFIG = {
    "webhook_url": "VOTRE_WEBHOOK_URL_DISCORD",
    "mentor_channel": "mentor-system",
    "alerts_channel": "trading-alerts"
}

# Configuration base de données
DATABASE_CONFIG = {
    "path": str(DATA_DIR / "mia_system.db"),
    "backup_interval": 3600,  # 1 heure
    "max_backups": 24
}

# Configuration logging
LOGGING_CONFIG = {
    "level": "INFO",
    "file": str(LOGS_DIR / "mia_system.log"),
    "max_size": 10 * 1024 * 1024,  # 10 MB
    "backup_count": 5
}

# Configuration trading
TRADING_CONFIG = {
    "symbol": "ES",  # E-mini S&P 500
    "exchange": "CME",
    "currency": "USD",
    "max_position_size": 1,
    "daily_loss_limit": 200.0,
    "min_signal_confidence": 0.75,
    "trading_start_hour": 9,
    "trading_end_hour": 16
}

# Configuration ML
ML_CONFIG = {
    "ensemble_enabled": True,
    "gamma_cycles_enabled": True,
    "model_update_interval": 3600,
    "cache_enabled": True,
    "cache_ttl_hours": 6
}

# Configuration monitoring
MONITORING_CONFIG = {
    "enabled": True,
    "interval_seconds": 30,
    "alert_thresholds": {
        "cpu_critical": 90.0,
        "cpu_warning": 70.0,
        "memory_critical": 85.0,
        "memory_warning": 70.0,
        "latency_critical": 5.0,
        "latency_warning": 2.0
    }
}
```

### 2. Configuration des variables d'environnement

Créer le fichier `.env` :

```bash
# Configuration IBKR
IBKR_HOST=localhost
IBKR_PORT=7497
IBKR_CLIENT_ID=1

# Configuration Discord
DISCORD_WEBHOOK_URL=VOTRE_WEBHOOK_URL_DISCORD

# Configuration base de données
DB_PATH=data/mia_system.db

# Configuration logging
LOG_LEVEL=INFO
LOG_FILE=logs/mia_system.log

# Configuration trading
TRADING_SYMBOL=ES
TRADING_EXCHANGE=CME
TRADING_CURRENCY=USD

# Configuration ML
ML_ENSEMBLE_ENABLED=true
ML_GAMMA_CYCLES_ENABLED=true

# Configuration monitoring
MONITORING_ENABLED=true
MONITORING_INTERVAL=30
```

### 3. Configuration des logs

Créer le fichier `config/logging_config.py` :

```python
import logging
import logging.handlers
from pathlib import Path

def setup_logging():
    """Configuration du système de logging"""
    
    # Créer le répertoire logs
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    
    # Configuration du logger principal
    logger = logging.getLogger("MIA_IA_SYSTEM")
    logger.setLevel(logging.INFO)
    
    # Handler pour fichier
    file_handler = logging.handlers.RotatingFileHandler(
        "logs/mia_system.log",
        maxBytes=10*1024*1024,  # 10 MB
        backupCount=5
    )
    file_handler.setLevel(logging.INFO)
    
    # Handler pour console
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # Format
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # Ajouter les handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger
```

---

## 🔌 INTÉGRATION IBKR

### 1. Installation IBKR TWS/Gateway

#### Téléchargement
1. Aller sur [Interactive Brokers](https://www.interactivebrokers.com/)
2. Télécharger **TWS** (Trader Workstation) ou **IB Gateway**
3. Installer selon votre système d'exploitation

#### Configuration TWS
1. **Lancer TWS**
2. **File → Global Configuration**
3. **API → Settings**
4. **Activer** : "Enable ActiveX and Socket Clients"
5. **Port** : 7497 (TWS) ou 4001 (Gateway)
6. **Permissions** : "Allow connections from localhost"

#### Configuration API
1. **File → Global Configuration**
2. **API → Precautions**
3. **Désactiver** : "Bypass Order Precautions for API Orders"
4. **Activer** : "Create API order log file"

### 2. Test de connexion

Créer le fichier `test_ibkr_connection.py` :

```python
#!/usr/bin/env python3
"""
Test de connexion IBKR
"""

from ib_insync import *
import asyncio

async def test_ibkr_connection():
    """Tester la connexion IBKR"""
    
    print("🔌 Test de connexion IBKR...")
    
    try:
        # Créer la connexion
        ib = IB()
        
        # Connexion
        await ib.connect('localhost', 7497, clientId=1)
        
        # Vérifier la connexion
        if ib.isConnected():
            print("✅ Connexion IBKR réussie")
            
            # Récupérer les informations du compte
            accounts = ib.managedAccounts()
            print(f"📊 Comptes disponibles: {accounts}")
            
            # Récupérer le solde
            if accounts:
                account = accounts[0]
                account_summary = ib.accountSummary(account)
                print(f"💰 Solde: {account_summary}")
            
        else:
            print("❌ Échec de connexion IBKR")
            
    except Exception as e:
        print(f"❌ Erreur connexion: {e}")
        
    finally:
        # Fermer la connexion
        if ib.isConnected():
            await ib.disconnect()

if __name__ == "__main__":
    asyncio.run(test_ibkr_connection())
```

### 3. Exécuter le test

```bash
python test_ibkr_connection.py
```

---

## 📱 CONFIGURATION DISCORD

### 1. Créer un serveur Discord

1. **Créer un nouveau serveur** sur Discord
2. **Créer les canaux** :
   - `#trading-signals` : Signaux de trading
   - `#trading-execution` : Exécution des trades
   - `#system-alerts` : Alertes système
   - `#mentor-system` : Conseils mentor
   - `#daily-reports` : Rapports quotidiens

### 2. Configurer le webhook

1. **Canal** → **Modifier le canal**
2. **Intégrations** → **Webhooks**
3. **Nouveau webhook**
4. **Copier l'URL** du webhook

### 3. Tester la connexion Discord

Créer le fichier `test_discord_webhook.py` :

```python
#!/usr/bin/env python3
"""
Test webhook Discord
"""

import aiohttp
import asyncio
import json

async def test_discord_webhook():
    """Tester le webhook Discord"""
    
    webhook_url = "VOTRE_WEBHOOK_URL_DISCORD"
    
    print("📱 Test webhook Discord...")
    
    try:
        # Message de test
        message = {
            "embeds": [{
                "title": "🧪 Test MIA_IA_SYSTEM",
                "description": "Test de connexion Discord réussi !",
                "color": 0x00ff00,
                "fields": [
                    {
                        "name": "Status",
                        "value": "✅ Connecté",
                        "inline": True
                    },
                    {
                        "name": "Système",
                        "value": "MIA_IA_SYSTEM v3.0.0",
                        "inline": True
                    }
                ]
            }]
        }
        
        # Envoyer le message
        async with aiohttp.ClientSession() as session:
            async with session.post(webhook_url, json=message) as response:
                if response.status == 204:
                    print("✅ Webhook Discord fonctionnel")
                else:
                    print(f"❌ Erreur webhook: {response.status}")
                    
    except Exception as e:
        print(f"❌ Erreur Discord: {e}")

if __name__ == "__main__":
    asyncio.run(test_discord_webhook())
```

### 4. Exécuter le test

```bash
python test_discord_webhook.py
```

---

## 🚀 PREMIER DÉMARRAGE

### 1. Script de démarrage

Créer le fichier `start_mia_system.py` :

```python
#!/usr/bin/env python3
"""
Script de démarrage MIA_IA_SYSTEM
"""

import asyncio
import logging
from pathlib import Path

# Imports locaux
from automation_main import MIAAutomationSystem, AutomationConfig
from monitoring_continu import monitor
from config.logging_config import setup_logging

async def start_mia_system():
    """Démarrer le système MIA_IA_SYSTEM"""
    
    print("🚀 Démarrage MIA_IA_SYSTEM v3.0.0")
    print("=" * 50)
    
    # Configuration logging
    logger = setup_logging()
    logger.info("Démarrage système")
    
    try:
        # Configuration
        config = AutomationConfig()
        config.trading.max_position_size = 1
        config.trading.daily_loss_limit = 200.0
        config.trading.min_signal_confidence = 0.75
        config.ml.ensemble_enabled = True
        config.confluence.base_threshold = 0.25
        
        # Créer le système
        system = MIAAutomationSystem(config)
        logger.info("Système initialisé")
        
        # Démarrer le monitoring
        monitoring_task = asyncio.create_task(
            monitor.start_monitoring(interval_seconds=30)
        )
        logger.info("Monitoring démarré")
        
        # Démarrer le système principal
        await system.start()
        
    except Exception as e:
        logger.error(f"Erreur démarrage: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(start_mia_system())
```

### 2. Exécuter le système

```bash
# Démarrage normal
python start_mia_system.py

# Démarrage avec logs détaillés
python start_mia_system.py --verbose

# Démarrage en mode test
python start_mia_system.py --test-mode
```

---

## 🧪 TESTS ET VALIDATION

### 1. Test complet du système

```bash
# Test d'intégration complet
python test_system_complet_final.py

# Test des modules individuels
python -m pytest tests/

# Test de performance
python test_performance.py
```

### 2. Validation des composants

#### Test ML Ensemble
```python
from ml.ensemble_filter import MLEnsembleFilter

# Créer l'instance
ml_filter = MLEnsembleFilter()

# Test features
test_features = {
    "confluence_score": 0.75,
    "momentum_flow": 0.8,
    "trend_alignment": 0.7,
    "volume_profile": 0.6,
    "support_resistance": 0.5,
    "market_regime_score": 0.6,
    "volatility_regime": 0.5,
    "time_factor": 0.5
}

# Prédiction
result = ml_filter.predict_signal_quality(test_features)
print(f"Signal approuvé: {result.signal_approved}")
print(f"Confidence: {result.confidence:.3f}")
```

#### Test Gamma Cycles
```python
from ml.gamma_cycles import GammaCyclesAnalyzer, GammaCycleConfig

# Configuration
config = GammaCycleConfig()
analyzer = GammaCyclesAnalyzer(config)

# Analyse
analysis = analyzer.analyze_gamma_cycle()
print(f"Phase: {analysis.gamma_phase.value}")
print(f"Facteur ajustement: {analysis.adjustment_factor:.2f}")
```

#### Test Monitoring
```python
from monitoring_continu import monitor

# Statut système
status = monitor.get_system_status()
print(f"CPU: {status.get('cpu_percent', 0):.1f}%")
print(f"Mémoire: {status.get('memory_percent', 0):.1f}%")
```

### 3. Validation des performances

#### Métriques système
```python
# CPU < 50%
# Mémoire < 80%
# Disque < 90%
# Latence < 1s
```

#### Métriques trading
```python
# Win Rate > 60%
# Profit Factor > 2.0
# Drawdown < 15%
# Trades/jour: 5-10
```

---

## 🔧 DÉPANNAGE

### Problèmes courants

#### 1. Erreur de connexion IBKR
```bash
# Vérifier TWS/Gateway
- TWS est-il lancé ?
- Port correct (7497/4001) ?
- API activée ?
- Permissions configurées ?

# Test de connexion
python test_ibkr_connection.py
```

#### 2. Erreur Discord webhook
```bash
# Vérifier webhook
- URL correcte ?
- Permissions webhook ?
- Canal accessible ?

# Test webhook
python test_discord_webhook.py
```

#### 3. Erreur modules Python
```bash
# Vérifier installation
pip list | grep -E "(pandas|numpy|scikit-learn|xgboost)"

# Réinstaller si nécessaire
pip install --upgrade pandas numpy scikit-learn xgboost
```

#### 4. Erreur base de données
```bash
# Vérifier permissions
ls -la data/

# Réinitialiser si nécessaire
rm data/mia_system.db
python -c "from core.database import init_database; init_database()"
```

### Logs et diagnostics

#### Vérifier les logs
```bash
# Logs système
tail -f logs/mia_system.log

# Logs trading
tail -f logs/trading.log

# Logs ML
tail -f logs/ml.log
```

#### Commandes de diagnostic
```bash
# Statut système
python -c "from monitoring_continu import monitor; print(monitor.get_system_status())"

# Test imports
python -c "import automation_main; print('✅ OK')"

# Test configuration
python -c "from config.automation_config import AutomationConfig; config = AutomationConfig(); print('✅ Config OK')"
```

### Procédures d'urgence

#### Arrêt d'urgence
```python
# Arrêt immédiat
await system.emergency_stop()

# Fermeture positions
await system.close_all_positions()
```

#### Redémarrage sécurisé
```python
# Vérifications préalables
await system.pre_start_checks()

# Redémarrage
await system.secure_startup()
```

---

## 📚 RESSOURCES ADDITIONNELLES

### Documentation
- **Architecture** : `docs/ARCHITECTURE_MASTER.md`
- **API Reference** : `docs/API_REFERENCE.md`
- **Configuration** : `docs/CONFIGURATION_GUIDE.md`

### Support
- **Logs** : `logs/`
- **Tests** : `tests/`
- **Configuration** : `config/`

### Commandes utiles
```bash
# Mise à jour système
git pull origin main

# Sauvegarde configuration
cp config/local_config.py config/local_config_backup.py

# Restauration configuration
cp config/local_config_backup.py config/local_config.py

# Nettoyage logs
find logs/ -name "*.log" -mtime +7 -delete
```

---

## 🎯 CONCLUSION

**MIA_IA_SYSTEM** est maintenant correctement installé et configuré !

### ✅ Checklist finale
- [ ] **Installation Python** : ✅
- [ ] **Dépendances installées** : ✅
- [ ] **Configuration créée** : ✅
- [ ] **IBKR connecté** : ✅
- [ ] **Discord configuré** : ✅
- [ ] **Tests validés** : ✅
- [ ] **Système opérationnel** : ✅

### 🚀 Prochaines étapes
1. **Paper Trading** : Tester avec IBKR Paper
2. **Optimisation** : Ajuster les paramètres
3. **Production** : Passer en mode live
4. **Monitoring** : Surveiller les performances

**Bonne chance avec MIA_IA_SYSTEM ! 🎯**

---

*Guide d'installation MIA_IA_SYSTEM v3.0.0 - Août 2025* 