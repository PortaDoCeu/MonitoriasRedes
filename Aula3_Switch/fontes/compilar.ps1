# Regera todo o material da Aula 3.
#   Entregas (PDFs, PowerPoint, Aula.ipynb) -> raiz de Aula3_Switch
#   Arquivos temporários (.aux, .log, imagens do PPTX...) -> Aula3_Switch\temporarios
#
# Uso, na pasta Aula3_Switch\fontes:
#     .\compilar.ps1
# (ou, no cmd: powershell -ExecutionPolicy Bypass -File compilar.ps1)

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
$raiz = Resolve-Path ".."
$tmp = Join-Path $raiz "temporarios"
$tmpLatex = Join-Path $tmp "latex"
$tmpPptx = Join-Path $tmp "pptx"
New-Item -ItemType Directory -Force $tmpLatex, (Join-Path $tmpPptx "imagens") | Out-Null

$miktex = Join-Path $env:LOCALAPPDATA "Programs\MiKTeX\miktex\bin\x64"
$xelatex = Join-Path $miktex "xelatex.exe"
$pdftoppm = Join-Path $miktex "miktex-pdftoppm.exe"

function Compilar($pasta, $arquivo, $passadas) {
    # o MiKTeX escreve avisos em stderr; no PowerShell 5.1 isso não pode interromper o script
    $ErrorActionPreference = "SilentlyContinue"
    Push-Location $pasta
    foreach ($i in 1..$passadas) {
        & $xelatex -interaction=nonstopmode "-aux-directory=$tmpLatex" "-output-directory=$raiz" $arquivo 2>$null | Out-Null
    }
    $log = Join-Path $tmpLatex ([IO.Path]::ChangeExtension($arquivo, ".log"))
    $erros = Select-String -Path $log -Pattern '^!|Overfull' -ErrorAction SilentlyContinue
    if ($erros) { Write-Host "  $arquivo com avisos:" -ForegroundColor Yellow; $erros | ForEach-Object { Write-Host "    $($_.Line)" } }
    else { Write-Host "  $arquivo ok" -ForegroundColor Green }
    Pop-Location
}

Write-Host "Figuras e roteiro"
python figuras.py | Out-Null
python gerar_roteiro.py | Out-Null

Write-Host "LaTeX"
Compilar "." "slides_aula3.tex" 2
Compilar "." "slides_aula3_notas.tex" 2
Compilar "." "mapa_bancada.tex" 1
Compilar "." "ficha_comandos.tex" 1
Compilar "guia" "guia_monitor.tex" 3

Write-Host "PowerPoint"
$pptx = Join-Path $raiz "slides_aula3.pptx"
try { [IO.File]::Open($pptx, 'OpenOrCreate', 'ReadWrite', 'None').Close() }
catch { Write-Host "  slides_aula3.pptx está aberto (feche o PowerPoint e rode de novo)" -ForegroundColor Red; exit 1 }
Get-ChildItem (Join-Path $tmpPptx "imagens") | Remove-Item -Force
$env:PYTHONIOENCODING = "utf-8"
python pptx\extrair_notas.py slides_aula3.tex (Join-Path $tmpPptx "notas.json") | Out-Null
& $pdftoppm -r 240 -png (Join-Path $raiz "slides_aula3.pdf") (Join-Path $tmpPptx "imagens\slide") 2>$null
Push-Location pptx
$env:NOTAS = Join-Path $tmpPptx "notas.json"
$env:IMAGENS = Join-Path $tmpPptx "imagens"
$env:TEX = "..\slides_aula3.tex"
node gerar_pptx.js $pptx | Out-Null
python separar_paragrafos.py $pptx | Out-Null
Pop-Location
Write-Host "  slides_aula3.pptx ok" -ForegroundColor Green
