// Test simple des Study IDs sur Chart 4
#include "sierrachart.h"
SCDLLName("MIA_Test_Chart4_StudyIDs")

static void WriteTestLog(SCStudyInterfaceRef sc, int chartNum, const SCString& message) {
  SCDateTime now = sc.CurrentSystemDateTime;
  int y = now.GetYear(), m = now.GetMonth(), d = now.GetDay();
  SCString fname;
  fname.Format("chart_%d_test_%04d%02d%02d.jsonl", chartNum, y, m, d);
  
  SCString line;
  line.Format("{\"t\":%.6f,\"type\":\"test\",\"chart\":%d,\"msg\":\"%s\"}", 
              now.GetAsDouble(), chartNum, message.GetChars());
  sc.AppendStringToFile(fname, line + "\n");
}

SCSFExport scsf_MIA_Test_Chart4_StudyIDs(SCStudyInterfaceRef sc)
{
  if (sc.SetDefaults) {
    sc.GraphName = "MIA Test Chart 4 Study IDs";
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
    WriteTestLog(sc, chart4, "no_bars_available");
    return;
  }
  
  int currentBar = lastArr.GetArraySize() - 1;
  if (currentBar == lastBar) return;
  lastBar = currentBar;
  
  WriteTestLog(sc, chart4, "new_bar_detected");
  
  // Tester Study ID 8 avec tous les subgraphs
  for (int sg = 0; sg <= 3; sg++) {
    SCFloatArray sgArray;
    sc.GetStudyArrayFromChartUsingID(chart4, study8, sg, sgArray);
    
    SCString msg;
    msg.Format("study_8_sg%d_size=%d", sg, sgArray.GetArraySize());
    WriteTestLog(sc, chart4, msg);
    
    if (sgArray.GetArraySize() > currentBar) {
      SCString val;
      val.Format("study_8_sg%d_value=%.2f", sg, sgArray[currentBar]);
      WriteTestLog(sc, chart4, val);
    }
  }
  
  // Tester Study ID 9 avec tous les subgraphs
  for (int sg = 0; sg <= 3; sg++) {
    SCFloatArray sgArray;
    sc.GetStudyArrayFromChartUsingID(chart4, study9, sg, sgArray);
    
    SCString msg;
    msg.Format("study_9_sg%d_size=%d", sg, sgArray.GetArraySize());
    WriteTestLog(sc, chart4, msg);
    
    if (sgArray.GetArraySize() > currentBar) {
      SCString val;
      val.Format("study_9_sg%d_value=%.2f", sg, sgArray[currentBar]);
      WriteTestLog(sc, chart4, val);
    }
  }
  
  // Tester d'autres Study IDs possibles
  for (int testId = 1; testId <= 20; testId++) {
    if (testId == study8 || testId == study9) continue;
    
    SCFloatArray sg1, sg2, sg3;
    sc.GetStudyArrayFromChartUsingID(chart4, testId, 1, sg1);
    sc.GetStudyArrayFromChartUsingID(chart4, testId, 2, sg2);
    sc.GetStudyArrayFromChartUsingID(chart4, testId, 3, sg3);
    
    if (sg1.GetArraySize() > 0 || sg2.GetArraySize() > 0 || sg3.GetArraySize() > 0) {
      SCString msg;
      msg.Format("found_study_%d_sizes: sg1=%d, sg2=%d, sg3=%d", 
                 testId, sg1.GetArraySize(), sg2.GetArraySize(), sg3.GetArraySize());
      WriteTestLog(sc, chart4, msg);
      
      if (sg1.GetArraySize() > currentBar && sg2.GetArraySize() > currentBar && sg3.GetArraySize() > currentBar) {
        SCString val;
        val.Format("study_%d_values: sg1=%.2f, sg2=%.2f, sg3=%.2f", 
                   testId, sg1[currentBar], sg2[currentBar], sg3[currentBar]);
        WriteTestLog(sc, chart4, val);
      }
    }
  }
}
