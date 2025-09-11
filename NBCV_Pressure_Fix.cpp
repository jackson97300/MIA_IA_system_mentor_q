// Patch pour corriger NBCV pressure_bearish = 0
// À intégrer dans le dumper principal

// CORRECTION NBCV PRESSURE BEARISH
// Remplace la logique existante par ceci :

void ComputeNBCVPressure(
  double ask_volume, double bid_volume, 
  int& pressure_bullish, int& pressure_bearish,
  double th_ratio = 1.20,  // seuil pour ratio
  double th_delta = 0.60   // seuil pour delta_ratio
) {
  // RÉINITIALISATION à chaque calcul
  pressure_bullish = 0;
  pressure_bearish = 0;
  
  if (ask_volume <= 0.0 || bid_volume <= 0.0) return;
  
  // Calculs des ratios
  double ask_bid_ratio = ask_volume / bid_volume;
  double bid_ask_ratio = bid_volume / ask_volume;
  double delta = ask_volume - bid_volume;
  double delta_ratio = delta / (ask_volume + bid_volume);
  
  // CONDITIONS DISJOINTES (pas de else qui écrase)
  // Pressure Bullish
  if (ask_bid_ratio >= th_ratio && delta > 0.0) {
    pressure_bullish = 1;
  }
  
  // Pressure Bearish  
  if (bid_ask_ratio >= th_ratio && delta < 0.0) {
    pressure_bearish = 1;
  }
  
  // Alternative: conditions basées sur delta_ratio
  if (delta_ratio >= th_delta) {
    pressure_bullish = 1;
  }
  if (delta_ratio <= -th_delta) {
    pressure_bearish = 1;
  }
}

// EXEMPLE D'UTILISATION dans le dumper :
/*
// Dans la section NBCV du dumper principal
double ask_vol = /* calcul ask volume */;
double bid_vol = /* calcul bid volume */;
int pressure_bullish = 0, pressure_bearish = 0;

ComputeNBCVPressure(ask_vol, bid_vol, pressure_bullish, pressure_bearish);

// Écrire dans le JSON
SCString nbcv;
nbcv.Format("{\"t\":%.6f,\"type\":\"nbcv_metrics\",\"chart\":%d,\"i\":%d,"
            "\"ask_volume\":%.2f,\"bid_volume\":%.2f,"
            "\"pressure_bullish\":%d,\"pressure_bearish\":%d,"
            "\"delta_ratio\":%.4f}",
            tnow, chartNum, iLast, ask_vol, bid_vol, 
            pressure_bullish, pressure_bearish, delta_ratio);
WritePerChartDaily(chartNum, nbcv);
*/
