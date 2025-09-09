# 📊 Analyseur de Données de Marché - MIA System

## 🎯 Objectif

Ce script Python analyse le fichier `chart_3_20250904.jsonl` pour :
- **Détecter** toutes les familles d'événements réellement collectées
- **Valider la cohérence** des champs clés selon les règles métiers
- **Produire un rapport** détaillé + un CSV des anomalies

## 🚀 Comment Exécuter

### Prérequis
- Python 3.7+ installé
- Fichier `chart_3_20250904.jsonl` dans le répertoire courant

### Commande d'exécution
```bash
python analyze_chart_data.py
```

### Exécution alternative
```bash
python3 analyze_chart_data.py
```

## 📁 Fichiers Générés

### 1. `report.md`
Rapport détaillé incluant :
- **Inventaire** des types de données présents/absents
- **Statistiques** par type (min/avg/max des champs numériques)
- **Top 10 anomalies** par règle avec exemples
- **Résumé** par famille (OK/Warnings/Errors)

### 2. `anomalies.csv`
Fichier CSV avec toutes les violations détectées :
- `t` : Timestamp de l'anomalie
- `type` : Type de données concerné
- `rule` : Règle violée
- `message` : Description de l'anomalie
- `snippet` : Extrait des données problématiques

## 🔍 Règles de Cohérence Vérifiées

### 📊 Basedata (OHLCV)
- `h ≥ o`, `l ≤ o`, `h ≥ c`, `l ≤ c`
- `v ≥ 0`
- `bidvol + askvol ≤ v` (tolérance configurable)

### 📈 NBCV (Net Buying vs Selling)
- `delta_calc = ask - bid` doit correspondre à `delta`
- `total ≈ ask + bid` (tolérance 1-2 lots)
- `trades` entier non négatif
- `cumdelta` redémarre à 0 en nouvelle session

### 💰 Quotes
- `ask ≥ bid`
- `spread = ask - bid` vérifié
- `mid = (ask+bid)/2` vérifié
- Détection d'échelle incohérente (×10/×100)

### 📊 Depth
- Niveaux consécutifs sans trous
- `size ≥ 0`
- Prix monotones (BID décroissant, ASK croissant)

### 📊 VWAP/PVWAP
- Valeurs proches des prix des barres
- Bandes `upX > v > dnX` respectées
- Détection de décalages d'échelle

### 📊 VVA (Volume Profile)
- `val ≥ vah` signalé comme anormal
- `vpoc` dans la fourchette [min(h,l), max(h,l)]

### 📊 VAP (Volume at Price)
- Agrégation par prix d'une même barre
- Somme des volumes ≈ volume de la barre (±5%)

### 📊 Trades
- `qty > 0`
- Prix dans [l,h] de la barre courante

## ⚙️ Configuration

### Constantes de Tolérance
```python
VOL_TOL = 2                    # Tolérance volume
VAP_MATCH_TOL = 0.05          # Tolérance correspondance VAP
QUOTE_SCALE_CANDIDATES = [1, 0.1, 0.01, 10, 100]  # Échelles à tester
PRICE_TOL = 0.01              # Tolérance prix
```

## 📊 Types de Données Supportés

- `basedata` : Données OHLCV
- `vwap` : VWAP et bandes
- `vva` : Volume Profile (VAH, VAL, VPOC)
- `pvwap` : PVWAP et bandes
- `vix` : Données VIX
- `nbcv` : Net Buying vs Selling
- `quote` : Quotes bid/ask
- `depth` : Profondeur de marché
- `vap` : Volume at Price
- `trade` : Trades individuels

## 🔧 Fonctionnalités Techniques

- **Lecture en streaming** pour gérer les gros fichiers
- **Gestion des erreurs** robuste (lignes corrompues, JSON invalide)
- **Parsing tolérant** avec gestion des exceptions
- **Analyse croisée** entre différents types de données
- **Détection automatique** des problèmes d'échelle
- **Rapport structuré** en Markdown et CSV

## 📈 Exemple de Sortie Console

```
🚀 Analyseur de Données de Marché - MIA System
============================================================
🔍 Analyse du fichier: chart_3_20250904.jsonl
📊 Début de l'analyse...
   Traité 10,000 lignes...
   Traité 20,000 lignes...
✅ Analyse terminée: 25,432 lignes traitées, 3 corrompues
📝 Génération du rapport...

============================================================
📊 RÉSUMÉ DE L'ANALYSE
============================================================
📈 Total des enregistrements: 25,432
⚠️  Total des anomalies: 47
📁 Types de données détectés: 8

🔍 Répartition des anomalies par règle:
   ohlc_high_low: 12
   volume_mismatch: 8
   timestamp_decreasing: 5
   ...

📋 Types de données analysés:
   ✅ basedata: 5,432 enregistrements
   ⚠️(15) nbcv: 8,765 enregistrements
   ✅ quote: 3,210 enregistrements
   ...
```

## 🚨 Dépannage

### Fichier non trouvé
```
❌ Fichier non trouvé: chart_3_20250904.jsonl
💡 Assurez-vous que le fichier est dans le répertoire courant
```

### Erreur de mémoire
- Le script utilise la lecture en streaming
- Si problème persiste, vérifiez l'espace disque disponible

### Erreur d'encodage
- Le script utilise UTF-8 par défaut
- Vérifiez l'encodage du fichier source

## 📝 Personnalisation

### Ajouter de nouvelles règles
1. Créer une nouvelle méthode `check_*_coherence()`
2. L'appeler dans `process_record()`
3. Utiliser `add_anomaly()` pour signaler les violations

### Modifier les tolérances
- Ajuster les constantes au début du script
- Recalculer selon vos besoins métiers

## 🤝 Support

Pour toute question ou amélioration :
- Vérifiez les logs d'erreur dans la console
- Consultez le fichier `anomalies.csv` pour les détails
- Le rapport `report.md` contient l'analyse complète







