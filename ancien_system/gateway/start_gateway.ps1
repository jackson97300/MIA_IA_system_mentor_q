# Script PowerShell pour démarrer IBKR Gateway
Write-Host "🚀 Démarrage IBKR Gateway..." -ForegroundColor Green

# Configuration Java
$JAVA_HOME = "D:\MIA_IA_system\OpenJDK17U-jdk_x64_windows_hotspot_17.0.16_8\jdk-17.0.16+8"
$JAVA_BIN = "$JAVA_HOME\bin\java.exe"

Write-Host "Java Home: $JAVA_HOME" -ForegroundColor Yellow

# Vérifier si Java existe
if (Test-Path $JAVA_BIN) {
    Write-Host "✅ Java trouvé: $JAVA_BIN" -ForegroundColor Green
    
    # Configuration Gateway
    $config_path = "D:\MIA_IA_system\clientportal.beta.gw\root\"
    $config_file = "conf.yaml"
    $runtime_path = "$config_path;dist\ibgroup.web.core.iblink.router.clientportal.gw.jar;build\lib\runtime\*"
    
    Write-Host "Config path: $config_path" -ForegroundColor Yellow
    Write-Host "Runtime path: $runtime_path" -ForegroundColor Yellow
    
    # Démarrer le Gateway
    Write-Host "🔧 Démarrage du Gateway..." -ForegroundColor Cyan
    
    & $JAVA_BIN -server `
        -Dvertx.disableDnsResolver=true `
        -Djava.net.preferIPv4Stack=true `
        -Dvertx.logger-delegate-factory-class-name=io.vertx.core.logging.SLF4JLogDelegateFactory `
        -Dnologback.statusListenerClass=ch.qos.logback.core.status.OnConsoleStatusListener `
        -Dnolog4j.debug=true `
        -Dnolog4j2.debug=true `
        -classpath $runtime_path `
        ibgroup.web.core.clientportal.gw.GatewayStart
        
} else {
    Write-Host "❌ Java non trouvé: $JAVA_BIN" -ForegroundColor Red
    Write-Host "Vérifiez l'installation de Java" -ForegroundColor Red
}

Write-Host "Gateway arrêté." -ForegroundColor Yellow





