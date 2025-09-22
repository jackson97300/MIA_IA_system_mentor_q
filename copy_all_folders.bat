@echo off
REM 🚀 MIA IA SYSTEM - Copie Tous les Dossiers
REM Script batch pour copier tous les dossiers de trading
REM Version: Production Ready v1.0

echo ========================================
echo 📁 COPIE TOUS LES DOSSIERS DE TRADING
echo ========================================
echo.

REM Créer le dossier MIA_SHARED s'il n'existe pas
if not exist "D:\MIA_SHARED" (
    echo 📁 Création du dossier MIA_SHARED...
    mkdir "D:\MIA_SHARED"
)

echo ✅ Dossier MIA_SHARED prêt
echo.

REM Vérifier et copier chaque dossier
echo 🔍 Vérification des dossiers sources...
echo.

REM 1. Dossier MIA IA System COMPLET (PRIORITÉ 1)
echo 📁 Copie du dossier MIA IA System COMPLET...
if exist "D:\MIA_IA_system" (
    robocopy "D:\MIA_IA_system" "D:\MIA_SHARED\MIA_IA_system" /E /R:3 /W:1 /MT:8 /NFL /NDL /NJH /NJS /NC /NS /NP
    echo ✅ MIA_IA_system COMPLET copié
) else (
    echo ❌ MIA_IA_system introuvable - CRITIQUE!
)

echo.

REM 2. Dossiers spécifiques MIA (pour organisation)
echo 📁 Copie des dossiers spécifiques MIA...
if exist "D:\MIA_IA_system\config_files" (
    robocopy "D:\MIA_IA_system\config_files" "D:\MIA_SHARED\config_files" /E /R:3 /W:1 /NFL /NDL /NJH /NJS /NC /NS /NP
    echo ✅ config_files copié
) else (
    echo ⚠️  config_files introuvable
)

if exist "D:\MIA_IA_system\DATA_SIERRA_CHART" (
    robocopy "D:\MIA_IA_system\DATA_SIERRA_CHART" "D:\MIA_SHARED\DATA_SIERRA_CHART" /E /R:3 /W:1 /NFL /NDL /NJH /NJS /NC /NS /NP
    echo ✅ DATA_SIERRA_CHART copié
) else (
    echo ⚠️  DATA_SIERRA_CHART introuvable
)

if exist "D:\MIA_IA_system\logs" (
    robocopy "D:\MIA_IA_system\logs" "D:\MIA_SHARED\logs" /E /R:3 /W:1 /NFL /NDL /NJH /NJS /NC /NS /NP
    echo ✅ logs copié
) else (
    echo ⚠️  logs introuvable
)

if exist "D:\MIA_IA_system\results" (
    robocopy "D:\MIA_IA_system\results" "D:\MIA_SHARED\results" /E /R:3 /W:1 /NFL /NDL /NJH /NJS /NC /NS /NP
    echo ✅ results copié
) else (
    echo ⚠️  results introuvable
)

echo.

REM 3. Dossier Dorian
echo 📁 Copie du dossier Dorian...
if exist "D:\DERNIER CHARBOOK DE DORIAN" (
    robocopy "D:\DERNIER CHARBOOK DE DORIAN" "D:\MIA_SHARED\DERNIER_CHARBOOK_DE_DORIAN" /E /R:3 /W:1 /NFL /NDL /NJH /NJS /NC /NS /NP
    echo ✅ DERNIER_CHARBOOK_DE_DORIAN copié
) else (
    echo ⚠️  DERNIER CHARBOOK DE DORIAN introuvable
)

echo.

REM 4. Dossier Quantower
echo 📁 Copie du dossier Quantower...
if exist "C:\Users\LILJACKS\OneDrive\Bureau\documents sur bureau\Quantower" (
    robocopy "C:\Users\LILJACKS\OneDrive\Bureau\documents sur bureau\Quantower" "D:\MIA_SHARED\Quantower" /E /R:3 /W:1 /NFL /NDL /NJH /NJS /NC /NS /NP
    echo ✅ Quantower copié
) else (
    echo ⚠️  Quantower introuvable
    echo 💡 Vérifiez le chemin: C:\Users\LILJACKS\OneDrive\Bureau\documents sur bureau\Quantower
)

echo.

REM 5. Dossier Sierra Chart 2024
echo 📁 Copie du dossier Sierra Chart 2024...
if exist "D:\MICRO SIERRA CHART 2024" (
    robocopy "D:\MICRO SIERRA CHART 2024" "D:\MIA_SHARED\MICRO_SIERRA_CHART_2024" /E /R:3 /W:1 /NFL /NDL /NJH /NJS /NC /NS /NP
    echo ✅ MICRO_SIERRA_CHART_2024 copié
) else (
    echo ⚠️  MICRO SIERRA CHART 2024 introuvable
)

echo.

REM 6. Fichiers unifiés
echo 📁 Copie des fichiers unifiés...
if exist "D:\MIA_IA_system\unified_*.jsonl" (
    copy "D:\MIA_IA_system\unified_*.jsonl" "D:\MIA_SHARED\"
    echo ✅ Fichiers unifiés copiés
) else (
    echo ⚠️  Fichiers unifiés introuvables
)

if exist "D:\MIA_IA_system\trades_taken_*.csv" (
    copy "D:\MIA_IA_system\trades_taken_*.csv" "D:\MIA_SHARED\"
    echo ✅ Fichiers de trades copiés
) else (
    echo ⚠️  Fichiers de trades introuvables
)

echo.

REM Afficher le résumé
echo ========================================
echo 📊 RÉSUMÉ DE LA COPIE
echo ========================================
echo.

echo 📁 Contenu du dossier MIA_SHARED:
dir "D:\MIA_SHARED" /b
echo.

echo 📊 Taille totale du dossier MIA_SHARED:
for /f "tokens=3" %%a in ('dir "D:\MIA_SHARED" /s /-c ^| find "File(s)"') do set "TOTAL_SIZE=%%a"
echo 📊 Taille totale: %TOTAL_SIZE% bytes
echo.

echo ========================================
echo 🎉 COPIE TERMINÉE
echo ========================================
echo.
echo 📋 Prochaines étapes:
echo    1. Configurer Syncthing pour synchroniser D:\MIA_SHARED
echo    2. Tester la synchronisation entre les 2 PC
echo    3. Configurer le démarrage automatique du bot
echo.

pause
