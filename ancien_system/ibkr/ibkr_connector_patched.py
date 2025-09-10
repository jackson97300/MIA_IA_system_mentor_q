# Import ib_insync avec mode asyncio
try:
    import math
    from datetime import datetime, timedelta
    from ib_insync import IB, Future, Contract, util
    
    util.useAsyncio()  # ✅ ib_insync piloté par asyncio (évite la double loop)
except ImportError:
    pass

# ... existing code ...

class IBKRConnector:
    def __init__(self, host='127.0.0.1', port=7496, client_id=100, mode='LIVE'):
        self.host, self.port, self.client_id, self.mode = host, port, client_id, mode
        self.simulation_mode = mode == 'SIMULATION'
        self.use_ib_insync = True
        self.use_ibapi = False
        self.ib_client = IB()
        self.contract_cache = {}     # {'ES': Contract, 'NQ': Contract}
        self.contract_cached_at = {} # {'ES': datetime, 'NQ': datetime}
        
        # ... existing code ...

    # ---------- Connexion ----------
    async def connect(self) -> bool:
        ok = await self.ib_client.connectAsync(self.host, self.port, clientId=self.client_id)
        if not ok:
            return False
        # 1 = LIVE, 2 = Frozen, 3 = Delayed, 4 = Delayed-Frozen
        self.ib_client.reqMarketDataType(1)
        if hasattr(self, "logger"):
            self.logger.info("📡 MarketDataType forcé sur LIVE (1)")
        return True

    async def disconnect(self):
        if self.ib_client.isConnected():
            await self.ib_client.disconnect()

    async def is_connected(self) -> bool:
        return self.ib_client.isConnected()

    # ---------- Sélection front-month ----------
    async def _fetch_front_month(self, symbol: str) -> Contract | None:
        """
        Choisit la prochaine échéance >= aujourd'hui sur CME (futures standard).
        Évite qualifyContractsAsync (paramètre timeout inexistant) : on passe par ContractDetails.
        """
        cds = await self.ib_client.reqContractDetailsAsync(
            Future(symbol=symbol, exchange='CME', currency='USD')
        )
        if not cds:
            if hasattr(self, "logger"):
                self.logger.error(f"❌ Aucun ContractDetails IB pour {symbol}")
            return None

        today = datetime.utcnow().date()

        def ltd_date(c: Contract):
            s = c.lastTradeDateOrContractMonth or ""
            if len(s) >= 8:
                return datetime(int(s[:4]), int(s[4:6]), int(s[6:8])).date()
            if len(s) == 6:
                return datetime(int(s[:4]), int(s[4:6]), 28).date()  # approx fin de mois
            return datetime(9999, 12, 31).date()

        rows = [cd for cd in cds if cd.contract.exchange == "CME"]
        rows.sort(key=lambda cd: ltd_date(cd.contract))

        candidates = [cd for cd in rows if ltd_date(cd.contract) >= today]
        chosen = (candidates or rows)[0].contract
        if hasattr(self, "logger"):
            self.logger.info(f"✅ Contrat choisi {symbol}: {chosen.localSymbol} ({chosen.lastTradeDateOrContractMonth})")
        return chosen

    def _need_refresh(self, symbol: str, contract: Contract) -> bool:
        """Rafraîchir cache si >10 min ou échéance <3 jours (pré-rollover)."""
        now = datetime.utcnow()
        last = self.contract_cached_at.get(symbol)
        if not last or (now - last).total_seconds() > 600:
            return True
        s = contract.lastTradeDateOrContractMonth or ""
        if len(s) >= 6:
            y, m = int(s[:4]), int(s[4:6])
            d = int(s[6:8]) if len(s) >= 8 else 28
            if datetime(y, m, d).date() - now.date() <= timedelta(days=3):
                return True
        return False

    async def _ensure_contract(self, symbol: str) -> Contract | None:
        c = self.contract_cache.get(symbol)
        if c and not self._need_refresh(symbol, c):
            return c
        chosen = await self._fetch_front_month(symbol)
        if chosen:
            self.contract_cache[symbol] = chosen
            self.contract_cached_at[symbol] = datetime.utcnow()
            return chosen
        return None  # pas de fallback inventé: l'appelant réessaie proprement

    # ---------- Market Data ----------
    @staticmethod
    def _clean(v):
        return None if (v is None or (isinstance(v, float) and math.isnan(v))) else v

    async def get_market_data(self, symbol: str):
        """
        Streaming non bloquant : attend les 1ers ticks via ib.sleep() (une seule event loop).
        """
        contract = await self._ensure_contract(symbol)
        if not contract:
            if hasattr(self, "logger"):
                self.logger.warning(f"❌ Aucun contrat disponible pour {symbol}")
            return {'symbol': symbol, 'mode': 'no_contract', 'last': None, 'bid': None, 'ask': None, 'volume': 0}

        ticker = self.ib_client.reqMktData(contract, '', False, False)

        # Attendre un tick utile (≤ ~6 s) sans bloquer la boucle ib_insync
        for _ in range(60):
            last = self._clean(getattr(ticker, 'last', None)) or self._clean(ticker.marketPrice())
            bid  = self._clean(getattr(ticker, 'bid', None))
            ask  = self._clean(getattr(ticker, 'ask', None))
            vol  = self._clean(getattr(ticker, 'volume', None)) or 0
            if last is not None or (bid is not None and ask is not None):
                mkt_type = getattr(ticker, 'marketDataType', None)
                if mkt_type in (3, 4) and hasattr(self, "logger"):
                    self.logger.warning(f"⚠️ Flux DELAYED pour {symbol} (marketDataType={mkt_type})")
                return {'symbol': symbol, 'mode': 'live', 'last': last, 'bid': bid, 'ask': ask, 'volume': vol}
            await self.ib_client.sleep(0.1)

        return {'symbol': symbol, 'mode': 'timeout', 'last': None, 'bid': None, 'ask': None, 'volume': 0}





