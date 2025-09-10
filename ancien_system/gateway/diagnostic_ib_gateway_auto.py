#!/usr/bin/env python3
"""
DIAGNOSTIC AUTOMATIQUE IB GATEWAY
MIA_IA_SYSTEM - Diagnostic complet des problèmes de connexion
"""
import asyncio
import socket
import subprocess
import sys
import time
from pathlib import Path
from datetime import datetime

sys.path.append(str(Path(__file__).parent))

from core.ibkr_connector import IBKRConnector

class IBGatewayDiagnostic:
    def __init__(self):
        self.host = "127.0.0.1"
        self.port = 4002
        self.results = []
        
    def log_result(self, test_name: str, success: bool, message: str):
        """Enregistrer un résultat de test"""
        status = "✅ SUCCÈS" if success else "❌ ÉCHEC"
        self.results.append({
            'test': test_name,
            'success': success,
            'message': message,
            'timestamp': datetime.now()
        })
        print(f"{status} - {test_name}: {message}")
        
    def test_port_connectivity(self) -> bool:
        """Tester la connectivité du port IB Gateway"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex((self.host, self.port))
            sock.close()
            
            if result == 0:
                self.log_result("Connectivité Port", True, f"Port {self.port} accessible")
                return True
            else:
                self.log_result("Connectivité Port", False, f"Port {self.port} non accessible")
                return False
        except Exception as e:
            self.log_result("Connectivité Port", False, f"Erreur: {e}")
            return False
            
    def test_ib_gateway_process(self) -> bool:
        """Vérifier si IB Gateway est en cours d'exécution"""
        try:
            # Vérifier les processus Windows
            result = subprocess.run(
                ['tasklist', '/FI', 'IMAGENAME eq ibgateway.exe'],
                capture_output=True, text=True
            )
            
            if 'ibgateway.exe' in result.stdout:
                self.log_result("Process IB Gateway", True, "IB Gateway en cours d'exécution")
                return True
            else:
                self.log_result("Process IB Gateway", False, "IB Gateway non trouvé")
                return False
        except Exception as e:
            self.log_result("Process IB Gateway", False, f"Erreur: {e}")
            return False
            
    async def test_ibkr_connection(self) -> bool:
        """Tester la connexion IBKR complète"""
        try:
            config = {
                'ibkr_host': self.host,
                'ibkr_port': self.port,
                'ibkr_client_id': 999,
                'connection_timeout': 30,
                'simulation_mode': False,
                'require_real_data': True
            }
            
            connector = IBKRConnector(config)
            success = await connector.connect()
            
            if success:
                # Test données marché
                market_data = await connector.get_market_data("ES")
                await connector.disconnect()
                
                if market_data:
                    self.log_result("Connexion IBKR", True, "Connexion et données marché OK")
                    return True
                else:
                    self.log_result("Connexion IBKR", False, "Connexion OK mais pas de données")
                    return False
            else:
                self.log_result("Connexion IBKR", False, "Échec connexion")
                return False
                
        except Exception as e:
            self.log_result("Connexion IBKR", False, f"Erreur: {e}")
            return False
            
    def analyze_logs(self) -> dict:
        """Analyser les logs récents pour détecter les problèmes"""
        log_analysis = {
            'errors': [],
            'warnings': [],
            'connection_issues': 0,
            'data_issues': 0
        }
        
        try:
            # Analyser le log IBKR le plus récent
            log_files = list(Path('logs').glob('core.ibkr_connector_*.log'))
            if log_files:
                latest_log = max(log_files, key=lambda x: x.stat().st_mtime)
                
                with open(latest_log, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    
                for line in lines[-100:]:  # Dernières 100 lignes
                    if 'ERROR' in line:
                        log_analysis['errors'].append(line.strip())
                        if 'reconnection attempts' in line:
                            log_analysis['connection_issues'] += 1
                    elif 'WARNING' in line:
                        log_analysis['warnings'].append(line.strip())
                        if '2119' in line or 'données de marché' in line:
                            log_analysis['data_issues'] += 1
                            
            if log_analysis['errors']:
                self.log_result("Analyse Logs", False, f"{len(log_analysis['errors'])} erreurs détectées")
            else:
                self.log_result("Analyse Logs", True, "Aucune erreur critique détectée")
                
        except Exception as e:
            self.log_result("Analyse Logs", False, f"Erreur analyse: {e}")
            
        return log_analysis
        
    def generate_recommendations(self) -> list:
        """Générer des recommandations basées sur les résultats"""
        recommendations = []
        
        # Analyser les résultats
        failed_tests = [r for r in self.results if not r['success']]
        
        if any('Port' in r['test'] for r in failed_tests):
            recommendations.append({
                'priority': 'CRITIQUE',
                'action': 'Démarrer IB Gateway',
                'description': 'Le port 4002 n\'est pas accessible. IB Gateway doit être démarré.'
            })
            
        if any('Process' in r['test'] for r in failed_tests):
            recommendations.append({
                'priority': 'CRITIQUE',
                'action': 'Installer/Configurer IB Gateway',
                'description': 'IB Gateway n\'est pas installé ou mal configuré.'
            })
            
        if any('Connexion' in r['test'] for r in failed_tests):
            recommendations.append({
                'priority': 'HAUTE',
                'action': 'Vérifier configuration IB Gateway',
                'description': 'IB Gateway est démarré mais la connexion échoue.'
            })
            
        if any('Logs' in r['test'] for r in failed_tests):
            recommendations.append({
                'priority': 'MOYENNE',
                'action': 'Vérifier abonnement CME',
                'description': 'Erreurs 2119 détectées - problème d\'abonnement données.'
            })
            
        return recommendations
        
    async def run_full_diagnostic(self):
        """Exécuter le diagnostic complet"""
        print("🔧 DIAGNOSTIC IB GATEWAY - MIA_IA_SYSTEM")
        print("=" * 50)
        
        # Tests de base
        self.test_port_connectivity()
        self.test_ib_gateway_process()
        
        # Test connexion IBKR
        await self.test_ibkr_connection()
        
        # Analyse logs
        log_analysis = self.analyze_logs()
        
        # Générer recommandations
        recommendations = self.generate_recommendations()
        
        # Rapport final
        print("\n" + "=" * 50)
        print("📊 RAPPORT DE DIAGNOSTIC")
        print("=" * 50)
        
        success_count = sum(1 for r in self.results if r['success'])
        total_count = len(self.results)
        
        print(f"Tests réussis: {success_count}/{total_count}")
        
        if recommendations:
            print(f"\n🛠️ RECOMMANDATIONS ({len(recommendations)}):")
            for i, rec in enumerate(recommendations, 1):
                print(f"{i}. [{rec['priority']}] {rec['action']}")
                print(f"   {rec['description']}")
        else:
            print("\n✅ Aucun problème détecté - système opérationnel")
            
        return {
            'success_rate': success_count / total_count if total_count > 0 else 0,
            'recommendations': recommendations,
            'log_analysis': log_analysis
        }

async def main():
    """Fonction principale"""
    diagnostic = IBGatewayDiagnostic()
    result = await diagnostic.run_full_diagnostic()
    
    # Sauvegarder le rapport
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = f"diagnostic_ib_gateway_{timestamp}.txt"
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("DIAGNOSTIC IB GATEWAY - MIA_IA_SYSTEM\n")
        f.write("=" * 50 + "\n")
        f.write(f"Date: {datetime.now()}\n\n")
        
        for result_item in diagnostic.results:
            status = "SUCCÈS" if result_item['success'] else "ÉCHEC"
            f.write(f"{status} - {result_item['test']}: {result_item['message']}\n")
            
        if result['recommendations']:
            f.write(f"\nRECOMMANDATIONS:\n")
            for rec in result['recommendations']:
                f.write(f"- [{rec['priority']}] {rec['action']}: {rec['description']}\n")
                
    print(f"\n📄 Rapport sauvegardé: {report_file}")

if __name__ == "__main__":
    asyncio.run(main())
























