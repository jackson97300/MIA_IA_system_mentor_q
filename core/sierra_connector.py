#!/usr/bin/env python3
"""
🔧 SIERRA CONNECTOR - MIA_IA_SYSTEM
===================================

Point d'entrée Sierra Chart pour MIA :
1. Lecture du fichier unifié JSONL (Charts 3/4/8/10) — pas de DTC pour la donnée
2. Trading via Sierra (DTC uniquement pour l'ordre), conforme à la config (ports ES/NQ)

FONCTIONNALITÉS:
- File tailer robuste avec rotation et backfill
- Interface DTC pour trading ES/NQ avec paper mode
- Intégration market_snapshot.apply_event
- Bus simple pour listeners
- Gestion multi-instance par symbole
"""

import time
import json
import socket
import threading
from pathlib import Path
from typing import Dict, Any, List, Callable, Optional
from dataclasses import dataclass
from core.logger import get_logger
from config.sierra_trading_ports import get_sierra_trading_config
from core.market_snapshot import get_market_snapshot_manager

logger = get_logger(__name__)

# === STRUCTURES DE DONNÉES ===

@dataclass
class DTCConnection:
    """Connexion DTC pour trading"""
    host: str
    port: int
    symbol: str
    socket: Optional[Any] = None  # socket.socket causait problème
    is_connected: bool = False
    paper_mode: bool = False
    last_heartbeat: float = 0.0

@dataclass
class FileTailer:
    """Tailer de fichier JSONL robuste"""
    file_path: Path
    on_event: Callable
    file_handle: Optional[Any] = None
    file_position: int = 0
    buffer: str = ""
    is_running: bool = False
    backfill_mb: int = 20
    thread: Optional[threading.Thread] = None

# === GESTIONNAIRE PRINCIPAL ===

class SierraConnector:
    """Point d'entrée Sierra Chart pour MIA"""
    
    def __init__(self, config=None):
        self.config = config or get_sierra_trading_config()
        self.market_snapshot_manager = get_market_snapshot_manager()
        self.dtc_connections: Dict[str, DTCConnection] = {}
        self.file_tailer: Optional[FileTailer] = None
        self.is_running = False
        self.event_callbacks: List[Callable] = []
        
        # Métriques
        self._last_metrics_time = time.time()
        self._events_count = 0
        
        logger.info("🔧 SierraConnector initialisé")
    
    def start(self) -> None:
        """Lance le tail du fichier unifié + DTC lazy"""
        if self.is_running:
            logger.warning("SierraConnector déjà démarré")
            return
        
        try:
            # 1. Démarrer le file tailer
            self._start_file_tailer()
            
            # 2. Établir connexions DTC (lazy)
            self._initialize_dtc_connections()
            
            self.is_running = True
            logger.info("✅ SierraConnector démarré avec succès")
            
        except Exception as e:
            logger.error(f"Erreur démarrage SierraConnector: {e}")
            raise
    
    def stop(self) -> None:
        """Arrête le connector"""
        if not self.is_running:
            return
        
        try:
            # 1. Arrêter file tailer
            if self.file_tailer:
                self.file_tailer.is_running = False
                if self.file_tailer.thread:
                    self.file_tailer.thread.join(timeout=5)
                if self.file_tailer.file_handle:
                    self.file_tailer.file_handle.close()
            
            # 2. Fermer connexions DTC
            for connection in self.dtc_connections.values():
                if connection.socket:
                    connection.socket.close()
            
            self.is_running = False
            logger.info("🛑 SierraConnector arrêté")
            
        except Exception as e:
            logger.error(f"Erreur arrêt SierraConnector: {e}")
    
    def add_event_callback(self, callback: Callable) -> None:
        """Ajoute un callback pour les événements"""
        self.event_callbacks.append(callback)
        logger.debug(f"Callback ajouté: {callback.__name__}")
    
    def remove_event_callback(self, callback: Callable) -> None:
        """Retire un callback"""
        if callback in self.event_callbacks:
            self.event_callbacks.remove(callback)
            logger.debug(f"Callback retiré: {callback.__name__}")
    
    # === API DE TRADING ===
    
    def place_order(self, symbol: str, side: str, qty: int, order_type: str,
                   limit_price: float = None, stop_price: float = None,
                   time_in_force: str = 'DAY', bracket: Dict = None) -> str:
        """API unifiée pour placer des ordres"""
        
        try:
            # 1. Valider symbol & sizing (via session_manager)
            # TODO: Intégrer avec session_manager pour validation
            
            # 2. Obtenir port DTC approprié
            port = self.config.get_port_by_symbol(symbol)
            
            # 3. Créer connexion si nécessaire
            connection = self._get_or_create_dtc_connection(symbol, port)
            
            # 4. Placer ordre
            order_id = connection.place_order(
                side, qty, order_type, limit_price, stop_price, time_in_force, bracket
            )
            
            return order_id
            
        except Exception as e:
            logger.error(f"Erreur placement ordre {symbol}: {e}")
            raise
    
    def cancel(self, order_id: str) -> bool:
        """Annule un ordre"""
        # TODO: Implémenter annulation DTC
        logger.warning(f"Annulation ordre {order_id} - non implémentée")
        return False
    
    def flatten_all(self, symbol: str) -> int:
        """Ferme toutes les positions d'un symbole"""
        # TODO: Implémenter flatten DTC
        logger.warning(f"Flatten {symbol} - non implémenté")
        return 0
    
    def get_open_orders(self, symbol: str) -> List[Dict]:
        """Retourne les ordres ouverts"""
        # TODO: Implémenter requête ordres DTC
        logger.warning(f"Requête ordres ouverts {symbol} - non implémentée")
        return []
    
    # === MÉTHODES PRIVÉES ===
    
    def _start_file_tailer(self) -> None:
        """Démarre le file tailer"""
        # Trouver le fichier unifié le plus récent
        unified_file = self._find_latest_unified_file()
        if not unified_file:
            raise FileNotFoundError("Aucun fichier mia_unified_*.jsonl trouvé")
        
        logger.info(f"Sierra tailing '{unified_file}' from {self.file_tailer.backfill_mb}MB backfill")
        
        # Créer le tailer
        self.file_tailer = FileTailer(
            file_path=unified_file,
            on_event=self._on_unified_event,
            backfill_mb=20
        )
        
        # Démarrer le thread
        self.file_tailer.thread = threading.Thread(target=self._file_tailer_worker, daemon=True)
        self.file_tailer.thread.start()
    
    def _find_latest_unified_file(self) -> Optional[Path]:
        """Trouve le fichier unifié le plus récent"""
        base_dir = Path("D:/MIA_IA_system")
        pattern = "mia_unified_*.jsonl"
        
        files = list(base_dir.glob(pattern))
        if not files:
            return None
        
        # Trier par date de modification
        latest_file = max(files, key=lambda f: f.stat().st_mtime)
        return latest_file
    
    def _file_tailer_worker(self) -> None:
        """Worker thread pour le file tailer"""
        try:
            self.file_tailer.is_running = True
            
            # Ouvrir fichier et se positionner
            self.file_tailer.file_handle = open(self.file_tailer.file_path, 'r', encoding='utf-8')
            self._seek_last_bytes(self.file_tailer.backfill_mb)
            
            # Boucle de lecture
            while self.file_tailer.is_running:
                try:
                    # Lire chunk de données
                    chunk = self.file_tailer.file_handle.read(8192)
                    if not chunk:
                        time.sleep(0.1)
                        continue
                    
                    # Ajouter au buffer
                    self.file_tailer.buffer += chunk
                    
                    # Traiter lignes complètes
                    while "\n" in self.file_tailer.buffer:
                        line, self.file_tailer.buffer = self.file_tailer.buffer.split("\n", 1)
                        if line.strip():
                            self._process_line(line.strip())
                
                except Exception as e:
                    logger.error(f"Erreur lecture fichier: {e}")
                    self._handle_file_rotate()
                    time.sleep(1)
        
        except Exception as e:
            logger.error(f"Erreur file tailer worker: {e}")
        finally:
            if self.file_tailer.file_handle:
                self.file_tailer.file_handle.close()
    
    def _seek_last_bytes(self, mb: int) -> None:
        """Se positionne à N MB de la fin"""
        file_size = self.file_tailer.file_path.stat().st_size
        target_size = mb * 1024 * 1024
        self.file_tailer.file_position = max(0, file_size - target_size)
        
        self.file_tailer.file_handle.seek(self.file_tailer.file_position)
        logger.info(f"Backfill: {mb}MB depuis la fin (pos: {self.file_tailer.file_position})")
    
    def _process_line(self, line: str) -> None:
        """Traite une ligne JSONL"""
        try:
            event = json.loads(line)
            self.file_tailer.on_event(event)
            self.file_tailer.file_position += len(line) + 1
        except json.JSONDecodeError as e:
            logger.warning(f"JSON mal formé ignoré: {line[:100]}...")
        except Exception as e:
            logger.error(f"Erreur traitement ligne: {e}")
    
    def _handle_file_rotate(self) -> None:
        """Gère la rotation du fichier"""
        logger.warning("Rotation fichier détectée - reprise à 0")
        self.file_tailer.file_position = 0
        self.file_tailer.file_handle.close()
        time.sleep(1)
        self.file_tailer.file_handle = open(self.file_tailer.file_path, 'r', encoding='utf-8')
        self.file_tailer.file_handle.seek(0)
    
    def _on_unified_event(self, event: Dict[str, Any]) -> None:
        """Callback pour événements du fichier unifié"""
        try:
            # 1. Appliquer au market snapshot
            self.market_snapshot_manager.apply_event(event)
            
            # 2. Notifier autres listeners
            for callback in self.event_callbacks:
                try:
                    callback(event)
                except Exception as e:
                    logger.error(f"Erreur callback: {e}")
            
            # 3. Métriques de débit
            self._update_metrics(event)
            
        except Exception as e:
            logger.error(f"Erreur traitement événement: {e}")
    
    def _update_metrics(self, event: Dict[str, Any]) -> None:
        """Met à jour les métriques de débit"""
        now = time.time()
        self._events_count += 1
        
        if now - self._last_metrics_time >= 60:  # Toutes les minutes
            events_per_min = self._events_count / ((now - self._last_metrics_time) / 60)
            logger.debug(f"events={int(events_per_min)}/min | last_line_ts={event.get('ts', 'N/A')}")
            
            self._last_metrics_time = now
            self._events_count = 0
    
    def _initialize_dtc_connections(self) -> None:
        """Initialise les connexions DTC (lazy)"""
        logger.info("DTC trading channel ready (ES@11099, NQ@11100)")
        
        # Les connexions seront créées à la demande
        # via _get_or_create_dtc_connection()
    
    def _get_or_create_dtc_connection(self, symbol: str, port: int) -> DTCConnection:
        """Obtient ou crée une connexion DTC"""
        if symbol not in self.dtc_connections:
            connection = DTCConnection(
                host=self.config.host,
                port=port,
                symbol=symbol
            )
            self.dtc_connections[symbol] = connection
        
        connection = self.dtc_connections[symbol]
        
        # Connecter si pas encore fait
        if not connection.is_connected and not connection.paper_mode:
            connection.connect()
        
        return connection

# === CONNEXION DTC ===

class DTCConnection:
    """Connexion DTC pour trading"""
    
    def __init__(self, host: str, port: int, symbol: str):
        self.host = host
        self.port = port
        self.symbol = symbol
        self.socket = None
        self.is_connected = False
        self.paper_mode = False
        self.last_heartbeat = time.time()
    
    def connect(self) -> bool:
        """Établit la connexion DTC"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(5.0)  # Timeout 5s
            self.socket.connect((self.host, self.port))
            self.is_connected = True
            self.last_heartbeat = time.time()
            logger.info(f"DTC connecté {self.symbol} @ {self.host}:{self.port}")
            return True
        except Exception as e:
            logger.warning(f"DTC non disponible {self.symbol}: {e} → PAPER MODE")
            self.paper_mode = True
            return False
    
    def place_order(self, side: str, qty: int, order_type: str, 
                   limit_price: float = None, stop_price: float = None,
                   time_in_force: str = 'DAY', bracket: Dict = None) -> str:
        """Place un ordre via DTC"""
        
        if self.paper_mode:
            return self._place_paper_order(side, qty, order_type, limit_price, stop_price, time_in_force, bracket)
        
        # Construire message DTC
        order_msg = self._build_dtc_order_message(side, qty, order_type, limit_price, stop_price, time_in_force, bracket)
        
        try:
            # Envoyer via socket
            self.socket.send(order_msg.encode())
            
            # Log clair
            price_str = f"L{limit_price}" if limit_price else f"S{stop_price}" if stop_price else "MKT"
            logger.info(f"ORDER {self.symbol} {side} {qty} @{price_str} tif={time_in_force} via {self.port}")
            
            if bracket:
                logger.info(f"BRACKET: SL={bracket.get('stop_loss')} TP={bracket.get('take_profit')}")
            
            return f"ORD_{int(time.time())}"
            
        except Exception as e:
            logger.error(f"Erreur envoi ordre {self.symbol}: {e}")
            # Passer en paper mode si erreur
            self.paper_mode = True
            return self._place_paper_order(side, qty, order_type, limit_price, stop_price, time_in_force, bracket)
    
    def _place_paper_order(self, side: str, qty: int, order_type: str, 
                          limit_price: float = None, stop_price: float = None,
                          time_in_force: str = 'DAY', bracket: Dict = None) -> str:
        """Simule un ordre en paper mode"""
        order_id = f"PAPER_{int(time.time())}"
        
        # Log identique à la trame réelle
        price_str = f"L{limit_price}" if limit_price else f"S{stop_price}" if stop_price else "MKT"
        logger.info(f"ORDER {self.symbol} {side} {qty} @{price_str} tif={time_in_force} via {self.port} [PAPER]")
        
        if bracket:
            logger.info(f"BRACKET {order_id}: SL={bracket.get('stop_loss')} TP={bracket.get('take_profit')} [PAPER]")
        
        return order_id
    
    def _build_dtc_order_message(self, side: str, qty: int, order_type: str,
                                limit_price: float = None, stop_price: float = None,
                                time_in_force: str = 'DAY', bracket: Dict = None) -> str:
        """Construit le message DTC pour l'ordre"""
        # TODO: Implémenter le format DTC réel
        # Pour l'instant, format simplifié
        msg = {
            "action": "PLACE_ORDER",
            "symbol": self.symbol,
            "side": side,
            "quantity": qty,
            "order_type": order_type,
            "limit_price": limit_price,
            "stop_price": stop_price,
            "time_in_force": time_in_force,
            "bracket": bracket,
            "timestamp": time.time()
        }
        
        return json.dumps(msg) + "\n"
    
    def send_heartbeat(self) -> bool:
        """Envoie un heartbeat pour maintenir la connexion"""
        if not self.is_connected or self.paper_mode:
            return True
        
        try:
            heartbeat_msg = json.dumps({"action": "HEARTBEAT", "timestamp": time.time()}) + "\n"
            self.socket.send(heartbeat_msg.encode())
            self.last_heartbeat = time.time()
            return True
        except Exception as e:
            logger.warning(f"Heartbeat échoué {self.symbol}: {e}")
            self.is_connected = False
            return False

# === INSTANCE GLOBALE ===

# Instance globale du connector
sierra_connector = SierraConnector()

def get_sierra_connector() -> SierraConnector:
    """Retourne l'instance globale du connector"""
    return sierra_connector

# === FONCTIONS UTILITAIRES ===

def start_sierra_connector() -> SierraConnector:
    """Démarre le connector Sierra et retourne l'instance"""
    connector = get_sierra_connector()
    connector.start()
    return connector

def stop_sierra_connector() -> None:
    """Arrête le connector Sierra"""
    connector = get_sierra_connector()
    connector.stop()

# === TESTS ===

if __name__ == "__main__":
    # Test de base
    connector = SierraConnector()
    
    try:
        connector.start()
        time.sleep(10)  # Laisser tourner 10 secondes
    except KeyboardInterrupt:
        pass
    finally:
        connector.stop()
