@echo off
rem Atalho para o iniciar.ps1: funciona com duplo clique, no cmd ou no PowerShell.
rem Repassa os argumentos (ex.: iniciar.bat -Broker).
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0iniciar.ps1" %*
pause
