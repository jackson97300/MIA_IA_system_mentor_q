#!/usr/bin/env python3
"""
🔍 TEST CONNEXION SIMPLE - DIAGNOSTIC TIMEOUT
============================================

Test de connexion simple pour diagnostiquer le problème de timeout
"""

import sys
import asyncio
import socket
from pathlib import Path

# Ajouter le chemin du projet
sys.path.append(str(Path(__file__).parent))

from core.logger import get_logger

logger = get_logger(__name__)

def test_socket_connection():
    """Test de connexion socket simple"""
    logger.info("🔍 TEST CONNEXION SOCKET SIMPLE")
    logger.info("=" * 40)
    
    host = "127.0.0.1"
    port = 7496
    
    try:
        # Test socket direct
        logger.info(f"🔌 Test connexion {host}:{port}")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        
        logger.info("📡 Tentative connexion...")
        result = sock.connect_ex((host, port))
        
        if result == 0:
            logger.info("✅ Connexion socket réussie!")
            
            # Test envoi données
            try:
                sock.send(b"test")
                logger.info("✅ Envoi données réussi")
            except Exception as e:
                logger.warning(f"⚠️ Erreur envoi: {e}")
            
            sock.close()
            return True
        else:
            logger.error(f"❌ Échec connexion socket: {result}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Erreur socket: {e}")
        return False

async def test_ib_insync_simple():
    """Test ib_insync simple"""
    logger.info("\n🚀 TEST IB_INSYNC SIMPLE")
    logger.info("=" * 40)
    
    try:
        from ib_insync import IB
        
        logger.info("📦 Import ib_insync réussi")
        
        # Créer instance IB
        ib = IB()
        ib.connect('127.0.0.1', 7496, clientId=1, timeout=20)
        
        logger.info("✅ Connexion ib_insync réussie!")
        
        # Test données
        if ib.isConnected():
            logger.info("✅ Statut connecté confirmé")
            
            # Test contrats
            try:
                from ib_insync import Contract
                es_contract = Contract(symbol='ES', secType='FUT', exchange='CME', currency='USD')
                logger.info("✅ Contrat ES créé")
            except Exception as e:
                logger.warning(f"⚠️ Erreur contrat: {e}")
            
        else:
            logger.error("❌ Statut non connecté")
        
        # Déconnexion
        ib.disconnect()
        logger.info("✅ Déconnexion propre")
        
    except Exception as e:
        logger.error(f"❌ Erreur ib_insync: {e}")
        logger.info("🔧 VÉRIFICATIONS TWS:")
        logger.info("   1. TWS ouvert et connecté")
        logger.info("   2. API activée dans TWS")
        logger.info("   3. Mode PAPER sélectionné")
        logger.info("   4. Permissions API accordées")

async def main():
    """Test principal"""
    logger.info("🔍 DIAGNOSTIC CONNEXION TWS")
    logger.info("=" * 50)
    
    # Test socket
    socket_ok = test_socket_connection()
    
    if socket_ok:
        # Test ib_insync
        await test_ib_insync_simple()
    else:
        logger.error("❌ Impossible de continuer - problème socket")

if __name__ == "__main__":
    asyncio.run(main())

