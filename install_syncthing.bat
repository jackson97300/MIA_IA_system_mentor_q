@echo off
REM 🚀 MIA IA SYSTEM - Installation Automatisée Syncthing
REM Script d'installation et configuration de Syncthing
REM Version: Production Ready v1.0

echo ========================================
echo 🔄 INSTALLATION SYNCING
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

REM Vérifier si Syncthing est déjà installé
sc query syncthing >nul 2>&1
if not errorlevel 1 (
    echo ⚠️  Syncthing est déjà installé
    set /p "REINSTALL=Voulez-vous le réinstaller ? (O/N): "
    if /i not "%REINSTALL%"=="O" (
        echo ❌ Installation annulée
        pause
        exit /b 0
    )
    echo 🛑 Arrêt du service Syncthing...
    net stop syncthing
)

echo.
echo 📥 Téléchargement de Syncthing...
echo.

REM Créer un dossier temporaire
if not exist "%TEMP%\syncthing_install" mkdir "%TEMP%\syncthing_install"
cd /d "%TEMP%\syncthing_install"

REM Télécharger Syncthing (version Windows 64-bit)
echo Telechargement en cours...
powershell -Command "& {Invoke-WebRequest -Uri 'https://github.com/syncthing/syncthing/releases/latest/download/syncthing-windows-amd64-v1.27.8.zip' -OutFile 'syncthing.zip'}"

if not exist "syncthing.zip" (
    echo ❌ Erreur lors du téléchargement
    echo 💡 Vérifiez votre connexion Internet
    pause
    exit /b 1
)

echo ✅ Téléchargement terminé
echo.

REM Extraire l'archive
echo 📦 Extraction de l'archive...
powershell -Command "& {Expand-Archive -Path 'syncthing.zip' -DestinationPath '.' -Force}"

if not exist "syncthing.exe" (
    echo ❌ Erreur lors de l'extraction
    pause
    exit /b 1
)

echo ✅ Extraction terminée
echo.

REM Installer Syncthing
echo 🔧 Installation de Syncthing...
echo.

REM Créer le répertoire d'installation
if not exist "C:\Program Files\Syncthing" mkdir "C:\Program Files\Syncthing"

REM Copier les fichiers
copy "syncthing.exe" "C:\Program Files\Syncthing\"
copy "syncthing.exe" "C:\Program Files\Syncthing\syncthing-service.exe"

REM Créer le service Windows
echo 🔧 Création du service Windows...
sc create syncthing binPath= "C:\Program Files\Syncthing\syncthing-service.exe" start= auto DisplayName= "Syncthing"

if errorlevel 1 (
    echo ❌ Erreur lors de la création du service
    pause
    exit /b 1
)

REM Démarrer le service
echo 🚀 Démarrage du service...
sc start syncthing

if errorlevel 1 (
    echo ❌ Erreur lors du démarrage du service
    pause
    exit /b 1
)

echo ✅ Service démarré avec succès
echo.

REM Attendre que Syncthing soit prêt
echo ⏱️  Attente du démarrage de Syncthing...
timeout /t 10 /nobreak >nul

REM Ouvrir l'interface web
echo 🌐 Ouverture de l'interface web...
start http://localhost:8384

echo.
echo ========================================
echo 🎉 INSTALLATION TERMINÉE
echo ========================================
echo.
echo ✅ Syncthing installé et démarré
echo 🌐 Interface web: http://localhost:8384
echo.
echo 📋 Prochaines étapes:
echo    1. Configurer le dossier partagé dans l'interface web
echo    2. Ajouter l'autre PC comme device
echo    3. Copier les fichiers vers D:\MIA_SHARED
echo.
echo 💡 Consultez le guide: GUIDE_INSTALLATION_SYNCING.md
echo.

REM Nettoyer les fichiers temporaires
cd /d "%TEMP%"
rmdir /s /q "syncthing_install" 2>nul

pause
