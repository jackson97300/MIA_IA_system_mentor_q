#include "sierrachart.h"

SCDLLName("debug_cumulative_delta.dll")

// Fonction utilitaire pour écrire dans un fichier de debug dédié
void WriteDebugLog(SCStudyInterfaceRef sc, const SCString& message) {
    // Filet de sécurité : log dans Message Log aussi
    sc.AddMessageToLog(message, 0);
    
    // Puis essaie d'écrire le fichier
    SCString filename;
    filename.Format("debug_cumulative_delta_%04d%02d%02d.jsonl", 
                   sc.CurrentSystemDateTime.GetYear(),
                   sc.CurrentSystemDateTime.GetMonth(),
                   sc.CurrentSystemDateTime.GetDay());
    
    FILE* file = fopen(filename.GetChars(), "a");
    if (file) {
        fprintf(file, "%s\n", message.GetChars());
        fclose(file);
    }
}

SCSFExport scsf_DebugCumulativeDelta(SCStudyInterfaceRef sc)
{
    if (sc.SetDefaults)
    {
        sc.GraphName = "Debug Cumulative Delta";
        sc.StudyDescription = "Focus sur le Cumulative Delta - NBCV vs Cumulative Delta Bars";
        sc.AutoLoop = 1;
        return;
    }

    // Log unique par session
    static bool s_logged = false;
    if (!s_logged) {
        s_logged = true;
        
        SCString log;
        log.Format("{\"t\":%.6f,\"type\":\"cumulative_delta_debug_start\",\"chart\":%d}",
                  sc.CurrentSystemDateTime.GetAsDouble(), sc.ChartNumber);
        WriteDebugLog(sc, log);
    }

    // === MÉTHODE 1: NBCV (ID 14) - SG10 Cumulative Delta (index 9) ===
    const int nbcvId = 14;
    SCFloatArray nbcvCumDelta;
    double nbcvCum = 0.0;
    bool nbcvValid = false;
    if (sc.GetStudyArrayUsingID(nbcvId, 9, nbcvCumDelta)) {
        if (nbcvCumDelta.GetArraySize() > sc.Index) {
            nbcvCum = nbcvCumDelta[sc.Index];
            nbcvValid = true;
            SCString log;
            log.Format("{\"t\":%.6f,\"type\":\"method1_nbcv_sg10\",\"study_id\":%d,\"sg\":10,\"i\":%d,\"value\":%.6f,\"chart\":%d}",
                      sc.CurrentSystemDateTime.GetAsDouble(), nbcvId, sc.Index, nbcvCum, sc.ChartNumber);
            WriteDebugLog(sc, log);
        }
    }

    // === MÉTHODE 2: Cumulative Delta Bars (ID 6) - SG4 Close (index 3) ===
    const int cumDeltaBarsId = 6;
    SCFloatArray cumDeltaBarsClose;
    double cumDeltaClose = 0.0;
    bool cumDeltaBarsValid = false;
    if (sc.GetStudyArrayUsingID(cumDeltaBarsId, 3, cumDeltaBarsClose)) {
        if (cumDeltaBarsClose.GetArraySize() > sc.Index) {
            cumDeltaClose = cumDeltaBarsClose[sc.Index];
            cumDeltaBarsValid = true;
            SCString log;
            log.Format("{\"t\":%.6f,\"type\":\"method2_cum_delta_bars_sg4\",\"study_id\":%d,\"sg\":4,\"i\":%d,\"value\":%.6f,\"chart\":%d}",
                      sc.CurrentSystemDateTime.GetAsDouble(), cumDeltaBarsId, sc.Index, cumDeltaClose, sc.ChartNumber);
            WriteDebugLog(sc, log);
        }
    }

    // === Cumulative Delta Bars (ID 6) - SG1 Open (index 0) ===
    SCFloatArray cumDeltaBarsOpen;
    if (sc.GetStudyArrayUsingID(cumDeltaBarsId, 0, cumDeltaBarsOpen)) {
        if (cumDeltaBarsOpen.GetArraySize() > sc.Index) {
            double cumDeltaOpen = cumDeltaBarsOpen[sc.Index];
            SCString log;
            log.Format("{\"t\":%.6f,\"type\":\"cum_delta_bars_open\",\"study_id\":%d,\"sg\":1,\"i\":%d,\"value\":%.6f,\"chart\":%d}",
                      sc.CurrentSystemDateTime.GetAsDouble(), cumDeltaBarsId, sc.Index, cumDeltaOpen, sc.ChartNumber);
            WriteDebugLog(sc, log);
        }
    }

    // === Cumulative Delta Bars (ID 6) - SG2 High (index 1) ===
    SCFloatArray cumDeltaBarsHigh;
    if (sc.GetStudyArrayUsingID(cumDeltaBarsId, 1, cumDeltaBarsHigh)) {
        if (cumDeltaBarsHigh.GetArraySize() > sc.Index) {
            double cumDeltaHigh = cumDeltaBarsHigh[sc.Index];
            SCString log;
            log.Format("{\"t\":%.6f,\"type\":\"cum_delta_bars_high\",\"study_id\":%d,\"sg\":2,\"i\":%d,\"value\":%.6f,\"chart\":%d}",
                      sc.CurrentSystemDateTime.GetAsDouble(), cumDeltaBarsId, sc.Index, cumDeltaHigh, sc.ChartNumber);
            WriteDebugLog(sc, log);
        }
    }

    // === Cumulative Delta Bars (ID 6) - SG3 Low ===
    SCFloatArray cumDeltaBarsLow;
    if (sc.GetStudyArrayUsingID(cumDeltaBarsId, 3, cumDeltaBarsLow)) {
        if (cumDeltaBarsLow.GetArraySize() > sc.Index) {
            double cumDeltaLow = cumDeltaBarsLow[sc.Index];
            SCString log;
            log.Format("{\"t\":%.6f,\"type\":\"cum_delta_bars_low\",\"study_id\":%d,\"sg\":3,\"i\":%d,\"value\":%.6f,\"chart\":%d}",
                      sc.CurrentSystemDateTime.GetAsDouble(), cumDeltaBarsId, sc.Index, cumDeltaLow, sc.ChartNumber);
            WriteDebugLog(sc, log);
        }
    }

    // === COMPARAISON FINALE DES 2 MÉTHODES ===
    if (nbcvValid && cumDeltaBarsValid) {
        double diff = cumDeltaClose - nbcvCum;
        SCString log;
        log.Format("{\"t\":%.6f,\"type\":\"methods_comparison\",\"i\":%d,\"method1_nbcv_sg10\":%.6f,\"method2_cum_delta_bars_sg4\":%.6f,\"diff\":%.6f,\"chart\":%d}",
                  sc.CurrentSystemDateTime.GetAsDouble(), sc.Index, nbcvCum, cumDeltaClose, diff, sc.ChartNumber);
        WriteDebugLog(sc, log);
    } else if (nbcvValid && !cumDeltaBarsValid) {
        SCString log;
        log.Format("{\"t\":%.6f,\"type\":\"method_status\",\"i\":%d,\"method1_nbcv_sg10\":%.6f,\"method2_cum_delta_bars_sg4\":\"unavailable\",\"chart\":%d}",
                  sc.CurrentSystemDateTime.GetAsDouble(), sc.Index, nbcvCum, sc.ChartNumber);
        WriteDebugLog(sc, log);
    } else if (!nbcvValid && cumDeltaBarsValid) {
        SCString log;
        log.Format("{\"t\":%.6f,\"type\":\"method_status\",\"i\":%d,\"method1_nbcv_sg10\":\"unavailable\",\"method2_cum_delta_bars_sg4\":%.6f,\"chart\":%d}",
                  sc.CurrentSystemDateTime.GetAsDouble(), sc.Index, cumDeltaClose, sc.ChartNumber);
        WriteDebugLog(sc, log);
    } else {
        SCString log;
        log.Format("{\"t\":%.6f,\"type\":\"method_status\",\"i\":%d,\"method1_nbcv_sg10\":\"unavailable\",\"method2_cum_delta_bars_sg4\":\"unavailable\",\"chart\":%d}",
                  sc.CurrentSystemDateTime.GetAsDouble(), sc.Index, sc.ChartNumber);
        WriteDebugLog(sc, log);
    }
}
