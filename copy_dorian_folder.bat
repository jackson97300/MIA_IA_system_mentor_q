@echo off
REM 🚀 MIA IA SYSTEM - Copie Dossier Dorian
REM Script batch pour copier le dossier de trading Dorian
REM Version: Production Ready v1.0

echo ========================================
echo 📁 COPIE DOSSIER DORIAN
echo ========================================
echo.

REM Vérifier que le dossier source existe
set "SOURCE_PATH=D:\DERNIER CHARBOOK DE DORIAN"
set "DEST_PATH=D:\MIA_SHARED\DERNIER_CHARBOOK_DE_DORIAN"

if not exist "%SOURCE_PATH%" (
    echo ❌ Dossier source introuvable: %SOURCE_PATH%
    echo 💡 Vérifiez le chemin et réessayez
    pause
    exit /b 1
)

echo ✅ Dossier source trouvé: %SOURCE_PATH%

REM Créer le dossier de destination s'il n'existe pas
if not exist "D:\MIA_SHARED" (
    echo 📁 Création du dossier MIA_SHARED...
    mkdir "D:\MIA_SHARED"
)

if not exist "%DEST_PATH%" (
    echo 📁 Création du dossier de destination...
    mkdir "%DEST_PATH%"
)

echo ✅ Dossier de destination prêt: %DEST_PATH%
echo.

REM Afficher la taille du dossier source
echo 📊 Calcul de la taille du dossier source...
for /f "tokens=3" %%a in ('dir "%SOURCE_PATH%" /s /-c ^| find "File(s)"') do set "SOURCE_SIZE=%%a"
echo 📊 Taille du dossier source: %SOURCE_SIZE% bytes
echo.

REM Demander confirmation
set /p "CONFIRMATION=Voulez-vous copier le dossier Dorian vers MIA_SHARED ? (O/N): "
if /i not "%CONFIRMATION%"=="O" (
    echo ❌ Copie annulée par l'utilisateur
    pause
    exit /b 0
)

echo.
echo 🚀 Début de la copie...
echo ⏱️  Cela peut prendre quelques minutes selon la taille du dossier
echo.

REM Copier le dossier avec robocopy
robocopy "%SOURCE_PATH%" "%DEST_PATH%" /E /R:3 /W:1 /MT:8 /NFL /NDL /NJH /NJS /NC /NS /NP

REM Vérifier le code de retour de robocopy
if %ERRORLEVEL% LEQ 7 (
    echo.
    echo ✅ Copie terminée avec succès!
    echo.
    echo 📊 Vérification de la taille du dossier de destination...
    for /f "tokens=3" %%a in ('dir "%DEST_PATH%" /s /-c ^| find "File(s)"') do set "DEST_SIZE=%%a"
    echo 📊 Taille du dossier de destination: %DEST_SIZE% bytes
    
    if "%SOURCE_SIZE%"=="%DEST_SIZE%" (
        echo ✅ Intégrité vérifiée: Tailles identiques
    ) else (
        echo ⚠️  Attention: Tailles différentes
    )
) else (
    echo.
    echo ❌ Erreur lors de la copie (Code: %ERRORLEVEL%)
    echo 💡 Codes d'erreur robocopy:
    echo    0-7: Succès
    echo    8+: Erreur
)

echo.
echo ========================================
echo 🎉 SCRIPT TERMINÉ
echo ========================================
echo.
echo 📋 Prochaines étapes:
echo    1. Vérifier que Syncthing est configuré
echo    2. Le dossier sera synchronisé automatiquement
echo    3. Accéder au dossier depuis l'autre PC
echo.

pause
