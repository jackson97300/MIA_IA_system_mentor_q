#!/usr/bin/env python3
"""
Diagnostic du Gateway IBKR BETA
Identifie les problèmes de configuration et de démarrage
"""

import os
import sys
import time
import subprocess
import requests
import logging
from pathlib import Path
import json

# Désactiver les warnings SSL pour les tests locaux
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def check_java():
    """Vérifier Java"""
    java_home = Path("OpenJDK17U-jdk_x64_windows_hotspot_17.0.16_8/jdk-17.0.16+8")
    java_bin = java_home / "bin" / "java.exe"
    
    print(f"🔍 Vérification Java...")
    print(f"   Java Home: {java_home}")
    print(f"   Java Bin: {java_bin}")
    
    if not java_bin.exists():
        print("   ❌ Java non trouvé")
        return False
    
    try:
        result = subprocess.run([str(java_bin), "-version"], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("   ✅ Java disponible")
            print(f"   Version: {result.stderr.strip()}")
            return True
        else:
            print(f"   ❌ Erreur Java: {result.stderr}")
            return False
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
        return False

def check_gateway_files():
    """Vérifier les fichiers du gateway"""
    gateway_path = Path("clientportal.beta.gw")
    
    print(f"\n🔍 Vérification fichiers Gateway...")
    print(f"   Gateway Path: {gateway_path}")
    
    required_files = [
        "dist/ibgroup.web.core.iblink.router.clientportal.gw.jar",
        "root/conf.yaml",
        "build/lib/runtime"
    ]
    
    all_ok = True
    for file_path in required_files:
        full_path = gateway_path / file_path
        if full_path.exists():
            print(f"   ✅ {file_path}")
        else:
            print(f"   ❌ {file_path} - MANQUANT")
            all_ok = False
    
    return all_ok

def check_ports():
    """Vérifier les ports utilisés"""
    print(f"\n🔍 Vérification des ports...")
    
    try:
        # Vérifier le port 5000
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('localhost', 5000))
        sock.close()
        
        if result == 0:
            print("   ⚠️ Port 5000 déjà utilisé")
            return False
        else:
            print("   ✅ Port 5000 libre")
            return True
    except Exception as e:
        print(f"   ❌ Erreur vérification port: {e}")
        return False

def start_gateway_with_output():
    """Démarrer le gateway et capturer la sortie"""
    print(f"\n🚀 Démarrage du Gateway avec sortie détaillée...")
    
    java_home = Path("OpenJDK17U-jdk_x64_windows_hotspot_17.0.16_8/jdk-17.0.16+8")
    gateway_path = Path("clientportal.beta.gw")
    
    env = os.environ.copy()
    env["JAVA_HOME"] = str(java_home)
    env["PATH"] = f"{java_home}/bin;{env.get('PATH', '')}"
    
    java_args = [
        str(java_home / "bin" / "java.exe"),
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
    
    try:
        process = subprocess.Popen(
            java_args,
            cwd=str(gateway_path),
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        print(f"   Processus démarré (PID: {process.pid})")
        
        # Attendre et lire la sortie
        time.sleep(10)
        
        if process.poll() is None:
            print("   ✅ Processus en cours d'exécution")
            
            # Lire la sortie disponible
            stdout, stderr = process.communicate(timeout=5)
            if stdout:
                print("   STDOUT:")
                for line in stdout.split('\n'):
                    if line.strip():
                        print(f"     {line}")
            if stderr:
                print("   STDERR:")
                for line in stderr.split('\n'):
                    if line.strip():
                        print(f"     {line}")
            
            # Tester la connexion
            print(f"\n🔍 Test de connexion...")
            try:
                response = requests.get(
                    "https://localhost:5000/v1/api/iserver/auth/status",
                    verify=False,
                    timeout=5
                )
                print(f"   ✅ Réponse HTTP: {response.status_code}")
                print(f"   Contenu: {response.text[:200]}...")
            except Exception as e:
                print(f"   ❌ Erreur connexion: {e}")
            
            # Arrêter le processus
            process.terminate()
            process.wait(timeout=10)
            print("   ✅ Processus arrêté")
            
        else:
            stdout, stderr = process.communicate()
            print("   ❌ Processus arrêté prématurément")
            if stdout:
                print("   STDOUT:")
                for line in stdout.split('\n'):
                    if line.strip():
                        print(f"     {line}")
            if stderr:
                print("   STDERR:")
                for line in stderr.split('\n'):
                    if line.strip():
                        print(f"     {line}")
                        
    except Exception as e:
        print(f"   ❌ Erreur: {e}")

def check_configuration():
    """Vérifier la configuration du gateway"""
    print(f"\n🔍 Vérification de la configuration...")
    
    config_file = Path("clientportal.beta.gw/root/conf.yaml")
    if config_file.exists():
        print(f"   ✅ Fichier de configuration trouvé: {config_file}")
        try:
            with open(config_file, 'r') as f:
                content = f.read()
                print(f"   Contenu (premières lignes):")
                for i, line in enumerate(content.split('\n')[:10]):
                    if line.strip():
                        print(f"     {i+1}: {line}")
        except Exception as e:
            print(f"   ❌ Erreur lecture config: {e}")
    else:
        print(f"   ❌ Fichier de configuration manquant")

def main():
    """Fonction principale"""
    print("========================================")
    print("DIAGNOSTIC GATEWAY IBKR BETA")
    print("========================================")
    
    # Vérifications préliminaires
    if not check_java():
        print("\n❌ Java non disponible - Arrêt du diagnostic")
        return
    
    if not check_gateway_files():
        print("\n❌ Fichiers gateway manquants - Arrêt du diagnostic")
        return
    
    if not check_ports():
        print("\n⚠️ Port 5000 occupé - Vérifiez les processus en cours")
    
    check_configuration()
    
    # Test de démarrage
    start_gateway_with_output()
    
    print("\n========================================")
    print("DIAGNOSTIC TERMINÉ")
    print("========================================")

if __name__ == "__main__":
    main()













