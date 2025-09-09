#include "sierrachart.h"
#ifdef _WIN32
  #include <windows.h>
#endif
#include <time.h>
#include <cmath>
using std::fabs;

// ========== DÉFINITIONS SIERRA CHART ==========
#ifndef SC_TIME
#define SC_TIME 0
#endif
#ifndef SC_OPEN
#define SC_OPEN 0
#endif
#ifndef SC_HIGH
#define SC_HIGH 1
#endif
#ifndef SC_LOW
#define SC_LOW 2
#endif
#ifndef SC_LAST
#define SC_LAST 3
#endif
#ifndef SC_VOLUME
#define SC_VOLUME 4
#endif
#ifndef SC_OPENINT
#define SC_OPENINT 5
#endif
#ifndef SC_BIDVOL
#define SC_BIDVOL 6
#endif
#ifndef SC_ASKVOL
#define SC_ASKVOL 7
#endif
#ifndef SC_TS_BID
#define SC_TS_BID 0
#endif
#ifndef SC_TS_ASK
#define SC_TS_ASK 1
#endif
#ifndef SC_TS_BIDASKVALUES
#define SC_TS_BIDASKVALUES 2
#endif

SCDLLName("MIA_Chart_Dumper_Patched_VIX_NBCV_Quotes_Corrected_Daily")

// Dumper complet : BaseData, DOM live, VAP, T&S, VWAP + VVA (depuis Volume Profile) + PVWAP + VIX + Numbers Bars Calculated Values + Quotes/Trades

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
  if (f) { fprintf(f, "%s\n", line.GetChars()); fclose(f); }
}

// ========== NORMALISATION DES PRIX ==========
inline double NormalizePx(const SCStudyInterfaceRef& sc, double raw)
{
  const double mult = (sc.RealTimePriceMultiplier != 0.0 ? sc.RealTimePriceMultiplier : 1.0);
  double px = raw / mult;
  px = sc.RoundToTickSize(px, sc.TickSize);
  if (px > 10000.0) px /= 100.0; // filet anti sur-scaling
  return px;
}

// ========== FONCTION DÉTECTSEQUENCESUPPORT ==========
static void DetectSequenceSupport(const c_SCTimeAndSalesArray& TnS, bool& g_UseSeq)
{
  for (int i = (int)TnS.Size() - 1; i >= 0 && i >= (int)TnS.Size() - 50; --i)
    if (TnS[i].Sequence > 0) { g_UseSeq = true; break; }
}

// ========== FONCTION PRINCIPALE ==========
SCSFExport scsf_MIA_Chart_Dumper_Patched_VIX_Daily(SCStudyInterfaceRef sc)
{
  if (sc.SetDefaults)
  {
    sc.GraphName = "MIA Chart Dumper (Patched + VIX + Numbers Bars Calculated Values + Quotes + Corrected Daily)";
    sc.AutoLoop = 0;
    sc.UpdateAlways = 1;
    sc.UsesMarketDepthData = 1;
    sc.MaintainVolumeAtPriceData = 1;
    sc.MaintainAdditionalChartDataArrays = 1;
    sc.CalculationPrecedence = LOW_PREC_LEVEL;

    // --- Inputs BaseData + DOM + VAP + T&S ---
    sc.Input[0].Name = "Max DOM Levels"; sc.Input[0].SetInt(20);
    sc.Input[1].Name = "Max VAP Elements"; sc.Input[1].SetInt(5);
    sc.Input[2].Name = "Max T&S Entries"; sc.Input[2].SetInt(10);

    // --- Inputs VWAP ---
    sc.Input[3].Name = "Export VWAP From Study (0/1)"; sc.Input[3].SetInt(1);
    sc.Input[4].Name = "VWAP Study ID (0=auto)"; sc.Input[4].SetInt(0);
    sc.Input[5].Name = "Export VWAP Bands Count (0..4)"; sc.Input[5].SetInt(4);

    // --- (ANCIEN) VVA générique : désactivé par défaut pour éviter doublons/inversions ---
    sc.Input[6].Name = "Export Value Area Lines (generic) (0/1)"; sc.Input[6].SetInt(0);
    sc.Input[7].Name = "VVA Current Study ID (0=off)"; sc.Input[7].SetInt(0);
    sc.Input[8].Name = "VVA Previous Study ID (0=off)"; sc.Input[8].SetInt(0);
    sc.Input[9].Name = "Emit VVA On New Bar Only (0/1)"; sc.Input[9].SetInt(1);
    sc.Input[10].Name = "Apply Price Multiplier to VVA (0/1)"; sc.Input[10].SetInt(1);

    // --- Inputs PVWAP ---
    sc.Input[11].Name = "Export Previous VWAP (0/1)"; sc.Input[11].SetInt(1);
    sc.Input[12].Name = "PVWAP Bands Count (0..4)"; sc.Input[12].SetInt(2);
    sc.Input[13].Name = "PVWAP On New Bar Only (0/1)"; sc.Input[13].SetInt(1);

    // --- VIX ---
    sc.Input[14].Name = "Export VIX (0/1)"; sc.Input[14].SetInt(1);
    sc.Input[15].Name = "Export VIX (VIX_CGI[M] 1 Min #8, ID:23, SG4=Last)"; sc.Input[15].SetYesNo(1);
    // VIX déplacé vers Input 45-47

    // --- Numbers Bars Calculated Values ---
    sc.Input[19].Name = "Collect Numbers Bars Calculated Values (SG index only)"; sc.Input[19].SetYesNo(true);
    sc.Input[20].Name = "Numbers Bars Calculated Values Study ID"; sc.Input[20].SetInt(33);
    sc.Input[21].Name = "SG Ask Total";  sc.Input[21].SetInt(6);
    sc.Input[22].Name = "SG Bid Total";  sc.Input[22].SetInt(7);
    sc.Input[23].Name = "SG Delta";      sc.Input[23].SetInt(1);
    sc.Input[24].Name = "SG Trades";     sc.Input[24].SetInt(12);
    sc.Input[25].Name = "SG CumDelta";   sc.Input[25].SetInt(10);
    sc.Input[26].Name = "Numbers Bars Calculated Values On New Bar Only"; sc.Input[26].SetInt(0);

    // --- Time & Sales / Quotes ---
    sc.Input[27].Name = "Collect Time & Sales"; sc.Input[27].SetYesNo(true);
    sc.Input[28].Name = "Collect Quotes (Bid/Ask)"; sc.Input[28].SetYesNo(true);
    sc.Input[29].Name = "T&S On New Bar Only (0/1)"; sc.Input[29].SetInt(1);

    // --- Graph 4 (30m) : VP + VWAP + OHLC ---
    sc.Input[30].Name = "Collect Volume Profile from Graph 4 (0/1)"; sc.Input[30].SetInt(1);
    sc.Input[31].Name = "Graph 4 Volume Profile Study ID"; sc.Input[31].SetInt(8);
    sc.Input[32].Name = "VP On New Bar Only (0/1)"; sc.Input[32].SetInt(0);

    sc.Input[33].Name = "Collect VWAP from Graph 4 (0/1)"; sc.Input[33].SetInt(1);
    sc.Input[34].Name = "Graph 4 Current VWAP Study ID"; sc.Input[34].SetInt(1);
    sc.Input[35].Name = "Graph 4 Previous VWAP Study ID"; sc.Input[35].SetInt(13);
    sc.Input[36].Name = "VWAP On New Bar Only (0/1)"; sc.Input[36].SetInt(0);

    sc.Input[37].Name = "Collect OHLC from Graph 4 (0/1)"; sc.Input[37].SetInt(1);
    sc.Input[38].Name = "OHLC On New Bar Only (0/1)"; sc.Input[38].SetInt(0);

    // --- Graph 3 : VP + Numbers Bars Calculated Values + MFI ---
    sc.Input[39].Name = "Collect Volume Profile from Graph 3 (0/1)"; sc.Input[39].SetInt(1);
    sc.Input[40].Name = "Graph 3 Volume Profile Current Study ID"; sc.Input[40].SetInt(1);
    sc.Input[41].Name = "Graph 3 Volume Profile Previous Study ID"; sc.Input[41].SetInt(2);
    sc.Input[42].Name = "VP Graph 3 On New Bar Only (0/1)"; sc.Input[42].SetInt(0);


    // --- VIX (décalé) ---
    sc.Input[45].Name = "VIX Chart Number"; sc.Input[45].SetInt(8);
    sc.Input[46].Name = "VIX Min Interval (sec)"; sc.Input[46].SetInt(0);
    sc.Input[47].Name = "VIX Min Change"; sc.Input[47].SetFloat(0.05f);
    
    // --- Numbers Bars Calculated Values Graph 4 ---
    sc.Input[48].Name = "Numbers Bars Calculated Values Graph 4 Study ID"; sc.Input[48].SetInt(14);
    return;
  }

  if (sc.ServerConnectionState != SCS_CONNECTED) return;

  // ========== DEBUG LOGGING ==========
  static int debug_counter = 0;
  if (++debug_counter % 100 == 0) { // Log toutes les 100 itérations
    SCString debug_info;
    debug_info.Format("DEBUG: VP_G4_ID=%d, NBCV_G3_ID=%d, NBCV_G4_ID=%d, MFI_ID=%d, VIX_CHART=%d", 
                     sc.Input[31].GetInt(), sc.Input[20].GetInt(), sc.Input[48].GetInt(), 
                     sc.Input[43].GetInt(), sc.Input[45].GetInt());
    WritePerChartDaily(sc.ChartNumber, debug_info);
  }

  const int max_levels = sc.Input[0].GetInt();
  const int max_vap    = sc.Input[1].GetInt();
  const int max_ts     = sc.Input[2].GetInt();

  // ========== ANTI-DOUBLONS T&S ==========
  static int      g_LastTsIndex = 0;
  static uint32_t g_LastSeq     = 0;
  static bool     g_UseSeq      = false;

  // ========== HORODATAGE MONOTONE + SEQ ==========
  static double   last_ts = 0.0;
  static uint64_t seq     = 0;

  const double TICK = sc.TickSize;
  double ts = sc.CurrentSystemDateTime.GetAsDouble();
  if (ts <= last_ts) ts = last_ts + 0.000001; // ~0.086 ms
  last_ts = ts;
  seq++;

  // Sanitizer prix générique (quotes/DOM)
  auto normalize_price = [&](double px)->double {
    if (px != px) return NAN;
    if (px > 100000.0) px /= 100.0;
    double n = round(px / TICK) * TICK;
    return n;
  };

  // ========== TRAITEMENT T&S ==========
  auto ProcessTS = [&](const s_TimeAndSales& r) -> void
  {
    const double tsec = r.DateTime.GetAsDouble();
    const char* kind =
      (r.Type == SC_TS_BID) ? "BID" :
      (r.Type == SC_TS_ASK) ? "ASK" :
      (r.Type == SC_TS_BIDASKVALUES) ? "BIDASK" : "TRADE";

    if (r.Type == SC_TS_BID || r.Type == SC_TS_ASK || r.Type == SC_TS_BIDASKVALUES)
    {
      // QUOTE depuis T&S (avec filtre spread)
      if (r.Bid > 0 && r.Ask > 0)
      {
        double bid = NormalizePx(sc, r.Bid);
        double ask = NormalizePx(sc, r.Ask);
        if (bid==bid && ask==ask && bid>0 && ask>0 && bid < ask)
        {
          SCString j;
          j.Format(R"({"t":%.6f,"sym":"%s","type":"quote","kind":"%s","bid":%.8f,"ask":%.8f,"bq":%d,"aq":%d,"seq":%u})",
                   tsec, sc.Symbol.GetChars(), kind, bid, ask, r.BidSize, r.AskSize, r.Sequence);
          WritePerChartDaily(sc.ChartNumber, j);
        }
      }
    }
    else
    {
      // TRADE
      if (r.Price > 0 && r.Volume > 0)
      {
        const double px = NormalizePx(sc, r.Price);
        if (px==px && px>0.0)
        {
          SCString j;
          j.Format(R"({"t":%.6f,"sym":"%s","type":"trade","px":%.8f,"vol":%d,"seq":%u})",
                   tsec, sc.Symbol.GetChars(), px, r.Volume, r.Sequence);
          WritePerChartDaily(sc.ChartNumber, j);
        }
      }
    }
  };

  // ---- BaseData ----
  if (sc.ArraySize > 0) {
    const int i = sc.ArraySize - 1;
    const double o = sc.BaseDataIn[SC_OPEN][i];
    const double h = sc.BaseDataIn[SC_HIGH][i];
    const double l = sc.BaseDataIn[SC_LOW][i];
    const double c = sc.BaseDataIn[SC_LAST][i];
    const double v = sc.BaseDataIn[SC_VOLUME][i];
    const double bvol = sc.BaseDataIn[SC_BIDVOL][i];
    const double avol = sc.BaseDataIn[SC_ASKVOL][i];

    SCString j;
    j.Format("{\"t\":%.6f,\"sym\":\"%s\",\"type\":\"basedata\",\"i\":%d,\"o\":%.8f,\"h\":%.8f,\"l\":%.8f,\"c\":%.8f,\"v\":%.0f,\"bidvol\":%.0f,\"askvol\":%.0f,\"seq\":%llu}",
      ts, sc.Symbol.GetChars(), i, o, h, l, c, v, bvol, avol, seq);
    WritePerChartDaily(sc.ChartNumber, j);
  }

  // ---- VWAP (chart courant) ----
  if (sc.Input[3].GetInt() != 0 && sc.ArraySize > 0) {
    static int vwapID = -2; // -2 resolve, -1 missing
    const int i = sc.ArraySize - 1;

    if (vwapID == -2) {
      int cand[3];
      cand[0] = sc.Input[4].GetInt();
      cand[1] = sc.GetStudyIDByName(sc.ChartNumber, "Volume Weighted Average Price", 0);
      cand[2] = sc.GetStudyIDByName(sc.ChartNumber, "VWAP (Volume Weighted Average Price)", 0);

      vwapID = -1;
      for (int k = 0; k < 3; ++k) {
        if (cand[k] > 0) {
          SCFloatArray test; sc.GetStudyArrayUsingID(cand[k], 0, test);
          if (test.GetArraySize() > i && test[i] != 0) { vwapID = cand[k]; break; }
        }
      }
      SCString d; d.Format("{\"t\":%.6f,\"sym\":\"%s\",\"type\":\"vwap_diag\",\"resolved_id\":%d,\"seq\":%llu}", ts, sc.Symbol.GetChars(), vwapID, seq);
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
        j.Format("{\"t\":%.6f,\"sym\":\"%s\",\"type\":\"vwap\",\"src\":\"study\",\"i\":%d,\"v\":%.8f,\"up1\":%.8f,\"dn1\":%.8f,\"up2\":%.8f,\"dn2\":%.8f,\"seq\":%llu}",
                 ts, sc.Symbol.GetChars(), i, v, up1, dn1, up2, dn2, seq);
        WritePerChartDaily(sc.ChartNumber, j);
      }
    }
  }

  // ---- PVWAP (veille) ----
  if (sc.Input[11].GetInt() != 0 && sc.ArraySize > 0 && sc.VolumeAtPriceForBars)
  {
    const int last = sc.ArraySize - 1;
    static int last_pvwap_bar = -1;
    const bool newbar_only = sc.Input[13].GetInt() != 0;

    if (!newbar_only || last != last_pvwap_bar)
    {
      last_pvwap_bar = last;

      int currStart = last;
      while (currStart > 0 && !sc.IsNewTradingDay(currStart)) currStart--;
      if (currStart > 0) {
        int prevEnd = currStart - 1;
        int prevStart = prevEnd;
        while (prevStart > 0 && !sc.IsNewTradingDay(prevStart)) prevStart--;

        double sumV=0.0, sumPV=0.0, sumP2V=0.0;
        for (int b = prevStart; b <= prevEnd; ++b) {
          int N = sc.VolumeAtPriceForBars->GetSizeAtBarIndex(b);
          for (int k = 0; k < N; ++k) {
            const s_VolumeAtPriceV2* v = nullptr;
            if (sc.VolumeAtPriceForBars->GetVAPElementAtIndex(b, k, &v) && v) {
              double p = NormalizePx(sc, sc.BaseDataIn[SC_LAST][b]); // fallback robuste
              double vol = (double)v->Volume;
              sumV += vol; sumPV += p * vol; sumP2V += p * p * vol;
            }
          }
        }

        if (sumV > 0.0) {
          double pvwap = sumPV / sumV;
          double var = (sumP2V / sumV) - (pvwap * pvwap);
          if (var < 0) var = 0;
          double sigma = sqrt(var);

          int nb = sc.Input[12].GetInt();
          double up1=0, dn1=0, up2=0, dn2=0, up3=0, dn3=0, up4=0, dn4=0;
          if (nb >= 1) { up1 = pvwap + 0.5 * sigma; dn1 = pvwap - 0.5 * sigma; }
          if (nb >= 2) { up2 = pvwap + 1.0 * sigma; dn2 = pvwap - 1.0 * sigma; }
          if (nb >= 3) { up3 = pvwap + 1.5 * sigma; dn3 = pvwap - 1.5 * sigma; }
          if (nb >= 4) { up4 = pvwap + 2.0 * sigma; dn4 = pvwap - 2.0 * sigma; }

          SCString j;
          j.Format("{\"t\":%.6f,\"sym\":\"%s\",\"type\":\"pvwap\",\"i\":%d,\"prev_start\":%d,\"prev_end\":%d,"
                   "\"pvwap\":%.8f,\"up1\":%.8f,\"dn1\":%.8f,\"up2\":%.8f,\"dn2\":%.8f,"
                   "\"up3\":%.8f,\"dn3\":%.8f,\"up4\":%.8f,\"dn4\":%.8f}",
                   sc.BaseDateTimeIn[last].GetAsDouble(), sc.Symbol.GetChars(), last,
                   prevStart, prevEnd, pvwap, up1, dn1, up2, dn2, up3, dn3, up4, dn4);
          WritePerChartDaily(sc.ChartNumber, j);
        }
      }
    }
  }

  // ---- VIX (sampling régulier + seuil) ----
  if (sc.Input[14].GetInt() != 0) {
    static double last_vix_ts = 0.0;
    static double last_vix    = 0.0;

    const int vixChart = sc.Input[45].GetInt(); // Input 45: VIX Chart Number
    const int minSec   = sc.Input[46].GetInt(); // Input 46: VIX Min Interval (sec)
    const double minCh = sc.Input[47].GetFloat(); // Input 47: VIX Min Change

    SCGraphData vixData; sc.GetChartBaseData(vixChart, vixData);
    int n = vixData[SC_LAST].GetArraySize();
    if (n > 0) {
      int jidx = n - 1;
      double vix_last = vixData[SC_LAST][jidx];
      if (vix_last <= 0.0 || vix_last > 1000.0) {
        double cands[4] = {
          vixData[SC_OPEN].GetArraySize()  > jidx ? vixData[SC_OPEN][jidx]  : 0.0,
          vixData[SC_HIGH].GetArraySize()  > jidx ? vixData[SC_HIGH][jidx]  : 0.0,
          vixData[SC_LOW].GetArraySize()   > jidx ? vixData[SC_LOW][jidx]   : 0.0,
          vixData[SC_LAST].GetArraySize()  > jidx ? vixData[SC_LAST][jidx]  : 0.0
        };
        for (double x : cands) if (x > 0.0 && x < 200.0) { vix_last = x; break; }
      }
      if (vix_last > 0.0 && vix_last < 200.0) {
        bool time_ok = (ts - last_vix_ts) * 86400.0 >= minSec;
        bool move_ok = fabs(vix_last - last_vix) >= minCh;
        if (time_ok || move_ok) {
          SCString out;
          out.Format("{\"t\":%.6f,\"sym\":\"%s\",\"type\":\"vix\",\"i\":%d,\"last\":%.2f,\"chart\":%d,\"seq\":%llu}",
                     ts, sc.Symbol.GetChars(), jidx, vix_last, vixChart, seq);
          WritePerChartDaily(sc.ChartNumber, out);
          last_vix = vix_last; last_vix_ts = ts;
        }
      }
    }
  }

  // ---- Graph 4 : OHLC + VP + VWAP + VVA (depuis VP) ----
  if (sc.Input[30].GetInt() != 0 || sc.Input[33].GetInt() != 0 || sc.Input[37].GetInt() != 0) {
    const int currentBar = sc.ArraySize > 0 ? sc.ArraySize - 1 : 0;
    const double timestamp = sc.CurrentSystemDateTime.GetAsDouble();
    static int lastGraph4Bar = -1;
    const bool newBarOnly = sc.Input[32].GetInt() != 0 || sc.Input[36].GetInt() != 0 || sc.Input[38].GetInt() != 0;

    if (!newBarOnly || currentBar != lastGraph4Bar) {
      lastGraph4Bar = currentBar;

      // OHLC Graph 4
      if (sc.Input[37].GetInt() != 0) {
        const int targetChartNumber = 4;
        SCFloatArray o,h,l,c,dt;
        sc.GetChartArray(targetChartNumber, SC_OPEN,  o);
        sc.GetChartArray(targetChartNumber, SC_HIGH,  h);
        sc.GetChartArray(targetChartNumber, SC_LOW,   l);
        sc.GetChartArray(targetChartNumber, SC_LAST,  c);
        sc.GetChartArray(targetChartNumber, SC_TIME,  dt);

        if (o.GetArraySize() && h.GetArraySize() && l.GetArraySize() && c.GetArraySize() && dt.GetArraySize()) {
          const int i = o.GetArraySize() - 1;
          auto fix = [&](double x){ return (x > 100000.0) ? NAN : x; };
          double open  = fix(o[i]), high  = fix(h[i]), low = fix(l[i]), close = fix(c[i]);
          double dt_g4 = dt[i];
          if (open>0 && high>0 && low>0 && close>0) {
            SCString s;
            s.Format("{\"t\":%.6f,\"sym\":\"%s\",\"type\":\"ohlc_graph4\",\"bar\":%d,\"source\":\"chart_array\",\"chart\":%d,\"dt_g4\":%.6f,\"open\":%.2f,\"high\":%.2f,\"low\":%.2f,\"close\":%.2f}",
                     timestamp, sc.Symbol.GetChars(), i, targetChartNumber, dt_g4, open, high, low, close);
            WritePerChartDaily(sc.ChartNumber, s);
          }
        }
      }

      // Volume Profile courant (ID:8) + VVA officiel
      if (sc.Input[30].GetInt() != 0) {
        const int currentVPStudyID = sc.Input[31].GetInt(); // Input 31: Graph 4 Volume Profile Study ID
        SCFloatArray poc, vah, val;
        sc.GetStudyArrayUsingID(currentVPStudyID, 1, poc);  // SG1 = POC ✅
        sc.GetStudyArrayUsingID(currentVPStudyID, 2, vah);  // SG2 = VAH ✅
        sc.GetStudyArrayUsingID(currentVPStudyID, 3, val);  // SG3 = VAL ✅

        // Debug: Log si les arrays sont vides
        if (poc.GetArraySize() == 0 || vah.GetArraySize() == 0 || val.GetArraySize() == 0) {
          SCString debug_vp;
          debug_vp.Format("DEBUG_VP_G4: ID=%d, POC_SIZE=%d, VAH_SIZE=%d, VAL_SIZE=%d", 
                         currentVPStudyID, poc.GetArraySize(), vah.GetArraySize(), val.GetArraySize());
          WritePerChartDaily(sc.ChartNumber, debug_vp);
        }

        if (poc.GetArraySize() > currentBar && vah.GetArraySize() > currentBar && val.GetArraySize() > currentBar) {
          auto fix = [&](double x){ return (x > 100000.0) ? NAN : x; };
          double POC = fix(poc[currentBar]), VAH = fix(vah[currentBar]), VAL = fix(val[currentBar]);
          if (POC>0 && VAH>0 && VAL>0) {
            // Export VP
            SCString s;
            s.Format("{\"t\":%.6f,\"sym\":\"%s\",\"type\":\"volume_profile\",\"bar\":%d,\"source\":\"graph4_current\",\"poc\":%.2f,\"vah\":%.2f,\"val\":%.2f,\"study_id\":%d}",
                     timestamp, sc.Symbol.GetChars(), currentBar, POC, VAH, VAL, currentVPStudyID);
            WritePerChartDaily(sc.ChartNumber, s);

            // VVA officiel depuis VP (swap si inversé)
            if (VAH < VAL) { double tmp = VAH; VAH = VAL; VAL = tmp; }
            SCString vva;
            vva.Format("{\"t\":%.6f,\"sym\":\"%s\",\"type\":\"vva\",\"i\":%d,\"vah\":%.2f,\"val\":%.2f,\"vpoc\":%.2f}",
                       timestamp, sc.Symbol.GetChars(), currentBar, VAH, VAL, POC);
            WritePerChartDaily(sc.ChartNumber, vva);
          }
        }
      }

      // Volume Profile précédent (ID:9)
      if (sc.Input[30].GetInt() != 0) {
        const int previousVPStudyID = 9; // Volume Profile Previous Study ID (fixe pour l'instant)
        SCFloatArray ppoc, pvah, pval;
        sc.GetStudyArrayUsingID(previousVPStudyID, 1, ppoc);  // SG1 = PPOC ✅
        sc.GetStudyArrayUsingID(previousVPStudyID, 2, pvah);  // SG2 = PVAH ✅
        sc.GetStudyArrayUsingID(previousVPStudyID, 3, pval);  // SG3 = PVAL ✅

        if (ppoc.GetArraySize() > currentBar && pvah.GetArraySize() > currentBar && pval.GetArraySize() > currentBar) {
          auto fix = [&](double x){ return (x > 100000.0) ? NAN : x; };
          double PPOC = fix(ppoc[currentBar]), PVAH = fix(pvah[currentBar]), PVAL = fix(pval[currentBar]);
          if (PPOC>0 && PVAH>0 && PVAL>0) {
            SCString s;
            s.Format("{\"t\":%.6f,\"sym\":\"%s\",\"type\":\"volume_profile_previous\",\"bar\":%d,\"source\":\"graph4_previous\",\"ppoc\":%.2f,\"pvah\":%.2f,\"pval\":%.2f,\"study_id\":%d}",
                     timestamp, sc.Symbol.GetChars(), currentBar, PPOC, PVAH, PVAL, previousVPStudyID);
            WritePerChartDaily(sc.ChartNumber, s);
          }
        }
      }

      // VWAP actuel (ID:1)
      if (sc.Input[33].GetInt() != 0) {
        const int currentVWAPStudyID = 1;
        SCFloatArray vwap, s_plus_1, s_minus_1, s_plus_2, s_minus_2;
        sc.GetStudyArrayUsingID(currentVWAPStudyID, 0, vwap);
        sc.GetStudyArrayUsingID(currentVWAPStudyID, 1, s_plus_1);
        sc.GetStudyArrayUsingID(currentVWAPStudyID, 2, s_minus_1);
        sc.GetStudyArrayUsingID(currentVWAPStudyID, 3, s_plus_2);
        sc.GetStudyArrayUsingID(currentVWAPStudyID, 4, s_minus_2);

        if (vwap.GetArraySize() > currentBar) {
          auto fix = [&](double x){ return (x > 100000.0) ? NAN : x; };
          double VW = fix(vwap[currentBar]);
          double up1 = fix(s_plus_1.GetArraySize() > currentBar ? s_plus_1[currentBar] : 0.0);
          double dn1 = fix(s_minus_1.GetArraySize() > currentBar ? s_minus_1[currentBar] : 0.0);
          double up2 = fix(s_plus_2.GetArraySize() > currentBar ? s_plus_2[currentBar] : 0.0);
          double dn2 = fix(s_minus_2.GetArraySize() > currentBar ? s_minus_2[currentBar] : 0.0);
          if (VW > 0.0) {
            SCString s;
            s.Format("{\"t\":%.6f,\"sym\":\"%s\",\"type\":\"vwap_current\",\"bar\":%d,\"source\":\"graph4\",\"vwap\":%.2f,\"s_plus_1\":%.2f,\"s_minus_1\":%.2f,\"s_plus_2\":%.2f,\"s_minus_2\":%.2f,\"study_id\":%d}",
                     timestamp, sc.Symbol.GetChars(), currentBar, VW, up1, dn1, up2, dn2, currentVWAPStudyID);
            WritePerChartDaily(sc.ChartNumber, s);
          }
        }
      }

      // VWAP précédent (ID:13) + bandes réalistes
      if (sc.Input[33].GetInt() != 0) {
        const int previousVWAPStudyID = 13;
        SCFloatArray pvwap, psd_plus_1, psd_minus_1;
        sc.GetStudyArrayUsingID(previousVWAPStudyID, 0, pvwap);
        sc.GetStudyArrayUsingID(previousVWAPStudyID, 1, psd_plus_1);
        sc.GetStudyArrayUsingID(previousVWAPStudyID, 2, psd_minus_1);

        if (pvwap.GetArraySize() > currentBar) {
          auto fix = [&](double x){ return (x > 100000.0) ? NAN : x; };
          double PVW = fix(pvwap[currentBar]);
          double PSDp = fix(psd_plus_1.GetArraySize() > currentBar ? psd_plus_1[currentBar] : 0.0);
          double PSDm = fix(psd_minus_1.GetArraySize() > currentBar ? psd_minus_1[currentBar] : 0.0);
          if (PVW > 0.0) {
            // si PSDp semble être en ticks (petit nombre), convertir
            double sigma_pts = (PSDp > 0.0 && PSDp < 100.0) ? PSDp * sc.TickSize : PSDp;
            double up1 = PVW + sigma_pts;
            double dn1 = PVW - sigma_pts;

            SCString s;
            s.Format("{\"t\":%.6f,\"sym\":\"%s\",\"type\":\"vwap_previous\",\"bar\":%d,\"source\":\"graph4\",\"pvwap\":%.2f,\"psd_plus_1\":%.2f,\"psd_minus_1\":%.2f,\"up1\":%.2f,\"dn1\":%.2f,\"study_id\":%d}",
                     timestamp, sc.Symbol.GetChars(), currentBar, PVW, PSDp, PSDm, up1, dn1, previousVWAPStudyID);
            WritePerChartDaily(sc.ChartNumber, s);
          }
        }
      }
    }
  }

  // ---- Numbers Bars Calculated Values (NBCV) Graph 3 - CORRIGÉ ----
  // Input[20] = NBCV Study ID (mettre l'ID exact du Graph 3)
  int nbcv_id = sc.Input[20].GetInt();
  if (nbcv_id > 0 && sc.ArraySize > 0) {
    const int i = sc.ArraySize - 1;
    
    // MAPPING DIRECT basé sur l'analyse des logs DEBUG_NBCV_SCAN
    // SG01 = Ask Volume (756K), SG12 = Bid Volume (799K), SG14 = Trades (1.5K), SG09 = CumDelta (-2.1M)
    const int sgAsk = 1;   // SG1 = Ask Volume (candidat principal)
    const int sgBid = 12;  // SG12 = Bid Volume (candidat principal)  
    const int sgDel = 1;   // SG1 = Delta (même que Ask)
    const int sgTrd = 14;  // SG14 = Trades (1.5K)
    const int sgCum = 9;   // SG9 = CumDelta (-2.1M)

    SCFloatArray aAsk, aBid, aDel, aTrd, aCum;
    sc.GetStudyArrayUsingID(nbcv_id, sgAsk, aAsk);
    sc.GetStudyArrayUsingID(nbcv_id, sgBid, aBid);
    sc.GetStudyArrayUsingID(nbcv_id, sgDel, aDel);
    sc.GetStudyArrayUsingID(nbcv_id, sgTrd, aTrd);
    sc.GetStudyArrayUsingID(nbcv_id, sgCum, aCum);

    auto has = [&](const SCFloatArray& A){ return A.GetArraySize() > i; };
    if (has(aAsk) && has(aBid)) {
      double ask = aAsk[i], bid = aBid[i];
      double delta = has(aDel) ? aDel[i] : (ask - bid);
      double trades = has(aTrd) ? aTrd[i] : 0.0;
      double cum = has(aCum) ? aCum[i] : 0.0;
      double tot = ask + bid;

      SCString j;
      j.Format("{\"t\":%.6f,\"sym\":\"%s\",\"type\":\"numbers_bars_calculated_values_graph3\","
               "\"i\":%d,\"ask\":%.0f,\"bid\":%.0f,\"delta\":%.0f,"
               "\"trades\":%.0f,\"cumdelta\":%.0f,\"total\":%.0f,\"source_graph\":3,\"study_id\":%d,\"mapping\":\"direct\"}",
               sc.CurrentSystemDateTime.GetAsDouble(), sc.Symbol.GetChars(), i, 
               ask, bid, delta, trades, cum, tot, nbcv_id);
      WritePerChartDaily(sc.ChartNumber, j);
    } else {
      SCString dbg;
      dbg.Format("DEBUG_NBCV_GRAPH3: ID=%d hasAsk=%d hasBid=%d hasDel=%d hasTrd=%d hasCum=%d",
                 nbcv_id, (int)has(aAsk), (int)has(aBid), (int)has(aDel), (int)has(aTrd), (int)has(aCum));
      WritePerChartDaily(sc.ChartNumber, dbg);
    }
  }

  // ---- Numbers Bars Calculated Values (Graph 4) ----
  static int last_numbers_bars_calculated_values_graph4_bar = -1;
  if (sc.ArraySize > 0) {
    const int i = sc.ArraySize - 1;
    const bool newbar_only = false; // Collection continue
    if (!newbar_only || i != last_numbers_bars_calculated_values_graph4_bar) {
      last_numbers_bars_calculated_values_graph4_bar = i;

              const int numbers_bars_calculated_values_graph4_id = sc.Input[48].GetInt(); // Input 48: Numbers Bars Calculated Values Graph 4 Study ID
      if (numbers_bars_calculated_values_graph4_id > 0) {
        const int sgAsk = 6;  // SG6 = Ask Total
        const int sgBid = 7;  // SG7 = Bid Total
        const int sgDel = 1;  // SG1 = Delta
        const int sgTrd = 12; // SG12 = Trades
        const int sgCum = 10; // SG10 = CumDelta

        SCFloatArray aAsk,aBid,aDel,aTrd,aCum;
        sc.GetStudyArrayUsingID(numbers_bars_calculated_values_graph4_id, sgAsk, aAsk);
        sc.GetStudyArrayUsingID(numbers_bars_calculated_values_graph4_id, sgBid, aBid);
        sc.GetStudyArrayUsingID(numbers_bars_calculated_values_graph4_id, sgDel, aDel);
        sc.GetStudyArrayUsingID(numbers_bars_calculated_values_graph4_id, sgTrd, aTrd);
        sc.GetStudyArrayUsingID(numbers_bars_calculated_values_graph4_id, sgCum, aCum);

        auto has = [&](const SCFloatArray& A){ return A.GetArraySize() > i; };
        if (has(aAsk) && has(aBid)) {
          double ask=aAsk[i], bid=aBid[i];
          double delta = has(aDel) ? aDel[i] : (ask - bid);
          double trades = has(aTrd)? aTrd[i] : 0.0;
          double cum    = has(aCum)? aCum[i] : 0.0;
          double tot    = ask + bid;

          SCString j;
          j.Format(R"({"t":%.6f,"sym":"%s","type":"numbers_bars_calculated_values_graph4","i":%d,"ask":%.0f,"bid":%.0f,"delta":%.0f,"trades":%.0f,"cumdelta":%.0f,"total":%.0f,"source_graph":4,"study_id":%d})",
                   sc.BaseDateTimeIn[i].GetAsDouble(), sc.Symbol.GetChars(), i, ask, bid, delta, trades, cum, tot, numbers_bars_calculated_values_graph4_id);
          WritePerChartDaily(sc.ChartNumber, j);
        }
      }
    }
  }

  // ---- Quotes & Trades (depuis sc.*) ----
  static int s_last_ts_bar = -1;
  if ((sc.Input[27].GetYesNo() || sc.Input[28].GetYesNo()) && sc.ArraySize > 0)
  {
    const int i = sc.ArraySize - 1;
    const bool newbar_only = sc.Input[29].GetInt() != 0;
    if (!newbar_only || i != s_last_ts_bar) {
      s_last_ts_bar = i;

      if (sc.Input[28].GetYesNo()) {
        double bid = normalize_price(sc.Bid);
        double ask = normalize_price(sc.Ask);
        if (bid==bid && ask==ask && bid>0 && ask>0 && bid < ask) {
          double spread = ask - bid;
          double mid = 0.5*(bid+ask);
          SCString j;
          j.Format("{\"t\":%.6f,\"sym\":\"%s\",\"type\":\"quote\",\"kind\":\"BIDASK\",\"bid\":%.2f,\"ask\":%.2f,\"bq\":%d,\"aq\":%d,\"spread\":%.2f,\"mid\":%.2f,\"chart\":%d,\"seq\":%llu}",
                   ts, sc.Symbol.GetChars(), bid, ask, sc.BidSize, sc.AskSize, spread, mid, sc.ChartNumber, seq);
          WritePerChartDaily(sc.ChartNumber, j);
        }
      }

      if (sc.Input[27].GetYesNo()) {
        double price = normalize_price(sc.Close[i]);
        int volume = (int)sc.Volume[i];
        if (price==price && price>0.0 && volume>0) {
          SCString j;
          j.Format("{\"t\":%.6f,\"sym\":\"%s\",\"type\":\"trade\",\"source\":\"basedata\",\"px\":%.2f,\"qty\":%d,\"chart\":%d,\"seq\":%llu}",
                   ts, sc.Symbol.GetChars(), price, volume, sc.ChartNumber, seq);
          WritePerChartDaily(sc.ChartNumber, j);
        }
      }
    }
  }

  // ---- DOM live (groupé) ----
  if (sc.UsesMarketDepthData) {
    static uint64_t dom_group = 0; dom_group++;
    for (int lvl = 1; lvl <= max_levels; ++lvl) {
      s_MarketDepthEntry eB, eA;
      if (sc.GetBidMarketDepthEntryAtLevel(eB, lvl) && eB.Price != 0.0 && eB.Quantity != 0) {
        double p = normalize_price(eB.Price);
        if (p==p && p>0.0) {
          SCString j;
          j.Format("{\"t\":%.6f,\"sym\":\"%s\",\"type\":\"depth\",\"side\":\"BID\",\"lvl\":%d,\"price\":%.2f,\"size\":%d,\"group\":%llu,\"seq\":%llu}",
                   ts, sc.Symbol.GetChars(), lvl, p, (int)eB.Quantity, dom_group, seq);
          WritePerChartDaily(sc.ChartNumber, j);
        }
      }
      if (sc.GetAskMarketDepthEntryAtLevel(eA, lvl) && eA.Price != 0.0 && eA.Quantity != 0) {
        double p = normalize_price(eA.Price);
        if (p==p && p>0.0) {
          SCString j;
          j.Format("{\"t\":%.6f,\"sym\":\"%s\",\"type\":\"depth\",\"side\":\"ASK\",\"lvl\":%d,\"price\":%.2f,\"size\":%d,\"group\":%llu,\"seq\":%llu}",
                   ts, sc.Symbol.GetChars(), lvl, p, (int)eA.Quantity, dom_group, seq);
          WritePerChartDaily(sc.ChartNumber, j);
        }
      }
    }
  }

  // ---- VAP ----
  if (sc.MaintainVolumeAtPriceData && sc.VolumeAtPriceForBars && sc.ArraySize > 0) {
    int bar = sc.ArraySize - 1;
    int vapSize = sc.VolumeAtPriceForBars->GetSizeAtBarIndex(bar);
    for (int k = 0; k < vapSize && k < max_vap; ++k) {
      const s_VolumeAtPriceV2* v = nullptr;
      if (sc.VolumeAtPriceForBars->GetVAPElementAtIndex(bar, k, &v) && v) {
        double price = NormalizePx(sc, sc.BaseDataIn[SC_LAST][bar]); // fallback robuste
        SCString j;
        j.Format("{\"t\":%.6f,\"sym\":\"%s\",\"type\":\"vap\",\"bar\":%d,\"k\":%d,\"price\":%.2f,\"vol\":%d,\"seq\":%llu}",
                 ts, sc.Symbol.GetChars(), bar, k, price, v->Volume, seq);
        WritePerChartDaily(sc.ChartNumber, j);
      }
    }
  }

  // ---- Replay T&S (seq ou index) ----
  c_SCTimeAndSalesArray TnS; sc.GetTimeAndSales(TnS);
  const int sz = (int)TnS.Size();
  if (sz < g_LastTsIndex) g_LastTsIndex = 0;
  static bool seqChecked = false;
  if (!seqChecked) { DetectSequenceSupport(TnS, g_UseSeq); seqChecked = true; }

  if (g_UseSeq) {
    for (int i = 0; i < sz; ++i) {
      const s_TimeAndSales& r = TnS[i];
      if (r.Sequence == 0 || r.Sequence <= g_LastSeq) continue;
      ProcessTS(r);
      g_LastSeq = r.Sequence;
    }
  } else {
    for (int i = g_LastTsIndex; i < sz; ++i) ProcessTS(TnS[i]);
    g_LastTsIndex = sz;
  }


  // ========== NOUVELLE SECTION : GRAPH 3 (ID:1 et ID:2) ==========
  // Export Volume Profile depuis Graph 3 pour comparaison avec Graph 4
  if (sc.ArraySize > 0) {
    const int currentBar = sc.ArraySize - 1;
    const double timestamp = sc.CurrentSystemDateTime.GetAsDouble();

    // --- Courant (ID:1) — SG1=POC, SG2=VAH, SG3=PVAL ---
    {
      SCFloatArray poc_g3, vah_g3, pval_g3;
      sc.GetStudyArrayUsingID(1, 1, poc_g3);
      sc.GetStudyArrayUsingID(1, 2, vah_g3);
      sc.GetStudyArrayUsingID(1, 3, pval_g3);
      if (poc_g3.GetArraySize() > currentBar && vah_g3.GetArraySize() > currentBar && pval_g3.GetArraySize() > currentBar) {
        auto fix = [&](double x){ return (x > 100000.0) ? NAN : x; };
        double POC = fix(poc_g3[currentBar]);
        double VAH = fix(vah_g3[currentBar]);
        double PVAL = fix(pval_g3[currentBar]);
        if (POC>0 && VAH>0 && PVAL>0) {
          bool corrected=false; std::vector<std::string> corrections;
          if (VAH < PVAL) { corrections.push_back("VAH<PVAL"); double tmp=VAH; VAH=PVAL; PVAL=tmp; corrected=true; }
          if (POC < PVAL || POC > VAH) {
            corrections.push_back("POC_outside_PVAL_VAH");
            if (POC < PVAL) POC = PVAL + (VAH - PVAL) * 0.1; else POC = VAH - (VAH - PVAL) * 0.1;
            corrected=true;
          }
          
          SCString s1;
          s1.Format("{\"t\":%.6f,\"sym\":\"%s\",\"type\":\"volume_profile_graph3\",\"bar\":%d,\"source\":\"graph3_current\",\"poc\":%.2f,\"vah\":%.2f,\"pval\":%.2f,\"study_id\":1,\"corrected\":%s,\"corrections\":\"%s\"}",
                     timestamp, sc.Symbol.GetChars(), currentBar, POC, VAH, PVAL, corrected?"true":"false", corrected?(corrections.size()?corrections[0].c_str():"unknown"):"none");
          WritePerChartDaily(sc.ChartNumber, s1);
          
          SCString s2;
          s2.Format("{\"t\":%.6f,\"sym\":\"%s\",\"type\":\"vva_graph3\",\"i\":%d,\"vah\":%.2f,\"pval\":%.2f,\"vpoc\":%.2f,\"corrected\":%s}",
                    timestamp, sc.Symbol.GetChars(), currentBar, VAH, PVAL, POC, corrected?"true":"false");
          WritePerChartDaily(sc.ChartNumber, s2);
        }
      }
    }

    // --- Précédent (ID:2) — SG1=PPOC, SG2=PVAH, SG3=PVAL ---
    {
      SCFloatArray ppoc_g3, pvah_g3, pval_prev_g3;
      sc.GetStudyArrayUsingID(2, 1, ppoc_g3);
      sc.GetStudyArrayUsingID(2, 2, pvah_g3);
      sc.GetStudyArrayUsingID(2, 3, pval_prev_g3);
      if (ppoc_g3.GetArraySize() > currentBar && pvah_g3.GetArraySize() > currentBar && pval_prev_g3.GetArraySize() > currentBar) {
        auto fix = [&](double x){ return (x > 100000.0) ? NAN : x; };
        double PPOC = fix(ppoc_g3[currentBar]);
        double PVAH = fix(pvah_g3[currentBar]);
        double PVAL = fix(pval_prev_g3[currentBar]);
        if (PPOC>0 && PVAH>0 && PVAL>0) {
          bool corrected=false; std::vector<std::string> corrections;
          if (PVAH < PVAL) { corrections.push_back("PVAH<PVAL"); double tmp=PVAH; PVAH=PVAL; PVAL=tmp; corrected=true; }
          if (PPOC < PVAL || PPOC > PVAH) {
            corrections.push_back("PPOC_outside_PVAL_PVAH");
            if (PPOC < PVAL) PPOC = PVAL + (PVAH - PVAL) * 0.1; else PPOC = PVAH - (PVAH - PVAL) * 0.1;
            corrected=true;
          }
          
          SCString s1;
          s1.Format("{\"t\":%.6f,\"sym\":\"%s\",\"type\":\"volume_profile_previous_graph3\",\"bar\":%d,\"source\":\"graph3_previous\",\"ppoc\":%.2f,\"pvah\":%.2f,\"pval\":%.2f,\"study_id\":2,\"corrected\":%s,\"corrections\":\"%s\"}",
                     timestamp, sc.Symbol.GetChars(), currentBar, PPOC, PVAH, PVAL, corrected?"true":"false", corrected?(corrections.size()?corrections[0].c_str():"unknown"):"none");
          WritePerChartDaily(sc.ChartNumber, s1);
        }
      }
    }
  }
}
