@echo off
setlocal enabledelayedexpansion
title Tarek's Portfolio and App Launcher

:menu
cls
echo =========================================================
echo              Tarek's App ^& Portfolio Launcher
echo =========================================================
echo.
echo   [1] Start Portfolio Website (Local Server)
echo   [2] Find and Run a Python App (.py) with Streamlit
echo   [0] Exit
echo.
echo =========================================================
set /p choice="Enter your choice (0-2): "

if "%choice%"=="1" goto start_portfolio
if "%choice%"=="2" goto list_apps
if "%choice%"=="0" exit

goto menu

:start_portfolio
echo.
echo Starting local web server...
echo Your browser will open automatically.
echo (Press Ctrl+C in this window to stop the server when done)
echo.
start http://localhost:8000
python -m http.server 8000
pause
goto menu

:list_apps
cls
echo =========================================================
echo                  Available Python Apps
echo =========================================================
echo.
set /a count=0
for /R "%~dp0" %%F in (*.py) do (
    set /a count+=1
    set "file!count!=%%F"
    set "folder=%%~dpF"
    set "rel_folder=!folder:%~dp0=!"
    echo   [!count!] %%~nxF ^(in .\!rel_folder!^)
)

echo.
if %count%==0 (
    echo No .py files found in this directory or subdirectories.
    echo.
    pause
    goto menu
)

echo   [0] Go back to main menu
echo.
echo =========================================================
set /p app_choice="Enter the number of the app to run: "

if "%app_choice%"=="0" goto menu
if "%app_choice%"=="" goto list_apps

set "target=!file%app_choice%!"
if not defined target (
    echo Invalid choice!
    pause
    goto list_apps
)

echo.
echo Starting Streamlit for "!target!"...
:: Run the selected streamlit app in a new command window so the menu stays open
for %%I in ("!target!") do (
    cd /d "%%~dpI"
    start cmd /k "title Streamlit - %%~nxI & echo Running %%~nxI... & echo. & streamlit run "%%~nxI""
)
:: Return to the base directory
cd /d "%~dp0"
goto menu
