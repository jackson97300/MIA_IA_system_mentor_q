// === MIA_Dumper_G4_Studies.cpp (header inlined - Approach 1) ===
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
// ===============    STUDY ENTRYPOINT (G4 STUDIES)    =======================
// =======================================================================

SCDLLName("MIA_Dumper_G4_Studies")

// Dumper spécialisé pour Chart 4 (30 minutes)
// Collecte UNIQUEMENT les données natives du Chart 4
// Sorties spécialisées : ohlc, vwap_current, pvwap, nbcv

SCSFExport scsf_MIA_Dumper_G4_Studies(SCStudyInterfaceRef sc)
{
  if (sc.SetDefaults)
  {
    sc.GraphName = "MIA Dumper G4 Studies";
    sc.StudyDescription = "Collecte spécialisée Chart 4 - Données M30 uniquement";
    sc.AutoLoop = 0;
    sc.UpdateAlways = 1;
    sc.MaintainVolumeAtPriceData = 1;
    sc.MaintainAdditionalChartDataArrays = 1;
    sc.CalculationPrecedence = LOW_PREC_LEVEL;

    // --- Inputs VWAP ---
    sc.Input[0].Name = "Export VWAP Current (0/1)";
    sc.Input[0].SetInt(1);
    sc.Input[1].Name = "VWAP Study ID (0=auto)";
    sc.Input[1].SetInt(1); // Study ID 1 pour Chart 4
    sc.Input[2].Name = "VWAP Bands Count (0..3)";
    sc.Input[2].SetInt(3);

    // --- Inputs PVWAP ---
    sc.Input[3].Name = "Export PVWAP (0/1)";
    sc.Input[3].SetInt(1);
    sc.Input[4].Name = "PVWAP Study ID";
    sc.Input[4].SetInt(3); // ID 3 pour PVWAP
    sc.Input[5].Name = "PVWAP Bands Count (0..2)";
    sc.Input[5].SetInt(2);

    // --- Inputs NBCV ---
    sc.Input[6].Name = "Export NBCV (0/1)";
    sc.Input[6].SetInt(1);
    sc.Input[7].Name = "NBCV Study ID";
    sc.Input[7].SetInt(14); // ID 14 pour Graph 4

    // --- Inputs Cumulative Delta ---
    sc.Input[8].Name = "Export Cumulative Delta (0/1)";
    sc.Input[8].SetInt(1);
    sc.Input[9].Name = "Cumulative Delta Study ID";
    sc.Input[9].SetInt(6); // ID 6 pour Cumulative Delta Bars

    // --- Inputs Correlation ---
    sc.Input[10].Name = "Export Correlation (0/1)";
    sc.Input[10].SetInt(1);
    sc.Input[11].Name = "Correlation Study ID";
    sc.Input[11].SetInt(15); // ID 15 pour Correlation

    // --- Inputs ATR ---
    sc.Input[12].Name = "Export ATR (0/1)";
    sc.Input[12].SetInt(1);
    sc.Input[13].Name = "ATR Study ID";
    sc.Input[13].SetInt(5); // ID 5 pour ATR
    sc.Input[14].Name = "ATR Subgraph Index";
    sc.Input[14].SetInt(0); // SG 0 pour ATR

    // --- Inputs VVA Previous ---
    sc.Input[15].Name = "Export VVA Previous (0/1)";
    sc.Input[15].SetInt(1);
    sc.Input[16].Name = "VVA Previous Study ID";
    sc.Input[16].SetInt(9); // ID 9 pour VVA Previous
    sc.Input[17].Name = "VVA Previous POC Subgraph";
    sc.Input[17].SetInt(0); // SG 0 = PPOC
    sc.Input[18].Name = "VVA Previous VAH Subgraph";
    sc.Input[18].SetInt(1); // SG 1 = PVAH
    sc.Input[19].Name = "VVA Previous VAL Subgraph";
    sc.Input[19].SetInt(2); // SG 2 = PVAL

    // --- Inputs Volume Profile (HVN/LVN) ---
    sc.Input[20].Name = "Export Volume Profile (0/1)";
    sc.Input[20].SetInt(1);
    sc.Input[21].Name = "Volume Profile Study ID";
    sc.Input[21].SetInt(14); // ID 14 pour Volume Profile (HVN/LVN valides)
    sc.Input[22].Name = "Export VPOC/VAH/VAL (0/1)";
    sc.Input[22].SetInt(1);
    sc.Input[23].Name = "Export HVN/LVN (0/1)";
    sc.Input[23].SetInt(1);

    return;
  }

  if (sc.ServerConnectionState != SCS_CONNECTED) return;

  // ---- OHLC Graph4 (chaque tick) ----
  if (sc.ArraySize > 0) {
    const int i = sc.ArraySize - 1;
    const double t = sc.BaseDateTimeIn[i].GetAsDouble();
    const double o = sc.BaseDataIn[SC_OPEN][i];
    const double h = sc.BaseDataIn[SC_HIGH][i];
    const double l = sc.BaseDataIn[SC_LOW][i];
    const double c = sc.BaseDataIn[SC_LAST][i];
    const double v = sc.BaseDataIn[SC_VOLUME][i];

    SCString j;
    j.Format("{\"t\":%.6f,\"sym\":\"%s\",\"type\":\"ohlc_graph4\",\"bar\":%d,\"source\":\"chart_array\",\"chart\":%d,\"dt_g4\":%.6f,\"open\":%.2f,\"high\":%.2f,\"low\":%.2f,\"close\":%.2f,\"volume\":%.0f}",
      t, sc.Symbol.GetChars(), i, sc.ChartNumber, c, o, h, l, c, v);
    WriteToSpecializedFile(sc.ChartNumber, "ohlc", j);
  }

  // ---- VWAP Current (chaque tick) ----
  if (sc.Input[0].GetInt() != 0 && sc.ArraySize > 0) {
    static int vwapID = -2;
    const int i = sc.ArraySize - 1;
    const double t = sc.BaseDateTimeIn[i].GetAsDouble();
  
    if (vwapID == -2) {
      int cand[3];
      cand[0] = sc.Input[1].GetInt(); // ID forcé
      cand[1] = ResolveStudyID(sc, sc.ChartNumber, "Volume Weighted Average Price", 0);
      cand[2] = ResolveStudyID(sc, sc.ChartNumber, "VWAP (Volume Weighted Average Price)", 0);
  
      vwapID = -1;
      for (int k = 0; k < 3; ++k) {
        if (cand[k] > 0) {
          SCFloatArray test;
          if (ReadSubgraph(sc, cand[k], VWAP_SG_MAIN, test)) {
            if (ValidateStudyData(test, i)) { 
              vwapID = cand[k]; 
              break; 
            }
          }
        }
      }
    }
  
    if (vwapID > 0) {
      SCFloatArray VWAP, UP1, DN1, UP2, DN2, UP3, DN3;
      ReadSubgraph(sc, vwapID, VWAP_SG_MAIN, VWAP);
      
      int bands = sc.Input[2].GetInt();
      if (bands >= 1) {
        ReadSubgraph(sc, vwapID, VWAP_SG_UP1, UP1);
        ReadSubgraph(sc, vwapID, VWAP_SG_DN1, DN1);
      }
      if (bands >= 2) {
        ReadSubgraph(sc, vwapID, VWAP_SG_UP2, UP2);
        ReadSubgraph(sc, vwapID, VWAP_SG_DN2, DN2);
      }
      if (bands >= 3) {
        ReadSubgraph(sc, vwapID, VWAP_SG_UP3, UP3);
        ReadSubgraph(sc, vwapID, VWAP_SG_DN3, DN3);
      }

      if (ValidateStudyData(VWAP, i)) {
        double v   = NormalizePx(sc, VWAP[i]);
        double up1 = (ValidateStudyData(UP1, i) ? NormalizePx(sc, UP1[i]) : 0);
        double dn1 = (ValidateStudyData(DN1, i) ? NormalizePx(sc, DN1[i]) : 0);
        double up2 = (ValidateStudyData(UP2, i) ? NormalizePx(sc, UP2[i]) : 0);
        double dn2 = (ValidateStudyData(DN2, i) ? NormalizePx(sc, DN2[i]) : 0);
        double up3 = (ValidateStudyData(UP3, i) ? NormalizePx(sc, UP3[i]) : 0);
        double dn3 = (ValidateStudyData(DN3, i) ? NormalizePx(sc, DN3[i]) : 0);

        SCString j;
        j.Format("{\"t\":%.6f,\"sym\":\"%s\",\"type\":\"vwap_current\",\"bar\":%d,\"source\":\"graph4\",\"vwap\":%.2f,\"s_plus_1\":%.2f,\"s_minus_1\":%.2f,\"s_plus_2\":%.2f,\"s_minus_2\":%.2f,\"study_id\":%d}",
                 t, sc.Symbol.GetChars(), i, v, up1, dn1, up2, dn2, vwapID);
        WriteToSpecializedFile(sc.ChartNumber, "vwap", j);
      }
    }
  }

  // ---- PVWAP (Previous VWAP) ----
  if (sc.Input[3].GetInt() != 0 && sc.ArraySize > 0) {
    const int i = sc.ArraySize - 1;
    const double t = sc.BaseDateTimeIn[i].GetAsDouble();
    const int pvwapID = sc.Input[4].GetInt();
    const int pvwapSG = 4; // SG4 = PVWAP

    SCFloatArray PVWAP;
    ReadSubgraph(sc, pvwapID, pvwapSG, PVWAP);
    
    if (ValidateStudyData(PVWAP, i)) {
      double pvwap = NormalizePx(sc, PVWAP[i]);
      
      // Calculer les bandes si demandé
      int nb = sc.Input[5].GetInt();
      double up1=0, dn1=0, up2=0, dn2=0;
      if (nb >= 1) { up1 = pvwap + 0.5; dn1 = pvwap - 0.5; }
      if (nb >= 2) { up2 = pvwap + 1.0; dn2 = pvwap - 1.0; }

      SCString j;
      j.Format("{\"t\":%.6f,\"sym\":\"%s\",\"type\":\"pvwap\",\"i\":%d,\"prev_start\":0,\"prev_end\":0,\"pvwap\":%.8f,\"up1\":%.8f,\"dn1\":%.8f,\"up2\":%.8f,\"dn2\":%.8f,\"up3\":0.0,\"dn3\":0.0,\"up4\":0.0,\"dn4\":0.0}",
               t, sc.Symbol.GetChars(), i, pvwap, up1, dn1, up2, dn2);
      WriteToSpecializedFile(sc.ChartNumber, "pvwap", j);
    }
  }

  // ---- NBCV (Numbers Bars Calculated Values) ----
  if (sc.Input[6].GetInt() != 0 && sc.ArraySize > 0) {
    const int i = sc.ArraySize - 1;
    const double t = sc.BaseDateTimeIn[i].GetAsDouble();
    const int nbcvID = sc.Input[7].GetInt();

    SCFloatArray askVolArr, bidVolArr, deltaArr, tradesArr;
    ReadSubgraph(sc, nbcvID, 5, askVolArr);   // Ask Volume = SG 5
    ReadSubgraph(sc, nbcvID, 6, bidVolArr);   // Bid Volume = SG 6
    ReadSubgraph(sc, nbcvID, 0, deltaArr);    // Delta = SG 0
    ReadSubgraph(sc, nbcvID, 11, tradesArr);  // Trades = SG 11

    if (ValidateStudyData(askVolArr, i) && ValidateStudyData(bidVolArr, i)) {
      const double askVolume = askVolArr[i];
      const double bidVolume = bidVolArr[i];
      const double delta = ValidateStudyData(deltaArr, i) ? deltaArr[i] : (askVolume - bidVolume);
      const double numberOfTrades = ValidateStudyData(tradesArr, i) ? tradesArr[i] : 0.0;
      const double total = askVolume + bidVolume;

      SCString j;
      j.Format("{\"t\":%.6f,\"sym\":\"%s\",\"type\":\"numbers_bars_calculated_values_graph4\",\"i\":%d,\"ask\":%.0f,\"bid\":%.0f,\"delta\":%.0f,\"trades\":%.0f,\"cumdelta\":0,\"total\":%.0f,\"source_graph\":%d,\"study_id\":%d}",
               t, sc.Symbol.GetChars(), i, askVolume, bidVolume, delta, numberOfTrades, total, sc.ChartNumber, nbcvID);
      WriteToSpecializedFile(sc.ChartNumber, "nbcv", j);
    }
  }

  // ---- Cumulative Delta Bars ----
  if (sc.Input[8].GetInt() != 0 && sc.ArraySize > 0) {
    const int i = sc.ArraySize - 1;
    const double t = sc.BaseDateTimeIn[i].GetAsDouble();
    const int cumDeltaID = sc.Input[9].GetInt();
    const int cumDeltaSG = 3; // SG3 = Close (Cumulative Delta)

    SCFloatArray cumDeltaArr;
    ReadSubgraph(sc, cumDeltaID, cumDeltaSG, cumDeltaArr);
    
    if (ValidateStudyData(cumDeltaArr, i)) {
      double cumulativeDelta = cumDeltaArr[i];

      SCString j;
      j.Format("{\"t\":%.6f,\"sym\":\"%s\",\"type\":\"cumulative_delta\",\"i\":%d,\"cumulative_delta\":%.0f,\"study_id\":%d,\"chart\":%d}",
               t, sc.Symbol.GetChars(), i, cumulativeDelta, cumDeltaID, sc.ChartNumber);
      WriteToSpecializedFile(sc.ChartNumber, "cumulative_delta", j);
    }
  }

  // ---- Correlation ES/NQ ----
  if (sc.Input[10].GetInt() != 0 && sc.ArraySize > 0) {
    const int i = sc.ArraySize - 1;
    const double t = sc.BaseDateTimeIn[i].GetAsDouble();
    const int correlationID = sc.Input[11].GetInt();
    const int correlationSG = 0; // SG0 = Correlation Coefficient

    SCFloatArray correlationArr;
    ReadSubgraph(sc, correlationID, correlationSG, correlationArr);
    
    if (ValidateStudyData(correlationArr, i)) {
      double correlation = correlationArr[i];
      double closeValue = sc.BaseDataIn[SC_LAST][i];

      SCString j;
      j.Format("{\"t\":%.6f,\"sym\":\"%s\",\"type\":\"correlation\",\"i\":%d,\"value\":%.6f,\"study_id\":%d,\"sg\":%d,\"chart\":%d,\"close\":%.6f,\"length\":20}",
               t, sc.Symbol.GetChars(), i, correlation, correlationID, correlationSG, sc.ChartNumber, closeValue);
      WriteToSpecializedFile(sc.ChartNumber, "correlation", j);
    }
  }

  // ========== ATR EXPORT ==========
  if (sc.Input[12].GetInt() != 0 && sc.ArraySize > 0) {
    const int i = sc.ArraySize - 1;
    const double t = sc.BaseDateTimeIn[i].GetAsDouble();
    
    const int atrStudyID = sc.Input[13].GetInt();
    const int atrSG = sc.Input[14].GetInt();
    
    if (atrStudyID > 0) {
      SCFloatArray atrData;
      ReadSubgraph(sc, atrStudyID, atrSG, atrData);
      
      if (ValidateStudyData(atrData, i)) {
        const double atr = atrData[i];
        SCString j;
        j.Format("{\"t\":%.6f,\"type\":\"atr\",\"i\":%d,\"atr\":%.6f,\"study\":%d,\"sg\":%d,\"chart\":%d}",
                 t, i, atr, atrStudyID, atrSG, sc.ChartNumber);
        WriteToSpecializedFile(sc.ChartNumber, "atr", j);
      }
    }
  }

  // ========== VVA PREVIOUS EXPORT ==========
  if (sc.Input[15].GetInt() != 0 && sc.ArraySize > 0) {
    const int i = sc.ArraySize - 1;
    const double t = sc.BaseDateTimeIn[i].GetAsDouble();
    
    const int vvaPrevStudyID = sc.Input[16].GetInt();
    const int ppocSG = sc.Input[17].GetInt();
    const int pvahSG = sc.Input[18].GetInt();
    const int pvalSG = sc.Input[19].GetInt();
    
    if (vvaPrevStudyID > 0) {
      SCFloatArray ppocData, pvahData, pvalData;
      ReadSubgraph(sc, vvaPrevStudyID, ppocSG, ppocData);
      ReadSubgraph(sc, vvaPrevStudyID, pvahSG, pvahData);
      ReadSubgraph(sc, vvaPrevStudyID, pvalSG, pvalData);
      
      if (ValidateStudyData(ppocData, i) && ValidateStudyData(pvahData, i) && ValidateStudyData(pvalData, i)) {
        const double ppoc = ppocData[i];
        const double pvah = pvahData[i];
        const double pval = pvalData[i];
        
        SCString j;
        j.Format("{\"t\":%.6f,\"type\":\"vva_previous\",\"i\":%d,\"ppoc\":%.6f,\"pvah\":%.6f,\"pval\":%.6f,\"study\":%d,\"chart\":%d}",
                 t, i, ppoc, pvah, pval, vvaPrevStudyID, sc.ChartNumber);
        WriteToSpecializedFile(sc.ChartNumber, "vva_previous", j);
      }
    }
  }

  // ========== VOLUME PROFILE EXPORT (VPOC/VAH/VAL + HVN/LVN) ==========
  if (sc.Input[20].GetInt() != 0 && sc.ArraySize > 0) {
    const int i = sc.ArraySize - 1;
    const double t = sc.BaseDateTimeIn[i].GetAsDouble();
    
    const int vpStudyID = sc.Input[21].GetInt();
    
    if (vpStudyID > 0) {
      // VPOC, VAH, VAL (si demandé)
      if (sc.Input[22].GetInt() != 0) {
        SCFloatArray vpocData, vahData, valData;
        ReadSubgraph(sc, vpStudyID, 1, vpocData);  // SG 1 = VPOC
        ReadSubgraph(sc, vpStudyID, 2, vahData);   // SG 2 = VAH
        ReadSubgraph(sc, vpStudyID, 3, valData);   // SG 3 = VAL
        
        if (ValidateStudyData(vpocData, i) && ValidateStudyData(vahData, i) && ValidateStudyData(valData, i)) {
          const double vpoc = vpocData[i];
          const double vah = vahData[i];
          const double val = valData[i];
          
          SCString j;
          j.Format("{\"t\":%.6f,\"type\":\"volume_profile\",\"i\":%d,\"vpoc\":%.6f,\"vah\":%.6f,\"val\":%.6f,\"study\":%d,\"chart\":%d}",
                   t, i, vpoc, vah, val, vpStudyID, sc.ChartNumber);
          WriteToSpecializedFile(sc.ChartNumber, "volume_profile", j);
        }
      }
      
      // HVN, LVN (si demandé)
      if (sc.Input[23].GetInt() != 0) {
        SCFloatArray hvnData, lvnData;
        ReadSubgraph(sc, vpStudyID, 17, hvnData);  // SG 17 = HVN
        ReadSubgraph(sc, vpStudyID, 18, lvnData);  // SG 18 = LVN
        
        if (ValidateStudyData(hvnData, i) && ValidateStudyData(lvnData, i)) {
          const double hvn = hvnData[i];
          const double lvn = lvnData[i];
          
          SCString j;
          j.Format("{\"t\":%.6f,\"type\":\"hvn_lvn\",\"i\":%d,\"hvn\":%.6f,\"lvn\":%.6f,\"study\":%d,\"chart\":%d}",
                   t, i, hvn, lvn, vpStudyID, sc.ChartNumber);
          WriteToSpecializedFile(sc.ChartNumber, "hvn_lvn", j);
        }
      }
    }
  }
}
