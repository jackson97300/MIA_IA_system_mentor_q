#!/usr/bin/env python3
"""
MIA_IA_SYSTEM - Diagnostic Spécialisé SPX Options
Diagnostic et correction spécifique pour données SPX
"""

import os
import sys
import asyncio
from datetime import datetime

# Ajouter le répertoire racine au path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def diagnostic_spx_specialise():
    """Diagnostic spécialisé SPX options"""
    
    print("MIA_IA_SYSTEM - DIAGNOSTIC SPÉCIALISÉ SPX OPTIONS")
    print("=" * 60)
    print(f"Diagnostic: {datetime.now()}")
    print("=" * 60)
    
    # 1. Vérification SPX Options Retriever
    print("\n1. ANALYSE SPX OPTIONS RETRIEVER")
    print("-" * 40)
    
    try:
        from features.spx_options_retriever import SPXOptionsRetriever
        print("✅ SPXOptionsRetriever importé")
        
        # Analyser le code source
        spx_file = 'features/spx_options_retriever.py'
        if os.path.exists(spx_file):
            with open(spx_file, 'r', encoding='utf-8') as f:
                spx_code = f.read()
            
            print("\n   ANALYSE CODE SPX:")
            
            # Vérifier méthodes critiques
            if 'get_real_spx_data' in spx_code:
                print("   ✅ Méthode get_real_spx_data présente")
            else:
                print("   ❌ Méthode get_real_spx_data manquante")
            
            if 'data_source = "ibkr_real"' in spx_code:
                print("   ✅ Source IBKR réelle configurée")
            else:
                print("   ❌ Source IBKR réelle non configurée")
            
            if 'self.force_real_data = True' in spx_code:
                print("   ✅ Force real data activé")
            else:
                print("   ❌ Force real data non activé")
            
            if 'return self._get_fallback_data()' in spx_code:
                print("   ⚠️ Fallback vers données simulées détecté")
            else:
                print("   ✅ Pas de fallback vers simulation")
                
    except Exception as e:
        print(f"❌ Erreur analyse SPX: {e}")
    
    # 2. Test connexion IBKR directe
    print("\n2. TEST CONNEXION IBKR DIRECTE")
    print("-" * 40)
    
    try:
        from core.ibkr_connector import IBKRConnector
        
        config = {
            'ibkr_host': '127.0.0.1',
            'ibkr_port': 7497,
            'ibkr_client_id': 1,
            'simulation_mode': False,
            'require_real_data': True,
            'fallback_to_saved_data': False
        }
        
        connector = IBKRConnector(config)
        print("✅ IBKRConnector créé")
        
        # Test connexion
        try:
            connected = await asyncio.wait_for(connector.connect(), timeout=10.0)
            if connected:
                print("✅ Connexion IBKR réussie")
                print(f"   Status: {getattr(connector, 'connection_status', 'N/A')}")
                print(f"   Connected: {getattr(connector, 'is_connected_flag', 'N/A')}")
                
                # Test récupération données SPX
                print("\n3. TEST RÉCUPÉRATION DONNÉES SPX")
                print("-" * 40)
                
                spx_retriever = SPXOptionsRetriever(connector)
                print("✅ SPXOptionsRetriever créé")
                
                # Vérifier attributs
                print(f"   Force real data: {getattr(spx_retriever, 'force_real_data', 'N/A')}")
                print(f"   Use ib insync: {getattr(spx_retriever, 'use_ib_insync', 'N/A')}")
                
                # Test récupération
                print("\n   Récupération données SPX...")
                spx_data = await spx_retriever.get_real_spx_data()
                
                if spx_data:
                    print("✅ Données SPX récupérées")
                    print(f"   Source: {spx_data.get('data_source', 'N/A')}")
                    print(f"   Put/Call Ratio: {spx_data.get('put_call_ratio', 'N/A')}")
                    print(f"   VIX Level: {spx_data.get('vix_level', 'N/A')}")
                    print(f"   Gamma Exposure: ${spx_data.get('gamma_exposure', 0)/1e9:.1f}B")
                    print(f"   Timestamp: {spx_data.get('timestamp', 'N/A')}")
                    
                    # Analyse source
                    data_source = spx_data.get('data_source', 'N/A')
                    if data_source == 'ibkr_real':
                        print("\n✅ SUCCÈS: Données SPX réelles confirmées")
                        return True
                    else:
                        print(f"\n❌ PROBLÈME: Source non réelle: {data_source}")
                        
                        # Diagnostic détaillé
                        print("\n   DIAGNOSTIC DÉTAILLÉ:")
                        if data_source == 'saved_data':
                            print("   - Utilise données sauvegardées au lieu de temps réel")
                        elif data_source == 'simulation':
                            print("   - Utilise données simulées")
                        elif data_source == 'fallback_simulated':
                            print("   - Fallback vers simulation activé")
                        else:
                            print(f"   - Source inconnue: {data_source}")
                        
                        return False
                else:
                    print("❌ Aucune donnée SPX récupérée")
                    return False
                    
            else:
                print("❌ Connexion IBKR échouée")
                return False
                
        except asyncio.TimeoutError:
            print("❌ Timeout connexion IBKR")
            return False
        except Exception as e:
            print(f"❌ Erreur connexion: {e}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur test IBKR: {e}")
        return False

def corriger_spx_options():
    """Correction spécifique SPX options"""
    
    print("\n4. CORRECTION SPÉCIFIQUE SPX OPTIONS")
    print("-" * 40)
    
    spx_file = 'features/spx_options_retriever.py'
    if not os.path.exists(spx_file):
        print(f"❌ Fichier {spx_file} non trouvé")
        return False
    
    try:
        # Créer backup
        backup_file = f"{spx_file}.backup_spx_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        import shutil
        shutil.copy2(spx_file, backup_file)
        print(f"✅ Backup créé: {backup_file}")
        
        # Lire contenu
        with open(spx_file, 'r', encoding='utf-8') as f:
            contenu = f.read()
        
        # Corrections spécifiques SPX
        contenu_modifie = contenu
        
        # 1. Forcer force_real_data
        if 'self.force_real_data = True' not in contenu_modifie:
            contenu_modifie = contenu_modifie.replace(
                'def __init__(self, ibkr_connector):',
                'def __init__(self, ibkr_connector):\n        self.force_real_data = True'
            )
        
        # 2. Forcer data_source ibkr_real
        contenu_modifie = contenu_modifie.replace(
            'data_source = "saved_data"',
            'data_source = "ibkr_real"'
        )
        contenu_modifie = contenu_modifie.replace(
            'data_source = "simulation"',
            'data_source = "ibkr_real"'
        )
        contenu_modifie = contenu_modifie.replace(
            'data_source = "fallback_simulated"',
            'data_source = "ibkr_real"'
        )
        
        # 3. Forcer fallback vers données réelles
        contenu_modifie = contenu_modifie.replace(
            'return self._get_fallback_data()',
            'return self._get_real_ibkr_data()'
        )
        
        # 4. Forcer use_ib_insync
        if 'self.use_ib_insync = True' not in contenu_modifie:
            contenu_modifie = contenu_modifie.replace(
                'self.ibkr_connector = ibkr_connector',
                'self.ibkr_connector = ibkr_connector\n        self.use_ib_insync = True'
            )
        
        # Écrire modifications
        if contenu_modifie != contenu:
            with open(spx_file, 'w', encoding='utf-8') as f:
                f.write(contenu_modifie)
            print("✅ Corrections SPX appliquées")
            return True
        else:
            print("⚠️ Aucune correction SPX nécessaire")
            return False
            
    except Exception as e:
        print(f"❌ Erreur correction SPX: {e}")
        return False

async def main():
    """Fonction principale"""
    try:
        print("Démarrage diagnostic spécialisé SPX...")
        
        # Diagnostic
        success = await diagnostic_spx_specialise()
        
        if not success:
            print("\n🔧 APPLICATION CORRECTIONS SPX...")
            correction_appliquee = corriger_spx_options()
            
            if correction_appliquee:
                print("\n🔄 TEST APRÈS CORRECTION...")
                success = await diagnostic_spx_specialise()
        
        print("\n" + "=" * 60)
        print("RÉSULTATS DIAGNOSTIC SPX SPÉCIALISÉ")
        print("=" * 60)
        
        if success:
            print("✅ SUCCÈS: Données SPX réelles confirmées")
            print("✅ Système prêt pour test 2h")
            print("🚀 Lancement recommandé: python lance_mia_ia_tws.py")
        else:
            print("❌ ÉCHEC: Données SPX non confirmées")
            print("\n🔧 ACTIONS MANUELLES RECOMMANDÉES:")
            print("1. Vérifier TWS connecté sur port 7497")
            print("2. Activer souscription données SPX options")
            print("3. Vérifier marchés SPX ouverts")
            print("4. Vérifier configuration IBKR")
            print("5. Redémarrer TWS si nécessaire")
        
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Erreur diagnostic: {e}")

if __name__ == "__main__":
    asyncio.run(main())


