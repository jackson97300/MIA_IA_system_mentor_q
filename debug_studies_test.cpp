#include "sierrachart.h"

SCDLLName("debug_studies_test.dll")

// Fonction utilitaire pour écrire dans un fichier de debug dédié
void WriteDebugLog(SCStudyInterfaceRef sc, const SCString& message) {
    // Filet de sécurité : log dans Message Log aussi
    sc.AddMessageToLog(message, 0);
    
    // Puis essaie d'écrire le fichier
    SCString filename;
    filename.Format("debug_studies_test_%04d%02d%02d.jsonl", 
                   sc.CurrentSystemDateTime.GetYear(),
                   sc.CurrentSystemDateTime.GetMonth(),
                   sc.CurrentSystemDateTime.GetDay());
    
    FILE* file = fopen(filename.GetChars(), "a");
    if (file) {
        fprintf(file, "%s\n", message.GetChars());
        fclose(file);
    }
}

SCSFExport scsf_DebugStudiesTest(SCStudyInterfaceRef sc)
{
    if (sc.SetDefaults)
    {
        sc.GraphName = "Debug Studies Test";
        sc.StudyDescription = "Test des études NBCV et Cumulative Delta Bars";
        sc.AutoLoop = 1;
        return;
    }

    // Log unique par session
    static bool s_logged = false;
    if (!s_logged) {
        s_logged = true;
        
        SCString log;
        log.Format("{\"t\":%.6f,\"type\":\"studies_test_start\",\"chart\":%d}",
                  sc.CurrentSystemDateTime.GetAsDouble(), sc.ChartNumber);
        WriteDebugLog(sc, log);
    }

    // === TEST NBCV (ID 14) ===
    const int nbcvId = 14;
    SCString nbcvLog;
    nbcvLog.Format("{\"t\":%.6f,\"type\":\"nbcv_test\",\"study_id\":%d,\"i\":%d,\"chart\":%d",
                  sc.CurrentSystemDateTime.GetAsDouble(), nbcvId, sc.Index, sc.ChartNumber);
    
    // Test tous les subgraphs de 0 à 15
    for (int sg = 0; sg <= 15; sg++) {
        SCFloatArray nbcvArray;
        if (sc.GetStudyArrayUsingID(nbcvId, sg, nbcvArray)) {
            if (nbcvArray.GetArraySize() > sc.Index) {
                double value = nbcvArray[sc.Index];
                SCString sgLog;
                sgLog.Format("{\"t\":%.6f,\"type\":\"nbcv_sg\",\"study_id\":%d,\"sg\":%d,\"i\":%d,\"value\":%.6f,\"chart\":%d}",
                          sc.CurrentSystemDateTime.GetAsDouble(), nbcvId, sg, sc.Index, value, sc.ChartNumber);
                WriteDebugLog(sc, sgLog);
            }
        }
    }

    // === TEST Cumulative Delta Bars (ID 6) ===
    const int cumDeltaBarsId = 6;
    for (int sg = 0; sg <= 10; sg++) {
        SCFloatArray cumDeltaArray;
        if (sc.GetStudyArrayUsingID(cumDeltaBarsId, sg, cumDeltaArray)) {
            if (cumDeltaArray.GetArraySize() > sc.Index) {
                double value = cumDeltaArray[sc.Index];
                SCString sgLog;
                sgLog.Format("{\"t\":%.6f,\"type\":\"cum_delta_bars_sg\",\"study_id\":%d,\"sg\":%d,\"i\":%d,\"value\":%.6f,\"chart\":%d}",
                          sc.CurrentSystemDateTime.GetAsDouble(), cumDeltaBarsId, sg, sc.Index, value, sc.ChartNumber);
                WriteDebugLog(sc, sgLog);
            }
        }
    }
}
