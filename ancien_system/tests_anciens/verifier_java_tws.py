#!/usr/bin/env python3
"""
MIA_IA_SYSTEM - Vérification Java TWS
Vérification et installation de Java pour TWS
"""

import os
import sys
import subprocess
import platform
from datetime import datetime

def verifier_java():
    """Vérifier si Java est installé"""
    print("☕ Vérification Java...")
    
    # Test 1: java -version
    print("   📍 Test java -version...")
    try:
        result = subprocess.run(['java', '-version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("      ✅ Java installé")
            print(f"      📝 Version: {result.stderr.strip()}")
            return True
        else:
            print("      ❌ Java non trouvé")
            return False
    except FileNotFoundError:
        print("      ❌ Java non installé")
        return False
    except subprocess.TimeoutExpired:
        print("      ⏰ Timeout Java")
        return False
    except Exception as e:
        print(f"      ❌ Erreur Java: {str(e)}")
        return False

def verifier_javac():
    """Vérifier si javac est installé"""
    print("   📍 Test javac -version...")
    try:
        result = subprocess.run(['javac', '-version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("      ✅ Java Compiler installé")
            print(f"      📝 Version: {result.stdout.strip()}")
            return True
        else:
            print("      ❌ Java Compiler non trouvé")
            return False
    except FileNotFoundError:
        print("      ❌ Java Compiler non installé")
        return False
    except Exception as e:
        print(f"      ❌ Erreur Java Compiler: {str(e)}")
        return False

def verifier_variables_environnement():
    """Vérifier les variables d'environnement Java"""
    print("   📍 Vérification variables d'environnement...")
    
    java_home = os.environ.get('JAVA_HOME')
    java_path = os.environ.get('PATH')
    
    if java_home:
        print(f"      ✅ JAVA_HOME: {java_home}")
    else:
        print("      ❌ JAVA_HOME non défini")
    
    if java_path and 'java' in java_path.lower():
        print("      ✅ Java dans PATH")
    else:
        print("      ❌ Java pas dans PATH")
    
    return java_home is not None

def verifier_tws_java():
    """Vérifier si TWS peut utiliser Java"""
    print("🖥️ Vérification TWS avec Java...")
    
    try:
        # Vérifier si TWS est démarré
        result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq tws.exe'], 
                              capture_output=True, text=True, shell=True)
        
        if 'tws.exe' in result.stdout:
            print("   ✅ TWS en cours d'exécution")
            
            # Vérifier les processus Java liés à TWS
            result_java = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq javaw.exe'], 
                                       capture_output=True, text=True, shell=True)
            
            if 'javaw.exe' in result_java.stdout:
                print("   ✅ Processus Java actif")
                return True
            else:
                print("   ❌ Aucun processus Java trouvé")
                return False
        else:
            print("   ❌ TWS non démarré")
            return False
            
    except Exception as e:
        print(f"   ❌ Erreur vérification TWS: {str(e)}")
        return False

def diagnostic_java():
    """Diagnostic complet Java"""
    
    print("🔄 MIA_IA_SYSTEM - DIAGNOSTIC JAVA TWS")
    print("=" * 60)
    print("🔍 Vérification Java pour TWS")
    print(f"⏰ {datetime.now().strftime('%H:%M:%S')}")
    print("🎯 Installation et configuration Java")
    print("=" * 60)
    
    # Tests Java
    java_ok = verifier_java()
    javac_ok = verifier_javac()
    env_ok = verifier_variables_environnement()
    tws_java_ok = verifier_tws_java()
    
    # Évaluation
    print("\n📊 ÉVALUATION JAVA")
    print("=" * 40)
    
    tests_reussis = sum([java_ok, javac_ok, env_ok, tws_java_ok])
    total_tests = 4
    
    print(f"✅ Tests réussis: {tests_reussis}/{total_tests}")
    print(f"📈 Taux de réussite: {(tests_reussis/total_tests)*100:.1f}%")
    
    if tests_reussis == 4:
        print("\n🟢 EXCELLENT - Java fonctionnel")
        print("   • Java installé et configuré")
        print("   • TWS peut utiliser Java")
        print("   • Aucune action requise")
    elif tests_reussis >= 2:
        print("\n🟡 BON - Java partiellement fonctionnel")
        print("   • Java installé mais configuration incomplète")
        print("   • Actions correctives nécessaires")
    else:
        print("\n🔴 CRITIQUE - Java non fonctionnel")
        print("   • Java non installé ou mal configuré")
        print("   • Installation Java requise")
    
    # RECOMMANDATIONS
    print("\n🚀 RECOMMANDATIONS")
    print("=" * 40)
    
    if not java_ok:
        print("☕ Java non installé:")
        print("   1. Télécharger Java JDK 8 ou 11")
        print("   2. Installer Java")
        print("   3. Redémarrer le PC")
        print("   4. Relancer ce diagnostic")
    
    if not javac_ok:
        print("🔧 Java Compiler manquant:")
        print("   1. Installer Java JDK (pas seulement JRE)")
        print("   2. Vérifier l'installation")
        print("   3. Redémarrer le PC")
    
    if not env_ok:
        print("🌍 Variables d'environnement:")
        print("   1. Définir JAVA_HOME")
        print("   2. Ajouter Java au PATH")
        print("   3. Redémarrer le PC")
    
    if not tws_java_ok:
        print("🖥️ TWS ne peut pas utiliser Java:")
        print("   1. Redémarrer TWS")
        print("   2. Vérifier que Java est installé")
        print("   3. Vérifier les paramètres TWS")
    
    # PLAN D'ACTION
    print("\n📋 PLAN D'ACTION")
    print("=" * 40)
    
    if tests_reussis == 4:
        print("✅ Java OK - Tester TWS")
        print("1. 🔄 Redémarrer TWS")
        print("2. 🔄 Tester connexion API")
        print("3. 🎯 Prêt pour trading")
    elif tests_reussis >= 2:
        print("⏳ Java partiellement OK")
        print("1. 🔧 Corriger configuration Java")
        print("2. 🔄 Redémarrer PC")
        print("3. 🔄 Relancer diagnostic")
    else:
        print("🔄 Installation Java requise")
        print("1. 📥 Télécharger Java JDK")
        print("2. 🔧 Installer Java")
        print("3. 🔄 Redémarrer PC")
        print("4. 🔄 Relancer diagnostic")
    
    # LIENS UTILES
    print("\n🔗 LIENS UTILES")
    print("=" * 40)
    print("📥 Java JDK 8: https://www.oracle.com/java/technologies/javase/javase8-archive-downloads.html")
    print("📥 Java JDK 11: https://www.oracle.com/java/technologies/javase/jdk11-archive-downloads.html")
    print("📥 OpenJDK: https://adoptium.net/")
    print("📖 Guide installation: https://docs.oracle.com/javase/8/docs/technotes/guides/install/")

if __name__ == "__main__":
    diagnostic_java()
