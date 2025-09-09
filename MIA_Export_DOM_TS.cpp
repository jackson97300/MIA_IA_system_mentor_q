#include "sierrachart.h"
#ifdef _WIN32
#include <windows.h>
#endif

SCDLLName("MIA_Export_DOM_TS")

// ====== GLOBALES ======
SCString g_sym;
FILE* g_file = nullptr;
HANDLE g_pipe = INVALID_HANDLE_VALUE;

// ====== CONFIGURATION DE COLLECTE OPTIMISÉE PAR GRAPHIQUE ======
struct GraphConfig {
    bool collect_time_sales = false;     // Time & Sales (trades + autres évts)
    bool collect_quotes = false;         // Quotes BID/ASK (niveau 1)
    bool collect_market_depth = false;   // Market Depth natif multi-niveaux
    bool collect_vwap = false;           // VWAP + SD
    bool collect_footprint = false;      // Footprint/Delta
    bool collect_volume_profile = false; // Volume Profile
    bool collect_basedata = false;       // BaseData
    bool collect_subgraphs = false;      // Subgraphs
    bool collect_price = false;          // Prix simple
};

// Configuration courante (pilotée par Inputs)
GraphConfig g_graph_config;

// ====== FONCTIONS UTILITAIRES ======
SCString JsonEscape(const SCString& str) {
    SCString result;
    for (int i = 0; i < str.GetLength(); ++i) {
        char c = str[i];
        if (c == '"') result += "\\\"";
        else if (c == '\\') result += "\\\\";
        else if (c == '\n') result += "\\n";
        else if (c == '\r') result += "\\r";
        else if (c == '\t') result += "\\t";
        else result += c;
    }
    return result;
}

void FileWriteLine(const SCString& line) {
    try {
        if (!g_file) {
            // Utiliser un chemin absolu pour s'assurer que le fichier est créé
            g_file = fopen("D:\\MIA_IA_system\\MIA_feed.jsonl", "a");

            if (g_file) {
                // Drapeau de démarrage
                fprintf(
                    g_file,
                    "{\"t\":%.6f,\"sym\":\"%s\",\"type\":\"startup\",\"msg\":\"MIA_Export_DOM_TS_started\"}\n",
                    (double)time(NULL),
                    g_sym.GetLength() > 0 ? g_sym.GetChars() : "UNKNOWN"
                );
                fflush(g_file);
            }
        }
        if (g_file) {
            fprintf(g_file, "%s\n", line.GetChars());
            fflush(g_file);
        }
    } catch (...) {
        // Ne bloque pas l'étude en cas d'erreur d'écriture
    }
}

#ifdef _WIN32
void PipeWriteLine(const SCString& line) {
    if (g_pipe == INVALID_HANDLE_VALUE) {
        g_pipe = CreateFileA("\\\\.\\pipe\\MIA_PIPE", GENERIC_WRITE, 0, nullptr, OPEN_EXISTING, 0, nullptr);
    }
    if (g_pipe != INVALID_HANDLE_VALUE) {
        DWORD written;
        SCString data = line + "\n";
        WriteFile(g_pipe, data.GetChars(), (DWORD)data.GetLength(), &written, nullptr);
    }
}
#endif

// ====== FONCTION PRINCIPALE ======
SCSFExport scsf_MIA_Export_DOM_TS(SCStudyInterfaceRef sc) {
    // ====== CONFIGURATION ======
    if (sc.SetDefaults) {
        sc.GraphName = "MIA Export DOM TS";
        sc.AutoLoop = 0;                 // Mode manuel
        sc.UpdateAlways = 1;             // À chaque tick
        sc.GraphRegion = 0;
        sc.ValueFormat = 2;
        sc.ScaleRangeType = SCALE_AUTO;

        // Activer DOM natif
        sc.UsesMarketDepthData = 1;

        // ====== INPUTS ======
        sc.Input[0].Name = "Collect Time&Sales";
        sc.Input[0].SetYesNo(true);

        sc.Input[1].Name = "Collect Market Depth";
        sc.Input[1].SetYesNo(false);

        sc.Input[2].Name = "Collect VWAP";
        sc.Input[2].SetYesNo(false);

        sc.Input[3].Name = "Collect Volume Profile";
        sc.Input[3].SetYesNo(false);

        sc.Input[4].Name = "Collect Footprint";
        sc.Input[4].SetYesNo(false);

        sc.Input[5].Name = "Chart Role (1=TS,2=DOM+TS,3=VWAP+VP,4=Footprint)";
        sc.Input[5].SetInt(1);

        sc.Input[6].Name = "Instance ID";
        sc.Input[6].SetInt(1);

        return;
    }

    // ====== INITIALISATION ======
    if (sc.IsFullRecalculation) {
        g_sym = sc.Symbol;

        const int in_role = sc.Input[5].GetInt();
        const bool in_collect_ts   = sc.Input[0].GetYesNo();
        const bool in_collect_dom  = sc.Input[1].GetYesNo();
        const bool in_collect_vwap = sc.Input[2].GetYesNo();
        const bool in_collect_vp   = sc.Input[3].GetYesNo();
        const bool in_collect_fp   = sc.Input[4].GetYesNo();

        switch (in_role) {
            case 1:  // Graphique 1 : Footprint uniquement
                g_graph_config.collect_time_sales = false;
                g_graph_config.collect_quotes = false;
                g_graph_config.collect_market_depth = false;
                g_graph_config.collect_vwap = false;
                g_graph_config.collect_footprint = in_collect_fp;
                g_graph_config.collect_volume_profile = false;
                g_graph_config.collect_basedata = true;
                g_graph_config.collect_subgraphs = true;
                g_graph_config.collect_price = false;
                break;

            case 2:  // Graphique 2 : DOM + T&S
                g_graph_config.collect_time_sales = in_collect_ts;
                g_graph_config.collect_quotes = in_collect_ts;
                g_graph_config.collect_market_depth = in_collect_dom;
                g_graph_config.collect_vwap = false;
                g_graph_config.collect_footprint = false;
                g_graph_config.collect_volume_profile = false;
                g_graph_config.collect_basedata = false;
                g_graph_config.collect_subgraphs = false;
                g_graph_config.collect_price = false;
                break;

            case 3:  // Graphique 3 : VWAP uniquement
                g_graph_config.collect_time_sales = false;
                g_graph_config.collect_quotes = false;
                g_graph_config.collect_market_depth = false;
                g_graph_config.collect_vwap = in_collect_vwap;
                g_graph_config.collect_footprint = false;
                g_graph_config.collect_volume_profile = false;
                g_graph_config.collect_basedata = false;
                g_graph_config.collect_subgraphs = false;
                g_graph_config.collect_price = true;
                break;

            case 4:  // Graphique 4 : Volume Profile uniquement
                g_graph_config.collect_time_sales = false;
                g_graph_config.collect_quotes = false;
                g_graph_config.collect_market_depth = false;
                g_graph_config.collect_vwap = false;
                g_graph_config.collect_footprint = false;
                g_graph_config.collect_volume_profile = in_collect_vp;
                g_graph_config.collect_basedata = true;
                g_graph_config.collect_subgraphs = true;
                g_graph_config.collect_price = false;
                break;

            default: // Graphiques supplémentaires : collecte large
                g_graph_config.collect_time_sales = in_collect_ts;
                g_graph_config.collect_quotes = in_collect_ts;
                g_graph_config.collect_market_depth = in_collect_dom;
                g_graph_config.collect_vwap = in_collect_vwap;
                g_graph_config.collect_footprint = in_collect_fp;
                g_graph_config.collect_volume_profile = in_collect_vp;
                g_graph_config.collect_basedata = true;
                g_graph_config.collect_subgraphs = true;
                g_graph_config.collect_price = true;
                break;
        }

        SCString debug_msg;
        debug_msg.Format("{\"t\":%.6f,\"sym\":\"%s\",\"type\":\"init\",\"chart\":%d,\"config\":\"optimized_collection\",\"msg\":\"MIA_Export_DOM_TS_initialized\"}",
                         sc.CurrentSystemDateTime.GetAsDouble(), JsonEscape(g_sym).GetChars(), sc.ChartNumber);
        FileWriteLine(debug_msg);
    }

    // MAJ symbole si besoin
    if (g_sym.GetLength() == 0 || g_sym == "UNKNOWN") {
        g_sym = sc.Symbol;
    }

    // ====== LECTURE DE L'INSTANCE ID ======
    const int instance_id = sc.Input[6].GetInt();

    // ====== TIME & SALES : QUOTES + TRADES + METRICS ======
    static int last_ts_count = 0;
    // Suppression de la boucle de debug qui tourne en boucle
    // static int tick_counter = 0;
    // tick_counter++;
    // if (tick_counter % 100 == 0) {
    //     SCString tick_debug;
    //     tick_debug.Format("{\"t\":%.6f,\"sym\":\"%s\",\"type\":\"debug\",\"tick\":%d,\"msg\":\"study_running\"}",
    //                       sc.CurrentSystemDateTime.GetAsDouble(), JsonEscape(g_sym).GetChars(), tick_counter);
    //     FileWriteLine(tick_debug);
    // }

    static double last_trade_price = 0.0;
    static int    last_trade_volume = 0;
    static double last_bid = 0.0;
    static double last_ask = 0.0;
    static int    last_bid_size = 0;
    static int    last_ask_size = 0;

    // Throttle pour realtime/stats
    static double last_rt_emit = 0.0;
    static double last_stats_emit = 0.0;
    const double RT_INTERVAL = 0.20;     // 200 ms
    const double STATS_INTERVAL = 0.50;  // 500 ms

    c_SCTimeAndSalesArray TnS;
    sc.GetTimeAndSales(TnS);
    int ts_sz = (int)TnS.Size();

    if (ts_sz < last_ts_count) {
        // Reset si redémarrage source T&S
        last_ts_count = 0;
        last_trade_price = 0.0;
        last_trade_volume = 0;
        last_bid = 0.0;
        last_ask = 0.0;
        last_bid_size = 0;
        last_ask_size = 0;
    }

    int    total_trades = 0;
    int    total_quotes = 0;
    double total_volume = 0.0;
    double total_value  = 0.0;
    double min_price = 9.0e99;
    double max_price = 0.0;

    for (int i = last_ts_count; i < ts_sz; ++i) {
        const s_TimeAndSales& ts = TnS[i];
        const double tsec = ts.DateTime.GetAsDouble();
        if (tsec <= 0.0)
            continue;

        // QUOTES (BID/ASK)
        if (ts.Type == SC_TS_BID || ts.Type == SC_TS_ASK) {
            if (ts.Bid > 0.0 && ts.Ask > 0.0 && ts.BidSize > 0 && ts.AskSize > 0) {
                last_bid = ts.Bid;
                last_ask = ts.Ask;
                last_bid_size = ts.BidSize;
                last_ask_size = ts.AskSize;

                if (g_graph_config.collect_quotes) {
                    SCString j_quote;
                    j_quote.Format(
                        R"({"t":%.6f,"sym":"%s","type":"quote","source":"ts","bid":%.8f,"ask":%.8f,"bq":%d,"aq":%d,"spread":%.8f,"mid":%.8f,"chart":%d,"instance_id":%d})",
                        tsec, JsonEscape(g_sym).GetChars(),
                        ts.Bid, ts.Ask, ts.BidSize, ts.AskSize,
                        ts.Ask - ts.Bid, (ts.Bid + ts.Ask) / 2.0, sc.ChartNumber, instance_id
                    );
                    #ifdef _WIN32
                        PipeWriteLine(j_quote);
                    #endif
                    FileWriteLine(j_quote);
                    total_quotes++;
                }
            }
        }
        // TRADES (ou autres enregistrements non BID/ASK si SC_TS_TRADE absent)
        #ifdef SC_TS_TRADE
        else if (ts.Type == SC_TS_TRADE) {
        #else
        else if (ts.Type != SC_TS_BID && ts.Type != SC_TS_ASK) {
        #endif
            if (ts.Price > 0.0 && ts.Volume > 0) {
                last_trade_price  = ts.Price;
                last_trade_volume = ts.Volume;

                total_trades++;
                total_volume += ts.Volume;
                total_value  += ts.Price * ts.Volume;
                if (ts.Price < min_price) min_price = ts.Price;
                if (ts.Price > max_price) max_price = ts.Price;

                if (g_graph_config.collect_time_sales) {
                    const double vwap_now = (total_volume > 0.0) ? (total_value / total_volume) : 0.0;
                    const double dpx = (last_trade_price > 0.0) ? (ts.Price - last_trade_price) : 0.0;

                    SCString j_trade;
                    j_trade.Format(
                        R"({"t":%.6f,"sym":"%s","type":"trade","source":"ts","px":%.8f,"qty":%d,"value":%.8f,"vwap":%.8f,"price_change":%.8f,"chart":%d,"instance_id":%d})",
                        tsec, JsonEscape(g_sym).GetChars(),
                        ts.Price, ts.Volume, ts.Price * ts.Volume,
                        vwap_now, dpx, sc.ChartNumber, instance_id
                    );
                    #ifdef _WIN32
                        PipeWriteLine(j_trade);
                    #endif
                    FileWriteLine(j_trade);
                }
            }
        }
        // AUTRES ÉVÉNEMENTS T&S
        else {
            if (g_graph_config.collect_time_sales) {
                SCString j_other;
                j_other.Format(
                    R"({"t":%.6f,"sym":"%s","type":"other","source":"ts","ts_type":%d,"price":%.8f,"volume":%d,"chart":%d,"instance_id":%d})",
                    tsec, JsonEscape(g_sym).GetChars(),
                    ts.Type, ts.Price, ts.Volume, sc.ChartNumber, instance_id
                );
                #ifdef _WIN32
                    PipeWriteLine(j_other);
                #endif
                FileWriteLine(j_other);
            }
        }
    }

    // Mise à jour du curseur T&S
    last_ts_count = ts_sz;

    // Stats T&S : cadence limitée
    {
        const double now_sec = sc.CurrentSystemDateTime.GetAsDouble();
        if (g_graph_config.collect_time_sales && (now_sec - last_stats_emit) >= STATS_INTERVAL) {
            if (total_volume > 0.0) {
                const double avg = total_value / total_volume;
                SCString j_stats;
                j_stats.Format(
                    R"({"t":%.6f,"sym":"%s","type":"ts_stats","source":"ts","total_trades":%d,"total_quotes":%d,"total_volume":%.8f,"avg_price":%.8f,"min_price":%.8f,"max_price":%.8f,"last_bid":%.8f,"last_ask":%.8f,"chart":%d,"instance_id":%d})",
                    now_sec, JsonEscape(g_sym).GetChars(),
                    total_trades, total_quotes, total_volume, avg,
                    (min_price < 9.0e98 ? min_price : 0.0), (max_price > 0.0 ? max_price : 0.0),
                    last_bid, last_ask, sc.ChartNumber, instance_id
                );
                #ifdef _WIN32
                    PipeWriteLine(j_stats);
                #endif
                FileWriteLine(j_stats);
            }
            last_stats_emit = now_sec;
        }

        if ((g_graph_config.collect_time_sales || g_graph_config.collect_quotes) && (now_sec - last_rt_emit) >= RT_INTERVAL) {
            SCString j_realtime;
            j_realtime.Format(
                R"({"t":%.6f,"sym":"%s","type":"realtime","source":"ts","last_trade":%.8f,"last_volume":%d,"last_bid":%.8f,"last_ask":%.8f,"spread":%.8f,"mid":%.8f,"chart":%d,"instance_id":%d})",
                now_sec, JsonEscape(g_sym).GetChars(),
                last_trade_price, last_trade_volume, last_bid, last_ask,
                (last_ask > 0.0 && last_bid > 0.0) ? (last_ask - last_bid) : 0.0,
                (last_ask > 0.0 && last_bid > 0.0) ? ((last_bid + last_ask) / 2.0) : 0.0,
                sc.ChartNumber, instance_id
            );
            #ifdef _WIN32
                PipeWriteLine(j_realtime);
            #endif
            FileWriteLine(j_realtime);
            last_rt_emit = now_sec;
        }
    }

    // ===== Market Depth natif multi-niveaux =====
    if (g_graph_config.collect_market_depth) {
        const int MAX_LVLS = 20;
        int nbid = sc.GetBidMarketDepthNumberOfLevels();
        int nask = sc.GetAskMarketDepthNumberOfLevels();
        if (nbid > MAX_LVLS) nbid = MAX_LVLS;
        if (nask > MAX_LVLS) nask = MAX_LVLS;

        const double now = sc.CurrentSystemDateTime.GetAsDouble();

        // BID side
        for (int i = 0; i < nbid; ++i) {
            s_MarketDepthEntry d{};
            if (sc.GetBidMarketDepthEntryAtLevel(d, i) && d.Price > 0.0 && d.Quantity > 0) {
                SCString j;
                j.Format(
                    R"({"t":%.6f,"sym":"%s","type":"depth","source":"dom","side":"BID","level":%d,"px":%.8f,"qty":%d,"chart":%d,"instance_id":%d})",
                    now, JsonEscape(g_sym).GetChars(), i, d.Price, (int)d.Quantity, sc.ChartNumber, instance_id
                );
                #ifdef _WIN32
                    PipeWriteLine(j);
                #endif
                FileWriteLine(j);
            }
        }
        // ASK side
        for (int i = 0; i < nask; ++i) {
            s_MarketDepthEntry d{};
            if (sc.GetAskMarketDepthEntryAtLevel(d, i) && d.Price > 0.0 && d.Quantity > 0) {
                SCString j;
                j.Format(
                    R"({"t":%.6f,"sym":"%s","type":"depth","source":"dom","side":"ASK","level":%d,"px":%.8f,"qty":%d,"chart":%d,"instance_id":%d})",
                    now, JsonEscape(g_sym).GetChars(), i, d.Price, (int)d.Quantity, sc.ChartNumber, instance_id
                );
                #ifdef _WIN32
                    PipeWriteLine(j);
                #endif
                FileWriteLine(j);
            }
        }
    }

    // ===== Index barre courant (sécurisé) =====
    const int idx = (sc.ArraySize > 0) ? (sc.ArraySize - 1) : 0;

    // ===== Prix simple (si activé) =====
    if (g_graph_config.collect_price && sc.ArraySize > 0) {
        SCString j_price;
        j_price.Format(
            R"({"t":%.6f,"sym":"%s","type":"price","source":"system","px":%.8f,"chart":%d,"instance_id":%d})",
            sc.CurrentSystemDateTime.GetAsDouble(), JsonEscape(g_sym).GetChars(), sc.Close[idx], sc.ChartNumber, instance_id
        );
        #ifdef _WIN32
            PipeWriteLine(j_price);
        #endif
        FileWriteLine(j_price);
    }

    // ===== VWAP + SD =====
    try {
        const int vwap_id = sc.GetStudyIDByName(sc.ChartNumber, "VWAP", 1);
        if (vwap_id > 0 && g_graph_config.collect_vwap && sc.ArraySize > 0) {
            SCFloatArray vwapArr, sd1pArr, sd1mArr, sd2pArr, sd2mArr;
            sc.GetStudyArrayFromChartUsingID(sc.ChartNumber, vwap_id, 0, vwapArr);  // VWAP
            sc.GetStudyArrayFromChartUsingID(sc.ChartNumber, vwap_id, 1, sd1pArr);  // +1SD
            sc.GetStudyArrayFromChartUsingID(sc.ChartNumber, vwap_id, 2, sd1mArr);  // -1SD
            sc.GetStudyArrayFromChartUsingID(sc.ChartNumber, vwap_id, 3, sd2pArr);  // +2SD
            sc.GetStudyArrayFromChartUsingID(sc.ChartNumber, vwap_id, 4, sd2mArr);  // -2SD

            SCString j_vwap;
            j_vwap.Format(
                R"({"t":%.6f,"sym":"%s","type":"vwap_sd","source":"vwap","vwap":%.8f,"sd_p1":%.8f,"sd_m1":%.8f,"sd_p2":%.8f,"sd_m2":%.8f,"chart":%d,"instance_id":%d})",
                sc.CurrentSystemDateTime.GetAsDouble(), JsonEscape(g_sym).GetChars(),
                vwapArr[idx], sd1pArr[idx], sd1mArr[idx], sd2pArr[idx], sd2mArr[idx], sc.ChartNumber, instance_id
            );
            #ifdef _WIN32
                PipeWriteLine(j_vwap);
            #endif
            FileWriteLine(j_vwap);
        }
    } catch (...) {
        // Continuer sans VWAP si erreur
    }

    // ===== FOOTPRINT (approche générique) =====
    try {
        int footprint_id = sc.GetStudyIDByName(sc.ChartNumber, "Footprint", 1);
        if (footprint_id <= 0)
            footprint_id = sc.GetStudyIDByName(sc.ChartNumber, "Volume by Price", 1);
        if (footprint_id <= 0)
            footprint_id = sc.GetStudyIDByName(sc.ChartNumber, "Cumulative Delta", 1);

        if (footprint_id > 0 && g_graph_config.collect_footprint && sc.ArraySize > 0) {
            SCFloatArray deltaArr, volumeArr, priceArr;
            sc.GetStudyArrayFromChartUsingID(sc.ChartNumber, footprint_id, 0, deltaArr);   // Delta (selon étude)
            sc.GetStudyArrayFromChartUsingID(sc.ChartNumber, footprint_id, 1, volumeArr);  // Volume
            sc.GetStudyArrayFromChartUsingID(sc.ChartNumber, footprint_id, 2, priceArr);   // Prix/Niveau

            if (volumeArr.GetArraySize() > 0) {
                const double currentDelta  = (deltaArr.GetArraySize() > idx)  ? deltaArr[idx]  : 0.0;
                const double currentVolume = (volumeArr.GetArraySize() > idx) ? volumeArr[idx] : 0.0;
                const double currentPrice  = (priceArr.GetArraySize() > idx)  ? priceArr[idx]  : 0.0;

                SCString j_footprint;
                j_footprint.Format(
                    R"({"t":%.6f,"sym":"%s","type":"footprint","source":"footprint","delta":%.8f,"volume":%.8f,"price":%.8f,"level":%d,"chart":%d,"instance_id":%d})",
                    sc.CurrentSystemDateTime.GetAsDouble(), JsonEscape(g_sym).GetChars(),
                    currentDelta, currentVolume, currentPrice, idx, sc.ChartNumber, instance_id
                );
                #ifdef _WIN32
                    PipeWriteLine(j_footprint);
                #endif
                FileWriteLine(j_footprint);
            }
        }
    } catch (...) {
        // Continuer sans Footprint si erreur
    }

    // ====== 4) BaseData / Subgraphs / Volume Profile ======
    try {
        // BaseData étendus
        if (g_graph_config.collect_basedata && sc.ArraySize > 0) {
            for (int bd = 0; bd < 50; ++bd) {
                if (sc.BaseData[bd].GetArraySize() > idx) {
                    SCString j_bd;
                    j_bd.Format(
                        R"({"t":%.6f,"sym":"%s","type":"basedata_extended","source":"basedata","bd":%d,"value":%.8f,"chart":%d,"instance_id":%d})",
                        sc.CurrentSystemDateTime.GetAsDouble(), JsonEscape(g_sym).GetChars(),
                        bd, sc.BaseData[bd][idx], sc.ChartNumber, instance_id
                    );
                    #ifdef _WIN32
                        PipeWriteLine(j_bd);
                    #endif
                    FileWriteLine(j_bd);
                }
            }
        }

        // Subgraphs génériques (placeholder)
        if (g_graph_config.collect_subgraphs) {
            for (int sg = 0; sg < 20; ++sg) {
                SCString j_sg;
                j_sg.Format(
                    R"({"t":%.6f,"sym":"%s","type":"subgraph","source":"subgraph","sg":%d,"value":%.8f,"chart":%d,"instance_id":%d})",
                    sc.CurrentSystemDateTime.GetAsDouble(), JsonEscape(g_sym).GetChars(),
                    sg, 0.0, sc.ChartNumber, instance_id
                );
                #ifdef _WIN32
                    PipeWriteLine(j_sg);
                #endif
                FileWriteLine(j_sg);
            }
        }

        // Prix/Index basique (traçabilité)
        if (g_graph_config.collect_basedata) {
            SCString j_basic;
            j_basic.Format(
                R"({"t":%.6f,"sym":"%s","type":"basic","source":"basedata","index":%d,"chart":%d,"instance_id":%d})",
                sc.CurrentSystemDateTime.GetAsDouble(), JsonEscape(g_sym).GetChars(),
                idx, sc.ChartNumber, instance_id
            );
            #ifdef _WIN32
                PipeWriteLine(j_basic);
            #endif
            FileWriteLine(j_basic);
        }

        // ===== Volume Profile =====
        int vp_id = -1;
        SCString vp_study_name = "";

        const char* vp_studies[] = {
            "Volume Value Area Lines",
            "Volume by Price",
            "MULTIPLE VOLUME PROFILE (VbP - 1 Days)",
            "Volume Profile",
            "VWAP Volume Profile",
            "Cumulative Volume Profile",
            "Smart Volume Profile",
            "Volume Profile VAH VAL POC"
        };

        for (int i = 0; i < 8 && vp_id <= 0; ++i) {
            vp_id = sc.GetStudyIDByName(sc.ChartNumber, vp_studies[i], 1);
            if (vp_id > 0) {
                vp_study_name = vp_studies[i];
                break;
            }
        }

        if (vp_id > 0 && g_graph_config.collect_volume_profile && sc.ArraySize > 0) {
            try {
                SCFloatArray allArrays[10];
                double poc = 0.0, vah = 0.0, val = 0.0;
                bool data_found = false;

                for (int sg = 0; sg < 10; ++sg)
                    sc.GetStudyArrayFromChartUsingID(sc.ChartNumber, vp_id, sg, allArrays[sg]);

                const int idx2 = sc.ArraySize - 1;

                // Mapping 1
                if (allArrays[0].GetArraySize() && allArrays[1].GetArraySize() && allArrays[2].GetArraySize()) {
                    poc = allArrays[0][idx2]; vah = allArrays[1][idx2]; val = allArrays[2][idx2];
                    if (poc || vah || val) data_found = true;
                }
                // Mapping 2
                if (!data_found && allArrays[1].GetArraySize() && allArrays[2].GetArraySize() && allArrays[3].GetArraySize()) {
                    poc = allArrays[1][idx2]; vah = allArrays[2][idx2]; val = allArrays[3][idx2];
                    if (poc || vah || val) data_found = true;
                }
                // Mapping 3
                if (!data_found && allArrays[2].GetArraySize() && allArrays[1].GetArraySize() && allArrays[0].GetArraySize()) {
                    poc = allArrays[2][idx2]; vah = allArrays[1][idx2]; val = allArrays[0][idx2];
                    if (poc || vah || val) data_found = true;
                }
                // Mapping 4 (auto)
                if (!data_found) {
                    for (int sg = 0; sg < 10; ++sg) {
                        if (allArrays[sg].GetArraySize() && allArrays[sg][idx2] != 0.0) {
                            if (poc == 0.0) poc = allArrays[sg][idx2];
                            else if (vah == 0.0) vah = allArrays[sg][idx2];
                            else if (val == 0.0) val = allArrays[sg][idx2];
                            else break;
                        }
                    }
                    if (poc || vah || val) data_found = true;
                }

                if (data_found) {
                    SCString j_vp;
                    j_vp.Format(
                        R"({"t":%.6f,"sym":"%s","type":"volume_profile","source":"vp","poc":%.8f,"vah":%.8f,"val":%.8f,"study":"%s","chart":%d,"instance_id":%d})",
                        sc.CurrentSystemDateTime.GetAsDouble(), JsonEscape(g_sym).GetChars(),
                        poc, vah, val, JsonEscape(vp_study_name).GetChars(), sc.ChartNumber, instance_id
                    );
                    #ifdef _WIN32
                        PipeWriteLine(j_vp);
                    #endif
                    FileWriteLine(j_vp);

                    for (int sg = 0; sg < 10; ++sg) {
                        if (allArrays[sg].GetArraySize()) {
                            SCString j_sg;
                            j_sg.Format(
                                R"({"t":%.6f,"sym":"%s","type":"volume_profile_subgraph","source":"vp","subgraph":%d,"value":%.8f,"study":"%s","chart":%d,"instance_id":%d})",
                                sc.CurrentSystemDateTime.GetAsDouble(), JsonEscape(g_sym).GetChars(),
                                sg, allArrays[sg][idx2], JsonEscape(vp_study_name).GetChars(), sc.ChartNumber, instance_id
                            );
                            #ifdef _WIN32
                                PipeWriteLine(j_sg);
                            #endif
                            FileWriteLine(j_sg);
                        }
                    }

                    const double vah_val_range = (vah && val) ? (vah - val) : 0.0;
                    const double poc_position  = (poc && vah && val && (vah - val) != 0.0)
                                               ? (poc - val) / (vah - val)
                                               : 0.0;

                    SCString j_stats;
                    j_stats.Format(
                        R"({"t":%.6f,"sym":"%s","type":"volume_profile_stats","source":"vp","vah_val_range":%.8f,"poc_position":%.8f,"study":"%s","chart":%d,"instance_id":%d})",
                        sc.CurrentSystemDateTime.GetAsDouble(), JsonEscape(g_sym).GetChars(),
                        vah_val_range, poc_position, JsonEscape(vp_study_name).GetChars(), sc.ChartNumber, instance_id
                    );
                    #ifdef _WIN32
                        PipeWriteLine(j_stats);
                    #endif
                    FileWriteLine(j_stats);
                }
            } catch (...) {
                SCString j_error;
                j_error.Format(
                    R"({"t":%.6f,"sym":"%s","type":"error","source":"vp","msg":"volume_profile_not_accessible","chart":%d,"instance_id":%d})",
                    sc.CurrentSystemDateTime.GetAsDouble(), JsonEscape(g_sym).GetChars(), sc.ChartNumber, instance_id
                );
                #ifdef _WIN32
                    PipeWriteLine(j_error);
                #endif
                FileWriteLine(j_error);
            }
        }
    } catch (...) {
        // Erreurs globales BaseData/Subgraphs/VP ignorées (robustesse)
    }

} // fin scsf_MIA_Export_DOM_TS
