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
static void EnsureOutDir() {
#ifdef _WIN32
  CreateDirectoryA("D:\\MIA_IA_system", NULL);
#endif
}

// Génération du nom de fichier quotidien par chart et type
static SCString DailyFilenameForChartType(int chartNumber, const char* dataType) {
  time_t now = time(NULL);
  struct tm* lt = localtime(&now);
  int y = lt ? (lt->tm_year + 1900) : 1970;
  int m = lt ? (lt->tm_mon + 1) : 1;
  int d = lt ? lt->tm_mday : 1;
  SCString filename;
  filename.Format("D:\\MIA_IA_system\\chart_%d_%s_%04d%02d%02d.jsonl", 
                  chartNumber, dataType, y, m, d);
  return filename;
}

// Écriture dans le fichier spécialisé
static void WriteToSpecializedFile(int chartNumber, const char* dataType, const SCString& line) {
  EnsureOutDir();
  const SCString filename = DailyFilenameForChartType(chartNumber, dataType);
  FILE* f = fopen(filename.GetChars(), "a");
  if (f) { 
    fprintf(f, "%s\n", line.GetChars()); 
    fclose(f); 
  }
}

// Anti-duplication simple par (chart, type, key)
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
  return array.GetArraySize() > index && array[index] != 0.0;
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
    sc.AutoLoop = 0;
    sc.UpdateAlways = 1;
    sc.CalculationPrecedence = LOW_PREC_LEVEL;

    // --- Inputs VIX ---
    sc.Input[0].Name = "Export VIX (0/1)";
    sc.Input[0].SetInt(1);
    sc.Input[1].Name = "Export OHLC (0/1)";
    sc.Input[1].SetInt(0); // 0 = Close seulement, 1 = OHLC complet

    return;
  }

  if (sc.ServerConnectionState != SCS_CONNECTED) return;

  // ========== COLLECTE VIX ==========
  if (sc.Input[0].GetInt() != 0 && sc.ArraySize > 0) {
    const int i = sc.ArraySize - 1;
    const double t = sc.BaseDateTimeIn[i].GetAsDouble();
    
    // Lire directement les données du chart VIX
    const double open = sc.BaseDataIn[SC_OPEN][i];
    const double high = sc.BaseDataIn[SC_HIGH][i];
    const double low = sc.BaseDataIn[SC_LOW][i];
    const double close = sc.BaseDataIn[SC_LAST][i];
    const double volume = sc.BaseDataIn[SC_VOLUME][i];

    if (sc.Input[1].GetInt() == 0) {
      // Mode minimal : Close seulement
      SCString j;
      j.Format("{\"t\":%.6f,\"type\":\"vix\",\"i\":%d,\"last\":%.6f,\"chart\":%d}",
               t, i, close, sc.ChartNumber);
      WriteToSpecializedFile(sc.ChartNumber, "vix", j);
    } else {
      // Mode OHLC complet
      SCString j;
      j.Format("{\"t\":%.6f,\"type\":\"vix\",\"i\":%d,\"open\":%.6f,\"high\":%.6f,\"low\":%.6f,\"close\":%.6f,\"volume\":%.0f,\"chart\":%d}",
               t, i, open, high, low, close, volume, sc.ChartNumber);
      WriteToSpecializedFile(sc.ChartNumber, "vix", j);
    }
  }
}
