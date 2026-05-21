@echo off
:: Cek apakah Python terinstal di Windows pengguna
where pythonw >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Python tidak ditemukan di sistem Windows ini!
    echo Silakan instal Python terlebih dahulu agar aplikasi ini bisa berjalan.
    echo.
    pause
    exit
)

:: Jalankan run.py tanpa memunculkan jendela hitam CMD
start "" "pythonw" "%~dp0run.py"
exit