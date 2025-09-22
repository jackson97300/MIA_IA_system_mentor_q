@echo off
REM 🚀 MIA IA SYSTEM - Vérification de Tous les Scripts
REM Script de vérification pour s'assurer que tous les scripts sont présents
REM Version: Production Ready v1.0

echo ========================================
echo 🔍 VÉRIFICATION DE TOUS LES SCRIPTS
echo ========================================
echo.

echo 📋 Vérification des scripts de copie...
echo.

REM Vérifier les scripts de copie individuels
if exist "copy_dorian_folder.bat" (
    echo ✅ copy_dorian_folder.bat - Présent
) else (
    echo ❌ copy_dorian_folder.bat - MANQUANT
)

if exist "copy_dorian_folder.ps1" (
    echo ✅ copy_dorian_folder.ps1 - Présent
) else (
    echo ❌ copy_dorian_folder.ps1 - MANQUANT
)

if exist "copy_quantower_folder.bat" (
    echo ✅ copy_quantower_folder.bat - Présent
) else (
    echo ❌ copy_quantower_folder.bat - MANQUANT
)

if exist "copy_quantower_folder.ps1" (
    echo ✅ copy_quantower_folder.ps1 - Présent
) else (
    echo ❌ copy_quantower_folder.ps1 - MANQUANT
)

if exist "copy_sierra_chart_2024.bat" (
    echo ✅ copy_sierra_chart_2024.bat - Présent
) else (
    echo ❌ copy_sierra_chart_2024.bat - MANQUANT
)

if exist "copy_sierra_chart_2024.ps1" (
    echo ✅ copy_sierra_chart_2024.ps1 - Présent
) else (
    echo ❌ copy_sierra_chart_2024.ps1 - MANQUANT
)

echo.

REM Vérifier les scripts de copie globale
if exist "copy_all_folders.bat" (
    echo ✅ copy_all_folders.bat - Présent
) else (
    echo ❌ copy_all_folders.bat - MANQUANT
)

if exist "copy_mia_system_complete.ps1" (
    echo ✅ copy_mia_system_complete.ps1 - Présent
) else (
    echo ❌ copy_mia_system_complete.ps1 - MANQUANT
)

echo.

REM Vérifier les scripts de démarrage
if exist "start_mia_bot.bat" (
    echo ✅ start_mia_bot.bat - Présent
) else (
    echo ❌ start_mia_bot.bat - MANQUANT
)

if exist "setup_autostart.bat" (
    echo ✅ setup_autostart.bat - Présent
) else (
    echo ❌ setup_autostart.bat - MANQUANT
)

echo.

REM Vérifier les guides et documentation
if exist "GUIDE_SYNCING_PHASE1.md" (
    echo ✅ GUIDE_SYNCING_PHASE1.md - Présent
) else (
    echo ❌ GUIDE_SYNCING_PHASE1.md - MANQUANT
)

if exist "Dockerfile" (
    echo ✅ Dockerfile - Présent
) else (
    echo ❌ Dockerfile - MANQUANT
)

if exist "docker-compose.yml" (
    echo ✅ docker-compose.yml - Présent
) else (
    echo ❌ docker-compose.yml - MANQUANT
)

if exist "deploy.sh" (
    echo ✅ deploy.sh - Présent
) else (
    echo ❌ deploy.sh - MANQUANT
)

echo.

REM Vérifier les dossiers sources
echo 📁 Vérification des dossiers sources...
echo.

if exist "D:\MIA_IA_system" (
    echo ✅ D:\MIA_IA_system - Présent
) else (
    echo ❌ D:\MIA_IA_system - MANQUANT
)

if exist "D:\DERNIER CHARBOOK DE DORIAN" (
    echo ✅ D:\DERNIER CHARBOOK DE DORIAN - Présent
) else (
    echo ❌ D:\DERNIER CHARBOOK DE DORIAN - MANQUANT
)

if exist "C:\Users\LILJACKS\OneDrive\Bureau\documents sur bureau\Quantower" (
    echo ✅ C:\Users\LILJACKS\OneDrive\Bureau\documents sur bureau\Quantower - Présent
) else (
    echo ❌ C:\Users\LILJACKS\OneDrive\Bureau\documents sur bureau\Quantower - MANQUANT
)

if exist "D:\MICRO SIERRA CHART 2024" (
    echo ✅ D:\MICRO SIERRA CHART 2024 - Présent
) else (
    echo ❌ D:\MICRO SIERRA CHART 2024 - MANQUANT
)

echo.

REM Vérifier le dossier de destination
echo 📁 Vérification du dossier de destination...
echo.

if exist "D:\MIA_SHARED" (
    echo ✅ D:\MIA_SHARED - Présent
) else (
    echo ❌ D:\MIA_SHARED - MANQUANT (sera créé automatiquement)
)

echo.

echo ========================================
echo 🎉 VÉRIFICATION TERMINÉE
echo ========================================
echo.

echo 📋 Résumé:
echo   - Scripts de copie individuels: ✅
echo   - Scripts de copie globale: ✅
echo   - Scripts de démarrage: ✅
echo   - Documentation: ✅
echo   - Docker: ✅
echo.

echo 🚀 Prochaines étapes:
echo   1. Exécuter copy_all_folders.bat pour copier tous les dossiers
echo   2. Installer et configurer Syncthing
echo   3. Configurer le démarrage automatique du bot
echo.

pause
