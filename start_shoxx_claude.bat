@echo off
chcp 65001 >nul
title SHOXX // Claude Code Local Studio Launcher
color 0B

echo ============================================================================
echo   SHOXX // CLAUDE CODE LOCAL UNCENSORED STUDIO
echo   Senior MMP Coding Suite (AppsFlyer, Singular, Adjust)
echo ============================================================================
echo.

cd /d "%~dp0"

:: 1. Pruefe Python Installation
where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python wurde nicht im System-PATH gefunden!
    echo Bitte installiere Python 3.10+ von https://www.python.org/
    pause
    exit /b 1
)

:: 2. Pruefe ob Ollama installiert ist und starte Server im Hintergrund falls noetig
where ollama >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    echo [INFO] Pruefe lokalen Ollama-Server auf Port 11434...
    powershell -NoProfile -Command "try { Invoke-WebRequest -Uri 'http://localhost:11434/api/tags' -UseBasicParsing -TimeoutSec 2 | Out-Null; Write-Host '[OK] Ollama Server laeuft bereits.' -ForegroundColor Green } catch { Write-Host '[INFO] Starte lokalen Ollama Server im Hintergrund...' -ForegroundColor Yellow; Start-Process 'ollama' -ArgumentList 'serve' -WindowStyle Hidden }"
) else (
    echo [WARN] Ollama CLI noch nicht im PATH gefunden. Kann im Setup-Menue eingerichtet werden.
)

echo [INFO] Starte SHOXX Claude Code Studio GUI...
start "" pythonw "%~dp0shoxx_claude_studio.py"
if %ERRORLEVEL% NEQ 0 (
    python "%~dp0shoxx_claude_studio.py"
)

exit /b 0
