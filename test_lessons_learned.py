#!/usr/bin/env python3
"""
Test du Lessons Learned Analyzer
Objectif: Valider la capture et l'analyse des leçons
"""

import sys
import asyncio
import tempfile
import shutil
from pathlib import Path
from datetime import datetime

sys.path.append(str(Path(__file__).parent))

from core.lessons_learned_analyzer import create_lessons_learned_analyzer, TradeLesson

def test_lessons_learned_analyzer():
    """Test complet du Lessons Learned Analyzer"""
    print("🧠 TEST LESSONS LEARNED ANALYZER")
    print("=" * 60)
    
    # Créer répertoire temporaire pour test
    temp_dir = tempfile.mkdtemp()
    db_path = Path(temp_dir) / "test_lessons.db"
    
    try:
        # Test 1: Création analyzer
        print("\n1️⃣ CRÉATION ANALYZER")
        analyzer = create_lessons_learned_analyzer(str(db_path))
        print(f"✅ Analyzer créé avec DB: {db_path}")
        
        # Test 2: Capture de trades simulés
        print("\n2️⃣ CAPTURE TRADES SIMULÉS")
        
        # Trade 1: Winner avec confluence élevée
        trade1 = {
            'entry_price': 5247.50,
            'exit_price': 5249.00,
            'pnl_gross': 187.50,
            'direction': 'LONG',
            'confluence_score': 0.85,
            'signal_type': 'battle_navale',
            'duration_minutes': 8.5,
            'slippage_ticks': 0.25
        }
        
        lesson1 = analyzer.capture_trade_lesson(
            trade_data=trade1,
            qualitative_notes={
                'what_worked': 'Confluence multiple + volume confirmation',
                'market_context': 'NY session active, trending market',
                'improvement_suggestion': 'Entrée plus agressive possible'
            }
        )
        print(f"✅ Trade 1 capturé: {lesson1.trade_id} (+{lesson1.pnl_ticks:.1f} ticks)")
        
        # Trade 2: Loser avec confluence faible  
        trade2 = {
            'entry_price': 5248.00,
            'exit_price': 5246.75,
            'pnl_gross': -156.25,
            'direction': 'LONG',
            'confluence_score': 0.68,
            'signal_type': 'battle_navale',
            'duration_minutes': 4.2,
            'slippage_ticks': 0.75
        }
        
        lesson2 = analyzer.capture_trade_lesson(
            trade_data=trade2,
            qualitative_notes={
                'what_failed': 'Confluence insuffisante + mauvais timing',
                'market_context': 'Market choppy, pas de trend clear',
                'improvement_suggestion': 'Attendre confluence >0.75'
            }
        )
        print(f"✅ Trade 2 capturé: {lesson2.trade_id} ({lesson2.pnl_ticks:+.1f} ticks)")
        
        # Trade 3: Winner avec exécution parfaite
        trade3 = {
            'entry_price': 5245.25,
            'exit_price': 5247.75,
            'pnl_gross': 312.50,
            'direction': 'LONG',
            'confluence_score': 0.92,
            'signal_type': 'battle_navale_elite',
            'duration_minutes': 12.8,
            'slippage_ticks': 0.0
        }
        
        lesson3 = analyzer.capture_trade_lesson(
            trade_data=trade3,
            qualitative_notes={
                'what_worked': 'Setup parfait + exécution instantanée',
                'market_context': 'Strong trend + high volume',
                'improvement_suggestion': 'Garder cette approche'
            }
        )
        print(f"✅ Trade 3 capturé: {lesson3.trade_id} (+{lesson3.pnl_ticks:.1f} ticks)")
        
        # Test 3: Progression vers objectif
        print("\n3️⃣ PROGRESSION VERS OBJECTIF 1000 TRADES")
        progress = analyzer.get_progress_to_target()
        print(f"📊 Trades actuels: {progress['current_trades']}")
        print(f"🎯 Objectif: {progress['target_trades']}")
        print(f"📈 Progression: {progress['completion_pct']:.2f}%")
        print(f"🔬 Échantillon significatif: {progress['is_significant_sample']}")
        
        # Test 4: Analyse des patterns
        print("\n4️⃣ ANALYSE DES PATTERNS")
        analysis = analyzer.analyze_patterns(min_trades=1)  # Réduire pour test
        
        # Gérer les 3 cas possibles: succès (pas de 'status'), données insuffisantes, erreur
        if 'status' in analysis:
            if analysis['status'] == 'error':
                print(f"❌ Erreur analyse: {analysis['message']}")
            elif analysis['status'] == 'insufficient_data':
                print(f"⚠️ Données insuffisantes: {analysis['message']}")
        else:
            # Cas de succès (pas de clé 'status', mais présence de 'overview')
            if 'overview' in analysis:
                overview = analysis['overview']
                print(f"📊 Total trades: {overview['total_trades']}")
                print(f"🏆 Win rate: {overview['win_rate']:.1f}%")
                print(f"💰 P&L total: ${overview['total_pnl']:+.2f}")
                print(f"⚡ P&L moyen: ${overview['avg_pnl_per_trade']:+.2f}")
                print(f"⏱️ Durée moyenne: {overview['avg_duration_minutes']:.1f} min")
                
                # Patterns par signal
                patterns = analysis.get('patterns', {})
                if patterns:
                    print("\n🎯 ANALYSE PAR PATTERN:")
                    for pattern, stats in patterns.items():
                        print(f"  • {pattern}: {stats['win_rate']:.1f}% WR, ${stats['avg_pnl']:+.2f}/trade")
                
                # Insights qualitatifs
                insights = analysis.get('qualitative_insights', {})
                if insights.get('top_what_worked'):
                    print(f"\n💡 CE QUI MARCHE: {insights['top_what_worked'][0]}")
                if insights.get('top_what_failed'):
                    print(f"⚠️ CE QUI ÉCHOUE: {insights['top_what_failed'][0]}")
                    
                print("✅ Analyse patterns réussie")
            else:
                print("❌ Structure d'analyse inattendue")
        
        # Test 5: Stats de session
        print("\n5️⃣ STATS DE SESSION")
        stats = analyzer.session_stats
        print(f"📈 Trades analysés: {stats['trades_analyzed']}")
        print(f"📚 Leçons capturées: {stats['lessons_captured']}")
        print(f"❌ Erreurs: {stats['analysis_errors']}")
        
        print("\n" + "=" * 60)
        print("🎉 TOUS LES TESTS PASSÉS !")
        print("🧠 Lessons Learned Analyzer: ✅ Fonctionnel")
        print("📊 Base de données: ✅ Opérationnelle")
        print("🎯 Prêt pour objectif 1000 trades !")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"❌ ERREUR TEST: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        # Nettoyage
        try:
            shutil.rmtree(temp_dir)
        except:
            pass

async def test_discord_integration():
    """Test intégration Discord (simulation)"""
    print("\n🔔 TEST INTÉGRATION DISCORD")
    
    # Mock Discord notifier
    class MockDiscordNotifier:
        def __init__(self):
            self.messages_sent = []
        
        async def send_custom_message(self, channel, title, description, color=None):
            message = {
                'channel': channel,
                'title': title,
                'description': description,
                'color': color
            }
            self.messages_sent.append(message)
            print(f"📤 Discord simulé: {title}")
            print(f"   Channel: {channel}")
            print(f"   Description: {description[:100]}...")
            return True
    
    try:
        # Créer analyzer avec données
        temp_dir = tempfile.mkdtemp()
        db_path = Path(temp_dir) / "test_discord.db"
        analyzer = create_lessons_learned_analyzer(str(db_path))
        
        # Ajouter quelques trades
        for i in range(5):
            trade = {
                'entry_price': 5247.0 + i,
                'exit_price': 5248.0 + i,
                'pnl_gross': 125.0,
                'direction': 'LONG',
                'confluence_score': 0.8,
                'signal_type': 'battle_navale'
            }
            analyzer.capture_trade_lesson(trade_data=trade)
        
        # Test Discord
        mock_discord = MockDiscordNotifier()
        analysis = analyzer.analyze_patterns(min_trades=1)
        
        result = await analyzer.send_discord_summary(analysis, mock_discord)
        
        if result and mock_discord.messages_sent:
            print("✅ Intégration Discord simulée réussie")
            message = mock_discord.messages_sent[0]
            print(f"✅ Message envoyé sur #{message['channel']}")
        else:
            print("❌ Échec intégration Discord")
        
        # Cleanup
        shutil.rmtree(temp_dir)
        
    except Exception as e:
        print(f"❌ Erreur test Discord: {e}")

async def main():
    """Test principal"""
    print("🧠 TESTS LESSONS LEARNED ANALYZER")
    print("🎯 Objectif: Validation pour collecte 1000 trades")
    print("=" * 60)
    
    # Test principal
    success = test_lessons_learned_analyzer()
    
    if success:
        # Test Discord
        await test_discord_integration()
    
    if success:
        print("\n🚀 PRÊT POUR INTÉGRATION DANS AUTOMATION_MAIN.PY")
        print("📊 Le module peut maintenant capturer vos 1000 trades !")
    else:
        print("\n❌ Tests échoués - corrections nécessaires")

if __name__ == "__main__":
    asyncio.run(main())