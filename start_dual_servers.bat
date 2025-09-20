@echo off
echo Starting dual React dev servers for two-user testing...
echo Port 3000: First user window
echo Port 3001: Second user window
echo.

cd react-chat-frontend

echo Starting React server on port 3000...
start "React Server 3000" cmd /k "npm start"

timeout /t 3 /nobreak > nul

echo Starting React server on port 3001...
start "React Server 3001" cmd /k "set PORT=3001 && npm start"

echo.
echo Both servers starting...
echo First user:  http://localhost:3000
echo Second user: http://localhost:3001
echo.
pause