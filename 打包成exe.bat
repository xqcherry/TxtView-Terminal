@echo off
chcp 65001 >nul
cd /d "%~dp0"

set "PY="
where py >nul 2>nul
if not errorlevel 1 set "PY=py -3"

if "%PY%"=="" (
  where python >nul 2>nul
  if not errorlevel 1 set "PY=python"
)

if "%PY%"=="" (
  echo [错误] 没找到 Python。
  echo 请安装 Windows 官方 Python：https://www.python.org/downloads/
  echo 安装时勾选 Add Python to PATH。
  pause
  exit /b 1
)

echo 使用 Python：
%PY% -c "import sys; print(sys.executable)"

%PY% -m pip --version >nul 2>nul
if errorlevel 1 (
  echo.
  echo 当前 Python 没有 pip，尝试启用 ensurepip...
  %PY% -m ensurepip --upgrade
)

%PY% -m pip --version >nul 2>nul
if errorlevel 1 (
  echo.
  echo [错误] 这个 Python 没有 pip，通常是 MSYS2 的 Python。
  echo 请安装 Windows 官方 Python： https://www.python.org/downloads/
  echo 安装时一定勾选 Add Python to PATH。
  pause
  exit /b 1
)

echo.
echo 安装/检查 PyInstaller 和 Pygments...
%PY% -m pip install pyinstaller pygments
if errorlevel 1 pause && exit /b 1

echo.
echo 打包终端版 txtview.exe...
%PY% -m PyInstaller --noconfirm --onefile --console --name txtview txtview.py
if errorlevel 1 pause && exit /b 1

echo.
echo 完成：dist\txtview.exe
echo 双击它会先弹出选文件窗口，然后进入真正终端渲染。
pause
