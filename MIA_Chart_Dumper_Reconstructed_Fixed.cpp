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

SCDLLName("MIA_Chart_Dumper_Patched_VIX_NBCV_Quotes_Corrected_Daily")

// Dumper complet : BaseData, DOM live, VAP, T&S, VWAP + VVA (Volume Value Area Lines) + PVWAP + VIX + NBCV Footprint + Quotes/Trades + Corrélation ES/NQ
// Collecte VAH/VAL/VPOC (courant) + PVAH/PVAL/PPOC (précédent) + PVWAP (VWAP période précédente) + VIX temps réel + NBCV OrderFlow + Time & Sales + Corrélation ES/NQ
// NBCV Mapping corrigé : SG6(Ask Vol), SG7(Bid Vol), SG1(Delta), SG12(Trades), Cumulative Delta Bars SG4

// ========== FONCTIONS UTILITAIRES ==========
static void EnsureOutDir() {
#ifdef _WIN32
  CreateDirectoryA("D:\\MIA_IA_system", NULL);
#endif
}

static SCString DailyFilenameForChart(int chartNumber) {
  time_t now = time(NULL);
  struct tm* lt = localtime(&now);
  int y = lt ? (lt->tm_year + 1900) : 1970;
  int m = lt ? (lt->tm_mon + 1) : 1;
  int d = lt ? lt->tm_mday : 1;
  SCString filename;
  filename.Format("D:\\MIA_IA_system\\chart_%d_%04d%02d%02d.jsonl", chartNumber, y, m, d);
  return filename;
}

static void WritePerChartDaily(int chartNumber, const SCString& line) {
  EnsureOutDir();
  const SCString filename = DailyFilenameForChart(chartNumber);
  FILE* f = fopen(filename.GetChars(), "a");
  if (f) { 
    fprintf(f, "%s\n", line.GetChars()); 
    fclose(f); 
  }
}

// Anti-duplication simple par (chart, key)
static void WritePerChartDailyIfChanged(int chartNumber, const std::string& key, const SCString& line) {
  static std::unordered_map<std::string, std::string> s_last_by_key;
  auto it = s_last_by_key.find(key);
  const std::string current = std::string(line.GetChars());
  if (it != s_last_by_key.end() && it->second == current) {
    return; // identique, on n'écrit pas
  }
  WritePerChartDaily(chartNumber, line);
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

// ========== FONCTION DÉTECTSEQUENCESUPPORT ==========
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

// ========== FONCTION PRINCIPALE ==========
SCSFExport scsf_MIA_Chart_Dumper_Patched_VIX_Daily(SCStudyInterfaceRef sc)
{
  if (sc.SetDefaults)
  {
    sc.GraphName = "MIA Chart Dumper (Patched + VIX + NBCV + Quotes + Corrected Daily)";
    sc.AutoLoop = 0;
    sc.UpdateAlways = 1;
    sc.UsesMarketDepthData = 1;
    sc.MaintainVolumeAtPriceData = 1;
    sc.MaintainAdditionalChartDataArrays = 1;
    sc.CalculationPrecedence = LOW_PREC_LEVEL; // important: calc VWAP avant notre étude

    // --- Inputs BaseData + DOM + VAP + T&S ---
    sc.Input[0].Name = "Max DOM Levels";
    sc.Input[0].SetInt(20);
    sc.Input[1].Name = "Max VAP Elements (DISABLED)";
    sc.Input[1].SetInt(0);
    sc.Input[2].Name = "Max T&S Entries";
    sc.Input[2].SetInt(10);

    // --- Inputs VWAP ---
    sc.Input[3].Name = "Export VWAP From Study (0/1)";
    sc.Input[3].SetInt(1); // 1 = on
    sc.Input[4].Name = "VWAP Study ID (0=auto)";
    sc.Input[4].SetInt(0); // Auto-résolution par nom (recommandé)
    sc.Input[5].Name = "Export VWAP Bands Count (0..4)";
    sc.Input[5].SetInt(4); // Default to 4 bands (SD+1, SD-1, SD+2, SD-2)
    // Mapping explicite des SG VWAP (aligné sur template: VWAP=SG1, SD+1=SG2, SD-1=SG3, etc.)
    sc.Input[39].Name = "VWAP SG - Main";      sc.Input[39].SetInt(1);  // SG1 = VWAP principal
    sc.Input[40].Name = "VWAP SG - UP1";       sc.Input[40].SetInt(2);  // SG2 = SD+1 Top Band 1
    sc.Input[41].Name = "VWAP SG - DN1";       sc.Input[41].SetInt(3);  // SG3 = SD-1 Bottom Band 1
    sc.Input[42].Name = "VWAP SG - UP2";       sc.Input[42].SetInt(4);  // SG4 = SD+2 Top Band 2
    sc.Input[43].Name = "VWAP SG - DN2";       sc.Input[43].SetInt(5);  // SG5 = SD-2 Bottom Band 2
    sc.Input[44].Name = "VWAP SG - UP3";       sc.Input[44].SetInt(6);  // SG6 = SD+3 Top Band 3
    sc.Input[45].Name = "VWAP SG - DN3";       sc.Input[45].SetInt(7);  // SG7 = SD-3 Bottom Band 3

    // --- Inputs VVA (Volume Value Area Lines) ---
    sc.Input[6].Name = "Export Value Area Lines (0/1)";
    sc.Input[6].SetInt(1);
    sc.Input[7].Name = "VVA Current Study ID (0=off)";
    sc.Input[7].SetInt(9);   // ID:9 = Volume Profile courant (comme ancien fichier)
    sc.Input[8].Name = "VVA Previous Study ID (0=off)";
    sc.Input[8].SetInt(8);   // ID:8 = Volume Profile précédent (comme ancien fichier)
    sc.Input[9].Name = "Emit VVA On New Bar Only (0/1)";
    sc.Input[9].SetInt(1);   // évite les doublons
    sc.Input[10].Name = "Apply Price Multiplier to VVA (0/1)";
    sc.Input[10].SetInt(1);  // normalisation des prix

    // --- Inputs PVWAP (Previous VWAP) ---
    sc.Input[11].Name = "Export Previous VWAP (0/1)";
    sc.Input[11].SetInt(1);
    sc.Input[12].Name = "PVWAP Bands Count (0..4)";
    sc.Input[12].SetInt(2);  // ±0.5σ et ±1.0σ par défaut
    sc.Input[13].Name = "PVWAP On New Bar Only (0/1)";
    sc.Input[13].SetInt(1);  // évite les doublons

    // --- Inputs VIX ---
    sc.Input[14].Name = "Export VIX (0/1)";
    sc.Input[14].SetInt(1);  // 1 = on
    sc.Input[15].Name = "VIX Source Mode (0=Chart, 1=Study)";
    sc.Input[15].SetInt(1);  // 0 = Chart direct, 1 = Study Overlay
    sc.Input[16].Name = "VIX Chart Number";
    sc.Input[16].SetInt(8);  // ex: VIX_CGI #8
    sc.Input[17].Name = "VIX Study ID (Overlay)";
    sc.Input[17].SetInt(23); // ex: Study/Price Overlay ID:23
    sc.Input[18].Name = "VIX Subgraph Index (SG#)";
    sc.Input[18].SetInt(4);  // SG4 = Last (d'après vos captures)

    // --- Inputs NBCV Footprint ---
    sc.Input[19].Name = "Collect NBCV Footprint";
    sc.Input[19].SetYesNo(true);

    sc.Input[20].Name = "NBCV Study ID (0=auto)";
    sc.Input[20].SetInt(33);  // ID 33 confirmé sur Graph 3

    // Alternative: Cumulative Delta Bars Study ID
    sc.Input[26].Name = "Cumulative Delta Bars Study ID (0=auto)";
    sc.Input[26].SetInt(6);  // ID 6 confirmé sur Graph 4

    // Mapping Subgraphs (corrigé selon vraie signification: SG6/7/1/12/10)
    sc.Input[21].Name = "NBCV SG - Ask Volume Total";
    sc.Input[21].SetInt(6);  // SG6 - Ask Volume Total

    sc.Input[22].Name = "NBCV SG - Bid Volume Total";
    sc.Input[22].SetInt(7);  // SG7 - Bid Volume Total

    sc.Input[23].Name = "NBCV SG - Delta (Ask-Bid)";
    sc.Input[23].SetInt(1);  // SG1 - Ask Volume Bid Volume Difference

    sc.Input[24].Name = "NBCV SG - Number of Trades";
    sc.Input[24].SetInt(12); // SG12 - Number of Trades

    sc.Input[25].Name = "NBCV SG - Cumulative Sum Of Ask Volume Bid Volume Difference - Day";
    sc.Input[25].SetInt(10); // SG10 - Cumulative Sum Of Ask Volume Bid Volume Difference - Day

    // Option: n'écrire que sur nouvelle barre
    sc.Input[27].Name = "NBCV On New Bar Only (0/1)";
    sc.Input[27].SetInt(1);

    // --- Inputs Time & Sales / Quotes ---
    sc.Input[28].Name = "Collect Time & Sales";
    sc.Input[28].SetYesNo(true);

    sc.Input[29].Name = "Collect Quotes (Bid/Ask)";
    sc.Input[29].SetYesNo(true);

    sc.Input[30].Name = "T&S On New Bar Only (0/1)";
    sc.Input[30].SetInt(1);

    // --- Inputs MenthorQ (Chart 10) ---
    sc.Input[31].Name = "Export MenthorQ Levels (0/1)";
    sc.Input[31].SetInt(1);
    sc.Input[32].Name = "MenthorQ Chart Number";
    sc.Input[32].SetInt(10);
    sc.Input[33].Name = "Gamma Levels Study ID (0=off)";
    sc.Input[33].SetInt(1);
    sc.Input[34].Name = "Gamma Levels Subgraphs Count";
    sc.Input[34].SetInt(19);
    sc.Input[35].Name = "Blind Spots Study ID (0=off)";
    sc.Input[35].SetInt(3);
    sc.Input[36].Name = "Blind Spots Subgraphs Count";
    sc.Input[36].SetInt(9);
    sc.Input[37].Name = "Swing Levels Study ID (0=off)";
    sc.Input[37].SetInt(2);
    sc.Input[38].Name = "Swing Levels Subgraphs Count";
    sc.Input[38].SetInt(9);
    sc.Input[47].Name = "MenthorQ On New Bar Only (0/1)";
    sc.Input[47].SetInt(1);

    // --- Inputs Corrélation ES/NQ ---
    sc.Input[46].Name = "Correlation Coefficient Study ID (0=off)";
    sc.Input[46].SetInt(15);  // ID 15 pour Graph 4

    return;
  }

  if (sc.ServerConnectionState != SCS_CONNECTED) return;

  const int max_levels = sc.Input[0].GetInt();
  const int max_vap = sc.Input[1].GetInt();
  const int max_ts = sc.Input[2].GetInt();

  // ========== HELPER VIX ==========
  auto read_vix_from_chart = [&](int vixChart, const SCDateTime& ts) -> double {
    SCGraphData gd;
    sc.GetChartBaseData(vixChart, gd);
    int sz = gd[SC_LAST].GetArraySize();
    if (sz <= 0) return 0.0;
    int vi = sc.GetContainingIndexForSCDateTime(vixChart, ts);
    if (vi < 0 || vi >= sz) vi = sz - 1;
    return gd[SC_LAST][vi];
  };

  auto read_vix_from_study = [&](int studyId, int sgIndex, int iDest) -> double {
    SCFloatArray arr;
    const int vixChart = sc.Input[16].GetInt(); // Chart 8
    if (sc.GetStudyArrayFromChartUsingID(vixChart, studyId, sgIndex, arr) == 0) return 0.0;
    if (iDest < 0 || iDest >= arr.GetArraySize()) return 0.0;
    return arr[iDest];
  };

  // ========== VARIABLES STATIQUES ANTI-DOUBLONS T&S ==========
  static int      g_LastTsIndex = 0;     // curseur d'index
  static uint32_t g_LastSeq     = 0;     // dernier sequence traité
  static bool     g_UseSeq      = false; // on préfère Sequence si dispo

  // ========== TRAITEMENT D'UN ENREGISTREMENT T&S ==========
  auto ProcessTS = [&](const s_TimeAndSales& ts) -> void
  {
      const double tsec = ts.DateTime.GetAsDouble();
      const char* kind = (ts.Type == SC_TS_BID) ? "BID" :
                         (ts.Type == SC_TS_ASK) ? "ASK" :
                         (ts.Type == SC_TS_BIDASKVALUES) ? "BIDASK" : "TRADE";

      if (ts.Type == SC_TS_BID || ts.Type == SC_TS_ASK || ts.Type == SC_TS_BIDASKVALUES)
      {
          // QUOTE
          if (ts.Bid > 0 && ts.Ask > 0)
          {
              const double bid = NormalizePx(sc, ts.Bid);
              const double ask = NormalizePx(sc, ts.Ask);
              SCString j;
              j.Format(R"({"t":%.6f,"sym":"%s","type":"quote","kind":"%s","bid":%.8f,"ask":%.8f,"bq":%d,"aq":%d,"seq":%u,"chart":%d})",
                       tsec, sc.Symbol.GetChars(), kind, bid, ask, ts.BidSize, ts.AskSize, ts.Sequence, sc.ChartNumber);
              WritePerChartDaily(sc.ChartNumber, j);
          }
      }
      else
      {
          // TRADE (fallback = tout ce qui n'est pas BID/ASK)
          if (ts.Price > 0 && ts.Volume > 0)
          {
              const double px = NormalizePx(sc, ts.Price);
              SCString j;
              j.Format(R"({"t":%.6f,"sym":"%s","type":"trade","px":%.8f,"vol":%d,"seq":%u,"chart":%d})",
                       tsec, sc.Symbol.GetChars(), px, ts.Volume, ts.Sequence, sc.ChartNumber);
              WritePerChartDaily(sc.ChartNumber, j);
          }
      }
  };

  // ---- BaseData (chaque tick) ----
  if (sc.ArraySize > 0) {
    const int i = sc.ArraySize - 1;
    const double t = sc.BaseDateTimeIn[i].GetAsDouble();
    const double o = sc.BaseDataIn[SC_OPEN][i];
    const double h = sc.BaseDataIn[SC_HIGH][i];
    const double l = sc.BaseDataIn[SC_LOW][i];
    const double c = sc.BaseDataIn[SC_LAST][i];
    const double v = sc.BaseDataIn[SC_VOLUME][i];
    const double bvol = sc.BaseDataIn[SC_BIDVOL][i];
    const double avol = sc.BaseDataIn[SC_ASKVOL][i];

    SCString j;
    j.Format("{\"t\":%.6f,\"sym\":\"%s\",\"type\":\"basedata\",\"i\":%d,\"o\":%.8f,\"h\":%.8f,\"l\":%.8f,\"c\":%.8f,\"v\":%.0f,\"bidvol\":%.0f,\"askvol\":%.0f,\"chart\":%d}",
      t, sc.Symbol.GetChars(), i, o, h, l, c, v, bvol, avol, sc.ChartNumber);
    WritePerChartDaily(sc.ChartNumber, j);
  }

  // ---- VWAP export (chaque tick) ----
  if (sc.Input[3].GetInt() != 0 && sc.ArraySize > 0) {
    static int vwapID = -2; // -2: à résoudre, -1: introuvable, >0: OK
    const int i = sc.ArraySize - 1;
    const double t = sc.BaseDateTimeIn[i].GetAsDouble();
  
      if (vwapID == -2) {
        int cand[3];
        cand[0] = sc.Input[4].GetInt(); // ID forcé
        cand[1] = sc.GetStudyIDByName(sc.ChartNumber, "Volume Weighted Average Price", 0);
        cand[2] = sc.GetStudyIDByName(sc.ChartNumber, "VWAP (Volume Weighted Average Price)", 0);
  
        vwapID = -1;
        for (int k = 0; k < 3; ++k) {
          if (cand[k] > 0) {
            SCFloatArray test;
            const int sgMain = sc.Input[39].GetInt();
            if (sgMain >= 0) {
              sc.GetStudyArrayUsingID(cand[k], sgMain, test);
              if (test.GetArraySize() > i && test[i] != 0) { vwapID = cand[k]; break; }
            }
          }
        }
        // Diagnostic uniquement à la première résolution
        SCString d; d.Format("{\"t\":%.6f,\"type\":\"vwap_diag\",\"resolved_id\":%d,\"chart\":%d}", t, vwapID, sc.ChartNumber);
        WritePerChartDaily(sc.ChartNumber, d);
      }
  
      if (vwapID > 0) {
        SCFloatArray VWAP, UP1, DN1, UP2, DN2, UP3, DN3;
        const int sgMain = sc.Input[39].GetInt();
        const int sgUp1  = sc.Input[40].GetInt();
        const int sgDn1  = sc.Input[41].GetInt();
        const int sgUp2  = sc.Input[42].GetInt();
        const int sgDn2  = sc.Input[43].GetInt();
        const int sgUp3  = sc.Input[44].GetInt();
        const int sgDn3  = sc.Input[45].GetInt();
        if (sgMain >= 0) sc.GetStudyArrayUsingID(vwapID, sgMain, VWAP);
        int bands = sc.Input[5].GetInt();
        if (bands >= 1) {
          if (sgUp1 >= 0) sc.GetStudyArrayUsingID(vwapID, sgUp1, UP1);
          if (sgDn1 >= 0) sc.GetStudyArrayUsingID(vwapID, sgDn1, DN1);
        }
        if (bands >= 2) {
          if (sgUp2 >= 0) sc.GetStudyArrayUsingID(vwapID, sgUp2, UP2);
          if (sgDn2 >= 0) sc.GetStudyArrayUsingID(vwapID, sgDn2, DN2);
        }
        if (bands >= 3) {
          if (sgUp3 >= 0) sc.GetStudyArrayUsingID(vwapID, sgUp3, UP3);
          if (sgDn3 >= 0) sc.GetStudyArrayUsingID(vwapID, sgDn3, DN3);
        }

        if (VWAP.GetArraySize() > i && VWAP[i] != 0.0) {
          double v   = NormalizePx(sc, VWAP[i]);
          double up1 = (UP1.GetArraySize() > i ? NormalizePx(sc, UP1[i]) : 0);
          double dn1 = (DN1.GetArraySize() > i ? NormalizePx(sc, DN1[i]) : 0);
          double up2 = (UP2.GetArraySize() > i ? NormalizePx(sc, UP2[i]) : 0);
          double dn2 = (DN2.GetArraySize() > i ? NormalizePx(sc, DN2[i]) : 0);
          double up3 = (UP3.GetArraySize() > i ? NormalizePx(sc, UP3[i]) : 0);
          double dn3 = (DN3.GetArraySize() > i ? NormalizePx(sc, DN3[i]) : 0);
          // Normalisation: s'assurer que up* est au-dessus de v et dn* en-dessous
          if (up1 < v && dn1 > v)
          {
            double tmp;
            tmp = up1; up1 = dn1; dn1 = tmp;
            tmp = up2; up2 = dn2; dn2 = tmp;
            tmp = up3; up3 = dn3; dn3 = tmp;
          }

          SCString j;
          j.Format("{\"t\":%.6f,\"sym\":\"%s\",\"type\":\"vwap\",\"src\":\"study\",\"i\":%d,\"v\":%.8f,\"up1\":%.8f,\"dn1\":%.8f,\"up2\":%.8f,\"dn2\":%.8f,\"up3\":%.8f,\"dn3\":%.8f,\"chart\":%d}",
                   t, sc.Symbol.GetChars(), i, v, up1, dn1, up2, dn2, up3, dn3, sc.ChartNumber);
          WritePerChartDaily(sc.ChartNumber, j);
        } else {
          SCString d; d.Format("{\"t\":%.6f,\"type\":\"vwap_diag\",\"msg\":\"main_sg_empty\",\"id\":%d,\"sgMain\":%d,\"i\":%d,\"chart\":%d}",
                               t, vwapID, sgMain, i, sc.ChartNumber);
          WritePerChartDaily(sc.ChartNumber, d);
        }
      } else {
        SCString d; d.Format("{\"t\":%.6f,\"type\":\"vwap_diag\",\"msg\":\"study_not_found\",\"chart\":%d}", t, sc.ChartNumber);
        WritePerChartDaily(sc.ChartNumber, d);
      }
  }

  // ========== VVA (VAH/VAL/VPOC + PVAH/PVAL/PPOC) ==========
  if (sc.Input[6].GetInt() != 0 && sc.ArraySize > 0)
  {
    const int i = sc.ArraySize - 1;

      const int id_curr = sc.Input[7].GetInt(); // ID:1 (Current)
      const int id_prev = sc.Input[8].GetInt(); // ID:2 (Previous)

      auto read_vva = [&](int id, double& vah, double& val, double& vpoc)
      {
        vah = val = vpoc = 0.0;
        if (id <= 0) return;

        SCFloatArray SG1, SG2, SG3;  // 1=POC, 2=VAH, 3=VAL
        sc.GetStudyArrayUsingID(id, 1, SG1);
        sc.GetStudyArrayUsingID(id, 2, SG2);
        sc.GetStudyArrayUsingID(id, 3, SG3);

        if (SG1.GetArraySize() > i) vpoc = NormalizePx(sc, SG1[i]);
        if (SG2.GetArraySize() > i) vah  = NormalizePx(sc, SG2[i]);
        if (SG3.GetArraySize() > i) val  = NormalizePx(sc, SG3[i]);
      };

      double vah=0,val=0,vpoc=0, pvah=0,pval=0,ppoc=0;
      read_vva(id_curr, vah, val, vpoc);
      read_vva(id_prev, pvah, pval, ppoc);

      // Re-order de sécurité: garantir VAL <= VAH
      if (val > vah && vah > 0.0 && val > 0.0) {
        double tmp = vah; vah = val; val = tmp;
      }

      SCString j;
      j.Format("{\"t\":%.6f,\"sym\":\"%s\",\"type\":\"vva\",\"i\":%d,"
               "\"vah\":%.8f,\"val\":%.8f,\"vpoc\":%.8f,"
               "\"pvah\":%.8f,\"pval\":%.8f,\"ppoc\":%.8f,"
               "\"id_curr\":%d,\"id_prev\":%d,\"chart\":%d}",
               sc.BaseDateTimeIn[i].GetAsDouble(), sc.Symbol.GetChars(), i,
               vah, val, vpoc, pvah, pval, ppoc, id_curr, id_prev, sc.ChartNumber);
      WritePerChartDaily(sc.ChartNumber, j);
  }

  // ========== PVWAP (Previous VWAP - VWAP de la période précédente) ==========
  if (sc.Input[11].GetInt() != 0 && sc.ArraySize > 0 && sc.VolumeAtPriceForBars)
  {
    const int last = sc.ArraySize - 1;
    static int last_pvwap_bar = -1;
    const bool newbar_only = sc.Input[13].GetInt() != 0;

    if (!newbar_only || last != last_pvwap_bar)
    {
      last_pvwap_bar = last;

      // 1) Trouver le début de la session du jour (currStart) :
      int currStart = last;
      while (currStart > 0 && !sc.IsNewTradingDay(currStart)) currStart--;

      // Si pas assez d'historique, on sort
      if (currStart <= 0) { 
        // Diagnostic si pas de session précédente
        SCString d; d.Format("{\"t\":%.6f,\"type\":\"pvwap_diag\",\"msg\":\"insufficient_history\",\"currStart\":%d,\"chart\":%d}", 
                             sc.BaseDateTimeIn[last].GetAsDouble(), currStart, sc.ChartNumber);
        WritePerChartDaily(sc.ChartNumber, d);
      }
      else {
        // 2) La veille = [prevStart .. currStart-1]
        int prevEnd = currStart - 1;
        int prevStart = prevEnd;
        while (prevStart > 0 && !sc.IsNewTradingDay(prevStart)) prevStart--;

        // 3) Accumuler VAP sur la veille
        double sumV  = 0.0;
        double sumPV = 0.0;
        double sumP2V = 0.0;

        for (int b = prevStart; b <= prevEnd; ++b) {
          int N = sc.VolumeAtPriceForBars->GetSizeAtBarIndex(b);
          for (int k = 0; k < N; ++k) {
            const s_VolumeAtPriceV2* v = nullptr;
            if (sc.VolumeAtPriceForBars->GetVAPElementAtIndex(b, k, &v) && v) {
              // Utiliser le bon nom de membre pour le prix (peut varier selon la version de Sierra Chart)
              double p = 0.0;
              // Essayer différents noms de membres possibles
              #ifdef SC_VAP_PRICE
                p = NormalizePx(sc, v->Price);
              #elif defined(SC_VAP_PRICE_IN_TICKS)
                p = NormalizePx(sc, v->PriceInTicks * sc.TickSize);
              #else
                // Fallback : utiliser le prix calculé à partir de l'index de barre
                p = NormalizePx(sc, sc.BaseDataIn[SC_LAST][b]);
              #endif
              
              double vol = (double)v->Volume;
              sumV   += vol;
              sumPV  += p * vol;
              sumP2V += p * p * vol;
            }
          }
        }

        if (sumV > 0.0) {
          double pvwap = sumPV / sumV;
          
          // Normaliser l'échelle au Close du bar courant
          double close_ref = sc.BaseDataIn[SC_LAST][last];
          auto norm=[&](double& x){
            if (close_ref>1000 && x>0 && x<100) x*=100.0;
            else if (close_ref<100 && x>1000)   x/=100.0;
          };
          norm(pvwap);

          // 4) Bandes ±kσ autour du PVWAP
          int nb = sc.Input[12].GetInt();
          double var = (sumP2V / sumV) - (pvwap * pvwap);
          if (var < 0) var = 0;
          double sigma = sqrt(var);
          norm(sigma); // si l'échelle VAP diffère

          double up1=0, dn1=0, up2=0, dn2=0, up3=0, dn3=0, up4=0, dn4=0;
          if (nb >= 1) { up1 = pvwap + 0.5 * sigma; dn1 = pvwap - 0.5 * sigma; }
          if (nb >= 2) { up2 = pvwap + 1.0 * sigma; dn2 = pvwap - 1.0 * sigma; }
          if (nb >= 3) { up3 = pvwap + 1.5 * sigma; dn3 = pvwap - 1.5 * sigma; }
          if (nb >= 4) { up4 = pvwap + 2.0 * sigma; dn4 = pvwap - 2.0 * sigma; }

          // 5) Écriture JSON
          SCString j;
          j.Format("{\"t\":%.6f,\"sym\":\"%s\",\"type\":\"pvwap\",\"i\":%d,\"prev_start\":%d,\"prev_end\":%d,"
                   "\"pvwap\":%.8f,\"up1\":%.8f,\"dn1\":%.8f,\"up2\":%.8f,\"dn2\":%.8f,"
                   "\"up3\":%.8f,\"dn3\":%.8f,\"up4\":%.8f,\"dn4\":%.8f,\"chart\":%d}",
                   sc.BaseDateTimeIn[last].GetAsDouble(), sc.Symbol.GetChars(), last,
                   prevStart, prevEnd,
                   pvwap, up1, dn1, up2, dn2, up3, dn3, up4, dn4, sc.ChartNumber);
          WritePerChartDaily(sc.ChartNumber, j);
        } else {
          // Diagnostic si pas de volume sur la veille
          SCString d; d.Format("{\"t\":%.6f,\"type\":\"pvwap_diag\",\"msg\":\"no_volume_prev_session\",\"prevStart\":%d,\"prevEnd\":%d,\"chart\":%d}", 
                               sc.BaseDateTimeIn[last].GetAsDouble(), prevStart, prevEnd, sc.ChartNumber);
          WritePerChartDaily(sc.ChartNumber, d);
        }
      }
    }
  }

  // ========== GRAPH 4 (M30) CROSS-CHART EXPORT ==========
  if (sc.ArraySize > 0)
  {
    const int i_src = sc.ArraySize - 1;
    const SCDateTime t_src = sc.BaseDateTimeIn[i_src];
    const int g4 = 4; // Graph 4

    SCGraphData gd4;
    sc.GetChartBaseData(g4, gd4);
    const int sz4 = gd4[SC_LAST].GetArraySize();
    if (sz4 > 0)
    {
      int i4 = sc.GetContainingIndexForSCDateTime(g4, t_src);
      if (i4 < 0 || i4 >= sz4) i4 = sz4 - 1;

      // ---- G4 basedata (OHLC/Volume) ----
      {
        const double t = t_src.GetAsDouble();
        const double o = gd4[SC_OPEN][i4];
        const double h = gd4[SC_HIGH][i4];
        const double l = gd4[SC_LOW][i4];
        const double c = gd4[SC_LAST][i4];
        const double v = gd4[SC_VOLUME][i4];
        SCString j;
        j.Format("{\"t\":%.6f,\"sym\":\"%s\",\"type\":\"basedata\",\"i\":%d,\"o\":%.8f,\"h\":%.8f,\"l\":%.8f,\"c\":%.8f,\"v\":%.0f,\"chart\":%d}",
                 t, sc.Symbol.GetChars(), i4, o, h, l, c, v, g4);
        WritePerChartDailyIfChanged(g4, SCString().Format("%d:basedata:%d", g4, i4).GetChars(), j);
      }

      // ---- G4 VWAP courant (mapping SG configurable) ----
      {
        // Résoudre un VWAP sur G4 par nom
        int vwapId4 = sc.GetStudyIDByName(g4, "Volume Weighted Average Price", 0);
        if (vwapId4 <= 0)
          vwapId4 = sc.GetStudyIDByName(g4, "VWAP (Volume Weighted Average Price)", 0);

        if (vwapId4 > 0)
        {
          SCFloatArray VWAP4, UP1, DN1, UP2, DN2, UP3, DN3;
          const int sgMain = sc.Input[39].GetInt();
          const int sgUp1  = sc.Input[40].GetInt();
          const int sgDn1  = sc.Input[41].GetInt();
          const int sgUp2  = sc.Input[42].GetInt();
          const int sgDn2  = sc.Input[43].GetInt();
          const int sgUp3  = sc.Input[44].GetInt();
          const int sgDn3  = sc.Input[45].GetInt();
          if (sgMain >= 0) sc.GetStudyArrayFromChartUsingID(g4, vwapId4, sgMain, VWAP4);
          int bands = sc.Input[5].GetInt();
          if (bands >= 1) { if (sgUp1 >= 0) sc.GetStudyArrayFromChartUsingID(g4, vwapId4, sgUp1, UP1); if (sgDn1 >= 0) sc.GetStudyArrayFromChartUsingID(g4, vwapId4, sgDn1, DN1); }
          if (bands >= 2) { if (sgUp2 >= 0) sc.GetStudyArrayFromChartUsingID(g4, vwapId4, sgUp2, UP2); if (sgDn2 >= 0) sc.GetStudyArrayFromChartUsingID(g4, vwapId4, sgDn2, DN2); }
          if (bands >= 3) { if (sgUp3 >= 0) sc.GetStudyArrayFromChartUsingID(g4, vwapId4, sgUp3, UP3); if (sgDn3 >= 0) sc.GetStudyArrayFromChartUsingID(g4, vwapId4, sgDn3, DN3); }

          if (VWAP4.GetArraySize() > i4 && VWAP4[i4] != 0.0)
          {
            double v   = NormalizePx(sc, VWAP4[i4]);
            double up1 = (UP1.GetArraySize() > i4 ? NormalizePx(sc, UP1[i4]) : 0);
            double dn1 = (DN1.GetArraySize() > i4 ? NormalizePx(sc, DN1[i4]) : 0);
            double up2 = (UP2.GetArraySize() > i4 ? NormalizePx(sc, UP2[i4]) : 0);
            double dn2 = (DN2.GetArraySize() > i4 ? NormalizePx(sc, DN2[i4]) : 0);
            double up3 = (UP3.GetArraySize() > i4 ? NormalizePx(sc, UP3[i4]) : 0);
            double dn3 = (DN3.GetArraySize() > i4 ? NormalizePx(sc, DN3[i4]) : 0);
            // Normalisation: s'assurer que up* est au-dessus de v et dn* en-dessous
            if (up1 < v && dn1 > v)
            {
              double tmp;
              tmp = up1; up1 = dn1; dn1 = tmp;
              tmp = up2; up2 = dn2; dn2 = tmp;
              tmp = up3; up3 = dn3; dn3 = tmp;
            }
            SCString j;
            j.Format("{\"t\":%.6f,\"sym\":\"%s\",\"type\":\"vwap\",\"src\":\"study\",\"i\":%d,\"v\":%.8f,\"up1\":%.8f,\"dn1\":%.8f,\"up2\":%.8f,\"dn2\":%.8f,\"up3\":%.8f,\"dn3\":%.8f,\"chart\":%d}",
                     t_src.GetAsDouble(), sc.Symbol.GetChars(), i4, v, up1, dn1, up2, dn2, up3, dn3, g4);
            WritePerChartDailyIfChanged(g4, SCString().Format("%d:vwap:%d", g4, i4).GetChars(), j);
          }
          else
          {
            SCString d; d.Format("{\"t\":%.6f,\"type\":\"vwap_diag\",\"msg\":\"main_sg_empty\",\"id\":%d,\"sgMain\":%d,\"i\":%d,\"chart\":%d}",
                                 t_src.GetAsDouble(), vwapId4, sgMain, i4, g4);
            WritePerChartDailyIfChanged(g4, SCString().Format("%d:vwap_diag:%d", g4, i4).GetChars(), d);
          }
        }
        else
        {
          SCString d; d.Format("{\"t\":%.6f,\"type\":\"vwap_diag\",\"msg\":\"study_not_found\",\"chart\":%d}", t_src.GetAsDouble(), g4);
          WritePerChartDaily(g4, d);
        }
      }

      // ---- G4 PVWAP (Previous VWAP depuis étude ID 3, SG5) ----
      {
        const int pvwapId4 = 3; // ID 3 = PREVIOUS VWAP SD+1 SD-1
        const int pvwapSG4 = 5; // SG5 = PVWAP - Volume Weighted Average Price
        
        SCFloatArray PVWAP4;
        sc.GetStudyArrayFromChartUsingID(g4, pvwapId4, pvwapSG4, PVWAP4);
        
        if (PVWAP4.GetArraySize() > i4 && PVWAP4[i4] != 0.0) {
          double pvwap = NormalizePx(sc, PVWAP4[i4]);
          SCString j;
          j.Format("{\"t\":%.6f,\"sym\":\"%s\",\"type\":\"pvwap\",\"src\":\"study\",\"i\":%d,\"pvwap\":%.8f,\"chart\":%d}",
                   t_src.GetAsDouble(), sc.Symbol.GetChars(), i4, pvwap, g4);
          WritePerChartDailyIfChanged(g4, SCString().Format("%d:pvwap:%d", g4, i4).GetChars(), j);
        } else {
          SCString d; d.Format("{\"t\":%.6f,\"type\":\"pvwap_diag\",\"msg\":\"no_data\",\"id\":%d,\"sg\":%d,\"i\":%d,\"chart\":%d}", 
                               t_src.GetAsDouble(), pvwapId4, pvwapSG4, i4, g4);
          WritePerChartDailyIfChanged(g4, SCString().Format("%d:pvwap_diag:%d", g4, i4).GetChars(), d);
        }
      }

      // ---- G4 NBCV (Numbers Bars Calculated Values) ----
      {
        int nbcvId4 = sc.GetStudyIDByName(g4, "Numbers Bars Calculated Values", 1);
        if (nbcvId4 <= 0)
          nbcvId4 = sc.GetStudyIDByName(g4, "Numbers Bars Calculated Values", 0);
        if (nbcvId4 > 0)
        {
          static int s_logged_nbcv_bind_id4 = -1;
          if (s_logged_nbcv_bind_id4 != nbcvId4) {
            s_logged_nbcv_bind_id4 = nbcvId4;
            SCString b; b.Format(R"({"t":%.6f,"type":"nbcv_bind","chart":%d,"study_id":%d,"sg":{"ask":6,"bid":7,"delta":1,"trades":12,"cum":"study6_sg4_close"}})",
                                 t_src.GetAsDouble(), g4, nbcvId4);
            WritePerChartDaily(g4, b);
          }

          SCFloatArray askVolArr, bidVolArr, deltaArr, tradesArr, cumDeltaArr;
          sc.GetStudyArrayFromChartUsingID(g4, nbcvId4, 6, askVolArr);  // SG6 - Ask Volume Total
          sc.GetStudyArrayFromChartUsingID(g4, nbcvId4, 7, bidVolArr);  // SG7 - Bid Volume Total
          sc.GetStudyArrayFromChartUsingID(g4, nbcvId4, 1, deltaArr);   // SG1 - Ask Volume Bid Volume Difference
          sc.GetStudyArrayFromChartUsingID(g4, nbcvId4, 12, tradesArr); // SG12 - Number of Trades
          
          // Cumulative Delta depuis Cumulative Delta Bars (Study ID 6, SG4 Close)
          const int cumDeltaBarsId4 = sc.Input[26].GetInt();
          if (cumDeltaBarsId4 > 0) {
            sc.GetStudyArrayFromChartUsingID(g4, cumDeltaBarsId4, 4, cumDeltaArr); // Study ID 6, SG4 Close (Cumulative Delta)
          }

          auto has4 = [&](const SCFloatArray& a){ return a.GetArraySize() > i4; };
          if (has4(askVolArr) && has4(bidVolArr) && has4(deltaArr))
          {
            const double t = t_src.GetAsDouble();
            const double askVolume      = askVolArr[i4];
            const double bidVolume      = bidVolArr[i4];
            const double delta          = askVolume - bidVolume; // fiabilisé comme sur G3
            double numberOfTrades = has4(tradesArr)   ? tradesArr[i4]   : 0.0;

            // Fallback cumulatif si SG10 absent/invalide
            double cumulativeDelta = 0.0;
            bool cum_from_sg = false;
            if (has4(cumDeltaArr)) {
              cumulativeDelta = cumDeltaArr[i4];
              // SG10 peut retourner 0.0 même quand il fonctionne, donc on force le fallback si on est au début
              cum_from_sg = (i4 > 50 && cumulativeDelta != 0.0); // Force le fallback si SG10 retourne 0.0
            }
            if (!cum_from_sg) {
              static std::vector<double> s_cum_fallback4;
              if ((int)s_cum_fallback4.size() < sz4) s_cum_fallback4.resize(sz4, 0.0);
              if (i4 <= 0) s_cum_fallback4[i4] = delta; else s_cum_fallback4[i4] = s_cum_fallback4[i4 - 1] + delta;
              cumulativeDelta = s_cum_fallback4[i4];
            }
            const double totalVolume = askVolume + bidVolume;
            const double deltaRatio  = (totalVolume > 0.0) ? (delta / totalVolume) : 0.0;
            const double bidAskRatio = (askVolume > 0.0) ? (bidVolume / askVolume) : 0.0;
            const double askBidRatio = (bidVolume > 0.0) ? (askVolume / bidVolume) : 0.0;

            // Trades douteux: neutraliser si manquant ou ~égal au volume total
            if (!(has4(tradesArr)) || (totalVolume > 0.0 && fabs(numberOfTrades - totalVolume) / totalVolume < 0.02)) {
              numberOfTrades = 0.0;
            }

            {
              SCString j;
              j.Format(R"({"t":%.6f,"sym":"%s","type":"nbcv_footprint","i":%d,"ask_volume":%.0f,"bid_volume":%.0f,"delta":%.0f,"trades":%.0f,"cumulative_delta":%.0f,"total_volume":%.0f,"chart":%d})",
                       t, sc.Symbol.GetChars(), i4, askVolume, bidVolume, delta, numberOfTrades, cumulativeDelta, totalVolume, g4);
              WritePerChartDailyIfChanged(g4, SCString().Format("%d:nbcv_footprint:%d", g4, i4).GetChars(), j);
            }
            {
              // Calcul robuste des pressions avec seuils symétriques
              const double th_ratio = 0.60;   // seuil fort pour delta_ratio
              const double th_ratio_r = 2.00; // seuil fort pour x/y
              const double min_vol = 10.0;    // évite le bruit
              
              int pressure_bullish = 0;
              int pressure_bearish = 0;
              
              if (totalVolume >= min_vol) {
                const double delta_signed = askVolume - bidVolume;
                const double delta_ratio_signed = delta_signed / totalVolume;
                
                // Détection de pression mutuellement exclusive par le signe
                if (delta_signed > 0) { // côté acheteur
                  if (delta_ratio_signed >= th_ratio || askBidRatio >= th_ratio_r) {
                    pressure_bullish = 1;
                  }
                } else if (delta_signed < 0) { // côté vendeur
                  if (-delta_ratio_signed >= th_ratio || bidAskRatio >= th_ratio_r) {
                    pressure_bearish = 1;
                  }
                }
              }
              
              SCString j;
              j.Format(R"({"t":%.6f,"sym":"%s","type":"nbcv_metrics","i":%d,"delta_ratio":%.6f,"bid_ask_ratio":%.6f,"ask_bid_ratio":%.6f,"pressure_bullish":%d,"pressure_bearish":%d,"chart":%d})",
                       t, sc.Symbol.GetChars(), i4, deltaRatio, bidAskRatio, askBidRatio, pressure_bullish, pressure_bearish, g4);
              WritePerChartDailyIfChanged(g4, SCString().Format("%d:nbcv_metrics:%d", g4, i4).GetChars(), j);
            }
            {
              const double absorp = (totalVolume > 0.0 && fabs(delta) > 0.10 * totalVolume) ? 1.0 : 0.0;
              const double dtrend = (cumulativeDelta > 0.0) ? 1.0 : (cumulativeDelta < 0.0 ? -1.0 : 0.0);
              SCString j;
              j.Format(R"({"t":%.6f,"sym":"%s","type":"nbcv_orderflow","i":%d,"volume_imbalance":%.6f,"trade_intensity":%.6f,"delta_trend":%.0f,"absorption_pattern":%.0f,"chart":%d})",
                       t, sc.Symbol.GetChars(), i4,
                       (totalVolume > 0.0 ? (askVolume - bidVolume) / totalVolume : 0.0),
                       (totalVolume > 0.0 ? numberOfTrades / totalVolume : 0.0),
                       dtrend, absorp, g4);
              WritePerChartDailyIfChanged(g4, SCString().Format("%d:nbcv_orderflow:%d", g4, i4).GetChars(), j);
            }
          }
          else
          {
            SCString j; j.Format("{\"t\":%.6f,\"type\":\"nbcv_diag\",\"msg\":\"insufficient_data\",\"i\":%d,\"chart\":%d}", t_src.GetAsDouble(), i4, g4);
            WritePerChartDaily(g4, j);
          }
        }
        else
        {
          SCString j; j.Format("{\"t\":%.6f,\"type\":\"nbcv_diag\",\"msg\":\"study_not_found\",\"chart\":%d}", t_src.GetAsDouble(), g4);
          WritePerChartDaily(g4, j);
        }
      }

      // === CORRÉLATION ES/NQ (Graph 4) ===
      const int correlationId4 = sc.Input[46].GetInt();
      if (correlationId4 > 0) {
        SCFloatArray correlationArr;
        sc.GetStudyArrayFromChartUsingID(g4, correlationId4, 0, correlationArr); // SG0 CC (ACSIL indexe à 0)
        
        // Collecter le Close du chart 4 (pas du chart courant)
        double closeValue = gd4[SC_LAST][i4];
        
        if (correlationArr.GetArraySize() > 0) {
          // Utiliser l'index aligné (pas "dernier non nul")
          const int j = min(i4, correlationArr.GetArraySize() - 1);
          const double correlation = correlationArr[j];
          
          SCString log;
          log.Format("{\"t\":%.6f,\"sym\":\"%s\",\"type\":\"correlation\",\"i\":%d,\"value\":%.6f,\"study_id\":%d,\"sg\":0,\"chart\":%d,\"corr_index\":%d,\"close\":%.6f,\"length\":20,\"base_id\":\"ID0.SG4\",\"ref_id\":\"ID16.SG1\"}",
                    t_src.GetAsDouble(), sc.Symbol.GetChars(), i4, correlation, correlationId4, g4, j, closeValue);
          
          // Utiliser déduplication pour éviter le spam
          SCString key; key.Format("%d:correlation:%d", g4, i4);
          WritePerChartDailyIfChanged(g4, std::string(key.GetChars()), log);
        }
      }
    }
  }

  // ========== VIX COLLECTION ==========
  if (sc.Input[14].GetInt() != 0 && sc.ArraySize > 0) {
    const int i = sc.ArraySize - 1;
    const double t = sc.BaseDateTimeIn[i].GetAsDouble();
      double vix = 0.0;
      bool vix_found = false;

      if (sc.Input[15].GetInt() == 0) {
        // Mode Chart : lire depuis un autre chart
        const int vixChart = sc.Input[16].GetInt();
        if (vixChart > 0) {
          vix = read_vix_from_chart(vixChart, sc.BaseDateTimeIn[i]);
          vix_found = (vix > 0.0);
        }
      } else {
        // Mode Study : lire depuis une étude overlay
        const int vixStudy = sc.Input[17].GetInt();
        const int vixSG = sc.Input[18].GetInt();
        if (vixStudy > 0) {
          vix = read_vix_from_study(vixStudy, vixSG, i);
          vix_found = (vix > 0.0);
        }
      }

      SCString jv;
      if (vix_found) {
        // Option A: reporter le chart du collecteur (3)
        jv.Format(
          "{\"t\":%.6f,\"type\":\"vix\",\"i\":%d,\"last\":%.6f,\"mode\":%d,\"chart\":%d,\"study\":%d,\"sg\":%d}",
          t, i, vix,
          sc.Input[15].GetInt(),
          sc.ChartNumber,
          sc.Input[17].GetInt(),
          sc.Input[18].GetInt()
        );
      } else {
        jv.Format(
          "{\"t\":%.6f,\"type\":\"vix_diag\",\"i\":%d,\"msg\":\"no_data\","
          "\"mode\":%d,\"chart\":%d,\"study\":%d,\"sg\":%d}",
          t, i,
          sc.Input[15].GetInt(),
          sc.ChartNumber,
          sc.Input[17].GetInt(),
          sc.Input[18].GetInt()
        );
      }
      WritePerChartDaily(sc.ChartNumber, jv);
  }

  // ========== MENTHORQ (GAMMA/BLIND/SWING depuis Chart 10) ==========
  if (sc.Input[31].GetInt() != 0 && sc.ArraySize > 0)
  {
    const int i = sc.ArraySize - 1;
    const int mqChart = sc.Input[32].GetInt();
    const bool newbar_only_mq = sc.Input[47].GetInt() != 0;
    static SCDateTime s_last_mq_bar_time(0.0);

    const SCDateTime cur_time = sc.BaseDateTimeIn[i];
    if (!newbar_only_mq || cur_time != s_last_mq_bar_time)
    {
      s_last_mq_bar_time = cur_time;

      auto level_type_for = [&](int studyId, int sg) -> SCString {
        SCString s;
        if (studyId == sc.Input[33].GetInt()) { // Gamma Levels
          switch(sg) {
            case 1: s = "call_resistance"; break;
            case 2: s = "put_support"; break;
            case 3: s = "hvl"; break;
            case 4: s = "1d_min"; break;
            case 5: s = "1d_max"; break;
            case 6: s = "call_resistance_0dte"; break;
            case 7: s = "put_support_0dte"; break;
            case 8: s = "hvl_0dte"; break;
            case 9: s = "gamma_wall_0dte"; break;
            case 10: s = "gex_1"; break;
            case 11: s = "gex_2"; break;
            case 12: s = "gex_3"; break;
            case 13: s = "gex_4"; break;
            case 14: s = "gex_5"; break;
            case 15: s = "gex_6"; break;
            case 16: s = "gex_7"; break;
            case 17: s = "gex_8"; break;
            case 18: s = "gex_9"; break;
            case 19: s = "gex_10"; break;
            default: s.Format("gamma_sg_%d", sg); break;
          }
        } else if (studyId == sc.Input[35].GetInt()) { // Blind Spots
          s.Format("blind_spot_%d", sg);
        } else if (studyId == sc.Input[37].GetInt()) { // Swing Levels
          s.Format("swing_lvl_%d", sg);
        } else {
          s.Format("sg_%d", sg);
        }
        return s;
      };

      auto emit_levels = [&](int studyId, int sgCount)
      {
        if (studyId <= 0 || mqChart <= 0) return;
        int iDest = sc.GetContainingIndexForSCDateTime(mqChart, cur_time);
        if (iDest < 0) return;

        for (int sg = 1; sg <= sgCount; ++sg)
        {
          SCFloatArray arr;
          sc.GetStudyArrayFromChartUsingID(mqChart, studyId, sg, arr);
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
                     cur_time.GetAsDouble(), sc.Symbol.GetChars(), mqChart, levelType.GetChars(), p, sg, studyId, iOut, mqChart);
            WritePerChartDaily(mqChart, j);
          }
          else
          {
            SCString d; d.Format("{\"t\":%.6f,\"type\":\"menthorq_diag\",\"chart\":%d,\"study\":%d,\"sg\":%d,\"msg\":\"no_value\"}",
                                 cur_time.GetAsDouble(), mqChart, studyId, sg);
            WritePerChartDaily(mqChart, d);
          }
        }
      };

      emit_levels(sc.Input[33].GetInt(), sc.Input[34].GetInt());
      emit_levels(sc.Input[35].GetInt(), sc.Input[36].GetInt());
      emit_levels(sc.Input[37].GetInt(), sc.Input[38].GetInt());
    }
  }

  // ===== NBCV FOOTPRINT (Numbers Bars Calculated Values) =====
  static int s_last_nbcv_bar = -1;

  if (sc.Input[19].GetYesNo() && sc.ArraySize > 0)
  {
    const int i = sc.ArraySize - 1;
    const bool newbar_only = sc.Input[27].GetInt() != 0;
    
    if (newbar_only && i == s_last_nbcv_bar) {
      // Skip - same bar
    } else {
      s_last_nbcv_bar = i;
      
      // 1) Résoudre l'ID d'étude NBCV
      int nbcv_id = sc.Input[20].GetInt();
      if (nbcv_id <= 0) {
        nbcv_id = sc.GetStudyIDByName(sc.ChartNumber, "Numbers Bars Calculated Values", 1);
      }
      
      if (nbcv_id > 0) {
        // 2) Charger les subgraphs demandés
        SCFloatArray askVolArr, bidVolArr, deltaArr, tradesArr, cumDeltaArr;
        const int sgAsk   = sc.Input[21].GetInt();
        const int sgBid   = sc.Input[22].GetInt();
        const int sgDelta = sc.Input[23].GetInt();
        const int sgNtr   = sc.Input[24].GetInt();
        const int sgCum   = sc.Input[25].GetInt();

        sc.GetStudyArrayUsingID(nbcv_id, sgAsk,   askVolArr);
        sc.GetStudyArrayUsingID(nbcv_id, sgBid,   bidVolArr);
        sc.GetStudyArrayUsingID(nbcv_id, sgDelta, deltaArr);
        sc.GetStudyArrayUsingID(nbcv_id, sgNtr,   tradesArr);
        
        // Cumulative Delta depuis Cumulative Delta Bars (Study ID 33, SG4 Close) - Graph 3
        const int cumDeltaBarsId = 33; // ID 33 pour Graph 3
        if (cumDeltaBarsId > 0) {
          sc.GetStudyArrayUsingID(cumDeltaBarsId, 4, cumDeltaArr); // Study ID 33, SG4 Close (Cumulative Delta)
        }

        // Log du binding NBCV pour Graph 3
        static int s_logged_nbcv_bind_id3 = -1;
        if (s_logged_nbcv_bind_id3 != nbcv_id) {
          s_logged_nbcv_bind_id3 = nbcv_id;
          SCString b; b.Format(R"({"t":%.6f,"type":"nbcv_bind","chart":%d,"study_id":%d,"sg":{"ask":%d,"bid":%d,"delta":%d,"trades":%d,"cum":"study33_sg4_close"}})",
                               sc.CurrentSystemDateTime.GetAsDouble(), sc.ChartNumber, nbcv_id, sgAsk, sgBid, sgDelta, sgNtr);
          WritePerChartDaily(sc.ChartNumber, b);
        }

        // 3) Vérifier la dispo à l'index i
        auto has = [&](const SCFloatArray& a){ return a.GetArraySize() > i; };
        if (has(askVolArr) && has(bidVolArr)) {
          
          // 4) Valeurs
          const double t = sc.BaseDateTimeIn[i].GetAsDouble();
          const double askVolume      = askVolArr[i];
          const double bidVolume      = bidVolArr[i];
          // Delta fiable basé sur volumes: Ask - Bid (au lieu de SG1 parfois mal mappé)
          const double delta          = askVolume - bidVolume;
          double numberOfTrades = has(tradesArr)   ? tradesArr[i]   : 0.0;

          // Fallback cumulatif si SG10 absent/invalide (Graph 3)
          double cumulativeDelta = 0.0;
          bool cum_from_sg = false;
          if (has(cumDeltaArr)) {
            cumulativeDelta = cumDeltaArr[i];
            // SG10 peut retourner 0.0 même quand il fonctionne, donc on force le fallback si on est au début
              cum_from_sg = (i > 50 && cumulativeDelta != 0.0); // Force le fallback si SG10 retourne 0.0
          }
          if (!cum_from_sg) {
            static std::vector<double> s_cum_fallback3;
            if ((int)s_cum_fallback3.size() < sc.ArraySize) s_cum_fallback3.resize(sc.ArraySize, 0.0);
            if (i <= 0) s_cum_fallback3[i] = delta; else s_cum_fallback3[i] = s_cum_fallback3[i - 1] + delta;
            cumulativeDelta = s_cum_fallback3[i];
          }

          const double totalVolume = askVolume + bidVolume;
          const double deltaRatio  = (totalVolume > 0.0) ? (delta / totalVolume) : 0.0;
          const double bidAskRatio = (askVolume > 0.0) ? (bidVolume / askVolume) : 0.0;
          const double askBidRatio = (bidVolume > 0.0) ? (askVolume / bidVolume) : 0.0;

          // Trades douteux: neutraliser si manquant ou ~égal au volume total (Graph 3)
          if (!(has(tradesArr)) || (totalVolume > 0.0 && fabs(numberOfTrades - totalVolume) / totalVolume < 0.02)) {
            numberOfTrades = 0.0;
          }

          // 5) Exports
          {
            SCString j;
            j.Format(
              R"({"t":%.6f,"sym":"%s","type":"nbcv_footprint","i":%d,"ask_volume":%.0f,"bid_volume":%.0f,"delta":%.0f,"trades":%.0f,"cumulative_delta":%.0f,"total_volume":%.0f,"chart":%d})",
              t, sc.Symbol.GetChars(), i,
              askVolume, bidVolume, delta, numberOfTrades, cumulativeDelta, totalVolume, sc.ChartNumber
            );
            WritePerChartDaily(sc.ChartNumber, j);
          }
          {
            // Calcul robuste des pressions avec seuils symétriques
            const double th_ratio = 0.60;   // seuil fort pour delta_ratio
            const double th_ratio_r = 2.00; // seuil fort pour x/y
            const double min_vol = 10.0;    // évite le bruit
            
            int pressure_bullish = 0;
            int pressure_bearish = 0;
            
            if (totalVolume >= min_vol) {
              const double delta_signed = askVolume - bidVolume;
              const double delta_ratio_signed = delta_signed / totalVolume;
              
              // Détection de pression mutuellement exclusive par le signe
              if (delta_signed > 0) { // côté acheteur
                if (delta_ratio_signed >= th_ratio || askBidRatio >= th_ratio_r) {
                  pressure_bullish = 1;
                }
              } else if (delta_signed < 0) { // côté vendeur
                if (-delta_ratio_signed >= th_ratio || bidAskRatio >= th_ratio_r) {
                  pressure_bearish = 1;
                }
              }
            }
            
            SCString j;
            j.Format(
              R"({"t":%.6f,"sym":"%s","type":"nbcv_metrics","i":%d,"delta_ratio":%.6f,"bid_ask_ratio":%.6f,"ask_bid_ratio":%.6f,"pressure_bullish":%d,"pressure_bearish":%d,"chart":%d})",
              t, sc.Symbol.GetChars(), i,
              deltaRatio, bidAskRatio, askBidRatio,
              pressure_bullish, pressure_bearish,
              sc.ChartNumber
            );
            WritePerChartDaily(sc.ChartNumber, j);
          }
          {
            // seuil simple d'absorption : |delta| > 10% du volume
            const double absorp = (totalVolume > 0.0 && fabs(delta) > 0.10 * totalVolume) ? 1.0 : 0.0;
            const double dtrend = (cumulativeDelta > 0.0) ? 1.0 : (cumulativeDelta < 0.0 ? -1.0 : 0.0);

            SCString j;
            j.Format(
              R"({"t":%.6f,"sym":"%s","type":"nbcv_orderflow","i":%d,"volume_imbalance":%.6f,"trade_intensity":%.6f,"delta_trend":%.0f,"absorption_pattern":%.0f,"chart":%d})",
              t, sc.Symbol.GetChars(), i,
              (totalVolume > 0.0 ? (askVolume - bidVolume) / totalVolume : 0.0),
              (totalVolume > 0.0 ? numberOfTrades / totalVolume : 0.0),
              dtrend, absorp, sc.ChartNumber
            );
            WritePerChartDaily(sc.ChartNumber, j);
          }
        } else {
          // Insufficient data
          SCString j; j.Format("{\"t\":%.6f,\"type\":\"nbcv_diag\",\"msg\":\"insufficient_data\",\"i\":%d,\"chart\":%d,"
                               "\"ask_sz\":%d,\"bid_sz\":%d,\"delta_sz\":%d,\"trades_sz\":%d,\"cum_sz\":%d}",
                               sc.BaseDateTimeIn[i].GetAsDouble(), i, sc.ChartNumber,
                               askVolArr.GetArraySize(), bidVolArr.GetArraySize(), deltaArr.GetArraySize(),
                               tradesArr.GetArraySize(), cumDeltaArr.GetArraySize());
          WritePerChartDaily(sc.ChartNumber, j);
        }
      } else {
        // Study not found
        SCString j; j.Format("{\"t\":%.6f,\"type\":\"nbcv_diag\",\"msg\":\"study_not_found\",\"i\":%d,\"chart\":%d}",
                             sc.BaseDateTimeIn[i].GetAsDouble(), i, sc.ChartNumber);
        WritePerChartDaily(sc.ChartNumber, j);
      }
    }
  }

  // ===== TIME & SALES / QUOTES =====
  static int s_last_ts_bar = -1;
  
  if ((sc.Input[27].GetYesNo() || sc.Input[28].GetYesNo()) && sc.ArraySize > 0)
  {
    const int i = sc.ArraySize - 1;
    const bool newbar_only = sc.Input[30].GetInt() != 0;
    
    if (newbar_only && i == s_last_ts_bar) {
      // Skip - same bar
    } else {
      s_last_ts_bar = i;
      
      // Collecte des Quotes (Bid/Ask niveau 1)
      static double s_last_l1_bid = 0.0, s_last_l1_ask = 0.0;
      static int    s_last_l1_bq  = -1,   s_last_l1_aq  = -1;
      if (sc.Input[28].GetYesNo()) {
        const double t = sc.BaseDateTimeIn[i].GetAsDouble();
        const double bid = NormalizePx(sc, sc.Bid);
        const double ask = NormalizePx(sc, sc.Ask);
        const int bidQty = sc.BidSize;
        const int askQty = sc.AskSize;
        
        if (bid > 0.0 && ask > 0.0) {
          if (!(bid == s_last_l1_bid && ask == s_last_l1_ask && bidQty == s_last_l1_bq && askQty == s_last_l1_aq))
          {
            const double spread = ask - bid;
            const double mid = (bid + ask) / 2.0;
            SCString j;
            j.Format("{\"t\":%.6f,\"sym\":\"%s\",\"type\":\"quote\",\"kind\":\"BIDASK\",\"bid\":%.8f,\"ask\":%.8f,\"bq\":%d,\"aq\":%d,\"spread\":%.8f,\"mid\":%.8f,\"chart\":%d}",
                     t, sc.Symbol.GetChars(), bid, ask, bidQty, askQty, spread, mid, sc.ChartNumber);
            WritePerChartDaily(sc.ChartNumber, j);
            s_last_l1_bid = bid; s_last_l1_ask = ask; s_last_l1_bq = bidQty; s_last_l1_aq = askQty;
          }
        }
      }
      
      // Collecte des Trades (si disponibles)
      if (sc.Input[27].GetYesNo()) {
        // Utiliser les données de base pour simuler les trades
        const double t = sc.BaseDateTimeIn[i].GetAsDouble();
        const double price = sc.Close[i];
        const int volume = (int)sc.Volume[i];
        
        if (price > 0.0 && volume > 0) {
          SCString j;
          j.Format("{\"t\":%.6f,\"sym\":\"%s\",\"type\":\"trade\",\"source\":\"basedata\",\"px\":%.8f,\"qty\":%d,\"chart\":%d}",
                   t, sc.Symbol.GetChars(), price, volume, sc.ChartNumber);
          WritePerChartDaily(sc.ChartNumber, j);
        }
      }
    }
  }

  // ---- DOM live (niveaux 1..max_levels) ----
  if (sc.UsesMarketDepthData) {
    static double s_last_bid_price[256];
    static int    s_last_bid_size[256];
    static double s_last_ask_price[256];
    static int    s_last_ask_size[256];
    for (int lvl = 1; lvl <= max_levels && lvl < 256; ++lvl) {
      s_MarketDepthEntry eBid;
      bool gotB = sc.GetBidMarketDepthEntryAtLevel(eBid, lvl);
      if (gotB && eBid.Price != 0.0 && eBid.Quantity != 0) {
        const double t = sc.BaseDateTimeIn[sc.ArraySize - 1].GetAsDouble();
        double p = (lvl == 1 ? NormalizePx(sc, sc.Bid) : NormalizePx(sc, eBid.Price));
        const int q = (lvl == 1 ? sc.BidSize : (int)eBid.Quantity);
        if (!(p == s_last_bid_price[lvl] && q == s_last_bid_size[lvl])) {
          SCString j;
          j.Format("{\"t\":%.6f,\"sym\":\"%s\",\"type\":\"depth\",\"side\":\"BID\",\"lvl\":%d,\"price\":%.8f,\"size\":%d,\"chart\":%d}",
                   t, sc.Symbol.GetChars(), lvl, p, q, sc.ChartNumber);
          WritePerChartDaily(sc.ChartNumber, j);
          s_last_bid_price[lvl] = p; s_last_bid_size[lvl] = q;
        }
      }

      s_MarketDepthEntry eAsk;
      bool gotA = sc.GetAskMarketDepthEntryAtLevel(eAsk, lvl);
      if (gotA && eAsk.Price != 0.0 && eAsk.Quantity != 0) {
        const double t = sc.BaseDateTimeIn[sc.ArraySize - 1].GetAsDouble();
        double p = (lvl == 1 ? NormalizePx(sc, sc.Ask) : NormalizePx(sc, eAsk.Price));
        const int q = (lvl == 1 ? sc.AskSize : (int)eAsk.Quantity);
        if (!(p == s_last_ask_price[lvl] && q == s_last_ask_size[lvl])) {
          SCString j;
          j.Format("{\"t\":%.6f,\"sym\":\"%s\",\"type\":\"depth\",\"side\":\"ASK\",\"lvl\":%d,\"price\":%.8f,\"size\":%d,\"chart\":%d}",
                   t, sc.Symbol.GetChars(), lvl, p, q, sc.ChartNumber);
          WritePerChartDaily(sc.ChartNumber, j);
          s_last_ask_price[lvl] = p; s_last_ask_size[lvl] = q;
        }
      }
    }
  }

  // VAP (Volume at Price) - SUPPRIMÉ - On utilise NBCV à la place

  // ========== T&S ANTI-DOUBLONS ROBUSTE ==========
  c_SCTimeAndSalesArray TnS;
  sc.GetTimeAndSales(TnS);
  const int sz = (int)TnS.Size();

  // Reset si Sierra a purgé l'historique
  if (sz < g_LastTsIndex) g_LastTsIndex = 0;

  // Première détection de support du Sequence
  static bool seqChecked = false;
  if (!seqChecked) { DetectSequenceSupport(TnS, g_UseSeq); seqChecked = true; }

  if (g_UseSeq)
  {
    // --- Mode "Sequence" (recommandé) ---
    // Traite tout ce dont Sequence est strictement > g_LastSeq
    for (int i = 0; i < sz; ++i)
    {
      const s_TimeAndSales& ts = TnS[i];
      if (ts.Sequence == 0) continue;           // certains enregs peuvent être 0
      if (ts.Sequence <= g_LastSeq) continue;   // déjà traité

      ProcessTS(ts);
      g_LastSeq = ts.Sequence;
    }

    // (Option) si détection d'un wrap/rollback de sequence : réinitialise
    // if (sz > 0 && TnS[sz-1].Sequence < g_LastSeq) g_LastSeq = 0;
  }
  else
  {
    // --- Mode "Index cursor" (fallback universel) ---
    for (int i = g_LastTsIndex; i < sz; ++i)
      ProcessTS(TnS[i]);

    g_LastTsIndex = sz;
  }

}
