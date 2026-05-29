@echo off
REM BRAINS Research Skill — cmd wrapper for install.ps1
powershell -ExecutionPolicy Bypass -File "%~dp0install.ps1" %*
