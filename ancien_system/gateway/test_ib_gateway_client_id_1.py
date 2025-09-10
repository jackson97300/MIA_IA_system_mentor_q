#!/usr/bin/env python3
"""
MIA_IA_SYSTEM - Test IB Gateway Client ID 1
Test de connexion simple et rapide
"""

import os
import sys
import asyncio
import socket
from datetime import datetime

# Ajouter le répertoire racine au path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.logger import get_logger

logger = get_logger(__name__)

class IBGatewayTest:
    """Test IB Gateway Client ID 1"""
    
    def __init__(self):
        self.host = "127.0.0.1"
        self.port = 4001  # Port IB Gateway Live
        self.client_id = 1
        self.timeout = 5
        
    def test_socket_connection(self):
        """Test connexion socket simple"""
        logger.info("🔍 Test connexion socket IB Gateway")
        
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)
            
            logger.info(f"📡 Connexion {self.host}:{self.port}")
            result = sock.connect_ex((self.host, self.port))
            sock.close()
            
            if result == 0:
                logger.info("✅ Port 4001 accessible")
                return True
            else:
                logger.error(f"❌ Port 4001 non accessible (code: {result})")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erreur socket: {e}")
            return False
    
    async def test_quick_api(self):
        """Test API rapide"""
        logger.info("🔧 Test API IB Gateway rapide")
        
        try:
            from ib_insync import IB
            
            # Créer connexion
            ib = IB()
            ib.connect(self.host, self.port, clientId=self.client_id, timeout=self.timeout)
            
            if ib.isConnected():
                logger.info("✅ Connexion IB Gateway réussie")
                
                # Test simple
                try:
                    account = ib.accountSummary()
                    logger.info(f"📊 Compte connecté: {len(account)} infos")
                except:
                    logger.info("📊 Compte connecté (pas d'infos détaillées)")
                
                ib.disconnect()
                return True
            else:
                logger.error("❌ Connexion échouée")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erreur API: {e}")
            return False
    
    async def run_test(self):
        """Test complet rapide"""
        logger.info("🚀 Test IB Gateway Client ID 1 - RAPIDE")
        logger.info("=" * 40)
        
        # Test socket
        socket_ok = self.test_socket_connection()
        
        # Test API si socket OK
        api_ok = False
        if socket_ok:
            api_ok = await self.test_quick_api()
        
        # Résumé
        logger.info("=" * 40)
        logger.info("📊 RÉSUMÉ")
        logger.info(f"Socket: {'✅ OK' if socket_ok else '❌ ÉCHEC'}")
        logger.info(f"API: {'✅ OK' if api_ok else '❌ ÉCHEC'}")
        
        if socket_ok and api_ok:
            logger.info("🎉 IB Gateway fonctionne")
            return True
        else:
            logger.error("❌ Problème IB Gateway")
            return False

async def main():
    """Fonction principale"""
    logger.info("🔧 TEST IB GATEWAY CLIENT ID 1")
    
    tester = IBGatewayTest()
    success = await tester.run_test()
    
    if success:
        logger.info("✅ Prêt pour MIA_IA_SYSTEM")
    else:
        logger.error("❌ Vérifier IB Gateway")

if __name__ == "__main__":
    asyncio.run(main())
