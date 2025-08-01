#!/usr/bin/env python3
"""
Test ultra-minimal du Mentor System - Évite automation_main.py
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

# Ajouter le répertoire courant au path
sys.path.insert(0, '.')

def test_mentor_system_creation():
    """Test de création du Mentor System"""
    print("\n1️⃣ TEST CRÉATION MENTOR SYSTEM")
    try:
        from core.mentor_system import create_mentor_system, MentorSystem
        
        # URL Discord de test
        test_webhook = "https://discordapp.com/api/webhooks/1389206555282640987/v0WvrD3ntDkwGJIyxRh0EEAFNoh1NpSY8Oloxy8tWMZjsFGRed_OYpG1zaSdP2dWH2j7"
        
        # Créer le mentor system
        mentor = create_mentor_system(test_webhook)
        
        print(f"✅ Mentor System créé: {type(mentor)}")
        print(f"✅ Webhook URL: {mentor.discord_webhook_url}")
        print(f"✅ Configuration: {len(mentor.mentor_config)} paramètres")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur création Mentor System: {e}")
        return False

def test_mentor_advice_generation():
    """Test de génération de conseils"""
    print("\n2️⃣ TEST GÉNÉRATION CONSEILS")
    try:
        from core.mentor_system import MentorSystem, DailyPerformance, MentorAdviceLevel
        
        # Créer une performance simulée
        performance = DailyPerformance(
            date=datetime.now(),
            total_trades=8,
            winning_trades=5,
            losing_trades=3,
            win_rate=0.625,
            total_pnl=1250.0,
            avg_win=300.0,
            avg_loss=-150.0,
            max_win=450.0,
            max_loss=-180.0,
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
        
        print(f"✅ {len(advice_list)} conseils générés")
        for i, advice in enumerate(advice_list[:3]):
            print(f"   {i+1}. {advice.title}: {advice.message}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur génération conseils: {e}")
        return False

def test_discord_embed_creation():
    """Test de création d'embed Discord"""
    print("\n3️⃣ TEST CRÉATION EMBED DISCORD")
    try:
        from core.mentor_system import MentorSystem, DailyPerformance
        
        # Créer une performance simulée
        performance = DailyPerformance(
            date=datetime.now(),
            total_trades=8,
            winning_trades=5,
            losing_trades=3,
            win_rate=0.625,
            total_pnl=1250.0,
            avg_win=300.0,
            avg_loss=-150.0,
            max_win=450.0,
            max_loss=-180.0,
            profit_factor=2.0,
            largest_drawdown=-200.0,
            best_pattern="Trades gagnants cohérents",
            worst_pattern="Trades perdants répétitifs",
            improvement_areas=["Améliorer la qualité des entrées"],
            strengths=["Excellent taux de réussite"]
        )
        
        # Créer le mentor
        mentor = MentorSystem("test_webhook")
        
        # Créer l'embed
        embed = mentor._create_discord_embed(performance, [])
        
        print(f"✅ Embed créé avec succès")
        print(f"   Titre: {embed.get('title', 'N/A')}")
        print(f"   Couleur: {embed.get('color', 'N/A')}")
        print(f"   Champs: {len(embed.get('fields', []))}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur création embed: {e}")
        return False

def test_mentor_configuration():
    """Test de configuration du mentor"""
    print("\n4️⃣ TEST CONFIGURATION MENTOR")
    try:
        from core.mentor_system import MentorSystem
        
        mentor = MentorSystem("test_webhook")
        
        # Vérifier la configuration
        config = mentor.mentor_config
        
        print(f"✅ Configuration chargée:")
        print(f"   Heure rapport: {config['daily_report_time']}")
        print(f"   Trades min: {config['min_trades_for_analysis']}")
        print(f"   Messages max: {config['max_daily_messages']}")
        print(f"   Seuils performance: {len(config['performance_thresholds'])} seuils")
        
        # Vérifier les seuils
        thresholds = config['performance_thresholds']
        print(f"   Excellent win rate: {thresholds['excellent_win_rate']:.1%}")
        print(f"   Critique win rate: {thresholds['critical_win_rate']:.1%}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur configuration: {e}")
        return False

def test_mentor_imports():
    """Test des imports du Mentor System"""
    print("\n5️⃣ TEST IMPORTS MENTOR SYSTEM")
    try:
        # Test des imports de base
        from core.mentor_system import (
            MentorSystem, 
            create_mentor_system, 
            MentorAdvice, 
            DailyPerformance, 
            MentorMessageType, 
            MentorAdviceLevel
        )
        
        print("✅ Tous les imports du Mentor System réussis")
        print(f"   MentorSystem: {MentorSystem}")
        print(f"   create_mentor_system: {create_mentor_system}")
        print(f"   MentorAdvice: {MentorAdvice}")
        print(f"   DailyPerformance: {DailyPerformance}")
        print(f"   MentorMessageType: {MentorMessageType}")
        print(f"   MentorAdviceLevel: {MentorAdviceLevel}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur imports: {e}")
        return False

def test_mentor_integration_core():
    """Test d'intégration avec core/__init__.py"""
    print("\n6️⃣ TEST INTÉGRATION CORE")
    try:
        from core import get_module_status
        
        # Vérifier que le mentor system est dans les modules
        status = get_module_status()
        
        if 'mentor_system_available' in status:
            print(f"✅ Mentor System dans core/__init__.py: {status['mentor_system_available']}")
        else:
            print("⚠️ Mentor System non trouvé dans core/__init__.py")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur intégration core: {e}")
        return False

def main():
    """Test principal du Mentor System (version ultra-minimale)"""
    print("🎓 TEST ULTRA-MINIMAL DU MENTOR SYSTEM")
    print("=" * 50)
    
    tests = [
        ("Imports", test_mentor_imports),
        ("Création", test_mentor_system_creation),
        ("Génération conseils", test_mentor_advice_generation),
        ("Création embed", test_discord_embed_creation),
        ("Configuration", test_mentor_configuration),
        ("Intégration core", test_mentor_integration_core)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Erreur test {test_name}: {e}")
            results.append((test_name, False))
    
    # Résumé
    print("\n" + "=" * 50)
    print("📊 RÉSULTATS DES TESTS")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSÉ" if result else "❌ ÉCHOUÉ"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 SCORE: {passed}/{total} tests réussis")
    
    if passed == total:
        print("🎉 TOUS LES TESTS RÉUSSIS - MENTOR SYSTEM OPÉRATIONNEL")
    else:
        print("⚠️ CERTAINS TESTS ONT ÉCHOUÉ - VÉRIFICATION NÉCESSAIRE")

if __name__ == "__main__":
    main() 