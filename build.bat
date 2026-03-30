@echo off
setlocal EnableExtensions

title FetchUrl - Compilation

echo ================================
echo  FetchUrl - Compilation en .exe
echo ================================
echo.

python --version >nul 2>&1
if %errorlevel% neq 0 (
  echo [ERREUR] Python introuvable. Lance setup.bat d'abord.
  pause & goto :eof
)

if not exist "bin\yt-dlp.exe" (
  echo [ERREUR] bin\yt-dlp.exe introuvable. Lance setup.bat d'abord.
  pause & goto :eof
)

if not exist "bin\ffmpeg.exe" (
  echo [ERREUR] bin\ffmpeg.exe introuvable. Lance setup.bat d'abord.
  pause & goto :eof
)

REM --- Compilation ---
echo Compilation en cours...
python -m PyInstaller --onefile --noconsole --name FetchUrl --distpath . app.py

if %errorlevel% neq 0 (
  echo.
  echo [ERREUR] La compilation a echoue.
  pause & goto :eof
)

echo.
echo Nettoyage des fichiers de build...
rd /s /q build 2>nul
del FetchUrl.spec 2>nul

REM --- Creation du zip de distribution ---
echo.
echo Creation de FetchUrl.zip...
if exist "FetchUrl.zip" del "FetchUrl.zip"

powershell -Command "Add-Type -Assembly 'System.IO.Compression.FileSystem'; $archive = [System.IO.Compression.ZipFile]::Open('FetchUrl.zip', 'Create'); [System.IO.Compression.ZipFileExtensions]::CreateEntryFromFile($archive, 'FetchUrl.exe', 'FetchUrl/FetchUrl.exe'); [System.IO.Compression.ZipFileExtensions]::CreateEntryFromFile($archive, 'bin\yt-dlp.exe', 'FetchUrl/bin/yt-dlp.exe'); [System.IO.Compression.ZipFileExtensions]::CreateEntryFromFile($archive, 'bin\ffmpeg.exe', 'FetchUrl/bin/ffmpeg.exe'); $archive.Dispose()"

if %errorlevel% neq 0 (
  echo [ERREUR] La creation du zip a echoue.
  pause & goto :eof
)

echo.
echo ================================
echo  Termine !
echo  - FetchUrl.exe  : pret
echo  - FetchUrl.zip  : pret pour GitHub Releases
echo ================================
echo.
pause
