@echo off
REM 🚀 MIA IA SYSTEM - Configuration Démarrage Automatique
REM Création d'une tâche planifiée pour démarrer MIA automatiquement
REM Version: Production Ready v1.0

echo ========================================
echo ⚙️ CONFIGURATION DÉMARRAGE AUTOMATIQUE
echo ========================================
echo.

REM Vérifier les privilèges administrateur
net session >nul 2>&1
if errorlevel 1 (
    echo ❌ Ce script doit être exécuté en tant qu'administrateur
    echo 💡 Clic droit sur le fichier → "Exécuter en tant qu'administrateur"
    pause
    exit /b 1
)

echo ✅ Privilèges administrateur confirmés
echo.

REM Chemin vers le script de démarrage
set SCRIPT_PATH=D:\MIA_IA_system\start_mia_bot.bat

REM Vérifier que le script existe
if not exist "%SCRIPT_PATH%" (
    echo ❌ Script de démarrage introuvable: %SCRIPT_PATH%
    pause
    exit /b 1
)

echo 📁 Script trouvé: %SCRIPT_PATH%
echo.

REM Supprimer la tâche existante si elle existe
schtasks /delete /tn "MIA_Bot_Startup" /f >nul 2>&1

REM Créer la nouvelle tâche planifiée
echo 🔧 Création de la tâche planifiée...
schtasks /create /tn "MIA_Bot_Startup" /tr "%SCRIPT_PATH%" /sc onstart /ru "SYSTEM" /rl highest /f

if errorlevel 1 (
    echo ❌ Erreur lors de la création de la tâche planifiée
    pause
    exit /b 1
)

echo ✅ Tâche planifiée créée avec succès
echo.

REM Afficher les informations de la tâche
echo 📋 Informations de la tâche:
schtasks /query /tn "MIA_Bot_Startup" /fo list

echo.
echo ========================================
echo 🎉 CONFIGURATION TERMINÉE
echo ========================================
echo.
echo 📋 La tâche "MIA_Bot_Startup" a été créée
echo 🚀 MIA démarrera automatiquement au démarrage de Windows
echo.
echo 🔧 Commandes utiles:
echo   - Voir la tâche: schtasks /query /tn "MIA_Bot_Startup"
echo   - Exécuter maintenant: schtasks /run /tn "MIA_Bot_Startup"
echo   - Supprimer: schtasks /delete /tn "MIA_Bot_Startup"
echo.
pause
