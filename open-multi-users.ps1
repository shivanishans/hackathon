#!/usr/bin/env powershell
# Script to open multiple browser windows for testing socket-based chat

Write-Host "🌐 Opening Multiple Browser Windows for Socket Testing..." -ForegroundColor Green
Write-Host "=====================================================" -ForegroundColor Green

$url = "http://localhost:3000"

Write-Host "`n📋 Testing Instructions:" -ForegroundColor Cyan
Write-Host "1. Each browser window represents a different user" -ForegroundColor Gray
Write-Host "2. Sign in with different names (e.g., Alice, Bob, Charlie)" -ForegroundColor Gray
Write-Host "3. Watch the CMD window for socket connection logs" -ForegroundColor Gray
Write-Host "4. Test real-time communication between users" -ForegroundColor Gray
Write-Host "5. Try sending abusive words to test ML moderation" -ForegroundColor Gray

Write-Host "`n🔗 Opening browser windows..." -ForegroundColor Yellow

# Open first browser window
Start-Process "msedge" -ArgumentList "--new-window", $url, "--window-position=0,0", "--window-size=800,600"
Write-Host "   User 1: New Edge window opened" -ForegroundColor Green

Start-Sleep -Seconds 2

# Open second browser window
Start-Process "msedge" -ArgumentList "--new-window", $url, "--window-position=820,0", "--window-size=800,600"
Write-Host "   User 2: New Edge window opened" -ForegroundColor Green

Start-Sleep -Seconds 2

# Open third browser window (optional)
$response = Read-Host "`nOpen third user window? (y/n)"
if ($response -eq "y" -or $response -eq "Y") {
    Start-Process "msedge" -ArgumentList "--new-window", $url, "--window-position=400,300", "--window-size=800,600"
    Write-Host "   User 3: New Edge window opened" -ForegroundColor Green
}

Write-Host "`n✅ Browser windows opened!" -ForegroundColor Green
Write-Host "💡 Check the CMD window running Daphne to see socket connections" -ForegroundColor Yellow
Write-Host "🔌 Each user connection will show as Socket 1, Socket 2, etc." -ForegroundColor Yellow