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
// ===============    STUDY ENTRYPOINT (G10 MENTHORQ)    =======================
// =======================================================================

SCDLLName("MIA_Dumper_G10_MenthorQ")

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
    sc.Input[4].SetInt(9);
    sc.Input[5].Name = "Swing Levels Study ID (0=off)";
    sc.Input[5].SetInt(2);
    sc.Input[6].Name = "Swing Levels Subgraphs Count";
    sc.Input[6].SetInt(60); // 60 niveaux selon le mapping
    sc.Input[7].Name = "MenthorQ On New Bar Only (0/1)";
    sc.Input[7].SetInt(1);

    return;
  }

  if (sc.ServerConnectionState != SCS_CONNECTED) return;

  // ========== COLLECTE MENTHORQ ==========
  if (sc.Input[0].GetInt() != 0 && sc.ArraySize > 0)
  {
    const int i = sc.ArraySize - 1;
    const bool newbar_only_mq = sc.Input[7].GetInt() != 0;
    static SCDateTime s_last_mq_bar_time(0.0);

    const SCDateTime cur_time = sc.BaseDateTimeIn[i];
    if (!newbar_only_mq || cur_time != s_last_mq_bar_time)
    {
      s_last_mq_bar_time = cur_time;

      auto level_type_for = [&](int studyId, int sg) -> SCString {
        SCString s;
        if (studyId == sc.Input[1].GetInt()) { // Gamma Levels
          switch(sg) {
            case 0: s = "call_resistance"; break;
            case 1: s = "put_support"; break;
            case 2: s = "hvl"; break;
            case 3: s = "1d_min"; break;
            case 4: s = "1d_max"; break;
            case 5: s = "call_resistance_0dte"; break;
            case 6: s = "put_support_0dte"; break;
            case 7: s = "hvl_0dte"; break;
            case 8: s = "gamma_wall_0dte"; break;
            case 9: s = "gex_1"; break;
            case 10: s = "gex_2"; break;
            case 11: s = "gex_3"; break;
            case 12: s = "gex_4"; break;
            case 13: s = "gex_5"; break;
            case 14: s = "gex_6"; break;
            case 15: s = "gex_7"; break;
            case 16: s = "gex_8"; break;
            case 17: s = "gex_9"; break;
            case 18: s = "gex_10"; break;
            default: s.Format("gamma_sg_%d", sg); break;
          }
        } else if (studyId == sc.Input[3].GetInt()) { // Blind Spots
          s.Format("blind_spot_%d", sg);
        } else if (studyId == sc.Input[5].GetInt()) { // Swing Levels
          s.Format("swing_lvl_%d", sg);
        } else {
          s.Format("sg_%d", sg);
        }
        return s;
      };

      auto emit_levels = [&](int studyId, int sgCount)
      {
        if (studyId <= 0) return;
        int iDest = i;

        for (int sg = 0; sg < sgCount; ++sg)
        {
          SCFloatArray arr;
          if (ReadSubgraph(sc, studyId, sg, arr)) {
            double val = 0.0;
            int iOut = iDest;
            if (arr.GetArraySize() > iDest)
              val = arr[iDest];
            // Fallback: prendre la dernière valeur non nulle si l'alignement ne donne rien
            if (val == 0.0 && arr.GetArraySize() > 0)
            {
              for (int k = arr.GetArraySize() - 1; k >= 0; --k)
              {
                if (arr[k] != 0.0) { val = arr[k]; iOut = k; break; }
              }
            }
            if (val != 0.0)
            {
              double p = NormalizePx(sc, val);
              SCString j;
              SCString levelType = level_type_for(studyId, sg);
              j.Format("{\"t\":%.6f,\"sym\":\"%s[M]  1 Min  #%d\",\"type\":\"menthorq_level\",\"level_type\":\"%s\",\"price\":%.2f,\"subgraph\":%d,\"study_id\":%d,\"bar\":%d,\"chart\":%d}",
                       cur_time.GetAsDouble(), sc.Symbol.GetChars(), sc.ChartNumber, levelType.GetChars(), p, sg, studyId, iOut, sc.ChartNumber);
              WriteToSpecializedFile(sc.ChartNumber, "menthorq", j);
            }
            else
            {
              SCString d; d.Format("{\"t\":%.6f,\"type\":\"menthorq_diag\",\"chart\":%d,\"study\":%d,\"sg\":%d,\"msg\":\"no_value\"}",
                                   cur_time.GetAsDouble(), sc.ChartNumber, studyId, sg);
              WriteToSpecializedFile(sc.ChartNumber, "menthorq", d);
            }
          }
        }
      };

      // Collecter les niveaux de chaque type
      emit_levels(sc.Input[1].GetInt(), sc.Input[2].GetInt()); // Gamma Levels
      emit_levels(sc.Input[3].GetInt(), sc.Input[4].GetInt()); // Blind Spots
      emit_levels(sc.Input[5].GetInt(), sc.Input[6].GetInt()); // Swing Levels
    }
  }
}
