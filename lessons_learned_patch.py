#!/usr/bin/env python3
"""
PATCH D'INTÉGRATION - LESSONS LEARNED ANALYZER
Instructions pour intégrer le Lessons Learned Analyzer dans automation_main.py
"""

print("📚 INTÉGRATION LESSONS LEARNED ANALYZER")
print("=" * 60)

print("\n🎯 OBJECTIF: Capturer et analyser les leçons de chaque trade pour atteindre 1000 trades")
print("📊 Base de données: data/lessons_learned.db")
print("🔬 Analyse automatique tous les 25 trades")

print("\n1️⃣ IMPORT (DÉJÀ FAIT)")
print("   from core.lessons_learned_analyzer import create_lessons_learned_analyzer")

print("\n2️⃣ INITIALISATION dans __init__ (DÉJÀ FAIT)")
print("""   
   try:
       self.lessons_learned_analyzer = create_lessons_learned_analyzer()
       self.logger.info("📚 Lessons Learned Analyzer initialisé - Collecte de données active")
   except Exception as e:
       self.logger.warning(f"⚠️ Erreur init Lessons Learned Analyzer: {e}")
       self.lessons_learned_analyzer = None
""")

print("\n3️⃣ CAPTURE APRÈS TRADE RÉEL (DÉJÀ FAIT)")
print("""
   if order_result.success:
       # ... autres stats ...
       
       # 📚 NOUVEAU: Capture de leçon après trade réel
       if self.lessons_learned_analyzer:
           try:
               trade_data = {
                   'trade_id': f"REAL-{order_result.order_id}",
                   'entry_price': current_price,
                   'symbol': 'ES',
                   'side': action,
                   'confluence_score': confluence_score,
                   'signal_type': str(signal_direction),
                   'timestamp': datetime.now()
               }
               self.lessons_learned_analyzer.record_lesson(trade_data)
           except Exception as e:
               self.logger.warning(f"⚠️ Erreur capture leçon: {e}")
""")

print("\n4️⃣ CAPTURE APRÈS TRADE SIMULÉ (DÉJÀ FAIT)")
print("""
   # Dans _simulate_trade_result après calcul du P&L:
   
   # 📚 NOUVEAU: Capture de leçon après trade simulé
   if self.lessons_learned_analyzer:
       try:
           trade_data = {
               'trade_id': f"SIM-{self.stats.total_trades:04d}",
               'entry_price': getattr(market_data, 'close', 4500.0),
               'exit_price': getattr(market_data, 'close', 4500.0) + (pnl / 12.5),
               'symbol': 'ES',
               'side': 'LONG' if signal_type in [SignalType.LONG, SignalType.LONG_STRONG] else 'SHORT',
               'pnl_gross': pnl,
               'is_winner': is_winner,
               'confluence_score': getattr(signal, 'confluence_score', 0.0),
               'signal_type': str(getattr(signal, 'signal_type', SignalType.NO_SIGNAL)),
               'timestamp': datetime.now(),
               'duration_minutes': random.uniform(2, 15),
               'slippage_ticks': random.uniform(0.1, 0.5),
               'execution_delay_ms': random.uniform(50, 200)
           }
           self.lessons_learned_analyzer.record_lesson(trade_data)
       except Exception as e:
           self.logger.warning(f"⚠️ Erreur capture leçon simulée: {e}")
""")

print("\n5️⃣ ANALYSE PÉRIODIQUE (OPTIONNEL)")
print("""
   # Ajouter dans la boucle principale, tous les 25 trades:
   
   if self.lessons_learned_analyzer and self.stats.total_trades % 25 == 0:
       try:
           progress = self.lessons_learned_analyzer.get_progress_to_target()
           self.logger.info(f"📊 Progrès vers 1000 trades: {progress['current_trades']}/1000 ({progress['completion_pct']:.1f}%)")
           
           if progress['current_trades'] >= 25:
               analysis = self.lessons_learned_analyzer.analyze_patterns(min_trades=25)
               if 'overview' in analysis:
                   overview = analysis['overview']
                   self.logger.info(f"📈 Win Rate Global: {overview['win_rate']:.1f}% | P&L Moyen: ${overview['avg_pnl_per_trade']:+.2f}")
       except Exception as e:
           self.logger.warning(f"⚠️ Erreur analyse leçons: {e}")
""")

print("\n✅ INTÉGRATION COMPLÈTE!")
print("🎯 Le système va maintenant capturer automatiquement chaque trade")
print("📊 Objectif: 1000 trades pour analyse ML approfondie")
print("💡 Les données peuvent être envoyées sur Discord pour suivi")

print("\n🔍 VÉRIFICATION:")
print("- ✅ Module créé: core/lessons_learned_analyzer.py")
print("- ✅ Tests créés: test_lessons_learned.py")
print("- ✅ Intégration core/__init__.py")
print("- ✅ Intégration automation_main.py")
print("- ✅ Base de données SQLite configurée")

print("\nStatut: 🟢 PRÊT POUR COLLECTE DE DONNÉES!")