@echo off
setlocal
cd /d "%~dp0"

call "%~dp0build.bat" nopause
if errorlevel 1 exit /b %errorlevel%

set "ISCC=D:\Program Files (x86)\Inno Setup 6\ISCC.exe"
if not exist "%ISCC%" (
  echo 未找到 Inno Setup 6 的 ISCC.exe：%ISCC%
  echo 请检查 Inno Setup 6 安装路径。
  pause
  exit /b 1
)

"%ISCC%" "%~dp0installer.iss"
set "INSTALLER_EXIT=%ERRORLEVEL%"
if not "%INSTALLER_EXIT%"=="0" exit /b %INSTALLER_EXIT%

echo.
echo 安装包已生成：installer\AIQuestionHelper_Setup.exe
if /I "%~1"=="--no-pause" exit /b 0
if /I "%~1"=="nopause" exit /b 0
pause
exit /b 0
