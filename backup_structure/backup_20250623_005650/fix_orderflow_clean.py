#!/usr/bin/env python3
"""
MIA_IA_SYSTEM - Fix OrderFlow Simple
Correction simple et propre du problème net_delta
"""

import shutil
from pathlib import Path
import logging

# Configure logging
logger = logging.getLogger(__name__)


def fix_orderflow_cleanly():
    """Correction propre d'OrderFlowData sans conflit property/parameter"""
    
    logger.info("🔧 FIX PROPRE: OrderFlowData net_delta")
    print("="*45)
    
    base_types_path = Path("core/base_types.py")
    
    if not base_types_path.exists():
        logger.error("core/base_types.py non trouvé")
        return False
    
    # Backup
    backup_path = Path("core/base_types.py.backup_clean")
    shutil.copy2(base_types_path, backup_path)
    logger.info("Backup créé: {backup_path}")
    
    # Lire contenu
    with open(base_types_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Stratégie simple : Remplacer toute la classe OrderFlowData
    orderflow_start = content.find('@dataclass\nclass OrderFlowData:')
    if orderflow_start == -1:
        orderflow_start = content.find('class OrderFlowData:')
    
    if orderflow_start == -1:
        logger.error("Classe OrderFlowData non trouvée")
        return False
    
    # Trouver la fin de la classe (prochaine classe ou fin de fichier)
    content_after_class = content[orderflow_start:]
    next_class_pos = content_after_class.find('\n@dataclass\nclass ')
    if next_class_pos == -1:
        next_class_pos = content_after_class.find('\nclass ')
        if next_class_pos == -1:
            next_class_pos = len(content_after_class)
    
    orderflow_end = orderflow_start + next_class_pos
    
    # Nouvelle classe OrderFlowData propre
    new_orderflow_class = '''@dataclass
class OrderFlowData:
    """Données order flow - VERSION SIMPLE SANS CONFLIT"""
    timestamp: pd.Timestamp
    symbol: str
    cumulative_delta: float
    bid_volume: int
    ask_volume: int
    aggressive_buys: int
    aggressive_sells: int
    
    # Champs optionnels - SOLUTION SIMPLE
    net_delta: Optional[float] = None  # Delta net fourni directement
    large_trades: List[Dict[str, Any]] = field(default_factory=list)
    absorption_score: float = 0.0
    imbalance_ratio: float = 0.0
    
    def __post_init__(self):
        """Calculs post-init"""
        total_volume = self.bid_volume + self.ask_volume
        if total_volume > 0:
            self.imbalance_ratio = abs(self.bid_volume - self.ask_volume) / total_volume
        
        # Si net_delta pas fourni, le calculer
        if self.net_delta is None:
            self.net_delta = self.ask_volume - self.bid_volume
    
    @property
    def total_volume(self) -> int:
        """Volume total"""
        return self.bid_volume + self.ask_volume
    
    @property
    def aggressor_ratio(self) -> float:
        """Ratio aggressive buyers vs sellers"""
        total_aggressive = self.aggressive_buys + self.aggressive_sells
        if total_aggressive == 0:
            return 0.0
        return self.aggressive_buys / total_aggressive
    
    def get_net_delta(self) -> float:
        """Méthode pour obtenir net_delta (compatibilité)"""
        return self.net_delta if self.net_delta is not None else (self.ask_volume - self.bid_volume)

'''
    
    # Remplacer la classe
    new_content = content[:orderflow_start] + new_orderflow_class + content[orderflow_end:]
    
    # Écrire le fichier modifié
    with open(base_types_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    logger.info("OrderFlowData corrigé - net_delta maintenant un champ simple")
    return True

def test_orderflow_fix():
    """Test de la correction OrderFlow"""
    
    logger.info("\n🔍 TEST ORDERFLOW CORRIGÉ")
    print("="*35)
    
    try:
        # Nettoyer cache
        import sys
        modules_to_clean = [k for k in sys.modules.keys() if 'core.base_types' in k or 'base_types' in k]
        for mod in modules_to_clean:
            del sys.modules[mod]
        logger.info("🧹 Cache nettoyé")
        
        # Test import
        from core.base_types import OrderFlowData, MarketData
        import pandas as pd
        
        # Test 1: OrderFlowData SANS net_delta (calcul automatique)
        order_flow1 = OrderFlowData(
            timestamp=pd.Timestamp.now(),
            symbol="ES",
            cumulative_delta=15.0,
            bid_volume=800,
            ask_volume=1200,  # net_delta sera 1200-800=400
            aggressive_buys=45,
            aggressive_sells=20
        )
        logger.info("Test 1 - net_delta calculé: {order_flow1.net_delta}")
        
        # Test 2: OrderFlowData AVEC net_delta fourni
        order_flow2 = OrderFlowData(
            timestamp=pd.Timestamp.now(),
            symbol="ES",
            cumulative_delta=15.0,
            bid_volume=800,
            ask_volume=1200,
            aggressive_buys=45,
            aggressive_sells=20,
            net_delta=150.0  # ← VALEUR FOURNIE
        )
        logger.info("Test 2 - net_delta fourni: {order_flow2.net_delta}")
        
        # Test 3: Méthode get_net_delta() pour compatibilité
        net_delta_value = order_flow2.get_net_delta()
        logger.info("Test 3 - get_net_delta(): {net_delta_value}")
        
        # Test 4: Battle Navale style (comme dans le test original)
        test_order_flow = OrderFlowData(
            timestamp=pd.Timestamp.now(),
            symbol="ES",
            cumulative_delta=15.0,
            bid_volume=800,
            ask_volume=1200,
            aggressive_buys=45,
            aggressive_sells=20,
            net_delta=150.0  # Le test original
        )
        logger.info("Test 4 - Style Battle Navale: {test_order_flow.net_delta}")
        
        return True
        
    except Exception as e:
        logger.error("Erreur test OrderFlow: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_full_integration():
    """Test integration complète avec Battle Navale"""
    
    logger.info("\n🔍 TEST INTEGRATION BATTLE NAVALE")
    print("="*40)
    
    try:
        from core.base_types import OrderFlowData, MarketData
        from core.battle_navale import create_battle_navale_detector
        import pandas as pd
        
        # Créer battle navale detector
        detector = create_battle_navale_detector()
        
        # Market data
        market_data = MarketData(
            timestamp=pd.Timestamp.now(),
            symbol="ES",
            open=4500.0,
            high=4510.0,
            low=4495.0,
            close=4505.0,
            volume=2000
        )
        
        # Order flow avec net_delta fourni (comme dans test_phase2)
        order_flow = OrderFlowData(
            timestamp=market_data.timestamp,
            symbol="ES",
            cumulative_delta=15.0,
            bid_volume=800,
            ask_volume=1200,
            aggressive_buys=45,
            aggressive_sells=20,
            net_delta=150.0  # ← DOIT MARCHER MAINTENANT
        )
        
        # Confluence data
        confluence_data = {
            'vwap_price': 4502.0,
            'poc_price': 4501.0,
            'put_wall': 4480.0,
            'call_wall': 4520.0,
            'volume_clusters': [4500.0, 4505.0]
        }
        
        # Test analyse Battle Navale
        import time
        start = time.perf_counter()
        signal = detector.analyze_market_tick(market_data, order_flow, confluence_data)
        elapsed = (time.perf_counter() - start) * 1000
        
        logger.info("Battle Navale analysis: {elapsed:.2f}ms")
        if signal:
            logger.info("Signal généré: confidence {signal.confidence:.2f}")
        else:
            logger.info("Pas de signal (normal)")
        
        return True
        
    except Exception as e:
        logger.error("Erreur integration: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Correction finale OrderFlow"""
    
    logger.info("🎯 FIX FINAL: OrderFlowData net_delta conflict")
    print("="*55)
    logger.info("🔧 STRATÉGIE: net_delta comme champ simple du dataclass")
    print()
    
    # Corriger OrderFlow
    success = fix_orderflow_cleanly()
    
    if success:
        # Test OrderFlow seul
        if test_orderflow_fix():
            logger.info("\n✅ OrderFlow corrigé!")
            
            # Test integration complète
            if test_full_integration():
                logger.info("\n🎉 INTEGRATION COMPLÈTE RÉUSSIE!")
                logger.info("OrderFlowData avec net_delta: OK")
                logger.info("Battle Navale integration: OK")
                print()
                logger.info("🚀 RELANCEZ MAINTENANT:")
                logger.info("   python test_phase2_integration.py")
                print()
                logger.info("🎯 Battle Navale devrait maintenant PASSER!")
            else:
                logger.info("\n⚠️ OrderFlow OK mais problème integration Battle Navale")
        else:
            logger.info("\n❌ Problème test OrderFlow")
    else:
        logger.info("\n❌ Échec correction OrderFlow")

if __name__ == "__main__":
    main()