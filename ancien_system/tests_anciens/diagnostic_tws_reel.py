#!/usr/bin/env python3
"""
🔍 DIAGNOSTIC TWS RÉEL - CONNEXION LIVE
======================================

Diagnostic rapide pour vérifier l'état de TWS en mode réel
"""

import sys
import asyncio
import socket
from pathlib import Path

# Ajouter le chemin du projet
sys.path.append(str(Path(__file__).parent))

from core.logger import get_logger

logger = get_logger(__name__)

def test_port_connectivity(host, port):
    """Test de connectivité du port"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except Exception as e:
        logger.error(f"❌ Erreur test port {port}: {e}")
        return False

async def diagnostic_tws_reel():
    """Diagnostic TWS mode réel"""
    logger.info("🔍 DIAGNOSTIC TWS RÉEL - CONNEXION LIVE")
    logger.info("=" * 50)
    
    # Test des ports TWS
    host = "127.0.0.1"
    ports_to_test = [
        (7495, "TWS RÉEL"),
        (7496, "TWS PAPER"),
        (7497, "Gateway RÉEL"),
        (4001, "Gateway PAPER")
    ]
    
    logger.info("🔌 TEST CONNECTIVITÉ PORTS:")
    for port, description in ports_to_test:
        is_open = test_port_connectivity(host, port)
        status = "✅ OUVERT" if is_open else "❌ FERMÉ"
        logger.info(f"   Port {port} ({description}): {status}")
    
    # Recommandations
    logger.info("\n💡 RECOMMANDATIONS:")
    
    # Vérifier quel port est ouvert
    open_ports = [port for port, desc in ports_to_test if test_port_connectivity(host, port)]
    
    if 7495 in open_ports:
        logger.info("✅ Port 7495 ouvert - TWS RÉEL disponible")
        logger.info("   🎯 Utiliser port 7495 pour mode réel")
    elif 7496 in open_ports:
        logger.info("✅ Port 7496 ouvert - TWS PAPER disponible")
        logger.info("   🎯 Utiliser port 7496 pour mode paper")
    elif 7497 in open_ports:
        logger.info("✅ Port 7497 ouvert - Gateway RÉEL disponible")
        logger.info("   🎯 Utiliser port 7497 pour mode réel")
    else:
        logger.error("❌ Aucun port TWS ouvert")
        logger.info("🔧 VÉRIFICATIONS TWS:")
        logger.info("   1. TWS ouvert et connecté")
        logger.info("   2. API activée dans TWS")
        logger.info("   3. Mode RÉEL sélectionné")
        logger.info("   4. Ports API activés")
    
    # Test rapide connexion
    if open_ports:
        test_port = open_ports[0]
        logger.info(f"\n🚀 TEST RAPIDE CONNEXION (port {test_port}):")
        
        try:
            from core.ibkr_connector import IBKRConnector
            
            ibkr_connector = IBKRConnector(
                host=host,
                port=test_port,
                client_id=1,
                mode="LIVE"
            )
            
            connection_result = await ibkr_connector.connect()
            
            if connection_result:
                logger.info("✅ Connexion réussie!")
                
                # Test données ES
                es_data = await ibkr_connector.get_orderflow_market_data('ES')
                if es_data:
                    logger.info("✅ Données ES récupérées:")
                    logger.info(f"   💱 Prix: {es_data.get('price', 'N/A')}")
                    logger.info(f"   📊 Volume: {es_data.get('volume', 'N/A')}")
                else:
                    logger.warning("⚠️ Aucune donnée ES")
                
                await ibkr_connector.disconnect()
            else:
                logger.error("❌ Échec connexion")
                
        except Exception as e:
            logger.error(f"❌ Erreur test connexion: {e}")

if __name__ == "__main__":
    asyncio.run(diagnostic_tws_reel())

