// === MIA_Dumper_G8_VIX.cpp (header inlined - Approach 1) ===
// Utilities previously in "mia_dump_utils.hpp" are embedded below to allow
// single-file remote builds on Sierra Chart.

#include "sierrachart.h"
#ifdef _WIN32
  #include <windows.h>
#endif
#include <time.h>
#include <cmath>
#include <unordered_map>
#include <string>
#include <vector>
using std::fabs;

// ========== UTILITAIRES COMMUNS ==========

// Création du répertoire de sortie
static void EnsureOutDir(const char* baseDir = "D:\\MIA_IA_system") {
#ifdef _WIN32
  CreateDirectoryA(baseDir, NULL);
#endif
}

// Génération du nom de fichier quotidien par chart et type
static SCString DailyFilenameForChartType(int chartNumber, const char* dataType, const char* baseDir = "D:\\MIA_IA_system") {
  time_t now = time(NULL);
  struct tm* lt = localtime(&now);
  int y = lt ? (lt->tm_year + 1900) : 1970;
  int m = lt ? (lt->tm_mon + 1) : 1;
  int d = lt ? lt->tm_mday : 1;
  SCString filename;
  filename.Format("%s\\chart_%d_%s_%04d%02d%02d.jsonl", 
                  baseDir, chartNumber, dataType, y, m, d);
  return filename;
}

// Écriture dans le fichier spécialisé avec déduplication
static void WriteToSpecializedFile(int chartNumber, const char* dataType, const SCString& line, const char* baseDir = "D:\\MIA_IA_system") {
  EnsureOutDir(baseDir);
  const SCString filename = DailyFilenameForChartType(chartNumber, dataType, baseDir);
  
  // Déduplication par fichier - vérifier si la ligne existe déjà
  static std::unordered_map<std::string, std::string> s_last_line_by_file;
  std::string fileKey = std::string(filename.GetChars());
  std::string currentLine = std::string(line.GetChars());
  
  // Si la ligne est identique à la dernière écrite, ne pas écrire
  auto it = s_last_line_by_file.find(fileKey);
  if (it != s_last_line_by_file.end() && it->second == currentLine) {
    return; // Ligne identique, ne pas écrire
  }
  
  // Écrire la ligne
  FILE* f = fopen(filename.GetChars(), "a");
  if (f) { 
    fprintf(f, "%s\n", line.GetChars()); 
    fclose(f);
    
    // Mettre à jour le cache
    s_last_line_by_file[fileKey] = currentLine;
  }
}

// ========== SYSTÈME DE DEBUG ==========
enum LogLevel { LOG_ERROR = 0, LOG_KEY = 1, LOG_VERBOSE = 2 };

static void DebugLog(SCStudyInterfaceRef& sc, const char* message) {
  sc.AddMessageToLog(message, 1);
}

static inline bool ShouldLog(const SCStudyInterfaceRef& sc, int level) {
  return sc.Input[2].GetInt() >= level;
}

// ========== DÉDUPLICATION INTELLIGENTE AMÉLIORÉE ==========
// Structure pour la déduplication par (sym, t, i)
struct LastKey { 
  double t = 0.0; // timestamp
  double i = -1;  // bar index
};

// Structures pour la détection de changement d'état
struct LastVIX {
  double open=0, high=0, low=0, close=0, volume=0;
};

// Structure améliorée pour VIX
struct LastVIXEnhanced {
  double open=0, high=0, low=0, close=0, volume=0;
  int bar_count = 0;
  double last_timestamp = 0.0;
};

// Maps de déduplication par symbole
static std::unordered_map<std::string, LastKey> g_LastKeyBySym;
static std::unordered_map<std::string, LastVIX> g_LastVIXBySym;
static std::unordered_map<std::string, LastVIXEnhanced> g_LastVIXEnhancedBySym;

// ========== DÉTECTION DE CHANGEMENT ==========
static inline bool has_changed(double a, double b, double eps=1e-9) {
  return fabs(a-b) > eps;
}

// Fonction de déduplication améliorée
static bool ShouldWriteData(const SCStudyInterfaceRef& sc, const char* symbol, double timestamp, double barIndex) {
  std::string symKey = std::string(symbol) + "|" + std::to_string(sc.ChartNumber);
  LastKey& lk = g_LastKeyBySym[symKey];
  
  // Vérifier si (sym, t, i) identique
  bool same_ti = (fabs(lk.t - timestamp) < 1e-9) && (fabs(lk.i - barIndex) < 1e-9);
  
  // Mettre à jour la clé
  lk.t = timestamp;
  lk.i = barIndex;
  
  return !same_ti; // Écrire si différent
}

// Fonction de déduplication ULTRA-STRICTE pour VIX
static bool ShouldWriteVIXData(const SCStudyInterfaceRef& sc, const char* symbol, double timestamp, double barIndex, 
                              double close, int barCount) {
  // Variables statiques GLOBALES (pas par symbole)
  static double s_last_timestamp = 0.0;
  static double s_last_close = 0.0;
  static int s_last_bar_count = -1;
  static int s_write_count = 0;
  
  // Vérifications ULTRA-STRICTES
  bool same_timestamp = (fabs(s_last_timestamp - timestamp) < 1e-9);
  bool same_close_value = (fabs(s_last_close - close) < 0.0001); // Tolérance ultra-stricte
  bool same_bar_count = (s_last_bar_count == barCount);
  
  // Si TOUT est identique, ne pas écrire
  if (same_timestamp && same_close_value && same_bar_count) {
    return false;
  }
  
  // Mettre à jour les valeurs
  s_last_timestamp = timestamp;
  s_last_close = close;
  s_last_bar_count = barCount;
  s_write_count++;
  
  return true; // Écrire si quelque chose a changé
}

// ========== VALIDATION DES DONNÉES ==========
static bool ValidateVIXData(double open, double high, double low, double close, double volume) {
  // Vérifier les valeurs de base
  if (open <= 0 || open > 100) return false;
  if (high <= 0 || high > 100) return false;
  if (low <= 0 || low > 100) return false;
  if (close <= 0 || close > 100) return false;
  if (volume < 0) return false;
  
  // Vérifier cohérence OHLC
  if (high < low) return false;
  if (high < open || high < close) return false;
  if (low > open || low > close) return false;
  
  // Vérifier que les valeurs sont finies
  if (!std::isfinite(open) || !std::isfinite(high) || !std::isfinite(low) || 
      !std::isfinite(close) || !std::isfinite(volume)) {
    return false;
  }
  
  return true;
}

// ========== MÉTRIQUES DE PERFORMANCE ==========
struct VIXMetrics {
  int total_bars_processed = 0;
  int vix_written = 0;
  int vix_close_written = 0;
  int invalid_values = 0;
  time_t last_update = 0;
};

static VIXMetrics g_vix_metrics;

// Fonction de mise à jour des métriques
static void UpdateVIXMetrics(const char* operation) {
  g_vix_metrics.total_bars_processed++;
  g_vix_metrics.last_update = time(NULL);
  
  if (strcmp(operation, "vix") == 0) g_vix_metrics.vix_written++;
  else if (strcmp(operation, "vix_close") == 0) g_vix_metrics.vix_close_written++;
  else if (strcmp(operation, "invalid") == 0) g_vix_metrics.invalid_values++;
}

// Rapport de performance (toutes les 5 minutes)
static void CheckVIXPerformance(SCStudyInterfaceRef& sc) {
  time_t now = time(NULL);
  if (ShouldLog(sc, LOG_KEY) && (now - g_vix_metrics.last_update > 300)) {
    SCString perfMsg;
    perfMsg.Format("PERF G8: Bars=%d, VIX=%d, VIX_Close=%d, Invalid=%d", 
                   g_vix_metrics.total_bars_processed,
                   g_vix_metrics.vix_written,
                   g_vix_metrics.vix_close_written,
                   g_vix_metrics.invalid_values);
    DebugLog(sc, perfMsg.GetChars());
  }
}

// Anti-duplication simple par (chart, type, key) - KEPT FOR COMPATIBILITY
static void WriteIfChanged(int chartNumber, const char* dataType, const std::string& key, const SCString& line) {
  static std::unordered_map<std::string, std::string> s_last_by_key;
  auto it = s_last_by_key.find(key);
  const std::string current = std::string(line.GetChars());
  if (it != s_last_by_key.end() && it->second == current) {
    return; // identique, on n'écrit pas
  }
  WriteToSpecializedFile(chartNumber, dataType, line);
  s_last_by_key[key] = current;
}

// ========== NORMALISATION DES PRIX ==========
inline double NormalizePx(const SCStudyInterfaceRef& sc, double raw)
{
  // 1) Dé-multiplier si besoin
  const double mult = (sc.RealTimePriceMultiplier != 0.0 ? sc.RealTimePriceMultiplier : 1.0);
  double px = raw / mult;

  // 2) Correction d'échelle avant arrondi (certains flux arrivent x100)
  if (px > 10000.0) {
    px /= 100.0;
    // Note: Debug logging supprimé car NormalizePx est appelé hors scope des fonctions de debug
  }

  // 3) Arrondi au tick
  px = sc.RoundToTickSize(px, sc.TickSize);

  // 4) Correction d'échelle résiduelle puis arrondi final (sécurité)
  if (px > 10000.0) {
    px /= 100.0;
    // Note: Debug logging supprimé car NormalizePx est appelé hors scope des fonctions de debug
  }
  px = sc.RoundToTickSize(px, sc.TickSize);
  return px;
}

// ========== HELPERS D'ACCÈS AUX STUDIES ==========

// Helper pour résoudre automatiquement un Study ID par nom
static int ResolveStudyID(SCStudyInterfaceRef& sc, int chartNumber, const char* studyName, int fallbackID = 0) {
  int id = sc.GetStudyIDByName(chartNumber, studyName, 0);
  if (id <= 0 && fallbackID > 0) {
    id = fallbackID;
  }
  return id;
}

// Helper pour lire un subgraph avec validation
static bool ReadSubgraph(SCStudyInterfaceRef& sc, int studyID, int subgraphIndex, SCFloatArray& array, int chartNumber = -1) {
  if (chartNumber > 0) {
    sc.GetStudyArrayFromChartUsingID(chartNumber, studyID, subgraphIndex, array);
    return array.GetArraySize() > 0;
  } else {
    sc.GetStudyArrayUsingID(studyID, subgraphIndex, array);
    return array.GetArraySize() > 0;
  }
}

// Helper pour valider qu'une étude a des données valides
static bool ValidateStudyData(const SCFloatArray& array, int index) {
  return array.GetArraySize() > index && !std::isnan(array[index]) && !std::isinf(array[index]);
}

// ========== DÉTECTION DE SUPPORT SEQUENCE ==========
static void DetectSequenceSupport(const c_SCTimeAndSalesArray& TnS, bool& g_UseSeq)
{
    // Cherche un enregistrement avec Sequence > 0 (du plus récent au plus ancien)
    for (int i = (int)TnS.Size() - 1; i >= 0 && i >= (int)TnS.Size() - 50; --i)
    {
        if (TnS[i].Sequence > 0)
        {
            g_UseSeq = true;
            break;
        }
    }
}

// ========== CONSTANTES DE MAPPING ==========

// VWAP Subgraphs (selon le mapping standard)
#define VWAP_SG_MAIN 1
#define VWAP_SG_UP1  2
#define VWAP_SG_DN1  3
#define VWAP_SG_UP2  4
#define VWAP_SG_DN2  5
#define VWAP_SG_UP3  6
#define VWAP_SG_DN3  7

// VVA Subgraphs (Volume Value Area) — indexation 0-based
#define VVA_SG_POC 0
#define VVA_SG_VAH 1
#define VVA_SG_VAL 2

// NBCV Subgraphs (Numbers Bars Calculated Values) — mapping confirmé
// (Ask=5, Bid=6, Delta=0, Trades=11, CumDelta=9, TotalVol=12, Delta%=10, Ask%=16, Bid%=17)
#define NBCV_SG_DELTA         0
#define NBCV_SG_ASK_VOLUME    5
#define NBCV_SG_BID_VOLUME    6
#define NBCV_SG_TRADES        11
#define NBCV_SG_CUMULATIVE     9
#define NBCV_SG_TOTAL_VOLUME  12
#define NBCV_SG_DELTA_PCT     10
#define NBCV_SG_ASK_PCT       16
#define NBCV_SG_BID_PCT       17

// VIX Subgraph
#define VIX_SG_LAST 4

// MenthorQ Subgraphs
#define MENTHORQ_GAMMA_SG_COUNT 19
#define MENTHORQ_BLIND_SG_COUNT 9
#define MENTHORQ_SWING_SG_COUNT 9

// =======================================================================
// ===============    STUDY ENTRYPOINT (G8 VIX)    =======================
// =======================================================================

SCDLLName("MIA_Dumper_G8_VIX")

// Dumper spécialisé pour Chart 8 (VIX)
// Lit directement le Close du chart VIX
// Sortie : chart_8_vix_YYYYMMDD.jsonl

SCSFExport scsf_MIA_Dumper_G8_VIX(SCStudyInterfaceRef sc)
{
  if (sc.SetDefaults)
  {
    sc.GraphName = "MIA Dumper G8 VIX";
    sc.StudyDescription = "Collecte spécialisée Chart 8 - VIX OHLC";
    sc.AutoLoop = 1;
    sc.UpdateAlways = 0;
    sc.CalculationPrecedence = LOW_PREC_LEVEL;

    // --- Inputs VIX ---
    sc.Input[0].Name = "Export VIX (0/1)";
    sc.Input[0].SetInt(1);
    sc.Input[1].Name = "Export OHLC (0/1)";
    sc.Input[1].SetInt(0); // 0 = Close seulement, 1 = OHLC complet
    
    // --- Input Debug ---
    sc.Input[2].Name = "Debug Log Level (0=Off,1=Key,2=Verbose)";
    sc.Input[2].SetInt(0); // Production = Off
    
    // --- Inputs PRO ---
    sc.Input[3].Name = "On New Bar Only (0/1)";
    sc.Input[3].SetInt(1); // 1 = 1 ligne/barre, 0 = intrabar OK
    
    sc.Input[4].Name = "Emit Interval (minutes)";
    sc.Input[4].SetInt(0); // 0 = pas de throttle, >0 = minutes
    
    sc.Input[5].Name = "Emit VIX Close (0/1)";
    sc.Input[5].SetInt(0); // 0 = fichier vix_close désactivé, 1 = activé

    return;
  }

  // Autoriser l'exécution en historique/replay également
  // if (sc.ServerConnectionState != SCS_CONNECTED) return;

  // ========== MESSAGE DE DÉMARRAGE ==========
  static bool startup_logged = false;
  if (!startup_logged && ShouldLog(sc, LOG_KEY)) {
    SCString startupMsg;
    startupMsg.Format("MIA_Dumper_G8_VIX v2.0 - Chart %d - Debug Level: %d", 
                     sc.ChartNumber, sc.Input[2].GetInt());
    DebugLog(sc, startupMsg.GetChars());
    startup_logged = true;
  }

  // ========== VÉRIFICATIONS PRÉLIMINAIRES ==========
  if (sc.ArraySize <= 0) {
    if (ShouldLog(sc, LOG_ERROR)) {
      DebugLog(sc, "ERROR G8: No data available");
    }
    return;
  }

  const int i = sc.ArraySize - 1;
  if (i < 0) {
    if (ShouldLog(sc, LOG_ERROR)) {
      DebugLog(sc, "ERROR G8: Invalid bar index");
    }
    return;
  }

  // ========== COLLECTE VIX (AutoLoop = 1) ==========
  if (sc.Input[0].GetInt() != 0 && sc.ArraySize > 0) {
    const double t = sc.BaseDateTimeIn[sc.Index].GetAsDouble();
    const int barIndex = sc.Index;
    const char* symbol = sc.Symbol.GetChars();
    
    // Lire directement les données du chart VIX
    const double open = sc.BaseDataIn[SC_OPEN][sc.Index];
    const double high = sc.BaseDataIn[SC_HIGH][sc.Index];
    const double low = sc.BaseDataIn[SC_LOW][sc.Index];
    const double close = sc.BaseDataIn[SC_LAST][sc.Index];
    const double volume = sc.BaseDataIn[SC_VOLUME][sc.Index];

    // ========== VALIDATION DES DONNÉES ==========
    if (!ValidateVIXData(open, high, low, close, volume)) {
      if (ShouldLog(sc, LOG_ERROR)) {
        SCString errorMsg;
        errorMsg.Format("ERROR G8: Invalid VIX data - O:%.6f H:%.6f L:%.6f C:%.6f V:%.0f", 
                       open, high, low, close, volume);
        DebugLog(sc, errorMsg.GetChars());
      }
      UpdateVIXMetrics("invalid");
      return;
    }

    // ========== LOGIQUE SIMPLIFIÉE AVEC DÉDUPLICATION PAR FICHIER ==========
    // Récupération des inputs
    bool on_new_bar_only = (sc.Input[3].GetInt() != 0);
    int emit_interval_min = sc.Input[4].GetInt();
    bool emit_vix_close = (sc.Input[5].GetInt() != 0);
    
    // Vérifier clôture de barre
    int barStatus = sc.GetBarHasClosedStatus(sc.Index);
    bool bar_closed = (barStatus == BHCS_BAR_HAS_CLOSED);
    
    // Logique d'écriture simplifiée
    bool should_write = false;
    if (on_new_bar_only) {
      // Mode "1 ligne/barre" - seulement nouvelle barre fermée
      should_write = bar_closed;
    } else {
      // Mode intrabar - toujours écrire (déduplication par fichier)
      should_write = true;
    }
    
    if (should_write) {
      if (sc.Input[1].GetInt() == 0) {
        // Mode minimal : Close seulement
        SCString j;
        j.Format("{\"t\":%.6f,\"type\":\"vix\",\"i\":%d,\"last\":%.6f,\"chart\":%d}",
                 t, barIndex, close, sc.ChartNumber);
        WriteToSpecializedFile(sc.ChartNumber, "vix", j);
        UpdateVIXMetrics("vix");
        
        if (ShouldLog(sc, LOG_VERBOSE)) {
          SCString debugMsg;
          debugMsg.Format("DEBUG G8: VIX written - C:%.6f, Bar:%d, BarClosed:%s", 
                         close, barIndex, bar_closed ? "true" : "false");
          DebugLog(sc, debugMsg.GetChars());
        }
      } else {
        // Mode OHLC complet
        SCString j;
        j.Format("{\"t\":%.6f,\"type\":\"vix\",\"i\":%d,\"open\":%.6f,\"high\":%.6f,\"low\":%.6f,\"close\":%.6f,\"volume\":%.0f,\"chart\":%d}",
                 t, barIndex, open, high, low, close, volume, sc.ChartNumber);
        WriteToSpecializedFile(sc.ChartNumber, "vix", j);
        UpdateVIXMetrics("vix");
        
        if (ShouldLog(sc, LOG_VERBOSE)) {
          SCString debugMsg;
          debugMsg.Format("DEBUG G8: VIX OHLC written - O:%.6f H:%.6f L:%.6f C:%.6f V:%.0f", 
                         open, high, low, close, volume);
          DebugLog(sc, debugMsg.GetChars());
        }
      }

      // ========== EVENT VIX CLOSE (OPTIONNEL) ==========
      if (emit_vix_close) {
        SCString vix_event;
        vix_event.Format("{\"t\":%.6f,\"type\":\"vix_close\",\"vix\":%.6f,\"chart\":%d}",
                         t, close, sc.ChartNumber);
        WriteToSpecializedFile(sc.ChartNumber, "vix_close", vix_event);
        UpdateVIXMetrics("vix_close");
        
        if (ShouldLog(sc, LOG_VERBOSE)) {
          SCString debugMsg;
          debugMsg.Format("DEBUG G8: VIX Close event written - VIX:%.6f", close);
          DebugLog(sc, debugMsg.GetChars());
        }
      }
      
      // Pas besoin de mettre à jour les variables statiques
      // La déduplication est gérée par WriteToSpecializedFile
    }
  }

  // ========== MÉTRIQUES DE PERFORMANCE ==========
  CheckVIXPerformance(sc);
}
