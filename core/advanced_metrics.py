# advanced_metrics.py
"""
Module de calcul des métriques avancées pour le trading algorithmique
Version professionnelle avec bonnes pratiques de l'industrie
"""

from collections import deque, defaultdict
import time
import math
from typing import Dict, Any, Optional, List, Tuple

# Configuration par défaut pour ES
TICK_SIZE = 0.25

def _sign(x: float) -> int:
    """Retourne le signe d'un nombre (-1, 0, 1)"""
    return 1 if x > 0 else (-1 if x < 0 else 0)

class EWMA:
    """Exponential Weighted Moving Average pour lissage des métriques"""
    def __init__(self, alpha: float = 0.3):
        self.alpha = alpha
        self._y = None

    def update(self, x: float) -> float:
        if self._y is None:
            self._y = x
        else:
            self._y = self.alpha * x + (1 - self.alpha) * self._y
        return self._y

class RollingCounter:
    """Compteur de trades/volumes par prix sur une fenêtre temporelle"""
    def __init__(self, window_sec: float = 5.0):
        self.window_sec = window_sec
        self.q = deque()  # (ts, price, size)
        self.trades_at_price = defaultdict(int)
        self.size_at_price = defaultdict(float)

    def push_trade(self, ts: float, price: float, size: float):
        """Ajoute un trade au compteur"""
        self.q.append((ts, price, size))
        self.trades_at_price[price] += 1
        self.size_at_price[price] += size
        self._evict(ts)

    def stats_for(self, price: float) -> Tuple[int, float]:
        """Retourne (nombre_trades, volume_total) pour un prix"""
        return self.trades_at_price.get(price, 0), self.size_at_price.get(price, 0.0)

    def _evict(self, now_ts: float):
        """Supprime les trades trop anciens"""
        while self.q and (now_ts - self.q[0][0] > self.window_sec):
            ts, price, size = self.q.popleft()
            self.trades_at_price[price] -= 1
            if self.trades_at_price[price] <= 0:
                self.trades_at_price.pop(price, None)
            self.size_at_price[price] -= size
            if self.size_at_price[price] <= 0:
                self.size_at_price.pop(price, None)

class AdvancedMetrics:
    """
    Calculateur de métriques avancées pour le trading algorithmique
    
    Calcule en streaming (tick par tick) les métriques suivantes :
    - quotes.speed_up : Vitesse des quotes (EWMA)
    - last_wick_ticks : Taille des mèches (upper, lower, total)
    - cvd : Cumulative Volume Delta
    - delta_burst : Rafale de delta
    - delta_flip : Changement de signe du delta
    - stacked_imbalance.rows : Déséquilibres DOM consécutifs
    - absorption : Absorption au meilleur prix
    - iceberg : Détection d'ordres iceberg
    - gamma_flip : Bascule des niveaux gamma
    """
    
    def __init__(self,
                 quotes_alpha: float = 0.3,
                 dom_imbalance_thresh: float = 3.0,
                 absorption_window: float = 3.0,
                 iceberg_window: float = 4.0,
                 iceberg_min_trades: int = 5,
                 tick_size: float = TICK_SIZE):
        """
        Initialise le calculateur de métriques avancées
        
        Args:
            quotes_alpha: Alpha pour EWMA des quotes (0.3 = réactif, 0.1 = lisse)
            dom_imbalance_thresh: Seuil de déséquilibre DOM (3.0 = 3:1 ratio)
            absorption_window: Fenêtre temporelle pour absorption (secondes)
            iceberg_window: Fenêtre temporelle pour iceberg (secondes)
            iceberg_min_trades: Nombre minimum de trades pour détecter iceberg
            tick_size: Taille du tick (0.25 pour ES)
        """
        self.tick_size = tick_size
        
        # Quotes speed (EWMA)
        self.last_bbo = None  # (bid, ask, ts)
        self.ewma_quotes = EWMA(alpha=quotes_alpha)

        # Delta / CVD
        self.prev_delta = 0.0
        self.cvd = 0.0

        # OHLC cache (pour wick)
        self.last_bar = None  # dict avec open, high, low, close

        # DOM
        self.dom_imbalance_thresh = dom_imbalance_thresh

        # Absorption
        self.absorption_window = absorption_window
        self.absorb_buf = deque()  # (ts, best_bid, best_ask, mid, traded_at_bb, traded_at_ba)

        # Iceberg
        self.iceberg_window = iceberg_window
        self.iceberg_min_trades = iceberg_min_trades
        self.rolling_trades = RollingCounter(window_sec=iceberg_window)
        self.displayed_qty_history = {}  # price -> last displayed qty seen

        # Gamma
        self.prev_price = None
        self.prev_gamma_level = None

    # ---------- helpers ----------
    @staticmethod
    def _mid(bid: Optional[float], ask: Optional[float]) -> Optional[float]:
        """Calcule le prix médian"""
        if bid is None or ask is None:
            return None
        return 0.5 * (bid + ask)

    @staticmethod
    def _consecutive_rows(booleans: List[bool]) -> int:
        """Compte le nombre de True consécutifs depuis le début"""
        cnt = 0
        for b in booleans:
            if b:
                cnt += 1
            else:
                break
        return cnt

    # ---------- main API ----------
    def update_from_tick(self, tick: Dict[str, Any]) -> Dict[str, Any]:
        """
        Met à jour les métriques à partir d'un tick de marché
        
        Args:
            tick: Dict avec les données du tick (voir docstring pour format attendu)
            
        Returns:
            Dict avec toutes les métriques calculées
            
        Format tick attendu (toutes les clés sont optionnelles selon la source) :
        {
          'ts': epoch_seconds(float),
          'best_bid': float, 'best_ask': float,
          'open': float, 'high': float, 'low': float, 'close': float,
          'delta': float,        # NBCV delta courant ou delta tick
          'cvd': float,          # NBCV cumulatif (si déjà fourni)
          'trade_price': float, 'trade_size': float,
          'dom_bids': [qty0, qty1, ...], 'dom_asks': [qty0, qty1, ...],
          'dom_bid_prices': [p0, p1, ...], 'dom_ask_prices': [p0, p1, ...],
          'gamma_level': float   # niveau de flip gamma (G10) si dispo
        }
        """
        out = {}
        ts = tick.get('ts', time.time())

        # ===== 1) quotes.speed_up =====
        bb = tick.get('best_bid')
        ba = tick.get('best_ask')
        quotes_speed = None
        if bb is not None and ba is not None:
            if self.last_bbo is None:
                self.last_bbo = (bb, ba, ts)
                quotes_speed = 0.0
            else:
                lbb, lba, lts = self.last_bbo
                changed = (bb != lbb) or (ba != lba)
                if changed:
                    dt = max(ts - lts, 1e-6)
                    inst = 1.0 / dt
                    quotes_speed = self.ewma_quotes.update(inst)
                    self.last_bbo = (bb, ba, ts)
                else:
                    # Pas de changement — garder l'EWMA (ou 0.0 si None)
                    quotes_speed = self.ewma_quotes._y if self.ewma_quotes._y is not None else 0.0
        out['quotes.speed_up'] = quotes_speed

        # ===== 2) last_wick_ticks =====
        o, h, l, c = tick.get('open'), tick.get('high'), tick.get('low'), tick.get('close')
        if all(v is not None for v in (o, h, l, c)):
            upper_wick = max(0.0, h - max(o, c)) / self.tick_size
            lower_wick = max(0.0, min(o, c) - l) / self.tick_size
            out['last_wick_ticks'] = (h - l) / self.tick_size
            out['last_upper_wick_ticks'] = upper_wick
            out['last_lower_wick_ticks'] = lower_wick
            self.last_bar = {'open': o, 'high': h, 'low': l, 'close': c}
        else:
            out['last_wick_ticks'] = None

        # ===== 3) cvd =====
        if 'cvd' in tick and tick['cvd'] is not None:
            self.cvd = tick['cvd']
        else:
            # reconstruit à partir de delta tick si tu ne fournis pas le cumul
            d = tick.get('delta')
            if d is not None:
                self.cvd += d
        out['cvd'] = self.cvd

        # ===== 5 & 6) delta_burst / delta_flip =====
        curr_delta = tick.get('delta', self.prev_delta)
        out['delta_burst'] = abs(curr_delta - self.prev_delta) if (self.prev_delta is not None) else 0.0
        out['delta_flip'] = (_sign(curr_delta) != _sign(self.prev_delta)) if (self.prev_delta is not None) else False
        self.prev_delta = curr_delta

        # ===== 4) stacked_imbalance.rows =====
        rows_ask = rows_bid = None
        dom_asks = tick.get('dom_asks')
        dom_bids = tick.get('dom_bids')
        if isinstance(dom_asks, list) and isinstance(dom_bids, list):
            depth = min(len(dom_asks), len(dom_bids))
            ask_dom = []
            bid_dom = []
            for k in range(depth):
                a = max(float(dom_asks[k]), 0.0)
                b = max(float(dom_bids[k]), 0.0)
                ask_dom.append((a / max(b, 1.0)) >= self.dom_imbalance_thresh)  # ask dominant
                bid_dom.append((b / max(a, 1.0)) >= self.dom_imbalance_thresh)  # bid dominant
            rows_ask = self._consecutive_rows(ask_dom)
            rows_bid = self._consecutive_rows(bid_dom)
        out['stacked_imbalance.rows.ask'] = rows_ask
        out['stacked_imbalance.rows.bid'] = rows_bid

        # ===== 7) absorption =====
        mid = self._mid(bb, ba)
        traded_at_bb = traded_at_ba = 0.0
        # approx : si trade_price <= best_bid => tape bid ; si >= best_ask => tape ask
        tp = tick.get('trade_price')
        tsz = float(tick.get('trade_size', 0.0) or 0.0)
        if tp is not None and bb is not None and ba is not None and tsz > 0:
            if tp <= bb: traded_at_bb = tsz
            elif tp >= ba: traded_at_ba = tsz

        self.absorb_buf.append((ts, bb, ba, mid, traded_at_bb, traded_at_ba))
        # evict
        while self.absorb_buf and (ts - self.absorb_buf[0][0] > self.absorption_window):
            self.absorb_buf.popleft()

        def _absorb(side='bid'):
            if len(self.absorb_buf) < 2: return False
            vols = sum(x[4] for x in self.absorb_buf) if side == 'bid' else sum(x[5] for x in self.absorb_buf)
            mids = [x[3] for x in self.absorb_buf if x[3] is not None]
            if len(mids) < 2: return False
            price_span = (max(mids) - min(mids)) / self.tick_size
            return (vols >= 50) and (price_span <= 1.0)  # seuils à ajuster
        out['absorption.bid'] = _absorb('bid')
        out['absorption.ask'] = _absorb('ask')

        # ===== 8) iceberg =====
        # Mécanique : cumule les trades et compare à la baisse affichée du DOM au même prix niveau0
        if tp is not None and tsz > 0:
            self.rolling_trades.push_trade(ts, tp, tsz)

        iceberg = False
        # Heuristique : regarde au meilleur ask/bid
        for side in ('dom_bid_prices', 'dom_ask_prices'):
            prices = tick.get(side)
            qtys = tick.get('dom_bids' if side == 'dom_bid_prices' else 'dom_asks')
            if isinstance(prices, list) and isinstance(qtys, list) and len(prices) > 0 and len(qtys) > 0:
                p0 = prices[0]
                q0 = float(qtys[0])
                trades_n, trades_sz = self.rolling_trades.stats_for(p0)
                prev_display = self.displayed_qty_history.get(p0, q0)
                displayed_drop = max(prev_display - q0, 0.0)
                self.displayed_qty_history[p0] = q0
                # Si bcp de petits prints mais affichage "tient", suspecte iceberg
                if trades_n >= self.iceberg_min_trades and trades_sz > 0 and displayed_drop < (0.3 * trades_sz):
                    iceberg = True
                    break
        out['iceberg'] = iceberg

        # ===== 9) gamma_flip =====
        price_t = mid if mid is not None else tick.get('close') or tick.get('trade_price')
        gamma_level = tick.get('gamma_level')
        gamma_flip_up = gamma_flip_down = False
        if price_t is not None and gamma_level is not None and self.prev_price is not None:
            gamma_flip_up = (self.prev_price < gamma_level) and (price_t >= gamma_level)
            gamma_flip_down = (self.prev_price > gamma_level) and (price_t <= gamma_level)
        out['gamma_flip_up'] = gamma_flip_up
        out['gamma_flip_down'] = gamma_flip_down
        self.prev_price = price_t
        self.prev_gamma_level = gamma_level

        return out

    def get_metrics_summary(self) -> Dict[str, Any]:
        """Retourne un résumé des métriques actuelles"""
        return {
            "cvd": self.cvd,
            "prev_delta": self.prev_delta,
            "quotes_ewma": self.ewma_quotes._y,
            "last_bar": self.last_bar,
            "absorption_buffer_size": len(self.absorb_buf),
            "iceberg_trades_count": len(self.rolling_trades.q),
            "displayed_qty_history_size": len(self.displayed_qty_history)
        }

    def reset(self):
        """Remet à zéro toutes les métriques (utile pour tests)"""
        self.last_bbo = None
        self.ewma_quotes = EWMA(alpha=self.ewma_quotes.alpha)
        self.prev_delta = 0.0
        self.cvd = 0.0
        self.last_bar = None
        self.absorb_buf.clear()
        self.rolling_trades = RollingCounter(window_sec=self.iceberg_window)
        self.displayed_qty_history.clear()
        self.prev_price = None
        self.prev_gamma_level = None
