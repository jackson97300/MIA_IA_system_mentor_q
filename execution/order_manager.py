#!/usr/bin/env python3
"""
MIA_IA_SYSTEM - Order Manager
Gestionnaire d'ordres multi-broker avec modes adaptatifs
Version: Production Ready v4.0 - Intégré Sierra Chart + IBKR Config
Location: D:\\MIA_IA_system\\execution\\order_manager.py

RESPONSABILITÉS CRITIQUES :
1. [PLUG] CONNEXION MULTI-BROKER - IBKR primary + Sierra Chart backup
2. [STATS] MODES ADAPTATIFS - Simulation/Paper/Live selon contexte
3. [OK] VALIDATION ORDRES - Prix, taille, limites avant soumission
4. [SYNC] RETRY LOGIC - Reconnexion auto, retry intelligent
5. [UP] MONITORING - Status ordres, fills, rejets temps réel
6. [SHIELD] SÉCURITÉ - Limites position, validation compte
7. [CONFIG] INTÉGRATION - Configuration Sierra Chart + IBKR centralisée

WORKFLOW PRINCIPAL :
SimpleBattleNavaleTrader → OrderManager → IBKR/Sierra → Fills → Position Updates

MODES SUPPORTÉS :
- DATA_COLLECTION : Simulation pour collecte de données
- PAPER : Paper trading avec broker réel mais positions virtuelles
- LIVE : Trading réel avec capital

NOUVEAUTÉS v4.0 :
- Intégration config sierra_config.py
- Synchronisation automatique des connexions
- Diagnostics étendus
- Validation selon mode trading
- Kill switch intégré
"""

import time
import asyncio
from core.logger import get_logger
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import json
import threading
from collections import defaultdict, deque

# Local imports
from core.base_types import ES_TICK_SIZE, ES_TICK_VALUE
# Importer TradingMode depuis simple_trader pour cohérence
from core.trading_types import TradingMode
from config.automation_config import get_automation_config
from config.sierra_config import (
    get_sierra_config,
    SierraIBKRConfig,
    OrderProvider,
    DataFeedMode
)

logger = get_logger(__name__)

# === ENUMS ===

class OrderType(Enum):
    """Types d'ordres supportés"""
    MARKET = "MKT"              # Ordre au marché
    LIMIT = "LMT"               # Ordre à cours limité
    STOP = "STP"                # Stop loss
    STOP_LIMIT = "STP LMT"      # Stop limit
    MARKET_ON_CLOSE = "MOC"     # Marché à la clôture
    BRACKET = "BRACKET"         # Ordre bracket (entry + SL + TP)

class OrderStatus(Enum):
    """Statuts des ordres"""
    PENDING = "pending"         # En attente soumission
    SUBMITTED = "submitted"     # Soumis au broker
    FILLED = "filled"           # Exécuté complètement
    PARTIAL = "partial"         # Exécuté partiellement
    CANCELLED = "cancelled"     # Annulé
    REJECTED = "rejected"       # Rejeté par broker
    ERROR = "error"             # Erreur système

class BrokerType(Enum):
    """Types de brokers supportés"""
    IBKR = "ibkr"              # Interactive Brokers
    SIERRA_CHART = "sierra"     # Sierra Chart
    SIMULATION = "simulation"   # Simulation interne

class ConnectionStatus(Enum):
    """Status de connexion broker"""
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    AUTHENTICATED = "authenticated"
    ERROR = "error"
    RECONNECTING = "reconnecting"

# === DATA STRUCTURES ===

@dataclass
class OrderRequest:
    """Requête d'ordre"""
    symbol: str
    side: str                   # BUY ou SELL
    size: int                   # Nombre de contrats
    order_type: OrderType = OrderType.MARKET
    price: Optional[float] = None
    stop_price: Optional[float] = None
    time_in_force: str = "DAY"
    account: Optional[str] = None

    # Battle Navale specific
    signal_confidence: Optional[float] = None
    trade_id: Optional[str] = None

    # Risk management
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    max_loss_dollars: Optional[float] = None

    # Metadata
    strategy: Optional[str] = None
    notes: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class OrderResult:
    """Résultat d'exécution ordre"""
    order_id: str
    status: OrderStatus
    fill_price: Optional[float] = None
    fill_quantity: int = 0
    remaining_quantity: int = 0
    fill_time: Optional[datetime] = None
    commission: float = 0.0

    # Error information
    error_code: Optional[str] = None
    error_message: Optional[str] = None

    # Broker information
    broker_order_id: Optional[str] = None
    broker: BrokerType = BrokerType.SIMULATION

    # Performance metrics
    submission_time: Optional[datetime] = None
    execution_time_ms: Optional[float] = None
    slippage_ticks: Optional[float] = None

@dataclass
class Position:
    """Position en cours"""
    symbol: str
    side: str
    quantity: int
    avg_price: float
    unrealized_pnl: float = 0.0
    realized_pnl: float = 0.0
    open_time: datetime = field(default_factory=datetime.now)

    # Associated orders
    entry_orders: List[str] = field(default_factory=list)
    exit_orders: List[str] = field(default_factory=list)

@dataclass
class BrokerConnection:
    """État connexion broker"""
    broker_type: BrokerType
    status: ConnectionStatus = ConnectionStatus.DISCONNECTED
    client: Optional[Any] = None
    last_heartbeat: Optional[datetime] = None
    connection_count: int = 0
    error_count: int = 0

    # Configuration (from sierra_config.py)
    host: str = "127.0.0.1"
    port: int = 7497
    client_id: int = 1
    account: Optional[str] = None

    # Additional config
    max_order_size: int = 10
    daily_loss_limit: float = 1000.0
    trading_enabled: bool = True

# === MAIN ORDER MANAGER ===

class OrderManager:
    """
    Gestionnaire d'ordres intelligent avec support multi-broker
    Intégré avec configuration Sierra Chart + IBKR
    """

    def __init__(self, mode: str = "paper", sierra_config: Optional[SierraIBKRConfig] = None):
        """
        Initialize Order Manager

        Args:
            mode: "data_collection", "paper", or "live"
            sierra_config: Configuration Sierra/IBKR (optionnelle)
        """
        # Mappe DATA_COLLECTION à simulation pour cohérence
        mode_mapping = {
            "data_collection": "simulation",
            "paper": "paper",
            "live": "live"
        }
        normalized_mode = mode_mapping.get(mode.lower(), mode.lower())

        try:
            self.mode = TradingMode(normalized_mode)
        except ValueError:
            logger.error(f"Mode invalide: {mode}. Valeurs attendues: {list(mode_mapping.keys())}")
            raise ValueError(f"Mode invalide: {mode}. Utilisez 'data_collection', 'paper' ou 'live'")

        # Configuration Sierra Chart + IBKR
        self.sierra_config = sierra_config or get_sierra_config()
        self.config = get_automation_config()

        # Déterminer providers selon configuration
        if self.sierra_config:
            self.data_provider = self.sierra_config.data_provider
            self.order_provider = self.sierra_config.order_provider
            logger.info(f"Configuration Sierra/IBKR détectée:")
            logger.info(f"  - Data Provider: {self.data_provider.value}")
            logger.info(f"  - Order Provider: {self.order_provider.value}")
            logger.info(f"  - Enabled Symbols: {self.sierra_config.contracts.enabled_symbols}")
            logger.info(f"  - Max Order Size: {self.sierra_config.sierra_chart.max_order_size}")
            logger.info(f"  - Daily Loss Limit: ${self.sierra_config.sierra_chart.daily_loss_limit}")
        else:
            # Fallback configuration
            self.data_provider = DataFeedMode.IBKR_ONLY
            self.order_provider = OrderProvider.SIMULATION
            logger.warning("Configuration Sierra/IBKR non trouvée, utilisation defaults")

        # Broker connections
        self.connections: Dict[BrokerType, BrokerConnection] = {}
        self.primary_broker = BrokerType.IBKR
        self.backup_broker = BrokerType.SIERRA_CHART
        self.current_broker = self.primary_broker

        # Order tracking
        self.orders: Dict[str, OrderRequest] = {}
        self.order_results: Dict[str, OrderResult] = {}
        self.positions: Dict[str, Position] = {}
        self.order_counter = 0

        # Status and control
        self.is_connected_flag = False
        self.is_running = False
        self.last_error = None
        self.kill_switch_triggered = False

        # Performance tracking
        self.execution_stats = {
            'orders_submitted': 0,
            'orders_filled': 0,
            'orders_rejected': 0,
            'avg_execution_time_ms': 0.0,
            'total_slippage_ticks': 0.0,
            'daily_pnl': 0.0,
            'daily_commission': 0.0
        }

        # Simulation data (for non-live modes)
        self.simulation_fills = deque(maxlen=1000)
        self.simulated_account_value = 100000.0

        # Thread safety
        self.lock = threading.RLock()

        logger.info(f"OrderManager initialisé en mode {self.mode.value}")
        logger.info(f"  - Order Provider: {self.order_provider.value}")
        logger.info(f"  - Primary Broker: {self.primary_broker.value}")

        # Auto-connect selon le mode et configuration
        if self.mode == TradingMode.DATA_COLLECTION or self.order_provider == OrderProvider.SIMULATION:
            self._init_simulation_mode()
        else:
            self._init_broker_connections()

    def _init_simulation_mode(self):
        """Initialise mode simulation"""
        self.is_connected_flag = True
        logger.info("[OK] Mode simulation activé")

        # Configuration simulation selon sierra_config
        if self.sierra_config:
            self.simulated_account_value = 100000.0
            logger.info(f"   - Account simulé: ${self.simulated_account_value:,.0f}")

    def _init_broker_connections(self):
        """Initialise connexions broker réelles selon sierra_config"""
        try:
            if not self.sierra_config:
                logger.error("Configuration Sierra/IBKR requise pour mode non-simulation")
                return

            # IBKR connection selon configuration
            if self.data_provider.value == "ibkr_only" or self.order_provider.value == "ibkr":
                ibkr_config = self.sierra_config.ibkr
                self.connections[BrokerType.IBKR] = BrokerConnection(
                    broker_type=BrokerType.IBKR,
                    host=ibkr_config.host,
                    port=ibkr_config.port,
                    client_id=ibkr_config.client_id,
                    trading_enabled=self.order_provider.value == "ibkr"
                )
                logger.info(
                    f"IBKR configuré: {
                        ibkr_config.host}:{
                        ibkr_config.port} (client {
                        ibkr_config.client_id})")

            # Sierra Chart connection selon configuration
            if self.order_provider.value == "sierra_chart":
                sierra_config = self.sierra_config.sierra_chart
                self.connections[BrokerType.SIERRA_CHART] = BrokerConnection(
                    broker_type=BrokerType.SIERRA_CHART,
                    host=sierra_config.server_address,
                    port=sierra_config.server_port,
                    trading_enabled=sierra_config.trading_enabled,
                    max_order_size=sierra_config.max_order_size,
                    daily_loss_limit=sierra_config.daily_loss_limit
                )
                logger.info(
                    f"Sierra Chart configuré: {
                        sierra_config.server_address}:{
                        sierra_config.server_port}")

                # Sierra Chart est primary si configuré pour orders
                self.primary_broker = BrokerType.SIERRA_CHART
                self.current_broker = BrokerType.SIERRA_CHART

            logger.info(f"Connexions broker configurées: {list(self.connections.keys())}")
            logger.info(f"Primary broker: {self.primary_broker.value}")

        except Exception as e:
            logger.error(f"Erreur init broker connections: {e}")

    # === CONNECTION MANAGEMENT ===

    def is_connected(self) -> bool:
        """Vérifie si connecté au broker"""
        with self.lock:
            if self.mode == TradingMode.DATA_COLLECTION or self.order_provider == OrderProvider.SIMULATION:
                return True

            # Vérifier connexion broker actuel
            current_connection = self.connections.get(self.current_broker)
            if current_connection:
                return current_connection.status == ConnectionStatus.AUTHENTICATED

            return False

    async def connect(self) -> bool:
        """Connexion au broker principal ou backup"""
        if self.mode == TradingMode.DATA_COLLECTION or self.order_provider == OrderProvider.SIMULATION:
            return True

        # Vérifier kill switch
        if self.kill_switch_triggered:
            logger.error("[ERROR] Kill switch activé, connexion interdite")
            return False

        # Tenter connexion broker principal
        success = await self._connect_to_broker(self.primary_broker)

        if not success and self.backup_broker in self.connections:
            logger.warning(
                f"Échec {
                    self.primary_broker.value}, tentative {
                    self.backup_broker.value}")
            success = await self._connect_to_broker(self.backup_broker)
            if success:
                self.current_broker = self.backup_broker

        with self.lock:
            self.is_connected_flag = success

        if success:
            logger.info(f"[OK] Connecté au broker {self.current_broker.value}")
        else:
            logger.error(f"[ERROR] Échec connexion tous brokers")

        return success

    async def _connect_to_broker(self, broker_type: BrokerType) -> bool:
        """Connexion à un broker spécifique"""
        try:
            connection = self.connections.get(broker_type)
            if not connection:
                logger.error(f"Connexion {broker_type.value} non configurée")
                return False

            connection.status = ConnectionStatus.CONNECTING
            logger.info(f"Connexion à {broker_type.value} ({connection.host}:{connection.port})...")

            if broker_type == BrokerType.IBKR:
                return await self._connect_ibkr(connection)
            elif broker_type == BrokerType.SIERRA_CHART:
                return await self._connect_sierra(connection)

            return False

        except Exception as e:
            logger.error(f"Erreur connexion {broker_type.value}: {e}")
            if broker_type in self.connections:
                self.connections[broker_type].error_count += 1
            return False

    async def _connect_ibkr(self, connection: BrokerConnection) -> bool:
        """Connexion IBKR spécifique"""
        try:
            # Try importing IBKR client
            try:
                from ib_insync import IB
            except ImportError:
                logger.warning("ib_insync non disponible, mode simulation")
                # Simuler connexion réussie pour paper mode
                if self.mode == TradingMode.PAPER:
                    connection.status = ConnectionStatus.AUTHENTICATED
                    connection.connection_count += 1
                    connection.last_heartbeat = datetime.now()
                    return True
                return False

            # Create and connect client
            client = IB()

            # Timeout plus long pour connexions instables
            timeout = 15 if self.mode == TradingMode.LIVE else 10

            try:
                await asyncio.wait_for(
                    asyncio.get_event_loop().run_in_executor(
                        None,
                        lambda: client.connect(
                            connection.host,
                            connection.port,
                            clientId=connection.client_id,
                            timeout=timeout
                        )
                    ),
                    timeout=timeout + 5
                )
            except asyncio.TimeoutError:
                logger.error(f"Timeout connexion IBKR ({timeout}s)")
                return False

            if client.isConnected():
                connection.client = client
                connection.status = ConnectionStatus.AUTHENTICATED
                connection.connection_count += 1
                connection.last_heartbeat = datetime.now()

                # Vérifier mode paper vs live
                if self.mode == TradingMode.LIVE and connection.port == 7497:
                    logger.warning("[WARN] Mode LIVE mais port paper (7497) détecté")
                elif self.mode == TradingMode.PAPER and connection.port == 7496:
                    logger.warning("[WARN] Mode PAPER mais port live (7496) détecté")

                logger.info(f"[OK] IBKR connecté sur {connection.host}:{connection.port}")
                return True

            return False

        except Exception as e:
            logger.error(f"Erreur connexion IBKR: {e}")
            connection.error_count += 1
            return False

    async def _connect_sierra(self, connection: BrokerConnection) -> bool:
        """Connexion Sierra Chart spécifique"""
        try:
            # Vérifier que trading est activé si requis
            if not connection.trading_enabled and self.mode == TradingMode.LIVE:
                logger.error("Sierra Chart trading désactivé en mode LIVE")
                return False

            # Placeholder for Sierra Chart DTC connection
            # TODO: Implémenter connexion réelle via protocole DTC
            logger.warning("[WARN] Sierra Chart connexion simulée (implémentation réelle en attente)")
            connection.status = ConnectionStatus.AUTHENTICATED
            connection.connection_count += 1
            connection.last_heartbeat = datetime.now()

            logger.info(f"[OK] Sierra Chart connecté (simulé)")
            return True

        except Exception as e:
            logger.error(f"Erreur connexion Sierra: {e}")
            connection.error_count += 1
            return False

    # === ORDER SUBMISSION ===

    async def submit_order(self, order_details: Dict[str, Any]) -> Dict[str, Any]:
        """
        Soumet un ordre au broker

        Args:
            order_details: Détails de l'ordre

        Returns:
            Résultat d'exécution
        """
        start_time = time.perf_counter()

        try:
            # Vérifier kill switch
            if self.kill_switch_triggered:
                return {
                    'status': 'REJECTED',
                    'error_message': 'Kill switch activé - Trading suspendu',
                    'order_id': None
                }

            # Créer requête d'ordre
            order_request = self._create_order_request(order_details)

            # Validation ordre
            validation_result = self._validate_order(order_request)
            if not validation_result['valid']:
                return {
                    'status': 'REJECTED',
                    'error_message': validation_result['error'],
                    'order_id': None
                }

            # Générer ID ordre
            order_id = self._generate_order_id()

            # Sauvegarder ordre
            with self.lock:
                self.orders[order_id] = order_request

            # Exécuter selon le mode et configuration
            if self.mode == TradingMode.DATA_COLLECTION or self.order_provider == OrderProvider.SIMULATION:
                result = await self._execute_simulated_order(order_id, order_request)
            else:
                result = await self._execute_real_order(order_id, order_request)

            # Calculer métriques performance
            execution_time = (time.perf_counter() - start_time) * 1000
            result.execution_time_ms = execution_time

            # Sauvegarder résultat
            with self.lock:
                self.order_results[order_id] = result
                self.execution_stats['orders_submitted'] += 1

                if result.status == OrderStatus.FILLED:
                    self.execution_stats['orders_filled'] += 1
                    # Mettre à jour P&L quotidien
                    if result.fill_price and order_request.symbol:
                        pnl_impact = self._calculate_pnl_impact(order_request, result)
                        self.execution_stats['daily_pnl'] += pnl_impact
                        self.execution_stats['daily_commission'] += result.commission
                elif result.status == OrderStatus.REJECTED:
                    self.execution_stats['orders_rejected'] += 1

            # Mettre à jour positions si rempli
            if result.status == OrderStatus.FILLED:
                self._update_position(order_request, result)

            # Vérifier kill switch après ordre
            await self._check_kill_switch()

            # Log résultat
            logger.info(f"Ordre {order_id}: {result.status.value} - "
                        f"{order_request.side} {order_request.size} {order_request.symbol} "
                        f"@ {result.fill_price or 'N/A'} "
                        f"({execution_time:.1f}ms)")

            return {
                'status': result.status.value.upper(),
                'fill_price': result.fill_price,
                'fill_time': result.fill_time,
                'order_id': order_id,
                'error_message': result.error_message,
                'execution_time_ms': execution_time,
                'broker': result.broker.value,
                'commission': result.commission
            }

        except Exception as e:
            logger.error(f"Erreur soumission ordre: {e}")
            return {
                'status': 'ERROR',
                'error_message': str(e),
                'order_id': None
            }

    def _create_order_request(self, details: Dict[str, Any]) -> OrderRequest:
        """Crée requête d'ordre depuis détails"""
        return OrderRequest(
            symbol=details['symbol'],
            side=details['side'],
            size=details['size'],
            order_type=OrderType(details.get('order_type', 'MKT')),
            price=details.get('price'),
            stop_price=details.get('stop_price'),
            signal_confidence=details.get('signal_confidence'),
            trade_id=details.get('trade_id'),
            stop_loss=details.get('stop_loss'),
            take_profit=details.get('take_profit'),
            max_loss_dollars=details.get('max_loss_dollars'),
            strategy=details.get('strategy'),
            notes=details.get('notes')
        )

    def _validate_order(self, order: OrderRequest) -> Dict[str, Any]:
        """Valide un ordre avant soumission"""
        try:
            # Vérifications de base
            if not order.symbol:
                return {'valid': False, 'error': 'Symbole manquant'}

            if order.side not in ['BUY', 'SELL']:
                return {'valid': False, 'error': f'Side invalide: {order.side}'}

            if order.size <= 0:
                return {'valid': False, 'error': f'Taille invalide: {order.size}'}

            # Vérification prix pour ordres limités
            if order.order_type in [OrderType.LIMIT, OrderType.STOP_LIMIT]:
                if not order.price or order.price <= 0:
                    return {'valid': False, 'error': 'Prix requis pour ordre limite'}

            # Vérification connexion
            if not self.is_connected():
                return {'valid': False, 'error': 'Broker non connecté'}

            # Vérifications selon configuration Sierra/IBKR
            if self.sierra_config:
                # Vérifier taille ordre vs limite configurée
                current_connection = self.connections.get(self.current_broker)
                if current_connection and order.size > current_connection.max_order_size:
                    return {'valid': False,
                            'error': f'Taille ordre > limite ({current_connection.max_order_size})'}

                # Vérifier symbole autorisé
                if order.symbol not in self.sierra_config.contracts.enabled_symbols:
                    return {'valid': False, 'error': f'Symbole {order.symbol} non autorisé'}

                # Vérifier limites sécurité
                security_config = self.sierra_config.security
                if order.size > security_config.max_net_position:
                    return {
                        'valid': False, 'error': f'Position > limite sécurité ({security_config.max_net_position})'}

            # Vérification limites compte (mode live seulement)
            if self.mode == TradingMode.LIVE:
                if not self._check_account_limits(order):
                    return {'valid': False, 'error': 'Limites de compte dépassées'}

            return {'valid': True, 'error': None}

        except Exception as e:
            return {'valid': False, 'error': f'Erreur validation: {e}'}

    def _check_account_limits(self, order: OrderRequest) -> bool:
        """Vérifie limites du compte"""
        try:
            # Vérifier P&L quotidien vs limite
            current_connection = self.connections.get(self.current_broker)
            if current_connection and hasattr(current_connection, 'daily_loss_limit'):
                if self.execution_stats['daily_pnl'] <= -current_connection.daily_loss_limit:
                    logger.warning(
                        f"Daily loss limit atteinte: {
                            self.execution_stats['daily_pnl']}")
                    return False

            # Vérifier positions totales
            total_positions = sum(abs(pos.quantity) for pos in self.positions.values())
            if self.sierra_config and total_positions >= self.sierra_config.security.max_gross_position:
                logger.warning(f"Max gross position atteinte: {total_positions}")
                return False

            # TODO: Implémenter vérifications buying power, margin, etc.
            return True

        except Exception as e:
            logger.error(f"Erreur vérification limites: {e}")
            return False

    async def _execute_simulated_order(self, order_id: str, order: OrderRequest) -> OrderResult:
        """Exécute ordre en mode simulation"""
        try:
            # Vérifier symbole autorisé
            if self.sierra_config and order.symbol not in self.sierra_config.contracts.enabled_symbols:
                return OrderResult(
                    order_id=order_id,
                    status=OrderStatus.REJECTED,
                    error_message=f"Symbole {order.symbol} non autorisé en simulation",
                    broker=BrokerType.SIMULATION,
                    submission_time=datetime.now()
                )

            # Simuler latence selon le broker
            if self.current_broker == BrokerType.SIERRA_CHART:
                await asyncio.sleep(0.005)  # 5ms latence Sierra Chart
            else:
                await asyncio.sleep(0.015)  # 15ms latence IBKR

            # Prix de fill simulé (petit slippage)
            if order.order_type == OrderType.MARKET:
                # Slippage selon taille ordre
                base_slippage = 0.25 if order.size <= 2 else 0.5
                slippage_ticks = base_slippage if order.side == 'BUY' else -base_slippage

                # Prix de base ou prix du marché
                base_price = order.price or 4500.0
                fill_price = base_price + (slippage_ticks * ES_TICK_SIZE)
            else:
                fill_price = order.price or 4500.0
                slippage_ticks = 0.0

            # Commission selon configuration
            if self.sierra_config:
                symbol_spec = self.sierra_config.contracts.get_contract_spec(order.symbol)
                if symbol_spec:
                    # Commission basée sur le contrat
                    if order.symbol == "ES":
                        commission = order.size * 4.5  # $4.50 par contrat ES
                    elif order.symbol == "MES":
                        commission = order.size * 1.25  # $1.25 par contrat MES
                    else:
                        commission = order.size * 3.0  # Default
                else:
                    commission = order.size * 2.5  # Fallback
            else:
                commission = order.size * 2.5  # Default

            # Simuler rejet occasionnel (1% chance)
            import random
            if random.random() < 0.01:  # 1% rejet
                return OrderResult(
                    order_id=order_id,
                    status=OrderStatus.REJECTED,
                    error_message="Simulation: Rejet aléatoire",
                    broker=BrokerType.SIMULATION,
                    submission_time=datetime.now()
                )

            return OrderResult(
                order_id=order_id,
                status=OrderStatus.FILLED,
                fill_price=fill_price,
                fill_quantity=order.size,
                remaining_quantity=0,
                fill_time=datetime.now(),
                commission=commission,
                broker_order_id=f"SIM_{order_id}",
                broker=BrokerType.SIMULATION,
                submission_time=datetime.now(),
                slippage_ticks=slippage_ticks
            )

        except Exception as e:
            return OrderResult(
                order_id=order_id,
                status=OrderStatus.ERROR,
                error_message=str(e),
                broker=BrokerType.SIMULATION
            )

    async def _execute_real_order(self, order_id: str, order: OrderRequest) -> OrderResult:
        """Exécute ordre avec broker réel"""
        try:
            connection = self.connections.get(self.current_broker)
            if not connection or not connection.client:
                return OrderResult(
                    order_id=order_id,
                    status=OrderStatus.ERROR,
                    error_message="Broker non connecté",
                    broker=self.current_broker
                )

            if self.current_broker == BrokerType.IBKR:
                return await self._execute_ibkr_order(order_id, order, connection)
            elif self.current_broker == BrokerType.SIERRA_CHART:
                return await self._execute_sierra_order(order_id, order, connection)

            return OrderResult(
                order_id=order_id,
                status=OrderStatus.ERROR,
                error_message="Broker non supporté",
                broker=self.current_broker
            )

        except Exception as e:
            logger.error(f"Erreur exécution ordre réel: {e}")
            return OrderResult(
                order_id=order_id,
                status=OrderStatus.ERROR,
                error_message=str(e),
                broker=self.current_broker
            )

    async def _execute_ibkr_order(self, order_id: str, order: OrderRequest,
                                  connection: BrokerConnection) -> OrderResult:
        """Exécute ordre IBKR"""
        try:
            # TODO: Implémenter soumission ordre IBKR réelle avec ib_insync
            logger.warning("[WARN] Exécution IBKR simulée (implémentation réelle en attente)")
            result = await self._execute_simulated_order(order_id, order)
            result.broker = BrokerType.IBKR
            result.broker_order_id = f"IBKR_{order_id}"
            return result

        except Exception as e:
            return OrderResult(
                order_id=order_id,
                status=OrderStatus.ERROR,
                error_message=f"Erreur IBKR: {e}",
                broker=BrokerType.IBKR
            )

    async def _execute_sierra_order(self, order_id: str, order: OrderRequest,
                                    connection: BrokerConnection) -> OrderResult:
        """Exécute ordre Sierra Chart"""
        try:
            # TODO: Implémenter soumission ordre Sierra Chart DTC réelle
            logger.warning("[WARN] Exécution Sierra Chart simulée (implémentation réelle en attente)")
            result = await self._execute_simulated_order(order_id, order)
            result.broker = BrokerType.SIERRA_CHART
            result.broker_order_id = f"SC_{order_id}"
            return result

        except Exception as e:
            return OrderResult(
                order_id=order_id,
                status=OrderStatus.ERROR,
                error_message=f"Erreur Sierra: {e}",
                broker=BrokerType.SIERRA_CHART
            )

    def _calculate_pnl_impact(self, order: OrderRequest, result: OrderResult) -> float:
        """Calcule impact P&L d'un ordre"""
        try:
            if not result.fill_price or not order.symbol:
                return 0.0

            # Obtenir specs du contrat
            if self.sierra_config:
                symbol_spec = self.sierra_config.contracts.get_contract_spec(order.symbol)
                if symbol_spec:
                    tick_value = symbol_spec['tick_value']
                else:
                    tick_value = ES_TICK_VALUE  # Default
            else:
                tick_value = ES_TICK_VALUE

            # Position existante
            existing_pos = self.positions.get(order.symbol)
            if not existing_pos:
                return 0.0  # Nouvelle position, pas de P&L réalisé

            # Calculer P&L réalisé si fermeture/réduction
            if existing_pos.side != order.side:
                # Fermeture partielle/totale
                close_quantity = min(existing_pos.quantity, result.fill_quantity)
                price_diff = result.fill_price - existing_pos.avg_price

                if existing_pos.side == 'BUY':
                    pnl_ticks = price_diff / ES_TICK_SIZE
                else:
                    pnl_ticks = -price_diff / ES_TICK_SIZE

                return pnl_ticks * close_quantity * tick_value

            return 0.0  # Augmentation position

        except Exception as e:
            logger.error(f"Erreur calcul P&L impact: {e}")
            return 0.0

    def _update_position(self, order: OrderRequest, result: OrderResult):
        """Met à jour position après fill"""
        try:
            with self.lock:
                symbol = order.symbol

                if symbol not in self.positions:
                    # Nouvelle position
                    self.positions[symbol] = Position(
                        symbol=symbol,
                        side=order.side,
                        quantity=result.fill_quantity,
                        avg_price=result.fill_price,
                        open_time=result.fill_time or datetime.now()
                    )
                    logger.info(
                        f"Nouvelle position: {symbol} {
                            order.side} {
                            result.fill_quantity} @ {
                            result.fill_price}")
                else:
                    # Position existante
                    pos = self.positions[symbol]

                    if pos.side == order.side:
                        # Augmenter position
                        total_quantity = pos.quantity + result.fill_quantity
                        total_value = (pos.quantity * pos.avg_price) + \
                            (result.fill_quantity * result.fill_price)
                        pos.avg_price = total_value / total_quantity
                        pos.quantity = total_quantity
                        logger.info(
                            f"Position augmentée: {symbol} {pos.side} {pos.quantity} @ {pos.avg_price:.2f}")
                    else:
                        # Réduire/fermer position
                        old_quantity = pos.quantity
                        pos.quantity -= result.fill_quantity

                        if pos.quantity <= 0:
                            logger.info(f"Position fermée: {symbol}")
                            del self.positions[symbol]
                        else:
                            logger.info(
                                f"Position réduite: {symbol} {pos.side} {pos.quantity} @ {pos.avg_price:.2f}")

        except Exception as e:
            logger.error(f"Erreur mise à jour position: {e}")

    async def _check_kill_switch(self):
        """Vérifie conditions kill switch"""
        try:
            if not self.sierra_config:
                return

            security_config = self.sierra_config.security
            if not security_config.enable_kill_switch:
                return

            # Vérifier seuil de perte
            daily_pnl = self.execution_stats['daily_pnl']
            if daily_pnl <= -security_config.kill_switch_loss_threshold:
                await self._trigger_kill_switch(f"Daily loss threshold: ${daily_pnl:.2f}")
                return

            # Vérifier position totale
            total_positions = sum(abs(pos.quantity) for pos in self.positions.values())
            if total_positions >= security_config.max_gross_position * 1.5:
                await self._trigger_kill_switch(f"Position threshold: {total_positions} contrats")
                return

        except Exception as e:
            logger.error(f"Erreur vérification kill switch: {e}")

    async def _trigger_kill_switch(self, reason: str):
        """Déclenche kill switch"""
        try:
            self.kill_switch_triggered = True
            logger.error(f"[ALERT] KILL SWITCH DÉCLENCHÉ: {reason}")

            # Fermer toutes les positions
            await self.close_all_positions()

            # Déconnexion
            await self.disconnect()

            logger.error("[STOP] Trading automatiquement suspendu")

        except Exception as e:
            logger.error(f"Erreur kill switch: {e}")

    def _generate_order_id(self) -> str:
        """Génère ID unique pour ordre"""
        with self.lock:
            self.order_counter += 1
            broker_prefix = self.current_broker.value[:3].upper()
            return f"MIA_{broker_prefix}_{self.mode.value}_{self.order_counter:06d}_{int(time.time())}"

    # === UTILITY METHODS ===

    def get_positions(self) -> Dict[str, Position]:
        """Retourne positions actuelles"""
        with self.lock:
            return self.positions.copy()

    def get_order_status(self, order_id: str) -> Optional[OrderResult]:
        """Retourne statut d'un ordre"""
        with self.lock:
            return self.order_results.get(order_id)

    def get_execution_stats(self) -> Dict[str, Any]:
        """Retourne statistiques d'exécution"""
        with self.lock:
            stats = self.execution_stats.copy()

            # Ajouter métriques calculées
            if stats['orders_submitted'] > 0:
                stats['fill_rate'] = stats['orders_filled'] / stats['orders_submitted']
                stats['rejection_rate'] = stats['orders_rejected'] / stats['orders_submitted']
            else:
                stats['fill_rate'] = 0.0
                stats['rejection_rate'] = 0.0

            # Ajouter info broker
            stats['current_broker'] = self.current_broker.value
            stats['is_connected'] = self.is_connected()
            stats['kill_switch_triggered'] = self.kill_switch_triggered

            return stats

    def get_connection_status(self) -> Dict[str, Any]:
        """Retourne statut connexions"""
        status = {}

        with self.lock:
            for broker_type, connection in self.connections.items():
                status[broker_type.value] = {
                    'status': connection.status.value,
                    'host': connection.host,
                    'port': connection.port,
                    'connection_count': connection.connection_count,
                    'error_count': connection.error_count,
                    'last_heartbeat': connection.last_heartbeat.isoformat() if connection.last_heartbeat else None,
                    'trading_enabled': getattr(connection, 'trading_enabled', True)
                }

        status['current_broker'] = self.current_broker.value
        status['primary_broker'] = self.primary_broker.value
        status['is_connected'] = self.is_connected()

        return status

    def cancel_order(self, order_id: str) -> bool:
        """Annule un ordre"""
        try:
            # TODO: Implémenter annulation ordre réelle
            logger.warning("[WARN] Annulation ordre simulée (implémentation réelle en attente)")
            return True

        except Exception as e:
            logger.error(f"Erreur annulation ordre: {e}")
            return False

    async def close_all_positions(self) -> List[str]:
        """Ferme toutes les positions"""
        closed_orders = []

        try:
            with self.lock:
                positions_to_close = list(self.positions.values())

            logger.info(f"Fermeture de {len(positions_to_close)} positions...")

            for position in positions_to_close:
                # Créer ordre de fermeture
                close_side = 'SELL' if position.side == 'BUY' else 'BUY'

                order_details = {
                    'symbol': position.symbol,
                    'side': close_side,
                    'size': position.quantity,
                    'order_type': 'MKT',
                    'notes': 'Close all positions',
                    'strategy': 'CLOSE_ALL'
                }

                result = await self.submit_order(order_details)
                if result.get('status') == 'FILLED':
                    closed_orders.append(result['order_id'])
                    logger.info(f"Position fermée: {position.symbol}")
                else:
                    logger.error(
                        f"Échec fermeture position {
                            position.symbol}: {
                            result.get('error_message')}")

            logger.info(f"[OK] Fermé {len(closed_orders)} positions avec succès")
            return closed_orders

        except Exception as e:
            logger.error(f"Erreur fermeture positions: {e}")
            return closed_orders

    async def disconnect(self):
        """Déconnexion de tous les brokers"""
        try:
            logger.info("Déconnexion des brokers...")

            for broker_type, connection in self.connections.items():
                try:
                    if connection.client and hasattr(connection.client, 'disconnect'):
                        await asyncio.get_event_loop().run_in_executor(
                            None, connection.client.disconnect
                        )
                        logger.info(f"Déconnecté de {broker_type.value}")
                    connection.status = ConnectionStatus.DISCONNECTED
                except Exception as e:
                    logger.error(f"Erreur déconnexion {broker_type.value}: {e}")

            with self.lock:
                self.is_connected_flag = False

            logger.info("[OK] OrderManager déconnecté")

        except Exception as e:
            logger.error(f"Erreur déconnexion: {e}")

    def reset_kill_switch(self):
        """Reset le kill switch (admin seulement)"""
        with self.lock:
            self.kill_switch_triggered = False
            logger.info("Kill switch reset")

    def log_diagnostics(self):
        """Log diagnostics complets"""
        logger.info("=" * 60)
        logger.info("[STATS] DIAGNOSTICS ORDER MANAGER")
        logger.info("=" * 60)

        # Configuration
        logger.info(f"Mode Trading:              {self.mode.value}")
        logger.info(f"Order Provider:            {self.order_provider.value}")
        logger.info(f"Current Broker:            {self.current_broker.value}")
        logger.info(f"Is Connected:              {'[OK]' if self.is_connected() else '[ERROR]'}")
        logger.info(
            f"Kill Switch:               {
                '[ALERT] ACTIVÉ' if self.kill_switch_triggered else '[OK] Normal'}")

        # Configuration Sierra/IBKR
        logger.info(f"\n[CONFIG] SIERRA/IBKR CONFIGURATION:")
        if self.sierra_config:
            logger.info(f"  - Data Provider:         {self.data_provider.value}")
            logger.info(f"  - Order Provider:        {self.order_provider.value}")
            logger.info(f"  - Primary Symbol:        {self.sierra_config.contracts.primary_symbol}")
            logger.info(f"  - Enabled Symbols:       {self.sierra_config.contracts.enabled_symbols}")
            logger.info(f"  - Max Order Size:        {self.sierra_config.sierra_chart.max_order_size}")
            logger.info(f"  - Daily Loss Limit:      ${self.sierra_config.sierra_chart.daily_loss_limit}")
            logger.info(f"  - Kill Switch Threshold: ${self.sierra_config.security.kill_switch_loss_threshold}")
        else:
            logger.warning("  - Aucune configuration Sierra/IBKR disponible")

        # Connexions
        logger.info(f"\n[PLUG] CONNEXIONS:")
        for broker_type, connection in self.connections.items():
            logger.info(
                f"{
                    broker_type.value:15} {
                    connection.status.value:15} {
                    connection.host}:{
                    connection.port}")

        # Positions
        logger.info(f"\n[UP] POSITIONS:")
        if self.positions:
            for symbol, pos in self.positions.items():
                logger.info(f"{symbol:6} {pos.side:4} {pos.quantity:3} @ {pos.avg_price:8.2f}")
        else:
            logger.info("Aucune position ouverte")

        # Statistiques
        stats = self.get_execution_stats()
        logger.info(f"\n[STATS] STATISTIQUES:")
        logger.info(f"Orders Submitted:          {stats['orders_submitted']}")
        logger.info(f"Orders Filled:             {stats['orders_filled']}")
        logger.info(f"Orders Rejected:           {stats['orders_rejected']}")
        logger.info(f"Fill Rate:                 {stats['fill_rate']:.1%}")
        logger.info(f"Daily P&L:                 ${stats['daily_pnl']:.2f}")
        logger.info(f"Daily Commission:          ${stats['daily_commission']:.2f}")

        logger.info("=" * 60)

# === FACTORY FUNCTION ===

def create_order_manager(mode: str = "paper",
                         sierra_config: Optional[SierraIBKRConfig] = None) -> OrderManager:
    """Factory function pour créer OrderManager"""
    return OrderManager(mode, sierra_config)

# === TESTING ===

async def test_order_manager():
    """Test du order manager"""
    logger.info("🧪 Test Order Manager v4.0...")

    # Test avec configuration
    try:
        from config.sierra_config import create_paper_trading_config
        sierra_config = create_paper_trading_config()
    except Exception:
        sierra_config = None

    # Créer instance
    om = create_order_manager("paper", sierra_config)

    # Test diagnostics
    om.log_diagnostics()

    # Test connexion
    connected = await om.connect()
    logger.info(f"Connexion: {connected}")
    logger.info(f"Is connected: {om.is_connected()}")

    # Test ordre simple
    order_details = {
        'symbol': 'ES',
        'side': 'BUY',
        'size': 2,
        'order_type': 'MKT',
        'signal_confidence': 0.85,
        'trade_id': 'TEST_001'
    }

    result = await om.submit_order(order_details)
    logger.info(f"Ordre résultat: {result}")

    # Test positions
    positions = om.get_positions()
    logger.info(f"Positions: {len(positions)}")

    # Test stats
    stats = om.get_execution_stats()
    logger.info(f"Stats: Fill rate {stats['fill_rate']:.1%}")

    # Test connexion status
    conn_status = om.get_connection_status()
    logger.info(f"Connexion status: {conn_status['current_broker']}")

    logger.info("\n[OK] Order Manager v4.0 test completed!")
    return True

if __name__ == "__main__":
    asyncio.run(test_order_manager())