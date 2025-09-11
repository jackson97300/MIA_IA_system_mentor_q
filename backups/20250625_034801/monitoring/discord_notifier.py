"""
MIA_IA_SYSTEM - Discord Notifier
Notifications Discord OBLIGATOIRES pour suivi du bot
Version: Production Ready

Discord est OBLIGATOIRE pour :
- Notifications trades en temps réel
- Alertes erreurs critiques
- Rapports de performance
- Suivi à distance sur mobile
"""

import os
import asyncio
import logging
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from enum import Enum
from datetime import datetime
import json
import time
from pathlib import Path

# Discord.py
try:
    import discord
    from discord.ext import commands
    DISCORD_AVAILABLE = True
except ImportError:
    # Si discord.py n'est pas installé, on DOIT arrêter
    raise ImportError(
        "discord.py est OBLIGATOIRE pour MIA_IA_SYSTEM\n"
        "Installer avec: pip install discord.py>=2.3.0"
    )

logger = logging.getLogger(__name__)

# === CONFIGURATION ===

class NotificationType(Enum):
    """Types de notifications Discord"""
    INFO = "ℹ️"
    SUCCESS = "✅"
    WARNING = "⚠️"
    ERROR = "❌"
    TRADE_OPEN = "📈"
    TRADE_CLOSE = "📊"
    ALERT = "🚨"
    PERFORMANCE = "📊"
    SYSTEM = "🔧"

@dataclass
class DiscordConfig:
    """Configuration Discord"""
    # Token bot (OBLIGATOIRE)
    bot_token: str
    
    # Channels IDs
    main_channel_id: int
    alerts_channel_id: Optional[int] = None
    trades_channel_id: Optional[int] = None
    errors_channel_id: Optional[int] = None
    
    # Options
    embed_color_info: int = 0x3498db      # Bleu
    embed_color_success: int = 0x2ecc71   # Vert
    embed_color_warning: int = 0xf39c12   # Orange
    embed_color_error: int = 0xe74c3c     # Rouge
    
    # Limites
    max_message_length: int = 2000
    max_embed_fields: int = 25
    rate_limit_messages: int = 5          # Max messages par seconde
    
    # Reconnexion
    auto_reconnect: bool = True
    max_reconnect_attempts: int = 10
    reconnect_delay_seconds: int = 30

# === DISCORD NOTIFIER ===

class DiscordNotifier:
    """
    Notificateur Discord OBLIGATOIRE pour MIA_IA_SYSTEM
    
    Gère toutes les notifications vers Discord avec :
    - Reconnexion automatique
    - Queue de messages en cas de déconnexion
    - Formatage riche avec embeds
    - Rate limiting automatique
    """
    
    def __init__(self, config: Optional[DiscordConfig] = None):
        """
        Initialise le notifier Discord
        
        Args:
            config: Configuration Discord ou charge depuis env
        """
        # Configuration
        self.config = config or self._load_config_from_env()
        self._validate_config()
        
        # Discord client
        intents = discord.Intents.default()
        intents.message_content = True
        self.client = discord.Client(intents=intents)
        
        # État
        self.is_ready = False
        self.reconnect_attempts = 0
        self.message_queue: List[Dict[str, Any]] = []
        self.last_message_time = 0
        
        # Channels
        self.main_channel = None
        self.alerts_channel = None
        self.trades_channel = None
        self.errors_channel = None
        
        # Setup event handlers
        self._setup_event_handlers()
        
        # Stats
        self.stats = {
            'messages_sent': 0,
            'messages_failed': 0,
            'reconnections': 0,
            'uptime_start': datetime.now()
        }
        
        logger.info("✅ DiscordNotifier initialisé (OBLIGATOIRE)")
    
    def _load_config_from_env(self) -> DiscordConfig:
        """Charge configuration depuis variables environnement"""
        # Token OBLIGATOIRE
        bot_token = os.environ.get('DISCORD_BOT_TOKEN')
        if not bot_token:
            raise ValueError(
                "DISCORD_BOT_TOKEN est OBLIGATOIRE!\n"
                "Définir dans .env ou variable environnement"
            )
        
        # Channel principal OBLIGATOIRE
        main_channel = os.environ.get('DISCORD_MAIN_CHANNEL_ID')
        if not main_channel:
            raise ValueError(
                "DISCORD_MAIN_CHANNEL_ID est OBLIGATOIRE!\n"
                "Définir dans .env ou variable environnement"
            )
        
        try:
            main_channel_id = int(main_channel)
        except ValueError:
            raise ValueError(f"DISCORD_MAIN_CHANNEL_ID invalide: {main_channel}")
        
        # Channels optionnels
        config = DiscordConfig(
            bot_token=bot_token,
            main_channel_id=main_channel_id
        )
        
        # Channels additionnels (optionnels)
        if alerts_channel := os.environ.get('DISCORD_ALERTS_CHANNEL_ID'):
            config.alerts_channel_id = int(alerts_channel)
        
        if trades_channel := os.environ.get('DISCORD_TRADES_CHANNEL_ID'):
            config.trades_channel_id = int(trades_channel)
        
        if errors_channel := os.environ.get('DISCORD_ERRORS_CHANNEL_ID'):
            config.errors_channel_id = int(errors_channel)
        
        return config
    
    def _validate_config(self):
        """Valide la configuration"""
        if not self.config.bot_token:
            raise ValueError("Bot token Discord OBLIGATOIRE")
        
        if not self.config.main_channel_id:
            raise ValueError("Main channel ID OBLIGATOIRE")
        
        logger.info(f"Configuration Discord validée - Main channel: {self.config.main_channel_id}")
    
    def _setup_event_handlers(self):
        """Configure les event handlers Discord"""
        
        @self.client.event
        async def on_ready():
            """Appelé quand le bot est connecté"""
            logger.info(f"✅ Discord bot connecté: {self.client.user}")
            
            # Récupérer les channels
            self.main_channel = self.client.get_channel(self.config.main_channel_id)
            if not self.main_channel:
                logger.error(f"❌ Channel principal introuvable: {self.config.main_channel_id}")
                return
            
            # Channels additionnels
            if self.config.alerts_channel_id:
                self.alerts_channel = self.client.get_channel(self.config.alerts_channel_id)
            
            if self.config.trades_channel_id:
                self.trades_channel = self.client.get_channel(self.config.trades_channel_id)
            
            if self.config.errors_channel_id:
                self.errors_channel = self.client.get_channel(self.config.errors_channel_id)
            
            self.is_ready = True
            self.reconnect_attempts = 0
            
            # Envoyer message de démarrage
            await self._send_startup_message()
            
            # Traiter la queue de messages
            await self._process_message_queue()
        
        @self.client.event
        async def on_disconnect():
            """Appelé lors d'une déconnexion"""
            logger.warning("⚠️ Discord déconnecté")
            self.is_ready = False
            self.stats['reconnections'] += 1
        
        @self.client.event
        async def on_error(event, *args, **kwargs):
            """Gestion des erreurs Discord"""
            logger.error(f"❌ Erreur Discord dans {event}: {args}, {kwargs}")
    
    async def start(self):
        """Démarre le bot Discord avec reconnexion automatique"""
        while self.config.auto_reconnect and self.reconnect_attempts < self.config.max_reconnect_attempts:
            try:
                logger.info(f"🔄 Connexion Discord... (tentative {self.reconnect_attempts + 1})")
                await self.client.start(self.config.bot_token)
                
            except discord.LoginFailure:
                logger.error("❌ Token Discord invalide - ARRÊT")
                raise
                
            except Exception as e:
                self.reconnect_attempts += 1
                logger.error(f"❌ Erreur connexion Discord: {e}")
                
                if self.reconnect_attempts >= self.config.max_reconnect_attempts:
                    logger.error("❌ Max tentatives atteint - Discord OBLIGATOIRE!")
                    raise RuntimeError("Impossible de connecter Discord (OBLIGATOIRE)")
                
                await asyncio.sleep(self.config.reconnect_delay_seconds)
    
    async def stop(self):
        """Arrête le bot Discord proprement"""
        if self.is_ready:
            await self._send_shutdown_message()
        
        await self.client.close()
        logger.info("✅ Discord déconnecté proprement")
    
    async def send_notification(self,
                              message: str,
                              notification_type: NotificationType = NotificationType.INFO,
                              channel: Optional[str] = None,
                              embed_data: Optional[Dict[str, Any]] = None,
                              urgent: bool = False) -> bool:
        """
        Envoie une notification Discord
        
        Args:
            message: Message à envoyer
            notification_type: Type de notification
            channel: Channel spécifique ('main', 'alerts', 'trades', 'errors')
            embed_data: Données pour créer un embed riche
            urgent: Si True, bypass rate limiting
            
        Returns:
            True si envoyé avec succès
        """
        # Préparer le message
        notification_data = {
            'message': message,
            'type': notification_type,
            'channel': channel,
            'embed_data': embed_data,
            'urgent': urgent,
            'timestamp': datetime.now(),
            'attempts': 0
        }
        
        # Si pas prêt, ajouter à la queue
        if not self.is_ready:
            self.message_queue.append(notification_data)
            logger.warning(f"Discord pas prêt - Message en queue: {message[:50]}...")
            return False
        
        # Envoyer directement
        return await self._send_notification(notification_data)
    
    async def _send_notification(self, notification_data: Dict[str, Any]) -> bool:
        """Envoie réellement la notification"""
        try:
            # Sélectionner le channel
            target_channel = self._get_target_channel(
                notification_data.get('channel'),
                notification_data['type']
            )
            
            if not target_channel:
                logger.error("Aucun channel Discord disponible")
                return False
            
            # Rate limiting (sauf urgent)
            if not notification_data.get('urgent', False):
                await self._apply_rate_limit()
            
            # Créer le message
            if embed_data := notification_data.get('embed_data'):
                embed = self._create_embed(
                    notification_data['message'],
                    notification_data['type'],
                    embed_data
                )
                await target_channel.send(embed=embed)
            else:
                # Message simple avec emoji
                emoji = notification_data['type'].value
                formatted_message = f"{emoji} **{notification_data['message']}**"
                
                # Truncate si trop long
                if len(formatted_message) > self.config.max_message_length:
                    formatted_message = formatted_message[:self.config.max_message_length-3] + "..."
                
                await target_channel.send(formatted_message)
            
            self.stats['messages_sent'] += 1
            return True
            
        except discord.HTTPException as e:
            logger.error(f"Erreur HTTP Discord: {e}")
            self.stats['messages_failed'] += 1
            
            # Retry logic
            notification_data['attempts'] += 1
            if notification_data['attempts'] < 3:
                self.message_queue.append(notification_data)
            
            return False
            
        except Exception as e:
            logger.error(f"Erreur envoi Discord: {e}")
            self.stats['messages_failed'] += 1
            return False
    
    def _get_target_channel(self, channel_name: Optional[str], 
                          notification_type: NotificationType):
        """Détermine le channel cible"""
        # Channel spécifique demandé
        if channel_name:
            channel_map = {
                'main': self.main_channel,
                'alerts': self.alerts_channel or self.main_channel,
                'trades': self.trades_channel or self.main_channel,
                'errors': self.errors_channel or self.main_channel
            }
            return channel_map.get(channel_name, self.main_channel)
        
        # Selon le type de notification
        if notification_type in [NotificationType.ERROR, NotificationType.ALERT]:
            return self.errors_channel or self.alerts_channel or self.main_channel
        elif notification_type in [NotificationType.TRADE_OPEN, NotificationType.TRADE_CLOSE]:
            return self.trades_channel or self.main_channel
        elif notification_type == NotificationType.WARNING:
            return self.alerts_channel or self.main_channel
        else:
            return self.main_channel
    
    async def _apply_rate_limit(self):
        """Applique le rate limiting"""
        current_time = time.time()
        time_since_last = current_time - self.last_message_time
        
        if time_since_last < (1.0 / self.config.rate_limit_messages):
            sleep_time = (1.0 / self.config.rate_limit_messages) - time_since_last
            await asyncio.sleep(sleep_time)
        
        self.last_message_time = time.time()
    
    def _create_embed(self, title: str, notification_type: NotificationType,
                     embed_data: Dict[str, Any]) -> discord.Embed:
        """Crée un embed Discord riche"""
        # Couleur selon le type
        color_map = {
            NotificationType.INFO: self.config.embed_color_info,
            NotificationType.SUCCESS: self.config.embed_color_success,
            NotificationType.WARNING: self.config.embed_color_warning,
            NotificationType.ERROR: self.config.embed_color_error,
            NotificationType.TRADE_OPEN: self.config.embed_color_info,
            NotificationType.TRADE_CLOSE: self.config.embed_color_success,
            NotificationType.ALERT: self.config.embed_color_error,
            NotificationType.PERFORMANCE: self.config.embed_color_info,
            NotificationType.SYSTEM: self.config.embed_color_warning
        }
        
        embed = discord.Embed(
            title=f"{notification_type.value} {title}",
            color=color_map.get(notification_type, self.config.embed_color_info),
            timestamp=datetime.now()
        )
        
        # Description
        if description := embed_data.get('description'):
            embed.description = description
        
        # Fields
        if fields := embed_data.get('fields'):
            for field in fields[:self.config.max_embed_fields]:
                embed.add_field(
                    name=field.get('name', 'Info'),
                    value=field.get('value', 'N/A'),
                    inline=field.get('inline', True)
                )
        
        # Footer
        if footer := embed_data.get('footer'):
            embed.set_footer(text=footer)
        else:
            embed.set_footer(text=f"MIA Trading Bot • {datetime.now().strftime('%H:%M:%S')}")
        
        # Thumbnail
        if thumbnail := embed_data.get('thumbnail'):
            embed.set_thumbnail(url=thumbnail)
        
        return embed
    
    async def _send_startup_message(self):
        """Envoie un message de démarrage"""
        embed_data = {
            'description': "Bot MIA_IA_SYSTEM démarré avec succès",
            'fields': [
                {'name': '📊 Mode', 'value': os.environ.get('TRADING_MODE', 'Unknown'), 'inline': True},
                {'name': '🔧 Version', 'value': '3.0.0', 'inline': True},
                {'name': '📅 Heure', 'value': datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'inline': True}
            ],
            'footer': 'Discord notifications opérationnelles'
        }
        
        await self.send_notification(
            "🚀 MIA Trading Bot DÉMARRÉ",
            NotificationType.SUCCESS,
            embed_data=embed_data
        )
    
    async def _send_shutdown_message(self):
        """Envoie un message d'arrêt"""
        uptime = datetime.now() - self.stats['uptime_start']
        
        embed_data = {
            'description': "Bot MIA_IA_SYSTEM arrêté",
            'fields': [
                {'name': '⏱️ Uptime', 'value': str(uptime).split('.')[0], 'inline': True},
                {'name': '📨 Messages', 'value': str(self.stats['messages_sent']), 'inline': True},
                {'name': '❌ Erreurs', 'value': str(self.stats['messages_failed']), 'inline': True}
            ]
        }
        
        await self.send_notification(
            "🛑 MIA Trading Bot ARRÊTÉ",
            NotificationType.WARNING,
            embed_data=embed_data,
            urgent=True
        )
    
    async def _process_message_queue(self):
        """Traite la queue de messages en attente"""
        if not self.message_queue:
            return
        
        logger.info(f"📨 Traitement de {len(self.message_queue)} messages en queue")
        
        messages_to_retry = []
        
        for notification_data in self.message_queue:
            success = await self._send_notification(notification_data)
            if not success and notification_data['attempts'] < 3:
                messages_to_retry.append(notification_data)
        
        self.message_queue = messages_to_retry
    
    # === MÉTHODES SPÉCIALISÉES ===
    
    async def send_trade_open(self, trade_data: Dict[str, Any]):
        """Notification ouverture de trade"""
        embed_data = {
            'description': f"Nouveau trade ouvert sur {trade_data.get('symbol', 'ES')}",
            'fields': [
                {'name': '📊 Type', 'value': trade_data.get('direction', 'N/A'), 'inline': True},
                {'name': '💰 Prix', 'value': str(trade_data.get('price', 0)), 'inline': True},
                {'name': '📏 Quantité', 'value': str(trade_data.get('quantity', 0)), 'inline': True},
                {'name': '🎯 TP', 'value': str(trade_data.get('take_profit', 0)), 'inline': True},
                {'name': '🛑 SL', 'value': str(trade_data.get('stop_loss', 0)), 'inline': True},
                {'name': '📈 Confiance', 'value': f"{trade_data.get('confidence', 0):.1%}", 'inline': True}
            ]
        }
        
        await self.send_notification(
            f"TRADE OUVERT: {trade_data.get('symbol', 'ES')}",
            NotificationType.TRADE_OPEN,
            channel='trades',
            embed_data=embed_data
        )
    
    async def send_trade_close(self, trade_result: Dict[str, Any]):
        """Notification fermeture de trade"""
        pnl = trade_result.get('pnl', 0)
        is_winner = pnl > 0
        
        embed_data = {
            'description': f"Trade fermé sur {trade_result.get('symbol', 'ES')}",
            'fields': [
                {'name': '💵 P&L', 'value': f"${pnl:+.2f}", 'inline': True},
                {'name': '📊 Résultat', 'value': "✅ WIN" if is_winner else "❌ LOSS", 'inline': True},
                {'name': '⏱️ Durée', 'value': f"{trade_result.get('duration', 0)} min", 'inline': True},
                {'name': '📈 Entry', 'value': str(trade_result.get('entry_price', 0)), 'inline': True},
                {'name': '📉 Exit', 'value': str(trade_result.get('exit_price', 0)), 'inline': True},
                {'name': '🎯 Raison', 'value': trade_result.get('exit_reason', 'N/A'), 'inline': True}
            ]
        }
        
        notification_type = NotificationType.SUCCESS if is_winner else NotificationType.WARNING
        
        await self.send_notification(
            f"TRADE FERMÉ: {'WIN' if is_winner else 'LOSS'} ${pnl:+.2f}",
            notification_type,
            channel='trades',
            embed_data=embed_data
        )
    
    async def send_error(self, error_message: str, error_details: Optional[str] = None):
        """Notification d'erreur"""
        embed_data = {
            'description': error_message,
            'fields': []
        }
        
        if error_details:
            embed_data['fields'].append({
                'name': '📋 Détails',
                'value': error_details[:1024],  # Limite Discord
                'inline': False
            })
        
        await self.send_notification(
            "ERREUR SYSTÈME",
            NotificationType.ERROR,
            channel='errors',
            embed_data=embed_data,
            urgent=True
        )
    
    async def send_performance_update(self, performance_data: Dict[str, Any]):
        """Notification mise à jour performance"""
        embed_data = {
            'description': "Mise à jour des performances",
            'fields': [
                {'name': '📊 Trades', 'value': str(performance_data.get('total_trades', 0)), 'inline': True},
                {'name': '📈 Win Rate', 'value': f"{performance_data.get('win_rate', 0):.1%}", 'inline': True},
                {'name': '💰 P&L Total', 'value': f"${performance_data.get('total_pnl', 0):.2f}", 'inline': True},
                {'name': '📉 Max DD', 'value': f"{performance_data.get('max_drawdown', 0):.1%}", 'inline': True},
                {'name': '🎯 Sharpe', 'value': f"{performance_data.get('sharpe_ratio', 0):.2f}", 'inline': True},
                {'name': '⚡ Profit Factor', 'value': f"{performance_data.get('profit_factor', 0):.2f}", 'inline': True}
            ]
        }
        
        await self.send_notification(
            "PERFORMANCE UPDATE",
            NotificationType.PERFORMANCE,
            embed_data=embed_data
        )
    
    def get_stats(self) -> Dict[str, Any]:
        """Retourne les statistiques du notifier"""
        uptime = datetime.now() - self.stats['uptime_start']
        
        return {
            'connected': self.is_ready,
            'uptime': str(uptime).split('.')[0],
            'messages_sent': self.stats['messages_sent'],
            'messages_failed': self.stats['messages_failed'],
            'messages_queued': len(self.message_queue),
            'reconnections': self.stats['reconnections']
        }

# === FACTORY FUNCTIONS ===

def create_discord_notifier(config: Optional[DiscordConfig] = None) -> DiscordNotifier:
    """
    Crée un notifier Discord
    
    Args:
        config: Configuration optionnelle
        
    Returns:
        DiscordNotifier instance
        
    Raises:
        ImportError: Si discord.py non installé
        ValueError: Si configuration invalide
    """
    return DiscordNotifier(config)

async def test_discord_notifier():
    """Test du notifier Discord"""
    logger.debug("TEST DISCORD NOTIFIER")
    print("=" * 50)
    
    # Test configuration
    try:
        notifier = create_discord_notifier()
        logger.info("Configuration Discord OK")
    except Exception as e:
        logger.error("Erreur configuration: {e}")
        return False
    
    # Test connexion (nécessite token valide)
    if os.environ.get('DISCORD_BOT_TOKEN'):
        logger.info("🔄 Test connexion Discord...")
        # Le test réel nécessiterait une boucle async
        logger.warning("Test connexion nécessite exécution async")
    else:
        logger.warning("DISCORD_BOT_TOKEN non défini - Skip test connexion")
    
    return True

# === EXPORTS ===

__all__ = [
    'DiscordNotifier',
    'DiscordConfig',
    'NotificationType',
    'create_discord_notifier',
    'test_discord_notifier',
    'DISCORD_AVAILABLE'
]