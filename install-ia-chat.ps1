wind# Script PowerShell pour installer le Chat IA
Write-Host "====================================" -ForegroundColor Cyan
Write-Host " Installation du Chat IA - Analyse  " -ForegroundColor Cyan
Write-Host "====================================" -ForegroundColor Cyan

# Installation des dépendances frontend
Write-Host "`n📦 Installation des packages NPM..." -ForegroundColor Yellow
Set-Location -Path "frontend"

Write-Host "Installation de react-markdown..." -ForegroundColor Green
npm install react-markdown@9.0.1

Write-Host "Installation de react-syntax-highlighter..." -ForegroundColor Green
npm install react-syntax-highlighter@15.5.0

Write-Host "Installation des types TypeScript..." -ForegroundColor Green
npm install --save-dev @types/react-syntax-highlighter@15.5.11

Write-Host "`n✅ Installation terminée!" -ForegroundColor Green

# Retour au dossier principal
Set-Location -Path ".."

Write-Host "`n🚀 Pour lancer l'application:" -ForegroundColor Cyan
Write-Host "   1. Terminal 1: cd backend && python main.py" -ForegroundColor White
Write-Host "   2. Terminal 2: cd frontend && npm run dev" -ForegroundColor White
Write-Host "   3. Ouvrir: http://localhost:3000" -ForegroundColor White
Write-Host "   4. Cliquer sur 'IA Analyst' dans le menu" -ForegroundColor White

Write-Host "`n💡 Commandes disponibles dans le chat:" -ForegroundColor Yellow
Write-Host "   - Analyse les performances du dernier backtest" -ForegroundColor Gray
Write-Host "   - Génère un code pour calculer le Sharpe ratio" -ForegroundColor Gray
Write-Host "   - Montre la distribution des PnL par heure" -ForegroundColor Gray
Write-Host "   - Analyse la volatilité récente" -ForegroundColor Gray

Write-Host "`n📊 Profitez de votre nouvel assistant IA!" -ForegroundColor Green
