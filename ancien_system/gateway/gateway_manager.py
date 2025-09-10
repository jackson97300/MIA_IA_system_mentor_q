#!/usr/bin/env python3
"""
Gestionnaire du Gateway IBKR BETA
Gère le démarrage, l'arrêt et la surveillance du gateway
"""

import os
import sys
import time
import subprocess
import threading
import requests
import logging
from pathlib import Path
from typing import Optional, Dict, Any
import json

class IBKRGatewayManager:
    """Gestionnaire du Gateway IBKR BETA"""
    
    def __init__(self, project_root: Optional[str] = None):
        self.project_root = Path(project_root) if project_root else Path(__file__).parent.parent
        self.gateway_path = self.project_root / "clientportal.beta.gw"
        self.java_home = self.project_root / "OpenJDK17U-jdk_x64_windows_hotspot_17.0.16_8" / "jdk-17.0.16+8"
        
        # Configuration
        self.gateway_url = "https://localhost:5000"
        self.api_base = f"{self.gateway_url}/v1/api"
        
        # État
        self.process = None
        self.is_running = False
        self.start_time = None
        
        # Logging
        self.logger = logging.getLogger(__name__)
        
    def check_java(self) -> bool:
        """Vérifier que Java est disponible"""
        try:
            java_bin = self.java_home / "bin" / "java.exe"
            if not java_bin.exists():
                self.logger.error(f"❌ Java non trouvé: {java_bin}")
                return False
                
            # Test de version
            result = subprocess.run(
                [str(java_bin), "-version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                self.logger.info("✅ Java disponible")
                self.logger.debug(f"Version: {result.stderr.strip()}")
                return True
            else:
                self.logger.error(f"❌ Erreur Java: {result.stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Erreur lors de la vérification Java: {e}")
            return False
    
    def check_gateway_files(self) -> bool:
        """Vérifier que les fichiers du gateway sont présents"""
        required_files = [
            "dist/ibgroup.web.core.iblink.router.clientportal.gw.jar",
            "root/conf.yaml",
            "build/lib/runtime"
        ]
        
        for file_path in required_files:
            full_path = self.gateway_path / file_path
            if not full_path.exists():
                self.logger.error(f"❌ Fichier manquant: {full_path}")
                return False
        
        self.logger.info("✅ Fichiers du gateway présents")
        return True
    
    def start_gateway(self) -> bool:
        """Démarrer le gateway IBKR"""
        try:
            if not self.check_java():
                return False
                
            if not self.check_gateway_files():
                return False
            
            # Préparer l'environnement
            env = os.environ.copy()
            env["JAVA_HOME"] = str(self.java_home)
            env["PATH"] = f"{self.java_home}/bin;{env.get('PATH', '')}"
            
            # Arguments Java
            java_args = [
                str(self.java_home / "bin" / "java.exe"),
                "-server",
                "-Dvertx.disableDnsResolver=true",
                "-Djava.net.preferIPv4Stack=true",
                "-Dvertx.logger-delegate-factory-class-name=io.vertx.core.logging.SLF4JLogDelegateFactory",
                "-Dnologback.statusListenerClass=ch.qos.logback.core.status.OnConsoleStatusListener",
                "-Dnolog4j.debug=true",
                "-Dnolog4j2.debug=true",
                "-classpath", f"root;dist/ibgroup.web.core.iblink.router.clientportal.gw.jar;build/lib/runtime/*",
                "ibgroup.web.core.clientportal.gw.GatewayStart"
            ]
            
            self.logger.info("🚀 Démarrage du Gateway IBKR BETA...")
            
            # Démarrer le processus
            self.process = subprocess.Popen(
                java_args,
                cwd=str(self.gateway_path),
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            self.start_time = time.time()
            self.is_running = True
            
            # Attendre un peu pour voir si le démarrage réussit
            time.sleep(5)
            
            if self.process.poll() is None:
                self.logger.info("✅ Gateway démarré avec succès")
                self.logger.info(f"🌐 Accessible sur: {self.gateway_url}")
                return True
            else:
                stdout, stderr = self.process.communicate()
                self.logger.error(f"❌ Échec du démarrage du gateway")
                self.logger.error(f"STDOUT: {stdout}")
                self.logger.error(f"STDERR: {stderr}")
                self.is_running = False
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Erreur lors du démarrage: {e}")
            self.is_running = False
            return False
    
    def stop_gateway(self) -> bool:
        """Arrêter le gateway IBKR"""
        try:
            if self.process and self.is_running:
                self.logger.info("🛑 Arrêt du Gateway IBKR...")
                self.process.terminate()
                
                # Attendre l'arrêt
                try:
                    self.process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    self.logger.warning("⚠️ Arrêt forcé du gateway")
                    self.process.kill()
                
                self.is_running = False
                self.process = None
                self.logger.info("✅ Gateway arrêté")
                return True
            else:
                self.logger.info("ℹ️ Gateway non en cours d'exécution")
                return True
                
        except Exception as e:
            self.logger.error(f"❌ Erreur lors de l'arrêt: {e}")
            return False
    
    def check_gateway_status(self) -> bool:
        """Vérifier si le gateway répond"""
        try:
            response = requests.get(
                f"{self.api_base}/iserver/auth/status",
                verify=False,
                timeout=5
            )
            return response.status_code == 200
        except:
            return False
    
    def wait_for_gateway(self, timeout: int = 60) -> bool:
        """Attendre que le gateway soit prêt"""
        self.logger.info(f"⏳ Attente du gateway (timeout: {timeout}s)...")
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            if self.check_gateway_status():
                self.logger.info("✅ Gateway prêt")
                return True
            time.sleep(2)
        
        self.logger.error("❌ Timeout - Gateway non prêt")
        return False
    
    def get_gateway_info(self) -> Dict[str, Any]:
        """Obtenir les informations du gateway"""
        info = {
            "is_running": self.is_running,
            "gateway_url": self.gateway_url,
            "java_home": str(self.java_home),
            "gateway_path": str(self.gateway_path)
        }
        
        if self.start_time:
            info["uptime"] = time.time() - self.start_time
            
        if self.process:
            info["pid"] = self.process.pid
            
        info["responding"] = self.check_gateway_status()
        
        return info
    
    def __enter__(self):
        if self.start_gateway():
            if self.wait_for_gateway():
                return self
        return None
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop_gateway()

def main():
    """Fonction principale pour tester le gestionnaire"""
    logging.basicConfig(level=logging.INFO)
    
    manager = IBKRGatewayManager()
    
    print("=== Test du Gestionnaire Gateway IBKR ===")
    print(f"Java Home: {manager.java_home}")
    print(f"Gateway Path: {manager.gateway_path}")
    print()
    
    # Test Java
    if manager.check_java():
        print("✅ Java OK")
    else:
        print("❌ Java KO")
        return
    
    # Test fichiers
    if manager.check_gateway_files():
        print("✅ Fichiers Gateway OK")
    else:
        print("❌ Fichiers Gateway KO")
        return
    
    # Démarrer le gateway
    if manager.start_gateway():
        print("✅ Gateway démarré")
        
        # Attendre et vérifier
        if manager.wait_for_gateway():
            print("✅ Gateway prêt")
            
            # Afficher les infos
            info = manager.get_gateway_info()
            print(f"Infos: {json.dumps(info, indent=2)}")
            
            # Garder en vie
            try:
                while True:
                    time.sleep(5)
                    if not manager.check_gateway_status():
                        print("❌ Gateway ne répond plus")
                        break
            except KeyboardInterrupt:
                print("\n🛑 Arrêt demandé par l'utilisateur")
        else:
            print("❌ Gateway non prêt")
    else:
        print("❌ Échec du démarrage")
    
    # Arrêter
    manager.stop_gateway()

if __name__ == "__main__":
    main()













