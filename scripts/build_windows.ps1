$ErrorActionPreference = "Stop"

$pythonExe = (Get-Command python).Source

function Remove-DirectorySafe {
    param(
        [Parameter(Mandatory = $true)][string]$PathToRemove
    )

    if (-not (Test-Path $PathToRemove)) {
        return
    }

    Get-Process -Name "Reproductor" -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue

    $attempts = 3
    for ($i = 1; $i -le $attempts; $i++) {
        try {
            Remove-Item $PathToRemove -Recurse -Force -ErrorAction Stop
            return
        } catch {
            if ($i -eq $attempts) {
                throw "No se pudo limpiar '$PathToRemove'. Cierra Reproductor.exe/Finder/Explorer en esa carpeta y reintenta. Detalle: $($_.Exception.Message)"
            }
            Start-Sleep -Milliseconds 600
        }
    }
}

function Run-Python {
    param([Parameter(ValueFromRemainingArguments = $true)][string[]]$Args)
    & $pythonExe @Args
    if ($LASTEXITCODE -ne 0) {
        throw "Fallo comando: python $($Args -join ' ') (exit $LASTEXITCODE)"
    }
}

Write-Host "Usando Python: $pythonExe"
Run-Python --version

Remove-DirectorySafe ".\\build"
Remove-DirectorySafe ".\\dist"
if (-not (Test-Path ".\\release")) { New-Item -ItemType Directory -Path ".\\release" | Out-Null }

Run-Python -m pip install --upgrade pip
Run-Python -m pip install --upgrade pyinstaller
Run-Python -m pip install -r requirements.txt

Run-Python -c "import tkinter; import vlc; import mutagen; import cryptography; print('Runtime Tkinter OK')"

Run-Python -m PyInstaller --noconfirm --clean Reproductor.spec

Write-Host ""
Write-Host "Build finalizado."
Write-Host "Ejecuta SIEMPRE este archivo:"
Write-Host ".\\dist\\Reproductor\\Reproductor.exe"
Write-Host "ZIP para distribuir (PowerShell):"
Write-Host "Compress-Archive -Path `".\\dist\\Reproductor\\*`" -DestinationPath `".\\release\\Reproductor-Windows.zip`" -Force"
