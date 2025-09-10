@echo off
echo Starting IBKR Beta Gateway...

REM Set Java path
set JAVA_HOME=D:\MIA_IA_system\OpenJDK17U-jdk_x64_windows_hotspot_17.0.16_8\jdk-17.0.16+8
set PATH=%JAVA_HOME%\bin;%PATH%

REM Set configuration
set config_path=%~dp0root\
set runtime_path=%config_path%;%~dp0dist\ibgroup.web.core.iblink.router.clientportal.gw.jar;%~dp0build\lib\runtime\*

echo Config path: %config_path%
echo Runtime path: %runtime_path%

REM Start the gateway
java -server ^
  -Dvertx.disableDnsResolver=true ^
  -Djava.net.preferIPv4Stack=true ^
  -Dvertx.logger-delegate-factory-class-name=io.vertx.core.logging.SLF4JLogDelegateFactory ^
  -Dnologback.statusListenerClass=ch.qos.logback.core.status.OnConsoleStatusListener ^
  -Dnolog4j.debug=true ^
  -Dnolog4j2.debug=true ^
  -classpath "%runtime_path%" ^
  ibgroup.web.core.clientportal.gw.GatewayStart

echo Gateway stopped.
pause

