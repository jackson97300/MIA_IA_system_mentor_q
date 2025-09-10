#include "sierrachart.h"

SCSFExport scsf_DebugStudiesDelta(SCStudyInterfaceRef sc)
{
    if (sc.SetDefaults)
    {
        sc.GraphName = "Debug Studies Delta";
        sc.StudyDescription = "Debug all studies to find cumulative delta";
        sc.AutoLoop = 1;
        return;
    }

    // Log unique par session
    static bool s_logged = false;
    if (!s_logged) {
        s_logged = true;
        
        SCString log;
        log.Format("{\"t\":%.6f,\"type\":\"studies_scan\",\"chart\":%d,\"studies\":[",
                  sc.CurrentSystemDateTime.GetAsDouble(), sc.ChartNumber);
        
        // Scan des études ID 1-50
        for (int id = 1; id <= 50; id++) {
            SCString studyName;
            if (sc.GetStudyNameFromID(id, studyName)) {
                if (studyName.GetLength() > 0) {
                    // Vérifier si l'étude a des subgraphs
                    SCFloatArray testArr;
                    if (sc.GetStudyArrayUsingID(id, 0, testArr)) {
                        int sgCount = 0;
                        for (int sg = 0; sg < 20; sg++) {
                            SCFloatArray sgArr;
                            if (sc.GetStudyArrayUsingID(id, sg, sgArr)) {
                                if (sgArr.GetArraySize() > 0) {
                                    sgCount++;
                                }
                            }
                        }
                        
                        if (sgCount > 0) {
                            SCString studyInfo;
                            studyInfo.Format("{\"id\":%d,\"name\":\"%s\",\"sg_count\":%d}", 
                                           id, studyName.GetChars(), sgCount);
                            if (id > 1) log += ",";
                            log += studyInfo;
                        }
                    }
                }
            }
        }
        
        log += "]}";
        sc.AddMessageToLog(log, 0);
    }
}
