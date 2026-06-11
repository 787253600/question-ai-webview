@echo off
setlocal
cd /d "%~dp0"

:: 清理旧文件
if exist dist rmdir /s /q dist
if exist build rmdir /s /q build
if exist __pycache__ rmdir /s /q __pycache__

:: 打包
.venv-build\Scripts\python.exe -m PyInstaller ^
 --clean ^
 --noconfirm ^
 --onefile ^
 --windowed ^
 --name AIQuestionHelper ^
 --collect-all webview ^
 --collect-all pythonnet ^
 --collect-all clr_loader ^
 --hidden-import uvicorn ^
 --hidden-import fastapi ^
 --hidden-import starlette ^
 --add-data "static;static" ^
 --add-data "config.example.json;." ^
 desktop.py

set "BUILD_EXIT=%ERRORLEVEL%"
if /I "%~1"=="--no-pause" exit /b %BUILD_EXIT%
if /I "%~1"=="nopause" exit /b %BUILD_EXIT%
pause
exit /b %BUILD_EXIT%