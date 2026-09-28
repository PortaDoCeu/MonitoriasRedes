# Sobe o projeto (ADR-024, ajustado pelas ADRs 030 e 031).
#
# Notebook de um grupo:   .\iniciar.ps1
#     sobe o broker do grupo (se BROKER_LOCAL=sim), o clp_simulado (se MODO=simulado),
#     o middleware e o gateway, cada um na sua janela.
# Notebook do monitor:    .\iniciar.ps1 -Broker
#     sobe só o Mosquitto compartilhado, plano B dos grupos (rode o PowerShell
#     como administrador na primeira vez, para criar as regras de firewall).

param([switch]$Broker)

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
$py = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"

if (-not (Test-Path $py)) {
    Write-Host "Ambiente virtual não encontrado. Rode antes:" -ForegroundColor Red
    Write-Host "    python -m venv .venv"
    Write-Host "    .venv\Scripts\python -m pip install -r requirements.txt"
    exit 1
}

function Abrir($titulo, $comando) {
    Start-Process powershell -WorkingDirectory $PSScriptRoot -ArgumentList @(
        "-NoExit", "-Command", "`$host.UI.RawUI.WindowTitle = '$titulo'; $comando")
}

function Ips {
    Get-NetIPAddress -AddressFamily IPv4 |
        Where-Object { $_.IPAddress -notmatch '^(127|169\.254)\.' } |
        Select-Object -ExpandProperty IPAddress
}

# ------------------------------------------------------------ broker (monitor)
if ($Broker) {
    $mosquitto = "C:\Program Files\mosquitto\mosquitto.exe"
    if (-not (Test-Path $mosquitto)) { Write-Host "Mosquitto não instalado." -ForegroundColor Red; exit 1 }
    $servico = Get-Service mosquitto -ErrorAction SilentlyContinue
    if ($servico -and $servico.Status -eq "Running") {
        Write-Host "O serviço Mosquitto do Windows está rodando e ocupa a porta 1883." -ForegroundColor Red
        Write-Host "Pare como administrador: Stop-Service mosquitto; Set-Service mosquitto -StartupType Manual"
        exit 1
    }
    if (-not (Test-Path "broker\senhas")) { & $py broker\criar_usuarios.py 6 }

    $admin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole(
        [Security.Principal.WindowsBuiltInRole]::Administrator)
    foreach ($porta in 1883, 9001) {
        $nome = "Planta MQTT $porta"
        if (-not (Get-NetFirewallRule -DisplayName $nome -ErrorAction SilentlyContinue)) {
            if ($admin) {
                New-NetFirewallRule -DisplayName $nome -Direction Inbound -Protocol TCP -LocalPort $porta -Action Allow | Out-Null
                Write-Host "regra de firewall criada: $nome"
            } else {
                Write-Host "Falta a regra de firewall da porta $porta. Rode uma vez como administrador." -ForegroundColor Yellow
            }
        }
    }
    Abrir "broker" "& '$mosquitto' -c broker\mosquitto.conf -v"
    Write-Host "Broker no ar. IPs deste notebook (use em MQTT_HOST dos grupos): $((Ips) -join ', ')" -ForegroundColor Green
    exit 0
}

# ------------------------------------------------------------ bancada (grupo)
if (-not (Test-Path "config.env")) {
    Write-Host "config.env não encontrado. Copie config.exemplo.env para config.env e preencha." -ForegroundColor Red
    exit 1
}
$cfg = @{}
Get-Content config.env | ForEach-Object {
    if ($_ -match '^\s*([^#=][^=]*?)\s*=\s*(.*)$') { $cfg[$Matches[1]] = $Matches[2] }
}

if ($cfg.BROKER_LOCAL -eq "sim") {
    # broker do próprio grupo (etapa 2, ADR-031)
    $mosquitto = "C:\Program Files\mosquitto\mosquitto.exe"
    $servico = Get-Service mosquitto -ErrorAction SilentlyContinue
    if ($servico -and $servico.Status -eq "Running") {
        Write-Host "O serviço Mosquitto do Windows está rodando e ocupa a porta 1883." -ForegroundColor Red
        Write-Host "Pare como administrador: Stop-Service mosquitto; Set-Service mosquitto -StartupType Manual"
        exit 1
    }
    if (-not (Test-Path "broker\senhas")) {
        Write-Host "broker\senhas não existe: crie os usuários com mosquitto_passwd (etapa 2)." -ForegroundColor Red
        exit 1
    }
    Abrir "broker" "& '$mosquitto' -c broker\mosquitto.conf -v"
    foreach ($i in 1..20) {
        if ((Test-NetConnection 127.0.0.1 -Port $cfg.MQTT_PORT -WarningAction SilentlyContinue).TcpTestSucceeded) { break }
        Start-Sleep -Milliseconds 500
    }
}

if ($cfg.MODO -eq "simulado") {
    Abrir "clp simulado" "& '$py' clp_simulado.py --porta $($cfg.MODBUS_PORT)"
    Start-Sleep -Seconds 1
}

Abrir "middleware" "& '$py' middleware\middleware.py"
$url = "http://127.0.0.1:$($cfg.HTTP_PORTA)/docs"
foreach ($i in 1..20) {
    try { Invoke-WebRequest $url -UseBasicParsing -TimeoutSec 1 | Out-Null; break } catch { Start-Sleep -Milliseconds 500 }
}

Abrir "gateway" "& '$py' gateway\gateway.py"

Write-Host ""
Write-Host "$($cfg.BANCADA) no ar. No celular, abra:" -ForegroundColor Green
Ips | ForEach-Object { Write-Host "    http://$($_):$($cfg.HTTP_PORTA)" }
