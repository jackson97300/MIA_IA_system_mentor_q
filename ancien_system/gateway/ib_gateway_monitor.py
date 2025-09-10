#!/usr/bin/env python3
"""
IB Gateway Monitor - MIA_IA_SYSTEM
===================================

Script de monitoring continu pour IB Gateway
avec surveillance Level 2 et Options.

USAGE:
python monitoring/ib_gateway_monitor.py
"""

import asyncio
import time
import json
from datetime import datetime, timedelta
import logging
import sys
import os

# Ajouter le répertoire parent au path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.ibkr_connector import create_ibkr_connector
from core.logger import get_logger

logger = get_logger(__name__)

class IBGatewayMonitor:
    def __init__(self):
        self.connector = create_ibkr_connector(use_gateway=True)
        self.stats = {
            'requests': 0,
            'errors': 0,
            'latency_avg': 0,
            'last_check': None,
            'level2_checks': 0,
            'options_checks': 0,
            'imbalance_alerts': 0,
            'start_time': datetime.now()
        }
        self.alert_threshold = 0.15  # Seuil d'alerte imbalance
        self.running = True
    
    async def monitor_connection(self):
        """Monitoring continu IB Gateway"""
        print("🚀 MONITORING IB GATEWAY DÉMARRÉ")
        print("=" * 40)
        print(f"⏰ Démarrage: {self.stats['start_time'].strftime('%H:%M:%S')}")
        print(f"🎯 Seuil alerte imbalance: {self.alert_threshold}")
        print("=" * 40)
        
        while self.running:
            try:
                start_time = time.time()
                
                # Test connexion
                if await self.connector.connect():
                    # Test Level 2
                    level2_data = await self.connector.get_level2_data("ES")
                    
                    if level2_data:
                        latency = time.time() - start_time
                        self.stats['requests'] += 1
                        self.stats['level2_checks'] += 1
                        self.stats['latency_avg'] = (
                            (self.stats['latency_avg'] * (self.stats['requests'] - 1) + latency) 
                            / self.stats['requests']
                        )
                        
                        # Analyse imbalance
                        imbalance = self.analyze_imbalance(level2_data)
                        if abs(imbalance) > self.alert_threshold:
                            self.stats['imbalance_alerts'] += 1
                            print(f"🚨 ALERTE IMBALANCE: {imbalance:.4f} à {datetime.now().strftime('%H:%M:%S')}")
                        
                        # Affichage statut
                        self.print_status(latency, imbalance)
                    else:
                        self.stats['errors'] += 1
                        print(f"❌ Erreur Level 2 à {datetime.now().strftime('%H:%M:%S')}")
                else:
                    self.stats['errors'] += 1
                    print(f"❌ Erreur connexion à {datetime.now().strftime('%H:%M:%S')}")
                
                self.stats['last_check'] = datetime.now()
                await asyncio.sleep(30)  # Check toutes les 30s
                
            except Exception as e:
                print(f"❌ Erreur monitoring: {e} à {datetime.now().strftime('%H:%M:%S')}")
                self.stats['errors'] += 1
                await asyncio.sleep(60)
    
    def analyze_imbalance(self, level2_data):
        """Analyse imbalance des données Level 2"""
        try:
            bids = level2_data['bids']
            asks = level2_data['asks']
            
            if not bids or not asks:
                return 0.0
            
            # Calcul imbalance pondéré (5 premiers niveaux)
            bid_volume = sum(size * (0.8 ** i) for i, (_, size) in enumerate(bids[:5]))
            ask_volume = sum(size * (0.8 ** i) for i, (_, size) in enumerate(asks[:5]))
            total_volume = bid_volume + ask_volume
            
            if total_volume > 0:
                return (bid_volume - ask_volume) / total_volume
            else:
                return 0.0
                
        except Exception as e:
            print(f"❌ Erreur analyse imbalance: {e}")
            return 0.0
    
    def print_status(self, latency, imbalance):
        """Affichage statut monitoring"""
        uptime = datetime.now() - self.stats['start_time']
        uptime_str = str(uptime).split('.')[0]  # Format HH:MM:SS
        
        # Calcul taux d'erreur
        error_rate = (self.stats['errors'] / max(self.stats['requests'], 1)) * 100
        
        # Statut imbalance
        if abs(imbalance) > self.alert_threshold:
            imbalance_status = "🚨 ALERTE"
        elif abs(imbalance) > 0.05:
            imbalance_status = "⚠️ ATTENTION"
        else:
            imbalance_status = "✅ NORMAL"
        
        print(f"⏰ {datetime.now().strftime('%H:%M:%S')} | "
              f"🕐 {uptime_str} | "
              f"⚡ {latency:.3f}s | "
              f"📊 {imbalance:.4f} {imbalance_status} | "
              f"❌ {error_rate:.1f}% | "
              f"🚨 {self.stats['imbalance_alerts']} alertes")
    
    def print_summary(self):
        """Affichage résumé final"""
        print("\n" + "=" * 50)
        print("📊 RÉSUMÉ MONITORING IB GATEWAY")
        print("=" * 50)
        
        uptime = datetime.now() - self.stats['start_time']
        total_requests = self.stats['requests']
        total_errors = self.stats['errors']
        error_rate = (total_errors / max(total_requests, 1)) * 100
        
        print(f"⏱️  Temps total: {str(uptime).split('.')[0]}")
        print(f"📡 Requêtes: {total_requests}")
        print(f"❌ Erreurs: {total_errors} ({error_rate:.1f}%)")
        print(f"⚡ Latence moyenne: {self.stats['latency_avg']:.3f}s")
        print(f"🚨 Alertes imbalance: {self.stats['imbalance_alerts']}")
        print(f"📊 Checks Level 2: {self.stats['level2_checks']}")
        print(f"📈 Checks Options: {self.stats['options_checks']}")
        
        if self.stats['latency_avg'] < 0.1:
            print("✅ Performance: EXCELLENTE")
        elif self.stats['latency_avg'] < 0.3:
            print("✅ Performance: BONNE")
        else:
            print("⚠️ Performance: À AMÉLIORER")
    
    def save_stats(self, filename="ib_gateway_stats.json"):
        """Sauvegarde statistiques"""
        try:
            stats_copy = self.stats.copy()
            stats_copy['start_time'] = stats_copy['start_time'].isoformat()
            stats_copy['last_check'] = stats_copy['last_check'].isoformat() if stats_copy['last_check'] else None
            
            with open(filename, 'w') as f:
                json.dump(stats_copy, f, indent=2)
            
            print(f"💾 Statistiques sauvegardées: {filename}")
        except Exception as e:
            print(f"❌ Erreur sauvegarde stats: {e}")

async def main():
    """Fonction principale"""
    import signal
    
    monitor = IBGatewayMonitor()
    
    def signal_handler(signum, frame):
        print("\n🛑 Arrêt du monitoring...")
        monitor.running = False
    
    # Gestion arrêt propre
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        await monitor.monitor_connection()
    except KeyboardInterrupt:
        print("\n🛑 Arrêt demandé par l'utilisateur")
    finally:
        monitor.print_summary()
        monitor.save_stats()
        await monitor.connector.disconnect()
        print("✅ Monitoring arrêté proprement")

if __name__ == "__main__":
    asyncio.run(main()) 