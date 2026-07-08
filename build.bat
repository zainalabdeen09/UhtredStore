@echo off
title Uhtred Store - Build EXE
echo =============================
echo  بناء ملف EXE للتطبيق
echo =============================
echo.

echo [*] تثبيت المكتبات المطلوبة...
pip install -r requirements.txt

echo [*] تثبيت PyInstaller...
pip install pyinstaller

echo [*] بناء التطبيق...
pyinstaller --name "UhtredStore" --windowed --onefile --icon resources\icon.png --add-data "resources;resources" --add-data "ui;ui" main.py

echo.
echo [✓] تم! ملف EXE موجود بمجلد: dist\UhtredStore.exe
pause
