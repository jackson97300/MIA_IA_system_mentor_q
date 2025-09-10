#!/usr/bin/env python3
"""
MIA_IA_SYSTEM - Test IB Gateway Simple
Test de connexion sans asyncio
"""

import os
import sys
import socket
import time
from datetime import datetime

# Ajouter le répertoire racine au path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.logger import get_logger

logger = get_logger(__name__)

def test_ib_gateway():
    """Test simple IB Gateway"""
    logger.info("🔧 TEST IB GATEWAY SIMPLE")
    logger.info("=" * 40)
    
    # Test 1: Socket
    logger.info("🔍 Test socket port 4001")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex(("127.0.0.1", 4001))
        sock.close()
        
        if result == 0:
            logger.info("✅ Port 4001 accessible")
            socket_ok = True
        else:
            logger.error(f"❌ Port 4001 non accessible (code: {result})")
            socket_ok = False
    except Exception as e:
        logger.error(f"❌ Erreur socket: {e}")
        socket_ok = False
    
    # Test 2: API simple
    logger.info("🔧 Test API simple")
    api_ok = False
    
    if socket_ok:
        try:
            from ib_insync import IB
            
            ib = IB()
            logger.info("🔗 Tentative connexion...")
            
            # Connexion avec timeout court
            ib.connect("127.0.0.1", 4001, clientId=1, timeout=5)
            
            if ib.isConnected():
                logger.info("✅ Connexion IB Gateway réussie")
                api_ok = True
                
                # Déconnexion
                ib.disconnect()
            else:
                logger.error("❌ Connexion échouée")
                
        except Exception as e:
            logger.error(f"❌ Erreur API: {e}")
    
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

if __name__ == "__main__":
    success = test_ib_gateway()
    
    if success:
        logger.info("✅ Prêt pour MIA_IA_SYSTEM")
    else:
        logger.error("❌ Vérifier IB Gateway")
