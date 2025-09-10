#!/usr/bin/env python3
"""
MIA_IA_SYSTEM - Vérifier et Démarrer TWS
Vérifie si TWS est démarré et le démarre si nécessaire
"""

import os
import sys
import subprocess
import time
from datetime import datetime

def verifier_tws():
    """Vérifier si TWS est en cours d'exécution"""
    print("1. VÉRIFICATION TWS")
    print("-" * 30)
    
    try:
        # Vérifier processus TWS
        result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq TWS.exe'], 
                              capture_output=True, text=True, shell=True)
        
        if 'TWS.exe' in result.stdout:
            print("✅ TWS.exe est en cours d'exécution")
            lines = result.stdout.strip().split('\n')
            for line in lines:
                if 'TWS.exe' in line:
                    print(f"   {line.strip()}")
            return True
        else:
            print("❌ TWS.exe n'est PAS en cours d'exécution")
            return False
            
    except Exception as e:
        print(f"❌ Erreur vérification TWS: {e}")
        return False

def trouver_chemin_tws():
    """Trouver le chemin d'installation de TWS"""
    print("\n2. RECHERCHE CHEMIN TWS")
    print("-" * 30)
    
    chemins_possibles = [
        r"C:\Jts\TWS\TWS.exe",
        r"C:\Program Files (x86)\Interactive Brokers\TWS\TWS.exe",
        r"C:\Program Files\Interactive Brokers\TWS\TWS.exe",
        os.path.expanduser(r"~\AppData\Local\Programs\Interactive Brokers\TWS\TWS.exe"),
        os.path.expanduser(r"~\AppData\Roaming\Interactive Brokers\TWS\TWS.exe")
    ]
    
    for chemin in chemins_possibles:
        if os.path.exists(chemin):
            print(f"✅ TWS trouvé: {chemin}")
            return chemin
    
    print("❌ TWS non trouvé dans les chemins standards")
    print("🔧 Vérifications manuelles:")
    print("1. TWS est-il installé?")
    print("2. Chercher TWS.exe manuellement")
    print("3. Réinstaller TWS si nécessaire")
    
    return None

def demarrer_tws(chemin_tws):
    """Démarrer TWS"""
    print(f"\n3. DÉMARRAGE TWS")
    print("-" * 30)
    
    try:
        print(f"Démarrage: {chemin_tws}")
        
        # Démarrer TWS en arrière-plan
        subprocess.Popen([chemin_tws], 
                        cwd=os.path.dirname(chemin_tws),
                        creationflags=subprocess.CREATE_NEW_CONSOLE)
        
        print("✅ Commande de démarrage TWS envoyée")
        print("⏳ Attendre 30-60 secondes que TWS se charge...")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur démarrage TWS: {e}")
        return False

def attendre_tws_demarrage():
    """Attendre que TWS soit complètement démarré"""
    print("\n4. ATTENTE DÉMARRAGE TWS")
    print("-" * 30)
    
    print("⏳ Attente du démarrage complet de TWS...")
    
    for i in range(12):  # 60 secondes max
        time.sleep(5)
        print(f"   Vérification {i+1}/12...")
        
        if verifier_tws():
            print("✅ TWS détecté et démarré!")
            return True
    
    print("❌ TWS non détecté après 60 secondes")
    return False

def verifier_port_apres_demarrage():
    """Vérifier le port 7497 après démarrage"""
    print("\n5. VÉRIFICATION PORT 7497")
    print("-" * 30)
    
    try:
        # Attendre un peu plus
        print("⏳ Attente supplémentaire pour initialisation port...")
        time.sleep(10)
        
        # Vérifier port
        result = subprocess.run(['netstat', '-an'], 
                              capture_output=True, text=True, shell=True)
        
        if '7497' in result.stdout:
            print("✅ Port 7497 détecté!")
            lines = result.stdout.strip().split('\n')
            for line in lines:
                if '7497' in line:
                    print(f"   {line.strip()}")
            return True
        else:
            print("❌ Port 7497 non détecté")
            return False
            
    except Exception as e:
        print(f"❌ Erreur vérification port: {e}")
        return False

def main():
    """Fonction principale"""
    print("MIA_IA_SYSTEM - VÉRIFIER ET DÉMARRER TWS")
    print("=" * 60)
    print(f"Vérification: {datetime.now()}")
    print("=" * 60)
    
    # Vérifier si TWS est déjà démarré
    if verifier_tws():
        print("\n🎉 TWS est déjà démarré!")
        print("✅ Système prêt pour test")
        return True
    
    # TWS n'est pas démarré, le démarrer
    print("\n🔧 TWS n'est pas démarré, tentative de démarrage...")
    
    chemin_tws = trouver_chemin_tws()
    if not chemin_tws:
        print("\n❌ Impossible de trouver TWS")
        print("🔧 Actions requises:")
        print("1. Installer TWS depuis Interactive Brokers")
        print("2. Ou démarrer TWS manuellement")
        return False
    
    # Démarrer TWS
    if not demarrer_tws(chemin_tws):
        print("\n❌ Échec démarrage TWS")
        return False
    
    # Attendre le démarrage
    if not attendre_tws_demarrage():
        print("\n❌ TWS n'a pas démarré correctement")
        print("🔧 Vérifications:")
        print("1. TWS s'est-il ouvert manuellement?")
        print("2. Y a-t-il des erreurs dans TWS?")
        print("3. Redémarrer TWS manuellement")
        return False
    
    # Vérifier le port
    if not verifier_port_apres_demarrage():
        print("\n⚠️ Port 7497 non détecté")
        print("🔧 Vérifications dans TWS:")
        print("1. Configuration > API > Settings")
        print("2. Socket port: 7497")
        print("3. Enable ActiveX and Socket Clients")
    
    print("\n" + "=" * 60)
    print("RÉSULTATS")
    print("=" * 60)
    
    if verifier_tws():
        print("✅ TWS démarré avec succès!")
        print("🚀 Prochaine étape: python test_connexion_ibkr_simple.py")
        return True
    else:
        print("❌ Échec démarrage TWS")
        return False

if __name__ == "__main__":
    main()

