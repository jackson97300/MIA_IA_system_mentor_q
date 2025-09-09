// ========== PATCH DE NORMALISATION DES QUOTES ==========
// À insérer dans la fonction de traitement des quotes du dumper

// Fonction de normalisation des prix (à ajouter dans la classe)
inline double NormalizeQuotePrice(const SCStudyInterfaceRef& sc, double raw_price, double tick_size = 0.25)
{
    // Détection et correction des prix ×100
    if (raw_price > 100000.0) {
        raw_price /= 100.0;
    }
    
    // Normalisation au tick size
    raw_price = sc.RoundToTickSize(raw_price, tick_size);
    
    return raw_price;
}

// Dans la fonction de traitement des quotes, remplacer :
// const double bid = quote_data.bid;
// const double ask = quote_data.ask;

// Par :
const double raw_bid = quote_data.bid;
const double raw_ask = quote_data.ask;

// Normalisation des prix
const double bid = NormalizeQuotePrice(sc, raw_bid);
const double ask = NormalizeQuotePrice(sc, raw_ask);

// Validation que le spread est raisonnable (max 5 ticks)
const double max_spread = 5.0 * sc.TickSize;
if (abs(ask - bid) <= max_spread) {
    // Écrire la quote normalisée
    SCString j;
    j.Format("{\"t\":%.6f,\"type\":\"quote\",\"bid\":%.8f,\"ask\":%.8f,\"spread\":%.8f}",
             timestamp, bid, ask, ask - bid);
    WritePerChartDaily(sc.ChartNumber, j);
} else {
    // Log de diagnostic pour les spreads aberrants
    SCString d;
    d.Format("{\"t\":%.6f,\"type\":\"quote_diag\",\"msg\":\"spread_too_large\",\"bid\":%.8f,\"ask\":%.8f,\"spread\":%.8f}",
             timestamp, bid, ask, ask - bid);
    WritePerChartDaily(sc.ChartNumber, d);
}







