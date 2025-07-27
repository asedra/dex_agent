@echo off
echo Windows PowerShell Agent Baslatiliyor...
echo.

REM Python'un yuklu olup olmadigini kontrol et
python --version >nul 2>&1
if errorlevel 1 (
    echo HATA: Python yuklu degil!
    echo Python 3.11+ yukleyin ve tekrar deneyin.
    pause
    exit /b 1
)

REM Virtual environment olustur (eger yoksa)
if not exist "venv" (
    echo Virtual environment olusturuluyor...
    python -m venv venv
)

REM Virtual environment'i aktif et
echo Virtual environment aktif ediliyor...
call venv\Scripts\activate.bat

REM Gereksinimleri yukle
echo Gereksinimler yukleniyor...
pip install -r requirements.txt

REM .env dosyasini olustur (eger yoksa)
if not exist ".env" (
    echo .env dosyasi olusturuluyor...
    copy env.example .env
    echo.
    echo DİKKAT: .env dosyasindaki API_TOKEN degerini degistirin!
    echo.
)

REM Sunucuyu baslat
echo.
echo Sunucu baslatiliyor...
echo API: http://localhost:8000
echo Dokumantasyon: http://localhost:8000/docs
echo.
python app.py

pause 