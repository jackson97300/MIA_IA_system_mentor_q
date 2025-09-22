@echo off
REM MIA IA SYSTEM - Installation Syncthing (Version Simple)
REM Script d'installation sans caracteres speciaux
REM Version: Production Ready v1.0

echo ========================================
echo INSTALLATION SYNCING
echo ========================================
echo.

REM Verifier les privileges administrateur
net session >nul 2>&1
if errorlevel 1 (
    echo ERREUR: Ce script doit etre execute en tant qu'administrateur
    echo Clic droit sur le fichier - "Executer en tant qu'administrateur"
    pause
    exit /b 1
)

echo Privileges administrateur confirmes
echo.

REM Verifier si Syncthing est deja installe
sc query syncthing >nul 2>&1
if not errorlevel 1 (
    echo ATTENTION: Syncthing est deja installe
    set /p "REINSTALL=Voulez-vous le reinstaller ? (O/N): "
    if /i not "%REINSTALL%"=="O" (
        echo Installation annulee
        pause
        exit /b 0
    )
    echo Arret du service Syncthing...
    net stop syncthing
)

echo.
echo Telechargement de Syncthing...
echo.

REM Creer un dossier temporaire
if not exist "%TEMP%\syncthing_install" mkdir "%TEMP%\syncthing_install"
cd /d "%TEMP%\syncthing_install"

REM Telecharger Syncthing (version Windows 64-bit)
echo Telechargement en cours...
powershell -Command "& {Invoke-WebRequest -Uri 'https://github.com/syncthing/syncthing/releases/latest/download/syncthing-windows-amd64-v1.27.8.zip' -OutFile 'syncthing.zip'}"

if not exist "syncthing.zip" (
    echo ERREUR: Impossible de telecharger Syncthing
    echo Verifiez votre connexion Internet
    pause
    exit /b 1
)

echo Telechargement termine
echo.

REM Extraire l'archive
echo Extraction de l'archive...
powershell -Command "& {Expand-Archive -Path 'syncthing.zip' -DestinationPath '.' -Force}"

if not exist "syncthing.exe" (
    echo ERREUR: Impossible d'extraire l'archive
    pause
    exit /b 1
)

echo Extraction terminee
echo.

REM Installer Syncthing
echo Installation de Syncthing...
echo.

REM Creer le repertoire d'installation
if not exist "C:\Program Files\Syncthing" mkdir "C:\Program Files\Syncthing"

REM Copier les fichiers
copy "syncthing.exe" "C:\Program Files\Syncthing\"
copy "syncthing.exe" "C:\Program Files\Syncthing\syncthing-service.exe"

REM Creer le service Windows
echo Creation du service Windows...
sc create syncthing binPath= "C:\Program Files\Syncthing\syncthing-service.exe" start= auto DisplayName= "Syncthing"

if errorlevel 1 (
    echo ERREUR: Impossible de creer le service
    pause
    exit /b 1
)

REM Demarrer le service
echo Demarrage du service...
sc start syncthing

if errorlevel 1 (
    echo ERREUR: Impossible de demarrer le service
    pause
    exit /b 1
)

echo Service demarre avec succes
echo.

REM Attendre que Syncthing soit pret
echo Attente du demarrage de Syncthing...
timeout /t 10 /nobreak >nul

REM Ouvrir l'interface web
echo Ouverture de l'interface web...
start http://localhost:8384

echo.
echo ========================================
echo INSTALLATION TERMINEE
echo ========================================
echo.
echo Syncthing installe et demarre
echo Interface web: http://localhost:8384
echo.
echo Prochaines etapes:
echo    1. Configurer le dossier partage dans l'interface web
echo    2. Ajouter l'autre PC comme device
echo    3. Copier les fichiers vers D:\MIA_SHARED
echo.
echo Guide detaille: GUIDE_INSTALLATION_SYNCING.md
echo.

REM Nettoyer les fichiers temporaires
cd /d "%TEMP%"
rmdir /s /q "syncthing_install" 2>nul

pause
