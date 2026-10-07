@echo off
rem 一键启动 DP832 GUI（静默运行，无控制台窗口）
set "PYW=%~dp0.venv\Scripts\pythonw.exe"
set "SCRIPT=%~dp0dp832gui\dpgui.py"
if not exist "%PYW%" (
    echo 未找到虚拟环境 Python，请先运行 install.bat 安装依赖。
    pause
    exit /b 1
)
start "" "%PYW%" "%SCRIPT%"
