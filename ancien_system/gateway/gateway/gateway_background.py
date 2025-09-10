#!/usr/bin/env python3
"""
Démarrage du Gateway IBKR en arrière-plan
"""

import os
import subprocess
import time
import requests
import threading
from pathlib import Path

# Désactiver les warnings SSL
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class GatewayBackground:
    def __init__(self):
        self.java_home = Path("OpenJDK17U-jdk_x64_windows_hotspot_17.0.16_8/jdk-17.0.16+8")
        self.gateway_path = Path("clientportal.beta.gw")
        self.process = None
        self.is_running = False
        
    def start_gateway(self):
        """Démarrer le gateway en arrière-plan"""
        print("🚀 Démarrage du Gateway IBKR en arrière-plan...")
        
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
            "-classpath", "root;dist/ibgroup.web.core.iblink.router.clientportal.gw.jar;build/lib/runtime/*",
            "ibgroup.web.core.clientportal.gw.GatewayStart"
        ]
        
        try:
            # Démarrer le processus en arrière-plan
            self.process = subprocess.Popen(
                java_args,
                cwd=str(self.gateway_path),
                env=env,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            
            self.is_running = True
            print(f"✅ Gateway démarré (PID: {self.process.pid})")
            print(f"🌐 Accessible sur: https://localhost:5000")
            
            return True
            
        except Exception as e:
            print(f"❌ Erreur lors du démarrage: {e}")
            return False
    
    def check_status(self):
        """Vérifier si le gateway répond"""
        try:
            response = requests.get(
                "https://localhost:5000/v1/api/iserver/auth/status",
                verify=False,
                timeout=5
            )
            return response.status_code == 200
        except:
            return False
    
    def wait_for_ready(self, timeout=60):
        """Attendre que le gateway soit prêt"""
        print(f"⏳ Attente du gateway (timeout: {timeout}s)...")
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            if self.check_status():
                print("✅ Gateway prêt et répondant")
                return True
            time.sleep(2)
        
        print("❌ Timeout - Gateway non prêt")
        return False
    
    def stop_gateway(self):
        """Arrêter le gateway"""
        if self.process and self.is_running:
            print("🛑 Arrêt du Gateway...")
            self.process.terminate()
            
            try:
                self.process.wait(timeout=10)
                print("✅ Gateway arrêté")
            except subprocess.TimeoutExpired:
                print("⚠️ Arrêt forcé du gateway")
                self.process.kill()
            
            self.is_running = False
            self.process = None

def main():
    """Fonction principale"""
    print("========================================")
    print("GATEWAY IBKR - DÉMARRAGE ARRIÈRE-PLAN")
    print("========================================")
    
    gateway = GatewayBackground()
    
    # Démarrer le gateway
    if gateway.start_gateway():
        # Attendre qu'il soit prêt
        if gateway.wait_for_ready():
            print("\n🎉 Gateway IBKR prêt !")
            print("Vous pouvez maintenant:")
            print("1. Ouvrir https://localhost:5000 dans votre navigateur")
            print("2. Utiliser le connecteur IBKR dans votre système MIA_IA")
            print("3. Appuyer sur Ctrl+C pour arrêter")
            
            try:
                # Surveiller le gateway
                while True:
                    time.sleep(10)
                    if not gateway.check_status():
                        print("❌ Gateway ne répond plus")
                        break
            except KeyboardInterrupt:
                print("\n🛑 Arrêt demandé par l'utilisateur")
        else:
            print("❌ Gateway non prêt")
    else:
        print("❌ Échec du démarrage")
    
    # Arrêter le gateway
    gateway.stop_gateway()

if __name__ == "__main__":
    main()













