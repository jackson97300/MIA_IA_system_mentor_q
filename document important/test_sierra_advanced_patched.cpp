#include "sierrachart.h"
#ifdef _WIN32
  #include <windows.h>
#endif

SCDLLName("Test_Sierra_Advanced_Patched")

// Test bench complet : BaseDataIn, DOM live, DOM historique, VAP, T&S.
// Logs séparés pour faciliter le debug.

static void WriteLine(const char* filename, const SCString& line) {
#ifdef _WIN32
  CreateDirectoryA("D:\\MIA_IA_system", NULL);
#endif
  FILE* f = fopen(filename, "a");
  if (f) { fprintf(f, "%s\n", line.GetChars()); fclose(f); }
}

SCSFExport scsf_Test_Sierra_Advanced_Patched(SCStudyInterfaceRef sc)
{
  if (sc.SetDefaults)
  {
    sc.GraphName = "Test Sierra Advanced (Patched)";
    sc.AutoLoop = 0;
    sc.UpdateAlways = 1;
    sc.UsesMarketDepthData = 1;
    sc.MaintainVolumeAtPriceData = 1;
    sc.MaintainAdditionalChartDataArrays = 1;
    sc.MaintainHistoricalMarketDepthData = 1;

    sc.Input[0].Name = "Max DOM Levels";
    sc.Input[0].SetInt(20);
    sc.Input[1].Name = "Dump Historical DOM";
    sc.Input[1].SetInt(0);
    return;
  }

  if (sc.ServerConnectionState != SCS_CONNECTED) return;

  const int max_levels = sc.Input[0].GetInt();
  const bool dump_hist = sc.Input[1].GetInt() != 0;

  // ---- Params diag (une fois au démarrage par chart) ----
  static bool logged = false;
  if (!logged) {
    logged = true;
    // Utiliser GetAsDouble() pour l'horodatage (compatible avec toutes les versions)
    double timestamp = sc.CurrentSystemDateTime.GetAsDouble();
    SCString diag;
    diag.Format("{\"t\":%.6f,\"chart\":%d,\"sym\":\"%s\",\"RTMultiplier\":%.6f,\"MDLevels\":%d,\"HasVAP\":%d,\"HasHistMD\":%d}",
      timestamp, sc.ChartNumber, sc.Symbol.GetChars(), sc.RealTimePriceMultiplier, max_levels, (int)sc.MaintainVolumeAtPriceData, (int)sc.MaintainHistoricalMarketDepthData);
    WriteLine("D:\\MIA_IA_system\\advanced_diag.log", diag);
  }

  // ---- BaseDataIn + Bid/AskVol (nouvelle barre uniquement) ----
  static int last_i = -1;
  if (sc.ArraySize > 0) {
    int i = sc.ArraySize - 1;
    if (i != last_i) {
      last_i = i;
      // Utiliser GetAsDouble() pour l'horodatage
      double timestamp = sc.BaseDateTimeIn[i].GetAsDouble();
      double o = sc.BaseDataIn[SC_OPEN][i];
      double h = sc.BaseDataIn[SC_HIGH][i];
      double l = sc.BaseDataIn[SC_LOW][i];
      double c = sc.BaseDataIn[SC_LAST][i];
      double v = sc.BaseDataIn[SC_VOLUME][i];
      double bvol = sc.BaseDataIn[SC_BIDVOL][i];
      double avol = sc.BaseDataIn[SC_ASKVOL][i];

      SCString j;
      j.Format("{\"t\":%.6f,\"type\":\"basedata\",\"i\":%d,\"o\":%.8f,\"h\":%.8f,\"l\":%.8f,\"c\":%.8f,\"v\":%.0f,\"bidvol\":%.0f,\"askvol\":%.0f}",
        timestamp, i, o,h,l,c,v,bvol,avol);
      WriteLine("D:\\MIA_IA_system\\advanced_basedata.log", j);
    }
  }

  // ---- DOM live ----
  if (sc.UsesMarketDepthData) {
    for (int lvl = 0; lvl < max_levels; ++lvl) {
      s_MarketDepthEntry be, ae;
      bool gotB = sc.GetBidMarketDepthEntryAtLevel(be, lvl);
      bool gotA = sc.GetAskMarketDepthEntryAtLevel(ae, lvl);
      if (!gotB && !gotA) break;

      if (gotB && be.Quantity > 0) {
        double p = be.Price * sc.RealTimePriceMultiplier;
        // Utiliser GetAsDouble() pour l'horodatage
        double timestamp = sc.CurrentSystemDateTime.GetAsDouble();
        SCString j;
        j.Format("{\"t\":%.6f,\"type\":\"dom\",\"side\":\"BID\",\"lvl\":%d,\"p\":%.8f,\"q\":%.0f}", timestamp, lvl, p, be.Quantity);
        WriteLine("D:\\MIA_IA_system\\advanced_dom_live.log", j);
      }
      if (gotA && ae.Quantity > 0) {
        double p = ae.Price * sc.RealTimePriceMultiplier;
        // Utiliser GetAsDouble() pour l'horodatage
        double timestamp = sc.CurrentSystemDateTime.GetAsDouble();
        SCString j;
        j.Format("{\"t\":%.6f,\"type\":\"dom\",\"side\":\"ASK\",\"lvl\":%d,\"p\":%.8f,\"q\":%.0f}", timestamp, lvl, p, ae.Quantity);
        WriteLine("D:\\MIA_IA_system\\advanced_dom_live.log", j);
      }
    }
  }

  // ---- VAP (dernier bar, 5 premiers éléments) ----
  if (sc.MaintainVolumeAtPriceData && sc.VolumeAtPriceForBars && sc.ArraySize > 0) {
    int bar = sc.ArraySize - 1;
    int vapSize = sc.VolumeAtPriceForBars->GetSizeAtBarIndex(bar);
    for (int k = 0; k < vapSize && k < 5; ++k) {
      const s_VolumeAtPriceV2* v = nullptr;
      if (sc.VolumeAtPriceForBars->GetVAPElementAtIndex(bar, k, &v) && v) {
        // Utiliser le bon nom de membre pour le prix (peut varier selon la version de Sierra Chart)
        double price = 0.0;
        // Essayer différents noms de membres possibles
        #ifdef SC_VAP_PRICE
          price = v->Price * sc.RealTimePriceMultiplier;
        #elif defined(SC_VAP_PRICE_IN_TICKS)
          price = v->PriceInTicks * sc.TickSize * sc.RealTimePriceMultiplier;
        #else
          // Fallback : utiliser le prix calculé à partir de l'index de barre
          price = sc.BaseDataIn[SC_LAST][bar] * sc.RealTimePriceMultiplier;
        #endif
        
        double timestamp = sc.CurrentSystemDateTime.GetAsDouble();
        SCString j;
        j.Format("{\"t\":%.6f,\"sym\":\"%s\",\"type\":\"vap\",\"bar\":%d,\"k\":%d,\"price\":%.8f,\"vol\":%d}",
          timestamp, sc.Symbol.GetChars(), bar, k, price, v->Volume);
        WriteLine("D:\\MIA_IA_system\\advanced_vap.log", j);
      }
    }
  }

  // ---- T&S (dernier) ----
  c_SCTimeAndSalesArray tns;
  // GetTimeAndSales ne retourne pas de bool, juste void
  sc.GetTimeAndSales(tns);
  int n = (int)tns.Size();
  if (n > 0) {
    const s_TimeAndSales& last = tns[n-1];
    const char* kind = (last.Type == SC_TS_BID) ? "BID" :
                       (last.Type == SC_TS_ASK) ? "ASK" :
                       (last.Type == SC_TS_BIDASKVALUES) ? "BIDASK" : "TRADE";
    double px = last.Price * sc.RealTimePriceMultiplier;
    // Utiliser GetAsDouble() pour l'horodatage
    double timestamp = last.DateTime.GetAsDouble();
    SCString j;
    j.Format("{\"t\":%.6f,\"type\":\"ts\",\"kind\":\"%s\",\"px\":%.8f,\"vol\":%d,\"seq\":%u}", timestamp, kind, px, last.Volume, last.Sequence);
    WriteLine("D:\\MIA_IA_system\\advanced_ts.log", j);
  }

  // ---- DOM historique (optionnel) ----
  if (dump_hist && sc.MaintainHistoricalMarketDepthData && sc.ArraySize > 0) {
    int i = sc.ArraySize - 1;
    c_ACSILDepthBars* pDepth = sc.GetMarketDepthBars();
    if (pDepth && pDepth->DepthDataExistsAt(i)) {
      int tickIdx = pDepth->GetBarLowestPriceTickIndex(i);
      do {
        double price = pDepth->TickIndexToPrice(tickIdx) * sc.RealTimePriceMultiplier;
        int bidMax = pDepth->GetMaxBidQuantity(i, tickIdx);
        int askMax = pDepth->GetMaxAskQuantity(i, tickIdx);

        if (bidMax > 0) {
          // Utiliser GetAsDouble() pour l'horodatage
          double timestamp = sc.BaseDateTimeIn[i].GetAsDouble();
          SCString j;
          j.Format("{\"t\":%.6f,\"type\":\"dom_hist\",\"side\":\"BID\",\"bar\":%d,\"price\":%.8f,\"qmax\":%d}", timestamp, i, price, bidMax);
          WriteLine("D:\\MIA_IA_system\\advanced_dom_hist.log", j);
        }
        if (askMax > 0) {
          // Utiliser GetAsDouble() pour l'horodatage
          double timestamp = sc.BaseDateTimeIn[i].GetAsDouble();
          SCString j;
          j.Format("{\"t\":%.6f,\"type\":\"dom_hist\",\"side\":\"ASK\",\"bar\":%d,\"price\":%.8f,\"qmax\":%d}", timestamp, i, price, askMax);
          WriteLine("D:\\MIA_IA_system\\advanced_dom_hist.log", j);
        }
      } while (pDepth->GetNextHigherPriceTickIndex(i, tickIdx));
    }
  }
}
