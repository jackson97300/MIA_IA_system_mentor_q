# Script pour nettoyer le dossier tests
# Garde seulement les nouveaux tests et déplace les anciens

# Créer le dossier d'archive
New-Item -ItemType Directory -Force -Path "tests_old"

# Liste des nouveaux tests à garder
$newTests = @(
    "test_sanity.py",
    "test_policies.py", 
    "test_structure_data.py",
    "test_pipeline_e2e.py",
    "test_schema_validation.py",
    "test_observability.py",
    "test_kill_switch_e2e.py",
    "test_phase2_integration.py",
    "conftest.py",
    "__init__.py"
)

# Déplacer tous les fichiers sauf les nouveaux
Get-ChildItem -Path "tests" -File | ForEach-Object {
    if ($_.Name -notin $newTests) {
        Move-Item -Path $_.FullName -Destination "tests_old\" -Force
        Write-Host "Déplacé: $($_.Name)"
    }
}

# Déplacer les dossiers aussi
Get-ChildItem -Path "tests" -Directory | ForEach-Object {
    Move-Item -Path $_.FullName -Destination "tests_old\" -Force
    Write-Host "Déplacé dossier: $($_.Name)"
}

Write-Host "Nettoyage terminé. Nouveaux tests gardés dans tests/"
Write-Host "Anciens tests déplacés dans tests_old/"

