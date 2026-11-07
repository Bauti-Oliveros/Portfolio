$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$Streamlit = Join-Path $ProjectRoot "venv\Scripts\streamlit.exe"
$App = Join-Path $ProjectRoot "src\app_v211_offline.py"
$ModelDir = Join-Path $ProjectRoot "models\bge-m3"
$DatabaseDir = Join-Path $ProjectRoot "data\db_vector_v2"

Clear-Host

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "          Perito.AR v2.1.1 Offline" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

if (-not (Test-Path $Streamlit)) {
    Write-Host "[ERROR] No se encontro Streamlit." -ForegroundColor Red
    exit 1
}

if (-not (Test-Path $App)) {
    Write-Host "[ERROR] No se encontro la interfaz offline." -ForegroundColor Red
    exit 1
}

if (-not (Test-Path $ModelDir)) {
    Write-Host "[ERROR] No se encontro BGE-M3 local." -ForegroundColor Red
    exit 1
}

if (-not (Test-Path $DatabaseDir)) {
    Write-Host "[ERROR] No se encontro ChromaDB v2." -ForegroundColor Red
    exit 1
}

$OllamaModel = ollama list | Select-String "qwen3:8b"

if (-not $OllamaModel) {
    Write-Host "[ERROR] qwen3:8b no esta disponible." -ForegroundColor Red
    exit 1
}

Write-Host "[OK] Snapshot local de BGE-M3 encontrado." -ForegroundColor Green
Write-Host "[OK] Base codigo_penal_v2 encontrada." -ForegroundColor Green
Write-Host "[OK] qwen3:8b disponible en Ollama." -ForegroundColor Green
Write-Host ""
Write-Host "Iniciando interfaz..." -ForegroundColor Yellow
Write-Host "La ventana mostrara MODELO DISPONIBLE al terminar el warm-up." -ForegroundColor DarkGray
Write-Host ""

Set-Location $ProjectRoot

& $Streamlit run $App `
    --server.address 127.0.0.1 `
    --server.headless false `r`n    --server.fileWatcherType none `
    --browser.gatherUsageStats false
