@echo off
setlocal
cd /d "%~dp0"

set "directory_scripts=%APPDATA%\Blackmagic Design\DaVinci Resolve\Support\Fusion\Scripts\Edit\YTPMVD"
set "directory_data=%ProgramFiles%\Blackmagic Design\YTPMVD"

REM --> Check admin
if /i "%~1"=="/admin" goto :Admin

REM --> Files requiring userprofile
if exist "%directory_scripts%" rmdir /s /q "%directory_scripts%"
mkdir "%directory_scripts%"
copy /y "YTPMVD_UI.py" "%directory_scripts%\" >nul
if errorlevel 1 (
    echo Failed to copy YTPMVD_UI.py
    pause
    exit /b 1
)
echo Installed UI script to: %directory_scripts%

REM --> Skip elevation if already admin
fltmc >nul 2>&1 && goto :Admin

REM --> Elevate to admin
echo Set UAC = CreateObject^("Shell.Application"^) > "%temp%\getadmin.vbs"
set params= %*
echo UAC.ShellExecute "%~s0", "%params%", "", "runas", 1 >> "%temp%\getadmin.vbs"

"%temp%\getadmin.vbs"
del "%temp%\getadmin.vbs"
exit /B

:Admin
REM --> Files requiring admin
if exist "%directory_data%" rmdir /s /q "%directory_data%"
mkdir "%directory_data%"
copy /y "YTPMVE.py" "%directory_data%\" >nul
copy /y "cantersoft.ico" "%directory_data%\" >nul
echo Installed data files to: %directory_data%

echo Installed YTPMVD
pause