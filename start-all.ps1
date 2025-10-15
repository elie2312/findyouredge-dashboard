# Script de démarrage automatique du dashboard NQ
# Auteur: Assistant AI
# Date: 2025-10-09

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   NQ Backtest Dashboard - Démarrage   " -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Vérifier si Node.js est installé
$nodeVersion = node --version 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "[X] Node.js n'est pas installe" -ForegroundColor Red
    Write-Host "   Telechargez-le sur: https://nodejs.org/" -ForegroundColor Yellow
    Write-Host "   Version recommandee: 18.x ou 20.x LTS" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "   Demarrage du backend uniquement..." -ForegroundColor Yellow
    Write-Host ""
    
    # Démarrer uniquement le backend
    Set-Location backend
    Write-Host "[*] Demarrage du backend..." -ForegroundColor Green
    python start.py
    exit
}

Write-Host "[OK] Node.js detecte: $nodeVersion" -ForegroundColor Green
Write-Host ""

# Demander à l'utilisateur ce qu'il veut démarrer
Write-Host "Que voulez-vous démarrer ?" -ForegroundColor Yellow
Write-Host "1. Backend uniquement"
Write-Host "2. Frontend uniquement"
Write-Host "3. Backend + Frontend (2 terminaux)"
Write-Host ""
$choice = Read-Host "Votre choix (1/2/3)"

switch ($choice) {
    "1" {
        Write-Host ""
        Write-Host "[*] Demarrage du backend..." -ForegroundColor Green
        Set-Location backend
        python start.py
    }
    "2" {
        Write-Host ""
        # Vérifier si node_modules existe
        if (-Not (Test-Path "frontend\node_modules")) {
            Write-Host "[!] node_modules non trouve" -ForegroundColor Yellow
            Write-Host "[*] Installation des dependances..." -ForegroundColor Yellow
            Set-Location frontend
            npm install
            Write-Host ""
            Write-Host "[OK] Installation terminee" -ForegroundColor Green
            Write-Host ""
        }
        
        Write-Host "[*] Demarrage du frontend..." -ForegroundColor Green
        Set-Location frontend
        npm run dev
    }
    "3" {
        Write-Host ""
        Write-Host "[*] Demarrage du backend + frontend..." -ForegroundColor Green
        Write-Host ""
        Write-Host "[>] Terminal 1: Backend (ce terminal)" -ForegroundColor Cyan
        Write-Host "[>] Terminal 2: Frontend (nouveau terminal)" -ForegroundColor Cyan
        Write-Host ""
        
        # Démarrer le backend dans ce terminal
        Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD\backend'; Write-Host '[*] Backend demarre' -ForegroundColor Green; python start.py"
        
        Start-Sleep -Seconds 2
        
        # Vérifier si node_modules existe
        if (-Not (Test-Path "frontend\node_modules")) {
            Write-Host "[!] node_modules non trouve" -ForegroundColor Yellow
            Write-Host "[*] Installation des dependances..." -ForegroundColor Yellow
            Write-Host "   (cela peut prendre 5-10 minutes)" -ForegroundColor Yellow
            Write-Host ""
            
            Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD\frontend'; Write-Host '[*] Installation des dependances...' -ForegroundColor Yellow; npm install; Write-Host ''; Write-Host '[OK] Installation terminee' -ForegroundColor Green; Write-Host '[*] Frontend demarre' -ForegroundColor Green; npm run dev"
        } else {
            # Démarrer le frontend dans un nouveau terminal
            Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD\frontend'; Write-Host '[*] Frontend demarre' -ForegroundColor Green; npm run dev"
        }
        
        Write-Host ""
        Write-Host "[OK] Services en cours de demarrage..." -ForegroundColor Green
        Write-Host ""
        Write-Host "[>] Backend: http://localhost:8000" -ForegroundColor Cyan
        Write-Host "[>] Frontend: http://localhost:3000" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "Appuyez sur une touche pour quitter ce script..." -ForegroundColor Yellow
        $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    }
    default {
        Write-Host ""
        Write-Host "[X] Choix invalide" -ForegroundColor Red
        exit
    }
}
