#include "sierrachart.h"
#ifdef _WIN32
  #include <windows.h>
#endif

SCDLLName("MIA_Chart_Dumper_Patched")

// Dumper complet : BaseData, DOM live, VAP, T&S, VWAP + VVA (Volume Value Area Lines) + PVWAP
// Collecte VAH/VAL/VPOC (courant) + PVAH/PVAL/PPOC (précédent) + PVWAP (VWAP période précédente)

static void WritePerChart(int chartNumber, const SCString& line) {
#ifdef _WIN32
  CreateDirectoryA("D:\\MIA_IA_system", NULL);
#endif
  SCString filename;
  filename.Format("D:\\MIA_IA_system\\chart_%d.jsonl", chartNumber);
  FILE* f = fopen(filename.GetChars(), "a");
  if (f) { fprintf(f, "%s\n", line.GetChars()); fclose(f); }
}

SCSFExport scsf_MIA_Chart_Dumper_Patched(SCStudyInterfaceRef sc)
{
  if (sc.SetDefaults)
  {
    sc.GraphName = "MIA Chart Dumper (Patched)";
    sc.AutoLoop = 0;
    sc.UpdateAlways = 1;
    sc.UsesMarketDepthData = 1;
    sc.MaintainVolumeAtPriceData = 1;
    sc.MaintainAdditionalChartDataArrays = 1;
    sc.CalculationPrecedence = LOW_PREC_LEVEL; // important: calc VWAP avant notre étude

    // --- Inputs VWAP ---
    sc.Input[0].Name = "Max DOM Levels";
    sc.Input[0].SetInt(20);
    sc.Input[1].Name = "Max VAP Elements";
    sc.Input[1].SetInt(5);
    sc.Input[2].Name = "Max T&S Entries";
    sc.Input[2].SetInt(10);
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

    return;
  }

  if (sc.ServerConnectionState != SCS_CONNECTED) return;

  const int max_levels = sc.Input[0].GetInt();
  const int max_vap = sc.Input[1].GetInt();
  const int max_ts = sc.Input[2].GetInt();

  // ---- BaseData (nouvelle barre uniquement) ----
  static int last_bar_index = -1;
  if (sc.ArraySize > 0) {
    const int i = sc.ArraySize - 1;
    if (i != last_bar_index) {
      last_bar_index = i;
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
      WritePerChart(sc.ChartNumber, j);
    }
  }

  // ---- VWAP export (uniquement à nouvelle barre pour éviter les doublons) ----
  if (sc.Input[3].GetInt() != 0 && sc.ArraySize > 0) {
    static int vwapID = -2; // -2: à résoudre, -1: introuvable, >0: OK
    static int last_vwap_bar = -1; // Pour éviter les doublons
    const int i = sc.ArraySize - 1;
    
    // N'écrire VWAP qu'à la nouvelle barre (comme BaseData)
    if (i != last_vwap_bar) {
      last_vwap_bar = i;
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
        WritePerChart(sc.ChartNumber, d);
      }
  
      if (vwapID > 0) {
        SCFloatArray VWAP, UP1, DN1, UP2, DN2;
        sc.GetStudyArrayUsingID(vwapID, 0, VWAP);
        int bands = sc.Input[5].GetInt();
        if (bands >= 1) { sc.GetStudyArrayUsingID(vwapID, 1, UP1); sc.GetStudyArrayUsingID(vwapID, 2, DN1); }
        if (bands >= 2) { sc.GetStudyArrayUsingID(vwapID, 3, UP2); sc.GetStudyArrayUsingID(vwapID, 4, DN2); }
  
        if (VWAP.GetArraySize() > i) {
          double v   = VWAP[i] * sc.RealTimePriceMultiplier;
          double up1 = (UP1.GetArraySize() > i ? UP1[i] : 0) * sc.RealTimePriceMultiplier;
          double dn1 = (DN1.GetArraySize() > i ? DN1[i] : 0) * sc.RealTimePriceMultiplier;
          double up2 = (UP2.GetArraySize() > i ? UP2[i] : 0) * sc.RealTimePriceMultiplier;
          double dn2 = (DN2.GetArraySize() > i ? DN2[i] : 0) * sc.RealTimePriceMultiplier;
  
          SCString j;
          j.Format("{\"t\":%.6f,\"sym\":\"%s\",\"type\":\"vwap\",\"src\":\"study\",\"i\":%d,\"v\":%.8f,\"up1\":%.8f,\"dn1\":%.8f,\"up2\":%.8f,\"dn2\":%.8f}",
                   t, sc.Symbol.GetChars(), i, v, up1, dn1, up2, dn2);
          WritePerChart(sc.ChartNumber, j);
        } else {
          SCString d; d.Format("{\"t\":%.6f,\"type\":\"vwap_diag\",\"msg\":\"array_too_small\",\"id\":%d,\"i\":%d}",
                               t, vwapID, i);
          WritePerChart(sc.ChartNumber, d);
        }
      } else {
        SCString d; d.Format("{\"t\":%.6f,\"type\":\"vwap_diag\",\"msg\":\"study_not_found\"}", t);
        WritePerChart(sc.ChartNumber, d);
      }
    }
  }

  // ========== VVA (VAH/VAL/VPOC + PVAH/PVAL/PPOC) ==========
  if (sc.Input[6].GetInt() != 0 && sc.ArraySize > 0)
  {
    const int i = sc.ArraySize - 1;
    static int last_vva_bar = -1;
    const bool newbar_only = sc.Input[9].GetInt() != 0;

    if (!newbar_only || i != last_vva_bar)
    {
      last_vva_bar = i;

      const int id_curr = sc.Input[7].GetInt(); // ID:1 (Current)
      const int id_prev = sc.Input[8].GetInt(); // ID:2 (Previous)
      const bool use_mult = sc.Input[10].GetInt() != 0;
      const double mult = use_mult ? sc.RealTimePriceMultiplier : 1.0;

      auto read_vva = [&](int id, double& vah, double& val, double& vpoc)
      {
        vah = val = vpoc = 0.0;
        if (id <= 0) return;

        SCFloatArray SG0, SG1, SG2;  // 0=VAH, 1=VAL, 2=VPOC
        sc.GetStudyArrayUsingID(id, 0, SG0);
        sc.GetStudyArrayUsingID(id, 1, SG1);
        sc.GetStudyArrayUsingID(id, 2, SG2);

        if (SG0.GetArraySize() > i) vah  = SG0[i] * mult;
        if (SG1.GetArraySize() > i) val  = SG1[i] * mult;
        if (SG2.GetArraySize() > i) vpoc = SG2[i] * mult;
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
      WritePerChart(sc.ChartNumber, j);
    }
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
        WritePerChart(sc.ChartNumber, d);
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
                p = v->Price;
              #elif defined(SC_VAP_PRICE_IN_TICKS)
                p = v->PriceInTicks * sc.TickSize;
              #else
                // Fallback : utiliser le prix calculé à partir de l'index de barre
                p = sc.BaseDataIn[SC_LAST][b];
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
          WritePerChart(sc.ChartNumber, j);
        } else {
          // Diagnostic si pas de volume sur la veille
          SCString d; d.Format("{\"t\":%.6f,\"type\":\"pvwap_diag\",\"msg\":\"no_volume_prev_session\",\"prevStart\":%d,\"prevEnd\":%d}", 
                               sc.BaseDateTimeIn[last].GetAsDouble(), prevStart, prevEnd);
          WritePerChart(sc.ChartNumber, d);
        }
      }
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
        double t = sc.CurrentSystemDateTime.GetAsDouble();
        SCString j;
        j.Format("{\"t\":%.6f,\"sym\":\"%s\",\"type\":\"depth\",\"side\":\"BID\",\"lvl\":%d,\"price\":%.8f,\"size\":%.0f}",
          t, sc.Symbol.GetChars(), lvl, p, be.Quantity);
        WritePerChart(sc.ChartNumber, j);
      }
      if (gotA && ae.Quantity > 0) {
        double p = ae.Price * sc.RealTimePriceMultiplier;
        double t = sc.CurrentSystemDateTime.GetAsDouble();
        SCString j;
        j.Format("{\"t\":%.6f,\"sym\":\"%s\",\"type\":\"depth\",\"side\":\"ASK\",\"lvl\":%d,\"price\":%.8f,\"size\":%.0f}",
          t, sc.Symbol.GetChars(), lvl, p, ae.Quantity);
        WritePerChart(sc.ChartNumber, j);
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
          price = v->Price * sc.RealTimePriceMultiplier;
        #elif defined(SC_VAP_PRICE_IN_TICKS)
          price = v->PriceInTicks * sc.TickSize * sc.RealTimePriceMultiplier;
        #else
          // Fallback : utiliser le prix calculé à partir de l'index de barre
          price = sc.BaseDataIn[SC_LAST][bar] * sc.RealTimePriceMultiplier;
        #endif
        
        double t = sc.CurrentSystemDateTime.GetAsDouble();
        SCString j;
        j.Format("{\"t\":%.6f,\"sym\":\"%s\",\"type\":\"vap\",\"bar\":%d,\"k\":%d,\"price\":%.8f,\"vol\":%d}",
          t, sc.Symbol.GetChars(), bar, k, price, v->Volume);
        WritePerChart(sc.ChartNumber, j);
      }
    }
  }

  // ---- T&S (Time & Sales) ----
  c_SCTimeAndSalesArray tns;
  // GetTimeAndSales ne retourne pas de bool, juste void
  sc.GetTimeAndSales(tns);
  int n = (int)tns.Size();
  if (n > 0) {
    // Prendre les derniers entries (max_ts)
    int start = (n > max_ts) ? (n - max_ts) : 0;
    for (int i = start; i < n; ++i) {
      const s_TimeAndSales& entry = tns[i];
      const char* kind = (entry.Type == SC_TS_BID) ? "BID" :
                         (entry.Type == SC_TS_ASK) ? "ASK" :
                         (entry.Type == SC_TS_BIDASKVALUES) ? "BIDASK" : "TRADE";
      double px = entry.Price * sc.RealTimePriceMultiplier;
      double t = entry.DateTime.GetAsDouble();
      SCString j;
      j.Format("{\"t\":%.6f,\"sym\":\"%s\",\"type\":\"ts\",\"kind\":\"%s\",\"px\":%.8f,\"vol\":%d,\"seq\":%u}",
        t, sc.Symbol.GetChars(), kind, px, entry.Volume, entry.Sequence);
      WritePerChart(sc.ChartNumber, j);
    }
  }
}
