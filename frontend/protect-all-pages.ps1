# Script pour protéger toutes les pages avec ProtectedRoute

$pagesToProtect = @(
    "app\backtesting\page.tsx",
    "app\analytics\page.tsx",
    "app\compare\page.tsx",
    "app\chart\page.tsx",
    "app\ia-analyst\page.tsx",
    "app\results\[runId]\page.tsx",
    "app\run\page.tsx",
    "app\strategies\[...strategyId]\page.tsx",
    "app\strategies\[strategyId]\page.tsx"
)

foreach ($page in $pagesToProtect) {
    $filePath = Join-Path $PSScriptRoot $page
    
    if (Test-Path $filePath) {
        Write-Host "🔒 Protection de $page..." -ForegroundColor Yellow
        
        $content = Get-Content $filePath -Raw
        
        # Vérifier si déjà protégé
        if ($content -match "ProtectedRoute") {
            Write-Host "   ✅ Déjà protégé" -ForegroundColor Green
            continue
        }
        
        # Ajouter l'import
        if ($content -notmatch "import.*ProtectedRoute") {
            $content = $content -replace "(import.*from '@/components/dashboard/header')", "`$1`nimport { ProtectedRoute } from '@/components/auth/protected-route'"
        }
        
        # Envelopper le return
        $content = $content -replace "(\s+return\s+\(\s*\n\s*<>)", "`$1`n    <ProtectedRoute>"
        $content = $content -replace "(\s+</>\s*\n\s+\))", "`n    </ProtectedRoute>`$1"
        
        Set-Content $filePath $content -NoNewline
        Write-Host "   ✅ Protégé avec succès" -ForegroundColor Green
    } else {
        Write-Host "   ⚠️  Fichier non trouvé: $page" -ForegroundColor Red
    }
}

Write-Host "`n✨ Protection terminée!" -ForegroundColor Cyan
