// MIA_Dumper_G4_Studies.cpp
// ACSIL — Sierra Chart (Chart #4)
// Exporte en JSONL : vwap, vva, vva_previous, previous_vp, previous_vwap, nbcv, cumulative_delta, volume_profile (si présent), atr, correlation (si présent).
// Robustesse : résolution par nom d'étude, anti-doublon (Write-If-Changed), gardes VVA, vérifs NBCV, timestamps monotones.
// © PRO97 / MIA_IA_SYSTEM

#include "sierrachart.h"
SCDLLName("MIA_Dumper_G4_Studies")

#include <cstdio>
#include <cstring>
#include <string>
#include <map>
#include <sstream>
#include <algorithm>

// =========================
// ====== CONFIG INPUT =====
// =========================

SCSFExport scsf_MIA_Dumper_G4_Studies(SCStudyInterfaceRef sc)
{
    SCInputRef In_OutputDir          = sc.Input[0];  // Dossier de sortie
    SCInputRef In_EnableVWAP         = sc.Input[1];
    SCInputRef In_EnableVVA          = sc.Input[2];
    SCInputRef In_EnableVVAPrevious  = sc.Input[3];
    SCInputRef In_EnablePrevVP       = sc.Input[4];
    SCInputRef In_EnablePrevVWAP     = sc.Input[5];
    SCInputRef In_EnableNBCV         = sc.Input[6];
    SCInputRef In_EnableCumDelta     = sc.Input[7];
    SCInputRef In_EnableVolumeProf   = sc.Input[8];   // si étude VP présente
    SCInputRef In_EnableATR          = sc.Input[9];   // si étude ATR présente
    SCInputRef In_EnableCorrelation  = sc.Input[10];  // si étude Corr présente
    SCInputRef In_SymbolOverride     = sc.Input[11];  // optionnel (symbole personnalisé dans JSON)

    if (sc.SetDefaults)
    {
        sc.GraphName = "MIA Dumper G4 — JSONL Export";
        sc.AutoLoop = 1;              // simple: 1 ligne par barre
        sc.GraphRegion = 0;

        In_OutputDir.Name = "Output Directory";
        In_OutputDir.SetString("D:\\MIA_IA_system");

        In_EnableVWAP.Name = "Export VWAP";
        In_EnableVWAP.SetYesNo(1);

        In_EnableVVA.Name = "Export VVA (Value Area Lines)";
        In_EnableVVA.SetYesNo(1);

        In_EnableVVAPrevious.Name = "Export VVA Previous";
        In_EnableVVAPrevious.SetYesNo(1);

        In_EnablePrevVP.Name = "Export Previous VP (PVPOC/PVAH/PVAL + PVWAP)";
        In_EnablePrevVP.SetYesNo(1);

        In_EnablePrevVWAP.Name = "Export Previous VWAP";
        In_EnablePrevVWAP.SetYesNo(1);

        In_EnableNBCV.Name = "Export NBCV (Numbers Bars Calculated Values)";
        In_EnableNBCV.SetYesNo(1);

        In_EnableCumDelta.Name = "Export Cumulative Delta (Volume)";
        In_EnableCumDelta.SetYesNo(1);

        In_EnableVolumeProf.Name = "Export Volume Profile (if present)";
        In_EnableVolumeProf.SetYesNo(1);

        In_EnableATR.Name = "Export ATR (if present)";
        In_EnableATR.SetYesNo(0);

        In_EnableCorrelation.Name = "Export Correlation (if present)";
        In_EnableCorrelation.SetYesNo(0);

        In_SymbolOverride.Name = "Symbol Override (optional)";
        In_SymbolOverride.SetString("");

        return;
    }

    // =========================
    // ====== HELPERS ==========
    // =========================

    struct StudyRefs {
        int vwap     = -1; // "VWAP"
        int vva      = -1; // "Volume Value Area Lines"
        int vva_prev = -1; // "Volume Value Area Previous"
        int nbcv     = -1; // "Numbers Bars Calculated Values"
        int cumdelta = -1; // "Cumulative Delta Bars - Volume"
        int volprof  = -1; // "Volume by Price" or "Volume Profile" (selon nom), OPTIONNEL
        int atr      = -1; // "Average True Range" (optionnel)
        int corr     = -1; // "Correlation Coefficient" (optionnel)
    };

    // Résolution par nom
    auto GetIDByName = [&](const char* StudyName)->int {
        return sc.GetStudyIDByName(4, StudyName, 0);
    };

    // Autorésolution Chart #4 par noms standard Sierra
    static bool s_resolved = false;
    static StudyRefs s_refs;

    if (!s_resolved)
    {
        s_refs.vwap     = GetIDByName("VWAP");
        s_refs.vva      = GetIDByName("Volume Value Area Lines");
        s_refs.vva_prev = GetIDByName("Volume Value Area Previous");
        s_refs.nbcv     = GetIDByName("Numbers Bars Calculated Values");
        s_refs.cumdelta = GetIDByName("Cumulative Delta Bars - Volume");

        // Optionnels (selon ton chart)
        // NB: l'étude Volume Profile sous Sierra peut s'appeler "Volume by Price".
        int vp1 = GetIDByName("Volume Profile");
        int vp2 = GetIDByName("Volume by Price");
        s_refs.volprof = (vp1 > 0 ? vp1 : vp2);

        s_refs.atr      = GetIDByName("Average True Range");
        s_refs.corr     = GetIDByName("Correlation Coefficient");

        // Logs utiles si manquants (non bloquants)
        if (s_refs.vwap <= 0)     sc.AddMessageToLog("G4: VWAP introuvable", 1);
        if (s_refs.vva <= 0)      sc.AddMessageToLog("G4: VVA introuvable", 1);
        if (s_refs.vva_prev <= 0) sc.AddMessageToLog("G4: VVA Previous introuvable", 1);
        if (s_refs.nbcv <= 0)     sc.AddMessageToLog("G4: NBCV introuvable", 1);
        if (s_refs.cumdelta <= 0) sc.AddMessageToLog("G4: CumDelta introuvable", 1);

        s_resolved = true;
    }

    auto ReadSG = [&](int StudyID, int SubgraphIndex, int BarIndex)->double {
        if (StudyID <= 0) return 0.0;
        SCFloatArray Subgraph;
        sc.GetStudyArrayUsingID(StudyID, SubgraphIndex, Subgraph);
        if (Subgraph.GetArraySize() == 0 || BarIndex < 0 || BarIndex >= Subgraph.GetArraySize())
            return 0.0;
        return Subgraph[BarIndex];
    };

    auto EnforceVVA = [&](double& val, double& poc, double& vah){
        if (val > vah) std::swap(val, vah);
        if (poc < val) poc = val;
        if (poc > vah) poc = vah;
    };

    auto NBCV_OK = [&](double total, double ask, double bid, double eps=1e-9)->bool {
        return (total + eps) >= (ask + bid);
    };

    // Format YYYYMMDD à partir d'un SCDateTime
    auto DateYYYYMMDD = [&](SCDateTime dt)->SCString {
        int Year=0, Month=0, Day=0, Hour=0, Minute=0, Second=0;
        dt.GetDateTimeYMDHMS(Year, Month, Day, Hour, Minute, Second);
        SCString s; s.Format("%04d%02d%02d", Year, Month, Day);
        return s;
    };

    // Fichier JSONL (append)
    auto AppendJSONL = [&](const SCString& filename, const SCString& jsonLine){
        FILE* f = fopen(filename.GetChars(), "ab");
        if (f)
        {
            fwrite(jsonLine.GetChars(), 1, jsonLine.GetLength(), f);
            fwrite("\n", 1, 1, f);
            fclose(f);
        }
        else
        {
            SCString msg; msg.Format("G4: Impossible d'ouvrir %s", filename.GetChars());
            sc.AddMessageToLog(msg, 1);
        }
    };

    // Build chemin : "<outdir>\\chart_4_<kind>_<yyyymmdd>.jsonl"
    auto BuildOutfile = [&](const char* kind, SCDateTime dt)->SCString {
        SCString outdir = In_OutputDir.GetString();
        SCString d = DateYYYYMMDD(dt);
        SCString path;
        path.Format("%s\\chart_4_%s_%s.jsonl", outdir.GetChars(), kind, d.GetChars());
        return path;
    };

    // Write-If-Changed cache par (kind,i)
    static std::map<std::string, std::string> s_lastPayloadByKey;
    auto KeyKindIndex = [&](const char* kind, int i)->std::string{
        std::ostringstream oss; oss<<kind<<"#"<<i; return oss.str();
    };
    auto ShouldWriteChanged = [&](const char* kind, int i, const SCString& payload)->bool{
        std::string k = KeyKindIndex(kind, i);
        auto it = s_lastPayloadByKey.find(k);
        if (it != s_lastPayloadByKey.end() && it->second == std::string(payload.GetChars()))
            return false;
        s_lastPayloadByKey[k] = payload.GetChars();
        return true;
    };

    // Timestamps monotones par fichier/kind
    struct TsMonotone { double last = -1e300; bool ok(double t){ if (t < last) return false; last = t; return true; } };
    static TsMonotone ts_vwap, ts_vva, ts_vva_prev, ts_prev_vp, ts_prev_vwap, ts_nbcv, ts_cumdelta, ts_vp, ts_atr, ts_corr;

    // Symbole (override si fourni)
    SCString Sym = In_SymbolOverride.GetString();
    if (Sym.GetLength() == 0)
        Sym = sc.Symbol;

    // Index barre courant
    const int i = sc.Index;
    if (i < 0) return;

    // Timestamp source (double)
    const double t = sc.BaseDateTimeIn[i].GetAsDouble();

    // =========================
    // ====== EXPORTS ==========
    // =========================

    // --- VWAP (SG0 = vwap, SG1..SG6 = bands) ---
    if (In_EnableVWAP.GetYesNo() && s_refs.vwap > 0)
    {
        double vw  = ReadSG(s_refs.vwap, 0, i);
        double sd1 = ReadSG(s_refs.vwap, 1, i);
        double sd2 = ReadSG(s_refs.vwap, 2, i);
        double sd3 = ReadSG(s_refs.vwap, 3, i);
        double sd4 = ReadSG(s_refs.vwap, 4, i);
        double sd5 = ReadSG(s_refs.vwap, 5, i);
        double sd6 = ReadSG(s_refs.vwap, 6, i);

        if (ts_vwap.ok(t))
        {
            SCString json;
            json.Format("{\"sym\":\"%s\",\"t\":%.9f,\"i\":%d,"
                        "\"vwap\":%.6f,\"sd1\":%.6f,\"sd2\":%.6f,\"sd3\":%.6f,\"sd4\":%.6f,\"sd5\":%.6f,\"sd6\":%.6f}",
                        Sym.GetChars(), t, i, vw, sd1, sd2, sd3, sd4, sd5, sd6);

            if (ShouldWriteChanged("vwap", i, json))
                AppendJSONL(BuildOutfile("vwap", sc.BaseDateTimeIn[i]), json);
        }
        else sc.AddMessageToLog("G4 VWAP: timestamp non monotone -> skip", 1);
    }

    // --- VVA courant (SG0=POC, SG1=VAH, SG2=VAL) ---
    if (In_EnableVVA.GetYesNo() && s_refs.vva > 0)
    {
        double poc = ReadSG(s_refs.vva, 0, i);
        double vah = ReadSG(s_refs.vva, 1, i);
        double val = ReadSG(s_refs.vva, 2, i);
        EnforceVVA(val, poc, vah);

        if (ts_vva.ok(t))
        {
            SCString json;
            json.Format("{\"sym\":\"%s\",\"t\":%.9f,\"i\":%d,\"poc\":%.6f,\"vah\":%.6f,\"val\":%.6f}",
                        Sym.GetChars(), t, i, poc, vah, val);

            if (ShouldWriteChanged("vva", i, json))
                AppendJSONL(BuildOutfile("vva", sc.BaseDateTimeIn[i]), json);
        }
        else sc.AddMessageToLog("G4 VVA: timestamp non monotone -> skip", 1);
    }

    // --- VVA Previous (SG0=PrevPOC, SG1=PrevVAH, SG2=PrevVAL) ---
    if (In_EnableVVAPrevious.GetYesNo() && s_refs.vva_prev > 0)
    {
        double ppoc = ReadSG(s_refs.vva_prev, 0, i);
        double pvah = ReadSG(s_refs.vva_prev, 1, i);
        double pval = ReadSG(s_refs.vva_prev, 2, i);

        // non initialisé -> skip
        if (!(ppoc==0.0 && pvah==0.0 && pval==0.0))
        {
            EnforceVVA(pval, ppoc, pvah);
            if (ts_vva_prev.ok(t))
            {
                SCString json;
                json.Format("{\"sym\":\"%s\",\"t\":%.9f,\"i\":%d,\"ppoc\":%.6f,\"pvah\":%.6f,\"pval\":%.6f}",
                            Sym.GetChars(), t, i, ppoc, pvah, pval);

                if (ShouldWriteChanged("vva_previous", i, json))
                    AppendJSONL(BuildOutfile("vva_previous", sc.BaseDateTimeIn[i]), json);
            }
            else sc.AddMessageToLog("G4 VVA_PREV: timestamp non monotone -> skip", 1);
        }
    }

    // --- Previous VP : pvpoc/pvah/pval + pvwap ---
    if (In_EnablePrevVP.GetYesNo() && s_refs.vva_prev > 0 && s_refs.vwap > 0)
    {
        double pvpoc = ReadSG(s_refs.vva_prev, 0, i);
        double pvah  = ReadSG(s_refs.vva_prev, 1, i);
        double pval  = ReadSG(s_refs.vva_prev, 2, i);

        // Exemple : PVWAP = VWAP(i-1). Adapte si tu utilises la VWAP de la veille par session.
        double pvwap = (i > 0 ? ReadSG(s_refs.vwap, 0, i-1) : 0.0);

        if (!(pvpoc==0.0 && pvah==0.0 && pval==0.0))
        {
            EnforceVVA(pval, pvpoc, pvah);
            if (ts_prev_vp.ok(t))
            {
                SCString json;
                json.Format("{\"sym\":\"%s\",\"t\":%.9f,\"i\":%d,"
                            "\"pvpoc\":%.6f,\"pvah\":%.6f,\"pval\":%.6f,\"pvwap\":%.6f}",
                            Sym.GetChars(), t, i, pvpoc, pvah, pval, pvwap);

                if (ShouldWriteChanged("previous_vp", i, json))
                    AppendJSONL(BuildOutfile("previous_vp", sc.BaseDateTimeIn[i]), json);
            }
            else sc.AddMessageToLog("G4 PREV_VP: timestamp non monotone -> skip", 1);
        }
    }

    // --- Previous VWAP : pvwap / psd1 / psd2 (extrait de VWAP(i-1)) ---
    if (In_EnablePrevVWAP.GetYesNo() && s_refs.vwap > 0)
    {
        double pvwp = (i > 0 ? ReadSG(s_refs.vwap, 0, i-1) : 0.0);
        double psd1 = (i > 0 ? ReadSG(s_refs.vwap, 1, i-1) : 0.0);
        double psd2 = (i > 0 ? ReadSG(s_refs.vwap, 2, i-1) : 0.0);

        if (!(pvwp==0.0 && psd1==0.0 && psd2==0.0))
        {
            if (ts_prev_vwap.ok(t))
            {
                SCString json;
                json.Format("{\"sym\":\"%s\",\"t\":%.9f,\"i\":%d,"
                            "\"pvwap\":%.6f,\"psd1\":%.6f,\"psd2\":%.6f}",
                            Sym.GetChars(), t, i, pvwp, psd1, psd2);

                if (ShouldWriteChanged("previous_vwap", i, json))
                    AppendJSONL(BuildOutfile("previous_vwap", sc.BaseDateTimeIn[i]), json);
            }
            else sc.AddMessageToLog("G4 PREV_VWAP: timestamp non monotone -> skip", 1);
        }
    }

    // --- NBCV (Delta, AskVol, BidVol, Trades, TotalVol) ---
    if (In_EnableNBCV.GetYesNo() && s_refs.nbcv > 0)
    {
        double delt = ReadSG(s_refs.nbcv, 0,  i);  // Delta
        double ask  = ReadSG(s_refs.nbcv, 5,  i);  // Ask Volume
        double bid  = ReadSG(s_refs.nbcv, 6,  i);  // Bid Volume
        double trad = ReadSG(s_refs.nbcv, 11, i);  // Trades Count (souvent entier)
        double tot  = ReadSG(s_refs.nbcv, 12, i);  // Total Volume

        if (!NBCV_OK(tot, ask, bid))
        {
            sc.AddMessageToLog("G4 NBCV: total < ask+bid -> skip", 1);
        }
        else if (ts_nbcv.ok(t))
        {
            SCString json;
            json.Format("{\"sym\":\"%s\",\"t\":%.9f,\"i\":%d,"
                        "\"delta\":%.6f,\"askvol\":%.6f,\"bidvol\":%.6f,"
                        "\"trades\":%.0f,\"totalvol\":%.6f}",
                        Sym.GetChars(), t, i, delt, ask, bid, trad, tot);

            if (ShouldWriteChanged("nbcv", i, json))
                AppendJSONL(BuildOutfile("nbcv", sc.BaseDateTimeIn[i]), json);
        }
        else sc.AddMessageToLog("G4 NBCV: timestamp non monotone -> skip", 1);
    }

    // --- Cumulative Delta (Volume) ---
    if (In_EnableCumDelta.GetYesNo() && s_refs.cumdelta > 0)
    {
        double cd = ReadSG(s_refs.cumdelta, 0, i);
        if (ts_cumdelta.ok(t))
        {
            SCString json;
            json.Format("{\"sym\":\"%s\",\"t\":%.9f,\"i\":%d,\"cumulative_delta\":%.6f}",
                        Sym.GetChars(), t, i, cd);

            if (ShouldWriteChanged("cumulative_delta", i, json))
                AppendJSONL(BuildOutfile("cumulative_delta", sc.BaseDateTimeIn[i]), json);
        }
        else sc.AddMessageToLog("G4 CumDelta: timestamp non monotone -> skip", 1);
    }

    // --- Volume Profile (si présent) ---
    // NOTE: selon l’étude, les subgraphs exportables varient. Exemple minimal : VVA-like si exposé.
    // Ici, on tentera d’extraire val/vpoc/vah + hvn/lvn si dispo (SG indices à ajuster selon ton chart).
    if (In_EnableVolumeProf.GetYesNo() && s_refs.volprof > 0)
    {
        // Exemple générique : si ton étude expose (comme VVA) SG0=poc,1=vah,2=val
        double vp_poc = ReadSG(s_refs.volprof, 0, i);
        double vp_vah = ReadSG(s_refs.volprof, 1, i);
        double vp_val = ReadSG(s_refs.volprof, 2, i);
        double hvn    = ReadSG(s_refs.volprof, 3, i); // si non dispo → 0
        double lvn    = ReadSG(s_refs.volprof, 4, i); // si non dispo → 0

        // garde ordre
        EnforceVVA(vp_val, vp_poc, vp_vah);

        if (ts_vp.ok(t))
        {
            SCString json;
            json.Format("{\"sym\":\"%s\",\"t\":%.9f,\"i\":%d,"
                        "\"val\":%.6f,\"vpoc\":%.6f,\"vah\":%.6f,\"hvn\":%.6f,\"lvn\":%.6f}",
                        Sym.GetChars(), t, i, vp_val, vp_poc, vp_vah, hvn, lvn);

            if (ShouldWriteChanged("volume_profile", i, json))
                AppendJSONL(BuildOutfile("volume_profile", sc.BaseDateTimeIn[i]), json);
        }
        else sc.AddMessageToLog("G4 VolumeProfile: timestamp non monotone -> skip", 1);
    }

    // --- ATR (optionnel) ---
    if (In_EnableATR.GetYesNo() && s_refs.atr > 0)
    {
        // SG0 = ATR value
        double atr = ReadSG(s_refs.atr, 0, i);
        if (ts_atr.ok(t))
        {
            SCString json;
            json.Format("{\"sym\":\"%s\",\"t\":%.9f,\"i\":%d,\"atr\":%.6f}",
                        Sym.GetChars(), t, i, atr);

            if (ShouldWriteChanged("atr", i, json))
                AppendJSONL(BuildOutfile("atr", sc.BaseDateTimeIn[i]), json);
        }
        else sc.AddMessageToLog("G4 ATR: timestamp non monotone -> skip", 1);
    }

    // --- Correlation (optionnel) ---
    if (In_EnableCorrelation.GetYesNo() && s_refs.corr > 0)
    {
        // SG0 = Correlation value (selon param de l'étude)
        double corr = ReadSG(s_refs.corr, 0, i);
        if (ts_corr.ok(t))
        {
            SCString json;
            json.Format("{\"sym\":\"%s\",\"t\":%.9f,\"i\":%d,\"correlation\":%.6f}",
                        Sym.GetChars(), t, i, corr);

            if (ShouldWriteChanged("correlation", i, json))
                AppendJSONL(BuildOutfile("correlation", sc.BaseDateTimeIn[i]), json);
        }
        else sc.AddMessageToLog("G4 Correlation: timestamp non monotone -> skip", 1);
    }
}

                      sym.GetChars(), t, i, cumdelta);
          AppendJSONL(fn, line);
          lcd.cumdelta = cumdelta;
        }
      }
    }
  }
}
                      sym.GetChars(), t, i, cumdelta);
          AppendJSONL(fn, line);
          lcd.cumdelta = cumdelta;
        }
      }
    }
  }
}
                      sym.GetChars(), t, i, cumdelta);
          AppendJSONL(fn, line);
          lcd.cumdelta = cumdelta;
        }
      }
    }
  }
}