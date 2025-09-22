@echo off
REM MIA IA SYSTEM - Installation Syncthing (Version Manuelle)
REM Script qui ouvre le site de telechargement
REM Version: Production Ready v1.0

echo ========================================
echo INSTALLATION SYNCING - VERSION MANUELLE
echo ========================================
echo.

echo Cette version ouvre le site de telechargement officiel
echo et vous guide pour l'installation manuelle
echo.

REM Verifier les privileges administrateur
net session >nul 2>&1
if errorlevel 1 (
    echo ATTENTION: Ce script devrait etre execute en tant qu'administrateur
    echo Mais ce n'est pas obligatoire pour l'installation manuelle
    echo.
)

echo Ouverture du site de telechargement...
echo.

REM Ouvrir le site de telechargement
start https://syncthing.net/downloads/

echo.
echo ========================================
echo INSTRUCTIONS D'INSTALLATION
echo ========================================
echo.
echo 1. Dans la page qui s'est ouverte:
echo    - Cliquer sur "Windows 64-bit (Installer)"
echo    - Telecharger le fichier .exe
echo.
echo 2. Executer le fichier telecharge:
echo    - Accepter la licence
echo    - Cocher "Start Syncthing automatically"
echo    - Cocher "Open Syncthing in browser"
echo    - Cliquer "Install"
echo.
echo 3. Apres l'installation:
echo    - L'interface web s'ouvrira automatiquement
echo    - Noter l'ID du device (Actions - Show ID)
echo.
echo 4. Executer ensuite: configure_syncthing.bat
echo.

pause
