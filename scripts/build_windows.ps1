$ErrorActionPreference = "Stop"

$pythonExe = (Get-Command python).Source

Write-Host "Usando Python: $pythonExe"
& $pythonExe --version

# Limpieza para evitar residuos de builds anteriores
if (Test-Path ".\build") { Remove-Item ".\build" -Recurse -Force }
if (Test-Path ".\dist") { Remove-Item ".\dist" -Recurse -Force }
if (Test-Path ".\SecureAudioPlayer.spec") { Remove-Item ".\SecureAudioPlayer.spec" -Force }

# Instalar PyInstaller en el mismo interpreter que construye
& $pythonExe -m pip install --upgrade pyinstaller
& $pythonExe -m pip install -r requirements.txt

# Build
& $pythonExe -m PyInstaller `
  --noconfirm `
  --clean `
  --windowed `
  --name SecureAudioPlayer `
  --exclude-module pythonnet `
  --exclude-module clr `
  --exclude-module clr_loader `
  --add-data "secure_audio_app\frontend;secure_audio_app\frontend" `
  app.py

Write-Host ""
Write-Host "Build finalizado."
Write-Host "Ejecuta SIEMPRE este archivo:"
Write-Host ".\dist\SecureAudioPlayer\SecureAudioPlayer.exe"
