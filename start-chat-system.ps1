#!/usr/bin/env powershell
# Comprehensive startup script for two-user chat testing

param(
    [switch]$Help,
    [switch]$CleanStart
)

if ($Help) {
    Write-Host @"
Two-User Chat Startup Script
============================

This script starts all required servers for testing two-user real-time communication:
- Daphne backend server (port 8000) with ML moderation
- React frontend server 1 (port 3001) for User 1
- React frontend server 2 (port 3002) for User 2

Parameters:
  -CleanStart    Kill existing processes before starting
  -Help          Show this help message

Usage:
  .\start-chat-system.ps1
  .\start-chat-system.ps1 -CleanStart

After starting, open:
  User 1: http://localhost:3001
  User 2: http://localhost:3002
"@
    exit 0
}

Write-Host "🚀 Starting Two-User Chat System..." -ForegroundColor Green
Write-Host "====================================" -ForegroundColor Green

# Clean start if requested
if ($CleanStart) {
    Write-Host "🧹 Cleaning existing processes..." -ForegroundColor Yellow
    Get-Process -Name "python" -ErrorAction SilentlyContinue | Where-Object {$_.MainWindowTitle -like "*daphne*"} | Stop-Process -Force
    Get-Process -Name "node" -ErrorAction SilentlyContinue | Stop-Process -Force
    Start-Sleep -Seconds 2
}

# Check if ports are available
$ports = @(8000, 3001, 3002)
foreach ($port in $ports) {
    $connection = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue
    if ($connection) {
        Write-Host "⚠️  Port $port is already in use" -ForegroundColor Yellow
    }
}

Write-Host "`n1️⃣  Starting Daphne Backend Server (port 8000)..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD'; python -m daphne -b 0.0.0.0 -p 8000 mysite.asgi:application" -WindowStyle Normal

Write-Host "⏳ Waiting for backend to initialize..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

Write-Host "`n2️⃣  Starting React Frontend for User 1 (port 3001)..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD\react-chat-frontend'; `$env:PORT=3001; npm start" -WindowStyle Normal

Write-Host "⏳ Waiting for first frontend..." -ForegroundColor Yellow
Start-Sleep -Seconds 3

Write-Host "`n3️⃣  Starting React Frontend for User 2 (port 3002)..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD\react-chat-frontend'; `$env:PORT=3002; npm start" -WindowStyle Normal

Write-Host "`n✅ All servers starting..." -ForegroundColor Green
Write-Host "`n📋 Access URLs:" -ForegroundColor White
Write-Host "   User 1: http://localhost:3001" -ForegroundColor Cyan
Write-Host "   User 2: http://localhost:3002" -ForegroundColor Cyan
Write-Host "   Backend: http://localhost:8000" -ForegroundColor Cyan

Write-Host "`n🧪 Testing Instructions:" -ForegroundColor White
Write-Host "1. Open both URLs in separate browser windows/tabs" -ForegroundColor Gray
Write-Host "2. Sign in with different usernames (e.g. Alice and Bob)" -ForegroundColor Gray
Write-Host "3. Both users should appear in each others online list" -ForegroundColor Gray
Write-Host "4. Click on a user to start chatting" -ForegroundColor Gray
Write-Host "5. Test real-time messaging and ML moderation" -ForegroundColor Gray

Write-Host "`n⏰ Servers will take 30-60 seconds to fully start..." -ForegroundColor Yellow
Write-Host "Press any key to continue..." -ForegroundColor White
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")