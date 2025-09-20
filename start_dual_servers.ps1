# PowerShell script to start React dev servers on ports 3000 and 3001
# This allows testing with two different browser windows

Write-Host "Starting dual React dev servers for two-user testing..." -ForegroundColor Green
Write-Host "Port 3000: First user window" -ForegroundColor Cyan
Write-Host "Port 3001: Second user window" -ForegroundColor Cyan

# Change to React frontend directory
Set-Location "react-chat-frontend"

# Start first React server on port 3000 (default)
Write-Host "`nStarting React server on port 3000..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "npm start" -WindowStyle Normal

# Wait a moment for the first server to start
Start-Sleep -Seconds 3

# Start second React server on port 3001
Write-Host "Starting React server on port 3001..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "set PORT=3001 && npm start" -WindowStyle Normal

Write-Host "`nBoth servers starting..." -ForegroundColor Green
Write-Host "First user:  http://localhost:3000" -ForegroundColor Cyan
Write-Host "Second user: http://localhost:3001" -ForegroundColor Cyan
Write-Host "`nPress any key to continue..." -ForegroundColor Yellow
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")