@echo off
setlocal EnableExtensions
cd /d "%~dp0"
title P2P File Transfer - Windows EXE Builder

echo =============================================
echo   P2P File Transfer - Windows EXE Builder
echo =============================================
echo.

REM Avoid a broken global `py` launcher selecting a removed Python 3.15 install.
set "PYTHON_CMD="

where python >nul 2>nul
if not errorlevel 1 (
  python -c "import sys; print(sys.version)" >nul 2>nul
  if not errorlevel 1 set "PYTHON_CMD=python"
)

if not defined PYTHON_CMD (
  for %%V in (3.14 3.13 3.12 3.11) do (
    if not defined PYTHON_CMD (
      py -%%V -c "import sys; print(sys.version)" >nul 2>nul
      if not errorlevel 1 set "PYTHON_CMD=py -%%V"
    )
  )
)

if not defined PYTHON_CMD (
  echo ERROR: A working Python 3.14, 3.13, 3.12, or 3.11 installation was not found.
  echo Install Python from python.org, enable the Python PATH option,
  echo then reopen this file. Avoid relying on the broken Python 3.15 launcher entry.
  echo.
  pause
  exit /b 1
)

echo Using Python command: %PYTHON_CMD%
%PYTHON_CMD% -c "import sys; print(sys.executable); print(sys.version)"
if errorlevel 1 goto :failed

echo.
echo [1/4] Creating build environment...
if not exist ".build_venv\Scripts\python.exe" (
  %PYTHON_CMD% -m venv .build_venv
  if errorlevel 1 goto :failed
)
set "BUILD_PY=.build_venv\Scripts\python.exe"

if not exist "%BUILD_PY%" (
  echo ERROR: Could not create the virtual environment.
  goto :failed
)

echo.
echo [2/4] Updating pip...
"%BUILD_PY%" -m pip install --upgrade pip
if errorlevel 1 goto :failed

echo.
echo [3/4] Installing build dependencies...
"%BUILD_PY%" -m pip install --upgrade "magic-wormhole>=0.23.0" pyinstaller pillow
if errorlevel 1 goto :failed

echo.
echo [4/4] Building EXE...
"%BUILD_PY%" -m PyInstaller --noconfirm --clean --onefile --windowed --name "P2P-File-Transfer" --icon "p2p_file_transfer.ico" --add-data "p2p_file_transfer.ico;." "kolay_dosya_aktarimi_duzeltilmis.py"
if errorlevel 1 goto :failed

echo.
echo Build finished. EXE: dist\P2P-File-Transfer.exe
echo.
echo IMPORTANT: This EXE build still expects the Magic Wormhole CLI to be available
 echo in the runtime environment. It may not run on a clean PC without Python and
 echo magic-wormhole installed. This build script does not yet bundle the Wormhole CLI.
echo.
pause
exit /b 0

:failed
echo.
echo Build failed. Read the error above.
echo If pip reports network/SSL errors, check your internet connection and proxy settings.
echo If Python cannot start, install Python 3.14, 3.13, 3.12, or 3.11 from python.org and enable PATH.
pause
exit /b 1
