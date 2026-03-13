$ErrorActionPreference = "Stop"

$pythonExe = (Get-Command python).Source

function Run-Python {
    param([Parameter(ValueFromRemainingArguments = $true)][string[]]$Args)
    & $pythonExe @Args
    if ($LASTEXITCODE -ne 0) {
        throw "Fallo comando: python $($Args -join ' ') (exit $LASTEXITCODE)"
    }
}

Write-Host "Usando Python: $pythonExe"
Run-Python --version

# Limpieza para evitar residuos de builds anteriores
if (Test-Path ".\\build") { Remove-Item ".\\build" -Recurse -Force }
if (Test-Path ".\\dist") { Remove-Item ".\\dist" -Recurse -Force }

# Instalar dependencias en el mismo interpreter que construye
Run-Python -m pip install --upgrade pip
Run-Python -m pip install --upgrade pyinstaller
Run-Python -m pip install -r requirements.txt

# Validar dependencias criticas del backend Qt (PySide6)
Run-Python -c "import webview; import qtpy; from PySide6 import QtCore; from PySide6 import QtWebEngineWidgets; print('Qt backend OK (PySide6)')"

# Build
Run-Python -m PyInstaller --noconfirm --clean Reproductor.spec

Write-Host ""
Write-Host "Build finalizado."
Write-Host "Ejecuta SIEMPRE este archivo:"
Write-Host ".\\dist\\Reproductor\\Reproductor.exe"
