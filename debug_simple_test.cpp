#include "sierrachart.h"

SCDLLName("debug_simple_test.dll")

// Fonction utilitaire pour écrire dans un fichier de debug dédié
void WriteDebugLog(SCStudyInterfaceRef sc, const SCString& message) {
    // Filet de sécurité : log dans Message Log aussi
    sc.AddMessageToLog(message, 0);
    
    // Puis essaie d'écrire le fichier
    SCString filename;
    filename.Format("debug_simple_test_%04d%02d%02d.jsonl", 
                   sc.CurrentSystemDateTime.GetYear(),
                   sc.CurrentSystemDateTime.GetMonth(),
                   sc.CurrentSystemDateTime.GetDay());
    
    FILE* file = fopen(filename.GetChars(), "a");
    if (file) {
        fprintf(file, "%s\n", message.GetChars());
        fclose(file);
    }
}

SCSFExport scsf_DebugSimpleTest(SCStudyInterfaceRef sc)
{
    if (sc.SetDefaults)
    {
        sc.GraphName = "Debug Simple Test";
        sc.StudyDescription = "Test ultra-simple pour vérifier que le script fonctionne";
        sc.AutoLoop = 1;
        return;
    }

    // Log à chaque tick pour vérifier que le script tourne
    SCString log;
    log.Format("{\"t\":%.6f,\"type\":\"simple_test\",\"i\":%d,\"chart\":%d,\"msg\":\"script_running\"}",
              sc.CurrentSystemDateTime.GetAsDouble(), sc.Index, sc.ChartNumber);
    WriteDebugLog(sc, log);

    // Test simple : lire le prix de clôture
    if (sc.BaseData[SC_LAST].GetArraySize() > sc.Index) {
        double close = sc.BaseData[SC_LAST][sc.Index];
        SCString log2;
        log2.Format("{\"t\":%.6f,\"type\":\"price_test\",\"i\":%d,\"close\":%.2f,\"chart\":%d}",
                  sc.CurrentSystemDateTime.GetAsDouble(), sc.Index, close, sc.ChartNumber);
        WriteDebugLog(sc, log2);
    }
}
