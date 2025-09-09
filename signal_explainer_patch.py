#!/usr/bin/env python3
"""
PATCH SIMPLE - Signal Explainer Integration
Instructions pour intégrer le Signal Explainer dans automation_main.py
"""

print("""
🔧 PATCH SIGNAL EXPLAINER - INTÉGRATION SIMPLE

ÉTAPE 1: Ajouter l'import en haut de automation_main.py
──────────────────────────────────────────────────────────

Ajoutez cette ligne vers la ligne 35 (après les autres imports core):

    from core.signal_explainer import create_signal_explainer


ÉTAPE 2: Initialiser dans __init__ de MIAAutomationSystem  
──────────────────────────────────────────────────────────

Dans la méthode __init__ de MIAAutomationSystem (vers ligne 950), ajoutez:

    # ✅ NOUVEAU: Signal Explainer
    self.signal_explainer = create_signal_explainer()
    self.last_signal_time = 0
    self.explanation_counter = 0


ÉTAPE 3: Modifier la boucle principale pour ajouter les explications
──────────────────────────────────────────────────────────────────

Remplacez les lignes 1237-1241:

    # Générer signal avec intégrations
    signal = await self._generate_signal(market_data)
    if not signal:
        await asyncio.sleep(0.1)
        continue

Par:

    # Générer signal avec intégrations
    signal = await self._generate_signal(market_data)
    if not signal:
        # ✅ NOUVEAU: Expliquer pourquoi pas de signal
        await self._explain_no_signal(market_data)
        await asyncio.sleep(0.1)
        continue
    
    # ✅ NOUVEAU: Mettre à jour last_signal_time
    import time
    self.last_signal_time = time.time()


ÉTAPE 4: Ajouter la méthode _explain_no_signal
─────────────────────────────────────────────

Ajoutez cette méthode dans la classe MIAAutomationSystem (vers la fin, ligne 1650):

    async def _explain_no_signal(self, market_data):
        \"\"\"Explique pourquoi aucun signal généré\"\"\"
        try:
            # Calculer confluence pour l'explication
            confluence_score = self.confluence_calc.calculate_enhanced_confluence(market_data)
            
            # Obtenir les raisons
            reasons = self.signal_explainer.explain_no_signal(
                market_data=market_data,
                confluence_score=confluence_score,
                last_signal_time=self.last_signal_time
            )
            
            # Logger seulement 1x par minute pour éviter spam
            if self.signal_explainer.should_log_explanation():
                explanation = self.signal_explainer.format_explanation(reasons)
                self.logger.info(f"🔍 {explanation}")
                
                # Optionnel: Envoyer à Discord (décommentez si vous voulez)
                # if hasattr(self, 'discord_notifier') and self.discord_notifier:
                #     await self.discord_notifier.send_custom_message(
                #         'signals_analysis',
                #         '🔍 Analyse Signal',
                #         explanation,
                #         color=0xFFA500
                #     )
                    
        except Exception as e:
            self.logger.debug(f"Erreur explain_no_signal: {e}")


ÉTAPE 5: Test rapide
───────────────────

1. Lancez d'abord: python test_signal_explainer.py
2. Si OK, lancez votre système normalement
3. Regardez les logs - vous devriez voir des messages "🔍 Pas de signal:" avec explications

C'est tout ! Aucune modification du core, juste un ajout simple.

""")