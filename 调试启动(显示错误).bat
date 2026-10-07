@echo off
rem 调试启动 DP832 GUI（保留控制台窗口，便于查看报错）
cd /d "%~dp0dp832gui"
"..\.venv\Scripts\python.exe" dpgui.py
pause
