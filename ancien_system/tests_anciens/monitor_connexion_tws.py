
#!/usr/bin/env python3
"""
Monitoring connexion TWS en temps réel
"""

import time
import socket
import threading
from datetime import datetime

class TWSConnectionMonitor:
    """Moniteur de connexion TWS en temps réel"""
    
    def __init__(self):
        self.is_monitoring = False
        self.connection_issues = 0
        self.last_check = None
        self.check_interval = 30  # secondes
        
    def start_monitoring(self):
        """Démarrer le monitoring"""
        self.is_monitoring = True
        print("📊 Monitoring connexion TWS démarré...")
        
        while self.is_monitoring:
            try:
                self.check_connection()
                time.sleep(self.check_interval)
            except KeyboardInterrupt:
                print("\n🛑 Monitoring arrêté")
                break
            except Exception as e:
                print(f"❌ Erreur monitoring: {e}")
                time.sleep(5)
    
    def check_connection(self):
        """Vérifier la connexion TWS"""
        current_time = datetime.now()
        
        try:
            # Test connexion TWS
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10)
            result = sock.connect_ex(('127.0.0.1', 7497))
            sock.close()
            
            if result == 0:
                status = "✅ CONNECTÉ"
                if self.connection_issues > 0:
                    print(f"🔄 Reconnexion réussie à {current_time.strftime('%H:%M:%S')}")
                    self.connection_issues = 0
            else:
                status = "❌ DÉCONNECTÉ"
                self.connection_issues += 1
                print(f"⚠️ Problème connexion #{self.connection_issues} à {current_time.strftime('%H:%M:%S')}")
            
            self.last_check = current_time
            
        except Exception as e:
            status = f"❌ ERREUR: {e}"
            self.connection_issues += 1
        
        # Afficher statut toutes les 5 minutes
        if not self.last_check or (current_time - self.last_check).seconds >= 300:
            print(f"📊 {current_time.strftime('%H:%M:%S')} - TWS: {status}")

if __name__ == "__main__":
    monitor = TWSConnectionMonitor()
    monitor.start_monitoring()
