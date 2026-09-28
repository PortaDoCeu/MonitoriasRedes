# Encerra os processos do projeto na ordem inversa da inicialização (ADR-024).
Set-Location $PSScriptRoot

foreach ($script in "gateway.py", "middleware.py", "clp_simulado.py") {
    Get-CimInstance Win32_Process -Filter "Name='python.exe'" |
        Where-Object { $_.CommandLine -like "*$script*" } |
        ForEach-Object {
            Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue
            Write-Host "encerrado: $script ($($_.ProcessId))"
        }
}
Get-CimInstance Win32_Process -Filter "Name='mosquitto.exe'" |
    Where-Object { $_.CommandLine -like "*broker\mosquitto.conf*" } |
    ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue; Write-Host "encerrado: broker" }

# fecha as janelas abertas pelo iniciar.ps1
Get-Process powershell -ErrorAction SilentlyContinue |
    Where-Object { $_.MainWindowTitle -in "gateway", "middleware", "clp simulado", "broker" } |
    Stop-Process -Force -ErrorAction SilentlyContinue