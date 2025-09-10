#!/usr/bin/env python3
"""
🔧 TEST CONNEXION TWS - VÉRIFICATION PORTS
==========================================

Script pour tester la connexion TWS sur différents ports
et identifier le bon port de connexion.
"""

import sys
import time
from pathlib import Path

# Ajouter le chemin du projet
sys.path.append(str(Path(__file__).parent))

from ib_insync import IB
from core.logger import get_logger

logger = get_logger(__name__)

def test_tws_connection(host="127.0.0.1", port=7496, client_id=1, timeout=10):
    """Teste la connexion TWS sur un port spécifique"""
    try:
        logger.info(f"🔍 Test connexion TWS: {host}:{port} (Client ID: {client_id})")
        
        # Créer connexion IB
        ib = IB()
        
        # Tentative de connexion
        start_time = time.time()
        connected = ib.connect(host, port, client_id, timeout=timeout)
        
        if connected:
            elapsed = time.time() - start_time
            logger.info(f"✅ Connexion RÉUSSIE en {elapsed:.2f}s")
            
            # Récupérer info TWS
            try:
                tws_time = ib.reqCurrentTime()
                logger.info(f"📅 TWS Time: {tws_time}")
            except:
                logger.warning("⚠️ Impossible de récupérer TWS time")
            
            # Récupérer comptes
            try:
                accounts = ib.managedAccounts()
                logger.info(f"💰 Comptes: {accounts}")
            except:
                logger.warning("⚠️ Impossible de récupérer les comptes")
            
            # Fermer connexion
            ib.disconnect()
            return True
            
        else:
            logger.error(f"❌ Connexion ÉCHOUÉE")
            return False
            
    except Exception as e:
        logger.error(f"❌ Erreur connexion: {e}")
        return False

def main():
    """Teste tous les ports TWS possibles"""
    logger.info("🔧 TEST CONNEXION TWS - VÉRIFICATION PORTS")
    logger.info("=" * 50)
    
    # Ports à tester
    ports_to_test = [
        (7496, "TWS Live Trading"),
        (7497, "TWS Paper Trading"), 
        (4001, "IB Gateway Live"),
        (4002, "IB Gateway Paper")
    ]
    
    results = []
    
    for port, description in ports_to_test:
        logger.info(f"\n🎯 Test {description} (Port {port})")
        logger.info("-" * 30)
        
        success = test_tws_connection(port=port)
        results.append((port, description, success))
        
        # Pause entre tests
        time.sleep(2)
    
    # Résumé
    logger.info("\n📊 RÉSUMÉ DES TESTS")
    logger.info("=" * 30)
    
    working_ports = []
    for port, description, success in results:
        status = "✅ RÉUSSI" if success else "❌ ÉCHOUÉ"
        logger.info(f"Port {port} ({description}): {status}")
        
        if success:
            working_ports.append((port, description))
    
    if working_ports:
        logger.info(f"\n🎉 PORTS FONCTIONNELS TROUVÉS:")
        for port, description in working_ports:
            logger.info(f"  ✅ Port {port}: {description}")
        
        # Recommandation
        best_port = working_ports[0][0]
        logger.info(f"\n💡 RECOMMANDATION: Utiliser le port {best_port}")
        logger.info(f"   Modifier config.ibkr_port = {best_port}")
        
    else:
        logger.error("\n❌ AUCUN PORT FONCTIONNEL")
        logger.error("💡 Vérifiez que TWS/IB Gateway est démarré")
        logger.error("💡 Vérifiez la configuration API dans TWS")

if __name__ == "__main__":
    main()



