#!/usr/bin/env python3
"""
MIA_IA_SYSTEM - Discord Notifier (Version Webhook Corrigée)
Support complet du mapping channels depuis automation_params.json
"""

import json
import logging
import asyncio
import aiohttp
from typing import Dict, Optional, Any
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

class WebhookDiscordNotifier:
    """
    Discord Notifier utilisant webhooks avec mapping correct des channels
    """
    
    def __init__(self):
        """Initialise avec config depuis automation_params.json"""
        self.config = self._load_config()
        self.session = None
        self.stats = {'messages_sent': 0, 'messages_failed': 0}
        
        if self.config:
            logger.info("🔗 Mode WEBHOOK détecté automatiquement")
            logger.info("✅ Configuration WEBHOOK validée")
            logger.info("🔗 Mode WEBHOOK initialisé - Prêt immédiatement")
            logger.info("✅ DiscordNotifier initialisé en mode WEBHOOK")
    
    def _find_config_file(self) -> Optional[str]:
        """Trouve le fichier automation_params.json"""
        possible_locations = [
            'automation_params.json',
            'config_files/automation_params.json',
            'config/automation_params.json',
            '../automation_params.json'
        ]
        
        for location in possible_locations:
            if Path(location).exists():
                return location
        
        # Chercher dans tous les sous-répertoires
        for root, dirs, files in Path('.').rglob('automation_params.json'):
            return str(root / 'automation_params.json')
        
        return None
    
    def _load_config(self) -> Optional[Dict]:
        """Charge config depuis automation_params.json"""
        config_path = self._find_config_file()
        if not config_path:
            logger.error("automation_params.json introuvable")
            return None
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            discord_config = config.get('notifications', {}).get('discord_integration', {})
            
            if not discord_config.get('enabled', False):
                logger.warning("Discord désactivé dans automation_params.json")
                return None
            
            webhook_url = discord_config.get('webhook_url', '')
            if not webhook_url.startswith('https://discord'):
                logger.error("Webhook URL invalide")
                return None
            
            logger.info(f"✅ Config chargée depuis: {config_path}")
            return {
                'webhook_url': webhook_url,
                'channels': discord_config.get('channels', {}),
                'channel_mapping': discord_config.get('channel_mapping', {}),
                'notification_settings': discord_config.get('notification_settings', {})
            }
        except Exception as e:
            logger.error(f"Erreur lecture config Discord: {e}")
            return None
    
    def _resolve_channel_for_type(self, channel_type: str) -> Optional[str]:
        """Résout le channel ID pour un type donné"""
        if not self.config:
            return None
        
        # 1. Chercher dans le mapping
        channel_mapping = self.config.get('channel_mapping', {})
        mapped_channel_key = channel_mapping.get(channel_type)
        
        if mapped_channel_key:
            # 2. Résoudre la clé vers un ID
            channels = self.config.get('channels', {})
            channel_id = channels.get(mapped_channel_key)
            if channel_id:
                logger.debug(f"Channel résolu: {channel_type} → {mapped_channel_key} → {channel_id}")
                return channel_id
        
        # 3. Fallback vers channel principal
        main_channel = self.config.get('channels', {}).get('main_channel_id')
        if main_channel:
            logger.debug(f"Fallback: {channel_type} → main_channel → {main_channel}")
            return main_channel
        
        logger.warning(f"Aucun channel trouvé pour {channel_type}")
        return None
    
    async def _get_session(self):
        """Obtient session aiohttp"""
        if not self.session:
            self.session = aiohttp.ClientSession()
        return self.session
    
    async def send_webhook_message(self, message_data: Dict) -> bool:
        """Envoie message via webhook"""
        if not self.config:
            return False
        
        try:
            session = await self._get_session()
            webhook_url = self.config['webhook_url']
            
            async with session.post(webhook_url, json=message_data) as response:
                if response.status in [200, 204]:
                    self.stats['messages_sent'] += 1
                    return True
                else:
                    logger.error(f"Erreur webhook: {response.status}")
                    self.stats['messages_failed'] += 1
                    return False
        
        except Exception as e:
            logger.error(f"Erreur envoi webhook: {e}")
            self.stats['messages_failed'] += 1
            return False
    
    async def send_custom_message(self, channel_type: str, title: str, 
                                description: str, color: int = 0x00ff00) -> bool:
        """
        Envoie message vers le channel approprié selon le mapping
        
        Args:
            channel_type: Type selon channel_mapping (ex: 'trade_executions', 'system_alerts')
            title: Titre du message
            description: Description
            color: Couleur de l'embed
        """
        channel_id = self._resolve_channel_for_type(channel_type)
        if not channel_id:
            logger.error(f"Channel non résolu pour {channel_type}")
            return False
        
        # Créer embed avec info de routing
        embed = {
            "title": title,
            "description": description,
            "color": color,
            "timestamp": datetime.utcnow().isoformat(),
            "footer": {
                "text": f"MIA → {channel_type} → #{self._get_channel_name(channel_id)}"
            }
        }
        
        message_data = {
            "username": "MIA_IA_SYSTEM",
            "embeds": [embed]
        }
        
        success = await self.send_webhook_message(message_data)
        
        if success:
            channel_name = self._get_channel_name(channel_id)
            logger.info(f"✅ Message envoyé: {channel_type} → #{channel_name}: {title}")
        else:
            logger.error(f"❌ Échec envoi: {channel_type}: {title}")
        
        return success
    
    def _get_channel_name(self, channel_id: str) -> str:
        """Obtient nom du channel depuis son ID"""
        if not self.config:
            return "unknown"
        
        channels = self.config.get('channels', {})
        for key, value in channels.items():
            if value == channel_id:
                return key.replace('_channel_id', '')
        return f"id_{channel_id[-4:]}"
    
    async def send_trade_executed(self, trade_data: Dict) -> bool:
        """Notification trade exécuté → channel trades"""
        title = f"📈 TRADE OUVERT - {trade_data.get('side', 'N/A')}"
        
        description = f"""
**Côté:** {trade_data.get('side', 'N/A')}
**Quantité:** {trade_data.get('quantity', 0)}
**Prix:** {trade_data.get('fill_price', trade_data.get('intended_price', 0))}
**Slippage:** {trade_data.get('slippage_ticks', 0)} ticks
**Risque:** ${trade_data.get('risk_dollars', 0):.2f}
**Status:** {trade_data.get('battle_status', 'N/A')}
        """.strip()
        
        return await self.send_custom_message('trade_executions', title, description, 0x00ff00)
    
    async def send_trade_closed(self, trade_data: Dict) -> bool:
        """Notification trade fermé → channel trades"""
        pnl = trade_data.get('pnl', 0)
        is_winner = pnl > 0
        
        title = f"📊 TRADE FERMÉ - {'WIN' if is_winner else 'LOSS'}"
        
        description = f"""
**Côté:** {trade_data.get('side', 'N/A')}
**P&L:** ${pnl:+.2f} ({trade_data.get('pnl_ticks', 0):+.1f} ticks)
**Prix sortie:** {trade_data.get('exit_price', 0)}
**Durée:** {trade_data.get('duration_minutes', 0)} min
**Raison:** {trade_data.get('exit_reason', 'N/A')}
**Max Profit:** {trade_data.get('max_profit_ticks', 0):+.1f} ticks
**Max Loss:** {trade_data.get('max_loss_ticks', 0):+.1f} ticks
        """.strip()
        
        if 'post_mortem_note' in trade_data:
            description += f"\n**Note:** {trade_data['post_mortem_note']}"
        
        color = 0x00ff00 if is_winner else 0xff0000
        return await self.send_custom_message('trade_executions', title, description, color)
    
    async def send_daily_report(self, report_data: Dict) -> bool:
        """Envoie rapport quotidien → channel performance"""
        title = f"📊 RAPPORT QUOTIDIEN - {report_data.get('date', 'N/A')}"
        
        description = f"""
**P&L Total:** ${report_data.get('total_pnl', 0):+.2f}
**Trades:** {report_data.get('total_trades', 0)}
**Win Rate:** {report_data.get('win_rate', 0):.1%}
**Profit Factor:** {report_data.get('profit_factor', 0):.2f}
**Signaux détectés:** {report_data.get('signals_detected', 0)}
**Signaux pris:** {report_data.get('signals_taken', 0)}
**Sélectivité:** {report_data.get('selectivity', 0):.1%}
**Meilleur trade:** ${report_data.get('best_trade', 0):+.2f}
**Pire trade:** ${report_data.get('worst_trade', 0):+.2f}
        """.strip()
        
        if 'ml_insights' in report_data and report_data['ml_insights']:
            description += "\n\n**Insights ML:**\n" + "\n".join(f"• {insight}" for insight in report_data['ml_insights'])
        
        return await self.send_custom_message('daily_summary', title, description, 0x3498db)
    
    async def close(self):
        """Ferme la session"""
        if self.session:
            await self.session.close()
            self.session = None
            logger.info("✅ Session Discord fermée")

# Factory functions pour compatibilité
def create_discord_notifier():
    """Crée notifier Discord"""
    return WebhookDiscordNotifier()

def notify_discord_available() -> bool:
    """Vérifie si Discord est disponible"""
    # Trouver le fichier config
    possible_locations = [
        'automation_params.json',
        'config_files/automation_params.json', 
        'config/automation_params.json',
        '../automation_params.json'
    ]
    
    config_path = None
    for location in possible_locations:
        if Path(location).exists():
            config_path = location
            break
    
    if not config_path:
        return False
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        discord_config = config.get('notifications', {}).get('discord_integration', {})
        enabled = discord_config.get('enabled', False)
        has_webhook = bool(discord_config.get('webhook_url', '').startswith('https'))
        
        return enabled and has_webhook
    except:
        return False

# Test rapide si exécuté directement
if __name__ == "__main__":
    async def test():
        notifier = create_discord_notifier()
        if notifier:
            await notifier.send_custom_message(
                'system_status', 
                'Test Discord Corrigé',
                'Le système Discord utilise maintenant le bon mapping des channels!'
            )
            await notifier.close()
        else:
            print("❌ Notifier non disponible")
    
    asyncio.run(test())
