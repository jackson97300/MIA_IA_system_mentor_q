#!/usr/bin/env python3
"""
PATCH CATASTROPHE MONITOR - Instructions d'intégration
"""

print("""
🛡️ PATCH CATASTROPHE MONITOR - PROTECTION ABSOLUE

OPTION A: Intégration dans automation_main.py (RECOMMANDÉE)
═══════════════════════════════════════════════════════════

ÉTAPE 1: Import
──────────────

Ajoutez en haut de automation_main.py (ligne ~35):

    from core.catastrophe_monitor import create_catastrophe_monitor, CatastropheLevel


ÉTAPE 2: Initialisation dans __init__
───────────────────────────────────────

Dans MIAAutomationSystem.__init__ (vers ligne 950), ajoutez:

    # 🛡️ Catastrophe Monitor - Protection absolue
    catastrophe_config = {
        'daily_loss_limit': getattr(config, 'daily_loss_limit', 500.0),
        'max_position_size': getattr(config, 'max_position_size', 2),
        'max_consecutive_losses': 5,
        'account_balance_min': 1000.0
    }
    self.catastrophe_monitor = create_catastrophe_monitor(catastrophe_config)
    self.daily_pnl = 0.0
    self.current_position_size = 0


ÉTAPE 3: Vérification avant chaque trade
──────────────────────────────────────────

Dans _execute_trade (vers ligne 1252), AVANT d'exécuter le trade, ajoutez:

    async def _execute_trade(self, signal, market_data):
        \"\"\"Exécuter trade avec protection catastrophe\"\"\"
        try:
            # 🛡️ VÉRIFICATION CATASTROPHE - AVANT TRADE
            alert = self.catastrophe_monitor.check_catastrophe_conditions(
                current_pnl=self.daily_pnl,
                account_balance=getattr(self, 'account_balance', 10000.0),  # À adapter selon votre vraie balance
                position_size=self.current_position_size,
                market_data=market_data
            )
            
            # Traitement selon niveau d'alerte
            if alert.level == CatastropheLevel.EMERGENCY:
                self.logger.critical(f"🚨 CATASTROPHE EMERGENCY: {alert.trigger}")
                self.logger.critical(f"ACTION REQUISE: {alert.action_required}")
                
                # ARRÊT IMMÉDIAT - Pas de nouveau trade
                await self.emergency_shutdown()
                return
                
            elif alert.level == CatastropheLevel.DANGER:
                self.logger.error(f"⚠️ CATASTROPHE DANGER: {alert.trigger}")
                self.logger.error(f"ACTION: {alert.action_required}")
                
                # Bloquer ce trade mais continuer monitoring
                self.stats.trades_blocked += 1
                return
                
            elif alert.level == CatastropheLevel.WARNING:
                self.logger.warning(f"💡 CATASTROPHE WARNING: {alert.trigger}")
                # Continuer mais avec attention
            
            # Si on arrive ici, conditions OK pour trader
            # ... votre code d'exécution existant ...


ÉTAPE 4: Enregistrer résultat après trade
────────────────────────────────────────────

Après chaque trade exécuté, ajoutez:

    # 🛡️ Enregistrer résultat pour monitoring
    trade_pnl = # ... votre calcul de P&L ...
    is_winner = trade_pnl > 0
    
    self.catastrophe_monitor.record_trade_result(trade_pnl, is_winner)
    self.daily_pnl += trade_pnl
    
    # Log pour debug
    self.logger.info(f"Trade result: PnL={trade_pnl:+.2f}, Daily PnL={self.daily_pnl:+.2f}")


ÉTAPE 5: Méthode emergency_shutdown
─────────────────────────────────────

Ajoutez cette méthode dans MIAAutomationSystem:

    async def emergency_shutdown(self):
        \"\"\"Arrêt d'urgence complet\"\"\"
        try:
            self.logger.critical("🚨 EMERGENCY SHUTDOWN TRIGGERED")
            
            # 1. Arrêter la boucle principale
            self.shutdown_requested = True
            self.is_running = False
            
            # 2. Fermer toutes positions (si vous avez cette logique)
            await self._close_all_positions()
            
            # 3. Notification Discord critique
            if hasattr(self, 'discord_notifier') and self.discord_notifier:
                await self.discord_notifier.send_custom_message(
                    'critical_errors',
                    '🚨 EMERGENCY SHUTDOWN',
                    f'Catastrophe monitor triggered emergency stop',
                    color=0xFF0000,  # Rouge
                    urgent=True
                )
            
            # 4. Stats
            self.stats.emergency_shutdowns = getattr(self.stats, 'emergency_shutdowns', 0) + 1
            
        except Exception as e:
            self.logger.critical(f"Erreur emergency_shutdown: {e}")


═══════════════════════════════════════════════════════════

OPTION B: Intégration dans risk_manager.py (Alternative)
═══════════════════════════════════════════════════════

Si vous préférez intégrer dans execution/risk_manager.py:

1. Ajoutez l'import en haut
2. Initialisez dans __init__ du RiskManager  
3. Appelez check_catastrophe_conditions dans validate_trade()
4. Retournez False si niveau DANGER ou EMERGENCY

═══════════════════════════════════════════════════════════

TEST AVANT PRODUCTION:
────────────────────

1. Lancez: python test_catastrophe_monitor.py
2. Vérifiez que tous les tests passent
3. Testez avec des petites limites d'abord
4. Augmentez progressivement les seuils

⚠️ ATTENTION: Ce module peut ARRÊTER votre trading automatiquement.
Testez bien avant de l'utiliser avec de l'argent réel !

""")