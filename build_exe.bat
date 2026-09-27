@echo off
setlocal
cd /d "%~dp0"
py -m pip install --upgrade pip
py -m pip install pyinstaller
py -m PyInstaller --noconfirm --clean --onefile --windowed ^
  --name BusinessAccounting ^
  --collect-all tkinter ^
  app\main.py
echo.
echo ============================================
echo EXE created in: dist\BusinessAccounting.exe
echo ============================================
pause
