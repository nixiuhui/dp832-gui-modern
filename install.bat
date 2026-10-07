@echo off
rem 安装/修复 DP832 GUI 依赖（创建 .venv 并安装 PySide6 / pyqtgraph / pyvisa）
cd /d "%~dp0"
python -m venv .venv
".venv\Scripts\python.exe" -m pip install --upgrade pip
".venv\Scripts\python.exe" -m pip install PySide6 pyqtgraph pyvisa
echo 依赖安装完成。
pause
