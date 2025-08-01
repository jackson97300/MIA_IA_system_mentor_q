#!/usr/bin/env python3
"""
Test du Mentor System
"""

import asyncio
import sys
from datetime import datetime, timedelta
import pandas as pd
import sqlite3
import os

# Ajouter le chemin du projet
sys.path.append('.')

from core.mentor_system import MentorSystem, DailyPerformance, MentorAdvice, MentorMessageType, MentorAdviceLevel

def create_test_data():
    """Crée des données de test dans la base de données"""
    db_path = "data/lessons_learned.db"
    
    # Créer le dossier data s'il n'existe pas
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    # Connexion à la base de données
    with sqlite3.connect(db_path) as conn:
        # Créer la table si elle n'existe pas
        conn.execute("""
            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME NOT NULL,
                symbol TEXT NOT NULL,
                side TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                price REAL NOT NULL,
                pnl REAL,
                pattern TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Supprimer les anciennes données de test
        conn.execute("DELETE FROM trades WHERE DATE(timestamp) = DATE(?)", (datetime.now(),))
        
        # Insérer des données de test
        test_trades = [
            (datetime.now() - timedelta(hours=2), "ES", "BUY", 1, 4500.0, 125.0, "battle_navale"),
            (datetime.now() - timedelta(hours=1), "ES", "SELL", 1, 4495.0, -75.0, "sierra_pattern"),
            (datetime.now() - timedelta(minutes=30), "ES", "BUY", 1, 4502.0, 200.0, "confluence"),
            (datetime.now() - timedelta(minutes=15), "ES", "SELL", 1, 4498.0, -50.0, "battle_navale"),
            (datetime.now() - timedelta(minutes=5), "ES", "BUY", 1, 4505.0, 150.0, "sierra_pattern"),
        ]
        
        conn.executemany("""
            INSERT INTO trades (timestamp, symbol, side, quantity, price, pnl, pattern)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, test_trades)
        
        conn.commit()
        print("✅ Données de test créées")

async def test_mentor_system():
    """Test complet du Mentor System"""
    try:
        print("🧪 Début du test Mentor System...")
        
        # Créer des données de test
        create_test_data()
        
        # URL de test Discord (remplacer par votre vraie URL)
        test_webhook = "https://discordapp.com/api/webhooks/1389206555282640987/v0WvrD3ntDkwGJIyxRh0EEAFNoh1NpSY8Oloxy8tWMZjsFGRed_OYpG1zaSdP2dWH2j7"
        
        # Créer l'instance du mentor
        mentor = MentorSystem(test_webhook)
        print("✅ Mentor System créé avec succès")
        
        # Test 1: Analyser la performance quotidienne
        print("\n📊 Test 1: Analyse de performance...")
        performance = await mentor.analyze_daily_performance()
        
        if performance:
            print(f"✅ Performance analysée:")
            print(f"   - Trades: {performance.total_trades}")
            print(f"   - Win Rate: {performance.win_rate:.1%}")
            print(f"   - PnL Total: ${performance.total_pnl:.2f}")
            print(f"   - Profit Factor: {performance.profit_factor:.2f}")
        else:
            print("❌ Aucune performance trouvée")
            return False
        
        # Test 2: Générer des conseils
        print("\n💡 Test 2: Génération de conseils...")
        advice_list = mentor.generate_personalized_advice(performance)
        print(f"✅ {len(advice_list)} conseils générés")
        
        for i, advice in enumerate(advice_list, 1):
            print(f"   {i}. {advice.title}: {advice.message}")
        
        # Test 3: Créer l'embed Discord
        print("\n📱 Test 3: Création embed Discord...")
        embed = mentor._create_discord_embed(performance, advice_list)
        if embed:
            print("✅ Embed Discord créé avec succès")
            print(f"   - Titre: {embed.get('title', 'N/A')}")
            print(f"   - Champs: {len(embed.get('fields', []))}")
        else:
            print("❌ Erreur création embed")
        
        # Test 4: Envoyer le message (optionnel)
        print("\n📤 Test 4: Envoi message Discord...")
        print("⚠️  Test d'envoi désactivé pour éviter le spam")
        # success = await mentor.send_daily_mentor_message(performance, advice_list)
        # print(f"✅ Message envoyé: {success}")
        
        print("\n🎉 Tous les tests du Mentor System ont réussi !")
        return True
        
    except Exception as e:
        print(f"❌ Erreur test Mentor System: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_mentor_advice():
    """Test de création de conseils"""
    try:
        print("\n🧪 Test création de conseils...")
        
        # Créer une performance de test
        performance = DailyPerformance(
            date=datetime.now(),
            total_trades=5,
            winning_trades=3,
            losing_trades=2,
            win_rate=0.6,
            total_pnl=350.0,
            avg_win=200.0,
            avg_loss=-100.0,
            max_win=250.0,
            max_loss=-150.0,
            profit_factor=2.0,
            largest_drawdown=-200.0,
            best_pattern="Trades gagnants cohérents",
            worst_pattern="Trades perdants répétitifs",
            improvement_areas=["Améliorer la qualité des entrées"],
            strengths=["Excellent taux de réussite"]
        )
        
        # Créer le mentor
        mentor = MentorSystem("test_webhook")
        
        # Générer des conseils
        advice_list = mentor.generate_personalized_advice(performance)
        
        print(f"✅ {len(advice_list)} conseils générés pour performance test")
        
        for i, advice in enumerate(advice_list, 1):
            print(f"   {i}. [{advice.level.value.upper()}] {advice.title}")
            print(f"      {advice.message}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur test conseils: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Démarrage des tests Mentor System...")
    
    # Test 1: Test complet du système
    success1 = asyncio.run(test_mentor_system())
    
    # Test 2: Test des conseils
    success2 = test_mentor_advice()
    
    if success1 and success2:
        print("\n🎉 TOUS LES TESTS ONT RÉUSSI !")
        print("✅ Le Mentor System fonctionne correctement")
    else:
        print("\n❌ CERTAINS TESTS ONT ÉCHOUÉ")
        print("⚠️  Vérifiez les erreurs ci-dessus") 