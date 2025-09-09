# 🔧 GUIDE ACTIVATION DONNÉES CME - Sierra Chart

## 🎯 OBJECTIF
Activer les données ES/NQ pour recevoir market data via DTC Protocol

## ✅ PRÉREQUIS
- ✅ Pack 12 Sierra Chart (déjà payé)
- ✅ Compte Sierra Chart actif
- ❌ Données CME (à activer)

---

## 📋 ÉTAPES D'ACTIVATION

### **1️⃣ CONNEXION AU COMPTE SIERRA CHART**

1. **Aller sur** : https://www.sierrachart.com/
2. **Se connecter** à votre compte
3. **Aller dans** : "Account Management" ou "Data Feeds"

### **2️⃣ ACTIVER DENALI DATA FEED**

1. **Rechercher** : "Denali Exchange Data Feed"
2. **Sélectionner** : "CME with Market Depth (Non-Professional)"
3. **Coût** : $13/mois
4. **Confirmer** l'abonnement

### **3️⃣ CONFIGURATION DANS SIERRA CHART**

1. **Ouvrir Sierra Chart**
2. **Global Settings → Data/Trade Service Settings**
3. **Onglet "Data Sources"**
4. **Activer "Denali Exchange Data Feed"**
5. **Sélectionner "CME" dans la liste**
6. **Apply & Save**

### **4️⃣ REDÉMARRER SIERRA CHART**

1. **Fermer complètement** Sierra Chart
2. **Redémarrer** Sierra Chart
3. **Vérifier** que CME apparaît dans "Data Sources"

### **5️⃣ TESTER LA RÉCEPTION**

1. **Créer un nouveau chart** ES ou NQ
2. **Vérifier** que les données arrivent
3. **Tester** les Level 2 (Market Depth)

---

## 🧪 COMMANDES DE TEST

### **Test rapide données CME :**
```bash
python test_dtc_data_reception.py
```

### **Résultat attendu après activation :**
```
📥 Message 1: Type=104 (Market Data)
📥 Message 2: Type=107 (Level 2 Update)  
📥 Message 3: Type=112 (Trade Update)
✅ ES/NQ données reçues !
```

---

## 💰 COÛT TOTAL AVEC DONNÉES

| Abonnement | Coût | Status |
|------------|------|--------|
| Pack 12 Sierra Chart | $164/mois | ✅ Payé |
| Denali CME Market Depth | $13/mois | ❌ À activer |
| CBOE Global Indexes (VIX) | $6/mois | ⚪ Optionnel |
| **TOTAL** | **$177-183/mois** | |

---

## 🔍 VÉRIFICATION POST-ACTIVATION

### **✅ Signes de succès :**
- Sierra Chart affiche données ES/NQ en temps réel
- Test DTC reçoit messages Type 104, 107, 112
- Charts ES/NQ se mettent à jour
- Level 2 DOM fonctionne

### **❌ Si ça ne marche toujours pas :**
1. **Vérifier** facturation Denali activée
2. **Redémarrer** Sierra Chart
3. **Contacter** support Sierra Chart
4. **Vérifier** permissions CME sur le compte

---

## 📞 SUPPORT

### **Sierra Chart Support :**
- **Email** : support@sierrachart.com
- **Sujet** : "Activation Denali CME Data Feed"
- **Mentionner** : Pack 12 déjà payé, besoin CME pour ES/NQ

### **Informations à fournir :**
- Username Sierra Chart
- Numéro compte Pack 12
- Symboles souhaités : ES, NQ
- Utilisation : DTC Protocol trading system

---

## 🎯 APRÈS ACTIVATION

Une fois les données CME activées, vous pourrez :

✅ **Recevoir market data ES/NQ via DTC**  
✅ **Utiliser Level 2 Order Book**  
✅ **Collecter données orderflow réelles**  
✅ **Tester Smart Money avec données live**  
✅ **Intégrer avec MIA_IA_SYSTEM complet**  

---

*Guide créé le : 30 Août 2025*  
*Status : 🎯 Action Required*


