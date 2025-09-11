#include "sierrachart.h"
#ifdef _WIN32
  #include <windows.h>
#endif
#include <time.h>
#include <cmath>

SCDLLName("MIA_VP_Charts3_4_Minimal")

// ===== Utils sortie =====
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
  if (FILE* f = fopen(filename.GetChars(), "a")) { fprintf(f, "%s\n", line.GetChars()); fclose(f); }
}

// Prix → tick & anti sur-scaling
static inline double NormalizePx(const SCStudyInterfaceRef& sc, double px) {
  if (px > 100000.0) px /= 100.0;
  return sc.RoundToTickSize(px, sc.TickSize);
}

// Lit VP (POC/VAH/VAL) depuis un chart cible (via Study ID)
static bool ReadVPFromChart(
  SCStudyInterfaceRef sc,
  int chartNum, int studyID, int barIndex,
  double& poc, double& vah, double& val)
{
  poc = vah = val = 0.0;
  if (chartNum <= 0 || studyID <= 0 || barIndex < 0) return false;

  auto read_triplet = [&](int iPOC, int iVAH, int iVAL, double& oPOC, double& oVAH, double& oVAL)->bool {
    SCFloatArray sgPOC, sgVAH, sgVAL;
    sc.GetStudyArrayFromChartUsingID(chartNum, studyID, iPOC, sgPOC);
    sc.GetStudyArrayFromChartUsingID(chartNum, studyID, iVAH, sgVAH);
    sc.GetStudyArrayFromChartUsingID(chartNum, studyID, iVAL, sgVAL);
    if (sgPOC.GetArraySize() == 0) return false;
    int i = barIndex; if (i >= sgPOC.GetArraySize()) i = sgPOC.GetArraySize() - 1;
    oPOC = (i < sgPOC.GetArraySize()) ? sgPOC[i] : 0.0;
    oVAH = (i < sgVAH.GetArraySize()) ? sgVAH[i] : 0.0;
    oVAL = (i < sgVAL.GetArraySize()) ? sgVAL[i] : 0.0;
    return oPOC > 0.0 && oVAH > 0.0 && oVAL > 0.0;
  };

  double POC=0, VAH=0, VAL=0;
  // Tentative 1 : (1,2,3)
  bool ok = read_triplet(1,2,3, POC,VAH,VAL);
  // Fallback : (0,1,2)
  if (!ok) ok = read_triplet(0,1,2, POC,VAH,VAL);

  if (sc.Input[7].GetYesNo()) {
    SCString debug;
    debug.Format("{\"t\":%.6f,\"type\":\"debug\",\"msg\":\"vp_mapping\",\"chart\":%d,\"study\":%d,"
                 "\"try_123_then_012\":true,\"ok\":%d,\"poc\":%.6f,\"vah\":%.6f,\"val\":%.6f}",
                 sc.CurrentSystemDateTime.GetAsDouble(), chartNum, studyID, ok?1:0, POC, VAH, VAL);
    WritePerChartDaily(chartNum, debug);  // chartNum (pas sc.ChartNumber)
  }

  if (!ok) return false;

  poc = NormalizePx(sc, POC);
  vah = NormalizePx(sc, VAH);
  val = NormalizePx(sc, VAL);
  if (vah < val) std::swap(vah, val);
  return true;
}

// Lit l'index du dernier bar d'un chart
static int LastBarIndexOfChart(SCStudyInterfaceRef sc, int chartNum) {
  SCFloatArray o;
  sc.GetChartArray(chartNum, SC_OPEN, o);
  if (o.GetArraySize() == 0) return -1;
  return o.GetArraySize() - 1;
}

SCSFExport scsf_MIA_VolumeProfile_Charts3_4(SCStudyInterfaceRef sc)
{
  if (sc.SetDefaults)
  {
    sc.GraphName = "MIA – VP Charts 3 & 4 (current + previous)";
    sc.AutoLoop = 0;
    sc.UpdateAlways = 1;
    sc.MaintainAdditionalChartDataArrays = 1;

    // CHARTS cibles
    sc.Input[0].Name = "Chart A Number";            sc.Input[0].SetInt(3);
    sc.Input[1].Name = "Chart B Number";            sc.Input[1].SetInt(4);

    // Studies VP (Current / Previous) pour chaque chart
    sc.Input[2].Name = "Chart A VP Current StudyID";  sc.Input[2].SetInt(9);
    sc.Input[3].Name = "Chart A VP Previous StudyID"; sc.Input[3].SetInt(8);

    sc.Input[4].Name = "Chart B VP Current StudyID";  sc.Input[4].SetInt(9);
    sc.Input[5].Name = "Chart B VP Previous StudyID"; sc.Input[5].SetInt(8);

    sc.Input[6].Name = "Emit On New Bar Only (0/1)";  sc.Input[6].SetYesNo(true);
    sc.Input[7].Name = "Debug Mode (0/1)";            sc.Input[7].SetYesNo(false);

    return;
  }

  if (sc.ServerConnectionState != SCS_CONNECTED) {
    if (sc.Input[7].GetYesNo()) {
      SCString debug;
      debug.Format("{\"t\":%.6f,\"type\":\"debug\",\"msg\":\"not_connected\"}", 
                   sc.CurrentSystemDateTime.GetAsDouble());
      WritePerChartDaily(sc.ChartNumber, debug);
    }
    return;
  }

  const int chartA = sc.Input[0].GetInt();
  const int chartB = sc.Input[1].GetInt();
  const bool newbar_only = sc.Input[6].GetYesNo();

  static int last_barA = -1, last_barB = -1;

  auto export_for_chart = [&](int chartNum, int idCurr, int idPrev, int& last_bar_mem)
  {
    int iLast = LastBarIndexOfChart(sc, chartNum);
    if (iLast < 0) {
      if (sc.Input[7].GetYesNo()) {
        SCString debug;
        debug.Format("{\"t\":%.6f,\"type\":\"debug\",\"msg\":\"no_bars\",\"chart\":%d}", 
                     sc.CurrentSystemDateTime.GetAsDouble(), chartNum);
        WritePerChartDaily(chartNum, debug);
      }
      return;
    }

    if (newbar_only && iLast == last_bar_mem) return;
    last_bar_mem = iLast;

    // Heure "maintenant" pour timestamp homogène
    double tnow = sc.CurrentSystemDateTime.GetAsDouble();

    // Debug: log de démarrage
    if (sc.Input[7].GetYesNo()) {
      SCString debug;
      debug.Format("{\"t\":%.6f,\"type\":\"debug\",\"msg\":\"processing\",\"chart\":%d,\"bar\":%d,\"curr_id\":%d,\"prev_id\":%d}", 
                   tnow, chartNum, iLast, idCurr, idPrev);
      WritePerChartDaily(chartNum, debug);
    }

    // CORRECTION: Variables statiques par chart (pas partagées)
    static double prev_poc_A=0, prev_vah_A=0, prev_val_A=0;
    static bool has_previous_A = false;
    static double prev_poc_B=0, prev_vah_B=0, prev_val_B=0;
    static bool has_previous_B = false;
    
    // Sélectionner les variables selon le chart
    double* prev_poc = (chartNum == chartA) ? &prev_poc_A : &prev_poc_B;
    double* prev_vah = (chartNum == chartA) ? &prev_vah_A : &prev_vah_B;
    double* prev_val = (chartNum == chartA) ? &prev_val_A : &prev_val_B;
    bool* has_previous = (chartNum == chartA) ? &has_previous_A : &has_previous_B;
    
    // CURRENT
    double poc=0, vah=0, val=0;
    if (ReadVPFromChart(sc, chartNum, idCurr, iLast, poc, vah, val)) {
      // Sauvegarder l'ancien current dans previous AVANT de mettre à jour
      if (*has_previous) {
        *prev_poc = poc; *prev_vah = vah; *prev_val = val;
      }
      
      SCString s;
      s.Format("{\"t\":%.6f,\"type\":\"volume_profile\",\"chart\":%d,\"bar\":%d,"
               "\"scope\":\"current\",\"poc\":%.8f,\"vah\":%.8f,\"val\":%.8f,\"study_id\":%d}",
               tnow, chartNum, iLast, poc, vah, val, idCurr);
      WritePerChartDaily(chartNum, s);

      // Ligne "VVA" utile
      SCString v;
      v.Format("{\"t\":%.6f,\"type\":\"vva\",\"chart\":%d,\"i\":%d,\"vah\":%.8f,\"val\":%.8f,\"vpoc\":%.8f}",
               tnow, chartNum, iLast, vah, val, poc);
      WritePerChartDaily(chartNum, v);

      // Prévisions VP (bias + targets)
      auto last_price_of_chart = [&](int cnum)->double{
        SCFloatArray lastArr;
        sc.GetChartArray(cnum, SC_LAST, lastArr);
        if (lastArr.GetArraySize() == 0) return 0.0;
        return lastArr[lastArr.GetArraySize()-1];
      };
      double last = NormalizePx(sc, last_price_of_chart(chartNum));

      if (last > 0.0) {
        const char* bias = "inside_VA";
        if (last > vah) bias = "breakout_up";
        else if (last < val) bias = "breakout_down";

        // targets simples
        double tgt1 = poc;                // aimant naturel
        double tgt2 = poc;                // 2e target simple (même que tgt1)

        SCString sig;
        sig.Format("{\"t\":%.6f,\"type\":\"vp_signal\",\"chart\":%d,\"i\":%d,"
                   "\"last\":%.8f,\"vah\":%.8f,\"val\":%.8f,\"vpoc\":%.8f,"
                   "\"bias\":\"%s\",\"targets\":[%.8f,%.8f]}",
                   tnow, chartNum, iLast, last, vah, val, poc, bias, tgt1, tgt2);
        WritePerChartDaily(chartNum, sig);
      }
      
      // Marquer qu'on a maintenant un previous
      *has_previous = true;
    } else {
      if (sc.Input[7].GetYesNo()) {
        SCString debug;
        debug.Format("{\"t\":%.6f,\"type\":\"debug\",\"msg\":\"current_vp_failed\",\"chart\":%d,\"study_id\":%d}", 
                     tnow, chartNum, idCurr);
        WritePerChartDaily(chartNum, debug);
      }
    }

    // PREVIOUS - utiliser les valeurs sauvegardées
    if (*has_previous) {
      SCString s2;
      s2.Format("{\"t\":%.6f,\"type\":\"volume_profile\",\"chart\":%d,\"bar\":%d,"
                "\"scope\":\"previous\",\"poc\":%.8f,\"vah\":%.8f,\"val\":%.8f,\"study_id\":%d}",
                tnow, chartNum, iLast, *prev_poc, *prev_vah, *prev_val, idCurr);
      WritePerChartDaily(chartNum, s2);
    }
  };

  export_for_chart(chartA, sc.Input[2].GetInt(), sc.Input[3].GetInt(), last_barA);
  export_for_chart(chartB, sc.Input[4].GetInt(), sc.Input[5].GetInt(), last_barB);
}
