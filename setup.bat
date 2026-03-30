@echo off
setlocal EnableExtensions

title FetchUrl - Installation

echo ================================
echo  FetchUrl - Installation initiale
echo ================================
echo.

REM --- Verification de Python ---
python --version >nul 2>&1
if %errorlevel% neq 0 (
  echo [ERREUR] Python est introuvable.
  echo Installe Python depuis https://www.python.org puis relance ce fichier.
  pause & goto :eof
)

REM --- Installation des dependances Python ---
echo Installation de pip...
python -m ensurepip --upgrade
python -m pip install --upgrade pip --quiet

echo Installation des dependances Python...
python -m pip install customtkinter pyinstaller --quiet
if %errorlevel% neq 0 (
  echo [ERREUR] pip a echoue.
  pause & goto :eof
)

REM --- Telechargement de yt-dlp ---
if not exist "bin" mkdir bin
echo.
echo Telechargement de yt-dlp...
curl -L "https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp.exe" -o "bin\yt-dlp.exe"
if %errorlevel% neq 0 (
  echo [ERREUR] Impossible de telecharger yt-dlp.
  pause & goto :eof
)

REM --- Telechargement de ffmpeg ---
echo Telechargement de ffmpeg...
curl -L "https://github.com/yt-dlp/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip" -o "bin\ffmpeg.zip"
if %errorlevel% neq 0 (
  echo [ERREUR] Impossible de telecharger ffmpeg.
  pause & goto :eof
)

echo Extraction de ffmpeg...
powershell -Command "Expand-Archive -Path 'bin\ffmpeg.zip' -DestinationPath 'bin\ffmpeg_tmp' -Force"
for /r "bin\ffmpeg_tmp" %%f in (ffmpeg.exe) do copy "%%f" "bin\ffmpeg.exe" >nul
rd /s /q "bin\ffmpeg_tmp"
del "bin\ffmpeg.zip"

echo.
echo Installation terminee !
echo.
echo Lance maintenant : python app.py
echo Ou compile en exe : build.bat
echo.
pause
