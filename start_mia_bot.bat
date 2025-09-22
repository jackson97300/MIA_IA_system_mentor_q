@echo off
REM 🚀 MIA IA SYSTEM - Script de Démarrage Automatique
REM Démarrage du bot de trading MIA sur PC fixe
REM Version: Production Ready v1.0

echo ========================================
echo 🚀 DÉMARRAGE MIA IA SYSTEM
echo ========================================
echo.

REM Vérifier que Python est installé
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python n'est pas installé ou pas dans le PATH
    pause
    exit /b 1
)

REM Aller dans le répertoire du système MIA
cd /d "D:\MIA_IA_system"

REM Vérifier que le répertoire existe
if not exist "D:\MIA_IA_system" (
    echo ❌ Répertoire MIA_IA_system introuvable
    pause
    exit /b 1
)

REM Vérifier que le fichier principal existe
if not exist "launch_hybrid_system.py" (
    echo ❌ Fichier launch_hybrid_system.py introuvable
    pause
    exit /b 1
)

echo ✅ Vérifications terminées
echo.

REM Créer les dossiers nécessaires s'ils n'existent pas
if not exist "logs" mkdir logs
if not exist "D:\MIA_SHARED" mkdir "D:\MIA_SHARED"
if not exist "D:\MIA_SHARED\MIA_IA_system" mkdir "D:\MIA_SHARED\MIA_IA_system"
if not exist "D:\MIA_SHARED\DERNIER_CHARBOOK_DE_DORIAN" mkdir "D:\MIA_SHARED\DERNIER_CHARBOOK_DE_DORIAN"
if not exist "D:\MIA_SHARED\Quantower" mkdir "D:\MIA_SHARED\Quantower"
if not exist "D:\MIA_SHARED\MICRO_SIERRA_CHART_2024" mkdir "D:\MIA_SHARED\MICRO_SIERRA_CHART_2024"

REM Démarrer le système MIA
echo 🚀 Démarrage du système MIA...
echo 📅 Date: %date% %time%
echo.

python launch_hybrid_system.py

REM Si le script se termine, afficher un message
echo.
echo ========================================
echo 🛑 SYSTÈME MIA ARRÊTÉ
echo ========================================
echo.
pause
