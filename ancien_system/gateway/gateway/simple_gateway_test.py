#!/usr/bin/env python3
"""
Test simple du Gateway IBKR BETA
"""

import os
import subprocess
import time
from pathlib import Path

def test_gateway():
    print("=== TEST SIMPLE GATEWAY IBKR ===")
    
    # Configuration
    java_home = Path("OpenJDK17U-jdk_x64_windows_hotspot_17.0.16_8/jdk-17.0.16+8")
    gateway_path = Path("clientportal.beta.gw")
    
    print(f"Java Home: {java_home}")
    print(f"Gateway Path: {gateway_path}")
    
    # Vérifier Java
    java_bin = java_home / "bin" / "java.exe"
    if not java_bin.exists():
        print("❌ Java non trouvé")
        return
    
    # Préparer l'environnement
    env = os.environ.copy()
    env["JAVA_HOME"] = str(java_home)
    env["PATH"] = f"{java_home}/bin;{env.get('PATH', '')}"
    
    # Arguments Java
    java_args = [
        str(java_bin),
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
    
    print(f"\nDémarrage du gateway...")
    print(f"Commande: {' '.join(java_args)}")
    
    try:
        # Démarrer le processus
        process = subprocess.Popen(
            java_args,
            cwd=str(gateway_path),
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        print(f"Processus démarré (PID: {process.pid})")
        
        # Attendre et lire la sortie
        time.sleep(15)
        
        if process.poll() is None:
            print("✅ Processus en cours d'exécution")
            
            # Lire la sortie
            stdout, stderr = process.communicate(timeout=5)
            
            if stdout:
                print("\nSTDOUT:")
                for line in stdout.split('\n'):
                    if line.strip():
                        print(f"  {line}")
            
            if stderr:
                print("\nSTDERR:")
                for line in stderr.split('\n'):
                    if line.strip():
                        print(f"  {line}")
            
            # Arrêter
            process.terminate()
            process.wait(timeout=10)
            
        else:
            stdout, stderr = process.communicate()
            print("❌ Processus arrêté")
            
            if stdout:
                print("\nSTDOUT:")
                for line in stdout.split('\n'):
                    if line.strip():
                        print(f"  {line}")
            
            if stderr:
                print("\nSTDERR:")
                for line in stderr.split('\n'):
                    if line.strip():
                        print(f"  {line}")
                        
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    test_gateway()













