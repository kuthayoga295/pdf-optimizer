@echo off
setlocal enabledelayedexpansion

:: Mendefinisikan lokasi tool pdf
set "EXE_PATH=%~dp0bin\qpdf.exe"

:start
cls
echo ======================================================
echo       PDF OPTIMIZER (Auto File/Folder Mode)
echo ======================================================
echo.
echo Lokasi Executable: %EXE_PATH%
echo.
echo Silahkan DROP FILE atau FOLDER ke sini, lalu ENTER.
echo.

set "userInput="
set /p "userInput=Target Path: "

:: Menghapus tanda kutip jika ada
if defined userInput set "userInput=%userInput:"=%"

:: Cek keberadaan executable file
if not exist "%EXE_PATH%" (
    echo [ERROR] Executable file tidak ditemukan di: "%EXE_PATH%"
    pause
    exit /b
)

:: Cek apakah input ada
if "%userInput%"=="" goto start
if not exist "%userInput%" (
    echo [ERROR] Target tidak ditemukan: "%userInput%"
    pause
    goto start
)

echo ------------------------------------------------------

:: LOGIKA DETEKSI FILE ATAU FOLDER
:: Cek apakah atributnya mengandung "d" (directory)
for %%i in ("%userInput%") do set "attr=%%~ai"
set "isDir=%attr:~0,1%"

if /i "%isDir%"=="d" (
    echo [MODE] Folder + Subfolder terdeteksi.
    set "count=0"
    :: Menggunakan /r untuk loop masuk ke subfolder secara rekursif
    for /r "%userInput%" %%f in (*.pdf) do (
        set /a count+=1
        echo [!count!] Memproses: %%f...
        call :process_pdf "%%f"
    )
) else (
    echo [MODE] Single File terdeteksi.
    :: Ambil path folder dari file tersebut
    for %%i in ("%userInput%") do (
        set "fileDir=%%~dpi"
        set "fileName=%%~nxi"
    )
    :: Pindah ke drive dan folder file tersebut
    cd /d "!fileDir!"
    echo Memproses: !fileName!...
    call :process_pdf "!fileName!"
    set "count=1"
)

echo ------------------------------------------------------
echo Selesai! %count% file telah diproses.
echo.
echo Ingin memproses lagi? (Y/N)
set /p "choice=Pilihan: "
if /i "%choice%"=="Y" goto start
exit

:: SUB-ROUTINE UNTUK PROSES TOOL PDF
:process_pdf
set "fname=%~1"
:: Menggunakan full path (%~dpn1) agar file sementara dibuat di folder yang sama dengan file aslinya
set "tmpname=%~dpn1_tmp.pdf"

:: Pastikan file bukan file sementara yang baru dibuat
if "%fname:~-8%"=="_tmp.pdf" goto :eof

"%EXE_PATH%" --empty --pages "%fname%" 1-z -- "%tmpname%"

if exist "%tmpname%" (
    move /y "%tmpname%" "%fname%" >nul
) else (
    echo      [GAGAL] %fname%
)
goto :eof