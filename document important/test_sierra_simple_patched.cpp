#include "sierrachart.h"
#ifdef _WIN32
  #include <windows.h>
#endif

SCDLLName("Test_Sierra_Simple_Patched")

// Smoke test ultra-léger : vérifie Bar/DOM/T&S et écrit 3 logs.

static void WriteLine(const SCString& path, const SCString& line) {
#ifdef _WIN32
  CreateDirectoryA("D:\\MIA_IA_system", NULL);
#endif
  FILE* f = fopen(path.GetChars(), "a");
  if (f) {
    fprintf(f, "%s\n", line.GetChars());
    fclose(f);
  }
}

SCSFExport scsf_Test_Sierra_Simple_Patched(SCStudyInterfaceRef sc)
{
  if (sc.SetDefaults)
  {
    sc.GraphName = "Test Sierra Simple (Patched)";
    sc.AutoLoop = 0;
    sc.UpdateAlways = 1;

    sc.UsesMarketDepthData = 1;
    sc.MaintainVolumeAtPriceData = 1;

    sc.Input[0].Name = "Debug Level (0/1)";
    sc.Input[0].SetInt(1);
    sc.Input[1].Name = "Max DOM Levels";
    sc.Input[1].SetInt(10);
    return;
  }

  if (sc.ServerConnectionState != SCS_CONNECTED) return;

  const int dbg = sc.Input[0].GetInt();
  const int max_levels = sc.Input[1].GetInt();

  // --- Test 1: BaseData (dernier index) ---
  if (sc.ArraySize > 0) {
    const int i = sc.ArraySize - 1;
    // Utiliser GetAsDouble() pour l'horodatage (compatible avec toutes les versions)
    double timestamp = sc.BaseDateTimeIn[i].GetAsDouble();
    SCString msg;
    msg.Format("{\"t\":%.6f,\"sym\":\"%s\",\"type\":\"bar\",\"i\":%d,\"close\":%.8f,\"volume\":%.0f,\"arraysz\":%d}",
      timestamp, sc.Symbol.GetChars(), i, sc.Close[i], sc.Volume[i], sc.ArraySize);
    WriteLine("D:\\MIA_IA_system\\test_sierra.log", msg);
  }

  // --- Test 2: DOM (live) ---
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
        j.Format("{\"t\":%.6f,\"sym\":\"%s\",\"type\":\"dom\",\"side\":\"BID\",\"lvl\":%d,\"price\":%.8f,\"size\":%.0f}",
          timestamp, sc.Symbol.GetChars(), lvl, p, be.Quantity);
        WriteLine("D:\\MIA_IA_system\\test_dom.log", j);
      }
      if (gotA && ae.Quantity > 0) {
        double p = ae.Price * sc.RealTimePriceMultiplier;
        // Utiliser GetAsDouble() pour l'horodatage
        double timestamp = sc.CurrentSystemDateTime.GetAsDouble();
        SCString j;
        j.Format("{\"t\":%.6f,\"sym\":\"%s\",\"type\":\"dom\",\"side\":\"ASK\",\"lvl\":%d,\"price\":%.8f,\"size\":%.0f}",
          timestamp, sc.Symbol.GetChars(), lvl, p, ae.Quantity);
        WriteLine("D:\\MIA_IA_system\\test_dom.log", j);
      }
    }
  }

  // --- Test 3: T&S (dernier event) ---
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
    j.Format("{\"t\":%.6f,\"sym\":\"%s\",\"type\":\"ts\",\"kind\":\"%s\",\"price\":%.8f,\"vol\":%d,\"seq\":%u}",
      timestamp, sc.Symbol.GetChars(), kind, px, last.Volume, last.Sequence);
    WriteLine("D:\\MIA_IA_system\\test_ts.log", j);
  }
}
