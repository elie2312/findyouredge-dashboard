# Script d'installation et configuration Firebase
# Exécutez ce script depuis le dossier frontend

Write-Host "🔥 Configuration Firebase pour NQ Dashboard" -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host ""

# Vérifier si npm est installé
if (-not (Get-Command npm -ErrorAction SilentlyContinue)) {
    Write-Host "❌ npm n'est pas installé. Installez Node.js d'abord." -ForegroundColor Red
    exit 1
}

# Vérifier si on est dans le bon dossier
if (-not (Test-Path "package.json")) {
    Write-Host "❌ Exécutez ce script depuis le dossier frontend" -ForegroundColor Red
    exit 1
}

# Étape 1 : Installation de Firebase
Write-Host "📦 Étape 1/3 : Installation de Firebase..." -ForegroundColor Yellow
npm install firebase

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Firebase installé avec succès" -ForegroundColor Green
} else {
    Write-Host "❌ Erreur lors de l'installation de Firebase" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Étape 2 : Vérifier si .env.local existe
Write-Host "🔑 Étape 2/3 : Configuration des variables d'environnement..." -ForegroundColor Yellow

if (Test-Path ".env.local") {
    Write-Host "⚠️  Le fichier .env.local existe déjà" -ForegroundColor Yellow
    $response = Read-Host "Voulez-vous le remplacer ? (o/N)"
    if ($response -ne "o" -and $response -ne "O") {
        Write-Host "✅ Conservation du fichier .env.local existant" -ForegroundColor Green
    } else {
        Copy-Item ".env.local.example" ".env.local" -Force
        Write-Host "✅ Fichier .env.local créé depuis .env.local.example" -ForegroundColor Green
        Write-Host "⚠️  N'oubliez pas de remplir vos credentials Firebase !" -ForegroundColor Yellow
    }
} else {
    Copy-Item ".env.local.example" ".env.local"
    Write-Host "✅ Fichier .env.local créé" -ForegroundColor Green
    Write-Host "⚠️  N'oubliez pas de remplir vos credentials Firebase !" -ForegroundColor Yellow
}

Write-Host ""

# Étape 3 : Instructions finales
Write-Host "📋 Étape 3/3 : Prochaines étapes" -ForegroundColor Yellow
Write-Host ""
Write-Host "1️⃣  Récupérez vos credentials Firebase :" -ForegroundColor Cyan
Write-Host "   → https://console.firebase.google.com/" -ForegroundColor Gray
Write-Host "   → Paramètres du projet → Général → Vos applications" -ForegroundColor Gray
Write-Host ""
Write-Host "2️⃣  Modifiez le fichier .env.local avec vos vraies valeurs" -ForegroundColor Cyan
Write-Host ""
Write-Host "3️⃣  Activez l'authentification Email/Password dans Firebase Console" -ForegroundColor Cyan
Write-Host "   → Authentication → Sign-in method → Email/Password" -ForegroundColor Gray
Write-Host ""
Write-Host "4️⃣  Créez un utilisateur de test dans Firebase Console" -ForegroundColor Cyan
Write-Host "   → Authentication → Users → Add user" -ForegroundColor Gray
Write-Host ""
Write-Host "5️⃣  Démarrez le serveur de développement :" -ForegroundColor Cyan
Write-Host "   npm run dev" -ForegroundColor Gray
Write-Host ""
Write-Host "6️⃣  Testez la connexion :" -ForegroundColor Cyan
Write-Host "   http://localhost:3000/login" -ForegroundColor Gray
Write-Host ""
Write-Host "📚 Pour plus de détails, consultez FIREBASE_SETUP.md" -ForegroundColor Magenta
Write-Host ""
Write-Host "✨ Configuration terminée !" -ForegroundColor Green
