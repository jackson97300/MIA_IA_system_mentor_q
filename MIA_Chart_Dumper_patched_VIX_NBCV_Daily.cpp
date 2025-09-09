#include "sierrachart.h"
#ifdef _WIN32
  #include <windows.h>
#endif
#include <time.h>
#include <cmath>
using std::fabs;

SCDLLName("MIA_Chart_Dumper_Patched_VIX_NBCV_Daily")

// Dumper complet : BaseData, DOM live, VAP, T&S, VWAP + VVA (Volume Value Area Lines) + PVWAP + VIX + NBCV Footprint
// Collecte VAH/VAL/VPOC (courant) + PVAH/PVAL/PPOC (précédent) + PVWAP (VWAP période précédente) + VIX temps réel + NBCV OrderFlow

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

// ========== NORMALISATION DES PRIX ==========
inline double NormalizePx(const SCStudyInterfaceRef& sc, double raw)
{
  // d'abord dé-multiplier si besoin
  const double mult = (sc.RealTimePriceMultiplier != 0.0 ? sc.RealTimePriceMultiplier : 1.0);
  double px = raw / mult;

  // arrondir au tick (ES = 0.25)
  px = sc.RoundToTickSize(px, sc.TickSize);

  // filet anti-sur-scaling (si un prix aberrant > 10000 traîne)
  if (px > 10000.0) px /= 100.0;
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
    sc.GraphName = "MIA Chart Dumper (Patched + VIX + NBCV Daily)";
    sc.AutoLoop = 0;
    sc.UpdateAlways = 1;
    sc.UsesMarketDepthData = 1;
    sc.MaintainVolumeAtPriceData = 1;
    sc.MaintainAdditionalChartDataArrays = 1;
    sc.CalculationPrecedence = LOW_PREC_LEVEL; // important: calc VWAP avant notre étude

    // --- Inputs BaseData + DOM + VAP + T&S ---
    sc.Input[0].Name = "Max DOM Levels";
    sc.Input[0].SetInt(20);
    sc.Input[1].Name = "Max VAP Elements";
    sc.Input[1].SetInt(5);
    sc.Input[2].Name = "Max T&S Entries";
    sc.Input[2].SetInt(10);

    // --- Inputs VWAP ---
    sc.Input[3].Name = "Export VWAP From Study (0/1)";
    sc.Input[3].SetInt(1); // 1 = on
    sc.Input[4].Name = "VWAP Study ID (0=auto)";
    sc.Input[4].SetInt(0); // Auto-résolution par nom (recommandé)
    sc.Input[5].Name = "Export VWAP Bands Count (0..4)";
    sc.Input[5].SetInt(4); // Default to 4 bands based on user's current config

    // --- Inputs VVA (Volume Value Area Lines) ---
    sc.Input[6].Name = "Export Value Area Lines (0/1)";
    sc.Input[6].SetInt(1);
    sc.Input[7].Name = "VVA Current Study ID (0=off)";
    sc.Input[7].SetInt(1);   // ID:1 = période COURANTE
    sc.Input[8].Name = "VVA Previous Study ID (0=off)";
    sc.Input[8].SetInt(2);   // ID:2 = période PRECEDENTE
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
    sc.Input[15].SetInt(0);  // 0 = Chart direct, 1 = Study Overlay
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
    sc.Input[20].SetInt(0);  // 0 = détection automatique par nom

    // Mapping Subgraphs (d'après ta config: SG6/7/1/5/10)
    sc.Input[21].Name = "NBCV SG - Ask Volume Total";
    sc.Input[21].SetInt(6);

    sc.Input[22].Name = "NBCV SG - Bid Volume Total";
    sc.Input[22].SetInt(7);

    sc.Input[23].Name = "NBCV SG - Delta (Ask-Bid)";
    sc.Input[23].SetInt(1);

    sc.Input[24].Name = "NBCV SG - Number of Trades";
    sc.Input[24].SetInt(5);

    sc.Input[25].Name = "NBCV SG - CumDelta Day (Ask-Bid)";
    sc.Input[25].SetInt(10);

    // Option: n'écrire que sur nouvelle barre
    sc.Input[26].Name = "NBCV On New Bar Only (0/1)";
    sc.Input[26].SetInt(1);

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
    if (sc.GetStudyArrayUsingID(studyId, sgIndex, arr) == 0) return 0.0;
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
              j.Format(R"({"t":%.6f,"sym":"%s","type":"quote","kind":"%s","bid":%.8f,"ask":%.8f,"bq":%d,"aq":%d,"seq":%u})",
                       tsec, sc.Symbol.GetChars(), kind, bid, ask, ts.BidSize, ts.AskSize, ts.Sequence);
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
              j.Format(R"({"t":%.6f,"sym":"%s","type":"trade","px":%.8f,"vol":%d,"seq":%u})",
                       tsec, sc.Symbol.GetChars(), px, ts.Volume, ts.Sequence);
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
    j.Format("{\"t\":%.6f,\"sym\":\"%s\",\"type\":\"basedata\",\"i\":%d,\"o\":%.8f,\"h\":%.8f,\"l\":%.8f,\"c\":%.8f,\"v\":%.0f,\"bidvol\":%.0f,\"askvol\":%.0f}",
      t, sc.Symbol.GetChars(), i, o, h, l, c, v, bvol, avol);
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
            sc.GetStudyArrayUsingID(cand[k], 0, test);
            if (test.GetArraySize() > i && test[i] != 0) { vwapID = cand[k]; break; }
          }
        }
        // Diagnostic uniquement à la première résolution
        SCString d; d.Format("{\"t\":%.6f,\"type\":\"vwap_diag\",\"resolved_id\":%d}", t, vwapID);
        WritePerChartDaily(sc.ChartNumber, d);
      }
  
      if (vwapID > 0) {
        SCFloatArray VWAP, UP1, DN1, UP2, DN2;
        sc.GetStudyArrayUsingID(vwapID, 0, VWAP);
        int bands = sc.Input[5].GetInt();
        if (bands >= 1) { sc.GetStudyArrayUsingID(vwapID, 1, UP1); sc.GetStudyArrayUsingID(vwapID, 2, DN1); }
        if (bands >= 2) { sc.GetStudyArrayUsingID(vwapID, 3, UP2); sc.GetStudyArrayUsingID(vwapID, 4, DN2); }
  
        if (VWAP.GetArraySize() > i) {
          double v   = NormalizePx(sc, VWAP[i]);
          double up1 = (UP1.GetArraySize() > i ? NormalizePx(sc, UP1[i]) : 0);
          double dn1 = (DN1.GetArraySize() > i ? NormalizePx(sc, DN1[i]) : 0);
          double up2 = (UP2.GetArraySize() > i ? NormalizePx(sc, UP2[i]) : 0);
          double dn2 = (DN2.GetArraySize() > i ? NormalizePx(sc, DN2[i]) : 0);
  
          SCString j;
          j.Format("{\"t\":%.6f,\"sym\":\"%s\",\"type\":\"vwap\",\"src\":\"study\",\"i\":%d,\"v\":%.8f,\"up1\":%.8f,\"dn1\":%.8f,\"up2\":%.8f,\"dn2\":%.8f}",
                   t, sc.Symbol.GetChars(), i, v, up1, dn1, up2, dn2);
          WritePerChartDaily(sc.ChartNumber, j);
        } else {
          SCString d; d.Format("{\"t\":%.6f,\"type\":\"vwap_diag\",\"msg\":\"array_too_small\",\"id\":%d,\"i\":%d}",
                               t, vwapID, i);
          WritePerChartDaily(sc.ChartNumber, d);
        }
      } else {
        SCString d; d.Format("{\"t\":%.6f,\"type\":\"vwap_diag\",\"msg\":\"study_not_found\"}", t);
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

        SCFloatArray SG0, SG1, SG2;  // 0=VAH, 1=VAL, 2=VPOC
        sc.GetStudyArrayUsingID(id, 0, SG0);
        sc.GetStudyArrayUsingID(id, 1, SG1);
        sc.GetStudyArrayUsingID(id, 2, SG2);

        if (SG0.GetArraySize() > i) vah  = NormalizePx(sc, SG0[i]);
        if (SG1.GetArraySize() > i) val  = NormalizePx(sc, SG1[i]);
        if (SG2.GetArraySize() > i) vpoc = NormalizePx(sc, SG2[i]);
      };

      double vah=0,val=0,vpoc=0, pvah=0,pval=0,ppoc=0;
      read_vva(id_curr, vah, val, vpoc);
      read_vva(id_prev, pvah, pval, ppoc);

      SCString j;
      j.Format("{\"t\":%.6f,\"sym\":\"%s\",\"type\":\"vva\",\"i\":%d,"
               "\"vah\":%.8f,\"val\":%.8f,\"vpoc\":%.8f,"
               "\"pvah\":%.8f,\"pval\":%.8f,\"ppoc\":%.8f,"
               "\"id_curr\":%d,\"id_prev\":%d}",
               sc.BaseDateTimeIn[i].GetAsDouble(), sc.Symbol.GetChars(), i,
               vah, val, vpoc, pvah, pval, ppoc, id_curr, id_prev);
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
        SCString d; d.Format("{\"t\":%.6f,\"type\":\"pvwap_diag\",\"msg\":\"insufficient_history\",\"currStart\":%d}", 
                             sc.BaseDateTimeIn[last].GetAsDouble(), currStart);
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
                   "\"up3\":%.8f,\"dn3\":%.8f,\"up4\":%.8f,\"dn4\":%.8f}",
                   sc.BaseDateTimeIn[last].GetAsDouble(), sc.Symbol.GetChars(), last,
                   prevStart, prevEnd,
                   pvwap, up1, dn1, up2, dn2, up3, dn3, up4, dn4);
          WritePerChartDaily(sc.ChartNumber, j);
        } else {
          // Diagnostic si pas de volume sur la veille
          SCString d; d.Format("{\"t\":%.6f,\"type\":\"pvwap_diag\",\"msg\":\"no_volume_prev_session\",\"prevStart\":%d,\"prevEnd\":%d}", 
                               sc.BaseDateTimeIn[last].GetAsDouble(), prevStart, prevEnd);
          WritePerChartDaily(sc.ChartNumber, d);
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
        jv.Format(
          "{\"t\":%.6f,\"type\":\"vix\",\"i\":%d,\"last\":%.6f,"
          "\"mode\":%d,\"chart\":%d,\"study\":%d,\"sg\":%d}",
          t, i, vix,
          sc.Input[15].GetInt(),
          sc.Input[16].GetInt(),
          sc.Input[17].GetInt(),
          sc.Input[18].GetInt()
        );
      } else {
        jv.Format(
          "{\"t\":%.6f,\"type\":\"vix_diag\",\"i\":%d,\"msg\":\"no_data\","
          "\"mode\":%d,\"chart\":%d,\"study\":%d,\"sg\":%d}",
          t, i,
          sc.Input[15].GetInt(),
          sc.Input[16].GetInt(),
          sc.Input[17].GetInt(),
          sc.Input[18].GetInt()
        );
      }
      WritePerChartDaily(sc.ChartNumber, jv);
  }

  // ===== NBCV FOOTPRINT (Numbers Bars Calculated Values) =====
  static int s_last_nbcv_bar = -1;

  if (sc.Input[19].GetYesNo() && sc.ArraySize > 0)
  {
    const int i = sc.ArraySize - 1;
    const bool newbar_only = sc.Input[26].GetInt() != 0;
    if (!newbar_only || i != s_last_nbcv_bar) s_last_nbcv_bar = i; else goto nbcv_done;

    // 1) Résoudre l'ID d'étude NBCV
    int nbcv_id = sc.Input[20].GetInt();
    if (nbcv_id <= 0) {
      nbcv_id = sc.GetStudyIDByName(sc.ChartNumber, "Numbers Bars Calculated Values", 1);
    }
    if (nbcv_id <= 0) {
      SCString j; j.Format("{\"t\":%.6f,\"type\":\"nbcv_diag\",\"msg\":\"study_not_found\",\"i\":%d}",
                           sc.BaseDateTimeIn[i].GetAsDouble(), i);
      WritePerChartDaily(sc.ChartNumber, j);
      goto nbcv_done;
    }

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
    sc.GetStudyArrayUsingID(nbcv_id, sgCum,   cumDeltaArr);

    // 3) Vérifier la dispo à l'index i
    auto has = [&](const SCFloatArray& a){ return a.GetArraySize() > i; };
    if (!(has(askVolArr) && has(bidVolArr) && has(deltaArr))) {
      SCString j; j.Format("{\"t\":%.6f,\"type\":\"nbcv_diag\",\"msg\":\"insufficient_data\",\"i\":%d,"
                           "\"ask_sz\":%d,\"bid_sz\":%d,\"delta_sz\":%d,\"trades_sz\":%d,\"cum_sz\":%d}",
                           sc.BaseDateTimeIn[i].GetAsDouble(), i,
                           askVolArr.GetArraySize(), bidVolArr.GetArraySize(), deltaArr.GetArraySize(),
                           tradesArr.GetArraySize(), cumDeltaArr.GetArraySize());
      WritePerChartDaily(sc.ChartNumber, j);
      goto nbcv_done;
    }

    // 4) Valeurs
    const double t = sc.BaseDateTimeIn[i].GetAsDouble();
    const double askVolume      = askVolArr[i];
    const double bidVolume      = bidVolArr[i];
    const double delta          = deltaArr[i];
    const double numberOfTrades = has(tradesArr)   ? tradesArr[i]   : 0.0;
    const double cumulativeDelta= has(cumDeltaArr) ? cumDeltaArr[i] : 0.0;

    const double totalVolume = askVolume + bidVolume;
    const double deltaRatio  = (totalVolume > 0.0) ? (delta / totalVolume) : 0.0;
    const double bidAskRatio = (askVolume > 0.0) ? (bidVolume / askVolume) : 0.0;
    const double askBidRatio = (bidVolume > 0.0) ? (askVolume / bidVolume) : 0.0;

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
      SCString j;
      j.Format(
        R"({"t":%.6f,"sym":"%s","type":"nbcv_metrics","i":%d,"delta_ratio":%.6f,"bid_ask_ratio":%.6f,"ask_bid_ratio":%.6f,"pressure_bullish":%.0f,"pressure_bearish":%.0f,"chart":%d})",
        t, sc.Symbol.GetChars(), i,
        deltaRatio, bidAskRatio, askBidRatio,
        (delta > 0.0) ? 1.0 : 0.0,
        (delta < 0.0) ? 1.0 : 0.0,
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

  nbcv_done: ;
  }

  // ---- DOM live (niveaux 1..max_levels) ----
  if (sc.UsesMarketDepthData) {
    for (int lvl = 1; lvl <= max_levels; ++lvl) {
      s_MarketDepthEntry eBid;
      bool gotB = sc.GetBidMarketDepthEntryAtLevel(eBid, lvl);
      if (gotB && eBid.Price != 0.0 && eBid.Quantity != 0) {
        const double t = sc.CurrentSystemDateTime.GetAsDouble();
        // Force normalisation DOM (prix arrivent x100 de Sierra Chart)
        double p = eBid.Price;
        if (p > 10000.0) p /= 100.0;  // Anti-sur-scaling DOM
        p = sc.RoundToTickSize(p, sc.TickSize);
        SCString j;
        j.Format("{\"t\":%.6f,\"sym\":\"%s\",\"type\":\"depth\",\"side\":\"BID\",\"lvl\":%d,\"price\":%.8f,\"size\":%d}",
                 t, sc.Symbol.GetChars(), lvl, p, (int)eBid.Quantity);
        WritePerChartDaily(sc.ChartNumber, j);
      }

      s_MarketDepthEntry eAsk;
      bool gotA = sc.GetAskMarketDepthEntryAtLevel(eAsk, lvl);
      if (gotA && eAsk.Price != 0.0 && eAsk.Quantity != 0) {
        const double t = sc.CurrentSystemDateTime.GetAsDouble();
        // Force normalisation DOM (prix arrivent x100 de Sierra Chart)
        double p = eAsk.Price;
        if (p > 10000.0) p /= 100.0;  // Anti-sur-scaling DOM
        p = sc.RoundToTickSize(p, sc.TickSize);
        SCString j;
        j.Format("{\"t\":%.6f,\"sym\":\"%s\",\"type\":\"depth\",\"side\":\"ASK\",\"lvl\":%d,\"price\":%.8f,\"size\":%d}",
                 t, sc.Symbol.GetChars(), lvl, p, (int)eAsk.Quantity);
        WritePerChartDaily(sc.ChartNumber, j);
      }
    }
  }

  // ---- VAP (Volume at Price) ----
  if (sc.MaintainVolumeAtPriceData && sc.VolumeAtPriceForBars && sc.ArraySize > 0) {
    int bar = sc.ArraySize - 1;
    int vapSize = sc.VolumeAtPriceForBars->GetSizeAtBarIndex(bar);
    for (int k = 0; k < vapSize && k < max_vap; ++k) {
      const s_VolumeAtPriceV2* v = nullptr;
      if (sc.VolumeAtPriceForBars->GetVAPElementAtIndex(bar, k, &v) && v) {
        // Utiliser le bon nom de membre pour le prix (peut varier selon la version de Sierra Chart)
        double price = 0.0;
        // Essayer différents noms de membres possibles
        #ifdef SC_VAP_PRICE
          price = NormalizePx(sc, v->Price);
        #elif defined(SC_VAP_PRICE_IN_TICKS)
          price = NormalizePx(sc, v->PriceInTicks * sc.TickSize);
        #else
          // Fallback : utiliser le prix calculé à partir de l'index de barre
          price = NormalizePx(sc, sc.BaseDataIn[SC_LAST][bar]);
        #endif
        
        double t = sc.CurrentSystemDateTime.GetAsDouble();
        SCString j;
        j.Format("{\"t\":%.6f,\"sym\":\"%s\",\"type\":\"vap\",\"bar\":%d,\"k\":%d,\"price\":%.8f,\"vol\":%d}",
          t, sc.Symbol.GetChars(), bar, k, price, v->Volume);
        WritePerChartDaily(sc.ChartNumber, j);
      }
    }
  }

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
