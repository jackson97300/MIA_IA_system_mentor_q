"""
Configuration principale - Importe depuis config/
"""

# Import depuis les vrais fichiers de config
try:
    from config.trading_config import *
except ImportError:
    def get_trading_config():
        return {"mock": True}

try:
    from config.automation_config import *
except ImportError:
    def get_automation_config():
        return {"mock": True}
