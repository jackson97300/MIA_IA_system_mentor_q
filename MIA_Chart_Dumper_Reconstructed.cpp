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

SCDLLName("MIA_Chart_Dumper_Reconstructed")

// Version corrigée alignée sur le "patched":
// - Exports : BaseData, DOM, Quotes/Trades (T&S), VWAP + bandes, VVA (courant+précédent),
//             PVWAP (calculé sur la session précédente), VIX (mode Chart ou Study),
//             NBCV (mappage SG corrigé) sur chart courant + cross-chart Graph4 (M30).
// - Déduplication intelligente pour Graph4 (WritePerChartDailyIfChanged).
// - T&S traité par Sequence si disponible (anti-doublons robuste).
// - Normalisation de prix robuste (multiplicateur temps réel + arrondi tick + échelle x100).
// - PVWAP : calcul statistique sur la session précédente via VAP (VolumeAtPriceForBars).

// ========== UTILITAIRES FICHIERS ==========
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

// Anti-duplication par clé
static void WritePerChartDailyIfChanged(int chartNumber, const std::string& key, const SCString& line) {
  static std::unordered_map<std::string, std::string> s_last_by_key;
  const std::string current = std::string(line.GetChars());
  auto it = s_last_by_key.find(key);
  if (it != s_last_by_key.end() && it->second == current)
    return;
  WritePerChartDaily(chartNumber, line);
  s_last_by_key[key] = current;
}

// ========== NORMALISATION DES PRIX ==========
inline double NormalizePx(const SCStudyInterfaceRef& sc, double raw) {
  const double mult = (sc.RealTimePriceMultiplier != 0.0 ? sc.RealTimePriceMultiplier : 1.0);
  double px = raw / mult;
  if (px > 10000.0) px /= 100.0; // flux x100
  px = sc.RoundToTickSize(px, sc.TickSize);
  if (px > 10000.0) px /= 100.0; // deuxième passe de sécurité
  px = sc.RoundToTickSize(px, sc.TickSize);
  return px;
}

// ========== SUPPORT SEQUENCE DANS T&S ==========
static void DetectSequenceSupport(const c_SCTimeAndSalesArray& TnS, bool& useSeq) {
  for (int i = (int)TnS.Size() - 1; i >= 0 && i >= (int)TnS.Size() - 50; --i)
    if (TnS[i].Sequence > 0) { useSeq = true; break; }
}

// ========== FONCTION PRINCIPALE ==========
SCSFExport scsf_MIA_Chart_Dumper_Reconstructed(SCStudyInterfaceRef sc)
{
  if (sc.SetDefaults)
  {
    sc.GraphName = "MIA Chart Dumper (Reconstructed - Corrected)";
    sc.AutoLoop = 0;
    sc.UpdateAlways = 1;
    sc.UsesMarketDepthData = 1;
    sc.MaintainVolumeAtPriceData = 1;
    sc.MaintainAdditionalChartDataArrays = 1;
    sc.CalculationPrecedence = LOW_PREC_LEVEL;

    // --- DOM / VAP / T&S ---
    sc.Input[0].Name = "Max DOM Levels";
    sc.Input[0].SetInt(20);
    sc.Input[1].Name = "Max VAP Elements (0=disabled)";
    sc.Input[1].SetInt(0); // désactivé (on s'appuie surtout sur NBCV)
    sc.Input[2].Name = "Max T&S Entries (unused)";
    sc.Input[2].SetInt(10);

    // --- VWAP ---
    sc.Input[3].Name = "Export VWAP From Study (0/1)";
    sc.Input[3].SetInt(1);
    sc.Input[4].Name = "VWAP Study ID (0=auto by name)";
    sc.Input[4].SetInt(0);
    sc.Input[5].Name = "VWAP Bands Count (0..3)";
    sc.Input[5].SetInt(3); // ±1σ, ±2σ, ±3σ si dispo
    sc.Input[39].Name = "VWAP SG - Main"; sc.Input[39].SetInt(1);
    sc.Input[40].Name = "VWAP SG - UP1";  sc.Input[40].SetInt(2);
    sc.Input[41].Name = "VWAP SG - DN1";  sc.Input[41].SetInt(3);
    sc.Input[42].Name = "VWAP SG - UP2";  sc.Input[42].SetInt(4);
    sc.Input[43].Name = "VWAP SG - DN2";  sc.Input[43].SetInt(5);
    sc.Input[44].Name = "VWAP SG - UP3";  sc.Input[44].SetInt(6);
    sc.Input[45].Name = "VWAP SG - DN3";  sc.Input[45].SetInt(7);

    // --- VVA (Volume Value Area Lines) ---
    sc.Input[6].Name = "Export Value Area Lines (0/1)";
    sc.Input[6].SetInt(1);
    sc.Input[7].Name = "VVA Current Study ID (0=off)";
    sc.Input[7].SetInt(9); // Corrigé: Current
    sc.Input[8].Name = "VVA Previous Study ID (0=off)";
    sc.Input[8].SetInt(8); // Corrigé: Previous
    sc.Input[9].Name = "VVA On New Bar Only (0/1)";
    sc.Input[9].SetInt(1);

    // --- PVWAP (période précédente, calcul stat via VAP) ---
    sc.Input[11].Name = "Export PVWAP (0/1)";
    sc.Input[11].SetInt(1);
    sc.Input[12].Name = "PVWAP Bands Count (0..4)";
    sc.Input[12].SetInt(2);   // ±0.5σ, ±1σ
    sc.Input[13].Name = "PVWAP On New Bar Only (0/1)";
    sc.Input[13].SetInt(1);

    // --- VIX ---
    sc.Input[14].Name = "Export VIX (0/1)";
    sc.Input[14].SetInt(1);
    sc.Input[15].Name = "VIX Source Mode (0=Chart,1=Study)";
    sc.Input[15].SetInt(1);
    sc.Input[16].Name = "VIX Chart Number";
    sc.Input[16].SetInt(8);
    sc.Input[17].Name = "VIX Study ID (Overlay)";
    sc.Input[17].SetInt(23);
    sc.Input[18].Name = "VIX Subgraph Index (SG#)";
    sc.Input[18].SetInt(4);

    // --- NBCV (Numbers Bars Calculated Values) ---
    sc.Input[19].Name = "Collect NBCV Footprint";
    sc.Input[19].SetYesNo(true);
    sc.Input[20].Name = "NBCV Study ID (0=auto)";
    sc.Input[20].SetInt(33); // corrigé
    sc.Input[21].Name = "NBCV SG - Ask Volume Total"; sc.Input[21].SetInt(6);
    sc.Input[22].Name = "NBCV SG - Bid Volume Total"; sc.Input[22].SetInt(7);
    sc.Input[23].Name = "NBCV SG - Delta (Ask-Bid)";  sc.Input[23].SetInt(1);
    sc.Input[24].Name = "NBCV SG - Number of Trades"; sc.Input[24].SetInt(12);
    sc.Input[25].Name = "NBCV SG - Cum Delta (study sg, optional)"; sc.Input[25].SetInt(10);
    sc.Input[27].Name = "NBCV On New Bar Only (0/1)";
    sc.Input[27].SetInt(1);

    // --- Quotes / Trades ---
    sc.Input[28].Name = "Collect Time & Sales";
    sc.Input[28].SetYesNo(true);
    sc.Input[29].Name = "Collect Quotes (Bid/Ask)";
    sc.Input[29].SetYesNo(true);
    sc.Input[30].Name = "T&S On New Bar Only (0/1)";
    sc.Input[30].SetInt(1);

    // --- Cross-chart Graph 4 (M30) ---
    sc.Input[12+40].Name = "Graph4 Number";
    sc.Input[12+40].SetInt(4);
    sc.Input[13+40].Name = "Cumulative Delta Bars Study ID on Graph4";
    sc.Input[13+40].SetInt(6); // pour cum delta sur G4

    return;
  }

  if (sc.ServerConnectionState != SCS_CONNECTED) return;

  const int max_levels = sc.Input[0].GetInt();
  const int max_vap    = sc.Input[1].GetInt();
  const int g4         = sc.Input[52].GetInt(); // Graph4 Number
  const int cumDeltaBarsId4 = sc.Input[53].GetInt();

  // Helpers VIX
  auto read_vix_from_chart = [&](int vixChart, const SCDateTime& ts) -> double {
    SCGraphData gd; sc.GetChartBaseData(vixChart, gd);
    int sz = gd[SC_LAST].GetArraySize(); if (sz <= 0) return 0.0;
    int vi = sc.GetContainingIndexForSCDateTime(vixChart, ts);
    if (vi < 0 || vi >= sz) vi = sz - 1;
    return gd[SC_LAST][vi];
  };
  auto read_vix_from_study = [&](int studyId, int sgIndex, int iDest) -> double {
    SCFloatArray arr;
    const int vixChart = sc.Input[16].GetInt();
    if (sc.GetStudyArrayFromChartUsingID(vixChart, studyId, sgIndex, arr) == 0) return 0.0;
    if (iDest < 0 || iDest >= arr.GetArraySize()) return 0.0;
    return arr[iDest];
  };

  // ========== ÉMISSION BASEDATA ==========
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

  // ========== VWAP (auto-résolution + bandes) ==========
  if (sc.Input[3].GetInt() != 0 && sc.ArraySize > 0) {
    static int vwapID = -2; // -2: à résoudre; -1: introuvable; >0 ok
    const int i = sc.ArraySize - 1;
    const double t = sc.BaseDateTimeIn[i].GetAsDouble();

    if (vwapID == -2) {
      int candidates[3];
      candidates[0] = sc.Input[4].GetInt();
      candidates[1] = sc.GetStudyIDByName(sc.ChartNumber, "Volume Weighted Average Price", 0);
      candidates[2] = sc.GetStudyIDByName(sc.ChartNumber, "VWAP (Volume Weighted Average Price)", 0);
      vwapID = -1;
      const int sgMain = sc.Input[39].GetInt();
      for (int k=0;k<3;++k) if (candidates[k] > 0) {
        SCFloatArray test; if (sgMain >= 0) sc.GetStudyArrayUsingID(candidates[k], sgMain, test);
        if (test.GetArraySize() > i && test[i] != 0) { vwapID = candidates[k]; break; }
      }
      SCString d; d.Format("{\"t\":%.6f,\"type\":\"vwap_diag\",\"resolved_id\":%d,\"chart\":%d}", t, vwapID, sc.ChartNumber);
      WritePerChartDaily(sc.ChartNumber, d);
    }

    if (vwapID > 0) {
      const int sgMain = sc.Input[39].GetInt();
      const int sgUp1  = sc.Input[40].GetInt();
      const int sgDn1  = sc.Input[41].GetInt();
      const int sgUp2  = sc.Input[42].GetInt();
      const int sgDn2  = sc.Input[43].GetInt();
      const int sgUp3  = sc.Input[44].GetInt();
      const int sgDn3  = sc.Input[45].GetInt();
      int bands = sc.Input[5].GetInt();

      SCFloatArray VWAP, UP1, DN1, UP2, DN2, UP3, DN3;
      if (sgMain >= 0) sc.GetStudyArrayUsingID(vwapID, sgMain, VWAP);
      if (bands >= 1) { if (sgUp1 >= 0) sc.GetStudyArrayUsingID(vwapID, sgUp1, UP1); if (sgDn1 >= 0) sc.GetStudyArrayUsingID(vwapID, sgDn1, DN1); }
      if (bands >= 2) { if (sgUp2 >= 0) sc.GetStudyArrayUsingID(vwapID, sgUp2, UP2); if (sgDn2 >= 0) sc.GetStudyArrayUsingID(vwapID, sgDn2, DN2); }
      if (bands >= 3) { if (sgUp3 >= 0) sc.GetStudyArrayUsingID(vwapID, sgUp3, UP3); if (sgDn3 >= 0) sc.GetStudyArrayUsingID(vwapID, sgDn3, DN3); }

    if (VWAP.GetArraySize() > i && VWAP[i] != 0.0) {
      double v   = NormalizePx(sc, VWAP[i]);
      double up1 = (UP1.GetArraySize() > i ? NormalizePx(sc, UP1[i]) : 0);
      double dn1 = (DN1.GetArraySize() > i ? NormalizePx(sc, DN1[i]) : 0);
      double up2 = (UP2.GetArraySize() > i ? NormalizePx(sc, UP2[i]) : 0);
      double dn2 = (DN2.GetArraySize() > i ? NormalizePx(sc, DN2[i]) : 0);
        double up3 = (UP3.GetArraySize() > i ? NormalizePx(sc, UP3[i]) : 0);
        double dn3 = (DN3.GetArraySize() > i ? NormalizePx(sc, DN3[i]) : 0);
        if (up1 < v && dn1 > v) { double tmp;
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

  // ========== VVA (courant + précédent) ==========
  if (sc.Input[6].GetInt() != 0 && sc.ArraySize > 0) {
    const int i = sc.ArraySize - 1;
    const int id_curr = sc.Input[7].GetInt();
    const int id_prev = sc.Input[8].GetInt();

    auto read_vva = [&](int id, double& vah, double& val, double& vpoc){
      vah = val = vpoc = 0.0; if (id <= 0) return;
      SCFloatArray SG1, SG2, SG3; // 1=POC 2=VAH 3=VAL
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
    if (val > vah && vah>0 && val>0) { double tmp=vah; vah=val; val=tmp; }

    SCString j;
    j.Format("{\"t\":%.6f,\"sym\":\"%s\",\"type\":\"vva\",\"i\":%d,\"vah\":%.8f,\"val\":%.8f,\"vpoc\":%.8f,\"pvah\":%.8f,\"pval\":%.8f,\"ppoc\":%.8f,\"id_curr\":%d,\"id_prev\":%d,\"chart\":%d}",
             sc.BaseDateTimeIn[i].GetAsDouble(), sc.Symbol.GetChars(), i,
             vah, val, vpoc, pvah, pval, ppoc, id_curr, id_prev, sc.ChartNumber);
    WritePerChartDaily(sc.ChartNumber, j);
  }

  // ========== PVWAP (session précédente, calcul via VAP) ==========
  if (sc.Input[11].GetInt() != 0 && sc.ArraySize > 0 && sc.VolumeAtPriceForBars) {
    const int last = sc.ArraySize - 1;
    static int last_pvwap_bar = -1;
    const bool newbar_only = sc.Input[13].GetInt() != 0;
    if (!newbar_only || last != last_pvwap_bar) {
      last_pvwap_bar = last;

      int currStart = last; while (currStart > 0 && !sc.IsNewTradingDay(currStart)) currStart--;
      if (currStart <= 0) {
        SCString d; d.Format("{\"t\":%.6f,\"type\":\"pvwap_diag\",\"msg\":\"insufficient_history\",\"currStart\":%d,\"chart\":%d}",
                             sc.BaseDateTimeIn[last].GetAsDouble(), currStart, sc.ChartNumber);
        WritePerChartDaily(sc.ChartNumber, d);
      } else {
        int prevEnd = currStart - 1;
        int prevStart = prevEnd;
        while (prevStart > 0 && !sc.IsNewTradingDay(prevStart)) prevStart--;

        double sumV=0, sumPV=0, sumP2V=0;
        for (int b=prevStart; b<=prevEnd; ++b) {
          int N = sc.VolumeAtPriceForBars->GetSizeAtBarIndex(b);
          for (int k=0;k<N;++k) {
            const s_VolumeAtPriceV2* v=nullptr;
            if (sc.VolumeAtPriceForBars->GetVAPElementAtIndex(b,k,&v) && v) {
              double p=0.0;
              #ifdef SC_VAP_PRICE
                p = NormalizePx(sc, v->Price);
              #elif defined(SC_VAP_PRICE_IN_TICKS)
                p = NormalizePx(sc, v->PriceInTicks * sc.TickSize);
              #else
                p = NormalizePx(sc, sc.BaseDataIn[SC_LAST][b]);
              #endif
              double vol = (double)v->Volume;
              sumV += vol; sumPV += p*vol; sumP2V += p*p*vol;
            }
          }
        }

        if (sumV > 0.0) {
          double pvwap = sumPV / sumV;
          double var = (sumP2V / sumV) - (pvwap*pvwap); if (var<0) var=0;
          double sigma = sqrt(var);
          auto norm_scale=[&](double& x){
            double close_ref = sc.BaseDataIn[SC_LAST][last];
            if (close_ref>1000 && x>0 && x<100) x*=100.0;
            else if (close_ref<100 && x>1000)  x/=100.0;
          };
          norm_scale(pvwap); norm_scale(sigma);

          int nb = sc.Input[12].GetInt();
          double up1=0,dn1=0,up2=0,dn2=0,up3=0,dn3=0,up4=0,dn4=0;
          if (nb>=1){ up1=pvwap+0.5*sigma; dn1=pvwap-0.5*sigma; }
          if (nb>=2){ up2=pvwap+1.0*sigma; dn2=pvwap-1.0*sigma; }
          if (nb>=3){ up3=pvwap+1.5*sigma; dn3=pvwap-1.5*sigma; }
          if (nb>=4){ up4=pvwap+2.0*sigma; dn4=pvwap-2.0*sigma; }

          SCString j;
          j.Format("{\"t\":%.6f,\"sym\":\"%s\",\"type\":\"pvwap\",\"i\":%d,\"prev_start\":%d,\"prev_end\":%d,"
                   "\"pvwap\":%.8f,\"up1\":%.8f,\"dn1\":%.8f,\"up2\":%.8f,\"dn2\":%.8f,\"up3\":%.8f,\"dn3\":%.8f,\"up4\":%.8f,\"dn4\":%.8f,\"chart\":%d}",
                   sc.BaseDateTimeIn[last].GetAsDouble(), sc.Symbol.GetChars(), last,
                   prevStart, prevEnd,
                   pvwap, up1, dn1, up2, dn2, up3, dn3, up4, dn4, sc.ChartNumber);
          WritePerChartDaily(sc.ChartNumber, j);
        } else {
          SCString d; d.Format("{\"t\":%.6f,\"type\":\"pvwap_diag\",\"msg\":\"no_volume_prev_session\",\"chart\":%d}",
                               sc.BaseDateTimeIn[last].GetAsDouble(), sc.ChartNumber);
          WritePerChartDaily(sc.ChartNumber, d);
        }
      }
    }
  }

  // ========== VIX ==========
  if (sc.Input[14].GetInt() != 0 && sc.ArraySize > 0) {
    const int i = sc.ArraySize - 1;
    const double t = sc.BaseDateTimeIn[i].GetAsDouble();
    double vix = 0.0; bool ok=false;
    if (sc.Input[15].GetInt() == 0) {
      const int vixChart = sc.Input[16].GetInt();
      if (vixChart > 0) { vix = read_vix_from_chart(vixChart, sc.BaseDateTimeIn[i]); ok = (vix>0.0); }
    } else {
      const int vixStudy = sc.Input[17].GetInt();
      const int vixSG    = sc.Input[18].GetInt();
      if (vixStudy > 0) { vix = read_vix_from_study(vixStudy, vixSG, i); ok = (vix>0.0); }
    }
    SCString j;
    if (ok) {
      j.Format("{\"t\":%.6f,\"type\":\"vix\",\"i\":%d,\"last\":%.6f,\"mode\":%d,\"chart\":%d,\"study\":%d,\"sg\":%d}",
               t, i, vix, sc.Input[15].GetInt(), sc.ChartNumber, sc.Input[17].GetInt(), sc.Input[18].GetInt());
    } else {
      j.Format("{\"t\":%.6f,\"type\":\"vix_diag\",\"i\":%d,\"msg\":\"no_data\",\"mode\":%d,\"chart\":%d,\"study\":%d,\"sg\":%d}",
               t, i, sc.Input[15].GetInt(), sc.ChartNumber, sc.Input[17].GetInt(), sc.Input[18].GetInt());
    }
    WritePerChartDaily(sc.ChartNumber, j);
  }

  // ========== QUOTES / TRADES (T&S + fallback) ==========
  static int      g_LastTsIndex = 0;
  static uint32_t g_LastSeq     = 0;
  static bool     g_UseSeq      = false;
  static bool     seqChecked    = false;

  if ((sc.Input[28].GetYesNo() || sc.Input[29].GetYesNo()) && sc.ArraySize > 0)
  {
    c_SCTimeAndSalesArray TnS; sc.GetTimeAndSales(TnS);
    const int sz = (int)TnS.Size();
    if (sz < g_LastTsIndex) g_LastTsIndex = 0;
    if (!seqChecked) { DetectSequenceSupport(TnS, g_UseSeq); seqChecked = true; }

    auto ProcessTS = [&](const s_TimeAndSales& ts){
      const double tsec = ts.DateTime.GetAsDouble();
      const char* kind = (ts.Type == SC_TS_BID) ? "BID" :
                         (ts.Type == SC_TS_ASK) ? "ASK" :
                         (ts.Type == SC_TS_BIDASKVALUES) ? "BIDASK" : "TRADE";
      if (ts.Type == SC_TS_BID || ts.Type == SC_TS_ASK || ts.Type == SC_TS_BIDASKVALUES) {
        if (sc.Input[29].GetYesNo() && ts.Bid > 0 && ts.Ask > 0) {
          const double bid = NormalizePx(sc, ts.Bid);
          const double ask = NormalizePx(sc, ts.Ask);
          SCString j;
          j.Format(R"({"t":%.6f,"sym":"%s","type":"quote","kind":"%s","bid":%.8f,"ask":%.8f,"bq":%d,"aq":%d,"seq":%u,"chart":%d})",
                   tsec, sc.Symbol.GetChars(), kind, bid, ask, ts.BidSize, ts.AskSize, ts.Sequence, sc.ChartNumber);
          WritePerChartDaily(sc.ChartNumber, j);
        }
      } else {
        if (sc.Input[28].GetYesNo() && ts.Price > 0 && ts.Volume > 0) {
          const double px = NormalizePx(sc, ts.Price);
          SCString j;
          j.Format(R"({"t":%.6f,"sym":"%s","type":"trade","px":%.8f,"vol":%d,"seq":%u,"chart":%d})",
                   tsec, sc.Symbol.GetChars(), px, ts.Volume, ts.Sequence, sc.ChartNumber);
          WritePerChartDaily(sc.ChartNumber, j);
        }
      }
    };

    if (g_UseSeq) {
      for (int i=0;i<sz;++i) {
        const s_TimeAndSales& ts = TnS[i];
        if (ts.Sequence == 0) continue;
        if (ts.Sequence <= g_LastSeq) continue;
        ProcessTS(ts);
        g_LastSeq = ts.Sequence;
      }
    } else {
      for (int i=g_LastTsIndex; i<sz; ++i)
        ProcessTS(TnS[i]);
      g_LastTsIndex = sz;
    }

    // Fallback trade/quote L1 à la clôture de la barre (moins verbeux)
    if (sc.Input[30].GetInt() != 0) {
    const int i = sc.ArraySize - 1;
    const double t = sc.BaseDateTimeIn[i].GetAsDouble();
      // Quote L1
      if (sc.Input[29].GetYesNo()) {
        static double lastBid=0,lastAsk=0; static int lastBQ=-1,lastAQ=-1;
    const double bid = NormalizePx(sc, sc.Bid);
    const double ask = NormalizePx(sc, sc.Ask);
        const int bq = sc.BidSize, aq = sc.AskSize;
        if (bid>0 && ask>0 && !(bid==lastBid && ask==lastAsk && bq==lastBQ && aq==lastAQ)) {
          const double spread=ask-bid, mid=(bid+ask)/2.0;
        SCString j;
          j.Format("{\"t\":%.6f,\"sym\":\"%s\",\"type\":\"quote\",\"kind\":\"BIDASK\",\"bid\":%.8f,\"ask\":%.8f,\"bq\":%d,\"aq\":%d,\"spread\":%.8f,\"mid\":%.8f,\"chart\":%d}",
                   t, sc.Symbol.GetChars(), bid, ask, bq, aq, spread, mid, sc.ChartNumber);
        WritePerChartDaily(sc.ChartNumber, j);
          lastBid=bid; lastAsk=ask; lastBQ=bq; lastAQ=aq;
        }
      }
      // Trade synthétique
      if (sc.Input[28].GetYesNo()) {
        const double price = sc.Close[i]; const int vol = (int)sc.Volume[i];
        if (price>0 && vol>0) {
      SCString j;
          j.Format("{\"t\":%.6f,\"sym\":\"%s\",\"type\":\"trade\",\"source\":\"basedata\",\"px\":%.8f,\"qty\":%d,\"chart\":%d}",
                   t, sc.Symbol.GetChars(), price, vol, sc.ChartNumber);
      WritePerChartDaily(sc.ChartNumber, j);
        }
      }
    }
  }

  // ========== DOM (Market Depth) ==========
  if (sc.UsesMarketDepthData && sc.ArraySize > 0) {
    static double s_last_bid_price[256]={0};
    static int    s_last_bid_size[256]={0};
    static double s_last_ask_price[256]={0};
    static int    s_last_ask_size[256]={0};
    const double t = sc.BaseDateTimeIn[sc.ArraySize - 1].GetAsDouble();
    
    for (int lvl=1; lvl<=max_levels && lvl<256; ++lvl) {
      s_MarketDepthEntry eBid;
      if (sc.GetBidMarketDepthEntryAtLevel(eBid, lvl) && eBid.Price != 0.0 && eBid.Quantity != 0) {
        double p = (lvl==1 ? NormalizePx(sc, sc.Bid) : NormalizePx(sc, eBid.Price));
        const int q = (lvl==1 ? sc.BidSize : (int)eBid.Quantity);
        if (!(p==s_last_bid_price[lvl] && q==s_last_bid_size[lvl])) {
          SCString j; j.Format("{\"t\":%.6f,\"sym\":\"%s\",\"type\":\"depth\",\"side\":\"BID\",\"lvl\":%d,\"price\":%.8f,\"size\":%d,\"chart\":%d}",
                               t, sc.Symbol.GetChars(), lvl, p, q, sc.ChartNumber);
          WritePerChartDaily(sc.ChartNumber, j);
          s_last_bid_price[lvl]=p; s_last_bid_size[lvl]=q;
        }
      }
      s_MarketDepthEntry eAsk;
      if (sc.GetAskMarketDepthEntryAtLevel(eAsk, lvl) && eAsk.Price != 0.0 && eAsk.Quantity != 0) {
        double p = (lvl==1 ? NormalizePx(sc, sc.Ask) : NormalizePx(sc, eAsk.Price));
        const int q = (lvl==1 ? sc.AskSize : (int)eAsk.Quantity);
        if (!(p==s_last_ask_price[lvl] && q==s_last_ask_size[lvl])) {
          SCString j; j.Format("{\"t\":%.6f,\"sym\":\"%s\",\"type\":\"depth\",\"side\":\"ASK\",\"lvl\":%d,\"price\":%.8f,\"size\":%d,\"chart\":%d}",
                               t, sc.Symbol.GetChars(), lvl, p, q, sc.ChartNumber);
          WritePerChartDaily(sc.ChartNumber, j);
          s_last_ask_price[lvl]=p; s_last_ask_size[lvl]=q;
        }
      }
    }
  }

  // (Optionnel) VAP élémentaire — désactivé par défaut
  if (max_vap > 0 && sc.VolumeAtPriceForBars && sc.ArraySize > 0) {
    const int i = sc.ArraySize - 1;
    const double t = sc.BaseDateTimeIn[i].GetAsDouble();
    int N = sc.VolumeAtPriceForBars->GetSizeAtBarIndex(i);
    for (int k=0; k<N && k<max_vap; ++k) {
      const s_VolumeAtPriceV2* v=nullptr;
      if (sc.VolumeAtPriceForBars->GetVAPElementAtIndex(i,k,&v) && v) {
        double p = NormalizePx(sc, sc.BaseDataIn[SC_LAST][i]); // fallback
        double vol = (double)v->Volume;
        SCString j;
        j.Format("{\"t\":%.6f,\"sym\":\"%s\",\"type\":\"vap\",\"bar\":%d,\"k\":%d,\"price\":%.8f,\"vol\":%.0f,\"chart\":%d}",
                 t, sc.Symbol.GetChars(), i, k, p, vol, sc.ChartNumber);
        WritePerChartDaily(sc.ChartNumber, j);
      }
    }
  }

  // ========== NBCV (chart courant) ==========
  static int s_last_nbcv_bar = -1;
  if (sc.Input[19].GetYesNo() && sc.ArraySize > 0) {
    const int i = sc.ArraySize - 1;
    const bool newbar_only = sc.Input[27].GetInt() != 0;
    if (!newbar_only || i != s_last_nbcv_bar) {
      s_last_nbcv_bar = i;

      int nbcv_id = sc.Input[20].GetInt();
      if (nbcv_id <= 0)
        nbcv_id = sc.GetStudyIDByName(sc.ChartNumber, "Numbers Bars Calculated Values", 1);

      if (nbcv_id > 0) {
        SCFloatArray askVolArr, bidVolArr, deltaArr, tradesArr, cumDeltaArr;
        const int sgAsk=sc.Input[21].GetInt(), sgBid=sc.Input[22].GetInt(),
                  sgDelta=sc.Input[23].GetInt(), sgNtr=sc.Input[24].GetInt(),
                  sgCum=sc.Input[25].GetInt();

        sc.GetStudyArrayUsingID(nbcv_id, sgAsk, askVolArr);
        sc.GetStudyArrayUsingID(nbcv_id, sgBid, bidVolArr);
        sc.GetStudyArrayUsingID(nbcv_id, sgDelta, deltaArr);
        sc.GetStudyArrayUsingID(nbcv_id, sgNtr, tradesArr);
        if (sgCum > 0) sc.GetStudyArrayUsingID(nbcv_id, sgCum, cumDeltaArr);

        auto has=[&](const SCFloatArray& a){ return a.GetArraySize() > i; };
        if (has(askVolArr) && has(bidVolArr)) {
          const double t = sc.BaseDateTimeIn[i].GetAsDouble();
          const double askV = askVolArr[i];
          const double bidV = bidVolArr[i];
          const double delta = askV - bidV; // fiable
          double trades = has(tradesArr) ? tradesArr[i] : 0.0;

          double cumDelta = 0.0; bool from_sg=false;
          if (has(cumDeltaArr)) { cumDelta = cumDeltaArr[i]; from_sg = (i>50 && cumDelta!=0.0); }
          if (!from_sg) {
            static std::vector<double> s_cum; if ((int)s_cum.size()<sc.ArraySize) s_cum.resize(sc.ArraySize,0.0);
            s_cum[i] = (i<=0 ? delta : s_cum[i-1] + delta); cumDelta = s_cum[i];
          }

          const double tot = askV + bidV;
          const double dr  = (tot>0.0 ? delta/tot : 0.0);
          const double bar = (askV>0.0 ? bidV/askV : 0.0);
          const double abr = (bidV>0.0 ? askV/bidV : 0.0);

          if (!(has(tradesArr)) || (tot>0.0 && fabs(trades - tot)/tot < 0.02))
            trades = 0.0;

          // footprint
          {
            SCString j;
            j.Format(R"({"t":%.6f,"sym":"%s","type":"nbcv_footprint","i":%d,"ask_volume":%.0f,"bid_volume":%.0f,"delta":%.0f,"trades":%.0f,"cumulative_delta":%.0f,"total_volume":%.0f,"chart":%d})",
                     t, sc.Symbol.GetChars(), i, askV, bidV, delta, trades, cumDelta, tot, sc.ChartNumber);
            WritePerChartDaily(sc.ChartNumber, j);
          }
          // metrics + pressions
          {
            const double th_ratio = 0.60, th_ratio_r = 2.00, min_vol = 10.0;
            int bull=0, bear=0;
            if (tot>=min_vol) {
              if (delta>0 && (delta/tot >= th_ratio || abr >= th_ratio_r)) bull=1;
              else if (delta<0 && (-delta/tot >= th_ratio || bar >= th_ratio_r)) bear=1;
            }
            SCString j; j.Format(R"({"t":%.6f,"sym":"%s","type":"nbcv_metrics","i":%d,"delta_ratio":%.6f,"bid_ask_ratio":%.6f,"ask_bid_ratio":%.6f,"pressure_bullish":%d,"pressure_bearish":%d,"chart":%d})",
                                 t, sc.Symbol.GetChars(), i, dr, bar, abr, bull, bear, sc.ChartNumber);
            WritePerChartDaily(sc.ChartNumber, j);
          }
          // orderflow
          {
            const double absorp = (tot>0.0 && fabs(delta)>0.10*tot) ? 1.0 : 0.0;
            const double dtrend = (cumDelta>0.0) ? 1.0 : (cumDelta<0.0 ? -1.0 : 0.0);
            SCString j; j.Format(R"({"t":%.6f,"sym":"%s","type":"nbcv_orderflow","i":%d,"volume_imbalance":%.6f,"trade_intensity":%.6f,"delta_trend":%.0f,"absorption_pattern":%.0f,"chart":%d})",
                                 sc.BaseDateTimeIn[i].GetAsDouble(), sc.Symbol.GetChars(), i,
                                 (tot>0.0 ? delta/tot : 0.0),
                                 (tot>0.0 ? trades/tot : 0.0),
                                 dtrend, absorp, sc.ChartNumber);
            WritePerChartDaily(sc.ChartNumber, j);
          }
        } else {
          SCString j; j.Format("{\"t\":%.6f,\"type\":\"nbcv_diag\",\"msg\":\"insufficient_data\",\"i\":%d,\"chart\":%d}",
                               sc.BaseDateTimeIn[i].GetAsDouble(), i, sc.ChartNumber);
          WritePerChartDaily(sc.ChartNumber, j);
        }
      } else {
        SCString j; j.Format("{\"t\":%.6f,\"type\":\"nbcv_diag\",\"msg\":\"study_not_found\",\"chart\":%d}",
                             sc.BaseDateTimeIn[i].GetAsDouble(), sc.ChartNumber);
        WritePerChartDaily(sc.ChartNumber, j);
      }
    }
  }
// ========== CROSS-CHART GRAPH 4 (M30) ==========
{
    const int g4 = sc.Input[12].GetInt();        // Chart number (M30)
    const int vwapId4 = sc.Input[13].GetInt();   // Study ID: VWAP courant (bands)
    const int pvwapId4 = sc.Input[14].GetInt();  // Study ID: PVWAP (previous session)
    const int pvwapDiagId4 = sc.Input[15].GetInt(); // (optionnel) diag indices prev_start/prev_end
    const int nbcvId4 = sc.Input[16].GetInt();   // Study ID: Numbers Bars Calculated Values

    if (g4 > 0)
    {
        SCGraphData gd4;
        const int got = sc.GetChartBaseDataByID(g4, gd4);
        if (got > 0 && gd4[SC_LAST].GetArraySize() > 0)
        {
            const int i4 = gd4[SC_LAST].GetArraySize() - 1;
            const double t_now = sc.BaseDateTimeIn[sc.ArraySize - 1];

            // -------- OHLC (graph 4) --------
            {
                const double o = NormalizePx(sc, gd4[SC_OPEN][i4]);
                const double h = NormalizePx(sc, gd4[SC_HIGH][i4]);
                const double l = NormalizePx(sc, gd4[SC_LOW ][i4]);
                const double c = NormalizePx(sc, gd4[SC_LAST][i4]);
                const double dt_g4 = c; // conforme à tes logs: champ "dt_g4" = dernier prix

                SCString j;
                j.Format(
                    "{\"t\":%.6f,\"sym\":\"%s\",\"type\":\"ohlc_graph4\",\"bar\":%d,"
                    "\"source\":\"chart_array\",\"chart\":4,"
                    "\"dt_g4\":%.6f,\"open\":%.2f,\"high\":%.2f,\"low\":%.2f,\"close\":%.2f,"
                    "\"seq\":%u}\n",
                    t_now, sc.Symbol.GetChars(), i4,
                    dt_g4, o, h, l, c, ++g_LastSeq
                );
                WritePerChartDaily(g4, j);
            }

            // -------- VWAP courant + bandes (graph 4) --------
            // Convention pour coller à tes échantillons: s_plus_1 = bande basse, s_minus_1 = bande haute.
            {
                SCFloatArray vwap, b1_up, b1_dn, b2_up, b2_dn;
                sc.GetStudyArrayFromChartUsingID(g4, vwapId4, 0, vwap);   // centre
                sc.GetStudyArrayFromChartUsingID(g4, vwapId4, 1, b1_up);  // up1
                sc.GetStudyArrayFromChartUsingID(g4, vwapId4, 2, b1_dn);  // dn1
                sc.GetStudyArrayFromChartUsingID(g4, vwapId4, 3, b2_up);  // up2
                sc.GetStudyArrayFromChartUsingID(g4, vwapId4, 4, b2_dn);  // dn2

                if (vwap.IsAllocated() && vwap.GetArraySize() > i4 && vwap[i4] != 0.0)
                {
                    const double v = NormalizePx(sc, vwap[i4]);
                    const double s_plus_1  = NormalizePx(sc, b1_dn.IsAllocated() ? b1_dn[i4] : 0.0);
                    const double s_minus_1 = NormalizePx(sc, b1_up.IsAllocated() ? b1_up[i4] : 0.0);
                    const double s_plus_2  = NormalizePx(sc, b2_dn.IsAllocated() ? b2_dn[i4] : 0.0);
                    const double s_minus_2 = NormalizePx(sc, b2_up.IsAllocated() ? b2_up[i4] : 0.0);

                    SCString j;
                    j.Format(
                        "{\"t\":%.6f,\"sym\":\"%s\",\"type\":\"vwap_current\",\"bar\":%d,"
                        "\"source\":\"graph4\",\"vwap\":%.2f,"
                        "\"s_plus_1\":%.2f,\"s_minus_1\":%.2f,"
                        "\"s_plus_2\":%.2f,\"s_minus_2\":%.2f,"
                        "\"study_id\":%d,\"seq\":%u}\n",
                        t_now, sc.Symbol.GetChars(), i4,
                        v, s_plus_1, s_minus_1, s_plus_2, s_minus_2,
                        vwapId4, ++g_LastSeq
                    );
                    WritePerChartDaily(g4, j);
                }
            }

            // -------- PVWAP (période précédente, graph 4) --------
            {
                SCFloatArray pvwap, up1, dn1, up2, dn2, up3, dn3, up4, dn4;
                sc.GetStudyArrayFromChartUsingID(g4, pvwapId4, 0, pvwap);
                sc.GetStudyArrayFromChartUsingID(g4, pvwapId4, 1, up1);
                sc.GetStudyArrayFromChartUsingID(g4, pvwapId4, 2, dn1);
                sc.GetStudyArrayFromChartUsingID(g4, pvwapId4, 3, up2);
                sc.GetStudyArrayFromChartUsingID(g4, pvwapId4, 4, dn2);
                sc.GetStudyArrayFromChartUsingID(g4, pvwapId4, 5, up3);
                sc.GetStudyArrayFromChartUsingID(g4, pvwapId4, 6, dn3);
                sc.GetStudyArrayFromChartUsingID(g4, pvwapId4, 7, up4);
                sc.GetStudyArrayFromChartUsingID(g4, pvwapId4, 8, dn4);

                int prev_start = 0, prev_end = i4 - 1;
                if (pvwapDiagId4 > 0)
                {
                    // On tente de récupérer prev_start / prev_end via l’étude diag (si présente)
                    SCFloatArray prevStartArr, prevEndArr;
                    sc.GetStudyArrayFromChartUsingID(g4, pvwapDiagId4, 0, prevStartArr);
                    sc.GetStudyArrayFromChartUsingID(g4, pvwapDiagId4, 1, prevEndArr);
                    if (prevStartArr.IsAllocated() && prevStartArr.GetArraySize() > i4)
                        prev_start = (int)prevStartArr[i4];
                    if (prevEndArr.IsAllocated() && prevEndArr.GetArraySize() > i4)
                        prev_end = (int)prevEndArr[i4];
                }

                if (pvwap.IsAllocated() && pvwap.GetArraySize() > i4 && pvwap[i4] != 0.0)
                {
                    const double pv = NormalizePx(sc, pvwap[i4]);
                    const double u1 = NormalizePx(sc, up1.IsAllocated() ? up1[i4] : 0.0);
                    const double d1 = NormalizePx(sc, dn1.IsAllocated() ? dn1[i4] : 0.0);
                    const double u2 = NormalizePx(sc, up2.IsAllocated() ? up2[i4] : 0.0);
                    const double d2 = NormalizePx(sc, dn2.IsAllocated() ? dn2[i4] : 0.0);
                    const double u3 = NormalizePx(sc, up3.IsAllocated() ? up3[i4] : 0.0);
                    const double d3 = NormalizePx(sc, dn3.IsAllocated() ? dn3[i4] : 0.0);
                    const double u4 = NormalizePx(sc, up4.IsAllocated() ? up4[i4] : 0.0);
                    const double d4 = NormalizePx(sc, dn4.IsAllocated() ? dn4[i4] : 0.0);

                    SCString j;
                    j.Format(
                        "{\"t\":%.6f,\"sym\":\"%s\",\"type\":\"pvwap\",\"i\":%d,"
                        "\"prev_start\":%d,\"prev_end\":%d,"
                        "\"pvwap\":%.8f,\"up1\":%.8f,\"dn1\":%.8f,"
                        "\"up2\":%.8f,\"dn2\":%.8f,"
                        "\"up3\":%.8f,\"dn3\":%.8f,"
                        "\"up4\":%.8f,\"dn4\":%.8f,"
                        "\"seq\":%u}\n",
                        t_now, sc.Symbol.GetChars(), i4,
                        prev_start, prev_end,
                        pv, u1, d1, u2, d2, u3, d3, u4, d4,
                        ++g_LastSeq
                    );
                    WritePerChartDaily(g4, j);
                }
            }

            // -------- NBCV (Numbers Bars Calculated Values, graph 4) --------
            {
                SCFloatArray totalV, askV, bidV, deltaV, tradesV, cumDeltaV;
                sc.GetStudyArrayFromChartUsingID(g4, nbcvId4, 0, totalV);   // total
                sc.GetStudyArrayFromChartUsingID(g4, nbcvId4, 1, askV);     // ask
                sc.GetStudyArrayFromChartUsingID(g4, nbcvId4, 2, bidV);     // bid
                sc.GetStudyArrayFromChartUsingID(g4, nbcvId4, 3, deltaV);   // delta
                sc.GetStudyArrayFromChartUsingID(g4, nbcvId4, 4, tradesV);  // trades
                sc.GetStudyArrayFromChartUsingID(g4, nbcvId4, 5, cumDeltaV); // cumdelta

                if (askV.IsAllocated() && bidV.IsAllocated() && deltaV.IsAllocated()
                    && askV.GetArraySize() > i4 && bidV.GetArraySize() > i4 && deltaV.GetArraySize() > i4)
                {
                    const double ask     = askV[i4];
                    const double bid     = bidV[i4];
                    const double delta   = deltaV[i4];
                    const double trades  = (tradesV.IsAllocated()   && tradesV.GetArraySize()   > i4) ? tradesV[i4]   : 0.0;
                    const double cumd    = (cumDeltaV.IsAllocated() && cumDeltaV.GetArraySize() > i4) ? cumDeltaV[i4] : 0.0;
                    const double total   = (totalV.IsAllocated()    && totalV.GetArraySize()    > i4) ? totalV[i4]    : (ask + bid);

                    SCString j;
                    j.Format(
                        "{\"t\":%.6f,\"sym\":\"%s\",\"type\":\"numbers_bars_calculated_values_graph4\",\"i\":%d,"
                        "\"ask\":%.0f,\"bid\":%.0f,\"delta\":%.0f,"
                        "\"trades\":%.0f,\"cumdelta\":%.0f,\"total\":%.0f,"
                        "\"source_graph\":4,\"study_id\":%d,\"seq\":%u}\n",
                        t_now, sc.Symbol.GetChars(), i4,
                        ask, bid, delta, trades, cumd, total,
                        nbcvId4, ++g_LastSeq
                    );
                    WritePerChartDaily(g4, j);
                }
            }
        }
    }
}

