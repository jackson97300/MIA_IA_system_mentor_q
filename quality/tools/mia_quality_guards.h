// ========== GARDE-FOUS QUALITÉ MIA ==========
// Version: 1.0
// Date: 2025-01-05

#ifndef MIA_QUALITY_GUARDS_H
#define MIA_QUALITY_GUARDS_H

#include <string>
#include <vector>
#include <map>

// ========== STRUCTURES DE CONFIGURATION ==========
struct QualityConfig {
  // Prix & normalisation
  double max_price_value = 100000.0;
  double tick_alignment_tolerance = 1e-9;
  double min_price_value = 0.0;
  
  // Volumes
  int min_volume_value = 0;
  int max_volume_value = 10000000;
  
  // Quotes & spread
  int max_spread_ticks = 4;
  double spread_alert_window_seconds = 2.0;
  int bid_ask_tolerance_ticks = 1;
  
  // NBCV
  double total_tolerance_percent = 5.0;
  double delta_tolerance_percent = 5.0;
  
  // VIX
  double vix_min_value = 5.0;
  double vix_max_value = 100.0;
  
  // Volume Profile
  double vp_max_corrections_percent = 2.0;
  double vah_val_tolerance = 0.0;
  
  // Basedata vs Trades
  double volume_tolerance_percent = 10.0;
  int close_tolerance_ticks = 1;
  
  // Séquence & temps
  int max_seq_gap = 1000;
  double gap_alert_window_seconds = 1.0;
  double monotonicity_tolerance_seconds = 0.001;
  
  // Seuils qualité globale
  double quarantine_rate_max = 0.1;
  double tick_alignment_min = 99.9;
  double quote_sanity_min = 99.5;
  double dom_shape_min = 99.5;
  double nbcv_consistency_min = 98.0;
  double vp_corrections_max = 2.0;
  int seq_gaps_max = 0;
  int time_monotonicity_violations_max = 0;
};

// ========== STRUCTURES DE VALIDATION ==========
struct ValidationResult {
  bool is_valid = true;
  std::string error_message;
  std::string quarantine_reason;
  bool requires_correction = false;
  std::string correction_applied;
};

struct QualityMetrics {
  // Compteurs
  int total_messages = 0;
  int quarantined_messages = 0;
  int corrected_messages = 0;
  
  // Taux de qualité
  double tick_alignment_rate = 0.0;
  double quote_sanity_rate = 0.0;
  double dom_shape_rate = 0.0;
  double vwap_bands_integrity_rate = 0.0;
  double nbcv_consistency_rate = 0.0;
  double vp_corrections_rate = 0.0;
  double dup_rate = 0.0;
  double seq_gap_rate = 0.0;
  
  // Violations
  int time_monotonicity_violations = 0;
  int price_anomalies = 0;
  int spread_alerts = 0;
  int vix_alerts = 0;
  int dom_alerts = 0;
  
  // Calculer le score global
  double GetOverallScore() const {
    double score = (tick_alignment_rate + quote_sanity_rate + dom_shape_rate + 
                   vwap_bands_integrity_rate + nbcv_consistency_rate) / 5.0;
    return score;
  }
  
  // Vérifier si on peut aller en production
  bool IsProductionReady(const QualityConfig& config) const {
    return (quarantined_messages / (double)total_messages) <= config.quarantine_rate_max &&
           tick_alignment_rate >= config.tick_alignment_min &&
           quote_sanity_rate >= config.quote_sanity_min &&
           dom_shape_rate >= config.dom_shape_min &&
           nbcv_consistency_rate >= config.nbcv_consistency_min &&
           vp_corrections_rate <= config.vp_corrections_max &&
           time_monotonicity_violations <= config.time_monotonicity_violations_max;
  }
};

// ========== CLASSES DE VALIDATION ==========
class PriceValidator {
public:
  static ValidationResult ValidatePrice(double price, double tick_size, const QualityConfig& config);
  static double NormalizePrice(double price, double tick_size, const QualityConfig& config);
  static bool IsTickAligned(double price, double tick_size, const QualityConfig& config);
};

class VolumeValidator {
public:
  static ValidationResult ValidateVolume(int volume, const QualityConfig& config);
  static ValidationResult ValidateVolume(double volume, const QualityConfig& config);
};

class QuoteValidator {
public:
  static ValidationResult ValidateQuote(double bid, double ask, double tick_size, const QualityConfig& config);
  static ValidationResult ValidateSpread(double spread, double tick_size, const QualityConfig& config);
  static bool IsSpreadReasonable(double spread, double tick_size, const QualityConfig& config);
};

class DOMValidator {
public:
  static ValidationResult ValidateDOMLevel(double bid_price, double ask_price, int level, const QualityConfig& config);
  static ValidationResult ValidateDOMShape(const std::vector<double>& bid_prices, const std::vector<double>& ask_prices, const QualityConfig& config);
};

class VWAPValidator {
public:
  static ValidationResult ValidateVWAPBands(double value, double upper_band_1, double lower_band_1, 
                                          double upper_band_2, double lower_band_2, const QualityConfig& config);
  static bool AreBandsOrdered(double value, double upper_band_1, double lower_band_1, 
                            double upper_band_2, double lower_band_2);
};

class NBCVValidator {
public:
  static ValidationResult ValidateNBCV(int ask, int bid, int delta, int total, const QualityConfig& config);
  static bool IsTotalConsistent(int ask, int bid, int total, const QualityConfig& config);
  static bool IsDeltaConsistent(int ask, int bid, int delta, const QualityConfig& config);
};

class VolumeProfileValidator {
public:
  static ValidationResult ValidateVolumeProfile(double poc, double vah, double val, const QualityConfig& config);
  static ValidationResult CorrectVolumeProfile(double& poc, double& vah, double& val, const QualityConfig& config);
};

class VIXValidator {
public:
  static ValidationResult ValidateVIX(double vix_value, const QualityConfig& config);
};

class TimestampValidator {
public:
  static ValidationResult ValidateTimestamp(double timestamp, double previous_timestamp, const QualityConfig& config);
  static bool IsMonotonic(double timestamp, double previous_timestamp, const QualityConfig& config);
};

class SequenceValidator {
public:
  static ValidationResult ValidateSequence(uint64_t current_seq, uint64_t previous_seq, const QualityConfig& config);
  static bool HasSignificantGap(uint64_t current_seq, uint64_t previous_seq, const QualityConfig& config);
};

// ========== GESTIONNAIRE DE QUALITÉ PRINCIPAL ==========
class QualityManager {
private:
  QualityConfig config_;
  QualityMetrics metrics_;
  std::map<std::string, double> last_timestamps_;
  std::map<std::string, uint64_t> last_sequences_;
  
public:
  QualityManager(const QualityConfig& config) : config_(config) {}
  
  // Validation générale
  ValidationResult ValidateMessage(const std::string& message_type, const std::map<std::string, double>& data);
  
  // Validation spécifique par type
  ValidationResult ValidateBasedata(const std::map<std::string, double>& data);
  ValidationResult ValidateQuote(const std::map<std::string, double>& data);
  ValidationResult ValidateDOM(const std::map<std::string, double>& data);
  ValidationResult ValidateVWAP(const std::map<std::string, double>& data);
  ValidationResult ValidateNBCV(const std::map<std::string, double>& data);
  ValidationResult ValidateVolumeProfile(const std::map<std::string, double>& data);
  ValidationResult ValidateVIX(const std::map<std::string, double>& data);
  ValidationResult ValidateTrade(const std::map<std::string, double>& data);
  
  // Gestion des métriques
  void UpdateMetrics(const ValidationResult& result);
  QualityMetrics GetMetrics() const { return metrics_; }
  void ResetMetrics();
  
  // Configuration
  void UpdateConfig(const QualityConfig& config) { config_ = config; }
  QualityConfig GetConfig() const { return config_; }
  
  // Export des métriques
  std::string ExportMetricsJSON() const;
  void WriteQualitySummary(const std::string& filename) const;
};

#endif // MIA_QUALITY_GUARDS_H
