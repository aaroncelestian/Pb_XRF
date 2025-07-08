@echo off
REM === Set these paths as needed ===
set PYTHON_EXE=python
set SCRIPT_PATH=C:\XRF_Pb\xrf_Pb_analysis.py
set WORK_DIR=C:\XRF_Pb
set SHORTCUT_NAME=XRF Pb Analyzer.lnk

REM === Optional: Set a custom icon (must be .ico file) ===
REM set ICON_PATH=C:\XRF_Pb\Pb_logo.ico

REM === Create the shortcut on the Desktop using PowerShell ===
powershell -Command ^
 $WshShell = New-Object -ComObject WScript.Shell; ^
 $Shortcut = $WshShell.CreateShortcut([Environment]::GetFolderPath('Desktop') + '\%SHORTCUT_NAME%'); ^
 $Shortcut.TargetPath = '%PYTHON_EXE%'; ^
 $Shortcut.Arguments = '"%SCRIPT_PATH%"'; ^
 $Shortcut.WorkingDirectory = '%WORK_DIR%'; ^
 REM If you want a custom icon, uncomment the next line and set ICON_PATH ^
 REM $Shortcut.IconLocation = '%ICON_PATH%'; ^
 $Shortcut.Save()
echo Shortcut created on your Desktop as %SHORTCUT_NAME%
pause 