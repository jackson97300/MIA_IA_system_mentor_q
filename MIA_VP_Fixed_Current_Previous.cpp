// Patch corrigé pour séparer Current/Previous et uniformiser l'émission
#include "sierrachart.h"
#include <time.h>
#include <cmath>
SCDLLName("MIA_VP_Fixed_Current_Previous")

// ---------- Utilitaires ----------
static double NormalizePx(SCStudyInterfaceRef sc, double px) {
  if (px <= 0.0) return 0.0;
  const double ts = sc.TickSize > 0 ? sc.TickSize : 0.25;
  const double ticks = floor(px / ts + 0.5);
  return ticks * ts;
}

// Fonction pour écrire dans les fichiers par chart (comme dans vos autres scripts)
static void WritePerChartDaily(int chartNumber, const SCString& line) {
  time_t now = time(NULL);
  struct tm* lt = localtime(&now);
  int y = lt ? (lt->tm_year + 1900) : 1970;
  int m = lt ? (lt->tm_mon + 1) : 1;
  int d = lt ? lt->tm_mday : 1;
  SCString filename;
  filename.Format("chart_%d_%04d%02d%02d.jsonl", chartNumber, y, m, d);
  
  FILE* f = fopen(filename.GetChars(), "a");
  if (f) { 
    fprintf(f, "%s\n", line.GetChars()); 
    fclose(f); 
  }
}

// Structure pour stocker les profils VP
struct VolumeProfile {
  double poc, vah, val;
  bool valid;
  int barIndex;
  
  VolumeProfile() : poc(0), vah(0), val(0), valid(false), barIndex(-1) {}
  
  void set(double p, double h, double l, int bar) {
    poc = p; vah = h; val = l; valid = true; barIndex = bar;
  }
  
  void clear() {
    poc = vah = val = 0; valid = false; barIndex = -1;
  }
};

// Auto-détection mapping VP (POC/VAH/VAL)
static bool ReadVPFromChart(
  SCStudyInterfaceRef sc,
  int chartNum, int studyID, int barIndex,
  double& poc, double& vah, double& val)
{
  poc = vah = val = 0.0;
  if (chartNum <= 0 || studyID <= 0 || barIndex < 0) return false;

  auto read_triplet = [&](int iPOC, int iVAH, int iVAL,
                          double& oPOC, double& oVAH, double& oVAL)->bool {
    SCFloatArray sgPOC, sgVAH, sgVAL;
    sc.GetStudyArrayFromChartUsingID(chartNum, studyID, iPOC, sgPOC);
    sc.GetStudyArrayFromChartUsingID(chartNum, studyID, iVAH, sgVAH);
    sc.GetStudyArrayFromChartUsingID(chartNum, studyID, iVAL, sgVAL);
    if (sgPOC.GetArraySize() == 0) return false;
    int i = barIndex;
    if (i >= sgPOC.GetArraySize()) i = sgPOC.GetArraySize() - 1;
    oPOC = (i < sgPOC.GetArraySize()) ? sgPOC[i] : 0.0;
    oVAH = (i < sgVAH.GetArraySize()) ? sgVAH[i] : 0.0;
    oVAL = (i < sgVAL.GetArraySize()) ? sgVAL[i] : 0.0;
    return (oPOC > 0.0 && oVAH > 0.0 && oVAL > 0.0);
  };

  double POC=0, VAH=0, VAL=0;
  bool ok = read_triplet(1,2,3, POC,VAH,VAL); // essai (1,2,3)
  if (!ok) ok = read_triplet(0,1,2, POC,VAH,VAL); // fallback (0,1,2)
  if (!ok) return false;

  poc = NormalizePx(sc, POC);
  vah = NormalizePx(sc, VAH);
  val = NormalizePx(sc, VAL);
  if (vah < val) std::swap(vah, val);
  return true;
}

static void ProcessChartVP(
  SCStudyInterfaceRef sc,
  int chartNum, int studyCurr, int studyPrev,
  int& lastProcessedIndex, bool debug)
{
  SCFloatArray lastArr;
  sc.GetChartArray(chartNum, SC_LAST, lastArr);
  if (lastArr.GetArraySize() == 0) return;
  const int iLast = lastArr.GetArraySize() - 1;
  if (iLast < 0) return;

  // 1 ligne par nouvelle barre
  if (lastProcessedIndex == iLast) return;
  lastProcessedIndex = iLast;

  const SCDateTime now = sc.CurrentSystemDateTime;
  const double tnow = now.GetAsDouble();

  // CORRECTION: Séparer correctement Current et Previous
  static VolumeProfile vp_curr, vp_prev;
  static bool has_prev = false;
  
  // Lire le nouveau profil courant
  double poc=0, vah=0, val=0;
  bool okCurr = ReadVPFromChart(sc, chartNum, studyCurr, iLast, poc, vah, val);
  
  if (okCurr) {
    // Sauvegarder l'ancien current dans previous AVANT de mettre à jour current
    if (vp_curr.valid) {
      vp_prev = vp_curr;  // Copie profonde
      has_prev = true;
    }
    
    // Mettre à jour le current
    vp_curr.set(poc, vah, val, iLast);
    
    // Écrire VVA (compat) avec current seulement
    SCString line;
    line.Format("{\"t\":%.6f,\"type\":\"vva\",\"i\":%d,"
                "\"vah\":%.8f,\"val\":%.8f,\"vpoc\":%.8f,"
                "\"chart\":%d}",
                tnow, iLast, vah, val, poc, chartNum);
    WritePerChartDaily(chartNum, line);
    
    // Écrire Volume Profile Current
    SCString l2;
    l2.Format("{\"t\":%.6f,\"type\":\"volume_profile\",\"chart\":%d,\"i\":%d,"
              "\"scope\":\"current\",\"poc\":%.8f,\"vah\":%.8f,\"val\":%.8f}",
              tnow, chartNum, iLast, poc, vah, val);
    WritePerChartDaily(chartNum, l2);
    
    // Écrire Volume Profile Previous SEULEMENT si disponible et différent
    if (has_prev && vp_prev.valid) {
      // Vérifier que previous est différent de current (invariant)
      if (vp_prev.poc != vp_curr.poc || vp_prev.vah != vp_curr.vah || vp_prev.val != vp_curr.val) {
        SCString l3;
        l3.Format("{\"t\":%.6f,\"type\":\"volume_profile\",\"chart\":%d,\"i\":%d,"
                  "\"scope\":\"previous\",\"poc\":%.8f,\"vah\":%.8f,\"val\":%.8f}",
                  tnow, chartNum, iLast, vp_prev.poc, vp_prev.vah, vp_prev.val);
        WritePerChartDaily(chartNum, l3);
      }
    }
    
    // Prévis VP (bias + targets)
    const double last = NormalizePx(sc, lastArr[iLast]);
    const double range = fmax(sc.TickSize, vah - val);
    const bool above = last > vah;
    const bool below = last < val;

    const char* bias =
      above ? "breakout_up" :
      below ? "breakout_down" : "inside_VA";

    const double tgt1 = poc;                                  // aimant naturel
    const double tgt2 = above ? vah : (below ? val : poc);    // retest

    // Confiance simple
    double conf = 0.0;
    if (!above && !below) {
      conf = 1.0 - fabs(last - poc) / (0.5 * range);  // plus proche du VPOC => + de confiance mean-revert
    } else {
      const double d = fabs(last - (above ? vah : val));
      conf = fmin(1.0, d / range);
    }

    SCString sig;
    sig.Format("{\"t\":%.6f,\"type\":\"vp_signal\",\"chart\":%d,\"i\":%d,"
               "\"last\":%.8f,\"vah\":%.8f,\"val\":%.8f,\"vpoc\":%.8f,"
               "\"bias\":\"%s\",\"targets\":[%.8f,%.8f],\"confidence\":%.3f}",
               tnow, chartNum, iLast, last, vah, val, poc, bias, tgt1, tgt2, conf);
    WritePerChartDaily(chartNum, sig);
  }

  if (debug) {
    SCString dbg;
    dbg.Format("{\"t\":%.6f,\"type\":\"debug\",\"msg\":\"processed\",\"chart\":%d,"
               "\"i\":%d,\"okCurr\":%d,\"hasPrev\":%d}", tnow, chartNum, iLast, okCurr?1:0, has_prev?1:0);
    WritePerChartDaily(chartNum, dbg);
  }
}

// ---------- Study principal ----------
SCSFExport scsf_MIA_VP_Fixed_Current_Previous(SCStudyInterfaceRef sc)
{
  if (sc.SetDefaults) {
    sc.GraphName = "MIA VP Fixed Current/Previous";
    sc.AutoLoop = 0;                      // on gère 1 écriture par nouvelle barre
    sc.GraphRegion = 0;

    sc.Input[0].Name = "Chart 3 Number";
    sc.Input[0].SetInt(3);
    sc.Input[1].Name = "Chart 4 Number";
    sc.Input[1].SetInt(4);

    sc.Input[2].Name = "Chart3 StudyID Current";
    sc.Input[2].SetInt(8);
    sc.Input[3].Name = "Chart3 StudyID Previous";
    sc.Input[3].SetInt(9);

    sc.Input[4].Name = "Chart4 StudyID Current";
    sc.Input[4].SetInt(8);
    sc.Input[5].Name = "Chart4 StudyID Previous";
    sc.Input[5].SetInt(9);

    sc.Input[6].Name = "Debug (0/1)";
    sc.Input[6].SetYesNo(false);

    return;
  }

  const int chart3 = sc.Input[0].GetInt();
  const int chart4 = sc.Input[1].GetInt();
  const int s3c    = sc.Input[2].GetInt();
  const int s3p    = sc.Input[3].GetInt();
  const int s4c    = sc.Input[4].GetInt();
  const int s4p    = sc.Input[5].GetInt();
  const bool debug = sc.Input[6].GetYesNo();

  // Persistents: dernier index traité par chart
  int& lastIdx3 = sc.GetPersistentInt(101);
  int& lastIdx4 = sc.GetPersistentInt(102);
  if (sc.IsFullRecalculation) { lastIdx3 = -1; lastIdx4 = -1; }

  // Traite les deux charts
  if (chart3 > 0) ProcessChartVP(sc, chart3, s3c, s3p, lastIdx3, debug);
  if (chart4 > 0) ProcessChartVP(sc, chart4, s4c, s4p, lastIdx4, debug);
}
