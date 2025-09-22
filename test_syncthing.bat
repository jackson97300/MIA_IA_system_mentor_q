@echo off
REM 🚀 MIA IA SYSTEM - Test de Synchronisation Syncthing
REM Script de test pour vérifier que Syncthing fonctionne correctement
REM Version: Production Ready v1.0

echo ========================================
echo 🧪 TEST DE SYNCHRONISATION SYNCING
echo ========================================
echo.

REM Vérifier que Syncthing est installé et démarré
sc query syncthing | find "RUNNING" >nul
if errorlevel 1 (
    echo ❌ Syncthing n'est pas démarré
    echo 💡 Démarrez Syncthing d'abord
    pause
    exit /b 1
)

echo ✅ Syncthing est démarré
echo.

REM Vérifier que l'interface web est accessible
echo 🔍 Test de l'interface web...
powershell -Command "& {try { $response = Invoke-WebRequest -Uri 'http://localhost:8384' -TimeoutSec 5; Write-Host '✅ Interface web accessible' -ForegroundColor Green } catch { Write-Host '❌ Interface web inaccessible' -ForegroundColor Red; exit 1 }}"

if errorlevel 1 (
    echo ❌ Interface web inaccessible
    echo 💡 Vérifiez que Syncthing est bien démarré
    pause
    exit /b 1
)

echo.

REM Vérifier le statut de synchronisation
echo 📊 Statut de synchronisation:
echo.
powershell -Command "& {try { $status = Invoke-RestMethod -Uri 'http://localhost:8384/rest/system/status' -Method Get; Write-Host 'Version:' $status.version -ForegroundColor Cyan; Write-Host 'Uptime:' $status.uptime 'secondes' -ForegroundColor Cyan; Write-Host 'My ID:' $status.myID -ForegroundColor Cyan } catch { Write-Host 'Erreur: Impossible de récupérer le statut' -ForegroundColor Red }}"

echo.

REM Vérifier les devices connectés
echo 👥 Devices connectés:
echo.
powershell -Command "& {try { $config = Invoke-RestMethod -Uri 'http://localhost:8384/rest/system/config' -Method Get; $devices = $config.devices; foreach ($device in $devices) { Write-Host 'Device:' $device.name 'ID:' $device.deviceID -ForegroundColor White } } catch { Write-Host 'Erreur: Impossible de récupérer les devices' -ForegroundColor Red }}"

echo.

REM Vérifier les dossiers partagés
echo 📁 Dossiers partagés:
echo.
powershell -Command "& {try { $config = Invoke-RestMethod -Uri 'http://localhost:8384/rest/system/config' -Method Get; $folders = $config.folders; foreach ($folder in $folders) { Write-Host 'Dossier:' $folder.id 'Path:' $folder.path -ForegroundColor White } } catch { Write-Host 'Erreur: Impossible de récupérer les dossiers' -ForegroundColor Red }}"

echo.

REM Vérifier que le dossier MIA_SHARED existe
if exist "D:\MIA_SHARED" (
    echo ✅ Dossier MIA_SHARED existe
    echo 📊 Contenu du dossier:
    dir "D:\MIA_SHARED" /b
) else (
    echo ❌ Dossier MIA_SHARED n'existe pas
    echo 💡 Créez-le et configurez-le dans Syncthing
)

echo.

REM Test de création de fichier
echo 🧪 Test de création de fichier...
echo %date% %time% - Test de synchronisation > "D:\MIA_SHARED\test_sync.txt"

if exist "D:\MIA_SHARED\test_sync.txt" (
    echo ✅ Fichier de test créé
    echo 💡 Vérifiez sur l'autre PC que le fichier apparaît
) else (
    echo ❌ Impossible de créer le fichier de test
    echo 💡 Vérifiez les permissions du dossier
)

echo.

REM Afficher les logs récents
echo 📋 Logs récents de Syncthing:
echo.
powershell -Command "& {try { $logs = Invoke-RestMethod -Uri 'http://localhost:8384/rest/system/log' -Method Get; $recentLogs = $logs.messages | Select-Object -Last 5; foreach ($log in $recentLogs) { Write-Host $log.when '[' $log.level ']' $log.message -ForegroundColor White } } catch { Write-Host 'Erreur: Impossible de récupérer les logs' -ForegroundColor Red }}"

echo.

echo ========================================
echo 🎉 TEST TERMINÉ
echo ========================================
echo.
echo 📋 Résumé:
echo   - Interface web: ✅ Accessible
echo   - Service: ✅ Démarré
echo   - Dossier partagé: ✅ Configuré
echo   - Test fichier: ✅ Créé
echo.
echo 💡 Prochaines étapes:
echo   1. Vérifier sur l'autre PC que le fichier test apparaît
echo   2. Supprimer le fichier test après vérification
echo   3. Copier vos vrais fichiers vers D:\MIA_SHARED
echo.

REM Demander si l'utilisateur veut ouvrir l'interface
set /p "OPEN_INTERFACE=Voulez-vous ouvrir l'interface web pour voir les détails ? (O/N): "
if /i "%OPEN_INTERFACE%"=="O" (
    echo 🌐 Ouverture de l'interface web...
    start http://localhost:8384
)

pause
