#!/usr/bin/env python3
"""
MIA_IA_SYSTEM - Diagnostic IBKR Gateway Paper Trading
Vérification complète de la connexion IBKR Gateway en mode paper
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

class IBKRGatewayDiagnostic:
    """Diagnostic complet IBKR Gateway"""
    
    def __init__(self):
        self.paper_port = 7497
        self.live_port = 7496
        self.gateway_paper_port = 4001
        self.gateway_live_port = 4002
        self.host = "127.0.0.1"
        
    def check_port_availability(self, port: int) -> bool:
        """Vérifier si un port est ouvert"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex((self.host, port))
            sock.close()
            return result == 0
        except Exception as e:
            logger.error(f"❌ Erreur vérification port {port}: {e}")
            return False
    
    def check_ibkr_ports(self):
        """Vérifier tous les ports IBKR"""
        logger.info("🔍 Vérification des ports IBKR...")
        
        ports_to_check = {
            "TWS Paper Trading": self.paper_port,
            "TWS Live Trading": self.live_port,
            "Gateway Paper Trading": self.gateway_paper_port,
            "Gateway Live Trading": self.gateway_live_port
        }
        
        results = {}
        for name, port in ports_to_check.items():
            is_open = self.check_port_availability(port)
            results[name] = {"port": port, "open": is_open}
            
            if is_open:
                logger.info(f"✅ {name} (port {port}): OUVERT")
            else:
                logger.warning(f"❌ {name} (port {port}): FERMÉ")
        
        return results
    
    async def test_ib_insync_connection(self, port: int, client_id: int = 999):
        """Tester connexion avec ib_insync"""
        try:
            from ib_insync import IB
            
            logger.info(f"🔌 Test connexion ib_insync (port {port}, client_id {client_id})...")
            
            ib = IB()
            await ib.connectAsync(self.host, port, clientId=client_id, timeout=10)
            
            if ib.isConnected():
                logger.info(f"✅ Connexion ib_insync RÉUSSIE (port {port})")
                
                # Récupérer info compte
                accounts = ib.managedAccounts()
                if accounts:
                    logger.info(f"📊 Comptes disponibles: {accounts}")
                
                await ib.disconnectAsync()
                return True
            else:
                logger.error(f"❌ Connexion ib_insync ÉCHOUÉE (port {port})")
                return False
                
        except ImportError:
            logger.error("❌ ib_insync non installé")
            return False
        except Exception as e:
            logger.error(f"❌ Erreur connexion ib_insync: {e}")
            return False
    
    def check_ibkr_config(self):
        """Vérifier la configuration IBKR du système"""
        logger.info("⚙️ Vérification configuration IBKR...")
        
        try:
            from config.automation_config import IBKRConfig
            
            config = IBKRConfig()
            logger.info(f"📋 Configuration IBKR:")
            logger.info(f"   🏠 Host: {config.host}")
            logger.info(f"   🔌 Port: {config.port}")
            logger.info(f"   🆔 Client ID: {config.client_id}")
            logger.info(f"   ⏱️ Timeout: {config.timeout_seconds}s")
            
            return config
            
        except ImportError as e:
            logger.error(f"❌ Erreur import configuration: {e}")
            return None
        except Exception as e:
            logger.error(f"❌ Erreur configuration: {e}")
            return None
    
    def check_ibkr_connector(self):
        """Vérifier le connecteur IBKR"""
        logger.info("🔧 Vérification connecteur IBKR...")
        
        try:
            from core.ibkr_connector import IBKRConnector
            
            connector = IBKRConnector()
            logger.info(f"✅ Connecteur IBKR chargé:")
            logger.info(f"   🏠 Host: {connector.host}")
            logger.info(f"   🔌 Port: {connector.port}")
            logger.info(f"   🆔 Client ID: {connector.client_id}")
            logger.info(f"   🎮 Simulation: {connector.simulation_mode}")
            
            return connector
            
        except ImportError as e:
            logger.error(f"❌ Erreur import connecteur: {e}")
            return None
        except Exception as e:
            logger.error(f"❌ Erreur connecteur: {e}")
            return None
    
    def check_ibkr_dependencies(self):
        """Vérifier les dépendances IBKR"""
        logger.info("📦 Vérification dépendances IBKR...")
        
        dependencies = {
            "ib_insync": "ib_insync",
            "ibapi": "ibapi"
        }
        
        results = {}
        for name, package in dependencies.items():
            try:
                __import__(package)
                logger.info(f"✅ {name}: Installé")
                results[name] = True
            except ImportError:
                logger.warning(f"❌ {name}: Non installé")
                results[name] = False
        
        return results
    
    def generate_diagnostic_report(self, port_results, config, connector, dependencies):
        """Générer rapport de diagnostic"""
        logger.info("📊 GÉNÉRATION RAPPORT DE DIAGNOSTIC...")
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "diagnostic": {
                "ports": port_results,
                "config_loaded": config is not None,
                "connector_loaded": connector is not None,
                "dependencies": dependencies
            },
            "recommendations": []
        }
        
        # Analyser les résultats
        paper_ports_open = any(
            result["open"] for name, result in port_results.items() 
            if "Paper" in name
        )
        
        if not paper_ports_open:
            report["recommendations"].append(
                "🚨 Aucun port paper trading ouvert - Démarrer IB Gateway"
            )
        
        if not dependencies.get("ib_insync", False):
            report["recommendations"].append(
                "📦 Installer ib_insync: pip install ib_insync"
            )
        
        if not config:
            report["recommendations"].append(
                "⚙️ Vérifier la configuration IBKR dans automation_config.py"
            )
        
        if not connector:
            report["recommendations"].append(
                "🔧 Vérifier le connecteur IBKR dans core/ibkr_connector.py"
            )
        
        # Sauvegarder le rapport
        report_file = Path("data/diagnostic_ibkr_report.json")
        report_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"✅ Rapport sauvegardé: {report_file}")
        return report
    
    async def run_full_diagnostic(self):
        """Exécuter diagnostic complet"""
        logger.info("🚀 DIAGNOSTIC COMPLET IBKR GATEWAY")
        logger.info("=" * 50)
        
        # 1. Vérifier les ports
        port_results = self.check_ibkr_ports()
        
        # 2. Vérifier les dépendances
        dependencies = self.check_ibkr_dependencies()
        
        # 3. Vérifier la configuration
        config = self.check_ibkr_config()
        
        # 4. Vérifier le connecteur
        connector = self.check_ibkr_connector()
        
        # 5. Tester connexion si port ouvert
        paper_ports_open = any(
            result["open"] for name, result in port_results.items() 
            if "Paper" in name
        )
        
        if paper_ports_open and dependencies.get("ib_insync", False):
            logger.info("🔌 Test connexion ib_insync...")
            
            # Tester port TWS Paper
            if port_results["TWS Paper Trading"]["open"]:
                await self.test_ib_insync_connection(self.paper_port)
            
            # Tester port Gateway Paper
            if port_results["Gateway Paper Trading"]["open"]:
                await self.test_ib_insync_connection(self.gateway_paper_port)
        
        # 6. Générer rapport
        report = self.generate_diagnostic_report(port_results, config, connector, dependencies)
        
        # 7. Afficher résumé
        logger.info("=" * 50)
        logger.info("📊 RÉSUMÉ DIAGNOSTIC:")
        
        if paper_ports_open:
            logger.info("✅ Port paper trading ouvert - IBKR Gateway prêt")
        else:
            logger.warning("❌ Aucun port paper trading ouvert")
        
        if dependencies.get("ib_insync", False):
            logger.info("✅ ib_insync installé")
        else:
            logger.warning("❌ ib_insync manquant")
        
        if config:
            logger.info("✅ Configuration IBKR chargée")
        else:
            logger.warning("❌ Configuration IBKR manquante")
        
        if connector:
            logger.info("✅ Connecteur IBKR chargé")
        else:
            logger.warning("❌ Connecteur IBKR manquant")
        
        # Afficher recommandations
        if report["recommendations"]:
            logger.info("💡 RECOMMANDATIONS:")
            for rec in report["recommendations"]:
                logger.info(f"   {rec}")
        
        return report

async def main():
    """Fonction principale"""
    diagnostic = IBKRGatewayDiagnostic()
    report = await diagnostic.run_full_diagnostic()
    
    # Retourner le statut
    paper_ports_open = any(
        result["open"] for name, result in report["diagnostic"]["ports"].items() 
        if "Paper" in name
    )
    
    if paper_ports_open and report["diagnostic"]["dependencies"].get("ib_insync", False):
        logger.info("🎉 DIAGNOSTIC RÉUSSI - IBKR Gateway prêt!")
        return True
    else:
        logger.error("❌ DIAGNOSTIC ÉCHOUÉ - Problèmes détectés")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    
    if not success:
        sys.exit(1)






