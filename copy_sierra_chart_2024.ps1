# 🚀 MIA IA SYSTEM - Copie Dossier Sierra Chart 2024
# Script PowerShell pour copier le dossier Sierra Chart 2024
# Version: Production Ready v1.0

Write-Host "========================================" -ForegroundColor Blue
Write-Host "📁 COPIE DOSSIER SIERRA CHART 2024" -ForegroundColor Blue
Write-Host "========================================" -ForegroundColor Blue
Write-Host ""

# Vérifier que le dossier source existe
$sourcePath = "D:\MICRO SIERRA CHART 2024"
$destinationPath = "D:\MIA_SHARED\MICRO_SIERRA_CHART_2024"

if (-not (Test-Path $sourcePath)) {
    Write-Host "❌ Dossier source introuvable: $sourcePath" -ForegroundColor Red
    Write-Host "💡 Vérifiez le chemin et réessayez" -ForegroundColor Yellow
    Write-Host "💡 Le dossier peut être dans un autre emplacement" -ForegroundColor Yellow
    Read-Host "Appuyez sur Entrée pour continuer"
    exit 1
}

Write-Host "✅ Dossier source trouvé: $sourcePath" -ForegroundColor Green

# Créer le dossier de destination s'il n'existe pas
if (-not (Test-Path "D:\MIA_SHARED")) {
    Write-Host "📁 Création du dossier MIA_SHARED..." -ForegroundColor Yellow
    New-Item -ItemType Directory -Path "D:\MIA_SHARED" -Force | Out-Null
}

if (-not (Test-Path $destinationPath)) {
    Write-Host "📁 Création du dossier de destination..." -ForegroundColor Yellow
    New-Item -ItemType Directory -Path $destinationPath -Force | Out-Null
}

Write-Host "✅ Dossier de destination prêt: $destinationPath" -ForegroundColor Green
Write-Host ""

# Afficher la taille du dossier source
$sourceSize = (Get-ChildItem -Path $sourcePath -Recurse | Measure-Object -Property Length -Sum).Sum
$sourceSizeMB = [math]::Round($sourceSize / 1MB, 2)

Write-Host "📊 Taille du dossier source: $sourceSizeMB MB" -ForegroundColor Cyan
Write-Host ""

# Afficher le contenu du dossier source
Write-Host "📋 Contenu du dossier Sierra Chart 2024:" -ForegroundColor Cyan
Get-ChildItem -Path $sourcePath -Directory | ForEach-Object {
    Write-Host "   📁 $($_.Name)" -ForegroundColor White
}
Get-ChildItem -Path $sourcePath -File | ForEach-Object {
    Write-Host "   📄 $($_.Name)" -ForegroundColor White
}
Write-Host ""

# Demander confirmation
$confirmation = Read-Host "Voulez-vous copier le dossier Sierra Chart 2024 vers MIA_SHARED ? (O/N)"
if ($confirmation -ne "O" -and $confirmation -ne "o") {
    Write-Host "❌ Copie annulée par l'utilisateur" -ForegroundColor Red
    exit 0
}

Write-Host ""
Write-Host "🚀 Début de la copie..." -ForegroundColor Green
Write-Host "⏱️  Cela peut prendre quelques minutes selon la taille du dossier" -ForegroundColor Yellow
Write-Host ""

# Copier le dossier avec robocopy
try {
    $robocopyArgs = @(
        "`"$sourcePath`"",
        "`"$destinationPath`"",
        "/E",           # Copier les sous-dossiers
        "/R:3",         # 3 tentatives en cas d'erreur
        "/W:1",         # Attendre 1 seconde entre les tentatives
        "/MT:8",        # Utiliser 8 threads pour la copie
        "/NFL",         # Ne pas lister les fichiers
        "/NDL",         # Ne pas lister les dossiers
        "/NJH",         # Pas d'en-tête de travail
        "/NJS",         # Pas de résumé
        "/NC",          # Pas de classe
        "/NS",          # Pas de taille
        "/NP"           # Pas de pourcentage
    )
    
    $process = Start-Process -FilePath "robocopy" -ArgumentList $robocopyArgs -Wait -PassThru -NoNewWindow
    
    if ($process.ExitCode -le 7) {
        Write-Host "✅ Copie terminée avec succès!" -ForegroundColor Green
        
        # Afficher la taille du dossier de destination
        $destSize = (Get-ChildItem -Path $destinationPath -Recurse | Measure-Object -Property Length -Sum).Sum
        $destSizeMB = [math]::Round($destSize / 1MB, 2)
        
        Write-Host "📊 Taille du dossier de destination: $destSizeMB MB" -ForegroundColor Cyan
        
        # Vérifier l'intégrité
        if ($sourceSize -eq $destSize) {
            Write-Host "✅ Intégrité vérifiée: Tailles identiques" -ForegroundColor Green
        } else {
            Write-Host "⚠️  Attention: Tailles différentes (source: $sourceSizeMB MB, dest: $destSizeMB MB)" -ForegroundColor Yellow
        }
        
        # Afficher le contenu du dossier de destination
        Write-Host ""
        Write-Host "📋 Contenu copié dans MIA_SHARED:" -ForegroundColor Cyan
        Get-ChildItem -Path $destinationPath -Directory | ForEach-Object {
            Write-Host "   📁 $($_.Name)" -ForegroundColor White
        }
        Get-ChildItem -Path $destinationPath -File | ForEach-Object {
            Write-Host "   📄 $($_.Name)" -ForegroundColor White
        }
        
    } else {
        Write-Host "❌ Erreur lors de la copie (Code: $($process.ExitCode))" -ForegroundColor Red
        Write-Host "💡 Codes d'erreur robocopy:" -ForegroundColor Yellow
        Write-Host "   0-7: Succès" -ForegroundColor White
        Write-Host "   8+: Erreur" -ForegroundColor White
    }
    
} catch {
    Write-Host "❌ Erreur lors de l'exécution de robocopy: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Blue
Write-Host "🎉 SCRIPT TERMINÉ" -ForegroundColor Blue
Write-Host "========================================" -ForegroundColor Blue
Write-Host ""
Write-Host "📋 Prochaines étapes:" -ForegroundColor Cyan
Write-Host "   1. Vérifier que Syncthing est configuré" -ForegroundColor White
Write-Host "   2. Le dossier sera synchronisé automatiquement" -ForegroundColor White
Write-Host "   3. Accéder au dossier depuis l'autre PC" -ForegroundColor White
Write-Host "   4. Configurer Sierra Chart pour utiliser le dossier partagé" -ForegroundColor White
Write-Host ""

Read-Host "Appuyez sur Entrée pour continuer"
