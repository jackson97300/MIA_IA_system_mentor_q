# 🛡️ Guide d'Intégration des Garde-fous MIA

## **📋 Vue d'ensemble**

Ce guide détaille comment intégrer les garde-fous de qualité dans le collecteur C++ et le pipeline MIA pour assurer la fiabilité des données.

## **🎯 Architecture des Garde-fous**

### **Niveau 1 : Validation en temps réel (C++ collecteur)**
- **Prix & normalisation** : Validation immédiate avant écriture
- **Quotes & spread** : Vérification bid < ask, spread raisonnable
- **VIX** : Plage de valeurs réalistes
- **Corrections VP** : Application automatique avec logging

### **Niveau 2 : Validation post-process (Python)**
- **Cohérences inter-flux** : Quotes vs DOM, Trades vs Quotes
- **Déduplication** : Détection et suppression des doublons
- **Métriques de qualité** : Calcul des taux de qualité
- **Alertes** : Notification des anomalies

### **Niveau 3 : Monitoring & alerting**
- **Résumés quotidiens** : KPIs de qualité
- **Alertes temps réel** : Seuils critiques dépassés
- **Mode dégradé** : Désactivation sélective des flux

## **🔧 Intégration dans le Collecteur C++**

### **1) Ajout des validations critiques**

```cpp
// Dans MIA_Chart_Dumper_patched.cpp
#include "mia_quality_guards.h"

// Initialisation du gestionnaire de qualité
static QualityManager quality_manager(QualityConfig::LoadFromFile("mia_quality_config.yml"));

// Validation avant écriture
static bool ValidateAndWrite(const SCString& line, DataType dataType) {
  // Parser le JSON pour validation
  auto data = ParseJSONData(line);
  
  // Validation selon le type
  ValidationResult result;
  switch (dataType) {
    case BASEDATA:
      result = quality_manager.ValidateBasedata(data);
      break;
    case QUOTE:
      result = quality_manager.ValidateQuote(data);
      break;
    case DOM:
      result = quality_manager.ValidateDOM(data);
      break;
    case VWAP:
      result = quality_manager.ValidateVWAP(data);
      break;
    case NBCV_GRAPH3:
    case NBCV_GRAPH4:
      result = quality_manager.ValidateNBCV(data);
      break;
    case VOLUME_PROFILE:
      result = quality_manager.ValidateVolumeProfile(data);
      break;
    case VIX:
      result = quality_manager.ValidateVIX(data);
      break;
    case TRADE:
      result = quality_manager.ValidateTrade(data);
      break;
  }
  
  // Mise à jour des métriques
  quality_manager.UpdateMetrics(result);
  
  // Décision d'écriture
  if (result.is_valid) {
    WritePerChartDaily(sc.ChartNumber, line, dataType);
    return true;
  } else if (result.requires_correction) {
    // Appliquer correction et réécrire
    SCString corrected_line = ApplyCorrection(line, result.correction_applied);
    WritePerChartDaily(sc.ChartNumber, corrected_line, dataType);
    return true;
  } else {
    // Mettre en quarantaine
    WriteToQuarantine(line, result.quarantine_reason);
    return false;
  }
}
```

### **2) Validation des prix (exemple)**

```cpp
// Validation prix avec normalisation
static double ValidateAndNormalizePrice(double raw_price, double tick_size) {
  // Vérification basique
  if (raw_price != raw_price || raw_price <= 0.0) {
    qa_counters.price_anomalies++;
    return NAN;
  }
  
  // Normalisation
  double normalized = NormalizePx(sc, raw_price);
  
  // Vérification alignement tick
  if (!PriceValidator::IsTickAligned(normalized, tick_size, config)) {
    qa_counters.tick_alignment_violations++;
    return NAN;
  }
  
  return normalized;
}
```

### **3) Validation des quotes (exemple)**

```cpp
// Validation quotes avec vérifications
static bool ValidateQuote(double bid, double ask, double tick_size) {
  // Vérification bid < ask
  if (bid >= ask) {
    qa_counters.quote_sanity_violations++;
    return false;
  }
  
  // Vérification spread
  double spread = ask - bid;
  if (spread > 4.0 * tick_size) {
    qa_counters.spread_alerts++;
    return false;
  }
  
  return true;
}
```

## **🐍 Intégration Post-Process (Python)**

### **1) Script de validation post-process**

```python
# mia_quality_validator.py
import json
import pandas as pd
from datetime import datetime
from typing import Dict, List, Tuple

class MIAQualityValidator:
    def __init__(self, config_file: str = "mia_quality_config.yml"):
        self.config = self.load_config(config_file)
        self.metrics = QualityMetrics()
        
    def validate_file(self, input_file: str) -> Tuple[str, str]:
        """
        Valide un fichier JSONL et produit:
        - Fichier validé (mia_unified_YYYYMMDD.jsonl)
        - Fichier quarantaine (mia_quarantine_YYYYMMDD.jsonl)
        """
        valid_lines = []
        quarantine_lines = []
        
        with open(input_file, 'r') as f:
            for line_num, line in enumerate(f, 1):
                try:
                    data = json.loads(line.strip())
                    result = self.validate_message(data)
                    
                    if result['is_valid']:
                        valid_lines.append(line)
                    else:
                        quarantine_lines.append({
                            'line_number': line_num,
                            'data': data,
                            'reason': result['reason']
                        })
                        
                except json.JSONDecodeError:
                    quarantine_lines.append({
                        'line_number': line_num,
                        'data': line.strip(),
                        'reason': 'invalid_json'
                    })
        
        # Écrire les fichiers
        valid_file = self.write_valid_file(valid_lines)
        quarantine_file = self.write_quarantine_file(quarantine_lines)
        
        return valid_file, quarantine_file
    
    def validate_message(self, data: Dict) -> Dict:
        """Valide un message selon son type"""
        msg_type = data.get('type', 'unknown')
        
        if msg_type == 'basedata':
            return self.validate_basedata(data)
        elif msg_type == 'quote':
            return self.validate_quote(data)
        elif msg_type == 'depth':
            return self.validate_dom(data)
        elif msg_type in ['vwap', 'vwap_current', 'vwap_previous']:
            return self.validate_vwap(data)
        elif msg_type.startswith('numbers_bars_calculated_values'):
            return self.validate_nbcv(data)
        elif msg_type == 'volume_profile':
            return self.validate_volume_profile(data)
        elif msg_type == 'vix':
            return self.validate_vix(data)
        elif msg_type == 'trade':
            return self.validate_trade(data)
        else:
            return {'is_valid': False, 'reason': f'unknown_type_{msg_type}'}
    
    def validate_basedata(self, data: Dict) -> Dict:
        """Valide les données basedata"""
        issues = []
        
        # Vérification prix
        for price_field in ['o', 'h', 'l', 'c']:
            if price_field in data:
                price = data[price_field]
                if not self.is_price_valid(price):
                    issues.append(f'invalid_price_{price_field}')
        
        # Vérification volume
        if 'v' in data:
            volume = data['v']
            if not self.is_volume_valid(volume):
                issues.append('invalid_volume')
        
        return {
            'is_valid': len(issues) == 0,
            'reason': ';'.join(issues) if issues else 'valid'
        }
    
    def validate_quote(self, data: Dict) -> Dict:
        """Valide les quotes"""
        issues = []
        
        bid = data.get('bid', 0)
        ask = data.get('ask', 0)
        
        # Vérification bid < ask
        if bid >= ask:
            issues.append('bid_ge_ask')
        
        # Vérification spread
        spread = ask - bid
        max_spread = self.config['quotes']['max_spread_ticks'] * self.config['markets']['ES']['tick_size']
        if spread > max_spread:
            issues.append('spread_too_wide')
        
        return {
            'is_valid': len(issues) == 0,
            'reason': ';'.join(issues) if issues else 'valid'
        }
    
    def validate_dom(self, data: Dict) -> Dict:
        """Valide le DOM"""
        issues = []
        
        # Vérification prix
        price = data.get('price', 0)
        if not self.is_price_valid(price):
            issues.append('invalid_price')
        
        # Vérification taille
        size = data.get('size', 0)
        if not self.is_volume_valid(size):
            issues.append('invalid_size')
        
        return {
            'is_valid': len(issues) == 0,
            'reason': ';'.join(issues) if issues else 'valid'
        }
    
    def validate_vwap(self, data: Dict) -> Dict:
        """Valide les VWAP et bandes"""
        issues = []
        
        # Vérification valeur VWAP
        value = data.get('value', data.get('vwap', 0))
        if not self.is_price_valid(value):
            issues.append('invalid_vwap_value')
        
        # Vérification bandes
        if 'upper_band_1' in data and 'lower_band_1' in data:
            upper_1 = data['upper_band_1']
            lower_1 = data['lower_band_1']
            
            if upper_1 <= value or lower_1 >= value:
                issues.append('invalid_band_1')
            
            if upper_1 <= lower_1:
                issues.append('bands_inverted')
        
        return {
            'is_valid': len(issues) == 0,
            'reason': ';'.join(issues) if issues else 'valid'
        }
    
    def validate_nbcv(self, data: Dict) -> Dict:
        """Valide les NBCV"""
        issues = []
        
        ask = data.get('ask', 0)
        bid = data.get('bid', 0)
        total = data.get('total', 0)
        delta = data.get('delta', 0)
        
        # Vérification cohérence total
        if total > 0:
            expected_total = ask + bid
            tolerance = self.config['nbcv']['total_tolerance_percent'] / 100.0
            if abs(total - expected_total) / total > tolerance:
                issues.append('total_inconsistent')
        
        # Vérification cohérence delta
        if delta != 0:
            expected_delta = ask - bid
            tolerance = self.config['nbcv']['delta_tolerance_percent'] / 100.0
            if abs(delta - expected_delta) / abs(delta) > tolerance:
                issues.append('delta_inconsistent')
        
        return {
            'is_valid': len(issues) == 0,
            'reason': ';'.join(issues) if issues else 'valid'
        }
    
    def validate_volume_profile(self, data: Dict) -> Dict:
        """Valide le Volume Profile"""
        issues = []
        
        poc = data.get('poc', 0)
        vah = data.get('vah', 0)
        val = data.get('val', data.get('pval', 0))
        
        # Vérification VAH >= VAL
        if vah < val:
            issues.append('vah_lt_val')
        
        # Vérification POC dans [VAL, VAH]
        if poc < val or poc > vah:
            issues.append('poc_outside_range')
        
        return {
            'is_valid': len(issues) == 0,
            'reason': ';'.join(issues) if issues else 'valid'
        }
    
    def validate_vix(self, data: Dict) -> Dict:
        """Valide le VIX"""
        issues = []
        
        vix_value = data.get('last', 0)
        min_vix = self.config['vix']['min_value']
        max_vix = self.config['vix']['max_value']
        
        if vix_value < min_vix or vix_value > max_vix:
            issues.append('vix_out_of_range')
        
        return {
            'is_valid': len(issues) == 0,
            'reason': ';'.join(issues) if issues else 'valid'
        }
    
    def validate_trade(self, data: Dict) -> Dict:
        """Valide les trades"""
        issues = []
        
        # Vérification prix
        price = data.get('px', 0)
        if not self.is_price_valid(price):
            issues.append('invalid_price')
        
        # Vérification volume
        volume = data.get('vol', data.get('qty', 0))
        if not self.is_volume_valid(volume):
            issues.append('invalid_volume')
        
        return {
            'is_valid': len(issues) == 0,
            'reason': ';'.join(issues) if issues else 'valid'
        }
    
    def is_price_valid(self, price: float) -> bool:
        """Vérifie si un prix est valide"""
        if price != price or price <= 0:  # NaN ou négatif
            return False
        
        # Vérification alignement tick
        tick_size = self.config['markets']['ES']['tick_size']
        remainder = price % tick_size
        if remainder > 1e-9:
            return False
        
        return True
    
    def is_volume_valid(self, volume: int) -> bool:
        """Vérifie si un volume est valide"""
        return isinstance(volume, int) and volume >= 0
    
    def write_valid_file(self, valid_lines: List[str]) -> str:
        """Écrit le fichier validé"""
        date_str = datetime.now().strftime("%Y%m%d")
        filename = f"mia_unified_{date_str}.jsonl"
        
        with open(filename, 'w') as f:
            for line in valid_lines:
                f.write(line)
        
        return filename
    
    def write_quarantine_file(self, quarantine_lines: List[Dict]) -> str:
        """Écrit le fichier de quarantaine"""
        date_str = datetime.now().strftime("%Y%m%d")
        filename = f"mia_quarantine_{date_str}.jsonl"
        
        with open(filename, 'w') as f:
            for item in quarantine_lines:
                f.write(json.dumps(item) + '\n')
        
        return filename
    
    def generate_quality_report(self) -> Dict:
        """Génère un rapport de qualité"""
        return {
            'date': datetime.now().isoformat(),
            'total_messages': self.metrics.total_messages,
            'quarantined_messages': self.metrics.quarantined_messages,
            'quarantine_rate': self.metrics.quarantined_messages / max(1, self.metrics.total_messages),
            'quality_score': self.metrics.GetOverallScore(),
            'is_production_ready': self.metrics.IsProductionReady(self.config)
        }

# Utilisation
if __name__ == "__main__":
    validator = MIAQualityValidator()
    valid_file, quarantine_file = validator.validate_file("chart_3_20250105.jsonl")
    
    print(f"Fichier validé: {valid_file}")
    print(f"Fichier quarantaine: {quarantine_file}")
    
    report = validator.generate_quality_report()
    print(f"Rapport qualité: {report}")
```

## **📊 Monitoring & Alertes**

### **1) Script de monitoring temps réel**

```python
# mia_quality_monitor.py
import time
import json
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class MIAQualityMonitor(FileSystemEventHandler):
    def __init__(self, config_file: str = "mia_quality_config.yml"):
        self.config = self.load_config(config_file)
        self.alert_thresholds = self.config['quality_thresholds']
        self.last_metrics = {}
        
    def on_modified(self, event):
        if event.is_file and event.src_path.endswith('.jsonl'):
            self.check_quality_metrics(event.src_path)
    
    def check_quality_metrics(self, file_path: str):
        """Vérifie les métriques de qualité en temps réel"""
        metrics = self.calculate_metrics(file_path)
        
        # Vérification des seuils critiques
        alerts = []
        
        if metrics['quarantine_rate'] > self.alert_thresholds['quarantine_rate_max']:
            alerts.append(f"Quarantine rate too high: {metrics['quarantine_rate']:.2%}")
        
        if metrics['tick_alignment_rate'] < self.alert_thresholds['tick_alignment_min']:
            alerts.append(f"Tick alignment rate too low: {metrics['tick_alignment_rate']:.2%}")
        
        if metrics['quote_sanity_rate'] < self.alert_thresholds['quote_sanity_min']:
            alerts.append(f"Quote sanity rate too low: {metrics['quote_sanity_rate']:.2%}")
        
        if alerts:
            self.send_alert(alerts, metrics)
    
    def send_alert(self, alerts: List[str], metrics: Dict):
        """Envoie une alerte"""
        alert_data = {
            'timestamp': datetime.now().isoformat(),
            'alerts': alerts,
            'metrics': metrics,
            'severity': 'HIGH' if len(alerts) > 2 else 'MEDIUM'
        }
        
        # Log l'alerte
        with open('mia_quality_alerts.jsonl', 'a') as f:
            f.write(json.dumps(alert_data) + '\n')
        
        # Optionnel: envoi email/Slack
        print(f"ALERT: {alerts}")

# Utilisation
if __name__ == "__main__":
    monitor = MIAQualityMonitor()
    observer = Observer()
    observer.schedule(monitor, path=".", recursive=False)
    observer.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
```

## **🚀 Déploiement & Tests**

### **1) Checklist de déploiement**

```bash
# 1. Compilation du collecteur avec garde-fous
g++ -o MIA_Chart_Dumper_patched.exe MIA_Chart_Dumper_patched.cpp mia_quality_guards.cpp

# 2. Test des garde-fous
python mia_quality_validator.py --test-mode

# 3. Vérification des seuils
python mia_quality_monitor.py --check-thresholds

# 4. Test de charge
python mia_quality_validator.py --stress-test --duration 3600

# 5. Validation finale
python mia_quality_validator.py --validate-all --output-report
```

### **2) Tests d'acceptation**

```python
# mia_quality_tests.py
import unittest
from mia_quality_validator import MIAQualityValidator

class TestMIAQuality(unittest.TestCase):
    def setUp(self):
        self.validator = MIAQualityValidator()
    
    def test_price_validation(self):
        # Test prix valides
        self.assertTrue(self.validator.is_price_valid(6534.25))
        self.assertTrue(self.validator.is_price_valid(6534.50))
        
        # Test prix invalides
        self.assertFalse(self.validator.is_price_valid(6534.13))  # Pas aligné tick
        self.assertFalse(self.validator.is_price_valid(-100.0))   # Négatif
        self.assertFalse(self.validator.is_price_valid(float('nan')))  # NaN
    
    def test_quote_validation(self):
        # Test quotes valides
        valid_quote = {'bid': 6534.25, 'ask': 6534.50}
        result = self.validator.validate_quote(valid_quote)
        self.assertTrue(result['is_valid'])
        
        # Test quotes invalides
        invalid_quote = {'bid': 6534.50, 'ask': 6534.25}  # bid >= ask
        result = self.validator.validate_quote(invalid_quote)
        self.assertFalse(result['is_valid'])
        self.assertIn('bid_ge_ask', result['reason'])
    
    def test_vwap_validation(self):
        # Test VWAP valide
        valid_vwap = {
            'value': 6534.25,
            'upper_band_1': 6536.25,
            'lower_band_1': 6532.25
        }
        result = self.validator.validate_vwap(valid_vwap)
        self.assertTrue(result['is_valid'])
        
        # Test VWAP invalide
        invalid_vwap = {
            'value': 6534.25,
            'upper_band_1': 6532.25,  # Bande inversée
            'lower_band_1': 6536.25
        }
        result = self.validator.validate_vwap(invalid_vwap)
        self.assertFalse(result['is_valid'])
        self.assertIn('bands_inverted', result['reason'])

if __name__ == '__main__':
    unittest.main()
```

## **📈 Métriques & KPIs**

### **1) Tableau de bord qualité**

```python
# mia_quality_dashboard.py
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

def create_quality_dashboard():
    st.title("🛡️ MIA Quality Dashboard")
    
    # Charger les métriques
    metrics = load_quality_metrics()
    
    # Métriques principales
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Quarantine Rate", f"{metrics['quarantine_rate']:.2%}")
    
    with col2:
        st.metric("Tick Alignment", f"{metrics['tick_alignment_rate']:.2%}")
    
    with col3:
        st.metric("Quote Sanity", f"{metrics['quote_sanity_rate']:.2%}")
    
    with col4:
        st.metric("Overall Score", f"{metrics['overall_score']:.1f}")
    
    # Graphiques
    st.subheader("📊 Quality Trends")
    
    # Tendance quarantaine
    fig_quarantine = px.line(metrics['quarantine_trend'], 
                            x='timestamp', y='quarantine_rate',
                            title='Quarantine Rate Over Time')
    st.plotly_chart(fig_quarantine)
    
    # Répartition des erreurs
    fig_errors = px.pie(metrics['error_distribution'], 
                       values='count', names='error_type',
                       title='Error Distribution')
    st.plotly_chart(fig_errors)
    
    # Alertes
    st.subheader("🚨 Active Alerts")
    for alert in metrics['active_alerts']:
        st.error(f"{alert['timestamp']}: {alert['message']}")

if __name__ == "__main__":
    create_quality_dashboard()
```

## **🎯 Prochaines Étapes**

1. **Implémentation des garde-fous C++** dans le collecteur
2. **Développement du validateur Python** post-process
3. **Configuration des seuils** par marché (ES/NQ/VIX)
4. **Tests d'acceptation** et validation
5. **Déploiement en production** avec monitoring
6. **Formation des équipes** sur les alertes et procédures

## **📞 Support & Maintenance**

- **Documentation** : Mise à jour des seuils et procédures
- **Formation** : Équipes sur les alertes et interventions
- **Monitoring** : Surveillance 24/7 des métriques critiques
- **Évolution** : Adaptation des seuils selon l'expérience terrain
