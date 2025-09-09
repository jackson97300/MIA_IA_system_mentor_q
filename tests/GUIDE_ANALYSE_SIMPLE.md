# 📊 GUIDE ANALYSE MIA_IA_SYSTEM

## 🚀 Utilisation Rapide

### 1. Test Rapide (30 secondes)
```bash
python test_analyse_rapide.py
```
**Objectif** : Vérifier rapidement si le système est actif

### 2. Analyse Complète (2 minutes)
```bash
python analyse_resultats_temps_reel.py
```
**Objectif** : Analyse détaillée pour validation avant 2h

### 3. Analyse Avancée (2 minutes)
```bash
python analyse_resultats_temps_reel_ameliore.py
```
**Objectif** : Analyse avec métriques étendues et score de qualité

## 📊 Ce que les scripts surveillent

### ✅ Métriques Positives
- **Trades** : Exécutions d'ordres détectées
- **Signaux** : Signaux d'entrée/sortie générés
- **Qualité des données** : Score 0-100

### ⚠️ Problèmes Détectés
- **Volumes constants** : Données statiques (ex: 192.0)
- **OHLC incohérents** : Données de prix invalides
- **Problèmes connexion** : Timeouts, déconnexions
- **Problèmes performance** : Latence, lenteurs

## 🎯 Critères de Validation

### ✅ SYSTÈME PARFAIT (Prêt pour 2h)
- Au moins 1 trade détecté
- Au moins 1 signal généré
- Score qualité ≥ 90/100
- Aucun problème critique

### ⚠️ SYSTÈME FONCTIONNEL (Corrections mineures)
- Au moins 1 trade détecté
- Au moins 1 signal généré
- Score qualité ≥ 70/100
- Quelques problèmes mineurs

### ❌ SYSTÈME NON FONCTIONNEL (Diagnostic nécessaire)
- Aucun trade ou signal
- Score qualité < 70/100
- Problèmes critiques détectés

## 🔧 Dépannage

### Aucun fichier de log trouvé
- Vérifier que MIA_IA_SYSTEM est démarré
- Vérifier les permissions des dossiers logs/

### Erreurs de lecture
- Vérifier l'encodage des fichiers
- Vérifier les permissions

### Analyse trop lente
- Réduire l'intervalle de vérification dans le code
- Fermer d'autres applications

## 📞 Support

En cas de problème :
1. Lancer le test rapide d'abord
2. Vérifier que le système est démarré
3. Consulter les logs d'erreur
4. Relancer l'analyse

---

**Note** : Ces scripts sont essentiels pour valider le système avant un test de 2 heures.


