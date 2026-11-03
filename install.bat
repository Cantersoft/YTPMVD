@echo off

:-------------------------------------
REM  --> Check for permissions
    IF "%PROCESSOR_ARCHITECTURE%" EQU "amd64" (
>nul 2>&1 "%SYSTEMROOT%\SysWOW64\cacls.exe" "%SYSTEMROOT%\SysWOW64\config\system"
) ELSE (
>nul 2>&1 "%SYSTEMROOT%\system32\cacls.exe" "%SYSTEMROOT%\system32\config\system"
)

REM --> If error flag set, we do not have admin.
if '%errorlevel%' NEQ '0' (
    echo Requesting administrative privileges...
    goto UACPrompt
) else ( goto gotAdmin )

:UACPrompt
    echo Set UAC = CreateObject^("Shell.Application"^) > "%temp%\getadmin.vbs"
    set params= %*
	REM  --> The user will switch to admin after we elevate and then the userprofile will be wrong, so let's capture the userprofile as it is originally.
    echo UAC.ShellExecute "cmd.exe", "/c ""%~s0"" ""%userprofile%"" %params:"=""%", "", "runas", 1 >> "%temp%\getadmin.vbs"

    "%temp%\getadmin.vbs"
    del "%temp%\getadmin.vbs"
    exit /B

:gotAdmin
    pushd "%CD%"
    CD /D "%~dp0"
:--------------------------------------    

set script_interface_installation_directory="%~1\AppData\Roaming\Blackmagic Design\DaVinci Resolve\Support\Fusion\Scripts\Edit\YTPMVD"
set data_installation_directory="%programfiles%\Blackmagic Design\YTPMVD"

rmdir /s /q %data_installation_directory%
mkdir %data_installation_directory%

rmdir /s /q %script_interface_installation_directory%
mkdir %script_interface_installation_directory% 

echo Y | xcopy YTPMVD_UI.py %script_interface_installation_directory%
echo Y | xcopy YTPMVE.py %data_installation_directory%
echo Y | xcopy cantersoft.ico %data_installation_directory%

echo %script_interface_installation_directory%
echo Installed YTPMVD
pause