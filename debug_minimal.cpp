#include "sierrachart.h"

SCDLLName("debug_minimal.dll")

SCSFExport scsf_DebugMinimal(SCStudyInterfaceRef sc)
{
    if (sc.SetDefaults)
    {
        sc.GraphName = "Debug Minimal";
        sc.StudyDescription = "Test minimal - juste un log";
        sc.AutoLoop = 1;
        return;
    }

    // Log minimal à chaque tick
    sc.AddMessageToLog("DEBUG MINIMAL: Script is running!", 0);
}
