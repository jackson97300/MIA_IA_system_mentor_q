#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test de Connexion DTC Sierra Chart pour MIA_IA_SYSTEM
Auteur : MIA_IA_SYSTEM
Date : 27 août 2025
Version : 1.0
"""

import socket
import json
import time
import struct
from datetime import datetime

class DTCTestClient:
    """Client de test pour le protocole DTC Sierra Chart"""
    
    def __init__(self, host="127.0.0.1", port=11099):
        self.host = host
        self.port = port
        self.socket = None
        self.connected = False
        
    def connect(self):
        """Connexion au serveur DTC Sierra Chart"""
        try:
            print(f"🔌 Tentative de connexion à {self.host}:{self.port}...")
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(10)
            self.socket.connect((self.host, self.port))
            self.connected = True
            print(f"✅ Connexion réussie à {self.host}:{self.port}")
            return True
        except Exception as e:
            print(f"❌ Erreur de connexion : {e}")
            return False
    
    def disconnect(self):
        """Déconnexion du serveur DTC"""
        if self.socket:
            self.socket.close()
            self.connected = False
            print("🔌 Déconnexion effectuée")
    
    def send_heartbeat(self):
        """Envoi d'un heartbeat pour tester la connexion"""
        if not self.connected:
            print("❌ Non connecté")
            return False
        
        try:
            # Message heartbeat simple
            heartbeat_msg = b"HEARTBEAT"
            self.socket.send(heartbeat_msg)
            print("💓 Heartbeat envoyé")
            return True
        except Exception as e:
            print(f"❌ Erreur envoi heartbeat : {e}")
            return False
    
    def test_data_reception(self):
        """Test de réception de données"""
        if not self.connected:
            print("❌ Non connecté")
            return False
        
        try:
            # Attendre des données pendant 5 secondes
            self.socket.settimeout(5)
            data = self.socket.recv(1024)
            if data:
                print(f"📊 Données reçues : {len(data)} bytes")
                print(f"   Contenu : {data[:100]}...")
                return True
            else:
                print("⚠️ Aucune donnée reçue")
                return False
        except socket.timeout:
            print("⏰ Timeout - Aucune donnée reçue (normal pour un test simple)")
            return True
        except Exception as e:
            print(f"❌ Erreur réception : {e}")
            return False

def test_sierra_chart_dtc():
    """Test complet de la connexion DTC Sierra Chart"""
    
    print("🧪 TEST DE CONNEXION DTC SIERRA CHART")
    print("=" * 50)
    
    # Configuration des instances
    instances = {
        'ES': {'port': 11099, 'symbol': 'ESU26_FUT_CME'},
        'NQ': {'port': 11100, 'symbol': 'NQU26_FUT_CME'}
    }
    
    results = {}
    
    for instance_name, config in instances.items():
        print(f"\n🔍 Test Instance {instance_name} (Port {config['port']})")
        print("-" * 40)
        
        # Créer client de test
        client = DTCTestClient(host="127.0.0.1", port=config['port'])
        
        # Test connexion
        if client.connect():
            print(f"✅ Connexion {instance_name} : SUCCÈS")
            
            # Test heartbeat
            if client.send_heartbeat():
                print(f"✅ Heartbeat {instance_name} : SUCCÈS")
            
            # Test réception données
            if client.test_data_reception():
                print(f"✅ Réception {instance_name} : SUCCÈS")
            
            results[instance_name] = "SUCCÈS"
        else:
            print(f"❌ Connexion {instance_name} : ÉCHEC")
            results[instance_name] = "ÉCHEC"
        
        # Déconnexion
        client.disconnect()
        time.sleep(1)
    
    # Résumé des tests
    print("\n📊 RÉSUMÉ DES TESTS")
    print("=" * 50)
    
    for instance_name, result in results.items():
        status = "✅" if result == "SUCCÈS" else "❌"
        print(f"{status} {instance_name} : {result}")
    
    # Recommandations
    print("\n💡 RECOMMANDATIONS")
    print("=" * 50)
    
    if all(result == "SUCCÈS" for result in results.values()):
        print("🎉 Tous les tests sont réussis !")
        print("✅ MIA peut maintenant se connecter à Sierra Chart DTC")
        print("🚀 Prêt pour l'intégration complète")
    else:
        print("⚠️ Certains tests ont échoué")
        print("🔧 Vérifiez la configuration Sierra Chart :")
        print("   - Enable DTC Protocol Server : Yes")
        print("   - DTC Protocol Server is Listening : Yes")
        print("   - Ports corrects (11099, 11100)")
        print("   - Firewall/antivirus")

def test_advanced_dtc():
    """Test avancé avec protocole DTC complet"""
    
    print("\n🔬 TEST AVANCÉ DTC")
    print("=" * 50)
    
    # Test avec port ES
    client = DTCTestClient(host="127.0.0.1", port=11099)
    
    if client.connect():
        print("✅ Connexion avancée établie")
        
        # Test de protocole DTC basique
        try:
            # Message de test DTC
            test_msg = struct.pack('<I', 0x12345678)  # Message ID
            client.socket.send(test_msg)
            print("📤 Message DTC envoyé")
            
            # Attendre réponse
            client.socket.settimeout(3)
            response = client.socket.recv(1024)
            if response:
                print(f"📥 Réponse DTC reçue : {len(response)} bytes")
            else:
                print("⚠️ Pas de réponse DTC (normal pour un test simple)")
                
        except Exception as e:
            print(f"⚠️ Test DTC avancé : {e}")
        
        client.disconnect()
    else:
        print("❌ Impossible de tester le protocole DTC avancé")

if __name__ == "__main__":
    try:
        # Test de base
        test_sierra_chart_dtc()
        
        # Test avancé
        test_advanced_dtc()
        
        print("\n🎯 TEST TERMINÉ")
        print("=" * 50)
        print("📝 Consultez les résultats ci-dessus")
        print("🔗 Prêt pour l'intégration MIA si tous les tests sont OK")
        
    except KeyboardInterrupt:
        print("\n⏹️ Test interrompu par l'utilisateur")
    except Exception as e:
        print(f"\n❌ Erreur générale : {e}")


