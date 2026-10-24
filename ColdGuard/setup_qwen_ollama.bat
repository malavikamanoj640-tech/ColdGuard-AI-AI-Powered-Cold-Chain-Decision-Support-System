@echo off
title SupplyShield AI - Qwen Ollama Setup
echo ==========================================
echo SupplyShield AI - Qwen Ollama Setup
echo ==========================================
where ollama >nul 2>&1
if errorlevel 1 (
  echo.
  echo Ollama is not installed or not in PATH.
  echo Install Ollama first, then run this file again.
  echo.
  pause
  exit /b 1
)
echo.
echo Checking Ollama...
ollama list
echo.
echo Pulling Qwen 2.5 0.5B...
ollama pull qwen2.5:0.5b
echo.
echo Qwen setup complete.
echo You can now run run.bat and open http://127.0.0.1:5000/ai-lab
echo.
pause
