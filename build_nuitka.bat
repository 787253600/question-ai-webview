@echo off
setlocal
cd /d "%~dp0"

if not exist ".venv-build\Scripts\python.exe" (
  echo Missing .venv-build. Create it with: python -m venv .venv-build
  exit /b 1
)

echo Cleaning...
if exist dist rmdir /s /q dist
if exist build rmdir /s /q build
if exist __pycache__ rmdir /s /q __pycache__

for /d %%i in ("%TEMP%\onefile_*") do (
  rmdir /s /q "%%i"
)

echo Installing dependencies...
.venv-build\Scripts\python.exe -m pip install --upgrade pip
.venv-build\Scripts\python.exe -m pip install --upgrade nuitka ordered-set zstandard
.venv-build\Scripts\python.exe -m pip install --upgrade pywebview
.venv-build\Scripts\python.exe -m pip install pythonnet==3.0.3
.venv-build\Scripts\python.exe -m pip install --upgrade uvicorn fastapi starlette openai clr_loader

echo Building...
.venv-build\Scripts\python.exe -m nuitka ^
  --standalone ^
  --windows-console-mode=force ^
  --enable-plugin=pywebview ^
  --enable-plugin=tk-inter ^
  --include-package=uvicorn ^
  --include-package=fastapi ^
  --include-package=starlette ^
  --include-package=openai ^
  --include-package=clr_loader ^
  --include-package=pythonnet ^
  --include-data-dir=static=static ^
  --include-data-file=config.example.json=config.example.json ^
  --nofollow-import-to=pytest ^
  --nofollow-import-to=tests ^
  --output-dir=dist ^
  desktop.py

if errorlevel 1 (
  echo Build failed.
  pause
  exit /b 1
)

echo Built: dist\AIQuestionHelper.exe
pause