#pragma once

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
    return sc.GetStudyArrayFromChartUsingID(chartNumber, studyID, subgraphIndex, array) != 0;
  } else {
    return sc.GetStudyArrayUsingID(studyID, subgraphIndex, array) != 0;
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

// VVA Subgraphs (Volume Value Area)
#define VVA_SG_POC 1
#define VVA_SG_VAH 2
#define VVA_SG_VAL 3

// NBCV Subgraphs (Numbers Bars Calculated Values)
#define NBCV_SG_ASK_VOLUME 6
#define NBCV_SG_BID_VOLUME 7
#define NBCV_SG_DELTA 1
#define NBCV_SG_TRADES 12
#define NBCV_SG_CUMULATIVE 10

// VIX Subgraph
#define VIX_SG_LAST 4

// MenthorQ Subgraphs
#define MENTHORQ_GAMMA_SG_COUNT 19
#define MENTHORQ_BLIND_SG_COUNT 9
#define MENTHORQ_SWING_SG_COUNT 9
