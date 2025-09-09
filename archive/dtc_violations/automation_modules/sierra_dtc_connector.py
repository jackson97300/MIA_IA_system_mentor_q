#!/usr/bin/env python3
"""
🚀 SIERRA DTC CONNECTOR - VRAIE CONNEXION
Connexion DTC Protocol réelle vers Sierra Chart
"""

import socket
import struct
import asyncio
import json
from typing import Dict, Any, Optional
from dataclasses import dataclass
from core.logger import get_logger

logger = get_logger(__name__)

@dataclass
class DTCConfig:
    """Configuration DTC Protocol"""
    host: str = "127.0.0.1"
    port: int = 11099  # Port ES par défaut
    username: str = ""
    password: str = ""
    heartbeat_interval: int = 30
    request_id_counter: int = 1

class SierraDTCConnector:
    """Connecteur DTC Protocol réel pour Sierra Chart"""
    
    def __init__(self, config: DTCConfig):
        self.config = config
        self.socket = None
        self.is_connected = False
        self.request_id = 0
        
        # Callbacks pour événements
        self.on_market_data = None
        self.on_order_update = None
        self.on_position_update = None
        
        logger.info("🔌 DTC Connector initialisé")
    
    async def connect(self) -> bool:
        """Connexion DTC réelle"""
        try:
            logger.info(f"🔌 Connexion DTC {self.config.host}:{self.config.port}")
            
            # Créer socket TCP
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(10.0)
            
            # Connexion
            await asyncio.get_event_loop().run_in_executor(
                None, self.socket.connect, (self.config.host, self.config.port)
            )
            
            # Handshake DTC
            if await self._dtc_handshake():
                self.is_connected = True
                logger.info("✅ Connexion DTC établie")
                
                # Démarrer heartbeat
                asyncio.create_task(self._heartbeat_loop())
                
                return True
            else:
                logger.error("❌ Échec handshake DTC")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erreur connexion DTC: {e}")
            return False
    
    async def _dtc_handshake(self) -> bool:
        """Handshake DTC Protocol"""
        try:
            # Message LOGON_REQUEST (Type 1)
            logon_request = {
                "Type": 1,
                "ProtocolVersion": 8,
                "Username": self.config.username,
                "Password": self.config.password,
                "GeneralTextData": "MIA_IA_SYSTEM",
                "ClientName": "MIA_IA_TRADER"
            }
            
            await self._send_dtc_message(logon_request)
            
            # Attendre LOGON_RESPONSE
            response = await self._receive_dtc_message()
            
            if response and response.get("Type") == 2:  # LOGON_RESPONSE
                if response.get("Result") == 1:  # Success
                    logger.info("✅ Handshake DTC réussi")
                    return True
                else:
                    logger.error(f"❌ Handshake échoué: {response.get('ResultText', 'Unknown')}")
                    return False
            else:
                logger.error("❌ Réponse handshake invalide")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erreur handshake: {e}")
            return False
    
    async def _send_dtc_message(self, message: Dict[str, Any]) -> bool:
        """Envoie message DTC format JSON avec terminateur NULL"""
        try:
            # 🔥 SOLUTION DOCUMENTÉE: JSON Compact + terminateur NULL
            # Référence: docs/sierra_chart/CHECKLIST_DTC_JSON_SIERRA_CHART.md
            
            json_data = json.dumps(message, separators=(',', ':')).encode('utf-8')
            
            # ✅ RÈGLE D'OR: Ajouter terminateur NULL \x00
            full_message = json_data + b'\x00'
            
            await asyncio.get_event_loop().run_in_executor(
                None, self.socket.send, full_message
            )
            
            logger.debug(f"📤 DTC JSON envoyé: Type={message.get('Type')}, Size={len(json_data)}")
            logger.debug(f"📤 JSON: {json_data.decode('utf-8')} + \\x00")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur envoi DTC: {e}")
            return False
    
    async def _receive_dtc_message(self) -> Optional[Dict[str, Any]]:
        """Reçoit message DTC avec terminateur NULL"""
        try:
            # 🔥 SOLUTION DOCUMENTÉE: Lire jusqu'au terminateur \x00
            # Référence: docs/sierra_chart/CHECKLIST_DTC_JSON_SIERRA_CHART.md
            
            buffer = b''
            
            # Lire byte par byte jusqu'au terminateur NULL
            while True:
                byte_data = await asyncio.get_event_loop().run_in_executor(
                    None, self.socket.recv, 1
                )
                
                if not byte_data:
                    logger.error("❌ Connexion fermée par Sierra Chart")
                    return None
                
                if byte_data == b'\x00':
                    # Terminateur trouvé, message complet
                    break
                
                buffer += byte_data
                
                # Sécurité: limite taille message
                if len(buffer) > 1048576:  # 1MB max
                    logger.error("❌ Message trop long (>1MB)")
                    return None
            
            if not buffer:
                return None
            
            # Parser JSON
            json_str = buffer.decode('utf-8')
            message = json.loads(json_str)
            
            logger.debug(f"📥 DTC JSON reçu: Type={message.get('Type')}, Size={len(buffer)}")
            logger.debug(f"📥 JSON: {json_str}")
            
            return message
            
        except json.JSONDecodeError as e:
            logger.error(f"❌ Erreur JSON DTC: {e}")
            logger.error(f"📥 Buffer: {buffer.decode('utf-8', errors='ignore')}")
            return None
        except Exception as e:
            logger.error(f"❌ Erreur réception DTC: {e}")
            return None
    
    async def request_market_data(self, symbol: str) -> bool:
        """Demande données marché temps réel"""
        try:
            self.request_id += 1
            
            request = {
                "Type": 101,  # MARKET_DATA_REQUEST
                "RequestID": self.request_id,
                "Symbol": symbol,
                "Exchange": "CME"
            }
            
            return await self._send_dtc_message(request)
            
        except Exception as e:
            logger.error(f"❌ Erreur demande market data: {e}")
            return False
    
    async def place_order_dtc(self, symbol: str, side: str, quantity: int, 
                             order_type: str, price: Optional[float] = None) -> Optional[str]:
        """Place ordre via DTC"""
        try:
            self.request_id += 1
            
            order_request = {
                "Type": 208,  # SUBMIT_NEW_SINGLE_ORDER
                "RequestID": self.request_id,
                "Symbol": symbol,
                "Exchange": "CME",
                "OrderType": order_type,
                "BuySell": side,
                "OrderQuantity": quantity,
                "Price1": price if price else 0.0,
                "TimeInForce": "DAY",
                "ClientOrderID": f"MIA_{self.request_id}"
            }
            
            if await self._send_dtc_message(order_request):
                return f"MIA_{self.request_id}"
            else:
                return None
                
        except Exception as e:
            logger.error(f"❌ Erreur placement ordre DTC: {e}")
            return None
    
    async def _heartbeat_loop(self):
        """Boucle heartbeat DTC"""
        while self.is_connected:
            try:
                # Envoyer HEARTBEAT
                heartbeat = {"Type": 3}
                await self._send_dtc_message(heartbeat)
                
                await asyncio.sleep(self.config.heartbeat_interval)
                
            except Exception as e:
                logger.error(f"❌ Erreur heartbeat: {e}")
                break
    
    async def heartbeat(self) -> bool:
        """Envoie heartbeat DTC"""
        try:
            if not self.is_connected:
                return False
            
            heartbeat_msg = {"Type": 3}
            return await self._send_dtc_message(heartbeat_msg)
            
        except Exception as e:
            logger.error(f"❌ Erreur heartbeat DTC: {e}")
            return False
    
    async def disconnect(self):
        """Déconnexion DTC"""
        try:
            if self.socket:
                # Message LOGOFF
                logoff = {"Type": 5}
                await self._send_dtc_message(logoff)
                
                self.socket.close()
                self.socket = None
            
            self.is_connected = False
            logger.info("🔌 Déconnexion DTC")
            
        except Exception as e:
            logger.error(f"❌ Erreur déconnexion: {e}")
