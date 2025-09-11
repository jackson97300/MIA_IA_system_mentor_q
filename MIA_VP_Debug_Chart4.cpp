// Script de diagnostic simple pour Chart 4
#include "sierrachart.h"
SCDLLName("MIA_VP_Debug_Chart4")

static void WriteDebugLog(SCStudyInterfaceRef sc, int chartNum, const SCString& message) {
  SCDateTime now = sc.CurrentSystemDateTime;
  int y = now.GetYear(), m = now.GetMonth(), d = now.GetDay();
  SCString fname;
  fname.Format("chart_%d_debug_%04d%02d%02d.jsonl", chartNum, y, m, d);
  
  SCString line;
  line.Format("{\"t\":%.6f,\"type\":\"debug\",\"chart\":%d,\"msg\":\"%s\"}", 
              now.GetAsDouble(), chartNum, message.GetChars());
  sc.AppendStringToFile(fname, line + "\n");
}

SCSFExport scsf_MIA_VP_Debug_Chart4(SCStudyInterfaceRef sc)
{
  if (sc.SetDefaults) {
    sc.GraphName = "MIA VP Debug Chart 4";
    sc.AutoLoop = 0;
    sc.GraphRegion = 0;
    
    sc.Input[0].Name = "Chart 4 Number";
    sc.Input[0].SetInt(4);
    
    sc.Input[1].Name = "Test Study ID 8";
    sc.Input[1].SetInt(8);
    
    sc.Input[2].Name = "Test Study ID 9";
    sc.Input[2].SetInt(9);
    
    return;
  }
  
  const int chart4 = sc.Input[0].GetInt();
  const int study8 = sc.Input[1].GetInt();
  const int study9 = sc.Input[2].GetInt();
  
  static int lastBar = -1;
  
  // Vérifier si nouvelle barre
  SCFloatArray lastArr;
  sc.GetChartArray(chart4, SC_LAST, lastArr);
  if (lastArr.GetArraySize() == 0) {
    WriteDebugLog(sc, chart4, "no_bars_available");
    return;
  }
  
  int currentBar = lastArr.GetArraySize() - 1;
  if (currentBar == lastBar) return;
  lastBar = currentBar;
  
  WriteDebugLog(sc, chart4, "new_bar_detected");
  
  // Tester Study ID 8
  SCFloatArray sg0_8, sg1_8, sg2_8, sg3_8;
  sc.GetStudyArrayFromChartUsingID(chart4, study8, 0, sg0_8);
  sc.GetStudyArrayFromChartUsingID(chart4, study8, 1, sg1_8);
  sc.GetStudyArrayFromChartUsingID(chart4, study8, 2, sg2_8);
  sc.GetStudyArrayFromChartUsingID(chart4, study8, 3, sg3_8);
  
  SCString msg8;
  msg8.Format("study_8_sizes: sg0=%d, sg1=%d, sg2=%d, sg3=%d", 
              sg0_8.GetArraySize(), sg1_8.GetArraySize(), 
              sg2_8.GetArraySize(), sg3_8.GetArraySize());
  WriteDebugLog(sc, chart4, msg8);
  
  // Tester Study ID 9
  SCFloatArray sg0_9, sg1_9, sg2_9, sg3_9;
  sc.GetStudyArrayFromChartUsingID(chart4, study9, 0, sg0_9);
  sc.GetStudyArrayFromChartUsingID(chart4, study9, 1, sg1_9);
  sc.GetStudyArrayFromChartUsingID(chart4, study9, 2, sg2_9);
  sc.GetStudyArrayFromChartUsingID(chart4, study9, 3, sg3_9);
  
  SCString msg9;
  msg9.Format("study_9_sizes: sg0=%d, sg1=%d, sg2=%d, sg3=%d", 
              sg0_9.GetArraySize(), sg1_9.GetArraySize(), 
              sg2_9.GetArraySize(), sg3_9.GetArraySize());
  WriteDebugLog(sc, chart4, msg9);
  
  // Tester les valeurs si disponibles
  if (sg1_8.GetArraySize() > currentBar) {
    SCString val8;
    val8.Format("study_8_values: sg1=%.2f, sg2=%.2f, sg3=%.2f", 
                sg1_8[currentBar], sg2_8[currentBar], sg3_8[currentBar]);
    WriteDebugLog(sc, chart4, val8);
  }
  
  if (sg1_9.GetArraySize() > currentBar) {
    SCString val9;
    val9.Format("study_9_values: sg1=%.2f, sg2=%.2f, sg3=%.2f", 
                sg1_9[currentBar], sg2_9[currentBar], sg3_9[currentBar]);
    WriteDebugLog(sc, chart4, val9);
  }
}
