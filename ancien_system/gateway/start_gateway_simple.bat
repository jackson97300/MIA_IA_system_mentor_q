@echo off
echo ========================================
echo Démarrage Gateway IBKR BETA - Version Simple
echo ========================================

REM Définir le chemin vers Java dans le projet
set JAVA_HOME=%~dp0OpenJDK17U-jdk_x64_windows_hotspot_17.0.16_8\jdk-17.0.16+8
set PATH=%JAVA_HOME%\bin;%PATH%

echo Java Home: %JAVA_HOME%
echo.

REM Vérifier que Java est accessible
echo Vérification de Java...
java -version
if %errorlevel% neq 0 (
    echo ❌ Erreur: Java n'est pas accessible
    pause
    exit /b 1
)

echo ✅ Java est correctement configuré
echo.

REM Aller dans le répertoire du gateway
cd /d "%~dp0clientportal.beta.gw"

echo Démarrage du Gateway IBKR BETA...
echo Le gateway sera accessible sur: https://localhost:5000
echo.
echo IMPORTANT: Après le démarrage, ouvrez votre navigateur sur:
echo https://localhost:5000
echo.
echo Appuyez sur Ctrl+C pour arrêter le gateway
echo.

REM Démarrer le gateway avec le script original
call start_gateway.bat

echo.
echo Gateway arrêté.
pause













