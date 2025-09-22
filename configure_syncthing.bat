@echo off
REM 🚀 MIA IA SYSTEM - Configuration Rapide Syncthing
REM Script de configuration automatique de Syncthing
REM Version: Production Ready v1.0

echo ========================================
echo ⚙️ CONFIGURATION RAPIDE SYNCING
echo ========================================
echo.

REM Vérifier que Syncthing est installé
sc query syncthing >nul 2>&1
if errorlevel 1 (
    echo ❌ Syncthing n'est pas installé
    echo 💡 Exécutez d'abord install_syncthing.bat
    pause
    exit /b 1
)

echo ✅ Syncthing est installé
echo.

REM Vérifier que le service est démarré
sc query syncthing | find "RUNNING" >nul
if errorlevel 1 (
    echo 🚀 Démarrage du service Syncthing...
    net start syncthing
    if errorlevel 1 (
        echo ❌ Erreur lors du démarrage du service
        pause
        exit /b 1
    )
)

echo ✅ Service Syncthing démarré
echo.

REM Créer le dossier MIA_SHARED s'il n'existe pas
if not exist "D:\MIA_SHARED" (
    echo 📁 Création du dossier MIA_SHARED...
    mkdir "D:\MIA_SHARED"
    echo ✅ Dossier MIA_SHARED créé
) else (
    echo ✅ Dossier MIA_SHARED existe déjà
)

echo.

REM Afficher l'ID du device
echo 📋 ID du Device actuel:
echo.
echo 🔍 Récupération de l'ID...
powershell -Command "& {try { $response = Invoke-RestMethod -Uri 'http://localhost:8384/rest/system/status' -Method Get; $config = Invoke-RestMethod -Uri 'http://localhost:8384/rest/system/config' -Method Get; Write-Host 'Device ID:' $config.myID -ForegroundColor Green } catch { Write-Host 'Erreur: Impossible de récupérer l''ID' -ForegroundColor Red }}"

echo.
echo 📋 Instructions de configuration:
echo.
echo 1. 🌐 Ouvrir l'interface web: http://localhost:8384
echo 2. 📁 Cliquer "Add Folder" et configurer:
echo    - Folder ID: mia-shared
echo    - Folder Path: D:\MIA_SHARED
echo    - ✅ Cocher "Share this folder"
echo 3. 👥 Cliquer "Add Remote Device" et ajouter l'autre PC
echo 4. 📋 Noter l'ID du device (affiché ci-dessus)
echo.

REM Demander si l'utilisateur veut ouvrir l'interface
set /p "OPEN_INTERFACE=Voulez-vous ouvrir l'interface web maintenant ? (O/N): "
if /i "%OPEN_INTERFACE%"=="O" (
    echo 🌐 Ouverture de l'interface web...
    start http://localhost:8384
)

echo.
echo ========================================
echo 🎉 CONFIGURATION PRÉPARÉE
echo ========================================
echo.
echo 📋 Prochaines étapes manuelles:
echo    1. Configurer le dossier partagé dans l'interface web
echo    2. Ajouter l'autre PC comme device
echo    3. Copier les fichiers vers D:\MIA_SHARED
echo    4. Tester la synchronisation
echo.
echo 💡 Guide détaillé: GUIDE_INSTALLATION_SYNCING.md
echo.

pause
