#!/usr/bin/env python3
"""
MIA_IA_SYSTEM - Test TWS Paper Trading Port 7497
Test de connexion TWS en mode paper trading
"""

import os
import sys
import asyncio
import socket
import json
from datetime import datetime
from pathlib import Path

# Ajouter le répertoire racine au path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.logger import get_logger

logger = get_logger(__name__)

class TWSPaperTest:
    """Test TWS Paper Trading Port 7497"""
    
    def __init__(self):
        self.host = "127.0.0.1"
        self.port = 7497  # Port TWS Paper Trading
        self.client_id = 1
        self.timeout = 15
        
    def test_socket_connection(self):
        """Test de connexion socket TWS"""
        logger.info("🔍 Test connexion socket TWS Paper Trading")
        
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)
            
            logger.info(f"📡 Tentative connexion {self.host}:{self.port}")
            result = sock.connect_ex((self.host, self.port))
            
            if result == 0:
                logger.info("✅ Port 7497 (TWS Paper) accessible")
                sock.close()
                return True
            else:
                logger.error(f"❌ Port 7497 (TWS Paper) non accessible (code: {result})")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erreur test socket: {e}")
            return False
    
    async def test_api_connection(self):
        """Test API TWS Paper Trading"""
        logger.info("🔧 Test API TWS Paper Trading")
        
        try:
            # Import IB API
            from ibapi.client import EClient
            from ibapi.wrapper import EWrapper
            from ibapi.connection import Connection
            
            class TWSTestWrapper(EWrapper):
                def __init__(self):
                    super().__init__()
                    self.connected = False
                    self.error_received = False
                    self.error_msg = ""
                    self.account_info = ""
                    self.contract_details = []
                
                def connectAck(self):
                    logger.info("✅ Connexion API TWS établie")
                    self.connected = True
                
                def error(self, reqId, errorCode, errorString):
                    logger.error(f"❌ Erreur API: {errorCode} - {errorString}")
                    self.error_received = True
                    self.error_msg = f"{errorCode}: {errorString}"
                
                def nextValidId(self, orderId):
                    logger.info(f"✅ ID valide reçu: {orderId}")
                
                def managedAccounts(self, accountsList):
                    logger.info(f"📊 Comptes disponibles: {accountsList}")
                    self.account_info = accountsList
                
                def contractDetails(self, reqId, contractDetails):
                    logger.info(f"📋 Détails contrat reçus pour reqId: {reqId}")
                    self.contract_details.append(contractDetails)
                
                def contractDetailsEnd(self, reqId):
                    logger.info(f"✅ Fin détails contrats pour reqId: {reqId}")
            
            # Créer client
            wrapper = TWSTestWrapper()
            client = EClient(wrapper)
            
            # Connexion avec Client ID 1
            logger.info(f"🔗 Connexion API TWS avec Client ID {self.client_id}")
            client.connect(self.host, self.port, self.client_id)
            
            # Attendre connexion
            start_time = datetime.now()
            while not wrapper.connected and not wrapper.error_received:
                if (datetime.now() - start_time).seconds > self.timeout:
                    logger.error("⏰ Timeout connexion API TWS")
                    break
                client.run()
                await asyncio.sleep(0.1)
            
            if wrapper.connected:
                logger.info("🎉 Test API TWS réussi")
                
                # Demander les comptes
                logger.info("📊 Demande des comptes...")
                client.reqManagedAccts()
                
                # Attendre réponse
                await asyncio.sleep(2)
                
                # Test ES contract
                logger.info("📋 Test contrat ES...")
                from ibapi.contract import Contract
                
                contract = Contract()
                contract.symbol = "ES"
                contract.secType = "FUT"
                contract.exchange = "CME"
                contract.currency = "USD"
                contract.lastTradingDay = "20241220"  # Décembre 2024
                
                client.reqContractDetails(1, contract)
                
                # Attendre réponse
                await asyncio.sleep(3)
                
                client.disconnect()
                return True
            else:
                logger.error(f"❌ Test API TWS échoué: {wrapper.error_msg}")
                return False
                
        except ImportError:
            logger.error("❌ IB API non installée")
            return False
        except Exception as e:
            logger.error(f"❌ Erreur test API TWS: {e}")
            return False
    
    def test_ib_insync(self):
        """Test avec ib_insync (alternative)"""
        logger.info("🔧 Test avec ib_insync")
        
        try:
            from ib_insync import *
            
            # Créer client
            ib = IB()
            
            # Connexion
            logger.info(f"🔗 Connexion ib_insync {self.host}:{self.port}")
            ib.connect(self.host, self.port, clientId=self.client_id, timeout=self.timeout)
            
            if ib.isConnected():
                logger.info("✅ Connexion ib_insync réussie")
                
                # Informations compte
                accounts = ib.managedAccounts()
                logger.info(f"📊 Comptes: {accounts}")
                
                # Test ES contract
                contract = Future('ES', '20241220', 'CME')
                logger.info(f"📋 Contrat ES: {contract}")
                
                # Déconnexion
                ib.disconnect()
                return True
            else:
                logger.error("❌ Connexion ib_insync échouée")
                return False
                
        except ImportError:
            logger.error("❌ ib_insync non installé")
            return False
        except Exception as e:
            logger.error(f"❌ Erreur ib_insync: {e}")
            return False
    
    async def run_complete_test(self):
        """Test complet TWS Paper Trading"""
        logger.info("🚀 Test complet TWS Paper Trading - Port 7497")
        logger.info("=" * 60)
        
        # Test 1: Socket
        socket_ok = self.test_socket_connection()
        
        # Test 2: API standard
        api_ok = False
        if socket_ok:
            api_ok = await self.test_api_connection()
        
        # Test 3: ib_insync
        insync_ok = False
        if socket_ok:
            insync_ok = self.test_ib_insync()
        
        # Résumé
        logger.info("=" * 60)
        logger.info("📊 RÉSUMÉ DES TESTS TWS PAPER")
        logger.info(f"Socket connexion: {'✅ OK' if socket_ok else '❌ ÉCHEC'}")
        logger.info(f"API standard: {'✅ OK' if api_ok else '❌ ÉCHEC'}")
        logger.info(f"ib_insync: {'✅ OK' if insync_ok else '❌ ÉCHEC'}")
        
        if socket_ok and (api_ok or insync_ok):
            logger.info("🎉 TWS PAPER TRADING FONCTIONNE - Prêt pour MIA_IA_SYSTEM")
            return True
        else:
            logger.error("❌ TESTS ÉCHOUÉS - Vérifier TWS Paper Trading")
            return False

async def main():
    """Fonction principale"""
    logger.info("🔧 DIAGNOSTIC TWS PAPER TRADING - PORT 7497")
    logger.info("Test de connexion pour MIA_IA_SYSTEM")
    
    tester = TWSPaperTest()
    success = await tester.run_complete_test()
    
    if success:
        logger.info("✅ TWS Paper Trading opérationnel - MIA_IA_SYSTEM peut démarrer")
        logger.info("📡 Configuration recommandée:")
        logger.info("   - Host: 127.0.0.1")
        logger.info("   - Port: 7497")
        logger.info("   - Client ID: 1")
        logger.info("   - Mode: Paper Trading")
    else:
        logger.error("❌ Problème de connexion TWS - Vérifier:")
        logger.error("   1. TWS est-il démarré?")
        logger.error("   2. Mode Paper Trading activé?")
        logger.error("   3. Port 7497 ouvert?")
        logger.error("   4. API activée dans TWS?")

if __name__ == "__main__":
    asyncio.run(main())

