// === MIA_Dumper_G10_MenthorQ.cpp (header inlined - Approach 1) ===
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

SCDLLName("MIA_Dumper_G10_MenthorQ")

// ========== UTILITAIRES COMMUNS ==========

// Création du répertoire de sortie organisé
static void EnsureOutDir(const char* baseDir = "D:\\MIA_IA_system") {
#ifdef _WIN32
  CreateDirectoryA(baseDir, NULL);
  CreateDirectoryA("D:\\MIA_IA_system\\DATA_SIERRA_CHART", NULL);
#endif
}

// Création de la structure de répertoires organisée
static void EnsureOrganizedDir(int chartNumber) {
#ifdef _WIN32
  time_t now = time(NULL);
  struct tm* lt = localtime(&now);
  int y = lt ? (lt->tm_year + 1900) : 1970;
  int m = lt ? (lt->tm_mon + 1) : 1;
  int d = lt ? lt->tm_mday : 1;
  
  // Noms des mois
  const char* monthNames[] = {"JANVIER", "FEVRIER", "MARS", "AVRIL", "MAI", "JUIN",
                             "JUILLET", "AOUT", "SEPTEMBRE", "OCTOBRE", "NOVEMBRE", "DECEMBRE"};
  
  char basePath[512];
  char yearPath[512];
  char monthPath[512];
  char dayPath[512];
  char chartPath[512];
  
  sprintf(basePath, "D:\\MIA_IA_system\\DATA_SIERRA_CHART");
  sprintf(yearPath, "%s\\DATA_%d", basePath, y);
  sprintf(monthPath, "%s\\%s", yearPath, monthNames[m-1]);
  sprintf(dayPath, "%s\\%04d%02d%02d", monthPath, y, m, d);
  sprintf(chartPath, "%s\\CHART_%d", dayPath, chartNumber);
  
  CreateDirectoryA(basePath, NULL);
  CreateDirectoryA(yearPath, NULL);
  CreateDirectoryA(monthPath, NULL);
  CreateDirectoryA(dayPath, NULL);
  CreateDirectoryA(chartPath, NULL);
#endif
}

// Génération du nom de fichier quotidien par chart et type dans la structure organisée
static SCString DailyFilenameForChartType(int chartNumber, const char* dataType, const char* baseDir = "D:\\MIA_IA_system") {
  time_t now = time(NULL);
  struct tm* lt = localtime(&now);
  int y = lt ? (lt->tm_year + 1900) : 1970;
  int m = lt ? (lt->tm_mon + 1) : 1;
  int d = lt ? lt->tm_mday : 1;
  
  // Noms des mois
  const char* monthNames[] = {"JANVIER", "FEVRIER", "MARS", "AVRIL", "MAI", "JUIN",
                             "JUILLET", "AOUT", "SEPTEMBRE", "OCTOBRE", "NOVEMBRE", "DECEMBRE"};
  
  SCString filename;
  filename.Format("D:\\MIA_IA_system\\DATA_SIERRA_CHART\\DATA_%d\\%s\\%04d%02d%02d\\CHART_%d\\chart_%d_%s_%04d%02d%02d.jsonl", 
                  y, monthNames[m-1], y, m, d, chartNumber, chartNumber, dataType, y, m, d);
  return filename;
}

// Écriture dans le fichier spécialisé avec structure organisée
static void WriteToSpecializedFile(int chartNumber, const char* dataType, const SCString& line, const char* baseDir = "D:\\MIA_IA_system") {
  EnsureOutDir(baseDir);
  EnsureOrganizedDir(chartNumber);  // Créer la structure de répertoires
  const SCString filename = DailyFilenameForChartType(chartNumber, dataType, baseDir);
  FILE* f = fopen(filename.GetChars(), "a");
  if (f) { 
    fprintf(f, "%s\n", line.GetChars()); 
    fclose(f); 
  }
}

// ========== DÉDUPLICATION INTELLIGENTE AMÉLIORÉE ==========
// Structure pour la déduplication par (sym, t, i)
struct LastKey { 
  double t = 0.0; // timestamp
  double i = -1;  // bar index
};

// Structures pour la détection de changement d'état
struct LastMenthorQ {
  std::unordered_map<std::string, double> last_values; // level_type -> price
};

// Maps de déduplication par symbole
static std::unordered_map<std::string, LastKey> g_LastKeyBySym;
static std::unordered_map<std::string, LastMenthorQ> g_LastMenthorQBySym;

// ========== DÉTECTION DE CHANGEMENT ==========
static inline bool has_changed(double a, double b, double eps=1e-9) {
  return fabs(a-b) > eps;
}

// ========== SYSTÈME DEBUG ==========
enum LogLevel { LOG_ERROR = 0, LOG_KEY = 1, LOG_VERBOSE = 2 };

static void DebugLog(SCStudyInterfaceRef& sc, const char* message) {
  sc.AddMessageToLog(message, 1);
}

static inline bool ShouldLog(const SCStudyInterfaceRef& sc, int level) {
  return sc.Input[11].GetInt() >= level;
}

// ========== PRÉCISION PRIX DYNAMIQUE ==========
static const char* get_price_format(double tick_size) {
  static char format_buf[16];
  if (tick_size >= 1.0) {
    snprintf(format_buf, sizeof(format_buf), "%.2f");
  } else {
    int decimals = min(6, (int)std::ceil(-std::log10(tick_size)));
    snprintf(format_buf, sizeof(format_buf), "%%.%df", decimals);
  }
  return format_buf;
}

// Fonction de déduplication améliorée avec clé (symbol|chart)
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

// ========== TIMER UTILITAIRE ==========
static inline bool ShouldEmitEveryNMinutes(const SCDateTime& now,
                                           SCDateTime& last_emit,
                                           int minutes)
{
  if (minutes <= 0) return true; // pas de throttle
  if (last_emit <= 0.0) { 
    last_emit = now; 
    return true; // 1ère fois - émettre immédiatement
  }
  const double dt_sec = (now.GetAsDouble() - last_emit.GetAsDouble()) * 86400.0;
  bool should_emit = dt_sec >= minutes * 60.0 - 0.5; // epsilon pour arrondis
  if (should_emit) {
    last_emit = now; // Mettre à jour le timer
  }
  return should_emit;
}

// ========== NORMALISATION DES PRIX ==========
inline double NormalizePx(const SCStudyInterfaceRef& sc, double raw)
{
  // 1) Dé-multiplier si besoin
  const double mult = (sc.RealTimePriceMultiplier != 0.0 ? sc.RealTimePriceMultiplier : 1.0);
  double px = raw / mult;

  // 2) Correction d'échelle avant arrondi (certains flux arrivent x100)
  if (px > 10000.0) px /= 100.0;

  // 3) Arrondi au tick
  px = sc.RoundToTickSize(px, sc.TickSize);

  // 4) Correction d'échelle résiduelle puis arrondi final (sécurité)
  if (px > 10000.0) px /= 100.0;
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
#define MENTHORQ_BLIND_SG_COUNT 10
#define MENTHORQ_SWING_SG_COUNT 9

// =======================================================================
// ===============    STUDY ENTRYPOINT (G10 MENTHORQ)    =======================
// =======================================================================

// Dumper spécialisé pour Chart 10 (MenthorQ)
// Collecte UNIQUEMENT les données MenthorQ du Chart 10
// Sortie spécialisée : menthorq

SCSFExport scsf_MIA_Dumper_G10_MenthorQ(SCStudyInterfaceRef sc)
{
  if (sc.SetDefaults)
  {
    sc.GraphName = "MIA Dumper G10 MenthorQ";
    sc.StudyDescription = "Collecte spécialisée Chart 10 - MenthorQ uniquement";
    sc.AutoLoop = 0;
    sc.UpdateAlways = 1;
    sc.CalculationPrecedence = LOW_PREC_LEVEL;

    // --- Inputs MenthorQ ---
    sc.Input[0].Name = "Export MenthorQ Levels (0/1)";
    sc.Input[0].SetInt(1);
    sc.Input[1].Name = "Gamma Levels Study ID (0=off)";
    sc.Input[1].SetInt(1);
    sc.Input[2].Name = "Gamma Levels Subgraphs Count";
    sc.Input[2].SetInt(19);
    sc.Input[3].Name = "Blind Spots Study ID (0=off)";
    sc.Input[3].SetInt(3);
    sc.Input[4].Name = "Blind Spots Subgraphs Count";
    sc.Input[4].SetInt(10);
    sc.Input[5].Name = "Swing Levels Study ID (0=off)";
    sc.Input[5].SetInt(2);
    sc.Input[6].Name = "Swing Levels Subgraphs Count";
    sc.Input[6].SetInt(60); // 60 niveaux selon le mapping
    
    sc.Input[7].Name = "Correlation Study ID (0=off)";
    sc.Input[7].SetInt(4);  // Study ID 4 selon l'inventory
    sc.Input[8].Name = "Correlation Subgraphs Count";
    sc.Input[8].SetInt(1);  // 1 subgraph pour la corrélation
    sc.Input[9].Name = "MenthorQ On New Bar Only (0/1)";
    sc.Input[9].SetInt(1);
    
    sc.Input[10].Name = "Debug Log Level (0=Off,1=Key,2=Verbose)";
    sc.Input[10].SetInt(1); // Debug = On pour diagnostiquer

    // --- Corrélation: SG configurable + mode émission ---
    sc.Input[11].Name = "Correlation Subgraph Index"; // 0 = CC (par défaut)
    sc.Input[11].SetInt(0);
    sc.Input[12].Name = "Correlation On New Bar Only (0/1)"; // 1 = par barre, 0 = timer intrabar
    sc.Input[12].SetInt(1);

    return;
  }

  // Ne pas bloquer en historique/replay: on autorise l'émission même hors connexion serveur
  // if (sc.ServerConnectionState != SCS_CONNECTED) return;

  // ========== COLLECTE MENTHORQ ==========
  if (sc.Input[0].GetInt() != 0 && sc.ArraySize > 0)
  {
    const int i = sc.ArraySize - 1;
    const SCDateTime tbar = sc.BaseDateTimeIn[i];
    const SCDateTime now = sc.CurrentSystemDateTime;
    const bool on_bar = (sc.Input[12].GetInt() != 0);
    
    // Timers statiques par type
    static SCDateTime s_last_gamma_emit(0.0);
    static SCDateTime s_last_blind_emit(0.0);
    static SCDateTime s_last_corr_emit(0.0);
    
    // ========== GAMMA LEVELS ==========
    const int gamma_min = 15; // 15 minutes fixe
    
    // Debug logging
    if (ShouldLog(sc, LOG_KEY)) {
      SCString debugMsg;
      debugMsg.Format("DEBUG: Gamma timer check - on_bar:%s, bar_closed:%s, gamma_min:%d", 
                     on_bar ? "true" : "false",
                     (sc.GetBarHasClosedStatus(i) == BHCS_BAR_HAS_CLOSED) ? "true" : "false",
                     gamma_min);
      DebugLog(sc, debugMsg.GetChars());
    }
    
    // Condition assouplie : émettre si pas de barre OU barre fermée
    bool can_emit_gamma = !on_bar || (sc.GetBarHasClosedStatus(i) == BHCS_BAR_HAS_CLOSED);
    if (can_emit_gamma && ShouldEmitEveryNMinutes(now, s_last_gamma_emit, gamma_min)) {

      // Boucle Gamma Levels (SG0-18)
      const int gamma_study_id = sc.Input[1].GetInt();
      const int gamma_sg_count = sc.Input[2].GetInt();
      const double t = tbar.GetAsDouble();
      const char* symbol = sc.Symbol.GetChars();
      
      for (int sg = 0; sg < gamma_sg_count; ++sg) {
        SCFloatArray arr;
        if (ReadSubgraph(sc, gamma_study_id, sg, arr) && arr.GetArraySize() > i) {
          double val = arr[i];
          if (ShouldLog(sc, LOG_KEY)) {
            SCString debugMsg;
            debugMsg.Format("DEBUG: Gamma SG%d - val:%.2f, finite:%s", sg, val, std::isfinite(val) ? "true" : "false");
            DebugLog(sc, debugMsg.GetChars());
          }
          if (std::isfinite(val) && val > 0.0) {
            double p = NormalizePx(sc, val);
            SCString levelType;
            switch(sg) {
              case 0: levelType = "call_resistance"; break;
              case 1: levelType = "put_support"; break;
              case 2: levelType = "hvl"; break;
              case 3: levelType = "1d_min"; break;
              case 4: levelType = "1d_max"; break;
              case 5: levelType = "call_resistance_0dte"; break;
              case 6: levelType = "put_support_0dte"; break;
              case 7: levelType = "hvl_0dte"; break;
              case 8: levelType = "gamma_wall_0dte"; break;
              case 9: levelType = "gex_1"; break;
              case 10: levelType = "gex_2"; break;
              case 11: levelType = "gex_3"; break;
              case 12: levelType = "gex_4"; break;
              case 13: levelType = "gex_5"; break;
              case 14: levelType = "gex_6"; break;
              case 15: levelType = "gex_7"; break;
              case 16: levelType = "gex_8"; break;
              case 17: levelType = "gex_9"; break;
              case 18: levelType = "gex_10"; break;
              default: levelType.Format("gamma_sg_%d", sg); break;
            }
            
            const char* price_fmt = get_price_format(sc.TickSize);
            SCString j;
            j.Format("{\"t\":%.6f,\"sym\":\"%s\",\"type\":\"menthorq_level\",\"level_type\":\"%s\",\"price\":",
                     t, symbol, levelType.GetChars());
            j += SCString().Format(price_fmt, p);
            j += SCString().Format(",\"subgraph\":%d,\"study_id\":%d,\"i\":%d,\"chart\":%d}",
                                   sg, gamma_study_id, i, sc.ChartNumber);
            WriteToSpecializedFile(sc.ChartNumber, "menthorq", j);
          }
        }
      }
    }
    
    // ========== BLIND SPOTS ==========
    const int blind_min = 15; // 15 minutes fixe
    
    // Debug logging
    if (ShouldLog(sc, LOG_KEY)) {
      SCString debugMsg;
      debugMsg.Format("DEBUG: Blind timer check - blind_min:%d", blind_min);
      DebugLog(sc, debugMsg.GetChars());
    }
    
    // Condition assouplie : émettre si pas de barre OU barre fermée
    bool can_emit_blind = !on_bar || (sc.GetBarHasClosedStatus(i) == BHCS_BAR_HAS_CLOSED);
    if (can_emit_blind && ShouldEmitEveryNMinutes(now, s_last_blind_emit, blind_min)) {
      const int blind_study_id = sc.Input[3].GetInt();
      const int blind_sg_count = sc.Input[4].GetInt();
      const double t = tbar.GetAsDouble();
      const char* symbol = sc.Symbol.GetChars();
      
      for (int sg = 0; sg < blind_sg_count; ++sg) {
        SCFloatArray arr;
        if (ReadSubgraph(sc, blind_study_id, sg, arr) && arr.GetArraySize() > i) {
          double val = arr[i];
          if (std::isfinite(val) && val > 0.0) { // N'écrire que si val > 0
            double p = NormalizePx(sc, val);
            SCString levelType;
            levelType.Format("blind_spot_%d", sg);
            
            const char* price_fmt = get_price_format(sc.TickSize);
            SCString j;
            j.Format("{\"t\":%.6f,\"sym\":\"%s\",\"type\":\"menthorq_level\",\"level_type\":\"%s\",\"price\":",
                     t, symbol, levelType.GetChars());
            j += SCString().Format(price_fmt, p);
            j += SCString().Format(",\"subgraph\":%d,\"study_id\":%d,\"i\":%d,\"chart\":%d}",
                                   sg, blind_study_id, i, sc.ChartNumber);
            WriteToSpecializedFile(sc.ChartNumber, "menthorq", j);
          }
        }
      }
    }
  }

  // ========== CORRÉLATION ==========
  if (sc.Input[7].GetInt() != 0 && sc.ArraySize > 0)
  {
    const int i = sc.ArraySize - 1;
    const SCDateTime tbar = sc.BaseDateTimeIn[i];
    const SCDateTime now = sc.CurrentSystemDateTime;
    const bool on_bar = (sc.Input[12].GetInt() != 0);
    
    // Timer statique pour corrélation
    static SCDateTime s_last_corr_emit(0.0);
    
    const int corr_min = 1; // 1 minute fixe
    
    // Debug logging
    if (ShouldLog(sc, LOG_KEY)) {
      SCString debugMsg;
      debugMsg.Format("DEBUG: Correlation timer check - corr_min:%d", corr_min);
      DebugLog(sc, debugMsg.GetChars());
    }
    
    // Condition assouplie : émettre si pas de barre OU barre fermée
    bool can_emit_corr = !on_bar || (sc.GetBarHasClosedStatus(i) == BHCS_BAR_HAS_CLOSED);
    if (can_emit_corr && ShouldEmitEveryNMinutes(now, s_last_corr_emit, corr_min)) {
      const int corr_study_id = sc.Input[7].GetInt();
      const int corr_sg = sc.Input[11].GetInt();
      
      SCFloatArray corr_array;
      sc.GetStudyArrayUsingID(corr_study_id, corr_sg, corr_array);
      if (corr_array.GetArraySize() > i) {
        const double cc = corr_array[i];
        if (std::isfinite(cc) && cc >= -1.0 && cc <= 1.0) {
          const double tsec = tbar.GetAsDouble();
          const double bar_index = (double)i;
          
          SCString j;
          j.Format(R"({"t":%.6f,"sym":"%s","type":"correlation","cc":%.6f,"study_id":%d,"sg":%d,"i":%.0f,"chart":%d})",
                   tsec, sc.Symbol.GetChars(), cc, corr_study_id, corr_sg, bar_index, sc.ChartNumber);
          WriteToSpecializedFile(sc.ChartNumber, "menthorq", j);
        }
      }
    }
  }
}