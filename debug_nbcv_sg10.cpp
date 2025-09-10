#include "sierrachart.h"
#include <stdio.h>

SCDLLName("Debug NBCV SG10")

// Script de diagnostic pour identifier le problème SG10 (Cumulative Delta)
SCSFExport scsf_Debug_NBCV_SG10(SCStudyInterfaceRef sc)
{
  if (sc.SetDefaults)
  {
    sc.GraphName = "Debug NBCV SG10 - Cumulative Delta";
    sc.AutoLoop = 0;
    sc.UpdateAlways = 1;
    sc.CalculationPrecedence = LOW_PREC_LEVEL;
    
    // Inputs pour configurer l'étude NBCV à diagnostiquer
    sc.Input[0].Name = "NBCV Study ID (0=auto)";
    sc.Input[0].SetInt(33); // ID par défaut
    
    sc.Input[1].Name = "SG Ask Volume";
    sc.Input[1].SetInt(5);
    
    sc.Input[2].Name = "SG Bid Volume";
    sc.Input[2].SetInt(6);
    
    sc.Input[3].Name = "SG Delta";
    sc.Input[3].SetInt(1);
    
    sc.Input[4].Name = "SG Trades";
    sc.Input[4].SetInt(12);
    
    sc.Input[5].Name = "SG Cumulative Delta";
    sc.Input[5].SetInt(10);
    
    return;
  }

  if (sc.ServerConnectionState != SCS_CONNECTED) return;
  if (sc.ArraySize <= 0) return;

  const int i = sc.ArraySize - 1;
  const double t = sc.BaseDateTimeIn[i].GetAsDouble();
  
  // 1) Résoudre l'ID NBCV - essayer plusieurs noms possibles
  int nbcv_id = sc.Input[0].GetInt();
  if (nbcv_id <= 0) {
    // Essayer différents noms d'études NBCV
    const char* study_names[] = {
      "Numbers Bars Calculated Values",
      "Numbers Bars Calculated Values (NBCV)",
      "NBCV",
      "Order Flow Numbers Bars",
      "Volume Profile Numbers Bars"
    };
    
    for (int k = 0; k < 5; k++) {
      nbcv_id = sc.GetStudyIDByName(sc.ChartNumber, study_names[k], 1);
      if (nbcv_id > 0) {
        SCString msg;
        msg.Format("Found NBCV Study: '%s' with ID: %d", study_names[k], nbcv_id);
        sc.AddMessageToLog(msg, 0);
        break;
      }
    }
  }
  
  if (nbcv_id <= 0) {
    SCString msg;
    msg.Format("NBCV Study NOT FOUND! Chart: %d", sc.ChartNumber);
    sc.AddMessageToLog(msg, 1);
    return;
  }
  
  // 2) Charger tous les subgraphs
  SCFloatArray askVolArr, bidVolArr, deltaArr, tradesArr, cumDeltaArr;
  const int sgAsk   = sc.Input[1].GetInt();
  const int sgBid   = sc.Input[2].GetInt();
  const int sgDelta = sc.Input[3].GetInt();
  const int sgTrades= sc.Input[4].GetInt();
  const int sgCum   = sc.Input[5].GetInt();

  sc.GetStudyArrayUsingID(nbcv_id, sgAsk,   askVolArr);
  sc.GetStudyArrayUsingID(nbcv_id, sgBid,   bidVolArr);
  sc.GetStudyArrayUsingID(nbcv_id, sgDelta, deltaArr);
  sc.GetStudyArrayUsingID(nbcv_id, sgTrades,tradesArr);
  sc.GetStudyArrayUsingID(nbcv_id, sgCum,   cumDeltaArr);

  // 3) Diagnostic complet
  auto has = [&](const SCFloatArray& a){ return a.GetArraySize() > i; };
  
  SCString diag;
  diag.Format("=== NBCV DIAGNOSTIC Chart:%d ID:%d ===\n", sc.ChartNumber, nbcv_id);
  
  // Lister tous les subgraphs disponibles (0-20)
  diag += "Available Subgraphs:\n";
  for (int sg = 0; sg <= 20; sg++) {
    SCFloatArray testArr;
    if (sc.GetStudyArrayUsingID(nbcv_id, sg, testArr) == 1) {
      if (testArr.GetArraySize() > i) {
        double val = testArr[i];
        diag += SCString().Format("  SG%d: %.2f (size:%d)\n", sg, val, testArr.GetArraySize());
      }
    }
  }
  
  // Tailles des arrays
  diag += SCString().Format("Array Sizes - Ask:%d Bid:%d Delta:%d Trades:%d Cum:%d\n",
                           askVolArr.GetArraySize(), bidVolArr.GetArraySize(), 
                           deltaArr.GetArraySize(), tradesArr.GetArraySize(), cumDeltaArr.GetArraySize());
  
  // Valeurs à l'index i
  if (has(askVolArr) && has(bidVolArr)) {
    double askVol = askVolArr[i];
    double bidVol = bidVolArr[i];
    double delta = askVol - bidVol;
    
    diag += SCString().Format("Values[i=%d] - Ask:%.0f Bid:%.0f Delta:%.0f\n", i, askVol, bidVol, delta);
    
    // SG10 Cumulative Delta
    if (has(cumDeltaArr)) {
      double cumDelta = cumDeltaArr[i];
      diag += SCString().Format("SG%d Cumulative Delta: %.0f\n", sgCum, cumDelta);
      
      // Vérifier les 5 dernières valeurs pour voir l'évolution
      diag += "Last 5 Cumulative Values: ";
      for (int j = max(0, i-4); j <= i; j++) {
        if (j < cumDeltaArr.GetArraySize()) {
          diag += SCString().Format("%.0f ", cumDeltaArr[j]);
        }
      }
      diag += "\n";
    } else {
      diag += SCString().Format("SG%d Cumulative Delta: NOT AVAILABLE (array too small)\n", sgCum);
    }
    
    // SG12 Trades
    if (has(tradesArr)) {
      double trades = tradesArr[i];
      diag += SCString().Format("SG%d Trades: %.0f\n", sgTrades, trades);
    } else {
      diag += SCString().Format("SG%d Trades: NOT AVAILABLE\n", sgTrades);
    }
    
    // Calcul manuel du cumulatif pour comparaison
    static double manual_cum = 0.0;
    manual_cum += delta;
    diag += SCString().Format("Manual Cumulative: %.0f\n", manual_cum);
    
  } else {
    diag += "ERROR: Ask/Bid volumes not available!\n";
  }
  
  // 4) Afficher le diagnostic
  sc.AddMessageToLog(diag, 0);
  
  // 5) Écrire aussi dans un fichier pour analyse
  FILE* f = fopen("D:\\MIA_IA_system\\nbcv_diagnostic.txt", "a");
  if (f) {
    fprintf(f, "Time: %.6f - %s\n", t, diag.GetChars());
    fclose(f);
  }
}
