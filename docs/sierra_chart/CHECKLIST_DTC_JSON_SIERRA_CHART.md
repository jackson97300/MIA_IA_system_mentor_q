# ✅ **Checklist Connexion DTC JSON Sierra Chart**

## 🎯 **RÈGLES CRITIQUES POUR CONNEXION RÉUSSIE**

### 1. **Format JSON**

* Utiliser uniquement **JSON standard ou JSON compact** (champs `"F": [...]`).
* Le champ **`"Type"` doit être le premier** du message.
* Encodage : **UTF-8 (8-bit)** → pas d'Unicode spécial ni d'accents.

---

### 2. **Structure des messages**

* Chaque message doit contenir les champs DTC valides (ex. `Type`, `ProtocolVersion`, `Username`, `Password`, …).
* Le serveur attend strictement la structure définie dans la doc DTC.

---

### 3. **Délimitation des messages**

* Chaque message JSON doit se terminer par **un caractère NULL (`\x00`)**.
* Le serveur **lit jusqu'au `\x00`** et considère que le message est complet.
* ⚠️ **Sans `\x00`, Sierra ignore le message** → erreur "Missing 'Type' field".

---

### 4. **Connexion**

* **TCP classique (port 11099/11100)** :
  * Envoyer **LOGON_REQUEST + `\x00`** immédiatement après connexion.
  * Si besoin, envoyer **ENCODING_REQUEST + `\x00`** pour forcer JSON compact.

* **WebSocket** :
  * Sierra passe automatiquement en **JSON compact**.
  * Pas besoin d'envoyer ENCODING_REQUEST manuellement.
  * Toujours terminer les messages avec `\x00`.

---

### 5. **Réception**

* Sierra envoie des messages JSON compact avec `"Type": ...` suivi d'un `\x00`.
* Tu dois parser chaque bloc jusqu'au `\x00`.
* Les **HEARTBEAT** (`{"Type":3,...}`) sont normaux → signe que la connexion vit.

---

### 6. **Signes d'erreur fréquents**

* `Missing 'Type' field` → message envoyé sans `\x00`.
* `Timeout LOGON_RESPONSE` → le serveur n'a pas validé ton LOGON (souvent à cause du manque de `\x00`).
* Déconnexion après 2–5s → Sierra n'a pas reçu de message logon valide.

---

## 🚨 **RÈGLE D'OR**

👉 **Toujours ajouter `\x00` à la fin de chaque message envoyé et vérifier que "Type" est le premier champ.**

---

## 📋 **Messages Types DTC**

### ENCODING_REQUEST (Type 0)
```json
{"Type":0,"F":[8,2]}
```

### LOGON_REQUEST (Type 1)
```json
{"Type":1,"F":[8,"username","password",20,"ClientName",0]}
```

### HEARTBEAT (Type 3)
```json
{"Type":3,"F":[session_id]}
```

### LOGON_RESPONSE (Type 2)
```json
{"Type":2,"F":[session_id,result_code]}
```

---

## 🔍 **Vérifications Rapides**

### ✅ Connexion réussie
- Connexion TCP établie
- LOGON_REQUEST envoyé avec `\x00`
- LOGON_RESPONSE reçu
- HEARTBEAT reçus régulièrement

### ❌ Problèmes courants
- "Missing 'Type' field" → Ajouter `\x00`
- Timeout LOGON_RESPONSE → Vérifier format JSON
- Déconnexion rapide → Heartbeat manquant

---

## 📚 **Ressources**

- **Documentation complète** : `SIERRA_CHART_DTC_SUCCESS.md`
- **Client fonctionnel** : `dtc_client_victoire_final.py`
- **Tests** : `test_sierra_connector_real.py`

---

**💡 Cette checklist doit être consultée AVANT chaque test de connexion DTC !**


