#!/usr/bin/env python3
"""
MIA_IA_SYSTEM - Forcer Mode LIVE TWS
Force TWS en mode LIVE et corrige les donnees anormales
"""

import os
import sys
import asyncio
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def forcer_mode_live_tws():
    """Force TWS en mode LIVE"""
    
    print("MIA_IA_SYSTEM - FORCER MODE LIVE TWS")
    print("=" * 50)
    print("Probleme: TWS en mode PAPER (donnees simulees)")
    print("Solution: Forcer le mode LIVE")
    print("=" * 50)

    print("\nETAPES REQUISES:")
    print("=" * 30)
    print("1. Fermer TWS completement")
    print("2. Redemarrer TWS en mode LIVE")
    print("3. Verifier la configuration")
    print("4. Tester les donnees")
    
    print("\nCONFIGURATION TWS LIVE:")
    print("=" * 30)
    print("- Demarrer TWS")
    print("- Choisir 'LIVE TRADING' (pas Paper)")
    print("- Se connecter avec vos identifiants LIVE")
    print("- Verifier que le compte affiche 'LIVE'")
    
    print("\nVERIFICATION API:")
    print("=" * 30)
    print("- File > Global Configuration")
    print("- API > Settings")
    print("- Enable ActiveX and Socket Clients: OUI")
    print("- Port: 7497")
    print("- Allow connections from localhost: OUI")
    
    # Test de connexion après configuration
    print("\nTEST CONNEXION LIVE:")
    print("=" * 30)
    
    try:
        from core.ibkr_connector import IBKRConnector
        
        ibkr = IBKRConnector()
        ibkr.host = "127.0.0.1"
        ibkr.port = 7497
        ibkr.client_id = 1
        ibkr.timeout = 15
        
        print("Connexion TWS LIVE...")
        await ibkr.connect()
        
        if await ibkr.is_connected():
            print("SUCCES: Connexion TWS etablie")
            
            # Test donnees ES
            data = await ibkr.get_market_data("ES")
            if data:
                prix = data.get('last', 0)
                print(f"Prix ES: {prix}")
                
                if 6000 < prix < 6500:
                    print("SUCCES: Prix ES normal (mode LIVE)")
                    print("Le systeme est pret pour le trading")
                    return True
                else:
                    print(f"ATTENTION: Prix toujours anormal: {prix}")
                    print("Verifiez que TWS est bien en mode LIVE")
                    return False
            else:
                print("ATTENTION: Aucune donnee ES")
                return False
        else:
            print("ECHEC: Impossible de se connecter")
            return False
            
    except Exception as e:
        print(f"ERREUR: {e}")
        return False

if __name__ == "__main__":
    print("INSTRUCTIONS:")
    print("1. Fermez TWS")
    print("2. Redemarrez TWS en mode LIVE")
    print("3. Configurez l'API")
    print("4. Puis executez ce script")
    
    response = input("\nTWS est-il maintenant en mode LIVE? (oui/non): ")
    
    if response.lower() in ['oui', 'yes', 'o', 'y']:
        success = asyncio.run(forcer_mode_live_tws())
        
        if success:
            print("\nSUCCES: Mode LIVE active")
            print("Le systeme peut maintenant trader")
        else:
            print("\nECHEC: Probleme de configuration")
            print("Verifiez TWS et relancez")
    else:
        print("\nVeuillez d'abord configurer TWS en mode LIVE")
        print("Puis relancez ce script")





