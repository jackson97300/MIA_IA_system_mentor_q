"""
MIA_IA_SYSTEM - Discord Notifier
Notifications Discord OBLIGATOIRES pour suivi du bot
Version: Production Ready - HYBRIDE WEBHOOK + BOT

Discord est OBLIGATOIRE pour :
- Notifications trades en temps réel
- Alertes erreurs critiques
- Rapports de performance
- Suivi à distance sur mobile

MODES SUPPORTÉS:
- WEBHOOK MODE: Utilise webhook URL (RECOMMANDÉ - Plus simple)
- BOT MODE: Utilise bot token (Avancé - Plus de fonctionnalités)
"""

import os
import asyncio
import requests
import json
import time
from core.logger import get_logger
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from enum import Enum
from datetime import datetime
from pathlib import Path

# Discord.py (optionnel pour bot mode)
try:
    import discord
    from discord.ext import commands
    DISCORD_BOT_AVAILABLE = True
except ImportError:
    DISCORD_BOT_AVAILABLE = False
    discord = None
    # Au lieu de raise, on log juste un warning
    import logging
    logging.warning(
        "discord.py n'est pas installé - Mode Bot Discord non disponible\n"
        "Mode Webhook reste fonctionnel. Pour bot mode: pip install discord.py>=2.3.0"
    )

logger = get_logger(__name__)

# === FONCTIONS UTILITAIRES ===

def notify_discord_available() -> bool:
    """
    Vérifie si Discord (discord.py) est installé et disponible.
    
    Returns:
        True si discord.py est installé, False sinon
    """
    return DISCORD_BOT_AVAILABLE

# === CONFIGURATION ===

class NotificationType(Enum):
    """Types de notifications Discord"""
    INFO = "ℹ️"
    SUCCESS = "[OK]"
    WARNING = "[WARN]"
    ERROR = "[ERROR]"
    TRADE_OPEN = "[UP]"
    TRADE_CLOSE = "[STATS]"
    ALERT = "[ALERT]"
    PERFORMANCE = "[STATS]"
    SYSTEM = "[CONFIG]"

class DiscordMode(Enum):
    """Modes de fonctionnement Discord"""
    WEBHOOK = "webhook"
    BOT = "bot"
    AUTO = "auto"  # Détection automatique

@dataclass
class DiscordConfig:
    """Configuration Discord hybride"""
    # Mode de fonctionnement
    mode: DiscordMode = DiscordMode.AUTO
    
    # Configuration Webhook (RECOMMANDÉ)
    webhook_url: Optional[str] = None
    webhook_username: str = "MIA_IA_SYSTEM"
    
    # Configuration Bot (optionnel)
    bot_token: Optional[str] = None

    # Channels IDs
    main_channel_id: Optional[int] = None
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
    webhook_timeout: int = 10

    # Reconnexion (bot mode uniquement)
    auto_reconnect: bool = True
    max_reconnect_attempts: int = 10
    reconnect_delay_seconds: int = 30

# === DISCORD NOTIFIER HYBRIDE ===

class DiscordNotifier:
    """
    Notificateur Discord Hybride pour MIA_IA_SYSTEM

    Supporte DEUX modes :
    1. WEBHOOK MODE - Simple, fiable, recommandé
    2. BOT MODE - Avancé, plus de fonctionnalités

    Détection automatique selon configuration disponible.
    """

    def __init__(self, config: Optional[DiscordConfig] = None):
        """
        Initialise le notifier Discord

        Args:
            config: Configuration Discord ou charge depuis env/automation_params.json
        """
        # Configuration
        self.config = config or self._load_config_from_multiple_sources()
        self._determine_mode()
        self._validate_config()

        # Variables communes
        self.is_ready = False
        self.message_queue: List[Dict[str, Any]] = []
        self.last_message_time = 0
        
        # Stats
        self.stats = {
            'messages_sent': 0,
            'messages_failed': 0,
            'reconnections': 0,
            'uptime_start': datetime.now(),
            'mode': self.config.mode.value
        }

        # Initialisation selon le mode
        if self.config.mode == DiscordMode.WEBHOOK:
            self._init_webhook_mode()
        elif self.config.mode == DiscordMode.BOT:
            self._init_bot_mode()
        else:
            raise ValueError(f"Mode Discord non supporté: {self.config.mode}")

        logger.info(f"✅ DiscordNotifier initialisé en mode {self.config.mode.value.upper()}")

    def _load_config_from_multiple_sources(self) -> DiscordConfig:
        """Charge configuration depuis plusieurs sources"""
        config = DiscordConfig()
        
        # 1. Essayer automation_params.json (PRIORITÉ)
        automation_config = self._load_from_automation_params()
        if automation_config:
            if automation_config.get('webhook_url'):
                config.webhook_url = automation_config['webhook_url']
            if automation_config.get('bot_token'):
                config.bot_token = automation_config['bot_token']
            if automation_config.get('channels'):
                channels = automation_config['channels']
                config.main_channel_id = self._safe_int(channels.get('main_channel_id'))
                config.alerts_channel_id = self._safe_int(channels.get('alertes_channel_id'))
                config.trades_channel_id = self._safe_int(channels.get('trades_channel_id'))
                config.errors_channel_id = self._safe_int(channels.get('errors_channel_id'))

        # 2. Variables environnement (FALLBACK)
        if not config.webhook_url:
            config.webhook_url = os.environ.get('DISCORD_WEBHOOK_URL')
        if not config.bot_token:
            config.bot_token = os.environ.get('DISCORD_BOT_TOKEN')
        if not config.main_channel_id:
            config.main_channel_id = self._safe_int(os.environ.get('DISCORD_MAIN_CHANNEL_ID'))

        return config
    
    def _load_from_automation_params(self) -> Optional[Dict]:
        """Charge depuis automation_params.json"""
        config_paths = [
            'automation_params.json',
            'config_files/automation_params.json',
            'config/automation_params.json'
        ]
        
        for path_str in config_paths:
            config_path = Path(path_str)
            if config_path.exists():
                try:
                    with open(config_path, 'r', encoding='utf-8') as f:
                        config_data = json.load(f)
                    
                    discord_config = config_data.get('notifications', {}).get('discord_integration', {})
                    
                    if discord_config.get('enabled', False):
                        return discord_config
                        
                except Exception as e:
                    logger.warning(f"Erreur lecture {config_path}: {e}")
                    continue
        
        return None
    
    def _safe_int(self, value) -> Optional[int]:
        """Conversion sécurisée en int"""
        if value is None:
            return None
        try:
            return int(value)
        except (ValueError, TypeError):
            return None

    def _determine_mode(self):
        """Détermine le mode de fonctionnement"""
        if self.config.mode == DiscordMode.AUTO:
            # Auto-détection
            if self.config.webhook_url and self.config.webhook_url.startswith('https://discord'):
                self.config.mode = DiscordMode.WEBHOOK
                logger.info("🔗 Mode WEBHOOK détecté automatiquement")
            elif self.config.bot_token and DISCORD_BOT_AVAILABLE:
                self.config.mode = DiscordMode.BOT
                logger.info("🤖 Mode BOT détecté automatiquement")
            elif self.config.webhook_url:
                self.config.mode = DiscordMode.WEBHOOK
                logger.warning("⚠️ Webhook URL présent mais invalide, tentative en mode webhook")
            else:
                raise ValueError(
                    "Aucune configuration Discord valide trouvée!\n"
                    "Configurer soit:\n"
                    "- WEBHOOK: webhook_url dans automation_params.json\n"
                    "- BOT: DISCORD_BOT_TOKEN + DISCORD_MAIN_CHANNEL_ID"
                )

    def _validate_config(self):
        """Valide la configuration selon le mode"""
        if self.config.mode == DiscordMode.WEBHOOK:
            if not self.config.webhook_url:
                raise ValueError("webhook_url requis pour mode WEBHOOK")
            if not self.config.webhook_url.startswith('https://discord'):
                raise ValueError(f"webhook_url invalide: {self.config.webhook_url[:50]}...")
                
        elif self.config.mode == DiscordMode.BOT:
            if not DISCORD_BOT_AVAILABLE:
                raise ImportError(
                    "discord.py non installé - Mode BOT non disponible\n"
                    "Installer avec: pip install discord.py>=2.3.0\n"
                    "Ou utiliser mode WEBHOOK"
                )
            if not self.config.bot_token:
                raise ValueError("bot_token requis pour mode BOT")
            if not self.config.main_channel_id:
                raise ValueError("main_channel_id requis pour mode BOT")

        logger.info(f"✅ Configuration {self.config.mode.value.upper()} validée")

    def _init_webhook_mode(self):
        """Initialisation mode webhook"""
        self.is_ready = True  # Webhook toujours prêt
        logger.info("🔗 Mode WEBHOOK initialisé - Prêt immédiatement")

    def _init_bot_mode(self):
        """Initialisation mode bot"""
        if not DISCORD_BOT_AVAILABLE:
            raise ImportError("discord.py requis pour mode BOT")
            
        # Discord client
        intents = discord.Intents.default()
        intents.message_content = True
        self.client = discord.Client(intents=intents)

        # Channels
        self.main_channel = None
        self.alerts_channel = None
        self.trades_channel = None
        self.errors_channel = None

        # Setup event handlers
        self._setup_bot_event_handlers()
        logger.info("🤖 Mode BOT initialisé - Connexion requise")

    def _setup_bot_event_handlers(self):
        """Configure les event handlers Discord (mode bot uniquement)"""
        if self.config.mode != DiscordMode.BOT or not hasattr(self, 'client'):
            return

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
            logger.warning("⚠️ Discord BOT déconnecté")
            self.is_ready = False
            self.stats['reconnections'] += 1

        @self.client.event
        async def on_error(event, *args, **kwargs):
            """Gestion des erreurs Discord"""
            logger.error(f"❌ Erreur Discord dans {event}: {args}, {kwargs}")

    # === MÉTHODES PUBLIQUES ===

    async def start(self):
        """Démarre le notifier selon le mode"""
        if self.config.mode == DiscordMode.WEBHOOK:
            # Webhook mode - Test de connectivité
            await self._test_webhook()
            logger.info("✅ Mode WEBHOOK opérationnel")
            
        elif self.config.mode == DiscordMode.BOT:
            # Bot mode - Connexion avec reconnexion automatique
            reconnect_attempts = 0
            while self.config.auto_reconnect and reconnect_attempts < self.config.max_reconnect_attempts:
                try:
                    logger.info(f"🔄 Connexion Discord BOT... (tentative {reconnect_attempts + 1})")
                    await self.client.start(self.config.bot_token)

                except discord.LoginFailure:
                    logger.error("❌ Token Discord invalide - ARRÊT")
                    raise

                except Exception as e:
                    reconnect_attempts += 1
                    logger.error(f"❌ Erreur connexion Discord: {e}")

                    if reconnect_attempts >= self.config.max_reconnect_attempts:
                        logger.error("❌ Max tentatives atteint")
                        raise RuntimeError("Impossible de connecter Discord BOT")

                    await asyncio.sleep(self.config.reconnect_delay_seconds)

    async def stop(self):
        """Arrête le notifier proprement"""
        if self.config.mode == DiscordMode.BOT and hasattr(self, 'client'):
            if self.is_ready:
                await self._send_shutdown_message()
            await self.client.close()
            
        logger.info("✅ Discord Notifier arrêté proprement")

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

        # Si pas prêt (bot mode), ajouter à la queue
        if not self.is_ready and self.config.mode == DiscordMode.BOT:
            self.message_queue.append(notification_data)
            logger.warning(f"Discord BOT pas prêt - Message en queue: {message[:50]}...")
            return False

        # Envoyer selon le mode
        if self.config.mode == DiscordMode.WEBHOOK:
            return await self._send_webhook_notification(notification_data)
        else:
            return await self._send_bot_notification(notification_data)

    # === MÉTHODES WEBHOOK MODE ===

    async def _test_webhook(self):
        """Test de connectivité webhook"""
        try:
            test_payload = {
                "username": self.config.webhook_username,
                "content": "🔗 Test connexion webhook Discord"
            }
            
            response = requests.post(
                self.config.webhook_url,
                json=test_payload,
                timeout=self.config.webhook_timeout
            )
            
            if response.status_code == 204:
                logger.info("✅ Test webhook Discord réussi")
            else:
                logger.warning(f"⚠️ Test webhook retourné: {response.status_code}")
                
        except Exception as e:
            logger.error(f"❌ Test webhook échoué: {e}")

    async def _send_webhook_notification(self, notification_data: Dict[str, Any]) -> bool:
        """Envoie notification via webhook"""
        try:
            # Rate limiting (sauf urgent)
            if not notification_data.get('urgent', False):
                await self._apply_rate_limit()

            # Construire payload
            payload = {
                "username": self.config.webhook_username
            }

            # Embed ou message simple
            if embed_data := notification_data.get('embed_data'):
                embed = self._create_webhook_embed(
                    notification_data['message'],
                    notification_data['type'],
                    embed_data
                )
                payload["embeds"] = [embed]
            else:
                # Message simple avec emoji
                emoji = notification_data['type'].value
                formatted_message = f"{emoji} **{notification_data['message']}**"
                
                # Truncate si trop long
                if len(formatted_message) > self.config.max_message_length:
                    formatted_message = formatted_message[:self.config.max_message_length-3] + "..."
                
                payload["content"] = formatted_message

            # Envoyer via webhook
            response = requests.post(
                self.config.webhook_url,
                json=payload,
                timeout=self.config.webhook_timeout
            )

            if response.status_code == 204:
                self.stats['messages_sent'] += 1
                return True
            else:
                logger.error(f"❌ Webhook error: {response.status_code} - {response.text}")
                self.stats['messages_failed'] += 1
                return False

        except Exception as e:
            logger.error(f"❌ Erreur envoi webhook: {e}")
            self.stats['messages_failed'] += 1
            return False

    def _create_webhook_embed(self, title: str, notification_type: NotificationType,
                              embed_data: Dict[str, Any]) -> Dict[str, Any]:
        """Crée un embed pour webhook"""
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

        embed = {
            "title": f"{notification_type.value} {title}",
            "color": color_map.get(notification_type, self.config.embed_color_info),
            "timestamp": datetime.now().isoformat()
        }

        # Description
        if description := embed_data.get('description'):
            embed["description"] = description

        # Fields
        if fields := embed_data.get('fields'):
            embed["fields"] = []
            for field in fields[:self.config.max_embed_fields]:
                embed["fields"].append({
                    "name": field.get('name', 'Info'),
                    "value": field.get('value', 'N/A'),
                    "inline": field.get('inline', True)
                })

        # Footer
        if footer := embed_data.get('footer'):
            embed["footer"] = {"text": footer}
        else:
            embed["footer"] = {"text": f"MIA Trading Bot • {datetime.now().strftime('%H:%M:%S')}"}

        # Thumbnail
        if thumbnail := embed_data.get('thumbnail'):
            embed["thumbnail"] = {"url": thumbnail}

        return embed

    # === MÉTHODES BOT MODE ===

    async def _send_bot_notification(self, notification_data: Dict[str, Any]) -> bool:
        """Envoie notification via bot Discord"""
        if self.config.mode != DiscordMode.BOT or not hasattr(self, 'client'):
            return False

        try:
            # Sélectionner le channel
            target_channel = self._get_target_channel(
                notification_data.get('channel'),
                notification_data['type']
            )

            if not target_channel:
                logger.error("❌ Aucun channel Discord disponible")
                return False

            # Rate limiting (sauf urgent)
            if not notification_data.get('urgent', False):
                await self._apply_rate_limit()

            # Créer le message
            if embed_data := notification_data.get('embed_data'):
                embed = self._create_bot_embed(
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
            logger.error(f"❌ Erreur HTTP Discord: {e}")
            self.stats['messages_failed'] += 1

            # Retry logic
            notification_data['attempts'] += 1
            if notification_data['attempts'] < 3:
                self.message_queue.append(notification_data)

            return False

        except Exception as e:
            logger.error(f"❌ Erreur envoi Discord BOT: {e}")
            self.stats['messages_failed'] += 1
            return False

    def _get_target_channel(self, channel_name: Optional[str], notification_type: NotificationType):
        """Détermine le channel cible (bot mode uniquement)"""
        if self.config.mode != DiscordMode.BOT:
            return None

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

    def _create_bot_embed(self, title: str, notification_type: NotificationType,
                          embed_data: Dict[str, Any]):
        """Crée un embed Discord pour bot mode"""
        if not DISCORD_BOT_AVAILABLE:
            return None

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

    # === MÉTHODES COMMUNES ===

    async def _apply_rate_limit(self):
        """Applique le rate limiting"""
        current_time = time.time()
        time_since_last = current_time - self.last_message_time

        if time_since_last < (1.0 / self.config.rate_limit_messages):
            sleep_time = (1.0 / self.config.rate_limit_messages) - time_since_last
            await asyncio.sleep(sleep_time)

        self.last_message_time = time.time()

    async def _send_startup_message(self):
        """Envoie un message de démarrage"""
        embed_data = {
            'description': "Bot MIA_IA_SYSTEM démarré avec succès",
            'fields': [
                {'name': '📊 Mode Discord', 'value': self.config.mode.value.upper(), 'inline': True},
                {'name': '🔧 Mode Trading', 'value': os.environ.get('TRADING_MODE', 'Unknown'), 'inline': True},
                {'name': '📋 Version', 'value': '3.2.2', 'inline': True},
                {'name': '🕐 Heure', 'value': datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'inline': False}
            ],
            'footer': f'Discord {self.config.mode.value} notifications opérationnelles'
        }

        await self.send_notification(
            "MIA Trading Bot DÉMARRÉ",
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
            "MIA Trading Bot ARRÊTÉ",
            NotificationType.WARNING,
            embed_data=embed_data,
            urgent=True
        )

    async def _process_message_queue(self):
        """Traite la queue de messages en attente (bot mode uniquement)"""
        if not self.message_queue or self.config.mode != DiscordMode.BOT:
            return

        logger.info(f"📨 Traitement de {len(self.message_queue)} messages en queue")

        messages_to_retry = []

        for notification_data in self.message_queue:
            success = await self._send_bot_notification(notification_data)
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
            'mode': self.config.mode.value,
            'connected': self.is_ready,
            'uptime': str(uptime).split('.')[0],
            'messages_sent': self.stats['messages_sent'],
            'messages_failed': self.stats['messages_failed'],
            'messages_queued': len(self.message_queue),
            'reconnections': self.stats['reconnections']
        }

# === FACTORY FUNCTIONS ===

def create_discord_notifier(config: Optional[DiscordConfig] = None) -> Optional[DiscordNotifier]:
    """
    Crée un notifier Discord si possible

    Args:
        config: Configuration optionnelle

    Returns:
        DiscordNotifier instance ou None si Discord non disponible

    Raises:
        ValueError: Si configuration invalide
    """
    try:
        return DiscordNotifier(config)
    except Exception as e:
        logger.error(f"Erreur création DiscordNotifier: {e}")
        return None

async def test_discord_notifier():
    """Test du notifier Discord"""
    logger.info("🧪 TEST DISCORD NOTIFIER")
    print("=" * 50)

    # Test configuration
    try:
        notifier = create_discord_notifier()
        if notifier:
            logger.info("✅ Configuration Discord OK")
            logger.info(f"Mode détecté: {notifier.config.mode.value.upper()}")
        else:
            logger.warning("❌ Discord notifier non créé")
            return False
    except Exception as e:
        logger.error(f"❌ Erreur configuration: {e}")
        return False

    # Test selon le mode
    if notifier.config.mode == DiscordMode.WEBHOOK:
        logger.info("🔗 Test mode WEBHOOK...")
        await notifier._test_webhook()
    elif notifier.config.mode == DiscordMode.BOT:
        logger.info("🤖 Mode BOT détecté - connexion requise pour test complet")

    return True

# === EXPORTS ===

__all__ = [
    'DiscordNotifier',
    'DiscordConfig',
    'DiscordMode',
    'NotificationType',
    'create_discord_notifier',
    'test_discord_notifier',
    'DISCORD_BOT_AVAILABLE',
    'notify_discord_available'
]